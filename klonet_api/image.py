from .common import Manager, Image

class ImageManager(Manager):
    '''镜像管理类

    Attributes:
        user(str): 用户名
    '''
    def __init__(self, user_name, backend_ip=None, backend_port=None):
        super().__init__(backend_ip, backend_port)
        self.user = user_name

    def get_images(self, quiet=False):
        '''获取当前用户的所有镜像名及镜像对象。

        Args:
            quiet(bool): 默认为False。若为False，则将打印镜像名列表；否则将关闭打印。

        Returns:
            一个字典，key为镜像名，value为Image对象
        '''
        resp = self._get("/my/image/", params={"username": self.user})
        resp_json = self._parse_resp(resp)
        try:
            self._check_resp_code(resp_json)
        except KeyError:
            pass
        image_list = {}
        for registry_type in resp_json.keys(): # 镜像仓库类型，如private/public
            for type in resp_json[registry_type].keys():# 镜像类型，如host/switch
                for image_dict in resp_json[registry_type][type]:
                    # 注意这里的subtype为前端显示的镜像名，在这里同样用作镜像名来向
                    # 用户屏蔽细节
                    image_list[image_dict["subtype"]] = Image(**image_dict)

        if not quiet:
            print(f"{self.user} has these images: {list(image_list.keys())}")
            
        return image_list