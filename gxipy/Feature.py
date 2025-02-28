#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

#以下已废弃，请使用上面的类型

from gxipy.gxiapi import *
from gxipy.ImageProc import *
from gxipy.StatusProcessor import *

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class Feature:
    def __init__(self, handle, feature):
        """
        :param  handle:      The handle of the device
        :param  feature:     The feature code ID
        """
        self.__handle = handle
        self.__feature = feature
        self.feature_name = self.get_name()

    def get_name(self):
        """
        brief:  Getting Feature Name
        return: Success:    feature name
                Failed:     convert feature ID to string
        """
        status, name = gx_get_feature_name(self.__handle, self.__feature)
        if status != GxStatusList.SUCCESS:
            name = (hex(self.__feature)).__str__()

        return name

    def is_implemented(self):
        """
        brief:  Determining whether the feature is implemented
        return: is_implemented
        """
        status, is_implemented = gx_is_implemented(self.__handle, self.__feature)
        if status == GxStatusList.SUCCESS:
            return is_implemented
        elif status == GxStatusList.INVALID_PARAMETER:
            return False
        else:
            StatusProcessor.process(status, 'Feature', 'is_implemented')

    def is_readable(self):
        """
        brief:  Determining whether the feature is readable
        return: is_readable
        """
        implemented = self.is_implemented()
        if not implemented:
            return False

        status, is_readable = gx_is_readable(self.__handle, self.__feature)
        StatusProcessor.process(status, 'Feature', 'is_readable')
        return is_readable

    def is_writable(self):
        """
        brief:  Determining whether the feature is writable
        return: is_writable
        """
        implemented = self.is_implemented()
        if not implemented:
            return False

        status, is_writable = gx_is_writable(self.__handle, self.__feature)
        StatusProcessor.process(status, 'Feature', 'is_writable')
        return is_writable


class IntFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param  handle:      The handle of the device
        :param  feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def __range_dict(self, int_range):
        """
        :brief      Convert GxIntRange to dictionary
        :param      int_range:  GxIntRange
        :return:    range_dicts
        """
        range_dicts = {
            "min": int_range.min,
            "max": int_range.max,
            "inc": int_range.inc
        }
        return range_dicts

    def get_range(self):
        """
        :brief      Getting integer range
        :return:    integer range dictionary
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.get_range is not support" % self.feature_name)
            raise NoImplemented("%s.get_range is not support" % self.feature_name)

        status, int_range = gx_get_int_range(self.__handle, self.__feature)
        StatusProcessor.process(status, 'IntFeature', 'get_range')
        return self.__range_dict(int_range)

    def get(self):
        """
        :brief      Getting integer value
        :return:    integer value
        """
        readable = self.is_readable()
        if not readable:
            #print("%s.get is not readable" % self.feature_name)
            raise InvalidAccess("%s.get is not readable" % self.feature_name)

        status, int_value = gx_get_int(self.__handle, self.__feature)
        StatusProcessor.process(status, 'IntFeature', 'get')
        return int_value

    def set(self, int_value):
        """
        :brief      Setting integer value
        :param      int_value
        :return:    None
        """
        if not isinstance(int_value, INT_TYPE):
            raise ParameterTypeError("IntFeature.set: "
                                     "Expected int_value type is int, not %s" % type(int_value))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set: is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set: is not writeable" % self.feature_name)

        int_range = self.get_range()
        check_ret = range_check(int_value, int_range["min"], int_range["max"], int_range["inc"])
        if not check_ret:
            #print("IntFeature.set: "
            #     "int_value out of bounds, %s.range=[%d, %d, %d]" %
            #      (self.feature_name, int_range["min"], int_range["max"], int_range["inc"]))
            raise OutOfRange("IntFeature.set: "
                  "int_value out of bounds, %s.range=[%d, %d, %d]" %
                  (self.feature_name, int_range["min"], int_range["max"], int_range["inc"]))
            return

        status = gx_set_int(self.__handle, self.__feature, int_value)
        StatusProcessor.process(status, 'IntFeature', 'set')


class FloatFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param      handle:      The handle of the device
        :param      feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def __range_dict(self, float_range):
        """
        :brief      Convert GxFloatRange to dictionary
        :param      float_range:  GxFloatRange
        :return:    range_dicts
        """
        range_dicts = {
            "min": float_range.min,
            "max": float_range.max,
            "inc": float_range.inc,
            "unit": string_decoding(float_range.unit),
            "inc_is_valid": float_range.inc_is_valid
        }
        return range_dicts

    def get_range(self):
        """
        :brief      Getting float range
        :return:    float range dictionary
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.get_range is not support" % self.feature_name)
            raise NoImplemented("%s.get_range is not support" % self.feature_name)

        status, float_range = gx_get_float_range(self.__handle, self.__feature)
        StatusProcessor.process(status, 'FloatFeature', 'get_range')
        return self.__range_dict(float_range)

    def get(self):
        """
        :brief      Getting float value
        :return:    float value
        """
        readable = self.is_readable()
        if not readable:
            #print("%s.get: is not readable" % self.feature_name)
            raise InvalidAccess("%s.get: is not readable" % self.feature_name)

        status, float_value = gx_get_float(self.__handle, self.__feature)
        StatusProcessor.process(status, 'FloatFeature', 'get')
        return float_value

    def set(self, float_value):
        """
        :brief      Setting float value
        :param      float_value
        :return:    None
        """
        if not isinstance(float_value, (INT_TYPE, float)):
            raise ParameterTypeError("FloatFeature.set: "
                                     "Expected float_value type is float, not %s" % type(float_value))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set: is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set: is not writeable" % self.feature_name)

        float_range = self.get_range()
        check_ret = range_check(float_value, float_range["min"], float_range["max"])
        if not check_ret:
            #print("FloatFeature.set: float_value out of bounds, %s.range=[%f, %f]" %
             #     (self.feature_name, float_range["min"], float_range["max"]))
            raise OutOfRange("FloatFeature.set: float_value out of bounds, %s.range=[%f, %f]" %
                  (self.feature_name, float_range["min"], float_range["max"]))
            return

        status = gx_set_float(self.__handle, self.__feature, float_value)
        StatusProcessor.process(status, 'FloatFeature', 'set')


class EnumFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param handle:      The handle of the device
        :param feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def get_range(self):
        """
        :brief      Getting range of Enum feature
        :return:    enum_dict:    enum range dictionary
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.get_range: is not support" % self.feature_name)
            raise NoImplemented("%s.get_range: is not support" % self.feature_name)

        status, enum_num = gx_get_enum_entry_nums(self.__handle, self.__feature)
        StatusProcessor.process(status, 'EnumFeature', 'get_range')

        status, enum_list = gx_get_enum_description(self.__handle, self.__feature, enum_num)
        StatusProcessor.process(status, 'EnumFeature', 'get_range')

        enum_dict = {}
        for i in range(enum_num):
            enum_dict[string_decoding(enum_list[i].symbolic)] = enum_list[i].fitness

        return enum_dict

    def get(self):
        """
        :brief      Getting value of Enum feature
        :return:    enum_value:     enum value
                    enum_str:       string for enum description
        """
        readable = self.is_readable()
        if not readable:
            #print("%s.get: is not readable" % self.feature_name)
            raise InvalidAccess("%s.get: is not readable" % self.feature_name)

        status, enum_value = gx_get_enum(self.__handle, self.__feature)
        StatusProcessor.process(status, 'EnumFeature', 'get')

        range_dict = self.get_range()
        new_dicts = {v: k for k, v in range_dict.items()}
        return enum_value, new_dicts[enum_value]

    def set(self, enum_value):
        """
        :brief      Setting enum value
        :param      enum_value
        :return:    None
        """
        if not isinstance(enum_value, INT_TYPE):
            raise ParameterTypeError("EnumFeature.set: "
                                     "Expected enum_value type is int, not %s" % type(enum_value))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set: is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set: is not writeable" % self.feature_name)

        range_dict = self.get_range()
        enum_value_list = range_dict.values()
        if enum_value not in enum_value_list:
            #print("EnumFeature.set: enum_value out of bounds, %s.range:%s" %
                #  (self.feature_name, range_dict.__str__()))
            raise OutOfRange("EnumFeature.set: enum_value out of bounds, %s.range:%s" %
                  (self.feature_name, range_dict.__str__()))
            return

        status = gx_set_enum(self.__handle, self.__feature, enum_value)
        StatusProcessor.process(status, 'EnumFeature', 'set')


class BoolFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param handle:      The handle of the device
        :param feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def get(self):
        """
        :brief      Getting bool value
        :return:    bool value[bool]
        """
        readable = self.is_readable()
        if not readable:
           # print("%s.get is not readable" % self.feature_name)
            raise InvalidAccess("%s.get is not readable" % self.feature_name)

        status, bool_value = gx_get_bool(self.__handle, self.__feature)
        StatusProcessor.process(status, 'BoolFeature', 'get')
        return bool_value

    def set(self, bool_value):
        """
        :brief      Setting bool value
        :param      bool_value[bool]
        :return:    None
        """
        if not isinstance(bool_value, bool):
            raise ParameterTypeError("BoolFeature.set: "
                                     "Expected bool_value type is bool, not %s" % type(bool_value))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set: is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set: is not writeable" % self.feature_name)

        status = gx_set_bool(self.__handle, self.__feature, bool_value)
        StatusProcessor.process(status, 'BoolFeature', 'set')


class StringFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param      handle:      The handle of the device
        :param      feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def get_string_max_length(self):
        """
        :brief      Getting the maximum length that string can set
        :return:    length:     the maximum length that string can set
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.get_string_max_length is not support" % self.feature_name)
            raise NoImplemented("%s.get_string_max_length is not support" % self.feature_name)

        status, length = gx_get_string_max_length(self.__handle, self.__feature)
        StatusProcessor.process(status, 'StringFeature', 'get_string_max_length')
        return length

    def get(self):
        """
        :brief      Getting string value
        :return:    strings
        """
        readable = self.is_readable()
        if not readable:
            #print("%s.get is not readable" % self.feature_name)
            raise InvalidAccess("%s.get is not readable" % self.feature_name)

        status, strings = gx_get_string(self.__handle, self.__feature)
        StatusProcessor.process(status, 'StringFeature', 'get')
        return strings

    def set(self, input_string):
        """
        :brief      Setting string value
        :param      input_string[string]
        :return:    None
        """
        if not isinstance(input_string, str):
            raise ParameterTypeError("StringFeature.set: "
                                     "Expected input_string type is str, not %s" % type(input_string))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set: is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set: is not writeable" % self.feature_name)

        max_length = self.get_string_max_length()
        if input_string.__len__() > max_length:
            #print("StringFeature.set: " "input_string length out of bounds, %s.length_max:%s"                  % (self.feature_name, max_length))
            raise OutOfRange("StringFeature.set: "
                  "input_string length out of bounds, %s.length_max:%s"
                  % (self.feature_name, max_length))
            return

        status = gx_set_string(self.__handle, self.__feature, input_string)
        StatusProcessor.process(status, 'StringFeature', 'set')


class BufferFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param      handle:      The handle of the device
        :param      feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def get_buffer_length(self):
        """
        :brief      Getting buffer length
        :return:    length:     buffer length
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.get_buffer_length is not support" % self.feature_name)
            raise NoImplemented("%s.get_buffer_length is not support" % self.feature_name)

        status, length = gx_get_buffer_length(self.__handle, self.__feature)
        StatusProcessor.process(status, 'BuffFeature', 'get_buffer_length')
        return length

    def get_buffer(self):
        """
        :brief      Getting buffer data
        :return:    Buffer object

        """
        readable = self.is_readable()
        if not readable:
            #print("%s.get_buffer is not readable" % self.feature_name)
            raise InvalidAccess("%s.get_buffer is not readable" % self.feature_name)

        status, buf = gx_get_buffer(self.__handle, self.__feature)
        StatusProcessor.process(status, 'BuffFeature', 'get_buffer')
        return Buffer(buf)

    def set_buffer(self, buf):
        """
        :brief      Setting buffer data
        :param      buf:    Buffer object
        :return:    None
        """
        if not isinstance(buf, Buffer):
            raise ParameterTypeError("BuffFeature.set_buffer: "
                                     "Expected buff type is Buffer, not %s" % type(buf))

        writeable = self.is_writable()
        if not writeable:
            #print("%s.set_buffer is not writeable" % self.feature_name)
            raise InvalidAccess("%s.set_buffer is not writeable" % self.feature_name)

        max_length = self.get_buffer_length()
        if buf.get_length() > max_length:
            #print("BuffFeature.set_buffer: "
             #     "buff length out of bounds, %s.length_max:%s" % (self.feature_name, max_length))
            raise OutOfRange("BuffFeature.set_buffer: "
                  "buff length out of bounds, %s.length_max:%s" % (self.feature_name, max_length))
            return

        status = gx_set_buffer(self.__handle, self.__feature,
                               buf.get_ctype_array(), buf.get_length())
        StatusProcessor.process(status, 'BuffFeature', 'set_buffer')


class CommandFeature(Feature):
    def __init__(self, handle, feature):
        """
        :param      handle:      The handle of the device
        :param      feature:     The feature code ID
        """
        Feature.__init__(self, handle, feature)
        self.__handle = handle
        self.__feature = feature

    def send_command(self):
        """
        :brief      Sending command
        :return:    None
        """
        implemented = self.is_implemented()
        if not implemented:
            #print("%s.send_command is not support" % self.feature_name)
            raise NoImplemented("%s.send_command is not support" % self.feature_name)

        status = gx_send_command(self.__handle, self.__feature)
        StatusProcessor.process(status, 'CommandFeature', 'send_command')

