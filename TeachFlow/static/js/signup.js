// static/js/signup.js

document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.step');
    const form = document.getElementById('signupForm');
    const stepIndicator = document.getElementById('step-indicator');
    const planOptions = document.querySelectorAll('label input[name="plan"]');
    let currentStep = 1;
    let isSubmitting = false;

    function showStep(step) {
        steps.forEach((el, idx) => {
            if (idx === step - 1) {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        });
        stepIndicator.textContent = `Etapa ${step} de 3`;
        currentStep = step;
    }

    // Navegação
    document.getElementById('next-1').addEventListener('click', () => {
        const selectedPlan = document.querySelector('input[name="plan"]:checked');
        if (!selectedPlan) {
            alert('Por favor, selecione um plano.');
            return;
        }
        showStep(2);
    });

    document.getElementById('next-2').addEventListener('click', async () => {
        const username = form.elements['username'].value.trim();
        const firstName = form.elements['first_name'].value.trim();
        const lastName = form.elements['last_name'].value.trim();
        const email = form.elements['email'].value.trim();

        if (!username || !firstName || !lastName || !email) {
            alert('Por favor, preencha todas as informações.');
            return;
        }

        try {
            const response = await fetch('/accounts/validate-username-email/?username=' + encodeURIComponent(username) + '&email=' + encodeURIComponent(email));
            const data = await response.json();
            if (!data.is_valid) {
                let messages = [];
                if (data.errors.username) messages.push(data.errors.username);
                if (data.errors.email) messages.push(data.errors.email);
                alert(messages.join('\n'));
                return;
            }
            showStep(3);
        } catch (error) {
            console.error('Erro na validação:', error);
            alert('Erro ao validar informações. Tente novamente.');
        }
    });

    document.getElementById('prev-2').addEventListener('click', () => showStep(1));
    document.getElementById('prev-3').addEventListener('click', () => showStep(2));

    // Controle de seleção visual dos cards de plano
    planOptions.forEach(plan => {
        plan.addEventListener('change', function () {
            planOptions.forEach(p => p.parentElement.classList.remove('border-2', 'border-primary', 'bg-blue-50'));
            this.parentElement.classList.add('border-2', 'border-primary', 'bg-blue-50');
        });
    });

    // Submissão final do formulário
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (isSubmitting) return;

        const password1 = form.elements['password1'].value;
        const password2 = form.elements['password2'].value;

        if (password1 !== password2) {
            alert('As senhas não coincidem.');
            return;
        }

        const passwordError = validatePassword(password1);
        if (passwordError) {
            alert(passwordError);
            return;
        }

        // Garante que o plano selecionado esteja no FormData
        const formData = new FormData(form);
        const selectedPlan = document.querySelector('input[name="plan"]:checked');
        if (selectedPlan) {
            formData.set('plan', selectedPlan.value);  // força o valor correto no envio
        }

        isSubmitting = true;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(Object.values(data.errors).flat().join('\n'));
            }

            if (data.success) {
                alert('Conta criada com sucesso! Agora você pode fazer login.');
                window.location.href = data.redirect_url || '/accounts/login/';
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

    function validatePassword(password) {
        const minLength = 8;
        const hasNumber = /\d/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasSpecialChar = /[@$!%*?&]/.test(password);

        if (password.length < minLength) return "A senha deve ter pelo menos 8 caracteres.";
        if (!hasNumber) return "A senha deve conter pelo menos um número.";
        if (!hasUppercase) return "A senha deve conter pelo menos uma letra maiúscula.";
        if (!hasLowercase) return "A senha deve conter pelo menos uma letra minúscula.";
        if (!hasSpecialChar) return "A senha deve conter pelo menos um caractere especial (@, $, !, %, *, ?, &).";
        return null;
    }

    function getCSRFToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) return csrfInput.value;
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
