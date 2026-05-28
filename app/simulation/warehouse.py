from app.models.robot import Robot
from app.models.task import Task


def build_benchmarks():
    benchmarks = []

    # ===== Benchmark 1: tutti fattibili, nessun vincolo busy dopo t=0 =====
    robots_1 = [
        Robot(id="R1", x=1, y=1, battery=100, busy=False),
        Robot(id="R2", x=9, y=1, battery=100, busy=False),
        Robot(id="R3", x=5, y=9, battery=100, busy=False),
    ]
    tasks_1 = [
        Task(id="T1", x=8, y=2, priority=10),
        Task(id="T2", x=4, y=8, priority=8),
        Task(id="T3", x=2, y=6, priority=7),
        Task(id="T4", x=6, y=2, priority=5),
    ]
    benchmarks.append(("B1_all_feasible", robots_1, tasks_1))

    # ===== Benchmark 2: alcuni task non assegnabili per batteria (safety_factor) =====
    # Nota: con safety_factor=1.10 e consumo=2*d, energia required = 2*d*1.10
    robots_2 = [
        Robot(id="R1", x=0, y=0, battery=5, busy=False),
        Robot(id="R2", x=10, y=0, battery=8, busy=False),
    ]
    tasks_2 = [
        Task(id="T1", x=1, y=0, priority=10),  # facile per R1
        Task(id="T2", x=9, y=0, priority=9),   # facile per R2
        Task(id="T3", x=5, y=0, priority=7),   # potrebbe risultare infeasible per entrambi
    ]
    benchmarks.append(("B2_battery_insufficient", robots_2, tasks_2))

    # ===== Benchmark 3: robot pochi -> coda pending (nessun preemption) =====
    robots_3 = [
        Robot(id="R1", x=0, y=0, battery=200, busy=False),
        Robot(id="R2", x=10, y=0, battery=200, busy=False),
    ]
    tasks_3 = [
        Task(id="T1", x=1, y=0, priority=100),
        Task(id="T2", x=9, y=0, priority=90),
        Task(id="T3", x=2, y=0, priority=80),
        Task(id="T4", x=8, y=0, priority=70),
        Task(id="T5", x=5, y=0, priority=60),
    ]
    benchmarks.append(("B3_pending_queue_no_preemption", robots_3, tasks_3))

    # ===== Benchmark 4: tie-break deterministico (stessa distanza/required) =====
    # Due robot equidistanti dal task a pari required_energy; vince quello con robot_id minore.
    robots_4 = [
        Robot(id="R2", x=1, y=0, battery=100, busy=False),
        Robot(id="R1", x=-1, y=0, battery=100, busy=False),
    ]
    tasks_4 = [
        Task(id="T1", x=0, y=0, priority=10),
    ]
    benchmarks.append(("B4_tie_break_deterministic", robots_4, tasks_4))

    # ===== Benchmark 5: tutti busy inizialmente (nessuna assegnazione) =====
    robots_5 = [
        Robot(id="R1", x=0, y=0, battery=100, busy=True),
        Robot(id="R2", x=5, y=5, battery=100, busy=True),
    ]
    tasks_5 = [
        Task(id="T1", x=1, y=1, priority=10),
        Task(id="T2", x=6, y=6, priority=9),
    ]
    benchmarks.append(("B5_all_busy_start", robots_5, tasks_5))

    # ===== Benchmark 6: priorità decrescente con stessa area (verifica ordine e completamenti) =====
    robots_6 = [
        Robot(id="R1", x=0, y=0, battery=300, busy=False),
        Robot(id="R2", x=10, y=10, battery=300, busy=False),
        Robot(id="R3", x=20, y=0, battery=300, busy=False),
    ]
    tasks_6 = [
        Task(id="T1", x=1, y=0, priority=9),
        Task(id="T2", x=2, y=0, priority=8),
        Task(id="T3", x=3, y=0, priority=7),
        Task(id="T4", x=4, y=0, priority=6),
    ]
    benchmarks.append(("B6_priority_effect_on_completion", robots_6, tasks_6))

    return benchmarks