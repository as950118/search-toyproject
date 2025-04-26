from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from backend import schemas


class CompanyServiceInterface(ABC):
    @abstractmethod
    def autocomplete_company(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.CompanyAutocompleteSchema]:
        """
        자동완성 기능을 위해 쿼리에 일치하는 회사 목록을 반환합니다.
        """
        pass

    @abstractmethod
    def get_company(
            self, db: Session, company_name: str, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        회사 이름으로 회사의 상세 정보를 반환합니다.
        """
        pass

    @abstractmethod
    def create_company(
            self, db: Session, company: schemas.CompanyCreateSchema, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        새로운 회사를 생성하고 해당 회사의 상세 정보를 반환합니다.
        """
        pass

    @abstractmethod
    def search_by_tag(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.TagSearchResponseSchema]:
        """
        태그 검색에 일치하는 회사 목록을 반환합니다.
        """
        pass

    @abstractmethod
    def add_tags_to_company(
            self, db: Session, company_name: str, tags: List[schemas.TagCreateSchema], lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        회사에 태그를 추가하고, 갱신된 회사의 상세 정보를 반환합니다.
        """
        pass

    @abstractmethod
    def delete_tag_from_company(
            self, db: Session, company_name: str, tag_name: str, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        회사에서 태그를 제거하고, 갱신된 회사의 상세 정보를 반환합니다.
        """
        pass
