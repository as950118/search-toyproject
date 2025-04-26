import csv
import os
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Company, CompanyName, Tag, TagName, CompanyTag

CSV_FILE_PATH = os.environ.get("INIT_CSV_PATH", "company_tag_sample.csv")

def get_or_create_tag(session: Session, tag_names: dict):
    # tag_names: {'ko': ..., 'en': ..., 'ja': ...}
    # Check if tag exists by ko name (or en/ja fallback)
    ko_name = tag_names.get("ko")
    tag = None
    if ko_name:
        tag = session.query(Tag).join(TagName).filter(TagName.language_code == "ko", TagName.name == ko_name).first()
    if not tag:
        tag = Tag()
        session.add(tag)
        session.flush()  # get tag.id
        for lang, name in tag_names.items():
            if name:
                tag_name = TagName(tag_id=tag.id, language_code=lang, name=name)
                session.add(tag_name)
    return tag

def get_or_create_company(session: Session, company_names: dict):
    # company_names: {'ko': ..., 'en': ..., 'ja': ...}
    # Check if company exists by ko name (or en/ja fallback)
    ko_name = company_names.get("ko")
    company = None
    if ko_name:
        company = session.query(Company).join(CompanyName).filter(CompanyName.language_code == "ko", CompanyName.name == ko_name).first()
    if not company:
        company = Company()
        session.add(company)
        session.flush()  # get company.id
        for lang, name in company_names.items():
            if name:
                company_name = CompanyName(company_id=company.id, language_code=lang, name=name)
                session.add(company_name)
    return company

def main():
    session = SessionLocal()
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 회사 이름
            company_names = {
                "ko": row.get("company_ko", "").strip() or None,
                "en": row.get("company_en", "").strip() or None,
                "ja": row.get("company_ja", "").strip() or None,
            }
            # 태그 이름 (파이프 구분)
            tag_ko_list = row.get("tag_ko", "").split("|") if row.get("tag_ko") else []
            tag_en_list = row.get("tag_en", "").split("|") if row.get("tag_en") else []
            tag_ja_list = row.get("tag_ja", "").split("|") if row.get("tag_ja") else []

            company = get_or_create_company(session, company_names)
            tag_count = max(len(tag_ko_list), len(tag_en_list), len(tag_ja_list))
            for i in range(tag_count):
                tag_names = {
                    "ko": tag_ko_list[i].strip() if i < len(tag_ko_list) else None,
                    "en": tag_en_list[i].strip() if i < len(tag_en_list) else None,
                    "ja": tag_ja_list[i].strip() if i < len(tag_ja_list) else None,
                }
                if not any(tag_names.values()):
                    continue
                tag = get_or_create_tag(session, tag_names)
                # CompanyTag 연결 (중복 방지)
                exists = session.query(CompanyTag).filter_by(company_id=company.id, tag_id=tag.id).first()
                if not exists:
                    session.add(CompanyTag(company_id=company.id, tag_id=tag.id))
        session.commit()
    print("DB 초기 데이터 입력 완료.")

if __name__ == "__main__":
    main()