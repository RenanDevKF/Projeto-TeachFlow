// tagModal.js
document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const addTagsBtn = document.getElementById('add-tags-btn');
    const tagModal = document.getElementById('tag-modal');
    const closeModalBtn = document.getElementById('close-tag-modal');
    const cancelModalBtn = document.getElementById('cancel-tag-modal');
    const tagForm = document.getElementById('tag-form');
    const submitBtn = document.getElementById('submit-tag-btn');
    
    // Verifica se os elementos existem (para evitar erros em páginas sem o modal)
    if (!addTagsBtn || !tagModal) return;
    
    // Abrir modal
    addTagsBtn.addEventListener('click', function(e) {
        e.preventDefault();
        tagModal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        document.getElementById('tag_name').focus();
    });
    
    // Fechar modal
    function closeModal() {
        tagModal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        addTagsBtn.focus();
    }
    
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    
    // Fechar modal ao pressionar ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !tagModal.classList.contains('hidden')) {
            closeModal();
        }
    });
    
    // Fechar modal ao clicar fora do conteúdo
    tagModal.addEventListener('click', function(e) {
        if (e.target === tagModal) {
            closeModal();
        }
    });
    
    // Validação do formulário
    if (tagForm) {
        tagForm.addEventListener('submit', function(e) {
            const tagName = document.getElementById('tag_name').value.trim();
            if (!tagName) {
                e.preventDefault();
                alert('Por favor, insira um nome para a tag');
                document.getElementById('tag_name').focus();
            } else if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i data-lucide="loader" class="animate-spin w-4 h-4 mr-2"></i> Salvando...';
                if (window.lucide) window.lucide.createIcons();
            }
        });
    }
    
     // Inicializar ícones do Lucide (se necessário)
     if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Verificar se há mensagens de sucesso no DOM e fechar o modal
    const successMessages = document.querySelectorAll('.bg-green-100.text-green-700');
    if (successMessages.length > 0) {
        tagModal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
});