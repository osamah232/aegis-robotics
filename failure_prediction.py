import csv

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
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
            float(row["battery_drop"]),
            float(row["temperature_change"])
        ])

        labels.append(row["fault_label"])

    return features, labels


rows = load_data("data/labeled_features.csv")

features, labels = prepare_data(rows)

x_train, x_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(x_train, y_train)

predictions = model.predict(x_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("Failure Prediction Model")
print("------------------------")
print("Training records:", len(x_train))
print("Testing records:", len(x_test))
print("Accuracy:", round(accuracy, 4))

print()
print("Classification Report")
print("---------------------")
print(
    classification_report(
        y_test,
        predictions
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