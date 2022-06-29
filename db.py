import os
import ssl
from urllib.parse import quote_plus as quote
from pymongo.mongo_client import MongoClient

url = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote('kukuruku'),
    pw=quote(os.environ['POSTGRESQL_PASSWORD']),
    hosts=','.join([
        'rc1c-gtjrhjmixjcjdjw8.mdb.yandexcloud.net:27018'
    ]),
    rs='rs01',
    auth_src='skills')

db = MongoClient(
    url,
    tlsCAFile='/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt')['skills']
