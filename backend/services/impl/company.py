from typing import List, Optional

from sqlalchemy.orm import Session

from backend import models, schemas
from backend.services.interfaces.company import CompanyServiceInterface
from backend.utils.util import get_localized_name


def _get_company_by_name(db: Session, company_name: str) -> Optional[models.Company]:
    """회사명(어느 언어든)으로 회사 객체 조회"""
    company_name_obj = db.query(models.CompanyName).filter(models.CompanyName.name == company_name).first()
    return company_name_obj.company if company_name_obj else None


def _get_tag_by_name(db: Session, tag_name: str) -> Optional[models.Tag]:
    """태그명(어느 언어든)으로 태그 객체 조회"""
    tag_name_obj = db.query(models.TagName).filter(models.TagName.name == tag_name).first()
    return tag_name_obj.tag if tag_name_obj else None


def _get_company_tag_names(company: models.Company, lang: str) -> List[str]:
    """회사에 연결된 태그명(언어별) 리스트 추출"""
    tag_names = []
    for ct in company.tags:
        tag = ct.tag
        tag_name_localized = get_localized_name(tag.names, lang)
        if tag_name_localized:
            tag_names.append(tag_name_localized)
    return sorted(set(tag_names))


class CompanyService(CompanyServiceInterface):
    def autocomplete_company(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.CompanyAutocompleteSchema]:
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
        company = _get_company_by_name(db, company_name)
        if not company:
            return None
        company_name_localized = get_localized_name(company.names, lang)
        tag_names = _get_company_tag_names(company, lang)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=tag_names
        )

    def create_company(
            self, db: Session, company: schemas.CompanyCreateSchema, lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        # 이미 존재하는 회사명 체크
        for l, name in company.company_name.dict().items():
            if name and db.query(models.CompanyName).filter(models.CompanyName.name == name).first():
                return None  # 이미 존재하면 None 반환

        db_company = models.Company()
        db.add(db_company)
        db.flush()
        for l, name in company.company_name.dict().items():
            if name:
                db.add(models.CompanyName(company_id=db_company.id, language_code=l, name=name))

        for tag in company.tags or []:
            tag_obj = None
            # 언어별 태그명으로 태그 찾기
            for l, tname in tag.tag_name.dict().items():
                if tname:
                    tag_obj = _get_tag_by_name(db, tname)
                    if tag_obj:
                        break
            if not tag_obj:
                tag_obj = models.Tag()
                db.add(tag_obj)
                db.flush()
                for l, tname in tag.tag_name.dict().items():
                    if tname:
                        db.add(models.TagName(tag_id=tag_obj.id, language_code=l, name=tname))
            if not db.query(models.CompanyTag).filter_by(company_id=db_company.id, tag_id=tag_obj.id).first():
                db.add(models.CompanyTag(company_id=db_company.id, tag_id=tag_obj.id))
        db.commit()

        company_name_localized = get_localized_name(db_company.names, lang)
        tag_names = _get_company_tag_names(db_company, lang)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=tag_names
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
        company = _get_company_by_name(db, company_name)
        if not company:
            return None
        for tag in tags:
            tag_obj = None
            for l, tname in tag.tag_name.dict().items():
                if tname:
                    tag_obj = _get_tag_by_name(db, tname)
                    if tag_obj:
                        break
            if not tag_obj:
                tag_obj = models.Tag()
                db.add(tag_obj)
                db.flush()
                for l, tname in tag.tag_name.dict().items():
                    if tname:
                        db.add(models.TagName(tag_id=tag_obj.id, language_code=l, name=tname))
            if not db.query(models.CompanyTag).filter_by(company_id=company.id, tag_id=tag_obj.id).first():
                db.add(models.CompanyTag(company_id=company.id, tag_id=tag_obj.id))
        db.commit()

        company_name_localized = get_localized_name(company.names, lang)
        tag_names = _get_company_tag_names(company, lang)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=tag_names
        )

    def delete_tag_from_company(
            self, db: Session, company_name: str, tag_name: str, lang: str
    ) -> Optional[schemas.CompanyResponseSchema]:
        company = _get_company_by_name(db, company_name)
        if not company:
            return None
        tag = _get_tag_by_name(db, tag_name)
        if not tag:
            return None

        mapping = db.query(models.CompanyTag).filter_by(company_id=company.id, tag_id=tag.id).first()
        if mapping:
            db.delete(mapping)
            db.commit()
            db.refresh(company)

        company_name_localized = get_localized_name(company.names, lang)
        tag_names = _get_company_tag_names(company, lang)
        return schemas.CompanyResponseSchema(
            company_name=company_name_localized,
            tags=tag_names
        )
