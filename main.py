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
        else:
            blocked_positions = set(blocked_positions)

        queue = deque([start])
        visited = {start}
        previous = {}

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

                while node != start:
                    path.append(node)
                    node = previous[node]

                path.append(start)
                path.reverse()

                return path

            for dx, dy in directions:
                next_position = (
                    current[0] + dx,
                    current[1] + dy
                )

                if not self.is_inside(*next_position):
                    continue

                if self.is_obstacle(*next_position):
                    continue

                if next_position in blocked_positions:
                    continue

                if next_position in visited:
                    continue

                visited.add(next_position)
                previous[next_position] = current
                queue.append(next_position)

        return None


class Task:
    def __init__(self, task_id, target_x, target_y, priority=1):
        self.task_id = task_id
        self.target_x = target_x
        self.target_y = target_y
        self.priority = priority
        self.status = "PENDING"
        self.assigned_robot = None
        self.steps_taken = 0

    def get_target(self):
        return self.target_x, self.target_y


class Robot:
    def __init__(
        self,
        name,
        battery,
        temperature,
        speed,
        x,
        y
    ):
        self.name = name
        self.initial_battery = battery
        self.battery = battery
        self.temperature = temperature
        self.speed = speed
        self.x = x
        self.y = y
        self.initial_position = (x, y)
        self.target_x = None
        self.target_y = None
        self.status = "IDLE"
        self.current_task = None
        self.telemetry = []
        self.faults = []
        self.maintenance_required = False
        self.distance_travelled = 0
        self.active_steps = 0
        self.completed_tasks = 0

    def health_check(self):
        if self.battery <= 10 or self.temperature >= 80:
            return "CRITICAL"

        if self.battery <= 30 or self.temperature >= 60:
            return "WARNING"

        return "HEALTHY"

    def consume_battery(self, amount):
        self.battery = max(0, self.battery - amount)

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
        self.distance_travelled += abs(dx) + abs(dy)
        self.active_steps += 1

        self.record_telemetry()

        return "MOVED"

    def record_telemetry(self):
        self.telemetry.append({
            "position": (self.x, self.y),
            "battery": self.battery,
            "temperature": self.temperature,
            "speed": self.speed,
            "status": self.status
        })

    def display_info(self):
        print(
            self.name,
            "Position:",
            (self.x, self.y),
            "Battery:",
            self.battery,
            "Temperature:",
            self.temperature,
            "Status:",
            self.status,
            "Distance:",
            self.distance_travelled,
            "Tasks:",
            self.completed_tasks
        )


class FaultDetector:
    def __init__(self):
        self.fault_history = []

    def analyze_robot(self, robot):
        faults = []

        if robot.battery <= 10:
            faults.append("CRITICAL_BATTERY")
        elif robot.battery <= 30:
            faults.append("LOW_BATTERY")

        if robot.temperature >= 80:
            faults.append("CRITICAL_TEMPERATURE")
        elif robot.temperature >= 60:
            faults.append("HIGH_TEMPERATURE")

        if robot.speed <= 0:
            faults.append("MOTOR_FAILURE")

        for fault in faults:
            event = {
                "robot": robot.name,
                "fault": fault,
                "battery": robot.battery,
                "temperature": robot.temperature
            }

            if event not in self.fault_history:
                self.fault_history.append(event)

            if fault not in robot.faults:
                robot.faults.append(fault)

        if robot.battery <= 30 or robot.temperature >= 60:
            robot.maintenance_required = True

        if (
            robot.battery <= 10
            or robot.temperature >= 80
            or robot.speed <= 0
        ):
            robot.status = "FAILED"

        return faults

    def analyze_fleet(self, fleet):
        results = {}

        for robot in fleet.robots:
            results[robot.name] = self.analyze_robot(robot)

        return results

    def predict_maintenance(self, robot):
        if robot.temperature >= 70:
            return "URGENT"

        if robot.battery <= 20:
            return "URGENT"

        if robot.temperature >= 55:
            return "SOON"

        if robot.battery <= 40:
            return "SOON"

        if robot.faults:
            return "SOON"

        return "NORMAL"

    def display_faults(self):
        print("Fault History")

        if not self.fault_history:
            print("No faults detected.")
            return

        for event in self.fault_history:
            print(
                event["robot"],
                event["fault"],
                "Battery:",
                event["battery"],
                "Temperature:",
                event["temperature"]
            )


class Fleet:
    def __init__(self):
        self.robots = []
        self.tasks = []

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, task):
        self.tasks.append(task)

    def get_available_robots(self):
        return [
            robot
            for robot in self.robots
            if robot.status == "IDLE"
            and robot.health_check() != "CRITICAL"
            and not robot.maintenance_required
        ]

    def calculate_distance(self, robot, task):
        return (
            abs(robot.x - task.target_x)
            + abs(robot.y - task.target_y)
        )

    def calculate_robot_score(self, robot, task):
        distance_score = self.calculate_distance(
            robot,
            task
        )

        battery_score = (
            100 - robot.battery
        ) * 0.3

        speed_score = 10 / max(
            robot.speed,
            0.1
        )

        health_score = 0

        if robot.health_check() == "WARNING":
            health_score = 10

        return (
            distance_score
            + battery_score
            + speed_score
            + health_score
        )

    def allocate_tasks(self):
        pending_tasks = [
            task
            for task in self.tasks
            if task.status == "PENDING"
        ]

        pending_tasks.sort(
            key=lambda task: task.priority,
            reverse=True
        )

        for task in pending_tasks:
            available_robots = self.get_available_robots()

            if not available_robots:
                break

            robot = min(
                available_robots,
                key=lambda current_robot:
                self.calculate_robot_score(
                    current_robot,
                    task
                )
            )

            task.status = "ASSIGNED"
            task.assigned_robot = robot.name

            robot.status = "BUSY"
            robot.current_task = task
            robot.target_x = task.target_x
            robot.target_y = task.target_y

    def get_blocked_positions(self, current_robot):
        return [
            (robot.x, robot.y)
            for robot in self.robots
            if robot.name != current_robot.name
            and robot.status != "FAILED"
        ]

    def calculate_path(self, robot, environment):
        if robot.current_task is None:
            return None

        return environment.find_path(
            (robot.x, robot.y),
            (
                robot.current_task.target_x,
                robot.current_task.target_y
            ),
            self.get_blocked_positions(robot)
        )

    def complete_task(self, robot):
        if robot.current_task is None:
            return

        robot.current_task.status = "COMPLETED"
        robot.current_task.assigned_robot = robot.name
        robot.completed_tasks += 1

        robot.current_task = None
        robot.target_x = None
        robot.target_y = None
        robot.status = "IDLE"

    def fail_robot(self, robot):
        if robot.current_task is not None:
            robot.current_task.status = "PENDING"
            robot.current_task.assigned_robot = None

        robot.current_task = None
        robot.target_x = None
        robot.target_y = None
        robot.status = "FAILED"

    def has_pending_tasks(self):
        return any(
            task.status == "PENDING"
            for task in self.tasks
        )


class SimulationEngine:
    def __init__(
        self,
        environment,
        fleet,
        fault_detector,
        max_steps=100
    ):
        self.environment = environment
        self.fleet = fleet
        self.fault_detector = fault_detector
        self.max_steps = max_steps
        self.current_step = 0

    def run(self):
        paths = {}
        path_indices = {}

        for step in range(self.max_steps):
            self.current_step = step + 1

            self.fault_detector.analyze_fleet(
                self.fleet
            )

            for robot in self.fleet.robots:
                if robot.status == "FAILED":
                    self.fleet.fail_robot(robot)

            self.fleet.allocate_tasks()

            active = False

            for robot in self.fleet.robots:
                if robot.status != "BUSY":
                    continue

                active = True

                if robot.current_task is None:
                    continue

                robot.current_task.steps_taken += 1

                path = paths.get(robot.name)

                if path is None:
                    path = self.fleet.calculate_path(
                        robot,
                        self.environment
                    )

                    paths[robot.name] = path
                    path_indices[robot.name] = 1

                if path is None:
                    self.fleet.fail_robot(robot)
                    paths[robot.name] = None
                    continue

                index = path_indices[robot.name]

                if index >= len(path):
                    self.fleet.complete_task(robot)
                    paths[robot.name] = None
                    continue

                next_position = path[index]

                if next_position in self.fleet.get_blocked_positions(robot):
                    paths[robot.name] = self.fleet.calculate_path(
                        robot,
                        self.environment
                    )

                    path_indices[robot.name] = 1
                    continue

                dx = next_position[0] - robot.x
                dy = next_position[1] - robot.y

                result = robot.move(
                    dx,
                    dy,
                    self.environment
                )

                if result == "MOVED":
                    path_indices[robot.name] += 1

                self.fault_detector.analyze_robot(
                    robot
                )

                if robot.status == "FAILED":
                    self.fleet.fail_robot(robot)
                    paths[robot.name] = None
                    continue

                if (
                    robot.x == robot.target_x
                    and robot.y == robot.target_y
                ):
                    self.fleet.complete_task(robot)
                    paths[robot.name] = None

            if not active and not self.fleet.has_pending_tasks():
                break

        return self.current_step


class SimulationReport:
    def __init__(self, fleet, fault_detector, steps):
        self.fleet = fleet
        self.fault_detector = fault_detector
        self.steps = steps

    def completed_tasks(self):
        return sum(
            task.status == "COMPLETED"
            for task in self.fleet.tasks
        )

    def pending_tasks(self):
        return sum(
            task.status == "PENDING"
            for task in self.fleet.tasks
        )

    def assigned_tasks(self):
        return sum(
            task.status == "ASSIGNED"
            for task in self.fleet.tasks
        )

    def success_rate(self):
        total = len(self.fleet.tasks)

        if total == 0:
            return 0

        return (
            self.completed_tasks()
            / total
        ) * 100

    def total_distance(self):
        return sum(
            robot.distance_travelled
            for robot in self.fleet.robots
        )

    def total_battery_used(self):
        return sum(
            robot.initial_battery - robot.battery
            for robot in self.fleet.robots
        )

    def failed_robots(self):
        return sum(
            robot.status == "FAILED"
            for robot in self.fleet.robots
        )

    def maintenance_robots(self):
        return sum(
            robot.maintenance_required
            for robot in self.fleet.robots
        )

    def display(self):
        print()
        print("========== SIMULATION REPORT ==========")
        print("Simulation Steps:", self.steps)
        print("Total Tasks:", len(self.fleet.tasks))
        print("Completed Tasks:", self.completed_tasks())
        print("Assigned Tasks:", self.assigned_tasks())
        print("Pending Tasks:", self.pending_tasks())
        print(
            "Success Rate:",
            round(self.success_rate(), 2),
            "%"
        )
        print(
            "Total Distance:",
            self.total_distance()
        )
        print(
            "Total Battery Used:",
            self.total_battery_used()
        )
        print(
            "Fault Events:",
            len(self.fault_detector.fault_history)
        )
        print(
            "Failed Robots:",
            self.failed_robots()
        )
        print(
            "Maintenance Required:",
            self.maintenance_robots()
        )

        print()
        print("Robot Performance")

        for robot in self.fleet.robots:
            maintenance = (
                self.fault_detector.predict_maintenance(
                    robot
                )
            )

            print(
                robot.name,
                "| Status:",
                robot.status,
                "| Battery:",
                robot.battery,
                "| Distance:",
                robot.distance_travelled,
                "| Tasks:",
                robot.completed_tasks,
                "| Maintenance:",
                maintenance
            )

        print()
        print("Task Results")

        for task in self.fleet.tasks:
            print(
                task.task_id,
                "| Status:",
                task.status,
                "| Robot:",
                task.assigned_robot,
                "| Steps:",
                task.steps_taken
            )

        print()
        print("Fault History")

        if not self.fault_detector.fault_history:
            print("No faults detected.")
        else:
            for event in self.fault_detector.fault_history:
                print(
                    event["robot"],
                    "|",
                    event["fault"],
                    "| Battery:",
                    event["battery"],
                    "| Temperature:",
                    event["temperature"]
                )

        print("=======================================")


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
    3
)

robot2 = Robot(
    "Aegis-02",
    60,
    40,
    2,
    5,
    3
)

robot3 = Robot(
    "Aegis-03",
    25,
    65,
    3.5,
    10,
    7
)

fleet = Fleet()

fleet.add_robot(robot1)
fleet.add_robot(robot2)
fleet.add_robot(robot3)

fleet.add_task(
    Task("Task-01", 8, 8, 3)
)

fleet.add_task(
    Task("Task-02", 1, 8, 2)
)

fleet.add_task(
    Task("Task-03", 2, 2, 1)
)

fleet.add_task(
    Task("Task-04", 9, 9, 2)
)

fleet.add_task(
    Task("Task-05", 1, 1, 1)
)

fault_detector = FaultDetector()

simulation = SimulationEngine(
    environment,
    fleet,
    fault_detector,
    max_steps=100
)

steps = simulation.run()

report = SimulationReport(
    fleet,
    fault_detector,
    steps
)

report.display()
