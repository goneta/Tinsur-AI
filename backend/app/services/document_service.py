import os
import re
import json
import html
import qrcode
import base64
import secrets
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from app.core.config import settings
from app.core.time import utcnow
from app.models.policy import Policy
from app.models.company import Company
from app.models.client import Client
from app.models.document import Document, DocumentLabel
from app.models.document_template import DocumentTemplate


class DocumentService:
    def __init__(self):
        project_root = Path(settings.PROJECT_ROOT).resolve().parent
        self.template_source_dir = project_root / "ai_docs" / "references" / "examples" / "insurance_docs" / "docs"
        self.output_dir = project_root / "static" / "documents"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._html_tags = {
            "html", "head", "body", "title", "style", "script", "div", "span", "p", "h1", "h2", "h3", "h4",
            "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "strong", "em", "small", "br"
        }

    def _generate_qr_code(self, data: str) -> str:
        """Generates a QR code and returns it as a base64 encoded string."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def _generate_qr_png_bytes(self, data: str) -> bytes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered.getvalue()

    def _generate_verification_code(self) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def _format_currency(self, amount: float, currency: str = "GBP") -> str:
        symbol = "Â£" if currency == "GBP" else "$" if currency == "USD" else "â‚¬"
        return f"{symbol}{amount:,.2f}"

    def _extract_placeholders(self, html_content: str) -> List[str]:
        raw = set(re.findall(r"<([a-zA-Z0-9_]+)>", html_content))
        return sorted(tag for tag in raw if tag not in self._html_tags)

    def _build_data_mapping(
        self,
        policy: Policy,
        client: Client,
        company: Company,
        vehicle: Optional[dict],
    ) -> Dict[str, Any]:
        vehicle_data = vehicle or {}
        return {
            "nom_client": client.display_name,
            "adresse_client": getattr(client, "address", "Address Not Provided"),
            "email_client": getattr(client, "email", ""),
            "telephone_client": getattr(client, "phone", ""),
            "compagnie_dassurance": company.name,
            "compagnie_logo": getattr(company, "logo_url", ""),
            "compagnie_couleur_primaire": getattr(company, "primary_color", "#00539F"),
            "compagnie_couleur_secondaire": getattr(company, "secondary_color", "#333333"),
            "compagnie_adresse": getattr(company, "address", "Company Address"),
            "compagnie_website": getattr(company, "website", "www.tinsur.ai"),
            "compagnie_telephone": getattr(company, "phone", "Contact Support"),
            "numero_police": policy.policy_number,
            "date_debut": policy.start_date.strftime("%d/%m/%Y") if policy.start_date else "",
            "date_fin": policy.end_date.strftime("%d/%m/%Y") if policy.end_date else "",
            "prime_totale": self._format_currency(float(policy.premium_amount or 0)),
            "montant_couverture": self._format_currency(float(policy.coverage_amount or 0)),
            "type_assurance": policy.policy_type.name if policy.policy_type else "General",
            "marque": vehicle_data.get("make", "N/A"),
            "modele": vehicle_data.get("model", "N/A"),
            "immatriculation": vehicle_data.get("registration", vehicle_data.get("registrationNumber", "N/A")),
            "numero_vehicule": vehicle_data.get("vin", ""),
        }

    def _html_to_text(self, html_content: str) -> str:
        cleaned = re.sub(r"<(script|style)[^>]*>.*?</\\1>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<br\\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</li>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = html.unescape(cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _render_pdf(
        self,
        html_content: str,
        output_path: Path,
        company: Company,
        client: Client,
        verification_code: str,
        qr_payload: str,
    ) -> None:
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(company.name, styles["Title"]))
        story.append(Paragraph(f"Client: {client.display_name}", styles["Normal"]))
        story.append(Paragraph(f"Verification Code: {verification_code}", styles["Normal"]))
        story.append(Spacer(1, 12))

        qr_bytes = self._generate_qr_png_bytes(qr_payload)
        qr_img = Image(BytesIO(qr_bytes), width=120, height=120)
        story.append(qr_img)
        story.append(Spacer(1, 16))

        text = self._html_to_text(html_content)
        for paragraph in text.split("\n\n"):
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 8))

        doc.build(story)

    def _load_templates_from_files(self) -> List[Dict[str, Any]]:
        if not self.template_source_dir.exists():
            return []

        templates = []
        for file_path in sorted(self.template_source_dir.glob("*.html")):
            content = file_path.read_text(encoding="utf-8")
            placeholders = self._extract_placeholders(content)
            templates.append({
                "code": file_path.stem.lower(),
                "name": file_path.stem.replace("_", " "),
                "description": None,
                "language": "fr",
                "template_html": content,
                "placeholders": placeholders,
                "source_path": str(file_path),
            })
        return templates

    def _ensure_templates_loaded(self, db) -> None:
        templates = self._load_templates_from_files()
        if not templates:
            return

        for tmpl in templates:
            existing = db.query(DocumentTemplate).filter(DocumentTemplate.code == tmpl["code"]).first()
            if existing:
                existing.name = tmpl["name"]
                existing.description = tmpl["description"]
                existing.language = tmpl["language"]
                existing.template_html = tmpl["template_html"]
                existing.placeholders = tmpl["placeholders"]
                existing.source_path = tmpl["source_path"]
            else:
                db.add(DocumentTemplate(**tmpl))
        db.commit()

    def _get_policy_vehicle(self, policy: Policy, client: Client) -> dict:
        if policy.details and isinstance(policy.details, dict):
            vehicle = policy.details.get("vehicle") or {}
            if vehicle:
                return {
                    "make": vehicle.get("make"),
                    "model": vehicle.get("model"),
                    "registrationNumber": vehicle.get("registrationNumber"),
                    "vin": vehicle.get("vin"),
                }
        if client.automobile_details:
            auto = client.automobile_details[0]
            return {
                "make": getattr(auto, "vehicle_make", None),
                "model": getattr(auto, "vehicle_model", None),
                "registration": getattr(auto, "vehicle_registration", None),
                "vin": getattr(auto, "vehicle_vin", None),
            }
        return {}

    def _generate_unique_code(self, db) -> str:
        code = self._generate_verification_code()
        while db.query(Document).filter(Document.verification_code == code).first():
            code = self._generate_verification_code()
        return code

    def generate_documents(self, db, policy: Policy, client: Client, company: Company) -> List[str]:
        """
        Generates all insurance documents for a given policy.
        Returns a list of generated file paths (relative to static/documents).
        """
        self._ensure_templates_loaded(db)

        policy_dir = self.output_dir / str(policy.id)
        policy_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        vehicle = self._get_policy_vehicle(policy, client)
        data_mapping = self._build_data_mapping(policy, client, company, vehicle)

        templates = db.query(DocumentTemplate).order_by(DocumentTemplate.created_at.asc()).all()
        for template in templates:
            content = template.template_html
            placeholders = template.placeholders or self._extract_placeholders(content)
            for key, value in data_mapping.items():
                content = content.replace(f"<{key}>", str(value))

            verification_code = self._generate_unique_code(db)
            now = utcnow()
            doc_specific_mapping = {
                "reference_document_interne": verification_code,
                "reference_document_produit": verification_code,
                "reference_template_document": template.code,
                "reference_document_version": "v1",
                "date_emission_document": now.strftime("%d/%m/%Y"),
                "horodatage_emission_document": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date_impression": now.strftime("%d/%m/%Y"),
                "heure_impression": now.strftime("%H:%M"),
                "numero_enregistrement_compagnie": getattr(company, "system_registration_number", "") or "",
                "numero_enregistrement_siege_social": getattr(company, "system_registration_number", "") or "",
                "numero_enregistrement_siege": getattr(company, "system_registration_number", "") or "",
                "reference_client": str(client.id),
                "reference_client_complete": str(client.id),
                "type_police": data_mapping.get("type_assurance", ""),
                "type_police_description": data_mapping.get("type_assurance", ""),
            }
            for key, value in doc_specific_mapping.items():
                content = content.replace(f"<{key}>", str(value))

            for placeholder in placeholders:
                if placeholder not in data_mapping and placeholder not in doc_specific_mapping:
                    content = content.replace(f"<{placeholder}>", "")

            qr_payload = json.dumps({
                "company_id": str(company.id),
                "company_name": company.name,
                "client_id": str(client.id),
                "client_name": client.display_name,
                "insurance_type": data_mapping.get("type_assurance"),
                "policy_number": policy.policy_number,
                "verification_code": verification_code,
                "platform_reference": settings.APP_NAME,
                "verification_url": f"/verify/document/{verification_code}",
            })

            output_filename = f"{template.code}_{policy.policy_number}.pdf"
            output_path = policy_dir / output_filename
            self._render_pdf(content, output_path, company, client, verification_code, qr_payload)

            file_url = f"documents/{policy.id}/{output_filename}"
            file_size = output_path.stat().st_size if output_path.exists() else 0

            db_doc = Document(
                company_id=company.id,
                policy_id=policy.id,
                client_id=client.id,
                template_id=template.id,
                uploaded_by=policy.created_by,
                name=output_filename,
                file_url=file_url,
                file_type="pdf",
                file_size=file_size,
                label=DocumentLabel.POLICY,
                visibility="PRIVATE",
                scope="B2C",
                verification_code=verification_code,
                qr_payload=qr_payload,
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            generated_files.append(file_url)

        return generated_files


document_service = DocumentService()
