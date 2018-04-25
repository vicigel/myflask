#!/usr/bin/env python

import paramiko
from datetime import date
import os
import multiprocessing
import socket
import logging
import commands

curr_dir = os.path.abspath(os.path.dirname(__file__))
mytuning_path = os.sep.join((curr_dir, 'mytuning.pl'))
dest_file_path = os.sep.join((curr_dir, 'result', date.isoformat(date.today())))
host_list_path = os.sep.join((curr_dir, 'host_list'))
host_list_dir = os.sep.join((curr_dir, 'host_dir'))
scripts_file_path = os.sep.join((curr_dir, 'scripts'))
source_file = './xunjian/{0}.txt'


def make_related_dirs():
    if os.path.exists(host_list_dir):
        for host_file in os.listdir(host_list_dir):
            os.remove(os.sep.join((host_list_dir, host_file)))

    for item_path in (dest_file_path, host_list_dir, scripts_file_path):
        if not os.path.exists(item_path):
            os.makedirs(item_path)

    temp_path = os.path.join(scripts_file_path, 'check_path')
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    if date.isoformat(date.today()) not in os.listdir(os.sep.join([curr_dir, 'result'])):
        os.mkdir(dest_file_path)


def make_running_script(hosts):
    for item in hosts:
        check_file = open(os.sep.join((scripts_file_path, 'check_path', item[0])), 'w')
        check_file.write('#!/bin/sh\n')
        check_file.write('top -b -d 2 -n 2 > ./xunjian/{0}.txt\n'.format(item[0]))
        check_file.write('free -m >> ./xunjian/{0}.txt\n'.format(item[0]))
        check_file.write('source /etc/profile && perl ./xunjian/mytuning.pl --user={0} --pass={1} --socket={3} >> ./xunjian/{2}.txt\n'.format(item[3], item[4], item[0], item[5]))
        check_file.write('source /etc/profile && mysql -u{0} -p{1} --socket={3} -e "show slave status\G" >> ./xunjian/{2}.txt\n'.format(item[3], item[4], item[0], item[5]))

        check_file.close()


def check(hosts, logger):
    for host in hosts:
        try:
            hostname, username, password, mysql_user, mysql_pass, mysql_socket = host
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(hostname, port=22, username=username, password=password, timeout=5)
            sftp = client.open_sftp()

            stdin, stdout, stderr = client.exec_command('ls -d xunjian')
            if stderr.read().find('No such file or directory') > 0:
                stdin, stdout, stderr = client.exec_command('mkdir xunjian')
                stderr.read()
                stdout.read()

            stdin, stdout, stderr = client.exec_command('ls -l ./xunjian/mytuning.pl')
            if stderr.read().find('No such file or directory') > 0:
                sftp.put(mytuning_path, './xunjian/mytuning.pl')

            sftp.put(os.sep.join((scripts_file_path, 'check_path', hostname)), './xunjian/xunjian.sh')
            client.exec_command('chmod a+x ./xunjian/mytuning.pl')
            stdin, stdout, stderr = client.exec_command('chmod a+x ./xunjian/xunjian.sh')
            stdout.read()
            stderr.read()
            stdin, stdout, stderr = client.exec_command('./xunjian/xunjian.sh', timeout=30)
            temp_dest_file = dest_file_path + '/{0}.txt'.format(hostname)
            print source_file.format(hostname), temp_dest_file
            stdout.read()
            stderr.read()
            sftp.get(source_file.format(hostname), dest_file_path + '/{0}.txt'.format(hostname))

            sftp.close()
            client.close()
            with open(temp_dest_file, 'r') as temp_file:
                temp_flag = 0
                for line in temp_file:
                    if line.find('but they were invalid') > 0:
                        temp_flag = 1
            if temp_flag == 1:
                logger.warn(hostname + ' mytuning.pl may execute failed,please check!')
            else:
                logger.info(hostname + ' check successfully!')
        except socket.timeout:
            logger.error(hostname + ' could not be reached,or execute command timeout!')
        except IOError:
            logger.error(hostname + ' has no Permission')
        except paramiko.ssh_exception.AuthenticationException:
            logger.error(hostname + ' authentication failure!')
        except paramiko.ssh_exception.SSHException:
            logger.error(hostname + ' No existing session!')
        finally:
            client.close()


def multi_check(hosts_list):

    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    file_handler = logging.FileHandler('check.log', 'w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    processes = []
    for host_filename, hosts in hosts_list.items():
        p = multiprocessing.Process(target=check, args=(hosts, logger, ))
        processes.append(p)
        p.start()

if __name__ == "__main__":
    make_related_dirs()
    with open(host_list_path, 'r') as f:
        lines = f.readlines()
        file_len = len(lines)

    commands.getoutput('split -l ' + ' '.join([str(file_len / 4), host_list_path]))
    commands.getoutput('mv xa* ' + host_list_dir)

    host_list = {}
    for host_file in os.listdir(host_list_dir):
        with open(os.sep.join((host_list_dir, host_file)), 'r') as f:
            host_list[host_file] = []
            for line in f:
                host_list[host_file].append(line.replace('\r\n', '').replace('\n', '').split())
                make_running_script(host_list[host_file])

    multi_check(host_list)
    for host_file in os.listdir(host_list_dir):
        os.remove(os.sep.join((host_list_dir, host_file)))

