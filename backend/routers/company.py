from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.services.impl.company import CompanyService
from backend.utils.util import get_language

router = APIRouter()

company_service = CompanyService()


@router.get("/search", response_model=List[schemas.CompanyAutocompleteSchema])
def autocomplete_company(
        query: str = Query(..., min_length=1),
        db: Session = Depends(get_db),
        lang: str = Depends(get_language)
):
    return company_service.autocomplete_company(db, query, lang)


@router.get("/companies/{company_name}", response_model=schemas.CompanyResponseSchema)
def get_company(company_name: str, db: Session = Depends(get_db), lang: str = Depends(get_language)):
    result = company_service.get_company(db, company_name, lang)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return result


@router.post("/companies", response_model=schemas.CompanyResponseSchema, status_code=status.HTTP_201_CREATED)
def create_company(company: schemas.CompanyCreateSchema, db: Session = Depends(get_db),
                   lang: str = Depends(get_language)):
    result = company_service.create_company(db, company, lang)
    if result is None:
        raise HTTPException(status_code=400, detail="Company already exists")
    return result


@router.get("/tags", response_model=List[schemas.TagSearchResponseSchema])
def search_by_tag(query: str, db: Session = Depends(get_db), lang: str = Depends(get_language)):
    return company_service.search_by_tag(db, query, lang)


@router.put("/companies/{company_name}/tags", response_model=schemas.CompanyResponseSchema)
def add_tags_to_company(company_name: str, tags: List[schemas.TagCreateSchema], db: Session = Depends(get_db),
                        lang: str = Depends(get_language)):
    result = company_service.add_tags_to_company(db, company_name, tags, lang)
    if result is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return result


@router.delete("/companies/{company_name}/tags/{tag_name}", response_model=schemas.CompanyResponseSchema)
def delete_tag_from_company(company_name: str, tag_name: str, db: Session = Depends(get_db),
                            lang: str = Depends(get_language)):
    result = company_service.delete_tag_from_company(db, company_name, tag_name, lang)
    if result is None:
        raise HTTPException(status_code=404, detail="Company or Tag not found")
    return result
