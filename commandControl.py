from collections import deque
from PyQt5.QtCore import QObject
import simulationConstants as SIM_CONST

class Command:
    def __init__(self, delay, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.delay = delay
        

class CommandControl(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_queue = deque()
        self.time_since_last_command = 0
        self.total_time_elapsed = 0

    def add_command(self, command):
        print("add command ", command.function.__name__)
        self.command_queue.append(command)
        self.time_since_last_command = 0


    def update(self):
        # Stop if there are no more commands
        if not self.command_queue: return

        self.time_since_last_command += SIM_CONST.SIMULATION_TIME_RESOLUTION
        self.total_time_elapsed += SIM_CONST.SIMULATION_TIME_RESOLUTION

        # Get the next command
        while self.command_queue and self.time_since_last_command >= self.command_queue[0].delay:
            command = self.command_queue.popleft()
            command.function(*command.args, **command.kwargs)
            self.time_since_last_command -= command.delay
            print(command.function.__name__)
