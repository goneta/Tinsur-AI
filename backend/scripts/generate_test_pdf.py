from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/knowledge_base"))
    os.makedirs(kb_dir, exist_ok=True)
    file_path = os.path.join(kb_dir, "test_policy.pdf")
    
    print(f"📄 Generating test PDF: {file_path}")
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Tinsur.AI - Vintage Car Special Clause")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "This clause applies to vehicles older than 25 years.")
    c.drawString(100, 700, "Modifications: All engine modifications must be reported.")
    c.drawString(100, 680, "Storage: The vehicle must be stored in a locked garage.")
    
    c.showPage()
    
    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Claims Procedure for Vintage Cars")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "1. Take 10 photos of the damage from all angles.")
    c.drawString(100, 700, "2. Provide a specialized appraisal report.")
    c.drawString(100, 680, "3. Submit everything via the Tinsur.AI app.")
    
    c.save()
    print("✅ Test PDF generated.")

if __name__ == "__main__":
    create_test_pdf()
