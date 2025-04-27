// static/js/signup.js

document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.step');
    const stepDots = document.querySelectorAll('.step-dot');
    const planOptions = document.querySelectorAll('.plan-option');
    const form = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');
    const selectedPlanInput = document.getElementById('selectedPlan');

    // Funções Auxiliares
    function goToStep(stepNumber) {
        steps.forEach(step => step.classList.remove('active'));
        stepDots.forEach(dot => dot.classList.remove('active'));
        document.getElementById(`step-${stepNumber}`).classList.add('active');
        document.querySelector(`.step-dot[data-step="${stepNumber}"]`).classList.add('active');
    }

    function validatePassword(password) {
        const minLength = 8;
        const hasNumber = /\d/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasSpecialChar = /[@$!%*?&]/.test(password);

        if (password.length < minLength) {
            return "A senha deve ter pelo menos 8 caracteres.";
        }
        if (!hasNumber) {
            return "A senha deve conter pelo menos um número.";
        }
        if (!hasUppercase) {
            return "A senha deve conter pelo menos uma letra maiúscula.";
        }
        if (!hasLowercase) {
            return "A senha deve conter pelo menos uma letra minúscula.";
        }
        if (!hasSpecialChar) {
            return "A senha deve conter pelo menos um caractere especial (@, $, !, %, *, ?, &).";
        }
        return null;
    }

    function getCSRFToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) return csrfInput.value;
        
        // Backup: parse dos cookies
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return null;
    }

    // Navegação nos steps
    document.getElementById('step1-next').addEventListener('click', () => goToStep(2));
    document.getElementById('step2-back').addEventListener('click', () => goToStep(1));
    document.getElementById('step2-next').addEventListener('click', async () => {
        const username = form.elements['username'].value.trim();
        const firstName = form.elements['first_name'].value.trim();
        const lastName = form.elements['last_name'].value.trim();
        const email = form.elements['email'].value.trim();

        if (!username || !firstName || !lastName || !email) {
            alert('Por favor, preencha todas as informações pessoais.');
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
    
            // Se passar na validação, avança para o Step 3
            goToStep(3);
        } catch (error) {
            console.error('Erro ao validar username/email', error);
            alert('Erro ao validar informações. Tente novamente.');
        }
    });

    document.getElementById('step3-back').addEventListener('click', () => goToStep(2));

    // Seleção de Plano
    planOptions.forEach(option => {
        option.addEventListener('click', function () {
            planOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            selectedPlanInput.value = radio.value;
        });
    });

    // Submissão do formulário
    let isSubmitting = false;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (isSubmitting) {
            // Se já está enviando, simplesmente ignora novos cliques
            return;
        }

        errorMessage.style.display = 'none';

        const password1 = form.elements['password1'].value;
        const password2 = form.elements['password2'].value;

        if (password1 !== password2) {
            errorMessage.textContent = 'As senhas não coincidem.';
            errorMessage.style.display = 'block';
            return;
        }

        const passwordError = validatePassword(password1);
        if (passwordError) {
            errorMessage.textContent = passwordError;
            errorMessage.style.display = 'block';
            return;
        }

        submitButton.disabled = true;
        isSubmitting = true; // Marca que está enviando agora
        submitButton.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>Criando conta...</span>
            </div>
        `;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
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
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Criar Conta';
            isSubmitting = false;
        }
    });
});
