I am using python 3.10.9, but other versions may work as well (not tested).
I am using Anaconda to manage my python packages, but these are the main dependencies:
- ptQT5
- numpy

How it works:
- click anywhere in the screen to set as target that the car must navigate to while avoiding obstacles

Issues:
- seems to be errors for long trajectories (maybe due to numeric inaccuracies?)
- if target is closely behind the car, the driveTo function is incorrect
- If target is near car, car may run over target