jalaliDatepicker.startWatch({ time: true, hasSecond: false, hideAfterChange: true });

(function () {
    var amountInput = document.querySelector(".amount-input");
    if (!amountInput) return;

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
})();

(function () {
    var typeSelect = document.getElementById("id_transaction_type");
    var employeeGroup = document.getElementById("employee-group");
    var customerGroup = document.getElementById("customer-group");
    var employeeSelect = document.getElementById("id_employee");
    var customerSelect = document.getElementById("id_customer");

    if (!typeSelect || !employeeGroup || !customerGroup) return;

    var EMPLOYEE_TYPES = ["salary", "delivery"];
    var CUSTOMER_TYPES = ["receivable"];

    function updateVisibility() {
        var value = typeSelect.value;
        var showEmployee = EMPLOYEE_TYPES.indexOf(value) !== -1;
        var showCustomer = CUSTOMER_TYPES.indexOf(value) !== -1;

        employeeGroup.style.display = showEmployee ? "" : "none";
        customerGroup.style.display = showCustomer ? "" : "none";

        if (!showEmployee && employeeSelect) {
            employeeSelect.value = "";
        }
        if (!showCustomer && customerSelect) {
            customerSelect.value = "";
        }
    }

    typeSelect.addEventListener("change", updateVisibility);
    updateVisibility();
})();