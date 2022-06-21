from typing import Optional


def what_can_you_do(command: str) -> Optional[bool]:
    if 'что ты умеешь' in command:
        return True

    return None


def quit(command: str) -> Optional[bool]:
    if command in ['хватит', 'выход', 'стоп']:
        return True

    return None


def help(command: str) -> Optional[bool]:
    if command in ["помощь", "повтори"]:
        return True

    return None
