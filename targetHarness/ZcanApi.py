from asyncio.windows_events import NULL
from itertools import chain
from log import Logger
from zlgcan import *
import time
import platform
log = Logger('target.log', level='debug')
zcanlib = ZCAN() 
g_dev_handle = NULL
g_chn_num = 0
g_chn_handle = NULL

g_error_check = 10


def open_usbcan2():
    device_handle = zcanlib.OpenDevice(ZCAN_USBCANFD_200U, 0,0)
    if device_handle == INVALID_DEVICE_HANDLE:
        log("Open Device failed!")
        exit(0)
    log("device handle:%d." %(device_handle))
    return device_handle

def close_usbcan2():
    zcanlib.CloseDevice(g_dev_handle)
    return


def ReadChannelStatus(channel):
    return zcanlib.ReadChannelStatus(channel)

def open_channel(device_handle, channel):
    chn_init_cfg = ZCAN_CHANNEL_INIT_CONFIG()
    chn_init_cfg.can_type = ZCAN_TYPE_CANFD
    chn_init_cfg.config.canfd.mode = 0
    # From dev_info.json
    chn_init_cfg.config.canfd.abit_timing = 104286	# 500K
    chn_init_cfg.config.canfd.dbit_timing = 4260362	# 2M
    chn_handle = zcanlib.InitCAN(device_handle, channel, chn_init_cfg)
    if chn_handle is None:
        return None
    zcanlib.StartCAN(chn_handle)
    return chn_handle


def transmit_can( id, data, len):
    global g_error_check
    transmit_num = 1
    msgs = (ZCAN_TransmitFD_Data * transmit_num)()
    if ReadChannelStatus(g_chn_handle) != ZCAN_STATUS_OK:
        reinit()
    for i in range(transmit_num):
        msgs[i].transmit_type = 0 #Send Self
        msgs[i].frame.eff     = 0
        msgs[i].frame.rtr     = 0 #remote frame
        msgs[i].frame.can_id  = id
        msgs[i].frame.brs     = 0 # 1: fast, for examplt: 2M
        msgs[i].frame.len     = len
        for j in range(len):
            msgs[i].frame.data[j] = data[j]
    ret = zcanlib.TransmitFD(g_chn_handle, msgs, transmit_num)


    return ret

def receive_can():
    rcv_num = zcanlib.GetReceiveNum(g_chn_handle, ZCAN_TYPE_CAN)
    rcv_canfd_num = zcanlib.GetReceiveNum(g_chn_handle, ZCAN_TYPE_CANFD)
    if rcv_num:
        log("Receive CAN message number:%d" % rcv_num)
        rcv_msg, rcv_num = zcanlib.Receive(g_chn_handle, rcv_num)
        for i in range(rcv_num):
            log("[%d]:timestamps:%d,type:CAN, id:%s, dlc:%d, eff:%d, rtr:%d, data:%s" %(i, rcv_msg[i].timestamp, 
                    hex(rcv_msg[i].frame.can_id), rcv_msg[i].frame.can_dlc, 
                    rcv_msg[i].frame.eff, rcv_msg[i].frame.rtr,
                    ''.join(hex(rcv_msg[i].frame.data[j])+ ' 'for j in range(rcv_msg[i].frame.can_dlc))))
    if rcv_canfd_num:
        log("Receive CANFD message number:%d" % rcv_canfd_num)
        rcv_canfd_msgs, rcv_canfd_num = zcanlib.ReceiveFD(g_chn_handle, rcv_canfd_num, 1000)
        for i in range(rcv_canfd_num):
            log("[%d]:timestamp:%d,type:canfd, id:%s, len:%d, eff:%d, rtr:%d, esi:%d, brs: %d, data:%s" %(
                    i, rcv_canfd_msgs[i].timestamp, hex(rcv_canfd_msgs[i].frame.can_id), rcv_canfd_msgs[i].frame.len,
                    rcv_canfd_msgs[i].frame.eff, rcv_canfd_msgs[i].frame.rtr, 
                    rcv_canfd_msgs[i].frame.esi, rcv_canfd_msgs[i].frame.brs,
                    ''.join(hex(rcv_canfd_msgs[i].frame.data[j]) + ' ' for j in range(rcv_canfd_msgs[i].frame.len))))

def receive_can_loop(chn_handle):
    while True:
        receive_can()


def reinit():
    global g_dev_handle
    global g_chn_handle
    log("reinit zcan...")
    close_usbcan2()
    g_dev_handle = open_usbcan2()
    g_chn_handle = open_channel(g_dev_handle, g_chn_num)
    log("re-init zcan fin")

def init(argv):
    global g_dev_handle
    global g_chn_handle
    log("init zcan...")
    g_dev_handle = open_usbcan2()
    g_chn_handle = open_channel(g_dev_handle, g_chn_num)
    log("init zcan fin")

if __name__ == "__main__":

    # dll support
    if platform.python_version()>='3.8.0':
        import os
        os.add_dll_directory(os.getcwd())

    # open device and channel 0
    dev_handle = open_usbcan2()
    chn_handle = open_channel(dev_handle, 0)
    #chn1_handle = open_channel(dev_handle, 1)
    log("channel 0 handle:%d." %(chn_handle))
    data = [0,1,2,3,4,5,6,0xFF]
    for i in range(2):
        transmit_can(chn_handle, 0, 0x100, data, 6)
        transmit_can(chn_handle, 1, 0x12345678, data, 8)
        data[0] = data[0] + 1
        time.sleep(0.1)

    zcanlib.ClearBuffer(chn_handle)
    time.sleep(3)
    receive_can_loop(chn_handle)

    zcanlib.ResetCAN(chn_handle)
    zcanlib.CloseDevice(dev_handle)
    print("Finished")