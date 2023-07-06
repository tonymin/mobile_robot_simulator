import math
import numpy as np
import algorithms as alg

class ControlAlgorithms:
    def __init__(self, car) -> None:
        self.car = car
        self.targets = []

    # This function is called once when given a target
    # OPTIONAL: return a sequence of points in an array to be plotted as trajectory markers
    def pathPlanning(self, targetLocation, obstacles):
        # target location
        x = targetLocation[0]
        y = targetLocation[1]
        self.targets.append((x, y))

        # return planned path to visualize
        return [(x, y)]

    # this is where you implement the internals of your control loop
    def controlLoopBody(self):
        if self.targets:
            print("Moving to : ",self.targets[0])
            reachedTarget = self.pointAndShoot(*self.targets[0], self.car)
            if reachedTarget:
                print("Reached target: ",self.targets[0])
                self.car.set_mobile_base_speed(0, 0, 0)
                self.targets.pop(0)
    
    def isTargetReached(self, x, y):
        robot_pose, pickup_location, dropoff_location, obstacles = self.car.get_poses()
        carX, carY, carTheta = robot_pose
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
        
    def pointAndShoot(self, x, y, car):

        if self.isTargetReached(x,y): return True

        # get pose of car and target location
        robot_pose, pickup_location, dropoff_location, obstacles = car.get_poses()
        carX, carY, carTheta = robot_pose
        carLoc = np.array([carX, carY])
        dst = np.array([x, y])

        # we want to drive the robot so that the target is within reach of the arm
        # reduce the amount of displacement needed
        arm_displacement = np.linalg.norm(dst - carLoc) - car.ARM_LENGTH

        # calculate orientations
        desiredOrientation = dst - carLoc
        carOrientation = np.array([np.cos(carTheta), np.sin(carTheta)])

        # re-calculate the desired orientation, but this time to the position where the arm can reach the target
        desiredOrientation = arm_displacement * desiredOrientation / np.linalg.norm(desiredOrientation)

        # there is a need for rotation, configure omega_dot
        cross_product = np.cross(carOrientation, desiredOrientation)
        sign = np.sign(cross_product) if abs(cross_product) > 1e-2 else 0

        # Calculate angular displacement
        delta_theta_numerator = carOrientation.dot(desiredOrientation)
        delta_theta_denominator = (np.linalg.norm(carOrientation)*np.linalg.norm(desiredOrientation))
        delta_theta = sign * np.arccos(delta_theta_numerator/delta_theta_denominator)
        delta_degree = np.rad2deg(delta_theta)

        print("car pos: %.2f, %.2f" % (carX, carY))
        print("car orientation: ", carOrientation)
        print("desired pos: %.2f, %.2f" % (x, y))
        print("desired orientation: ", desiredOrientation)
        print("delta_degree: ", delta_degree)
        
        if abs(delta_degree) > 5:
            # find omega_dot
            angle_displacement_per_step = sign*car.MAX_ANGULAR_SPEED*car.TIMEOUT_DRIVE_SPEED
            omega_dot = sign*car.MAX_ANGULAR_SPEED
            if abs(angle_displacement_per_step) > abs(delta_degree):
                omega_dot = delta_degree / car.TIMEOUT_DRIVE_SPEED
            car.set_mobile_base_speed(0, 0, np.radians(omega_dot))
            return
        
        # translation
        linearDisplacement = np.linalg.norm(desiredOrientation)
        linear_displacement_per_timestep = car.MAX_LINEAR_SPEED * car.TIMEOUT_DRIVE_SPEED
        stepDisplacement = car.MAX_LINEAR_SPEED
        if abs(linear_displacement_per_timestep) > abs(linearDisplacement):
            stepDisplacement = linearDisplacement / car.TIMEOUT_DRIVE_SPEED
        car.set_mobile_base_speed(stepDisplacement, 0, 0)

        return False

