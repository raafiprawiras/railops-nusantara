"use strict";
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("roSidebarToggle");
    const sidebar = document.getElementById("roSidebar");
    const overlay = document.getElementById("roOverlay");

    if (toggle && sidebar) {
        toggle.addEventListener("click", function () {
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

    // Active nav state
    const path = window.location.pathname;
    document.querySelectorAll(".ro-sidebar-link").forEach(function (link) {
        const href = link.getAttribute("href");
        if (href && href !== "#" && path.startsWith(href)) {
            link.classList.add("active");
        }
    });
});
