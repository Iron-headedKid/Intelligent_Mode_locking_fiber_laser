import csv
import os
from datetime import datetime


# 创建数据保存路径
def init_path():
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
    return image_path, waveform_csv_path, spectrum_csv_path


def init_path_GA():
    current_date = datetime.now().strftime("%Y_%m_%d")
    current_time = datetime.now().strftime("%H_%M_%S")
    save_path_date = 'D:/Experiment_Data/Auto_mode-locking_py/GA_Test/' + str(current_date)
    save_path_time = save_path_date + '/' + current_time
    # image_path = save_path_time + '/Image'
    trajectory_csv_path = save_path_time + '/' + current_time + 'Trajectory.csv'
    MLpoints_csv_path = save_path_time + '/' + current_time + 'MLpoints.csv'
    generation_csv_path = save_path_time + '/' + current_time + 'Generation.csv'
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
    return trajectory_csv_path, MLpoints_csv_path, generation_csv_path


def init_path_GA_saving_time():
    current_date = datetime.now().strftime("%Y_%m_%d")
    current_time = datetime.now().strftime("%H_%M_%S")
    save_path_date = 'D:/Experiment_Data/Auto_mode-locking_py/GA_Test/' + str(current_date)
    save_path_time = save_path_date + '/' + current_time + 'saving_time'
    timing_path = save_path_time + '/' + current_time + 'Timing.csv'
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
    return timing_path


def save_csv(path, data):
    with open(path, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


