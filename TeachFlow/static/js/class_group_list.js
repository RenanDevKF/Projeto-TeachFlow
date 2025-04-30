document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const cards = document.querySelectorAll('.group-card');

    searchInput.addEventListener('input', function () {
        const search = this.value.toLowerCase();

        cards.forEach(card => {
            const name = card.dataset.name || '';
            const school = card.dataset.school || '';
            const period = card.dataset.period || '';
            const year = card.dataset.year || '';

            const visible = [name, school, period, year].some(field => field.includes(search));

            card.style.display = visible ? 'flex' : 'none';
        });
    });
});
