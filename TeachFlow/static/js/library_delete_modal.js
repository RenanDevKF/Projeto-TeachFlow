document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('library-delete-modal');
    const form = document.getElementById('library-delete-form');
    const title = document.getElementById('library-delete-modal-title');
    const resourceName = document.getElementById('library-delete-resource-name');
    const cancelButton = document.getElementById('library-delete-modal-cancel');
    const closeButton = document.getElementById('library-delete-modal-close');
    const triggers = document.querySelectorAll('[data-library-delete-trigger]');

    if (!modal || !form || !title || !resourceName || !triggers.length) return;

    let triggerElement = null;

    function openModal(trigger) {
        const deleteUrl = trigger.dataset.deleteUrl;
        const deleteName = trigger.dataset.deleteName;
        const deleteLabel = trigger.dataset.deleteLabel;

        if (!deleteUrl || !deleteName || !deleteLabel) return;

        triggerElement = trigger;

        form.action = deleteUrl;
        title.textContent = `Excluir ${deleteLabel}`;
        resourceName.textContent = `"${deleteName}"`;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.classList.add('overflow-hidden');

        window.setTimeout(() => {
            cancelButton?.focus();
        }, 0);
    }

    function closeModal() {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.classList.remove('overflow-hidden');

        form.removeAttribute('action');

        if (triggerElement instanceof HTMLElement) {
            triggerElement.focus();
        }

        triggerElement = null;
    }

    triggers.forEach(trigger => {
        trigger.addEventListener('click', () => openModal(trigger));
    });

    cancelButton?.addEventListener('click', closeModal);
    closeButton?.addEventListener('click', closeModal);

    modal.addEventListener('click', event => {
        if (event.target === modal) closeModal();
    });

    document.addEventListener('keydown', event => {
        if (
            event.key === 'Escape'
            && !modal.classList.contains('hidden')
        ) {
            closeModal();
        }
    });
});