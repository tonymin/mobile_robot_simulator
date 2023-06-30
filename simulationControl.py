from PyQt5.QtCore import QObject
import numpy as np
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsEllipseItem
from PyQt5.QtGui import QPainter, QPen, QColor, QTransform, QFont
from car import Car
from obstacle import Obstacle
from astar import a_star, ramer_douglas_peucker
import math
import simulationConstants as SIM_CONST

class Controller(QObject):
    def __init__(self, car, parent=None):
        super().__init__(parent)
        self.car = car
        self.markers = [] # to visualize path planning

        self.transform = QTransform()
        self.transform.scale(1, -1) # un-invert transformation since we flipped the view to have y-axis grow up
        self.graphicsScene = parent

        # self.target = None
        self.targets = []

    def setTarget(self, x, y):
        # self.targets.append((100, 100))
        # self.targets.append((0, 0))
        # self.targets.append((100, 100))
        
        self.targets.clear()
        paths = self.pathPlanning(x, y, self.graphicsScene)
        for (pathX, pathY) in paths:
            self.targets.append((pathX, pathY))

    def setObstacles(self, obstacles):
        self.obstacles = obstacles
    
    

    def update(self):
        if self.targets:
            # check if the first target is reached. If yes, remove it.
            if self._isTargetReached(*self.targets[0]):
                print("Reached target: ",self.targets[0])
                self.car.set_mobile_base_speed(0, 0, 0)
                self.targets.pop(0)

            # if there are still targets, move towards the first one
            if self.targets:
                print("Moving to : ",self.targets[0])
                self._pointAndShoot2(*self.targets[0], self.car)
    
    def _isTargetReached(self, x, y):
        carX, carY, carTheta = self.car.getPose()
        distance_to_target = np.sqrt((x - carX)**2 + (y - carY)**2)
        desired_orientation = math.atan2(y - carY, x - carX)

        orientation_diff = abs(carTheta - desired_orientation)
        orientation_diff = min(orientation_diff, 2*math.pi - orientation_diff)

        # Check if target is within the arm's reach and if car is aligned with target
        errorMarginArm = 3
        errorMarginTheta = 0.1
        isAligned = orientation_diff < errorMarginTheta
        isCloseEnough = distance_to_target <= self.car.ARM_LENGTH + errorMarginArm
        if isCloseEnough and isAligned:
            return True
        return False
        
    def _pointAndShoot2(self, x, y, car):
        # This control is based on point and shoot
        # We do pure rotation and pure translation, never both at the same time

        # get pose of car and target location
        carX, carY, carTheta = car.getPose()
        carLoc = np.array([carX, carY])
        dst = np.array([x, y])

        # we want to drive the robot so that the target is within reach of the arm
        # reduce the amount of displacement needed
        arm_displacement = np.linalg.norm(dst - carLoc) - car.ARM_LENGTH

        # if the arm can already reach the target, no need to move further
        # if arm_displacement < 0:
        #     print("Target already in arm's reach, no need to move.")
        #     return

        # calculate orientations
        desiredOrientation = dst - carLoc
        carOrientation = np.array([np.cos(carTheta), np.sin(carTheta)])

        # re-calculate the desired orientation, but this time to the position where the arm can reach the target
        desiredOrientation = arm_displacement * desiredOrientation / np.linalg.norm(desiredOrientation)

        # determine rotation angle and rotation direction
        # sign = 1
        # if np.cross(carOrientation, desiredOrientation) < 1: sign = -1

        # Calculate angular displacement
        # delta_theta_numerator = carOrientation.dot(desiredOrientation)
        # delta_theta_denominator = (np.linalg.norm(carOrientation)*np.linalg.norm(desiredOrientation))
        # delta_theta = sign * np.arccos(delta_theta_numerator/delta_theta_denominator)
        # delta_degree = np.rad2deg(delta_theta)

        # there is a need for rotation, configure omega_dot
        cross_product = np.cross(carOrientation, desiredOrientation)
        sign = np.sign(cross_product) if abs(cross_product) > 1e-2 else 0

        # Calculate angular displacement
        delta_theta_numerator = carOrientation.dot(desiredOrientation)
        delta_theta_denominator = (np.linalg.norm(carOrientation)*np.linalg.norm(desiredOrientation))
        delta_theta = sign * np.arccos(delta_theta_numerator/delta_theta_denominator)
        delta_degree = np.rad2deg(delta_theta)

        # print("car pos: %.2f, %.2f" % (carX, carY))
        # print("car orientation: ", carOrientation)
        # print("desired pos: %.2f, %.2f" % (x, y))
        # print("desired orientation: ", desiredOrientation)

        # Correct the angles if they are outside the -180 to 180 degree range
        if delta_degree > 180:
            delta_degree -= 360
        elif delta_degree < -180:
            delta_degree += 360
        
        # calculate angular displacement
        dot_product = delta_theta_numerator / delta_theta_denominator

        # Handle the case where the dot product is negative (i.e., angle should be 180, not 0)
        if dot_product < 0:
            delta_theta = np.pi
        else:
            delta_theta = sign * np.arccos(dot_product)

        delta_degree = np.rad2deg(delta_theta)

        if abs(delta_degree) > 5:
            # stop translation

            # find omega_dot
            angle_displacement_per_step = sign*car.MAX_ANGULAR_SPEED*car.TIMEOUT_DRIVE_SPEED
            omega_dot = sign*car.MAX_ANGULAR_SPEED
            if abs(angle_displacement_per_step) > abs(delta_degree):
                omega_dot = delta_degree / car.TIMEOUT_DRIVE_SPEED
            self.car.set_mobile_base_speed(0, 0, np.radians(omega_dot))
            # we do not wish to translate while rotation is happening
            return
        
        # translation

        # break down the complete linear translation into control sequences
        linearDisplacement = np.linalg.norm(desiredOrientation)
        linear_displacement_per_timestep = car.MAX_LINEAR_SPEED * car.TIMEOUT_DRIVE_SPEED
        stepDisplacement = car.MAX_LINEAR_SPEED
        if abs(linear_displacement_per_timestep) > abs(linearDisplacement):
            stepDisplacement = linearDisplacement / car.TIMEOUT_DRIVE_SPEED
        self.car.set_mobile_base_speed(stepDisplacement, 0, 0)

    def pathPlanning(self, x, y, graphicsScene):
        self.clearMarkersFromGraphicsScene(graphicsScene)

        obstacles = [(obstacle.x, obstacle.y, obstacle.width, obstacle.height) for obstacle in self.obstacles]
        paths = a_star((self.car.getPose()[0], self.car.getPose()[1]), (x, y), obstacles)
        simplified_path = ramer_douglas_peucker(paths, 50)
        for (pathX, pathY) in simplified_path: self.addMarkerToGraphicsScene(pathX, pathY, graphicsScene)
        
        return simplified_path

    def clearMarkersFromGraphicsScene(self, graphicsScene):
        for marker in self.markers: graphicsScene.removeItem(marker)
        self.markers = []

    def addMarkerToGraphicsScene(self, markerX, markerY, graphicsScene):
        pen = QPen(QColor(Qt.red))
        marker = QGraphicsEllipseItem(0,0, 5, 5)
        marker.setPen(pen)
        graphicsScene.addItem(marker)
        marker.setPos(markerX, markerY)
        self.markers.append(marker)

        font = QFont()
        font.setPointSize(7)

        markerLabel = QGraphicsTextItem()
        markerLabel.setTransform(self.transform)
        markerLabel.setPos(markerX, markerY)
        graphicsScene.addItem(markerLabel)
        markerLabel.setPlainText("(%.0f, %.0f)" % (markerX, markerY))
        markerLabel.setFont(font)
        self.markers.append(markerLabel)