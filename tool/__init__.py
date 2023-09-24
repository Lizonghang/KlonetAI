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
    KlonetLinkQueryTool,  # TODO: To be added.
    KlonetGetWorkerIPTool,
    KlonetConfigurePublicNetworkTool,  # TODO: To be debug.
    KlonetCheckPublicNetworkTool,  # TODO: To be debug.
    KlonetFileDownloadTool,
    KlonetFileUploadTool,  # TODO: To be test.
    KlonetManageWorkerTool,  # TODO: To be test.
    KlonetCheckHealthTool,  # TODO: To be test.
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
