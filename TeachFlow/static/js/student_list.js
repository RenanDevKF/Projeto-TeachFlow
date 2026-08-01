document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('student-filter-form');
    const searchInput = document.getElementById('student-search-input');
    const resultsContainer = document.getElementById('student-results');
    const classGroupFilter = document.getElementById('student-class-group-filter');

    if (!form || !searchInput || !resultsContainer) {
        return;
    }

    let timeoutId;
    let activeRequest;

    async function updateStudentResults() {
        if (activeRequest) {
            activeRequest.abort();
        }

        activeRequest = new AbortController();

        const formData = new FormData(form);
        const queryParams = new URLSearchParams(formData);
        const requestUrl = `${window.location.pathname}?${queryParams.toString()}`;

        resultsContainer.setAttribute('aria-busy', 'true');
        resultsContainer.classList.add('opacity-60');

        try {
            const response = await fetch(requestUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                signal: activeRequest.signal,
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const html = await response.text();
            const documentParser = new DOMParser();
            const newDocument = documentParser.parseFromString(html, 'text/html');
            const newResults = newDocument.getElementById('student-results');

            if (!newResults) {
                throw new Error('A área de resultados não foi encontrada na resposta.');
            }

            resultsContainer.innerHTML = newResults.innerHTML;
            window.history.replaceState({}, '', requestUrl);

            if (window.lucide) {
                window.lucide.createIcons();
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Erro ao atualizar a lista de alunos:', error);
            }
        } finally {
            if (!activeRequest.signal.aborted) {
                resultsContainer.removeAttribute('aria-busy');
                resultsContainer.classList.remove('opacity-60');
            }
        }
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(timeoutId);

        timeoutId = setTimeout(() => {
            updateStudentResults();
        }, 300);
    });

    if (classGroupFilter) {
        classGroupFilter.addEventListener('change', () => {
            updateStudentResults();
        });
    }
});