# -*- coding: utf-8 -*-
import pyvisa
import numpy as np
import time


class AQ6370C:
    def __init__(self, address='GPIB0::1::INSTR'):
        self.rm = pyvisa.ResourceManager()
        self.address = address
        self.AQ6370C = self.rm.open_resource(self.address)   # 打开AQ6370C
        print(self.AQ6370C.query('*IDN?'))  # 查询设备的ID信息
        self.AQ6370C.write('*CLS')  # 清除设备的事件寄存器
        self.setting()
        self.single_scan()
        self.judge_scan()
        print("OSA initialized")

    # format 0 means AQ6317(short command), 1 means AQ6370C(long command).
    def setting(self, start_wl='960.00', stop_wl='1170.00', res='0.5', mode='6', format='1'):
        if format == '0':
            self.AQ6370C.write(':SYSTem:COMMunicate:CFORmat ', format)
            # 设置扫描波长范围 (short command)
            self.AQ6370C.write('STAWL' + start_wl)
            self.AQ6370C.write('STPWL' + stop_wl)
            # 设置扫描分辨率
            self.AQ6370C.write('RESLN' + res)
            # print('分辨率是', int(self.AQ6370C.query('RESLN?')), 'nm')
        elif format == '1':
            self.AQ6370C.write('CFORM' + format)
            # 设置扫描波长范围 (long command)
            self.AQ6370C.write(f':SENSe:WAVelength:STARt {start_wl}NM')
            self.AQ6370C.write(f':SENSe:WAVelength:STOP {stop_wl}NM')
            # 设置扫描分辨率
            self.AQ6370C.write(f':SENSe:BANDwidth:RESolution {res}NM')
            # 设置扫描模式, 默认normal=6,
            self.AQ6370C.write(f':SENSe:SENSe {mode}')
            # print('分辨率是', self.AQ6370C.query(':SENSE:BANDWIDTH?'))
        print('setting finish')

    def single_scan(self):
        self.judge_zeroing()
        # 进行单次扫描
        self.AQ6370C.write(':INITiate:SMODe SINGle;:INITiate')

    def judge_scan(self):
        # start_time = time.time()
        # 查询扫描状态，1-扫描完成，0-扫描中。在扫描完成读取后该操作事件寄存器的1会马上变成0
        while True:
            if int(self.AQ6370C.query(':STATus:OPERation?')) == 1:
                # end_time = time.time()
                # print("scan finish")
                # print(f"单次扫描耗时：{end_time - start_time}秒")
                break

        # print('operation', self.AQ6370C.query(':STATus:OPERation?'))
        # print('condition', self.AQ6370C.query(':STATus:OPERation:CONDition?'))  # 查询操作状态寄存器，0-未扫描，1-完成扫描

    def get_trace_wave_length(self):
        # 切换到短命令模式
        self.AQ6370C.write(':SYSTem:COMMunicate:CFORmat 0')
        # 读取数据
        wl = self.AQ6370C.query('WDATA').strip().split(',')[1:]
        wl = np.asarray(wl, 'f').T
        # 切换回长命令模式
        self.AQ6370C.write('CFORM1')
        return wl

    def get_trace_intensity(self):
        # 切换到短命令模式
        self.AQ6370C.write(':SYSTem:COMMunicate:CFORmat 0')
        # 读取数据
        intensity = self.AQ6370C.query('LDATA').strip().split(',')[1:]
        intensity = np.asarray(intensity, 'f').T
        # 切换回长命令模式
        self.AQ6370C.write('CFORM1')
        return intensity

    def judge_zeroing(self):
        # self.AQ6370C.write(':CALIBRATION:ZERO ONCE')
        if int(self.AQ6370C.query(':CALIBRATION:ZERO:STATUS?')) == 1:
            print("正在进行校正...")
        # start_time = time.time()
        while int(self.AQ6370C.query(':CALIBRATION:ZERO:STATUS?')) == 1:
            time.sleep(0.05)
        # end_time = time.time()
        # print(f"单次校正耗时：{end_time - start_time}秒")
        # print("校正完成")


# OSA = AQ6370C()
# OSA.single_scan()
# OSA.judge_scan()
# print(OSA.get_trace_wave_length())
# print(OSA.get_trace_intensity())
# OSA.single_scan()
# OSA.judge_scan()

