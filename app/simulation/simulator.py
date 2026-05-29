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

        self.pending_tasks = []
        self.running: Dict[str, Dict[str, Any]] = {}  # robot_id -> info

        self.completed: List[Tuple[str, str, float]] = []  # (robot_id, task_id, end_time)
        self.assignment_log: List[Dict[str, Any]] = []
        self.not_assigned_log: List[Dict[str, Any]] = []
        
        # temporary diagnostic: non assigned during the first cycle, but likely assigned later
        self.not_assigned_during_run_log: List[Dict[str, Any]] = []

        # heap of events
        self.events: List[ScheduledEvent] = []

        # task arrival/completion metrics
        self.arrival_time_by_task_id: Dict[str, float] = {}
        self.completion_time_by_task_id: Dict[str, float] = {}

        # robot utilization (busy time)
        self.busy_time_total_by_robot_id: Dict[str, float] = {r.id: 0.0 for r in self.robots}

        # counts allocation triggers / new assignments
        self.allocation_triggers_count: int = 0
        self.new_assignments_count: int = 0

        # helper: map task_id -> task object per durata
        self.task_by_id: Dict[str, Any] = {}

        # store all tasks for final reporting
        self.tasks_total: List[Any] = []

    def _push_event(self, time: float, event_type: str, payload: Dict[str, Any]):
        self._seq += 1
        heapq.heappush(self.events, ScheduledEvent(time=time, seq=self._seq, event_type=event_type, payload=payload))

    def _duration(self, robot, task) -> float:
        # T = d / v, deterministic; using allocator distance model for consistency
        dist = self.allocator.calculate_distance(robot, task)
        if self.v <= 0:
            raise ValueError("v must be > 0")
        return dist / self.v

    def _prepare_task_maps(self):
        """
        tasks input atteso in Milestone 3:
        [
          {"task": Task, "arrival_time": float},
          {"task": Task, "arrival_time": float},
          ...
        ]
        """
        self.pending_tasks = []
        self.running = {}
        self.completed = []
        self.assignment_log = []
        self.not_assigned_log = []
        self.not_assigned_during_run_log = []

        self.arrival_time_by_task_id = {}
        self.completion_time_by_task_id = {}
        self.busy_time_total_by_robot_id = {r.id: 0.0 for r in self.robots}

        self.allocation_triggers_count = 0
        self.new_assignments_count = 0

        self.task_by_id = {}
        self.tasks_total = []

        # reset event heap
        self.events = []
        self._seq = 0

        for item in self.tasks:
            task = item["task"]
            arrival_time = float(item["arrival_time"])
            self.task_by_id[task.id] = task
            self.tasks_total.append(task)
            self.arrival_time_by_task_id[task.id] = arrival_time

            self._push_event(arrival_time, "TASK_ARRIVED", {
                "task_id": task.id
            })

        # tie-break: trigger initial allocations at t=0 only via RobotFree.

    def _try_allocate_pending(self, now: float):
        # Allocate as many pending tasks as possible among robots that are free.
        # Option 2 (no preemption): we only allocate pending tasks when robots free.
        free_snapshot = [r for r in self.robots if not r.busy]
        if not free_snapshot:
            return

        # Consider only currently pending tasks
        if not self.pending_tasks:
            return
            
        self.allocation_triggers_count += 1    

        # Run allocator on pending tasks. It will set busy=True immediately.
        assignments, not_assigned, trace = self.allocator.allocate(self.robots, self.pending_tasks)

        # Log traces for audit (Milestone 2 deliverable)
        self.assignment_log.extend(trace)

        # remove assigned tasks from pending
        assigned_task_ids = set(tid for _, tid in assignments)
        before_count = len(self.pending_tasks)

        # Mark not assigned tasks removed from pending
        if not_assigned:
            for item in not_assigned:
                self.not_assigned_during_run_log.append({
                    "time": now,
                    "task_id": item["task_id"],
                    "reasons": item.get("reasons", [])
                })
                
        self.pending_tasks = [t for t in self.pending_tasks if t.id not in assigned_task_ids]
        
        # metric: new assignments created in this trigger
        self.new_assignments_count += len(assignments)
       

        for robot_id, task_id in assignments:
            robot = next(r for r in free_snapshot if r.id == robot_id)
            task = self.task_by_id[task_id]

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
            
    def _finish_robot(self, robot_id: str, now: float, task_id: str):
        robot = next(r for r in self.robots if r.id == robot_id)
        
        #update battery
        task = self.task_by_id.get(task_id)
        if task is not None:
            consumption = self.allocator.calculate_consumption(robot, task)
            robot.battery -= consumption

            # opzionale: evita valori negativi che possono confondere debug
            if robot.battery < 0:
                robot.battery = 0   
        robot.busy = False
        
        info = self.running.get(robot_id)
        if info:
            start_time = info.get("start_time", now)
            # busy time accounting
            self.busy_time_total_by_robot_id[robot_id] += max(0.0, now - start_time)

            end_time = info.get("end_time", now)
            self.completed.append((robot_id, task_id, end_time))
            self.completion_time_by_task_id[task_id] = end_time

            del self.running[robot_id]
        else:
            # fallback: if running entry missing
            self.completed.append((robot_id, task_id, now))
            self.completion_time_by_task_id[task_id] = now
            
    def _compute_metrics(self):
        total_tasks = len(self.tasks_total)
        completed_ids = set(self.completion_time_by_task_id.keys())
        completed_count = len(completed_ids)

        # makespan based on last completion
        if completed_count > 0:
            t_end = max(self.completion_time_by_task_id.values())
        else:
            t_end = 0.0
        total_time = max(0.0, t_end - 0.0)

        throughputs = completed_count
        throughput_rate = (completed_count / total_time) if total_time > 0 else 0.0

        # latency stats
        latencies = []
        for tid, ctime in self.completion_time_by_task_id.items():
            atime = self.arrival_time_by_task_id.get(tid, 0.0)
            lat = ctime - atime
            latencies.append(lat)

        if latencies:
            latencies_sorted = sorted(latencies)
            p50 = latencies_sorted[int(0.50 * (len(latencies_sorted) - 1))]
            p90 = latencies_sorted[int(0.90 * (len(latencies_sorted) - 1))]
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
        else:
            p50 = p90 = avg_latency = max_latency = 0.0

        # utilization
        utilization_per_robot = {}
        for r_id, busy_t in self.busy_time_total_by_robot_id.items():
            utilization_per_robot[r_id] = (busy_t / total_time) if total_time > 0 else 0.0

        avg_utilization = (sum(utilization_per_robot.values()) / len(utilization_per_robot)) if utilization_per_robot else 0.0

        return {
            "total_tasks": total_tasks,
            "completed_count": completed_count,
            "throughput_total": throughputs,
            "makespan": t_end,
            "throughput_rate": throughput_rate,
            "avg_latency": avg_latency,
            "p50_latency": p50,
            "p90_latency": p90,
            "max_latency": max_latency,
            "avg_utilization": avg_utilization,
            "utilization_per_robot": utilization_per_robot,
            "allocation_triggers_count": self.allocation_triggers_count,
            "new_assignments_count": self.new_assignments_count,
        }

    def run(self):
        self._prepare_task_maps()

        while self.events:
            ev = heapq.heappop(self.events)
            self._time = ev.time

            if ev.event_type == "TASK_ARRIVED":
                task_id = ev.payload["task_id"]
                task = self.task_by_id[task_id]
                self.pending_tasks.append(task)

                # trigger anche su arrivo se ci sono robot free
                self._try_allocate_pending(self._time)
                continue

            if ev.event_type == "TASK_COMPLETED":
                robot_id = ev.payload["robot_id"]
                task_id = ev.payload["task_id"]

                self._finish_robot(robot_id=robot_id, now=self._time, task_id=task_id)

                # trigger allocation only after robot becomes free
                self._try_allocate_pending(self._time)
                continue

            raise ValueError(f"Unknown event type: {ev.event_type}")

        # final not assigned: tasks remaining in pending OR tasks never completed
        completed_task_ids = set(self.completion_time_by_task_id.keys())
        final_not_assigned = []
        for t in self.pending_tasks:
            if t.id not in completed_task_ids:
                final_not_assigned.append({
                    "task_id": t.id,
                    "reasons": ["not_completed (remained pending until simulation end)"]
                })

        metrics = self._compute_metrics()

        battery_remaining = {r.id: float(r.battery) for r in self.robots}
        
        
        return {
            "completed": self.completed,
            "not_assigned": final_not_assigned,
            "not_assigned_during_run": self.not_assigned_during_run_log,
            "assignment_log": self.assignment_log,
            "metrics": metrics,
            "tasks_total": self.tasks_total,
            "battery_remaining": battery_remaining
        }