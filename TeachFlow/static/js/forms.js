document.addEventListener('DOMContentLoaded', () => {
    const selectorConfigs = {
        objectives: {
            type: 'objectives',
            triggerId: 'objective-trigger',
            dropdownId: 'objective-dropdown',
            filterId: 'objective-filter',
            listId: 'objective-list',
            selectedContainerId: 'selected-objectives',
            selectId: 'id_objectives',
            arrowId: 'objective-dropdown-arrow',
            placeholderId: 'objectives-placeholder',
            placeholderText: 'Clique para selecionar objetivos',
            checkboxAttribute: 'data-objective-select',
            removeAttribute: 'data-remove-objective',
            labelAttribute: 'data-objective-title',
            fallbackLabelAttribute: 'data-objective-description',
            descriptionAttribute: 'data-objective-description',
            emptyIcon: 'target',
            emptyText: 'Nenhum objetivo cadastrado.',
            badgeClasses: 'border border-blue-200 bg-blue-50 text-blue-700',
        },
        exercises: {
            type: 'exercises',
            triggerId: 'exercise-trigger',
            dropdownId: 'exercise-dropdown',
            filterId: 'exercise-filter',
            listId: 'exercise-list',
            selectedContainerId: 'selected-exercises',
            selectId: 'id_exercises',
            arrowId: 'dropdown-arrow',
            placeholderId: 'exercises-placeholder',
            placeholderText: 'Clique para selecionar exercícios',
            checkboxAttribute: 'data-exercise-select',
            removeAttribute: 'data-remove-exercise',
            labelAttribute: 'data-exercise-title',
            emptyIcon: 'clipboard-list',
            emptyText: 'Nenhum exercício cadastrado.',
            badgeClasses: 'border border-green-200 bg-green-50 text-green-700',
        },
        tags: {
            type: 'tags',
            triggerId: 'tag-trigger',
            dropdownId: 'tag-dropdown',
            filterId: 'tag-filter',
            listId: 'tag-list',
            selectedContainerId: 'selected-tags',
            selectId: 'id_tags',
            arrowId: 'tag-dropdown-arrow',
            placeholderId: 'tags-placeholder',
            placeholderText: 'Clique para selecionar tags',
            checkboxAttribute: 'data-tag-select',
            removeAttribute: 'data-remove-tag',
            labelAttribute: 'data-tag-name',
            colorAttribute: 'data-tag-color',
            emptyIcon: 'tags',
            emptyText: 'Nenhuma tag cadastrada.',
        },
    };

    const managers = {};

    Object.entries(selectorConfigs).forEach(([type, config]) => {
        const select = document.getElementById(config.selectId);
        if (!select) return;

        const manager = createMultiSelector(config);
        if (manager) managers[type] = manager;
    });

    window.multiSelectorManager = {
        addItem(type, item) {
            const manager = managers[type];

            if (!manager) {
                console.error(`Seletor múltiplo "${type}" não encontrado.`);
                return false;
            }

            return manager.addItem(item);
        },

        selectItem(type, itemId) {
            const manager = managers[type];
            if (!manager) return false;

            return manager.selectItem(String(itemId));
        },

        removeItem(type, itemId) {
            const manager = managers[type];
            if (!manager) return false;

            return manager.removeItem(String(itemId));
        },

        refresh(type) {
            const manager = managers[type];
            if (!manager) return false;

            manager.refresh();
            return true;
        },

        hasSelector(type) {
            return Boolean(managers[type]);
        },
    };

    function createMultiSelector(config) {
        const trigger = document.getElementById(config.triggerId);
        const dropdown = document.getElementById(config.dropdownId);
        const filter = document.getElementById(config.filterId);
        const list = document.getElementById(config.listId);
        const selectedContainer = document.getElementById(config.selectedContainerId);
        const select = document.getElementById(config.selectId);
        const arrow = document.getElementById(config.arrowId);

        if (!trigger || !dropdown || !list || !selectedContainer || !select) {
            console.error(`Estrutura incompleta do seletor ${config.selectId}.`);
            return null;
        }

        let isOpen = false;

        trigger.addEventListener('click', (event) => {
            event.stopPropagation();
            toggleDropdown();
        });

        trigger.addEventListener('keydown', (event) => {
            if (!['Enter', ' ', 'ArrowDown', 'ArrowUp'].includes(event.key)) return;

            event.preventDefault();

            if (!isOpen) openDropdown();

            if (event.key === 'ArrowDown') {
                list.querySelector(`[${config.checkboxAttribute}]:not(:disabled)`)?.focus();
            }
        });

        dropdown.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;

            closeDropdown();
            trigger.focus();
        });

        document.addEventListener('click', (event) => {
            if (!trigger.contains(event.target) && !dropdown.contains(event.target)) closeDropdown();
        });

        filter?.addEventListener('input', () => filterItems(filter.value));

        list.addEventListener('change', (event) => {
            const checkbox = event.target.closest(`[${config.checkboxAttribute}]`);
            if (!checkbox) return;

            setSelectedState(checkbox.value, checkbox.checked);
            renderSelectedItems();
        });

        selectedContainer.addEventListener('click', (event) => {
            const removeButton = event.target.closest(`[${config.removeAttribute}]`);
            if (!removeButton) return;

            event.stopPropagation();

            const itemId = removeButton.getAttribute(config.removeAttribute);
            setSelectedState(itemId, false);
            renderSelectedItems();
        });

        refresh();

        return {
            addItem,
            selectItem,
            removeItem,
            refresh,
        };

        function toggleDropdown() {
            isOpen ? closeDropdown() : openDropdown();
        }

        function openDropdown() {
            dropdown.classList.remove('hidden');
            arrow?.classList.add('rotate-180');
            trigger.setAttribute('aria-expanded', 'true');
            isOpen = true;
            filter?.focus();
        }

        function closeDropdown() {
            dropdown.classList.add('hidden');
            arrow?.classList.remove('rotate-180');
            trigger.setAttribute('aria-expanded', 'false');
            isOpen = false;
        }

        function filterItems(searchTerm) {
            const normalizedTerm = normalizeText(searchTerm);

            list.querySelectorAll('[data-selector-item]').forEach((item) => {
                const searchableText = normalizeText(item.textContent);
                item.classList.toggle('hidden', !searchableText.includes(normalizedTerm));
            });
        }

        function normalizeText(value) {
            return String(value || '')
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .toLowerCase()
                .trim();
        }

        function getOption(itemId) {
            return Array.from(select.options).find((option) => option.value === String(itemId));
        }

        function getCheckbox(itemId) {
            return list.querySelector(`[${config.checkboxAttribute}][value="${CSS.escape(String(itemId))}"]`);
        }

        function getLabel(itemId) {
            const option = getOption(itemId);
            const checkbox = getCheckbox(itemId);

            return checkbox?.getAttribute(config.labelAttribute)
                || checkbox?.getAttribute(config.fallbackLabelAttribute)
                || option?.textContent.trim()
                || '';
        }

        function getDescription(itemId) {
            return getCheckbox(itemId)?.getAttribute(config.descriptionAttribute) || '';
        }

        function getColor(itemId) {
            return getCheckbox(itemId)?.getAttribute(config.colorAttribute) || '';
        }

        function setSelectedState(itemId, selected) {
            const normalizedId = String(itemId);
            const option = getOption(normalizedId);
            const checkbox = getCheckbox(normalizedId);

            if (option) option.selected = selected;
            if (checkbox) checkbox.checked = selected;
        }

        function selectItem(itemId) {
            const option = getOption(itemId);
            if (!option) return false;

            setSelectedState(itemId, true);
            renderSelectedItems();
            return true;
        }

        function removeItem(itemId) {
            const option = getOption(itemId);
            const checkbox = getCheckbox(itemId);
            const item = checkbox?.closest('[data-selector-item]');

            if (!option && !checkbox) return false;

            option?.remove();
            item?.remove();

            renderSelectedItems();
            renderEmptyState();
            return true;
        }

        function addItem(item) {
            if (!item?.id) {
                console.error(`Item inválido recebido pelo seletor "${config.type}".`);
                return false;
            }

            const itemId = String(item.id);
            const existingOption = getOption(itemId);

            if (existingOption) {
                setSelectedState(itemId, item.selected !== false);
                renderSelectedItems();
                return true;
            }

            const label = String(item.label || item.title || item.name || '').trim();

            if (!label) {
                console.error(`Item sem texto recebido pelo seletor "${config.type}".`);
                return false;
            }

            const option = new Option(label, itemId, item.selected !== false, item.selected !== false);
            select.add(option);

            removeEmptyState();
            list.appendChild(createListItem({
                id: itemId,
                label,
                description: item.description || '',
                color: item.color || '',
                selected: item.selected !== false,
            }));

            renderSelectedItems();
            filterItems(filter?.value || '');

            return true;
        }

        function createListItem(item) {
            const labelElement = document.createElement('label');
            labelElement.dataset.selectorItem = '';
            labelElement.className = config.type === 'tags'
                ? 'flex cursor-pointer items-center gap-3 px-3 py-3 transition-colors hover:bg-gray-50'
                : 'flex cursor-pointer items-start gap-3 px-3 py-3 transition-colors hover:bg-gray-50';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item.id;
            checkbox.checked = item.selected;
            checkbox.setAttribute(config.checkboxAttribute, '');
            checkbox.setAttribute(config.labelAttribute, item.label);
            checkbox.className = config.type === 'objectives'
                ? 'mt-0.5 h-4 w-4 flex-shrink-0 rounded border-gray-300 text-primary focus:ring-primary'
                : 'h-4 w-4 flex-shrink-0 rounded border-gray-300 text-primary focus:ring-primary';

            if (config.descriptionAttribute) checkbox.setAttribute(config.descriptionAttribute, item.description);
            if (config.colorAttribute) checkbox.setAttribute(config.colorAttribute, item.color);

            labelElement.appendChild(checkbox);

            if (config.type === 'tags') {
                const colorDot = document.createElement('span');
                colorDot.className = 'h-2.5 w-2.5 flex-shrink-0 rounded-full';
                colorDot.style.backgroundColor = item.color;
                labelElement.appendChild(colorDot);

                const tagName = document.createElement('span');
                tagName.className = 'min-w-0 truncate text-sm text-gray-700';
                tagName.textContent = item.label;
                labelElement.appendChild(tagName);

                return labelElement;
            }

            const textContainer = document.createElement('span');
            textContainer.className = 'min-w-0';

            const title = document.createElement('span');
            title.className = 'block text-sm font-medium leading-5 text-gray-700';
            title.textContent = item.label;
            textContainer.appendChild(title);

            if (item.description) {
                const description = document.createElement('span');
                description.className = 'mt-1 block text-xs leading-5 text-gray-500';
                description.textContent = item.description;
                textContainer.appendChild(description);
            }

            labelElement.appendChild(textContainer);
            return labelElement;
        }

        function renderSelectedItems() {
            selectedContainer.replaceChildren();

            const selectedOptions = Array.from(select.selectedOptions);

            if (!selectedOptions.length) {
                selectedContainer.appendChild(createPlaceholder());
                return;
            }

            selectedOptions.forEach((option) => {
                const itemId = option.value;
                const badge = document.createElement('span');

                badge.className = config.type === 'tags'
                    ? 'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium'
                    : `inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${config.badgeClasses}`;

                if (config.type === 'tags') {
                    const color = getColor(itemId) || '#6B7280';
                    badge.style.backgroundColor = `${color}20`;
                    badge.style.color = color;
                }

                const text = document.createElement('span');
                text.textContent = getLabel(itemId);
                badge.appendChild(text);

                const removeButton = document.createElement('button');
                removeButton.type = 'button';
                removeButton.setAttribute(config.removeAttribute, itemId);
                removeButton.setAttribute('aria-label', `Remover ${getLabel(itemId)}`);
                removeButton.className = 'ml-1.5 inline-flex h-4 w-4 items-center justify-center rounded-full text-current transition-transform hover:scale-110 hover:text-red-600 focus:outline-none';

                const removeIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                removeIcon.setAttribute('viewBox', '0 0 24 24');
                removeIcon.setAttribute('fill', 'none');
                removeIcon.setAttribute('stroke', 'currentColor');
                removeIcon.setAttribute('class', 'h-3 w-3');

                const removePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                removePath.setAttribute('stroke-linecap', 'round');
                removePath.setAttribute('stroke-linejoin', 'round');
                removePath.setAttribute('stroke-width', '2');
                removePath.setAttribute('d', 'M6 18 18 6M6 6l12 12');

                removeIcon.appendChild(removePath);
                removeButton.appendChild(removeIcon);
                badge.appendChild(removeButton);
                selectedContainer.appendChild(badge);
            });
        }

        function createPlaceholder() {
            const placeholder = document.createElement('span');
            placeholder.id = config.placeholderId;
            placeholder.className = 'text-gray-500';
            placeholder.textContent = config.placeholderText;

            return placeholder;
        }

        function renderEmptyState() {
            if (list.querySelector('[data-selector-item]')) {
                removeEmptyState();
                return;
            }

            if (list.querySelector('[data-selector-empty]')) return;

            const emptyState = document.createElement('div');
            emptyState.dataset.selectorEmpty = '';
            emptyState.className = 'px-4 py-6 text-center';

            const text = document.createElement('p');
            text.className = 'text-sm text-gray-500';
            text.textContent = config.emptyText;

            emptyState.appendChild(text);
            list.appendChild(emptyState);
        }

        function removeEmptyState() {
            list.querySelector('[data-selector-empty]')?.remove();

            list.querySelectorAll(':scope > div:not([data-selector-item])').forEach((element) => {
                if (element.querySelector('p')?.textContent.includes(config.emptyText)) element.remove();
            });
        }

        function syncCheckboxes() {
            const selectedValues = new Set(Array.from(select.selectedOptions).map((option) => option.value));

            list.querySelectorAll(`[${config.checkboxAttribute}]`).forEach((checkbox) => {
                checkbox.checked = selectedValues.has(checkbox.value);
            });
        }

        function prepareExistingItems() {
            list.querySelectorAll(`label:has([${config.checkboxAttribute}])`).forEach((labelElement) => {
                labelElement.dataset.selectorItem = '';

                const checkbox = labelElement.querySelector(`[${config.checkboxAttribute}]`);
                if (!checkbox) return;

                if (!checkbox.getAttribute(config.labelAttribute)) {
                    const option = getOption(checkbox.value);
                    checkbox.setAttribute(config.labelAttribute, option?.textContent.trim() || '');
                }
            });
        }

        function refresh() {
            prepareExistingItems();
            syncCheckboxes();
            renderSelectedItems();
            renderEmptyState();
        }
    }
});