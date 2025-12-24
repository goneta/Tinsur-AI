from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.ml_model import MLModel
import uuid

@tool
def list_active_models(company_id: str) -> str:
    """
    Lists all deployed machine learning models, their type, and accuracy for the company.
    Args:
        company_id: The UUID of the company.
    """
    db = SessionLocal()
    try:
        models = db.query(MLModel).filter(
            MLModel.company_id == uuid.UUID(company_id),
            MLModel.is_active == True
        ).all()
        if not models:
            return f"No active ML models found for company {company_id}."
            
        lines = [f"- {m.model_name} ({m.model_type}): Version {m.model_version}, Accuracy: {float(m.accuracy or 0)*100:.2f}%" for m in models]
        return "Active ML Models:\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing ML models: {str(e)}"
    finally:
        db.close()

@tool
def get_model_insight(company_id: str, model_name: str) -> str:
    """
    Provides specific deployment details and performance insights for a named ML model.
    Args:
        company_id: The UUID of the company.
        model_name: Exact name of the model.
    """
    db = SessionLocal()
    try:
        model = db.query(MLModel).filter(
            MLModel.company_id == uuid.UUID(company_id),
            MLModel.model_name == model_name
        ).first()
        if not model:
            return f"Model '{model_name}' not found for company {company_id}."
            
        return (f"ML Model Insight: {model.model_name}\n"
                f"- Type: {model.model_type}\n"
                f"- Version: {model.model_version}\n"
                f"- Accuracy: {float(model.accuracy or 0)*100:.2f}%\n"
                f"- Deployed at: {model.deployed_at.strftime('%Y-%m-%d %H:%M') if model.deployed_at else 'Unknown'}\n"
                f"- Active: {model.is_active}")
    except Exception as e:
        return f"Error retrieving model insight: {str(e)}"
    finally:
        db.close()
