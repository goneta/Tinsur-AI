from decimal import Decimal
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.payroll import PayrollTransaction
from app.models.employee import EmployeeProfile
from app.models.user import User
from app.models.commission import Commission
from app.repositories.commission_repository import CommissionRepository

class PayrollService:
    def __init__(self, db: Session):
        self.db = db
        self.commission_repo = CommissionRepository(db)
        from app.services.accounting_service import AccountingService
        self.accounting_service = AccountingService(db)

    def calculate_taxes(self, gross_salary: Decimal) -> Dict[str, Decimal]:
        """
        Calculate Côte d'Ivoire specific taxes.
        Simplified for implementation but follows standard logic.
        """
        # 1. Base Calculable (80% of Gross)
        base_calculable = gross_salary * Decimal('0.80')

        # 2. IS (Impôt sur le Salaire) - 1.5% of 80% Gross
        tax_is = base_calculable * Decimal('0.015')

        # 3. CN (Contribution Nationale)
        # 0-50k: 0%, 50k-130k: 1.5%, 130k-200k: 5%, >200k: 10%
        if gross_salary <= 50000:
            tax_cn = Decimal('0')
        elif gross_salary <= 130000:
            tax_cn = (gross_salary - 50000) * Decimal('0.015')
        elif gross_salary <= 200000:
            tax_cn = (130000 - 50000) * Decimal('0.015') + (gross_salary - 130000) * Decimal('0.05')
        else:
            tax_cn = (130000 - 50000) * Decimal('0.015') + (200000 - 130000) * Decimal('0.05') + (gross_salary - 200000) * Decimal('0.10')

        # 4. CNPS (Social Security) - 6.3% of Gross (ceiling usually 3M, ignoring for simplicity)
        tax_cnps = gross_salary * Decimal('0.063')

        # 5. IGR (Impôt Général sur le Revenu)
        # Simplified IGR calculation (standard formula can be very complex)
        # Using a flat 5% of gross as a placeholder or a simplified tiered model
        tax_igr = gross_salary * Decimal('0.05')

        return {
            "tax_is": tax_is.quantize(Decimal('0.01')),
            "tax_cn": tax_cn.quantize(Decimal('0.01')),
            "tax_igr": tax_igr.quantize(Decimal('0.01')),
            "tax_cnps": tax_cnps.quantize(Decimal('0.01'))
        }

    def process_monthly_payroll(self, company_id: uuid.UUID, month: str, processor_id: uuid.UUID) -> List[PayrollTransaction]:
        """
        Process payroll for all employees in a company for a specific month.
        Month format: "YYYY-MM"
        """
        # 1. Get all employees with profiles
        stmt = select(User).join(EmployeeProfile).where(User.company_id == company_id)
        employees = self.db.execute(stmt).scalars().all()
        
        results = []
        for employee in employees:
            # Check if already processed
            check_stmt = select(PayrollTransaction).where(
                and_(
                    PayrollTransaction.employee_id == employee.id,
                    PayrollTransaction.payment_month == month
                )
            )
            # Use .first() to avoid MultipleResultsFound
            existing = self.db.execute(check_stmt).scalars().first()
            if existing:
                continue

            profile = employee.employee_profile
            base_salary = profile.base_salary or Decimal('0')
            
            # 2. Fetch pending commissions
            # Fixed: Use get_by_company instead of non-existent get_by_agent
            commissions, _ = self.commission_repo.get_by_company(
                company_id=company_id,
                agent_id=employee.id,
                status='pending'
            )
            commissions_total = sum(c.amount for c in commissions)
            
            # Gross Salary
            gross_salary = base_salary + commissions_total
            
            # 3. Calculate Taxes
            taxes = self.calculate_taxes(gross_salary)
            
            total_deductions = taxes["tax_is"] + taxes["tax_cn"] + taxes["tax_igr"] + taxes["tax_cnps"]
            net_pay = gross_salary - total_deductions
            
            # 4. Create Transaction
            transaction = PayrollTransaction(
                employee_id=employee.id,
                company_id=company_id,
                amount=gross_salary,
                currency=profile.currency or 'XOF',
                payment_month=month,
                payment_method=profile.payment_method or 'bank_transfer',
                base_salary=base_salary,
                commissions_total=commissions_total,
                tax_is=taxes["tax_is"],
                tax_cn=taxes["tax_cn"],
                tax_igr=taxes["tax_igr"],
                social_security_cnps=taxes["tax_cnps"],
                net_pay=net_pay,
                status='pending',
                description=f"Salary for {month}",
                processed_by=processor_id
            )
            self.db.add(transaction)
            
            # 5. Mark commissions as paid
            for c in commissions:
                c.status = 'paid'
            
            results.append(transaction)
            
        if results:
            self._post_payroll_to_ledger(company_id, month, results, processor_id)
            
        self.db.commit()
        return results

    def _post_payroll_to_ledger(self, company_id: uuid.UUID, month: str, transactions: List[PayrollTransaction], processor_id: uuid.UUID):
        """Post consolidated payroll to general ledger."""
        try:
            from app.schemas.ledger import JournalEntryCreate, LedgerEntryCreate
            
            # 1. Initialize accounts
            self.accounting_service.initialize_chart_of_accounts(company_id)
            
            # 2. Collect Totals
            total_salary_expense = sum(t.base_salary for t in transactions)
            total_commission_expense = sum(t.commissions_total for t in transactions)
            total_is = sum(t.tax_is for t in transactions)
            total_cn = sum(t.tax_cn for t in transactions)
            total_igr = sum(t.tax_igr for t in transactions)
            total_cnps = sum(t.social_security_cnps for t in transactions)
            total_net_payable = sum(t.net_pay for t in transactions)
            
            # 3. Get Accounts
            acc_salary = self.accounting_service.get_or_create_account(company_id, "5000", "Salary Expense", "Expense")
            acc_comm = self.accounting_service.get_or_create_account(company_id, "5100", "Commission Expense", "Expense")
            acc_tax = self.accounting_service.get_or_create_account(company_id, "2200", "Tax Payable", "Liability")
            acc_payroll_pay = self.accounting_service.get_or_create_account(company_id, "2100", "Payroll Payable", "Liability")
            
            ledger_entries = [
                # Debits (Expenses)
                LedgerEntryCreate(account_id=acc_salary.id, debit=total_salary_expense, credit=Decimal('0')),
                LedgerEntryCreate(account_id=acc_comm.id, debit=total_commission_expense, credit=Decimal('0')),
                # Credits (Liabilities)
                LedgerEntryCreate(account_id=acc_tax.id, debit=Decimal('0'), credit=total_is + total_cn + total_igr + total_cnps),
                LedgerEntryCreate(account_id=acc_payroll_pay.id, debit=Decimal('0'), credit=total_net_payable)
            ]
            
            # 4. Post
            entry_data = JournalEntryCreate(
                description=f"Payroll Consolidation for {month}",
                reference=f"PAYROLL-{month}",
                entries=ledger_entries
            )
            
            self.accounting_service.post_journal_entry(company_id, entry_data, processor_id)
            
        except Exception as e:
            import traceback
            print(f"CRITICAL: Failed to post payroll to ledger: {str(e)}")
            traceback.print_exc()
