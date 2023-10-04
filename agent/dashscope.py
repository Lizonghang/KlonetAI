import dashscope
from key import DashScope_API_Key
from transformers.tools import Agent
from transformers.tools.prompts import CHAT_MESSAGE_PROMPT


class DashScopeAgent(Agent):
    """
    Agent that uses Aliyun DashScope Inference SDK to generate code.

    Args:
        model_name (`str`): The name of the model to be used, could be "ernie-bot" or "ernie-bot-turbo".
        key (`str`, *optional*): The API key obtained from Aliyun Dashboard.
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
    agent = DashScopeAgent("ernie-bot-turbo")
    agent.run("Create a star topology with 5 host nodes and interconnect them with an OVS switch.")
    ```
    """

    def __init__(self, model_name, key="", chat_prompt_template=None, run_prompt_template=None, additional_tools=None):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.model_name = model_name
        dashscope.api_key = key or DashScope_API_Key
        self._gen = dashscope.Generation()
        self._mode = "agent"

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

    def generate_one(self, prompt, stop):
        response = self._gen.call(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        if response["status_code"] != 200:
            raise ValueError(f"Error {response.status_code}: {response}")

        result = response["output"]["text"]
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
