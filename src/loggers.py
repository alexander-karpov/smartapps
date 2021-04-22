from abc import abstractmethod
from typing import Protocol
from pymongo import MongoClient
import time


class CommandLogger(Protocol):
    @abstractmethod
    def log(self, command: str, reply: str, session: str) -> None:
        raise NotImplementedError


class MognoCommandLogger(CommandLogger):
    _db: MongoClient
    _collection_name: str


    def __init__(self, db: MongoClient, collection_name :str) -> None:
        self._db = db
        self._collection_name = collection_name


    def log(self, command: str, reply: str, session: str) -> None:
        self._db[self._collection_name].insert({
            "command": command,
            "reply": reply,
            "session": session,
            "time": time.time()
        }, {
            "writeConcern": { "w": 0, "j": False }
        })


class StdoutCommandLogger(CommandLogger):
    def log(self, command: str, reply: str, session: str) -> None:
        print(f"Command: {command}, reply: {reply}")


class RiddleLogger(Protocol):
    @abstractmethod
    def log(self, riddle: str, guess: bool, answer: bool, is_user: bool) -> None:
        raise NotImplementedError


class MongoRiddleLogger(RiddleLogger):
    _db: MongoClient
    _collection_name: str


    def __init__(self, db: MongoClient, collection_name :str) -> None:
        self._db = db
        self._collection_name = collection_name


    def log(self, riddle: str, guess: bool, answer: bool, is_user: bool) -> None:
        self._db.eat_guess.insert({
            "riddle": riddle,
            "guess": guess,
            "answer": answer,
            "is_user": is_user
        }, {
            "writeConcern": { "w": 0, "j": False }
        })


class StdoutRiddleLogger(RiddleLogger):
    def log(self, riddle: str, guess: bool, answer: bool, is_user: bool) -> None:
        print(f"Riddle: {riddle}, guess: {guess}, answer: {answer}, is_user: {is_user}")
