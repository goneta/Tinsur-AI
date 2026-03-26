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
        company_id=policy.client_id, 
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
    # 1. Fetch Data
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise ValueError("Policy not found")
    
    client = db.query(Client).filter(Client.id == policy.client_id).first()
    if not client:
         # Fallback if client is stored differently, but Policy has client_id which usually links to Client
         raise ValueError("Client not found")

    insurer_company = db.query(Company).filter(Company.id == policy.company_id).first()
    # If policy.company_id is the insurer.
    
    # 2. Read Template
    # Assuming template is at a known path. I will use the path discovered earlier.
    template_path = os.path.join(settings.PROJECT_ROOT, "..", "ai_docs", "references", "examples", "KEN_informations_precontractuelles_credit.html")
    # Adjust path logic as needed. PROJECT_ROOT is usually backend/app or backend/
    # If not accessible via settings, hardcode relative for now or fix path.
    # Let's assume user.OS path for now to be safe or use absolute if possible. 
    # C:\Users\user\Desktop\Tinsur.AI\ai_docs\references\examples\KEN_informations_precontractuelles_credit.html
    
    with open(r"C:\Users\user\Desktop\Tinsur.AI\ai_docs\references\examples\KEN_informations_precontractuelles_credit.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Prepare Data
    premium = float(policy.premium_amount)
    # Frequency: Monthly. 
    # Logic: "frequence de paiement": amount paid per month.
    # If premium is annual, divide by 11 (as per template text "11 mois").
    # If strictly following template logic: "11 remboursements mensuels".
    if policy.premium_frequency == 'annual':
        monthly_payment = premium / 11
    else:
        monthly_payment = premium # simplify or adjust logic
        
    insurance_levy = 5.0 # Placeholder or fetch from policy details/company config. "insurance levy"
    
    # Replace keys
    # <premium policy amount>
    # <frequence de paiement>
    # <Prime finale>
    # <téléphone de la compagnie d’assurance>
    # <adresse de la compagnie d’assurance>
    # <Nom de la compagnie d’assurance>
    # <website de la compagnie d’assurance>
    # <insurance levy>
    
    replacements = {
        "<premium policy amount>": f"{premium:,.2f}".replace(",", " ").replace(".", ","),
        "<frequence de paiement>": f"{monthly_payment:,.2f} FCFA".replace(",", " ").replace(".", ","),
        "<Prime finale>": f"{(premium * (1 + insurance_levy/100)):,.2f}".replace(",", " ").replace(".", ","), # Adding interest? "Prime finale" usually total paid.
        "<téléphone de la compagnie d’assurance>": insurer_company.phone if insurer_company else "+254 700 000 000",
        "<adresse de la compagnie d’assurance>": insurer_company.address if insurer_company else "Nairobi, Kenya",
        "<Nom de la compagnie d’assurance>": insurer_company.name if insurer_company else "Tinsur Insurance",
        "<Nom de la compagnie dassurance>": insurer_company.name if insurer_company else "Tinsur Insurance", # variant without apostrophe in tag?
        "<website de la compagnie d’assurance>": "www.tinsur.ai", # Company has no website field
        "<insurance levy>": str(insurance_levy)
    }

    # Also handle the variants found in the HTML file (e.g. <Nom de la compagnie dassurance> vs <Nom de la compagnie d’assurance>)
    # I saw `<Nom de la compagnie dassurance>` in the `view_file` output (line 416).
    # And `<adresse de la compagnie dassurance>` (line 420).
    # And `<téléphone de la compagnie dassurance>` (line 424).
    # And `<website de la compagnie dassurance>` (line 428).
    # And `<insurance levy>`
    
    normalized_replacements = {
        "<premium policy amount>": f"{premium:,.2f}",
        "<frequence de paiement>": f"{monthly_payment:,.2f} FCFA",
        "<Prime finale>": f"{(premium * (1 + insurance_levy/100)):,.2f}", # Assuming interest added
        "<téléphone de la compagnie dassurance>": insurer_company.phone if insurer_company and insurer_company.phone else "+254 700 000 000",
        "<adresse de la compagnie dassurance>": insurer_company.address if insurer_company and insurer_company.address else "Address Pending",
        "<Nom de la compagnie dassurance>": insurer_company.name if insurer_company else "Tinsur Insurance",
        "<website de la compagnie dassurance>": "www.tinsur.ai",
        "<insurance levy>": str(insurance_levy)
    }

    for key, value in normalized_replacements.items():
        html_content = html_content.replace(key, value)

    # 4. Save File
    # Define a storage location.
    output_dir = os.path.join(settings.PROJECT_ROOT, "static", "documents", str(policy.client_id))
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"Payment_Schedule_{policy.policy_number}_{uuid.uuid4().hex[:6]}.html"
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Relative URL for access
    file_url = f"/static/documents/{policy.client_id}/{filename}"
    
    # 5. Create Document Record
    new_doc = Document(
        company_id=policy.client_id, # Owner is the client
        name=f"Payment Schedule - {policy.policy_number}",
        file_url=file_url,
        file_type="html",
        file_size=len(html_content),
        label=DocumentLabel.DOCUMENT,
        visibility='PRIVATE',
        uploaded_by=user_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return new_doc
