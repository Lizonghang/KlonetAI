from transformers import Tool


class MXNETTutorial(Tool):
    name = "read_mxnet_tutorial"
    description = ('''
    MXNet supports distributed training enabling us to leverage multiple machines 
    for faster training. In this document, we describe how it works, how to 
    launch a distributed training job and some environment variables which 
    provide more control.
    
    MXNet uses environment variables to assign roles to different processes 
    and to let different processes find the scheduler. The environment 
    variables are required to be set correctly as follows for the training 
    to start:
    
    - DMLC_ROLE: Specifies the role of the process. This can be server, 
        worker or scheduler. Note that there should only be one scheduler.
    - DMLC_PS_ROOT_URI: Specifies the IP of the scheduler.
    - DMLC_PS_ROOT_PORT: Specifies the port that the scheduler listens to.
    - DMLC_NUM_SERVER: Specifies how many server nodes are in the cluster.
    - DMLC_NUM_WORKER: Specifies how many worker nodes are in the cluster.
    
    Below is an example to start 1 scheduler, 1 server, and 2 workers locally:
    # Start a scheduler.
    DMLC_ROLE=scheduler DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 
    DMLC_NUM_SERVER=1 DMLC_NUM_WORKER=2 python demo.py --kvstore dist_sync

    # Start a server.
    DMLC_ROLE=server DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 
    DMLC_NUM_SERVER=1 DMLC_NUM_WORKER=2 python demo.py --kvstore dist_sync
    
    # For two workers, run the following command for each of them.
    DMLC_ROLE=worker DMLC_PS_ROOT_URI=127.0.0.1 DMLC_PS_ROOT_PORT=9092 
    DMLC_NUM_SERVER=1 DMLC_NUM_WORKER=2 python demo.py --kvstore dist_sync
    ''')
