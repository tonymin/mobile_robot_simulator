import math
import numpy as np
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsObject
from PyQt5.QtCore import Qt, QRectF, QPointF, QEvent, pyqtProperty, QEventLoop, QTime
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QTimer

class Car(QGraphicsObject):
    def __init__(self, x = 0.0, y = 0.0, theta=0.0):
        super().__init__()

        self.obstacles = []
        self.pickup_location = []
        self.dropoff_location = []
        
        # car pose in the global frame
        self.pos= QPointF(x,y)
        self.rotate = np.rad2deg(theta)
        self.zeroOutVelocities()

        # constraints
        self.MAX_LINEAR_SPEED = 0.1 * 100 # centimeters / second
        self.MAX_ANGULAR_SPEED = 30 # degrees / second
        self.TIMEOUT_DRIVE_SPEED = 0.5 # seconds
        self.ARM_LENGTH = 40

        # in cm
        self.WIDTH = 24 # cm
        self.LENGTH = 32 # cm
        self.HEIGHT = 27 # cm
        self.ORIGIN_OFFSET_FROM_LENGTH = 4 # assume the origin is 4 cm from the end of car

        self.last_command_time = 0.0
        self.elapsed_simulation_time=0

    def setObstacles(self, obs): self.obstacles = obs
    def setPickupLocs(self, loc): self.pickup_location = loc
    def setDropoffLocs(self, loc): self.dropoff_location = loc

    def update_pose(self, current_sim_time):
        # dt needs to be in seconds since velocities are in seconds
        dt = (current_sim_time - self.elapsed_simulation_time) / 1000.0

        self.elapsed_simulation_time = current_sim_time

        self.print()

        # if no new command is received, zero the velocities
        elapsed = self.elapsed_simulation_time - self.last_command_time
        if elapsed > self.TIMEOUT_DRIVE_SPEED * 1000: self.zeroOutVelocities()

        # get current pose
        x, y, theta = self._getPose()

        # calculate global velocities
        # by convention theta is taken from x-axis, increasing in CCW
        x_dot_g = self.x_dot * np.cos(theta) - self.y_dot * np.sin(theta)
        y_dot_g = self.x_dot * np.sin(theta) + self.y_dot * np.cos(theta)
        print("x_dot_g:", x_dot_g)
        print("y_dot_g:", y_dot_g)
        print("x_dot:", self.x_dot)
        print("y_dot:", self.y_dot)


        # update pose in global frame
        finalX = x + dt * x_dot_g
        finalY = y + dt * y_dot_g
        finalAngle = np.rad2deg(theta) - dt * self.omega_dot
        # NOTE: self.omega_dot here is in degrees
        # NOTE: QT takes positive angle as rotation in CW direction, but simulation is CCW

        self.pos = QPointF(finalX, finalY)
        self.rotate = finalAngle

    def _getPose(self):
        pos = self.pos
        angle = np.radians(self.rotate)
        return [pos.x(), pos.y(), angle]
    
    def get_poses(self):
        return [self._getPose(), self.pickup_location, self.dropoff_location, self.obstacles]
    
    def print(self):
        print("Pose: (%.2f, %.2f), %.2f deg (%.2f rad) " 
              % (self.pos.x(), self.pos.y(), self.rotate, np.radians(self.rotate)))

    # main control API
    def set_mobile_base_speed(self, x_dot, y_dot, omega_dot):
        omega_dot = 180.0 / math.pi * omega_dot # degrees / seconds
        x_dot, y_dot, omega_dot = self.__saturate_speeds(x_dot, y_dot, omega_dot)
        y_dot = -y_dot # flipped ref frame on the robot (x>0 is forward, y>0 is right)
        omega_dot = -omega_dot # flipped ref frame on the robot (z>0 is downward)

        self.x_dot = x_dot
        self.y_dot = y_dot
        self.omega_dot = omega_dot

        self.last_command_time = self.elapsed_simulation_time

    def set_arm_pose(self, q1, q2):
        pass

    def close_gripper(self):
        pass

    def open_gripper(self):
        pass

    def set_leds(self, red_level, green_level, blue_level):
        pass

    @pyqtProperty(QPointF)
    def pos(self):
        return super().pos()

    @pos.setter
    def pos(self, point):
        super().setPos(point)

    @pyqtProperty(float)
    def rotate(self):
        return super().rotation()

    @rotate.setter
    def rotate(self, angle):
        super().setRotation(angle)

    def boundingRect(self):
        return QRectF(-10, -20, 60, 30)

    def paint(self, painter, option, widget):
        painter.save()  
        
        # draw the car
        painter.setPen(QPen(Qt.black))
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(-self.ORIGIN_OFFSET_FROM_LENGTH, -int(self.WIDTH/2), self.LENGTH, self.WIDTH)
        painter.drawLine(0, 0, 0, 50)
        painter.drawLine(0, 0, 50, 0)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.LENGTH-self.ORIGIN_OFFSET_FROM_LENGTH, -int(self.WIDTH/2), 20, self.WIDTH)

        # manipulator pickup zone
        painter.setBrush(Qt.black)  # Set fill color to black
        painter.drawEllipse(QPointF(0, 0), 5, 5)
        painter.drawEllipse(QPointF(self.ARM_LENGTH, 0), 5, 5)
        painter.restore()

    def __saturate_speeds(self, x_dot, y_dot, omega_dot):
        x_dot = max(-self.MAX_LINEAR_SPEED, min(x_dot, self.MAX_LINEAR_SPEED))
        y_dot = max(-self.MAX_LINEAR_SPEED, min(y_dot, self.MAX_LINEAR_SPEED))
        omega_dot = max(-self.MAX_ANGULAR_SPEED, min(omega_dot, self.MAX_ANGULAR_SPEED))
        return x_dot, y_dot, omega_dot

    def zeroOutVelocities(self):
        self.x_dot = 0
        self.y_dot = 0
        self.omega_dot = 0

