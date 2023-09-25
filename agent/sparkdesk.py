import ssl
import hmac
import json
import base64
import hashlib
import websocket
import _thread as thread
from urllib.parse import urlencode, urlparse
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from key import SparkDesk_AppId, SparkDesk_API_Secret, SparkDesk_API_Key
from transformers.tools import Agent

websocket.enableTrace(False)
result = ""


def on_error(ws, error):
    print("[WebSocket Error]", error)


def on_close(ws, args1, args2):
    print("[WebSocket Closed]")


def on_open(ws):
    thread.start_new_thread(run, (ws,))


def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'Error {code}: {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        global result
        result += content
        if status == 2:
            ws.close()


def run(ws, *args):
    ws.send(json.dumps(gen_params(ws.prompt)))


def gen_params(prompt):
    return {
        "header": {
            "app_id": SparkDesk_AppId,
            "uid": "klonetai-user"
        },
        "parameter": {
            "chat": {
                "domain": "generalv2",
                "temperature": 0.1,
                "max_tokens": 2048,
            }
        },
        "payload": {
            "message": {
                "text": [
                    {"role": "user", "content": prompt},
                ]
            }
        }
    }


class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, Spark_URL):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_URL).netloc
        self.path = urlparse(Spark_URL).path
        self.Spark_url = Spark_URL

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(
            self.APISecret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.Spark_url + '?' + urlencode(v)
        return url


class SparkDesk(Agent):
    """
    Agent that uses Xunfei SparkDesk REST API to generate code.

    Args:
        chat_prompt_template (`str`, *optional*):
            Pass along your own prompt if you want to override the default template for the `chat` method. Can be the
            actual prompt template or a repo ID (on the Hugging Face Hub). The prompt should be in a file named
            `chat_prompt_template.txt` in this repo in this case.
        run_prompt_template (`str`, *optional*):
            Pass along your own prompt if you want to override the default template for the `run` method. Can be the
            actual prompt template or a repo ID (on the Hugging Face Hub). The prompt should be in a file named
            `run_prompt_template.txt` in this repo in this case.
        additional_tools ([`Tool`], list of tools or dictionary with tool values, *optional*):
            Any additional tools to include on top of the default ones. If you pass along a tool with the same name as
            one of the default tools, that default tool will be overridden.

    Example:

    ```py
    agent = SparkDesk()
    agent.run("Create a star topology with 5 host nodes and interconnect them with an OVS switch.")
    ```
    """

    def __init__(self, chat_prompt_template=None, run_prompt_template=None, additional_tools=None):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.model_name = "spark-v2"

    def generate_one(self, prompt, stop):
        global result
        result = ""

        wsParam = Ws_Param(
            APPID=SparkDesk_AppId,
            APIKey=SparkDesk_API_Key,
            APISecret=SparkDesk_API_Secret,
            Spark_URL="ws://spark-api.xf-yun.com/v2.1/chat"
        )
        ws = websocket.WebSocketApp(
            wsParam.create_url(),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        ws.prompt = prompt
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        # Inference API returns the stop sequence
        for stop_seq in stop:
            if result.endswith(stop_seq):
                return result[: -len(stop_seq)]
        return result
