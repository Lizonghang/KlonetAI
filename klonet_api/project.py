import time
from .common import Manager, Topo

class ProjectManager(Manager):
    '''项目管理类

    用于项目创建、查询与删除。

    Attributes:
        user(str): 用户名
        project(str): 项目名

    '''
    def __init__(self, user_name, backend_ip=None, backend_port=None):
        super().__init__(backend_ip, backend_port)
        self.user = user_name

    def deploy(self, project_name, topo, quiet=False, timeout_min=30,
        pool_interval_s=1):
        '''创建项目，即向后台创建拓扑。

        拓扑的创建意味着一个项目的建立。创建项目的过程为：向后台发送异步拓扑创建请求，
        此时后端会立即返回请求结果；之后，本方法会持续请求进度条API并默认打印进度，
        直至进度为100%，则认为拓扑创建成功。本拓扑创建方法为推荐方法。

        Args:
            project_name(str): 项目名
            topo(Topo): Topo对象。请注意在传入Topo对象前使用Topo对象的add_node和add_link
                方法设计拓扑
            quiet(bool): 默认为False。若为False，则将打印进度；否则将关闭打印
            timeout_min(int): 超时时间（分钟）。默认为30分钟
            pool_interval_s(int): 轮询进度条API的间隔（秒）

        
        '''
        start_time = time.time()
        duration_s = 0

        self.async_deploy(project_name, topo)
        
        while duration_s <= timeout_min * 60:
            progress_value = self._get_progress(project_name, usage="deploy")
            if not quiet:
                print(f"Deployment progress: {progress_value} %")
            if progress_value == 100:
                break
            duration_s = time.time() - start_time
            time.sleep(pool_interval_s)

    def destroy(self, project_name, quiet=False, timeout_min=30,
            pool_interval_s=1):
        '''删除项目

        包含拓扑、网络实验监控服务、流量服务等该项目相关的所有内容。
        删除项目的过程为：向后台发送异步拓扑删除请求，此时后端会立即返回请求结果；之后，
        本方法会持续请求进度条API并默认打印进度，直至进度为100%，则认为项目删除成功。
        本拓扑删除方法为推荐方法。

        Args:
            project_name(str): 项目名
            quiet(bool): 默认为False。若为False，则将打印进度；否则将关闭打印。
            timeout_min(int): 超时时间（分钟）。默认为30分钟。
            pool_interval_s(int): 轮询进度条API的间隔（秒）

        Returns:
            None
        '''
        start_time = time.time()
        duration_s = 0

        self.async_destroy(project_name)
        
        while duration_s <= timeout_min * 60:
            progress_value = self._get_progress(project_name, usage="delete")
            if not quiet:
                print(f"Destruction progress: {progress_value} %")
            if progress_value == 100:
                break
            duration_s = time.time() - start_time
            time.sleep(pool_interval_s)

    def async_deploy(self, project_name, topo):
        '''向后台发送异步拓扑创建请求，令后台开始创建拓扑。

        Args:
            project_name(str): 项目名
            topo(Topo): Topo对象。请注意在传入Topo对象前使用Topo对象的add_node和add_link
                方法设计拓扑

        Returns:
            None
        '''
        payload = {"user": self.user, "topo": project_name,
            "networks": topo.dictform()}
        resp = self._post("/master/topo/", json=payload)
        self._check_resp_code(self._parse_resp(resp))

    def async_destroy(self, project_name):
        '''向后台发送异步拓扑删除请求，令后台开始删除拓扑。

        Args:
            project_name(str): 项目名

        Returns:
            None
        '''
        payload = {"user": self.user, "topo": project_name}
        resp = self._delete("/master/topo/", json=payload)
        self._check_resp_code(self._parse_resp(resp))

    def _get_progress(self, project_name, usage="deploy"):
        '''请求后端进度条API。

        Args:
            project_name(str): 项目名
            usage(str): 进度条类型（如deploy表示“拓扑创建”的进度条）

        Returns:
            一个float类型的变量，其值代表了进度值。100代表进度为100%
        '''
        payload = {"user": self.user, "topo": project_name, "usage": usage}
        resp = self._post("/master/process_bar/", json=payload)
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

        return resp_json["process_value"]

    def get_topo(self, project_name):
        '''获取目标已创建项目的Topo对象。

        Args:
            project_name(str): 项目名

        Returns:
            Topo对象
        '''
        resp = self._get(f"/re/project/{project_name}/",
            params={"user": self.user})
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

        return Topo(**resp_json["project"]["topo"])

    def deploy_with_topo_description_dict(self, project_name,
                                        topo_description_dict):
        '''使用拓扑描述字典来创建项目（不推荐）。

        此API使得用户可通过其它方式生成拓扑描述，
        再调用此API来创建项目。（拓扑描述字典实质上与Topo对象的__dict__相同。）

        Args:
            project_name(str)：项目名
            topo_description_dict(dict)：拓扑描述字典

        '''
        topo = Topo(**topo_description_dict)
        self.deploy(project_name, topo)
    
    def get_projects(self):
        '''获取用户已创建的项目列表

        Returns:
            一个列表，包含了所有已创建的项目名。如：

            ["project1", "project2", "project3", ...]
        '''
        resp = self._get(f"/re/project/",
            params={"user": self.user})
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

        return resp_json["topo_list"]