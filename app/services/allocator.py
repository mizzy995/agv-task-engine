from math import sqrt


class Allocator:


    def calculate_distance(
        self,
        robot,
        task
    ):

        return sqrt(
            (robot.x-task.x)**2+
            (robot.y-task.y)**2
        )


    def allocate(
        self,
        robots,
        tasks
    ):

        assignments=[]


        sorted_tasks=sorted(
            tasks,
            key=lambda t:t.priority,
            reverse=True
        )


        for task in sorted_tasks:

            available=[

                r for r in robots
                if not r.busy

            ]


            if not available:

                break


            best=min(

                available,

                key=lambda r:
                self.calculate_distance(
                    r,
                    task
                )

            )


            best.busy=True


            assignments.append(

                (best.id,task.id)

            )


        return assignments