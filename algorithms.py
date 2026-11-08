
# ------------------------------------------
# EXISTING BATCH SCHEDULING ALGORITHMS
# ------------------------------------------

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
        path += left
    else:
        path += sorted(left, reverse=True)
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


# ------------------------------------------
# DYNAMIC SCHEDULING ENGINE
# ------------------------------------------

def run_dynamic_algorithm(
    requests,
    initial_head,
    initial_direction,
    maximum,
    algorithm_name
):
    """
    Event-driven, non-preemptive disk scheduling.

    Head movement: 1 cylinder per time unit.
    Request service time: 0.
    Scheduling decisions occur when the head becomes free.
    """

    future = sorted(
        [dict(req) for req in requests],
        key=lambda r: (r["arrival_time"], r["id"])
    )

    pending = []
    current_head = initial_head
    current_time = 0
    direction = initial_direction

    head_path = [initial_head]
    service_order = []
    service_ids = []
    completion_details = []

    total_movement = 0

    def add_arrived_requests():
        while future and future[0]["arrival_time"] <= current_time:
            pending.append(future.pop(0))

    def move_to(target):
        nonlocal current_head, current_time, total_movement

        distance = abs(target - current_head)

        current_time += distance
        total_movement += distance
        current_head = target

        head_path.append(target)

        add_arrived_requests()

    def choose_directional_request():
        if direction == "right":
            candidates = [
                r for r in pending
                if r["cylinder"] >= current_head
            ]
            return min(
                candidates,
                key=lambda r: (r["cylinder"], r["arrival_time"], r["id"])
            ) if candidates else None

        candidates = [
            r for r in pending
            if r["cylinder"] <= current_head
        ]

        return min(
            candidates,
            key=lambda r: (-r["cylinder"], r["arrival_time"], r["id"])
        ) if candidates else None

    while future or pending:

        add_arrived_requests()

        # If no request is waiting, advance time to the next arrival.
        if not pending:
            current_time = future[0]["arrival_time"]
            add_arrived_requests()
            continue

        chosen = None

        if algorithm_name == "FCFS":
            chosen = min(
                pending,
                key=lambda r: (r["arrival_time"], r["id"])
            )

        elif algorithm_name == "SSTF":
            chosen = min(
                pending,
                key=lambda r: (
                    abs(r["cylinder"] - current_head),
                    r["arrival_time"],
                    r["id"]
                )
            )

        elif algorithm_name in ("SCAN", "C-SCAN", "LOOK", "C-LOOK"):

            chosen = choose_directional_request()

            if chosen is None:

                if algorithm_name == "SCAN":
                    # Continue to the physical disk boundary.
                    boundary = maximum if direction == "right" else 0
                    move_to(boundary)
                    direction = "left" if direction == "right" else "right"

                elif algorithm_name == "C-SCAN":
                    # Reach the boundary and wrap to the opposite end.
                    boundary = maximum if direction == "right" else 0
                    opposite = 0 if direction == "right" else maximum

                    move_to(boundary)
                    move_to(opposite)

                elif algorithm_name == "LOOK":
                    direction = "left" if direction == "right" else "right"

                elif algorithm_name == "C-LOOK":
                    # Jump to the opposite extreme pending request.
                    if direction == "right":
                        chosen = min(
                            pending,
                            key=lambda r: (
                                r["cylinder"],
                                r["arrival_time"],
                                r["id"]
                            )
                        )
                    else:
                        chosen = max(
                            pending,
                            key=lambda r: (
                                r["cylinder"],
                                -r["arrival_time"],
                                -r["id"]
                            )
                        )

            if chosen is None:
                chosen = choose_directional_request()

        if chosen is None:
            raise RuntimeError(
                f"Unable to select a request for {algorithm_name}."
            )

        # Record waiting time when the seek starts.
        waiting_time = current_time - chosen["arrival_time"]

        # Remove only the selected request.
        pending.remove(chosen)

        # Perform the seek. New arrivals during this seek
        # become pending after the movement completes.
        move_to(chosen["cylinder"])

        completion_time = current_time
        response_time = completion_time - chosen["arrival_time"]

        service_order.append(chosen["cylinder"])
        service_ids.append(chosen["id"])

        completion_details.append({
            "id": chosen["id"],
            "cylinder": chosen["cylinder"],
            "arrival_time": chosen["arrival_time"],
            "waiting_time": waiting_time,
            "completion_time": completion_time,
            "response_time": response_time
        })

    count = len(requests)

    total_waiting = sum(
        item["waiting_time"] for item in completion_details
    )

    total_response = sum(
        item["response_time"] for item in completion_details
    )

    max_waiting = max(
        (item["waiting_time"] for item in completion_details),
        default=0
    )

    return {
        "service_order": service_order,
        "service_ids": service_ids,
        "head_path": head_path,
        "total_movement": total_movement,
        "average_movement": round(total_movement / count, 2) if count else 0,
        "average_waiting_time": round(total_waiting / count, 2) if count else 0,
        "maximum_waiting_time": max_waiting,
        "average_response_time": round(total_response / count, 2) if count else 0,
        "total_completion_time": current_time,
        "throughput": round(count / current_time, 4) if current_time > 0 else 0,
        "completed_requests": completion_details
    }


def run_all_dynamic_algorithms(
    requests,
    head,
    direction,
    maximum
):
    results = {}

    for name in ALGORITHMS:
        results[name] = run_dynamic_algorithm(
            requests=requests,
            initial_head=head,
            initial_direction=direction,
            maximum=maximum,
            algorithm_name=name
        )

    return results
