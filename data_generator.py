import csv
import random

from main import Environment, Task, Robot, Fleet, FaultDetector, SimulationEngine


def create_simulation(scenario):
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
        random.randint(80, 100),
        random.randint(30, 40),
        random.uniform(2.0, 3.0),
        3,
        3
    )

    robot2 = Robot(
        "Aegis-02",
        random.randint(70, 90),
        random.randint(30, 40),
        random.uniform(2.0, 3.0),
        5,
        3
    )

    robot3 = Robot(
        "Aegis-03",
        random.randint(80, 100),
        random.randint(30, 40),
        random.uniform(2.0, 3.0),
        10,
        7
    )

    fleet.add_robot(robot1)
    fleet.add_robot(robot2)
    fleet.add_robot(robot3)

    tasks = [
        ("Task-01", 8, 8, 3),
        ("Task-02", 1, 8, 2),
        ("Task-03", 2, 2, 1),
        ("Task-04", 9, 9, 2),
        ("Task-05", 1, 1, 1)
    ]

    for task_id, x, y, priority in tasks:
        fleet.add_task(
            Task(task_id, x, y, priority)
        )

    for robot in fleet.robots:
        robot.record_telemetry()

    fault_detector = FaultDetector()

    simulation = SimulationEngine(
        environment,
        fleet,
        fault_detector,
        max_steps=100
    )

    simulation.run()

    return fleet


def apply_progressive_degradation(robot, scenario, step):
    if robot.name != "Aegis-02":
        return

    if scenario == "BATTERY_DEGRADATION":
        robot.battery = max(
            0,
            robot.battery - 0.8
        )

    elif scenario == "CRITICAL_BATTERY":
        robot.battery = max(
            0,
            robot.battery - 1.2
        )

    elif scenario == "LOW_BATTERY":
        robot.battery = max(
            0,
            robot.battery - 0.9
        )

    elif scenario == "TEMPERATURE_SPIKE":
        robot.temperature += 0.7

    elif scenario == "HIGH_TEMPERATURE":
        robot.temperature += 0.9

    elif scenario == "MOTOR_FAILURE":
        if step >= 25:
            robot.speed = max(
                0,
                robot.speed - 0.15
            )


def collect_data(runs):
    rows = []

    scenarios = [
        "NORMAL",
        "LOW_BATTERY",
        "CRITICAL_BATTERY",
        "HIGH_TEMPERATURE",
        "TEMPERATURE_SPIKE",
        "MOTOR_FAILURE",
        "BATTERY_DEGRADATION"
    ]

    for run_id in range(1, runs + 1):
        scenario = scenarios[
            (run_id - 1) % len(scenarios)
        ]

        fleet = create_simulation(scenario)

        for robot in fleet.robots:
            robot.telemetry = []

            robot.record_telemetry()

            for step in range(100):
                if robot.status == "FAILED":
                    break

                apply_progressive_degradation(
                    robot,
                    scenario,
                    step
                )

                if step > 0:
                    robot.record_telemetry()

                if (
                    robot.battery <= 10
                    or robot.temperature >= 80
                    or robot.speed <= 0
                ):
                    robot.status = "FAILED"

                if robot.status == "FAILED":
                    robot.record_telemetry()
                    break

            robot_label = (
                scenario
                if robot.name == "Aegis-02"
                else "NORMAL"
            )

            for step, telemetry in enumerate(
                robot.telemetry
            ):
                rows.append({
                    "run": run_id,
                    "step": step,
                    "scenario": scenario,
                    "robot": robot.name,
                    "x": telemetry["position"][0],
                    "y": telemetry["position"][1],
                    "battery": telemetry["battery"],
                    "temperature": telemetry["temperature"],
                    "speed": telemetry["speed"],
                    "status": telemetry["status"],
                    "fault_label": robot_label
                })

    return rows


def save_data(rows):
    filename = "data/telemetry.csv"

    if not rows:
        return

    fieldnames = rows[0].keys()

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


rows = collect_data(70)

save_data(rows)

print("Progressive dataset generation completed.")
print("Total telemetry records:", len(rows))