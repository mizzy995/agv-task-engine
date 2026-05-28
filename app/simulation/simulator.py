import heapq
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from app.services.allocator import Allocator


@dataclass(order=True)
class ScheduledEvent:
    time: float
    seq: int
    event_type: str
    payload: Dict[str, Any]


class AGVEventDrivenSimulator:
    def __init__(self, robots, tasks, allocator: Allocator, v: float = 1.0):
        self.robots = robots
        self.tasks = tasks
        self.allocator = allocator
        self.v = v

        self._time = 0.0
        self._seq = 0

        self.pending_tasks = list(tasks)
        self.running: Dict[str, Dict[str, Any]] = {}  # robot_id -> info

        self.completed: List[Tuple[str, str, float]] = []  # (robot_id, task_id, end_time)
        self.assignment_log: List[Dict[str, Any]] = []
        self.not_assigned_log: List[Dict[str, Any]] = []
        
        # temporary diagnostic: non assigned during the first cycle, but likely assigned later
        self.not_assigned_during_run_log: List[Dict[str, Any]] = []

        # heap of events
        self.events: List[ScheduledEvent] = []

    def _push_event(self, time: float, event_type: str, payload: Dict[str, Any]):
        self._seq += 1
        heapq.heappush(self.events, ScheduledEvent(time=time, seq=self._seq, event_type=event_type, payload=payload))

    def _duration(self, robot, task) -> float:
        # T = d / v, deterministic; using allocator distance model for consistency
        dist = self.allocator.calculate_distance(robot, task)
        if self.v <= 0:
            raise ValueError("v must be > 0")
        return dist / self.v

    def _try_allocate_pending(self, now: float):
        # Allocate as many pending tasks as possible among robots that are free.
        # Option 2 (no preemption): we only allocate pending tasks when robots free.
        free_snapshot = [r for r in self.robots if not r.busy]
        if not free_snapshot:
            return

        # Consider only currently pending tasks
        if not self.pending_tasks:
            return

        # Run allocator on pending tasks. It will set busy=True immediately.
        assignments, not_assigned, trace = self.allocator.allocate(self.robots, self.pending_tasks)

        # Log traces for audit (Milestone 2 deliverable)
        self.assignment_log.extend(trace)

        # Mark not assigned tasks removed from pending
        if not_assigned:
            for item in not_assigned:
                self.not_assigned_during_run_log.append({
                    "time": now,
                    "task_id": item["task_id"],
                    "reasons": item.get("reasons", [])
                })
        assigned_task_ids = set(tid for _, tid in assignments)
        self.pending_tasks = [t for t in self.pending_tasks if t.id not in assigned_task_ids]

        # For each assignment, schedule completion based on deterministic duration
        robot_by_id = {r.id: r for r in self.robots}
        task_by_id = {t.id: t for t in self.tasks}

        for robot_id, task_id in assignments:
            robot = robot_by_id[robot_id]
            task = task_by_id[task_id]

            duration = self._duration(robot, task)
            end_time = now + duration

            # store running info
            self.running[robot_id] = {
                "task_id": task_id,
                "start_time": now,
                "end_time": end_time
            }

            self._push_event(end_time, "TASK_COMPLETED", {
                "robot_id": robot_id,
                "task_id": task_id
            })

    def run(self):
        # Batch mode: all tasks arrive at t=0; initial allocation attempt
        self._push_event(0.0, "TICK", {})

        while self.events:
            ev = heapq.heappop(self.events)
            self._time = ev.time

            if ev.event_type == "TICK":
                # At time 0, attempt allocations
                self._try_allocate_pending(self._time)

            elif ev.event_type == "TASK_COMPLETED":
                robot_id = ev.payload["robot_id"]
                task_id = ev.payload["task_id"]

                # release robot
                robot = next(r for r in self.robots if r.id == robot_id)
                robot.busy = False

                info = self.running.get(robot_id)
                end_time = info["end_time"] if info and "end_time" in info else self._time
                self.completed.append((robot_id, task_id, end_time))

                # remove running entry
                if robot_id in self.running:
                    del self.running[robot_id]

                # After release, attempt to allocate pending tasks again (Option 2, no preemption)
                self._try_allocate_pending(self._time)

            else:
                raise ValueError(f"Unknown event type: {ev.event_type}")
        
        # final not assigned
        final_not_assigned = []
        completed_task_ids = {tid for _, tid, _ in self.completed}
        for t in self.pending_tasks:
            if t.id not in completed_task_ids:
                final_not_assigned.append({
                    "task_id": t.id,
                    "reasons": ["not_completed (remained pending until simulation end)"]
                })
                
                
        return {
            "completed": self.completed,
            "not_assigned": final_not_assigned, 
            "not_assigned_during_run": self.not_assigned_during_run_log,
            "assignment_log": self.assignment_log
        }