/* =========================================================
   ORDER APP - order_list
   تبدیل تاریخ به شمسی، فرمت مبلغ و فیلتر زنده‌ی لیست سفارش‌ها
   کتابخانه‌ی jalalidatepicker باید قبل از این فایل لود شود.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    // ==================================================
    // ۱) تبدیل تاریخ میلادی ردیف‌ها به شمسی (Intl داخلی مرورگر)
    // ==================================================

    var jalaliFmt = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    });

    var jalaliCache = {};

    function toJalali(iso) {
        if (jalaliCache[iso]) return jalaliCache[iso];

        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
        if (!m) return null;

        // ظهر می‌گذاریم تا جابه‌جایی منطقه زمانی روز را عوض نکند
        var d = new Date(+m[1], +m[2] - 1, +m[3], 12);
        var v = {};
        jalaliFmt.formatToParts(d).forEach(function (p) { v[p.type] = p.value; });

        return (jalaliCache[iso] = v.year + "/" + v.month + "/" + v.day);
    }

    document.querySelectorAll("time[data-jalali-date]").forEach(function (t) {
        var j = toJalali(t.getAttribute("datetime"));
        if (j) t.textContent = j;
    });


    // جداسازی سه‌رقمی مبلغ‌ها (مستقل از تنظیمات زبان جنگو)
    var moneyFmt = new Intl.NumberFormat("en-US");

    document.querySelectorAll("[data-money]").forEach(function (m) {
        var n = Number(m.getAttribute("data-money"));
        if (!isNaN(n)) m.textContent = moneyFmt.format(n);
    });


    // ==================================================
    // ۲) فیلتر و جستجوی لحظه‌ای
    // ==================================================

    var rows = Array.prototype.slice.call(document.querySelectorAll("tr[data-order-row]"));
    if (!rows.length) return;

    var el = {
        number:   document.getElementById("filter-number"),
        customer: document.getElementById("filter-customer"),
        dateFrom: document.getElementById("filter-date-from"),
        dateTo:   document.getElementById("filter-date-to"),
        timeFrom: document.getElementById("filter-time-from"),
        timeTo:   document.getElementById("filter-time-to"),
        count:    document.getElementById("filter-count"),
        reset:    document.getElementById("filter-reset"),
        empty:    document.getElementById("no-results"),
        table:    document.querySelector(".table-wrapper")
    };

    // ارقام فارسی/عربی → انگلیسی، و یکسان‌سازی ی/ک عربی
    function normalize(str) {
        return String(str || "")
            .replace(/[۰-۹]/g, function (c) { return c.charCodeAt(0) - 1776; })
            .replace(/[٠-٩]/g, function (c) { return c.charCodeAt(0) - 1632; })
            .replace(/ي/g, "ی")
            .replace(/ك/g, "ک")
            .replace(/\u200c/g, " ")
            .trim()
            .toLowerCase();
    }

    // اطلاعات هر ردیف یک بار خوانده می‌شود
    rows.forEach(function (row) {
        var t = row.querySelector("time[data-jalali-date]");
        row._hidden = false;
        row._f = {
            number:   normalize(row.dataset.number),
            customer: normalize(row.dataset.customer),
            date:     t ? normalize(t.textContent) : "",   // 1405/07/08
            time:     normalize(row.dataset.time)          // 14:35
        };
    });

    var fa = new Intl.NumberFormat("fa-IR");
    var lastKey = null;

    function applyFilters() {

        var number   = normalize(el.number.value).replace(/^#/, "");
        var customer = normalize(el.customer.value);
        var dateFrom = normalize(el.dateFrom.value);
        var dateTo   = normalize(el.dateTo.value);
        var timeFrom = normalize(el.timeFrom.value);
        var timeTo   = normalize(el.timeTo.value);

        // اگر هیچ فیلتری عوض نشده کاری نکن
        var key = [number, customer, dateFrom, dateTo, timeFrom, timeTo].join("|");
        if (key === lastKey) return;
        lastKey = key;

        var overnight = timeFrom && timeTo && timeFrom > timeTo;
        var visible = 0;

        // جدول را موقتاً از چیدمان خارج می‌کنیم تا مرورگر برای هر ردیف
        // دوباره محاسبه‌ی layout نکند (مهم‌ترین عامل کندی)
        el.table.style.display = "none";

        for (var k = 0; k < rows.length; k++) {
            var row = rows[k];
            var f = row._f;
            var ok = true;

            if (number && f.number.indexOf(number) === -1) ok = false;
            else if (customer && f.customer.indexOf(customer) === -1) ok = false;
            else if (dateFrom && f.date < dateFrom) ok = false;
            else if (dateTo && f.date > dateTo) ok = false;
            else if (overnight) {
                if (!(f.time >= timeFrom || f.time <= timeTo)) ok = false;
            } else {
                if (timeFrom && f.time < timeFrom) ok = false;
                else if (timeTo && f.time > timeTo) ok = false;
            }

            if (ok) visible++;

            // فقط ردیف‌هایی که وضعیتشان عوض شده را تغییر بده
            if (row._hidden === ok) {
                row.style.display = ok ? "" : "none";
                row._hidden = !ok;
            }
        }

        el.table.style.display = visible ? "" : "none";
        el.empty.style.display = visible ? "none" : "";

        el.count.textContent =
            "نمایش " + fa.format(visible) + " از " + fa.format(rows.length) + " سفارش";
    }

    // چند رویداد پشت‌سرهم (input + change + ...) یک‌بار محاسبه شوند
    var timer = null;
    function scheduleFilter() {
        clearTimeout(timer);
        timer = setTimeout(applyFilters, 120);
    }

    [el.number, el.customer, el.dateFrom, el.dateTo, el.timeFrom, el.timeTo]
        .forEach(function (input) {
            ["input", "change", "jdp:change"].forEach(function (evt) {
                input.addEventListener(evt, scheduleFilter);
            });
            // پاک کردن از داخل خود تقویم
            input.addEventListener("blur", scheduleFilter);
        });

    el.reset.addEventListener("click", function () {
        [el.number, el.customer, el.dateFrom, el.dateTo, el.timeFrom, el.timeTo]
            .forEach(function (input) { input.value = ""; });
        applyFilters();
    });

    if (typeof jalaliDatepicker !== "undefined") {
        jalaliDatepicker.startWatch({
            time: true,
            hasSecond: "attr",
            autoReadOnlyInput: true,
            showEmptyBtn: true,
            zIndex: 900
        });
    }

    applyFilters();

});