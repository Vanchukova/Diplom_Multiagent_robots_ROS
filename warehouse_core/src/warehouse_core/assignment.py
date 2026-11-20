"""Task-to-robot assignment (extracted from distributor/scripts/distribute_goal_*.py)."""
import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

ELEVATOR_ENTRANCE: Tuple[float, float] = (-23.0, 40.0)


@dataclass(frozen=True)
class Robot:
    number: int
    x: float
    y: float
    level: int


@dataclass(frozen=True)
class Task:
    x: float
    y: float
    level: int
    urgent: bool


@dataclass(frozen=True)
class Assignment:
    task_index: int
    robot_number: int
    via_elevator: bool


def sort_by_urgency(tasks: Sequence[Task]) -> List[Task]:
    """Urgent tasks first; tasks with equal urgency keep their order."""
    return sorted(tasks, key=lambda task: task.urgent, reverse=True)


def distance(robot: Robot, x: float, y: float) -> float:
    return math.sqrt((robot.x - x) ** 2 + (robot.y - y) ** 2)


def nearest_robot(robots: Sequence[Robot], x: float, y: float) -> Robot:
    """Closest robot to (x, y); on a tie the one listed first wins."""
    return min(robots, key=lambda robot: distance(robot, x, y))


def assign_tasks(
    pending_tasks: Sequence[Task],
    ready_robots: Sequence[Robot],
    elevator_free: bool,
) -> List[Assignment]:
    """Assign pending tasks to ready robots, in task order.

    A task goes to the nearest ready robot on the same level. If there is none,
    and the elevator is free, it goes to the ready robot nearest to the elevator
    (that robot will ride the elevator); only one such ride per call. Otherwise
    the task waits for the next call.
    """
    free_robots = list(ready_robots)
    assignments: List[Assignment] = []

    for task_index, task in enumerate(pending_tasks):
        if not free_robots:
            break

        same_level = [robot for robot in free_robots if robot.level == task.level]
        if same_level:
            robot = nearest_robot(same_level, task.x, task.y)
            via_elevator = False
        elif elevator_free:
            robot = nearest_robot(free_robots, *ELEVATOR_ENTRANCE)
            via_elevator = True
            elevator_free = False
        else:
            continue

        free_robots.remove(robot)
        assignments.append(Assignment(task_index, robot.number, via_elevator))

    return assignments
