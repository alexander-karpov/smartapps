from typing import TypeVar

T = TypeVar("T")


def safeget(data, *nested_path, default: T = None) -> T:
    """
    Извлекает значение из вложенных словарей
    """
    value = None

    for key in nested_path:
        if isinstance(data, dict):
            value = data.get(key)
            data = value
        else:
            return default

    return value or default
