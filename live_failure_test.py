from maintenance_risk import MaintenanceRiskModel
from live_risk import LiveRiskCalculator
from main import Robot


model = MaintenanceRiskModel()

model.train(
    "data/predictive_features.csv"
)

robot = Robot(
    "Aegis-02",
    60,
    40,
    2.0,
    5,
    3
)

calculator = LiveRiskCalculator(
    model
)

print("Live Predictive Maintenance Failure Test")
print("-----------------------------------------")

for step in range(60):
    robot.battery = max(
        0,
        robot.battery - 0.9
    )

    robot.record_telemetry()

    result = calculator.predict(
        robot
    )

    if result is not None:
        probability = result["probability"]
        risk = result["risk"]

        if step >= 30:
            print(
                "Step:",
                step,
                "Battery:",
                round(robot.battery, 1),
                "Probability:",
                round(probability, 3),
                "Risk:",
                risk
            )

    if robot.battery <= 10:
        print(
            "Actual failure threshold reached."
        )
        break
