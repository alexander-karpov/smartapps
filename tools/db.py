from urllib.parse import quote_plus as quote
import ssl
import pymongo
import os

_CONNECTION_STRING = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote('kukuruku'),
    pw=quote(os.environ['POSTGRESQL_PASSWORD']),
    hosts=','.join([
        'rc1c-gtjrhjmixjcjdjw8.mdb.yandexcloud.net:27018'
    ]),
    rs='rs01',
    auth_src='skills')

db = pymongo.MongoClient(
    _CONNECTION_STRING,
    ssl_ca_certs='/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt',
    ssl_cert_reqs=ssl.CERT_REQUIRED)['skills']
