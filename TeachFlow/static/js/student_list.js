document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('student-filter-form');
    const searchInput = document.getElementById('student-search-input');

    if (!form || !searchInput) {
        return;
    }

    const shouldRestoreFocus = sessionStorage.getItem('studentSearchActive') === 'true';

    if (shouldRestoreFocus) {
        searchInput.focus();

        const textLength = searchInput.value.length;
        searchInput.setSelectionRange(textLength, textLength);

        sessionStorage.removeItem('studentSearchActive');
    }

    let timeoutId;

    searchInput.addEventListener('input', () => {
        clearTimeout(timeoutId);

        timeoutId = setTimeout(() => {
            sessionStorage.setItem('studentSearchActive', 'true');
            form.requestSubmit();
        }, 200);
    });
});