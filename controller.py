import requests
from klonet_api import *


def http_response_handler(response, func):
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


class KlonetController:

    def __init__(self):
        self._backend_host = ""
        self._port = 0
        self._project = ""
        self._user = ""
        self._image_manager = None
        self._images = []
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
        return self._images

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
            project_info = data_json.get('project', {})
            topo = project_info.get('topo', 'No topo data')
            return topo
        return http_response_handler(response, get_topo)

    @property
    def nodes(self):
        return self._topo.get_nodes()

    @property
    def links(self):
        return self._topo.get_links()

    def login(self, project_name, user_name, host_ip, port):
        self._project = project_name
        self._user = user_name
        self._backend_host = host_ip
        self._port = port
        self._image_manager = ImageManager(self._user, self._backend_host, self._port)
        self._images = self._image_manager.get_images()
        self._project_manager = ProjectManager(self._user, self._backend_host, self._port)
        self._node_manager = NodeManager(self._user, project, self._backend_host, self._port)
        self._link_manager = LinkManager(self._user, project, self._backend_host, self._port)
        self._cmd_manager = CmdManager(self._user, project, self._backend_host, self._port)

    def reset_project(self):
        self._topo = Topo()
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

    def enable_ssh_service(self, node_name):
        return self._node_manager.ssh_service(node_name, True)

    def port_mapping(self, node_name, container_port, host_port):
        return self._node_manager.modify_port_mapping(
            node_name, [container_port, host_port])

    def get_port_mapping(self, node_name):
        return self._node_manager.get_port_mapping(node_name)

    def get_worker_id(self, node_name=None):
        return self._node_manager.get_node_worker_ip(node_name)
