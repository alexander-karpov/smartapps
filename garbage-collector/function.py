from datetime import datetime, timedelta
import os
import requests
from dateutil import parser


def handler(event, context):
    resp = requests.get(
        "https://dialogs.yandex.net/api/v1/skills/01aa8cf1-03ef-4549-8d0f-0389d85f7587/images",
        headers={
            "Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}",
        }
    )

    for image in resp.json()["images"]:
        created_at = parser.isoparse(image["createdAt"])
        is_old = created_at < datetime.now(tz=created_at.tzinfo) - timedelta(minutes=1)

        if is_old:
            requests.delete(
                f"https://dialogs.yandex.net/api/v1/skills/01aa8cf1-03ef-4549-8d0f-0389d85f7587/images/{image['id']}",
                headers={
                    "Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}",
                }
            )

    return {
        'statusCode': 200,
    }

if __name__ == "__main__":
    handler(None, None)
