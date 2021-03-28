import DataGui as gui
import numpy as np
import time
import sys
from DataHandler import DataHandlerClass
from EskfGlueCode import EskfGlue
import GS_timing as gt

def lowpriority():
    """ Set the priority of the process to below-normal."""

    import sys
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        import win32api,win32process,win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        import os

        os.nice(1)

USE_GUI = True
if __name__ == '__main__':
    lowpriority()
    guiCaller = gui.DataGui()
    dataHandler = DataHandlerClass("/dev/ttyACM0", 115200)
    dataHandler.flush()

    eskfProcessor = EskfGlue()
    # dataGetter.init()
    # guiCaller.callLoop()
    i = 0
    try:
        while(True):
            i += 1
            i %= 1000
            # time.sleep(1)
            startTime = gt.millis()
            meas = dataHandler.readFromPort()
            if(meas == None):
                print("MEAS RETURN NONE")
                continue
            #Process ESKF
            # print("PROC ESKF")
            eskfProcessor.processESKF(meas)
            # print(gt.millis()-startTime)
            #Update GUI
            pos = eskfProcessor.getPosition()
            quat = eskfProcessor.getQuaternion()
            render = False
            if(USE_GUI and i % 20 == 0):
                print("GUI START")
                render = True
                print("GUI END")
            guiCaller.updateGUI(pos, [1, 2, 3], quat, render=render)
    except KeyboardInterrupt:
        print ('Interrupted')
        sys.exit(0)

# theta = -4.0 * np.pi + 4.0 * np.pi* i / 100
# z = -2.0 + 4 *(i/100.0)
# r = z**2 + 1.0
# x = r * np.sin(theta)
# y = r * np.cos(theta)

# startNonGuiThread()
# guiCaller.callLoop(i)
# guiCaller.insertPointAndAnimate(x, y, z)
# guiCaller.insertPointTry(i)
# guiCaller.trialCheckHowMuchTime()
