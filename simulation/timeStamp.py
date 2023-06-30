import sys
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsTextItem

class TimeStamp(QGraphicsScene):
    def __init__(self, parent=None):
        super(TimeStamp, self).__init__(parent)
        self.time_stamp = QGraphicsTextItem()
        self.time_stamp.setPos(0, 0)  # Position text item
        self.addItem(self.time_stamp)  # Add text item to scene

        # Create a QTimer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_stamp)

        # Set the timer to update every second (1000 ms)
        self.timer.start(1000)

    def update_time_stamp(self):
        current_time = QTime.currentTime().toString()
        self.time_stamp.setPlainText(current_time)