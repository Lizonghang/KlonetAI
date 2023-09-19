from transformers import Tool


class NetworkTutorial(Tool):
    name = "network_tutorial"
    description = ('''
    [Q] How to measure data transfer rate / bandwidth between any two hosts ?
    [A] Take host nodes h1 and h2 as an example, follow these two steps:
        1. Start the iperf server on host node h2.
        2. Launch the iperf client on host node h1. Ensure to convert h2 to
        its IP address as name resolution is not available.
    Args:
        None
        
    Returns:
        None

    Examples:
        >>> network_tutorial()
    ''')

    def __call__(self):
        print(self.description)
