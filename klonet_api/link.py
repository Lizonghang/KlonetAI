from .common import Manager, Link, LinkNotExistsError, LinkParallelError, LinkInconsistentError, cidr2ip_and_netmask

class LinkManager(Manager):
    '''链路管理类

    用于已创建项目中的链路相关管理。

    Attributes:
        user(str): 用户名
        project(str): 项目名

    '''
    def __init__(self, user_name, project_name,
                backend_ip=None, backend_port=None):
        super().__init__(backend_ip, backend_port)
        self.user = user_name
        self.project = project_name

    def dynamic_add_link(self, link_name, src_node, dst_node, src_IP="",
        dst_IP=""):
        '''动态添加链路

        注意：该API仅对已创建项目生效！
        （参数中的源和目的仅用于区分不同的两端，不含有方向的意思，链路为双向链路）

        Args:
            link_name(str): 要添加的链路名
            src_node(Node): 源节点的Node对象
            dst_node(Node): 目的节点的Node对象
            src_IP(str): 源节点的IP地址，例如"192.168.1.1/24"，默认为""
            dst_IP(str): 目的节点的IP地址，例如"192.168.1.2/24"，默认为""

        Returns:
            None

        Raises:
            HttpStatusError: 当HTTP的返回状态码不为200时，触发此异常
            JsonDecodeError: 当返回体不包含json时，触发此异常
            VemuExecError: 当HTTP请求成功，但json中的返回码不为1时，触发此异常
            LinkParallelError: 当出现平行边（即新边与已有边的两端节点名相同）时，触发
                此异常
        '''
        # 参数检查
        if src_node.name == dst_node.name:
            raise ValueError(f"Node cannot connect to itself!")
        if src_IP != "":
            cidr2ip_and_netmask(src_IP)
        if dst_IP != "":
            cidr2ip_and_netmask(dst_IP)

        # 检查平行边
        self._check_parallel_link(link_name, src_node.name, dst_node.name)

        # 创建链路
        payload = {
            "user": self.user,
            "topo": self.project,
            "info": {
                "config": {
                    "source": {"bw_kbit":"", "queue_size_byte":"", "delay_us":"",
                        "loss_rate":"", "jitter_us":"", "correlation":"",
                        "delay_distribution":"normal"},
                    "target":{"bw_kbit":"", "queue_size_byte":"", "delay_us":"",
                        "loss_rate":"", "jitter_us":"", "correlation":"",
                        "delay_distribution":"normal"}
                }
            }
        }
        payload["info"]["name"] = link_name
        payload["info"]["source"] = src_node.name
        payload["info"]["sourceIP"] = src_IP
        payload["info"]["sourceType"] = src_node.type
        payload["info"]["target"] = dst_node.name
        payload["info"]["targetIP"] = dst_IP
        payload["info"]["targetType"] = dst_node.type

        resp = self._post("/modification/link/", json=payload)
        self._check_resp_code(self._parse_resp(resp))

        # 修改节点信息
        if src_IP != "":
            ip, netmask = cidr2ip_and_netmask(src_IP)
            print(netmask)
            nic_nickname = f"{src_node.name}{dst_node.name}"
            src_node.interfaces.append({"ip": ip, "netmask": netmask, 
                "name": nic_nickname})
            payload = {}
            payload = {"user": self.user, "topo": self.project, 
                "info": src_node.dictform()}
            resp = self._put("/modification/container/", json=payload)
            self._check_resp_code(self._parse_resp(resp))

        if dst_IP != "":
            ip, netmask = cidr2ip_and_netmask(dst_IP)
            nic_nickname = f"{dst_node.name}{src_node.name}"
            dst_node.interfaces.append({"ip": ip, "netmask": netmask, 
                "name": nic_nickname})
            payload = {}
            payload = {"user": self.user, "topo": self.project, 
                "info": dst_node.dictform()}
            resp = self._put("/modification/container/", json=payload)
            self._check_resp_code(self._parse_resp(resp))

    def dynamic_delete_link(self, link_name):
        '''动态删除节点。
        
        注意：该API仅对已创建项目生效！

        Args:
            node_name(str): 要删除节点名

        Returns:
            None

        Raises:
            HttpStatusError: 当HTTP的返回状态码不为200时，触发此异常
            JsonDecodeError: 当返回体不包含json时，触发此异常
            VemuExecError: 当HTTP请求成功，但json中的返回码不为1时，触发此异常
        '''
        link = self.get_link(link_name)

        payload = {"user": self.user, "topo": self.project, 
            "info": link.__dict__}
        resp = self._delete("/modification/link/", json=payload)
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

    def config_link(self, src_link_config, dst_link_config):
        '''配置链路属性。

        链路属性底层使用linux traffic control(tc)实现，因此链路属性实质上是对链路两侧
        节点上网卡的队列的配置，从网卡发出的数据包将经过配置的队列。

        Args:
            src_link_config(LinkConfiguration): 链路源端的LinkConfiguration对象
            dst_link_config(LinkConfiguration): 链路目的端的LinkConfiguration对象

        Returns:
            None

        Raises:
            LinkInconsistentError: 当链路属性配置时，链路两端的LinkConfiguration
                对象的链路名不一致时，触发该异常。
        '''
        # 是否是同一条链路检查
        if src_link_config.link != dst_link_config.link:
            raise LinkInconsistentError(f"src_link_config.link("
                f"{src_link_config.link}) is inconsistent with "
                f"dst_link_config.link({dst_link_config.link}), please check!")

        src_link_config.link = f"link_{src_link_config.link}"
        dst_link_config.link = f"link_{dst_link_config.link}"
        payload = {
            "user": self.user,
            "topo": self.project,
            "links": [src_link_config.dictform(), dst_link_config.dictform()]
        }

        resp = self._post('/master/link/', json=payload)
        print(self._parse_resp(resp))
        self._check_resp_code(self._parse_resp(resp))
        

    def clear_link_configuration(self, link_name):
        '''清除链路上的队列配置。

        Args:
            link_name(str): 链路名

        Returns:
            None
        '''
        link = self.get_link(link_name)
        payload = {
            "user": self.user,
            "topo": self.project,
            "links": [
                {
                    "link": f"link_{link_name}",
                    "linkchoice": "static",
                    "ne": link.source
                },
                {
                    "link": f"link_{link_name}",
                    "linkchoice": "static",
                    "ne": link.target
                }
            ]
        }
        resp = self._delete("/master/link/", json=payload)
        self._check_resp_code(self._parse_resp(resp))

    def get_links(self):
        '''获取该项目下所有的链路名及对应的Link对象

        Returns:
            一个字典，包含该项目所有的链路名及对应的Link对象。比如：

            {"l1": l1的Link对象,"l2": l2的Link对象}

        '''
        resp = self._get(f"/re/project/{self.project}/",
            params={"user": self.user})
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

        links = {}
        for link_name, link_dict in resp_json["project"]["topo"][
            "links"].items():
            links[link_name] = Link(**link_dict)

        return links

    def get_link(self, link_name):
        '''获取目标链路的Link对象。

        Args:
            link_name(str): 链路名

        Returns:
            目标链路的Link对象。

        Raises:
            HttpStatusError: 当HTTP的返回状态码不为200时，触发此异常
            JsonDecodeError: 当返回体不包含json时，触发此异常
            VemuExecError: 当HTTP请求成功，但json中的返回码不为1时，触发此异常
            LinkNotExistsError: 当目标链路不存在时，触发此异常
        '''
        links = self.get_links()
        try:
            link = links[link_name]
            return link
        except KeyError:
            raise LinkNotExistsError(f"Link [{link_name}] does not exist, "
                f"avaliable links are {list(links.keys())}")

    def _check_parallel_link(self, link_name, src_node_name, dst_node_name):
        '''检查新添加的链路是否为平行边（即新链路与已有链路的两端节点名相同）

        Args:
            src_node_name(str): 链路的源节点名
            dst_node_name(ste)：链路的目的节点名

        Returns:
            None。

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

