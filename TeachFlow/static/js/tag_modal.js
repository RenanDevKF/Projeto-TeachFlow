document.addEventListener('DOMContentLoaded', () => {
    const openButton = document.getElementById('add-tags-btn');
    const modal = document.getElementById('tag-modal');
    const cancelButton = document.getElementById('cancel-tag-modal');
    const closeButton = document.getElementById('close-modal-x');
    const form = document.getElementById('tag-form');
    const nameInput = document.getElementById('tag_name');
    const submitButton = document.getElementById('submit-tag-btn');
    const feedback = document.getElementById('tag-modal-feedback');

    if (
        !openButton ||
        !modal ||
        !form ||
        !nameInput ||
        !submitButton
    ) {
        return;
    }

    let isSubmitting = false;
    let triggerElement = null;

    function clearFeedback() {
        if (!feedback) {
            return;
        }

        feedback.textContent = '';
        feedback.className = 'mt-2 hidden text-sm';
    }

    function showFeedback(message, type = 'error') {
        if (!feedback) {
            return;
        }

        feedback.textContent = message;
        feedback.className = [
            'mt-2',
            'text-sm',
            type === 'success'
                ? 'text-green-600'
                : 'text-red-600',
        ].join(' ');
    }

    function updateSubmitButton() {
        submitButton.disabled = (
            isSubmitting ||
            nameInput.value.trim() === ''
        );
    }

    function openModal() {
        triggerElement = document.activeElement;
        
        clearFeedback();

        modal.classList.remove('hidden');
        modal.classList.add('flex');

        document.body.classList.add('overflow-hidden');

        window.setTimeout(() => {
            nameInput.focus();
        }, 0);

        updateSubmitButton();
    }

    function closeModal() {
        if (isSubmitting) {
            return;
        }

        modal.classList.add('hidden');
        modal.classList.remove('flex');

        document.body.classList.remove('overflow-hidden');

        form.reset();
        clearFeedback();
        updateSubmitButton();

        if (triggerElement instanceof HTMLElement) {
            triggerElement.focus();
        }

        triggerElement = null;        
    }

    openButton.addEventListener('click', openModal);
    cancelButton?.addEventListener('click', closeModal);
    closeButton?.addEventListener('click', closeModal);

    nameInput.addEventListener('input', () => {
        clearFeedback();
        updateSubmitButton();
    });

    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (
            event.key === 'Escape' &&
            !modal.classList.contains('hidden')
        ) {
            closeModal();
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (isSubmitting) {
            return;
        }

        const tagName = nameInput.value.trim();

        if (!tagName) {
            showFeedback('Informe um nome para a tag.');
            nameInput.focus();
            updateSubmitButton();
            return;
        }

        const csrfInput = form.querySelector(
            '[name="csrfmiddlewaretoken"]'
        );

        if (!csrfInput) {
            showFeedback(
                'Não foi possível validar a requisição. Recarregue a página.'
            );
            return;
        }

        isSubmitting = true;
        submitButton.disabled = true;
        submitButton.textContent = 'Criando...';
        clearFeedback();

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: JSON.stringify({
                    tag_name: tagName,
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfInput.value,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            let data = {};

            try {
                data = await response.json();
            } catch {
                data = {};
            }

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    'Não foi possível criar a tag.'
                );
            }

            showFeedback(
                data.message || 'Tag criada com sucesso.',
                'success'
            );

            window.setTimeout(() => {
                window.location.reload();
            }, 500);

        } catch (error) {
            console.error('Erro ao criar tag:', error);

            showFeedback(
                error.message ||
                'Erro ao comunicar com o servidor.'
            );

            isSubmitting = false;
            submitButton.textContent = 'Criar tag';
            updateSubmitButton();
        }
    });

    updateSubmitButton();
});