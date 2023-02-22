"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2019-10-16

   Requires:                       
       Python 2.7, 3
   Generate a single given lenght pulse
"""
import csv
from ctypes import *
import time
from datetime import datetime

import numpy
import schedule as schedule
from matplotlib import pyplot as plt

from dwfconstants import *
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
channel = c_int(0)
pulse = 510e-9
Vwrite = 0.3
Vread = 0.1
Rs = 5000
dif = 10000
measure_second = 10 # วัดทุกๆ กี่วินาที นับจำนวนการวัด
break_time = 10
nSamples = 3000
measure = True
fist = True
value = True
one = True
day = 24
hr = 60
minute = 60
target_count = day*hr*minute / measure_second
current_count = 0
timeout_write = 1000
current_write = 0
sleep_in = 0.1
sleep_out = 2

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

#open device
print("Opening first device...")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))


if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

# the device will be configured only when calling FDwfAnalogOutConfigure
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0))

dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutIdleSet(hdwf, channel, DwfAnalogOutIdleOffset)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, funcDC)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel, AnalogOutNodeCarrier, c_double(0)) # low frequency
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel, AnalogOutNodeCarrier, c_double(3.3))
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, channel, AnalogOutNodeCarrier, c_double(0.3))

dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(1)) #Set range for all channels
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(1000000))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(nSamples))

# dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0xFFFF))
# dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0001))


print("Generating pulse")
dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))

time.sleep(sleep_out)

print("Starting acquisition...")

info = ['Date/Time', 'ValueRm', 'ValueVa']
with open('/Users/Admin/PycharmProjects/WaveFormsSDK1/FormValue_Write.csv', 'a+', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(info)

while measure:
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))
    sts = c_int()
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value:
            break
        time.sleep(sleep_in)

    rg = (c_double * nSamples)()
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), rg, len(rg))  # get channel 1 data

    Va = sum(rg) / len(rg)
    print("Va: " + str(Va) + "V")

    Rm = ((Vwrite * Rs) / Va) - Rs
    print("Rm: " + str(Rm))

    now = datetime.today()
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    info2 = [str(dt), float(Rm), float(Va)]

    with open('/Users/Admin/PycharmProjects/WaveFormsSDK1/FormValue_Write.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(info2)

    if fist:
        Rm_old = Rm
        fist = False
        print('R_fist: ' + str(Rm))
        continue

    if abs(Rm_old - Rm) < dif:
        print('R_last: ', + Rm)
        measure = False
    else:
        Rm_old = Rm
        print('R_now: ' + str(Rm))
        # time.sleep(measure_second)

    if (current_write == timeout_write):
        print('Write timeout!')
        break
    else:
        current_write = current_write + 1

dwf.FDwfAnalogOutNodeOffsetSet(hdwf, channel, AnalogOutNodeCarrier, c_double(0))
dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))
time.sleep(sleep_out)

Data = ['Date/Time', 'ValueR_read', 'ValueVa_read']
with open('/Users/Admin/PycharmProjects/WaveFormsSDK1/FormValue_Read.csv', 'a+', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(Data)

while value:
    dwf.FDwfAnalogOutNodeOffsetSet(hdwf, channel, AnalogOutNodeCarrier, c_double(Vread))
    dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))
    time.sleep(sleep_out)

    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))
    sts = c_int()
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value:
            break
        time.sleep(sleep_in)

    dwf.FDwfAnalogOutNodeOffsetSet(hdwf, channel, AnalogOutNodeCarrier, c_double(0))
    dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))
    time.sleep(sleep_out)

    rg = (c_double * nSamples)()
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), rg, len(rg))  # get channel 1 data

    Va_read = sum(rg) / len(rg)
    print("Va_read: " + str(Va_read) + "V")

    R_read = ((Vread * Rs) / Va_read) - Rs
    print("R_read: " + str(R_read))

    now = datetime.today()
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    Data2 = [str(dt), float(R_read), float(Va_read)]

    with open('/Users/Admin/PycharmProjects/WaveFormsSDK1/FormValue_Read.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(Data2)

    if (current_count == target_count):
        break
    else:
        current_count = current_count + 1

    time.sleep(measure_second - sleep_out - sleep_out - sleep_in)

# dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000))
# dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0xFFFF))
dwf.FDwfDeviceClose(hdwf)
