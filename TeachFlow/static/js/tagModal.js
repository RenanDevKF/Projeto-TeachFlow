document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const addTagsBtn = document.getElementById('add-tags-btn');
    const tagModal = document.getElementById('tag-modal');
    const cancelModalBtn = document.getElementById('cancel-tag-modal');
    const closeModalX = document.getElementById('close-modal-x');
    const tagForm = document.getElementById('tag-form');
    const tagNameInput = document.getElementById('tag_name');
    const submitBtn = document.getElementById('submit-tag-btn');

    if (!tagModal || !tagForm || !tagNameInput) {
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
    }    
    
    // Funções básicas do modal
    function openModal() {
        tagModal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        tagNameInput.focus();
    }
    
    function closeModal() {
        tagModal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        tagForm.reset();
    }
    
    // Event listeners
    addTagsBtn?.addEventListener('click', openModal);
    cancelModalBtn?.addEventListener('click', closeModal);
    closeModalX?.addEventListener('click', closeModal);
    
    // Fechar ao clicar fora ou pressionar ESC
    tagModal?.addEventListener('click', function(e) {
        if (e.target === tagModal) closeModal();
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !tagModal.classList.contains('hidden')) {
            closeModal();
        }
    });
    
    // Envio do formulário
    tagForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const tagName = tagNameInput.value.trim();
        
        if (!tagName) {
            alert('Por favor, insira um nome para a tag');
            return;
        }
        
        submitBtn.disabled = true;
        
        try {
            const tagName = tagNameInput.value.trim();
            const formData = JSON.stringify({ tag_name: tagName });
            const response = await fetch(tagForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                alert(data.error || 'Erro ao adicionar tag');
                return;
            }
            
            alert(data.message);
            closeModal();
            window.location.reload(); // Recarrega para atualizar as tags
            
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao comunicar com o servidor');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        }
    });
});