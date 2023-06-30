import sys
import numpy as np
from PyQt5.QtCore import Qt, QRectF, QPointF, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtGui import QPainter, QPen, QColor, QTransform
from car import Car
from simulationScene import SimulationScene
import math

class CustomEventFilter(QGraphicsView):
    def __init__(self, parent=None):
        super(CustomEventFilter, self).__init__(parent)

    def eventFilter(self, source, event):
        print(1)
        if event.type() == QEvent.GraphicsSceneMousePress:
            print("Mouse press detected!")
            # handle the event here
            return True
        return super(CustomEventFilter, self).eventFilter(source, event)


class MainWindow(QMainWindow):
    def __init__(self, car, parent=None):
        super(MainWindow, self).__init__(parent)

        self.car = car

        # Set up the QGraphicsView and scene
        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)
        self.scene = SimulationScene(self.car, self)
        self.view.setScene(self.scene)
        self.view.setFixedSize(1200, 850)


        self.view.scale(1,-1) # flip the y-axis

        
        self.scene.setSceneRect(-400, -400, 800, 800) # set origin to center

        # Draw boundary box for the scene
        self.scene.addRect(QRectF(-400, -400, 800, 800))

        # install event filter
        eventFilter = CustomEventFilter()
        self.view.installEventFilter(eventFilter)

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    car = Car(100, -10, math.pi/2)  # Center the car
    window = MainWindow(car)
    window.show()

    sys.exit(app.exec_())
