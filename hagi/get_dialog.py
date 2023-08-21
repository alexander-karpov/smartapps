from functools import lru_cache
from dialoger import Dialog, DialogAPI


def _create_hagi_dialog() -> Dialog:
    dialog = Dialog()
    api = DialogAPI(dialog)

    @api.otherwise
    def _():
        api.say("Я говорящий котёнок и я повторю что ты скажешь.")

    return dialog


@lru_cache(maxsize=64)
def get_dialog(session_id: str) -> Dialog:
    return _create_hagi_dialog()
