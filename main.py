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
        distance = 0

        if direction == "up":
            while self.is_inside(x, y + distance + 1):
                if self.is_obstacle(x, y + distance + 1):
                    return distance + 1
                distance += 1

        elif direction == "down":
            while self.is_inside(x, y - distance - 1):
                if self.is_obstacle(x, y - distance - 1):
                    return distance + 1
                distance += 1

        elif direction == "right":
            while self.is_inside(x + distance + 1, y):
                if self.is_obstacle(x + distance + 1, y):
                    return distance + 1
                distance += 1

        elif direction == "left":
            while self.is_inside(x - distance - 1, y):
                if self.is_obstacle(x - distance - 1, y):
                    return distance + 1
                distance += 1

        return None

    def find_path(self, start, target):
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
                break

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

                visited.add(next_position)
                previous[next_position] = current
                queue.append(next_position)

        if target not in visited:
            return None

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()

        return path


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
        if self.battery <= 10 or self.temperature >= 70:
            return "CRITICAL"

        if self.battery <= 30 or self.temperature >= 60:
            return "WARNING"

        return "HEALTHY"

    def display_info(self):
        print(f"Robot: {self.name}")
        print(f"Battery: {self.battery} %")
        print(f"Temperature: {self.temperature} °C")
        print(f"Speed: {self.speed} m/s")
        print(f"Position: ( {self.x} , {self.y} )")
        print(f"Target: ( {self.target_x} , {self.target_y} )")
        print(f"Status: {self.health_check()}")
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

        dx = 0
        dy = 0

        if self.x < self.target_x:
            dx = 1
        elif self.x > self.target_x:
            dx = -1

        if self.y < self.target_y:
            dy = 1
        elif self.y > self.target_y:
            dy = -1

        sensor = self.scan(environment)

        if dx == 1 and sensor["right"] == 1:
            return "BLOCKED"

        if dx == -1 and sensor["left"] == 1:
            return "BLOCKED"

        if dy == 1 and sensor["up"] == 1:
            return "BLOCKED"

        if dy == -1 and sensor["down"] == 1:
            return "BLOCKED"

        return dx, dy

    def find_alternative_move(self, environment):
        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            if not environment.is_inside(new_x, new_y):
                continue

            if environment.is_obstacle(new_x, new_y):
                continue

            return dx, dy

        return None

    def move_to_target(self, environment):
        next_move = self.get_next_move(environment)

        if next_move == "TARGET_REACHED":
            return "TARGET_REACHED"

        if next_move == "BLOCKED":
            next_move = self.find_alternative_move(environment)

            if next_move is None:
                return "NO_AVAILABLE_MOVE"

        dx, dy = next_move

        return self.move(dx, dy, environment)

    def follow_path(self, path, environment):
        if path is None:
            return "NO_PATH"

        for position in path[1:]:
            dx = position[0] - self.x
            dy = position[1] - self.y

            result = self.move(dx, dy, environment)

            if result != "MOVED":
                return result

            print(
                f"{self.name} moved to "
                f"( {self.x} , {self.y} )"
            )

        if self.x == self.target_x and self.y == self.target_y:
            return "TARGET_REACHED"

        return "PATH_INCOMPLETE"


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

robot1.consume_battery(10)
robot2.consume_battery(10)
robot3.consume_battery(15)

result2 = robot2.move(-1, 2, environment)
result3 = robot3.move(3, -2, environment)

print("Aegis-02:", result2)
print("Aegis-03:", result3)
print()

print("Aegis-01 Sensor:")
print(robot1.scan(environment))
print()

print("Aegis-01 Next Move:")
print(robot1.get_next_move(environment))
print()

print("Aegis-01 Move To Target:")
print(robot1.move_to_target(environment))
print()

path = environment.find_path(
    (robot1.x, robot1.y),
    (robot1.target_x, robot1.target_y)
)

print("Aegis-01 Path:")
print(path)
print()

print("Aegis-01 Follow Path:")
print(robot1.follow_path(path, environment))
print()

print("BFS Test 1:")
test_path_1 = environment.find_path(
    (1, 1),
    (10, 10)
)
print(test_path_1)
print()

print("BFS Test 2:")
test_path_2 = environment.find_path(
    (1, 1),
    (8, 8)
)
print(test_path_2)
print()

blocked_environment = Environment(
    5,
    5,
    [
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5)
    ]
)

print("BFS Test 3:")
test_path_3 = blocked_environment.find_path(
    (1, 3),
    (3, 3)
)
print(test_path_3)
print()

robot1.display_info()
robot2.display_info()
robot3.display_info()