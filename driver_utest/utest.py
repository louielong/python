# !/usr/bin/env python
# ^_^ coding=utf-8 ^_^!

# > File Name: utest.py
# > Author: louie.long
# > Mail: louie.long@pica8.local
# > Created Time: Tuesday, May 03, 2016 PM02:04:11 HKT


'''
This is a driver unit test script
Please run in super user mode
Using example: python utest.py as5712.config
'''

import os
import re
import sys
import copy
import time
import random
import os.path
import commands
import datetime


#err number
ERRNO ={'EPATH':1, 'EEMPTY':2, 'EVALUE':3, 'EINVALID':4, 'EMODE':5, 'EVA&MO':6,
        'EIN&MO':7, 'UNSUPPORT':8, 'EOTHER':20}


#define attrbute class
class Attr(object):
    def __init__(self):
        self.name = ''
        self.path = ''
        self.value = '0'
        self.ref_vaule = 'NULL'
        self.mode = 'r'
        self.ref_mode = 'r'
        self.flag = 0

    def set_name(self, name):
        self.name = name

    def set_path(self, path):
        self.path = path

    def set_value(self, value):
        self.value = value

    def set_refer_value(self, refer_value):
        self.refer_value = refer_value

    def set_mode(self, mode):
        self.mode = mode

    def set_refer_mode(self, refer_mode):
        self.mode = mode

    def set_flag(self, flag):
        self.flag = flag

    def get_name():
        return self.name

    def get_path():
        return self.path

    def get_value():
        return self.value

    def get_refer_value():
        return self.refer_value

    def get_mode():
        return self.mode

    def get_refer_mode():
        return self.mode

    def get_flag():
        return self.flag

    #get attr info
    def get_info(self, file_path, refer_value, refer_mode):
        self.path = file_path
        self.name = os.path.basename(file_path)
        self.refer_value = refer_value
        self.refer_mode = refer_mode

        if os.path.isfile(file_path):
            self.mode = oct(os.stat(file_path).st_mode)[-3:]
            if self.mode == '200':   #write only file
                self.value = '----'
                self.flag = 0
                return
        else:
            self.flag = ERRNO['EPATH']
            return

        try:
            f = open(file_path, 'r')
            value = f.readline().splitlines()
            f.close()
            #if file have more than 2 lines, here  will throw error
            self.value = ''.join(value)
            self.flag = 0
            return
        except IOError:
            self.flag = ERRNO['EPATH']
            return

    #get value fast to make judgement
    def get_value_fast(self, file_path):
        try:
            f = open(file_path, 'r')
            value = f.readline().splitlines()
            f.close()
            #if file have more than 2 lines, here  will throw error
            self.value = ''.join(value)
            self.flag = 0
            return
        except IOError:
            self.flag = ERRNO['EPATH']
            return
    
    #check value
    def check_value(self):
        if self.flag != 0:
            return

        if len(self.value) <= 0:
            self.flag = ERRNO['EEMPTY']
            return

        if self.mode == '200':
            self.flag = 0
            return

        if self.value == 'invalid':
            self.flag = ERRNO['UNSUPPORT']
            return

        refer_value = self.refer_value
        if self.name == 'start_mode':   #start mode check
            if self.value == 'cold start' or self.value == 'warm start':
                self.flag = 0
                return
            else:
                self.flag = ERRNO['EVALUE']
                return
        elif 'max' in refer_value and 'char' in refer_value:#self value is a string
            refer_value = (re.findall(r'\d+',refer_value))#get the max string number
            refer_value[0] = int(refer_value[0])

            if len(self.value) <= refer_value[0]:
                self.flag = 0
                return
            else:
                self.flag = ERRNO['EVALUE']
                return
        elif '-' in refer_value:            #refer value is a range
            value = ''                      #temp var avoid to change self.value
            if '-' in self.value:           #judge for negative number
                value = int(self.value)
            elif self.value.isdigit():
                value = int(self.value)
            else:
                self.flag = ERRNO['EEMPTY']
                return
            refer_value = re.findall(r'\d+',refer_value)
            refer_value[0] = int(refer_value[0])
            refer_value[1] = int(refer_value[1])
            if 'temp' in self.name:
                if value > -1*refer_value[0] and value <= refer_value[1]:
                    self.flag = 0
                    return
                elif value == -128000:      #temp -12800 is a invalid number
                    self.flag = ERRNO['EINVALID']
                    return
                else:
                    self.flag = ERRNO['EVALUE']
                    return
            elif 'fault' in self.name:
                if value == 0:
                    self.flag = 0
                    return
                elif value == 1:        #XXX_fault = 1  represent device XXX is fault
                    self.flag = ERRNO['EVALUE']
                    return
            else:
                if value >= int(refer_value[0]) and value <= int(refer_value[1]):
                    self.flag = 0
                    return
                else:
                    self.flag = ERRNO['EVALUE']
                    return
        elif 'mac' in self.name:
            mac = re.match(r'^([0-9a-fA-F]{2})(([/\s:][0-9a-fA-F]{2}){5})$', self.value)
            if mac:
                if mac.group() == self.value:
                    self.flag = 0
                    return
                else:
                    self.flag = ERRNO['EVALUE']
                    return
            else:
                self.flag = ERRNO['EVALUE']
                return

        self.flag = ERRNO['EOTHER']
        return

    #check mode
    def check_mode(self):
        if self.flag == ERRNO['EPATH']:
            return

        if self.mode == '444':      #read only
            self.mode = 'r'
        elif self.mode == '644':    #read and write
            self.mode = 'rw'
        elif self.mode == '200':    #write only
            self.mode = 'w'
        else:
            self.mode = 'E'

        flag = self.flag
        if self.flag == ERRNO['UNSUPPORT']:
            self.flag = flag
            return

        if self.mode != self.refer_mode:
            if flag == ERRNO['EVALUE']:
                self.flag = ERRNO['EVA&MO']
            elif flag == ERRNO['EINVALID']:
                self.flag = ERRNO['EIN&MO']
            else:
                self.flag = ERRNO['EMODE']
        else:
            self.flag = flag

        self.flag = flag
        return


#init log file
def init_log():
    global log_file
    log_file = ''.join([sys.argv[1].split('.')[0], '.log'])

    try:
        log = open(log_file, 'w')
        log.truncate()      #empty log file
        log.close()
        ret = commands.getstatusoutput('version')
        if ret[0] == 0:
            tmp = os.popen('version')   #get box name
            boxinfo = tmp.readlines();tmp.close()
            box = boxinfo[2].split(':')[1].strip()
            box = ''.join(['Box:', box])
            version = boxinfo[3].split(':')[1].strip()  #get system version
            version = ''.join(['version', ':', version])

        #ip = os.popen('ifconfig | grep 10.10.51.')  #get box ip address
        #addr = ip.read();ip.close();addr = addr.split(' ')
        #ip = ''.join([x for x in addr if 'addr' in x])
        tmp = os.popen('ifconfig')  #get box ip address
        ip = tmp.read();tmp.close()
        ip = re.search(r'addr:((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))', ip)
        if ip:
            ip = ''.join(ip.group())

        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time = ''.join(['time:', time])   #get current time
        if ret[0] == 0:
            info = ''.join(['# ', box, '  ', version, '\n# ', ip, '  ', time])
        else:
            info = ''.join(['#', ip, '  ', time])
        write_log(info)
        write_log('')
    except IOError:
        print "open log file failed"
        os._exit(-1)
    return

#write log file
def write_log(name, ret = -1, value = None, refer = '----', mode = 'r'):
    try:
        log = open(log_file, 'a')
        if ret == 0:        #open file success,  write info to the log file
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[pass]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[pass]')
        elif ret == 1:        #sysfs path or file is not exist
            log.write('{0:<22}{1:<56}{2}'.format(name, 'is not exist',      \
                    '[EPATH]\n'))
            print '{0:<22}{1:<56}{2}'.format(name, 'is not exist', '[EPATH]')
        elif ret == 2:        #open file fail, an empty file
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    '----', refer, mode, '[EEMPTY]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, '----', \
                    refer, mode, '[EEMPTY]')
        elif ret == 3:        #error value
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EVALUE]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EVALUE]')
        elif ret == 4:        #error invalid value
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EINVALID]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EINVALID]')
        elif ret == 5:        #error mode
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EMODE]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EMODE]')
        elif ret == 6:        #error value and mode
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EVA&MO]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EVA&MO]')
        elif ret == 7:        #error invalid value and mode
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EIN&MO]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EIN&MO]')
        elif ret == 8:        #UNSUPPORT
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[UNSUPPORT]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[UNSUPPORT]')
        elif ret == 20:        #other error
            log.write('{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}{5}'.format(name,  \
                    value, refer, mode, '[EOTHER]', '\n'))
            print '{0:<22}{1:<32}{2:<18}{3:^6}{4:<10}'.format(name, value,  \
                    refer, mode, '[EOTHER]')
        elif ret == -1:       #print log without prefix
            log.write(name + '\n')
            print name
        log.close()
    except IOError:
        print "open log file fail"
        os._exit(-1)
    return log

#check path
def check_path(check_list):
    unit_name = check_list[0].replace('#####','').strip()   #get unit name
    write_log('{0:^72}'.format(unit_name))
    dir_path = check_list[1].strip()    #joint path
    if os.path.exists(dir_path) == False:   #check path exist or not
        write_log(dir_path, 1)
        write_log('')
        return dir_path, ERRNO['EPATH']
    else:
        return dir_path, 0

#check info
def read_info(file_path):
    attr = Attr()
    attr.path = file_path
    attr.name = os.path.basename(file_path)
    if os.path.isfile(file_path):
        attr.mode = oct(os.stat(file_path).st_mode)[-3:]
        if attr.mode == '200':   #write only file
            attr.value = '----'
            attr.flag = 0
            return attr
    else:
        attr.flag = ERRNO['EPATH']
        return attr
    try:
        f = open(file_path, 'r')
        value = f.readline().splitlines()
        f.close()
        #if value have more than 1 element, here  will throw error
        attr.value = ''.join(value)
        attr.flag = 0
        return attr
    except IOError:
        attr.flag = ERRNO['EPATH']
        return attr

    return attr

#split config file
def config_split(config_file):
    with open(config_file, 'r') as f:
        config_tab = f.readlines()
        check_list = []
        arr = []
        for i,tmp in enumerate(config_tab):
            if tmp == '\n':
                arr.append(i)
        if len(config_tab)-1 not in arr:
            arr.append(len(config_tab)-1)
        for i,tmp in enumerate(arr):
            if tmp == arr[-1]:
                continue
            else:
                a=config_tab[arr[i] + 1 : arr[i+1]]
                check_list.append(a)
    return  check_list

#check sysfs
def check_sysfs(check_list):
    for sys_path in check_list:
        if 'hwinfo' in sys_path[0]:     #hwinfo
            #pass
            check_hwinfo(sys_path)
        elif 'psu' in sys_path[0]:      #psu
            #pass
            check_psu(sys_path)
        elif 'sfp/sfp+' in sys_path[0]: #sfp
            #pass
            check_Xsfp(sys_path, '3')
        elif 'qsfp' in sys_path[0]:     #qsfp
            #pass
            check_Xsfp(sys_path, '4')
        elif 'ctrl' in sys_path[0]:     #ctrl
            #pass
            check_ctrl(sys_path)
        elif 'leds' in sys_path[0]:     #leds
            #pass
            check_leds(sys_path)
        elif 'watchdog' in sys_path[0]: #watchdog
            #pass
            check_watchdog(sys_path)
    return

#check hwinfo
def check_hwinfo(check_list):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global hwinfo_path
    hwinfo_path = ret[0]
    write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items',\
                'value','reference', 'mode', 'result'))
    for line in check_list[2:]:
        attr = Attr()
        arry = line.strip().split('|')
        name = arry[0].strip()
        refer_value = arry[1].strip()
        refer_mode = arry[2].strip()

        file_path = os.path.join(hwinfo_path, name)
        attr.get_info(file_path, refer_value, refer_mode)
        attr.check_value()
        attr.check_mode()
        write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
        del attr

    write_log('')
    return

#check psu
def check_psu(check_list):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global psu_path
    psu_path = ret[0]
    global psu_no

    psu_num = os.listdir(psu_path)
    for psu in psu_num:
        X = psu.replace('psu', '')  #get psu num
        psuX_path = os.path.join(psu_path, psu)  #joint psu path
        title = ''.join(['#****************', psu, '****************#'])
        write_log('{0:^80}'.format(title))
        write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items', \
                'value','reference', 'mode', 'result'))
        attrX = [''.join(x) for x in os.listdir(psuX_path) \
                            if 'fan' in x or 'temp' in x]
        attrX.sort()
        tmp_list = copy.deepcopy(check_list)  #deep copy check_list to tmp_list
        tmp_list.extend(attrX)

        refer_tempX_input = ''
        refer_fanX_input = ''
        refer_pwmX = ''
        refer_fanX_fault = ''
        refer_mode_pwm = ''
        refer_mode_default = 'r'

        for line in tmp_list[2:]:
            attr = Attr()
            arry = line.strip().split('|')
            name = arry[0].strip()
            if len(arry) >= 2:
                refer_value = arry[1].strip()
                refer_mode = arry[2].strip()

            if 'tempX_input' in name:     #record reference value
                refer_tempX_input = refer_value
                continue
            elif 'fanX_input' in name:
                refer_fanX_input = refer_value
                continue
            elif 'pwmX' in name:
                refer_pwmX = refer_value
                refer_mode_pwm = refer_mode
                continue
            elif 'fanX_fault' in name:
                refer_fanX_fault = refer_value
                continue
            elif 'X' in name:
                continue

            if 'temp' in name and 'input' in name:
                refer_value = refer_tempX_input
                refer_mode = refer_mode_default
            elif 'fan' in name and 'input' in name:
                refer_value = refer_fanX_input
                refer_mode = refer_mode_default
            elif 'pwmX' in name:
                refer_value = refer_pwmX
                refer_mode = refer_mode_pwm
            elif 'fan' in name and 'fault' in name:
                refer_value = refer_fanX_fault
                refer_mode = refer_mode_default

            file_path = os.path.join(psuX_path, name)
            attr.get_info(file_path, refer_value, refer_mode)
            if 'present' in attr.name and attr.value == '0':
                log = ''.join([psu, ' is not present'])
                write_log(log)
                break
            else:
                attr.check_value()
                attr.check_mode()
                write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
                if 'power_good' in attr.name and int(attr.value) == 1:
                    psu_no = psu
            del attr
    write_log('')
    return

#check ports sfp or qsfp
def check_Xsfp(check_list, modu_type):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global Xsfp_path
    Xsfp_path = ret[0]
    global Xsfp_port

    portX = os.listdir(Xsfp_path)
    for port in portX:
        attr = Attr()
        file_path = os.path.join(Xsfp_path, port, 'identifier')#check ports type
        attr.get_value_fast(file_path)
        modu_id = attr.value
        if modu_id != '3':  #only 3 represent for sfp, others default to qsfp
            modu_id = '4'
        if modu_id == modu_type:
            #title = ''.join(['#********', port, '********#'])
            #write_log(title)
            line = check_list[2].strip()
            arry = line.strip().split('|')
            name = arry[0].strip()
            file_path = os.path.join(Xsfp_path, port, name)

            attr.get_value_fast(file_path)
            if attr.value == '0':  #check module plug in or out
                #log = ''.join(['     module plug out     '])
                #write_log(log)
                #write_log('')
                pass
            else:
                title = ''.join(['#****************', port, '****************#'])
                Xsfp_port = port    #get a Xsfp present port for time cost calc
                write_log('{0:^80}'.format(title))
                write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items', \
                        'value', 'reference', 'mode', 'result'))
                for line in check_list[2:]:
                    arry = line.strip().split('|')
                    name = arry[0].strip()
                    if len(arry) >= 2:
                        refer_value = arry[1].strip()
                        refer_mode = arry[2].strip()
                    file_path = os.path.join(Xsfp_path, port, name)
                    attr.get_info(file_path, refer_value, refer_mode)
                    attr.check_value()
                    attr.check_mode()
                    write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
        else:
            continue
        del attr

    write_log('')
    return

#check ctrl
def check_ctrl(check_list):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global ctrl_path
    ctrl_path = ret[0]

    global fan_number
    fan_number = 0
    global fanr_number
    fanr_number = 0
    write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items', \
                'value','reference', 'mode', 'result'))
    
    attr = Attr()
    arry = check_list[2].strip().split('|')    #get fan number
    name = arry[0].strip()
    if len(arry) >= 2:
        refer_value = arry[1].strip()
        refer_mode = arry[2].strip()
    file_path = os.path.join(ctrl_path, name)
    attr.get_info(file_path, refer_value, refer_mode)
    if attr.value.isdigit() and int(attr.value) < 20:#fan number must be a digist
        fan_number = attr.value
        attr.check_value()
        attr.check_mode()
        write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
    else:
        write_log('fan number error')
        return

    arry = check_list[3].strip().split('|')    #get fanr number
    name = arry[0].strip()
    if len(arry) >= 2:
        refer_value = arry[1].strip()
        refer_mode = arry[2].strip()
    file_path = os.path.join(ctrl_path, name)
    attr.get_info(file_path, refer_value, refer_mode)
    if attr.value.isdigit() and int(attr.value) < 20:#fanr number must be a digist
        fanr_number = attr.value
        attr.check_value()
        attr.check_mode()
        write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
    else:
        write_log('fanr number error')
        return
    del attr

    for line in check_list[4:]:
        attr = Attr()
        arry = line.strip().split('|')
        name = arry[0].strip()
        if len(line) >= 2:
            refer_value = arry[1].strip()
            refer_mode = arry[2].strip()

        if 'fanX' in name or 'pwmX' in name:  #get fanX info
            n = 1
            while n <= int(fan_number):
                attrX = name.replace('X',str(n))
                file_path = os.path.join(ctrl_path, attrX)
                attr.get_info(file_path, refer_value, refer_mode)
                attr.check_value()
                attr.check_mode()
                write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
                n += 1
        elif 'fanrX' in name:   #get fanrX info
            n = 1
            while n <= int(fanr_number):
                attrX = name.replace('X',str(n))
                file_path = os.path.join(ctrl_path, attrX)
                attr.get_info(file_path, refer_value, refer_mode)
                attr.check_value()
                attr.check_mode()
                write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
                n += 1
        else:
            file_path = os.path.join(ctrl_path, name)
            attr.get_info(file_path, refer_value, refer_mode)
            attr.check_value()
            attr.check_mode()
            write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
        del attr

    write_log('')
    return

#check leds
def check_leds(check_list):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global leds_path
    leds_path = ret[0]

    write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items', \
                'value','reference', 'mode', 'result'))
    attrX = [''.join([x, '/brightness'])    \
                for x in os.listdir(leds_path) if 'psu' in x]

    check_list.extend(attrX)
    refer_psuX_led = ''
    refer_psuX_mode = ''

    for line in check_list[2:]:
        attr = Attr()
        arry = line.strip().split('|')
        name = arry[0].strip()
        if len(arry) >= 2:
            refer_value = arry[1].strip()
            refer_mode = arry[2].strip()
        if 'psuX_led' in name:
            refer_psuX_led = refer_value
            refer_psuX_mode = refer_mode
            continue
        elif 'X' in name:
            continue

        if 'psu' in name and 'led' in name:
            refer_value = refer_psuX_led
            refer_mode = refer_psuX_mode

        file_path = os.path.join(leds_path, name)
        attr.get_info(file_path, refer_value, refer_mode)
        attr.set_name(name)
        attr.check_value()
        attr.check_mode()
        write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
        del attr

    write_log('')
    return

#check watchdog
def check_watchdog(check_list):
    ret = check_path(check_list)
    if ret[1] != 0:
        return
    global watchdog_path
    watchdog_path = ret[0]

    write_log('{0:<22}{1:<32}{2:<18}{3:<6}{4:<10}'.format('items', \
                'value','reference', 'mode', 'result'))
    
    for line in check_list[2:]:
        attr = Attr()
        arry = line.strip().split('|')
        name = arry[0].strip()
        if len(arry) >= 2:
            refer_value = arry[1].strip()
            refer_mode = arry[2].strip()
        file_path = os.path.join(watchdog_path, name)
        attr.get_info(file_path, refer_value, refer_mode)
        attr.check_value()
        attr.check_mode()
        write_log(attr.name, attr.flag, attr.value, attr.refer_value, attr.mode)
        del attr

    write_log('')
    return

#input tips
def check_input():
    key = raw_input('input yes or no:')

    while key != 'yes' and key != 'no':
        key = raw_input('input yes or no:')

    if key == 'no':
        return 1
    else:
        return 0

#check psu fan pwm control
def check_fan_ctrl():
    if int(fan_number) <= 1:
        return

    print '\n*****************************************'
    write_log('{0:^80}'.format('check fan pwm set'))
    i = random.randint(1,int(fan_number))
    pwmX = 'pwmX'.replace('X', str(i))
    fanX_input = 'fanX_input'.replace('X', str(i))
    fanX_fault = 'fanX_fault'.replace('X', str(i))
    pwm_value = read_info(ctrl_path + '/'  + pwmX).value
    input_value = read_info(ctrl_path + '/' + fanX_input).value
    fault_value = read_info(ctrl_path + '/' + fanX_fault).value

    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))
    write_log('pwm set test')
    os.system('echo 0 > '+ ctrl_path + '/' + pwmX)
    write_log('set pwm 0')
    time.sleep(2)
    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))
    os.system('echo 50 > '+ ctrl_path + '/' + pwmX)
    write_log('set pwm 50')
    time.sleep(2)
    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))
    os.system('echo 100 > '+ ctrl_path + '/' + pwmX)
    write_log('set pwm 100')
    time.sleep(2)
    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))
    os.system('echo 150 > '+ ctrl_path + '/' + pwmX)
    write_log('set pwm 150')
    time.sleep(2)
    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))
    os.system('echo 255 > '+ ctrl_path + '/' + pwmX)
    write_log('set pwm 255')
    time.sleep(2)
    write_log('{0}{1}{2:<5}{3}{4}{5:<8}{6}{7}{8:<2}'.format(pwmX, ':',\
            pwm_value, fanX_input, ':', input_value, fanX_fault, ':', fault_value))

    raw_input('press any key to continue..')
    print ''

    return

#show some shell cat commend cost time
def show_cost_time():
    print '\n*****************************************'
    print 'do you want test mutiple read data'
    ret = check_input()
    if ret:
        return

    print 'calc multiple read data cost time, please wait a moment......\n'
    write_log('{0:^80}'.format('check cat attr cost time'))
    dir_path = []
    attr = []
    dir_path.append(os.path.join(psu_path, psu_no,'fan*_input'))
    dir_path.append(os.path.join(Xsfp_path, Xsfp_port, 'temperature'))
    dir_path.append(os.path.join(ctrl_path,'fan*_input'))
    attr.append(psu_no + '/fan*_input')
    attr.append(Xsfp_port + '/temperature')
    attr.append('ctrl' + '/fan*_input')

    for i in range(0,3):
        delta = 0
        for n in range(0,5):
            d1 = datetime.datetime.now()
            os.system('cat ' + dir_path[i] + ' >/dev/null')
            d2 = datetime.datetime.now()
            delta += (d2 - d1).microseconds
            time.sleep(4)
        delta /= (10.0*1000000)#get average run time and convert microsecond to second
        write_log('cat ' + attr[i] + ' run time:' + str(delta) + 's')
    write_log('')
    return

#ckeck kernel .config
def check_kernel_config(config_file):
    write_log('{0:^80}'.format('check kernel config'))
    if os.path.isfile('/proc/config.gz'): 
        ret = commands.getstatusoutput('zcat /proc/config.gz')
        if ret[0] != 0:
            write_log(ret[1])
            return
        kernel_config = [x for x in ret[1].split('\n') if '#' not in x]
       
        with open(config_file, 'r') as f:
            check_config_list = f.readlines()
            count = 0
            for x in check_config_list:
                x = x.strip()
                i = 0
                for y in kernel_config:
                    if x in y:
                        i = 1
                        break
                if i == 0:
                    count += 1
                    write_log('{0}{1}'.format(x, ' is not set'))
            if count == 0:
                write_log('check kernel config  [pass]')
    else:
        write_log('/proc/config.gz is not exist')
        write_log('please set CONFIG_IKCONFIG=y and CONFIG_IKCONFIG_PROC=y ')

    write_log('')
    return

#check rtc
def check_rtc():
    print '\n*****************************************'
    print 'rtc check....'
    print 'system time:'
    os.system('date')
    print 'rtc time:'
    os.system('hwclock -r')

    print 'do you want test rtc?'
    ret = check_input()
    if ret:
        return

    key = raw_input('please input real time(format:"20160525 10:01:00"):')
    os.system('date -s ' + key)
    os.system('hwclock -w')
    print 'rtc time:'
    os.system('hwclock -r')
    os.system('hwclock -s')
    print 'system time:'
    os.system('date')
    #print '*****************************************'
    #print '**please check system time after reboot**'
    #print '*****************************************'
    raw_input('press any key to continue..')
    print ''

    return


#test watchdog work normal or not
def test_watchdog():
    print '\n*****************************************'
    print 'do you want test watchdog, it will reboot machine.'
    ret = check_input()
    if ret:
        return

    write_log('{0:^80}'.format('watchdog test'))
    #print '{0:^80}'.format('watchdog test')
    print 'enable watchdog'
    os.system('echo 10 > ' + watchdog_path  +'/timeout')
    os.system('echo 1 > ' + watchdog_path  +'/wdt_enable')
    for i in range(0,9):
        #os.system('cat ' + watchdog_path  +'/time_left')
        ret = commands.getstatusoutput('cat ' + watchdog_path  +'/time_left')
        write_log(ret[1])
        time.sleep(1)
    write_log('feed the dog')
    #print 'feed the dog'
    os.system('echo 1 > ' + watchdog_path  +'/keep_alive')
    time.sleep(5)
    write_log('feed the dog success')
    #print 'feed the dog success'

    os.system('echo 0 > ' + watchdog_path  +'/wdt_enable')
    write_log('test watchdog reboot')
    #print 'test watchdog reboot'
    os.system('echo 10 > ' + watchdog_path  +'/timeout')
    os.system('echo 1 > ' + watchdog_path  +'/wdt_enable')
    for i in range(0,10):
        #os.system('cat ' + watchdog_path  +'/time_left')
        ret = commands.getstatusoutput('cat ' + watchdog_path  +'/time_left')
        write_log(ret[1])
        time.sleep(1)
    time.sleep(5)   #watchdog will wait a moment to reboot
    write_log('watchdog reboot failed')
    #print 'watchdog reboot failed'

    return

#main function entry
if __name__=="__main__":
    if len(sys.argv) <= 1:
        print '****** ERR:please input config file name *****'
        print 'Under super user mode'
        print 'Example: python utest.py as5712.config check_config-x86.config'
        exit(-1)
    init_log()
    check_list = config_split(sys.argv[1])
    check_sysfs(check_list)
    #check_fan_ctrl()
    #check_kernel_config(sys.argv[2])
    show_cost_time()
    check_rtc()
    test_watchdog()
