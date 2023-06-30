# Configure the environment here

from obstacle import Obstacle

class SimulationEnvironment:
    def __init__(self):
        self.obstacles = []
        self.defineTheEnvironment()

    def defineTheEnvironment(self):
        self.defineObstacles()
        
    def defineObstacles(self):
        self.obstacles.append(Obstacle(100, 200, 10, 10))
        self.obstacles.append(Obstacle(200, 200, 50, 60))
        self.obstacles.append(Obstacle(250, 100, 30, 20))
        self.obstacles.append(Obstacle(-200, -200, 100, 60))
        self.obstacles.append(Obstacle(-60, -100, 100, 60))
        
    def getObstacles(self):
        return self.obstacles
