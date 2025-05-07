// Gerenciamento do dropdown de objetivos
document.addEventListener('DOMContentLoaded', function() {
    // Elementos de Objetivos de Aprendizagem
    const objectiveTrigger = document.getElementById('objective-trigger');
    const objectiveDropdown = document.getElementById('objective-dropdown');
    const objectiveFilter = document.getElementById('objective-filter');
    const objectiveCheckboxes = document.querySelectorAll('[data-objective-select]');
    const objectivesElement = document.getElementById('id_objectives');
    const selectedObjectives = document.getElementById('selected-objectives');
    const objectivesPlaceholder = document.getElementById('objectives-placeholder');
    const objectiveDropdownArrow = document.getElementById('objective-dropdown-arrow');

    // Elementos de Tags
    const tagTrigger = document.getElementById('tag-trigger');
    const tagDropdown = document.getElementById('tag-dropdown');
    const tagFilter = document.getElementById('tag-filter');
    const tagCheckboxes = document.querySelectorAll('[data-tag-select]');
    const tagsElement = document.getElementById('id_tags');
    const selectedTags = document.getElementById('selected-tags');
    const tagsPlaceholder = document.getElementById('tags-placeholder');
    const tagDropdownArrow = document.getElementById('tag-dropdown-arrow');

    // Funções auxiliares
    function toggleDropdown(trigger, dropdown, arrow) {
        dropdown.classList.toggle('hidden');
        // Rotacionar a seta quando o dropdown está aberto
        if (!dropdown.classList.contains('hidden')) {
            arrow.classList.add('rotate-180');
        } else {
            arrow.classList.remove('rotate-180');
        }
    }

    function filterItems(filter, items) {
        const query = filter.value.toLowerCase();
        items.forEach(item => {
            const label = item.nextElementSibling;
            const text = label.textContent.toLowerCase();
            const parent = item.closest('label');
            
            if (text.includes(query)) {
                parent.classList.remove('hidden');
            } else {
                parent.classList.add('hidden');
            }
        });
    }

    function updateSelectedItems(checkboxes, selectedContainer, placeholder, hiddenInput) {
        const selectedItems = [];
        selectedContainer.innerHTML = '';
        
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                // Para objetivos
                if (checkbox.hasAttribute('data-objective-description')) {
                    const description = checkbox.getAttribute('data-objective-description');
                    const span = document.createElement('span');
                    span.className = 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700';
                    span.textContent = description;
                    selectedContainer.appendChild(span);
                    selectedItems.push(checkbox.value);
                }
                // Para tags
                else if (checkbox.hasAttribute('data-tag-name') && checkbox.hasAttribute('data-tag-color')) {
                    const name = checkbox.getAttribute('data-tag-name');
                    const color = checkbox.getAttribute('data-tag-color');
                    const span = document.createElement('span');
                    span.className = 'px-2 py-1 text-xs rounded-full';
                    span.style.backgroundColor = color + '20';  // Adiciona transparência
                    span.style.color = color;
                    span.textContent = name;
                    selectedContainer.appendChild(span);
                    selectedItems.push(checkbox.value);
                }
            }
        });
        
        // Mostrar placeholder se nenhum item for selecionado
        if (selectedItems.length === 0) {
            placeholder.style.display = 'block';
            selectedContainer.appendChild(placeholder);
        } else {
            placeholder.style.display = 'none';
        }
        
        // Atualizar o campo oculto com os valores selecionados
        Array.from(hiddenInput.options).forEach(option => {
            option.selected = selectedItems.includes(option.value);
        });
    }

    // Event listeners para Objetivos
    if (objectiveTrigger) {
        objectiveTrigger.addEventListener('click', () => {
            toggleDropdown(objectiveTrigger, objectiveDropdown, objectiveDropdownArrow);
        });

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {
            if (!objectiveTrigger.contains(e.target) && !objectiveDropdown.contains(e.target)) {
                objectiveDropdown.classList.add('hidden');
                objectiveDropdownArrow.classList.remove('rotate-180');
            }
        });

        // Filtrar objetivos
        if (objectiveFilter) {
            objectiveFilter.addEventListener('input', () => {
                filterItems(objectiveFilter, objectiveCheckboxes);
            });
        }

        // Lidar com a seleção de objetivos
        objectiveCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateSelectedItems(objectiveCheckboxes, selectedObjectives, objectivesPlaceholder, objectivesElement);
            });
        });

        // Inicializar o estado dos objetivos selecionados
        updateSelectedItems(objectiveCheckboxes, selectedObjectives, objectivesPlaceholder, objectivesElement);
    }

    // Event listeners para Tags
    if (tagTrigger) {
        tagTrigger.addEventListener('click', () => {
            toggleDropdown(tagTrigger, tagDropdown, tagDropdownArrow);
        });

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {
            if (!tagTrigger.contains(e.target) && !tagDropdown.contains(e.target)) {
                tagDropdown.classList.add('hidden');
                tagDropdownArrow.classList.remove('rotate-180');
            }
        });

        // Filtrar tags
        if (tagFilter) {
            tagFilter.addEventListener('input', () => {
                filterItems(tagFilter, tagCheckboxes);
            });
        }

        // Lidar com a seleção de tags
        tagCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateSelectedItems(tagCheckboxes, selectedTags, tagsPlaceholder, tagsElement);
            });
        });

        // Inicializar o estado das tags selecionadas
        updateSelectedItems(tagCheckboxes, selectedTags, tagsPlaceholder, tagsElement);
    }
});