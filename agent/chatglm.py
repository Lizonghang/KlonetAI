import zhipuai
from key import ZhiPuAI_API_Key
from transformers.tools import Agent

zhipuai.api_key = ZhiPuAI_API_Key


class ChatGLMAgent(Agent):
    """
    Agent that uses ChatGLM Inference SDK to generate code.

    Args:
        model_name (`str`): The name of the model to be used, could be "chatglm_pro", "chatglm_std", "chatglm_lite",
            or "chatglm_lite_32k".
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
    agent = ChatGLMAgent("chatglm_std")
    agent.run("Create a star topology with 5 host nodes and interconnect them with an OVS switch.")
    ```
    """

    def __init__(self, model_name, chat_prompt_template=None, run_prompt_template=None, additional_tools=None):
        super().__init__(
            chat_prompt_template=chat_prompt_template,
            run_prompt_template=run_prompt_template,
            additional_tools=additional_tools,
        )
        self.model_name = model_name

    def generate_one(self, prompt, stop):
        response = zhipuai.model_api.invoke(
            model=self.model_name,
            prompt=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        if response["code"] != 200:
            raise ValueError(f"Error {response.status_code}: {response.json()}")

        result = response["data"]["choices"][0]["content"]\
            .strip('"').replace('\\n', '\n').replace('\\"', '\"')

        # Inference API returns the stop sequence
        for stop_seq in stop:
            if result.endswith(stop_seq):
                return result[: -len(stop_seq)]
        return result
