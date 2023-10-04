from transformers.tools import OpenAiAgent
from transformers.tools.prompts import CHAT_MESSAGE_PROMPT


class KAIOpenAIAgent(OpenAiAgent):

    def __init__(self, *args, **kwargs):
        self._mode = "agent"
        super().__init__(*args, **kwargs)

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

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
