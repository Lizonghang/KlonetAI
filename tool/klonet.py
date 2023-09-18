from transformers import Tool
from controller import KlonetController

PROJECT_NAME = "klonetai"
USER_NAME = "wudx"
controller = KlonetController(PROJECT_NAME, USER_NAME)


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

    def __call__(self):
        return controller.images().keys()


class KlonetViewTopoTool(Tool):
    name = "klonet_view_topo"
    description = ('''
    Overview the current network topology on Klonet.
    
    Example:
        >>> klonet_view_topo()
    ''')

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
    Add a node to the Klonet network. 
    
    Args:
        name (str, optional): The name of the node being added. The name of this 
            new node cannot be the same as existing nodes.
        image (str, optional): The name of Docker image used by the node.
        cpu_limit (int, optional): CPU utilization limit for the node, unit: %, 
            default to None, which will use the default cpu limits from the Docker image.
        mem_limit (int, optional): Memory utilization limit for the node, unit: Mbytes, 
            default to None, which will use the default memory limits from the Docker image.

    Raises:
        NodeDuplicatesError: Raised when the provided node name is a duplicate.

    Example:
        # Add two host nodes (h1, h2) using the klonet_add_node function.
        >>> h1 = klonet_add_node("h1", "ubuntu")
        >>> h2 = klonet_add_node("h2", "ubuntu", cpu_limit=1000, mem_limit=1000)

        # Add an ovs node (s1) using the klonet_add_node function.
        >>> s1 = klonet_add_node("s1", "ovs")
    ''')

    inputs = ["str", "str", "int", "int"]

    def __call__(self, name: str = "", image: str = "ubuntu", 
                 cpu_limit: int = None, mem_limit: int = None):
        node = controller.add_node(
            name, controller.images[image], cpu_limit, mem_limit)
        print(f"A new node (name: {node.name}, image: {node.image_name}, "
              f"resource limit: {node.resource_limit}) have been added to the network.")


class KlonetRuntimeAddNodeTool(Tool):
    name = "klonet_runtime_add_node"
    description = ('''
    Add a node to the Klonet network. This tool is designed for post-deployment 
    use, allowing adding nodes to the network during runtime. 
    
    Args:
        name (str, optional): The name of the node being added. Be sure not 
            to use the same name as existing nodes.
        image (str, optional): The name of Docker image used by the node.
        cpu_limit (int, optional): CPU utilization limit for the node, unit: %, 
            default to None, which will use the default cpu limits from the Docker image.
        mem_limit (int, optional): Memory utilization limit for the node, unit: Mbytes, 
            default to None, which will use the default memory limits from the Docker image.

    Raises:
        NodeDuplicatesError: Raised when the provided node name is a duplicate.
    
    Example:
        >>> klonet_runtime_add_node("h3", "ubuntu")
    ''')

    inputs = ["str", "str", "int", "int"]

    def __call__(self, name: str = "", image: str = "ubuntu",
                 cpu_limit: int = None, mem_limit: int = None):
        node = controller.add_node_runtime(
            name, controller.images[image], cpu_limit, mem_limit)
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
        link_name (str, optional): The name of the link (default is None, to be auto-generated).
            The name of this new link cannot be the same as existing links.
        src_ip (str, optional): The source IP address (default is an empty string).
        dst_ip (str, optional): The destination IP address (default is an empty string).

    Returns:
        None
    
    Example:
        # Replace "h1", "h2", "s1" with the names of nodes you want to link.
        >>> klonet_add_link("h1", "s1", "l1")
        >>> klonet_add_link("h2", "s1")  # Link name will be auto-generated.
    ''')

    inputs = ["str", "str", "str", "str", "str"]

    def __call__(self, src_node: str, dst_node: str, link_name: str = None,
                 src_ip: str = "", dst_ip: str = ""):
        src_node = controller.nodes[src_node]
        dst_node = controller.nodes[dst_node]
        link = controller.add_link(
            src_node, dst_node, link_name, src_ip, dst_ip)
        print(f"A link with name ({link.name}) was added between nodes {link.source} "
              f"(ip: {link.sourceIP}) and {link.target} (ip: {link.targetIP})")


class KlonetRuntimeAddLinkTool(Tool):
    name = "klonet_runtime_add_link"
    description = ('''
    Add a network link between nodes <src_node> and <dst_node> in the Klonet network.
    This tool is designed for post-deployment use, allowing adding links to the network 
    during runtime. 
    
    Args:
        src_node (str): The name of the source node.
        dst_node (str): The name of the destination node.
        link_name (str, optional): The name of the link (default is None, to be auto-generated).
            The name of this new link cannot be the same as existing links.
        src_ip (str, optional): The source IP address (default is an empty string).
        dst_ip (str, optional): The destination IP address (default is an empty string).
    
    Returns:
        None
    
    Example:
        # Replace "h1", "h2", "s1" with the names of nodes you want to link.
        >>> klonet_runtime_add_link("h1", "s1", "l1")
        >>> klonet_runtime_add_link("h2", "s1")  # Link name will be auto-generated.
    ''')

    inputs = ["str", "str", "str", "str", "str"]

    def __call__(self, src_node: str, dst_node: str, link_name: str = None,
                 src_ip: str = "", dst_ip: str = ""):
        src_node = controller.nodes[src_node]
        dst_node = controller.nodes[dst_node]
        controller.add_link_runtime(
            src_node, dst_node, link_name, src_ip, dst_ip)
        print(f"A link with name ({link_name}) was added between nodes {src_node.name} "
              f"(ip: {src_ip}) and {dst_node.name} (ip: {dst_ip})")


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

    def __call__(self):
        controller.reset_project()


class KlonetCommandExecTool(Tool):
    name = "klonet_command_exec"
    description = ('''
    Execute the given command on the specified node.

    Args:
        node_name (str): The name of the node where the command will be executed.
        command (str): The command to execute on the specified node. Multiple 
            commands can be separated by semicolons ';', and they will be executed sequentially.

    Returns: 
        dict: A dictionary describing the results of command execution on nodes. 
            The keys are node names, and the values are dictionaries containing 
            the specific command's execution results. For example:
            {
                'h1': {
                    'ls': {
                        "exit_code": 0,
                        "output": "bin"
                    }
                }
            }
    
    Example:
        >>> klonet_command_exec("h1", "ls; pwd")
    ''')

    inputs = ["str", "str"]

    def __call__(self, node_name: str, command: str):
        print("Calling Klonet Exec Command API ...")
        print(f"Feedback from {node_name} after calling {command}.")
        return None
