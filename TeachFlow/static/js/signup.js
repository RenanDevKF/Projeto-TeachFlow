// static/js/signup.js

document.addEventListener('DOMContentLoaded', function() {
    const steps = document.querySelectorAll('.step');
    const stepDots = document.querySelectorAll('.step-dot');
    const planOptions = document.querySelectorAll('.plan-option');
    const form = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');
    const selectedPlanInput = document.getElementById('selectedPlan');

    // Função para obter o token CSRF
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || form.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    // Selecionar plano
    planOptions.forEach(option => {
        option.addEventListener('click', function() {
            planOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            selectedPlanInput.value = radio.value;
        });
    });

    // Avançar e voltar nos steps
    document.getElementById('step1-next').addEventListener('click', () => goToStep(2));
    document.getElementById('step2-back').addEventListener('click', () => goToStep(1));
    document.getElementById('step2-next').addEventListener('click', () => {
        const firstName = form.elements['first_name'].value;
        const lastName = form.elements['last_name'].value;
        const email = form.elements['email'].value;

        if (!firstName || !lastName || !email) {
            alert('Preencha todos os campos');
            return;
        }
        goToStep(3);
    });
    document.getElementById('step3-back').addEventListener('click', () => goToStep(2));

    function goToStep(stepNumber) {
        steps.forEach(step => step.classList.remove('active'));
        stepDots.forEach(dot => dot.classList.remove('active'));

        document.getElementById(`step-${stepNumber}`).classList.add('active');
        document.querySelector(`.step-dot[data-step="${stepNumber}"]`).classList.add('active');
    }

    // Função para mostrar erros do servidor
    function displayFormErrors(form, errors) {
        // Limpa erros anteriores
        form.querySelectorAll('.error-message').forEach(el => {
            if (el.id !== 'errorMessage') el.remove();
        });
        form.querySelectorAll('.auth-input').forEach(input => {
            input.classList.remove('error');
        });

        // Adiciona novos erros
        for (const [field, messages] of Object.entries(errors)) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('error');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = Array.isArray(messages) ? messages.join(' ') : messages;
                input.parentNode.insertBefore(errorDiv, input.nextSibling);
            }
        }
    }

    // Submeter formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        errorMessage.style.display = 'none';

        // Validação básica do cliente
        const password1 = form.elements['password1'].value;
        const password2 = form.elements['password2'].value;

        if (password1 !== password2) {
            errorMessage.textContent = 'As senhas não coincidem';
            errorMessage.style.display = 'block';
            return;
        }

        if (password1.length < 6) {
            errorMessage.textContent = 'Senha deve ter pelo menos 6 caracteres';
            errorMessage.style.display = 'block';
            return;
        }

        const selectedPlan = selectedPlanInput.value;
        submitButton.disabled = true;

        // Mostrar estado de carregamento
        submitButton.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>${selectedPlan !== 'free' ? 'Redirecionando para pagamento...' : 'Criando sua conta...'}</span>
            </div>
        `;

        // Modifique o bloco try/catch do seu event listener para:
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
        
            // Verificação EXTRA do content-type
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`O servidor retornou uma resposta inválida: ${response.status}`);
            }
        
            const data = await response.json();
            
            if (!response.ok) {
                if (data.errors) {
                    displayFormErrors(form, data.errors);
                } else {
                    throw new Error(data.error || 'Erro no cadastro');
                }
                return;
            }
        
            if (data.success) {
                window.location.href = data.redirect_url || "/accounts/login/";
            }
        } catch (error) {
            console.error('Erro completo:', {
                error: error,
                response: await response?.text()
            });
            
            errorMessage.textContent = error.message.includes('inválida') ? 
                'Erro no servidor. Tente novamente.' : error.message;
            errorMessage.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Criar Conta';
        }
    });
});