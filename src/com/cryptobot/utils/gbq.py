from datetime import datetime

import pandas_gbq
from com.cryptobot.config import Config
from com.cryptobot.utils.path import get_dev_path
from google.oauth2 import service_account

import pandas as pd

settings = Config().get_settings()

pandas_gbq.context.credentials = service_account.Credentials.from_service_account_file(
    get_dev_path() + settings.gbq.service_credentials,
)
pandas_gbq.context.project = settings.gbq.project_id


def publish_to_table(table_name, data, schema=None):
    try:
        now = datetime.utcnow()

        pandas_gbq.to_gbq(pd.DataFrame.from_dict({'time_utc': now, **data}), f'{settings.gbq.dataset_id}.{table_name}',
                          project_id=settings.gbq.project_id, if_exists='append', table_schema=schema)
    except Exception as error:
        print({'error': error, 'data': data})


def query_table(query: str):
    return pandas_gbq.read_gbq(query)


def get_table_path(table_name):
    return f'{settings.gbq.dataset_id}.{table_name}'
