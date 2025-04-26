from typing import List, Optional
from pydantic import BaseModel

class TagNameSchema(BaseModel):
    ko: Optional[str] = None
    en: Optional[str] = None
    ja: Optional[str] = None
    tw: Optional[str] = None

class TagCreateSchema(BaseModel):
    tag_name: TagNameSchema

class CompanyNameSchema(BaseModel):
    ko: Optional[str] = None
    en: Optional[str] = None
    ja: Optional[str] = None
    tw: Optional[str] = None

class CompanyCreateSchema(BaseModel):
    company_name: CompanyNameSchema
    tags: Optional[List[TagCreateSchema]] = []

class CompanyResponseSchema(BaseModel):
    company_name: str
    tags: List[str]

class CompanyAutocompleteSchema(BaseModel):
    company_name: str

class TagSearchResponseSchema(BaseModel):
    company_name: str