document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('exercise-filter-form');
    const statusInput = document.getElementById('exercise-status-input');
    const typeInput = document.getElementById('exercise-type-input');
    const searchInput = document.getElementById('exercise-search-input');
    const durationSelect = document.getElementById(
        'exercise-duration-filter'
    );

    if (!filterForm) {
        return;
    }

    const statusButtons = Array.from(
        document.querySelectorAll('[data-exercise-status]')
    );

    const typeButtons = Array.from(
        document.querySelectorAll('[data-exercise-type]')
    );

    let searchTimeout = null;
    let isSubmitting = false;

    function submitFilters() {
        if (isSubmitting) {
            return;
        }

        isSubmitting = true;
        filterForm.requestSubmit();
    }

    statusButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!statusInput) {
                return;
            }

            const nextStatus = button.dataset.exerciseStatus;

            if (!nextStatus || statusInput.value === nextStatus) {
                return;
            }

            statusInput.value = nextStatus;
            submitFilters();
        });
    });

    typeButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!typeInput) {
                return;
            }

            const nextType = button.dataset.exerciseType;

            if (!nextType || typeInput.value === nextType) {
                return;
            }

            typeInput.value = nextType;
            submitFilters();
        });
    });

    durationSelect?.addEventListener('change', submitFilters);

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            window.clearTimeout(searchTimeout);

            searchTimeout = window.setTimeout(() => {
                submitFilters();
            }, 400);
        });

        const urlParameters = new URLSearchParams(
            window.location.search
        );

        if (urlParameters.has('search')) {
            searchInput.focus();

            const valueLength = searchInput.value.length;

            searchInput.setSelectionRange(
                valueLength,
                valueLength
            );
        }
    }

    const dropdownControllers = [];

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

        const checkboxes = Array.from(
            dropdown.querySelectorAll(
                '[data-exercise-multiple-filter]'
            )
        );

        const items = Array.from(
            dropdown.querySelectorAll(
                '[data-multiple-filter-item]'
            )
        );

        function closeDropdown() {
            dropdown.classList.add('hidden');
            trigger.setAttribute('aria-expanded', 'false');
            arrow?.classList.remove('rotate-180');

            if (search) {
                search.value = '';

                items.forEach((item) => {
                    item.classList.remove('hidden');
                });
            }
        }

        function openDropdown() {
            dropdownControllers.forEach((controller) => {
                if (controller.trigger !== trigger) {
                    controller.close();
                }
            });

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
                submitFilters();
            });
        });

        search?.addEventListener('input', () => {
            const query = search.value
                .trim()
                .toLocaleLowerCase('pt-BR');

            items.forEach((item) => {
                const text = item.textContent
                    .toLocaleLowerCase('pt-BR');

                item.classList.toggle(
                    'hidden',
                    !text.includes(query)
                );
            });
        });

        dropdownControllers.push({
            trigger,
            dropdown,
            close: closeDropdown,
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

    document.addEventListener('click', (event) => {
        dropdownControllers.forEach((controller) => {
            if (
                !controller.trigger.contains(event.target) &&
                !controller.dropdown.contains(event.target)
            ) {
                controller.close();
            }
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') {
            return;
        }

        dropdownControllers.forEach((controller) => {
            controller.close();
        });
    });
});