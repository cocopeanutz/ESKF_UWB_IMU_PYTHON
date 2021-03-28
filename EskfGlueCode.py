from ctypes import *
import os
from DataHandler import MeasData
import numpy as np
import GS_timing as gt

DIRECTORY = "/home/edo/SIPA/myProjects/ErrorStateKalmanFilter"
DYNAMIC_LIBRARY_LOCATION = "/home/edo/SIPA/myProjects/ErrorStateKalmanFilter/libESKF.so"
PREVIOUS_TIME_MEASUREMENT = None


os.chdir(DIRECTORY)
eskfLib = cdll.LoadLibrary(DYNAMIC_LIBRARY_LOCATION)
eskfLib.glueCodeCreateESKF.restype = c_void_p
eskfLib.glueCodeGetPosition.argtypes = [POINTER(c_float * 3), c_void_p]
# eskfLib.glueCodeGetPosition.restype = (c_float * 3)
eskfLib.glueCodeGetVelocity.argtypes = [POINTER(c_float * 3), c_void_p]
eskfLib.glueCodeGetQuaternion.argtypes = [POINTER(c_float * 4), c_void_p]
# eskfLib.glueCodeGetVelocity.restype = (c_float * 3)
# eskfLib.glueCodeGetQuaternion.restype = (c_float * 4)

#eskf state
#-> covariances -> numpy n x n dimensional array
#state array float x 9
#covariance drift update?

class EskfGlue:
    def __init__(self):
        self.eskfPos = (c_float * 3)(0, 0, 0)
        self.eskfVel = (c_float * 3)(0, 0, 0)
        self.eskfQuat = (c_float * 4)(0, 0, 0, 0)
        self.eskfPtr = eskfLib.glueCodeCreateESKF()
        self.lastUWBData = None
    def processESKF(self, meas):
        global PREVIOUS_TIME_MEASUREMENT
        if (meas.rawAAvail == 1):
            if(PREVIOUS_TIME_MEASUREMENT == None):
                deltaTime = 0.001
                PREVIOUS_TIME_MEASUREMENT = gt.millis()
            else:
                now = gt.millis()
                deltaTime = (now-PREVIOUS_TIME_MEASUREMENT)/1000
                PREVIOUS_TIME_MEASUREMENT = now
            print("deltaTime:", deltaTime)
            self.predictEskf    (meas, deltaTime)
            self.updateEskfAcc  (meas)
        if(meas.rawMAvail == 1):
            # self.updateEskfMagn(meas)
            pass
        # Because there is no flag for new uwb data, so instead, just see if the reading changes
        if(meas.rawPosi !=0):
            if(self.lastUWBData != meas.rawPosi):
                self.lastUWBData = meas.rawPosi
                self.updateEskfUwb(meas)

    def predictEskf(self, meas, deltaTime):
        deltaTime = c_float(deltaTime)
        accMeas  = (c_float * 3)(meas.rawAx, meas.rawAy, meas.rawAz)
        # magnMeas = (c_float * 3)(meas.rawMx, meas.rawMy, meas.rawMz)
        gyroMeas = (c_float * 3)(meas.rawWx, meas.rawWy, meas.rawWz)
        eskfLib.glueCodePredictESKF(self.eskfPtr, accMeas, gyroMeas, deltaTime)

    # def updateEskfImu(self, meas):
    #     accMeas  = (c_float * 3)(meas.rawAx, meas.rawAy, meas.rawAz)
    #     magnMeas = (c_float * 3)(meas.rawMx, meas.rawMy, meas.rawMz)
    #     eskfLib.glueCodeUpdateEskfImu(self.eskfPtr, accMeas, magnMeas)

    def updateEskfAcc(self, meas):
        accMeas  = (c_float * 3)(meas.rawAx, meas.rawAy, meas.rawAz)
        eskfLib.glueCodeUpdateEskfAccelerometer(self.eskfPtr, accMeas)

    def updateEskfMagn(self, meas):
        magnMeas = (c_float * 3)(meas.rawMx, meas.rawMy, meas.rawMz)
        eskfLib.glueCodeUpdateEskfMagnetometer(self.eskfPtr, magnMeas)

    def updateEskfUwb(self, meas):
        uwbPos  = (c_float * 3)(meas.rawPosi, meas.rawPosj, meas.rawPosk)
        eskfLib.glueCodeUpdateEskfUwb(self.eskfPtr, uwbPos)







    def getPosition(self):
        retPtr = cast(self.eskfPos, POINTER(c_float * 3))
        eskfLib.glueCodeGetPosition(retPtr, self.eskfPtr)
        return np.array([*self.eskfPos])

    def getVelocity(self):
        retPtr = cast(self.eskfVel, POINTER(c_float * 3))
        vel = eskfLib.glueCodeGetVelocity(retPtr, self.eskfPtr)
        return np.array([*self.eskfVel])

    def getQuaternion(self):
        retPtr = cast(self.eskfQuat, POINTER(c_float * 4))
        quaternion = eskfLib.glueCodeGetQuaternion(retPtr, self.eskfPtr)
        return np.array([*self.eskfQuat])
    # def numpyArrayToCPPArray(numpyArray, *dimLength):
    #     x = dimLength[0]
    #     y = dimLength[1]
    #     if(len(dimLength) == 1):
    #         retArray = (array, (c_float(4) * x)
    #         for i in range(dimLength[0]):
    #             retArray[i] = numpyArray[i]
    #         return retArray
    #     else:
    #         retArray = (array, (c_float(4) * x) * y)
    #         for i in range(dimLength[0]):
    #             for j in range(dimLength[1]):
    #                 retArray[i][j] = numpyArray[i][j]
    #         return retArray

    # def cppArrayToNumpyArray(cppArray, *dimLength):
    #     if(len(dimLength) == 1):
    #         retArray = numpy.createArray(dimLength[0])
    #         for i in range(dimLength[0]):
    #             retArray[i] = cppArray[i]
    #         return retArray
    #     else:
    #         retArray = numpy.createArray(dimLength[0], dimLength[1])
    #         for i in range(dimLength[0]):
    #             for j in range(dimLength[1]):
    #                 retArray[i][j] = cppArray[i][j]
    #         return retArray
    # def getStateAndCovariance():
    #     return (cppArraytoNumpyArray(self.state),
    #             cppArraytoNumpyArray(self.covMatrix))
if __name__ == "__main__":
    eskfGlue = EskfGlue()
    print(eskfGlue.getPosition())
    meas = MeasData(*[0 for i in range(0, 15)])
    eskfGlue.predictEskf(meas, deltaTime=0.1)
    eskfGlue.updateEskfUwb(meas)
    eskfGlue.updateEskfImu(meas)
    print(eskfGlue.getPosition())
