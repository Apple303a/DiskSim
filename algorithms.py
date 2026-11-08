def fcfs(requests, head, direction, maximum):
    return list(requests), list(requests)


def sstf(requests, head, direction, maximum):
    pending = list(requests)
    order = []
    current = head

    while pending:
        nearest = min(
            pending,
            key=lambda x: (abs(x - current), x)
        )
        order.append(nearest)
        pending.remove(nearest)
        current = nearest

    return order, order.copy()


def scan(requests, head, direction, maximum):
    equal = [x for x in requests if x == head]
    left = sorted([x for x in requests if x < head], reverse=True)
    right = sorted([x for x in requests if x > head])

    if direction == "right":
        order = equal + right + left
        path = equal + right

        if left:
            if not path or path[-1] != maximum:
                path.append(maximum)
            path += left

    else:
        order = equal + left + right
        path = equal + left

        if right:
            if not path or path[-1] != 0:
                path.append(0)
            path += right

    return order, path


def cscan(requests, head, direction, maximum):
    equal = [x for x in requests if x == head]
    left = sorted([x for x in requests if x < head])
    right = sorted([x for x in requests if x > head])

    if direction == "right":
        order = equal + right + left
        path = equal + right

        if left:
            path += [maximum, 0] + left

    else:
        order = equal + sorted(left, reverse=True) + sorted(right, reverse=True)
        path = equal + sorted(left, reverse=True)

        if right:
            path += [0, maximum] + sorted(right, reverse=True)

    return order, path


def look(requests, head, direction, maximum):
    equal = [x for x in requests if x == head]
    left = sorted([x for x in requests if x < head], reverse=True)
    right = sorted([x for x in requests if x > head])

    if direction == "right":
        order = equal + right + left
    else:
        order = equal + left + right

    return order, order.copy()


def clook(requests, head, direction, maximum):
    equal = [x for x in requests if x == head]
    left = sorted([x for x in requests if x < head])
    right = sorted([x for x in requests if x > head])

    if direction == "right":
        order = equal + right + left
    else:
        order = equal + sorted(left, reverse=True) + sorted(right, reverse=True)

    path = equal.copy()

    if direction == "right":
        path += right
        if left:
            path += left
    else:
        path += sorted(left, reverse=True)
        if right:
            path += sorted(right, reverse=True)

    return order, path


ALGORITHMS = {
    "FCFS": fcfs,
    "SSTF": sstf,
    "SCAN": scan,
    "C-SCAN": cscan,
    "LOOK": look,
    "C-LOOK": clook
}


def calculate_metrics(order, movement_points, initial_head):
    head_path = [initial_head] + movement_points

    total = sum(
        abs(head_path[i] - head_path[i - 1])
        for i in range(1, len(head_path))
    )

    return {
        "service_order": order,
        "head_path": head_path,
        "total_movement": total,
        "average_movement": round(total / len(order), 2) if order else 0
    }


def run_all_algorithms(requests, head, direction, maximum):
    results = {}

    for name, algorithm in ALGORITHMS.items():
        order, movement_points = algorithm(
            requests, head, direction, maximum
        )

        results[name] = calculate_metrics(
            order, movement_points, head
        )

    return results