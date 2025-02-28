#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxiapi import *
from gxipy.gxidef import *
from gxipy.ImageProc import *
import types

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class ImageFormatConvert:
    def __init__(self):
        self.alpha_value = 255
        self.image_pixel_format_des = GxPixelFormatEntry.UNDEFINED
        self.interpolation_type = DxBayerConvertType.NEIGHBOUR
        self.image_convert_handle = None
        self.valid_bits = DxValidBit.BIT0_7

    def __new__(cls, *args, **kw):
        return object.__new__(cls, *args)

    def __del__(self):
        if self.image_convert_handle is not None:
            status = dx_image_format_convert_destroy(self.image_convert_handle)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_image_format_convert_destroy failure, Error code:%s" % hex(status).__str__())
            self.image_convert_handle = None

    def set_dest_format(self, dest_pixel_format):
        """
        :brief      set desired pixel format
        :param:    dest_pixel_format(desired pixel format)
        """
        if not (isinstance(dest_pixel_format, INT_TYPE)):
            raise ParameterTypeError("dest_pixel_format must to be GxPixelFormatEntry's element.")

        self.__check_handle()
        status = dx_image_format_convert_set_output_pixel_format(self.image_convert_handle, dest_pixel_format)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_image_format_convert_set_output_pixel_format failure, Error code:%s" % hex(status).__str__())
        self.image_pixel_format_des = dest_pixel_format

    def get_dest_format(self):
        """
        :brief     get desired pixel format
        :param:    dest_pixel_format(desired pixel format)
        """
        self.__check_handle()
        status, pixel_format = dx_image_format_convert_get_output_pixel_format(self.image_convert_handle)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_image_format_convert_get_output_pixel_format failure, Error code:%s" % hex(status).__str__())

        return pixel_format

    def set_interpolation_type(self, cvt_type):
        """
        :brief  set the conversion algorithm
        :param  cvt_type：conversion algorithm       [in] deault: DxBayerConvertType.NEIGHBOUR
        """
        if not isinstance(cvt_type, INT_TYPE):
            raise ParameterTypeError("cc_type param must be int in DxRGBChannelOrder")

        self.__check_handle()
        status = dx_image_format_convert_set_interpolation_type(self.image_convert_handle, cvt_type)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_image_format_convert_set_interpolation_type failure, Error code:%s" % hex(status).__str__())
        self.interpolation_type = cvt_type

    def get_interpolation_type(self):
        """
        :brief   get the conversion algorithm
        """
        return self.interpolation_type

    def set_alpha_value(self, alpha_value):
        """
        :brief  Sets the Alpha value for images with Alpha channels
        :param  alpha_value: alpha value,range 0~255 deault 255
        :return void
        """
        if not isinstance(alpha_value, INT_TYPE):
            raise ParameterTypeError("alpha_value param must be int type.")

        self.__check_handle()
        if alpha_value < 0 or alpha_value > 255:
            raise InvalidParameter("DX_PARAMETER_OUT_OF_BOUND")

        status = dx_image_format_convert_set_alpha_value(self.image_convert_handle, alpha_value)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_set_alpha_value failure, Error code:%s" % hex(status).__str__())

        self.alpha_value = alpha_value

    def get_alpha_value(self):
        """
        :brief  Gets the Alpha value for images with Alpha channels
        """
        return self.alpha_value

    def set_valid_bits(self, valid_bits):
        """
        :brief Set valid Bits
        :param  valid_bits, refer to DxValidBit
        :return void
        """

        if not isinstance(valid_bits, INT_TYPE):
            raise ParameterTypeError("valid_bits param must be int in DxValidBit element.")

        self.__check_handle()
        status = dx_image_format_convert_set_valid_bits(self.image_convert_handle, valid_bits)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_set_alpha_value failure, Error code:%s" % hex(status).__str__())

        self.valid_bits = valid_bits

    def get_valid_bits(self):
        """
        :brief  Get valid Bits
        """
        return self.valid_bits

    def get_buffer_size_for_conversion_ex(self, width, height, pixel_format):
        """
        :brief  Calculating Buffer size for conversion
        :param  emPixelFormat   [in]   Pixel Format
        :param  nImgWidth       [in]   Image Width
        :param  nImgHeight      [in]   Image Height
        :return image buffer size
        """
        if not isinstance(width, INT_TYPE):
            raise ParameterTypeError("width param must be int type.")

        if not isinstance(height, INT_TYPE):
            raise ParameterTypeError("height param must be int type.")

        if not (isinstance(pixel_format, INT_TYPE)):
            raise ParameterTypeError("pixel_format must to be GxPixelFormatEntry's element.")

        self.__check_handle()
        status, buffer_size_c = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle, pixel_format, width, height)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(status).__str__())

        return buffer_size_c

    def get_buffer_size_for_conversion(self, raw_image):
        """
        :brief  Calculating Buffer size for conversion
        :param  raw_image.get_width       [in]   Image Width
        :param  raw_image.get_height      [in]   Image Height
        :return image buffer size
        """

        if not isinstance(raw_image, RawImage):
            raise ParameterTypeError("raw_image param must be RawImage type")

        self.__check_handle()
        status, buffer_size_c = dx_image_format_convert_get_buffer_size_for_conversion(self.image_convert_handle, self.image_pixel_format_des,
                                                                                       raw_image.get_width(), raw_image.get_height())
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(status).__str__())

        return buffer_size_c

    def convert_ex(self, input_address, input_width, input_height, src_fixel_format, output_address, output_length, flip):
        """
        :brief  Image Format Convert Process

        Supported image format conversion include

        1.Bayer conversion
         a. input image format  GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GB8 GX_PIXEL_FORMAT_BAYER_BG8
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_RGB8  GX_PIXEL_FORMAT_RGBA8 GX_PIXEL_FORMAT_BGRA8
                                GX_PIXEL_FORMAT_ARGB8 GX_PIXEL_FORMAT_ABGR8 GX_PIXEL_FORMAT_RGB8_PLANAR

         b. input image format  GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GB10 GX_PIXEL_FORMAT_BAYER_BG10
                                GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GB12 GX_PIXEL_FORMAT_BAYER_BG12
                                GX_PIXEL_FORMAT_BAYER_GR14 GX_PIXEL_FORMAT_BAYER_RG14 GX_PIXEL_FORMAT_BAYER_GB14 GX_PIXEL_FORMAT_BAYER_BG14
                                GX_PIXEL_FORMAT_BAYER_GR16 GX_PIXEL_FORMAT_BAYER_RG16 GX_PIXEL_FORMAT_BAYER_GB16 GX_PIXEL_FORMAT_BAYER_BG16
            output image format GX_PIXEL_FORMAT_MONO16 GX_PIXEL_FORMAT_RGB16  GX_PIXEL_FORMAT_BGR16 GX_PIXEL_FORMAT_RGB16_PLANAR
			                    GX_PIXEL_FORMAT_RGB8 GX_PIXEL_FORMAT_BGR8

        2.RGB conversion
         a. input image format  GX_PIXEL_FORMAT_RGB8 GX_PIXEL_FORMAT_BGR8
            output image format GX_PIXEL_FORMAT_YUV444_8 GX_PIXEL_FORMAT_YUV422_8 GX_PIXEL_FORMAT_YUV411_8 GX_PIXEL_FORMAT_YUV420_8_PLANAR
                                GX_PIXEL_FORMAT_YCBCR444_8 GX_PIXEL_FORMAT_YCBCR422_8 GX_PIXEL_FORMAT_YCBCR411_8 GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_RGB8

         b. input image format  GX_PIXEL_FORMAT_RGB16 GX_PIXEL_FORMAT_BGR16
            output image format GX_PIXEL_FORMAT_MONO16

        3.Packed conversion(GVSP)
         a. input image format  GX_PIXEL_FORMAT_MONO10_PACKED GX_PIXEL_FORMAT_MONO12_PACKED
		                        GX_PIXEL_FORMAT_BAYER_RG10_PACKED GX_PIXEL_FORMAT_BAYER_GR10_PACKED GX_PIXEL_FORMAT_BAYER_BG10_PACKED GX_PIXEL_FORMAT_BAYER_GB10_PACKED
								GX_PIXEL_FORMAT_BAYER_RG12_PACKED GX_PIXEL_FORMAT_BAYER_GR12_PACKED GX_PIXEL_FORMAT_BAYER_BG12_PACKED GX_PIXEL_FORMAT_BAYER_GB12_PACKED
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_RGB8
                                GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_BG8 GX_PIXEL_FORMAT_BAYER_GB8
                                GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_BG10 GX_PIXEL_FORMAT_BAYER_GB10
                                GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_BG12 GX_PIXEL_FORMAT_BAYER_GB12
								GX_PIXEL_FORMAT_RGB8

        4.Packed conversion(PFNC)
         a. input image format  GX_PIXEL_FORMAT_MONO10_P GX_PIXEL_FORMAT_MONO12_P GX_PIXEL_FORMAT_MONO14_P
		                        GX_PIXEL_FORMAT_BAYER_RG10_P GX_PIXEL_FORMAT_BAYER_GR10_P GX_PIXEL_FORMAT_BAYER_BG10_P GX_PIXEL_FORMAT_BAYER_GB10_P
								GX_PIXEL_FORMAT_BAYER_RG12_P GX_PIXEL_FORMAT_BAYER_GR12_P GX_PIXEL_FORMAT_BAYER_BG12_P GX_PIXEL_FORMAT_BAYER_GB12_P
   								GX_PIXEL_FORMAT_BAYER_RG14_P GX_PIXEL_FORMAT_BAYER_GR14_P GX_PIXEL_FORMAT_BAYER_BG14_P GX_PIXEL_FORMAT_BAYER_GB14_P
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_MONO14 GX_PIXEL_FORMAT_RGB8
                                GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_BG8 GX_PIXEL_FORMAT_BAYER_GB8
                                GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_BG10 GX_PIXEL_FORMAT_BAYER_GB10
                                GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_BG12 GX_PIXEL_FORMAT_BAYER_GB12
                                GX_PIXEL_FORMAT_BAYER_RG14 GX_PIXEL_FORMAT_BAYER_GR14 GX_PIXEL_FORMAT_BAYER_BG14 GX_PIXEL_FORMAT_BAYER_GB14
        5.Mono conversion
         a. input image format  GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_R8 GX_PIXEL_FORMAT_G8 GX_PIXEL_FORMAT_B8
            output image format GX_PIXEL_FORMAT_RGB8

         b. input image format  GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_MONO14 GX_PIXEL_FORMAT_MONO16
            output image format GX_PIXEL_FORMAT_RGB8

        :param  input_address    [in]     Image in
        :param  output_length   [in&out] Image out
        :param  nOutBufferSize  [in]     Output Image buffer size
        :param  src_fixel_format [in]     Input Image Pixel Type
        :param  input_width       [in]     Image width
        :param  input_height      [in]     Image height
        :param  flip           [in]     Image flip or not, true:flip false:not flip

        :return emStatus
        """

        if input_address is None:
            raise ParameterTypeError("input_address is NULL pointer.")

        if output_address is None:
            raise ParameterTypeError("output_address is NULL pointer.")

        if not isinstance(input_width, INT_TYPE):
            raise ParameterTypeError("input_width param must be int type.")

        if not isinstance(input_height, INT_TYPE):
            raise ParameterTypeError("input_height param must be int type.")

        if not (isinstance(src_fixel_format, INT_TYPE)):
            raise ParameterTypeError("src_fixel_format must to be GxPixelFormatEntry's element.")

        if not (isinstance(output_length, INT_TYPE)):
            raise ParameterTypeError("output_length must to be  int type.")

        if not (isinstance(flip, bool)):
            raise ParameterTypeError("flip must to be  bool type.")

        self.__check_handle()
        input_length = self.get_buffer_size_for_conversion_ex(input_width, input_height, src_fixel_format)

        status = dx_image_format_convert(self.image_convert_handle, input_address, input_length, output_address, output_length, src_fixel_format, input_width,
                                input_height, flip)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())

    def convert(self, raw_image, output_address, output_length, flip):
        """
        :brief  Image Format Convert Process

        Supported image format conversion include

        1.Bayer conversion
         a. input image format  GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GB8 GX_PIXEL_FORMAT_BAYER_BG8
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_RGB8  GX_PIXEL_FORMAT_RGBA8 GX_PIXEL_FORMAT_BGRA8
                                GX_PIXEL_FORMAT_ARGB8 GX_PIXEL_FORMAT_ABGR8 GX_PIXEL_FORMAT_RGB8_PLANAR

         b. input image format  GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GB10 GX_PIXEL_FORMAT_BAYER_BG10
                                GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GB12 GX_PIXEL_FORMAT_BAYER_BG12
                                GX_PIXEL_FORMAT_BAYER_GR14 GX_PIXEL_FORMAT_BAYER_RG14 GX_PIXEL_FORMAT_BAYER_GB14 GX_PIXEL_FORMAT_BAYER_BG14
                                GX_PIXEL_FORMAT_BAYER_GR16 GX_PIXEL_FORMAT_BAYER_RG16 GX_PIXEL_FORMAT_BAYER_GB16 GX_PIXEL_FORMAT_BAYER_BG16
            output image format GX_PIXEL_FORMAT_MONO16 GX_PIXEL_FORMAT_RGB16  GX_PIXEL_FORMAT_BGR16 GX_PIXEL_FORMAT_RGB16_PLANAR
			                    GX_PIXEL_FORMAT_RGB8 GX_PIXEL_FORMAT_BGR8

        2.RGB conversion
         a. input image format  GX_PIXEL_FORMAT_RGB8 GX_PIXEL_FORMAT_BGR8
            output image format GX_PIXEL_FORMAT_YUV444_8 GX_PIXEL_FORMAT_YUV422_8 GX_PIXEL_FORMAT_YUV411_8 GX_PIXEL_FORMAT_YUV420_8_PLANAR
                                GX_PIXEL_FORMAT_YCBCR444_8 GX_PIXEL_FORMAT_YCBCR422_8 GX_PIXEL_FORMAT_YCBCR411_8 GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_RGB8

         b. input image format  GX_PIXEL_FORMAT_RGB16 GX_PIXEL_FORMAT_BGR16
            output image format GX_PIXEL_FORMAT_MONO16

        3.Packed conversion(GVSP)
         a. input image format  GX_PIXEL_FORMAT_MONO10_PACKED GX_PIXEL_FORMAT_MONO12_PACKED
		                        GX_PIXEL_FORMAT_BAYER_RG10_PACKED GX_PIXEL_FORMAT_BAYER_GR10_PACKED GX_PIXEL_FORMAT_BAYER_BG10_PACKED GX_PIXEL_FORMAT_BAYER_GB10_PACKED
								GX_PIXEL_FORMAT_BAYER_RG12_PACKED GX_PIXEL_FORMAT_BAYER_GR12_PACKED GX_PIXEL_FORMAT_BAYER_BG12_PACKED GX_PIXEL_FORMAT_BAYER_GB12_PACKED
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_RGB8
                                GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_BG8 GX_PIXEL_FORMAT_BAYER_GB8
                                GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_BG10 GX_PIXEL_FORMAT_BAYER_GB10
                                GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_BG12 GX_PIXEL_FORMAT_BAYER_GB12
								GX_PIXEL_FORMAT_RGB8

        4.Packed conversion(PFNC)
         a. input image format  GX_PIXEL_FORMAT_MONO10_P GX_PIXEL_FORMAT_MONO12_P GX_PIXEL_FORMAT_MONO14_P
		                        GX_PIXEL_FORMAT_BAYER_RG10_P GX_PIXEL_FORMAT_BAYER_GR10_P GX_PIXEL_FORMAT_BAYER_BG10_P GX_PIXEL_FORMAT_BAYER_GB10_P
								GX_PIXEL_FORMAT_BAYER_RG12_P GX_PIXEL_FORMAT_BAYER_GR12_P GX_PIXEL_FORMAT_BAYER_BG12_P GX_PIXEL_FORMAT_BAYER_GB12_P
   								GX_PIXEL_FORMAT_BAYER_RG14_P GX_PIXEL_FORMAT_BAYER_GR14_P GX_PIXEL_FORMAT_BAYER_BG14_P GX_PIXEL_FORMAT_BAYER_GB14_P
            output image format GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_MONO14 GX_PIXEL_FORMAT_RGB8
                                GX_PIXEL_FORMAT_BAYER_RG8 GX_PIXEL_FORMAT_BAYER_GR8 GX_PIXEL_FORMAT_BAYER_BG8 GX_PIXEL_FORMAT_BAYER_GB8
                                GX_PIXEL_FORMAT_BAYER_RG10 GX_PIXEL_FORMAT_BAYER_GR10 GX_PIXEL_FORMAT_BAYER_BG10 GX_PIXEL_FORMAT_BAYER_GB10
                                GX_PIXEL_FORMAT_BAYER_RG12 GX_PIXEL_FORMAT_BAYER_GR12 GX_PIXEL_FORMAT_BAYER_BG12 GX_PIXEL_FORMAT_BAYER_GB12
                                GX_PIXEL_FORMAT_BAYER_RG14 GX_PIXEL_FORMAT_BAYER_GR14 GX_PIXEL_FORMAT_BAYER_BG14 GX_PIXEL_FORMAT_BAYER_GB14
        5.Mono conversion
         a. input image format  GX_PIXEL_FORMAT_MONO8 GX_PIXEL_FORMAT_R8 GX_PIXEL_FORMAT_G8 GX_PIXEL_FORMAT_B8
            output image format GX_PIXEL_FORMAT_RGB8

         b. input image format  GX_PIXEL_FORMAT_MONO10 GX_PIXEL_FORMAT_MONO12 GX_PIXEL_FORMAT_MONO14 GX_PIXEL_FORMAT_MONO16
            output image format GX_PIXEL_FORMAT_RGB8

        :param  raw_image    [in]     Image in
        :param  output_length   [in&out] Image out
        :param  nOutBufferSize  [in]     Output Image buffer size
        :param  flip           [in]     Image flip or not, true:flip false:not flip

        :return emStatus
        """
        if not isinstance(raw_image, RawImage):
            raise ParameterTypeError("raw_image param must be RawImage type")

        if raw_image.frame_data.image_buf is None:
            raise ParameterTypeError("raw_image.frame_data.image_buf is NULL pointer")

        if output_address is None:
            raise ParameterTypeError("output_address is NULL pointer")

        if not isinstance(output_length, INT_TYPE):
            raise ParameterTypeError("output_length param must be int type.")

        if not (isinstance(flip, bool)):
            raise ParameterTypeError("flip must to be  bool type.")

        self.__check_handle()
        input_length = self.get_buffer_size_for_conversion_ex(raw_image.get_width(), raw_image.get_height(), raw_image.get_pixel_format())

        status = dx_image_format_convert(self.image_convert_handle, raw_image.frame_data.image_buf, input_length, output_address,
                                         output_length, raw_image.get_pixel_format(), raw_image.get_width(), raw_image.get_height(), flip)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())

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




