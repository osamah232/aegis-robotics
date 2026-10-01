class LiveRiskCalculator:
    def __init__(self, model, window_size=10):
        self.model = model
        self.window_size = window_size

    def build_features(self, robot):
        telemetry = robot.telemetry

        if len(telemetry) < self.window_size:
            return None

        window = telemetry[-self.window_size:]

        batteries = [
            float(row["battery"])
            for row in window
        ]

        temperatures = [
            float(row["temperature"])
            for row in window
        ]

        speeds = [
            float(row["speed"])
            for row in window
        ]

        battery_drops = []

        temperature_changes = []

        for index in range(1, len(window)):
            battery_drop = max(
                0,
                batteries[index - 1] - batteries[index]
            )

            temperature_change = (
                temperatures[index]
                - temperatures[index - 1]
            )

            battery_drops.append(
                battery_drop
            )

            temperature_changes.append(
                temperature_change
            )

        battery_drops.insert(0, 0)
        temperature_changes.insert(0, 0)

        return {
            "battery": batteries[-1],
            "temperature": temperatures[-1],
            "speed": speeds[-1],
            "battery_mean": sum(batteries) / len(batteries),
            "temperature_mean": sum(temperatures) / len(temperatures),
            "speed_mean": sum(speeds) / len(speeds),
            "battery_drop_mean": sum(battery_drops) / len(battery_drops),
            "temperature_change_mean": sum(temperature_changes) / len(temperature_changes),
            "temperature_max": max(temperatures),
            "battery_min": min(batteries)
        }

    def predict(self, robot):
        features = self.build_features(robot)

        if features is None:
            return None

        probability, risk = self.model.predict_risk(
            features
        )

        return {
            "robot": robot.name,
            "probability": probability,
            "risk": risk
        }
