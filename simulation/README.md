Dependencies:
- ptQT5
- numpy

Issues:
- seems to be errors for long trajectories (maybe due to numeric inaccuracies?)
- if target is closely behind the car, the driveTo function is incorrect
- If target is near car, car may run over target

TODO:
- trajectory planning