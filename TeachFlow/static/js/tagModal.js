document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const addTagsBtn = document.getElementById('add-tags-btn');
    const tagModal = document.getElementById('tag-modal');
    const closeModalBtn = document.getElementById('close-tag-modal');
    const cancelModalBtn = document.getElementById('cancel-tag-modal');
    const tagForm = document.getElementById('tag-form');
    
    // Verifica se os elementos existem
    if (!addTagsBtn || !tagModal) return;
    
    // Abrir modal
    addTagsBtn.addEventListener('click', function(e) {
        e.preventDefault();
        openModal();
    });
    
    // Função para abrir modal
    function openModal() {
        tagModal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        document.getElementById('tag_name').focus();
    }
    
    // Função para fechar modal
    function closeModal() {
        tagModal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        addTagsBtn.focus();
        tagForm.reset(); // Limpa o formulário
    }
    
    // Event listeners para fechar
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    
    // Fechar com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !tagModal.classList.contains('hidden')) {
            closeModal();
        }
    });
    
    // Fechar ao clicar fora
    tagModal.addEventListener('click', function(e) {
        if (e.target === tagModal) {
            closeModal();
        }
    });
    
    // Validação do formulário
    if (tagForm) {
        tagForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const tagNameInput = document.getElementById('tag_name');
            const tagName = tagNameInput.value.trim().toLowerCase(); // Converte para minúsculo
            
            if (!tagName) {
                alert('Por favor, insira um nome para a tag');
                tagNameInput.focus();
                return;
            }
            
            try {
                // Verifica se tag já existe
                const response = await fetch(`/api/check-tag/?name=${encodeURIComponent(tagName)}`);
                const data = await response.json();
                
                if (data.exists) {
                    alert('Esta tag já existe!');
                    return;
                }
                
                // Envia o formulário se a tag não existir
                tagForm.submit();
                
            } catch (error) {
                console.error('Erro ao verificar tag:', error);
                // Envia mesmo sem verificação (fallback)
                tagForm.submit();
            }
        });
    }
    
    // Inicializar ícones
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});