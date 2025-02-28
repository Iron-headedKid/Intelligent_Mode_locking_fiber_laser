#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.FeatureControl import *
from gxipy.StatusProcessor import *
import types

class Interface:
    def __init__(self, handle, interface_info):
        """
        :brief  Constructor for instance initialization
        :param handle:  Interface Handle
        :param interface_info: Interface info list
        """
        self.__interface_handle = handle
        self.__interface_info = interface_info

    def get_interface_info(self):
        """
        :brief  Get interface info list
        :return: __interface_info
        """
        return self.__interface_info

    #def get_all_device_info_list(self):
    #    return None

    def get_feature_control(self):
        """
        :brief  Get interface feature control object
        :return: Interface feature control object
        """
        feature_control = FeatureControl( self.__interface_handle)
        return feature_control
