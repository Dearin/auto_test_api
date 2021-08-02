# /bin/bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
version=`cat /opt/auto_test_api/conf/conf.yml | grep name | awk '{print $2}'`
cd /root/zddiv3/
git pull
git checkout ${version}
git branch
git pull
cd /root/zddiv3/etc/
./rebuild_and_restart.sh
cd /root/coverage/sample/
/usr/local/bin/rake test
grep "auto_test.sh" /var/spool/cron/root >/dev/null
if [ $? -ne 0 ]; then
	echo "0 08 * * * /opt/auto_test_api/bin/auto_test.sh >>/opt/auto_test_api/bin/rake.log 2>&1 &" >>/var/spool/cron/root	
fi
python /root/coverage/sample/report/send_email.py
/usr/sbin/ntpdate ntp1.aliyun.com
/usr/local/appsys/package/nginx/sbin/nginx -s reload
