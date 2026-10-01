import csv

from sklearn.ensemble import IsolationForest


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def prepare_features(rows):
    data = []

    for row in rows:
        data.append([
            float(row["battery"]),
            float(row["temperature"]),
            float(row["speed"]),
            float(row["battery_drop"]),
            float(row["temperature_change"])
        ])

    return data


def detect_anomalies(rows, data):
    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )

    predictions = model.fit_predict(data)
    scores = model.decision_function(data)

    results = []

    for row, prediction, score in zip(
        rows,
        predictions,
        scores
    ):
        result = row.copy()

        result["anomaly_score"] = round(float(score), 4)
        result["anomaly"] = (
            "ANOMALY"
            if prediction == -1
            else "NORMAL"
        )

        results.append(result)

    return results


def save_results(rows, filename):
    if not rows:
        return

    fieldnames = rows[0].keys()

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


rows = load_data("data/features.csv")

data = prepare_features(rows)

results = detect_anomalies(rows, data)

save_results(
    results,
    "data/anomalies.csv"
)

anomaly_count = sum(
    1 for row in results
    if row["anomaly"] == "ANOMALY"
)

print("Anomaly detection completed.")
print("Total records:", len(results))
print("Anomalies detected:", anomaly_count)