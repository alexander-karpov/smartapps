from pymongo.database import Database
import time
import math

class MognoLogger:
    _db: Database
    _app_name: str

    def __init__(self, db: Database, app_name :str) -> None:
        self._db = db
        self._app_name = app_name


    def log(self, request: dict, response: dict) -> None:
        if 'ping' in request['request']['command']:
            return

        self._db['repka_logs'].insert_one({
            'app': self._app_name,
            'request': request['request']['original_utterance'],
            'message_id': request['session']['message_id'],
            'session_id': request['session']['session_id'],
            'response': response['response']['text'][:64],
            'time': math.ceil(time.time()*1000),
            'screen': request['meta']['interfaces']['screen'] is not None,
            'version': 4,
        })
