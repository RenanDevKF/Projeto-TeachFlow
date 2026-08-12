document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('library-filter-form');
    const searchInput = document.getElementById('library-search');
    const statusSelect = document.getElementById('library-status-filter');

    if (!filterForm) return;

    let searchTimeout = null;
    let isSubmitting = false;

    function submitFilters() {
        if (isSubmitting) return;

        isSubmitting = true;
        filterForm.requestSubmit();
    }

    statusSelect?.addEventListener('change', submitFilters);

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            window.clearTimeout(searchTimeout);

            searchTimeout = window.setTimeout(() => {
                submitFilters();
            }, 300);
        });

        const urlParameters = new URLSearchParams(
            window.location.search
        );

        if (urlParameters.has('q')) {
            searchInput.focus();

            const valueLength = searchInput.value.length;

            searchInput.setSelectionRange(
                valueLength,
                valueLength
            );
        }
    }

    filterForm.addEventListener('submit', () => {
        isSubmitting = true;
    });
});