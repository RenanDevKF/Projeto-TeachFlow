let studentIdToDelete = null;
let classGroupIdToDelete = null;

function confirmStudentDeletion(studentId, fullName, classGroupId) {
  studentIdToDelete = studentId;
  classGroupIdToDelete = classGroupId;

  const modal = document.getElementById('deleteModal');
  const text = document.getElementById('deleteModalText');
  text.textContent = `Deseja realmente excluir o aluno "${fullName}"?`;

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function closeDeleteModal() {
  const modal = document.getElementById('deleteModal');
  modal.classList.remove('flex');
  modal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
  const confirmBtn = document.getElementById('confirmDeleteBtn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      if (!studentIdToDelete || !classGroupIdToDelete) return;

      fetch(`/class-groups/${classGroupIdToDelete}/students/${studentIdToDelete}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(response => {
          if (response.ok) {
            // Remove o aluno da DOM
            const row = document.getElementById(`student-row-${studentIdToDelete}`);
            if (row) row.remove();
            closeDeleteModal();
          } else {
            alert("Erro ao excluir aluno.");
          }
        });
    });
  }
});

// Reutilização do token CSRF
function getCSRFToken() {
    return getCookie('csrftoken');
  }
  
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  
