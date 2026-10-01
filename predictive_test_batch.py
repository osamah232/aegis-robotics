from maintenance_risk import MaintenanceRiskModel
from live_risk import LiveRiskCalculator
from main import Robot


model = MaintenanceRiskModel()

model.train(
    "data/predictive_features.csv"
)

calculator = LiveRiskCalculator(
    model
)

total_tests = 20
early_warnings = 0

print("Batch Predictive Maintenance Test")
print("----------------------------------")

for test in range(1, total_tests + 1):
    robot = Robot(
        "Aegis-02",
        60,
        40,
        2.0,
        5,
        3
    )

    warning_step = None
    failure_step = None

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
            if (
                result["risk"] == "HIGH"
                and warning_step is None
            ):
                warning_step = step

        if robot.battery <= 10:
            failure_step = step
            break

    if (
        warning_step is not None
        and failure_step is not None
        and warning_step < failure_step
    ):
        early_warnings += 1

    print(
        "Test:",
        test,
        "Warning:",
        warning_step,
        "Failure:",
        failure_step
    )

print()
print("Early warnings:", early_warnings)
print("Total tests:", total_tests)
print(
    "Early warning rate:",
    round(
        early_warnings / total_tests * 100,
        1
    ),
    "%"
)
