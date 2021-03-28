import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial
import time
import GS_timing as accurateClock
from pyquaternion import Quaternion

QUATERNION_GUI = True
TWO_D_GUI = False
THREE_D_GUI = False

class DataGui:
    def __init__(self):
        self.fig = plt.figure()

        if THREE_D_GUI:
            self.ax = self.fig.add_subplot(2, 2, (1, 4), projection='3d', animated=True)

            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')
            # self.ax = self.fig.gca(projection='3d')
            # self.ax.set(xlim=(0,15), ylim=(0,15))
            self.ax.set_xlim([0, 15], auto=False)
            self.ax.set_ylim([0, 15], auto=False)
            self.ax.set_zlim([0, 3])

            # self.ax.set_animated(False)
            self.posX = np.array([0])
            self.posY = np.array([0])
            self.posZ = np.array([1.31])

            self.line, = self.ax.plot(self.posX, self.posY, animated=True)
            self.line.set_3d_properties(self.posZ)

            self.line.set_data((self.posX, self.posY))
            self.line.set_3d_properties(self.posZ)

        # self.ax.legend()



        if TWO_D_GUI == True:
            self.posXTWO_D = np.array([0.0])
            self.posYTWO_D = np.array([0.0])

            self.axTWO_D = self.fig.add_subplot(2, 2, (1, 4))
            # self.ax = self.fig.gca(projection='3d')
            # self.axTWO_D.set(xlim=(0,15), ylim=(0,15))
            # self.axTWO_D.set(xlim=([0,15]), ylim=([0,15]))
            self.axTWO_D.set_xlim([-2,15])
            self.axTWO_D.set_ylim([-2,15])

            self.lineTWO_D, = self.axTWO_D.plot(self.posXTWO_D, self.posYTWO_D, animated=True)
            self.lineTWO_D.set_data((self.posXTWO_D, self.posYTWO_D))
            self.axTWO_D.set_xlabel('X')
            self.axTWO_D.set_ylabel('Y')


        if QUATERNION_GUI == True:
            self.quatAxis = self.fig.add_subplot(2, 2, 2, projection='3d')
            # self.quatAxis = self.fig.add_axes([0, 0, 1, 1], projection='3d')
            self.quatAxis.set_xlabel('X')
            self.quatAxis.set_ylabel('Y')
            self.quatAxis.set_zlabel('Z')
            #self.quatAxis.axis('off')

            # use a different color for each axis
            colors = ['r', 'g', 'b']

            # set up lines and points
            self.quatLines = sum([self.quatAxis.plot([], [], [], c=c, animated=True)
                         for c in colors], [])

            self.startpoints = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
            self.endpoints = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

            # for line in self.lines:
            #     line.set_data(([], []))
            #     line.set_3d_properties([])

            # prepare the axes limits
            self.quatAxis.set_xlim((-2, 2))
            self.quatAxis.set_ylim((-2, 2))
            self.quatAxis.set_zlim((-2, 2))

            # set point-of-view: specified by (altitude degrees, azimuth degrees)
            self.quatAxis.view_init(30, 270)


        plt.ion()
        plt.show(block=False)
        plt.pause(0.1)


        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    def insertPointTry(self, i):

        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100) + i/100

        self.posZ = np.linspace(-2, 2, 100)
        r = self.posZ**2 + 1
        self.posX = r * np.sin(theta)
        self.posY = r * np.cos(theta)
        # print(z)
        self.line.set_data((x[0:i], y[0:i]))
        self.line.set_3d_properties(z[0:i])
        plt.draw()
        self.fig.canvas.flush_events() # flush the GUI events

    def updateGUI(self, pos, vel, quaternion, render=False):
        self.fig.canvas.restore_region(self.bg)

        self.updatePos(pos)
        # self.updateVel(vel)
        if(render==True):
            if THREE_D_GUI:
                self.renderPos()
            if TWO_D_GUI==True:
                self.renderPosTWO_D()
            if QUATERNION_GUI==True:
                self.renderQuat(quaternion)
            self.fig.canvas.blit(self.fig.bbox)
            self.fig.canvas.flush_events()

    def updatePos(self, pos):
        if THREE_D_GUI == True:
            self.posX = np.append(self.posX, [pos[0]])
            self.posY = np.append(self.posY, [pos[1]])
            self.posZ = np.append(self.posZ, [pos[2]])
        # print("POSITION PYTHON:")
        # print(pos[0], pos[1], pos[2])
        if TWO_D_GUI == True:
            self.posXTWO_D = np.append(self.posXTWO_D, [pos[0]])
            self.posYTWO_D = np.append(self.posYTWO_D, [pos[1]])

    def renderPos(self):
        startTime = accurateClock.millis()
        self.line.set_data((self.posX, self.posY))
        self.line.set_3d_properties(self.posZ)

        self.ax.draw_artist(self.line)

        endTime = accurateClock.millis()
    def renderPosTWO_D(self):
        startTime = accurateClock.millis()
        self.lineTWO_D.set_data((self.posXTWO_D, self.posYTWO_D))

        self.axTWO_D.draw_artist(self.lineTWO_D)

        endTime = accurateClock.millis()

    def renderQuat(self, quat):
        q = Quaternion(*quat)
        for line, start, end in zip(self.quatLines, self.startpoints, self.endpoints):
            #end *= 5

            start_ = q.rotate(start)
            end_ = q.rotate(end)

            # start_ = start
            # end_ = end

            x = np.array([start_[0], end_[0]])
            y = np.array([start_[1], end_[1]])
            z = np.array([start_[2], end_[2]])
            line.set_data((x, y))
            line.set_3d_properties(z)

            #pt.set_data(x[-1:], y[-1:])
            #pt.set_3d_properties(z[-1:])

        #ax.view_init(30, 0.6 * i)
        for line in self.quatLines:
            self.quatAxis.draw_artist(line)

        # self.fig.canvas.draw()
    # def trialCheckHowMuchTime(self):
    #     theta = np.linspace(-4 * np.pi, 4 * np.pi, 1000)
    #     self.z = np.linspace(-2, 2, 1000)
    #     self.r = self.z**2 + 1
    #     self.x = self.r * np.sin(theta)
    #     self.y = self.r * np.cos(theta)
    #     startTime = accurateClock.millis()
    #
    #     self.line.set_data((self.x, self.y))
    #     self.line.set_3d_properties(self.z)
    #     self.ax.draw_artist(self.line)
    #     self.fig.canvas.blit(self.fig.bbox)
    #     self.fig.canvas.flush_events() # flush the GUI events
    #     endTime = accurateClock.millis()
    #     print(endTime - startTime)
if __name__ == "__main__":
    dataGui = DataGui()

    # dataGui.updateGUI([4, 4, 4], [0,0,0], [0,0,0,0])
    # time.sleep(10)
    # while(True):
    #     for i in range(100):
    #         time.sleep(0.1)
    #         # dataGui.updateGUI([i, i, i], [0,0,0], [1,1,0,0])
    #         dataGui.updateGUI([i/10, i/10, i/10], [0,0,0], [0,1,0,0])
    # dataGui.updatePos([2, 3, 5])
    # dataGui.renderPos()
    dataGui.updateGUI([2, 3, 5], [0, 0, 0], [1, 0, 0, 0], render=True)
    time.sleep(0.1)
    dataGui.updateGUI([2, 3, 5], [0, 0, 0], [1, 0, 0, 0], render=True)

    time.sleep(10)
    # time.sleep(2)
    # time.sleep(2)
    # dataGui.updateGUI([4, 4, 4], [0,0,0], [0,0,0,0])
    # dataGui.updateGUI([1, 1, 1], [0,0,0], [0,0,0,0])
    # time.sleep(3)
