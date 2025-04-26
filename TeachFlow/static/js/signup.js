// static/js/signup.js

document.addEventListener('DOMContentLoaded', function() {
    const steps = document.querySelectorAll('.step');
    const stepDots = document.querySelectorAll('.step-dot');
    const planOptions = document.querySelectorAll('.plan-option');
    const form = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');
    const selectedPlanInput = document.getElementById('selectedPlan');

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

    // Submeter formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        errorMessage.style.display = 'none';

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

        if (selectedPlan !== 'free') {
            submitButton.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <span>Redirecionando para pagamento...</span>
                </div>
            `;
            setTimeout(() => {
                alert(`Redirecionando para pagamento do plano ${selectedPlan}`);
                // window.location.href = '/payment/?plan=' + selectedPlan;
            }, 1500);
            return;
        }

        submitButton.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>Criando sua conta...</span>
            </div>
        `;

        setTimeout(() => {
            alert('Conta criada com sucesso!');
            // form.submit(); // Em projeto real, descomente aqui
        }, 2000);
    });
});
