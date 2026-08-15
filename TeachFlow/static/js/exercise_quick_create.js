document.addEventListener('DOMContentLoaded', () => {
    const objectiveController = setupQuickCreate({
        type: 'objectives',
        modalId: 'quick-objective-modal',
        formId: 'quick-objective-form',
        openSelector: '[data-open-objective-modal]',
        closeSelector: '[data-close-objective-modal]',
        submitId: 'quick-objective-submit',
        feedbackId: 'quick-objective-feedback',
        focusId: 'quick-objective-title',
        loadingText: 'Criando objetivo...',
        buildPayload: (form) => ({
            title: form.querySelector('#quick-objective-title')?.value.trim() || '',
            description: form.querySelector('#quick-objective-description')?.value.trim() || '',
        }),
        validate: ({ title }) => {
            if (!title) return 'Informe o título do objetivo.';
            if (title.length > 200) return 'O título deve possuir no máximo 200 caracteres.';
            return '';
        },
        mapItem: (item) => ({
            id: item.id,
            title: item.title,
            description: item.description || '',
            selected: true,
        }),
    });

    const tagController = setupQuickCreate({
        type: 'tags',
        modalId: 'quick-tag-modal',
        formId: 'quick-tag-form',
        openSelector: '[data-open-tag-modal]',
        closeSelector: '[data-close-tag-modal]',
        submitId: 'quick-tag-submit',
        feedbackId: 'quick-tag-feedback',
        focusId: 'quick-tag-name',
        loadingText: 'Criando tag...',
        buildPayload: (form) => ({
            name: form.querySelector('#quick-tag-name')?.value.trim() || '',
        }),
        validate: ({ name }) => {
            if (!name) return 'Informe o nome da tag.';
            if (name.length > 50) return 'O nome deve possuir no máximo 50 caracteres.';
            if (!/^[\w\sÀ-ÿ-]+$/u.test(name)) return 'Use apenas letras, números, espaços, hífens e underscores.';
            return '';
        },
        mapItem: (item) => ({
            id: item.id,
            name: item.name,
            color: item.color,
            selected: true,
        }),
    });

    function setupQuickCreate(config) {
        const modal = document.getElementById(config.modalId);
        const form = document.getElementById(config.formId);
        const submitButton = document.getElementById(config.submitId);
        const feedback = document.getElementById(config.feedbackId);
        const openButtons = document.querySelectorAll(config.openSelector);

        if (!modal || !form || !submitButton || !feedback || !openButtons.length) return null;

        const closeButtons = modal.querySelectorAll(config.closeSelector);
        const defaultSubmitContent = submitButton.innerHTML;
        let lastFocusedElement = null;
        let isSubmitting = false;

        openButtons.forEach((button) => button.addEventListener('click', () => openModal(button)));
        closeButtons.forEach((button) => button.addEventListener('click', closeModal));

        modal.addEventListener('click', (event) => {
            if (event.target === modal) closeModal();
        });

        modal.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                closeModal();
            }

            if (event.key === 'Tab') keepFocusInsideModal(event);
        });

        form.addEventListener('submit', handleSubmit);

        function openModal(trigger) {
            if (isSubmitting) return;

            lastFocusedElement = trigger || document.activeElement;
            resetFeedback();
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.classList.add('overflow-hidden');
            modal.setAttribute('aria-hidden', 'false');

            window.setTimeout(() => document.getElementById(config.focusId)?.focus(), 0);
        }

        function closeModal() {
            if (isSubmitting) return;

            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.classList.remove('overflow-hidden');
            modal.setAttribute('aria-hidden', 'true');
            form.reset();
            resetFeedback();
            lastFocusedElement?.focus();
        }

        async function handleSubmit(event) {
            event.preventDefault();
            if (isSubmitting) return;

            const payload = config.buildPayload(form);
            const validationError = config.validate(payload);

            if (validationError) {
                showFeedback(validationError, 'error');
                document.getElementById(config.focusId)?.focus();
                return;
            }

            const manager = window.multiSelectorManager;

            if (!manager?.hasSelector(config.type)) {
                showFeedback('Não foi possível localizar o seletor deste formulário.', 'error');
                return;
            }

            const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]')?.value;

            if (!csrfToken) {
                showFeedback('Token de segurança não encontrado. Atualize a página e tente novamente.', 'error');
                return;
            }

            setSubmitting(true);
            resetFeedback();

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(payload),
                });

                const data = await parseResponse(response);

                if (!response.ok || !data.success) throw new Error(data.error || data.message || 'Não foi possível criar o recurso.');

                const itemAdded = manager.addItem(config.type, config.mapItem(data.item));

                if (!itemAdded) throw new Error('O recurso foi criado, mas não pôde ser incluído no seletor.');

                showFeedback(data.message || 'Recurso criado e selecionado.', 'success');

                window.setTimeout(() => {
                    setSubmitting(false);
                    closeModal();
                }, 650);
            } catch (error) {
                console.error(`Erro na criação rápida de ${config.type}:`, error);
                showFeedback(error.message || 'Ocorreu um erro inesperado.', 'error');
                setSubmitting(false);
            }
        }

        function setSubmitting(submitting) {
            isSubmitting = submitting;
            submitButton.disabled = submitting;

            if (submitting) {
                submitButton.innerHTML = `
                    <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4Z"></path>
                    </svg>
                    ${config.loadingText}
                `;
            } else {
                submitButton.innerHTML = defaultSubmitContent;
            }
        }

        function showFeedback(message, type) {
            feedback.textContent = message;
            feedback.classList.remove('hidden', 'text-red-600', 'text-green-700');
            feedback.classList.add(type === 'success' ? 'text-green-700' : 'text-red-600');
            feedback.setAttribute('role', type === 'success' ? 'status' : 'alert');
        }

        function resetFeedback() {
            feedback.textContent = '';
            feedback.classList.add('hidden');
            feedback.classList.remove('text-red-600', 'text-green-700');
        }

        function keepFocusInsideModal(event) {
            const focusableElements = Array.from(
                modal.querySelectorAll(
                    'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
                )
            ).filter((element) => !element.closest('.hidden'));

            if (!focusableElements.length) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (event.shiftKey && document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            } else if (!event.shiftKey && document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }

        return { open: openModal, close: closeModal };
    }

    async function parseResponse(response) {
        try {
            return await response.json();
        } catch {
            return {
                success: false,
                error: 'O servidor retornou uma resposta inválida.',
            };
        }
    }
});