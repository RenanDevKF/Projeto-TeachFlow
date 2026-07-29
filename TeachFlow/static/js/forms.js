/**
 * Gerenciador de Seletores Múltiplos
 * Script unificado para formulários de exercícios e aulas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configurações disponíveis no formulário
    const formConfigs = {
        // Configuração para Objetivos de Aprendizagem (do formulário de exercício)
        objectives: {
            triggerId: 'objective-trigger',
            dropdownId: 'objective-dropdown',
            filterId: 'objective-filter',
            listId: 'objective-list',
            selectedContainerId: 'selected-objectives',
            selectId: 'id_objectives',
            dropdownArrowId: 'objective-dropdown-arrow',
            placeholderId: 'objectives-placeholder',
            dataAttributePrefix: 'objective',
            placeholderText: 'Clique para selecionar objetivos',
            // Propriedade especial para tratar descrições de objetivos
            useDescription: true
        },
        
        // Configuração para Exercícios (do formulário de aula)
        exercises: {
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
        },
        
        // Configuração para Tags (comum a ambos formulários)
        tags: {
            triggerId: 'tag-trigger',
            dropdownId: 'tag-dropdown',
            filterId: 'tag-filter',
            listId: 'tag-list',
            selectedContainerId: 'selected-tags',
            selectId: 'id_tags',
            dropdownArrowId: 'tag-dropdown-arrow',
            placeholderId: 'tags-placeholder',
            dataAttributePrefix: 'tag',
            placeholderText: 'Clique para selecionar tags',
            // Propriedade especial para tratar cores de tags
            useCustomColors: true
        }
    };

    // Inicializa todos os seletores configurados que existem na página atual
    Object.values(formConfigs).forEach(config => {
        // Verifica se o seletor existe na página atual
        if (document.getElementById(config.selectId)) {
            setupMultiSelector(config);
        }
    });

    /**
     * Configura um seletor múltiplo baseado na configuração passada
     * @param {Object} config - Configuração do seletor
     */
    function setupMultiSelector(config) {
        // Elementos do DOM
        const trigger = document.getElementById(config.triggerId);
        const dropdown = document.getElementById(config.dropdownId);
        const filter = document.getElementById(config.filterId);
        const list = document.getElementById(config.listId) || document.querySelector(`#${config.dropdownId} .dropdown-list`);
        const selectedContainer = document.getElementById(config.selectedContainerId);
        const select = document.getElementById(config.selectId);
        const dropdownArrow = document.getElementById(config.dropdownArrowId);
        const placeholder = document.getElementById(config.placeholderId);

        // Verificação de elementos críticos
        if (!select) {
            console.error(`Elemento ${config.selectId} não encontrado! O formulário não está renderizando o campo corretamente.`);
            return;
        }

        if (!trigger || !dropdown) {
            console.error(`Elementos de interface para ${config.selectId} não encontrados!`);
            return;
        }

        // Variável para controlar o estado do dropdown
        let isDropdownOpen = false;

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

        // 1. Suporte a teclado
        trigger.addEventListener('keydown', (e) => {
            if (['Enter', ' ', 'ArrowDown', 'ArrowUp'].includes(e.key)) {
                e.preventDefault();
                if (!isDropdownOpen) openDropdown();
                
                // Navegação com setas (melhoria extra)
                if (e.key === 'ArrowDown' && isDropdownOpen) {
                    const firstItem = dropdown.querySelector('input:not([disabled])');
                    firstItem?.focus();
                }
            }
        });

        // 2. Fechar com Escape
        dropdown.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeDropdown();
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
            if (dropdownArrow) dropdownArrow.classList.add('rotate-180');
            if (filter) filter.focus();
            isDropdownOpen = true;
        }

        // Função para fechar o dropdown
        function closeDropdown() {
            dropdown.classList.add('hidden');
            if (dropdownArrow) dropdownArrow.classList.remove('rotate-180');
            isDropdownOpen = false;
        }

        // Função para filtrar itens no dropdown
        function filterItems() {
            const filterText = filter.value.toLowerCase();
            const items = list.querySelectorAll('label');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const parent = item.closest('label') || item;
                
                if (text.includes(filterText)) {
                    parent.style.display = 'flex';
                } else {
                    parent.style.display = 'none';
                }
            });
        }

        // Função para obter o texto a ser exibido para um item selecionado
        function getItemDisplayText(option, checkbox) {
            // Se é um objetivo e tem descrição, usa a descrição
            if (config.useDescription && checkbox && checkbox.getAttribute(`data-${config.dataAttributePrefix}-description`)) {
                return checkbox.getAttribute(`data-${config.dataAttributePrefix}-description`);
            }
            
            // Se é um exercício com título específico
            if (checkbox && checkbox.getAttribute(`data-${config.dataAttributePrefix}-title`)) {
                return checkbox.getAttribute(`data-${config.dataAttributePrefix}-title`);
            }
            
            // Se é uma tag com nome específico
            if (checkbox && checkbox.getAttribute(`data-${config.dataAttributePrefix}-name`)) {
                return checkbox.getAttribute(`data-${config.dataAttributePrefix}-name`);
            }
            
            // Padrão: usa o texto da opção
            return option.text;
        }

        // Função para obter a cor para um item (tag)
        function getItemColor(checkbox) {
            // Se tem cor personalizada definida e a configuração permite, usa a cor personalizada
            if (config.useCustomColors && checkbox && checkbox.getAttribute(`data-${config.dataAttributePrefix}-color`)) {
                return checkbox.getAttribute(`data-${config.dataAttributePrefix}-color`);
            }
            
            return null; // Sem cor personalizada
        }

        // Função para atualizar os itens selecionados
        function updateSelectedItems() {
            selectedContainer.innerHTML = '';
            const selectedOptions = Array.from(select.selectedOptions);
            
            if (selectedOptions.length === 0) {
                if (placeholder) {
                    placeholder.textContent = config.placeholderText;
                    placeholder.classList.remove('hidden');
                    selectedContainer.appendChild(placeholder);
                }
                return;
            } else if (placeholder) {
                placeholder.classList.add('hidden');
            }
            
            selectedOptions.forEach((option, index) => {
                const itemId = option.value;
                const dataAttr = `data-${config.dataAttributePrefix}-select`;
                const checkbox = document.querySelector(`[${dataAttr}][value="${itemId}"]`);
                
                // Verifica se deve usar cor personalizada
                const customColor = getItemColor(checkbox);
                
                // Cria o elemento de exibição
                const itemElement = document.createElement('span');
                
                if (customColor) {
                    // Estilo para tags com cores personalizadas
                    itemElement.className = 'px-2 py-1 text-xs rounded-full flex items-center mr-2 mb-1';
                    itemElement.style.backgroundColor = `${customColor}20`;
                    itemElement.style.color = customColor;
                } else {
                    // Estilo com cor alternada para outros itens
                    const colorClass = colors[index % colors.length];
                    itemElement.className = `${colorClass} px-2 py-1 text-xs rounded-full flex items-center mr-2 mb-1`;
                }
                
                // Texto do item
                const displayText = getItemDisplayText(option, checkbox);
                
                // Conteúdo HTML do item
                itemElement.innerHTML = `
                    <span>${displayText}</span>
                    <button type="button" 
                            class="ml-1.5 text-current hover:text-red-600 hover:scale-110 transition-all focus:outline-none"
                            data-remove-${config.dataAttributePrefix}="${itemId}"
                            aria-label="Remover ${displayText}">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
                
                selectedContainer.appendChild(itemElement);
            });
        }

        // Função para sincronizar os checkboxes com o select oculto
        function syncCheckboxesWithSelect() {
            const dataAttr = `data-${config.dataAttributePrefix}-select`;
            const checkboxes = document.querySelectorAll(`[${dataAttr}]`);
            const selectedValues = Array.from(select.selectedOptions).map(opt => opt.value);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectedValues.includes(checkbox.value);
            });
        }

        // Event listeners
        
        // 1. Abrir/fechar dropdown ao clicar no trigger
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown();
        });

        // 2. Fechar dropdown ao clicar fora
        document.addEventListener('click', function(e) {
            if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        // 3. Filtrar itens ao digitar
        if (filter) {
            filter.addEventListener('input', filterItems);
        }

        // 4. Adicionar/remover ao marcar/desmarcar checkboxes
        if (list) {
            list.addEventListener('change', (e) => {
                const dataAttr = `data-${config.dataAttributePrefix}-select`;
                const checkbox = e.target.closest(`[${dataAttr}]`);
                
                if (checkbox) {
                    const itemId = checkbox.value;
                    const displayText = checkbox.getAttribute(`data-${config.dataAttributePrefix}-${config.dataAttributePrefix === 'objective' ? 'description' : 'title'}`) || 
                                      checkbox.nextElementSibling?.textContent.trim();
        
                    const option = Array.from(select.options).find(opt => opt.value === itemId);
                    
                    if (checkbox.checked) {
                        if (!option) {
                            const newOption = new Option(displayText, itemId, true, true);
                            select.add(newOption);
                        } else {
                            option.selected = true;
                        }
                    } else {
                        if (option) option.selected = false;
                    }
                    
                    updateSelectedItems();
                }
            });
        }

        // 5. Remover item ao clicar no X
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