import serial
import re
import binascii
import time
import random
# import pandas as pd
import csv
import serial.tools.list_ports as LP


METERIDS = 100
CUMULANTS = 100

WAITING = 20
INIT_SAVE_DATA = ['numble',
            'time',
            'mode',
            'setData',
            'resultData',
            'isErr',
            'setSendData',
            'setRecvData',
            'readSendData',
            'readRecvData',]

TEST_LIST = ['meterID'] #,'model','cumulant','mode','meterTime']


def get_time(st = "%Y-%m-%d %H:%M:%S"):
    return time.strftime(st,time.localtime(time.time()))


class ser_my(serial.Serial):
    def __init__(self,port, baudrate=9600, parity = serial.PARITY_NONE):
        super().__init__(port=port, baudrate = baudrate, parity=parity)
        self.closed()

    def send(self,data):
        self.opened()
        try:
            data = binascii.unhexlify(data)
            self.write(data)
        except Exception as e:
            print("{} | {}".format(get_time(),str(e)))

    def recv(self):
        self.opened()
        for i in range(0, WAITING):
            inwaiting = self.in_waiting
            if inwaiting:
                recv = self.read_all()
                return self.recv_parse(recv)
            time.sleep(1)

    def recv_parse(self, data, code='utf-8'):
        datas = data
        if code == 'utf-8':
            try:
                datas = binascii.hexlify(data).decode('utf-8').upper()
                re_com = re.compile('68.*16')
                datas = re.findall(re_com, datas)[0]
            except:
                self.recv_parse(data,'ascii')
        if code == 'ascii':
            try:
                datas = data.decode('ascii')
            except:
                self.recv_parse(data,'GBK')

        if code == 'GBK':
            try:
                datas = data.decode('GBK').replace('\n','').replace('\r','')
            except:
                datas = data
        return datas

    def closed(self):
        if self.is_open:
            self.close()

    def opened(self):
        if not self.is_open:
            self.open()


class protocol():

    @classmethod
    def get_name(cls,):
        return cls.__dict__

    def parse(self, data, mode):
        mode = 'parse_' + mode
        name = self.get_name()
        assert mode in [i for i in name.keys()]
        res = eval('self.' + mode)(data)
        return res

    def set(self, data, mode):
        mode = 'set_' + mode
        name = self.get_name()
        assert mode in [i for i in name.keys()]
        res = eval('self.' + mode)(data)
        return res

    def read(self,mode):
        mode = 'read_' + mode
        name = self.get_name()
        assert mode in name.keys()
        res = eval('self.' + mode)()
        return res

    def set_meterID(self, meterID):
        assert isinstance(meterID, str)
        meterID = meterID.upper()
        L = len(meterID)
        if L < 10:
            meterID = meterID.rjust(10, '0')
        elif L > 10:
            meterID = meterID[:10]
        p0 = 'FE FE FE FE FE '
        p1 = '68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 15 00 0A A0 18 03 00 00'
        p2 = meterID
        p3 = self.checkSum(p1 + p2)
        p4 = '16'

        return (p0+ p1+p2+p3+p4).replace(' ','')

    def set_model(self, model):
        model_dict = {
            'G1.6':'02', 'G2.5':'03', 'G4.0':'04',
            'G4':'04', 'G6.0':'05','G6':'05',
            'G10':'06', 'G10.0':'06', 'G16':'07',
            'G16.0':'07','G25':'08','G25.0':'08',
            'G40':'09', 'G40.0':'09', 'G65':'0A',
            'G65.0':'0A','G4.0P': '0B', 'G4P': '0B',
        }
        assert model in model_dict.keys()

        model = model_dict[model]
        p1 = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 04 00 06 A0 22 01 00 00'
        p2 = model
        p3 = self.checkSum(p1+p2)
        p4 = '16'
        return (p1+p2+p3+p4).replace(' ','')

    def set_cumulant(self, cumulant):
        assert isinstance(cumulant, str)
        if int(cumulant) >= 99999999 or int(cumulant) <= 0:
            return False
        cumulant = cumulant.rjust(8, '0')
        p1 = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 16 00 0B A0 16 01 00 00 '
        p2 = cumulant
        p3 = '00 00'
        p4 = self.checkSum(p1+p2+p3)
        p5 = '16'
        return (p1+p2+p3+p4+p5).replace(' ','')

    def set_mode(self, mode):
        assert isinstance(mode, str)
        mode_dict = {
            '正常态':'03',
            '检测态':'02',
            '校正态':'01'
        }
        assert mode in mode_dict.keys()
        mode = mode_dict[mode]
        p1 = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 04 00 06 A0 23 01 00 00'
        p2 = mode
        p3 = self.checkSum(p1+p2)
        p4 = '16'
        return (p1+p2+p3+p4).replace(' ','')

    def set_meterTime(self, setTime):
        assert len(setTime) == 14
        p1 = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F9 77 88 99 55 04 00 0C A0 15 01 00 00'
        p2 = setTime
        p3 = self.checkSum(p1+p2)
        p4 = '16'
        return (p1+p2+p3+p4).replace(' ','')

    def read_meterID(self):
        p = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 03 00 03 81 0A 01 85 16'
        return p.replace(' ','')

    def read_model(self):
        p = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 01 00 03 81 0C 01 85 16'
        return p.replace(' ','')

    def read_meterTime(self):
        p = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 21 00 03 90 0F 01 B7 16'
        return p.replace(' ', '')

    def read_cumulant(self):
        p = 'FE FE FE FE FE 68 AB 57 58 AA AA AA AA AA F2 77 88 99 55 21 00 03 90 0F 01 B7 16'
        return p.replace(' ', '')

    def parse_meterID(self, data):
        '''FE FE FE FE FE 68 AB 57 58 F2 77 88 99 55 12 34 56 78 90 83 00 03 81 0A 01 57 16'''
        data = data.replace(' ','')
        re_com = '68.*?77889955(.*?)830003810A01'
        meterID = re.findall(re_com,data)
        if meterID:
            return meterID

    def parse_model(self, data):
        pass

    def parse_cumulant(self, data):
        pass

    def parse_meterTime(self, data):
        pass

    def checkSum(self, data):
        data = data.replace(' ', '')
        check = 0x00
        L = len(data)
        for i in range(0, L, 2):
            check = int(data[i:(i + 2)], 16) + check
            if check > 0xff:
                check -= 0x100
        check_hex = hex(check)[2:]
        return check_hex.rjust(2, '0').upper()


class testCase():
    def __init__(self):
        self.randomData = randomset()
        self.pro = protocol()
        self.data_list = []

    @classmethod
    def name(cls):
        return cls.__dict__

    def run(self):
        for i in TEST_LIST:
            self.test(i)
        return self.data_list


    def test(self, mode):
        modes = 'test_' + mode
        name = self.name()
        assert modes in name.keys()
        eval('self.' + modes)()

    def test_meterID(self,):
        res = []
        for i in range(METERIDS):
            data = self.randomData.set('meterID')
            res.append({
                'mode': 'meterID',
                'setData': data,
                'wishData':data,
            })
        self.data_list += res

    def test_model(self,):
        res = []
        p = ['G1.6', 'G2.5', 'G4.0', 'G6.0', 'G10.0', 'G16.0', 'G25.0', 'G40.0', 'G65.0', 'G4.0P']
        for i in p:
            res.append({
                'mode': 'model',
                'setData':i,
                'wishData':i,
            })
        self.data_list += res

    def test_cumulant(self, max = '999999'):
        cumulant_list = ['0','9','99','999','9999','99999','999999','9999999','99999999']
        res = [{'mode': 'model','setData':i,'wishData':i} for i in cumulant_list[:cumulant_list.index(max)+1]]

        for i in range(METERIDS-len(res)):
            res.append({
                'mode': 'model',
                'setData':i,
                'wishData':i
            })

        self.data_list += res

    def test_mode(self,):
        mode_list = ['正常态','检测态','校正态']
        res = [{'mode': 'mode','setData': i, 'wishData': i} for i in mode_list]
        self.data_list += res

    def test_meterTime(self,):
        res = [
        {'mode': 'meterTime', 'setData': '20160228235955', 'wishData': '2016022900'},
        {'mode': 'meterTime', 'setData': '20160229235955', 'wishData': '2016030100'},
        {'mode': 'meterTime', 'setData':, 'wishData':},
        {'mode': 'meterTime', 'setData': '20190228235955', 'wishData': '2019030100'},
        {'mode': 'meterTime', 'setData': '20190229235955', 'wishData': '2019030100'},

        {'mode': 'meterTime', 'setData':, 'wishData':},
        {'mode': 'meterTime', 'setData':, 'wishData':},
        {'mode': 'meterTime', 'setData':, 'wishData':},
        {'mode': 'meterTime', 'setData':, 'wishData':},
        {'mode': 'meterTime', 'setData':, 'wishData':},

        ]


class randomset():
    @classmethod
    def name(cls):
        return cls.__dict__

    def set(self, mode):
        mode = 'set_random_' + mode
        assert mode in self.name().keys()
        res = eval('self.{}'.format(mode))()
        return res

    def set_random_meterID(self, length = 10, isHex = 0):
        meterID_list = ['0','1','2','3','4','5','6','7','8','9']
        if isHex:
            meterID_list = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        res = ''
        for i in range(length):
            res += random.choice(meterID_list)

        return res

    def set_random_cumulant(self,max=99999999,):
        return str(random.randint(0,max))


class print_save():
    def __init__(self):
        self.init_save()

    def run(self,data):
        try:
            self.save_data(data)
            print("{} | 存储成功 | {},{}".format(get_time(), data['mode'], data['setData']))
            self.print_data(data)
            return True

        except Exception as e:
            print('{} | 存储失败 | {}'.format(get_time(),str(e)))

    def init_save(self):
        self.save_data(INIT_SAVE_DATA,m='w')

    def save_data(self,data,m='a'):
        if isinstance(data, dict):
            data = [
                data[i] for i in INIT_SAVE_DATA
            ]
        with open('xx.csv', m, newline='') as f:
            csv_f = csv.writer(f)
            csv_f.writerow(data)

    def print_data(self,data):
        for i in INIT_SAVE_DATA:
            print(i.ljust(20,'—'),data[i])
        print('')



class main():
    def __init__(self, port, baudrate=9600):
        self.pro = protocol()
        self.ser = ser_my(port, baudrate=baudrate)
        self.testcase = testCase()
        self.save = print_save()
        self.result = {}

    def run(self,):
        data_list = self.testcase.run()

        for i in range(len(data_list)):
            initdata = data_list[i]
            mode = initdata['mode']
            self.result['mode'] = mode
            self.result['numble'] = i+1
            self.result['setData'] = initdata['setData']

            setRecv = self.set(initdata)
            if setRecv:
                readRecv = self.read(initdata)
                if readRecv:
                    self.parse(readRecv, initdata)

            self.result['time'] = get_time()

            if self.save.run(self.result):
                self.result = {}

            for i in range(5):
                if self.ser.in_waiting:
                    time.sleep(10)

    def set(self,data):
        mode = data['mode']
        setData = data['setData']
        sendData = self.pro.set(setData,mode)
        self.ser.send(sendData)
        self.result['setSendData'] = sendData
        recv = self.ser.recv()
        self.result['setRecvData'] = recv
        return recv


    def read(self, data):
        mode = data['mode']
        sendData = self.pro.read(mode)
        self.ser.send(sendData)
        self.result['readSendData'] = sendData
        recv = self.ser.recv()
        self.result['readRecvData'] = recv
        return recv

    def parse(self, recvdata, data):
        mode = data['mode']
        res = self.pro.parse(recvdata,mode)[0]
        self.result['resultData'] = res
        if res == self.result['setData']:
            err = 'Pass'
        else:
            err = 'Error'
        self.result['isErr'] = err

def choose_port():
    s = lambda x:str(x).split('-')[0].strip(' ').upper()
    pl = list(LP.comports())
    port_list = [s(i) for i in pl]
    nb_port_list = [s(i)[3:] for i in pl]
    port_in = input('{}\n输入端口号：'.format(str(port_list)[1:-1].replace("'",''))).upper()
    if port_in in port_list:
        return port_in
    elif port_in in nb_port_list:
        return 'com' + port_in
    else:
        print('串口输入错误，请重新输入\n')

if __name__ == '__main__':
    port = choose_port()
    m = main(port)
    m.run()