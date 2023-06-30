# This affects performance of your system and how "fast" simulation goes
# High FPS -> high CPU usage & fast simulation
FPS = 100
TIME_RESOLUTION = round(1000 / FPS) # in miliseconds

# Controls how "fast" the simulation goes. Unit is in miliseconds
# the larger this is, the faster the simulation, BUT you get a scaling error
TIME_SCALE = 100
SIMULATION_TIME_RESOLUTION = 1 * TIME_SCALE # milisecond