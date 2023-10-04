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
from key import SparkDesk_AppId, SparkDesk_AppSecret, SparkDesk_API_Key
from transformers.tools import Agent
from transformers.tools.prompts import CHAT_MESSAGE_PROMPT

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
        key (`str`, *optional*): The API key obtained from Xunfei SparkDesk Dashboard.
        appid (`str`, *optional*): The App Id obtained from Xunfei SparkDesk Dashboard.
        appsecret (`str`, *optional*): The App Secret obtained from Xunfei SparkDesk Dashboard.
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

    def __init__(self, key="", appid="", appsecret="", chat_prompt_template=None,
                 run_prompt_template=None, additional_tools=None):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.model_name = "spark-v2"
        if key: SparkDesk_API_Key = key
        if appid: SparkDesk_AppId = appid
        if appsecret: SparkDesk_AppSecret = appsecret
        self._mode = "agent"

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

    def generate_one(self, prompt, stop):
        global result
        result = ""

        wsParam = Ws_Param(
            APPID=SparkDesk_AppId,
            APIKey=SparkDesk_API_Key,
            APISecret=SparkDesk_AppSecret,
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

    def chat(self, task, *, return_code=False, remote=False, **kwargs):
        if not self._mode == "chat":
            return super().chat(task, return_code=return_code, remote=remote, **kwargs)

        if self.chat_history is None:
            description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.toolbox.items()])
            prompt = self.chat_prompt_template.replace("<<all_tools>>", description)
        else:
            prompt = self.chat_history
        prompt += CHAT_MESSAGE_PROMPT.replace("<<task>>", f"[Chat only] {task}")
        response = self.generate_one(prompt, stop=["Human:", "====="])
        self.chat_history = prompt + response.strip() + "\n"
        self.log(response + "\n")
