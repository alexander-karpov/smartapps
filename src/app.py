from collections import OrderedDict
from typing import Dict
import topics
from dialog import Dialog, ReplyBuilder
from flask import Flask, request
from urllib.parse import quote_plus as quote
import json
import os
import ssl
import pymongo
from loggers import CommandLogger, RiddleLogger, MognoCommandLogger, MongoRiddleLogger, StdoutCommandLogger, StdoutRiddleLogger

app = Flask(__name__)


CONNECTION_STRING = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote('kukuruku'),
    pw=quote(os.environ['POSTGRESQL_PASSWORD']),
    hosts=','.join([
        'rc1c-gtjrhjmixjcjdjw8.mdb.yandexcloud.net:27018'
    ]),
    rs='rs01',
    auth_src='skills')

db = pymongo.MongoClient(
    CONNECTION_STRING,
    ssl_ca_certs='/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt',
    ssl_cert_reqs=ssl.CERT_REQUIRED)['skills']

command_logger: CommandLogger = MognoCommandLogger(db, 'eat_log') if 'PRODUCTION' in os.environ else StdoutCommandLogger()
guess_logger: RiddleLogger = MongoRiddleLogger(db, 'eat_guess') if 'PRODUCTION' in os.environ else StdoutRiddleLogger()

class SessionsManager:
    _sessions: OrderedDict
    _max_size: int


    def __init__(self) -> None:
        self._sessions = OrderedDict()
        self._max_size = 64


    def __contains__(self, key: str) -> bool:
        return key in self._sessions


    def __getitem__(self, key: str):
        self._sessions.move_to_end(key)

        return self._sessions[key]


    def __setitem__(self, key: str, dialog: Dialog):
        self._sessions[key] = dialog

        if len(self._sessions) > self._max_size:
            self._sessions.popitem(False)


sessions = SessionsManager()


def _get_dialog() -> Dialog:
    return Dialog(topics.EatableTopic(
        guess_logger
    ))


@app.route("/", methods=['POST']) # type:ignore
def main():
    if request.json is None:
        return json.dumps({ "error": "empty request" }, ensure_ascii=False)

    req = request.json
    session_id: str = req['session']["session_id"]
    command: str = req["request"]["command"]

    if session_id not in sessions:
        sessions[session_id] = _get_dialog()

    dialog = sessions[session_id]
    reply = ReplyBuilder()
    dialog.handle_command(command, reply)

    text = " ".join(reply._display)
    tts = " ".join(reply._voice)

    command_logger.log(command, text, session_id)

    return json.dumps({
        "version": req['version'],
        "session": req['session'],
        "response": {
            "text": text,
            "tts": tts,
            "end_session": False
        }
    }, ensure_ascii=False)
