from asyncio.windows_events import NULL
from re import S
from log import Logger
#from gettext import dpgettext
import os,sys
import win32pipe
import win32file
import winerror,pywintypes
import time
import sys, getopt, time, ctypes, array, os, platform


os.chdir('D:\\workspace\\McuFuzz\\targetHarness')
import T32Api,ZcanApi
from ctypes import *
from struct import *

PIPE_ETM = r'\\.\pipe\DataPipe'
PIPE_CTRL = r'\\.\pipe\CmdPipe'

control_pipe = NULL
etm_pipe = NULL


ETM_PIPE_BUFFER_SIZE = 65536
FILE_PATH_LEN = 256
log = Logger('target.log', level='debug')
rawcov_path = os.path.join(os.getcwd(), 'rawcov.txt')
rawCover = open(rawcov_path,"w")

CMD_INIT = 0xdead1001
CMD_GO = 0xdead1002
CMD_SUSPEND = 0xdead1002


STATUS_READY = 0xbeef0221
STATUS_SUSPEND = 0xbeef0222
STATUS_LOOP1DONE = 0xbeef0223
STATUS_ERROR = 0xbeef022f


'''

|  main  |                   | target |

         ->---- CMD_GO--------
         ->     file_path----
'''

CtrlBUFSIZE=512
DataBUFSIZE=65536

def init_trace32(argv):
    T32Api.init(argv)

def init_zcanpro(argv):
    ZcanApi.init(argv)

def t32_startTarget(argv): 
    #T32Api.
    return

def t32_break(argv):
    T32Api.t32break()
def t32_go(argv):
    T32Api.t32go()

def t32_stopTarget(argv):
    T32Api.stop()

def t32_getstate():
    return T32Api.t32state()



def t32_getEtmData(argv):
    arr = []
    num, pbuf = T32Api.getEtm()
    last_pc = 0
    #de duplicate
    log("t32_getEtmData:%d"%(num))
    for i in range(0,num):
        if pbuf[i] == 0 or pbuf[i] == last_pc:
            continue
        last_pc = pbuf[i]
        arr.append(pbuf[i])
    return arr


def t32_clearEtmData(argv):
    #t32api.T32_Cmd
    T32Api.clearEtmData()

def t32_coverageAdd():
    T32Api.coverageAdd()


def zcan_sendCanData(argv):
    return

def send_cmd(cmd):
    log("send_cmd %x"%(cmd))
    try:
        rc = win32file.WriteFile(control_pipe, cmd.to_bytes(4, byteorder="big", signed=False))
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        log("send_cmd:",e )


def send_payload(payload):
    log("send_payload %s"%(payload))
    try:
        rc = win32file.WriteFile(control_pipe, payload.encode())
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        log("send_payload:",e )



def send_etm_count(count):
    try:
        rc = win32file.WriteFile(control_pipe, count.to_bytes(4, byteorder="big", signed=False))
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        log("send_payload:",e )


def send_etm_data(PCs):
    pcBytes = bytes()
    for pc in PCs:
        pcBytes += pc.to_bytes(4, byteorder='little')

    try:
        rc = win32file.WriteFile(etm_pipe, pcBytes)
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        log("send_payload:",e )




def wait_cmd():

    #PeekNamedPipe   
    #log("wait_cmd...")
    while True:
        try:
            result, data = win32file.ReadFile(control_pipe,4, None)
            #while result == winerror.ERROR_MORE_DATA: 
            #log("ReadFile result: %x"%(result))

            if result != 0 or data is None or len(data) == 0:
                #time.sleep(0.1)
                log("try to read again...")
                continue
            else:
                return int.from_bytes(data, byteorder='big', signed=False)
        except pywintypes.error as e:
            if e.args[0] == 232:
                log("read none,retry..." )
                #time.sleep(0.1)
                continue
            else:
                raise
def waitFilePath():
    while True:
        try:
            result, data = win32file.ReadFile(control_pipe,FILE_PATH_LEN, None)
            #while result == winerror.ERROR_MORE_DATA: 
            #log("result: %x %s"%(result, data.decode('ascii')))

            if result != 0 or data is None or len(data) == 0:
                #time.sleep(0.1)
                log("try to read again...")
                continue
            else:
                return data.decode('utf-8')
        except pywintypes.error as e:
            if e.args[0] == 232:
                log("read none,retry..." )
                #time.sleep(0.1)
                continue
            else:
                raise


def sendEtmData(msg):
    log("sendEtmData...")
    try:
        win32file.WriteFile(etm_pipe, msg.encode())
        #time.sleep(0.1)
    except Exception as e:
        log(e)

def zcan_send(filename):
    # Open it for reading.
    log("zcan_send:%s"%(filename))
    fhandle = win32file.CreateFile(filename, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, 0, None)
    log("zcan_send:0000")
    #rc, canid_b = win32file.ReadFile(fhandle, 2, None)
    rc, data = win32file.ReadFile(fhandle, 64, None)
    log("zcan_send:1111")
    if rc == winerror.ERROR_MORE_DATA:
        log("There more data in ", filename)

    fhandle.Close()


    ret = ZcanApi.transmit_can(0x222, data, len(data))
    log("zcan_send transmit_can:%d"%(ret))

def modHeartBeat():
    T32Api.t32cmd(b"(*(part_list.part[0])).state = 131")
def main(argv):
    global control_pipe
    global etm_pipe

    while True:
        try:
            control_pipe = win32file.CreateFile(PIPE_CTRL,
                                        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                        win32file.FILE_SHARE_WRITE, None,
                                        win32file.OPEN_EXISTING, 0, None)

            etm_pipe = win32file.CreateFile(PIPE_ETM,
                                        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                        win32file.FILE_SHARE_WRITE, None,
                                        win32file.OPEN_EXISTING, 0, None)
            break
        except pywintypes.error as e:
            if e.args[0] == 2:
                log("Sever not setup, retry...")
                #time.sleep(0.1)
                continue
            else:
                log("Createfile unkown error:",e)

    #create_etm_server()
    log("connect sucess")
    try:
        init_trace32(argv)
        init_zcanpro(argv)
    except Exception as e:
        log("Except ", e)
        win32file.CloseHandle(control_pipe)
        win32file.CloseHandle(etm_pipe)
        exit()

    t32_break(None)
    while(1):
        #time.sleep(0.1)
        send_cmd(STATUS_READY)
        cmd = wait_cmd()
        if  cmd == CMD_GO:
            log("Get CMD_GO")
            fp = waitFilePath()
            modHeartBeat()
            t32_go(None)
            zcan_send(fp)
            log("zcan_send return")
            #sleep？
            time.sleep(0.01)

            if t32_getstate() == 2:
                log("t32_getstate stopped")
                break
            t32_break(None)

            log("t32_getEtmData")
            pcArr = t32_getEtmData(None)
            rawCover.write("#NUM:0x%x\n"%(len(pcArr)))
            for pc in pcArr:
                rawCover.write("0x%x\n"%(pc))
            
            rawCover.flush()
            rawCover.write("#NUM:0x%x END...\n"%(len(pcArr)))

            log("t32_getEtmData pc count:%d"%(len(pcArr)))
            ####################################################
            ##############以下顺序不可调换#######################
            send_cmd(STATUS_LOOP1DONE)
            send_etm_count(len(pcArr))
            if len(pcArr) > 0:
                send_etm_data(pcArr)
            ####################################################
        else:
            log("Invalid command:%x"%(cmd))
    return

if __name__ == "__main__":
    main(sys.argv[1:])
    #zcan_send("s4.bin0x43c")