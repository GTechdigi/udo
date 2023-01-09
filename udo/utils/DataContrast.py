from udo.utils import Connection
from udo.models.Source import DatabaseSource, TableSource
from udo.utils.AEScoder import AES_Decrypt

key = '0CoJUm6Qyw8W8jud'


def data_contrast(db_code, sql=None, where_values=None, limit=5000):
    if where_values is None:
        where_values = []
    config = DatabaseSource.query.filter_by(db_code=db_code).first()
    config = config.to_json()
    config['password'] = AES_Decrypt(key, config['password'])
    if config['source_type'] == 'hive':
        result = Connection.__hive(config, sql, where_values, limit)
    elif config['source_type'] == 'mysql':
        result = Connection.__mysql(config, sql, where_values, limit)
    elif config['source_type'] == 'es':
        result = Connection.__es(config, sql, where_values, limit)
    elif config['source_type'] == 'clickhouse':
        result = Connection.__clickhouse(config, sql, where_values, limit)
    return result

