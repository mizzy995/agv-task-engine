from math import sqrt
from typing import List, Tuple, Dict, Any, Optional


class Allocator:
    def __init__(self, safety_factor: float = 1.10):
        if safety_factor <= 0:
            raise ValueError("safety_factor must be > 0")
        self.safety_factor = safety_factor

    def calculate_distance(self, robot, task) -> float:
        return sqrt((robot.x - task.x) ** 2 + (robot.y - task.y) ** 2)

    def calculate_consumption(self, robot, task) -> float:
        # energy model: E = 2 * distance
        return 2 * self.calculate_distance(robot, task)

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
            # robots available = not busy
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
            for r in available:
                dist = self.calculate_distance(r, task)
                required_energy = self._required_energy(r, task)
                energy_ok = r.battery >= required_energy

                task_trace["candidates"].append({
                    "robot_id": r.id,
                    "distance": dist,
                    "required_energy": required_energy,
                    "energy_ok": energy_ok
                })

                if energy_ok:
                    candidates.append((r, required_energy, dist))

            if not candidates:
                reason = "battery_insufficient_for_all_available_robots"
                not_assigned.append({"task_id": task.id, "reasons": [reason]})
                task_trace["failure_reasons"] = [reason]
                decision_trace.append(task_trace)
                continue

            best_robot, best_required_energy, best_distance = min(
                candidates,
                key=lambda x: (x[1], x[2], x[0].id)  # required_energy, distance, robot_id
            )

            best_robot.busy = True
            assignments.append((best_robot.id, task.id))
            task_trace["selected_robot_id"] = best_robot.id

            # record selected cost summary (deterministic)
            task_trace["selected_summary"] = {
                "selected_required_energy": best_required_energy,
                "selected_distance": best_distance
            }

            decision_trace.append(task_trace)

        return assignments, not_assigned, decision_trace