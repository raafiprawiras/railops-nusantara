/**
 * RailOps Nusantara — Main JavaScript
 * Sidebar toggle and active navigation state.
 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    // --- Sidebar Toggle (Mobile) ---
    const toggleBtn = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("show");
            if (overlay) overlay.classList.toggle("show");
        });
    }

    if (overlay) {
        overlay.addEventListener("click", function () {
            sidebar.classList.remove("show");
            overlay.classList.remove("show");
        });
    }

    // --- Active Navigation State ---
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".sidebar-link");

    navLinks.forEach(function (link) {
        const href = link.getAttribute("href");
        if (href && href !== "#" && currentPath.startsWith(href)) {
            link.classList.add("active");
        }
    });
});
