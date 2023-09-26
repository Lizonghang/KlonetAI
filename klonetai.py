import requests
from klonet_api import *


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as msg:
            print(f"[Error] {msg}")

    return wrapper


def http_response_handler(response, func=lambda r: r["msg"]):
    if response.status_code != 200:
        err_msg = f"Request failed with status code {response.status_code}"
        return err_msg
    else:
        data = response.json()
        code = data.get("code", 1)
        msg = data.get("msg", "Unknown")
        if code == 0:
            return f"Request failed. Error message: {msg}"
        else:
            return func(data)


class KlonetAI:

    def __init__(self):
        self._agent = None
        self._backend_host = ""
        self._port = 0
        self._project = ""
        self._user = ""
        self._image_manager = None
        self._project_manager = None
        self._node_manager = None
        self._link_manager = None
        self._cmd_manager = None
        self._topo = Topo()
        self._link_config = {}

    @property
    def project_name(self):
        return self._project

    @property
    def user(self):
        return self._user

    @property
    def backend_host(self):
        return self._backend_host

    @property
    def port(self):
        return self._port

    @property
    def images(self):
        return self._image_manager.get_images()

    @property
    def topo(self):
        return self._topo

    @property
    def remote_topo(self):
        ip = self._backend_host
        port = self._port
        project = self._project
        user = self._user
        url = f"http://{ip}:{port}/re/project/{project}/?user={user}"
        response = requests.get(url)

        def get_topo(data_json):
            project_info = data_json.get("project", {})
            topo = project_info.get("topo", "No topo data")
            return topo
        return http_response_handler(response, get_topo)

    @property
    def nodes(self):
        return self._topo.get_nodes()

    @property
    def remote_nodes(self):
        ip = self._backend_host
        port = self._port
        project = self._project
        user = self._user
        url = f"http://{ip}:{port}/re/project/{project}/node/?user={user}"
        response = requests.get(url)

        def get_node_info(data_json):
            node_info = data_json.get("node_info", {})
            return node_info
        return http_response_handler(response, get_node_info)

    @property
    def links(self):
        return self._topo.get_links()

    @property
    def remote_links(self):
        ip = self._backend_host
        port = self._port
        project = self._project
        user = self._user
        url = f"http://{ip}:{port}/re/project/{project}/link/?user={user}"
        response = requests.get(url)

        def get_link_info(data_json):
            link_info = data_json.get("link_info", {})
            return link_info
        return http_response_handler(response, get_link_info)

    def klonet_login(self, project_name, user_name, host_ip, port):
        self._project = project_name
        self._user = user_name
        self._backend_host = host_ip
        self._port = port
        self._image_manager = ImageManager(self._user, self._backend_host, self._port)
        self._project_manager = ProjectManager(self._user, self._backend_host, self._port)
        self._node_manager = NodeManager(self._user, project, self._backend_host, self._port)
        self._link_manager = LinkManager(self._user, project, self._backend_host, self._port)
        self._cmd_manager = CmdManager(self._user, project, self._backend_host, self._port)

    def create_agent(self, agent=None, agent_name="", tools=[],
                     openai_model="gpt-3.5-turbo-16k", keep_tools=False):
        if agent:
            self._agent = agent
            print(f"Connected to Agent {agent.model_name}.")
        elif agent_name == "openai":
            from transformers.tools import OpenAiAgent
            from key import OpenAI_API_Key
            self._agent = OpenAiAgent(
                model=openai_model, api_key=OpenAI_API_Key, additional_tools=tools)
            print("Connected to OpenAI Agent.")
        else:
            from transformers.tools import HfAgent
            from key import Huggingface_API_Key
            pinned_model = {
                "starcoder": "bigcode/starcoder",
                "codellama-13b-hf": "codellama/CodeLlama-13b-hf",
                "codeLlama-34b-instruct-hf": "codellama/CodeLlama-34b-Instruct-hf",
                "phind-codellama-34b-v2": "Phind/Phind-CodeLlama-34B-v2",
            }
            model_suffix = pinned_model.get(agent_name, "bigcode/starcoder")
            url = f"https://api-inference.huggingface.co/models/{model_suffix}"
            self._agent = HfAgent(url, token=Huggingface_API_Key, additional_tools=tools)
            print(f"Connected to 🤗 Agent: {model_suffix}.")

        # Remove unnecessary built-in tools.
        if not keep_tools:
            self._agent.toolbox.pop("document_qa")
            self._agent.toolbox.pop("image_captioner")
            self._agent.toolbox.pop("image_qa")
            self._agent.toolbox.pop("image_segmenter")
            self._agent.toolbox.pop("transcriber")
            self._agent.toolbox.pop("text_qa")
            self._agent.toolbox.pop("text_classifier")
            self._agent.toolbox.pop("text_reader")
            self._agent.toolbox.pop("translator")
            self._agent.toolbox.pop("image_transformer")
            self._agent.toolbox.pop("image_generator")
            self._agent.toolbox.pop("video_generator")

        # Replace the built-in summarizer with ours.
        import tool
        self._agent.toolbox["summarizer"] = tool.SummarizeTool()
        print(f"All available tools:", list(self._agent.toolbox.keys()))

    @property
    def toolbox(self):
        return self._agent.toolbox

    @property
    def chat_history(self):
        return self._agent.chat_history

    @property
    def chat_state(self):
        return self._agent.chat_state

    @error_handler
    def new_chat(self):
        self._agent.prepare_for_new_chat()

    @error_handler
    def chat(self, *args, **kwargs):
        return self._agent.chat(*args, **kwargs)

    @error_handler
    def run(self, *args, **kwargs):
        return self._agent.run(*args, **kwargs)

    def reset_project(self):
        del self._topo
        self._topo = Topo()
        self._link_config.clear()
        self._project_manager.destroy(self._project)

    def add_node(self, name, image, cpu_limit=None, mem_limit=None, x=0, y=0):
        node = self._topo.add_node(
            image, name,
            resource_limit={"cpu": cpu_limit, "mem": mem_limit},
            location={"x": x, "y": y})
        return node

    def add_node_runtime(self, name, image, cpu_limit=None, mem_limit=None, x=0, y=0):
        node = self._node_manager.dynamic_add_node(
            name, image,
            resource_limit={"cpu": cpu_limit, "mem": mem_limit},
            location={"x": x, "y": y}
        )
        return node

    def delete_node_runtime(self, name):
        self._node_manager.dynamic_delete_node(name)

    def add_link(self, src_node, dst_node, link_name=None, src_ip="", dst_ip=""):
        link = self._topo.add_link(
            src_node, dst_node, link_name, src_ip, dst_ip)
        return link

    def add_link_runtime(self, src_node, dst_node, link_name=None, src_ip="", dst_ip=""):
        self._link_manager.dynamic_add_link(
            link_name, src_node, dst_node, src_ip, dst_ip)

    def delete_link_runtime(self, link_name):
        self._link_manager.dynamic_delete_link(link_name)

    def configure_link(self, config):
        link_name = config["link"]
        _ = self._link_config.setdefault(link_name, {})

        node_name = config["ne"]
        src_node = self.links[link_name].source
        dst_node = self.links[link_name].target
        src_link_config = _.setdefault(src_node, {})
        dst_link_config = _.setdefault(dst_node, {})

        if node_name == src_node:
            src_link_config.update(**config)
            dst_link_config.update({"link": link_name, "ne": dst_node})
        elif node_name == dst_node:
            src_link_config.update({"link": link_name, "ne": src_node})
            dst_link_config.update(**config)
        else:
            raise LinkInconsistentError(f"Node {node_name} is not on link {link_name}.")

        src_config_obj = LinkConfiguration(**src_link_config)
        dst_config_obj = LinkConfiguration(**dst_link_config)
        self._link_manager.config_link(src_config_obj, dst_config_obj)
        return src_link_config if node_name == src_node else dst_link_config

    def reset_link(self, link_name, clean_cache=False):
        self._link_manager.clear_link_configuration(link_name)
        if clean_cache: self._link_config.clear()

    def query_link(self, link_name, node_name):
        # TODO: To be added.
        return None

    def deploy(self):
        self._project_manager.deploy(self._project, self._topo)

    def check_deployed(self):
        ip = self._backend_host
        port = self._port
        user = self._user
        project = self._project
        url = f"http://{ip}:{port}/master/topo/?user={user}&topo={project}"
        response = requests.get(url)

        def get_deploy_status(data_json):
            return data_json["stat"]
        return http_response_handler(response, get_deploy_status)

    def execute(self, node_name, command):
        response = self._cmd_manager.exec_cmds_in_nodes({
            node_name: [command]
        })
        return response

    def batch_exec(self, ctns, command):
        url = f"http://{self._backend_host}:{self._port}/master/batch_exec_cmd/"
        data = {
            "user": self._user,
            "topo": self._project,
            "ctns": ctns,
            "cmd": command
        }
        response = requests.post(url, json=data)

        def get_exec_result(data_json):
            return data_json["exec_results"]
        return http_response_handler(response, get_exec_result)

    def enable_ssh_service(self, node_name):
        return self._node_manager.ssh_service(node_name, True)

    def port_mapping(self, node_name, container_port, host_port):
        return self._node_manager.modify_port_mapping(
            node_name, [container_port, host_port])

    def get_port_mapping(self, node_name):
        return self._node_manager.get_port_mapping(node_name)

    def get_worker_id(self, node_name=None):
        return self._node_manager.get_node_worker_ip(node_name)

    def deploy_from_config(self, config):
        del self._topo; self._topo = Topo(**config)
        url = f"http://{self._backend_host}:{self._port}/master/topo/"
        data = {
            "user": self._user,
            "topo": self._project,
            "networks": config
        }
        response = requests.post(url, json=data)
        return http_response_handler(response)

    def create_template_topo(self, config):
        url = f"http://{self._backend_host}:{self._port}/generate"
        response = requests.post(url, json=config)

        def get_topo_config(data_json):
            return data_json["net"]
        return http_response_handler(response, get_topo_config)

    def config_public_network(self, node_name, turn_on=True):
        url = f"http://{self._backend_host}:{self._port}/node/network"
        data = {
            "user": self._user,
            "topo": self._project,
            "ne": node_name
        }
        req_func = requests.post if turn_on else requests.delete
        response = req_func(url, json=data)
        return http_response_handler(response)

    def check_public_network(self, node_name):
        ip = self._backend_host
        port = self._port
        user = self._user
        project = self._project
        url = f"http://{ip}:{port}/node/network/?user={user}&topo={project}&ne={node_name}"
        response = requests.get(url)

        def get_status(data_json):
            return data_json["status"]
        return http_response_handler(response, get_status)

    def upload_file(self, node_name, src_filepath, tgt_filepath="/home"):
        url = f"http://{self._backend_host}:{self._port}/file/uload/"
        data = {
            "user": self._user,
            "topo": self._project,
            "ne_name": node_name,
            "file_path": tgt_filepath,
            "file": open(src_filepath, "rb")
        }
        response = requests.post(url, data=data)
        return http_response_handler(response)

    def manage_worker(self, worker_ip, delete_worker=False):
        url = f"http://{self._backend_host}:{self._port}/master/worker/{worker_ip}/"
        data = {"worker_ip": worker_ip}
        req_func = requests.delete if delete_worker else requests.post
        response = req_func(url, json=data)
        return http_response_handler(response)

    def check_health(self):
        ip = self._backend_host
        port = self._port
        user = self._user
        project = self._project
        url = f"http://{ip}:{port}/master/heartbeat_health/?user={user}&project={project}"
        response = requests.get(url)

        def get_broken_nodes(data_json):
            is_broken = data_json["is_broken"]
            broken_nodes = data_json["broken_nes"]
            return is_broken, broken_nodes
        return http_response_handler(response, get_broken_nodes)
