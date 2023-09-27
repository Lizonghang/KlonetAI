from transformers import Tool
from klonetai import KlonetAI, error_handler


kai = KlonetAI()


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
        >>> klonet_get_all_images()
    ''')

    @error_handler
    def __call__(self):
        kai.images.keys()


class KlonetViewTopoTool(Tool):
    name = "klonet_view_topo"
    description = ('''
    Overview the current network topology on Klonet backend.
    
    Example:
        >>> klonet_view_topo()
    ''')

    @error_handler
    def __call__(self):
        result = kai.remote_topo
        print(result)


class KlonetAddNodeTool(Tool):
    name = "klonet_add_node"
    description = ('''
    Add a node to the Klonet network. The node with position (x, y) cannot overlap with
    other nodes.
    
    Args:
        name (str): The name of the node being added. The name of this new node cannot be 
            the same as existing nodes.
        image (str): The name of Docker image used by the node. Use the klonet_get_all_images
            tool to see the available images.
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
        # Add a ubuntu host named h1.
        >>> klonet_add_node("h1", "ubuntu", x=500, y=500)
        # Add an OVS switch named s1.
        >>> klonet_add_node("s1", "ovs", x=500, y=500)
    ''')

    inputs = ["str", "str", "int", "int", "int", "int"]

    @error_handler
    def __call__(self, name: str, image: str, x: int, y: int,
                 cpu_limit: int = None, mem_limit: int = None):
        node = kai.add_node(
            name, kai.images[image], cpu_limit, mem_limit, x, y)
        print(f"A new node (name: {node.name}, image: {node.image_name}, "
              f"resource limit: {node.resource_limit}) have been added to the network.")


class KlonetRuntimeAddNodeTool(Tool):
    name = "klonet_runtime_add_node"
    description = ('''
    Add a node to the Klonet network. This tool is designed for post-deployment 
    use, allowing adding nodes to the network during runtime. The node with position 
    (x, y) cannot overlap with other nodes.
    
    Args:
        name (str): The name of the node being added. Be sure not to use the same name as 
            existing nodes.
        image (str): The name of Docker image used by the node. Use the klonet_get_all_images
            tool to see the available images.
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
        # Add a ubuntu host named h2.
        >>> klonet_runtime_add_node("h2", "ubuntu", x=500, y=500)
        # Add an OVS switch named s1.
        >>> klonet_runtime_add_node("s2", "ovs", x=500, y=500)
    ''')

    inputs = ["str", "str", "int", "int", "int", "int"]

    @error_handler
    def __call__(self, name: str, image: str, x: int, y: int,
                 cpu_limit: int = None, mem_limit: int = None):
        node = kai.add_node_runtime(
            name, kai.images[image], cpu_limit, mem_limit, x, y)
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
        kai.delete_node_runtime(name)
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
        src_node = kai.nodes[src_node]
        dst_node = kai.nodes[dst_node]
        link = kai.add_link(src_node, dst_node, link_name, src_ip)
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
        src_node = kai.nodes[src_node]
        dst_node = kai.nodes[dst_node]
        kai.add_link_runtime(src_node, dst_node, link_name, src_ip)
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
        kai.delete_link_runtime(name)
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
        kai.deploy()
        print(f"Deploy project {kai.project_name} success.")


class KlonetCheckDeployedTool(Tool):
    name = "klonet_check_deployed"
    description = ('''
    Check whether the network is deployed on remote Klonet backend. 
    Run this tool to confirm whether some operations can be performed. 
    
    Args:
        None
    
    Returns:
        bool: True if the network has been deployed, False otherwise.
    
    Example:
        >>> is_deployed = klonet_check_deployed()
        >>> print(f"Is this project deployed: {is_deployed}.")
    ''')

    outputs = ["bool"]

    @error_handler
    def __call__(self):
        return kai.check_deployed()


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
        kai.reset_project()
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
        None
    
    Example:
        >>> klonet_command_exec("h1", "ls; pwd")
    ''')

    inputs = ["str", "str"]

    @error_handler
    def __call__(self, node_name: str, command: str):
        response = kai.execute(node_name, command)
        print(response[node_name][command]['output'].strip())


class KlonetBatchCommandExecTool(Tool):
    name = "klonet_batch_command_exec"
    description = ('''
    Execute the given command on batched nodes.
    
    Args:
        node_list (list): A list of target nodes where the command will be executed.
        node_type (str): The type of nodes, could be: "all", "specified_ctn_type", 
            or "specified_ctn_list".
            - When node_type is "all", the command is executed on all nodes, and 
                node_list should be empty.
            - When node_type is "specified_ctn_type", the nodes are selected by their
                type, and the selected nodes should execute the command. The types 
                include: "hosts", "controllers", "routers", and "switches". For example,
                when node_list is ["hosts"], all host nodes should execute the command.
            - When node_type is "specified_ctn_list", the nodes are selected by their
                name, and the selected nodes should execute the command. For example, 
                when node_list is ["h1", "s1"], the nodes h1 and s1 should execute the
                command.
        command (str): The command to be executed on the selected nodes. Multiple 
            commands can be separated by semicolons ';', and they will be executed 
            sequentially.
    
    Returns:
        None
        
    Example:
        # Case 1: Run a command on all nodes.
        >>> klonet_batch_command_exec([], "all", "ifconfig")
        # Case 2: Run a command on all host nodes.
        >>> klonet_batch_command_exec(["hosts"], "specified_ctn_type", "ifconfig")
        # Case 3: Run a command on the selected nodes.
        >>> klonet_batch_command_exec(["h1", "s1"], "specified_ctn_list", "ifconfig")
    ''')

    inputs = ["list", "str", "str"]

    @error_handler
    def __call__(self, node_list: list, node_type: str, command: str):
        ctns = {"list_type": node_type, "list": node_list}
        result = kai.batch_exec(ctns, command)
        print(result)


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
        success = kai.enable_ssh_service(node_name)
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
        success = kai.port_mapping(node_name, container_port, host_port)
        print(f"Port mapping on {node_name} {'success' if success else 'failed'}.")


class KlonetGetPortMappingTool(Tool):
    name = "klonet_get_port_mapping"
    description = ('''
    Show the port map for a given node. 
    
    Args:
        node_name (str): The name of the node to query.
    
    Returns:
        None
    
    Example:
        >>> klonet_get_port_mapping()
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, node_name: str):
        result = kai.get_port_mapping(node_name)
        print(f"Port map: {result['ne_port']}")


class KlonetGetIPTool(Tool):
    name = "klonet_get_ip"
    description = ('''
    Retrieve the IP address of a Klonet node by its name. When you need 
    to communicate with a target host, use this tool to retrieve the 
    target IP address. For example, if h1 wants to ping h2, it should
    call klonet_get_ip('h2') to retrieve its IP address (e.g., 10.0.0.3),
    and then ping 10.0.0.3.
    
    Args:
        node_name (str): The name of the Klonet node for which you want 
            to retrieve the IP address.
    
    Returns:
        str: The IP address of the specified node.
    
    Example:
        >>> ip_address = klonet_get_ip('h1')
        >>> print(ip_address)
    ''')

    inputs = ["str"]
    outputs = ["str"]

    @error_handler
    def __call__(self, node_name: str):
        return kai.nodes[node_name].interfaces[0]['ip']


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
        kai.reset_link(link_name, clean_cache=False)
        merged_config = kai.configure_link(config)
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
        kai.reset_link(link_name, clean_cache=True)
        print(f"Link {link_name} has been reset.")


class KlonetLinkQueryTool(Tool):
    name = "klonet_link_query"
    description = ('''
    Query information about a link.
    
    Args:
        link_name (str): The name of the link to query.
        node_name (str): The name of the node associated with the link to query.
    
    Returns:
        dict: A dictionary containing information about the queried link.
    
    Example:
        >>> link_info = klonet_link_query("l1", "h1")
    ''')

    inputs = ["str", "str"]
    outputs = ["dict"]

    def __call__(self, link_name: str, node_name: str):
        return kai.query_link(link_name, node_name)


class KlonetGetWorkerIPTool(Tool):
    name = "klonet_get_worker_ip"
    description = ('''
    Show the worker IP for a given node. The worker IP is the IP address 
    of the host machine where the given node is deployed on.

    Args:
        node_name (str, optional): The name of the node to query. If given,
            query only the given node. If not given, query the worker IP of
            all the nodes.

    Returns:
        None

    Example:
        >>> klonet_get_worker_ip()
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, node_name: str = None):
        result = kai.get_worker_id(node_name)
        print(f"Worker IP: {result}")


class KlonetTreeTopoTemplate(Tool):
    name = "klonet_tree_topo_template"
    description = ('''
    Deploy a tree network topology on Klonet. Do not call the
    klonet_deploy_network tool if you use this template.
    
    Args:
        subnet (str): The subnet to deploy the topology.
        ndepth (int, optional): The depth of the tree (default is 2).
        nbranch (int, optional): The number of branches at each level 
            (default is 2).
        density (int, optional): The number of hosts connected to each 
            leaf switch (default is 2).
    
    Returns:
        None
    
    Example:
        >>> klonet_tree_topo_template("192.168.1.0/24", ndepth=2, nbranch=2, density=1)
    ''')

    inputs = ["str", "int", "int", "int"]

    @error_handler
    def __call__(self, subnet: str, ndepth: int = 2, nbranch: int = 2, density: int = 1):
        print("[Warning] This operation will overwrite the existing topology.")
        kai.reset_project()
        print("[Warning] Creating topology in this way will not layout the view.")
        params_config = {
            "topology_type": "tree",
            "tree_depths": ndepth,
            "tree_branches": nbranch,
            "tree_host_density": density,
            "host_counter": 1,
            "switch_counter": 1,
            "link_counter": 1,
            "ip_prefix": subnet
        }
        net_config = kai.create_template_topo(params_config)
        result = kai.deploy_from_config(net_config)
        print(result)


class KlonetStarTopoTemplate(Tool):
    name = "klonet_star_topo_template"
    description = ('''
    Deploy a star network topology on Klonet. Do not call the
    klonet_deploy_network tool if you use this template.
    
    Args:
        subnet (str): The subnet to deploy the topology.
        nstar (str, optional): The number of host nodes (default is 3).
    
    Returns:
        None
    
    Example:
        >>> klonet_star_topo_template("192.168.1.0/24", nstar=3)
    ''')

    inputs = ["str", "int"]

    @error_handler
    def __call__(self, subnet: str, nstar: int = 3):
        print("[Warning] This operation will overwrite the existing topology.")
        kai.reset_project()
        print("[Warning] Creating topology in this way will not layout the view.")
        params_config = {
            "topology_type": "star",
            "star_n": nstar,
            "host_counter": 1,
            "switch_counter": 1,
            "link_counter": 1,
            "ip_prefix": subnet
        }
        net_config = kai.create_template_topo(params_config)
        result = kai.deploy_from_config(net_config)
        print(result)


class KlonetFatTreeTopoTemplate(Tool):
    name = "klonet_fattree_topo_template"
    description = ('''
    Deploy a Fat-Tree network topology template on Klonet. Do not call the
    klonet_deploy_network tool if you use this template.
    
    Args:
        subnet (str): The subnet to deploy the topology.
        npod (int, optional): The number of pods of the Fat-Tree (default is 4).
    
    Returns:
        None
        
    Example:
        >>> klonet_fattree_topo_template("192.168.1.0/24", npod=2)
    ''')

    inputs = ["str", "int"]

    @error_handler
    def __call__(self, subnet: str, npod: int = 4):
        print("[Warning] This operation will overwrite the existing topology.")
        kai.reset_project()
        print("[Warning] Creating topology in this way will not layout the view.")
        params_config = {
            "topology_type": "fattree",
            "fattree_k": npod,
            "host_counter": 1,
            "switch_counter": 1,
            "link_counter": 1,
            "ip_prefix": subnet
        }
        net_config = kai.create_template_topo(params_config)
        result = kai.deploy_from_config(net_config)
        print(result)


class KlonetLinearTopoTemplate(Tool):
    name = "klonet_linear_topo_template"
    description = ('''
    Deploy a linear network topology template on Klonet. Do not call the
    klonet_deploy_network tool if you use this template.
    
    Args:
        subnet (str): The subnet to deploy the topology.
        nswitch (int, optional): The number of switches (default is 3).
        nnodes (int, optional): The number of host nodes on each side of 
            the switches (default is 2).
    
    Returns:
        None
    
    Example:
        >>> klonet_linear_topo_template("192.168.1.0/24", nswitch=3, nnodes=2)
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, subset: str, nswitch: int = 3, nnodes: int = 2):
        print("[Warning] This operation will overwrite the existing topology.")
        kai.reset_project()
        print("[Warning] Creating topology in this way will not layout the view.")
        params_config = {
            "topology_type": "linear",
            "linear_m": nswitch,
            "linear_n": nnodes,
            "host_counter": 1,
            "switch_counter": 1,
            "link_counter": 1,
            "ip_prefix": subset
        }
        net_config = kai.create_template_topo(params_config)
        result = kai.deploy_from_config(net_config)
        print(result)


class KlonetConfigurePublicNetworkTool(Tool):
    name = "klonet_configure_public_network"
    description = ('''
    Use this tool to enable external network access for containers. It connects 
    containers to the Internet via the docker0 bridge, utilizing the eth0 network 
    interface.
    
    Args:
        node_name (str): The name of the node.
        turn_on (bool, optional): True for enabling public network access and False
            for disconnecting this node from the Internet (default is True).
    
    Returns:
        None
    
    Example:
        # To connect h1 to the Internet, use:
        >>> klonet_configure_public_network('h1', turn_on=True)
        # To disconnect h1 from the Internet, use:
        >>> klonet_configure_public_network('h1', turn_on=False)
    ''')

    inputs = ["str", "bool"]

    @error_handler
    def __call__(self, node_name: str, turn_on: bool = True):
        result = kai.config_public_network(node_name, turn_on)
        print(result)


class KlonetCheckPublicNetworkTool(Tool):
    name = "klonet_check_public_network"
    description = ('''
    Check if a given node has access to the Internet.
    
    Args:
        node_name (str): The name of the node.
    
    Returns:
        None
    
    Example:
        # 1 means connected and 0 means disconnected.
        >>> klonet_check_public_network('h1')
    ''')

    inputs = ["str"]

    @error_handler
    def __call__(self, node_name: str):
        result = kai.check_public_network(node_name)
        print(result)


class KlonetFileDownloadTool(Tool):
    name = "klonet_file_download"
    description = ('''
    Download file from Klonet nodes. 
    
    Args:
        node_name (str): The name of the node to download from.
        file_name (str): The path of the file to download.
    
    Returns:
        None
    ''')

    inputs = ["str", "str"]

    @error_handler
    def __call__(self, node_name: str, file_name: str):
        print("KlonetAI does not support file download. Please use "
              "Klonet WebUI to download files manually.")


class KlonetFileUploadTool(Tool):
    name = "klonet_file_upload"
    description = ('''
    Upload a file to a given node.
    
    Args:
        node_name (str): The name of the target container node.
        src_filepath (str): The path to the source file to be uploaded.
        tgt_filepath (str, optional): The path on the target node where 
            the file will be stored (default is '/home').
    
    Returns:
        None
    
    Example:
        # Upload the local main.py to the path /home within the container h1.
        >>> klonet_file_upload("/PathTo/main.py", "h1", "/home")
    ''')

    inputs = ["str", "str", "str"]

    @error_handler
    def __call__(self, src_filepath: str, node_name: str, tgt_filepath: str = "/home"):
        result = kai.upload_file(node_name, src_filepath, tgt_filepath)
        print(result)


class KlonetManageWorkerTool(Tool):
    name = "klonet_manage_worker"
    description = ('''
    Register or unregister a physical host machine.
    
    Args:
        worker_ip (str): The IP address of the physical host machine to be 
            registered or unregistered.
        delete_worker (bool, optional): If True, the specified physical host 
            machine will be unregistered. Otherwise, it will be registered
            (default is False).
    
    Returns:
        None
    
    Example:
        # Register a new physical host machine of IP 10.1.1.16 to Klonet system.
        >>> klonet_manage_worker("10.1.1.16", delete_worker=False)
        # Unregister the physical host machine of IP 10.1.1.16 from Klonet system.
        >>> klonet_manage_worker("10.1.1.16", delete_worker=True)
    ''')

    inputs = ["str", "bool"]

    @error_handler
    def __call__(self, worker_ip: str, delete_worker: bool = False):
        result = kai.manage_worker(worker_ip, delete_worker)
        print(result)


class KlonetCheckHealthTool(Tool):
    name = "klonet_check_health"
    description = ('''
    Check the heartbeat health status of all nodes.
    
    Args:
        None
    
    Returns:
        None
    
    Example:
        >>> klonet_check_health()
    ''')

    @error_handler
    def __call__(self):
        is_broken, broken_nodes = kai.check_health()
        print(f"[{'Broken' if is_broken else 'Health'}]", broken_nodes)
