import csv


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def analyze(rows):
    anomalies = [
        row for row in rows
        if row["anomaly"] == "ANOMALY"
    ]

    low_battery = [
        row for row in anomalies
        if float(row["battery"]) <= 30
    ]

    high_temperature = [
        row for row in anomalies
        if float(row["temperature"]) >= 60
    ]

    high_battery_drop = [
        row for row in anomalies
        if float(row["battery_drop"]) > 1
    ]

    temperature_rise = [
        row for row in anomalies
        if float(row["temperature_change"]) > 0
    ]

    robots = {}

    for row in anomalies:
        robot = row["robot"]
        robots[robot] = robots.get(robot, 0) + 1

    return (
        anomalies,
        low_battery,
        high_temperature,
        high_battery_drop,
        temperature_rise,
        robots
    )


def display_results(
    anomalies,
    low_battery,
    high_temperature,
    high_battery_drop,
    temperature_rise,
    robots
):
    print("Anomaly Analysis")
    print("----------------")
    print("Total anomalies:", len(anomalies))
    print("Low battery anomalies:", len(low_battery))
    print("High temperature anomalies:", len(high_temperature))
    print("High battery drop anomalies:", len(high_battery_drop))
    print("Temperature rise anomalies:", len(temperature_rise))

    print()
    print("Anomalies by robot")

    for robot, count in robots.items():
        print(robot, ":", count)


rows = load_data("data/anomalies.csv")

results = analyze(rows)

display_results(*results)