class Robot:
    def __init__(self, name, battery, temperature, speed):
        self.name = name
        self.battery = battery
        self.temperature = temperature
        self.speed = speed

    def health_check(self):
        status = "HEALTHY"

        if self.battery < 20:
            status = "CRITICAL"
        elif self.battery < 40:
            status = "WARNING"

        if self.temperature > 70:
            status = "CRITICAL"
        elif self.temperature > 50 and status != "CRITICAL":
            status = "WARNING"

        if self.speed > 3:
            status = "CRITICAL"
        elif self.speed > 2.5 and status != "CRITICAL":
            status = "WARNING"

        print("Status:", status)


robot1 = Robot("Aegis-01", 80, 35, 2.5)
robot2 = Robot("Aegis-02", 60, 40, 2)
robot3 = Robot("Aegis-03", 10, 75, 3.5)

robots = [robot1, robot2, robot3]

for robot in robots:
    print("\nRobot:", robot.name)
    print("Battery:", robot.battery, "%")
    print("Temperature:", robot.temperature, "°C")
    print("Speed:", robot.speed, "m/s")
    robot.health_check()
