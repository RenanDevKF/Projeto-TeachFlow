// static/js/login.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset estados (da nova versão)
        errorMessage.style.display = 'none';
        form.querySelectorAll('.auth-input').forEach(input => {
            input.classList.remove('error');
        });

        // Validação básica (da versão original)
        const email = form.email.value;
        const password = form.password.value;

        if (!email || !password) {
            errorMessage.textContent = 'Por favor, preencha todos os campos';
            errorMessage.style.display = 'block';
            return;
        }

        // Estado de loading (melhorado da versão original)
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>Entrando...</span>
            </div>
        `;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': form.querySelector('input[name="csrfmiddlewaretoken"]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            // Tratamento da resposta (combinação das duas versões)
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Falha no login');
            }

            if (data.success) {
                window.location.href = data.redirect_url || '/dashboard';
            } else {
                throw new Error(data.error || 'Credenciais inválidas');
            }

        } catch (error) {
            // Tratamento de erro (combinado e melhorado)
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            
            // Destacar campos inválidos (da nova versão)
            form.querySelectorAll('.auth-input').forEach(input => {
                input.classList.add('error');
            });

        } finally {
            // Reset do botão (combinado)
            submitButton.disabled = false;
            submitButton.textContent = 'Entrar';
        }
    });
});