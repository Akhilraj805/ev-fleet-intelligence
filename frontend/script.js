const API_URL = "https://ev-fleet-intelligence-9ysb.onrender.com";
let selectedVehicleData = null;

/* =========================================================
   THEME TOGGLE
   ========================================================= */

const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

const savedTheme = localStorage.getItem("theme");

if (savedTheme === "light") {
    document.documentElement.setAttribute(
        "data-theme",
        "light"
    );

    if (themeIcon) {
        themeIcon.textContent = "☀";
    }
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {

        const isLight =
            document.documentElement.getAttribute(
                "data-theme"
            ) === "light";

        if (isLight) {

            document.documentElement.removeAttribute(
                "data-theme"
            );

            localStorage.setItem(
                "theme",
                "dark"
            );

            themeIcon.textContent = "☾";

        } else {

            document.documentElement.setAttribute(
                "data-theme",
                "light"
            );

            localStorage.setItem(
                "theme",
                "light"
            );

            themeIcon.textContent = "☀";
        }
        // Rebuild Chart.js charts with the new theme colors
        if (
            document.getElementById("healthChart")
        ) {
            loadFleetAnalytics();
        }
    });
}

function openVehicleDetails(vehicleId) {

    window.location.href =
        `vehicle-details.html?id=${vehicleId}`;

}


// -----------------------------
// Load Fleet Summary
// -----------------------------

async function loadFleetSummary() {

    try {

        const response = await authenticatedFetch(
            `${API_URL}/fleet/summary`
        );

        const data = await response.json();


        // -----------------------------
        // Dashboard Summary
        // -----------------------------

        const totalVehicles =
            document.getElementById("totalVehicles");

        if (totalVehicles) {
            totalVehicles.textContent =
                data.total_vehicles;
        }


        const batteryHealth =
            document.getElementById("batteryHealth");

        if (batteryHealth) {
            batteryHealth.textContent =
                data.average_battery_health + "%";
        }


        const faultRecords =
            document.getElementById("faultRecords");

        if (faultRecords) {
            faultRecords.textContent =
                data.fault_records;
        }


       


        // -----------------------------
        // Analytics Page
        // -----------------------------

        const analyticsFaultRecords =
            document.getElementById(
                "analyticsFaultRecords"
            );

        if (analyticsFaultRecords) {

            analyticsFaultRecords.textContent =
                data.fault_records;

        }


        const analyticsNormalRecords =
            document.getElementById(
                "analyticsNormalRecords"
            );

        if (analyticsNormalRecords) {

            analyticsNormalRecords.textContent =
                data.normal_records ??
                (
                    data.total_vehicles === undefined
                        ? "--"
                        : data.normal_records
                );

        }


        const analyticsBatteryHealth =
            document.getElementById(
                "analyticsBatteryHealth"
            );

        if (analyticsBatteryHealth) {

            analyticsBatteryHealth.textContent =
                data.average_battery_health + "%";

        }


        const analyticsTotalVehicles =
            document.getElementById(
                "analyticsTotalVehicles"
            );

        if (analyticsTotalVehicles) {

            analyticsTotalVehicles.textContent =
                data.total_vehicles;

        }


    } catch (error) {

        console.error(
            "Error loading fleet summary:",
            error
        );

    }
}


// -----------------------------
// Load Vehicles
// -----------------------------

async function loadVehicles() {

    try {

        const response = await authenticatedFetch(
    `${API_URL}/vehicles`
        );

        const data = await response.json();

        const fleetSize =
            document.getElementById("fleetSize");

        if (fleetSize) {
            fleetSize.textContent =
                data.total_vehicles;
        }

        const vehicleCount =
            document.getElementById("vehicleCount");

        if (vehicleCount) {
            vehicleCount.textContent =
                data.total_vehicles;
        }

        const vehicleList =
            document.getElementById("vehicleList");


        vehicleList.innerHTML = "";

        const vehiclesToDisplay =
    window.location.pathname.endsWith("vehicles.html")
        ? data.vehicles
        : data.vehicles.slice(0, 6);


        vehiclesToDisplay.forEach(vehicle => {
        
        const div = document.createElement("div");

        div.className = "vehicle-item";

        div.innerHTML = `
            <span class="vehicle-id">
                ${vehicle}
            </span>

            <span class="vehicle-status">
                Fleet Vehicle
            </span>

            <span class="vehicle-health">
                Active
            </span>

            <button
                class="vehicle-action"
                type="button">
                View
            </button>
        `;


    const viewButton =
        div.querySelector(".vehicle-action");


    viewButton.addEventListener(
    "click",
    (event) => {

        event.stopPropagation();

        openVehicleDetails(vehicle);

    }
);


    vehicleList.appendChild(div);

});

    } catch (error) {

        console.error(
            "Error loading vehicles:",
            error
        );

    }
}


// -----------------------------
// Load Vehicle Details
// -----------------------------

async function loadVehicleDetails(vehicleId) {

    try {

            const response = await authenticatedFetch(
                `${API_URL}/vehicles/${vehicleId}`
            );

            if (!response.ok) {

                throw new Error(
                    `Vehicle API returned ${response.status}`
                );

            }

            const data = await response.json();

                selectedVehicleData = data;

                console.log(
                    "Vehicle data received:",
                    data
                );


        if (data.error) {

            alert(data.error);

            return;
        }


        // Show details section

        document.getElementById(
            "vehicleDetails"
        ).style.display = "block";


        
        
        // Basic telemetry

        document.getElementById(
            "detailVoltage"
        ).textContent =
            `${data.battery_voltage.toFixed(2)} V`;


        document.getElementById(
            "detailCurrent"
        ).textContent =
            `${data.battery_current.toFixed(2)} A`;


        document.getElementById(
            "detailBatteryTemp"
        ).textContent =
            `${data.battery_temperature.toFixed(2)} °C`;


        document.getElementById(
            "detailMotorTemp"
        ).textContent =
            `${data.motor_temperature.toFixed(2)} °C`;


        document.getElementById(
            "detailSpeed"
        ).textContent =
            `${data.vehicle_speed.toFixed(2)} km/h`;


        document.getElementById(
            "detailOdometer"
        ).textContent =
            `${data.odometer.toFixed(2)} km`;


        document.getElementById(
            "detailCycles"
        ).textContent =
            data.charging_cycles;


        // Fault

        document.getElementById(
            "detailFault"
        ).textContent =
            data.fault_code;

        // Battery health
        // Use the value calculated by the backend

        const health = data.battery_health;


        document.getElementById(
            "detailHealth"
        ).textContent =
            `${health.toFixed(2)}%`;


        // Maintenance risk

        let risk;

        if (
            health < 50 ||
            data.battery_temperature > 48 ||
            data.motor_temperature > 90 ||
            data.charging_cycles > 1200
        ) {

            risk = "HIGH";

        } else if (
            health < 70 ||
            data.battery_temperature > 43 ||
            data.motor_temperature > 80 ||
            data.charging_cycles > 1000
        ) {

            risk = "MEDIUM";

        } else {

            risk = "LOW";
        }


        document.getElementById(
            "detailRisk"
        ).textContent = risk;


        // Recommendation

        let recommendation;

        if (health < 50) {

            recommendation =
                "Battery inspection recommended";

        } else if (data.battery_temperature > 48) {

            recommendation =
                "Check battery cooling system";

        } else if (data.motor_temperature > 90) {

            recommendation =
                "Inspect motor cooling system";

        } else if (data.charging_cycles > 1200) {

            recommendation =
                "Battery degradation inspection recommended";

        } else if (health < 70) {

            recommendation =
                "Schedule battery maintenance";

        } else {

            recommendation =
                "No immediate maintenance required";
        }


        document.getElementById(
            "detailRecommendation"
        ).textContent = recommendation;

     loadVehicleHistory(vehicleId);   

    } catch (error) {

        console.error(
            "Error loading vehicle details:",
            error
        );

    }
}

// -----------------------------
// Get Current Vehicle Data
// -----------------------------

async function getCurrentVehicleData() {

    if (selectedVehicleData) {
        return selectedVehicleData;
    }

    const params =
        new URLSearchParams(
            window.location.search
        );

    const vehicleId =
        params.get("id");

    if (!vehicleId) {
        return null;
    }

    try {

        const response = await authenticatedFetch(
            `${API_URL}/vehicles/${vehicleId}`
        );

        if (!response.ok) {
            throw new Error(
                `Vehicle request failed: ${response.status}`
            );
        }

        const data =
            await response.json();

        if (data.error) {
            return null;
        }

        selectedVehicleData = data;

        return data;

    } catch (error) {

        console.error(
            "Error loading current vehicle:",
            error
        );

        return null;
    }
}

// -----------------------------
// Add the AI function 
// -----------------------------
async function runAIAnalysis() {

    const resultBox =
        document.getElementById("aiResult");

    const button =
        document.getElementById("analyzeButton");


    // If result is already visible, hide it

    if (resultBox.style.display === "block") {

        resultBox.style.display = "none";

        button.textContent =
            "Run AI Analysis";

        return;
    }


    const vehicleData =
        await getCurrentVehicleData();

    if (!vehicleData) {

        resultBox.textContent =
            "Vehicle data is not available.";

        resultBox.style.display = "block";

        return;
    }


    resultBox.innerHTML =
        "<p>Analyzing vehicle...</p>";

    resultBox.style.display = "block";


    const vehicleId =
        vehicleData.vehicle_id;


    try {

        const historyResponse = await authenticatedFetch(
            `${API_URL}/vehicles/${vehicleId}/history`
        );

        if (!historyResponse.ok) {
            throw new Error(
                `History request failed: ${historyResponse.status}`
            );
        }

        const historyData =
            await historyResponse.json();


        if (
            !historyData.records ||
            historyData.records.length === 0
        ) {

            throw new Error(
                "No telemetry records available."
            );

        }


        const latestRecord =
            historyData.records[
                historyData.records.length - 1
            ];


        const input = {

            vehicle_id:
                vehicleId,

            battery_voltage:
                latestRecord.battery_voltage,

            battery_current:
                latestRecord.battery_current,

            battery_temperature:
                latestRecord.battery_temperature,

            soc:
                latestRecord.soc,

            motor_temperature:
                latestRecord.motor_temperature,

            vehicle_speed:
                latestRecord.vehicle_speed,

            odometer:
                latestRecord.odometer,

            charging_cycles:
                latestRecord.charging_cycles,

            charging_power:
                latestRecord.charging_power,

            ambient_temperature:
                latestRecord.ambient_temperature

        };


                    const response = await 
                        authenticatedFetch(
                        `${API_URL}/predict`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(input)
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `AI request failed: ${response.status} ${errorText}`
            );

        }


        const result =
            await response.json();


        resultBox.innerHTML = `

            <p>
                Prediction:
                <strong>
                    ${result.fault_prediction}
                </strong>
            </p>

            <p>
                Fault Probability:
                <strong>
                    ${result.fault_probability}%
                </strong>
            </p>

            <p>
                Battery Health:
                <strong>
                    ${result.battery_health}%
                </strong>
            </p>

            <p>
                Maintenance Risk:
                <strong>
                    ${result.maintenance_risk}
                </strong>
            </p>

            <p>
                Recommendation:
                ${result.recommendation}
            </p>

        `;


        // Change button to Hide

        button.textContent =
            "Hide AI Analysis";


    } catch (error) {

        console.error(
            "AI analysis error:",
            error
        );

        resultBox.textContent =
            "Unable to run AI analysis.";

    }
}
// -----------------------------
// Load Fleet Risk Overview
// -----------------------------

async function loadFleetRisk() {

    try {

        const response = await authenticatedFetch(
            `${API_URL}/fleet/risk`
        );

        const data = await response.json();

        // Risk counts
        document.getElementById(
            "highRiskVehicles"
        ).textContent = data.high_risk;

        const highRisk =
            document.getElementById("highRisk");

        if (highRisk) {
            highRisk.textContent =
                data.high_risk;
        }

        document.getElementById(
            "mediumRiskVehicles"
        ).textContent = data.medium_risk;

        document.getElementById(
            "lowRiskVehicles"
        ).textContent = data.low_risk;


        // Vehicles requiring attention
        const attentionList =
            document.getElementById("attentionList");

        attentionList.innerHTML = "";


       data.vehicles_requiring_attention
                .slice(0, 6)
                .forEach(
                    vehicle => {

                const div =
                    document.createElement("div");

                div.className = "attention-item";


                div.innerHTML = `
    <strong>
        ${vehicle.vehicle_id}
    </strong>

    <span class="risk-status">
        ${vehicle.risk}
    </span>

    <span>
        Score: ${vehicle.maintenance_score}/100
    </span>

    <span>
        Health: ${vehicle.battery_health}%
    </span>

    <span>
        Cycles: ${vehicle.charging_cycles}
    </span>

    <div class="reasons-container">

        <button
            class="view-reasons"
            type="button">
            View Reasons
        </button>

        <div
            class="reason-details"
            style="display: none;">

            ${vehicle.reasons
                .map(reason => `<div>• ${reason}</div>`)
                .join("")}

        </div>

    </div>

    <button
        class="view-vehicle"
        type="button">
        View Vehicle
    </button>
`;


                // -----------------------------
                // View Reasons
                // -----------------------------

                const reasonButton =
                    div.querySelector(".view-reasons");

                const reasonDetails =
                    div.querySelector(".reason-details");


                    reasonButton.addEventListener(
                        "click",
                        () => {

                            const isOpen =
                                reasonDetails.style.display === "block";

                            // Close all other open reason panels
                            document
                                .querySelectorAll(
                                    "#attentionList .reason-details"
                                )
                                .forEach(details => {
                                    details.style.display = "none";
                                });

                            document
                                .querySelectorAll(
                                    "#attentionList .view-reasons"
                                )
                                .forEach(button => {
                                    button.textContent = "View Reasons";
                                });

                            // Open selected panel
                            if (!isOpen) {

                                reasonDetails.style.display =
                                    "block";

                                reasonButton.textContent =
                                    "Hide Reasons";

                            }

                        }
                    );


                // -----------------------------
                // View Vehicle
                // -----------------------------

                const vehicleButton =
                    div.querySelector(".view-vehicle");


                 vehicleButton.addEventListener(
                        "click",
                        () => {

                            window.location.href =
                                `vehicle-details.html?id=${vehicle.vehicle_id}`;

                        }
                    );

                attentionList.appendChild(div);

            }
        );

    } catch (error) {

        console.error(
            "Error loading fleet risk:",
            error
        );

    }
}


function getChartThemeColors() {

    const isLight =
        document.documentElement
            .getAttribute("data-theme") === "light";

    return {
        text: isLight
            ? "#334155"
            : "#94a3b8",

        label: isLight
            ? "#1e293b"
            : "#cbd5e1",

        grid: isLight
            ? "rgba(100, 116, 139, 0.20)"
            : "#172233",

        tooltipBackground: isLight
            ? "#ffffff"
            : "#0b101b",

        tooltipText: isLight
            ? "#0f172a"
            : "#cbd5e1",

        tooltipBorder: isLight
            ? "#cbd5e1"
            : "#1e293b"
    };
}

// -----------------------------
// Load Fleet Analytics
// -----------------------------

async function loadFleetAnalytics() {

    const chartTheme = 
        getChartThemeColors();

    try {

        const response = await authenticatedFetch(
            `${API_URL}/fleet/analytics`
        );

        if (!response.ok) {
            throw new Error(
                `Analytics API returned ${response.status}`
            );
        }

        const data = await response.json();

        // =====================================================
        // HEALTH CHART
        // =====================================================

        const healthCanvas =
            document.getElementById("healthChart");

        if (
            typeof Chart !== "undefined" &&
            healthCanvas
        ) {

            const existingHealthChart =
                Chart.getChart(healthCanvas);

            if (existingHealthChart) {
                existingHealthChart.destroy();
            }

        }


        // =====================================================
        // DATA
        // =====================================================

        const normal =
            data.fault_distribution.NORMAL || 0;

        const fault =
            data.fault_distribution.FAULT || 0;

        const normalRecords = normal;
        const faultRecords = fault;


        const totalFaultRecords =
            normal + fault;


        const faultRate =
            totalFaultRecords > 0
                ? fault / totalFaultRecords
                : 0;


        const faultPercentage =
            (faultRate * 100).toFixed(1);


        const normalPercentage =
            ((1 - faultRate) * 100).toFixed(1);


        // =====================================================
        // UPDATE FAULT GAUGE
        // =====================================================

        const gaugeLength = 346;


        const normalLength =
            gaugeLength * (1 - faultRate);


        const faultLength =
            gaugeLength * faultRate;


        const normalGauge =
            document.getElementById("normalGauge");


        const faultGauge =
            document.getElementById("faultGauge");


        normalGauge.setAttribute(
            "stroke-dasharray",
            `${normalLength} ${gaugeLength}`
        );


        normalGauge.setAttribute(
            "stroke-dashoffset",
            "0"
        );


        faultGauge.setAttribute(
            "stroke-dasharray",
            `${faultLength} ${gaugeLength}`
        );


        faultGauge.setAttribute(
            "stroke-dashoffset",
            `-${normalLength}`
        );


        // =====================================================
        // UPDATE NEEDLE
        // =====================================================

        const needleAngle =
            Math.PI +
            (Math.PI * (1 - faultRate));


        const needleLength = 96;


        const needleX =
            140 +
            Math.cos(needleAngle) *
            needleLength;


        const needleY =
            140 +
            Math.sin(needleAngle) *
            needleLength;


        const needle =
            document.getElementById("faultNeedle");


        needle.setAttribute(
            "x2",
            needleX
        );


        needle.setAttribute(
            "y2",
            needleY
        );


        // =====================================================
        // UPDATE TEXT
        // =====================================================

        document.getElementById(
            "faultRateValue"
        ).textContent =
            `${faultPercentage}%`;


        document.getElementById(
            "normalStatusValue"
        ).textContent =
            `NORMAL STATUS: ${normalPercentage}%`;


        document.getElementById(
            "normalLegend"
        ).textContent =
            `NORMAL (${normalPercentage}%)`;


        document.getElementById(
            "faultLegend"
        ).textContent =
            `FAULT (${faultPercentage}%)`;


        // =====================================================
        // FAULT GAUGE TOOLTIP
        // =====================================================

        const faultTooltip =
            document.getElementById(
                "faultGaugeTooltip"
            );


        const faultTooltipTitle =
            document.getElementById(
                "faultTooltipTitle"
            );


        const faultTooltipRecords =
            document.getElementById(
                "faultTooltipRecords"
            );


        const faultTooltipPercentage =
            document.getElementById(
                "faultTooltipPercentage"
            );


        function showFaultTooltip(
            type,
            records,
            percentage,
            event
        ) {

            faultTooltipTitle.textContent =
                type;


            faultTooltipRecords.textContent =
                `${records.toLocaleString()} records`;


            faultTooltipPercentage.textContent =
                `${percentage}%`;


            const card =
                faultTooltip.closest(
                    ".chart-card"
                );


            const cardRect =
                card.getBoundingClientRect();


            const tooltipX =
                event.clientX -
                cardRect.left +
                12;


            const tooltipY =
                event.clientY -
                cardRect.top +
                12;


            faultTooltip.style.left =
                `${tooltipX}px`;


            faultTooltip.style.top =
                `${tooltipY}px`;


            faultTooltip.classList.add(
                "visible"
            );

        }


        function hideFaultTooltip() {

            faultTooltip.classList.remove(
                "visible"
            );

        }


        normalGauge.addEventListener(
            "mousemove",
            (event) => {

                showFaultTooltip(
                    "NORMAL",
                    normalRecords,
                    normalPercentage,
                    event
                );

            }
        );


        normalGauge.addEventListener(
            "mouseleave",
            hideFaultTooltip
        );


        faultGauge.addEventListener(
            "mousemove",
            (event) => {

                showFaultTooltip(
                    "FAULT",
                    faultRecords,
                    faultPercentage,
                    event
                );

            }
        );


        faultGauge.addEventListener(
            "mouseleave",
            hideFaultTooltip
        );


        // =====================================================
        // BATTERY HEALTH VALUE PLUGIN
        // =====================================================

        const healthValuePlugin = {

            id: "healthValuePlugin",

            afterDatasetsDraw(chart) {

                const {
                    ctx
                } = chart;


                const meta =
                    chart.getDatasetMeta(0);


                ctx.save();


                ctx.fillStyle =
                    chartTheme.label;


                ctx.font =
                    "600 11px 'JetBrains Mono', monospace";


                ctx.textAlign =
                    "left";


                ctx.textBaseline =
                    "middle";


                meta.data.forEach(
                    (bar, index) => {

                        const value =
                            chart.data.datasets[0]
                                .data[index];


                        ctx.fillText(
                            value,
                            bar.x + 10,
                            bar.y
                        );

                    }
                );


                ctx.restore();

            }

        };


        // =====================================================
        // BATTERY HEALTH CHART
        // =====================================================

        const healthLabels =
            Object.keys(
                data.battery_health_distribution
            );


        const healthValues =
            Object.values(
                data.battery_health_distribution
            );


        new Chart(
            healthCanvas,
            {

                type: "bar",


                data: {

                    labels: healthLabels,


                    datasets: [{

                        label: "Vehicles",

                        data: healthValues,


                        backgroundColor:
                            function(context) {

                                const chart =
                                    context.chart;


                                const {
                                    ctx,
                                    chartArea
                                } = chart;


                                if (!chartArea) {
                                    return "#38a3f8";
                                }


                                const gradient =
                                    ctx.createLinearGradient(
                                        chartArea.left,
                                        0,
                                        chartArea.right,
                                        0
                                    );


                                gradient.addColorStop(
                                    0,
                                    "#1e5f8a"
                                );


                                gradient.addColorStop(
                                    1,
                                    "#38a3f8"
                                );


                                return gradient;

                            },


                        borderWidth: 0,

                        borderRadius: 4,

                        barThickness: 22,

                        maxBarThickness: 22

                    }]

                },


                plugins: [
                    healthValuePlugin
                ],


                options: {

                    indexAxis: "y",

                    responsive: true,

                    maintainAspectRatio: false,


                    layout: {

                        padding: {
                            right: 35,
                            left: 5
                        }

                    },


                    scales: {

                        x: {

                            beginAtZero: true,

                            max: 60,

                            grid: {

                                color:
                                    chartTheme.grid,

                                borderDash: [
                                    3,
                                    3
                                ],

                                drawBorder: false
                            },

                            ticks: {

                                stepSize: 20,

                                color:
                                    chartTheme.text,

                                font: {

                                    family:
                                        "'JetBrains Mono', monospace",

                                    size: 10
                                }
                            },

                            border: {
                                display: false
                            }
                        },


                        y: {

                            grid: {
                                display: false
                            },

                            ticks: {

                                color:
                                    chartTheme.label,

                                font: {

                                    family:
                                        "'JetBrains Mono', monospace",

                                    size: 11
                                },

                                padding: 8
                            },

                            border: {
                                display: false
                            }
                        }
                    },


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {

                            backgroundColor:
                                chartTheme.tooltipBackground,

                            borderColor:
                                chartTheme.tooltipBorder,

                            borderWidth: 1,

                            titleColor:
                                chartTheme.label,

                            bodyColor:
                                chartTheme.tooltipText,

                            padding: 12

                        }

                    }

                }

            }

        );


        // =====================================================
        // TEMPERATURE
        // =====================================================

        document.getElementById(
            "avgBatteryTemp"
        ).textContent =
            `${data.temperature.average_battery_temperature} °C`;


        document.getElementById(
            "maxBatteryTemp"
        ).textContent =
            `${data.temperature.maximum_battery_temperature} °C`;


        document.getElementById(
            "avgMotorTemp"
        ).textContent =
            `${data.temperature.average_motor_temperature} °C`;


        document.getElementById(
            "maxMotorTemp"
        ).textContent =
            `${data.temperature.maximum_motor_temperature} °C`;


    } catch (error) {

        console.error(
            "Error loading fleet analytics:",
            error
        );

    }

}

async function loadVehicleHistory(vehicleId) {

    try {

        const response = await authenticatedFetch(
            `${API_URL}/vehicles/${vehicleId}/history`
        );

        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const records = data.records;

        const timestamps = records.map(
            record => record.timestamp
        );

        const batteryTemperatures = records.map(
            record => record.battery_temperature
        );

        const motorTemperatures = records.map(
            record => record.motor_temperature
        );

        const socValues = records.map(
            record => record.soc
        );

        const voltageValues = records.map(
            record => record.battery_voltage
        );


        // -----------------------------
        // Temperature Chart
        // -----------------------------

        new Chart(
            document.getElementById("temperatureChart"),
            {
                type: "line",

                data: {
                    labels: timestamps,

                    datasets: [
                        {
                            label: "Battery Temperature (°C)",
                            data: batteryTemperatures,
                            tension: 0.3
                        },

                        {
                            label: "Motor Temperature (°C)",
                            data: motorTemperatures,
                            tension: 0.3
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        title: {
                            display: true,
                            text: "Temperature Over Time"
                        }
                    }
                }
            }
        );


        // -----------------------------
        // SOC Chart
        // -----------------------------

        new Chart(
            document.getElementById("socChart"),
            {
                type: "line",

                data: {
                    labels: timestamps,

                    datasets: [
                        {
                            label: "State of Charge (%)",
                            data: socValues,
                            tension: 0.3
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    scales: {
                        y: {
                            min: 0,
                            max: 100
                        }
                    },

                    plugins: {
                        title: {
                            display: true,
                            text: "Battery SOC Over Time"
                        }
                    }
                }
            }
        );


        // -----------------------------
        // Voltage Chart
        // -----------------------------

        new Chart(
            document.getElementById("voltageChart"),
            {
                type: "line",

                data: {
                    labels: timestamps,

                    datasets: [
                        {
                            label: "Battery Voltage (V)",
                            data: voltageValues,
                            tension: 0.3
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        title: {
                            display: true,
                            text: "Battery Voltage Over Time"
                        }
                    }
                }
            }
        );

    } catch (error) {

        console.error(
            "Error loading vehicle history:",
            error
        );

    }
}

// -----------------------------
// Check Vehicle Anomalies
// -----------------------------

async function checkAnomalies() {

    const resultBox =
        document.getElementById(
            "anomalyResult"
        );

    const button =
        document.getElementById(
            "anomalyButton"
        );


    /* Toggle result visibility */

    if (resultBox.style.display === "block") {

        resultBox.style.display = "none";

        button.textContent =
            "Check Anomalies";

        return;
    }


    const vehicleData =
        await getCurrentVehicleData();

    if (!vehicleData) {

        resultBox.textContent =
            "Vehicle data is not available.";

        resultBox.style.display =
            "block";

        return;
    }


    const vehicleId =
        vehicleData.vehicle_id;


    resultBox.style.display =
        "block";

    resultBox.innerHTML =
        "<p>Analyzing vehicle behavior...</p>";


    try {

        const response = await authenticatedFetch(
            `${API_URL}/vehicles/${vehicleId}/anomalies`
        );


        if (!response.ok) {

            throw new Error(
                `Anomaly request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        if (data.error) {

            resultBox.textContent =
                data.error;

            return;
        }


        if (data.anomaly_count === 0) {

            resultBox.innerHTML = `

                <p>
                    No unusual behavior detected.
                </p>

                <p>
                    Analyzed
                    ${data.total_records}
                    telemetry records.
                </p>

            `;

            button.textContent =
                "Hide Anomalies";

            return;
        }


   let summaryHTML = "";

if (
    data.anomaly_summary &&
    Object.keys(data.anomaly_summary).length > 0
) {

    summaryHTML = `

        <div class="anomaly-summary">

            <strong>
                Anomaly Summary
            </strong>

            <p>
                Anomaly Rate:
                ${data.anomaly_rate}%
            </p>

    `;


    Object.entries(
        data.anomaly_summary
    ).forEach(
        ([reason, count]) => {

            summaryHTML += `

                <div class="anomaly-summary-item">

                    <span>
                        ${reason}
                    </span>

                    <strong>
                        ${count}
                    </strong>

                </div>

            `;
        }
    );


    summaryHTML += `
        </div>
    `;
}


let html = `

    <p>

        <strong>
            ${data.anomaly_count}
            anomalies detected
        </strong>

    </p>

    <p>
        Analyzed
        ${data.total_records}
        telemetry records.
    </p>

    ${summaryHTML}

`;


        data.anomalies.forEach(
            anomaly => {

                html += `

                    <div class="anomaly-item">

                        <strong>
                            ${anomaly.timestamp}
                        </strong>

                        <div>
                            Battery Temperature:
                            ${anomaly.battery_temperature}
                            °C
                        </div>

                        <div>
                            Motor Temperature:
                            ${anomaly.motor_temperature}
                            °C
                        </div>

                        <div>
                            Battery Voltage:
                            ${anomaly.battery_voltage}
                            V
                        </div>

                        <div>
                            SOC:
                            ${anomaly.soc}%
                        </div>

                        ${
                            anomaly.reasons
                                .map(
                                    reason => `
                                        <div class="anomaly-reason">
                                            ${reason}
                                        </div>
                                    `
                                )
                                .join("")
                        }

                    </div>

                `;
            }
        );


        resultBox.innerHTML =
            html;


        button.textContent =
            "Hide Anomalies";


    } catch (error) {

        console.error(
            "Anomaly detection error:",
            error
        );

        resultBox.textContent =
            "Unable to detect anomalies.";
    }
}
// -----------------------------
// Predictive Maintenance
// -----------------------------

async function calculateMaintenanceRisk() {

    const resultBox =
        document.getElementById(
            "maintenanceResult"
        );

    const button =
        document.getElementById(
            "maintenanceButton"
        );


    /* Toggle result visibility */

    if (resultBox.style.display === "block") {

        resultBox.style.display =
            "none";

        button.textContent =
            "Calculate Maintenance Risk";

        return;
    }


    const vehicleData =
        await getCurrentVehicleData();

    if (!vehicleData) {

        resultBox.textContent =
            "Vehicle data is not available.";

        resultBox.style.display =
            "block";

        return;
    }


    const vehicleId =
        vehicleData.vehicle_id;


    resultBox.style.display =
        "block";

    resultBox.innerHTML =
        "<p>Calculating maintenance risk...</p>";


    try {

        const response = await authenticatedFetch(
            `${API_URL}/vehicles/${vehicleId}/maintenance`
        );

        if (!response.ok) {

            throw new Error(
                `Maintenance request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        if (data.error) {

            resultBox.textContent =
                data.error;

            return;
        }


        let reasonsHTML = "";


        if (
            !data.reasons ||
            data.reasons.length === 0
        ) {

            reasonsHTML =
                "<p>No major risk factors detected.</p>";

        } else {

            data.reasons.forEach(
                reason => {

                    reasonsHTML += `

                        <p class="maintenance-reason">
                            ${reason}
                        </p>

                    `;

                }
            );
        }


        resultBox.innerHTML = `

            <p>
                Maintenance Risk:
                <strong>
                    ${data.risk_level}
                </strong>
            </p>

            <div class="maintenance-score">
                ${data.predictive_maintenance_score}/100
            </div>

            <p>
                Battery Health:
                ${data.battery_health}%
            </p>

            <div>
                ${reasonsHTML}
            </div>

            <div class="maintenance-recommendation">
                ${data.recommendation}
            </div>

        `;


        button.textContent =
            "Hide Maintenance Risk";


    } catch (error) {

        console.error(
            "Maintenance analysis error:",
            error
        );

        resultBox.textContent =
            "Unable to calculate maintenance risk.";
    }
}
// -----------------------------
// Load Maintenance Page
// -----------------------------

async function loadMaintenancePage() {

    try {

        const response = await authenticatedFetch(
            `${API_URL}/fleet/risk`
        );

        const data = await response.json();


        // Risk counts

        const highRisk =
            document.getElementById("maintenanceHighRisk");

        if (highRisk) {
            highRisk.textContent =
                data.high_risk;
        }


        const mediumRisk =
            document.getElementById("maintenanceMediumRisk");

        if (mediumRisk) {
            mediumRisk.textContent =
                data.medium_risk;
        }


        const lowRisk =
            document.getElementById("maintenanceLowRisk");

        if (lowRisk) {
            lowRisk.textContent =
                data.low_risk;
        }


        // Vehicle list

        const vehicleList =
            document.getElementById(
                "maintenanceVehicleList"
            );

        if (!vehicleList) {
            return;
        }


        vehicleList.innerHTML = "";


             data.vehicles_requiring_attention
                .slice(0, 6)
                .forEach(
                    vehicle => {

                const div =
                    document.createElement("div");

                div.className =
                    "maintenance-vehicle-item";

          div.innerHTML = `

            <div class="maintenance-vehicle-info">

                <strong>
                    ${vehicle.vehicle_id}
                </strong>

                <span class="risk-status">
                    ${vehicle.risk}
                </span>

            </div>


            <div class="maintenance-score">

                <span>
                    Score
                </span>

                <strong>
                    ${vehicle.maintenance_score}
                </strong>

            </div>


            <div class="maintenance-health">

                <span>
                    Health
                </span>

                <strong>
                    ${vehicle.battery_health}%
                </strong>

            </div>


            <div class="maintenance-fault">

                <span>
                    AI Fault
                </span>

                <strong>
                    ${vehicle.fault_probability}%
                </strong>

            </div>


            <div class="maintenance-anomalies">

                <span>
                    Anomalies
                </span>

                <strong>
                    ${vehicle.anomaly_count}
                </strong>

            </div>


            <div class="maintenance-actions">

                <button
                    class="maintenance-reasons-button"
                    type="button">
                    View Reasons
                </button>

                <button
                    class="vehicle-action"
                    type="button">
                    View
                </button>

            </div>


            <div class="maintenance-reasons">

                <strong>
                    Risk Factors
                </strong>

                <div class="maintenance-reasons-list"></div>

                <div class="maintenance-recommendation">
                    ${vehicle.recommendation}
                </div>

            </div>

        `;


                const viewButton =
                    div.querySelector(
                        ".vehicle-action"
                    );
                    const reasonsButton =
    div.querySelector(
        ".maintenance-reasons-button"
    );

const reasonsBox =
    div.querySelector(
        ".maintenance-reasons"
    );

const reasonsList =
    div.querySelector(
        ".maintenance-reasons-list"
    );


vehicle.reasons.forEach(
    reason => {

        const reasonItem =
            document.createElement("p");

        reasonItem.textContent =
            reason;

        reasonsList.appendChild(
            reasonItem
        );

    }
);


reasonsButton.addEventListener(
    "click",
    () => {

        const isVisible =
            reasonsBox.style.display === "block";

        reasonsBox.style.display =
            isVisible ? "none" : "block";

        reasonsButton.textContent =
            isVisible
                ? "View Reasons"
                : "Hide Reasons";

    }
);


                viewButton.addEventListener(
                    "click",
                    () => {

                        openVehicleDetails(
                            vehicle.vehicle_id
                        );

                    }
                );


                vehicleList.appendChild(div);

            }
        );


    } catch (error) {

        console.error(
            "Error loading maintenance page:",
            error
        );

    }

}

// -----------------------------
// Load Attention Page
// -----------------------------

async function loadAttentionPage() {

    try {

        const response = await authenticatedFetch(
            `${API_URL}/fleet/risk`
        );

        const data = await response.json();

        const vehicleList =
            document.getElementById(
                "attentionVehicleList"
            );

        if (!vehicleList) {
            return;
        }

        vehicleList.innerHTML = "";


        data.vehicles_requiring_attention.forEach(
            vehicle => {

                const div =
                    document.createElement("div");

                div.className =
                    "attention-page-item";


                div.innerHTML = `

                    <div class="attention-vehicle-main">

                        <strong>
                            ${vehicle.vehicle_id}
                        </strong>

                        <span class="attention-risk ${vehicle.risk.toLowerCase()}">
                            ${vehicle.risk}
                        </span>

                    </div>


                    <div class="attention-vehicle-metrics">

                        <span>
                            Score
                            <strong>
                                ${vehicle.maintenance_score}/100
                            </strong>
                        </span>

                        <span>
                            Battery Health
                            <strong>
                                ${vehicle.battery_health}%
                            </strong>
                        </span>

                        <span>
                            AI Fault
                            <strong>
                                ${vehicle.fault_probability}%
                            </strong>
                        </span>

                        <span>
                            Anomalies
                            <strong>
                                ${vehicle.anomaly_count}
                            </strong>
                        </span>

                        <span>
                            Battery Temp
                            <strong>
                                ${vehicle.battery_temperature} °C
                            </strong>
                        </span>

                        <span>
                            Motor Temp
                            <strong>
                                ${vehicle.motor_temperature} °C
                            </strong>
                        </span>

                        <span>
                            Cycles
                            <strong>
                                ${vehicle.charging_cycles}
                            </strong>
                        </span>

                    </div>


                    <div class="attention-reasons">

                            <button
                                class="view-reasons"
                                type="button">

                                View Reasons

                            </button>

                            <div class="reason-details">

                                ${vehicle.reasons
                                    .map(
                                        reason =>
                                            `<div>${reason}</div>`
                                    )
                                    .join("")}

                            </div>
                            <div class="attention-recommendation">

                                <strong>
                                    Recommendation
                                </strong>

                                <p>
                                    ${vehicle.recommendation}
                                </p>

                            </div>

                    </div>

                    <button
                        class="vehicle-action"
                        type="button">

                        View Vehicle

                    </button>

                `;


                const viewButton =
                    div.querySelector(
                        ".vehicle-action"
                    );

                const reasonsButton =
                div.querySelector(
                    ".view-reasons"
                );

                const reasonDetails =
                    div.querySelector(
                        ".reason-details"
                    );

                reasonsButton.addEventListener(
                    "click",
                    () => {
                        const isVisible =
                        reasonDetails.classList.toggle(
                            "show"
                        );
                        reasonsButton.textContent = isVisible
                            ? "Hide Reasons"
                            : "View Reasons";   

                    }
                );


                viewButton.addEventListener(
                    "click",
                    () => {

                        openVehicleDetails(
                            vehicle.vehicle_id
                        );

                    }
                );


                vehicleList.appendChild(div);

            }
        );


    } catch (error) {

        console.error(
            "Error loading attention page:",
            error
        );

    }

}

// -----------------------------
// Global Vehicle Search
// -----------------------------

function setupGlobalSearch() {

    const searchInput =
        document.getElementById(
            "globalSearch"
        );

    if (!searchInput) {
        return;
    }


    searchInput.addEventListener(
        "keydown",
        async (event) => {

            if (event.key !== "Enter") {
                return;
            }


            const query =
                searchInput.value
                    .trim()
                    .toUpperCase();


            if (!query) {
                return;
            }


            try {

                const response =
                    await authenticatedFetch(
                        `${API_URL}/vehicles`
                    );

                const data =
                    await response.json();


                const vehicle =
                    data.vehicles.find(
                        id =>
                            id.toUpperCase()
                                === query
                    );


                if (vehicle) {

                    openVehicleDetails(
                        vehicle
                    );

                } else {

                    alert(
                        "Vehicle not found."
                    );

                }

            } catch (error) {

                console.error(
                    "Search error:",
                    error
                );

            }

        }
    );

}

// -----------------------------
// Load Selected Vehicle Page
// -----------------------------

function loadSelectedVehiclePage() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    const vehicleId =
        params.get("id");

    if (!vehicleId) {
        return;
    }

    const vehicleTitle =
        document.getElementById(
            "selectedVehicle"
        );

    if (vehicleTitle) {

        vehicleTitle.textContent =
            `${vehicleId} — Vehicle Details`;

    }

    loadVehicleDetails(vehicleId);
}

// -----------------------------
// Active Navigation Link
// -----------------------------

const currentPage =
    window.location.pathname.split("/").pop() || "index.html";

document
    .querySelectorAll(".nav-link")
    .forEach(link => {

        const linkPage =
            link.getAttribute("href");

        if (linkPage === currentPage) {
            link.classList.add("active");
        }

    });

// -----------------------------
// Page Initialization
// -----------------------------

if (
    document.getElementById("totalVehicles") ||
    document.getElementById("analyticsFaultRecords")
) {
    loadFleetSummary();
}


if (
    document.getElementById("vehicleList")
) {
    loadVehicles();
}


if (
    document.getElementById("highRiskVehicles")
) {
    loadFleetRisk();
}

if (
    document.getElementById("faultGauge") &&
    document.getElementById("healthChart")
) {
    loadFleetAnalytics();
}

if (
    document.getElementById("attentionVehicleList")
) {
    loadAttentionPage();
}


if (
    document.getElementById("maintenanceVehicleList")
) {
    loadMaintenancePage();
}


if (
    window.location.pathname.endsWith(
        "vehicle-details.html"
    )
) {
    loadSelectedVehiclePage();
}


setupGlobalSearch();


const analyzeButton =
    document.getElementById(
        "analyzeButton"
    );

if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        runAIAnalysis
    );

}


const anomalyButton =
    document.getElementById(
        "anomalyButton"
    );

if (anomalyButton) {

    anomalyButton.addEventListener(
        "click",
        checkAnomalies
    );

}


const maintenanceButton =
    document.getElementById(
        "maintenanceButton"
    );

if (maintenanceButton) {

    maintenanceButton.addEventListener(
        "click",
        calculateMaintenanceRisk
    );

}

// =========================================
// ANALYSIS SECTION HIDE / SHOW
// =========================================

document
    .querySelectorAll(".analysis-hide-button")
    .forEach(button => {

        button.addEventListener("click", () => {

            const targetId =
                button.dataset.target;

            const target =
                document.getElementById(targetId);

            if (!target) {
                return;
            }

            if (target.style.display === "none") {

                target.style.display = "block";
                button.textContent = "Hide";

            } else {

                target.style.display = "none";
                button.textContent = "Show";

            }

        });

    });

    // =========================================
    // FOR LOGIN PAGE 
    // =========================================

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {

        loginForm.addEventListener("submit", async (event) => {

            event.preventDefault();

            const username =
                document.getElementById("username").value;

            const password =
                document.getElementById("password").value;

            const loginError =
                document.getElementById("loginError");

            try {

                const formData = new URLSearchParams();

                formData.append("username", username);
                formData.append("password", password);

                const response = await fetch(
                    `${API_URL}/auth/login`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },
                        body: formData
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail ||
                        "Login failed"
                    );
                }

                sessionStorage.setItem(
                    "access_token",
                    data.access_token
                );

                window.location.href =
                    "index.html";

            } catch (error) {

                loginError.textContent =
                    error.message;

            }

        });

    }
    
    const togglePassword =
    document.getElementById("togglePassword");

    const passwordInput =
        document.getElementById("password");

    if (togglePassword && passwordInput) {

        togglePassword.addEventListener(
            "click",
            () => {

                const isPassword =
                    passwordInput.type === "password";

                passwordInput.type =
                    isPassword
                        ? "text"
                        : "password";

                togglePassword.textContent =
                    isPassword
                        ? "Hide"
                        : "Show";

                togglePassword.setAttribute(
                    "aria-label",
                    isPassword
                        ? "Hide password"
                        : "Show password"
                );
            }
        );
    }

    // =========================================
    // FOR LOGIN PAGE 
    // =========================================

    const logoutButton =
    document.getElementById("logoutButton");

    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            () => {

                sessionStorage.removeItem(
                    "access_token"
                );

                window.location.href =
                    "login.html";
            }
        );
    }

function requireAuthentication() {

    const token =
        sessionStorage.getItem("access_token");

    const isLoginPage =
        window.location.pathname.endsWith(
            "login.html"
        );

    if (!token && !isLoginPage) {
        window.location.href =
            "login.html";
    }
}

requireAuthentication();

async function authenticatedFetch(
    url,
    options = {}
) {
    const token =
        sessionStorage.getItem("access_token");

    if (!token) {
        window.location.replace("login.html");
        return null;
    }

    const headers = new Headers(
        options.headers || {}
    );

    headers.set(
        "Authorization",
        `Bearer ${token}`
    );

    const response = await fetch(
        url,
        {
            ...options,
            headers: headers
        }
    );

    if (response.status === 401) {

        sessionStorage.removeItem(
            "access_token"
        );

        window.location.replace("login.html");

        return null;
    }

    return response;
}


// -----------------------------
// Protect Browser Back / Forward
// -----------------------------

window.addEventListener(
    "pageshow",
    function () {

        const token =
            sessionStorage.getItem("access_token");

        const isLoginPage =
            window.location.pathname.endsWith(
                "login.html"
            );

        // Already logged in → don't allow login page
        if (token && isLoginPage) {
            window.location.replace("index.html");
            return;
        }

        // Logged out → don't allow protected pages
        if (!token && !isLoginPage) {
            window.location.replace("login.html");
        }

    }
);