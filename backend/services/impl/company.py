from typing import List, Optional

from sqlalchemy.orm import Session

from backend import models, schemas
from backend.services.interfaces.company import CompanyServiceInterface
from backend.utils.util import get_localized_name


class CompanyService(CompanyServiceInterface):
    def autocomplete_company(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.CompanyAutocompleteSchema]:
        """
        Returns a list of companies matching the query for autocomplete.
        """
        lang_config_map = {
            "ko": "simple",
            "en": "english",
            "ja": "simple",
            "tw": "simple"
        }
        # config = lang_config_map.get(lang, "simple")  # 현재 미사용, 추후 FTS 적용 시 활용
        q = db.query(models.CompanyName).filter(
            models.CompanyName.language_code == lang,
            models.CompanyName.name.ilike(f"%{query}%")
        ).all()
        return [schemas.CompanyAutocompleteSchema(company_name=c.name) for c in q]

    def get_company(
            self, db: Session, company_name: str, lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        company_name_obj = db.query(models.CompanyName).filter(
            models.CompanyName.name == company_name
        ).first()
        if not company_name_obj:
            return None
        company = company_name_obj.company

        # Get company name in requested language, fallback to any
        company_name_localized = get_localized_name(company.names, lang)

        # Get tags in requested language, fallback to any
        tag_names = []
        for ct in company.tags:
            tag = ct.tag
            tag_name_localized = get_localized_name(tag.names, lang)
            if tag_name_localized:
                tag_names.append(tag_name_localized)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=sorted(set(tag_names))
        )

    def create_company(
            self, db: Session, company: schemas.CompanyCreateSchema, lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        # Check if company exists in any language
        for l, name in company.company_name.dict().items():
            if name and db.query(models.CompanyName).filter(models.CompanyName.name == name).first():
                return None  # 이미 존재하면 None 반환

        db_company = models.Company()
        db.add(db_company)
        db.flush()
        # Add names
        for l, name in company.company_name.dict().items():
            if name:
                db.add(models.CompanyName(company_id=db_company.id, language_code=l, name=name))
        # Add tags
        tag_ids = []
        for tag in company.tags or []:
            tag_obj = None
            # Try to find tag by any language
            for l, tname in tag.tag_name.dict().items():
                if tname:
                    tag_name_obj = db.query(models.TagName).filter(models.TagName.name == tname).first()
                    if tag_name_obj:
                        tag_obj = tag_name_obj.tag
                        break
            if not tag_obj:
                tag_obj = models.Tag()
                db.add(tag_obj)
                db.flush()
                for l, tname in tag.tag_name.dict().items():
                    if tname:
                        db.add(models.TagName(tag_id=tag_obj.id, language_code=l, name=tname))
            tag_ids.append(tag_obj.id)
            db.add(models.CompanyTag(company_id=db_company.id, tag_id=tag_obj.id))
        db.commit()
        # Response
        company_name_localized = get_localized_name(db_company.names, lang)
        tag_names = []
        for ct in db_company.tags:
            tag = ct.tag
            tag_name_localized = get_localized_name(tag.names, lang)
            if tag_name_localized:
                tag_names.append(tag_name_localized)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=sorted(set(tag_names))
        )

    def search_by_tag(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.TagSearchResponseSchema]:
        tag_names = db.query(models.TagName).filter(
            models.TagName.name.contains(query)
        ).all()
        company_ids = set()
        companies = []
        for tag_name in tag_names:
            tag = tag_name.tag
            for ct in tag.companies:
                company = ct.company
                if company.id not in company_ids:
                    company_name_localized = get_localized_name(company.names, lang)
                    companies.append(schemas.TagSearchResponseSchema(company_name=company_name_localized))
                    company_ids.add(company.id)
        return companies

    def add_tags_to_company(
            self,
            db: Session,
            company_name: str,
            tags: List[schemas.TagCreateSchema],
            lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        # Find company by name in any language
        company_name_obj = db.query(models.CompanyName).filter(models.CompanyName.name == company_name).first()
        if not company_name_obj:
            return None
        company = company_name_obj.company
        for tag in tags:
            tag_obj = None
            # Try to find tag by any language
            for l, tname in tag.tag_name.dict().items():
                if tname:
                    tag_name_obj = db.query(models.TagName).filter(models.TagName.name == tname).first()
                    if tag_name_obj:
                        tag_obj = tag_name_obj.tag
                        break
            if not tag_obj:
                tag_obj = models.Tag()
                db.add(tag_obj)
                db.flush()
                for l, tname in tag.tag_name.dict().items():
                    if tname:
                        db.add(models.TagName(tag_id=tag_obj.id, language_code=l, name=tname))
            # Add mapping if not exists
            if not db.query(models.CompanyTag).filter_by(company_id=company.id, tag_id=tag_obj.id).first():
                db.add(models.CompanyTag(company_id=company.id, tag_id=tag_obj.id))
        db.commit()
        # Response
        company_name_localized = get_localized_name(company.names, lang)
        tag_names = []
        for ct in company.tags:
            tag = ct.tag
            tag_name_localized = get_localized_name(tag.names, lang)
            if tag_name_localized:
                tag_names.append(tag_name_localized)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=sorted(set(tag_names))
        )

    def delete_tag_from_company(
            self, db: Session, company_name: str, tag_name: str, lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        # Find company by name in any language
        company_name_obj = db.query(models.CompanyName).filter(models.CompanyName.name == company_name).first()
        if not company_name_obj:
            return None
        company = company_name_obj.company
        # Find tag by name in any language
        tag_name_obj = db.query(models.TagName).filter(models.TagName.name == tag_name).first()
        if not tag_name_obj:
            return None
        tag = tag_name_obj.tag

        # Remove mapping
        mapping = db.query(models.CompanyTag).filter_by(company_id=company.id, tag_id=tag.id).first()
        if mapping:
            db.delete(mapping)
            db.commit()
            db.refresh(company)

        # 삭제 후 회사 정보 반환 (언어별)
        company_name_localized = get_localized_name(company.names, lang)
        tag_names = []
        for ct in company.tags:
            tag = ct.tag
            tag_name_localized = get_localized_name(tag.names, lang)
            if tag_name_localized:
                tag_names.append(tag_name_localized)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=sorted(set(tag_names))
        )
