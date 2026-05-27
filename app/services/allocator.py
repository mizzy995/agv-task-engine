from math import sqrt
from typing import List, Tuple, Dict, Any


class Allocator:
    def __init__(self, safety_factor: float = 1.10):
        if safety_factor <= 0:
            raise ValueError("safety_factor must be > 0")
        self.safety_factor = safety_factor

    def calculate_distance(self, robot, task) -> float:
        return sqrt((robot.x - task.x) ** 2 + (robot.y - task.y) ** 2)

    def calculate_consumption(self, robot, task) -> float:
        # energy model as previously defined: E = 2 * distance
        return 2 * self.calculate_distance(robot, task)

    def _required_energy(self, robot, task) -> float:
        return self.calculate_consumption(robot, task) * self.safety_factor

    def allocate(self, robots, tasks):
        # NOTE: This function mutates robots[].busy like your current implementation.
        # If you want an immutable approach later, we can refactor in Milestone 2.
        assignments: List[Tuple[str, str, float, float, float]] = []
        # (robot_id, task_id, required_energy, distance, consumed_energy_estimate)

        not_assigned: List[Dict[str, Any]] = []

        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        for task in sorted_tasks:
            # robots available by "hard" state constraint only (busy)
            available = [r for r in robots if not r.busy]

            if not available:
                not_assigned.append({
                    "task_id": task.id,
                    "reasons": ["no_robot_available (all robots busy)"]
                })
                continue

            # compute required energy for each available robot
            candidates = []
            for r in available:
                required_energy = self._required_energy(r, task)
                energy_ok = r.battery >= required_energy
                # tie-break inputs:
                # 1) required_energy (primary)
                # 2) distance (secondary for stability)
                distance = self.calculate_distance(r, task)
                # 3) robot_id (tertiary deterministic)
                if energy_ok:
                    candidates.append((r, required_energy, distance))

            if not candidates:
                # Distinguish "battery insufficient for all available robots"
                not_assigned.append({
                    "task_id": task.id,
                    "reasons": ["battery_insufficient_for_all_available_robots"]
                })
                continue

            # Deterministic tie-break:
            # min by required_energy, then by distance, then by robot_id
            best_robot, best_required_energy, best_distance = min(
                candidates,
                key=lambda x: (x[1], x[2], x[0].id)
            )

            best_robot.busy = True
            assignments.append((
                best_robot.id,
                task.id,
                best_required_energy,
                best_distance,
                self.calculate_consumption(best_robot, task)  # energy without safety_factor
            ))

        # Backward-compatible shape for main.py:
        # results: [(robot_id, task_id)]
        results_simple = [(r_id, t_id) for (r_id, t_id, _, _, _) in assignments]

        # richer diagnostics:
        return assignments, not_assigned