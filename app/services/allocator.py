from math import sqrt


class Allocator:


    def calculate_distance(
        self,
        robot,
        task
    ):

        return sqrt((robot.x-task.x)**2 + (robot.y-task.y)**2)
    
    def calculate_consumption(
        self,
        robot,
        task
    ):
        return  2 * self.calculate_distance(robot, task)
    
    def allocate(
        self,
        robots,
        tasks
    ):

        assignments=[]
        tasknotexec=[]


        sorted_tasks=sorted(tasks, key=lambda t:t.priority, reverse=True)


        for task in sorted_tasks:

            available=[

                r for r in robots
                if (not r.busy) and (r.battery >= 20)

            ]
            
            consumptions = [
                (r, self.calculate_consumption(r, task))
                for r in available
            ]

            
            feasible = [
                (r, c) for (r, c) in consumptions
                if r.battery >= c
            ]
            
            if not feasible:

                tasknotexec.append(task.id)

            else:
                
                best, _ = min(feasible,key=lambda rc: rc[1])

                best.busy=True

                assignments.append((best.id,task.id))


        return assignments, tasknotexec