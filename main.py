from collections import deque


class Environment:
    def __init__(self, width, height, obstacles):
        self.width = width
        self.height = height
        self.obstacles = obstacles

    def is_inside(self, x, y):
        return 1 <= x <= self.width and 1 <= y <= self.height

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def distance_to_obstacle(self, x, y, direction):
        dx, dy = {
            "up": (0, 1),
            "down": (0, -1),
            "right": (1, 0),
            "left": (-1, 0)
        }[direction]

        distance = 0
        current_x = x + dx
        current_y = y + dy

        while self.is_inside(current_x, current_y):
            if self.is_obstacle(current_x, current_y):
                return distance + 1

            distance += 1
            current_x += dx
            current_y += dy

        return None

    def find_path(self, start, target, blocked_positions=None):
        if blocked_positions is None:
            blocked_positions = set()

        queue = deque([start])
        visited = {start}
        previous = {start: None}

        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        while queue:
            current = queue.popleft()

            if current == target:
                path = []
                node = current

                while node is not None:
                    path.append(node)
                    node = previous[node]

                path.reverse()
                return path

            for dx, dy in directions:
                next_position = (
                    current[0] + dx,
                    current[1] + dy
                )

                if next_position in visited:
                    continue

                if not self.is_inside(
                    next_position[0],
                    next_position[1]
                ):
                    continue

                if self.is_obstacle(
                    next_position[0],
                    next_position[1]
                ):
                    continue

                if (
                    next_position in blocked_positions
                    and next_position != target
                ):
                    continue

                visited.add(next_position)
                previous[next_position] = current
                queue.append(next_position)

        return None


class Robot:
    def __init__(
        self,
        name,
        battery,
        temperature,
        speed,
        x,
        y,
        target_x,
        target_y
    ):
        self.name = name
        self.battery = battery
        self.temperature = temperature
        self.speed = speed
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y

    def health_check(self):
        if self.battery <= 20 or self.temperature >= 70:
            return "CRITICAL"

        if self.battery <= 40 or self.temperature >= 60:
            return "WARNING"

        return "HEALTHY"

    def display_info(self):
        print("Robot:", self.name)
        print("Battery:", self.battery)
        print("Temperature:", self.temperature)
        print("Speed:", self.speed)
        print("Position:", (self.x, self.y))
        print("Target:", (self.target_x, self.target_y))
        print("Health:", self.health_check())
        print()

    def consume_battery(self, amount):
        self.battery -= amount

        if self.battery < 0:
            self.battery = 0

    def move(self, dx, dy, environment):
        new_x = self.x + dx
        new_y = self.y + dy

        if not environment.is_inside(new_x, new_y):
            return "OUT_OF_BOUNDS"

        if environment.is_obstacle(new_x, new_y):
            return "COLLISION"

        self.x = new_x
        self.y = new_y

        self.consume_battery(1)

        return "MOVED"

    def scan(self, environment):
        return {
            "up": environment.distance_to_obstacle(
                self.x,
                self.y,
                "up"
            ),
            "down": environment.distance_to_obstacle(
                self.x,
                self.y,
                "down"
            ),
            "right": environment.distance_to_obstacle(
                self.x,
                self.y,
                "right"
            ),
            "left": environment.distance_to_obstacle(
                self.x,
                self.y,
                "left"
            )
        }

    def get_next_move(self, environment):
        if self.x == self.target_x and self.y == self.target_y:
            return "TARGET_REACHED"

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if abs(dx) >= abs(dy):
            if dx > 0:
                direction = "right"
                move = (1, 0)
            elif dx < 0:
                direction = "left"
                move = (-1, 0)
            elif dy > 0:
                direction = "up"
                move = (0, 1)
            else:
                direction = "down"
                move = (0, -1)
        else:
            if dy > 0:
                direction = "up"
                move = (0, 1)
            elif dy < 0:
                direction = "down"
                move = (0, -1)
            elif dx > 0:
                direction = "right"
                move = (1, 0)
            else:
                direction = "left"
                move = (-1, 0)

        sensors = self.scan(environment)

        if sensors[direction] == 1:
            return "BLOCKED"

        return move

    def find_alternative_move(self, environment):
        directions = [
            ("up", (0, 1)),
            ("down", (0, -1)),
            ("right", (1, 0)),
            ("left", (-1, 0))
        ]

        for direction, move in directions:
            distance = environment.distance_to_obstacle(
                self.x,
                self.y,
                direction
            )

            if distance != 1:
                return move

        return None

    def move_to_target(self, environment):
        next_move = self.get_next_move(environment)

        if next_move == "TARGET_REACHED":
            return "TARGET_REACHED"

        if next_move == "BLOCKED":
            next_move = self.find_alternative_move(environment)

            if next_move is None:
                return "BLOCKED"

        dx, dy = next_move

        return self.move(dx, dy, environment)

    def follow_path(self, path, environment):
        if path is None:
            return "NO_PATH"

        for position in path[1:]:
            dx = position[0] - self.x
            dy = position[1] - self.y

            result = self.move(
                dx,
                dy,
                environment
            )

            if result != "MOVED":
                return result

            print(
                self.name,
                "moved to",
                (self.x, self.y)
            )

        return "TARGET_REACHED"


class Task:
    def __init__(self, task_id, target_x, target_y):
        self.task_id = task_id
        self.target_x = target_x
        self.target_y = target_y

    def get_target(self):
        return (self.target_x, self.target_y)


class Fleet:
    def __init__(self):
        self.robots = []

    def add_robot(self, robot):
        self.robots.append(robot)

    def display_robots(self):
        for robot in self.robots:
            robot.display_info()

    def calculate_paths(self, environment):
        paths = {}

        for robot in self.robots:
            start = (robot.x, robot.y)
            target = (robot.target_x, robot.target_y)

            paths[robot.name] = environment.find_path(
                start,
                target
            )

        return paths

    def calculate_distance(self, robot, task):
        return abs(
            robot.x - task.target_x
        ) + abs(
            robot.y - task.target_y
        )

    def allocate_tasks(self, tasks):
        assignments = {}
        available_robots = self.robots.copy()

        for task in tasks:
            if not available_robots:
                break

            selected_robot = min(
                available_robots,
                key=lambda robot: self.calculate_distance(
                    robot,
                    task
                )
            )

            assignments[task.task_id] = selected_robot.name

            available_robots.remove(
                selected_robot
            )

        return assignments

    def get_blocked_positions(self, current_robot):
        blocked_positions = set()

        for robot in self.robots:
            if robot is current_robot:
                continue

            blocked_positions.add(
                (robot.x, robot.y)
            )

        return blocked_positions

    def replan_path(self, robot, environment):
        start = (robot.x, robot.y)
        target = (robot.target_x, robot.target_y)

        blocked_positions = self.get_blocked_positions(
            robot
        )

        return environment.find_path(
            start,
            target,
            blocked_positions
        )

    def is_position_occupied(self, position, current_robot):
        for robot in self.robots:
            if robot is current_robot:
                continue

            if (robot.x, robot.y) == position:
                return True

        return False

    def execute_paths(self, paths, environment):
        active_paths = dict(paths)

        path_indices = {
            robot.name: 1
            for robot in self.robots
        }

        max_steps = 100

        for step in range(1, max_steps + 1):
            print("Step", step)

            all_targets_reached = True

            for robot in self.robots:
                if (
                    robot.x == robot.target_x
                    and robot.y == robot.target_y
                ):
                    print(
                        robot.name,
                        "TARGET_REACHED"
                    )
                    continue

                all_targets_reached = False

                path = active_paths.get(
                    robot.name
                )

                if path is None:
                    print(
                        robot.name,
                        "NO_PATH"
                    )
                    continue

                path_index = path_indices[
                    robot.name
                ]

                if path_index >= len(path):
                    new_path = self.replan_path(
                        robot,
                        environment
                    )

                    if new_path is None:
                        print(
                            robot.name,
                            "NO_PATH"
                        )
                        continue

                    active_paths[
                        robot.name
                    ] = new_path

                    path_indices[
                        robot.name
                    ] = 1

                    path = new_path
                    path_index = 1

                next_position = path[
                    path_index
                ]

                if self.is_position_occupied(
                    next_position,
                    robot
                ):
                    print(
                        robot.name,
                        "ROBOT_COLLISION"
                    )

                    new_path = self.replan_path(
                        robot,
                        environment
                    )

                    if new_path is not None:
                        active_paths[
                            robot.name
                        ] = new_path

                        path_indices[
                            robot.name
                        ] = 1

                        print(
                            robot.name,
                            "REPLANNED"
                        )
                    else:
                        print(
                            robot.name,
                            "NO_PATH"
                        )

                    continue

                dx = (
                    next_position[0]
                    - robot.x
                )

                dy = (
                    next_position[1]
                    - robot.y
                )

                result = robot.move(
                    dx,
                    dy,
                    environment
                )

                if result == "MOVED":
                    path_indices[
                        robot.name
                    ] += 1

                    print(
                        robot.name,
                        "moved to",
                        (robot.x, robot.y)
                    )
                else:
                    print(
                        robot.name,
                        result
                    )

            print()

            if all_targets_reached:
                break


environment = Environment(
    10,
    10,
    [
        (2, 6),
        (4, 3),
        (4, 5),
        (6, 6),
        (8, 2)
    ]
)


robot1 = Robot(
    "Aegis-01",
    80,
    35,
    2.5,
    3,
    3,
    8,
    8
)

robot2 = Robot(
    "Aegis-02",
    60,
    40,
    2,
    5,
    3,
    1,
    8
)

robot3 = Robot(
    "Aegis-03",
    10,
    75,
    3.5,
    10,
    7,
    2,
    2
)


fleet = Fleet()

fleet.add_robot(robot1)
fleet.add_robot(robot2)
fleet.add_robot(robot3)


tasks = [
    Task("Task-01", 8, 8),
    Task("Task-02", 1, 8),
    Task("Task-03", 2, 2)
]


assignments = fleet.allocate_tasks(tasks)

print("Task Assignments:")
print()

for task_id, robot_name in assignments.items():
    print(
        task_id,
        "->",
        robot_name
    )

print()


paths = fleet.calculate_paths(
    environment
)

for robot_name, path in paths.items():
    print(
        robot_name,
        "Path:"
    )
    print(path)
    print()


print("Synchronized Fleet Execution:")
print()

fleet.execute_paths(
    paths,
    environment
)


print("Fleet Robots:")
fleet.display_robots()