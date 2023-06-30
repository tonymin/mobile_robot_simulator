import numpy as np
from PyQt5.QtCore import Qt, QRectF, QPointF, QEvent, QTimeLine
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPropertyAnimation
import math

class Obstacle(QGraphicsItem):
    def __init__(self, x, y, width, height):
        super(Obstacle, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def boundingRect(self):
        return QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.save()  
        painter.setBrush(Qt.black)  # red color for obstacles
        painter.drawRect(self.x, self.y, self.width, self.height)
        painter.restore()
