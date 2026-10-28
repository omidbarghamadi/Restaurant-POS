document.addEventListener("DOMContentLoaded", function () {

    /* ===== تقویم شمسی ===== */
    if (typeof jalaliDatepicker !== "undefined") {
        jalaliDatepicker.startWatch({
            time: true,
            hasSecond: false,
            hideAfterChange: true
        });
    }

    /* ===== جداکننده سه‌رقمی مبلغ ===== */
    var amountInput = document.querySelector(".amount-input");

    if (amountInput) {

        function toEnglishDigits(str) {
            return str.replace(/[۰-۹]/g, function (d) {
                return "۰۱۲۳۴۵۶۷۸۹".indexOf(d);
            });
        }

        function formatWithCommas(rawValue) {
            var digitsOnly = toEnglishDigits(rawValue).replace(/[^\d]/g, "");
            if (!digitsOnly) return "";
            return Number(digitsOnly).toLocaleString("en-US");
        }

        amountInput.value = formatWithCommas(amountInput.value);

        amountInput.addEventListener("input", function () {
            var cursorFromEnd = amountInput.value.length - amountInput.selectionStart;
            amountInput.value = formatWithCommas(amountInput.value);
            var newPos = amountInput.value.length - cursorFromEnd;
            amountInput.setSelectionRange(newPos, newPos);
        });

        var formEl = amountInput.closest("form");
        if (formEl) {
            formEl.addEventListener("submit", function () {
                amountInput.value = amountInput.value.replace(/,/g, "");
            });
        }
    }

    /* ===== نمایش/اجباری بودن مشتری و کارمند ===== */
    var typeSelect = document.getElementById("id_transaction_type");
    var employeeGroup = document.getElementById("employee-group");
    var customerGroup = document.getElementById("customer-group");
    var employeeSelect = document.getElementById("id_employee");
    var customerSelect = document.getElementById("id_customer");

    if (!typeSelect || !employeeGroup || !customerGroup) return;

    var EMPLOYEE_TYPES = ["salary", "delivery"];
    var CUSTOMER_TYPES = ["receivable"];

    function clearSelect(selectEl) {
        if (!selectEl) return;
        selectEl.value = "";
        // اگر Select2 فعال است، نمایش آن هم به‌روز شود
        if (window.jQuery && window.jQuery(selectEl).data("select2")) {
            window.jQuery(selectEl).trigger("change.select2");
        }
    }

    function setRequired(groupEl, selectEl, required) {
        groupEl.classList.toggle("is-required", required);
        if (selectEl) {
            selectEl.required = required;
        }
    }

    function updateVisibility() {
        var value = typeSelect.value;
        var showEmployee = EMPLOYEE_TYPES.indexOf(value) !== -1;
        var showCustomer = CUSTOMER_TYPES.indexOf(value) !== -1;

        employeeGroup.style.display = showEmployee ? "" : "none";
        customerGroup.style.display = showCustomer ? "" : "none";

        setRequired(employeeGroup, employeeSelect, showEmployee);
        setRequired(customerGroup, customerSelect, showCustomer);

        if (!showEmployee) clearSelect(employeeSelect);
        if (!showCustomer) clearSelect(customerSelect);
    }

    typeSelect.addEventListener("change", updateVisibility);
    updateVisibility();
});