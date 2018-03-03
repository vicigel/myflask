import paramiko
from datetime import date
import os
import threading
import sys
import socket

curr_dir = os.path.abspath(os.path.dirname(__file__))
mytuning_path = os.sep.join([curr_dir, 'mytuning.pl'])
dest_file_path = os.sep.join([curr_dir, 'result', date.isoformat(date.today())])
host_list_path = os.sep.join([curr_dir, 'host_list'])
host_list_dir = os.sep.join([curr_dir, 'host_dir'])
scripts_file_path = os.sep.join([curr_dir, 'scripts'])
source_file = './xunjian/{0}.txt'

if date.isoformat(date.today()) not in os.listdir(os.sep.join([curr_dir, 'result'])):
    os.mkdir(dest_file_path)


def make_running_script(hosts):
    for item in hosts:
        print item
        check_path_file = open(os.sep.join([scripts_file_path, 'check_file_path', item[0]]), 'w')
        check_file = open(os.sep.join((scripts_file_path, 'check_path', item[0])), 'w')
        check_path_file.write('#!/bin/sh\n')
        check_path_file.write('source /etc/profile && which mysqladmin\n')

        check_file.write('#!/bin/sh\n')
        check_file.write('top -b -d 2 -n 2 > ./xunjian/{0}.txt\n'.format(item[0]))
        check_file.write('free -m >> ./xunjian/{0}.txt\n'.format(item[0]))
        check_file.write('source /etc/profile && perl ./xunjian/mytuning.pl --user={0} --pass={1} --socket={3} >> ./xunjian/{2}.txt\n'.format(item[3], item[4], item[0], item[5]))
        check_file.write('source /etc/profile && mysql -u{0} -p{1} --socket={3} -e "show slave status\G" >> ./xunjian/{2}.txt\n'.format(item[3], item[4], item[0], item[5]))

        check_file.close()
        check_path_file.close()


def check_mysql_path(host):
    try:
        hostname, username, password, mysql_user, mysql_pass, mysql_socket = host
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

        client.connect(hostname, port=22, username=username, password=password)

        t = paramiko.Transport((hostname, 22))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)

        stdin, stdout, stderr = client.exec_command('ls -d xunjian')
        if stderr.read().find('No such file or directory') > 0:
            stdin, stdout, stderr = client.exec_command('mkdir xunjian')
            print stderr.read()
            print stdout.read()

        sftp.put(os.sep.join((scripts_file_path, 'check_file_path', hostname)), './xunjian/check_mysql_path.sh')
        stdin, stdout, stderr = client.exec_command('sh ./xunjian/check_mysql_path.sh')
        if stderr.read().find('no mysqladmin in') > 0:
            print hostname + ' mysql related path is not configured,please configure it manually in ~/.bash_profile'
    except IOError, e:
        print hostname, 'has no Permission Error!'
        print e.message
    except UnboundLocalError, e1:
        print hostname, 'has some errors ,maybe because couldn\'t connect'
        print e1.message 
    finally:
        print 'hostname is', hostname
        client.close()
        t.close()


def check(host):
    try:
        hostname, username, password, mysql_user, mysql_pass, mysql_socket = host
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

        client.connect(hostname, port=22, username=username, password=password)
        sftp = client.open_sftp()

        stdin, stdout, stderr = client.exec_command('ls -d xunjian')
        if stderr.read().find('No such file or directory') > 0:
            stdin, stdout, stderr = client.exec_command('mkdir xunjian')
            print stderr.read()
            print stdout.read()

        stdin, stdout, stderr = client.exec_command('ls -l ./xunjian/mytuning.pl')
        if stderr.read().find('No such file or directory') > 0:
            sftp.put(mytuning_path, './xunjian/mytuning.pl')
        
        sftp.put(os.sep.join((scripts_file_path, 'check_path', hostname)), './xunjian/xunjian.sh')

        client.exec_command('chmod a+x ./xunjian/mytuning.pl')

        stdin, stdout, stderr = client.exec_command('chmod a+x ./xunjian/xunjian.sh')
        stdout.read()
        stderr.read()
        stdin, stdout, stderr = client.exec_command('./xunjian/xunjian.sh')
        print source_file.format(hostname), dest_file_path + '/{0}.txt'.format(hostname)
        stdout.read()
        stderr.read()
        sftp.get(source_file.format(hostname), dest_file_path + '/{0}.txt'.format(hostname))

        sftp.close()
        client.close()

    except IOError:
        print hostname, 'has no Permission Error!'
    except socket.timeout:
        print 'Connect timeout, maybe host ' + hostname + ' could not be reached!'
    except paramiko.ssh_exception.AuthenticationException:
        print 'Authentication failed,either username or password is wrong!'
    finally:
        client.close()


def multi_check(check_name, host_list):
    threads = []
    if check_name == 'check':
        for index, host in enumerate(host_list):
            threads.append(threading.Thread(target=check, args=[host]))

    if check_name == 'check_mysql_path':
        for host in host_list:
            threads.append(threading.Thread(target=check_mysql_path, args=[host]))

    for t in threads:
        t.setDaemon(True)
        t.start()
        t.join()

    print "all over!"

if __name__ == "__main__":
    param = sys.argv
    if param[1] not in ('check_mysql_path', 'check'):
        print 'Your input have something wrong,please check'
        sys.exit(1)
    for host_file in os.listdir(host_list_dir):
        with open(os.sep.join((host_list_dir, host_file)), 'r') as f:
            host_list = []
            for line in f:
                host_list.append(line.replace('\r\n', '').replace('\n', '').split())
            make_running_script(host_list)
            multi_check(param[1], host_list)

