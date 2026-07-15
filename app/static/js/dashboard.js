/**
 * RailOps Nusantara — Dashboard Charts (Chart.js)
 * Reads data from global `dashboardData` injected by the template.
 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    if (typeof dashboardData === "undefined") return;

    // --- Doughnut: Status Perjalanan ---
    const doughnutCtx = document.getElementById("chartStatusPerjalanan");
    if (doughnutCtx) {
        new Chart(doughnutCtx, {
            type: "doughnut",
            data: {
                labels: ["Tepat Waktu", "Terlambat", "Dibatalkan"],
                datasets: [{
                    data: [
                        dashboardData.tepat_waktu,
                        dashboardData.terlambat,
                        dashboardData.dibatalkan
                    ],
                    backgroundColor: ["#27AE60", "#F39C12", "#E74C3C"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { padding: 16, usePointStyle: true }
                    }
                },
                cutout: "65%"
            }
        });
    }

    // --- Line: Keterlambatan Harian ---
    const lineCtx = document.getElementById("chartKeterlambatan");
    if (lineCtx) {
        new Chart(lineCtx, {
            type: "line",
            data: {
                labels: dashboardData.delay_labels,
                datasets: [{
                    label: "Menit Keterlambatan",
                    data: dashboardData.delay_values,
                    borderColor: "#2E86DE",
                    backgroundColor: "rgba(46, 134, 222, 0.1)",
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: "#2E86DE",
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: "Menit" }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
});
