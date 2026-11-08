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
                # Access near the previous request.
                cylinder = round(rng.gauss(current, num_cylinders * 0.04))

            elif choice < 0.90:
                # Occasionally jump to a hotspot.
                cylinder = rng.choice(hotspots)

            else:
                # Occasional disk-wide random access.
                cylinder = rng.randint(0, max_cylinder)

            current = max(0, min(max_cylinder, cylinder))
            requests.append(current)

        return requests
    
    elif distribution == "sequential":
        requests = []

        while len(requests) < num_requests:
            start = rng.randint(0, max_cylinder)
            direction = rng.choice([-1, 1])

            for i in range(burst_size):
                if len(requests) >= num_requests:
                    break

                cylinder = start + direction * i

                if 0 <= cylinder <= max_cylinder:
                    requests.append(cylinder)

        return requests

    else:
        raise ValueError("Invalid workload distribution")