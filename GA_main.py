import Thorlabs_MPC320_api as EPC
import Rigol_DS4054_control as Osc
import time
import tools
import numpy as np
import GA
import random
import Data_processing as dp

# 可视化初始化
# plt.ion()       # 开启交互模式
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.set_xlim(0, 160)
# ax.set_ylim(0, 160)
# ax.set_zlim(0, 160)
# sc = ax.scatter(-1, -1, -1, s=20, c=5, cmap='inferno', vmin=0, vmax=5)
# plt.colorbar(sc)


def gaussian(d, sigma=3, alpha=1):
    return alpha * np.exp(-(d ** 2) / (2 * sigma ** 2))


def update_values_map(angle):
    global values_map
    calculate_range = 5
    # 获取 anlge 附近的点的坐标范围
    x_min = max(int(angle[0] - calculate_range), 0)
    x_max = min(int(angle[0] + calculate_range), values_map.shape[0])
    y_min = max(int(angle[1] - calculate_range), 0)
    y_max = min(int(angle[1] + calculate_range), values_map.shape[1])
    z_min = max(int(angle[2] - calculate_range), 0)
    z_max = min(int(angle[2] + calculate_range), values_map.shape[2])

    # 只计算附近点的距离
    nearby_coords = values_map[x_min:x_max, y_min:y_max, z_min:z_max]
    x_coords, y_coords, z_coords = np.indices(nearby_coords.shape)
    x_coords += x_min
    y_coords += y_min
    z_coords += z_min
    d = np.sqrt((x_coords - angle[0]) ** 2 + (y_coords - angle[1]) ** 2 + (z_coords - angle[2]) ** 2)
    # 计算附近点的高斯值
    gaussian_values = gaussian(d)
    # 将高斯值加到 color 数组上
    values_map[x_min:x_max, y_min:y_max, z_min:z_max] += gaussian_values


# 定义评价函数
def fitness(data):
    global values_map
    # 如果峰峰值大于2V，表明该状态大概率并非锁模，将其设置为0.1
    if data[3] > 2:
        data[3] = 0.1
    vm = values_map[round(data[0]), round(data[1]), round(data[2])]
    # 计算适应度 = values_map + vpp + 频率相关参数
    result = vm + data[3] + 1/((data[4]/f0-1)**2+1)
    return result


def judge_ML(threshold=0.5):
    # 根据示波器的vpp和频率判断是否锁模
    if threshold < DS4054.get_vpp() < 3 and (f0-5e6) < DS4054.get_frequency() < 10*f0:
        return True
    else:
        return False


# 判断是否达到目标
def judge_achieving_goal(v):
    if v > 5:
        return -v
    else:
        return v


def update_data(repeat=5):
    now_angle = MPC.get_angle()
    v = 0
    # 锁模判断
    if judge_ML():
        # 反复确认锁模
        for i in range(repeat):
            if judge_ML():
                if i == repeat-1:
                    print("*****锁模！保存数据*****")
                    now_data = now_angle + [DS4054.get_vpp()] + [DS4054.get_frequency()]
                    # 计算适应度
                    v = fitness(now_data)
                    now_data = now_data + [v]
                    # 更新背景图
                    update_values_map(now_angle)
                    # 保存波形信息
                    # tools.save_csv(MLpoints_csv_path, now_data)
                    # tools.save_csv(MLpoints_csv_path, DS4054.get_waveform())

                    # 锁模用星号表示
                    # ax.scatter(now_angle[0], now_angle[1], now_angle[2], s=50, c=[v], marker='*',
                    #            alpha=0.5, cmap='inferno', vmin=0, vmax=5)
                    # plt.draw()  # 更新图形
                    # plt.pause(0.001)

                    # 判断是否达到目标，如果是返回负值
                    v = judge_achieving_goal(v)
                    print(now_data)
                else:
                    time.sleep(0.1)
            else:
                break
    # 未锁模
    else:
        now_data = now_angle + [DS4054.get_vpp()] + [DS4054.get_frequency()]
        v = fitness(now_data)
        print(now_data)
        # now_data[3] = DS4054.get_vpp()
        # now_data[4] = DS4054.get_frequency()
        # v = fitness(now_data)
        # 未锁模用小点标出轨迹
        # ax.scatter(now_angle[0], now_angle[1], now_angle[2], s=10, c=[v], marker='.',
        #            alpha=0.3, cmap='inferno', vmin=0, vmax=5)
        # plt.draw()  # 更新图形
        # plt.pause(0.001)
    # 保存轨迹信息
    # now_data = now_data + [v]
    # tools.save_csv(trajectory_csv_path, now_data)
    return v


# EPC调整过程
def jog_to(target_angle):
    v = 0
    # 依次转动3个paddles
    for i in range(3):
        # 如果角度大于当前角度，正向运动，否则反向运动
        if target_angle[i] > MPC.get_angle()[i]:
            while abs(target_angle[i]-MPC.get_angle()[i]) > 1:
                MPC.move_jog(i+1, 1)
                v = update_data()
                if v < 0:
                    return v
        else:
            while abs(target_angle[i]-MPC.get_angle()[i]) > 1:
                MPC.move_jog(i+1, 2)
                v = update_data()
                if v < 0:
                    return v
    # ax.scatter(target_angle[0], target_angle[1], target_angle[2], s=20, c=[v], marker='x',
    #            alpha=0.5, cmap='inferno', vmin=0, vmax=5)
    # plt.draw()  # 更新图形
    # plt.pause(0.001)
    # 更新种群个体适应度
    return v


def genetic_algorithm():
    # 初始化种群，输入参数为种群大小
    POPULATION_SIZE = 20
    population = GA.generate_population(POPULATION_SIZE)
    print("-------------------------------------------开始迭代----------------------------------------------\n"
          "-------------------------------------------------------------------------------------------------")
    # 迭代演化开始
    for generation in range(50):
        # 保存种群信息
        # tools.save_csv(generation_csv_path, population)
        # 获取种群适应度
        for i in range(POPULATION_SIZE):
            # 控制EPC运动到种群个体位置，返回适应度
            population[i][3] = jog_to(population[i][:3])
            if population[i][3] < 0:
                print(f"已完成锁模！\n稳定锁模位置为：{population[i]}")
                tools.save_csv(timing_path, population[i])
                return
            print(f"Generation {generation}: genome{i}  is {population[i]}")
        # 产生新一代种群
        population = GA.generate_new_population(population)
        print(f"累计耗时：{time.time() - start_time}")


timing_path= tools.init_path_GA_saving_time()
# 初始化连接设备
MPC = EPC.MPC320()
DS4054 = Osc.DS4054()
# 激光器参数
f0 = 15e6
test_times = 50
ML_num = 0
total_time = 0

for i in range(test_times):
    time.sleep(1)
    # 初始化EPC
    for j in range(3):
        angle = random.randint(0, 160)
        time.sleep(0.5)
        MPC.move_to(j+1, angle)

    # 数据存储路径
    # trajectory_csv_path, MLpoints_csv_path, generation_csv_path = tools.init_path_GA()
    # 定义评价函数背景图, 精度1
    values_map = np.zeros((161, 161, 161))

    start_time = time.time()
    genetic_algorithm()
    end_time = time.time()
    ML_time = end_time - start_time
    total_time += ML_time
    print("------------------------------------------迭代结束----------------------------------------------\n"
          "------------------------------------------------------------------------------------------------")
    print(f"第{i+1}次遍历，总耗时：{end_time - start_time}")
    # 验证锁模
    time.sleep(5)
    waveform = DS4054.get_waveform()
    pulse_number, pulse_peaks, pulse_positions = dp.pulse_feature(waveform)
    ML = 0
    if judge_ML() and pulse_number > 15:
        ML_num += 1
        ML = 1
        print("稳定锁模！")
    else:
        print("失锁！")
    # 保存数据
    tools.save_csv(timing_path, [i + 1] + [ML_time] + [ML] + [pulse_number])
    tools.save_csv(timing_path, waveform)

success_rate = ML_num/test_times
average_time = total_time/test_times
tools.save_csv(timing_path, [success_rate] + [average_time])
print(f'锁模成功率为：{success_rate}')
print(f'平均锁模时间为：{average_time}')

# plt.ioff()
# plt.show(block=True)
