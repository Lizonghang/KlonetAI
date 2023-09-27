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
    KlonetCheckDeployedTool,
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
    KlonetLinkQueryTool,
    KlonetGetWorkerIPTool,
    KlonetTreeTopoTemplate,
    KlonetStarTopoTemplate,
    KlonetFatTreeTopoTemplate,
    KlonetLinearTopoTemplate,
    KlonetConfigurePublicNetworkTool,
    KlonetCheckPublicNetworkTool,
    KlonetFileDownloadTool,
    KlonetFileUploadTool,
    KlonetManageWorkerTool,
    KlonetCheckHealthTool,
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
    KlonetCheckDeployedTool,
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
    KlonetLinkQueryTool,
    KlonetGetWorkerIPTool,
    KlonetConfigurePublicNetworkTool,
    KlonetCheckPublicNetworkTool,
    KlonetFileDownloadTool,
    KlonetFileUploadTool,
    KlonetManageWorkerTool,  # TODO: To be test.
    KlonetCheckHealthTool,
)

topo = (
    KlonetTreeTopoTemplate,
    KlonetStarTopoTemplate,
    KlonetFatTreeTopoTemplate,
    KlonetLinearTopoTemplate,
)

gpt = (
    SummarizeTool,
)
