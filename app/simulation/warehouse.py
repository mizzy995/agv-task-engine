from app.models.robot import Robot
from app.models.task import Task


robots=[

Robot(
id="R1",
x=1,
y=2,
battery=90
),

Robot(
id="R2",
x=7,
y=4,
battery=60
),

Robot(
id="R3",
x=4,
y=8,
battery=70
)

]


tasks=[

Task(
id="T1",
x=6,
y=7,
priority=10
),

Task(
id="T2",
x=1,
y=5,
priority=5
)

]