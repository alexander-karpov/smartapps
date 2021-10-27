from typing import Any, ClassVar, Dict, List
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict
from urllib.parse import quote_plus as quote
import os
import ssl
import pymongo


class EatableClassifierService:
    """
    Распознаёт съедобное и несъедобное
    """
    _classifier: ClassVar[Any] = None

    def is_eatable(self, command: str) -> bool:
        if not EatableClassifierService._classifier:
            EatableClassifierService._classifier = pipeline(
                'sentiment-analysis',
                model=AutoModelForSequenceClassification.from_pretrained('alexander-karpov/bert-eatable-classification-en-ru', num_labels=2),
                tokenizer=AutoTokenizer.from_pretrained('alexander-karpov/bert-eatable-classification-en-ru'),
            )

        predict:Dict[str, str] = EatableClassifierService._classifier(command)[0]

        return predict["label"] == "LABEL_1"


class MongoDbService:
    _mongodb_client: ClassVar[pymongo.MongoClient] = None

    def __init__(self) -> None:
        super().__init__()

        if MongoDbService._mongodb_client:
            return

        CONNECTION_STRING = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
            user=quote('kukuruku'),
            pw=quote(os.environ['POSTGRESQL_PASSWORD']),
            hosts=','.join(['rc1c-gtjrhjmixjcjdjw8.mdb.yandexcloud.net:27018']),
            rs='rs01',
            auth_src='skills')

        MongoDbService._mongodb_client = pymongo.MongoClient(
            CONNECTION_STRING,
            ssl_ca_certs='/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt',
            ssl_cert_reqs=ssl.CERT_REQUIRED)['skills']

    def get_db(self) -> pymongo.MongoClient:
        return MongoDbService._mongodb_client


class EatableRiddleService(MongoDbService):
    _eatable_riddles: List[str]
    _uneatable_riddles: List[str]

    def __init__(self):
        super().__init__()

        self._eatable_riddles = []
        self._uneatable_riddles = []

    def get_eatable_riddle(self) -> str:
        if not self._eatable_riddles:
            self._eatable_riddles = self._get_next_batch(is_eatable=True)

        return self._eatable_riddles.pop()

    def get_uneatable_riddle(self) -> str:
        if not self._uneatable_riddles:
            self._uneatable_riddles = self._get_next_batch(is_eatable=False)

        return self._uneatable_riddles.pop()

    def _get_next_batch(self, is_eatable) -> List[str]:
        pipeline = [
            {'$match': {'is_eatable': is_eatable, 'is_hidden': {"$ne": True}}},
            {'$sample': {'size': 8}}
        ]

        with super().get_db().get_collection('eat_eatable').aggregate(pipeline) as cur:
            return [doc['name'] for doc in cur]
