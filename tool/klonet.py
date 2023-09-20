from transformers import Tool
from controller import KlonetController
from klonet_api import VemuExecError, LinkInconsistentError

PROJECT_NAME = "klonetai"
USER_NAME = "wudx"
controller = KlonetController(PROJECT_NAME, USER_NAME)


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as msg:
            print(f"[Error] {msg}")

    return wrapper


class KlonetGetAllImagesTool(Tool):
    name = "klonet_get_all_images"
    description = ('''
    This method fetches a list of all image names and their associated 
    Docker Image objects.

    Args: 
        None

    Returns:
        None

    Example:
        >>> images = klonet_get_all_images()
        >>> print(images)
        {'ubuntu': <ImageObject1>, 'ovs': <ImageObject2>, ...}
    ''')

    @error_handler
    def __call__(self):
        return controller.images().keys()


class KlonetViewTopoTool(Tool):
    name = "klonet_view_topo"
    description = ('''
    Overview the current network topology on Klonet.
    
    Example:
        >>> klonet_view_topo()
    ''')

    @error_handler
    def __call__(self):
        node_info = {
            name: obj.image_name
            for name, obj in controller.nodes.items()}
        link_info = {
            name: (obj.source, obj.target)
            for name, obj in controller.links.items()}
        msg = f"Nodes: {node_info}\nLinks: {link_info}"
        print(msg)


class KlonetAddNodeTool(Tool):
    name = "klonet_add_node"
    description = ('''
    Add a node to the Klonet network. The node with position (x, y) cannot overlap with
    other nodes.
    
    Args:
        name (str): The name of the node being added. The name of this 
            new node cannot be the same as existing nodes.
        image (str): The name of Docker image used by the node.
        x (int): The x-coordinate of the node on the canvas. It should be set as an integer 
            value between 0 and 700. The agent should set this for pretty visual layout.
        y (int): The y-coordinate of the node on the canvas. It should be set as an integer 
            value between 0 and 700. The agent should set this for pretty visual layout.
        cpu_limit (int, optional): CPU utilization limit for the node, unit: %, 
            default to None, which will use the default cpu limits from the Docker image.
        mem_limit (int, optional): Memory utilization limit for the node, unit: Mbytes, 
            default to None, which will use the default memory limits from the Docker image.
    
    Returns:
        None

    Raises:
        NodeDuplicatesError: Raised when the provided node name is a duplicate.

    Example:
        >>> klonet_add_node("h1", "ubuntu", x=500, y=500, cpu_limit=1000, mem_limit=1000)
    ''')

    inputs = ["str", "str", "int", "int", "int", "int"]

    @error_handler
    def __call__(self, name: str, image: str, x: int, y: int,
                 cpu_limit: int = None, mem_limit: int = None):
        node = controller.add_node(
            name, controller.images[image], cpu_limit, mem_limit, x, y)
        print(f"A new node (name: {node.name}, image: {node.image_name}, "
              f"resource limit: {node.resource_limit}) have been added to the network.")


class KlonetRuntimeAddNodeTool(Tool):
    name = "klonet_runtime_add_node"
    description = ('''
    Add a node to the Klonet network. This tool is designed for post-deployment 
    use, allowing adding nodes to the network during runtime. The node with position 
    (x, y) cannot overlap with other nodes.
    
    Args:
        name (str): The name of the node being added. Be sure not 
            to use the same name as existing nodes.
        image (str): The name of Docker image used by the node.
        x (int): The x-coordinate of the node on the canvas. It should be set as an integer 
            value between 0 and 700. The agent should set this for pretty visual layout.
        y (int): The y-coordinate of the node on the canvas. It should be set as an integer 
            value between 0 and 700. The agent should set this for pretty visual layout.
        cpu_limit (int, optional): CPU utilization limit for the node, unit: %, 
            default to None, which will use the default cpu limits from the Docker image.
        mem_limit (int, optional): Memory utilization limit for the node, unit: Mbytes, 
            default to None, which will use the default memory limits from the Docker image.

    Returns:
        None

    Raises:
        NodeDuplicatesError: Raised when the provided node name is a duplicate.
    
    Example:
        >>> klonet_runtime_add_node("h3", "ubuntu", x=500, y=500, cpu_limit=1000, mem_limit=1000)
    ''')

    inputs = ["str", "str", "int", "int", "int", "int"]

    @error_handler
    def __call__(self, name: str, image: str, x: int, y: int,
                 cpu_limit: int = None, mem_limit: int = None):
        node = controller.add_node_runtime(
            name, controller.images[image], cpu_limit, mem_limit, x, y)
        print(f"A new node (name: {node.name}, image: {node.image_name}, "
              f"resource limit: {node.resource_limit}) have been added to the network.")


class KlonetRuntimeDeleteNodeTool(Tool):
    name = "klonet_runtime_delete_node"
    description = ('''
    Delete a node from the Klonet network by its name. This tool is designed for 
    post-deployment use, allowing deletion of nodes from the network during runtime.

    Args:
        name (str): The name of the node to delete.

    Returns:
        None

    Example:
        # Replace h1 with the name of the node you want to delete.
        >>> klonet_runtime_delete_node("h1")  
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, name: str):
        controller.delete_node_runtime(name)
        print(f"Node {name} has been removed.")


class KlonetAddLinkTool(Tool):
    name = "klonet_add_link"
    description = ('''
    Add a network link between nodes <src_node> and <dst_node> in the Klonet network.
    
    Args:
        src_node (str): The name of the source node.
        dst_node (str): The name of the destination node.
        link_name (str): The name of the link. The name of this new link cannot be 
            the same as existing links.
        src_ip (str): The source IP address. Avoid using the first two and last IP 
            addresses in the subnet. For example, avoid using 10.0.0.0, 10.0.0.1, 
            and 10.0.0.255 in the subnet 10.0.0.0/24.

    Returns:
        None
    
    Example:
        # Replace "h1", "h2", "s1" with the names of nodes you want to link.
        >>> klonet_add_link("h1", "s1", "l1", "10.0.0.2/24")
        >>> klonet_add_link("h2", "s1", "l2", "10.0.0.3/24")
    ''')

    inputs = ["str", "str", "str", "str"]

    @error_handler
    def __call__(self, src_node: str, dst_node: str, link_name: str, src_ip: str):
        src_node = controller.nodes[src_node]
        dst_node = controller.nodes[dst_node]
        link = controller.add_link(src_node, dst_node, link_name, src_ip)
        print(f"A link with name ({link.name}) was added between nodes "
              f"{link.source} (IP: {link.sourceIP}) and {link.target}")


class KlonetRuntimeAddLinkTool(Tool):
    name = "klonet_runtime_add_link"
    description = ('''
    Add a network link between nodes <src_node> and <dst_node> in the Klonet network.
    This tool is designed for post-deployment use, allowing adding links to the network 
    during runtime. 
    
    Args:
        src_node (str): The name of the source node.
        dst_node (str): The name of the destination node.
        link_name (str): The name of the link. The name of this new link cannot be 
            the same as existing links.
        src_ip (str): The source IP address. Avoid using the first two and last IP 
            addresses in the subnet. For example, avoid using 10.0.0.0, 10.0.0.1, 
            and 10.0.0.255 in the subnet 10.0.0.0/24.
    
    Returns:
        None
    
    Example:
        # Replace "h1", "h2", "s1" with the names of nodes you want to link.
        >>> klonet_add_link("h1", "s1", "l1", "10.0.0.2/24")
        >>> klonet_add_link("h2", "s1", "l2", "10.0.0.3/24")
    ''')

    inputs = ["str", "str", "str", "str"]

    @error_handler
    def __call__(self, src_node: str, dst_node: str, link_name: str, src_ip: str):
        src_node = controller.nodes[src_node]
        dst_node = controller.nodes[dst_node]
        controller.add_link_runtime(src_node, dst_node, link_name, src_ip)
        print(f"A link with name ({link_name}) was added between nodes "
              f"{src_node.name} (IP: {src_ip}) and {dst_node.name}")


class KlonetRuntimeDeleteLinkTool(Tool):
    name = "klonet_runtime_delete_link"
    description = ('''
    Delete a network link by its name. This tool is designed for post-deployment use, 
    allowing deletion of links from the network during runtime. 
    
    Args:
        name (str): The name of the link to delete.

    Returns:
        None

    Example:
        # Replace l1 with the name of the link you want to delete.
        >>> klonet_runtime_delete_link("l1")  
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, name: str):
        controller.delete_link_runtime(name)
        print(f"Link {name} has been removed.")


class KlonetDeployTool(Tool):
    name = "klonet_deploy_network"
    description = ('''
    Deploy the designed network to Klonet.
    
    Inputs:
        None

    Returns:
        None
        
    Example:
        >>> klonet_deploy_network()
    ''')

    @error_handler
    def __call__(self):
        controller.deploy()
        print(f"Deploy project {PROJECT_NAME} success.")


class KlonetDestroyProjectTool(Tool):
    name = "klonet_destroy_project"
    description = ('''
    Destroy the current project in Klonet.
    
    Inputs:
        None
    
    Returns:
        None
    
    Example:
        >>> klonet_destroy_project()
    ''')

    @error_handler
    def __call__(self):
        controller.reset_project()
        print("This project has been deleted.")


class KlonetCommandExecTool(Tool):
    name = "klonet_command_exec"
    description = ('''
    Execute the given command on the specified node.

    Args:
        node_name (str): The name of the node where the command will be executed.
        command (str): The command to execute on the specified node. Multiple 
            commands can be separated by semicolons ';', and they will be executed sequentially.

    Returns: 
        str: The output of command execution on nodes. 
    
    Example:
        >>> output = klonet_command_exec("h1", "ls; pwd")
        >>> print(output)
    ''')

    inputs = ["str", "str"]
    outputs = ["str"]

    @error_handler
    def __call__(self, node_name: str, command: str):
        response = controller.execute(node_name, command)
        return response[node_name][command]['output'].strip()


class KlonetSSHServiceTool(Tool):
    name = "klonet_enable_ssh_service"
    description = ('''
    Enable SSH service on a specified Klonet node.
    
    Args:
        node_name (str): The name of the node on which SSH service should be enabled.
    
    Returns:
        None
    
    Example:
        >>> klonet_enable_ssh_service('h1')
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, node_name: str):
        success = controller.enable_ssh_service(node_name)
        print(f"SSH service on {node_name} started {'success' if success else 'failed'}.")


class KlonetPortMappingTool(Tool):
    name = "klonet_port_mapping"
    description = ('''
    Perform port mapping for a specified Klonet node.
    
    Args:
        node_name (str): The name of the node on which a port to be mapped.
        container_port (int): The port number in the container to be mapped.
        host_port (int): The port number on the host to map to. The host port
            should be between 9200 and 40000.
    
    Returns:
        None
    
    Example:
        # Map the port 80 of the container to the port 8080 of the host.
        >>> klonet_port_mapping('h1', 80, 8080)
    ''')

    inputs = ["str", "int", "int"]

    @error_handler
    def __call__(self, node_name: str, container_port: int, host_port: int):
        success = controller.port_mapping(node_name, container_port, host_port)
        print(f"Port mapping on {node_name} is {'success' if success else 'failed'}")


class KlonetGetIPTool(Tool):
    name = "klonet_get_ip"
    description = ('''
    Retrieve the IP address of a Klonet node by its name. When you need 
    to communicate with a target host, use this tool to retrieve the 
    target IP address. For example, if h1 wants to ping h2, it should
    call klonet_get_ip('h2') to retrieve its IP address (e.g., 10.0.0.1),
    and then ping 10.0.0.1.
    
    Args:
        node_name (str): The name of the Klonet node for which you want 
            to retrieve the IP address.
    
    Returns:
        str: The IP address of the specified Klonet node.
    
    Example:
        >>> ip_address = klonet_get_ip('h1')
        >>> print(ip_address)
    ''')

    inputs = ["str"]
    outputs = ["str"]

    @error_handler
    def __call__(self, node_name: str):
        ip = controller.nodes[node_name]['interfaces'][0]['ip']
        return ip


class KlonetLinkConfigurationTool(Tool):
    name = "klonet_configure_link"
    description = ('''
    This tool allows you to customize the network link settings for a specific node,
    including bandwidth, delay, jitter, packet loss, and queue size, to simulate 
    various network conditions. 
    
    Args:
        link_name (str): The name of the link to configure.
        node_name (str): The name of the node to which the link is connected.
        bandwidth (int, optional): The desired link bandwidth in kbps (must be a 
            positive value).
        delay (int, optional): The desired link delay in microseconds (must be a 
            non-negative value).
        delay_dist (str, optional): The distribution of delay variations. Options 
            include: uniform, normal, pareto, and paretonomal.
        jitter (int, optional): The desired jitter in microseconds (must be a 
            non-negative value).
        correlation (int, optional): The percentage of jitter correlation (must 
            be a non-negative percentage).
        loss (int, optional): The desired packet loss percentage (must be a 
            non-negative percentage).
        queue_size (int, optional): The desired queue size in bytes (must be a 
            non-negative value).
    
    Returns:
        None
    
    Example:
        >>> klonet_configure_link(
                'l1', 'h1', 
                bandwidth = 1000, 
                delay = 30, 
                delay_dist = 'normal',
                jitter = 100,
                correlation = 1,
                loss = 1,
                queue_size = 200000
            )
    ''')

    inputs = ["str", "str", "int", "int", "str", "int", "int", "int", "int"]

    @error_handler
    def __call__(
        self,
        link_name: str,
        node_name: str,
        bandwidth: int = -1,
        delay: int = -1,
        delay_dist: str = "",
        jitter: int = -1,
        correlation: int = -1,
        loss: int = -1,
        queue_size: int = -1
    ):
        config = {
            "link": link_name,
            "ne": node_name,
            **({"bw_kbps": bandwidth} if bandwidth > 0 else {}),
            **({"delay_us": delay} if delay >= 0 else {}),
            **({"delay_distribution": delay_dist} if delay_dist else {}),
            **({"jitter_us": jitter} if jitter >= 0 else {}),
            **({"correlation": correlation} if correlation >= 0 else {}),
            **({"loss": loss} if loss >= 0 else {}),
            **({"queue_size_bytes": queue_size} if queue_size >= 0 else {}),
        }
        # Reset the link configuration before modifying it.
        controller.reset_link(link_name, clean_cache=False)
        merged_config = controller.configure_link(config)
        print(f"Link {link_name} (on the {node_name} side) is configured "
              f"with: {merged_config}")


class KlonetResetLinkConfigurationTool(Tool):
    name = "klonet_reset_link"
    description = ('''
    Reset the configuration of a given network link.
    
    Args:
        link_name (str): The name of the link to reset.

    Returns:
        None
    
    Example:
        >>> klonet_reset_link('l1')
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, link_name: str):
        controller.reset_link(link_name, clean_cache=True)
        print(f"Link {link_name} has been reset.")
