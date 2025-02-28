#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.Feature_s import *
from gxipy.StatusProcessor import *
import types

class FeatureControl:
    def __init__(self,handle):
        """
        :brief  Constructor for instance initialization
        :param handle:
        """
        self.__handle = handle

    def is_implemented(self,feature_name):
        """
        :brief      Get feature node is implemented
        :param feature_name: Feature node name
        :return:    Is implemented
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.is_implemented: "
                                     "Expected feature_name type is int, not %s" % type(feature_name))

        status, node_access = gx_get_node_access_mode( self.__handle ,feature_name)
        StatusProcessor.process(status, 'FeatureControl', 'is_implemented')
        if ((node_access == GxNodeAccessMode.MODE_NI) or (node_access == GxNodeAccessMode.MODE_UNDEF)):
            return  False
        else:
            return True

    def is_readable(self, feature_name):
        """
        brief:  Determining whether the feature is readable
        return: is_readable
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_int_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        status, node_access = gx_get_node_access_mode( self.__handle ,feature_name)
        StatusProcessor.process(status, 'FeatureControl', 'is_readable')
        if ((node_access == GxNodeAccessMode.MODE_RO) or (node_access == GxNodeAccessMode.MODE_RW)):
            return True
        else:
            return False

    def is_writable(self, feature_name):
        """
        brief:  Determining whether the feature is writable
        return: is_writable
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_int_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        status, node_access = gx_get_node_access_mode( self.__handle ,feature_name)
        StatusProcessor.process(status, 'FeatureControl', 'is_readable')
        if ((node_access == GxNodeAccessMode.MODE_WO) or (node_access == GxNodeAccessMode.MODE_RW)):
            return True
        else:
            return False

    def get_int_feature(self, feature_name):
        """
        :brief      Get int type feature object
        :param feature_name:    Feature node name
        :return:    Int type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_int_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_int_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        int_feature = IntFeature_s( self.__handle, feature_name)
        return int_feature

    def get_enum_feature(self, feature_name):
        """
        :brief      Get enum type feature object
        :param feature_name: Feature node name
        :return:    Enum type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_enum_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_enum_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        enum_feature = EnumFeature_s( self.__handle, feature_name)
        return enum_feature

    def get_float_feature(self, feature_name):
        """
        :brief      Get float type feature object
        :param feature_name: Feature node name
        :return:    Float type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_float_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_float_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        float_feature = FloatFeature_s( self.__handle, feature_name)
        return float_feature

    def get_bool_feature(self, feature_name):
        """
        :brief      Get bool type feature object
        :param feature_name: Feature node name
        :return:    Bool type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_bool_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_bool_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        bool_feature = BoolFeature_s( self.__handle, feature_name)
        return bool_feature

    def get_string_feature(self, feature_name):
        """
        :brief      Get string type feature object
        :param feature_name: Feature node name
        :return:    String type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_string_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_string_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        string_feature = StringFeature_s( self.__handle, feature_name)
        return string_feature

    def get_command_feature(self, feature_name):
        """
        :brief      Get command type feature object
        :param feature_name: Feature node name
        :return:    Command type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_command_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_command_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        command_feature = CommandFeature_s( self.__handle, feature_name)
        return command_feature

    def get_register_feature(self, feature_name):
        """
        :brief      Get register type feature object
        :param feature_name: Feature node name
        :return:    Register type feature object
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("FeatureControl.get_register_feature: "
                                     "Expected feature_name type is str, not %s" % type(feature_name))

        if not self.is_implemented( feature_name):
             raise  UnexpectedError( "FeatureControl.get_register_feature: "
                                     "The feature '%s' is not implemented" %feature_name)

        register_feature = RegisterFeature_s( self.__handle, feature_name)
        return register_feature

    def feature_save(self, file_path):
        """
        :brief      Save User Parameter Group
        :param file_path: Save Parameter file path
        :return:    None
        """
        status =  gx_feature_save( self.__handle, file_path)
        StatusProcessor.process(status, 'FeatureControl', 'feature_save')

    def feature_load(self, file_path, verify=False):
        """
        :brief      Load User Parameter Group
        :param file_path: Load Parameter file path
        :return:    None
        """
        status = gx_feature_load(self.__handle, file_path, verify)
        StatusProcessor.process(status, 'FeatureControl', 'feature_load')

    def read_port(self, address, size):
        """
        :brief      Read register
        :param      address:    The address of the register to be read.(type: int)
        :param      bytearray:  The data to be read from user.(type: buffer)
        :return:    none
        """
        if not isinstance(address, INT_TYPE):
            raise ParameterTypeError("Device.read_port: "
                                     "Expected address type is int, not %s" % type(address))

        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.read_port: "
                                     "Expected size type is int, not %s" % type(size))

        status, buff_value = gx_read_port( self.__handle, address, size)
        StatusProcessor.process(status, 'FeatureControl', 'read_port')
        return  buff_value

    def write_port(self, address, buff, size):
        """
        :brief      Write register
        :param      address:    The address of the register to be written.(type: int)
        :param      bytearray:  The data to be written from user.(type: buffer)
        :return:    none
        """
        if not isinstance(address, INT_TYPE):
            raise ParameterTypeError("Device.write_remote_device_port: "
                                     "Expected address type is int, not %s" % type(address))

        status = gx_writer_port( self.__handle, address, buff, size)
        StatusProcessor.process(status, 'FeatureControl', 'write_port')

    def read_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]Batch read register addresses and values
                      [out]Read the data to the corresponding register
        :read_num     [in]Read the number of device registers
                      [out]The number of registers that were successfully read
        :return:    none
        """
        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.set_read_remote_device_port_stacked: "
                                     "Expected size type is int, not %s" % type(size))

        status = gx_read_port_stacked(self.__handle, entries, size)
        StatusProcessor.process(status, 'Device', 'read_remote_device_port_stacked')

        return status

    def write_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]The address and value of the batch write register
        :read_num     [in]Sets the number of device registers
                      [out]The number of registers that were successfully written
        :return:    none
        """
        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.set_read_remote_device_port_stacked: "
                                     "Expected size type is int, not %s" % type(size))

        status = gx_set_write_remote_device_port_stacked(self.__handle, entries, size)
        StatusProcessor.process(status, 'Device', 'set_write_remote_device_port_stacked')

        return status