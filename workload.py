
import random


def generate_workload(
    distribution,
    num_requests,
    num_cylinders,
    seed,
    hotspot_count=3,
    burst_size=8
):
    rng = random.Random(seed)
    max_cylinder = num_cylinders - 1

    if distribution == "uniform":
        return [
            rng.randint(0, max_cylinder)
            for _ in range(num_requests)
        ]

    elif distribution == "locality":
        hotspots = [
            rng.randint(0, max_cylinder)
            for _ in range(hotspot_count)
        ]

        current = rng.choice(hotspots)
        requests = []

        for _ in range(num_requests):
            choice = rng.random()

            if choice < 0.70:
                cylinder = round(
                    rng.gauss(current, num_cylinders * 0.04)
                )
            elif choice < 0.90:
                cylinder = rng.choice(hotspots)
            else:
                cylinder = rng.randint(0, max_cylinder)

            current = max(0, min(max_cylinder, cylinder))
            requests.append(current)

        return requests

    elif distribution == "sequential":
        requests = []
        actual_burst_size = min(burst_size, num_cylinders)

        while len(requests) < num_requests:
            direction = rng.choice([-1, 1])

            if direction == 1:
                start = rng.randint(
                    0, max_cylinder - actual_burst_size + 1
                )
            else:
                start = rng.randint(
                    actual_burst_size - 1, max_cylinder
                )

            for i in range(actual_burst_size):
                if len(requests) >= num_requests:
                    break

                requests.append(start + direction * i)

        return requests

    else:
        raise ValueError("Invalid workload distribution")


def generate_dynamic_workload(
    distribution,
    num_requests,
    num_cylinders,
    seed
):
    """
    Generate the same cylinder workload as batch mode,
    but assign an arrival time to each request.

    First request arrives at time 0.
    Subsequent requests arrive after random intervals of 1-5 units.
    """

    cylinders = generate_workload(
        distribution=distribution,
        num_requests=num_requests,
        num_cylinders=num_cylinders,
        seed=seed
    )

    rng = random.Random(seed + 1)
    current_time = 0
    requests = []

    for index, cylinder in enumerate(cylinders):
        if index > 0:
            current_time += rng.randint(1, 5)

        requests.append({
            "id": index + 1,
            "cylinder": cylinder,
            "arrival_time": current_time
        })

    return requests
