from maintenance_risk import MaintenanceRiskModel
from live_risk import LiveRiskCalculator


model = MaintenanceRiskModel()

model.train(
    "data/predictive_features.csv"
)

rows = model.load_data(
    "data/predictive_features.csv"
)

rows = [
    row
    for row in rows
    if row["robot"] == "Aegis-02"
    and int(row["failure_within_next_10_steps"]) == 1
]

window = rows[:10]

robot_data = []

for row in window:
    robot_data.append({
        "battery": row["battery"],
        "temperature": row["temperature"],
        "speed": row["speed"]
    })


class TestRobot:
    def __init__(self, name, telemetry):
        self.name = name
        self.telemetry = telemetry


robot = TestRobot(
    "Aegis-02",
    [
        {
            "battery": float(row["battery"]),
            "temperature": float(row["temperature"]),
            "speed": float(row["speed"])
        }
        for row in window
    ]
)

calculator = LiveRiskCalculator(
    model
)

result = calculator.predict(
    robot
)

print("Live Risk Test")
print("--------------")
print("Robot:", result["robot"])
print("Probability:", round(result["probability"], 3))
print("Risk:", result["risk"])
