from .common import (
    GetCurrentDateTimeTool,
    GetCurrentDayTool
)
from .klonet import (
    KlonetAddLinkTool,
    KlonetAddNodeTool,
    KlonetCommandExecTool,
    KlonetRuntimeDeleteNodeTool,
    KlonetDeployTool,
    KlonetGetAllImagesTool,
    KlonetViewTopoTool,
    KlonetDestroyProjectTool,
    KlonetRuntimeAddNodeTool,
    KlonetRuntimeAddLinkTool,
    KlonetRuntimeDeleteLinkTool,
    KlonetSSHServiceTool,
    KlonetPortMappingTool,
    KlonetGetPortMappingTool,
    KlonetGetIPTool,
    KlonetLinkConfigurationTool,
    KlonetResetLinkConfigurationTool,
    KlonetGetWorkerIPTool,
)
from .gpt import SummarizeTool

base = (
    GetCurrentDateTimeTool,
    GetCurrentDayTool,
)

klonet = (
    KlonetAddLinkTool,
    KlonetAddNodeTool,
    KlonetCommandExecTool,
    KlonetRuntimeDeleteNodeTool,
    KlonetDeployTool,
    KlonetGetAllImagesTool,
    KlonetViewTopoTool,
    KlonetDestroyProjectTool,
    KlonetRuntimeAddNodeTool,
    KlonetRuntimeAddLinkTool,
    KlonetRuntimeDeleteLinkTool,
    KlonetSSHServiceTool,
    KlonetPortMappingTool,
    KlonetGetPortMappingTool,
    KlonetGetIPTool,
    KlonetLinkConfigurationTool,
    KlonetResetLinkConfigurationTool,
    KlonetGetWorkerIPTool,
)

gpt = (
    SummarizeTool,
)
