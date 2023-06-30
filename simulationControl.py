from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsEllipseItem
from PyQt5.QtGui import QPainter, QPen, QColor, QTransform, QFont
from car import Car
from obstacle import Obstacle
from controlAlgorithms import ControlAlgorithms

class Controller(QObject):
    def __init__(self, car, parent=None):
        super().__init__(parent)
        self.car = car
        self.markers = [] # to visualize path planning

        self.transform = QTransform()
        self.transform.scale(1, -1) # un-invert transformation since we flipped the view to have y-axis grow up
        self.graphicsScene = parent

        self.controlAlgorithms = ControlAlgorithms(self.car)

    def pathPlanning(self, x, y):
        self.clearMarkersFromGraphicsScene()

        obstacles = [(obstacle.x, obstacle.y, obstacle.width, obstacle.height) for obstacle in self.obstacles]
        paths = self.controlAlgorithms.pathPlanning([x,y], obstacles)

        for (pathX, pathY) in paths: self.addMarkerToGraphicsScene(pathX, pathY)

    def setObstacles(self, obstacles):
        self.obstacles = obstacles

    def update(self):
        self.controlAlgorithms.controlLoopBody()

    def clearMarkersFromGraphicsScene(self):
        for marker in self.markers: self.graphicsScene.removeItem(marker)
        self.markers = []

    def addMarkerToGraphicsScene(self, markerX, markerY):
        pen = QPen(QColor(Qt.red))
        marker = QGraphicsEllipseItem(0,0, 5, 5)
        marker.setPen(pen)
        self.graphicsScene.addItem(marker)
        marker.setPos(markerX, markerY)
        self.markers.append(marker)

        font = QFont()
        font.setPointSize(7)

        markerLabel = QGraphicsTextItem()
        markerLabel.setTransform(self.transform)
        markerLabel.setPos(markerX, markerY)
        self.graphicsScene.addItem(markerLabel)
        markerLabel.setPlainText("(%.0f, %.0f)" % (markerX, markerY))
        markerLabel.setFont(font)
        self.markers.append(markerLabel)