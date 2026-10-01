import csv


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def create_features(rows):
    features = []
    previous = {}

    for row in rows:
        key = (row["run"], row["robot"])

        battery = float(row["battery"])
        temperature = float(row["temperature"])
        speed = float(row["speed"])
        x = int(row["x"])
        y = int(row["y"])

        if key in previous:
            battery_drop = max(
                0,
                previous[key]["battery"] - battery
            )

            temperature_change = (
                temperature - previous[key]["temperature"]
            )
        else:
            battery_drop = 0
            temperature_change = 0

        features.append({
            "run": row["run"],
            "step": row["step"],
            "scenario": row["scenario"],
            "robot": row["robot"],
            "x": x,
            "y": y,
            "battery": battery,
            "temperature": temperature,
            "speed": speed,
            "battery_drop": battery_drop,
            "temperature_change": temperature_change,
            "status": row["status"],
            "fault_label": row["fault_label"]
        })

        previous[key] = {
            "battery": battery,
            "temperature": temperature
        }

    return features


def save_features(rows, filename):
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
    "data/telemetry.csv"
)

features = create_features(rows)

save_features(
    features,
    "data/labeled_features.csv"
)

print("Feature engineering completed.")
print("Total feature records:", len(features))