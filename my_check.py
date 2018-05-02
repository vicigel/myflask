#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import commands
import copy
from datetime import date, timedelta


def init_dict():
    initial_dict = {
        'cpu_usage': '',
        'system_load': '',
        'memory_usage': '',
        'disk_usage': '',
        'up_time': '',
        'storage_distribute': '',
        'rw_ratio': '无',
        'slow_query_ratio': '无',
        'connection_info': '无',
        'innodb_log_wait': '无',
        'innodb_buffer_pool_hit': '无',
        'key_buffer_hit': '无',
        'thread_cache_hit': '无',
        'table_cache_hit': '无',
        'tmp_table_ratio': '无',
        'slave_status': '无',
        'ip_address': '',
        'suggestion': '',
        'recommendations': []
    }
    return copy.copy(initial_dict)

e2c_recommendations = {
    'Adjust your join queries to always utilize indexes': u'以使用索引的方式优化join查询',
    'Read this before increasing table_cache over 64: http://bit.ly/1mi7c4C': u'lalalal',
    'Increase table_cache gradually to avoid file descriptor limits': u'通过逐渐增加table\_cache的方式避免文件描述符的限制',
    'Full table scan query too much, enable slow query log to analyze': u'全表扫描过多，打开慢查询日志分析',
    'Reduce your overall MySQL memory footprint for system stability': u'为了系统稳定运行，减小MySQL占用内存',
    'Binary Log Usage Exceeding Disk Cache Memory Limits, increase binlog_cache_size': u'增加binlog\_cache\_size大小',
    'Run OPTIMIZE TABLE to defragment tables for better performance': u'运行optimize table优化表获得更好的性能',
    'Optimize queries and/or use InnoDB to reduce lock wait': u'优化查询或使用innodb存储引擎减少锁等待',
    'Your applications are not closing MySQL connections properly': u'应用未正确关闭MySQL连接',
    'Reduce or eliminate persistent connections to reduce connection usage': u'通过减少或消除长连接的方式来减少连接的使用',
    'When making adjustments, make tmp_table_size/max_heap_table_size equal': u'调整tmp\_table\_size max\_heap\_table\_size相等',
    'Reduce your SELECT DISTINCT queries without LIMIT clauses': u'减少select distinct后无limit语句的执行',
    'Add skip-innodb to MySQL configuration to disable InnoDB': u'通过向MySQL配置文件增加skip-innodb的方式禁用innodb',
    'MySQL data directory need increase disk space!': u'MySQL数据文件目录需要增加磁盘空间'
}

customer_dict = {
    '1': '中央国债',
    '2': '全国股转',
    '3': '阳光保险'
}


def rename_ip_to_name(target_dir):
    file_dict = {}
    with open('/home/vicigel/works/sunshine/ip2name.txt') as f:
        for item in f:
            temp = item.split('\t')
            print temp
            file_dict[temp[0]] = temp[1].replace('\n', '')
    os.chdir(target_dir)

    for item in os.listdir(os.getcwd()):
        if item.find(':3306') == -1:
            if file_dict.has_key(item[:-4]):
                os.rename(item, file_dict[item[:-4]] + '(' + item[:-4] + ':3306).txt')
            else:
                print item[:-4] + ' not in ip2name.txt,please check!'


def collect_data(target_dir):

    try:
        os.chdir(target_dir)
    except Exception:
        print 'Please check if the directory exists!'
        sys.exit(2)
    result_dict = {}
    file_list = os.listdir(os.getcwd())
    for file_name in file_list:
        print file_name
        slave_io_status = False
        slave_sql_status = False
        temp_dict = init_dict()
        with open(file_name, 'r') as f:
            line_terminator = '\r\n' if commands.getoutput('file ' + file_name).find('CRLF') > 0 else '\n'
            data = f.read().split(line_terminator)
        temp_dict['cpu_usage'] = '10\%以内'
        for idx_item, item in enumerate(data):
            if item.find('load average:') > 0:
                temp_dict['system_load'] = item[item.find('load average:'):]
            if item.find('IPADDR') > 0:
                temp_dict['ip_address'] = item.split(':')[1]
                continue
            elif item.find('Total:') > 0:
                temp_dict['memory_usage'] = 'Total:' + item.split(':')[1]
                continue
            elif item.find('Free:') > 0:
                temp_dict['memory_usage'] += ' Free:' + item.split(':')[1]
                continue
            elif item.find('Data in MyISAM tables:') > 0:
                temp_dict['storage_distribute'] = item[item.find('MyISAM tables'):] + ' '
                continue
            elif item.find('Data in InnoDB tables:') > 0:
                temp_dict['storage_distribute'] += item[item.find('InnoDB tables'):]
                continue
            elif item.find('MySQL datadir') > 0:
                temp_dict['disk_usage'] = item[item.find('Avali:'):].replace('Avali', 'Avail').replace('%', '\%')
                if item.find('G') > 0:
                    avali = float(item[item.find('Avali:') + 7:item.find('G')])
                else:
                    avali = float(item[item.find('Avali:') + 7:item.find('T')]) * 1024
                continue
            elif item.find('Up for:') > 0:
                temp_dict['up_time'] = item[item.find(':') + 2:item.find('(') - 1]
                continue
            elif item.find('Reads / Writes') > 0:
                temp_dict['rw_ratio'] = '读/写: ' + item[item.find(':') + 2:].replace('%', '\%')
                continue
            elif item.find('Slow queries') > 0:
                temp_dict['slow_query_ratio'] = item[item.find(':') + 2:item.find('(')].replace('%', '\%')
                continue
            elif item.find('available connections') > 0:
                connect_info = item[item.find('(') + 1:item.find(')')].split('/')
                temp_dict['connection_info'] = '最大连接数: ' + connect_info[1] + ';历史最大并发连接数： ' + connect_info[0]
                continue
            elif item.find('Key buffer hit rate') > 0:
                temp_dict['key_buffer_hit'] = item[item.find(':') + 2:item.find('(')].replace('%', '\%')
                continue
            elif item.find('Temporary tables created') > 0:
                temp_dict['tmp_table_ratio'] = item[item.find(':') + 2:item.find('(')].replace('%', '\%')
                continue
            elif item.find('Thread cache hit rate') > 0:
                temp_dict['thread_cache_hit'] = item[item.find(':') + 2:item.find('(')].replace('%', '\%')
                continue
            elif item.find('Table cache hit rate') > 0:
                temp_dict['table_cache_hit'] = item[item.find(':') + 2:item.find('(')].replace('%', '\%')
                continue
            elif item.find('InnoDB log waits') > 0:
                temp_dict['innodb_log_wait'] = item[item.find(':') + 1:]
                continue
            elif item.find('InnoDB Buffer Pool Hit hate') > 0:
                temp_dict['innodb_buffer_pool_hit'] = item[item.find(':') + 1:].replace('%', '\%')
                continue
            elif item.find('Slave_UUID') >= 0:
                temp_dict['slave_status'] = '主库'
                continue
            elif item.find('Slave_IO_Running:') > 0:
                if item.split(':')[1].strip() == 'Yes':
                    slave_io_status = True
                continue
            elif item.find('Slave_SQL_Running:') > 0:
                if item.split(':')[1].strip() == 'Yes':
                    slave_sql_status = True
                continue
            elif item.find('General recommendations') >= 0:
                while True:
                    if data[idx_item + 1].find('Variables to adjust') == -1:
                        temp_dict['recommendations'].append(data[idx_item + 1].replace('\n', '').lstrip().rstrip())
                        idx_item += 1
                    else:
                        break
                if temp_dict['recommendations'].count('Read this before increasing table_cache over 64: http://bit.ly/1mi7c4C'):
                    temp_dict['recommendations'].remove('Read this before increasing table_cache over 64: http://bit.ly/1mi7c4C')

        if slave_io_status and slave_sql_status:
            temp_dict['slave_status'] = '正常'
        result_dict[file_name] = temp_dict
    return result_dict


def write_tex(result_data, file_name, customer):
    f = open(file_name, 'w')
    s = []
    for value in result_data.values():
        for a in value['recommendations']:
            if a not in s:
                s.append(a)
    const = '''
    \\documentclass{article}

    \\usepackage[UTF8]{ctex}
    \\usepackage{tabularx,ragged2e,colortbl}
    \\usepackage{color}
    \\usepackage[section]{placeins}
    \\usepackage[left=7em,right=7em]{geometry}
    \\usepackage[colorlinks,linkcolor=black]{hyperref}
    \\usepackage{lastpage}
    \\usepackage{ifthen}

    \\usepackage{fancyhdr}
    \\definecolor{mycolor}{RGB}{49,132,155}
    \\definecolor{tblcolor}{RGB}{53,118,201}
    \\pagestyle{fancy}
    \\fancyhf{}
    \\lhead{\\ifthenelse{\\value{page}=1}{\\includegraphics[width=3cm]{lalala}}{}}
    \\chead{\\ifthenelse{\\value{page}=1}{}{\\textcolor{mycolor}{<MySQL数据库巡检报告>}}}
    \\rhead{\\ifthenelse{\\value{page}=1}{\\textbf {\\Large 上海爱可生信息技术股份有限公司}}{\\footnotesize Page \\thepage\\ of \\pageref{LastPage}}}
    \\rfoot{\\ifthenelse{\\value{page}=1}{\\small 上海爱可生---服务部}{}}
    \\author{Vicigel}
    \\title{''' + customer_dict.get(customer) + '''MySQL数据库健康巡检报告}
    \\date{\\vspace{-5ex}}


    \\begin{document}
        \\normalsize
        \\maketitle
        \\thispagestyle{fancy}
        \\centering
            \\paragraph{Version 1.0}
        \\clearpage
        \\justify

        \\underline{\\textbf {\\large 版权声明：}}\\\\
    	\\small
    	Copyright 2018 上海爱可生信息技术股份有限公司.\\\\
    	这封电子邮件（包括附件）是保密的，并可能在法律上受到保护，请勿透露邮件内容给任何第三方。如果您不是收件人或其授权的代理收件人，您是禁止使用，复制或分发这封电子邮件的内容以及附件。如果您收到了这封误发的电子邮件，请通知寄件人立即返回电子邮箱，删除此邮件的所有副本以及附件。\\\\
    	\\clearpage
    	\\normalsize
        \\tableofcontents

        \\justify
        \\section{报告说明}
        本巡检报告是针对''' + customer_dict.get(customer) + '''的MySQL数据库主机的系统资源、数据库各种重要的性能指标采集分析，得出调整建议供用户决策评估。
        \\FloatBarrier
        \\section{巡检项}
            \\subsection{系统资源部分}
            \\begin{table}[!ht]
            \\setlength\extrarowheight{2pt}
            \\begin{tabularx}{\\textwidth}{|p{4.5cm}|X|}
                \\hline
                \\rowcolor{tblcolor}\\textbf{巡检项} & \\textbf{描述项}
                \\\\
                \\hline
                CPU利用率 & 评估系统CPU运转情况
                \\\\
                \\hline
                系统负载 & 评估系统繁忙程度
                \\\\
                \\hline
                内存使用率 & 评估系统内存是否充足
                \\\\
                \\hline
                数据库磁盘空间可用率 & 评估数据库系统磁盘空间是否充足
                \\\\
                \\hline
            \\end{tabularx}
            \\end{table}
            \\FloatBarrier
            \\clearpage
            \\subsection{MySQL数据库部分}
            \\begin{table}[!ht]
            \\setlength\extrarowheight{2pt}
            \\begin{tabularx}{\\textwidth}{|p{4.5cm}|X|}
                \\hline
                \\rowcolor{tblcolor}\\textbf{巡检项} & \\textbf{描述}
                \\\\
                \\hline
                连续运行时长 & 可反映数据库连续的可用性
                \\\\
                \\hline
                存储引擎分布 & 反映不同存储引擎的数据量
                \\\\
                \\hline
                读写比例 & 读写比例表示数据库读、写操作所占比例，反映数据库是读密集型或写密集型
                \\\\
                \\hline
                慢查询比例 & 慢查询比例反映数据库慢查询所占全部查询的比例，越大说明该数据库慢查询越多
                \\\\
                \\hline
                连接数 & 反映数据库连接请求压力
                \\\\
                \\hline
                InnoDB Log Wait & 反映InnoDB redo log 写入时是否需要等待，正常情况应小于0
                \\\\
                \\hline
                InnoDB Buffer Pool命中率 & 反映InnoDB Buffer Pool命中情况，越大越好
                \\\\
                \\hline
                Key Buffer Size 命中率 & 反映MyISAM 索引缓冲区的命中情况，越大越好
                \\\\
                \\hline
                Thread Cache命中率 & 反映线程缓存的命中情况，越大越好
                \\\\
                \\hline
                Table Cache命中率 & 反映表缓存的命中情况，越大越好
                \\\\
                \\hline
                磁盘临时表使用比例 & 反映在所有临时表中创建磁盘表的比例，比例越小越好，应10\\%以内
                \\\\
                \\hline
                网络流量 & 反映数据库收发流量，评估网卡瓶颈
                \\\\
                \\hline
                磁盘IO & 反映磁盘使用情况，评估磁盘瓶颈
                \\\\
                \\hline
                复制状态和延迟 & 检查复制状态是否正常，是否有延迟
                \\\\
                \\hline
            \\end{tabularx}
            \\end{table}


        \\FloatBarrier
        \\clearpage
        \\section{主机巡检结果}

        '''
    f.write(const)
    for k, v in result_data.items():
        f.write('\\subsection{' + k[:-4] + '}\n')
        f.write('\\begin{table}[!ht]\n')
        f.write('\\setlength\\extrarowheight{2pt}\n')
        f.write('\\begin{tabularx}{\\textwidth}{|p{4.5cm}|X|}\n')
        f.write('\\hline\n')
        f.write('\\rowcolor{tblcolor}\\multicolumn{2}{|l|}{\\textbf{系统资源巡检}}\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('CPU利用率 & ' + v.get('cpu_usage') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('系统负载 & ' + v.get('system_load') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('内存使用率 & ' + v.get('memory_usage') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('数据库磁盘空间可用率 & ' + v.get('disk_usage') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('\\rowcolor{tblcolor}\\multicolumn{2}{|l|}{\\textbf{MySQL数据库巡检}}\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('连续运行时长 & ' + v.get('up_time') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('存储引擎分布 & ' + v.get('storage_distribute') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('读写比例 & ' + v.get('rw_ratio') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('慢查询比例 & ' + v.get('slow_query_ratio') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('连接数 & ' + v.get('connection_info') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('InnoDB Log Wait & ' + v.get('innodb_log_wait') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('InnoDB Buffer Pool命中率 & ' + v.get('innodb_buffer_pool_hit') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('Key Buffer Size命中率 & ' + v.get('key_buffer_hit') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('Thread Cache命中率 & ' + v.get('thread_cache_hit') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('Table Cache命中率 & ' + v.get('table_cache_hit') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('磁盘临时表使用比例 & ' + v.get('tmp_table_ratio') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('复制状态 & ' + v.get('slave_status') + '\n')
        f.write('\\\\\n')
        f.write('\\hline\n')
        f.write('\\end{tabularx}\n')
        f.write('\\end{table}\n')
        f.write('\\FloatBarrier\n')
        f.write('\\clearpage\n')
        f.write('\n\n')
    f.write('\\section{数据库建议}')
    f.write('\n')
    f.write('\\noindent\n')
    idx = 0
    for k, v in result_data.items():
        idx += 1
        if len(v['recommendations']) == 0:
            continue
        f.write(str(idx) + '、' + (k[:k.find(')') + 1] if customer == '3' else k[:-4]) + '\n')
        f.write('\\\\\n')
        for a, b in enumerate(v['recommendations']):
            if b in e2c_recommendations:
                f.write(str(a + 1) + ') ' + e2c_recommendations[b].encode('utf-8') + '\n')
                f.write('\\\\\n')
        f.write('\\\\\n')

    f.write('\\end{document}')
    f.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print 'Please specify the source file directory!'
        sys.exit(1)

    if sys.argv[2] == '3':
        rename_ip_to_name(sys.argv[1])
    print True
    result_dict_data = collect_data(sys.argv[1])
    print True

    if 1 < date.today().day < 15:
        target_date = (date.today() - timedelta(days=31)).strftime('%Y%m')
    else:
        target_date = date.today().strftime('%Y%m')
    target_file_name = '/home/vicigel/工作/latex/' + customer_dict.get(sys.argv[2]) + \
                       'MySQL数据库健康巡检报告-' + target_date + '.tex'
    write_tex(result_dict_data, target_file_name, sys.argv[2])
