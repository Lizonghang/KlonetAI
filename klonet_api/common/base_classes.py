import requests
import copy
from .. import config
from .base_funcs import cidr2ip_and_netmask, get_plural_of_words
from .errors import *


'''基础类'''

class Manager(object):
    '''vemu api的manager基类
    
    提供：1. 后端ip和端口的配置。
    2. 基本的post/get等请求方式的封装。
    3. 对response的解析。

    Attributes:
        backend_ip(str): 后端服务器IP
        backend_port(int): 后端服务器端口
        url(str): 请求url
    '''
    def __init__(self, backend_ip=None, backend_port=None):
        if not backend_ip or not backend_port:
            try:
                backend_ip, backend_port = config.backend_ip, config.backend_port
            except AttributeError:
                raise ValueError("Please config backend_ip and backend_port by "
                "function args or config.py!")
        self.url = (f"http://{backend_ip}:{backend_port}")

    def _post(self, url_suffix, json=None, data=None):
        return requests.post(url=f"{self.url}{url_suffix}", 
            json=json, data=data)

    def _delete(self, url_suffix, json=None, data=None):
        return requests.delete(url=f"{self.url}{url_suffix}", 
            json=json, data=data)

    def _put(self, url_suffix, json=None, data=None):
        return requests.put(url=f"{self.url}{url_suffix}", 
            json=json, data=data)

    def _get(self, url_suffix, json=None, data=None, params=None):
        return requests.get(url=f"{self.url}{url_suffix}", 
            json=json, data=data, params=params)

    def _parse_resp(self, response):
        '''对response对象进行解析，返回其json格式。

        同时该函数会对response的状态码进行校验，若状态码不是200，则会抛出异常。

        Args:
            response(Response): requests库的Response对象

        Returns:
            返回response.json()

        Raises:
            HttpStatusError: 当HTTP的返回状态码不为200时，触发此异常
            JsonDecodeError: 当返回体不包含json时，触发此异常
        '''
        if response.status_code != 200:
            raise HttpStatusError(f"HTTP status code is not 200. "
                f"response.status_code = {response.status_code}, "
                f"response.text = {response.text}")

        response_json = None
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            raise JsonDecodeError(f"The response does not contain valid json. "
                f"response.status_code = {response.status_code}, "
                f"response.text = {response.text}")

        return response_json

    def _check_resp_code(self, resp_json, code_field="code", success_code=1,
                        msg_filed="msg"):
        '''检查response json中的code

        若code不为success_code，则抛出异常

        Args:
            resp_json(dict): 响应response的json，例子:
                {"code": 1,
                "msg": "success!"
                }
            code_filed(str): 响应response的json中记录code的key
            success_code(int): 执行成功的code
            msg_filed(str): 响应response的json中记录提示信息的key

        Raises:
            VemuExecError: 当HTTP请求成功，但json中的返回码不为1时，触发此异常
        '''
        if resp_json[code_field] != success_code:
            raise VemuExecError(f"Return code={resp_json[code_field]} after vemu "
                f"execute this request, msg: {resp_json[msg_filed]}")

class Dict2Class(object):
    '''镜像、节点、链路等的基类'''
    # https://stackoverflow.com/a/1305663
    def __init__(self, **properties):
        self.__dict__.update(properties)

    def dictform(self):
        return self.__dict__

class Image(Dict2Class):
    '''镜像类

    需要传字典来确定其拥有的属性，要查看实例化对象所具有的属性，请调用dictform()方法
    '''
    def __init__(self, **properties):
        super().__init__(**properties)

class Node(Dict2Class):
    '''节点类

    需要传字典来确定其拥有的属性要查看实例化对象所具有的属性，请调用dictform()方法
    '''
    def __init__(self, **properties):
        super().__init__(**properties)

class Link(Dict2Class):
    '''链路类

    需要传字典来确定其拥有的属性要查看实例化对象所具有的属性，请调用dictform()方法
    '''
    def __init__(self, **properties):
        super().__init__(**properties)

class Topo(Dict2Class):
    '''拓扑类

    用于项目创建前通过类中的add_node和add_link方法设计拓扑，设计完成后需将Topo对
    象传入TopoManager的deploy方法，以完成实际的项目创建。
    '''
    def __init__(self, **properties):
        self.__dict__ = {} # topo结构的维护是由拓扑对象中的字典来实现
        elements = ["links", "controllers", "hosts", "routers", "switches"]
        for element in elements:
            self.__dict__.setdefault(element, {})
        super().__init__(**properties)

    def add_node(self, image, node_name=None, resource_limit=None,
            location={"x": 0, "y": 0}, worker_specified=None):
        '''向Topo对象中添加节点。

        Args:
            image(Image): 节点所用镜像的Image对象，需先通过镜像相关API获取
            node_name(str): 所添加节点的名称。
            resource_limit(dict): 资源限制。例子：
                {"cpu": "1000", # CPU利用率限制，单位：%
                "mem": "1000" # 内存限制，单位：Mbytes
                }
                默认为None，将采用镜像中的默认资源限制。
            location(dict): 在前端画布上的横纵坐标，x和y均应该大于等于0。例子：
                {"x": 0,
                "y": 0
                }
                默认值同样为{"x":0, "y":0}

        Returns:
            所添加节点的Node对象，便于后续直接对其进行相关操作

        Raises:
            NodeDuplicatesError: 当所添加的节点名重复时，触发此异常
        '''   
        # 默认名称分配
        if not node_name:
            node_name = self._assign_default_node_name()

        # 名称重复检查
        nodes = self.get_nodes()
        if node_name in nodes.keys():
            raise NodeDuplicatesError(f"node name [{node_name}] is duplicate, "
                f"existing node names are {list(nodes.keys())}")

        # node对象构建
        node = copy.deepcopy(image) # 将image对象当作node对象使用
        if resource_limit:
            node.resource_limit = resource_limit
        node.name = node_name
        node.x = location["x"]
        node.y = location["y"]

        if worker_specified:
            node.config.update({"worker_specified": worker_specified})

        # 加入topo的字典中
        category = get_plural_of_words(node.type)
        self.__dict__[category][node_name] = node.dictform()

        return Node(**node.dictform())

    def add_link(self, src_node, dst_node, link_name=None, src_IP="",
        dst_IP=""):
        '''向Topo对象中添加链路

        参数中的源和目的仅用于区分不同的两端，不含有方向的意思，链路为双向链路

        Args:
            src_node(Node): 源节点的Node对象
            dst_node(Node): 目的节点的Node对象
            link_name(str): 要添加的链路名，例如"link1"，默认为None，默认情况下会将链路命
                名为"l<拓扑中现有链路数量+1>"
            src_IP(str): 源节点的IP地址，例如"192.168.1.1/24"，默认为""
            dst_IP(str): 目的节点的IP地址，例如"192.168.1.2/24"，默认为""

        Returns:
            所添加链路的Link对象，便于后续直接对其进行相关操作
        '''
        # 参数检查
        if src_node.name == dst_node.name:
            raise ValueError(f"Node cannot connect to itself!")
        if src_IP != "":
            cidr2ip_and_netmask(src_IP)
        if dst_IP != "":
            cidr2ip_and_netmask(dst_IP)

        # 默认名称分配
        if not link_name:
            link_name = self._assign_default_link_name()

        # 检查平行边
        self._check_parallel_link(link_name, src_node.name, dst_node.name)

        # 名称重复检查
        links = self.get_links()
        if link_name in links.keys():
            raise LinkDuplicatesError(f"link name [{link_name}] is duplicate, "
                f"existing link names are {list(links.keys())}")

        # 构建Link对象并将其加入Topo中
        link = Link()
        link.config = {
            "source" : {
                "bw_kbit" : "",
                "queue_size_byte" : "",
                "delay_us" : "",
                "loss_rate" : "", 
                "jitter_us" : "", 
                "correlation" : "", 
                "delay_distribution" : "normal"
            },
            "target":{
                "bw_kbit" : "",
                "queue_size_byte" : "",
                "delay_us" : "",
                "loss_rate" : "", 
                "jitter_us" : "", 
                "correlation" : "", 
                "delay_distribution" : "normal"
            }
        }
        link.name = link_name
        link.source = src_node.name
        link.sourceIP = src_IP
        link.sourceType = src_node.type
        link.target = dst_node.name
        link.targetIP = dst_IP
        link.targetType = dst_node.type

        self.__dict__["links"][link.name] = link.dictform()

        # 修改节点信息
        if src_IP != "":
            ip, netmask = cidr2ip_and_netmask(src_IP)
            nic_nickname = f"{src_node.name}{dst_node.name}"
            category = get_plural_of_words(src_node.type)
            self.__dict__[category][src_node.name]["interfaces"].append(
                {"ip": ip, "netmask": netmask, "name": nic_nickname})

        if dst_IP != "":
            ip, netmask = cidr2ip_and_netmask(dst_IP)
            nic_nickname = f"{dst_node.name}{src_node.name}"
            category = get_plural_of_words(dst_node.type)
            self.__dict__[category][dst_node.name]["interfaces"].append(
                {"ip": ip, "netmask": netmask, "name": nic_nickname})

        return link

    def get_nodes(self):
        '''获取Topo对象中所有的节点名及对应的Node对象

        Returns:
            一个字典，包含该Topo对象中所有的节点名及对应的Node对象。例子：
            {"h1": h1的Node对象,
            ...
            }
        '''
        nodes = {}
        for type in self.__dict__.keys():
            if type == "links":
                continue
            for node_name, node_dict in self.__dict__[type].items():
                nodes[node_name] = Node(**node_dict)
        
        return nodes

    def get_links(self):
        '''
        获取Topo对象中所有的链路名及对应的Link对象

        Returns:
            一个字典，包含该Topo对象中所有的链路名及对应的Link对象。例子：

            {"l1": l1的Node对象,
            ...
            }
        '''
        links = {}
        for link_name, link_dict in self.__dict__["links"].items():
            links[link_name] = Link(**link_dict)
        
        return links

    def _assign_default_link_name(self):
        '''分配默认链路名

        默认链路名为"l<拓扑中现有链路数量+1>"
        '''
        link_num = len(self.get_links())
        link_name = f"l{link_num+1}"
        return link_name

    def _assign_default_node_name(self):
        '''分配默认节点名

        默认节点名为"n<拓扑中现有链路数量+1>"
        '''
        node_num = len(self.get_nodes())
        node_name = f"n{node_num+1}"
        return node_name

    def _check_parallel_link(self, link_name, src_node_name, dst_node_name):
        '''检查新添加的链路是否为平行边（即新链路与已有链路的两端节点名相同）

        Args:
            src_node_name(str): 链路的源节点名
            dst_node_name(str): 链路的目的节点名

        Raises:
            LinkParallelError: 当出现平行边（即新边与已有边的两端节点名相同）时，触发
                该异常
        '''
        links = self.get_links()
        my_endpoints = set([src_node_name, dst_node_name])
        for _, link in links.items():
            exist_endpoints = set([link.source, link.target])
            if my_endpoints == exist_endpoints:
                raise LinkParallelError(f"New link {link_name}({src_node_name}"
                    f"---{dst_node_name}) repeat with exist link {link.name}"
                    f"({link.source}---{link.target})")

class LinkConfiguration(Dict2Class):
    '''链路配置类。

    默认的属性及说明为：
    "bw_kbps":"10000", # 链路带宽（kbps）,需为正数
    "delay_us":"0", # 链路时延(us)，需为非负数
    "jitter_us":"0", # 时延抖动(us)，需为非负数
    "correlation":"0%", # 抖动相关率(%)，需为非负百分率，如1%
    "delay_distribution":"uniform", # 时延抖动分布，可选项：uniform/normal/pareto/paretonomal
    "loss":"0", # 链路丢包率(%)，需为非负数，如1
    "queue_size_bytes":"100000", # 队列大小(字节)，需为非负数，如10000
    "linkchoice":"static", # 固定为static，无需改变
    "link":None, # 链路名
    "ne":None # 节点名
    '''
    def __init__(self, **properties):
        default_config = {
            "bw_kbps":"10000", # 链路带宽（kbps）,需为正数
            "delay_us":"0", # 链路时延(us)，需为非负数
            "jitter_us":"0", # 时延抖动(us)，需为非负数
            "correlation":"0%", # 抖动相关率(%)，需为非负百分率，如1%
            "delay_distribution":"uniform", # 时延抖动分布，可选项：uniform/normal/pareto/paretonomal
            "loss":"0", # 链路丢包率(%)，需为非负数，如1
            "queue_size_bytes":"100000", # 队列大小(字节)，需为非负数，如10000
            "linkchoice":"static", # 固定为static，无需改变
            "link":None, # 链路名
            "ne":None # 节点名
        }
        self.__dict__ = default_config
        super().__init__(**properties)