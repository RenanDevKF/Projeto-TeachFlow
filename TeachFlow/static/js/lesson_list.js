document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.querySelector('#lesson-filter-form');

    if (!filterForm) return;

    const automaticFilters = filterForm.querySelectorAll(
        '#lesson-class-filter, #lesson-tag-filter, #lesson-date-filter'
    );

    let isSubmitting = false;

    automaticFilters.forEach((filter) => {
        filter.addEventListener('change', () => {
            if (isSubmitting) return;

            isSubmitting = true;
            filterForm.requestSubmit();
        });
    });

    filterForm.addEventListener('submit', () => {
        isSubmitting = true;
    });
});