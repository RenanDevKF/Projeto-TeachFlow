document.addEventListener('DOMContentLoaded', () => {
    const templateCheckbox = document.getElementById('id_is_template');
    const templateCard = document.getElementById('template-info-card');

    function updateTemplateCard() {
        if (!templateCheckbox || !templateCard) {
            return;
        }

        templateCard.classList.toggle(
            'hidden',
            !templateCheckbox.checked
        );
    }

    templateCheckbox?.addEventListener(
        'change',
        updateTemplateCard
    );

    updateTemplateCard();

    function setupCounter(textareaId, counterId) {
        const textarea = document.getElementById(textareaId);
        const counter = document.getElementById(counterId);

        if (!textarea || !counter) {
            return;
        }

        function updateCounter() {
            const total = textarea.value.length;

            counter.textContent =
                `${total} ${total === 1 ? 'caractere' : 'caracteres'}`;
        }

        textarea.addEventListener(
            'input',
            updateCounter
        );

        updateCounter();
    }

    setupCounter(
        'id_description',
        'description-counter'
    );

    setupCounter(
        'id_materials',
        'materials-counter'
    );
});