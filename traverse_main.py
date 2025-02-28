# -*- coding: utf-8 -*-
from datetime import datetime
import time
import tools
import Thorlabs_MPC320_api as MPC320
import DAHENG_Camera_control as DAHENG
import Rigol_DS4054_control as DS4054
import YOKOGAWA_AQ6370C_control as YOKOGAWA


# 判断锁模并保存数据
def judge_mode_locking(now_angle, threshold=0.5):
    global last_angle
    print(now_angle)
    if (threshold < DS4054.get_vpp() < 10) and (any(abs(x-y) > 5 for x, y in zip(last_angle, now_angle))):
        OSA.single_scan()        # 光谱仪扫描
        for i in range(5):
            if threshold < DS4054.get_vpp() < 10:
                if i == 4:
                    print("锁模！保存数据")
                    current_time = datetime.now().strftime("%m%d_%H%M%S")
                    # 保存光斑图像和波形信息
                    Camera.save_image(image_path, current_time)
                    tools.save_csv(waveform_path, [current_time] + now_angle + [DS4054.get_vpp()] + [DS4054.get_frequency()])
                    tools.save_csv(waveform_path, DS4054.get_waveform())
                    # 保存光谱信息
                    OSA.judge_scan()
                    tools.save_csv(spectrum_path, [current_time])
                    tools.save_csv(spectrum_path, OSA.get_trace_intensity())
                    last_angle = now_angle[:]  # 更新上一次锁模的角度
                else:
                    time.sleep(0.1)
            else:
                break


# 连接设备
MPC = MPC320.MPC320()
DS4054 = DS4054.DS4054()
Camera = DAHENG.DAHENGCamera()
OSA = YOKOGAWA.AQ6370C()
# 初始化数据存储路径
image_path, waveform_path, spectrum_path = tools.init_path()

wl = OSA.get_trace_wave_length()
tools.save_csv(spectrum_path, wl)


last_angle = [-10, -10, -10]
# 定义初始位置
original_angle = [0, 0, 0]
for i in range(3):
    MPC.move_to(i+1, original_angle[i])

# 开始遍历
start_time = time.time()
print("开始遍历")
angle = MPC.get_angle()
judge_mode_locking(angle)
while angle[2] <= 159.6:
    if angle[1] < 80:
        while angle[1] <= 159.6:
            if angle[0] < 80:
                # 正向旋转
                while angle[0] <= 159.6:
                    MPC.move_jog(1, 1)
                    angle = MPC.get_angle()
                    judge_mode_locking(angle)
                # end_time = time.time()
                # print(f"耗时{end_time - start_time}s")
            else:
                # 反向旋转
                while angle[0] >= 0.4:
                    MPC.move_jog(1, 2)
                    angle = MPC.get_angle()
                    judge_mode_locking(angle)
            for i in range(5):
                MPC.move_jog(2, 1)
                angle = MPC.get_angle()
                judge_mode_locking(angle)
            end_time = time.time()
            print(f"遍历过程累计耗时{end_time - start_time} s")
    else:
        while angle[1] >= 0.4:
            if angle[0] < 80:
                while angle[0] <= 159.6:
                    MPC.move_jog(1, 1)
                    angle = MPC.get_angle()
                    judge_mode_locking(angle)
            else:
                while angle[0] >= 0.4:
                    MPC.move_jog(1, 2)
                    angle = MPC.get_angle()
                    judge_mode_locking(angle)
            for i in range(5):
                MPC.move_jog(2, 2)
                angle = MPC.get_angle()
                judge_mode_locking(angle)
            end_time = time.time()
            print(f"遍历过程累计耗时{end_time - start_time} s")
    for i in range(5):
        MPC.move_jog(3, 1)
        angle = MPC.get_angle()
        judge_mode_locking(angle)
end_time = time.time()
print("遍历结束")
print(f"遍历过程总耗时{end_time - start_time} s")
