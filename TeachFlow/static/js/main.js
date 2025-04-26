// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Função para formatar e exibir a data atual
    function formatCurrentDate() {
      const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
      const date = new Date();
      let formattedDate = date.toLocaleDateString('pt-BR', options);
      
      // Capitalizar primeira letra
      formattedDate = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
      
      const dateElement = document.getElementById('current-date');
      if (dateElement) {
        dateElement.textContent = formattedDate;
      }
    }
  
    // Função para gerenciar tabs
    function setupTabs() {
      const tabButtons = document.querySelectorAll('.tab-button');
      const tabContents = document.querySelectorAll('.tab-content');
      
      if (tabButtons.length > 0 && tabContents.length > 0) {
        // Mostrar a primeira tab por padrão
        tabButtons[0].classList.add('active');
        document.getElementById(`${tabButtons[0].dataset.tab}-tab`).classList.add('active');
        
        tabButtons.forEach(button => {
          button.addEventListener('click', () => {
            const tab = button.dataset.tab;
            
            // Atualizar botão ativo
            tabButtons.forEach(btn => {
              btn.classList.remove('active');
              btn.classList.add('text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'border-transparent');
            });
            button.classList.remove('text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'border-transparent');
            button.classList.add('active');
            
            // Mostrar conteúdo ativo
            tabContents.forEach(content => {
              content.classList.add('hidden');
            });
            document.getElementById(`${tab}-tab`).classList.remove('hidden');
          });
        });
      }
    }
  
    // Função para confirmar ações importantes
    function setupConfirmations() {
      const confirmationButtons = document.querySelectorAll('[data-confirm]');
      
      confirmationButtons.forEach(button => {
        button.addEventListener('click', (e) => {
          const message = button.getAttribute('data-confirm') || 'Tem certeza que deseja realizar esta ação?';
          if (!confirm(message)) {
            e.preventDefault();
          }
        });
      });
    }
  
    // Função para alternar elementos
    function setupToggles() {
      const toggleButtons = document.querySelectorAll('[data-toggle]');
      
      toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
          const target = button.getAttribute('data-toggle');
          const element = document.getElementById(target);
          
          if (element) {
            element.classList.toggle('hidden');
            
            // Atualizar ícone se existir
            const icon = button.querySelector('svg');
            if (icon) {
              const showIcon = button.getAttribute('data-show-icon');
              const hideIcon = button.getAttribute('data-hide-icon');
              
              if (element.classList.contains('hidden') && hideIcon) {
                icon.innerHTML = hideIcon;
              } else if (showIcon) {
                icon.innerHTML = showIcon;
              }
            }
          }
        });
      });
    }
  
    // Função para máscaras de campos
    function setupMasks() {
      // Máscara para telefone
      const phoneInputs = document.querySelectorAll('input[type="tel"]');
      
      phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
          let value = e.target.value.replace(/\D/g, '');
          value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
          value = value.replace(/(\d)(\d{4})$/, '$1-$2');
          e.target.value = value;
        });
      });
    }
  
    // Função para busca dinâmica
    function setupSearch() {
      const searchInputs = document.querySelectorAll('[data-search]');
      
      searchInputs.forEach(input => {
        input.addEventListener('input', function() {
          const searchValue = this.value.toLowerCase();
          const target = this.getAttribute('data-search');
          const items = document.querySelectorAll(target);
          
          items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchValue)) {
              item.classList.remove('hidden');
            } else {
              item.classList.add('hidden');
            }
          });
        });
      });
    }
  
    // Função para pré-carregar imagens
    function preloadImages() {
      const images = document.querySelectorAll('img[data-src]');
      
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const image = entry.target;
            image.src = image.getAttribute('data-src');
            image.removeAttribute('data-src');
            observer.unobserve(image);
          }
        });
      });
      
      images.forEach(image => {
        imageObserver.observe(image);
      });
    }
  
    // Função para mensagens flash
    function setupFlashMessages() {
      const messages = document.querySelectorAll('.alert-message');
      
      messages.forEach(message => {
        setTimeout(() => {
          message.classList.add('opacity-0');
          setTimeout(() => {
            message.remove();
          }, 500);
        }, 5000);
      });
    }
  
    // Inicializar todas as funções
    formatCurrentDate();
    setupTabs();
    setupConfirmations();
    setupToggles();
    setupMasks();
    setupSearch();
    preloadImages();
    setupFlashMessages();
  
    // Event listeners adicionais
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function() {
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.disabled = true;
          submitButton.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Salvando...';
        }
      });
    });
  });