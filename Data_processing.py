import numpy as np
# import Drawing


def waveform_reading(file_path_of_waveform):
    # 读取数据文件
    with open(file_path_of_waveform, "r") as file:
        content = file.read()
    data = content.split("\n")  # 将一个字符串按行分成多个字符串，保存为一个列表
    # 将字符串列表数据转换成整形数组
    i = 0
    array = np.empty((int((len(data) - 1) / 2), 1400), dtype=int)   # 因为data最后一行数据是空，所以减一
    while i < (len(data) - 1) / 2:
        array[i] = np.genfromtxt(data[2 * i].splitlines(), dtype=int)
        i += 1
    return array


def spectrum_reading(file_path_of_spectrum):
    with open(file_path_of_spectrum, 'r') as file:
        content = file.read()
    data = content.split("\n")
    i = 0
    spectrum_amplitude = np.empty((int((len(data) - 1) / 2), 2101), float)
    spectrum_wavelength = np.empty((int((len(data) - 1) / 2), 2101), float)
    while i < (len(data) - 1) / 2:
        spectrum_wavelength[i] = np.genfromtxt(data[2 * i].splitlines(), float)
        spectrum_amplitude[i] = np.genfromtxt(data[2 * i + 1].splitlines(), float)
        i += 1
    return spectrum_wavelength, spectrum_amplitude


def pulse_feature(waveform, threshold=60):
    """
    :param waveform: the input waveform, type=array
    :param threshold: Criteria for pulse discrimination, type=float
    :return:pules_number: the number of pulses, type=int
            pules_peak: the value of pulse peak, type=array
            peak_position: the position of pulse peak, type=array
    """
    pulses_number = 0
    previous_state = 'low'
    pulse_peak = []
    peak_position = []
    for i in range(1, len(waveform)):
        # Check for rising edge (low to high)
        if waveform[i - 1] < threshold <= waveform[i] and previous_state == 'low':
            pulses_number += 1
            previous_state = 'high'
            pulse_peak.append(waveform[i])
            peak_position.append(i)
        # Find peak value and corresponding position
        elif previous_state == 'high' and waveform[i] > pulse_peak[pulses_number - 1]:
            pulse_peak[pulses_number - 1] = waveform[i]
            peak_position[pulses_number - 1] = i
        # Check for falling edge (high to low)
        elif waveform[i - 1] >= threshold > waveform[i]:
            previous_state = 'low'
    return pulses_number, pulse_peak, peak_position


def nice_mode_locking_waveform(waveform):
    n, pk, ps = pulse_feature(waveform)
    # 返回脉冲数和峰峰值方差
    return np.array([n, np.var(pk)])


def spectrum_feature(spectrum_wavelength, spectrum_amplitude):
    peak_number = 0
    previous_state = 'low'
    peak = []
    peak_position = []
    threshold = -40
    threshold10dB = max(spectrum_amplitude) - 10
    start = 0
    end = len(spectrum_amplitude) - 1
    max_index = np.argmax(spectrum_amplitude)
    center = spectrum_wavelength[max_index]
    spectrum_diff = np.diff(spectrum_amplitude)
    for i in range(1, len(spectrum_amplitude)):
        # Check for rising edge (low to high)
        if (spectrum_amplitude[i] >= threshold10dB > spectrum_amplitude[i-1]
                and previous_state == 'low'):
            peak_number += 1
            previous_state = 'high'
            peak.append(spectrum_amplitude[i])
            peak_position.append(spectrum_wavelength[i])
        # Find peak value and corresponding position
        elif previous_state == 'high' and spectrum_amplitude[i] > peak[peak_number - 1]:
            peak[peak_number - 1] = spectrum_amplitude[i]
            peak_position[peak_number - 1] = spectrum_wavelength[i]
        # Check for falling edge (high to low)
        elif spectrum_amplitude[i] <= (threshold10dB-4) < spectrum_amplitude[i - 1]:
            previous_state = 'low'
        # find 10 dB bandwidth
        if i < max_index:
            if spectrum_amplitude[i] <= threshold10dB or abs(spectrum_diff[i]) > 10:
                start = i
        elif i > max_index:
            if spectrum_amplitude[i] >= threshold10dB and abs(spectrum_diff[i]) < 15:
                end = i
    ten_db_bandwidth = end - start
    # 返回中心波长，10dB带宽，峰数，峰值，峰值对应的波长
    return center, ten_db_bandwidth, peak_number, peak, peak_position


def nice_mode_locking_spectrum(x, y):
    c, t, n, pk, ps = spectrum_feature(x, y)
    max_len = max(3, len(ps))
    td_array = np.zeros((3, max_len))
    td_array[0, :3] = [c, t, n]
    td_array[1, :len(ps)] = pk
    td_array[2, :len(ps)] = ps
    return td_array


"""
# 求数组均值
def mean(nparray):
    return np.mean(nparray)


# 求数组方差
def variance(nparray):
    return np.var(nparray)


# 数组差分
def difference(nparray):
    return np.diff(nparray)
"""





