class Environment:
    def __init__(self, width, height, obstacles):
        self.width = width
        self.height = height
        self.obstacles = obstacles

    def is_inside(self, x, y):
        return 0 <= x <= self.width and 0 <= y <= self.height

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def distance_to_obstacle(self, x, y, direction):
        distance = 0

        if direction == "up":
            for current_y in range(y + 1, self.height + 1):
                distance += 1
                if self.is_obstacle(x, current_y):
                    return distance

        elif direction == "down":
            for current_y in range(y - 1, -1, -1):
                distance += 1
                if self.is_obstacle(x, current_y):
                    return distance

        elif direction == "right":
            for current_x in range(x + 1, self.width + 1):
                distance += 1
                if self.is_obstacle(current_x, y):
                    return distance

        elif direction == "left":
            for current_x in range(x - 1, -1, -1):
                distance += 1
                if self.is_obstacle(current_x, y):
                    return distance

        return None


class Robot:
    def __init__(self, name, battery, temperature, speed, x, y):
        self.name = name
        self.battery = battery
        self.temperature = temperature
        self.speed = speed
        self.x = x
        self.y = y

    def health_check(self):
        status = "HEALTHY"

        if self.battery < 20:
            status = "CRITICAL"
        elif self.battery < 40:
            status = "WARNING"

        if self.temperature > 70:
            status = "CRITICAL"
        elif self.temperature > 50 and status != "CRITICAL":
            status = "WARNING"

        if self.speed > 3:
            status = "CRITICAL"
        elif self.speed > 2.5 and status != "CRITICAL":
            status = "WARNING"

        return status

    def display_info(self):
        print("Robot:", self.name)
        print("Battery:", self.battery, "%")
        print("Temperature:", self.temperature, "°C")
        print("Speed:", self.speed, "m/s")
        print("Position:", "(", self.x, ",", self.y, ")")

        status = self.health_check()
        print("Status:", status)

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
        sensors = {
            "up": environment.distance_to_obstacle(self.x, self.y, "up"),
            "down": environment.distance_to_obstacle(self.x, self.y, "down"),
            "right": environment.distance_to_obstacle(self.x, self.y, "right"),
            "left": environment.distance_to_obstacle(self.x, self.y, "left")
        }

        return sensors


environment = Environment(
    10,
    10,
    [
        (2, 6),
        (4, 5),
        (6, 6),
        (8, 2)
    ]
)

robot1 = Robot("Aegis-01", 80, 35, 2.5, 0, 0)
robot2 = Robot("Aegis-02", 60, 40, 2, 5, 3)
robot3 = Robot("Aegis-03", 10, 75, 3.5, 10, 7)

robots = [robot1, robot2, robot3]

for robot in robots:
    robot.consume_battery(10)

result1 = robot1.move(2, 3, environment)
result2 = robot2.move(-1, 2, environment)
result3 = robot3.move(3, -2, environment)

print("Aegis-01:", result1)
print("Aegis-02:", result2)
print("Aegis-03:", result3)

print()
print("Aegis-01 Sensor:")
sensor_data = robot1.scan(environment)
print(sensor_data)

for robot in robots:
    print()
    robot.display_info()