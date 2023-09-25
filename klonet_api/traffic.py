import json
from .common import Traffic, Manager, FlowGeneratorNotExitsError, FlowAPISchemaError, PktLengthToBigPktGen1Error
from ...webserver.schema.schema import parameter_check
from ...webserver.schema.flow_scheme import scheme_pkt_gen1, scheme_pkt_gen2, scheme_traffic_gens
from ...webserver.schema.schema import parameter_check
# from .flow_scheme import scheme_pkt_gen1, scheme_pkt_gen2, scheme_traffic_gen


# from jsonschema import validate, draft7_format_checker
# from jsonschema.exceptions import SchemaError, ValidationError

# def parameter_check(data,schema_data):
#     try:
#         validate(instance=data, schema=schema_data, format_checker=draft7_format_checker)
#     except SchemaError as e:
#         #print("验证模式schema出错:\n出错位置：{}\n提示信息：{}".format(e.path, e.message))
#         raise ValueError("验证模式schema出错:\n出错位置：{}\n提示信息：{}".format(e.path, e.message))
#     except ValidationError as e:
#         print("json数据不符合schema规定:\n出错字段：{}\n提示信息：{}".format(e.path, e.message))
#         return  {'code': 0, 'msg': "您填写的数据不符合规则，请修改! 错误信息：{}".format(e.message)}
#     else:
#         return  {'code': 1, 'msg': "schema参数检查通过！"}


class TrafficEvent():
    '''流量事件类

    用于给管理流量事件，一个流量事件中可能包含多种流

    Attributes:
        traffic_event_name(str): 要添加的流事件的名称，如f1

    '''
    def __init__(self, traffic_event_name) -> None:
        self.traffic_event_name = traffic_event_name
        self.traffic_event = {traffic_event_name:{'traffic_gen':[],
                            'pkt_gen1':[], 'pkt_gen2':[], 'trace':[]}}
        self.traffic_gen_cli_param_dict = {"EARB":"b", "RT":"t", "RN":"n", "SEED":"s"}
    
    def add_flow(self, traffic_generator, **kwargs):
        '''外部调用TrafficEvent添加不同流模式的流

        注意：目前只有三种generator可以指定

        Args:
            traffic_generator(str): 添加的流的generator
            kwargs(dict): 相关参数
        
        Returns:
            None

        Raises:
            FlowGeneratorNotExitsError: 当指定了不存在的generator时触发
        '''
        if traffic_generator == "traffic_gen":
            self.flow_add_traffic_gen(**kwargs)
        elif traffic_generator == "pkt_gen1":
            self.flow_add_pkt_gen1(**kwargs)
        elif traffic_generator == "pkt_gen2":
            self.flow_add_pkt_gen2(**kwargs)
        else:
            raise FlowGeneratorNotExitsError("请指定存在的流量generator(traffic_gen\pkt_gen1\pkt_gen2)")

    def flow_add_traffic_gen(self, **kwargs):
        '''在此流量事件中添加traffic_gen模式的流

        注意：

        Args:
            kwargs(dict): 相关参数
        
        Returns:
            None
        
        Raises:
            FlowAPISchemaError: 参数有误触发此Error
        '''
        para_check_result = parameter_check(kwargs, scheme_traffic_gen)
        if para_check_result['code'] == 1:
            flow_conf = self.get_default_para_traffic_gen(kwargs['server_list'], kwargs['client_name'])
            for key in ["req_size_dist", "dscp", "rate"]:
                if key in kwargs:
                    flow_conf["client"]["client_config"][key] = kwargs[key]
            for key in ["EARB", "RT", "RN", "SEED"]: #期望平均接收带宽、请求时间、请求个数、生成随机数的种子
                if key in kwargs:
                    flow_conf["client"]["cli_param"][key] = kwargs[key]
            self.traffic_event[self.traffic_event_name]['traffic_gen'].append(flow_conf)
        else:
            raise FlowAPISchemaError("[traffic_gen]参数有误，请参照API编程指南中流相关API确保参数正确")


    def flow_add_pkt_gen1(self, **kwargs):
        '''在此流量事件中添加pkt_gen1模式的流

        注意：

        Args:
            kwargs(dict): 相关参数
        
        Returns:
            None
        
        Raises:
            FlowAPISchemaError: 参数有误触发此Error
        '''
        para_check_result = parameter_check(kwargs, scheme_pkt_gen1)
        if para_check_result['code'] == 1:
            if "pkt_length" in kwargs:
                if kwargs["pkt_length"] > "1500":
                    raise PktLengthToBigPktGen1Error(f'''指定pkt_length为{kwargs["pkt_length"]},\
                    不满足小于1500要求''')
            if "ip_id" in kwargs:
                if kwargs["ip_id"] > "65536":
                    raise IOError("ip_id超出范围")
            flow_conf = self.get_default_para_pkt_gen12(if_pkt_gen1=True)
            for key in kwargs:
                flow_conf[key] = kwargs[key]
            self.traffic_event[self.traffic_event_name]['pkt_gen1'].append(flow_conf)
        else:
            raise FlowAPISchemaError("[pkt_gen1]参数有误，请参照API编程指南中流相关API确保参数正确")



    def flow_add_pkt_gen2(self, **kwargs):
        '''在此流量事件中添加pkt_gen2模式的流

        注意：

        Args:
            kwargs(dict): 相关参数
        
        Returns:
            None
        
        Raises:
            FlowAPISchemaError: 参数有误触发此Error
        '''
        para_check_result = parameter_check(kwargs, scheme_pkt_gen2)
        if para_check_result['code'] == 1:
            flow_conf = self.get_default_para_pkt_gen12(if_pkt_gen1=False)
            for key in kwargs:
                flow_conf[key] = kwargs[key]
            self.traffic_event[self.traffic_event_name]['pkt_gen2'].append(flow_conf)
        else:
            raise FlowAPISchemaError("[pkt_gen2]参数有误，请参照API编程指南中流相关API确保参数正确")

    def get_default_para_pkt_gen12(self, if_pkt_gen1):
        '''定义pkt_gen1或pkt_gen2的默认参数

        Args:
            if_pkt_gen1(Boolean): 是否为pkt_gen1
            src(str): 源节点
            dst(str): 目的节点
            src_ip(str): 源IP
            dst_ip(str): 目的IP
        
        Returns:
            pkt_gen1或者pkt_gen2的默认参数
        
        Raises:
            None
        '''
        flow = {
            "rate": "1",
            "duration": "10",
        }
        if if_pkt_gen1:
            pkt_gen1_para = {
                "pkt_length": "1000",
                "dist": "normal",
                "normal_scale": "0.1",
                "ip_tos": "0",
                "ip_ttl": "64",
                "ip_id": "1",
                "proto": "tcp",
                "tcp_header": {
                    "tcp_window": "1000",
                    "sport": "10000",
                    "dport": "10000"
                },
                "udp_header": {}
            }
            flow.update(pkt_gen1_para)
        else:
            pkt_gen2_para = {
                "pkt_length": {
					"1000": "1"
				},
				"on_k": "2",
				"on_min": "1",
				"off_k": "2",
				"off_min": "1"
            }
            flow.update(pkt_gen2_para)
        return flow

    def get_default_para_traffic_gen(self, server_list, client_name):
        '''定义traffic_gen的默认参数

        Args:
            server_list(list): [目的网元的主机名＋端口号]构成的数组
            client_name(str): 客户端网元名，发送网元的主机名
        
        Returns:
            traffic_gen的默认参数
        
        Raises:
            None
        '''
        flow = {
            "mode":"0", #默认为client模式非incast模式
            "server_list": server_list,
            "client": {
                "client_name": client_name,
                "client_config": {
                    "server_list": server_list,
                    "req_size_dist": {
                        "100": "0.1",
                        "200": "0.4",
                        "300": "1"
                    },
                    "dscp": {
                        "0": "50",
                        "1": "50"
                    },
                    "rate": {
                        "1Mbps": "50",
                        "2Mbps": "50"
                    }
				},
                "cli_param": {
                    "b": "1.5",
                    "t": "10",
                    "n": "",
                    "s": "1"
                }
            }
        }
        return flow
    

class TrafficManager(Manager):
    '''流量管理类
    
    用于已创建项目中的流量相关管理
    
    Attributes:
        user_name(str): 用户名
        project_name(str): 实验名
        backend_ip(str): 后端master IP
        backend_port(str): 后端master Port
    
    '''

    def __init__(self, user_name, project_name,
                backend_ip=None, backend_port=None):
        super().__init__(backend_ip, backend_port)
        self.user = user_name
        self.project = project_name
        self.traffics = {
            "user": self.user,
            "traffics":{}
        }

    def add_event(self, trafficEvent:TrafficEvent):
        '''将流数据存储到数据库中

        注意：该API仅对已创建的项目生效！

        Args:
            flow_generator(str): 流量发生器类型(pkt_gen1,pkt_gen2,traffic_gen)
            flow_name(str): 流的名称
            **kwargs(dict): 参数字典，不同流量发生器参数字典不同,详情请看操作手册

        Returns:
            None

        Raises:
            pass
        
        '''
        self.traffics['traffics'].update(trafficEvent.traffic_event)

        # print(payload)
    def save_event(self):
        """
        The save_event function saves the traffic events to the database.
        It takes no arguments and returns nothing.
        
        Args:
            self: Refer to the object of the class
        
        Returns:
            A dictionary with the key &quot;code&quot; and value 0
        
        Doc Author:
            Trelent
        """
        if self.traffics['traffics'] == {}:
            raise RuntimeError("请先使用add_event函数，添加流量事件后再存储")
        resp = self._post(f"/re/project/{self.project}/traffic_app/", self.traffics)
        self._check_resp_code(self._parse_resp(resp))

    def deploy_event(self, traffic_event_name):
        '''将已保存的流事件部署下去

        注意：需要先存储流事件，再执行部署操作

        Args:
            traffic_event_name(str): 流量事件名称

        Returns:
            None

        Raises:
            None
        '''
        payload = {"user":self.user, "topo":self.project, "app_name":traffic_event_name}
        resp = self._post("/master/traffic/", payload)
        self._check_resp_code(self._parse_resp(resp))

    def stop_event(self, traffic_event_name):
        """
        The stop_event function is used to stop a traffic event.
        
        Args:
            traffic_event_name(str): Specify the name of the traffic event that is to be stopped
        
        Returns:
            The response code
        
        Doc Author:
            Trelent
        """
        payload = {"user":self.user, "topo":self.project, "app_name":traffic_event_name}
        resp = self._delete("/master/traffic/", payload)
        self._check_resp_code(self._parse_resp(resp))

    
    def rm_event(self, traffic_event_name, force=False):
        payload = {"user":self.user}
        if force:
            self.stop_event(traffic_event_name)
        resp = self._delete(f"/re/project/{self.project}/traffic_app/{traffic_event_name}/", payload)
        self._check_resp_code(self._parse_resp(resp))

    # def get_flow_monitor_status(self):

        

