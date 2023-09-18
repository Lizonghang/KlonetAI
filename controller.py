from klonet_api import *


class KlonetController:

    def __init__(self, project, user):
        self._backend_host = "kb310server.f3322.net"
        self._port = 12313
        self._project = project
        self._user = user

        self._image_manager = ImageManager(user, self._backend_host, self._port)
        self._images = self._image_manager.get_images()
        self._project_manager = ProjectManager(user, self._backend_host, self._port)
        self._node_manager = NodeManager(user, project, self._backend_host, self._port)
        self._link_manager = LinkManager(user, project, self._backend_host, self._port)
        self._cmd_manager = CmdManager(user, project, self._backend_host, self._port)
        self._topo = Topo()

    @property
    def images(self):
        return self._images

    @property
    def topo(self):
        return self._topo

    @property
    def nodes(self):
        return self._topo.get_nodes()

    @property
    def links(self):
        return self._topo.get_links()

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

    def deploy(self):
        self._project_manager.deploy(self._project, self._topo)

    def execute(self, node_name, command):
        response = self._cmd_manager.exec_cmds_in_nodes({
            node_name: [command]
        })
        return response
