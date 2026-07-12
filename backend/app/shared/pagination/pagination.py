import math
from collections.abc import Callable


def calculate_pagination(page: int, page_size: int, total: int) -> dict[str, int]:
    pages = math.ceil(total / page_size) if total > 0 else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


def apply_pagination(query: Callable, page: int, page_size: int) -> tuple[list, int]:
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return items, total
