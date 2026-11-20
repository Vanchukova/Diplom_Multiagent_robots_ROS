from warehouse_core.assignment import (
    ELEVATOR_ENTRANCE,
    Assignment,
    Robot,
    Task,
    assign_tasks,
    nearest_robot,
    sort_by_urgency,
)


def test_urgent_tasks_go_first_and_keep_order():
    a = Task(0, 0, 1, False)
    b = Task(1, 0, 1, True)
    c = Task(2, 0, 1, False)
    d = Task(3, 0, 1, True)
    assert sort_by_urgency([a, b, c, d]) == [b, d, a, c]


def test_nearest_robot_tie_goes_to_first_listed():
    first = Robot(1, -1, 0, 1)
    second = Robot(2, 1, 0, 1)
    assert nearest_robot([first, second], 0, 0) == first


def test_task_goes_to_nearest_robot_on_same_level():
    robots = [Robot(1, 10, 0, 1), Robot(2, 2, 0, 1), Robot(3, 0, 0, 2)]
    result = assign_tasks([Task(0, 0, 1, False)], robots, elevator_free=True)
    assert result == [Assignment(0, 2, False)]


def test_each_robot_gets_at_most_one_task():
    robots = [Robot(1, 0, 0, 1)]
    tasks = [Task(0, 0, 1, True), Task(1, 0, 1, False)]
    assert assign_tasks(tasks, robots, elevator_free=True) == [Assignment(0, 1, False)]


def test_other_level_task_uses_robot_nearest_to_elevator():
    near_elevator = Robot(1, ELEVATOR_ENTRANCE[0] + 1, ELEVATOR_ENTRANCE[1], 1)
    far = Robot(2, 20, -40, 1)
    result = assign_tasks([Task(0, 0, 2, False)], [far, near_elevator], elevator_free=True)
    assert result == [Assignment(0, 1, True)]


def test_only_one_elevator_ride_per_round():
    robots = [Robot(1, 0, 0, 1), Robot(2, 5, 0, 1)]
    tasks = [Task(0, 0, 2, False), Task(1, 0, 2, False)]
    result = assign_tasks(tasks, robots, elevator_free=True)
    assert [a.task_index for a in result] == [0]


def test_other_level_task_waits_when_elevator_busy():
    robots = [Robot(1, 0, 0, 1)]
    tasks = [Task(0, 0, 2, False), Task(5, 5, 1, False)]
    assert assign_tasks(tasks, robots, elevator_free=False) == [Assignment(1, 1, False)]


def test_no_ready_robots_means_no_assignments():
    assert assign_tasks([Task(0, 0, 1, True)], [], elevator_free=True) == []
