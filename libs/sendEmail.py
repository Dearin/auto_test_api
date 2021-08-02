# -*-coding:utf-8-*-
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(username, password, to, sender_name, subject, content, email_type):
    """
    :param username:
    :param password:
    :param to: 接收者列表 []
    :param sender_name:
    :param subject:
    :param content:
    :param email_type:
    :return:
    """
    from_addr = username
    password = password
    to_addr = to
    smtp_server = "smtp.exmail.qq.com"

    # 邮件正文是MIMEText类型
    msg = MIMEText('%s' % (content), '%s' % (email_type), 'utf-8')
    msg['From'] = _format_addr('%s<%s>' % (sender_name, from_addr))
    msg['To'] = _format_addr('<%s>' % to_addr)
    msg['Subject'] = Header('%s' % (subject), 'utf-8').encode()

    # 普通登陆端口是25，带ssl验证时候端口是465
    # smtp_server = 'smtp.exmail.qq.com'
    # server = smtplib.SMTP_SSL(smtp_server, 465)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    #server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


if __name__ == '__main__':
    """发送简单文本邮件"""

    import sys
    email = sys.argv[1].split(",")
    ip = sys.argv[2].strip()
    rpm_name = sys.argv[3].strip()
    print(ip)
    username = "weidengyi@zdns.cn"  # 用户名
    password = "L9o9ddv2tNanwQAd"  # 口令
    sender_name = 'sendmail@zdns.cn'

    subject = 'RPM包制作完成提示'
    content = '<h5>RPM包已制作完成，请下载安装, scp root@{0}:/root/rpm/{1} ./</h5></html>'.format(ip, rpm_name)
    # email_type 取值：plain,文本类型邮件;html,html类型邮件
    email_type = 'html'
    #_to = ['weidengyi@zdns.cn']
    for to in email:
        send_mail(username, password, to, sender_name, subject, content, email_type)
    print('send mail to %s success' % to)
