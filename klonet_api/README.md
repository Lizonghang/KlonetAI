# VEMU API

> 最后更新时间：2022/7/24

VEMU（又名：klonet）网络模拟平台的后台编程API，便于用户使用API来编写实验脚本，与VEMU
平台进行交互。

本文档设有两部分，分别面向：
- 使用API的用户
- 编写API的开发人员

(推荐使用Typora软件或VSCode的`Markdown Preview Enhance`插件阅读本文档)

[TOC]

## （面向用户的）使用说明

### 使用前提

VEMU API用于控制后端。因此使用时，需保证启动了对应的后端，且能正常与后端建立连接。

### API结构

API包含以下元素，均可通过`from vemu_api import xxx`完成引用：
- 若干基础类，包括Link、Node、Image、Topo。
  这些基础类没有预设的属性，会通过vemu平台的响应来填充自身的属性，以实现对细节的屏蔽。这些类实例化为对象后，可通过这些类的`dictform()`方法获知类的属性。
- 若干管理类，包括LinkManager、NodeManager、ImageManager、ProjectManager。
  这些管理类用于对对应的对象进行增、删、改、查等操作。初始化时需传入后端的IP地址和端口号，方可在调用时实现与后端的通信。
- 若干异常类，包括VemuExecError、HttpStatusError等。
  引用后可用于捕获特定异常。

具体的API信息（如API列表、作用、输入、输出等）可查阅文档（TODO）或代码，均有较详细的注释。

### 示例

以下以一个示例来演示VEMU API的使用方法。

示例的内容为：
- 首先设计一个两个主机、一个交换机的拓扑（`host-switch-host`），主机具有ip地址
- 设计完成拓扑之后，将拓扑创建至后台
- 在已创建的拓扑上的节点上执行一些命令，如`ls`、`ifconfig`
- 为已创建的拓扑动态添加/删除节点及链路
- 删除拓扑

本示例的代码为vemu_api_demo.py，假设与api目录在同级（文件所在位置关系到如何去import vemu_api包）。
```
---|
   |---vemu_api/
   |---vemu_api_demo.py
```

#### 1. 拓扑设计

首先需实例化各个所用到的管理类。

```python
# 用户名和项目名配置
user_name = "demo_user"
project_name = "demo_test"

# 管理类的后端ip和端口号可由参数指定（优先级高），或读取vemu_api包中
# 的配置文件（config.py）
image_manager = ImageManager(user_name)
project_manager = ProjectManager(user_name)
node_manager = NodeManager(user_name, project_name)
link_manager = LinkManager(user_name, project_name)
cmd_manager = CmdManager(user_name, project_name)
```

获取当前用户可用的镜像列表。此函数会请求后端返回一个拥有若干key-value对的字典，key为镜像名，value为镜像对象（Image对象）。

```python
images = image_manager.get_images()
```

此函数默认会打印出当前用户拥有的镜像名列表，如

```shell
demo_user have these images: ['my_ubuntu_latest', 'floodlight', 'ryu', 'l2fwd', 'ubuntu', 'snort', 'udt', 'mars', 'blockchain', 'dpdk_latest', 'quagga', 'ovs']
```

选择对应的镜像。此步骤应建立在知晓自己有哪些镜像的基础之上（即需提前运行`image_manager.get_images()`或是在前端查看自己的镜像列表。）

```python
ubuntu_image = images["ubuntu"]
ovs_image = images["ovs"]
```

实例化Topo类为Topo对象。Topo对象用于在创建拓扑前设计拓扑。

```python
topo = Topo()
```

调用Topo对象的`add_node`和`add_link`方法来进行拓扑设计。如上文所述，我们的拓扑设计目标为`host-switch-host`。在这里，我们为主机和交换机取名，即取名后的拓扑为`demo_h1-demo_s1-demo_h2`；此外，我们希望`demo_h1`的ip地址为`192.168.1.1/24`，`demo_h2`的ip地址为`192.168.1.2/24`。

首先添加节点，`add_node`方法的返回值为所添加的Node对象。

```python
demo_h1 = topo.add_node(ubuntu_image, node_name="demo_h1")
demo_h2 = topo.add_node(ubuntu_image, node_name="demo_h2")
demo_s1 = topo.add_node(ovs_image, node_name="demo_s1")
```

之后在节点之间连接链路，并配置IP。

```python
topo.add_link(demo_h1, demo_s1, link_name="demo_l1", src_IP="192.168.1.1/24")
topo.add_link(demo_s1, demo_h2, link_name="demo_l2", dst_IP="192.168.1.2/24")
```

至此，我们的拓扑已完成设计，只需将设计好的topo对象传入项目创建函数，即可在后端完成拓扑的实际创建。

#### 2. 项目创建

拓扑设计完成后，我们需调用`project_manager`的`deploy`方法将设计好的拓扑实际创建至后端（拓扑的创建也意味着一个项目的创建）。

```python
project_manager.deploy(project_name, topo)
```

此时，项目已实际创建，我们称已实际创建的项目为**已创建项目**。

#### 3. 项目获取

在某个用户已有多个项目的情况下，我们可以通过`project_manager`的`get_projects`方法获取用户已创建项目的项目名列表，以供用户查询相关信息及后续的选择使用。
```python
project_list = project_manager.get_projects()
```

#### 4. 节点获取

在某个项目中，我们可以通过`node_manager`的`get_nodes`方法获取包含所有节点名与节点对象的字典，也可以通过`get_node`方法利用节点名获取对应的节点对象。
```python
nodes_dict = node_manager.get_nodes()
temple_node = node_manager.get_node("demo_h1")
```
#### 5. 链路获取

在某个项目中，我们可以通过`link_manager`的`get_links`方法获取包含所有链路名与链路对象的字典，也可以通过`get_link`方法利用链路名获取对应的链路对象。
```python
links_dict = link_manager.get_links()
temple_link = link_manager.get_link("demo_l1")
```
#### 6. 链路配置

这里，我们对链路的属性进行配置。平台的链路配置实质上是对链路两端网卡上的TC(Linux Traffic Control)队列规则的配置。

我们将`demo_l1`的`demo_h1`侧的队列属性设置为带宽2000kbps、队列大小设置为200000字节，`demo_h2`侧的队列属性设置为带宽4000kbps，时延30000us。其它未提及属性为默认值，详见`LinkConfiguration`类的默认值。

```python
src_link_config = LinkConfiguration(bw_kbps="2000", 
        queue_size_bytes="200000", link="demo_l1", ne="demo_h1")
dst_link_config = LinkConfiguration(bw_kbps="4000", delay_us="30000",
    link="demo_l1", ne="demo_s1")
link_manager.config_link(src_link_config, dst_link_config)
```

配置完成后，也可以调用`link_manager`的`clear_link_configuration`方法清除链路配置。

```python
link_manager.clear_link_configuration("demo_l1")
```

#### 7. 命令执行

以下这句代码演示了如何在各个节点上执行指定shell命令。

```python
exec_results = cmd_manager.exec_cmds_in_nodes(
        {"demo_h1": ["ls"], "demo_h2": ["ifconfig"]})
print("exec_results: ", exec_results)
```

#### 8. 动态增删

下面，我们想要对已创建项目中的拓扑进行微调。我们称在已创建项目上的节点增加/删除和链路增加/删除操作为**动态增删**。

在这里，我们添加了一个主机节点`demo_h3`，之后在主机节点`demo_h3`和交换机节点`demo_s1`间添加了一条链路`demo_l3`，然后删除了链路`demo_l3`，最后删除了主机节点`demo_h3`。

```python
demo_h3 = node_manager.dynamic_add_node("demo_h3", ubuntu_image)

link_manager.dynamic_add_link("demo_l3", demo_h3, demo_s1, 
    src_IP="192.168.1.1/24")

link_manager.dynamic_delete_link("demo_l3")

node_manager.dynamic_delete_node("demo_h3")
```

#### 9. 删除项目

最后，我们对项目进行删除。

```python
project_manager.destroy(project_name)
```

#### 10. 完整代码

完整版代码如下，相比与前述分散代码，我们在例程中增加了一些睡眠时间（`time.sleep(20)`），供运行示例者在睡眠期间从前端查看API效果（此处仅为体验API效果，实际使用时，无需睡眠和在前端查看）。需要注意，在前端查看时，可用看到拓扑中的各个节点均在画布的左上角，这是因为示例中为了简单，未指定节点的坐标，实际使用时若有图形化查看需求，可指定节点的坐标。

```python
# vemu_api_demo.py，用于演示vemu_api的使用
from vemu_api import *
import time

if __name__ == "__main__":
    # 用户名和项目名配置
    user_name = "demo_user"
    project_name = "demo_test"
    
    # 管理类的后端ip和端口号可由参数指定（优先级高），或读取vemu_api包中
    # 的配置文件（config.py）
    image_manager = ImageManager(user_name)
    project_manager = ProjectManager(user_name)
    node_manager = NodeManager(user_name, project_name)
    link_manager = LinkManager(user_name, project_name)
    cmd_manager = CmdManager(user_name, project_name)
    
    '''拓扑设计'''
    images = image_manager.get_images()

    ubuntu_image = images["ubuntu"]
    ovs_image = images["ovs"]

    topo = Topo()
    demo_h1 = topo.add_node(ubuntu_image, node_name="demo_h1")
    demo_h2 = topo.add_node(ubuntu_image, node_name="demo_h2")
    demo_s1 = topo.add_node(ovs_image, node_name="demo_s1")
    topo.add_link(demo_h1, demo_s1, link_name="demo_l1", src_IP="192.168.1.1/24")
    topo.add_link(demo_s1, demo_h2, link_name="demo_l2", dst_IP="192.168.1.2/24")

    '''项目创建'''
    project_manager.deploy(project_name, topo)
    print(f"Deploy {project_name} successfully! Please check the effect at the "
        "frontend! Sleep 20s...")
    time.sleep(20)

    '''项目获取'''
    projects_list = project_manager.get_projects()
    print("projects_list: ", projects_list)
    time.sleep(20)

    '''节点获取'''
    nodes_dict = node_manager.get_nodes()
    print("nodes_dict: ", nodes_dict)
    temple_node = node_manager.get_node("demo_h1")
    print("temple_node: ", temple_node)
    time.sleep(20)

    '''链路获取'''
    links_dict = link_manager.get_links()
    print("links_list: ", links_dict)
    temple_link = link_manager.get_link("demo_l1")
    print("temple_link: ", temple_link)
    time.sleep(20)

    '''链路配置'''
    src_link_config = LinkConfiguration(bw_kbps="2000", 
        queue_size_bytes="200000", link="demo_l1", ne="demo_h1")
    dst_link_config = LinkConfiguration(bw_kbps="4000", delay_us="30000",
        link="demo_l1", ne="demo_s1")
    link_manager.config_link(src_link_config, dst_link_config)
    print(f"Config demo_l1 successfully! Please check the effect at the "
        "frontend! Sleep 20s...")
    time.sleep(20)
    link_manager.clear_link_configuration("demo_l1")
    print(f"Clear demo_l1 configuration successfully! Please check the effect "
        "at the frontend! Sleep 20s...")
    time.sleep(20)
    
    '''命令执行'''
    exec_results = cmd_manager.exec_cmds_in_nodes(
        {"demo_h1": ["ls"], "demo_h2": ["ifconfig"]})
    print("exec_results: ", exec_results)

    '''动态增删'''
    demo_h3 = node_manager.dynamic_add_node("demo_h3", ubuntu_image)
    print("Add demo_h3 successfully! Please check the effect at the frontend! "
        "Sleep 20s...")
    time.sleep(20) # 请在前端查看动态增加节点效果
    
    link_manager.dynamic_add_link("demo_l3", demo_h3, demo_s1, 
        src_IP="192.168.1.1/24")
    print("Add demo_l3 successfully! Please check the effect at the frontend! "
        "Sleep 20s...")
    time.sleep(20) # 请在前端查看动态增加链路效果
    
    link_manager.dynamic_delete_link("demo_l3")
    print("Delete demo_l3 successfully! Please check the effect at the "
        "frontend! Sleep 20s...")
    time.sleep(20) # 请在前端查看动态删除链路效果
    
    node_manager.dynamic_delete_node("demo_h3")
    print("Delete demo_h3 successfully! Please check the effect at the "
        "frontend! Sleep 20s...")
    time.sleep(20) # 请在前端查看动态删除节点效果

    '''项目删除'''
    project_manager.destroy(project_name)
    print(f"Destroy {project_name} successfully! Please check the effect at "
        "the frontend!")
    print("vemu_api_demo done!")
```


## （面向开发人员的）开发说明

- 注意，开发完毕后需及时对文档做修改！
- 基础类（会被管理类调用的类）应写在`base_classes.py`中
- 异常定义类应写在`errors.py`中
- 一些会被各个类调用的基础函数应写在`base_funcs.py`中
- 管理类应写在`vemu_api`目录下
- 应在`vemu_api`目录下的`__init__.py`中引用想向用户暴露的类
- 每次响应需使用`Manager`类的`_parse_resp`和`_check_resp_code`方法检查其状态码是否
  为200，以及返回值中的code是否为1
- 仿照已有的API开发是最快速的上手方式

