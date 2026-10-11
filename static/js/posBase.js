document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       Elements
    ====================================================== */

    const sidebar = document.querySelector(".pos-sidebar");
    const sidebarOpen = document.getElementById("sidebarOpen");
    const sidebarClose = document.getElementById("sidebarClose");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    const navSections = document.querySelectorAll(".pos-nav-section");


    /* =====================================================
       Sidebar
    ====================================================== */

    function openSidebar() {
        if (!sidebar) return;

        sidebar.classList.add("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.add("active");
        }

        document.body.classList.add("sidebar-open");
    }


    function closeSidebar() {
        if (!sidebar) return;

        sidebar.classList.remove("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("active");
        }

        document.body.classList.remove("sidebar-open");
    }


    /* Desktop: fully collapse/expand the sidebar (no overlay) */

    function collapseSidebarDesktop() {
        if (!sidebar) return;

        sidebar.classList.add("pos-collapsed");
        document.body.classList.add("pos-sidebar-collapsed");
    }


    function expandSidebarDesktop() {
        if (!sidebar) return;

        sidebar.classList.remove("pos-collapsed");
        document.body.classList.remove("pos-sidebar-collapsed");
    }


    if (sidebarOpen) {

        sidebarOpen.addEventListener("click", function () {

            if (window.innerWidth <= 768) {
                openSidebar();
            } else {
                expandSidebarDesktop();
            }

        });

    }


    if (sidebarOverlay) {

        sidebarOverlay.addEventListener("click", function () {
            closeSidebar();
        });

    }


    if (sidebarClose) {

        sidebarClose.addEventListener("click", function () {

            if (window.innerWidth <= 768) {
                closeSidebar();
            } else {
                collapseSidebarDesktop();
            }

        });

    }


    /* =====================================================
       Close sidebar when clicking a link on mobile
    ====================================================== */

    const sidebarLinks = document.querySelectorAll(
        ".pos-sidebar a"
    );


    sidebarLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            if (window.innerWidth <= 768) {
                closeSidebar();
            }

        });

    });


    /* =====================================================
       Sub Menus
    ====================================================== */

    navSections.forEach(function (section) {

        const title = section.querySelector(
            ".pos-nav-section-title"
        );

        if (!title) return;


        title.addEventListener("click", function () {

            section.classList.toggle("open");

        });

    });


    /* =====================================================
       Price Formatting (thousand separators)
    ====================================================== */

    const priceElements = document.querySelectorAll(".price-value");

    priceElements.forEach(function (el) {

        const raw = el.textContent.trim();
        const num = parseFloat(raw);

        if (!isNaN(num)) {
            el.textContent = num.toLocaleString("en-US");
        }

    });


    /* =====================================================
       Current Page
    ====================================================== */

    const currentPath = window.location.pathname;

    const navLinks = document.querySelectorAll(
        ".pos-sidebar a[href]"
    );


    navLinks.forEach(function (link) {

        const href = link.getAttribute("href");

        if (!href || href === "#") {
            return;
        }


        try {

            const linkUrl = new URL(
                href,
                window.location.origin
            );


            if (
                linkUrl.pathname === currentPath &&
                link.classList.contains("pos-nav-subitem")
            ) {

                link.classList.add("active");

                const parentSection =
                    link.closest(".pos-nav-section");

                if (parentSection) {
                    parentSection.classList.add("open");
                }

            }

        } catch (error) {
            console.warn(
                "Could not process navigation URL:",
                href
            );
        }

    });


    /* =====================================================
       Persian Date & Time
    ====================================================== */

    const dateElement =
        document.getElementById("pos-date");

    const timeElement =
        document.getElementById("pos-time");


    function updateDateTime() {

        const now = new Date();


        /* ---------------------------------------------
           Time
        --------------------------------------------- */

        if (timeElement) {

            const timeFormatter =
                new Intl.DateTimeFormat(
                    "fa-IR",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                        hour12: false
                    }
                );

            timeElement.textContent =
                timeFormatter.format(now);

        }


        /* ---------------------------------------------
           Date
        --------------------------------------------- */

        if (dateElement) {

            const dateFormatter =
                new Intl.DateTimeFormat(
                    "fa-IR",
                    {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric"
                    }
                );

            dateElement.textContent =
                dateFormatter.format(now);

        }

    }


    updateDateTime();


    /* Update every second */

    setInterval(
        updateDateTime,
        1000
    );


    /* =====================================================
       Close sidebar when resizing to desktop
    ====================================================== */

    window.addEventListener("resize", function () {

        if (window.innerWidth > 768) {
            closeSidebar();
        }

    });

});