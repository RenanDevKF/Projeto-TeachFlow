// student_form.js
document.addEventListener('DOMContentLoaded', function() {
    const birthDateInput = document.getElementById('birth_date_input');
    
    // Remove qualquer foco automático
    if (document.activeElement && document.activeElement !== document.body) {
        document.activeElement.blur();
    }
    
    // Força o campo de data a perder o foco quando outros elementos são clicados
    document.addEventListener('click', function(e) {
        // Se o clique não foi no campo de data ou em seu calendário
        if (!e.target.closest('#birth_date_input') && 
            !e.target.closest('.datepicker') && 
            !e.target.closest('[data-date]')) {
            
            if (document.activeElement === birthDateInput) {
                birthDateInput.blur();
                // Força o fechamento do calendário
                birthDateInput.setAttribute('readonly', true);
                setTimeout(() => {
                    birthDateInput.removeAttribute('readonly');
                }, 10);
            }
        }
    });
    
    // Adiciona evento específico para quando o campo perde o foco
    birthDateInput.addEventListener('blur', function() {
        // Força o fechamento de qualquer calendário que possa estar aberto
        this.setAttribute('readonly', true);
        setTimeout(() => {
            this.removeAttribute('readonly');
        }, 10);
    });
    
    // Previne que o campo mantenha foco indefinidamente
    birthDateInput.addEventListener('change', function() {
        setTimeout(() => {
            this.blur();
        }, 100);
    });
    
    // Event listener para ESC key fechar o calendário
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.activeElement === birthDateInput) {
            birthDateInput.blur();
        }
    });
});

// Função para confirmar exclusão de estudante
function confirmStudentDeletion(studentId, studentName, classGroupId) {
    // Força o campo de data a perder foco antes de abrir o modal
    const birthDateInput = document.getElementById('birth_date_input');
    if (document.activeElement === birthDateInput) {
        birthDateInput.blur();
    }
    
    const modal = document.getElementById('deleteModal');
    const modalText = document.getElementById('deleteModalText');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    modalText.textContent = `Tem certeza que deseja excluir o aluno "${studentName}"? Esta ação não pode ser desfeita.`;
    
    confirmBtn.onclick = function() {
        deleteStudent(studentId, classGroupId);
    };
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function deleteStudent(studentId, classGroupId) {
    fetch(`/student/${studentId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (response.ok) {
            // Remove a linha do estudante da lista
            const studentRow = document.getElementById(`student-row-${studentId}`);
            if (studentRow) {
                studentRow.remove();
            }
            closeDeleteModal();
        } else {
            alert('Erro ao excluir o aluno. Tente novamente.');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao excluir o aluno. Tente novamente.');
    });
}

// Configuração do modal de exclusão
document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = document.getElementById('deleteModal');
    
    if (deleteModal) {
        // Previne propagação de eventos no modal
        deleteModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeDeleteModal();
            }
        });
    }
});