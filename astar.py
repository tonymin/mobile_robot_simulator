import math

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def eulideanDistance(x1, y1, x2,y2):
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

def point_line_distance(point, start, end):
    if (start == end):
        return eulideanDistance(point[0], point[1], start[0], start[1])
    else:
        n = abs((end[0] - start[0]) * (start[1] - point[1]) - (start[0] - point[0]) * (end[1] - start[1]))
        d = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        return n / d

def ramer_douglas_peucker(points, epsilon):
    dmax = 0.0
    index = 0
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax >= epsilon:
        results1 = ramer_douglas_peucker(points[:index+1], epsilon)
        results2 = ramer_douglas_peucker(points[index:], epsilon)
        result_points = results1[:-1] + results2
    else:
        result_points = [points[0], points[-1]]

    return result_points

def a_star(start, end, obstacles):
    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)

    # Initialize both open and closed list
    open_list = []
    closed_list = []
    open_list.append(start_node)

    MAX_ITER = 1500
    iter = 0 

    # Loop until you find the end
    while len(open_list) > 0 and iter < MAX_ITER:
        iter+=1
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # the further we are, the bigger jumps we take
        distance = eulideanDistance(current_node.position[0], current_node.position[1], 
                            end_node.position[0], end_node.position[1])
        searchDistance = 50
        if distance < 20: searchDistance = 1

        # Found the node that is close enough to target
        THRESHOLD = 50
        if distance < THRESHOLD:
            path = []
            path.append(end_node.position)
            current = current_node
            while current is not None:
                if current == start_node:
                    break
                path.append(current.position)
                current = current.parent
            return path[::-1]

        # look at neighboring nodes
        for newPosition in [(0, -searchDistance), (0, searchDistance), (-searchDistance, 0), (searchDistance, 0)]:
            nodePosition = (current_node.position[0] + newPosition[0], current_node.position[1] + newPosition[1])
            child = Node(current_node, nodePosition)

            if child in closed_list: continue

            # Check distance to obstacles
            tooCloseToObstacle = False
            proximityToObstacles = 0
            for obstacle in obstacles:
                # check if node is within proximity of obstacle
                obs_width = obstacle[2]
                obs_height = obstacle[3]

                margin = 30
                
                if ((nodePosition[0] > obstacle[0] - margin and nodePosition[0] < obstacle[0] + obs_width + margin) and
                    (nodePosition[1] > obstacle[1] - margin and nodePosition[1] < obstacle[1] + obs_height + margin)):
                    # print("%d, %d too close to obstacle (%d, %d, %d, %d)" 
                    #       % (nodePosition[0], nodePosition[1], obstacle[0], obstacle[1], obstacle[2] , obstacle[3]))
                    tooCloseToObstacle = True
                    break

                x_clearance = min(abs(nodePosition[0] - (obstacle[0] - margin)), 
                                  abs(nodePosition[0] -(obstacle[0] + obs_width + margin) ))
                y_clearance = min(abs(nodePosition[1] - (obstacle[1] - margin)), 
                                  abs(nodePosition[1] -(obstacle[1] + obs_height + margin) ))
                
                obstacleProximity = min(x_clearance, y_clearance)
                if obstacleProximity > 100: continue # far enough away that we don't care

                # close obstacles, we care more
                proximityToObstacles += 100 - obstacleProximity

            if tooCloseToObstacle: continue
            
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.h += proximityToObstacles # add penalty based on closeness to obstacles
            child.f = child.g + child.h

            # for open_node in open_list:
            #     if child == open_node and child.f < open_node.f:
            #         continue

            open_list.append(child)

    return []