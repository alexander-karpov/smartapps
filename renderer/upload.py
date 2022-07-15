import io
import os
from PIL.Image import Image
from requests import Session, Request

s = Session()

s.headers.update({"Authorization": f"OAuth {os.environ['DIALOGS_OAUTH']}"})

def upload(file: bytes):
    dialoder_renderer_skill_id = "75c022e8-3076-4b92-90c8-44ab38d29950"

    resp = s.post(f"https://dialogs.yandex.net/api/v1/skills/{dialoder_renderer_skill_id}/images", files={'file': file})



    # resp = s.send(prepped,
    #     # stream=stream,
    #     # verify=verify,
    #     # proxies=proxies,
    #     # cert=cert,
    #     # timeout=timeout
    # )
    resp_json = resp.json()
    resp.close()

    if "image" not in resp_json:
        print(resp_json)
        return "Error"

    return resp.json()["image"]
