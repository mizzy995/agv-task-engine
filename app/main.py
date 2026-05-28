from rich import print

from app.services.allocator import Allocator
from app.simulation.simulator import AGVEventDrivenSimulator
from app.simulation.warehouse import build_benchmarks

benchmarks = build_benchmarks()
allocator = Allocator(safety_factor=1.10)

index = 5  # scegli manualmente quale benchmark
bench_name, robots, tasks = benchmarks[index]

sim = AGVEventDrivenSimulator(robots=robots, tasks=tasks, allocator=allocator, v=1.0)
result = sim.run()

completed = result["completed"]
not_assigned_final = result["not_assigned"]
not_assigned_during_run = result.get("not_assigned_during_run", [])

print()
print("Completed assignments")
print("----------------------")
for robot_id, task_id, end_time in completed:
    print(f"{robot_id} ---> {task_id} (end_time={end_time:.2f}s)")

if not_assigned_final:
    print()
    print("Not assigned tasks (FINAL)")
    print("----------------------------")
    for item in not_assigned_final:
        task_id = item["task_id"]
        reasons = item.get("reasons", [])
        print(f"{task_id} | reasons: {', '.join(reasons)}")

#if not_assigned_during_run:
#    print()
#   print("Not assigned tasks (DURING RUN - trace)")
#    print("----------------------------------------")
#    for item in not_assigned_during_run:
#        time = item.get("time", 0.0)
#        task_id = item["task_id"]
#        reasons = item.get("reasons", [])
#        print(f"t={time:.2f}s | {task_id} | reasons: {', '.join(reasons)}")

print()
print("Simulation summary")
print("-------------------")
print(f"Tasks completed: {len(completed)} / {len(tasks)}")
print(f"Tasks not assigned: {len(not_assigned_final)}")