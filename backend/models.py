from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

NAME_LENGTH = 255
LANGUAGE_CODE_LENGTH = 8

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    names = relationship("CompanyName", back_populates="company", cascade="all, delete-orphan")
    tags = relationship("CompanyTag", back_populates="company", cascade="all, delete-orphan")


class CompanyName(Base):
    __tablename__ = "company_names"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    language_code = Column(String(LANGUAGE_CODE_LENGTH), nullable=False)
    name = Column(String(NAME_LENGTH), nullable=False)

    company = relationship("Company", back_populates="names")
    __table_args__ = (UniqueConstraint('company_id', 'language_code', name='_company_lang_uc'),)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    names = relationship("TagName", back_populates="tag", cascade="all, delete-orphan")
    companies = relationship("CompanyTag", back_populates="tag", cascade="all, delete-orphan")


class TagName(Base):
    __tablename__ = "tag_names"
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    language_code = Column(String(LANGUAGE_CODE_LENGTH), nullable=False)
    name = Column(String(NAME_LENGTH), nullable=False)

    tag = relationship("Tag", back_populates="names")
    __table_args__ = (UniqueConstraint('tag_id', 'language_code', name='_tag_lang_uc'),)


class CompanyTag(Base):
    __tablename__ = "company_tags"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    company = relationship("Company", back_populates="tags")
    tag = relationship("Tag", back_populates="companies")
    __table_args__ = (UniqueConstraint('company_id', 'tag_id', name='_company_tag_uc'),)
