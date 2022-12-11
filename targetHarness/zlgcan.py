# -*- coding:utf-8 -*-
#  zlgcan.py
#
#  ~~~~~~~~~~~~
#
#  ZLGCAN API
#
#  ~~~~~~~~~~~~
#
#  ------------------------------------------------------------------
#  Author : guochuangjian    
#  Last change: 21.02.2019
#
#  Language: Python 2.7, 3.6
#  ------------------------------------------------------------------
#
from ctypes import *
import platform
import threading

import time



ZCAN_DEVICE_TYPE = c_uint

INVALID_DEVICE_HANDLE  = 0
INVALID_CHANNEL_HANDLE = 0

'''
 Device Type
'''
ZCAN_PCI5121          = ZCAN_DEVICE_TYPE(1) 
ZCAN_PCI9810          = ZCAN_DEVICE_TYPE(2) 
ZCAN_USBCAN1          = ZCAN_DEVICE_TYPE(3) 
ZCAN_USBCAN2          = ZCAN_DEVICE_TYPE(4) 
ZCAN_PCI9820          = ZCAN_DEVICE_TYPE(5) 
ZCAN_CAN232           = ZCAN_DEVICE_TYPE(6) 
ZCAN_PCI5110          = ZCAN_DEVICE_TYPE(7) 
ZCAN_CANLITE          = ZCAN_DEVICE_TYPE(8) 
ZCAN_ISA9620          = ZCAN_DEVICE_TYPE(9) 
ZCAN_ISA5420          = ZCAN_DEVICE_TYPE(10)
ZCAN_PC104CAN         = ZCAN_DEVICE_TYPE(11)
ZCAN_CANETUDP         = ZCAN_DEVICE_TYPE(12)
ZCAN_CANETE           = ZCAN_DEVICE_TYPE(12)
ZCAN_DNP9810          = ZCAN_DEVICE_TYPE(13)
ZCAN_PCI9840          = ZCAN_DEVICE_TYPE(14)
ZCAN_PC104CAN2        = ZCAN_DEVICE_TYPE(15)
ZCAN_PCI9820I         = ZCAN_DEVICE_TYPE(16)
ZCAN_CANETTCP         = ZCAN_DEVICE_TYPE(17)
ZCAN_PCIE_9220        = ZCAN_DEVICE_TYPE(18)
ZCAN_PCI5010U         = ZCAN_DEVICE_TYPE(19)
ZCAN_USBCAN_E_U       = ZCAN_DEVICE_TYPE(20)
ZCAN_USBCAN_2E_U      = ZCAN_DEVICE_TYPE(21)
ZCAN_PCI5020U         = ZCAN_DEVICE_TYPE(22)
ZCAN_EG20T_CAN        = ZCAN_DEVICE_TYPE(23)
ZCAN_PCIE9221         = ZCAN_DEVICE_TYPE(24)
ZCAN_WIFICAN_TCP      = ZCAN_DEVICE_TYPE(25)
ZCAN_WIFICAN_UDP      = ZCAN_DEVICE_TYPE(26)
ZCAN_PCIe9120         = ZCAN_DEVICE_TYPE(27)
ZCAN_PCIe9110         = ZCAN_DEVICE_TYPE(28)
ZCAN_PCIe9140         = ZCAN_DEVICE_TYPE(29)
ZCAN_USBCAN_4E_U      = ZCAN_DEVICE_TYPE(31)
ZCAN_CANDTU_200UR     = ZCAN_DEVICE_TYPE(32)
ZCAN_CANDTU_MINI      = ZCAN_DEVICE_TYPE(33)
ZCAN_USBCAN_8E_U      = ZCAN_DEVICE_TYPE(34)
ZCAN_CANREPLAY        = ZCAN_DEVICE_TYPE(35)
ZCAN_CANDTU_NET       = ZCAN_DEVICE_TYPE(36)
ZCAN_CANDTU_100UR     = ZCAN_DEVICE_TYPE(37)
ZCAN_PCIE_CANFD_100U  = ZCAN_DEVICE_TYPE(38)
ZCAN_PCIE_CANFD_200U  = ZCAN_DEVICE_TYPE(39)
ZCAN_PCIE_CANFD_400U  = ZCAN_DEVICE_TYPE(40)
ZCAN_USBCANFD_200U    = ZCAN_DEVICE_TYPE(41)
ZCAN_USBCANFD_100U    = ZCAN_DEVICE_TYPE(42)
ZCAN_USBCANFD_MINI    = ZCAN_DEVICE_TYPE(43)
ZCAN_CANFDCOM_100IE   = ZCAN_DEVICE_TYPE(44)
ZCAN_CANSCOPE         = ZCAN_DEVICE_TYPE(45)
ZCAN_CLOUD            = ZCAN_DEVICE_TYPE(46)
ZCAN_CANDTU_NET_400   = ZCAN_DEVICE_TYPE(47)
ZCAN_VIRTUAL_DEVICE   = ZCAN_DEVICE_TYPE(99)

'''
 Interface return status
'''
ZCAN_STATUS_ERR         = 0
ZCAN_STATUS_OK          = 1
ZCAN_STATUS_ONLINE      = 2
ZCAN_STATUS_OFFLINE     = 3
ZCAN_STATUS_UNSUPPORTED = 4

'''
 CAN type
'''
ZCAN_TYPE_CAN    = c_uint(0)
ZCAN_TYPE_CANFD  = c_uint(1)

def input_thread():
   input()


'''
 Device information
'''
class ZCAN_DEVICE_INFO(Structure):
    _fields_ = [("hw_Version", c_ushort),
                ("fw_Version", c_ushort),
                ("dr_Version", c_ushort), 
                ("in_Version", c_ushort), 
                ("irq_Num", c_ushort),
                ("can_Num", c_ubyte),
                ("str_Serial_Num", c_ubyte * 20),
                ("str_hw_Type", c_ubyte * 40),
                ("reserved", c_ushort * 4)]

    def __str__(self):
        return "Hardware Version:%s\nFirmware Version:%s\nDriver Interface:%s\nInterface Interface:%s\nInterrupt Number:%d\nCAN Number:%d\nSerial:%s\nHardware Type:%s\n" %( \
                self.hw_version, self.fw_version, self.dr_version, self.in_version, self.irq_num, self.can_num, self.serial, self.hw_type)
                
    def _version(self, version):
        return ("V%02x.%02x" if version // 0xFF >= 9 else "V%d.%02x") % (version // 0xFF, version & 0xFF)
    
    @property
    def hw_version(self):
        return self._version(self.hw_Version)

    @property
    def fw_version(self):
        return self._version(self.fw_Version)
    
    @property
    def dr_version(self):
        return self._version(self.dr_Version)
    
    @property
    def in_version(self):
        return self._version(self.in_Version)

    @property
    def irq_num(self):
        return self.irq_Num

    @property
    def can_num(self):
        return self.can_Num

    @property
    def serial(self):
        serial = ''
        for c in self.str_Serial_Num:
            if c > 0: 
               serial += chr(c)
            else:
                break 
        return serial

    @property
    def hw_type(self):
        hw_type = ''
        for c in self.str_hw_Type:
            if c > 0:
                hw_type += chr(c)
            else:
                break
        return hw_type

class _ZCAN_CHANNEL_CAN_INIT_CONFIG(Structure):
    _fields_ = [("acc_code", c_uint),
                ("acc_mask", c_uint),
                ("reserved", c_uint),
                ("filter",   c_ubyte),
                ("timing0",  c_ubyte),
                ("timing1",  c_ubyte),
                ("mode",     c_ubyte)]

class _ZCAN_CHANNEL_CANFD_INIT_CONFIG(Structure):
    _fields_ = [("acc_code",     c_uint),
                ("acc_mask",     c_uint),
                ("abit_timing",  c_uint),
                ("dbit_timing",  c_uint),
                ("brp",          c_uint),
                ("filter",       c_ubyte),
                ("mode",         c_ubyte),
                ("pad",          c_ushort),
                ("reserved",     c_uint)]

class _ZCAN_CHANNEL_INIT_CONFIG(Union):
    _fields_ = [("can", _ZCAN_CHANNEL_CAN_INIT_CONFIG), ("canfd", _ZCAN_CHANNEL_CANFD_INIT_CONFIG)]

class ZCAN_CHANNEL_INIT_CONFIG(Structure):
    _fields_ = [("can_type", c_uint),
                ("config", _ZCAN_CHANNEL_INIT_CONFIG)]

class ZCAN_CHANNEL_ERR_INFO(Structure):
    _fields_ = [("error_code", c_uint),
                ("passive_ErrData", c_ubyte * 3),
                ("arLost_ErrData", c_ubyte)]

class ZCAN_CHANNEL_STATUS(Structure):
    _fields_ = [("errInterrupt", c_ubyte),
                ("regMode",      c_ubyte),
                ("regStatus",    c_ubyte), 
                ("regALCapture", c_ubyte),
                ("regECCapture", c_ubyte),
                ("regEWLimit",   c_ubyte),
                ("regRECounter", c_ubyte),
                ("regTECounter", c_ubyte),
                ("Reserved",     c_ubyte)]

class ZCAN_CAN_FRAME(Structure):
    _fields_ = [("can_id",  c_uint, 29),
                ("err",     c_uint, 1),
                ("rtr",     c_uint, 1),
                ("eff",     c_uint, 1), 
                ("can_dlc", c_ubyte),
                ("__pad",   c_ubyte),
                ("__res0",  c_ubyte),
                ("__res1",  c_ubyte),
                ("data",    c_ubyte * 8)]

class ZCAN_CANFD_FRAME(Structure):
    _fields_ = [("can_id", c_uint, 29), 
                ("err",    c_uint, 1),
                ("rtr",    c_uint, 1),
                ("eff",    c_uint, 1), 
                ("len",    c_ubyte),
                ("brs",    c_ubyte, 1),
                ("esi",    c_ubyte, 1),
                ("__res",  c_ubyte, 6),
                ("__res0", c_ubyte),
                ("__res1", c_ubyte),
                ("data",   c_ubyte * 64)]

class ZCAN_Transmit_Data(Structure):
    _fields_ = [("frame", ZCAN_CAN_FRAME), ("transmit_type", c_uint)]

class ZCAN_Receive_Data(Structure):
    _fields_  = [("frame", ZCAN_CAN_FRAME), ("timestamp", c_ulonglong)]

class ZCAN_TransmitFD_Data(Structure):
    _fields_ = [("frame", ZCAN_CANFD_FRAME), ("transmit_type", c_uint)]

class ZCAN_ReceiveFD_Data(Structure):
    _fields_ = [("frame", ZCAN_CANFD_FRAME), ("timestamp", c_ulonglong)]

class ZCAN_AUTO_TRANSMIT_OBJ(Structure):
    _fields_ = [("enable",   c_ushort),
                ("index",    c_ushort),
                ("interval", c_uint),
                ("obj",      ZCAN_Transmit_Data)]

class ZCANFD_AUTO_TRANSMIT_OBJ(Structure):
    _fields_ = [("enable",   c_ushort),
                ("index",    c_ushort),
                ("interval", c_uint),
                ("obj",      ZCAN_TransmitFD_Data)]

class ZCANFD_AUTO_TRANSMIT_OBJ_PARAM(Structure):   #auto_send delay
    _fields_ = [("indix",  c_ushort),
                ("type",   c_ushort),
                ("value",  c_uint)]

class IProperty(Structure):
    _fields_ = [("SetValue", c_void_p), 
                ("GetValue", c_void_p),
                ("GetPropertys", c_void_p)]

class ZCAN(object):
    def __init__(self):
        if platform.system() == "Windows":
            self.__dll = windll.LoadLibrary("./zlgcan.dll")
        else:
            print("No support now!")
        if self.__dll == None:
            print("DLL couldn't be loaded!")

    def OpenDevice(self, device_type, device_index, reserved):
        try:
            return self.__dll.ZCAN_OpenDevice(device_type, device_index, reserved)
        except:
            print("Exception on OpenDevice!") 
            raise

    def CloseDevice(self, device_handle):
        try:
            return self.__dll.ZCAN_CloseDevice(device_handle)
        except:
            print("Exception on CloseDevice!")
            raise

    def GetDeviceInf(self, device_handle):
        try:
            info = ZCAN_DEVICE_INFO()
            ret = self.__dll.ZCAN_GetDeviceInf(device_handle, byref(info))
            return info if ret == ZCAN_STATUS_OK else None
        except:
            print("Exception on ZCAN_GetDeviceInf")
            raise

    def DeviceOnLine(self, device_handle):
        try:
            return self.__dll.ZCAN_IsDeviceOnLine(device_handle)
        except:
            print("Exception on ZCAN_ZCAN_IsDeviceOnLine!")
            raise

    def InitCAN(self, device_handle, can_index, init_config):
        try:
            return self.__dll.ZCAN_InitCAN(device_handle, can_index, byref(init_config))
        except:
            print("Exception on ZCAN_InitCAN!")
            raise

    def StartCAN(self, chn_handle):
        try:
            return self.__dll.ZCAN_StartCAN(chn_handle)
        except:
            print("Exception on ZCAN_StartCAN!")
            raise

    def ResetCAN(self, chn_handle):
        try:
            return self.__dll.ZCAN_ResetCAN(chn_handle)
        except:
            print("Exception on ZCAN_ResetCAN!")
            raise

    def ClearBuffer(self, chn_handle):
        try:
            return self.__dll.ZCAN_ClearBuffer(chn_handle)
        except:
            print("Exception on ZCAN_ClearBuffer!")
            raise

    def ReadChannelErrInfo(self, chn_handle):
        try:
            ErrInfo = ZCAN_CHANNEL_ERR_INFO()
            ret = self.__dll.ZCAN_ReadChannelErrInfo(chn_handle, byref(ErrInfo))
            return ErrInfo if ret == ZCAN_STATUS_OK else None
        except:
            print("Exception on ZCAN_ReadChannelErrInfo!")
            raise

    def ReadChannelStatus(self, chn_handle):
        try:
            status = ZCAN_CHANNEL_STATUS()
            ret = self.__dll.ZCAN_ReadChannelStatus(chn_handle, byref(status))
            return status if ret == ZCAN_STATUS_OK else None
        except:
            print("Exception on ZCAN_ReadChannelStatus!")
            raise

    def GetReceiveNum(self, chn_handle, can_type = ZCAN_TYPE_CAN):
        try:
            return self.__dll.ZCAN_GetReceiveNum(chn_handle, can_type)
        except:
            print("Exception on ZCAN_GetReceiveNum!")
            raise

    def Transmit(self, chn_handle, std_msg, len):
        try:
            return self.__dll.ZCAN_Transmit(chn_handle, byref(std_msg), len)
        except:
            print("Exception on ZCAN_Transmit!")
            raise

    def Receive(self, chn_handle, rcv_num, wait_time = c_int(-1)):
        try:
            rcv_can_msgs = (ZCAN_Receive_Data * rcv_num)()
            ret = self.__dll.ZCAN_Receive(chn_handle, byref(rcv_can_msgs), rcv_num, wait_time)
            return rcv_can_msgs, ret
        except:
            print("Exception on ZCAN_Receive!")
            raise
    
    def TransmitFD(self, chn_handle, fd_msg, len):
        try:
            return self.__dll.ZCAN_TransmitFD(chn_handle, byref(fd_msg), len)
        except:
            print("Exception on ZCAN_TransmitFD!")
            raise
    
    def ReceiveFD(self, chn_handle, rcv_num, wait_time = c_int(-1)):
        try:
            rcv_canfd_msgs = (ZCAN_ReceiveFD_Data * rcv_num)()
            ret = self.__dll.ZCAN_ReceiveFD(chn_handle, byref(rcv_canfd_msgs), rcv_num, wait_time)
            return rcv_canfd_msgs, ret
        except:
            print("Exception on ZCAN_ReceiveFD!")
            raise

    def GetIProperty(self, device_handle):
        try:
            self.__dll.GetIProperty.restype = POINTER(IProperty)
            return self.__dll.GetIProperty(device_handle)
        except:
            print("Exception on ZCAN_GetIProperty!")
            raise

    def SetValue(self, iproperty, path, value):
        try:
            func = CFUNCTYPE(c_uint, c_char_p, c_char_p)(iproperty.contents.SetValue)
            return func(c_char_p(path.encode("utf-8")), c_char_p(value.encode("utf-8")))
        except:
            print("Exception on IProperty SetValue")
            raise
            
    def SetValue1(self, iproperty, path, value):                                              #############################
        try:
            func = CFUNCTYPE(c_uint, c_char_p, c_char_p)(iproperty.contents.SetValue)
            return func(c_char_p(path.encode("utf-8")), c_void_p(value))
        except:
            print("Exception on IProperty SetValue")
            raise
            

    def GetValue(self, iproperty, path):
        try:
            func = CFUNCTYPE(c_char_p, c_char_p)(iproperty.contents.GetValue)
            return func(c_char_p(path.encode("utf-8")))
        except:
            print("Exception on IProperty GetValue")
            raise

    def ReleaseIProperty(self, iproperty):
        try:
            return self.__dll.ReleaseIProperty(iproperty)
        except:
            print("Exception on ZCAN_ReleaseIProperty!")
            raise
###############################################################################
'''
USBCANFD-MINI Demo
'''
def canfd_start(zcanlib, device_handle, chn):
    ip = zcanlib.GetIProperty(device_handle)
    ret = zcanlib.SetValue(ip, str(chn) + "/clock", "60000000")
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d CANFD clock failed!" %(chn))
    ret = zcanlib.SetValue(ip, str(chn) + "/canfd_standard", "0")
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d CANFD standard failed!" %(chn))
    ret = zcanlib.SetValue(ip, str(chn) + "/initenal_resistance", "1")
    if ret != ZCAN_STATUS_OK:
        print("Open CH%d resistance failed!" %(chn))
    ret = zcanlib.SetValue(ip,str(chn)+"/canfd_abit_baud_rate","500000")  #设置波特率
    ret = zcanlib.SetValue(ip,str(chn)+"/canfd_dbit_baud_rate","2000000")
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d baud failed!" %(chn))      

        
    ret = zcanlib.SetValue(ip, "0/set_cn","A001")
    if ret == ZCAN_STATUS_OK:
        t = zcanlib.GetValue(ip, "0/get_cn/1")

        print(type(t)) 
        print(str(t))   
        

    chn_init_cfg = ZCAN_CHANNEL_INIT_CONFIG()
    chn_init_cfg.can_type = ZCAN_TYPE_CANFD
 #   chn_init_cfg.config.canfd.abit_timing = 101166 #1Mbps
 #   chn_init_cfg.config.canfd.dbit_timing = 101166 #1Mbps
    chn_init_cfg.config.canfd.mode        = 0
    chn_handle = zcanlib.InitCAN(device_handle, chn, chn_init_cfg)
    if chn_handle is None:
        return None
###SET filter  
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_clear","0")
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_clear failed!" %(chn))
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_mode","0")    #标准帧滤波
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_mode failed!" %(chn)) 
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_start","0")    
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_start failed!" %(chn))    
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_end","0x7FF")    
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_end failed!" %(chn))    
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_mode","1")    #扩展帧滤波
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_mode failed!" %(chn))
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_start","0")    
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_start failed!" %(chn))    
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_end","0x1FFFFFFF")    
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_end failed!" %(chn))   
    ret = zcanlib.SetValue(ip,str(chn)+"/filter_ack","0")    
    if ret != ZCAN_STATUS_OK:
        print("Set CH%d USBCANFD filter_ack failed!" %(chn))  


    zcanlib.StartCAN(chn_handle)


### Set Auto Transmit   
    ret = zcanlib.SetValue(ip,str(chn)+"/clear_auto_send","0")
    if ret != ZCAN_STATUS_OK:
        print("Clear CH%d USBCANFD AutoSend failed!" %(chn))



    path = str(chn)+"/auto_send"
    func = CFUNCTYPE(c_uint, c_char_p, c_void_p)(ip.contents.SetValue)
    ret = func(c_char_p(path.encode("utf-8")), cast(byref(AutoCAN_A), c_void_p))

    ret = func(c_char_p(path.encode("utf-8")), cast(byref(AutoCAN_B), c_void_p))
    
    path = str(chn)+"/auto_send_param"
    ret = func(c_char_p(path.encode("utf-8")), cast(byref(AutoCAN_B_delay), c_void_p))  #delay 100ms

    '''   ret = zcanlib.SetValue(ip,str(chn)+"/apply_auto_send","0")  
    if ret != ZCAN_STATUS_OK:
      print("Apply CH%d USBCANFD AutoSend failed!" %(chn))'''
 
    zcanlib.ReleaseIProperty(ip) 
    return chn_handle


if __name__ == "__main__":
    zcanlib = ZCAN() 
    testcantype =1 #0:CAN; 1:canfd
    handle = zcanlib.OpenDevice(ZCAN_USBCANFD_200U, 0,0)
    if handle == INVALID_DEVICE_HANDLE:
        print("Open CANFD Device failed!")
        exit()
    print("device handle:%d." %(handle))

    info = zcanlib.GetDeviceInf(handle)
    print("Device Information:\n%s" %(info))

    #set auto send obj
    
    
    AutoCAN_A    =  ZCAN_AUTO_TRANSMIT_OBJ()
    AutoCAN_B    =  ZCAN_AUTO_TRANSMIT_OBJ()
    AutoCAN_A.enable                    = 1  #enable
    AutoCAN_A.index                     = 0
    AutoCAN_A.interval                  = 200  #ms
    AutoCAN_A.obj.frame.can_id          = 0x100
    AutoCAN_A.obj.transmit_type         = 0
    AutoCAN_A.obj.frame.eff             = 0
    AutoCAN_A.obj.frame.rtr             = 0
    AutoCAN_A.obj.frame.can_dlc         = 8
    for j in range(AutoCAN_A.obj.frame.can_dlc):
        AutoCAN_A.obj.frame.data[j] = j
    
    AutoCAN_B.enable                    = 1  #enable
    AutoCAN_B.index                     = 1
    AutoCAN_B.interval                  = 200  #ms
    AutoCAN_B.obj.frame.can_id          = 0x300
    AutoCAN_B.obj.transmit_type         = 0
    AutoCAN_B.obj.frame.eff             = 0
    AutoCAN_B.obj.frame.rtr             = 0
    AutoCAN_B.obj.frame.can_dlc         = 8
    for j in range(AutoCAN_B.obj.frame.can_dlc):
        AutoCAN_B.obj.frame.data[j] = j

    AutoCAN_B_delay=ZCANFD_AUTO_TRANSMIT_OBJ_PARAM()
    AutoCAN_B_delay.index = AutoCAN_B.index
    AutoCAN_B_delay.type  = 1
    AutoCAN_B_delay.value = 100

    #Start CAN

    chn_handle = canfd_start(zcanlib, handle, 0)
    print("channel handle:%d." %(chn_handle))

    #Send CAN Messages
    transmit_num = 10
    msgs = (ZCAN_Transmit_Data * transmit_num)()
    for i in range(transmit_num):
        msgs[i].transmit_type = 0 #0-正常发送，2-自发自收
        msgs[i].frame.eff     = 0 #0-标准帧，1-扩展帧
        msgs[i].frame.rtr     = 0 #0-数据帧，1-远程帧
        msgs[i].frame.can_id  = i
        msgs[i].frame.can_dlc = 8
        for j in range(msgs[i].frame.can_dlc):
            msgs[i].frame.data[j] = j
    ret = zcanlib.Transmit(chn_handle, msgs, transmit_num)
    print("Tranmit Num: %d." % ret)
    
    #Send CANFD Messages
    transmit_canfd_num = 10
    canfd_msgs = (ZCAN_TransmitFD_Data * transmit_canfd_num)()
    for i in range(transmit_num):
        canfd_msgs[i].transmit_type = 0 #0-正常发送，2-自发自收
        canfd_msgs[i].frame.eff     = 0 #0-标准帧，1-扩展帧
        canfd_msgs[i].frame.rtr     = 0 #0-数据帧，1-远程帧
        canfd_msgs[i].frame.brs     = 1 #BRS 加速标志位：0不加速，1加速
        canfd_msgs[i].frame.can_id  = i
        canfd_msgs[i].frame.len     = 8
        for j in range(canfd_msgs[i].frame.len):
            canfd_msgs[i].frame.data[j] = j
    ret = zcanlib.TransmitFD(chn_handle, canfd_msgs, transmit_canfd_num)
    print("Tranmit CANFD Num: %d." % ret)

    thread=threading.Thread(target=input_thread)
    thread.start()

    #Receive Messages
    while True:
        rcv_num = zcanlib.GetReceiveNum(chn_handle, ZCAN_TYPE_CAN)
        rcv_canfd_num = zcanlib.GetReceiveNum(chn_handle, ZCAN_TYPE_CANFD)
        if rcv_num:
            print("Receive CAN message number:%d" % rcv_num)
            rcv_msg, rcv_num = zcanlib.Receive(chn_handle, rcv_num)
            for i in range(rcv_num):
                print("[%d]:timestamps:%d,type:CAN, id:%s, dlc:%d, eff:%d, rtr:%d, data:%s" %(i, rcv_msg[i].timestamp, 
                      hex(rcv_msg[i].frame.can_id), rcv_msg[i].frame.can_dlc, 
                      rcv_msg[i].frame.eff, rcv_msg[i].frame.rtr,
                      ''.join(hex(rcv_msg[i].frame.data[j])+ ' 'for j in range(rcv_msg[i].frame.can_dlc))))
        elif rcv_canfd_num:
            print("Receive CANFD message number:%d" % rcv_canfd_num)
            rcv_canfd_msgs, rcv_canfd_num = zcanlib.ReceiveFD(chn_handle, rcv_canfd_num, 1000)
            for i in range(rcv_canfd_num):
                print("[%d]:timestamp:%d,type:canfd, id:%s, len:%d, eff:%d, rtr:%d, esi:%d, brs: %d, data:%s" %(
                        i, rcv_canfd_msgs[i].timestamp, hex(rcv_canfd_msgs[i].frame.can_id), rcv_canfd_msgs[i].frame.len,
                        rcv_canfd_msgs[i].frame.eff, rcv_canfd_msgs[i].frame.rtr, 
                        rcv_canfd_msgs[i].frame.esi, rcv_canfd_msgs[i].frame.brs,
                        ''.join(hex(rcv_canfd_msgs[i].frame.data[j]) + ' ' for j in range(rcv_canfd_msgs[i].frame.len))))
        else:
            if thread.is_alive() == False:
                break
            

    #Close CAN 
    ret=zcanlib.ResetCAN(chn_handle)
    if ret==1:
        print("ResetCAN success! ")
    #Close Device
    ret=zcanlib.CloseDevice(handle)
    if ret==1:
        print("CloseDevice success! ")
