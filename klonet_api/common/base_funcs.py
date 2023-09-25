import re

'''基础函数'''
def is_ip_leagal(ip):
    '''检查ip地址的合法性

    Args:
        ip(str): ip地址，如192.168.1.1（合法），256.0.0.1（不合法），aaaa（不合法）

    Returns:
        合法则返回True，不合法返回False
    '''
    compile_ip = re.compile("^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\."
        "(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\."
        "(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\."
        "(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$")
    if compile_ip.match(ip):
        return True
    else:    
        return False

def is_cidr_leagal(cidr):
    '''检查cidr形式的ip地址和掩码的合法性

    Args:
        ip(str): cidr形式的ip地址，如192.168.1.1/24（合法），256.0.0.1（不合法），
            aaaa（不合法），192.168.1.1/33（不合法）
    '''
    ip_and_mask = cidr.split("/")

    if len(ip_and_mask) != 2:
        return False
    else:
        try:
            mask = int(ip_and_mask[1])
        except:
            return False
        if mask < 0 or mask > 32:
            return False
        if not is_ip_leagal(ip_and_mask[0]):
            return False

    return True

def cidr2ip_and_netmask(cidr):
    '''将cidr形式的地址转换为ip和子网掩码

    如192.168.1.1/24转换为192.168.1.1和255.255.255.0。
    也可作为cidr形式的合法性检验函数。

    Args:
        cidr(str): cidr形式的地址，如192.168.1.1/24

    Returns:
        返回转换后的ip及子网掩码如192.168.1.1,255.255.255.0

    Raises:
        ValueError: cidr形式的地址不合法
    '''
    if not is_cidr_leagal(cidr):
        raise ValueError(f"Address [{cidr}] is illegal, please check!")

    ip_and_netmask = cidr.split("/")
    ip = ip_and_netmask[0]
    netmask = cidr_netmask(int(ip_and_netmask[1]))

    return ip, netmask

def cidr_netmask(prefix):
    '''将int类型的掩码转换为地址类型的掩码

    Args:
        prefix(int): int类型的掩码，如24

    Returns:
        地址类型的掩码，如255.255.255.0
    '''
    bin_arr = ['0' for _ in range(32)]
    for i in range(prefix):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)

def get_plural_of_words(word):
    """返回单词的复数形式

    用于根据节点/镜像的type字段返回复数形式type的字段。

    Args:
        word(str): type字段

    Returns:
        word的复数形式
    """
    if word in ['host', 'router', 'floodlight', 'controller', 'dpdk']:
        return word + 's'
    elif word in ['switch',]:
        return word + 'es'
    else:
        raise TypeError(f'get_plural_of_words() do not support the word '
            f'[{word}]')