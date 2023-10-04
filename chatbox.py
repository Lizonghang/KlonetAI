import io
import os
import os.path
import requests.exceptions
import tool
import tutorial
import panel as pn
from datetime import datetime
from panel.widgets import SpeechToText
from contextlib import redirect_stdout
from tool.klonet import kai

tools = [obj() for obj in tool.base]        # 119 tokens
tools += [obj() for obj in tool.klonet]     # 4922 tokens
tools += [obj() for obj in tool.topo]       # 541 tokens
tools += [obj() for obj in tool.gpt]        # 184 tokens
tools += [obj() for obj in tutorial.base]   # 121 tokens
tools += [obj() for obj in tutorial.mxnet]

chat_time = None
save_dir = "output"
os.makedirs(save_dir, exist_ok=True)

pn.extension("floatpanel", notifications=True)

# Login to Klonet backend.
project_name_input = pn.widgets.TextInput(name="Project:", placeholder="", value="")
user_name_input = pn.widgets.TextInput(name="User:", placeholder="", value="")
host_ip_input = pn.widgets.TextInput(name="Klonet Backend Host IP:", placeholder="", value="")
port_input = pn.widgets.TextInput(name="Klonet Backend Port:", placeholder="", value="")


def click_login_klonet_button(event):
    project_name = project_name_input.value
    user_name = user_name_input.value
    host_ip = host_ip_input.value
    port = port_input.value
    kai.klonet_login(project_name, user_name, host_ip, port)
    if kai.test_klonet_connection():
        pn.state.notifications.success("Connected to Klonet backend.")
        login_klonet_button.button_type = "default"
        login_klonet_button.disabled = True
    else:
        pn.state.notifications.error('Connect to Klonet backend failed.', duration=0)


# Login to Klonet backend.
login_klonet_button = pn.widgets.Button(name="Login", button_type="primary", width=140)
login_klonet_button.on_click(click_login_klonet_button)


def click_test_klonet_connection_button(event):
    if kai.test_klonet_connection():
        pn.state.notifications.success("The connection has been established.")
    else:
        pn.state.notifications.error("Cannot reach Klonet backend. The reason may be "
                                     "that you are not logged in or the network is unreachable.", duration=0)


# Test Klonet connection.
test_klonet_connection_button = pn.widgets.Button(name="Test Connection", button_type="default", width=140)
test_klonet_connection_button.on_click(click_test_klonet_connection_button)

klonet_card = pn.Card(
    project_name_input,
    user_name_input,
    host_ip_input,
    port_input,
    pn.Row(login_klonet_button, test_klonet_connection_button),
    title="Login to Remote Klonet",
    collapsible=True,
    collapsed=False,
    width=320
)

organizations = ["OpenAI", "Huggingface (Free Trials)", u"阿里通义", u"智谱清言", u"百度文心", u"讯飞星火"]


def update_model_options(event):
    selected_org = event.new
    if selected_org == "OpenAI":
        select_model_button.options = {
            "GPT-3.5 Turbo (4K)": "gpt-3.5-turbo",
            "GPT-3.5 Turbo (16K)": "gpt-3.5-turbo-16k",
            "GPT-4 (8K)": "gpt-4",
            "GPT-4 (32K)": "gpt-4-32k"
        }
    elif selected_org == "Huggingface (Free Trials)":
        select_model_button.options = {
            "StarCoder (Recommended)": "starcoder",
            "CodeLlama 13b (4K)": "codellama-13b-hf",
            "CodeLlama 34b (4K)": "codeLlama-34b-instruct-hf",
            "CodeLlama 34b Phind v2": "phind-codellama-34b-v2"
        }
    elif selected_org == u"阿里通义":
        select_model_button.options = {
            u"通义千问 Turbo": "qwen-turbo",
            u"通义千问 Plus": "qwen-plus"
        }
    elif selected_org == u"智谱清言":
        select_model_button.options = {
            "ChatGLM Lite (8K)": "chatglm_lite",
            "ChatGLM Lite (32K)": "chatglm_lite_32k",
            "ChatGLM Std": "chatglm_std",
            "ChatGLM Pro": "chatglm_pro"
        }
    elif selected_org == u"百度文心":
        select_model_button.options = {
            u"文心一言": "ernie-bot",
            u"文心一言 Turbo": "ernie-bot-turbo"
        }
    elif selected_org == u"讯飞星火":
        select_model_button.options = {
            u"星火认知": "spark-v2"
        }
    else:
        raise NotImplementedError()


# Choose Agent.
select_organization_button = pn.widgets.Select(name="Model Source:", options=[])
select_model_button = pn.widgets.Select(name="Model Name:")
select_organization_button.param.watch(update_model_options, "value")
select_organization_button.options = organizations

APIKey_input = pn.widgets.TextInput(
    name="API Key:", placeholder="Default to use the APIKey in key.py", value="")
APPID_input = pn.widgets.TextInput(
    name="APP ID (optional):", placeholder="Default to use the APPID in key.py", value="")
APPSecret_input = pn.widgets.TextInput(
    name="APP Secret (optional):", placeholder="Default to use the APPSecret in key.py", value="")
run_mode_switch = pn.widgets.Switch(name="Chat-only", value=False)


def click_login_agent_button(event):
    selected_org = select_organization_button.value
    selected_model = select_model_button.value
    api_key = APIKey_input.value
    app_id = APPID_input.value
    app_secret = APPSecret_input.value
    if run_mode_switch.value:
        prompt_template = "The AI assistant tries to be helpful, polite, honest, and humble-but-knowledgeable."
    else:
        prompt_template = "LIKirin/klonetai-prompts"

    try:
        if selected_org == "OpenAI":
            kai.create_agent(
                agent_name="openai", key=api_key, tools=tools, openai_model=selected_model,
                chat_prompt_template=prompt_template, run_prompt_template=prompt_template)
        elif selected_org == "Huggingface (Free Trials)":
            kai.create_agent(
                agent_name=selected_model, key=api_key, tools=tools,
                chat_prompt_template=prompt_template, run_prompt_template=prompt_template)
        elif selected_org == u"阿里通义":
            from agent.dashscope import DashScopeAgent
            custom_agent = DashScopeAgent(
                selected_model, api_key, chat_prompt_template=prompt_template,
                run_prompt_template=prompt_template, additional_tools=tools)
            kai.create_agent(agent=custom_agent)
        elif selected_org == u"智谱清言":
            from agent.chatglm import ChatGLMAgent
            custom_agent = ChatGLMAgent(
                selected_model, api_key, chat_prompt_template=prompt_template,
                run_prompt_template=prompt_template, additional_tools=tools)
            kai.create_agent(agent=custom_agent)
        elif selected_org == u"百度文心":
            from agent.erniebot import ErnieBotAgent
            custom_agent = ErnieBotAgent(
                selected_model, api_key, chat_prompt_template=prompt_template,
                run_prompt_template=prompt_template, additional_tools=tools)
            kai.create_agent(agent=custom_agent)
        elif selected_org == u"讯飞星火":
            from agent.sparkdesk import SparkDesk
            custom_agent = SparkDesk(
                api_key, app_id, app_secret, chat_prompt_template=prompt_template,
                run_prompt_template=prompt_template, additional_tools=tools)
            kai.create_agent(agent=custom_agent)
        else:
            raise NotImplementedError()
    except requests.exceptions.ConnectionError:
        pn.state.notifications.error(f"Connect to {selected_org} ({selected_model}) failed.", duration=0)
        chat_box.append({
            AGENT_NAME: f"Failed to establish connection, try to solve this by using a VPN service."})
        return

    if run_mode_switch.value:
        kai.set_mode("chat")
        chat_box.append(
            {AGENT_NAME: "Chat-only mode is turned on, this chat can only be used forgeneral conversations."})

    login_agent_button.button_type = "success"
    login_agent_button.name = "Try Another Agent"
    login_agent_from_repo_button.name = "Try Another Agent"
    chat_box.append({
        AGENT_NAME: f"I will use the model {selected_model} provided by {selected_org} to take actions."})
    pn.state.notifications.success(f"Connect to {selected_org} ({selected_model}) success.")
    global chat_time
    chat_time = datetime.now().strftime("%Y%m%d-%H%M%S")


login_agent_button = pn.widgets.Button(name="Login", button_type="primary", width=300)
login_agent_button.on_click(click_login_agent_button)

model_card = pn.Card(
    select_organization_button,
    select_model_button,
    APIKey_input,
    APPID_input,
    APPSecret_input,
    login_agent_button,
    title="Login to Remote Agent",
    collapsible=True,
    collapsed=False,
    width=320
)

repo_input = pn.widgets.TextInput(name="HuggingFace Repo:", placeholder="To be done", value="")
login_agent_from_repo_button = pn.widgets.Button(name="Login", button_type="default", width=300)

local_agent_card = pn.Card(
    pn.Column(repo_input, login_agent_from_repo_button),
    title="Login to Local Agent",
    collapsible=True,
    collapsed=False,
    width=320
)

run_mode_card = pn.Card(
    pn.Row(
        pn.widgets.StaticText(value="Run the agent in chat-only mode?"),
        run_mode_switch,
        pn.widgets.TooltipIcon(value='Click "Login" to Remote/Local Agent or "Try Another Agent" to take effect.')
    ),
    title="Agent Mode",
    collapsible=True,
    collapsed=False,
    width=320
)

# Create a KlonetAI agent.
# kai.create_agent(agent_name="starcoder", tools=tools)

USER_NAME = "User"
AGENT_NAME = "KAI"


def command_handler(command):
    if not kai.is_agent_initialized:
        chat_box.append({AGENT_NAME: "Agent not found, please initialize the agent first."})
        return

    global chat_time
    if command == "/reset_chat":
        kai.new_chat()
        chat_box.clear()
        chat_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        chat_box.append({AGENT_NAME: "Welcome to a new chat, let's start over."})
    elif command == "/clear":
        chat_box.clear()
    elif command == "/reset_topo":
        kai.reset_project()
        chat_box.append({AGENT_NAME: "The topology has been reset."})
    elif command == "/chat":
        kai.set_mode("chat")
        chat_box.append({AGENT_NAME: "I'm running in chat mode right now, what do you want to know?"})
    elif command == "/agent":
        kai.set_mode("agent")
        chat_box.append({AGENT_NAME: "I'm running in agent mode now, please tell me what you want to do on Klonet."})
    elif command == "/save":
        save_path = os.path.join(save_dir, f"chat-{chat_time}.txt")
        chat_history = "\n\n".join([f"{row.name}: {row.value[0]}" for row in chat_box.rows])
        fp = open(save_path, "w")
        fp.write(chat_history)
        fp.close()
        chat_box.append({AGENT_NAME: f"This chat has been saved at {save_path}."})
    else:
        chat_box.append({AGENT_NAME: "Invalid command."})


def chat(event):
    if len(chat_box.rows) == 0: return
    last_message = chat_box.rows[-1]
    last_sender = last_message.name
    if last_sender == USER_NAME:
        prompt = last_message.value[0].strip()
        # Handle commands.
        if prompt[0] == '/':
            command_handler(prompt)
            return
        # Check login status.
        if not kai.is_logged_in:
            chat_box.append({AGENT_NAME: "You are not logged in, please login to Klonet first."})
            return
        # Chat with agent.
        with redirect_stdout(io.StringIO()) as output:
            kai.chat(prompt)
        output_str = output.getvalue()
        # Wrap python code.
        start_idx = output_str.find("==Code generated by the agent==")
        if start_idx != -1:
            start_idx += len("==Code generated by the agent==")
            output_str = output_str[:start_idx + 1] + "\n```py\n" + output_str[start_idx + 1:]
        end_idx = output_str.find("==Result==")
        if end_idx != -1:
            for idx in range(end_idx - 1, 0, -1):
                if output_str[idx] != '\n':
                    end_idx = idx
                    break
            output_str = output_str[:end_idx + 1] + "\n```" + output_str[end_idx + 1:]
        chat_box.append({AGENT_NAME: output_str})


chat_box = pn.widgets.ChatBox(
    value=[
        {USER_NAME: "You have joined the chat, please enjoy it!"},
        {AGENT_NAME: "Hello, this is KAI, I can help you interact with Klonet. "
                     "Please tell me what can I do for you :)"}
    ],
    show_names=False
)
chat_box.param.watch(chat, "value")


def click_send_speech_text_button(event):
    speech_text = speech_to_text.value.strip()
    if not speech_text: return
    chat_box.append({USER_NAME: speech_text})


send_speech_text_button = pn.widgets.Button(name="Send", button_type="primary", width=250)
send_speech_text_button.on_click(click_send_speech_text_button)

speech_to_text = SpeechToText(button_type="light")
speech_layout = pn.Column(
    pn.Row(speech_to_text.controls(["value"], jslink=False)),
    pn.Row(send_speech_text_button, speech_to_text)
)
speech_card = pn.Card(
    speech_layout,
    title="Speech to Text",
    collapsible=True,
    collapsed=False,
    width=340
)

quick_command_selector = pn.widgets.Select(
    options=[
        "/agent",
        "/clear",
        "/chat",
        "/reset_chat",
        "/reset_topo",
        "/save",
    ],
    value="/clear",
    width=247
)


def click_send_command_button(event):
    command = quick_command_selector.value
    if not command: return
    chat_box.append({USER_NAME: command})


send_command_button = pn.widgets.Button(name="Send", button_type="primary")
send_command_button.on_click(click_send_command_button)

quick_command_card = pn.Card(
    pn.Row(quick_command_selector, send_command_button),
    title="Quick Command",
    collapsible=True,
    collapsed=False,
    width=340
)


def collect_target_nodes(checkbox, node_input):
    if not kai.is_topo_deployed:
        pn.state.notifications.error(f"No project found, please deploy the project `klonetai` first.")
        chat_box.append({AGENT_NAME: "No project found, please deploy the project `klonetai` first."})
        return []

    all_nodes = kai.remote_topo
    controllers = list(all_nodes["controllers"].keys())
    hosts = list(all_nodes["hosts"].keys())
    routers = list(all_nodes["routers"].keys())
    switches = list(all_nodes["switches"].keys())
    node_groups = checkbox.value
    if "all" in node_groups:
        return controllers + hosts + routers + switches
    else:
        target_nodes = []
        if "hosts" in node_groups: target_nodes += hosts
        if "routers" in node_groups: target_nodes += routers
        if "switches" in node_groups: target_nodes += switches
        if "controllers" in node_groups: target_nodes += controllers

        for item in node_input.value.split(','):
            item = item.strip()
            if item and item not in target_nodes:
                target_nodes.append(item)
        return target_nodes


def click_send_file_button(event):
    if not kai.is_logged_in:
        chat_box.append({AGENT_NAME: "You are not logged in, please login to Klonet first."})
        return

    file_data_list = file_selector.value
    file_name_list = file_selector.filename
    if not (file_data_list and file_name_list): return

    target_nodes = collect_target_nodes(node_group_checkbox, target_node_input)
    if not target_nodes: return

    target_file_path = target_path_input.value
    if not target_file_path: return

    for file_bytes, file_name in zip(file_data_list, file_name_list):
        file_name = file_name.replace(' ', '-')
        for tgt_node in target_nodes:
            if target_file_path[-1] == '/':
                target_file_path = os.path.join(target_file_path, file_name)
            kai.upload_file(tgt_node, (file_name, file_bytes), target_file_path)
    pn.state.notifications.info(f"File uploaded.")
    chat_box.append({AGENT_NAME: f"I have tried to upload the files `{', '.join(file_name_list)}` "
                                 f"to nodes {', '.join(target_nodes)}, but I am not sure whether "
                                 f"they are successfully uploaded. Please manually check them."})
    file_selector.value = None
    file_selector.filename = ""


# File selector
send_file_button = pn.widgets.Button(name="Send", button_type="primary")
send_file_button.on_click(click_send_file_button)

file_selector = pn.widgets.FileInput(multiple=True, width=247)
target_path_input = pn.widgets.TextInput(
    name="Which directory to put these files in?",
    placeholder="/home", value="/home", width=320)
node_group_checkbox_text = pn.widgets.StaticText(
    value="Which types of nodes to upload these files to?")
node_group_checkbox = pn.widgets.CheckBoxGroup(
    inline=True, options=["all", "hosts", "controllers", "routers", "switches"])
target_node_input = pn.widgets.TextInput(
    name="Which nodes to upload these files to?", placeholder="h1,h2,h4", value="")

file_selector_card = pn.Card(
    pn.Column(
        target_path_input,
        node_group_checkbox_text,
        node_group_checkbox,
        target_node_input,
        pn.Row(file_selector, send_file_button),
    ),
    title="Upload File",
    collapsible=True,
    collapsed=False,
    width=340
)

SOURCE_COMMAND = "source /root/.bashrc"
preset_command = f"{SOURCE_COMMAND}"


def click_run_command_button(event):
    if not kai.is_logged_in:
        chat_box.append({AGENT_NAME: "You are not logged in, please login to Klonet first."})
        return

    command = command_input.value.strip()
    if not command: return

    target_nodes = collect_target_nodes(node_group_checkbox_for_command, target_node_input_for_command)
    if not target_nodes: return

    chat_box.append({AGENT_NAME: f"Run commands `{command}` on nodes {', '.join(target_nodes)}."})

    global preset_command
    ctns = {"list_type": "specified_ctn_list", "list": target_nodes}

    full_command = preset_command[:]
    conda_path = conda_path_input.value
    conda_env = conda_env_name.value
    if conda_path and conda_env:
        full_command = " && ".join([
            full_command,
            f"source {conda_path}",
            f"conda activate {conda_env}"
        ])
    full_command = " && ".join([full_command, command])
    print(f"Running command: {full_command}")
    response = kai.batch_exec(ctns, f'bash -c "{full_command}"', block="true")

    # Update current path.
    if ';' in command:
        command_list = command.split(';')
    elif '&&' in command:
        command_list = command.split('&&')
    else:
        command_list = [command]
    for cmd in command_list:
        cmd = cmd.strip()
        if cmd[:4] == "cd /" or cmd == "cd":
            preset_command = f"{SOURCE_COMMAND} && {cmd}"
        elif cmd[:3] == "cd ":
            if preset_command == SOURCE_COMMAND:
                preset_command = f"{SOURCE_COMMAND} && {cmd}"
            else:
                preset_command = " && ".join([preset_command, cmd])

    def reformat_json(response):
        reformated_response = {}
        for worker_ip, item in response.items():
            result = item["worker_exec_results"]
            for node_name, node_item in result.items():
                reformated_response[node_name] = node_item["output"]
        return reformated_response

    if type(response) is not dict:
        chat_box.append({AGENT_NAME: response})
        return

    output_str = ""
    for node_name, output in reformat_json(response).items():
        output_str += f"```shell\n"
        output_str += f"{node_name}$ {command}"
        output_str += f"\n{output}"
        output_str += "\n```\n"
    chat_box.append({AGENT_NAME: output_str})


def click_clear_command_button(event):
    command_input.value = ""


command_input = pn.widgets.TextAreaInput(name="Command:", value="", width=320, height=70)
run_command_button = pn.widgets.Button(name="Run", button_type="primary", width=150)
run_command_button.on_click(click_run_command_button)
clear_command_button = pn.widgets.Button(name="Clear Command", button="default", width=150)
clear_command_button.on_click(click_clear_command_button)
node_group_checkbox_text_for_command = pn.widgets.StaticText(
    value="Which types of nodes to run these commands?")
node_group_checkbox_for_command = pn.widgets.CheckBoxGroup(
    inline=True, options=["all", "hosts", "controllers", "routers", "switches"])
target_node_input_for_command = pn.widgets.TextInput(
    name="Which nodes to run these commands?", placeholder="h1,h2,h4", value="", width=320)


def configure_conda(event):
    kai.additional_info["conda_path"] = conda_path_input.value
    kai.additional_info["conda_env"] = conda_env_name.value


conda_path_input = pn.widgets.TextInput(
    name="Path to conda configuration file within containers:",
    placeholder="/opt/conda/etc/profile.d/conda.sh",
    value="/opt/conda/etc/profile.d/conda.sh")
conda_path_input.param.watch(configure_conda, "value")

conda_env_name = pn.widgets.TextInput(
    name="Name of conda environment to be used:", placeholder="base", value="base")
conda_path_input.param.watch(configure_conda, "value")
configure_conda(None)

# Execute batch commands
exec_command_card = pn.Card(
    pn.Column(
        command_input,
        node_group_checkbox_text_for_command,
        node_group_checkbox_for_command,
        target_node_input_for_command,
        conda_path_input,
        conda_env_name,
        pn.Row(run_command_button, clear_command_button)
    ),
    title="Command Execution",
    collapsible=True,
    collapsed=False,
    width=340
)

layout_left = pn.Column(klonet_card, model_card, local_agent_card, run_mode_card)
layout_right = pn.Column(speech_card, exec_command_card, file_selector_card, quick_command_card)
layout = pn.Row(layout_left, chat_box, layout_right)

pn.serve(
    layout,
    title="KAI Dashboard",
    websocket_max_message_size=1024 * 1024 * 1014,
    http_server_kwargs={"max_buffer_size": 1024 * 1024 * 1014}
)
