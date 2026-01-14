from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core import dependencies as deps
from app.models.translation import Translation
from app.schemas.translation import TranslationCreate, TranslationUpdate, TranslationResponse

router = APIRouter()

@router.get("/", response_model=Dict[str, Dict[str, str]])
def get_translations(
    db: Session = Depends(deps.get_db),
    language_code: str = Query(None, description="Filter by specific language code")
) -> Any:
    """
    Retrieve all translations, grouped by language code and key.
    Format: { "en": { "key1": "val1" }, "fr": { "key1": "val2" } }
    """
    query = db.query(Translation).filter(Translation.is_active == True)
    if language_code:
        query = query.filter(Translation.language_code == language_code)
    
    translations = query.all()
    
    result = {}
    for t in translations:
        if t.language_code not in result:
            result[t.language_code] = {}
        result[t.language_code][t.key] = t.value
        
    return result

@router.get("/list", response_model=List[TranslationResponse])
def list_translations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    language_code: str = Query(None)
) -> Any:
    """
    Retrieve raw list of translations (for admin table).
    """
    query = db.query(Translation)
    if language_code:
        query = query.filter(Translation.language_code == language_code)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=TranslationResponse)
def create_translation(
    *,
    db: Session = Depends(deps.get_db),
    translation_in: TranslationCreate,
) -> Any:
    """
    Create new translation.
    """
    existing = db.query(Translation).filter(
        Translation.key == translation_in.key,
        Translation.language_code == translation_in.language_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The translation with this key and language already exists in the system.",
        )
        
    translation = Translation(
        key=translation_in.key,
        language_code=translation_in.language_code,
        value=translation_in.value,
        group=translation_in.group,
        is_active=translation_in.is_active,
    )
    db.add(translation)
    db.commit()
    db.refresh(translation)
    return translation

@router.put("/{id}", response_model=TranslationResponse)
def update_translation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    translation_in: TranslationUpdate,
) -> Any:
    """
    Update a translation.
    """
    translation = db.query(Translation).filter(Translation.id == id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
        
    update_data = translation_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(translation, field, value)
        
    db.add(translation)
    db.commit()
    db.refresh(translation)
    return translation
