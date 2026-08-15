document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('id_name');
    const colorSelect = document.getElementById('id_color');
    const preview = document.getElementById('tag-color-preview');

    function updatePreview() {
        if (!preview || !colorSelect) return;

        const color = colorSelect.value || '#3B82F6';
        preview.textContent = nameInput?.value.trim() || 'Prévia da tag';
        preview.style.backgroundColor = `${color}20`;
        preview.style.color = color;
    }

    nameInput?.addEventListener('input', updatePreview);
    colorSelect?.addEventListener('change', updatePreview);
    updatePreview();
});