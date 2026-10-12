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