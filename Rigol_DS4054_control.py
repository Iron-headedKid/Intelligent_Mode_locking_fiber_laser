# -*- coding: utf-8 -*-
import pyvisa


class DS4054:
    def __init__(self, address='USB0::0x1AB1::0x04B1::DS4A200400040::INSTR'):
        self.rm = pyvisa.ResourceManager()
        self.address = address
        self.DS4054 = self.rm.open_resource(self.address)   # 打开DS4054
        print(self.DS4054.query('*IDN?'))  # 查询DS4054的ID信息
        self.DS4054.write('*CLS')  # 清除DS4054的事件寄存器
        self.setting()
        print("Oscilloscope initialized")

    def setting(self, channel=1, y_scale=0.5, x_scale=1e-7, y_offset=-1.5, trigger_level=0.3):
        self.DS4054.write(f':CHANnel{channel}:DISPlay ON')  # Open channel
        self.DS4054.write(f':CHANnel{channel}:COUPling AC')  # Set channel to AC coupling
        self.DS4054.write(f':CHANnel{channel}:IMPedance FIFTy')  # Set channel to 50 ohm impedance
        self.DS4054.write(f':TRIGger:CAN:SOURce CHANnel{channel}')  # Set trigger source to channel 1
        self.DS4054.write(f':CHANnel{channel}:SCALe {y_scale}')  # Set scale to {y_scale} V/div
        self.DS4054.write(f':TIMebase:SCALe {x_scale}')  # Set timebase scale to {x_scale} s/div
        self.DS4054.write(f':CHANnel{channel}:OFFSet {y_offset}')  # Set offset to {y_offset} V
        self.DS4054.write(f':TRIGger:CAN:SOURce CHANnel{channel}')  # Set trigger source to channel
        self.DS4054.write(f':TRIGger:CAN:LEVel {trigger_level}')  # Set trigger level to {trigger_level} V
        self.DS4054.write(f':MEASure:SOURce CHANnel{channel}')      # 设置测量源为通道1
        print("setting finish")

    def get_vpp(self):
        return float(self.DS4054.query(':MEASure:VPP:SCURrent?'))  # 测量通道的当前峰峰值（V）

    def get_frequency(self):
        return float(self.DS4054.query(':MEASure:FREQuency:SCURrent?'))  # 测量通道的当前频率（Hz）

    def get_waveform(self, channel=1):
        self.DS4054.write(f':WAVeform:SOURce CHANnel{channel}')  # 设置波形数据的来源。
        self.DS4054.write(':WAVeform:FORMat BYTE')  # 设置波形数据的格式
        self.DS4054.write(':WAVeform:DATA?')
        raw_data = self.DS4054.read_raw()        # 读取当前显示图像的位图数据流。数据类型是bytes。
        # 返回一个列表，这个列表是从十六进制形式的字节类型转换成十进制整型的列表。
        return list(raw_data[11:-1])

    def close(self):
        self.DS4054.close()
        print("Oscilloscope closed")


# OSI = DS4054()
# waveform = OSI.get_waveform()
# print(waveform)
# OSI.close()



