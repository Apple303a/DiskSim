from flask import Flask, render_template, request, jsonify

from workload import generate_workload
from algorithms import run_all_algorithms

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/benchmark", methods=["POST"])
def benchmark():
    try:
        data = request.get_json()

        cylinders = int(data.get("cylinders", 200))
        num_requests = int(data.get("num_requests", 100))
        head = int(data.get("head", 100))
        direction = data.get("direction", "right")
        distribution = data.get("distribution", "uniform")
        seed = int(data.get("seed", 42))

        if not 2 <= cylinders <= 10000:
            raise ValueError("Cylinders must be between 2 and 10000.")

        if not 1 <= num_requests <= 10000:
            raise ValueError("Requests must be between 1 and 10000.")

        if not 0 <= head < cylinders:
            raise ValueError("Initial head must be within disk boundaries.")

        if direction not in ("left", "right"):
            raise ValueError("Invalid direction.")

        if distribution not in ("uniform", "locality", "sequential"):
            raise ValueError("Invalid distribution.")

        requests_list = generate_workload(
            distribution=distribution,
            num_requests=num_requests,
            num_cylinders=cylinders,
            seed=seed
        )

        results = run_all_algorithms(
            requests=requests_list,
            head=head,
            direction=direction,
            maximum=cylinders - 1
        )

        return jsonify({
            "workload": requests_list,
            "configuration": {
                "cylinders": cylinders,
                "num_requests": num_requests,
                "head": head,
                "direction": direction,
                "distribution": distribution,
                "seed": seed
            },
            "results": results
        })

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)