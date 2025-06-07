document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const addTagsBtn = document.getElementById('add-tags-btn');
    const tagModal = document.getElementById('tag-modal');
    const cancelModalBtn = document.getElementById('cancel-tag-modal');
    const closeModalX = document.getElementById('close-modal-x');
    const tagForm = document.getElementById('tag-form');
    const tagNameInput = document.getElementById('tag_name');
    const submitBtn = document.getElementById('submit-tag-btn');
    
    // Verifica se os elementos existem
    if (!addTagsBtn || !tagModal) {
        console.warn('Elementos do modal de tags não encontrados');
        return;
    }
    
    // Estado do modal
    let isSubmitting = false;
    
    // Abrir modal
    addTagsBtn.addEventListener('click', function(e) {
        e.preventDefault();
        openModal();
    });
    
    // Função para abrir modal
    function openModal() {
        tagModal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        
        // Foca no input após pequeno delay
        setTimeout(() => {
            tagNameInput?.focus();
        }, 100);
    }
    
    // Função para fechar modal
    function closeModal() {
        tagModal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        tagForm?.reset();
        removeErrorMessages();
        
        // Retorna foco para o botão que abriu o modal
        setTimeout(() => {
            addTagsBtn?.focus();
        }, 100);
    }
    
    // Event listeners para fechar modal
    // Botão cancelar
    cancelModalBtn?.addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
    });
    
    // Botão X
    closeModalX?.addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
    });
    
    // Tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !tagModal.classList.contains('hidden')) {
            e.preventDefault();
            closeModal();
        }
    });
    
    // Clicar fora do modal (backdrop)
    tagModal.addEventListener('click', function(e) {
        if (e.target === tagModal) {
            closeModal();
        }
    });
    
    // Funções para mensagens de status
    function showError(message) {
        removeErrorMessages();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4';
        errorDiv.id = 'tag-error-message';
        errorDiv.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm">${message}</p>
                </div>
            </div>
        `;
        
        const formContainer = tagForm?.querySelector('.space-y-4');
        formContainer?.insertBefore(errorDiv, formContainer.firstChild);
    }
    
    function showSuccess(message) {
        removeErrorMessages();
        
        const successDiv = document.createElement('div');
        successDiv.className = 'bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4';
        successDiv.id = 'tag-success-message';
        successDiv.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm">${message}</p>
                </div>
            </div>
        `;
        
        const formContainer = tagForm?.querySelector('.space-y-4');
        formContainer?.insertBefore(successDiv, formContainer.firstChild);
    }
    
    function removeErrorMessages() {
        document.getElementById('tag-error-message')?.remove();
        document.getElementById('tag-success-message')?.remove();
    }
    
    // Estado de carregamento
    function setLoadingState(loading) {
        isSubmitting = loading;
        
        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.innerHTML = loading ? `
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Salvando...
            ` : 'Salvar Tag';
        }
        
        if (tagNameInput) tagNameInput.disabled = loading;
        if (cancelModalBtn) cancelModalBtn.disabled = loading;
        if (closeModalX) closeModalX.disabled = loading;
    }
    
    // Função para obter o token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Validação em tempo real
    tagNameInput?.addEventListener('input', function() {
        removeErrorMessages();
        const value = this.value.trim();
        
        if (value.length > 50) {
            showError('O nome da tag deve ter no máximo 50 caracteres');
        }
        
        if (!/^[a-zA-ZÀ-ÿ0-9\s\-_]+$/.test(value) && value.length > 0) {
            showError('Use apenas letras, números, espaços, hífens e underscores');
        }
    });
    
    // Validação do formulário com AJAX
    tagForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        if (isSubmitting) return;
        
        const tagName = tagNameInput.value.trim();
        
        // Validações básicas do cliente
        if (!tagName) {
            showError('Por favor, insira um nome para a tag');
            tagNameInput.focus();
            return;
        }
        
        if (tagName.length < 2) {
            showError('O nome da tag deve ter pelo menos 2 caracteres');
            tagNameInput.focus();
            return;
        }
        
        if (!/^[a-zA-ZÀ-ÿ0-9\s\-_]+$/.test(tagName)) {
            showError('Use apenas letras, números, espaços, hífens e underscores');
            tagNameInput.focus();
            return;
        }
        
        setLoadingState(true);
        
        try {
            const formData = new FormData(tagForm);
            formData.append('model_type', 'lesson');
            formData.append('model_id', tagForm.action.split('/').slice(-2, -1)[0]); // Extrai o ID da URL
            
            const response = await fetch(tagForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                showError(data.error);
                return;
            }
            
            // Sucesso - mostra mensagem e fecha o modal após delay
            showSuccess(data.message || 'Tag criada com sucesso!');
            
            setTimeout(() => {
                closeModal();
                window.location.reload(); // Recarrega para atualizar as tags
            }, 1500);
            
        } catch (error) {
            console.error('Erro:', error);
            showError('Erro ao processar tag. Tente novamente.');
        } finally {
            setLoadingState(false);
        }
    });
    
    // Inicializar ícones Lucide se disponível
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});