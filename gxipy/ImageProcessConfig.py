#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.ImageProc import *
import threading
import types

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class ImageProcessConfig:
    def __init__(self, color_correction_param):
        self.valid_bits = DxValidBit.BIT0_7
        self.b_defective_pixel_correct = False
        self.b_denoise = False
        self.b_sharpness = False
        self.b_flip = False
        self.b_color_correction = False
        self.b_accelerate = False
        self.b_user_set_mode = False
        self.sharp_factor = 0.1
        self.convert_type = DxBayerConvertType.NEIGHBOUR
        self.contrast_factor = 0
        self.gamma_factor = 1.0
        self.lightness_factor = 0
        self.saturation_factor = 64
        self.color_correction_param = color_correction_param
        self.color_transform_factor = ColorTransformFactor()
        self.color_transform_factor.fGain00 = 1
        self.color_transform_factor.fGain01 = 0
        self.color_transform_factor.fGain02 = 0
        self.color_transform_factor.fGain10 = 0
        self.color_transform_factor.fGain11 = 1
        self.color_transform_factor.fGain12 = 0
        self.color_transform_factor.fGain20 = 0
        self.color_transform_factor.fGain21 = 0
        self.color_transform_factor.fGain22 = 1

        self.cc_param_buffer = None
        self.lut = None
        self.lut_length = 0
        self.gamma_lut = None
        self.gamma_lut_length = 0
        self.contrast_lut = None
        self.contrast_lut_length = 0
        self.mutex = threading.Lock()

        self.__sharp_factor_min = 0.1
        self.__sharp_factor_max = 5.0
        self.__contrast_factor_min = -50
        self.__contrast_factor_max = 100
        self.__gamma_factor_min = 0.1
        self.__gamma_factor_max = 10.0
        self.__lightness_factor_min = -150
        self.__lightness_factor_max = 150
        self.__saturation_factor_min = 0
        self.__saturation_factor_max = 128

        self.set_gamma_param(self.gamma_factor)
        self.set_contrast_param(self.contrast_factor)
        self.set_lightness_param(self.lightness_factor)
        self.set_saturation_param(self.saturation_factor)


    def set_valid_bits(self, valid_bits):
        """
        :brief    Select Get the specified 8-bit valid data bits. This interface is set up for non-8-bit raw data
        :param:   valid_bits: Valid data bits 0 to 7,  refer to DxValidBit
        """
        if not isinstance(valid_bits, INT_TYPE):
            raise ParameterTypeError("valid_bits param must be int in DxValidBit.")

        self.valid_bits = valid_bits

    def get_valid_bits(self):
        """
        :brief     Get the specified 8-bit valid data bits. This interface is set up for non-8-bit raw data
        :return    Valid data bits 0 to 7,  refer to DxValidBit
        """
        return self.valid_bits

    def enable_defective_pixel_correct(self, enable):
        """
        :brief     enable defective pixel correct
        :param:    enable: True enable defective pixel correct, False disable defective pixel correct
        """
        if not isinstance(enable, bool):
            raise ParameterTypeError("enable param must is bool type.")

        self.b_defective_pixel_correct = enable

    def is_defective_pixel_correct(self):
        """
        :brief     get defective pixel correct status
        :return    True enable defective pixel correct, False disable defective pixel correct
        """
        return self.b_defective_pixel_correct

    def enable_sharpen(self, enable):
        """
        :brief     enable sharpen
        :param:    enable: True enable sharpen, False disable sharpen
        """
        if not isinstance(enable, bool):
            raise ParameterTypeError("enable param must is bool type.")

        self.b_sharpness = enable

    def is_sharpen(self):
        """
        :brief     get sharpen status
        :return    True enable sharpen, False disable sharpen
        """
        return self.b_sharpness

    def set_sharpen_param(self, param):
        """
        :brief     set sharpen param factor
        :param:    param: sharpen param factor (0.1 ~5.0)
        """
        if not isinstance(param, (INT_TYPE, float)):
            raise ParameterTypeError("param must to be int or float type.")

        if (param >= self.__sharp_factor_min and param <= self.__sharp_factor_max):
            self.sharp_factor = param
        else:
            raise UnexpectedError("SharpFactor Range is {%f}~{%f}" %(self.__sharp_factor_min, self.__sharp_factor_max))

    def get_sharpen_param(self):
        """
        :brief    get sharpen param factor
        :return   sharpen param factor (0.1 ~5.0)
        """
        return self.sharp_factor

    def set_contrast_param(self, param):
        """
        :brief    set contrast param factor
        :param:   param: contrast param factor (-50, 100)
        """

        if not (isinstance(param, INT_TYPE)):
            raise ParameterTypeError("param must to be INT type.")

        if (param >= self.__contrast_factor_min and param <= self.__contrast_factor_max):
            self.contrast_factor = param
        else:
            raise UnexpectedError("ContrastFactor Range is {%d}~{%d}" %(self.__contrast_factor_min ,self.__contrast_factor_max))

        self.__calc_lut()
        self.__calc_contrast_lut()

    def get_contrast_param(self):
        """
        :brief     get contrast param
        :return    contrast param factor (-50, 100)
        """
        return self.contrast_factor

    def set_gamma_param(self, param):
        """
        :brief    set gamma param factor
        :param:   param: gamma param factor (0.1, 10.0)
        """
        if not (isinstance(param, (INT_TYPE, float))):
            raise ParameterTypeError("param must to be INT or FLOAT type.")

        if (param >= self.__gamma_factor_min and param <= self.__gamma_factor_max):
            self.gamma_factor = param
        else:
            raise UnexpectedError("GammaFactor Range is {%f}~{%f}" %(self.__gamma_factor_min, self.__gamma_factor_max))

        self.__calc_lut()
        self.__calc_gamma_lut()

    def get_gamma_param(self):
        """
        :brief     get contrast param factor
        :return    contrast param factor (0.1, 10.0)
        """
        return self.gamma_factor

    def set_lightness_param(self, param):
        """
        :brief    set lightness param factor
        :param:   param: lightness param factor (-150, 150)
        """
        if not (isinstance(param, INT_TYPE)):
            raise ParameterTypeError("param must to be INT type.")

        if (param >= self.__lightness_factor_min and param <= self.__lightness_factor_max):
            self.lightness_factor = param
        else:
            raise UnexpectedError("LightnessFactor Range is {%d}~{%d}" %(self.__lightness_factor_min, self.__lightness_factor_max))

        self.__calc_lut()

    def get_lightness_param(self):
        """
        :brief     get lightness param factor
        :return    lightness param factor (-150, 150)
        """
        return self.lightness_factor

    def enable_denoise(self, enable):
        """
        :brief    enable denoise 【not support mono camera】
        :param:   enable：True enable denoise, False disable enable denoise
        """
        if not (isinstance(enable, bool)):
            raise ParameterTypeError("param must to be bool type.")

        self.b_denoise = enable

    def is_denoise(self):
        """
        :brief     get denoise status 【not support mono camera】
        :return    True enable denoise, False disable enable denoise
        """
        return self.b_denoise

    def set_saturation_param(self, param):
        """
        :brief    set saturation param 【not support mono camera】
        :param:   param: saturation param (0, 128)
        """
        if not (isinstance(param, INT_TYPE)):
            raise ParameterTypeError("param must to be int type.")

        if (param >= self.__saturation_factor_min and param <= self.__saturation_factor_max):
            self.saturation_factor = param
        else:
            raise UnexpectedError("LightnessFactor Range is {%d}~{%d}" %(self.__saturation_factor_min, self.__saturation_factor_max))

        if self.is_user_set_ccparam():
            self.__calc_user_set_cc_param()
        else:
            self.__calc_cc_param()

    def get_saturation_param(self):
        """
        :brief     get saturation param  【not support mono camera】
        :return    saturation param (0, 128)
        """

        return self.saturation_factor

    def set_convert_type(self, cv_type):
        """
        :brief    set convert type 【not support mono camera】
        :param:   param: convert type, refer to DxBayerConvertType
        """
        if not isinstance(cv_type, INT_TYPE):
            raise ParameterTypeError("cc_type param must be int in DxRGBChannelOrder.")

        self.convert_type = cv_type

    def get_convert_type(self):
        """
        :brief     get sconvert type 【not support mono camera】
        :return    convert type, refer to DxBayerConvertType
        """

        return self.convert_type

    def enable_convert_flip(self, flip):
        """
        :brief    enable convert flip 【not support mono camera】
        :param:   flip：True enable convert flip, False disable convert flip
        """
        if not isinstance(flip, bool):
            raise ParameterTypeError("flip param must be bool type.")

        self.b_flip = flip

    def is_convert_flip(self):
        """
        :brief    get convert flip status 【not support mono camera】
        :return   True enable convert flip, False disable convert flip
        """

        return self.b_flip

    def enable_accelerate(self, accelerate):
        """
        :brief    If the current CPU supports acceleration, setting acceleration throws an illegal call exception
        :param:   accelerate: True accelerate, False, not accelerate
        """
        if not isinstance(accelerate, bool):
            raise ParameterTypeError("accelerate param must be bool type.")

        self.b_accelerate = accelerate

    def is_accelerate(self):
        """
        :brief     get accelerate status
        :return
        """
        return self.b_accelerate

    def enable_color_correction(self, enable):
        """
        :brief    enable color correction 【not support mono camera】
        :param:   enable:True enable color correction, False disable color correction
        """
        if not isinstance(enable, bool):
            raise ParameterTypeError("enable param must be bool type.")

        self.b_color_correction = enable

        if self.is_user_set_ccparam():
            self.__calc_user_set_cc_param()
        else:
            self.__calc_cc_param()

    def is_color_correction(self):
        """
        :brief     get accelerate status 【not support mono camera】
        :return    True enable color correction, False disable color correction
        """

        return self.b_color_correction

    def enable_user_set_ccparam(self, enable):
        """
        :brief    enable user mode 【not support mono camera】
        :param:   enable: True user mode
        """
        if not isinstance(enable, bool):
            raise ParameterTypeError("enable param must be bool type.")

        self.b_user_set_mode = enable

    def is_user_set_ccparam(self):
        """
        :brief     get user mode status
        :return
        """
        return self.b_user_set_mode

    def set_user_ccparam(self, color_transform_factor):
        """
        :brief    set user ccparam 【not support mono camera】
        :param:   color_transform_factor: color correction parameter, refer to ColorTransformFactor
        """

        if not isinstance(color_transform_factor, ColorTransformFactor):
            raise ParameterTypeError("color_transform_factor param must be ColorTransformFactor type.")

        self.color_transform_factor = color_transform_factor

    def get_user_ccparam(self):
        """
        :brief    get user ccparam 【not support mono camera】
        :return
        """
        return self.color_transform_factor

    def get_color_correction_param(self):
        """
        :brief    get color correction param
        :return
        """
        if self.b_color_correction is True:
            return self.color_correction_param
        else:
            return 0

    def get_gamma_lut(self):
        """
        :brief   Calculating gamma lookup table (RGB24)
        :param   self.gamma_factor:  gamma param,range(0.1 ~ 10)
        :return: gamma_lut buffer
        """
        if self.gamma_lut is None:
            raise UnexpectedError("Gamma Lut is empty. You should first call set_gamma_param to calculate it.")
        return Buffer(self.gamma_lut)

    def get_contrast_lut(self):
        """
        :brief   Calculating contrast lookup table (RGB24)
        :param   self.contrast_factor:   contrast param,range(-50 ~ 100)
        :return: contrast_lut buffer
        """
        if self.contrast_lut is None:
            raise UnexpectedError("contrast lut Lut is empty. You should first call set_contrast_param to calculate it.")
        return Buffer(self.contrast_lut)

    def get_color_image_process(self, color_filter_layout):
        color_img_process_param = DxColorImgProcess()

        color_img_process_param.accelerate = self.is_accelerate()
        color_img_process_param.defective_pixel_correct = self.is_defective_pixel_correct()
        color_img_process_param.denoise = self.is_denoise()
        color_img_process_param.flip = self.is_convert_flip()
        color_img_process_param.sharpness = self.is_sharpen()
        color_img_process_param.convert_type = self.get_convert_type()
        color_img_process_param.color_filter_layout = color_filter_layout
        color_img_process_param.sharp_factor = self.get_sharpen_param()
        color_img_process_param.pro_lut, color_img_process_param.pro_lut_length = self.__get_lut()
        color_img_process_param.cc_param_length = 18
        color_img_process_param.cc_param = self.__get_calc_color_correction_param()

        return color_img_process_param

    def get_mono_image_process(self):
        mono_img_process_param = DxMonoImgProcess()
        mono_img_process_param.accelerate = self.is_accelerate()
        mono_img_process_param.defective_pixel_correct = self.is_defective_pixel_correct()
        mono_img_process_param.sharpness = self.is_sharpen()
        mono_img_process_param.sharp_factor = self.get_sharpen_param()
        mono_img_process_param.pro_lut, mono_img_process_param.pro_lut_length = self.__get_lut()
        return mono_img_process_param

    def get_mutex(self):
        return self.mutex

    def reset(self):
        """
        :brief  reset config
        :return NONE
        """
        self.valid_bits = DxValidBit.BIT0_7
        self.b_defective_pixel_correct = False
        self.b_denoise = False
        self.b_sharpness = False
        self.b_flip = False
        self.b_color_correction = True
        self.b_user_set_mode = False
        self.sharp_factor = 0.1
        self.convert_type = DxBayerConvertType.NEIGHBOUR
        self.contrast_factor = 0
        self.gamma_factor = 1.0
        self.lightness_factor = 0
        self.saturation_factor = 64
        self.color_transform_factor = ColorTransformFactor()
        self.color_transform_factor.fGain00 = 1
        self.color_transform_factor.fGain01 = 0
        self.color_transform_factor.fGain02 = 0
        self.color_transform_factor.fGain10 = 0
        self.color_transform_factor.fGain11 = 1
        self.color_transform_factor.fGain12 = 0
        self.color_transform_factor.fGain20 = 0
        self.color_transform_factor.fGain21 = 0
        self.color_transform_factor.fGain22 = 1



    def __get_calc_color_correction_param(self):
        """
        :brief      calculating array of image processing color adjustment
        :return:    cc param buffer
        """
        return Buffer(self.cc_param_buffer)

    def __calc_cc_param(self):
        """
        :brief      calculating array of image processing color adjustment
        :param      self.color_correction_param: color correction param address(get from camera)
        :param      self.saturation_factor:             saturation factor,Range(0~128)
        :return:    void
        """
        with self.mutex:
            status, cc_param = dx_calc_cc_param(self.get_color_correction_param(), self.saturation_factor)
            if status != DxStatus.OK:
                print("Utility.calc_cc_param: calc correction param failure, Error code:%s" % hex(status).__str__())
                return None

            self.cc_param_buffer = cc_param

    def __calc_user_set_cc_param(self):
        """
        :brief      calculating array of image processing color adjustment
        :param      self.color_transform_factor: color correction param address(user set),
                                            type should be list or tuple, size = 3*3=9
        :param      self.saturation_factor:             saturation factor,Range(0~128)
        :return:    void
        """
        with self.mutex:
            status, cc_param = dx_calc_user_set_cc_param(self.color_transform_factor, self.saturation_factor)
            if status != DxStatus.OK:
                print("Utility.calc_user_set_cc_param: calc correction param failure, "
                      "Error code:%s" % hex(status).__str__())
                return None

            self.cc_param_buffer = cc_param

    def __get_lut(self):
        """
        :brief      Calculating lookup table of 8bit image
        :return:    lut buffer, lut length
        """

        return Buffer(self.lut), self.lut_length

    def __calc_lut(self):
        """
        :brief  calculate the Lut value
        :return NONE
        """
        with self.mutex:
            status, self.lut, self.lut_length = dx_get_lut(self.contrast_factor, self.gamma_factor, self.lightness_factor)
            if status != DxStatus.OK:
                raise UnexpectedError("dx_get_lut failure, Error code:%s" % hex(status).__str__())

    def __calc_gamma_lut(self):
        """
        :brief  calculate the gamma lut value
        :return NONE
        """
        with self.mutex:
            status, self.gamma_lut, self.gamma_lut_length = dx_get_gamma_lut(self.gamma_factor)
            if status != DxStatus.OK:
                raise UnexpectedError("dx_get_gamma_lut failure, Error code:%s" % hex(status).__str__())

    def __calc_contrast_lut(self):
        """
        :brief  calculate the contrast lut value
        :return NONE
        """
        with self.mutex:
            status, self.contrast_lut, self.contrast_lut_length = dx_get_contrast_lut(self.contrast_factor)
            if status != DxStatus.OK:
                raise UnexpectedError("__calc_contrast_lut failure, Error code:%s" % hex(status).__str__())



