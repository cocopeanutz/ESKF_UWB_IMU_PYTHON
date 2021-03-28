from collections import namedtuple
import serial
import time
import GS_timing as gt

# G_CONS = 9.81;
G_CONS = 9.781
PI = 3.14
MeasData = namedtuple("MeasData", "rawPosi rawPosj rawPosk rawMx rawMy rawMz rawMAvail rawAx rawAy rawAz rawAAvail rawWx rawWy rawWz rawWAvail")


def moveStreamToStruct(buff):
    try:
        s=buff.decode('ascii')
        dataList = list(map(float,s.split(',')))
        measRaw = MeasData(*dataList)
        gyroBias = [-0.11245064113451089, 2.614698548247849, -0.3286168195199276]
        # print(measRaw.rawWz)
        # print((measRaw.rawAz/16384*G_CONS))
        print("x acceleratoin:", measRaw.rawAx/16384*G_CONS)
        print("y acceleratoin:", -measRaw.rawAy/16384*G_CONS)
        meas = MeasData(
            measRaw.rawPosi/1000.0,
            measRaw.rawPosj/1000.0,
            measRaw.rawPosk/1000.0,

            measRaw.rawMx*0.15,
            measRaw.rawMy*0.15,
            measRaw.rawMz*0.15,
            measRaw.rawMAvail,

            measRaw.rawAx/16384*G_CONS,
            -measRaw.rawAy/16384*G_CONS,
            -measRaw.rawAz/16384*G_CONS-0.04,
            measRaw.rawAAvail,

            # (measRaw.rawWx/16384*125-gyroBias[0])*PI/180,
            # -(measRaw.rawWy/16384*125-gyroBias[1])*PI/180,
            # -(measRaw.rawWz/16384*125-gyroBias[2])*PI/180,
            # (measRaw.rawWx/16384*125-gyroBias[0])/5,
            # -(measRaw.rawWy/16384*125-gyroBias[1])/5,
            # -(measRaw.rawWz/16384*125-gyroBias[2])/5,
            (measRaw.rawWx/32768.0*1000)*PI/180,
            -(measRaw.rawWy/32768.0*1000)*PI/180,
            -(measRaw.rawWz/32768.0*1000)*PI/180,
            measRaw.rawWAvail
        )
        return meas
    except Exception as e:
        print(e)
    return None
class DataHandlerClass:
    def __init__(self, port, baudrate):
        try:
            self.serialPort = serial.Serial(port, baudrate, timeout=0)
            self.buff = bytearray()
            self.startTime = None
        except Exception as e:
            print(e)
            print ('Serial port cannot open!')
            pass
    def readFromPort(self):
        connected = True
        retval = None
        # while self.serialPort.inWaiting():
        while True:
            #reading = serial_port.read().decode('ascii')
            reading = self.serialPort.read()
            # if(reading!=b''):
            #      print(reading)
            if(reading == b'<'):
                self.buff=bytearray()
                self.startTime = gt.millis()
            elif(reading==b'>'):
                retval = moveStreamToStruct(self.buff)
                self.buff=bytearray()
                # if(self.startTime != None):
                    # print(gt.millis()-self.startTime)
                return retval
            else:
                self.buff+=reading
        return retval
    def getMeasFromPort(self):
        return moveStreamToStruct(self.readFromPort())
    def flush(self):
        self.serialPort.flushInput()
