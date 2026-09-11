from flask import request

def paginate_query(query, default_page_size=20, max_page_size=100):
    """Utility to paginate an SQLAlchemy query from request query params."""
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    try:
        page_size = int(request.args.get("page_size", default_page_size))
        if page_size < 1:
            page_size = default_page_size
        elif page_size > max_page_size:
            page_size = max_page_size
    except ValueError:
        page_size = default_page_size

    total_count = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    return {
        "items": [item.to_dict() if hasattr(item, "to_dict") else item for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    }
