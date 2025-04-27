// static/js/login.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset estados
        errorMessage.style.display = 'none';
        errorMessage.innerText = '';
        form.querySelectorAll('.auth-input').forEach(input => {
            input.classList.remove('error');
        });

        const email = form.email.value.trim();
        const password = form.password.value.trim();

        if (!email || !password) {
            errorMessage.textContent = 'Por favor, preencha todos os campos.';
            errorMessage.style.display = 'block';
            return;
        }

        // Loading
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

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                if (data && data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error('Email ou senha incorretos.');
                }
            }

            if (data.success) {
                window.location.href = data.redirect_url || '/dashboard/';
            } else {
                throw new Error(data.error || 'Email ou senha incorretos.');
            }

        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            form.querySelectorAll('.auth-input').forEach(input => {
                input.classList.add('error');
            });
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Entrar';
        }
    });
});
