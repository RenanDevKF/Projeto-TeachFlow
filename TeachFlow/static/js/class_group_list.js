document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const cards = document.querySelectorAll('.group-card');

    if (!searchInput || !cards.length) {
        return;
    }

    searchInput.addEventListener('input', function () {
        const search = this.value.trim().toLowerCase();

        cards.forEach(card => {
            const name = (card.dataset.name || '').toLowerCase();
            const school = (card.dataset.school || '').toLowerCase();
            const period = (card.dataset.period || '').toLowerCase();
            const year = (card.dataset.year || '').toLowerCase();

            const visible = [name, school, period, year].some(field =>
                field.includes(search)
            );

            card.style.display = visible ? 'flex' : 'none';
        });
    });
});