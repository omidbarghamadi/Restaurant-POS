/* =========================================================
   ORDER FORM PAGE
   جاوااسکریپت صفحه ثبت/ویرایش سفارش (order_form.html)

   مقادیری که قبلاً با تگ‌های تمپلیت جنگو داخل اسکریپت می‌آمدند،
   حالا از data-attributeهای تگ <form id="order-form"> خوانده می‌شوند:
     data-is-edit               → حالت ویرایش (true/false)
     data-customer-create-url   → آدرس ثبت سریع مشتری
     data-field-*               → id فیلدهای فرم (id_for_label)

   همچنین اسکریپت json_script با id="customers-data" باید در صفحه باشد.
   کتابخانه‌ی jalalidatepicker باید قبل از این فایل لود شده باشد.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    // ==================================================
    // تنظیمات (از data-attributeهای فرم)
    // ==================================================

    var orderFormEl = document.getElementById("order-form");

    if (!orderFormEl) {
        return;
    }

    var cfg = orderFormEl.dataset;

    var IS_EDIT = cfg.isEdit === "true";

    // آدرس endpoint ثبت سریع مشتری
    var CUSTOMER_CREATE_URL = cfg.customerCreateUrl;

    // اطلاعات همه‌ی مشتری‌ها (از ویو)؛ برای نمایش موبایل و آدرس بعد از انتخاب
    var customersDataEl = document.getElementById("customers-data");
    var customersData = customersDataEl ? JSON.parse(customersDataEl.textContent) : {};

    var csrfToken = orderFormEl.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    ).value;


    // ==================================================
    // پیام توست
    // ==================================================

    var toastContainer = document.getElementById("toast-container");

    function showToast(message, type) {

        if (!toastContainer) {
            return;
        }

        var toast = document.createElement("div");
        toast.className = "toast" + (type === "success" ? " toast--success" : "");
        toast.setAttribute("role", type === "success" ? "status" : "alert");

        var text = document.createElement("span");
        text.className = "toast__text";
        text.textContent = message;

        var close = document.createElement("button");
        close.type = "button";
        close.className = "toast__close";
        close.setAttribute("aria-label", "بستن");
        close.textContent = "×";

        toast.appendChild(text);
        toast.appendChild(close);
        toastContainer.appendChild(toast);

        function dismiss() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }

        toast.addEventListener("click", dismiss);
        setTimeout(dismiss, type === "success" ? 3500 : 6000);
    }

    // نمایش چند خطا با هم؛ بیش از ۴ مورد در یک توست خلاصه می‌شود
    function showToasts(messages) {
        var MAX = 4;
        messages.slice(0, MAX).forEach(function (m) {
            showToast(m, "error");
        });
        if (messages.length > MAX) {
            showToast("و " + (messages.length - MAX) + " خطای دیگر. لطفاً فرم را بررسی کنید.", "error");
        }
    }

    // خطاهایی که سرور بعد از ارسال فرم برگردانده است
    var serverMessages = [];
    document.querySelectorAll("#server-errors span").forEach(function (el) {
        var text = el.textContent.trim();
        if (text) {
            serverMessages.push(text);
        }
    });
    showToasts(serverMessages);


    // ==================================================
    // افزودن / حذف آیتم سفارش
    // ==================================================

    var container = document.getElementById("order-items");
    var addButton = document.getElementById("add-item");
    var totalForms = document.getElementById("id_items-TOTAL_FORMS");
    var emptyForm = document.getElementById("empty-form").innerHTML;

    if (IS_EDIT) {
        // در حالت ویرایش، ردیف(های) خالی انتهایی که formset خودش اضافه کرده
        // (extra) حذف می‌شود. فقط ردیف‌های انتهایی که ذخیره نشده‌اند، محصولی
        // ندارند و خطایی هم ندارند حذف می‌شوند؛ پس ایندکس بقیه ردیف‌ها
        // پیوسته می‌ماند و TOTAL_FORMS با تعداد ردیف‌های باقی‌مانده برابر می‌شود.
        (function removeBlankTrailingRows() {

            var rows = Array.prototype.slice.call(container.querySelectorAll("[data-item-row]"));

            while (rows.length) {
                var row = rows[rows.length - 1];
                var idInput = row.querySelector('input[name$="-id"]');
                var variant = row.querySelector(".menu-item-select");
                var hasErrors = !!row.querySelector(".field-error");
                var isSaved = !!(idInput && idInput.value);
                var isBlank = !isSaved && variant && !variant.value && !hasErrors;

                if (!isBlank) {
                    break;
                }

                row.remove();
                rows.pop();
            }

            totalForms.value = rows.length;
        })();
    }

    addButton.addEventListener("click", function () {

        var formIndex = parseInt(totalForms.value, 10);

        var newForm = emptyForm.replace(/__prefix__/g, formIndex);

        container.insertAdjacentHTML("beforeend", newForm);

        totalForms.value = formIndex + 1;

        var addedRow = container.lastElementChild;
        var addedSelect = addedRow ? addedRow.querySelector(".menu-item-select") : null;

        if (addedSelect && typeof initSearchableSelect === "function") {
            initSearchableSelect(addedSelect);
        }

        recalcSummary();

    });


    container.addEventListener("click", function (event) {

        var removeBtn = event.target.closest(".item-remove-btn");

        if (removeBtn) {

            var row = removeBtn.closest(".item-row");

            if (!row) {
                return;
            }

            var deleteInput = row.querySelector('input[name$="-DELETE"]');

            if (deleteInput) {
                deleteInput.checked = true;
                row.hidden = true;
            } else {
                // ردیف ذخیره‌نشده را نباید از DOM حذف کرد: TOTAL_FORMS ثابت می‌ماند
                // و فرمِ بدون داده برای Django «تغییرکرده» حساب می‌شود (چون مقدار
                // اولیه تعداد ۱ است) و خطای «محصول الزامی است» می‌دهد. به‌جای آن،
                // مقادیر را به حالت اولیه برمی‌گردانیم و ردیف را مخفی می‌کنیم تا
                // Django آن را ردیف خالی بداند و نادیده بگیرد.
                var rowSelect = row.querySelector(".menu-item-select");
                var rowSearchInput = row.querySelector(".searchable-select__input");
                var rowQty = row.querySelector(".quantity-input");
                var rowNote = row.querySelector('input[name$="-note"]');

                if (rowSelect) { rowSelect.value = ""; }
                if (rowSearchInput) { rowSearchInput.value = ""; }
                if (rowQty) { rowQty.value = 1; }
                if (rowNote) { rowNote.value = ""; }

                row.hidden = true;
            }

            recalcSummary();

        } else if (event.target.classList.contains("qty-btn")) {

            var qtyRow = event.target.closest(".item-row");
            var qtyInput = qtyRow.querySelector(".quantity-input");

            if (!qtyInput) {
                return;
            }

            var current = parseInt(qtyInput.value, 10) || 1;
            var min = parseInt(qtyInput.min, 10) || 1;

            if (event.target.classList.contains("qty-btn--plus")) {
                qtyInput.value = current + 1;
            } else {
                qtyInput.value = Math.max(current - 1, min);
            }

            recalcSummary();

        }

    });


    container.addEventListener("change", function (event) {
        if (
            event.target.classList.contains("menu-item-select") ||
            event.target.classList.contains("quantity-input")
        ) {
            recalcSummary();
        }
    });

    container.addEventListener("input", function (event) {
        if (event.target.classList.contains("quantity-input")) {
            recalcSummary();
        }
    });


    // ==================================================
    // خلاصه زنده سفارش
    // ==================================================

    var numberFormatter = new Intl.NumberFormat("fa-IR");

    function toToman(value) {
        return numberFormatter.format(value || 0) + " تومان";
    }

    function fieldValue(id) {
        var el = document.getElementById(id);
        if (!el) {
            return 0;
        }
        var digits = (el.value || "").replace(/[^\d]/g, "");
        return parseInt(digits, 10) || 0;
    }

    function setSummary(key, value) {
        var el = document.querySelector('[data-summary="' + key + '"]');
        if (el) {
            el.textContent = toToman(value);
        }
    }

    function recalcSummary() {

        var itemsTotal = 0;

        document.querySelectorAll("[data-item-row]").forEach(function (row) {

            if (row.hidden) {
                return;
            }

            var select = row.querySelector(".menu-item-select");
            var qtyInput = row.querySelector(".quantity-input");
            var lineTotalEl = row.querySelector("[data-line-total]");

            var selectedOption = select
                ? select.options[select.selectedIndex]
                : null;

            var price = selectedOption
                ? parseInt(selectedOption.getAttribute("data-price"), 10) || 0
                : 0;

            // آیتم ذخیره‌شده با همان زیرمنو: قیمتِ زمان ثبت سفارش ملاک است،
            // نه قیمت فعلی زیرمنو.
            var savedPrice = row.getAttribute("data-saved-price");
            var savedVariant = row.getAttribute("data-saved-variant");
            if (savedPrice && savedVariant && select && select.value === savedVariant) {
                price = parseInt(savedPrice, 10) || 0;
            }

            var qty = qtyInput ? (parseInt(qtyInput.value, 10) || 0) : 0;
            var lineTotal = price * qty;

            if (lineTotalEl) {
                lineTotalEl.textContent = toToman(lineTotal);
            }

            itemsTotal += lineTotal;

        });

        var discount = fieldValue(cfg.fieldDiscount);
        var delivery = fieldValue(cfg.fieldDelivery);
        var packaging = fieldValue(cfg.fieldPackagingCost);

        var total = Math.max(itemsTotal + delivery + packaging - discount, 0);

        setSummary("items", itemsTotal);
        setSummary("discount", discount);
        setSummary("delivery", delivery);
        setSummary("packaging", packaging);
        setSummary("total", total);

    }

    // ==================================================
    // جداکننده هزار برای فیلدهای مبلغ
    // ==================================================

    var groupFormatter = new Intl.NumberFormat("en-US");

    function formatMoneyInput(el) {
        var digits = (el.value || "").replace(/[^\d]/g, "");
        el.value = digits ? groupFormatter.format(parseInt(digits, 10)) : "";
    }

    document.querySelectorAll(".money-input").forEach(function (el) {
        formatMoneyInput(el);
        el.addEventListener("input", function () {
            formatMoneyInput(el);
            recalcSummary();
        });
    });

    // قبل از ارسال فرم، جداکننده‌های نمایشی حذف می‌شوند تا مقدار خام
    // (فقط رقم) به سرور برسد.
    orderFormEl.addEventListener("submit", function () {
        document.querySelectorAll(".money-input").forEach(function (el) {
            el.value = (el.value || "").replace(/[^\d]/g, "");
        });
    });

    recalcSummary();


    // ==================================================
    // نمایش/الزامی بودن شماره میز برای سفارش داخل سالن
    // ==================================================

    var orderTypeSelect = document.getElementById(cfg.fieldOrderType);
    var tableNumberGroup = document.getElementById("table-number-group");

    function toggleTableNumber() {
        if (!orderTypeSelect || !tableNumberGroup) {
            return;
        }
        var opt = orderTypeSelect.options[orderTypeSelect.selectedIndex];
        var isDineIn = !!(opt && opt.textContent.indexOf("داخل سالن") !== -1);
        tableNumberGroup.classList.toggle("is-required", isDineIn);
    }

    if (orderTypeSelect) {
        orderTypeSelect.addEventListener("change", toggleTableNumber);
        toggleTableNumber();
    }


    // ==================================================
    // مودال افزودن مشتری جدید
    // ==================================================

    var customerModal = document.getElementById("customer-modal");
    var openCustomerModalBtn = document.getElementById("open-customer-modal");
    var closeCustomerModalBtn = document.getElementById("customer-modal-close");
    var cancelCustomerModalBtn = document.getElementById("customer-modal-cancel");
    var saveCustomerBtn = document.getElementById("customer-modal-save");
    var customerCodeInput = document.getElementById("new-customer-code");
    var customerNameInput = document.getElementById("new-customer-name");
    var customerMobileInput = document.getElementById("new-customer-mobile");
    var customerPhoneInput = document.getElementById("new-customer-phone");
    var customerAddressInput = document.getElementById("new-customer-address");
    var customerModalError = document.getElementById("customer-modal-error");
    var customerSelect = document.getElementById(cfg.fieldCustomer);

    function openCustomerModal() {
        customerModalError.hidden = true;
        customerCodeInput.value = "";
        customerNameInput.value = "";
        customerMobileInput.value = "";
        customerPhoneInput.value = "";
        customerAddressInput.value = "";
        customerModal.hidden = false;
        customerCodeInput.focus();
    }

    function closeCustomerModal() {
        customerModal.hidden = true;
    }

    function showCustomerError(message) {
        // خطا به صورت توست نمایش داده می‌شود (z-index بالاتر از مودال)
        showToast(message, "error");
    }

    if (openCustomerModalBtn) {
        openCustomerModalBtn.addEventListener("click", openCustomerModal);
    }

    closeCustomerModalBtn.addEventListener("click", closeCustomerModal);
    cancelCustomerModalBtn.addEventListener("click", closeCustomerModal);

    customerModal.addEventListener("click", function (event) {
        if (event.target === customerModal) {
            closeCustomerModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !customerModal.hidden) {
            closeCustomerModal();
        }
    });

    saveCustomerBtn.addEventListener("click", function () {

        var subscriptionCode = customerCodeInput.value.trim();
        var name = customerNameInput.value.trim();
        var mobile = customerMobileInput.value.trim();
        var phone = customerPhoneInput.value.trim();
        var address = customerAddressInput.value.trim();

        if (!subscriptionCode) {
            showCustomerError("لطفاً کد اشتراک را وارد کنید.");
            customerCodeInput.focus();
            return;
        }

        if (!name) {
            showCustomerError("لطفاً نام مشتری را وارد کنید.");
            customerNameInput.focus();
            return;
        }

        if (!/^\d{11}$/.test(mobile)) {
            showCustomerError("شماره موبایل باید ۱۱ رقم و فقط عدد باشد.");
            customerMobileInput.focus();
            return;
        }

        saveCustomerBtn.disabled = true;
        saveCustomerBtn.querySelector(".btn-label").textContent = "در حال ذخیره...";

        fetch(CUSTOMER_CREATE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify({
                subscription_code: subscriptionCode,
                name: name,
                mobile: mobile,
                phone: phone,
                address: address,
            }),
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok) {
                        throw new Error(data.error || "request-failed");
                    }
                    return data;
                });
            })
            .then(function (data) {

                var label = data.name || (subscriptionCode + " " + name);

                // اطلاعات مشتری تازه‌ساخته‌شده را هم به لیست محلی اضافه می‌کنیم
                customersData[String(data.id)] = {
                    code: subscriptionCode,
                    name: name,
                    mobile: mobile,
                    phone: phone,
                    address: address
                };

                if (customerSearchable) {
                    // گزینه جدید را به <select> اصلی اضافه و انتخاب می‌کنیم؛
                    // کامپوننت جستجو خودش با آن هماهنگ می‌شود.
                    customerSearchable.addOption(String(data.id), label, true);
                } else {
                    var option = document.createElement("option");
                    option.value = data.id;
                    option.textContent = label;
                    option.selected = true;
                    customerSelect.appendChild(option);
                    customerSelect.value = data.id;
                }

                closeCustomerModal();
                showToast("مشتری جدید با موفقیت ثبت شد.", "success");

            })
            .catch(function (err) {
                showCustomerError(
                    (err && err.message && err.message !== "request-failed")
                        ? err.message
                        : "ثبت مشتری با خطا مواجه شد. دوباره تلاش کنید یا مسیر endpoint را بررسی کنید."
                );
            })
            .finally(function () {
                saveCustomerBtn.disabled = false;
                saveCustomerBtn.querySelector(".btn-label").textContent = "ذخیره مشتری";
            });

    });


    // ==================================================
    // جستجوی درون‌خطی روی لیست‌های کشویی (بدون کتابخانه خارجی)
    //
    // به‌جای باز شدن یک کادر جستجوی جداگانه، همان فیلد نمایشی
    // select به یک ورودی متنی قابل‌تایپ تبدیل می‌شود؛ با تایپ در
    // همان فیلد، گزینه‌ها فیلتر می‌شوند. <select> اصلی مخفی می‌ماند
    // اما مقدارش هماهنگ نگه داشته می‌شود، پس هیچ منطق دیگری
    // (محاسبه قیمت، الزامی‌بودن شماره میز و ...) نیاز به تغییر ندارد.
    // ==================================================

    // options.clearable: اگر true باشد، کاربر می‌تواند انتخاب را برگرداند
    // و مقدار را خالی کند (برای فیلدهای غیراجباری مثل مشتری و کارمند).
    function initSearchableSelect(selectEl, options) {

        var clearable = !!(options && options.clearable);

        if (!selectEl || selectEl.dataset.searchableInit) {
            return null;
        }

        selectEl.dataset.searchableInit = "1";

        var wrapper = document.createElement("div");
        wrapper.className = "searchable-select";

        selectEl.parentNode.insertBefore(wrapper, selectEl);
        wrapper.appendChild(selectEl);
        selectEl.classList.add("searchable-select__native");

        var input = document.createElement("input");
        input.type = "text";
        input.autocomplete = "off";
        input.className = "form-control searchable-select__input";

        var list = document.createElement("div");
        list.className = "searchable-select__list";
        list.hidden = true;

        wrapper.appendChild(input);
        wrapper.appendChild(list);

        function getOptions() {
            return Array.prototype.map.call(selectEl.options, function (opt) {
                return { value: opt.value, label: opt.textContent };
            });
        }

        function currentLabel() {
            var opt = selectEl.options[selectEl.selectedIndex];
            return opt ? opt.textContent : "";
        }

        function syncInputFromSelect() {
            if (clearable && selectEl.value === "") {
                // مقدار خالی: به جای «---------» فیلد خالی با راهنما نمایش داده می‌شود
                input.value = "";
                input.placeholder = "بدون انتخاب";
                return;
            }
            input.value = currentLabel();
        }

        function closeList() {
            list.hidden = true;
            wrapper.classList.remove("is-open");
        }

        function selectValue(value, label) {
            selectEl.value = value;
            input.value = label;
            closeList();
            selectEl.dispatchEvent(new Event("change", { bubbles: true }));
        }

        function renderList(filterText) {

            list.innerHTML = "";

            var query = (filterText || "").trim().toLowerCase();
            var options = getOptions();
            var hasMatch = false;

            // گزینه خالی در بالای لیست، فقط وقتی چیزی انتخاب شده باشد
            if (clearable && selectEl.value !== "" && !query) {
                var clearItem = document.createElement("div");
                clearItem.className = "searchable-select__clear";
                clearItem.textContent = "× بدون انتخاب (پاک کردن)";
                clearItem.addEventListener("mousedown", function (event) {
                    event.preventDefault();
                    selectValue("", "");
                });
                list.appendChild(clearItem);
            }

            options.forEach(function (opt) {

                // گزینه خالی («---------») در لیست جستجو نشان داده نمی‌شود
                if (opt.value === "") {
                    return;
                }

                if (query && opt.label.toLowerCase().indexOf(query) === -1) {
                    return;
                }

                hasMatch = true;

                var item = document.createElement("div");
                item.className = "searchable-select__option";
                item.textContent = opt.label;
                item.dataset.value = opt.value;

                if (opt.value === selectEl.value) {
                    item.classList.add("is-selected");
                }

                item.addEventListener("mousedown", function (event) {
                    event.preventDefault();
                    selectValue(opt.value, opt.label);
                });

                list.appendChild(item);

            });

            if (!hasMatch) {
                var empty = document.createElement("div");
                empty.className = "searchable-select__empty";
                empty.textContent = "موردی یافت نشد";
                list.appendChild(empty);
            }

        }

        function openList() {
            renderList("");
            list.hidden = false;
            wrapper.classList.add("is-open");
        }

        input.addEventListener("focus", function () {
            input.select();
            openList();
        });

        input.addEventListener("input", function () {
            renderList(input.value);
            list.hidden = false;
            wrapper.classList.add("is-open");
        });

        input.addEventListener("blur", function () {
            if (clearable && input.value.trim() === "" && selectEl.value !== "") {
                selectValue("", "");
            }
            // با کمی تاخیر، تا رویداد کلیک روی گزینه زودتر ثبت شود
            setTimeout(function () {
                syncInputFromSelect();
                closeList();
            }, 120);
        });

        input.addEventListener("keydown", function (event) {

            var items = list.querySelectorAll(".searchable-select__option");
            var activeIndex = -1;

            items.forEach(function (item, idx) {
                if (item.classList.contains("is-active")) {
                    activeIndex = idx;
                }
            });

            if (event.key === "ArrowDown") {
                event.preventDefault();
                if (!items.length) return;
                if (activeIndex >= 0) items[activeIndex].classList.remove("is-active");
                var next = items[Math.min(activeIndex + 1, items.length - 1)];
                next.classList.add("is-active");
                next.scrollIntoView({ block: "nearest" });

            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                if (!items.length) return;
                if (activeIndex >= 0) items[activeIndex].classList.remove("is-active");
                var prev = items[Math.max(activeIndex - 1, 0)];
                prev.classList.add("is-active");
                prev.scrollIntoView({ block: "nearest" });

            } else if (event.key === "Enter") {
                event.preventDefault();
                var active = list.querySelector(".searchable-select__option.is-active") || items[0];
                if (active) {
                    selectValue(active.dataset.value, active.textContent);
                }

            } else if (event.key === "Escape") {
                syncInputFromSelect();
                closeList();
                input.blur();
            }

        });

        document.addEventListener("click", function (event) {
            if (!wrapper.contains(event.target)) {
                closeList();
            }
        });

        syncInputFromSelect();

        return {
            addOption: function (value, label, selectIt) {
                var opt = document.createElement("option");
                opt.value = value;
                opt.textContent = label;
                selectEl.appendChild(opt);
                if (selectIt) {
                    selectValue(value, label);
                }
            },
        };
    }

    // مشتری جدا مقداردهی می‌شود چون نمونه آن برای افزودن مشتری
    // تازه‌ساخته‌شده از داخل مودال لازم است.
    var customerSearchable = initSearchableSelect(customerSelect, { clearable: true });

    // ==================================================
    // نمایش اطلاعات مشتری (موبایل، تلفن، آدرس) پس از انتخاب
    // ==================================================

    var customerInfoBox = document.getElementById("customer-info");

    function renderCustomerInfo() {

        if (!customerInfoBox) {
            return;
        }

        var info = customerSelect && customerSelect.value
            ? customersData[String(customerSelect.value)]
            : null;

        if (!info) {
            customerInfoBox.hidden = true;
            return;
        }

        Object.keys(info).forEach(function (key) {
            var el = customerInfoBox.querySelector('[data-customer="' + key + '"]');
            if (el) {
                el.textContent = info[key] || "";  // textContent: امن در برابر XSS
            }
        });

        // فیلدهای اختیاری وقتی خالی‌اند مخفی شوند
        ["phone", "address"].forEach(function (key) {
            var row = customerInfoBox.querySelector('[data-customer-row="' + key + '"]');
            if (row) {
                row.hidden = !info[key];
            }
        });

        customerInfoBox.hidden = false;
    }

    if (customerSelect) {
        customerSelect.addEventListener("change", renderCustomerInfo);
    }

    renderCustomerInfo(); // حالت ویرایش یا بازگشت فرم با خطا

    initSearchableSelect(
        document.getElementById(cfg.fieldEmployee),
        { clearable: true }
    );

    initSearchableSelect(orderTypeSelect);

    document.querySelectorAll(".menu-item-select").forEach(function (el) {
        initSearchableSelect(el);
    });


    // ==================================================
    // نمایش/الزامی بودن مشتری و کارمند بر اساس نوع سفارش و نوع پرداخت
    //
    // - «شام کارکنان»: مشتری مخفی؛ کارمند نمایش و الزامی
    // - سایر نوع‌ها: کارمند مخفی
    // - «تلفنی» یا پرداخت «نسیه»: مشتری الزامی
    //
    // تطبیق با متن گزینه انجام می‌شود (مثل بخش «داخل سالن» بالاتر).
    // ==================================================

    var customerGroup = document.getElementById("customer-group");
    var employeeGroup = document.getElementById("employee-group");
    var employeeSelect = document.getElementById(cfg.fieldEmployee);
    var paymentMethodSelect = document.getElementById(cfg.fieldPaymentMethod);
    var paymentStatusSelect = document.getElementById("id_payment_status"); // اگر در فرم باشد

    function selectedText(selectEl) {
        if (!selectEl || selectEl.selectedIndex < 0) {
            return "";
        }
        return (selectEl.options[selectEl.selectedIndex].textContent || "").trim();
    }

    // مقدار select مخفی را خالی می‌کند و متن فیلد جستجوگر را هم پاک می‌کند
    function clearSearchableSelect(selectEl, groupEl) {
        if (!selectEl || !selectEl.value) {
            return;
        }
        selectEl.value = "";
        var visibleInput = groupEl.querySelector(".searchable-select__input");
        if (visibleInput) {
            visibleInput.value = "";
            visibleInput.placeholder = "بدون انتخاب";
        }
        // تا بخش‌هایی مثل کارت اطلاعات مشتری هم به‌روز شوند
        selectEl.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function applyOrderRules() {

        var typeText = selectedText(orderTypeSelect);
        var isStaffDinner = typeText.indexOf("شام کارکنان") !== -1;
        var isPhone = typeText.indexOf("تلفنی") !== -1;
        var isCredit =
            selectedText(paymentMethodSelect).indexOf("نسیه") !== -1 ||
            (paymentStatusSelect && (paymentStatusSelect.value === "credit" ||
                selectedText(paymentStatusSelect).indexOf("نسیه") !== -1));

        // کارمند: فقط برای شام کارکنان؛ همیشه الزامی وقتی نمایش داده می‌شود
        employeeGroup.style.display = isStaffDinner ? "" : "none";
        employeeGroup.classList.toggle("is-required", isStaffDinner);
        if (!isStaffDinner) {
            clearSearchableSelect(employeeSelect, employeeGroup);
        }

        // مشتری: در شام کارکنان مخفی؛ در تلفنی یا نسیه الزامی
        customerGroup.style.display = isStaffDinner ? "none" : "";
        customerGroup.classList.toggle("is-required", !isStaffDinner && (isPhone || isCredit));
        if (isStaffDinner) {
            clearSearchableSelect(customerSelect, customerGroup);
        }
    }

    // select اصلی display:none است؛ پس required مرورگر روی آن کار نمی‌کند.
    // (فرم novalidate است و همه بررسی‌ها اینجا انجام و با توست نمایش داده می‌شوند.)

    function validateOrderForm() {

        applyOrderRules();
        syncGregorianFromJalali();

        var errors = []; // هر مورد: { message, focusEl }

        function fail(message, focusEl) {
            errors.push({ message: message, focusEl: focusEl || null });
        }

        function inputOf(groupEl) {
            return groupEl ? groupEl.querySelector(".searchable-select__input, input, select") : null;
        }

        if (orderTypeSelect && !orderTypeSelect.value) {
            fail("نوع سفارش را انتخاب کنید.", inputOf(orderTypeSelect.closest(".form-group")));
        }

        if (employeeGroup.classList.contains("is-required") && !employeeSelect.value) {
            fail("برای شام کارکنان، انتخاب کارمند الزامی است.", inputOf(employeeGroup));
        }

        if (customerGroup.classList.contains("is-required") && !customerSelect.value) {
            fail("برای سفارش تلفنی یا نسیه، انتخاب مشتری الزامی است.", inputOf(customerGroup));
        }

        if (tableNumberGroup && tableNumberGroup.classList.contains("is-required")) {
            var tableInput = tableNumberGroup.querySelector("input, select");
            if (tableInput && !String(tableInput.value).trim()) {
                fail("برای سفارش داخل سالن، شماره میز را وارد کنید.", tableInput);
            }
        }

        if (dateGregorian && !dateGregorian.value) {
            fail("تاریخ سفارش را مشخص کنید.", dateJalali);
        }

        var rows = Array.prototype.filter.call(
            container.querySelectorAll("[data-item-row]"),
            function (row) { return !row.hidden; }
        );

        if (!rows.length) {
            fail("حداقل یک آیتم به سفارش اضافه کنید.", addButton);
        }

        rows.forEach(function (row, index) {
            var label = "آیتم " + (index + 1);
            var select = row.querySelector(".menu-item-select");
            var qty = row.querySelector(".quantity-input");

            if (!select || !select.value) {
                fail(label + ": محصول را انتخاب کنید.", row.querySelector(".searchable-select__input"));
            } else if (!qty || (parseInt(qty.value, 10) || 0) < 1) {
                fail(label + ": تعداد باید حداقل ۱ باشد.", qty);
            }
        });

        return errors;
    }

    orderFormEl.addEventListener("submit", function (event) {

        var errors = validateOrderForm();

        if (!errors.length) {
            return;
        }

        event.preventDefault();

        // لیسنر بالاتر جداکننده هزارگان را قبل از ارسال حذف کرده؛ نمایش را برمی‌گردانیم
        document.querySelectorAll(".money-input").forEach(formatMoneyInput);

        showToasts(errors.map(function (e) { return e.message; }));

        var firstFocusable = errors.filter(function (e) { return e.focusEl; })[0];
        if (firstFocusable) {
            firstFocusable.focusEl.focus();
        }
    });

    [orderTypeSelect, paymentMethodSelect, paymentStatusSelect].forEach(function (el) {
        if (el) {
            el.addEventListener("change", applyOrderRules);
        }
    });

    applyOrderRules(); // برای حالت ویرایش یا بازگشت فرم با خطا


    // ==================================================
    // تاریخ (شمسی) و ساعت سفارش
    // - مقدار پیش‌فرض: همین لحظه (اگر سرور مقداری نداده باشد)
    // - کاربر تاریخ شمسی را می‌بیند؛ مقدار میلادی در فیلد مخفی
    //   order_date ذخیره و به سرور ارسال می‌شود.
    // ==================================================

    var dateGregorian = document.getElementById(cfg.fieldOrderDate);
    var dateJalali = document.getElementById("order-date-jalali");
    var timeInput = document.getElementById(cfg.fieldOrderTime);

    function pad2(n) {
        return String(n).padStart(2, "0");
    }

    function toGregorianString(d) {
        return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
    }

    // تبدیل Date به رشته شمسی مثل 1405/07/08 با Intl داخلی مرورگر
    function toJalaliString(d) {
        var parts = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        }).formatToParts(d);

        var v = {};
        parts.forEach(function (p) { v[p.type] = p.value; });

        return v.year + "/" + v.month + "/" + v.day;
    }

    function normalizeDigits(str) {
        return String(str || "")
            .replace(/[\u06F0-\u06F9]/g, function (c) { return c.charCodeAt(0) - 0x06F0; })
            .replace(/[\u0660-\u0669]/g, function (c) { return c.charCodeAt(0) - 0x0660; });
    }

    // تبدیل تاریخ شمسی به میلادی (الگوریتم استاندارد jalaali)
    function jalaliToGregorian(jy, jm, jd) {
        jy += 1595;
        var days = -355668 + (365 * jy) + (Math.floor(jy / 33) * 8) +
            Math.floor(((jy % 33) + 3) / 4) + jd +
            ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
        var gy = 400 * Math.floor(days / 146097);
        days %= 146097;
        if (days > 36524) {
            days--;
            gy += 100 * Math.floor(days / 36524);
            days %= 36524;
            if (days >= 365) { days++; }
        }
        gy += 4 * Math.floor(days / 1461);
        days %= 1461;
        if (days > 365) {
            gy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        var gd = days + 1;
        var monthDays = [0, 31,
            ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        var gm = 0;
        while (gm < 13 && gd > monthDays[gm]) {
            gd -= monthDays[gm];
            gm++;
        }
        return [gy, gm, gd];
    }

    // مقدار فیلد شمسی (قابل مشاهده) را به فیلد میلادی مخفی منتقل می‌کند
    function syncGregorianFromJalali() {
        if (!dateGregorian || !dateJalali) {
            return;
        }
        var text = normalizeDigits(dateJalali.value).trim().replace(/[-.]/g, "/");
        var m = /^(\d{4})\/(\d{1,2})\/(\d{1,2})/.exec(text);
        if (!m) {
            dateGregorian.value = "";
            return;
        }
        var g = jalaliToGregorian(+m[1], +m[2], +m[3]);
        dateGregorian.value = g[0] + "-" + pad2(g[1]) + "-" + pad2(g[2]);
    }

    if (dateGregorian && dateJalali) {

        var now = new Date();
        var match = /^(\d{4})-(\d{2})-(\d{2})/.exec(dateGregorian.value || "");
        var baseDate;

        if (match) {
            // ظهر می‌گذاریم تا جابه‌جایی ساعت/منطقه زمانی روز را عوض نکند
            baseDate = new Date(+match[1], +match[2] - 1, +match[3], 12);
        } else {
            // سفارش جدید: امروز
            baseDate = now;
            dateGregorian.value = toGregorianString(now);
        }

        // پیش‌فرض: تاریخ شمسی همان روز (یا تاریخ ذخیره‌شده در حالت ویرایش)
        dateJalali.value = toJalaliString(baseDate);

        if (timeInput && !timeInput.value) {
            timeInput.value = pad2(now.getHours()) + ":" + pad2(now.getMinutes());
        }

        // هر بار که تقویم مقدار را عوض کرد، فیلد میلادی هم به‌روز شود
        ["jdp:change", "change", "input", "blur"].forEach(function (evt) {
            dateJalali.addEventListener(evt, syncGregorianFromJalali);
        });

        if (typeof jalaliDatepicker !== "undefined") {
            try {
                jalaliDatepicker.startWatch({
                    time: false,
                    autoReadOnlyInput: true,
                    showTodayBtn: true,
                    showEmptyBtn: false,
                    zIndex: 2000
                });
            } catch (err) {
                console.error("jalaliDatepicker init failed:", err);
            }
        }
    }

});