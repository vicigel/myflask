import paramiko

mytuning_path = '/home/vicigel/works/sunshine/mytuning.pl'
source_file = './xunjian/{0}.txt'
dest_file_path = '/home/vicigel'

command_list = ['top -d 2 -n 3 -b > ./xunjian/{0}.txt',
                'perl xunjian/mytuning.pl --user={1} --pass={2} --socket=/opt/mysql/data/3432/mysqld.sock >> ' + source_file,
                'mysql -u{1} -p{2} -P5678 -e "show slave status\G" >> ' + source_file
                ]

with open('host_list', 'r') as f:
    host_list = []
    for line in f:
        host_list.append(line.replace('\r\n', '').replace('\n', '').split())

try:
    for host in host_list:
        hostname, username, password, mysql_user, mysql_pass = host
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
            sftp.put(mytuning_path, '/home/vicigel/mytuning.pl')
            stdin, stdout, stderr = client.exec_command('chmod a+x xunjian/mytuning.pl')

        stdin, stdout, stderr = client.exec_command('export $PATH=$PATH:/data/actiontech-balm/mysql/bin')
        print stderr.read()
        stdin, stdout, stderr = client.exec_command('echo $PATH')
        print stdout.read()

        for command in command_list:
            print command.format(hostname, mysql_user, mysql_pass)
            stdin, stdout, stderr = client.exec_command(command.format(hostname, mysql_user, mysql_pass))
            print stderr.read()

        sftp.get(source_file.format(hostname), dest_file_path + '/aa.txt')

        client.close()
        t.close()

finally:
    client.close()
    t.close()