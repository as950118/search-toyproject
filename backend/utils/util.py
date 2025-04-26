from typing import Optional

from fastapi import Header


def get_language(x_wanted_language: Optional[str] = Header(None)):
    if x_wanted_language not in {"ko", "en", "ja", "tw"}:
        return "ko"
    return x_wanted_language


def get_localized_name(name_objs, lang: str):
    """
    name_objs: List of objects with .language_code and .name attributes
    lang: preferred language code
    Returns: name string in preferred language, or fallback to any available
    """
    if not name_objs:
        return None
    name_obj = next((n for n in name_objs if n.language_code == lang), None)
    if not name_obj:
        name_obj = name_objs[0]
    return name_obj.name if name_obj else None
