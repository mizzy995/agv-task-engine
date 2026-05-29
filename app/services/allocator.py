from math import sqrt
from typing import List, Tuple, Dict, Any, Optional


class Allocator:
    def __init__(self, safety_factor: float = 1.10, routing_engine=None):
        if safety_factor <= 0:
            raise ValueError("safety_factor must be > 0")
        self.safety_factor = safety_factor
        self.routing_engine = routing_engine

    def calculate_distance(self, robot, task) -> Optional[float]:
        """
        If routing is present: return routing distance (int steps) or None.
        Altrimenti: fallback euclideo (per compatibilità).
        """
        if self.routing_engine is None:
            return sqrt((robot.x - task.x) ** 2 + (robot.y - task.y) ** 2)

        start = (robot.x, robot.y)
        goal = (task.x, task.y)
        dist_steps = self.routing_engine.shortest_path_distance(start, goal)
        return dist_steps  # int | None

    def calculate_consumption(self, robot, task) -> float:
        # Milestone 5: consumo = 2 * distanza routing
        dist = self.calculate_distance(robot, task)
        if dist is None:
            # Non dovrebbe essere chiamato da allocate() quando dist=None,
            # ma gestiamo comunque.
            return float("inf")
        return 2 * dist

    def _required_energy(self, robot, task) -> float:
        return self.calculate_consumption(robot, task) * self.safety_factor

    def allocate(self, robots, tasks):
        """
        Returns:
          - assignments: List[Tuple[robot_id, task_id]]
          - not_assigned: List[Dict{task_id, reasons}]
          - decision_trace: List[Dict]
        """
        assignments: List[Tuple[str, str]] = []
        not_assigned: List[Dict[str, Any]] = []
        decision_trace: List[Dict[str, Any]] = []

        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        for task in sorted_tasks:
            available = [r for r in robots if not r.busy]

            task_trace: Dict[str, Any] = {
                "task_id": task.id,
                "priority": task.priority,
                "available_robots": [r.id for r in available],
                "candidates": [],
                "selected_robot_id": None,
                "failure_reasons": []
            }

            if not available:
                reason = "no_robot_available (all robots busy)"
                not_assigned.append({"task_id": task.id, "reasons": [reason]})
                task_trace["failure_reasons"] = [reason]
                decision_trace.append(task_trace)
                continue

            candidates: List[Tuple[Any, float, float]] = []
            route_blocked_count = 0
            route_ok_count = 0

            for r in available:
                dist = self.calculate_distance(r, task)  # float|None
                if dist is None:
                    route_blocked_count += 1
                    task_trace["candidates"].append({
                        "robot_id": r.id,
                        "route_distance": None,
                        "required_energy": None,
                        "energy_ok": False,
                        "route_ok": False
                    })
                    continue

                route_ok_count += 1
                required_energy = self._required_energy(r, task)
                energy_ok = r.battery >= required_energy

                task_trace["candidates"].append({
                    "robot_id": r.id,
                    "route_distance": dist,
                    "required_energy": required_energy,
                    "energy_ok": energy_ok,
                    "route_ok": True
                })

                if energy_ok:
                    # key minima: (required_energy, distance, robot_id) come prima
                    candidates.append((r, required_energy, dist))

            if not candidates:
                if route_ok_count == 0:
                    reason = "no_route_available"
                else:
                    reason = "battery_insufficient_for_all_available_robots"

                not_assigned.append({"task_id": task.id, "reasons": [reason]})
                task_trace["failure_reasons"] = [reason]
                decision_trace.append(task_trace)
                continue

            best_robot, best_required_energy, best_distance = min(
                candidates,
                key=lambda x: (x[1], x[2], x[0].id)
            )

            best_robot.busy = True
            assignments.append((best_robot.id, task.id))
            task_trace["selected_robot_id"] = best_robot.id

            task_trace["selected_summary"] = {
                "selected_required_energy": best_required_energy,
                "selected_route_distance": best_distance
            }

            decision_trace.append(task_trace)

        return assignments, not_assigned, decision_trace