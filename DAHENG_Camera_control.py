import sys
import gxipy as gx
from PIL import Image
from datetime import datetime


class DAHENGCamera:
    def __init__(self):
        self.device_manager = gx.DeviceManager()
        dev_num, dev_info_list = self.device_manager.update_device_list()
        if dev_num == 0:
            print("Number of enumerated devices is 0")
            sys.exit(1)
        # Open the first device
        self.cam = self.device_manager.open_device_by_index(1)
        self.setting()
        print("Camera initialized")

    # 曝光单位：微秒us
    def setting(self, exposure_time=2000.0):
        remote_device_feature = self.cam.get_remote_device_feature_control()
        exposure_time_feature = remote_device_feature.get_float_feature("ExposureTime")
        exposure_time_feature.set(exposure_time)

    def save_image(self, image_path, image_name):
        self.cam.stream_on()    # 开始采集数据
        raw_image = self.cam.data_stream[0].get_image()
        numpy_image = raw_image.get_numpy_array()

        image = Image.fromarray(numpy_image, 'L')  # 数组转化为图像
        image_name = image_name + '.jpg'
        image.save(image_path + '/' + image_name)  # 根据路径保存数据
        self.cam.stream_off()   # 停止采集数据
