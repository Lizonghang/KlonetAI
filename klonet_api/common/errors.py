'''异常定义'''

class HttpStatusError(RuntimeError):
    '''当HTTP的返回状态码不为200时，触发此异常'''
    pass

class JsonDecodeError(RuntimeError):
    '''当返回体不包含json时，触发此异常'''
    pass

class VemuExecError(RuntimeError):
    '''当HTTP请求成功，但json中的返回码不为1时，触发此异常'''
    pass

class NodeNotExistsError(RuntimeError):
    pass

class NodeDuplicatesError(RuntimeError):
    pass

class LinkDuplicatesError(RuntimeError):
    pass

class LinkNotExistsError(RuntimeError):
    '''当目标链路不存在时，触发此异常'''
    pass

class LinkParallelError(RuntimeError):
    '''当出现平行边（即新边与已有边的两端节点名相同）时，触发该异常'''
    pass

class LinkInconsistentError(RuntimeError):
    '''当链路属性配置时，链路两端的LinkConfiguration对象的链路名不一致时，触发该异常
    '''
    pass