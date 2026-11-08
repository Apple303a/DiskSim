
let movementChart = null;
let pathChart = null;
let workloadChart = null;

let currentMetrics = {};
let currentIsDynamic = false;
let sortKey = null;
let sortDirection = "asc";

async function runBenchmark() {
    const button = document.getElementById("runButton");
    const error = document.getElementById("error");

    error.textContent = "";
    button.disabled = true;
    button.textContent = "Running...";

    const data = {
        mode: document.getElementById("mode").value,
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
    const isDynamic = data.mode === "dynamic";

    document.getElementById("results").style.display = "block";

    document.getElementById("workloadInfo").textContent =
        `${data.configuration.num_requests} requests | ` +
        `${data.configuration.cylinders} cylinders | ` +
        `Distribution: ${data.configuration.distribution} | ` +
        `Mode: ${data.mode} | Seed: ${data.configuration.seed}`;

    // Display workload.
    const requestList = document.getElementById("requestList");

    if (isDynamic) {
        requestList.innerHTML = "";

        const table = document.createElement("table");
        table.className = "table table-sm table-bordered mt-2";

        table.innerHTML = `
            <thead>
                <tr>
                    <th>Request ID</th>
                    <th>Cylinder</th>
                    <th>Arrival Time</th>
                </tr>
            </thead>
        `;

        const tbody = document.createElement("tbody");

        data.workload.forEach(request => {
            const row = document.createElement("tr");

            [request.id, request.cylinder, request.arrival_time]
                .forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        requestList.appendChild(table);

    } else {
        requestList.textContent = data.workload.join(", ");
    }

    // Metrics table headers.

    // Metrics table.
    currentMetrics = results;
    currentIsDynamic = isDynamic;
    sortKey = null;
    sortDirection = "asc";

    renderMetricsTable();

    // Destroy previous charts.
    if (movementChart) movementChart.destroy();
    if (pathChart) pathChart.destroy();
    if (workloadChart) workloadChart.destroy();

    // Workload distribution chart.
    const workloadPoints = isDynamic
        ? data.workload.map(request => ({
            x: request.arrival_time,
            y: request.cylinder
        }))
        : data.workload.map((cylinder, index) => ({
            x: index + 1,
            y: cylinder
        }));

    document.getElementById("workloadChartInfo").textContent =
        isDynamic
            ? "X-axis: Arrival time. Y-axis: Requested cylinder."
            : "X-axis: Request arrival order. Y-axis: Requested cylinder.";

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
                            text: isDynamic ? "Arrival Time" : "Request Order"
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

    // Total movement comparison.
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

    // Head movement paths.
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

    document.getElementById("pathChartInfo").textContent =
        isDynamic
            ? "X-axis: Movement event (not simulated time). Y-axis: Cylinder position."
            : "X-axis: Movement step. Y-axis: Cylinder position.";

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
                            text: "Movement Event"
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

function renderMetricsTable() {
    const metricsHead = document.getElementById("metricsHead");
    const table = document.getElementById("metricsTable");

    metricsHead.innerHTML = "";
    table.innerHTML = "";

    const columns = currentIsDynamic
        ? [
            { label: "Algorithm", key: "algorithm" },
            { label: "Total Movement", key: "total_movement" },
            { label: "Average Movement", key: "average_movement" },
            { label: "Average Waiting", key: "average_waiting_time" },
            { label: "Maximum Waiting", key: "maximum_waiting_time" },
            { label: "Average Response", key: "average_response_time" },
            { label: "Throughput", key: "throughput" },
            { label: "Completion Time", key: "total_completion_time" }
        ]
        : [
            { label: "Algorithm", key: "algorithm" },
            { label: "Total Movement", key: "total_movement" },
            { label: "Average Movement", key: "average_movement" }
        ];

    // Create sortable column headings.
    const headerRow = document.createElement("tr");

    columns.forEach(column => {
        const th = document.createElement("th");
        const button = document.createElement("button");

        button.className =
            "btn btn-link p-0 text-dark text-decoration-none fw-bold";
        button.style.cursor = "pointer";

        let arrow = "";

        if (sortKey === column.key) {
            arrow = sortDirection === "asc" ? " ▲" : " ▼";
        }

        button.textContent = column.label + arrow;

        button.onclick = () => {
            if (sortKey === column.key) {
                sortDirection =
                    sortDirection === "asc" ? "desc" : "asc";
            } else {
                sortKey = column.key;
                sortDirection = "asc";
            }

            renderMetricsTable();
        };

        th.appendChild(button);
        headerRow.appendChild(th);
    });

    metricsHead.appendChild(headerRow);

    // Prepare rows.
    let names = Object.keys(currentMetrics);

    // Sort rows when a column is selected.
    if (sortKey !== null) {
        names.sort((a, b) => {
            const valueA = sortKey === "algorithm"
                ? a
                : currentMetrics[a][sortKey];

            const valueB = sortKey === "algorithm"
                ? b
                : currentMetrics[b][sortKey];

            let comparison;

            if (typeof valueA === "string") {
                comparison = valueA.localeCompare(valueB);
            } else {
                comparison = valueA - valueB;
            }

            return sortDirection === "asc"
                ? comparison
                : -comparison;
        });
    }

    // Populate table.
    names.forEach(name => {
        const metric = currentMetrics[name];

        const values = currentIsDynamic
            ? [
                name,
                metric.total_movement,
                metric.average_movement,
                metric.average_waiting_time,
                metric.maximum_waiting_time,
                metric.average_response_time,
                Number(metric.throughput).toFixed(3),
                metric.total_completion_time
            ]
            : [
                name,
                metric.total_movement,
                metric.average_movement
            ];

        const row = document.createElement("tr");

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        table.appendChild(row);
    });
}