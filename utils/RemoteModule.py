# # -*-coding: utf-8-*-
# import yagmail
# import time
# from fabric import Connection
# from conf.data_env_config import *
#
# class RemoteModule():
#     def __init__(self, ip, port, user, passwd, file_path, remote_path):
#         self.ip     = ip
#         self.port   = port
#         self.user   = user
#         self.passwd = passwd
#         self.file_path = file_path
#         self.remote_path = remote_path
#
#     def upload_file(self, file, remote_dir, upload_path=upload_path):
#         """
#             file_with_path:: file with Absolute Path    eg:/root/maple/bin/maple
#             remote_path:: remote path    eg:/root
#         """
#         try:
#             c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120, connect_kwargs={"password": self.passwd})
#             file_with_path = f'{upload_path}/{file}'
#             c.put(file_with_path, remote_dir)
#             c.close()
#         except Exception as e:
#             logger.error(f"{file_with_path} send failed----{e}")
#
#     def download_file(self, remote_file_with_path, local_path):
#         """
#             remote_file_with_path:: file with Absolute Path    eg:/root/maple/bin/maple
#             local_path:: remote path    eg:/root
#         """
#         try:
#             c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120, connect_kwargs={"password": self.passwd})
#             c.get(remote_file_with_path, local_path)
#             c.close()
#         except Exception as e:
#             logger.error(f"download file {remote_file_with_path} failed：{e}");
#
#     def exec_cmd(self, cmd):
#         """
#             cmd:: remote exec cmd
#         """
#         try:
#             c = Connection(self.ip, user=self.user, port=self.port, connect_timeout=120, connect_kwargs={"password": self.passwd})
#             result = c.run(cmd, pty=False, warn=True, hide=True).stdout
#             c.close()
#             return result
#         except Exception as e:
#             logger.error(f"exec cmd {cmd} failed：{e}");
#
#
# class MailModule():
#     def send_email(self, attachment=None, new_name=None):
#         #send server
#         smtpserver = 'smtp.163.com'
#         #send server user and passwd
#         user = 'zdns_mail'
#         password='Abcd123456'
#         #send email address
#         sender ='zdns_mail@163.com'
#         #receiver list
#         #receiver = ['jiajingbin@zdns.cn']
#         #subject
#         subject = f'{runname}-稳定性测试结果-{time.strftime("%Y_%m%d_%H_%M_%S")}'
#         #body
#         body = f'{runname}-稳定性测试-{time.strftime("%Y_%m%d_%H_%M_%S")} 已完成, 结果如附件'
#         #HTML msg
#         yag = yagmail.SMTP(user=sender, password=password, host=smtpserver, port=25, smtp_ssl=False)
#         if attachment is not None:
#             if not os.path.exists(attachment):
#                 subject = f'{runname}-稳定性测试结果-{time.strftime("%Y_%m%d_%H_%M_%S")} 出错了，附件未产生'
#                 body = f'{runname}-稳定性测试-{time.strftime("%Y_%m%d_%H_%M_%S")} 出错了，附件未产生'
#                 yag.send(mail_receiver, subject, contents=[body])
#             else:
#                 yag.send(mail_receiver, subject, contents=[body, attachment])
#         else:
#             body = f'{runname}-稳定性测试-{time.strftime("%Y_%m%d_%H_%M_%S")} 已完成'
#             yag.send(mail_receiver, subject, contents=[body])
#
#
# if __name__ == '__main__':
#     # 初始化一个RemoteModule实例remote_test
# #     remote_test = RemoteModule('202.173.9.7', 3022, 'root', 'zdns@knet.cn')
#     #    # 测试文件上传功能
#     #    remote_test.upload_file('/home/arisskz6/test_remotemodule.txt','/root/')
#     #    # 测试远程命令执行功能
#     #    remote_test.exec_cmd('ls -l')
#     #    # 测试文件下载功能
# #     remote_test.download_file('/root/data/etc/view.lua','/home/arisskz6/view.lua')
#     mailSender = MailModule()
#     mailSender.send_email(attachment='../../log/stability.log')