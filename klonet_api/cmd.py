from .common import Manager

class CmdManager(Manager):
    '''命令管理类

    用于在已创建项目的节点中执行shell命令。

    Attributes:
        user(str): 用户名
        project(str): 项目名
    '''
    def __init__(self, user_name, project_name,
                backend_ip=None, backend_port=None):
        super().__init__(backend_ip, backend_port)
        self.user = user_name
        self.project = project_name

    def exec_cmds_in_nodes(self, node2cmds, block="false", timeout=60):
        """在多个节点中执行多条shell命令

        需注意，若执行较长时间阻塞的命令，如iperf3 -s，后台会执行此命令，
        但会触发超时机制，无法获取到命令的退出码及输出。

        Args:
            node2cmd(dict): 命令字典，key为节点名，value为shell命令列表。如：
                {"h1": ["ls", "ls"],"h2": ["pwd"]}

        Returns:
            一个字典，描述了节点命令执行的情况。key为节点名，value为该节点中
            具体命令的执行结果字典。比如：

            {'h1': {'ls': { "exit_code": 0, "output": "bin"}}}

        """
        payload = {
            "user": self.user,
            "topo": self.project,
            "node_and_cmd": node2cmds,
            "block": block,
            "cmd_timeout_s": timeout
        }
        resp = self._post("/master/node_exec_cmd/", json=payload)
        resp_json = self._parse_resp(resp)
        self._check_resp_code(resp_json)

        return resp_json["exec_results"]



