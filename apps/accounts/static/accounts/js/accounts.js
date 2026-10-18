/* =========================================================
   ACCOUNTS APP
   جاوااسکریپت مخصوص اپ accounts
   (فرم‌ها، لیست مشتریان، صفحه جزئیات مشتری)

   هر بخش فقط وقتی اجرا می‌شود که المان‌های مربوط به خودش
   در صفحه وجود داشته باشند؛ پس می‌شود این فایل را در همه‌ی
   تمپلیت‌های accounts بدون نگرانی لود کرد.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       1) جداکننده‌ی هزارگان برای فیلد «مانده حساب / جمع دریافتی»
          (customer_form, employee_form)
          سرور (MoneyField) کاماها را خودش پاک می‌کند.
    ====================================================== */

    function initBalanceInput() {

        var balanceInput = document.getElementById("id_balance");

        if (!balanceInput) {
            return;
        }

        function groupDigits(raw) {
            var negative = raw.trim().startsWith("-");
            var digits = raw.replace(/[^0-9]/g, "");

            digits = digits.replace(/^0+(?=\d)/, "");

            if (!digits) {
                return negative ? "-" : "";
            }

            var withCommas = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

            return negative ? "-" + withCommas : withCommas;
        }

        balanceInput.addEventListener("input", function () {
            var cursorFromEnd = this.value.length - this.selectionStart;

            this.value = groupDigits(this.value);

            var pos = this.value.length - cursorFromEnd;
            this.setSelectionRange(pos, pos);
        });
    }


    /* =====================================================
       2) تقویم شمسی (employee_form → تاریخ استخدام)
          کتابخانه‌ی jalalidatepicker باید قبل از این فایل
          در تمپلیت لود شده باشد.
    ====================================================== */

    function initJalaliDatepicker() {

        if (
            typeof jalaliDatepicker === "undefined" ||
            !document.querySelector("[data-jdp]")
        ) {
            return;
        }

        jalaliDatepicker.startWatch({
            time: false,
            hideAfterChange: true
        });
    }


    /* =====================================================
       3) فیلتر زنده‌ی لیست مشتریان (customer_list)
    ====================================================== */

    function initCustomerFilter() {

        var inputs = {
            name: document.getElementById("filter-name"),
            code: document.getElementById("filter-code"),
            phone: document.getElementById("filter-phone")
        };

        var resetBtn = document.getElementById("filter-reset");
        var noResults = document.getElementById("no-results-row");
        var countEl = document.getElementById("visible-count");
        var rows = document.querySelectorAll(
            "#customer-table-body .customer-row"
        );

        if (!inputs.name || !rows.length) {
            return;
        }

        // ارقام فارسی/عربی و حروف ی/ک عربی یکسان می‌شوند تا جستجو دقیق باشد
        function normalize(str) {
            return (str || "")
                .toString()
                .replace(/[۰-۹]/g, function (d) { return d.charCodeAt(0) - 1776; })
                .replace(/[٠-٩]/g, function (d) { return d.charCodeAt(0) - 1632; })
                .replace(/ي/g, "ی")
                .replace(/ك/g, "ک")
                .replace(/[\u200c\u200f\u200e]/g, " ")
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();
        }

        var data = Array.prototype.map.call(rows, function (row) {
            return {
                el: row,
                counter: row.querySelector(".row-counter"),
                name: normalize(row.dataset.name),
                code: normalize(row.dataset.code),
                phone: normalize(row.dataset.phone)
            };
        });

        function applyFilters() {

            var n = normalize(inputs.name.value);
            var c = normalize(inputs.code.value);
            var p = normalize(inputs.phone.value);
            var visible = 0;

            Object.keys(inputs).forEach(function (key) {
                inputs[key].classList.toggle(
                    "has-value",
                    inputs[key].value.trim() !== ""
                );
            });

            data.forEach(function (item) {

                var match =
                    (!n || item.name.indexOf(n) !== -1) &&
                    (!c || item.code.indexOf(c) !== -1) &&
                    (!p || item.phone.indexOf(p) !== -1);

                item.el.style.display = match ? "" : "none";

                if (match) {
                    visible++;
                    item.counter.textContent = visible;
                }
            });

            noResults.style.display = visible === 0 ? "" : "none";
            countEl.textContent = visible;
        }

        Object.keys(inputs).forEach(function (key) {
            inputs[key].addEventListener("input", applyFilters);
        });

        // دکمه‌ی «×» داخل هر فیلد
        document.querySelectorAll(".filter-clear").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var input = document.getElementById(btn.dataset.clear);

                input.value = "";
                applyFilters();
                input.focus();
            });
        });

        resetBtn.addEventListener("click", function () {
            Object.keys(inputs).forEach(function (key) {
                inputs[key].value = "";
            });

            applyFilters();
            inputs.name.focus();
        });
    }


    /* =====================================================
       4) نمایش تاریخ شمسی و مبلغ با جداکننده (customer_detail)
          <time data-jalali-date datetime="YYYY-MM-DD">
          <span data-money="123456">
    ====================================================== */

    function initDetailFormatting() {

        var jalaliFmt = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        });

        document.querySelectorAll("time[data-jalali-date]").forEach(function (t) {

            var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(
                t.getAttribute("datetime") || ""
            );

            if (!m) {
                return;
            }

            // ظهر می‌گذاریم تا جابه‌جایی منطقه زمانی روز را عوض نکند
            var d = new Date(+m[1], +m[2] - 1, +m[3], 12);
            var v = {};

            jalaliFmt.formatToParts(d).forEach(function (p) {
                v[p.type] = p.value;
            });

            t.textContent = v.year + "/" + v.month + "/" + v.day;
        });

        var moneyFmt = new Intl.NumberFormat("en-US");

        document.querySelectorAll("[data-money]").forEach(function (el) {
            var n = Number(el.getAttribute("data-money"));

            if (!isNaN(n)) {
                el.textContent = moneyFmt.format(n);
            }
        });
    }


    initBalanceInput();
    initJalaliDatepicker();
    initCustomerFilter();
    initDetailFormatting();

});