from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
import random

from app.models.quote import Quote
from app.models.client import Client
from app.models.client_details import ClientAutomobile
from app.models.premium_policy import PremiumPolicyType
from app.services.premium_policy_service import PremiumPolicyService
from sqlalchemy.orm import Session


class QuoteGenerationService:
    """
    Service for auto-generating recommended insurance quotes for clients.

    This service handles:
    1. Loading client data and vehicles
    2. Finding matching premium policies
    3. Calculating premiums
    4. Sorting by price (cheapest first)
    5. Returning recommendations
    """

    def __init__(self, db: Session):
        self.db = db
        self.policy_service = PremiumPolicyService(db)

    def auto_generate_quotes(self, client_id: UUID) -> List[Dict[str, Any]]:
        """
        Auto-generate recommended quotes for a client.

        Process:
        1. Load client data
        2. Load vehicles
        3. Find matching premium policies
        4. Calculate premium for each policy/vehicle combo
        5. Sort by price (cheapest first)
        6. Return list of quotes with recommendation order

        Args:
            client_id: UUID of the client

        Returns:
            List of quote dictionaries sorted by premium (cheapest first)

        Raises:
            ValueError: If client not found or has no vehicles
        """
        # Load client
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found")

        # Load vehicles
        vehicles = self.db.query(ClientAutomobile).filter(
            ClientAutomobile.client_id == client_id
        ).all()

        if not vehicles:
            raise ValueError("Client has no vehicles")

        # Load all active premium policies for the client's company
        policies = self.db.query(PremiumPolicyType).filter(
            PremiumPolicyType.company_id == client.company_id,
            PremiumPolicyType.is_active == True
        ).all()

        # Build client data for matching
        client_age = None
        if client.date_of_birth:
            today = date.today()
            client_age = today.year - client.date_of_birth.year - (
                (today.month, today.day) < (client.date_of_birth.month, client.date_of_birth.day)
            )

        quotes = []

        for vehicle in vehicles:
            # Use the policy matching service which already handles criteria evaluation
            match_result = self.policy_service.match_eligible_policies(
                company_id=client.company_id,
                client_id=client.id,
                overrides={
                    'vehicle_details': {
                        'vehicle_year': vehicle.vehicle_year,
                        'vehicle_mileage': vehicle.vehicle_mileage,
                        'parked_location': getattr(vehicle, 'parked_location', None),
                    }
                }
            )

            if match_result.get('status') == 'success' and match_result.get('data'):
                for policy_obj in match_result['data']:
                    # match_eligible_policies returns PremiumPolicyType objects directly
                    premium = Decimal(str(policy_obj.price)) if policy_obj.price else Decimal('0')

                    quotes.append({
                        'policy_name': policy_obj.name,
                        'policy_id': str(policy_obj.id),
                        'premium': premium,
                        'excess': Decimal(str(policy_obj.excess)) if policy_obj.excess else Decimal('0'),
                        'vehicle_id': str(vehicle.id),
                        'auto_generated': True,
                        'company_id': str(client.company_id),
                        'client_id': str(client.id),
                        'recommendation_order': len(quotes) + 1,
                        'services': [s.name for s in (policy_obj.services or [])],
                    })

        # Sort by premium (cheapest first)
        quotes.sort(key=lambda x: x['premium'])

        # Update recommendation order after sorting
        for i, quote in enumerate(quotes, 1):
            quote['recommendation_order'] = i

        return quotes

    def get_quote_details(self, quote_id: UUID) -> Dict[str, Any]:
        """
        Get full details of a quote including coverage and benefits.

        Args:
            quote_id: UUID of the quote

        Returns:
            Dictionary with complete quote details

        Raises:
            ValueError: If quote not found
        """
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        # Build details from actual quote and policy data
        policy = quote.policy_type if hasattr(quote, 'policy_type') else None
        services = []
        if quote.included_services:
            services = quote.included_services if isinstance(quote.included_services, list) else []

        details = {
            'id': str(quote.id),
            'quote_number': quote.quote_number,
            'premium': float(quote.premium_amount) if quote.premium_amount else 0,
            'final_premium': float(quote.final_premium) if quote.final_premium else 0,
            'deductible': float(quote.excess) if quote.excess else 0,
            'tax_amount': float(quote.tax_amount) if quote.tax_amount else 0,
            'admin_fee': float(quote.admin_fee) if quote.admin_fee else 0,
            'discount_percent': float(quote.discount_percent) if quote.discount_percent else 0,
            'coverage_amount': float(quote.coverage_amount) if quote.coverage_amount else 0,
            'included_services': services,
            'status': quote.status,
            'calculation_breakdown': quote.calculation_breakdown or {},
        }

        if policy:
            details['policy_name'] = policy.name
            details['policy_description'] = policy.description

        return details

    def auto_generate_and_save(self, client_id: UUID) -> List[Quote]:
        """
        Auto-generate quotes and save them to the database.

        Args:
            client_id: UUID of the client

        Returns:
            List of created Quote objects

        Raises:
            ValueError: If client not found or has no vehicles
        """
        generated_quotes = self.auto_generate_quotes(client_id)
        saved_quotes = []

        # Get client for company_id
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found")

        for i, quote_data in enumerate(generated_quotes):
            # Generate unique quote number
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = random.randint(1000, 9999)
            quote_number = f"Q-AUTO-{timestamp}-{random_suffix}-{i}"

            premium = Decimal(str(quote_data['premium'])) if not isinstance(quote_data['premium'], Decimal) else quote_data['premium']
            excess = Decimal(str(quote_data.get('excess', 0)))

            quote = Quote(
                company_id=client.company_id,
                client_id=client_id,
                policy_type_id=UUID(quote_data['policy_id']),
                quote_number=quote_number,
                premium_amount=premium,
                final_premium=premium,
                coverage_amount=premium,
                excess=excess,
                included_services=quote_data.get('services', []),
                auto_generated=True,
                recommendation_order=quote_data.get('recommendation_order', i + 1),
                status='recommended'
            )
            self.db.add(quote)
            saved_quotes.append(quote)

        self.db.commit()
        for q in saved_quotes:
            self.db.refresh(q)
        return saved_quotes
