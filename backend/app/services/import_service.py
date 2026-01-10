"""
Import Service for processing data from various file formats.
"""
import csv
import json
import io
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import openpyxl
from pypdf import PdfReader
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.client import Client
from app.models.employee import EmployeeProfile
from app.models.user import User
from app.models.policy import Policy

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def parse_file(self, content: bytes, file_format: str) -> List[Dict[str, Any]]:
        """
        Parse file content based on format.
        """
        file_format = file_format.lower()
        if file_format == 'csv':
            return self._parse_csv(content)
        elif file_format == 'json':
            return self._parse_json(content)
        elif file_format in ['xls', 'xlsx']:
            return self._parse_excel(content)
        elif file_format == 'xml':
            return self._parse_xml(content)
        elif file_format == 'pdf':
            return self._parse_pdf(content)
        elif file_format == 'markdown' or file_format == 'md':
            return self._parse_markdown(content)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _parse_csv(self, content: bytes) -> List[Dict[str, Any]]:
        text = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        return [row for row in reader]

    def _parse_json(self, content: bytes) -> List[Dict[str, Any]]:
        data = json.loads(content.decode('utf-8'))
        if isinstance(data, list):
            return data
        return [data]

    def _parse_excel(self, content: bytes) -> List[Dict[str, Any]]:
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(dict(zip(headers, row)))
        return data

    def _parse_xml(self, content: bytes) -> List[Dict[str, Any]]:
        root = ET.fromstring(content)
        data = []
        for item in root:
            row = {}
            for child in item:
                row[child.tag] = child.text
            data.append(row)
        return data

    def _parse_pdf(self, content: bytes) -> List[Dict[str, Any]]:
        """
        Basic PDF text extraction. Returns lines as potential records or attempts to find tables.
        This is a heuristic implementation.
        """
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Simple heuristic: Split by lines and try to find tab-separated or comma-separated values
        # or just return each line as a 'raw_content' field if it looks meaningful
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return [{"raw_content": line} for line in lines]

    def _parse_markdown(self, content: bytes) -> List[Dict[str, Any]]:
        """
        Parse Markdown tables.
        """
        text = content.decode('utf-8')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        table_rows = []
        for line in lines:
            if line.startswith('|') and '|' in line[1:]:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if all(p == '---' or p == ':---' or p == '---:' or p == ':---:' for p in parts):
                    continue # Skip separator line
                table_rows.append(parts)
        
        if not table_rows:
            return []
            
        headers = table_rows[0]
        data = []
        for row in table_rows[1:]:
            if len(row) == len(headers):
                data.append(dict(zip(headers, row)))
        return data

    def find_duplicates(self, data_type: str, records: List[Dict[str, Any]], company_id: str) -> List[Dict[str, Any]]:
        """
        Check for duplicates in the database.
        Returns a list of tuples (imported_record, matching_existing_record).
        """
        duplicates = []
        if data_type == 'clients':
            for record in records:
                match = self._find_client_match(record, company_id)
                if match:
                    duplicates.append({
                        "imported": record,
                        "existing": {
                            "id": str(match.id),
                            "name": match.display_name,
                            "email": match.email,
                            "phone": match.phone,
                            "date_of_birth": str(match.date_of_birth) if match.date_of_birth else None,
                            "address": match.address
                        },
                        "matching_fields": self._get_matching_fields(record, match, ['first_name', 'last_name', 'phone', 'date_of_birth', 'address'])
                    })
        elif data_type == 'employees':
            for record in records:
                match = self._find_employee_match(record, company_id)
                if match:
                    duplicates.append({
                        "imported": record,
                        "existing": {
                            "id": str(match.id),
                            "name": match.full_name,
                            "email": match.email,
                            "phone": match.phone
                        },
                        "matching_fields": self._get_matching_fields(record, match, ['first_name', 'last_name', 'phone', 'email'])
                    })
        elif data_type == 'policies':
             for record in records:
                match = self._find_policy_match(record, company_id)
                if match:
                    duplicates.append({
                        "imported": record,
                        "existing": {
                            "id": str(match.id),
                            "policy_number": match.policy_number
                        },
                        "matching_fields": ['policy_number']
                    })
                    
        return duplicates

    def _find_client_match(self, record: Dict[str, Any], company_id: str) -> Optional[Client]:
        # Keys: Name, DOB, Address, Phone
        # We need to map the imported keys to our model keys
        # For simplicity, we assume they are already mapped or we use a fallback
        first_name = record.get('first_name')
        last_name = record.get('last_name')
        phone = record.get('phone')
        dob = record.get('date_of_birth')
        
        query = self.db.query(Client).filter(Client.company_id == company_id)
        
        filters = []
        if first_name and last_name:
            filters.append(and_(Client.first_name == first_name, Client.last_name == last_name))
        if phone:
            filters.append(Client.phone == phone)
        if dob:
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    dob = None
            if dob:
                filters.append(Client.date_of_birth == dob)
        
        if not filters:
            return None
            
        return query.filter(or_(*filters)).first()

    def _find_employee_match(self, record: Dict[str, Any], company_id: str) -> Optional[User]:
        email = record.get('email')
        phone = record.get('phone')
        
        query = self.db.query(User).filter(User.company_id == company_id, User.role != 'client')
        
        filters = []
        if email:
            filters.append(User.email == email)
        if phone:
            filters.append(User.phone == phone)
            
        if not filters:
            return None
            
        return query.filter(or_(*filters)).first()

    def _find_policy_match(self, record: Dict[str, Any], company_id: str) -> Optional[Policy]:
        policy_number = record.get('policy_number')
        if not policy_number:
            return None
        return self.db.query(Policy).filter(Policy.company_id == company_id, Policy.policy_number == policy_number).first()

    def _get_matching_fields(self, imported: Dict[str, Any], existing: Any, fields: List[str]) -> List[str]:
        matches = []
        for f in fields:
            imp_val = imported.get(f)
            ext_val = getattr(existing, f, None)
            
            # Normalize for comparison
            if isinstance(ext_val, (date, datetime)):
                ext_val = str(ext_val)
            if imp_val and ext_val and str(imp_val).strip().lower() == str(ext_val).strip().lower():
                matches.append(f)
        return matches
