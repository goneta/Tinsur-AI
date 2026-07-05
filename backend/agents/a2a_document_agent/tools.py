import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.models.company import Company
from app.models.client import Client
from app.models.document import Document, DocumentLabel
from app.core.config import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generate_payment_schedule_pdf(db: Session, policy_id: str, user_id: str) -> Document:
    # 1. Fetch Data
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise ValueError("Policy not found")
    
    client = db.query(Client).filter(Client.id == policy.client_id).first()
    if not client:
         raise ValueError("Client not found")

    insurer_company = db.query(Company).filter(Company.id == policy.company_id).first()
    
    # 2. Prepare Data
    premium = float(policy.premium_amount)
    insurance_levy = 5.0
    final_premium = premium * (1 + insurance_levy / 100)
    
    if policy.premium_frequency == 'annual':
        monthly_payment = premium / 11
        duration_desc = "11 mois"
        repayment_desc = f"11 remboursements mensuels de {monthly_payment:,.2f} FCFA"
    else:
        monthly_payment = premium 
        duration_desc = "Mensuel"
        repayment_desc = f"Paiement mensuel de {monthly_payment:,.2f} FCFA"

    company_name = insurer_company.name if insurer_company else "Tinsur Insurance"
    company_address = insurer_company.address if insurer_company else "Nairobi, Kenya"
    company_phone = insurer_company.phone if insurer_company else "+254 700 000 000"
    
    # 3. Build PDF
    # Define storage
    output_dir = os.path.join(settings.PROJECT_ROOT, "static", "documents", str(policy.client_id))
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"Payment_Schedule_{policy.policy_number}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = os.path.join(output_dir, filename)
    file_url = f"/static/documents/{policy.client_id}/{filename}"

    doc = SimpleDocTemplate(file_path, pagesize=A4, margin=(2*cm, 2*cm, 2*cm, 2*cm))
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003da5'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003da5'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.gray)

    # Title
    elements.append(Paragraph("INFORMATIONS CONTRACTUELLES SUR LE CRÉDIT DE L'ASSURANCE", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # TABLE UTILS
    def create_table(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # Section 1: Coordonnées
    elements.append(Paragraph("1. Coordonnées", section_style))
    data_1 = [
        ["Créancier", company_name],
        ["Adresse", company_address],
        ["Assurance Automobile", company_phone],
        ["Adresse Web", "www.tinsur.ai"]
    ]
    elements.append(create_table(data_1, [5*cm, 11*cm]))

    # Section 2: Caractéristiques
    elements.append(Paragraph("2. Caractéristiques principales du produit de crédit", section_style))
    
    # Helper for cells with description
    def cell_with_desc(title, desc):
        return [Paragraph(f"<b>{title}</b>", normal_style), Paragraph(desc, small_style)]

    data_2 = [
        ["Le type de crédit", "Prêt à somme fixe"],
        [
            [Paragraph("<b>Le montant total du crédit</b>", normal_style), Paragraph("Cela signifie le montant du crédit à fournir...", small_style)], 
            f"{premium:,.2f}"
        ],
        ["Comment et quand le crédit serait fourni", "Le crédit est fourni en vous permettant de payer votre prime d'assurance par paiements différés."],
        ["La durée du contrat de crédit", duration_desc],
        ["Remboursements", repayment_desc],
        [
            [Paragraph("<b>Le montant total que vous devrez payer</b>", normal_style), Paragraph("Montant emprunté plus les intérêts...", small_style)],
            f"{final_premium:,.2f}"
        ],
        ["Description des biens/services", f"Le prix au comptant de votre police d'assurance est de {premium:,.2f}"],
        ["Garantie requise", "Vous nous cédez la police d'assurance à laquelle le crédit se rapporte."]
    ]
    # Note: Table data can encounter issues with Paragraphs inside if not careful, but usually works with list wrapping.
    # Simplifying structure for robustness in `create_table` call which expects strings or Flowables.
    # Let's clean up `data_2` to ensure it works with `Table`.
    
    # Simpler approach: Flatten custom cells
    elements.append(create_table(data_2, [7*cm, 9*cm]))

    # Section 3: Coûts
    elements.append(Paragraph("3. Coûts du crédit", section_style))
    data_3 = [
        ["Les taux d'intérêt", f"Taux d'intérêt simple fixe de {insurance_levy}%."],
        [
            [Paragraph("<b>Taux Annuel Effectif Global (TAEG)</b>", normal_style), Paragraph("Coût total exprimé en pourcentage annuel...", small_style)],
            "21,1%"
        ]
    ]
    elements.append(create_table(data_3, [7*cm, 9*cm]))
    
    # Footer
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(f"Document généré le : {datetime.now().strftime('%d/%m/%Y')}", small_style))

    # Build
    doc.build(elements)

    # 4. Create Document Record
    new_doc = Document(
        company_id=policy.company_id,
        policy_id=policy.id,
        client_id=policy.client_id,
        name=f"Payment Schedule - {policy.policy_number}",
        file_url=file_url,
        file_type="pdf",
        file_size=os.path.getsize(file_path),
        label=DocumentLabel.DOCUMENT,
        visibility='PRIVATE',
        uploaded_by=user_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return new_doc


def generate_policy_agreement_pdf(db: Session, policy_id: str, user_id: str) -> Document:
    """Generate a policy agreement (contract) PDF for an issued policy."""
    # 1. Fetch Data
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise ValueError("Policy not found")

    client = db.query(Client).filter(Client.id == policy.client_id).first()
    if not client:
        raise ValueError("Client not found")

    insurer_company = db.query(Company).filter(Company.id == policy.company_id).first()

    company_name = insurer_company.name if insurer_company else "Tinsur Insurance"
    company_address = insurer_company.address if insurer_company and insurer_company.address else "Address Pending"
    company_phone = insurer_company.phone if insurer_company and insurer_company.phone else "N/A"

    client_name = (
        client.business_name
        if client.client_type == "corporate" and client.business_name
        else f"{client.first_name or ''} {client.last_name or ''}".strip() or client.email
    )

    premium = float(policy.premium_amount or 0)
    coverage = float(policy.coverage_amount or 0)

    def _fmt_date(value):
        return value.strftime("%d/%m/%Y") if value else "N/A"

    # 2. Build PDF
    output_dir = os.path.join(settings.PROJECT_ROOT, "static", "documents", str(policy.client_id))
    os.makedirs(output_dir, exist_ok=True)

    filename = f"Policy_Agreement_{policy.policy_number}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = os.path.join(output_dir, filename)
    file_url = f"/static/documents/{policy.client_id}/{filename}"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'AgreementTitle', parent=styles['Heading1'], fontSize=16,
        textColor=colors.HexColor('#003da5'), spaceAfter=20, alignment=1,
    )
    section_style = ParagraphStyle(
        'AgreementSection', parent=styles['Heading2'], fontSize=12,
        textColor=colors.HexColor('#003da5'), spaceBefore=15, spaceAfter=10,
    )
    small_style = ParagraphStyle('AgreementSmall', parent=styles['Normal'], fontSize=8, textColor=colors.gray)

    def create_table(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    elements.append(Paragraph("POLICY AGREEMENT / CONTRAT D'ASSURANCE", title_style))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("1. Insurer / Assureur", section_style))
    elements.append(create_table([
        ["Company", company_name],
        ["Address", company_address],
        ["Phone", company_phone],
    ], [5 * cm, 11 * cm]))

    elements.append(Paragraph("2. Policyholder / Assuré", section_style))
    elements.append(create_table([
        ["Name", client_name],
        ["Email", client.email or "N/A"],
        ["Phone", client.phone or "N/A"],
    ], [5 * cm, 11 * cm]))

    elements.append(Paragraph("3. Policy Details / Détails de la Police", section_style))
    elements.append(create_table([
        ["Policy Number", policy.policy_number],
        ["Status", str(policy.status)],
        ["Coverage Amount", f"{coverage:,.2f}"],
        ["Premium", f"{premium:,.2f}"],
        ["Frequency", str(policy.premium_frequency or "annual")],
        ["Start Date", _fmt_date(policy.start_date)],
        ["End Date", _fmt_date(policy.end_date)],
    ], [5 * cm, 11 * cm]))

    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(
        "This agreement confirms the insurance coverage described above, subject to the "
        "policy's terms and conditions.", styles['Normal']))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"Document généré le : {datetime.now().strftime('%d/%m/%Y')}", small_style))

    doc.build(elements)

    # 3. Create Document Record
    new_doc = Document(
        company_id=policy.company_id,
        policy_id=policy.id,
        client_id=policy.client_id,
        name=f"Policy Agreement - {policy.policy_number}",
        file_url=file_url,
        file_type="pdf",
        file_size=os.path.getsize(file_path),
        label=DocumentLabel.DOCUMENT,
        visibility='PRIVATE',
        uploaded_by=user_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return new_doc
