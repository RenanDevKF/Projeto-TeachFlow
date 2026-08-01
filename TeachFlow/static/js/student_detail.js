document.addEventListener('DOMContentLoaded', () => {
    const deleteForm = document.querySelector('.student-delete-form');

    if (!deleteForm) {
        return;
    }

    const deleteButton = deleteForm.querySelector('.student-delete-button');
    const deleteLabel = deleteForm.querySelector('.student-delete-label');
    const studentName = deleteForm.dataset.studentName;

    deleteForm.addEventListener('submit', (event) => {
        event.preventDefault();

        if (deleteForm.dataset.submitting === 'true') {
            return;
        }

        const confirmed = window.confirm(
            `Deseja excluir permanentemente o aluno "${studentName}"? Esta ação não poderá ser desfeita.`
        );

        if (!confirmed) {
            return;
        }

        deleteForm.dataset.submitting = 'true';

        if (deleteButton) {
            deleteButton.disabled = true;
        }

        if (deleteLabel) {
            deleteLabel.textContent = 'Excluindo...';
        }

        HTMLFormElement.prototype.submit.call(deleteForm);
    });
});