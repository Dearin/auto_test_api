#!/bin/bash
source /etc/profile

base_path='/opt/auto_test_api/'
python_path='/root/.virtualenvs/auto_test/bin/'
python_packages_path='/root/.virtualenvs/auto_test/lib/python3.6/site-packages/network_manage.pth'

data_base_name='auto_test'

# 检查python安装包路径下是否存在python的自定义模块搜索配置
if [ ! -s $python_packages_path ]; then
	echo $base_path >> $python_packages_path	
fi

# 检查数据库文件是否是存在
db_path='/usr/local/auto_test'
if [ ! -e $db_path ]; then
	mkdir $db_path
	chown postgres:postgres $db_path
	su - postgres -c "initdb -D $db_path"    
	rm -rf $db_path/postgres.conf
	cp $base_path/conf/postgresql.conf $db_path
	su - postgres -c "/usr/local/pgsql/bin/pg_ctl -D $db_path -l /home/postgres/pg_lease.log start"
	sleep 60
	#psql -U postgres -p 5430 -c "create database $data_base_name;"
fi

rm -rf $base_path/apps/code_coverage/migrations/00*
rm -rf $base_path/apps/account/migrations/00*
rm -rf $base_path/apps/remote_login/migrations/00*


su - postgres -c "/usr/local/pgsql/bin/pg_ctl -D $db_path -l /home/postgres/pg_lease.log start"

cd $base_path
psql -U postgres -p 5430 -c "drop database $data_base_name;"
psql -U postgres -p 5430 -c "create database $data_base_name;"
$python_path/python manage.py makemigrations
$python_path/python manage.py migrate

# 新增默认用户 admin/admin
now_time=$(date "+%Y-%m-%d %H:%M:%S")
sql="insert into users(username, password_hash, type, is_supper, is_active, access_token, last_login, last_ip, created_at) values('admin', 'pbkdf2_sha256\$100000\$Cc0Pvi7tFnBr\$OOssQODpzJUFBMMb18Qwv3PB6JuHzQsGvYPwbzKvdUA=', 'default', 't', 't', '', '', '', '$now_time');"
echo $sql
echo `psql -U postgres -p 5430 -d $data_base_name -c "$sql"`

cat /var/spool/cron/root | grep "service_monitor.sh"
#if [ $? -ne 0 ];then
	# Todo
	# 不清楚为什么执行$python_path/python $base_path/bin/service_monitor.py，后台实际上没有执行
    # echo "*/1 * * * * $base_path/bin/service_monitor.sh >>/dev/null 2>&1" >>  /var/spool/cron/root
#fi
