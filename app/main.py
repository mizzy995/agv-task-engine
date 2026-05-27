from rich import print

from app.simulation.warehouse import robots, tasks
from app.services.allocator import Allocator


allocator = Allocator(safety_factor=1.10)

results, not_assigned = allocator.allocate(robots, tasks)

print()
print("Assignments")
print("----------------")
for (r_id, t_id, _, dist, en_cons) in results:
    print(f"{r_id} ---> {t_id} - Distance {dist:.2f} m, Energy consumed {en_cons:.2f} u")

if not_assigned:
    print()
    print("Not assigned tasks")
    print("----------------")
    for item in not_assigned:
        task_id = item["task_id"]
        reasons = item.get("reasons", [])
        if reasons:
            print(f"{task_id} | reasons: {', '.join(reasons)}")
        else:
            print(f"{task_id}")