# -*- coding: utf-8 -*-
from datetime import datetime
import os
import csv
import time
import Thorlabs_MPC320_api as MPC320
import DAHENG_Camera_control as DAHENG
import Rigol_DS4054_control as DS4054
import YOKOGAWA_AQ6370C_control as YOKOGAWA

MPC = MPC320.MPC320()
Camera = DAHENG.DAHENGCamera()
DS4054 = DS4054.DS4054()
OSA = YOKOGAWA.AQ6370C()


current_date = datetime.now().strftime("%Y_%m_%d")
current_time = datetime.now().strftime("%H_%M_%S")
# print(current_date)
# print(current_time)
save_path_date = 'D:/Experiment_Data/Auto_mode-locking_py/Test/' + str(current_date)
save_path_time = save_path_date + '/' + current_time
image_path = save_path_time + '/Image'
waveform_csv_path = save_path_time + '/' + current_time + 'Waveform.csv'
spectrum_csv_path = save_path_time + '/' + current_time + 'Spectrum.csv'
try:
    os.mkdir(save_path_date)
    print(f'{save_path_date}文件夹已创建')
except FileExistsError:
    print('date文件夹已存在')
try:
    os.mkdir(save_path_time)
    print(f'{save_path_time}文件夹已创建')
except FileExistsError:
    print('time文件夹已存在')
try:
    os.mkdir(image_path)
    print(f'{image_path}文件夹已创建')
except FileExistsError:
    print('image文件夹已存在')


print("开始保存数据")
start_time = time.time()
current_time = datetime.now().strftime("%m%d_%H%M%S")

OSA.single_scan()

Camera.save_image(image_path, current_time)

angle = MPC.get_angle()
angle.insert(0, current_time)
waveform = DS4054.get_waveform()
with open(waveform_csv_path, "a", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(angle)
    writer.writerow(waveform)

OSA.judge_scan()
wl = OSA.get_trace_wave_length()
spectrum = OSA.get_trace_intensity()
with open(spectrum_csv_path, "a", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(wl)
    writer.writerow([current_time])
    writer.writerow(spectrum)

end_time = time.time()
print(f'数据保存花费总时间：{end_time - start_time}秒')

