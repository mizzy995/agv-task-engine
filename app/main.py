from rich import print

from app.simulation.warehouse import (
robots,
tasks
)

from app.services.allocator import (
Allocator
)



allocator=Allocator()


results=allocator.allocate(

robots,
tasks

)


print()

print("Assignments")

print("----------------")


for robot,task in results:

    print(
        f"{robot} ---> {task}"
    )