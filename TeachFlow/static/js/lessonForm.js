document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const exerciseTrigger = document.getElementById('exercise-trigger');
    const exerciseDropdown = document.getElementById('exercise-dropdown');
    const exerciseFilter = document.getElementById('exercise-filter');
    const exerciseList = document.getElementById('exercise-list');
    const selectedExercises = document.getElementById('selected-exercises');
    const exercisesSelect = document.getElementById('id_exercises');
    const dropdownArrow = document.getElementById('dropdown-arrow');

    // Verificação de elementos críticos
    if (!exercisesSelect) {
        console.error('Elemento id_exercises não encontrado! O formulário Django não está renderizando o campo exercises.');
        return;
    }

    // Variável para controlar o estado do dropdown
    let isDropdownOpen = false;

    // Abre/fecha o dropdown
    exerciseTrigger.addEventListener('click', function(e) {
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
        exerciseDropdown.classList.remove('hidden');
        dropdownArrow.classList.add('rotate-180');
        exerciseFilter.focus();
        isDropdownOpen = true;
    }

    // Função para fechar o dropdown
    function closeDropdown() {
        exerciseDropdown.classList.add('hidden');
        dropdownArrow.classList.remove('rotate-180');
        isDropdownOpen = false;
    }

    // Fecha o dropdown ao clicar fora
    document.addEventListener('click', function(e) {
        if (!exerciseTrigger.contains(e.target) && !exerciseDropdown.contains(e.target)) {
            closeDropdown();
        }
    });

    // Filtra exercícios
    exerciseFilter.addEventListener('input', function() {
        const filter = this.value.toLowerCase();
        const items = exerciseList.querySelectorAll('label');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filter) ? 'flex' : 'none';
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

    // Atualiza exercícios selecionados
    function updateSelectedExercises() {
        selectedExercises.innerHTML = '';
        const selectedOptions = Array.from(exercisesSelect.selectedOptions);
        
        // Esconde o container de tags selecionadas se não houver nenhuma
        if (selectedOptions.length === 0) {
            selectedExercises.classList.add('hidden');
            exerciseTrigger.querySelector('span').textContent = 'Clique para selecionar exercícios';
            return;
        }
        
        // Mostra o container e atualiza o texto do trigger
        selectedExercises.classList.remove('hidden');
        exerciseTrigger.querySelector('span').textContent = `${selectedOptions.length} exercício(s) selecionado(s)`;
        
        // Cria tags para cada exercício selecionado
        selectedOptions.forEach((option, index) => {
            const colorClass = colors[index % colors.length];
            
            const tag = document.createElement('div');
            tag.className = `${colorClass} px-3 py-1 rounded-full text-sm font-medium flex items-center shadow-sm`;
            tag.innerHTML = `
                <span>${option.text}</span>
                <button type="button" 
                        class="ml-1.5 text-current hover:text-red-600 hover:scale-125 transition-all focus:outline-none"
                        data-remove-exercise="${option.value}"
                        aria-label="Remover exercício">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            `;
            selectedExercises.appendChild(tag);
        });
    }

    // Sincroniza checkboxes com o select oculto
    function syncCheckboxesWithSelect() {
        const checkboxes = document.querySelectorAll('[data-exercise-select]');
        const selectedValues = Array.from(exercisesSelect.selectedOptions).map(opt => opt.value);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectedValues.includes(checkbox.value);
        });
    }

    // Adiciona/remove exercícios
    document.addEventListener('change', function(e) {
        if (e.target.matches('[data-exercise-select]')) {
            const checkbox = e.target;
            const exerciseId = checkbox.value;
            const exerciseTitle = checkbox.getAttribute('data-exercise-title');
            const option = Array.from(exercisesSelect.options).find(opt => opt.value === exerciseId);
            
            if (checkbox.checked) {
                // Adiciona ao select se não existir
                if (!option) {
                    const newOption = new Option(exerciseTitle, exerciseId, true, true);
                    exercisesSelect.add(newOption);
                } else {
                    option.selected = true;
                }
            } else {
                // Remove do select
                if (option) {
                    option.selected = false;
                }
            }
            
            updateSelectedExercises();
        }
    });

    // Remove exercício ao clicar no X
    selectedExercises.addEventListener('click', function(e) {
        const removeButton = e.target.closest('[data-remove-exercise]');
        if (removeButton) {
            e.stopPropagation();
            const exerciseId = removeButton.getAttribute('data-remove-exercise');
            
            // Desmarca o checkbox na lista
            const checkbox = document.querySelector(`[data-exercise-select][value="${exerciseId}"]`);
            if (checkbox) {
                checkbox.checked = false;
            }
            
            // Remove a seleção no select oculto
            const option = Array.from(exercisesSelect.options).find(opt => opt.value === exerciseId);
            if (option) {
                option.selected = false;
            }
            
            updateSelectedExercises();
        }
    });

    // Inicialização
    updateSelectedExercises();
    syncCheckboxesWithSelect();
});
