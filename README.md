<br>
<p align="center">
  <img src="icon.png" alt="Icon" width="500">
</p>

This repo provides an AI agent for intelligent interaction with the 
Klonet platform. Some examples are provided to show what this repo 
is used for, as below.

```python
import tool
import tutorial
import inspect
from transformers.tools import OpenAiAgent

# Collect our KlonetAI tools.
klonetai_tools = [obj() for obj in tool.free_tools] 
klonetai_tools += [obj() for obj in tool.gpt_tools]  # note: these are not free.
klonetai_tools += [obj() for obj in tutorial.tutorials]

# Replace <OpenAI-API-Key> with your actual OpenAI API key.
api_key = "<Your-OpenAI-API-Key>"

# Instantiate the Agent with our KlonetAI tools.
agent = OpenAiAgent(
    model="gpt-3.5-turbo", api_key, additional_tools=custom_tools)

# Replace the default summarizer with our GPT summarizer.
agent.toolbox["summarizer"] = tool.SummarizeTool()

# List all tools we have.
print(agent.toolbox.keys())
```

Next, we can use <code>agent</code> to interact with KlonetAI. For example:

### Case 1: Generate the Network Topology: Internet2
```python
>>> agent.chat("Create an Internet2 network topology with interconnected links." 
"Internet2 is a secure, high-speed network that provides services for research "
"and education.")
```
```text
Outputs:

==Explanation from the agent==
To create an Internet2 network topology, we will use the `klonet_add_node` and `klonet_add_link` tools. We will add nodes representing the major hubs in the Internet2 network and then connect them with links. 

Please note that this is a simplified version of the Internet2 network topology. In reality, the Internet2 network has many more nodes and links.


==Code generated by the agent==
# Add nodes
klonet_add_node("Seattle", "ubuntu")
klonet_add_node("San Francisco", "ubuntu")
klonet_add_node("Denver", "ubuntu")
klonet_add_node("Chicago", "ubuntu")
klonet_add_node("New York", "ubuntu")
klonet_add_node("Washington DC", "ubuntu")
klonet_add_node("Atlanta", "ubuntu")
klonet_add_node("Houston", "ubuntu")
klonet_add_node("Los Angeles", "ubuntu")

# Add links
klonet_add_link("Seattle", "San Francisco")
klonet_add_link("San Francisco", "Los Angeles")
klonet_add_link("Los Angeles", "Houston")
klonet_add_link("Houston", "Atlanta")
klonet_add_link("Atlanta", "Washington DC")
klonet_add_link("Washington DC", "New York")
klonet_add_link("New York", "Chicago")
klonet_add_link("Chicago", "Denver")
klonet_add_link("Denver", "Seattle")

# Deploy the network
klonet_deploy_network("Internet2")


==Result==
Calling Klonet Add Node API ...
A new node (name: Seattle, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 1 nodes.
Calling Klonet Add Node API ...
A new node (name: San Francisco, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 2 nodes.
Calling Klonet Add Node API ...
A new node (name: Denver, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 3 nodes.
Calling Klonet Add Node API ...
A new node (name: Chicago, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 4 nodes.
Calling Klonet Add Node API ...
A new node (name: New York, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 5 nodes.
Calling Klonet Add Node API ...
A new node (name: Washington DC, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 6 nodes.
Calling Klonet Add Node API ...
A new node (name: Atlanta, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 7 nodes.
Calling Klonet Add Node API ...
A new node (name: Houston, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 8 nodes.
Calling Klonet Add Node API ...
A new node (name: Los Angeles, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 9 nodes.
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Seattle (ip: ) and San Francisco (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes San Francisco (ip: ) and Los Angeles (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Los Angeles (ip: ) and Houston (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Houston (ip: ) and Atlanta (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Atlanta (ip: ) and Washington DC (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Washington DC (ip: ) and New York (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes New York (ip: ) and Chicago (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Chicago (ip: ) and Denver (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes Denver (ip: ) and Seattle (ip: )
Calling Klonet Deploy Network API ...
Deploy project Internet2 success.
```

### Case 2: Create a Star Topology and Launch MXNET Distributed Training
```python
>>> agent.chat("Create a star network with 6 nodes and 1 ovs, " 
"deploy 1 MXNET scheduler, 2 MXNET server, and 3 MXNET workers on these " 
"nodes, and run MXNET jobs. The scheduler is launched on IP 192.168.1.22. " 
"Do not use ListComp and BinOp, write the codes line by line instead.")
```
```text
Outputs:

==Explanation from the agent==
I will use the following tools: `klonet_add_node` to add nodes to the network, `klonet_add_link` to create network links between nodes, `klonet_deploy_network` to deploy the network, and `klonet_command_exec` to run MXNET jobs.


==Code generated by the agent==
# Add nodes to the network
node1 = klonet_add_node(name="node1")
node2 = klonet_add_node(name="node2")
node3 = klonet_add_node(name="node3")
node4 = klonet_add_node(name="node4")
node5 = klonet_add_node(name="node5")
node6 = klonet_add_node(name="node6")
ovs = klonet_add_node(name="ovs", image="ovs")

# Create network links
klonet_add_link(src_node="node1", dst_node="ovs")
klonet_add_link(src_node="node2", dst_node="ovs")
klonet_add_link(src_node="node3", dst_node="ovs")
klonet_add_link(src_node="node4", dst_node="ovs")
klonet_add_link(src_node="node5", dst_node="ovs")
klonet_add_link(src_node="node6", dst_node="ovs")

# Deploy the network
klonet_deploy_network(project_name="star_network")

# Run MXNET jobs
klonet_command_exec(node_name="node1", command="DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")
klonet_command_exec(node_name="node2", command="DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")
klonet_command_exec(node_name="node3", command="DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")
klonet_command_exec(node_name="node4", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")
klonet_command_exec(node_name="node5", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")
klonet_command_exec(node_name="node6", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py")


==Result==
Calling Klonet Add Node API ...
A new node (name: node1, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 13 nodes.
Calling Klonet Add Node API ...
A new node (name: node2, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 14 nodes.
Calling Klonet Add Node API ...
A new node (name: node3, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 15 nodes.
Calling Klonet Add Node API ...
A new node (name: node4, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 16 nodes.
Calling Klonet Add Node API ...
A new node (name: node5, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 17 nodes.
Calling Klonet Add Node API ...
A new node (name: node6, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network, now we have 18 nodes.
Calling Klonet Add Node API ...
A new node (name: ovs, image: ovs, cpu_limit: None, mem_limit: None) have been added to the network, now we have 19 nodes.
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node1 (ip: ) and ovs (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node2 (ip: ) and ovs (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node3 (ip: ) and ovs (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node4 (ip: ) and ovs (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node5 (ip: ) and ovs (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes node6 (ip: ) and ovs (ip: )
Calling Klonet Deploy Network API ...
Deploy project star_network success.
Calling Klonet Exec Command API ...
Feedback from node1 after calling DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
Calling Klonet Exec Command API ...
Feedback from node2 after calling DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
Calling Klonet Exec Command API ...
Feedback from node3 after calling DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
Calling Klonet Exec Command API ...
Feedback from node4 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
Calling Klonet Exec Command API ...
Feedback from node5 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
Calling Klonet Exec Command API ...
Feedback from node6 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python mxnet_job.py.
```

### Case 3: Read Online Tutorials to Launch Klonet and Upper-Level Apps

```python
>>> doc = agent.run("Summarize how to manually launch MXNET jobs from "
"https://mxnet.apache.org/versions/1.9.1/api/faq/distributed_training")
print(len(doc))
```
```text
==Explanation from the agent==
I will use the following tool: `summarizer` to summarize the tutorial text.


==Code generated by the agent==
tutorial_url = "https://mxnet.apache.org/versions/1.9.1/api/faq/distributed_training"
tutorial_text = text_downloader(url=tutorial_url)
query = "How to manually launch MXNET jobs?"
summary = summarizer(context=tutorial_text, query=query)
print(f"The summarized tutorial is: {summary}")


==Result==
The summarized tutorial is: To manually launch MXNet jobs, you can set the necessary environment variables and execute the training script on each machine. Here is an example command for launching jobs locally on Linux or macOS:

export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'
DMLC_ROLE=server DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=server DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=worker DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=worker DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND

Make sure to replace `example/gluon/image_classification.py` with the path to your training script. You should also adjust the values of `DMLC_PS_ROOT_URI`, `DMLC_PS_ROOT_PORT`, `DMLC_NUM_SERVER`, and `DMLC_NUM_WORKER` according to your cluster setup.

Note: Manually launching jobs on the same machine is not recommended for distributed training, as it may not utilize the benefits of parallel computation across multiple machines.
1343
```

```python
agent.run(f'''
The tutorials are here: {doc}

Create a star network with 6 host nodes and 1 ovs node, 
deploy 1 MXNET scheduler, 2 MXNET server, and 3 MXNET workers on the host 
nodes and run MXNET jobs on them, and the ovs node as the center. 
The scheduler is launched on host node with IP 192.168.1.22. 
Do not use ListComp and BinOp, write the codes line by line instead.
Do not add invalid text (e.g. Note) in the generated code.
''')
```
```text
==Explanation from the agent==
I will use the following tools: `klonet_add_node`, `klonet_add_link`, `klonet_command_exec`, `klonet_deploy_network`.


==Code generated by the agent==
# Create host nodes
h1 = klonet_add_node(name="h1", image="ubuntu")
h2 = klonet_add_node(name="h2", image="ubuntu")
h3 = klonet_add_node(name="h3", image="ubuntu")
h4 = klonet_add_node(name="h4", image="ubuntu")
h5 = klonet_add_node(name="h5", image="ubuntu")
h6 = klonet_add_node(name="h6", image="ubuntu")

# Create ovs node
s1 = klonet_add_node(name="s1", image="ovs")

# Add links between host nodes and ovs node
klonet_add_link(src_node="h1", dst_node="s1")
klonet_add_link(src_node="h2", dst_node="s1")
klonet_add_link(src_node="h3", dst_node="s1")
klonet_add_link(src_node="h4", dst_node="s1")
klonet_add_link(src_node="h5", dst_node="s1")
klonet_add_link(src_node="h6", dst_node="s1")

# Deploy network
klonet_deploy_network(project_name="star_network")

# Execute MXNET jobs on host nodes
klonet_command_exec(node_name="h1", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")
klonet_command_exec(node_name="h2", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")
klonet_command_exec(node_name="h3", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")
klonet_command_exec(node_name="h4", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")
klonet_command_exec(node_name="h5", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")
klonet_command_exec(node_name="h6", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")

# Execute MXNET jobs on ovs node
klonet_command_exec(node_name="s1", command="export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND")


==Result==
Calling Klonet Add Node API ...
A new node (name: h1, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: h2, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: h3, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: h4, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: h5, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: h6, image: ubuntu, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Node API ...
A new node (name: s1, image: ovs, cpu_limit: None, mem_limit: None) have been added to the network.
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h1 (ip: ) and s1 (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h2 (ip: ) and s1 (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h3 (ip: ) and s1 (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h4 (ip: ) and s1 (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h5 (ip: ) and s1 (ip: )
Calling Klonet Add Link API ...
A link with name (None) was added between nodes h6 (ip: ) and s1 (ip: )
Calling Klonet Deploy Network API ...
Deploy project star_network success.
Calling Klonet Exec Command API ...
Feedback from h1 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from h2 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from h3 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from h4 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from h5 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from h6 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
Calling Klonet Exec Command API ...
Feedback from s1 after calling export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'; DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND.
```

This tool is currently under development. Please stay tuned for updates!