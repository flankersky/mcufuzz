#!/usr/bin/python
# -*- coding: latin-1 -*-
# --------------------------------------------------------------------------------
# @Title: Python example demonstrating various functions of the TRACE32 remote API
# @Description:
#  After establishing a remote connection with TRACE32 PowerView a menu offers
#  various API commands for selection. For accessing real HW the data memory
#  location can be specified by <hexaddr>.
#
#  Syntax:   t32apimenu.py [--node <ip-addr>] [--port <num>] [--address <hexaddr>]
#
#  Example:  t32apimenu.py --node localhost --port 20000 --address 0x400C000
#
#  TRACE32's configuration file "config.t32" has to contain these lines:
#    RCL=NETASSIST
#    PORT=20000
#  The port value may be changed but has to match with the port number
#  used with this python script.
#
#
# @Keywords: python
# @Author: WBA
# @Copyright: (C) 1989-2015 Lauterbach GmbH, licensed for use with TRACE32(R) only
# --------------------------------------------------------------------------------
# $Id: t32apimenu.py 116756 2020-01-27 07:42:44Z jvogl $
#

import sys, getopt, time, ctypes, array, os, platform
from ctypes import *
from tkinter.messagebox import RETRY
from log import Logger


log = Logger('target.log', level='debug')
# auto-detect the correct library
if (platform.system()=='Windows') or (platform.system()[0:6]=='CYGWIN') :
  if ctypes.sizeof(ctypes.c_voidp)==4:
    # WINDOWS 32bit
    t32api = ctypes.CDLL("./t32api.dll")
    # alternative using windows DLL search order:
#   t32api = ctypes.cdll.t32api
  else:
    # WINDOWS 64bit
    t32api = ctypes.CDLL("./t32api64.dll")
    # alternative using windows DLL search order:
#   t32api = ctypes.cdll.t32api64
elif platform.system()=='Darwin' :
  # Mac OS X
  t32api = ctypes.CDLL("./t32api.dylib")
else :
  if ctypes.sizeof(ctypes.c_voidp)==4:
    # Linux 32bit
    t32api = ctypes.CDLL("./t32api.so")
  else:
    # Linux 64bit
    t32api = ctypes.CDLL("./t32api64.so")

T32_OK = 0
T32_MEMORY_ACCESS_DATA=0
sel = '  '
address = 0xffffffff
pcval = c_long(0xffffffff)
wp = array.array('i', list(range(512)))
wpbuffer = (c_ulong * 256).from_buffer(wp)
wpbuffer[0]=0xcafefeca
rw = array.array('i', list(range(4)))
rwbuffer = (c_ulong * 2).from_buffer(rw)
rwbuffer[0] = 0xcafefeca
rwbuffer[1] = 0xbabebeba
ui32val = array.array('i', list(range(16)))
pui32val = (c_ulong * 8).from_buffer(ui32val)
ui16val = array.array('i', list(range(64)))
pui16val = (c_ushort * 32).from_buffer(ui16val)
EXIT_SUCCESS=0
EXIT_FAILURE=1
T32_MEMORY_ACCESS_PROGRAM=0x1
retval = EXIT_SUCCESS
PROGNAME=os.path.basename(__file__)


buf = array.array('i', list(range(65536)))
pbuf = (c_uint32 * 16384).from_buffer(buf)
for i in range (0,16384):
  pbuf[i] = 0xcccccccc


def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()

# [API]: https://www2.lauterbach.com/pdf/api_remote_c.pdf

def init(argv):
  node = 'localhost'
  port = '20000'

  string=create_string_buffer(50)
  string='Data.DUMP D:0x1000      '
  address = '0xffffffff'
   ### Debugger operation
  t32api.T32_Config(b"NODE=",node.encode('latin-1'))
  if t32api.T32_Config(b"PORT=",port.encode('latin-1'))!=T32_OK:
    log(' Invalid port number \'%s\' specified.'%(port))
    sys.exit(EXIT_FAILURE)
  t32api.T32_Config(b"PACKLEN=",b"1024")
  log("")
  log(' Connecting...')
  for i in range (1, 3):
    if t32api.T32_Init()==T32_OK:
      if t32api.T32_Attach(1)==T32_OK:
        log(' Successfully established a remote connection with TRACE32 PowerView.')
        break
      else :
        if i==1:
          log(' Failed once to established a remote connection with TRACE32 PowerView.')
          t32api.T32_Exit()
        elif i==2 :
          log(' Failed twice to established a remote connection with TRACE32 PowerView.')
          log(' Terminating ...')
          sys.exit(EXIT_FAILURE)
    else :
      if i==1:
        log(' Failed once to initialize a remote connection with TRACE32 PowerView.')
        t32api.T32_Exit()
      elif i==2 :
        log(' Failed twice to initialize a remote connection with TRACE32 PowerView.')
        log(' Terminating ...')
        sys.exit(EXIT_FAILURE)
  systemstate =c_uint(0)

  retval = t32api.T32_EvalGet(pui32val)
  if ((retval != T32_OK) or (pui32val[0] == 0)) :    #/* marginal setup in case of */
    t32api.T32_Cmd(b"WINPOS 40% 0 60% 40% , , APIWin4")  #/* real HW or eval-failure   */
    t32api.T32_Cmd(b"Data.List")
    t32api.T32_Cmd(b"WINPOS 40% 40% 60% 40% , , APIWin5")
    t32api.T32_Cmd(string.encode('latin-1'))
    if (address == 0xffffffff) :
      t32api.T32_Cmd(b"PRINT \042Real hardware is accessed but no address\042")
      t32api.T32_Cmd(b"PRINT \042for data access has been specified,\042")
      t32api.T32_Cmd(b"PRINT \042Read/WriteMemory will access D:0x1000\042")
      t32api.T32_Cmd(b"PRINT")
      log("")
      log("")
      log(" Syntax: %s.py [--node <name_or_IP>] [--port <num>] [-address <hexaddr>]" %( PROGNAME))
      log(" Example: %s.py  --node localhost   --port 20000  --address 0x400C000\n" % (PROGNAME))
      log("")
      log(" Hexaddress is used by Read/WriteMemory if real hardware is accessed.")
      log("")
      log("")
      log(' Real hardware is accessed but no address for data access')
      log(' has been specified, Read/WriteMemory will access D:0x1000')
      address = 0x1000
  else:
    t32api.T32_Cmd(b"SYStem.Up")
  t32api.T32_Cmd(b"Break.List")
  t32api.T32_Cmd(b"break")
  log('Try to read Register R1: 0x%x ' %(read_register_by_name("R1")))



def ping():
    return t32api.T32_Ping()
def stop():
    return t32api.T32_Stop()

def clearEtmData():
    t32api.T32_Cmd()
def t32break():
    t32api.T32_Break()

def t32go():
    t32api.T32_Go()


def t32cmd(cmd):
  t32api.T32_Cmd(cmd);



def t32state():
    state =c_uint(-1)
    retval = t32api.T32_GetState(byref(state))
    if (retval == T32_OK) :
        return state.value #/*safeguard the little trick*/
    else:
        return -1

def get_symbol_address(symbol_name):

    addr = ctypes.c_uint32(0)
    size = ctypes.c_uint32(0)
    access = ctypes.c_uint32(0)

    ret = t32api.T32_GetSymbol(symbol_name.encode(),
                            ctypes.byref(addr),
                            ctypes.byref(size),
                            ctypes.byref(access))

    #print("get_symbol_address ret:%x"%ret)
    if ret == T32_OK:
        return addr.value
    else:
        return -1


# def t32WriteMem(addr, data, len):
#     t32api.T32_WriteMemory(addr,0xC0, data, len)
def writeMem(aAddr, aNumBytes, aData, aType=1):
    if aType == 1:
        pData = (ctypes.c_int8  * len(aData))(*aData)
    elif aType == 2:
        pData = (ctypes.c_int16 * len(aData))(*aData)
    elif aType == 4:
        pData = (ctypes.c_int32 * len(aData))(*aData)
    else:
        pData = (ctypes.c_int64 * len(aData))(*aData)

    retVal = t32api.T32_WriteMemory(ctypes.c_uint32(aAddr), 0x20, pData, ctypes.c_uint32(aNumBytes))
    if (retVal != 0):
        print('Error in T32_WriteMemory', hex(aAddr))
    return retVal


def coverageAdd():
    t32api.T32_Cmd(b"COVerage.ADD")


def read_register_by_name(name):
    upper = ctypes.c_uint32(0)
    lower = ctypes.c_uint32(0)
    ret = t32api.T32_ReadRegisterByName(name.encode(),
                                     ctypes.byref(lower),
                                     ctypes.byref(upper))
    if ret == T32_OK:
        return upper.value * 2**32 + lower.value
    else:
        return -1

def getEtm():
    global pbuf
    states = ["off", "armed", "triggered", "breaked"]
    total = c_int()
    min = c_int()
    max = c_int()

    systemstate =c_uint(0)
    
    retval = t32api.T32_GetTraceState(0, byref(systemstate), byref(total), byref(min), byref(max))

    if (retval == T32_OK) :
        systemstate.value=systemstate.value & 0x3 #/*safeguard the little trick*/
    
    num=max.value - min.value + 1
    if ((num > 0) and (systemstate.value == 0)) :
        retval = t32api.T32_ReadTrace(0, max.value - num + 1, num, 0x10, pbuf)#  4 bytes are written to 'buf' for
        
        if (retval != T32_OK) : 
            log("T32_ReadTrace return error:%d"%(retval))

    return num, pbuf

def init_trace32(argv):
  init(sys.argv[1:])

##############################################################################

if __name__ == "__main__":

  init(sys.argv[1:])
  t32go()
  #sleep？
  time.sleep(5)
  t32break()
  g_Mem_inject_flag_addr = get_symbol_address("Mem_inject_flag")
  print("%x"%g_Mem_inject_flag_addr)
  val = [1]
  writeMem(0x345ACC4C, 1, val, 1)
  # getEtm()