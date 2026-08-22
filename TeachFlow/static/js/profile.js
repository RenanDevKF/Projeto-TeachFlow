document.addEventListener('DOMContentLoaded', () => {
    const tabList = document.querySelector('[role="tablist"]');
    const tabButtons = Array.from(document.querySelectorAll('[role="tab"]'));
    const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

    if (!tabList || !tabButtons.length || !tabPanels.length) {
        return;
    }

    function activateTab(selectedButton) {
        tabButtons.forEach(button => {
            const isSelected = button === selectedButton;

            button.setAttribute('aria-selected', String(isSelected));
            button.setAttribute('tabindex', isSelected ? '0' : '-1');

            button.classList.toggle('active', isSelected);
            button.classList.toggle('text-primary', isSelected);
            button.classList.toggle('border-b-2', isSelected);
            button.classList.toggle('border-primary', isSelected);
            button.classList.toggle('text-gray-500', !isSelected);
        });

        tabPanels.forEach(panel => {
            const isActive = panel.id === selectedButton.getAttribute('aria-controls');

            panel.classList.toggle('hidden', !isActive);
            panel.classList.toggle('active', isActive);
        });
    }

    tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            activateTab(button);
        });

        button.addEventListener('keydown', event => {
            let nextIndex = null;

            if (event.key === 'ArrowRight') {
                nextIndex = (index + 1) % tabButtons.length;
            } else if (event.key === 'ArrowLeft') {
                nextIndex = (index - 1 + tabButtons.length) % tabButtons.length;
            } else if (event.key === 'Home') {
                nextIndex = 0;
            } else if (event.key === 'End') {
                nextIndex = tabButtons.length - 1;
            }

            if (nextIndex === null) {
                return;
            }

            event.preventDefault();

            const nextButton = tabButtons[nextIndex];

            activateTab(nextButton);
            nextButton.focus();
        });
    });
});