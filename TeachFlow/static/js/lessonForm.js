document.addEventListener('DOMContentLoaded', function() {
    // Configuração para Exercícios
    setupMultiSelector({
        triggerId: 'exercise-trigger',
        dropdownId: 'exercise-dropdown',
        filterId: 'exercise-filter',
        listId: 'exercise-list',
        selectedContainerId: 'selected-exercises',
        selectId: 'id_exercises',
        dropdownArrowId: 'dropdown-arrow',
        placeholderId: 'exercises-placeholder',
        dataAttributePrefix: 'exercise',
        placeholderText: 'Clique para selecionar exercícios'
    });

    // Configuração para Tags
    setupMultiSelector({
        triggerId: 'tag-trigger',
        dropdownId: 'tag-dropdown',
        filterId: 'tag-filter',
        listId: 'tag-list',
        selectedContainerId: 'selected-tags',
        selectId: 'id_tags',
        dropdownArrowId: 'tag-dropdown-arrow',
        placeholderId: 'tags-placeholder',
        dataAttributePrefix: 'tag',
        placeholderText: 'Clique para selecionar tags'
    });

    // Função reutilizável para configurar os seletores múltiplos
    function setupMultiSelector(config) {
        // Elementos do DOM
        const trigger = document.getElementById(config.triggerId);
        const dropdown = document.getElementById(config.dropdownId);
        const filter = document.getElementById(config.filterId);
        const list = document.getElementById(config.listId);
        const selectedContainer = document.getElementById(config.selectedContainerId);
        const select = document.getElementById(config.selectId);
        const dropdownArrow = document.getElementById(config.dropdownArrowId);
        const placeholder = document.getElementById(config.placeholderId);

        // Verificação de elementos críticos
        if (!select) {
            console.error(`Elemento ${config.selectId} não encontrado! O formulário Django não está renderizando o campo corretamente.`);
            return;
        }

        // Variável para controlar o estado do dropdown
        let isDropdownOpen = false;

        // Abre/fecha o dropdown
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown();
        });

        // Função para alternar o dropdown
        function toggleDropdown() {
            if (isDropdownOpen) {
                closeDropdown();
            } else {
                openDropdown();
            }
        }

        // Função para abrir o dropdown
        function openDropdown() {
            dropdown.classList.remove('hidden');
            dropdownArrow.classList.add('rotate-180');
            filter.focus();
            isDropdownOpen = true;
        }

        // Função para fechar o dropdown
        function closeDropdown() {
            dropdown.classList.add('hidden');
            dropdownArrow.classList.remove('rotate-180');
            isDropdownOpen = false;
        }

        // Fecha o dropdown ao clicar fora
        document.addEventListener('click', function(e) {
            if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        // Filtra itens
        filter.addEventListener('input', function() {
            const filterText = this.value.toLowerCase();
            const items = list.querySelectorAll('label');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(filterText) ? 'flex' : 'none';
            });
        });

        // Cores para as tags (alternância entre várias cores)
        const colors = [
            'bg-blue-100 text-blue-800 border border-blue-200',
            'bg-green-100 text-green-800 border border-green-200',
            'bg-yellow-100 text-yellow-800 border border-yellow-200',
            'bg-purple-100 text-purple-800 border border-purple-200',
            'bg-pink-100 text-pink-800 border border-pink-200',
            'bg-indigo-100 text-indigo-800 border border-indigo-200',
            'bg-red-100 text-red-800 border border-red-200',
            'bg-emerald-100 text-emerald-800 border border-emerald-200',
            'bg-amber-100 text-amber-800 border border-amber-200',
            'bg-cyan-100 text-cyan-800 border border-cyan-200'
        ];

        // Atualiza itens selecionados
        function updateSelectedItems() {
            selectedContainer.innerHTML = '';
            const selectedOptions = Array.from(select.selectedOptions);
            
            // Mostra/esconde o placeholder conforme seleção
            if (selectedOptions.length === 0) {
                placeholder.textContent = config.placeholderText;
                placeholder.classList.remove('hidden');
                return;
            } else {
                placeholder.classList.add('hidden');
            }
            
            // Cria tags para cada item selecionado
            selectedOptions.forEach((option, index) => {
                const colorClass = colors[index % colors.length];
                
                const tag = document.createElement('div');
                tag.className = `${colorClass} px-3 py-1 rounded-full text-sm font-medium flex items-center shadow-sm`;
                tag.innerHTML = `
                    <span>${option.text}</span>
                    <button type="button" 
                            class="ml-1.5 text-current hover:text-red-600 hover:scale-125 transition-all focus:outline-none"
                            data-remove-${config.dataAttributePrefix}="${option.value}"
                            aria-label="Remover ${config.dataAttributePrefix}">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
                selectedContainer.appendChild(tag);
            });
        }

        // Sincroniza checkboxes com o select oculto
        function syncCheckboxesWithSelect() {
            const dataAttr = `data-${config.dataAttributePrefix}-select`;
            const checkboxes = document.querySelectorAll(`[${dataAttr}]`);
            const selectedValues = Array.from(select.selectedOptions).map(opt => opt.value);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectedValues.includes(checkbox.value);
            });
        }

        // Adiciona/remove itens
        list.addEventListener('change', function(e) {
            const dataAttr = `data-${config.dataAttributePrefix}-select`;
            if (e.target.matches(`[${dataAttr}]`)) {
                const checkbox = e.target;
                const itemId = checkbox.value;
                const itemTitle = checkbox.getAttribute(`data-${config.dataAttributePrefix}-${config.dataAttributePrefix === 'exercise' ? 'title' : 'name'}`);
                const option = Array.from(select.options).find(opt => opt.value === itemId);
                
                if (checkbox.checked) {
                    // Adiciona ao select se não existir
                    if (!option) {
                        const newOption = new Option(itemTitle, itemId, true, true);
                        select.add(newOption);
                    } else {
                        option.selected = true;
                    }
                } else {
                    // Remove do select
                    if (option) {
                        option.selected = false;
                    }
                }
                
                updateSelectedItems();
            }
        });

        // Remove item ao clicar no X
        selectedContainer.addEventListener('click', function(e) {
            const removeButton = e.target.closest(`[data-remove-${config.dataAttributePrefix}]`);
            if (removeButton) {
                e.stopPropagation();
                const itemId = removeButton.getAttribute(`data-remove-${config.dataAttributePrefix}`);
                
                // Desmarca o checkbox na lista
                const dataAttr = `data-${config.dataAttributePrefix}-select`;
                const checkbox = document.querySelector(`[${dataAttr}][value="${itemId}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                }
                
                // Remove a seleção no select oculto
                const option = Array.from(select.options).find(opt => opt.value === itemId);
                if (option) {
                    option.selected = false;
                }
                
                updateSelectedItems();
            }
        });

        // Inicialização
        updateSelectedItems();
        syncCheckboxesWithSelect();
    }
});