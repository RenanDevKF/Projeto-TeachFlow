document.addEventListener('DOMContentLoaded', () => {
    const deleteForm = document.querySelector('.exercise-delete-form');

    if (!deleteForm) {
        return;
    }

    const deleteButton = deleteForm.querySelector(
        '.exercise-delete-button'
    );
    const deleteLabel = deleteForm.querySelector(
        '.exercise-delete-label'
    );
    const exerciseTitle = deleteForm.dataset.exerciseTitle;

    deleteForm.addEventListener('submit', (event) => {
        event.preventDefault();

        if (deleteForm.dataset.submitting === 'true') {
            return;
        }

        const confirmed = window.confirm(
            `Deseja excluir permanentemente o exercício "${exerciseTitle}"? Esta ação não poderá ser desfeita.`
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