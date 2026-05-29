from app.models.robot import Robot
from app.models.task import Task


def build_stream():
    robots = [
        Robot(id="R1", x=0,  y=0,  battery=100, busy=False),
        Robot(id="R2", x=10, y=0,  battery=100, busy=False),
        Robot(id="R3", x=5,  y=10, battery=100, busy=False),
    ]

    stream = [
        {"task": Task(id="T1",  x=9,  y=1,  priority=8),  "arrival_time": 0.0},
        {"task": Task(id="T2",  x=1,  y=1,  priority=7),  "arrival_time": 0.0},  # stesso tempo di T1
        {"task": Task(id="T3",  x=6,  y=9,  priority=9),  "arrival_time": 0.3},
        {"task": Task(id="T4",  x=2,  y=8,  priority=6),  "arrival_time": 0.5},
        {"task": Task(id="T5",  x=8,  y=8,  priority=10), "arrival_time": 1.0},
        {"task": Task(id="T6",  x=7,  y=7,  priority=10), "arrival_time": 1.0},  # tie sul priority
        {"task": Task(id="T7",  x=0,  y=10, priority=5),  "arrival_time": 1.1},
        {"task": Task(id="T8",  x=10, y=10, priority=4),  "arrival_time": 1.3},
        {"task": Task(id="T9",  x=3,  y=2,  priority=9),  "arrival_time": 2.0},
        {"task": Task(id="T10", x=4,  y=4,  priority=3),  "arrival_time": 2.2},
    ]

    return robots, stream

def build_stream_battery_depletion_sequence():
    robots = [
        Robot(id="R1", x=0,  y=0,  battery=35, busy=False),
        Robot(id="R2", x=10, y=0,  battery=35, busy=False),
        Robot(id="R3", x=5,  y=10, battery=35, busy=False),
    ]

    stream = [
        {"task": Task(id="T1",  x=1,  y=0,  priority=10), "arrival_time": 0.0},
        {"task": Task(id="T2",  x=9,  y=0,  priority=9),  "arrival_time": 0.1},
        {"task": Task(id="T3",  x=5,  y=9,  priority=8),  "arrival_time": 0.2},

        {"task": Task(id="T4",  x=2,  y=1,  priority=10), "arrival_time": 0.9},
        {"task": Task(id="T5",  x=8,  y=1,  priority=9),  "arrival_time": 1.0},
        {"task": Task(id="T6",  x=6,  y=8,  priority=7),  "arrival_time": 1.1},

        {"task": Task(id="T7",  x=0,  y=2,  priority=8),  "arrival_time": 1.8},
        {"task": Task(id="T8",  x=10, y=2,  priority=7),  "arrival_time": 1.9},
        {"task": Task(id="T9",  x=5,  y=7,  priority=6),  "arrival_time": 2.0},

        {"task": Task(id="T10", x=1,  y=4,  priority=5),  "arrival_time": 3.0},
        {"task": Task(id="T11", x=9,  y=4,  priority=4),  "arrival_time": 3.2},
        {"task": Task(id="T12", x=4,  y=6,  priority=3),  "arrival_time": 3.4},
    ]

    return robots, stream
    
def build_stream_battery_insufficient_burst():
    robots = [
        Robot(id="R1", x=0,  y=0,  battery=18, busy=False),
        Robot(id="R2", x=20, y=0,  battery=18, busy=False),
    ]

    stream = [
        # Prime missioni “brevi” per ridurre la batteria
        {"task": Task(id="T1", x=2,  y=1,  priority=10), "arrival_time": 0.0},
        {"task": Task(id="T2", x=18, y=1,  priority=9),  "arrival_time": 0.1},

        {"task": Task(id="T3", x=3,  y=2,  priority=8),  "arrival_time": 0.6},
        {"task": Task(id="T4", x=17, y=2,  priority=7),  "arrival_time": 0.7},

        # Arrivano task più “lunghe”: dopo il consumo precedente dovrebbero diventare infeasible
        {"task": Task(id="T5", x=10, y=10, priority=10), "arrival_time": 1.5},
        {"task": Task(id="T6", x=12, y=12, priority=9),  "arrival_time": 1.6},
        {"task": Task(id="T7", x=8,  y=14, priority=8),  "arrival_time": 1.7},
        {"task": Task(id="T8", x=15, y=13, priority=7),  "arrival_time": 1.8},
    ]

    return robots, stream
    

def build_stream_priority_vs_battery():
    robots = [
        Robot(id="R1", x=0,  y=0,  battery=22, busy=False),
        Robot(id="R2", x=12, y=0,  battery=22, busy=False),
        Robot(id="R3", x=6,  y=12, battery=22, busy=False),
    ]

    stream = [
        {"task": Task(id="T1",  x=2,  y=1,  priority=5),  "arrival_time": 0.0},
        {"task": Task(id="T2",  x=10, y=1,  priority=5),  "arrival_time": 0.1},
        {"task": Task(id="T3",  x=6,  y=11, priority=5),  "arrival_time": 0.2},

        # burst di priorità alte: alcuni robot potrebbero essere vicini all’infeasible
        {"task": Task(id="T4",  x=1,  y=0,  priority=20), "arrival_time": 1.0},
        {"task": Task(id="T5",  x=11, y=0,  priority=18), "arrival_time": 1.1},
        {"task": Task(id="T6",  x=6,  y=10, priority=16), "arrival_time": 1.2},

        # ulteriori task medio-basse per vedere come si stabilizza la coda
        {"task": Task(id="T7",  x=3,  y=2,  priority=7),  "arrival_time": 2.0},
        {"task": Task(id="T8",  x=9,  y=2,  priority=6),  "arrival_time": 2.1},
        {"task": Task(id="T9",  x=5,  y=9,  priority=4),  "arrival_time": 2.2},
        {"task": Task(id="T10", x=0,  y=12, priority=3),  "arrival_time": 3.0},
    ]

    return robots, stream