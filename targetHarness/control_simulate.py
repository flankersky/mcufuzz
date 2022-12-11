from asyncio.windows_events import NULL
from itertools import count
from logging import exception
#from gettext import dpgettext
import os,sys
import win32pipe
import win32file,pywintypes
import time
import sys, getopt, time, ctypes, array, os, platform
import T32Api,ZcanApi
from ctypes import *



PIPE_ETM = r'\\.\pipe\DataPipe'
PIPE_CTRL = r'\\.\pipe\CmdPipe'

CTRL_PIPE_BUFFER_SIZE = 128
DATA_PIPE_BUFFER_SIZE = 65536
#ETM_PIPE_BUFFER_SIZE = 65536
FILE_PATH_LEN = 256

###################
# cmd and status 
CMD_INIT = 0xdead1001
CMD_GO = 0xdead1002
CMD_SUSPEND = 0xdead1002


STATUS_READY = 0xbeef0221
STATUS_SUSPEND = 0xbeef0222
STATUS_LOOP1DONE = 0xbeef0223
STATUS_ERROR = 0xbeef022f

#######################
control_pipe = NULL
etm_pipe = NULL

def send_cmd(cmd):
    print("send_cmd %x"%(cmd))
    try:
        #rc = win32file.WriteFile(control_pipe, cmd.to_bytes(4,byteorder = 'big'))
        #print(cmd.to_bytes(4, byteorder="little", signed=False))
        rc = win32file.WriteFile(control_pipe, cmd.to_bytes(4, byteorder="big", signed=False))
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        print("send_cmd:",e )


def send_payload(payload):
    print("send_payload %s"%(payload))
    try:
        #rc = win32file.WriteFile(control_pipe, cmd.to_bytes(4,byteorder = 'big'))
        #print(cmd.to_bytes(4, byteorder="little", signed=False))
        rc = win32file.WriteFile(control_pipe, payload.encode())
        #print("send cmd rc:%x"%(rc))
    except Exception as e:
        print("send_payload:",e )



def wait_status():
    print("wait_status...")
    

    while True:
        try:
            result, data = win32file.ReadFile(control_pipe,4, None)
            #while result == winerror.ERROR_MORE_DATA: 
            print("result: %x,"%(result), data)

            if result != 0 or data is None or len(data) == 0:
                time.sleep(1)
                print("try to read again...")
                continue
            else:
                return int.from_bytes(data, byteorder='big', signed=False)
        except pywintypes.error as e:
            if e.args[0] == 232:
                print("read none,retry..." )
                time.sleep(1)
                continue
            else:
                raise
def wait_etm_count():
    print("wait_status...")
    

    while True:
        try:
            result, data = win32file.ReadFile(control_pipe,4, None)
            #while result == winerror.ERROR_MORE_DATA: 
            print("result: %x,"%(result), data)

            if result != 0 or data is None or len(data) == 0:
                time.sleep(1)
                print("try to read again...")
                continue
            else:
                return int.from_bytes(data, byteorder='big', signed=False)
        except pywintypes.error as e:
            if e.args[0] == 232:
                print("read none,retry..." )
                time.sleep(1)
                continue
            else:
                raise
def wait_etm_data():
    print("wait_etm...")
    etm =  win32file.ReadFile(etm_pipe,DATA_PIPE_BUFFER_SIZE, None)
    print("Receive ETM: %d", len(etm))



def init_child():
    pass



def init_pipes():
    global control_pipe
    global etm_pipe
    print("init_pipes...")
    try:
        control_pipe = win32pipe.CreateNamedPipe(PIPE_CTRL,
                                            win32pipe.PIPE_ACCESS_DUPLEX,
                                            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_NOWAIT | win32pipe.PIPE_READMODE_BYTE,
                                            win32pipe.PIPE_UNLIMITED_INSTANCES,
                                            CTRL_PIPE_BUFFER_SIZE,
                                            CTRL_PIPE_BUFFER_SIZE, 500, None)
        
        etm_pipe = win32pipe.CreateNamedPipe(PIPE_ETM,
                                            win32pipe.PIPE_ACCESS_DUPLEX,
                                            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_NOWAIT | win32pipe.PIPE_READMODE_BYTE,
                                            win32pipe.PIPE_UNLIMITED_INSTANCES,
                                            DATA_PIPE_BUFFER_SIZE,
                                            DATA_PIPE_BUFFER_SIZE, 500, None)
    except Exception as e:
        print("init_pipes:", e)    

def connect_pipes():
    while True:
        try:
            win32pipe.ConnectNamedPipe(control_pipe, None)
            win32pipe.ConnectNamedPipe(etm_pipe, None)
            print("connect pipe sucess")

            #data = win32file.ReadFile(named_pipe, PIPE_BUFFER_SIZE, None)
            # if data is None or len(data) < 2:
            #     continue
            #print 'receive msg:', data
            break
        except pywintypes.error as e:
            if e.args[0] == 536:
                time.sleep(1)
                print("connect_pipes try again:")
                continue
        except BaseException as e:
            print("connect_pipes:", e)
            continue    


def close_pipes():
    try:
        win32pipe.DisconnectNamedPipe(control_pipe)
        win32pipe.DisconnectNamedPipe(etm_pipe)
        win32file.CloseHandle(control_pipe)
        win32file.CloseHandle(etm_pipe)
    except BaseException as e:
        print("close_pipes:", e)

def re_init_pipes():
    close_pipes()
    init_pipes()
    connect_pipes()
def main(argv):
    # global control_pipe
    # global etm_pipe
    print("creating named pipe")

    init_pipes()
    print("try to connect pipe")
    connect_pipes()

    while True:

        try:
            time.sleep(1)
            status = wait_status()
            if status == STATUS_READY:
                print("Receive STATUS_READY " )
            else:
                print("Receive unknown status:%x "%(status) )
                exit()

            send_cmd(CMD_GO)
            send_payload("seed.txt")


            status = wait_status()
            if status == STATUS_LOOP1DONE:
                print("Receive STATUS_LOOP1DONE " )
            else:
                print("Receive unknown status:%x "%(status) )
                exit()

            
            count = wait_etm_count()
            print("wait_etm_count ",count )

            wait_etm_data()
            time.sleep(3)
        except KeyboardInterrupt:
            print("exit:")
            exit()
        except pywintypes.error as e:
            if e.args[0] == 109:
                print("re_init_pipes:",e)
                re_init_pipes()

    try:
        win32pipe.DisconnectNamedPipe(control_pipe)
        win32pipe.DisconnectNamedPipe(etm_pipe)
    except:
        pass



    #create_etm_server()
    print("handshake sucess")



    return

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    