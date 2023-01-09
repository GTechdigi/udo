from sqlalchemy.orm import class_mapper


class BaseModel:

    def to_json(self):
        return dict((col.name, getattr(self, col.name))
                    for col in class_mapper(self.__class__).mapped_table.c)
