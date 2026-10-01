import csv

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)
from sklearn.model_selection import train_test_split


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def prepare_data(rows):
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


rows = load_data(
    "data/predictive_features.csv"
)

features, labels = prepare_data(rows)

x_train, x_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42
)

model.fit(
    x_train,
    y_train
)

predictions = model.predict(x_test)
probabilities = model.predict_proba(x_test)[:, 1]

accuracy = accuracy_score(
    y_test,
    predictions
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

print("Predictive Maintenance Model")
print("----------------------------")
print("Training records:", len(x_train))
print("Testing records:", len(x_test))
print("Accuracy:", round(accuracy, 4))
print("ROC-AUC:", round(roc_auc, 4))

print()
print("Classification Report")
print("---------------------")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "NO_FAILURE",
            "FAILURE"
        ]
    )
)

print("Confusion Matrix")
print("----------------")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)
import csv

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)


FEATURE_COLUMNS = [
    "battery",
    "temperature",
    "speed",
    "battery_mean",
    "temperature_mean",
    "speed_mean",
    "battery_drop_mean",
    "temperature_change_mean",
    "temperature_max",
    "battery_min"
]


def load_data(filename):
    with open(filename, "r", newline="") as file:
        return list(csv.DictReader(file))


def prepare_data(rows):
    features = []
    labels = []

    for row in rows:
        features.append([
            float(row[column])
            for column in FEATURE_COLUMNS
        ])

        labels.append(
            int(row["failure_within_next_10_steps"])
        )

    return features, labels


def split_by_run(rows):
    train_rows = []
    test_rows = []

    for row in rows:
        run = int(row["run"])

        if run <= 56:
            train_rows.append(row)
        else:
            test_rows.append(row)

    return train_rows, test_rows


rows = load_data(
    "data/predictive_features.csv"
)

train_rows, test_rows = split_by_run(rows)

x_train, y_train = prepare_data(train_rows)
x_test, y_test = prepare_data(test_rows)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42
)

model.fit(
    x_train,
    y_train
)

predictions = model.predict(x_test)
probabilities = model.predict_proba(x_test)[:, 1]

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

print("Run-Based Predictive Maintenance Evaluation")
print("--------------------------------------------")
print("Training runs: 1-56")
print("Testing runs: 57-70")
print("Training records:", len(x_train))
print("Testing records:", len(x_test))
print("ROC-AUC:", round(roc_auc, 4))

print()
print("Classification Report")
print("---------------------")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "NO_FAILURE",
            "FAILURE"
        ]
    )
)

print("Confusion Matrix")
print("----------------")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)