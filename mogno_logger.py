import math
from pymongo.database import Database
import time
from util import safeget


class MognoLogger:
    _db: Database

    def __init__(self, db: Database) -> None:
        self._db = db

    def log(self, request: dict, response: dict, app_name: str) -> None:
        """
        Сохраняет запрос и ответ в нашу могну
        """
        if "ping" in request["request"]["command"]:
            return

        self._db["repka_logs"].insert_one(
            {
                "app": app_name,
                "request": request["request"]["original_utterance"],
                "message_id": request["session"]["message_id"],
                "session_id": request["session"]["session_id"],
                "response": response["response"]["text"],
                "time": math.ceil(time.time() * 1000),
                "screen": safeget(request, "meta", "interfaces", "screen") is not None,
                "version": 4,
            }
        )
