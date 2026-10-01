import csv


WINDOW_SIZE = 10


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def group_by_robot(rows):
    groups = {}

    for row in rows:
        key = (row["run"], row["robot"])

        if key not in groups:
            groups[key] = []

        groups[key].append(row)

    return groups


def calculate_features(window):
    batteries = [
        float(row["battery"])
        for row in window
    ]

    temperatures = [
        float(row["temperature"])
        for row in window
    ]

    speeds = [
        float(row["speed"])
        for row in window
    ]

    battery_drops = [
        float(row["battery_drop"])
        for row in window
    ]

    temperature_changes = [
        float(row["temperature_change"])
        for row in window
    ]

    return {
        "battery": batteries[-1],
        "temperature": temperatures[-1],
        "speed": speeds[-1],
        "battery_mean": sum(batteries) / len(batteries),
        "temperature_mean": sum(temperatures) / len(temperatures),
        "speed_mean": sum(speeds) / len(speeds),
        "battery_drop_mean": sum(battery_drops) / len(battery_drops),
        "temperature_change_mean": sum(temperature_changes) / len(temperature_changes),
        "temperature_max": max(temperatures),
        "battery_min": min(batteries)
    }


def create_predictive_features(rows):
    groups = group_by_robot(rows)

    results = []

    for (run, robot), robot_rows in groups.items():
        robot_rows.sort(
            key=lambda row: int(row["step"])
        )

        for index in range(WINDOW_SIZE, len(robot_rows)):
            window = robot_rows[
                index - WINDOW_SIZE:index
            ]

            future_rows = robot_rows[index:]

            failure_within_window = any(
                row["status"] == "FAILED"
                for row in future_rows[:WINDOW_SIZE]
            )

            features = calculate_features(window)

            result = {
                "run": run,
                "robot": robot,
                "step": robot_rows[index]["step"],
                "failure_within_next_10_steps": int(
                    failure_within_window
                )
            }

            result.update(features)

            results.append(result)

    return results


def save_data(rows, filename):
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


rows = load_data(
    "data/labeled_features.csv"
)

predictive_rows = create_predictive_features(
    rows
)

save_data(
    predictive_rows,
    "data/predictive_features.csv"
)

failure_count = sum(
    row["failure_within_next_10_steps"] == 1
    for row in predictive_rows
)

normal_count = sum(
    row["failure_within_next_10_steps"] == 0
    for row in predictive_rows
)

print("Predictive feature engineering completed.")
print("Total records:", len(predictive_rows))
print("Failure within next 10 steps:", failure_count)
print("No failure within next 10 steps:", normal_count)