
let movementChart = null;
let pathChart = null;
let workloadChart = null;

async function runBenchmark() {
    const button = document.getElementById("runButton");
    const error = document.getElementById("error");

    error.textContent = "";
    button.disabled = true;
    button.textContent = "Running...";

    const data = {
        cylinders: Number(document.getElementById("cylinders").value),
        num_requests: Number(document.getElementById("numRequests").value),
        head: Number(document.getElementById("head").value),
        direction: document.getElementById("direction").value,
        distribution: document.getElementById("distribution").value,
        seed: Number(document.getElementById("seed").value)
    };

    try {
        const response = await fetch("/api/benchmark", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Benchmark failed.");
        }

        displayResults(result);

    } catch (err) {
        error.textContent = err.message;
    } finally {
        button.disabled = false;
        button.textContent = "Run Benchmark";
    }
}


function displayResults(data) {
    const results = data.results;
    const names = Object.keys(results);

    document.getElementById("results").style.display = "block";

    document.getElementById("workloadInfo").textContent =
        `${data.configuration.num_requests} requests | ` +
        `${data.configuration.cylinders} cylinders | ` +
        `Distribution: ${data.configuration.distribution} | ` +
        `Seed: ${data.configuration.seed}`;

    document.getElementById("requestList").textContent =
        data.workload.join(", ");

    // Populate metrics table.
    const table = document.getElementById("metricsTable");
    table.innerHTML = "";

    names.forEach(name => {
        const metric = results[name];

        const row = document.createElement("tr");

        [name, metric.total_movement, metric.average_movement]
            .forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

        table.appendChild(row);
    });

    // Destroy old charts before creating new ones.
    if (movementChart) movementChart.destroy();
    if (pathChart) pathChart.destroy();
    if (workloadChart) workloadChart.destroy();

    // Generated workload distribution scatter chart.
    const workloadPoints = data.workload.map(
        (cylinder, index) => ({
            x: index + 1,
            y: cylinder
        })
    );

    workloadChart = new Chart(
        document.getElementById("workloadChart"),
        {
            type: "scatter",
            data: {
                datasets: [{
                    label: "Disk Requests",
                    data: workloadPoints,
                    showLine: false,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Request Arrival Order"
                        }
                    },
                    y: {
                        min: 0,
                        max: data.configuration.cylinders - 1,
                        title: {
                            display: true,
                            text: "Cylinder Number"
                        }
                    }
                }
            }
        }
    );

    // Total movement bar chart.
    movementChart = new Chart(
        document.getElementById("movementChart"),
        {
            type: "bar",
            data: {
                labels: names,
                datasets: [{
                    label: "Total Head Movement",
                    data: names.map(
                        name => results[name].total_movement
                    ),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Total Cylinders Moved"
                        }
                    }
                }
            }
        }
    );

    // Head movement path line chart.
    const datasets = names.map(name => ({
        label: name,
        data: results[name].head_path.map(
            (cylinder, index) => ({
                x: index,
                y: cylinder
            })
        ),
        borderWidth: 2,
        pointRadius: 1,
        tension: 0
    }));

    pathChart = new Chart(
        document.getElementById("pathChart"),
        {
            type: "line",
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                parsing: false,
                scales: {
                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Movement Step"
                        }
                    },
                    y: {
                        min: 0,
                        max: data.configuration.cylinders - 1,
                        title: {
                            display: true,
                            text: "Cylinder Position"
                        }
                    }
                }
            }
        }
    );
}
