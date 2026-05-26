from rich import print

from app.simulation.warehouse import (
robots,
tasks
)

from app.services.allocator import (
Allocator
)



allocator=Allocator()


results,notassignedtask = allocator.allocate(

robots,
tasks

)


print()

print("Assignments")

print("----------------")


for robot,task in results:

    print(f"{robot} ---> {task}")

if notassignedtask:
    
    print()
        
    print("Not assigned tasks")

    print("----------------")

    for task_id in notassignedtask:

        print(f"{task_id}")