#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.gxiapi import *
import types

class UnexpectedError(Exception):
    """
    brief:  Unexpected error exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class NotFoundTL(Exception):
    """
    brief:  not found TL exception
    param:  args             exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class NotFoundDevice(Exception):
    """
    brief:  not found device exception
    param:  args              exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class OffLine(Exception):
    """
    brief:  device offline exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class InvalidParameter(Exception):
    """
    brief:  input invalid parameter exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class InvalidHandle(Exception):
    """
    brief:  invalid handle exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class InvalidCall(Exception):
    """
    brief:  invalid callback exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class InvalidAccess(Exception):
    """
    brief:  invalid access exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class NeedMoreBuffer(Exception):
    """
    brief:  need more buffer exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class FeatureTypeError(Exception):
    """
    brief:  feature id error exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class OutOfRange(Exception):
    """
    brief:  param out of range exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)
class NoImplemented(Exception):
    """
    brief:  param out of Implemented exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class NotInitApi(Exception):
    """
    brief:  not init api exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class Timeout(Exception):
    """
    brief:  timeout exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


class ParameterTypeError(Exception):
    """
    brief:  parameter type error exception
    param:  args            exception description
    return: none
    """
    def __init__(self, args):
        Exception.__init__(self, args)


def exception_deal(status, args):
    """
    brief:  deal with different exception
    param:  status         function return value
    param:  args            exception description
    return: none
    """
    if status == GxStatusList.ERROR:
        raise UnexpectedError(args)
    elif status == GxStatusList.NOT_FOUND_TL:
        raise NotFoundTL(args)
    elif status == GxStatusList.NOT_FOUND_DEVICE:
        raise NotFoundDevice(args)
    elif status == GxStatusList.OFFLINE:
        raise OffLine(args)
    elif status == GxStatusList.INVALID_PARAMETER:
        raise InvalidParameter(args)
    elif status == GxStatusList.INVALID_HANDLE:
        raise InvalidHandle(args)
    elif status == GxStatusList.INVALID_CALL:
        raise InvalidCall(args)
    elif status == GxStatusList.INVALID_ACCESS:
        raise InvalidAccess(args)
    elif status == GxStatusList.NEED_MORE_BUFFER:
        raise NeedMoreBuffer(args)
    elif status == GxStatusList.ERROR_TYPE:
        raise FeatureTypeError(args)
    elif status == GxStatusList.OUT_OF_RANGE:
        raise OutOfRange(args)
    elif status == GxStatusList.NOT_IMPLEMENTED:
        raise NoImplemented(args)
    elif status == GxStatusList.NOT_INIT_API:
        raise NotInitApi(args)
    elif status == GxStatusList.TIMEOUT:
        raise Timeout(args)
    elif status == GxStatusList.REPEAT_OPENED:
        raise InvalidAccess(args)
    else:
        raise Exception(args)
