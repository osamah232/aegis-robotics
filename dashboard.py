import streamlit as st

from maintenance_risk import MaintenanceRiskModel
from main import Environment, Task, Robot, Fleet, FaultDetector, SimulationEngine


st.set_page_config(
    page_title="Aegis Robotics",
    layout="wide"
)


@st.cache_resource
def create_simulation():
    environment = Environment(
        10,
        10,
        [
            (2, 6),
            (4, 3),
            (4, 5),
            (6, 6),
            (8, 2)
        ]
    )

    fleet = Fleet()

    robots = [
        Robot("Aegis-01", 80, 35, 2.5, 3, 3),
        Robot("Aegis-02", 60, 40, 2.0, 5, 3),
        Robot("Aegis-03", 25, 65, 3.5, 10, 7)
    ]

    for robot in robots:
        fleet.add_robot(robot)

    tasks = [
        Task("Task-01", 8, 8, 3),
        Task("Task-02", 1, 8, 2),
        Task("Task-03", 2, 2, 1),
        Task("Task-04", 9, 9, 2),
        Task("Task-05", 1, 1, 1)
    ]

    for task in tasks:
        fleet.add_task(task)

    fault_detector = FaultDetector()

    risk_model = MaintenanceRiskModel()
    risk_model.train(
        "data/predictive_features.csv"
    )

    simulation = SimulationEngine(
        environment,
        fleet,
        fault_detector,
        max_steps=100,
        risk_model=risk_model
    )

    simulation.run()

    return fleet


fleet = create_simulation()

st.title("Aegis Robotics")
st.caption("Autonomous Robot Fleet Simulation & Predictive Maintenance")

st.divider()

completed = sum(
    1
    for task in fleet.tasks
    if task.status == "COMPLETED"
)

failed = sum(
    1
    for robot in fleet.robots
    if robot.status == "FAILED"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Robots",
    len(fleet.robots)
)

col2.metric(
    "Tasks",
    len(fleet.tasks)
)

col3.metric(
    "Completed Tasks",
    completed
)

col4.metric(
    "Failed Robots",
    failed
)

st.divider()

st.subheader("Robot Fleet")

for robot in fleet.robots:
    st.write(f"### {robot.name}")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Battery",
        f"{robot.battery:.1f}"
    )

    col2.metric(
        "Temperature",
        f"{robot.temperature:.1f}"
    )

    col3.metric(
        "Status",
        robot.status
    )

    col4.metric(
        "Risk",
        robot.maintenance_risk
    )

    col5.metric(
        "Failure Probability",
        f"{robot.failure_probability:.2f}"
    )

st.divider()

st.subheader("Task Allocation")

for task in fleet.tasks:
    st.write(
        f"{task.task_id} | "
        f"Status: {task.status} | "
        f"Robot: {task.assigned_robot}"
    )

st.divider()

st.subheader("Fleet Summary")

for robot in fleet.robots:
    st.write(
        f"{robot.name} — "
        f"Position: ({robot.x}, {robot.y}) — "
        f"Distance: {robot.distance_travelled} — "
        f"Tasks: {robot.completed_tasks}"
    )