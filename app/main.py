from rich import print

from app.services.allocator import Allocator
from app.simulation.simulator import AGVEventDrivenSimulator
from app.simulation.warehouse import build_stream

from app.services.routing import GridRoutingEngine

def build_grid_20x20():
    # 0 libero, 1 bloccato
    grid = [[0 for _ in range(20)] for _ in range(20)]

    # 1st block
    for y in range(20):
        grid[y][10] = 1
    grid[9][10] = 0  # gap

    # extra blocks
    grid[2][3] = 1
    grid[3][3] = 1
    grid[4][3] = 1

    return grid


grid = build_grid_20x20()
routing = GridRoutingEngine(grid)

allocator = Allocator(safety_factor=1.10, routing_engine=routing)
robots, stream = build_stream()

sim = AGVEventDrivenSimulator(robots=robots, tasks=stream, allocator=allocator, v=1.0)
result = sim.run()

print()
print("Battery remaining per robot")
print("-----------------------------")
for robot_id, rem in result.get("battery_remaining", {}).items():
    print(f"{robot_id}: {rem:.2f}")

completed = result["completed"]
not_assigned_final = result["not_assigned"]

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

print()
print("Simulation summary")
print("-------------------")
print(f"Tasks completed: {len(completed)} / {len(result.get('tasks_total', []))}")
print(f"Tasks not assigned: {len(not_assigned_final)}")