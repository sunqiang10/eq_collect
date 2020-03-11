import json
import datetime
import os


class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d %H:%M:%S')


def serialize_model(model):
    from sqlalchemy.orm import class_mapper
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


STATIC_FILE_PATH = os.path.abspath(os.path.dirname(__file__)).split('eq_collect')[
                       0] + 'eq_collect' + os.sep + 'static' + os.sep
