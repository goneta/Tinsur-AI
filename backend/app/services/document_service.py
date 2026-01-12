import os
import qrcode
import base64
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings
from app.models.policy import Policy
from app.models.company import Company
from app.models.client import Client

class DocumentService:
    def __init__(self):
        # Setup Jinja2 environment for templates
        template_dir = os.path.join(os.getcwd(), 'app', 'templates', 'documents')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.output_dir = os.path.join(os.getcwd(), 'static', 'documents')
        os.makedirs(self.output_dir, exist_ok=True)

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

    def _format_currency(self, amount: float, currency: str = "GBP") -> str:
        # TODO: Get proper currency symbol from admin settings
        symbol = "£" if currency == "GBP" else "$" if currency == "USD" else "€"
        return f"{symbol}{amount:,.2f}"

    def _inject_header(self, html_content: str, policy: Policy, client_name: str, company_name: str, qr_data: str) -> str:
        """Injects standarized header with Logo, Title, and QR Code."""
        # Simple string injection after <body> tag or at the top if body not found
        # This assumes templates are roughly standard HTML. 
        # For a more robust solution, we might want to use BeautifulSoup or similar, 
        # but string manipulation is faster and sufficient if templates are controlled.
        
        qr_base64 = self._generate_qr_code(qr_data)
        
        header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px;">
            <div style="flex: 1;">
                <div style="font-size: 24px; font-weight: bold; color: #00539F; margin-bottom: 10px;">{company_name}</div>
                <div style="font-size: 18px; font-weight: bold; color: #333;">Insurance Policy Document</div>
            </div>
            <div style="text-align: right;">
                <img src="data:image/png;base64,{qr_base64}" alt="QR Code" style="width: 100px; height: 100px;" />
                <div style="font-size: 10px; color: #666; margin-top: 5px;">Ref: {policy.policy_number}</div>
            </div>
        </div>
        """
        
        if "<body" in html_content:
            # Inject after the opening body tag
            # Find the index of the closing angle bracket of <body>
            import re
            match = re.search(r"<body[^>]*>", html_content)
            if match:
                end_index = match.end()
                return html_content[:end_index] + header_html + html_content[end_index:]
        
        # Fallback: Prepend to content
        return header_html + html_content

    def generate_documents(self, policy: Policy, client: Client, company: Company) -> List[str]:
        """
        Generates all insurance documents for a given policy.
        Returns a list of generated file paths (relative to static/documents).
        """
        policy_dir = os.path.join(self.output_dir, str(policy.id))
        os.makedirs(policy_dir, exist_ok=True)
        
        generated_files = []
        
        # Mapping for placeholders
        data_mapping = {
            "nom_client": client.display_name,
            "adresse_client": getattr(client, "address", "Address Not Provided"), # Assuming address field exists
            "compagnie_dassurance": company.name,
            "compagnie_adresse": getattr(company, "address", "Company Address"),
            "compagnie_website": getattr(company, "website", "www.tinsur.ai"),
            "compagnie_telephone": getattr(company, "phone", "Contact Support"),
            "numero_police": policy.policy_number,
            "date_debut": policy.start_date.strftime("%d/%m/%Y"),
            "date_fin": policy.end_date.strftime("%d/%m/%Y"),
            "prime_totale": self._format_currency(policy.premium_amount),
            # Vehicle details - assuming single vehicle per policy for now, passed via details or separate query
            # For this implementation, we check policy.details which often contains vehicle info
            "marque": policy.details.get("vehicle", {}).get("make", "N/A") if policy.details else "N/A",
            "modele": policy.details.get("vehicle", {}).get("model", "N/A") if policy.details else "N/A",
            "immatriculation": policy.details.get("vehicle", {}).get("registrationNumber", "N/A") if policy.details else "N/A",
        }
        
        # QR Data content
        qr_content = f"Policy: {policy.policy_number}\nClient: {client.display_name}\nCompany: {company.name}"

        # Iterate through all templates
        for template_name in self.env.list_templates():
            if not template_name.endswith(".html"):
                continue
                
            template = self.env.get_template(template_name)
            
            # Simple render doesn't work well with custom < > placeholders if they aren't Jinja2 syntax {{ }}
            # So we load source, do string replacement for legacy placeholders, then inject header
            
            # 1. Read raw template content
            with open(os.path.join(self.env.loader.searchpath[0], template_name), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 2. Replace placeholders
            for key, value in data_mapping.items():
                content = content.replace(f"<{key}>", str(value))
                
            # 3. Inject Header
            final_content = self._inject_header(content, policy, client.display_name, company.name, qr_content)
            
            # 4. Save file
            # Generate a cleaner filename
            output_filename = f"{template_name.replace('_template.html', '').replace('.html', '')}_{policy.policy_number}.html"
            output_path = os.path.join(policy_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            generated_files.append(f"documents/{policy.id}/{output_filename}") # Relative path for API
            
        return generated_files

document_service = DocumentService()
