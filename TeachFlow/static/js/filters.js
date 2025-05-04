document.addEventListener('DOMContentLoaded', function() {
    // Elementos do dropdown
    const dropdownButton = document.getElementById('filter-dropdown-button');
    const dropdownContent = document.getElementById('filter-dropdown-content');
    const dropdownArrow = document.getElementById('filter-arrow');

    // Alternar dropdown
    dropdownButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const isOpen = dropdownContent.classList.toggle('hidden');
        dropdownArrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function() {
        dropdownContent.classList.add('hidden');
        dropdownArrow.style.transform = 'rotate(0deg)';
    });

    // Evitar que o dropdown feche ao clicar dentro dele
    dropdownContent.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Função para aplicar filtros
    function applyFilters() {
        const classId = document.getElementById('filter-class').value;
        const tagId = document.getElementById('filter-tag').value;
        const date = document.getElementById('filter-date').value;
        
        let url = window.location.pathname + '?';
        if (classId) url += `class=${classId}&`;
        if (tagId) url += `tag=${tagId}&`;
        if (date) url += `date=${date}&`;
        
        url = url.endsWith('&') ? url.slice(0, -1) : url;
        window.location.href = url;
    }
    
    // Função para resetar filtros
    function resetFilters() {
        window.location.href = window.location.pathname;
    }
    
    // Event listeners para os botões
    document.getElementById('apply-filters')?.addEventListener('click', applyFilters);
    document.getElementById('reset-filters')?.addEventListener('click', resetFilters);
    
    // Aplicar filtros com Enter
    const filterInputs = document.querySelectorAll('#filter-class, #filter-tag, #filter-date');
    filterInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    });
});