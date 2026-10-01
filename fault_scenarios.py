import csv


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def classify_fault(row):
    battery = float(row["battery"])
    temperature = float(row["temperature"])
    speed = float(row["speed"])
    battery_drop = float(row["battery_drop"])
    temperature_change = float(row["temperature_change"])

    if battery <= 10:
        return "CRITICAL_BATTERY"

    if temperature >= 80:
        return "CRITICAL_TEMPERATURE"

    if speed <= 0:
        return "MOTOR_FAILURE"

    if battery <= 30:
        return "LOW_BATTERY"

    if temperature >= 60:
        return "HIGH_TEMPERATURE"

    if battery_drop >= 2:
        return "BATTERY_DEGRADATION"

    if temperature_change >= 1:
        return "TEMPERATURE_SPIKE"

    return "NORMAL"


def label_data(rows):
    labeled_rows = []

    for row in rows:
        labeled_row = row.copy()
        labeled_row["fault_label"] = classify_fault(row)
        labeled_rows.append(labeled_row)

    return labeled_rows


def save_data(rows, filename):
    if not rows:
        return

    fieldnames = rows[0].keys()

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def display_distribution(rows):
    distribution = {}

    for row in rows:
        label = row["fault_label"]
        distribution[label] = distribution.get(label, 0) + 1

    print("Fault Label Distribution")
    print("------------------------")

    for label, count in distribution.items():
        print(label, ":", count)


rows = load_data("data/features.csv")

labeled_rows = label_data(rows)

save_data(
    labeled_rows,
    "data/labeled_features.csv"
)

display_distribution(labeled_rows)

print()
print("Labeled dataset created.")
print("Total records:", len(labeled_rows))