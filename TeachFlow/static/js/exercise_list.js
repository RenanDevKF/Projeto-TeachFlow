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

    function setupMultipleFilter({
        triggerId,
        dropdownId,
        searchId,
    }) {
        const trigger = document.getElementById(triggerId);
        const dropdown = document.getElementById(dropdownId);
        const search = document.getElementById(searchId);

        if (!trigger || !dropdown) {
            return;
        }

        const arrow = trigger.querySelector('[data-filter-arrow]');
        const checkboxes = dropdown.querySelectorAll(
            '[data-exercise-multiple-filter]'
        );
        const items = dropdown.querySelectorAll(
            '[data-multiple-filter-item]'
        );

        function closeDropdown() {
            dropdown.classList.add('hidden');
            trigger.setAttribute('aria-expanded', 'false');
            arrow?.classList.remove('rotate-180');
        }

        function openDropdown() {
            dropdown.classList.remove('hidden');
            trigger.setAttribute('aria-expanded', 'true');
            arrow?.classList.add('rotate-180');

            window.setTimeout(() => {
                search?.focus();
            }, 0);
        }

        trigger.addEventListener('click', () => {
            if (dropdown.classList.contains('hidden')) {
                openDropdown();
            } else {
                closeDropdown();
            }
        });

        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener('change', () => {
                filterForm.requestSubmit();
            });
        });

        search?.addEventListener('input', () => {
            const query = search.value.trim().toLowerCase();

            items.forEach((item) => {
                const text = item.textContent.toLowerCase();

                item.classList.toggle(
                    'hidden',
                    !text.includes(query)
                );
            });
        });

        document.addEventListener('click', (event) => {
            if (
                !trigger.contains(event.target) &&
                !dropdown.contains(event.target)
            ) {
                closeDropdown();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeDropdown();
            }
        });
    }

    setupMultipleFilter({
        triggerId: 'exercise-tag-filter-trigger',
        dropdownId: 'exercise-tag-filter-dropdown',
        searchId: 'exercise-tag-filter-search',
    });

    setupMultipleFilter({
        triggerId: 'exercise-objective-filter-trigger',
        dropdownId: 'exercise-objective-filter-dropdown',
        searchId: 'exercise-objective-filter-search',
    });    
});