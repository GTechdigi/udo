from flask_sqlalchemy import BaseQuery


def page(query: BaseQuery, page_num, page_size):
    return query.paginate(page_num, per_page=page_size).items, query.count()


