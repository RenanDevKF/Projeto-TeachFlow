document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const submitButton = document.getElementById('submitButton');
    let isSubmitting = false;

    form.addEventListener('submit', function (e) {
        if (isSubmitting) {
            e.preventDefault();
            return;
        }

        const name = form.elements['name'].value.trim();
        const school = form.elements['school'].value.trim();
        const period = form.elements['period'].value;
        const year = form.elements['year'].value.trim();

        if (!name || !school || !period || !year) {
            e.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios.');
            return;
        }

        if (year.length !== 4 || isNaN(year)) {
            e.preventDefault();
            alert('O ano letivo deve ser um número de 4 dígitos.');
            return;
        }

        // Bloqueia envio duplo
        isSubmitting = true;
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>Salvando...</span>
            </div>
        `;
    });
});
