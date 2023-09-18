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
from key import OpenAI_API_Key

# Collect our KlonetAI tools.
klonetai_tools = [obj() for obj in tool.free_tools] 
klonetai_tools += [obj() for obj in tool.gpt_tools]  # note: these are not free.
klonetai_tools += [obj() for obj in tutorial.tutorials]

# Instantiate the Agent with our KlonetAI tools.
agent = OpenAiAgent(
    model="gpt-3.5-turbo", 
    api_key=OpenAI_API_Key, 
    additional_tools=custom_tools
)

# Replace the default summarizer with our GPT summarizer.
agent.toolbox["summarizer"] = tool.SummarizeTool()

# List all tools we have.
print(agent.toolbox.keys())
```

Next, we can use <code>agent</code> to interact with KlonetAI. For example:

### Case 1: Create a Star Network on Klonet
```python
>>> agent.chat("Create a star network with 5 host nodes and 1 ovs switch, and deploy it.")
```
```text
Outputs:

==Explanation from the agent==
I will use the tools `klonet_add_node`, `klonet_add_link`, and `klonet_deploy_network` to create a star network with 5 host nodes and 1 ovs switch, and deploy it.


==Code generated by the agent==
# Add 5 host nodes.
for i in range(5):
    klonet_add_node(f"h{i}", "ubuntu")

# Add 1 ovs switch.
klonet_add_node("s1", "ovs")

# Add links between the nodes.
for i in range(5):
    klonet_add_link(f"h{i}", "s1")

# Deploy the network.
klonet_deploy_network()


==Result==
A new node (name: h0, image: host/ubuntu, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A new node (name: h1, image: host/ubuntu, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A new node (name: h2, image: host/ubuntu, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A new node (name: h3, image: host/ubuntu, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A new node (name: h4, image: host/ubuntu, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A new node (name: s1, image: switch/ovs, resource limit: {'cpu': None, 'mem': None}) have been added to the network.
A link with name (l1) was added between nodes h0 (ip: ) and s1 (ip: )
A link with name (l2) was added between nodes h1 (ip: ) and s1 (ip: )
A link with name (l3) was added between nodes h2 (ip: ) and s1 (ip: )
A link with name (l4) was added between nodes h3 (ip: ) and s1 (ip: )
A link with name (l5) was added between nodes h4 (ip: ) and s1 (ip: )
Deployment progress: 0 %
Deployment progress: 0 %
Deployment progress: 0 %
Deployment progress: 0 %
Deployment progress: 17 %
Deployment progress: 21 %
Deployment progress: 25 %
Deployment progress: 25 %
Deployment progress: 35 %
Deployment progress: 75 %
Deployment progress: 100 %
Deploy project klonetai success.
```

<p align="center">
  <img src="images/klonet-star-topo.png" alt="Klonet Screenshot" width="700">
</p>

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
I will use the following tool: `summarizer` to summarize the tutorial text from the given URL.


==Code generated by the agent==
url = "https://mxnet.apache.org/versions/1.9.1/api/faq/distributed_training"
tutorial = text_downloader(url)
summary = summarizer(context=tutorial, query="How to manually launch MXNET jobs?")
print(f"The summary is: {summary}")


==Result==
The summary is: To manually launch MXNet jobs, you can set the required environment variables and execute the training command on each machine. Here is an example for launching jobs locally on Linux/Mac machines:


shell
export COMMAND='python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync'
DMLC_ROLE=server DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=server DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=worker DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND &
DMLC_ROLE=worker DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=2 $COMMAND



Make sure to replace `$COMMAND` with the appropriate command for your training job. This example assumes that you have the `image_classification.py` script accessible on all machines in the cluster.

Note that starting all jobs on the same machine is not recommended for production environments.
1199
```

```python
>>> agent.run(f'''
=== Tutorials ===
{doc}

=== Task to be executed ===
Create a star network with 6 host nodes and 1 ovs node, then run
a MXNET scheduler, two MXNET server, and three MXNET workers on 
the host nodes. The scheduler is launched on host node with IP 192.168.1.22. 
Do not use ListComp and BinOp, write the codes line by line instead.
''')
```
```text
==Explanation from the agent==
I will use the following tools: `klonet_add_node` to add the host and ovs nodes, `klonet_add_link` to create the network links, and `klonet_command_exec` to run the MXNET scheduler, servers, and workers on the host nodes.


==Code generated by the agent==
# Add the host nodes
h1 = klonet_add_node(name="h1", image="ubuntu")
h2 = klonet_add_node(name="h2", image="ubuntu")
h3 = klonet_add_node(name="h3", image="ubuntu")
h4 = klonet_add_node(name="h4", image="ubuntu")
h5 = klonet_add_node(name="h5", image="ubuntu")
h6 = klonet_add_node(name="h6", image="ubuntu")

# Add the ovs node
s1 = klonet_add_node(name="s1", image="ovs")

# Create network links
klonet_add_link(src_node="h1", dst_node="s1")
klonet_add_link(src_node="h2", dst_node="s1")
klonet_add_link(src_node="h3", dst_node="s1")
klonet_add_link(src_node="h4", dst_node="s1")
klonet_add_link(src_node="h5", dst_node="s1")
klonet_add_link(src_node="h6", dst_node="s1")

# Run MXNET scheduler, servers, and workers on the host nodes
klonet_command_exec(node_name="h1", command="DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")
klonet_command_exec(node_name="h2", command="DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")
klonet_command_exec(node_name="h3", command="DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")
klonet_command_exec(node_name="h4", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")
klonet_command_exec(node_name="h5", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")
klonet_command_exec(node_name="h6", command="DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync")


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
Calling Klonet Exec Command API ...
Feedback from h1 after calling DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
Calling Klonet Exec Command API ...
Feedback from h2 after calling DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
Calling Klonet Exec Command API ...
Feedback from h3 after calling DMLC_ROLE=server DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
Calling Klonet Exec Command API ...
Feedback from h4 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
Calling Klonet Exec Command API ...
Feedback from h5 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
Calling Klonet Exec Command API ...
Feedback from h6 after calling DMLC_ROLE=worker DMLC_PS_ROOT_URI=192.168.1.22 DMLC_PS_ROOT_PORT=9092 DMLC_NUM_SERVER=2 DMLC_NUM_WORKER=3 python example/gluon/image_classification.py --dataset cifar10 --model vgg11 --epochs 1 --kvstore dist_sync.
```

This tool is currently under development. Please stay tuned for updates!