/**
 * Gerenciamento dos checkboxes de exercícios aplicados
 * Arquivo: static/js/lesson-detail.js
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeExerciseCheckboxes();
});

/**
 * Inicializa os event listeners dos checkboxes de exercícios
 */
function initializeExerciseCheckboxes() {
    const checkboxes = document.querySelectorAll('.exercise-applied-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });
}

/**
 * Manipula a mudança de estado do checkbox
 * @param {Event} event - Evento de mudança do checkbox
 */
function handleCheckboxChange(event) {
    const checkbox = event.target;
    const lessonId = checkbox.getAttribute('data-lesson-id');
    const exerciseId = checkbox.getAttribute('data-exercise-id');
    const isChecked = checkbox.checked;
    
    // Atualizar visual imediatamente
    updateExerciseVisualStatus(checkbox, isChecked);
    
    // Enviar requisição para o servidor
    toggleExerciseAppliedStatus(lessonId, exerciseId, isChecked, checkbox);
}

/**
 * Atualiza o status visual do exercício
 * @param {HTMLElement} checkbox - Elemento checkbox
 * @param {boolean} isChecked - Status do checkbox
 */
function updateExerciseVisualStatus(checkbox, isChecked) {
    const card = checkbox.closest('.border.border-gray-200');
    const statusBadge = card.querySelector('.exercise-status-badge');
    const statusDot = statusBadge.querySelector('span');
    const statusText = statusBadge.querySelector('.status-text');
    
    if (isChecked) {
        // Aplicado
        statusBadge.className = statusBadge.className.replace('bg-gray-100 text-gray-600', 'bg-green-100 text-green-800');
        statusDot.className = statusDot.className.replace('bg-gray-400', 'bg-green-600');
        statusText.textContent = 'Aplicado';
    } else {
        // Não aplicado
        statusBadge.className = statusBadge.className.replace('bg-green-100 text-green-800', 'bg-gray-100 text-gray-600');
        statusDot.className = statusDot.className.replace('bg-green-600', 'bg-gray-400');
        statusText.textContent = 'Não aplicado';
    }
}

/**
 * Envia requisição AJAX para alterar status do exercício
 * @param {string} lessonId - ID da aula
 * @param {string} exerciseId - ID do exercício
 * @param {boolean} isChecked - Novo status
 * @param {HTMLElement} checkbox - Elemento checkbox para reverter em caso de erro
 */
function toggleExerciseAppliedStatus(lessonId, exerciseId, isChecked, checkbox) {
    const csrfToken = getCSRFToken();
    
    if (!csrfToken) {
        console.error('Token CSRF não encontrado');
        revertCheckboxChange(checkbox, isChecked);
        return;
    }
    
    fetch(`/lessons/${lessonId}/exercises/${exerciseId}/toggle-applied/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'is_applied': isChecked
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgressBar();
        } else {
            console.error('Erro do servidor:', data.message);
            revertCheckboxChange(checkbox, isChecked);
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        revertCheckboxChange(checkbox, isChecked);
    });
}

/**
 * Reverte o estado do checkbox em caso de erro
 * @param {HTMLElement} checkbox - Elemento checkbox
 * @param {boolean} currentState - Estado atual que deve ser revertido
 */
function revertCheckboxChange(checkbox, currentState) {
    // Reverter checkbox
    checkbox.checked = !currentState;
    
    // Reverter visual
    updateExerciseVisualStatus(checkbox, !currentState);
}

/**
 * Atualiza a barra de progresso e contadores
 */
function updateProgressBar() {
    const checkboxes = document.querySelectorAll('.exercise-applied-checkbox');
    const totalExercises = checkboxes.length;
    const appliedExercises = document.querySelectorAll('.exercise-applied-checkbox:checked').length;
    const percentage = totalExercises > 0 ? Math.round((appliedExercises / totalExercises) * 100) : 0;
    
    // Atualizar contador de exercícios aplicados
    const appliedCount = document.querySelector('.applied-count');
    if (appliedCount) {
        appliedCount.textContent = appliedExercises;
    }
    
    // Atualizar barra de progresso
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
    
    // Atualizar texto da porcentagem
    const progressText = document.querySelector('.progress-text');
    if (progressText) {
        progressText.textContent = percentage + '%';
    }
}

/**
 * Obtém o token CSRF da página
 * @returns {string|null} Token CSRF ou null se não encontrado
 */
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : null;
}

/**
 * Utilitário para debug - mostra estatísticas atuais
 */
function showExerciseStats() {
    const checkboxes = document.querySelectorAll('.exercise-applied-checkbox');
    const applied = document.querySelectorAll('.exercise-applied-checkbox:checked');
    
    console.log('Estatísticas dos Exercícios:');
    console.log(`Total: ${checkboxes.length}`);
    console.log(`Aplicados: ${applied.length}`);
    console.log(`Porcentagem: ${checkboxes.length > 0 ? Math.round((applied.length / checkboxes.length) * 100) : 0}%`);
}