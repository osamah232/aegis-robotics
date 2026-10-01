import csv

from sklearn.ensemble import RandomForestClassifier


class MaintenanceRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42
        )

    def load_data(self, filename):
        with open(filename, "r", newline="") as file:
            return list(csv.DictReader(file))

    def prepare_data(self, rows):
        features = []
        labels = []

        for row in rows:
            features.append([
                float(row["battery"]),
                float(row["temperature"]),
                float(row["speed"]),
                float(row["battery_mean"]),
                float(row["temperature_mean"]),
                float(row["speed_mean"]),
                float(row["battery_drop_mean"]),
                float(row["temperature_change_mean"]),
                float(row["temperature_max"]),
                float(row["battery_min"])
            ])

            labels.append(
                int(row["failure_within_next_10_steps"])
            )

        return features, labels

    def train(self, filename):
        rows = self.load_data(filename)

        features, labels = self.prepare_data(rows)

        self.model.fit(
            features,
            labels
        )

    def predict_risk(self, row):
        features = [[
            float(row["battery"]),
            float(row["temperature"]),
            float(row["speed"]),
            float(row["battery_mean"]),
            float(row["temperature_mean"]),
            float(row["speed_mean"]),
            float(row["battery_drop_mean"]),
            float(row["temperature_change_mean"]),
            float(row["temperature_max"]),
            float(row["battery_min"])
        ]]

        probability = self.model.predict_proba(
            features
        )[0][1]

        if probability >= 0.8:
            risk = "HIGH"
        elif probability >= 0.4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return probability, risk