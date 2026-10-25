document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.step');
    const form = document.getElementById('signupForm');
    const stepIndicator = document.getElementById('step-indicator');

    let currentStep = 1;
    let isSubmitting = false;

    function showStep(step) {
        steps.forEach((element, index) => {
            if (index === step - 1) {
                element.classList.remove('hidden');
            } else {
                element.classList.add('hidden');
            }
        });

        stepIndicator.textContent = `Etapa ${step} de 2`;
        currentStep = step;
    }

    document.getElementById('next-1').addEventListener('click', () => {
        const username = form.elements['username'].value.trim();
        const firstName = form.elements['first_name'].value.trim();
        const lastName = form.elements['last_name'].value.trim();
        const email = form.elements['email'].value.trim();

        if (!username || !firstName || !lastName || !email) {
            alert('Por favor, preencha todas as informações.');
            return;
        }

        showStep(2);
    });

    document.getElementById('prev-2').addEventListener('click', () => {
        showStep(1);
    });

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        if (isSubmitting) {
            return;
        }

        const password1 = form.elements['password1'].value;
        const password2 = form.elements['password2'].value;

        if (password1 !== password2) {
            alert('As senhas não coincidem.');
            return;
        }

        isSubmitting = true;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    Object.values(data.errors).flat().join('\n')
                );
            }

            if (data.success) {
                window.location.href =
                    data.redirect_url ||
                    '/accounts/register/check-email/';
            } else {
                throw new Error('Erro ao criar a conta.');
            }

        } catch (error) {
            console.error(error);
            alert(error.message);

        } finally {
            isSubmitting = false;
        }
    });

    function getCSRFToken() {
        const csrfInput = document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        );

        if (csrfInput) {
            return csrfInput.value;
        }

        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }

        return null;
    }
});