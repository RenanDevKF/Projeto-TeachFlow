document.addEventListener('DOMContentLoaded', function() {
    // Elementos do dropdown genérico
    const dropdownButton = document.getElementById('filter-dropdown-button');
    const dropdownContent = document.getElementById('filter-dropdown-content');
    const dropdownArrow = document.getElementById('filter-arrow');

    // Lógica do dropdown (funciona para qualquer página)
    if (dropdownButton && dropdownContent) {
        dropdownButton.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = dropdownContent.classList.toggle('hidden');
            if (dropdownArrow) {
                dropdownArrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
            }
        });

        document.addEventListener('click', function() {
            dropdownContent.classList.add('hidden');
            if (dropdownArrow) {
                dropdownArrow.style.transform = 'rotate(0deg)';
            }
        });

        dropdownContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Função genérica para aplicar filtros
    function applyFilters() {
        const form = document.querySelector('#filter-dropdown-content form');
        if (!form) return;
        
        const formData = new FormData(form);
        const params = new URLSearchParams();
        
        formData.forEach((value, key) => {
            if (value) params.append(key, value);
        });
        
        window.location.href = window.location.pathname + '?' + params.toString();
    }
    
    // Função para resetar filtros
    function resetFilters() {
        window.location.href = window.location.pathname;
    }
    
    // Event listeners genéricos
    document.getElementById('apply-filters')?.addEventListener('click', applyFilters);
    document.getElementById('reset-filters')?.addEventListener('click', resetFilters);
    
    // Aplicar filtros com Enter em qualquer input dentro do form
    const filterInputs = document.querySelectorAll('#filter-dropdown-content input, #filter-dropdown-content select');
    filterInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    });
});