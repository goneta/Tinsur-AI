from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.translation import Translation
from app.schemas.translation import TranslationCreate, TranslationUpdate, TranslationResponse, TranslationMap

router = APIRouter()

@router.get("/keys/all", response_model=List[TranslationResponse])
def get_all_translations(
    skip: int = 0,
    limit: int = 100,
    lang: str = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all translation records (for admin management).
    """
    query = db.query(Translation)
    if lang:
        query = query.filter(Translation.language_code == lang)
    return query.offset(skip).limit(limit).all()

@router.get("/{lang}", response_model=TranslationMap)
def get_translations(lang: str, db: Session = Depends(get_db)) -> Any:
    """
    Get all translations for a specific language as a key-value map.
    """
    translations = db.query(Translation).filter(
        Translation.language_code == lang,
        Translation.is_active == True
    ).all()
    return {t.key: t.value for t in translations}
    """
    Get all translation records (for admin management).
    """
    query = db.query(Translation)
    if lang:
        query = query.filter(Translation.language_code == lang)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=TranslationResponse)
def create_translation(
    translation_in: TranslationCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new translation.
    """
    existing = db.query(Translation).filter(
        Translation.key == translation_in.key,
        Translation.language_code == translation_in.language_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Translation for this key and language already exists"
        )
    
    translation = Translation(**translation_in.dict())
    db.add(translation)
    db.commit()
    db.refresh(translation)
    return translation

@router.put("/{translation_id}", response_model=TranslationResponse)
def update_translation(
    translation_id: int,
    translation_in: TranslationUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a translation.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    if translation_in.value is not None:
        translation.value = translation_in.value
    if translation_in.is_active is not None:
        translation.is_active = translation_in.is_active
        
    db.commit()
    db.refresh(translation)
    return translation
