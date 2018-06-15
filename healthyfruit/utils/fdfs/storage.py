from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
import os

# 文件存储类<通过后台管理页面上传文件保存文件时 Storage 中的 save 方法会被调用，在 save 方法中调用了文件存储类的 _save 方法来实现保存， _save 方法的返回值最终会被保存在表中的 image 字段中
class FDFSStorage(Storage):

    def __init__(self, client_conf=None, nginx_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
            self.clinet_conf = client_conf

        if nginx_url is None:
            nginx_url = settings.FDFS_NGINX_URL
            self.nginx_url = nginx_url
    # 在文件被打开时调用
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        # name：上传文件的名字
        # content:包含上传文件内容的File类的实例对象

        # 创建一个fdfs_client类对象
        client = Fdfs_client(self.clinet_conf)
        # 上传文件到 fdfs 中
        # 获取上传文件的内容
        content = content.read()

        # 根据文件的内容上传图片
        response = client.upload_by_buffer(content)

        # return dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None
        if response is None or response.get('Status') != 'Upload successed.':
            # 上传失败
            return Exception('上传文件到fdfs系统失败')
        # 获取文件的ID
        file_id = response.get('Remote file_id')
        return file_id

    def exists(self, name):
        # 判断文件是否存在
        return False

    def url(self, name):
        # 返回可访问到的文件的URL路径
        return self.nginx_url + name


