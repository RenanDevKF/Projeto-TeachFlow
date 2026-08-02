document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('exercise-filter-form');
    const statusInput = document.getElementById('exercise-status-input');
    const typeInput = document.getElementById('exercise-type-input');
    const searchInput = document.getElementById('exercise-search-input');

    const statusButtons = document.querySelectorAll(
        '[data-exercise-status]'
    );
    const typeButtons = document.querySelectorAll(
        '[data-exercise-type]'
    );

    const automaticSelects = [
        document.getElementById('exercise-duration-filter'),
        document.getElementById('exercise-tag-filter'),
        document.getElementById('exercise-objective-filter'),
    ].filter(Boolean);

    if (!filterForm) {
        return;
    }

    let searchTimeout = null;

    statusButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!statusInput) {
                return;
            }

            statusInput.value = button.dataset.exerciseStatus;
            filterForm.requestSubmit();
        });
    });

    typeButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!typeInput) {
                return;
            }

            typeInput.value = button.dataset.exerciseType;
            filterForm.requestSubmit();
        });
    });

    automaticSelects.forEach((select) => {
        select.addEventListener('change', () => {
            filterForm.requestSubmit();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            window.clearTimeout(searchTimeout);

            searchTimeout = window.setTimeout(() => {
                filterForm.requestSubmit();
            }, 400);
        });

        const urlParameters = new URLSearchParams(window.location.search);

        if (urlParameters.has('search')) {
            searchInput.focus();

            const valueLength = searchInput.value.length;
            searchInput.setSelectionRange(valueLength, valueLength);
        }
    }
});