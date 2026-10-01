import csv


class DataCollector:
    def __init__(self, filename):
        self.filename = filename

    def collect_robot_data(self, robots):
        rows = []

        for robot in robots:
            for telemetry in robot.telemetry:
                rows.append({
                    "robot": robot.name,
                    "x": telemetry["position"][0],
                    "y": telemetry["position"][1],
                    "battery": telemetry["battery"],
                    "temperature": telemetry["temperature"],
                    "speed": telemetry["speed"],
                    "status": telemetry["status"]
                })

        return rows

    def save(self, rows):
        if not rows:
            return

        fieldnames = rows[0].keys()

        with open(self.filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)