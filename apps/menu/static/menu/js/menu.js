function toggleVariantRow(rowId, triggerBtn) {

    var row = document.getElementById(rowId);

    if (!row) {
        return;
    }

    var isOpen = row.classList.contains('open');

    if (isOpen) {
        row.classList.remove('open');
        triggerBtn.classList.remove('open');
    } else {
        row.classList.add('open');
        triggerBtn.classList.add('open');
    }

}

(function () {

    var form = document.getElementById('menu-filter-form');
    var searchInput = document.getElementById('filter-search-input');
    var categorySelect = document.getElementById('filter-category-select');
    var resultsContainer = document.getElementById('menu-items-results');
    var loadingIndicator = document.getElementById('filter-loading-indicator');

    // این بخش فقط در صفحهٔ لیست آیتم‌های منو وجود دارد
    if (!form || !searchInput || !categorySelect || !resultsContainer) {
        return;
    }

    var debounceTimer = null;
    var activeController = null;

    function buildUrl() {

        var params = new URLSearchParams();

        if (searchInput.value.trim()) {
            params.set('q', searchInput.value.trim());
        }

        if (categorySelect.value) {
            params.set('category', categorySelect.value);
        }

        var qs = params.toString();

        return window.location.pathname + (qs ? '?' + qs : '');
    }

    function runFilter() {

        var url = buildUrl();

        if (activeController) {
            activeController.abort();
        }

        activeController = new AbortController();

        loadingIndicator.classList.add('visible');

        fetch(url, {
            signal: activeController.signal,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (response) {
                return response.text();
            })
            .then(function (html) {

                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
                var newResults = doc.getElementById('menu-items-results');

                if (newResults) {
                    resultsContainer.innerHTML = newResults.innerHTML;
                }

                var newClearBtn = doc.getElementById('filter-clear-btn');
                var currentClearBtn = document.getElementById('filter-clear-btn');

                if (newClearBtn && !currentClearBtn) {
                    loadingIndicator.insertAdjacentHTML('afterend', newClearBtn.outerHTML);
                } else if (!newClearBtn && currentClearBtn) {
                    currentClearBtn.remove();
                }

                window.history.replaceState({}, '', url);
                loadingIndicator.classList.remove('visible');
            })
            .catch(function (err) {
                if (err.name !== 'AbortError') {
                    loadingIndicator.classList.remove('visible');
                }
            });
    }

    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runFilter, 350);
    });

    categorySelect.addEventListener('change', function () {
        clearTimeout(debounceTimer);
        runFilter();
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearTimeout(debounceTimer);
        runFilter();
    });

})();

/* =========================================================
   فرم زیرمنو (variant_form)
   فقط وقتی فرم #variant-form در صفحه باشد اجرا می‌شود
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {

    var variantForm = document.getElementById('variant-form');

    if (!variantForm) {
        return;
    }

    /* 1) Select2 برای انتخاب آیتم منو */

    var menuItemSelect = variantForm.querySelector('[name="menu_item"]');

    if (menuItemSelect && window.jQuery && window.jQuery.fn.select2) {
        window.jQuery(menuItemSelect).select2({
            width: '100%',
            dir: 'rtl',
            language: {
                noResults: function () {
                    return 'موردی یافت نشد';
                },
                searching: function () {
                    return 'در حال جستجو...';
                }
            },
            placeholder: 'انتخاب آیتم منو'
        });
    }

    /* 2) جداکننده سه‌رقمی فیلد قیمت */

    var priceInput = variantForm.querySelector('[name="price"]');

    if (!priceInput) {
        return;
    }

    // کاما در type=number مجاز نیست، پس نوع فیلد را به text تغییر می‌دهیم
    priceInput.type = 'text';
    priceInput.setAttribute('inputmode', 'numeric');
    priceInput.setAttribute('autocomplete', 'off');

    function formatPrice(value) {
        var digitsOnly = String(value).replace(/,/g, '').replace(/[^0-9]/g, '');

        if (!digitsOnly) {
            return '';
        }

        return Number(digitsOnly).toLocaleString('en-US');
    }

    // فرمت‌دهی مقدار اولیه (در حالت ویرایش)
    if (priceInput.value) {
        var initial = parseFloat(String(priceInput.value).replace(/,/g, ''));

        if (!isNaN(initial)) {
            priceInput.value = formatPrice(Math.round(initial));
        }
    }

    priceInput.addEventListener('input', function (e) {
        var cursorFromEnd = e.target.value.length - e.target.selectionStart;

        e.target.value = formatPrice(e.target.value);

        var newPos = e.target.value.length - cursorFromEnd;
        e.target.setSelectionRange(newPos, newPos);
    });

    // حذف کاماها قبل از ارسال فرم به سرور
    variantForm.addEventListener('submit', function () {
        priceInput.value = priceInput.value.replace(/,/g, '');
    });

});