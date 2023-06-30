from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import QTimer, QTime
from obstacle import Obstacle
from simulationControl import Controller
import simulationConstants as SIM_CONST
from PyQt5.QtGui import QTransform
from simulationEnvironment import SimulationEnvironment

class SimulationScene(QGraphicsScene):
    def __init__(self, car, parent):
        super(SimulationScene, self).__init__(parent)
        self.car = car
        self.addItem(self.car)

        self.transform = QTransform()
        self.transform.scale(1, -1) # un-invert transformation since we flipped the view to have y-axis grow up
        
        self.setup()
        self.addAxes()
        self.setupLabels()

    def _tick(self):
        # called at every time step / frame
        self.elapsed_simulation_time += SIM_CONST.SIMULATION_TIME_RESOLUTION
        self.car.update_pose(self.elapsed_simulation_time)
        self.controller.update()

        if (self.elapsed_simulation_time > 10000):
            self.time_stamp.setPlainText("Sim Time (s): %.2f" % (self.elapsed_simulation_time/1000.0))
        else:
            self.time_stamp.setPlainText("Sim Time (ms): " + str(self.elapsed_simulation_time))
        self.update()  # update the entire scene

    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        self.mouseLastClickedPositionInScene.setPlainText("Mouse clicked: (%.2f, %.2f)" % (x,y))
        self.controller.setTarget(x, y)
   
    def mouseMoveEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        self.mousePositionInScene.setPlainText("Mouse Pos: (%.2f, %.2f)" % (x,y))

    def setup(self):
        self.simEnv = SimulationEnvironment()
        self.controller = Controller(self.car, self)
        self.setupObstacles()
        self.setupSimulationTimer()

    def setupSimulationTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(SIM_CONST.TIME_RESOLUTION)
        self.elapsed_simulation_time = 0

    def setupObstacles(self):
        obstacles = self.simEnv.getObstacles()
        self.controller.setObstacles(obstacles)
        for obstacle in obstacles:
            self.addItem(obstacle)

    def setupLabels(self):
        label_X = -600

        self.time_stamp = QGraphicsTextItem()
        self.time_stamp.setTransform(self.transform)
        self.time_stamp.setPos(label_X, 400)  # Position text item
        self.addItem(self.time_stamp)

        self.mousePositionInScene = QGraphicsTextItem()
        self.mousePositionInScene.setTransform(self.transform)
        self.mousePositionInScene.setPos(label_X, 380)  # Position text item
        self.addItem(self.mousePositionInScene)
        self.mousePositionInScene.setPlainText("Mouse Pos: ")

        self.mouseLastClickedPositionInScene = QGraphicsTextItem()
        self.mouseLastClickedPositionInScene.setTransform(self.transform)
        self.mouseLastClickedPositionInScene.setPos(label_X, 360)  # Position text item
        self.addItem(self.mouseLastClickedPositionInScene)
        self.mouseLastClickedPositionInScene.setPlainText("Mouse clicked: ")

    def addAxes(self):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        x_axis = QGraphicsLineItem(-400, 0, 400, 0)  # x-axis
        y_axis = QGraphicsLineItem(0, -400, 0, 400)  # y-axis
        x_axis.setPen(pen)
        y_axis.setPen(pen)
        self.addItem(x_axis)
        self.addItem(y_axis)

        # Label the axes
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        x_label = QGraphicsTextItem('x')
        x_label.setTransform(self.transform)
        y_label = QGraphicsTextItem('y')
        y_label.setTransform(self.transform)
        x_label.setPos(450, 0)  # adjust the position as needed
        y_label.setPos(0, -350)  # adjust the position as needed
        x_label.setFont(font)
        y_label.setFont(font)
        x_label.setDefaultTextColor(Qt.red)
        y_label.setDefaultTextColor(Qt.red)
        self.addItem(x_label)
        self.addItem(y_label)

        # Add ticks and labels to the axes
        for i in range(-400, 500, 100):  # adjust range and step as needed
            # Add x-axis ticks and labels
            x_tick = QGraphicsLineItem(i, -10, i, 10)  # adjust -10 and 10 as needed
            x_label = QGraphicsTextItem(str(i))
            x_label.setTransform(self.transform)
            x_label.setPos(i, 20)  # adjust 15 as needed
            self.addItem(x_tick)
            self.addItem(x_label)

            # Add y-axis ticks and labels
            y_tick = QGraphicsLineItem(-10, i, 10, i)  # adjust -10 and 10 as needed
            y_label = QGraphicsTextItem(str(i))
            y_label.setTransform(self.transform)
            y_label.setPos(-30, i)  # adjust -30 as needed
            self.addItem(y_tick)
            self.addItem(y_label)