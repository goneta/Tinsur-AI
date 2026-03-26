import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.user import User
from app.services.ai_service import AiService
from app.models.system_settings import SystemSettings
import uuid

def test_ai_service_key_hierarchy(db_session: Session, test_company: Company):
    service = AiService(db_session)
    
    # Ensure test_company has correct initial plan
    test_company.ai_plan = "CREDIT"
    test_company.ai_credits_balance = 10.0
    db_session.commit()

    # 1. System Global
    db_session.query(SystemSettings).filter(SystemSettings.key == "AI_CONFIG").delete()
    db_session.add(SystemSettings(key="AI_CONFIG", value={"google_api_key": "system-key"}))
    db_session.commit()
    
    key, plan, can_use = service.get_effective_ai_config(str(test_company.id))
    assert key == "system-key"
    assert plan == "CREDIT"
    assert can_use is True

    # 2. Company BYOK (Overwrites System)
    test_company.ai_plan = "BYOK"
    test_company.ai_api_key_encrypted = service.encrypt_key("company-key")
    db_session.commit()
    
    key, plan, can_use = service.get_effective_ai_config(str(test_company.id))
    assert key == "company-key"
    assert plan == "BYOK"

    # 3. Credit Exhaustion
    test_company.ai_plan = "CREDIT"
    test_company.ai_credits_balance = 0
    db_session.commit()
    
    key, plan, can_use = service.get_effective_ai_config(str(test_company.id))
    assert can_use is False
    assert plan == "CREDIT"

def test_ai_service_key_hierarchy_no_company(db_session: Session):
    service = AiService(db_session)
    
    # 1. System Global
    db_session.query(SystemSettings).filter(SystemSettings.key == "AI_CONFIG").delete()
    db_session.add(SystemSettings(key="AI_CONFIG", value={"google_api_key": "global-admin-key"}))
    db_session.commit()
    
    key, plan, can_use = service.get_effective_ai_config(None)
    assert key == "global-admin-key"
    assert plan == "CREDIT"
    assert can_use is True

def test_ai_usage_logging(db_session: Session, test_company: Company):
    service = AiService(db_session)
    test_company.ai_plan = "CREDIT"
    test_company.ai_credits_balance = 10.0
    db_session.commit()
    
    initial_balance = test_company.ai_credits_balance
    
    user_id = uuid.uuid4()
    service.log_and_consume_usage(str(test_company.id), str(user_id), "test_agent")
    
    db_session.refresh(test_company)
    assert test_company.ai_credits_balance < initial_balance
    
    # Check log entry
    from app.models.system_settings import AiUsageLog
    log = db_session.query(AiUsageLog).filter(AiUsageLog.company_id == test_company.id).first()
    assert log is not None
    assert log.agent_name == "test_agent"
