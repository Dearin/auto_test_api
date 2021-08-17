# -*- coding: utf-8 -*-
# @Time    : 2021/6/23 9:54
# @Author  : weidengyi

from fabric import Connection
from loguru import logger


class RemoteModule():
    def __init__(self, ip, user, passwd, port=22, file_path=None, remote_path=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.passwd = passwd
        self.file_path = file_path
        self.remote_path = remote_path

    def upload_file(self, file, remote_dir):
        """
            file_with_path:: file with Absolute Path    eg:/root/maple/bin/maple
            remote_path:: remote path    eg:/root
        """
        try:
            c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120,
                           connect_kwargs={"password": self.passwd})
            file_with_path = f'{self.file_path}/{file}'
            c.put(file_with_path, remote_dir)
            c.close()
        except Exception as e:
            logger.error(f"{file_with_path} send failed----{e}")

    def download_file(self, remote_file_with_path, local_path):
        """
            remote_file_with_path:: file with Absolute Path    eg:/root/maple/bin/maple
            local_path:: remote path    eg:/root
        """
        try:
            c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120,
                           connect_kwargs={"password": self.passwd})
            c.get(remote_file_with_path, local_path)
            c.close()
        except Exception as e:
            logger.error(f"download file {remote_file_with_path} failed：{e}");

    def exec_command(self, cmd):
        """
            cmd:: remote exec cmd
        """
        try:
            c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120,
                           connect_kwargs={"password": self.passwd})

            result = c.run(cmd, pty=False, warn=True, hide=True)
            if result.return_code == 0:
                logger.info("result:{0}".format(result.stdout[:-1]))
                return result.stdout[:-1]
            else:
                logger.error("result:{0}".format(result.stdout[:-1]))
                return result.stdout[:-1]
        except Exception as e:
            logger.error(f"exec cmd {result.command!r}  failed：{e}")
        finally:
            c.close()

    def exec_command_err(self, cmd):
        """
            cmd:: remote exec cmd
        """
        try:
            c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120,
                           connect_kwargs={"password": self.passwd})
            result = c.run(cmd, pty=False, warn=True, hide=True).stderr[:-1]
            c.close()
            return result
        except Exception as e:
            logger.error(f"exec cmd {cmd} failed：{e}")


if __name__ == "__main__":
    ssh = RemoteModule("10.1.107.31", 'root', 'zdns@knet.cn')
    res = ssh.exec_command("cd /root/zddi-build-v4/ && git pull")
    print("res1：", res)

    res = ssh.exec_command("cd /root/zddi-build-v4/ && git checkout -f sjhisjia")
    print("res2：", res)