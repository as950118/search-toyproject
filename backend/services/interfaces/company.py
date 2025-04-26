from typing import List, Optional, overload
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from backend import schemas

class CompanyServiceInterface(ABC):
    @abstractmethod
    def autocomplete_company(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.CompanyAutocompleteSchema]:
        """
        Returns a list of companies matching the query for autocomplete.
        """
        pass

    @abstractmethod
    def get_company(
            self, db: Session, company_name: str, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        Returns company details by name.
        """
        pass

    @abstractmethod
    def create_company(
            self, db: Session, company: schemas.CompanyCreateSchema, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        Creates a new company and returns its details.
        """
        pass

    @abstractmethod
    def search_by_tag(
            self, db: Session, query: str, lang: str
    ) -> List[schemas.TagSearchResponseSchema]:
        """
        Returns companies matching a tag search.
        """
        pass

    @abstractmethod
    def add_tags_to_company(
            self, db: Session, company_name: str, tags: List[schemas.TagCreateSchema], lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        Adds tags to a company and returns updated company details.
        """
        pass

    @abstractmethod
    def delete_tag_from_company(
            self, db: Session, company_name: str, tag_name: str, lang: str
    ) -> schemas.CompanyResponseSchema:
        """
        Removes a tag from a company and returns updated company details.
        """
        pass