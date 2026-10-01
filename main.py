from collections import deque

from maintenance_risk import MaintenanceRiskModel
from live_risk import LiveRiskCalculator


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
        self.failure_probability = 0.0
        self.maintenance_risk = "LOW"

    def health_check(self):
        if self.battery <= 10 or self.temperature >= 80:
            return "CRITICAL"

        if self.battery <= 30 or self.temperature >= 60:
            return "WARNING"

        return "HEALTHY"

    def consume_battery(self, amount):
        self.battery = max(0, self.battery - amount)

    def update_temperature(self):
        temperature_increase = self.speed * 0.4
        self.temperature += temperature_increase

        if self.temperature > 40:
            self.temperature -= 0.05

    def move(self, dx, dy, environment):
        new_x = self.x + dx
        new_y = self.y + dy

        if not environment.is_inside(new_x, new_y):
            return "OUT_OF_BOUNDS"

        if environment.is_obstacle(new_x, new_y):
            return "COLLISION"

        self.x = new_x
        self.y = new_y

        battery_consumption = max(
            1,
            round(self.speed * 0.5)
        )

        self.consume_battery(
            battery_consumption
        )

        self.update_temperature()

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
            self.completed_tasks,
            "Risk:",
            self.maintenance_risk,
            "Failure Probability:",
            round(
                self.failure_probability,
                3
            )
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
        and robot.current_task is None
        and robot.maintenance_risk != "HIGH"
    ]

    def calculate_distance(self, robot, task):
        return abs(robot.x - task.target_x) + abs(
            robot.y - task.target_y
        )

    def calculate_robot_score(self, robot, task):
        distance_score = self.calculate_distance(
            robot,
            task
        )

        battery_score = (
            (100 - robot.battery) * 0.3
        )

        speed_score = (
            10 / max(robot.speed, 0.1)
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

            available_robots.sort(
                key=lambda robot: self.calculate_robot_score(
                    robot,
                    task
                )
            )

            robot = available_robots[0]

            task.assigned_robot = robot.name
            task.status = "ASSIGNED"

            robot.current_task = task
            robot.target_x = task.target_x
            robot.target_y = task.target_y
            robot.status = "BUSY"

    def get_blocked_positions(self, robot):
        return {
            (other.x, other.y)
            for other in self.robots
            if other.name != robot.name
            and other.status != "FAILED"
        }

    def calculate_path(self, robot, environment):
        if robot.current_task is None:
            return None

        start = (robot.x, robot.y)
        target = robot.current_task.get_target()

        blocked_positions = self.get_blocked_positions(
            robot
        )

        blocked_positions.discard(target)

        return environment.find_path(
            start,
            target,
            blocked_positions
        )

    def complete_task(self, robot):
        task = robot.current_task

        if task is None:
            return

        task.status = "COMPLETED"
        task.steps_taken = robot.active_steps
        robot.completed_tasks += 1

        robot.current_task = None
        robot.target_x = None
        robot.target_y = None
        robot.status = "IDLE"

    def fail_robot(self, robot):
        robot.status = "FAILED"

        if robot.current_task is not None:
            robot.current_task.status = "PENDING"
            robot.current_task.assigned_robot = None
            robot.current_task = None

        robot.target_x = None
        robot.target_y = None

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
        max_steps=100,
        risk_model=None
    ):
        self.environment = environment
        self.fleet = fleet
        self.fault_detector = fault_detector
        self.max_steps = max_steps
        self.current_step = 0
        self.risk_calculator = None

        if risk_model is not None:
            self.risk_calculator = LiveRiskCalculator(
                risk_model
            )

    def update_risk(self, robot):
        if self.risk_calculator is None:
            return

        result = self.risk_calculator.predict(
            robot
        )

        if result is None:
            return

        robot.failure_probability = result[
            "probability"
        ]

        robot.maintenance_risk = result[
            "risk"
        ]

    def update_fleet_risk(self):
        for robot in self.fleet.robots:
            self.update_risk(robot)

    def run(self):
        for robot in self.fleet.robots:
            robot.record_telemetry()

        self.update_fleet_risk()

        for step in range(self.max_steps):
            self.current_step = step + 1

            self.fault_detector.analyze_fleet(
                self.fleet
            )

            for robot in self.fleet.robots:
                if robot.status == "FAILED":
                    self.fleet.fail_robot(robot)

            self.fleet.allocate_tasks()

            active_robots = 0

            for robot in self.fleet.robots:
                if (
                    robot.status != "BUSY"
                    or robot.current_task is None
                ):
                    continue

                active_robots += 1

                path = self.fleet.calculate_path(
                    robot,
                    self.environment
                )

                if path is None:
                    continue

                if len(path) <= 1:
                    self.fleet.complete_task(
                        robot
                    )
                    continue

                next_position = path[1]

                dx = next_position[0] - robot.x
                dy = next_position[1] - robot.y

                result = robot.move(
                    dx,
                    dy,
                    self.environment
                )

                if result != "MOVED":
                    continue

                if (
                    robot.x,
                    robot.y
                ) == robot.current_task.get_target():
                    self.fleet.complete_task(
                        robot
                    )

                self.update_risk(robot)

            self.fault_detector.analyze_fleet(
                self.fleet
            )

            for robot in self.fleet.robots:
                if robot.status == "FAILED":
                    self.fleet.fail_robot(robot)

            self.update_fleet_risk()

            if (
                not self.fleet.has_pending_tasks()
                and active_robots == 0
            ):
                break

        return self.current_step


class SimulationReport:
    def __init__(
        self,
        fleet,
        fault_detector,
        steps
    ):
        self.fleet = fleet
        self.fault_detector = fault_detector
        self.steps = steps

    def completed_tasks(self):
        return [
            task
            for task in self.fleet.tasks
            if task.status == "COMPLETED"
        ]

    def pending_tasks(self):
        return [
            task
            for task in self.fleet.tasks
            if task.status == "PENDING"
        ]

    def assigned_tasks(self):
        return [
            task
            for task in self.fleet.tasks
            if task.status == "ASSIGNED"
        ]

    def success_rate(self):
        total = len(self.fleet.tasks)

        if total == 0:
            return 0

        return (
            len(self.completed_tasks())
            / total
            * 100
        )

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
        return [
            robot
            for robot in self.fleet.robots
            if robot.status == "FAILED"
        ]

    def maintenance_robots(self):
        return [
            robot
            for robot in self.fleet.robots
            if robot.maintenance_required
            or robot.maintenance_risk in [
                "MEDIUM",
                "HIGH"
            ]
        ]

    def display(self):
        print()
        print("Simulation Report")
        print("-----------------")
        print("Simulation steps:", self.steps)
        print("Total tasks:", len(self.fleet.tasks))
        print(
            "Completed tasks:",
            len(self.completed_tasks())
        )
        print(
            "Assigned tasks:",
            len(self.assigned_tasks())
        )
        print(
            "Pending tasks:",
            len(self.pending_tasks())
        )
        print(
            "Success rate:",
            round(self.success_rate(), 2),
            "%"
        )
        print(
            "Total distance:",
            self.total_distance()
        )
        print(
            "Total battery used:",
            self.total_battery_used()
        )

        print()
        print("Predictive Maintenance")

        for robot in self.fleet.robots:
            print(
                robot.name,
                "Probability:",
                round(
                    robot.failure_probability,
                    3
                ),
                "Risk:",
                robot.maintenance_risk
            )

        print()
        print(
            "Fault events:",
            len(
                self.fault_detector.fault_history
            )
        )

        print(
            "Failed robots:",
            len(self.failed_robots())
        )

        print(
            "Maintenance required:",
            len(self.maintenance_robots())
        )

        print()
        print("Robot Performance")

        for robot in self.fleet.robots:
            robot.display_info()

        print()
        print("Task Results")

        for task in self.fleet.tasks:
            print(
                task.task_id,
                "Status:",
                task.status,
                "Robot:",
                task.assigned_robot
            )

        print()
        self.fault_detector.display_faults()


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

fleet = Fleet()

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

risk_model = MaintenanceRiskModel()

risk_model.train(
    "data/predictive_features.csv"
)

simulation = SimulationEngine(
    environment,
    fleet,
    fault_detector,
    max_steps=100,
    risk_model=risk_model
)

steps = simulation.run()

report = SimulationReport(
    fleet,
    fault_detector,
    steps
)

report.display()