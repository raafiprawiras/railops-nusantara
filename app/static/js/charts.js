"use strict";
document.addEventListener("DOMContentLoaded", function () {
    if (typeof dashboardData === "undefined") return;
    Chart.defaults.font.family = "'Poppins', sans-serif";
    Chart.defaults.font.size = 12;

    var dCtx = document.getElementById("chartDoughnut");
    if (dCtx) {
        new Chart(dCtx, {
            type: "doughnut",
            data: {
                labels: ["Tepat Waktu", "Terlambat", "Dibatalkan"],
                datasets: [{
                    data: [dashboardData.tepat_waktu, dashboardData.terlambat, dashboardData.dibatalkan],
                    backgroundColor: ["#16A34A", "#F59E0B", "#DC2626"],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: "70%",
                plugins: { legend: { position: "bottom", labels: { padding: 16, usePointStyle: true } } } }
        });
    }

    var lCtx = document.getElementById("chartLine");
    if (lCtx) {
        new Chart(lCtx, {
            type: "line",
            data: {
                labels: dashboardData.delay_labels,
                datasets: [{
                    label: "Keterlambatan (menit)",
                    data: dashboardData.delay_values,
                    borderColor: "#005BAC", backgroundColor: "rgba(0,91,172,0.08)",
                    fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: "#005BAC"
                }]
            },
            options: { responsive: true, maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { display: false } } }
        });
    }
});
