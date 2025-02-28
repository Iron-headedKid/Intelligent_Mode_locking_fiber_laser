#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy

import gxipy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.ImageFormatConvert import *
from gxipy.ImageProcessConfig import *
from gxipy.Exception import *
import types

class ImageProcess:

    def __init__(self):
        self.image_convert_handle = None

    def __new__(cls, *args, **kw):
        return object.__new__(cls, *args)

    def __del__(self):
        if self.image_convert_handle is not None:
            status = dx_image_format_convert_destroy(self.image_convert_handle)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_image_format_convert_destroy failure, Error code:%s" % hex(status).__str__())
            self.image_convert_handle = None

    def image_improvement(self, image, output_address, image_process_config):
        """
        :brief:     Improve image quality of the raw_image
        :param      image: image is RawImage or GXImageInfo

        :param      output_address: output image
        :param      image_process_config: image process config
        :param
        :return:    None
        """
        if output_address is None:
            raise ParameterTypeError("output_address param is null pointer.")

        if not isinstance(image_process_config, ImageProcessConfig):
            raise ParameterTypeError("image_process_config param must be ImageProcessConfig type.")

        pixel_format = GxPixelFormatEntry.UNDEFINED
        raw_image_width = 0
        raw_image_height = 0
        input_image_buffer = None
        channel_order = DxRGBChannelOrder.ORDER_RGB
        if isinstance(image, (RawImage, RGBImage)):
            pixel_format = image.frame_data.pixel_format
            raw_image_width = image.frame_data.width
            raw_image_height = image.frame_data.height
            input_image_buffer = image.frame_data.image_buf
        elif isinstance(image, GxImageInfo):
            pixel_format = image.image_pixel_format
            raw_image_width = image.image_width
            raw_image_height = image.image_height
            input_image_buffer = image.image_buf
        else:
            raise ParameterTypeError("image param must be RawImage or GxImageInfo type.")

        if input_image_buffer is None:
            raise ParameterTypeError("input_image_buffer param is null pointer.")

        if pixel_format == GxPixelFormatEntry.RGB8:
            channel_order = DxRGBChannelOrder.ORDER_RGB
        elif pixel_format == GxPixelFormatEntry.BGR8:
            channel_order = DxRGBChannelOrder.ORDER_BGR

        if pixel_format in (GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8):
            if pixel_format == GxPixelFormatEntry.BGR8:

                self.__check_handle()
                status = dx_image_format_convert_set_output_pixel_format(self.image_convert_handle,
                                                                         GxPixelFormatEntry.RGB8)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_set_output_pixel_format failure, Error code:%s" % hex(
                            status).__str__())

                status = dx_image_format_convert_set_valid_bits(self.image_convert_handle, DxValidBit.BIT0_7)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "image_format_convert_set_alpha_value failure, Error code:%s" % hex(status).__str__())

                status, out_lenght = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle,
                                                                                            GxPixelFormatEntry.RGB8,
                                                                                            image.frame_data.width,
                                                                                            image.frame_data.height)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(
                            status).__str__())

                image_temp = (c_ubyte * out_lenght)()
                output_image_temp = addressof(image_temp)

                status, input_length = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle,
                                                                                              image.frame_data.pixel_format,
                                                                                              image.frame_data.width,
                                                                                              image.frame_data.height)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(
                            status).__str__())

                status = dx_image_format_convert(self.image_convert_handle, image.frame_data.image_buf, input_length,
                                                 output_image_temp,
                                                 out_lenght, image.frame_data.pixel_format,
                                                 image.frame_data.width, image.frame_data.height, False)

                if status != DxStatus.OK:
                    raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())

                input_image_buffer = output_image_temp
            status = dx_image_improvement_ex(input_image_buffer, output_address,
                                             raw_image_width, raw_image_height,
                                             image_process_config.get_color_correction_param(),
                                             image_process_config.get_contrast_lut().get_ctype_array(),
                                             image_process_config.get_gamma_lut().get_ctype_array(),
                                             channel_order)
            if status != DxStatus.OK:
                raise UnexpectedError("RGBImage.image_improvement: failed, error code:%s" % hex(status).__str__())
            return

        if Utility.is_gray(pixel_format):
            ImageProcess.__mono_image_process(self, output_address, image, image_process_config)
        else:
            rgb_image_array_temp = (c_ubyte * image.frame_data.height * image.frame_data.width * 3)()
            rgb_image_array_temp_address = addressof(rgb_image_array_temp)
            ImageProcess.__raw_image_process(rgb_image_array_temp_address, image, image_process_config)

            # convert to rgb
            self.__check_handle()
            status = dx_image_format_convert_set_output_pixel_format(self.image_convert_handle,
                                                                     GxPixelFormatEntry.RGB8)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_image_format_convert_set_output_pixel_format failure, Error code:%s" % hex(
                        status).__str__())
            status = dx_image_format_convert_set_valid_bits(self.image_convert_handle, DxValidBit.BIT0_7)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "image_format_convert_set_alpha_value failure, Error code:%s" % hex(status).__str__())

            status, out_lenght = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle,
                                                                                        GxPixelFormatEntry.BGR8,
                                                                                        image.frame_data.width,
                                                                                        image.frame_data.height)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(
                        status).__str__())

            input_length = image.frame_data.width * image.frame_data.height * 3
            status = dx_image_format_convert(self.image_convert_handle, rgb_image_array_temp_address, input_length,
                                             output_address,
                                             out_lenght, GxPixelFormatEntry.BGR8,
                                             image.frame_data.width, image.frame_data.height, False)
            if status != DxStatus.OK:
                raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())


    def static_defect_correction(self, input_address, output_address, defect_correction, defect_pos_buffer_address,
                                    defect_pos_buffer_size):
        """
        :brief Image defect pixel correction
        :param input_address:                      The input raw image buff address, buff size = width * height
        :param output_address:                     The output rgb image buff address, buff size = width * height * 3
        :param defect_correction:                  Image parameter used to do defect correction
        :param defect_pos_buffer_address:          Defect Pixel position file buffer
        :param  defect_pos_buffer_size:            Defect Pixel position file buffer size

        :return: status                            State return value, See detail in DxStatus
                 data_array                        Array of output images, buff size = width * height * 3
        """
        if input_address is None:
            raise ParameterTypeError("input_address param is null pointer.")

        if output_address is None:
            raise ParameterTypeError("output_address param is null pointer.")

        if not isinstance(defect_correction, StaticDefectCorrection):
            raise ParameterTypeError("StaticDefectCorrection param must be StaticDefectCorrection type.")

        if defect_pos_buffer_address is None:
            raise ParameterTypeError("defect_pos_buffer_address param is null pointer.")

        if not isinstance(defect_pos_buffer_size, INT_TYPE):
            raise ParameterTypeError("defect_pos_buffer_size param must be Int type.")

        status = dx_static_defect_correction(input_address, output_address, defect_correction, defect_pos_buffer_address,
                                           defect_pos_buffer_size)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_static_defect_correction failure, Error code:%s" % hex(status).__str__())


    @staticmethod
    def calcula_lut(contrast_param, gamma, light_ness, lut_address,
                                  lut_length_address):
        """
        :brief calculating lookup table of camera
        :param contrast_param:                      contrast param,range(-50~100)
        :param gamma:                               gamma param,range(0.1~10)
        :param light_ness:                          lightness param,range(-150~150)
        :param lut_address:                         lookup table
        :param  lut_length_address:                 lookup table length(unit:byte)

        Lookup table length should be obtained through the interface GXGetBufferLength.
        :return: status                            State return value, See detail in DxStatus
                 data_array                        Array of output images, buff size = width * height * 3
        """
        if not (isinstance(contrast_param, INT_TYPE)):
            raise ParameterTypeError("contrast_param param must to be int type.")

        if not (isinstance(gamma, (INT_TYPE, float))):
            raise ParameterTypeError("gamma param must to be int or float type.")

        if not (isinstance(light_ness, INT_TYPE)):
            raise ParameterTypeError("light_ness param must to be int type.")

        if lut_address is None:
            raise ParameterTypeError("lut_address is NULL pointer")

        if lut_length_address is None:
            raise ParameterTypeError("lut_length_address is NULL pointer")

        status = dx_calc_camera_lut_buffer(contrast_param, gamma, light_ness, lut_address,
                                  lut_length_address)
        if status != DxStatus.OK:
            raise UnexpectedError("calc_camera_lut_buffer failure, Error code:%s" % hex(status).__str__())

    @staticmethod
    def read_lut_file(lut_file_path, lut_address, lut_length_address):
        """
        :brief read lut file
        :param lut_file_path:                        Lut file path. Lut file(xxx.lut) can be obtained from Lut
                                 Create Tool Plugin,which can be get by select Plugin->Lut
                                 Create Tool Plugin from the menu bar in GalaxyView.
        :param lut_address:                          Lookup table. Users need to apply for memory in advance.The
                                 memory size is also lookup table length(nLutLength),should be
                                 obtained through the interface GXGetBufferLength,
                                 e.g. GXGetBufferLength(m_hDevice, GX_BUFFER_LUT_VALUEALL,&nLutLength),
        :param lut_length_address:                   Lookup table length(unit:byte),which should be obtained through
                                 the interface GXGetBufferLength, e.g.
                                 GXGetBufferLength(m_hDevice, GX_BUFFER_LUT_VALUEALL,&nLutLength),
        :return: status                            State return value, See detail in DxStatus
                 data_array                        Array of output images, buff size = width * height * 3
        """

        if os.path.exists(lut_file_path) is False:
            raise ParameterTypeError("%s file is not exits" % lut_file_path)

        if lut_address is None:
            raise ParameterTypeError("lut_address is NULL pointer")

        if lut_length_address is None:
            raise ParameterTypeError("lut_length_address is NULL pointer")

        path = create_string_buffer(string_encoding(lut_file_path))

        status = dx_read_lut_file(path, lut_address, lut_length_address)
        if status != DxStatus.OK:
            raise UnexpectedError("read_lut_file failure, Error code:%s" % hex(status).__str__())

    @staticmethod
    def __is_bayer(pixel_format):
        bayer_gr8_id = (GxPixelFormatEntry.BAYER_GR8 & PIXEL_ID_MASK)
        bayer_bg12_id = (GxPixelFormatEntry.BAYER_BG12 & PIXEL_ID_MASK)

        bayer_gr16_id = (GxPixelFormatEntry.BAYER_GR16 & PIXEL_ID_MASK)
        bayer_bg16_id = (GxPixelFormatEntry.BAYER_BG16 & PIXEL_ID_MASK)
        if ((pixel_format & PIXEL_ID_MASK) >= bayer_gr8_id) and ((pixel_format & PIXEL_ID_MASK) <= bayer_bg12_id):
            return True
        elif ((pixel_format & PIXEL_ID_MASK) >= bayer_gr16_id) and ((pixel_format & PIXEL_ID_MASK) <= bayer_bg16_id):
            return True

        return False

    @staticmethod
    def __is_gray(pixel_format):
        if (pixel_format & PIXEL_COLOR_MASK) != PIXEL_MONO:
            return False
        elif (ImageProcess.__is_bayer(pixel_format)):
            return False
        else:
            return True

    @staticmethod
    def __get_pixel_color_filter(pixel_format):
        """
        :brief      Calculate pixel color filter based on pixel format
        :param      pixel_format
        :return:    pixel color filter
        """
        gr_tup = (GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_GR10,
                  GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_GR16)
        rg_tup = (GxPixelFormatEntry.BAYER_RG8, GxPixelFormatEntry.BAYER_RG10,
                  GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_RG16)
        gb_tup = (GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_GB10,
                  GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_GB16)
        bg_tup = (GxPixelFormatEntry.BAYER_BG8, GxPixelFormatEntry.BAYER_BG10,
                  GxPixelFormatEntry.BAYER_BG12, GxPixelFormatEntry.BAYER_BG16)
        mono_tup = (GxPixelFormatEntry.MONO8, GxPixelFormatEntry.MONO8_SIGNED,
                    GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO12,
                    GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO16,
                    GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO12_PACKED)

        if pixel_format in gr_tup:
            return DxPixelColorFilter.GR
        elif pixel_format in rg_tup:
            return DxPixelColorFilter.RG
        elif pixel_format in gb_tup:
            return DxPixelColorFilter.GB
        elif pixel_format in bg_tup:
            return DxPixelColorFilter.BG
        elif pixel_format in mono_tup:
            return DxPixelColorFilter.NONE
        else:
            return -1

    @staticmethod
    def __raw_image_process(output_address, image, image_process_config):
        """
        :brief  Raw8 image process
        :param  color_img_process_param:  image process param, refer to DxColorImgProcess
        :return img_rgb
        """
        pixel_format = 0
        raw_image_width = 0
        raw_image_height = 0
        input_image_buffer = None
        if isinstance(image, (RawImage, RGBImage)):
            pixel_format = image.frame_data.pixel_format
            raw_image_width = image.frame_data.width
            raw_image_height = image.frame_data.height
            input_image_buffer = image.frame_data.image_buf
        elif isinstance(image, GxImageInfo):
            pixel_format = image.image_pixel_format
            raw_image_width = image.image_width
            raw_image_height = image.image_height
            input_image_buffer = image.image_buf
        else:
            raise ParameterTypeError("image param must be RawImage or GxImageInfo type")

        if input_image_buffer is None or output_address is None:
            raise ParameterTypeError("input_image_buffer or output_address is NULL pointer")

        if pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            status = dx_raw16_to_raw8(input_image_buffer, input_image_buffer,
                                      raw_image_width, raw_image_height,
                                      image_process_config.get_valid_bits())
            if status != DxStatus.OK:
                raise UnexpectedError("RawImage.convert: raw16 convert to raw8 failed, Error core: %s"
                                      % hex(status).__str__())

        color_filter = ImageProcess.__get_pixel_color_filter(pixel_format)
        mutex = image_process_config.get_mutex()
        with mutex:
            color_img_process_param = image_process_config.get_color_image_process(color_filter)
            status = dx_raw8_image_process(input_image_buffer, output_address,
                                           raw_image_width, raw_image_height, color_img_process_param)
            if status != DxStatus.OK:
                raise UnexpectedError("RawImage.raw8_image_process: failed, error code:%s" % hex(status).__str__())

    def __mono_image_process(self, output_address, image, image_process_config):
        """
        :brief  mono8 image process
        :param  mono_img_process_param:  image process param, refer to DxMonoImgProcess
        :return img_mono
        """
        pixel_format = 0
        raw_image_width = 0
        raw_image_height = 0
        input_image_buffer = None
        if isinstance(image, (RawImage, RGBImage)):
            pixel_format = image.frame_data.pixel_format
            raw_image_width = image.frame_data.width
            raw_image_height = image.frame_data.height
            input_image_buffer = image.frame_data.image_buf
        elif isinstance(image, GxImageInfo):
            pixel_format = image.image_pixel_format
            raw_image_width = image.image_width
            raw_image_height = image.image_height
            input_image_buffer = image.image_buf
        else:
            raise ParameterTypeError("image param must be RawImage or GxImageInfo type")

        if input_image_buffer is None or output_address is None:
            raise ParameterTypeError("input_image_buffer or output_address is NULL pointer")

        if ((pixel_format & PIXEL_BIT_MASK) != GX_PIXEL_8BIT):
            image_temp = None
            output_image_temp = None
            if self.__is_packed_pixel_format(pixel_format):
                self.__check_handle()
                status = dx_image_format_convert_set_output_pixel_format(self.image_convert_handle, GxPixelFormatEntry.MONO8)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_set_output_pixel_format failure, Error code:%s" % hex(
                            status).__str__())

                status, out_lenght = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle, GxPixelFormatEntry.MONO8,
                                                                                               raw_image_width, raw_image_height)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(
                            status).__str__())

                image_temp = (c_ubyte * out_lenght)()
                output_image_temp = addressof(image_temp)

                status, input_length = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle, pixel_format,
                                                                                      raw_image_width, raw_image_height)
                if status != DxStatus.OK:
                    raise UnexpectedError(
                        "dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(
                            status).__str__())

                status = dx_image_format_convert(self.image_convert_handle, input_image_buffer, input_length,
                                                 output_image_temp,
                                                 out_lenght, pixel_format,
                                                 raw_image_width, raw_image_height, False)

                if status != DxStatus.OK:
                    raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())
            else:
                image_temp = (c_ubyte * raw_image_width *raw_image_height)()
                output_image_temp = addressof(image_temp)

                status = dx_raw16_to_raw8(input_image_buffer, output_image_temp,
                                          raw_image_width, raw_image_height,
                                          image_process_config.get_valid_bits())
                if status != DxStatus.OK:
                    raise UnexpectedError("RawImage.convert: raw16 convert to raw8 failed, Error core: %s"
                                          % hex(status).__str__())

            input_image_buffer = output_image_temp

        mutex = image_process_config.get_mutex()
        with mutex:
            mono_img_process_param = image_process_config.get_mono_image_process()
            status = dx_mono8_image_process(input_image_buffer, output_address,
                                            raw_image_width, raw_image_height, mono_img_process_param)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "RawImage.dx_mono8_image_process: failed, error code:%s" % hex(status).__str__())

    def __check_handle(self):
        """
        :brief  The transformation handle is initialized the first time it is called
        :return NONE
        """
        if self.image_convert_handle is None:
            status, handle = dx_image_format_convert_create()
            if status != DxStatus.OK:
                raise UnexpectedError("dx_image_format_convert_create failure, Error code:%s" % hex(status).__str__())
            self.image_convert_handle = handle


    def __get_pixel_bit(self, pixel_format):
        """
        :brief  get pixel bit
        :return pixel bit
        """
        return (pixel_format & PIXEL_BIT_MASK)

    def __is_packed_pixel_format(self, pixel_format):
        """
        :brief  Get whether it is in packed pixel format

        :return true is packed , false is not packed
        """
        pixel_bit = self.__get_pixel_bit(pixel_format)
        if (pixel_format & PIXEL_MONO):
            if pixel_bit in (gxipy.GX_PIXEL_10BIT, gxipy.GX_PIXEL_12BIT, gxipy.GX_PIXEL_14BIT,):
                return True

        return False


