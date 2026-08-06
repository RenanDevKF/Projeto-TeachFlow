document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
    const progressBars = document.querySelectorAll('.progress-bar');
    const progressTexts = document.querySelectorAll('.progress-text');
    const appliedCounters = document.querySelectorAll('.applied-count');
    const totalCounters = document.querySelectorAll('.total-exercises-count');
    const checkboxes = document.querySelectorAll('.exercise-applied-checkbox');
    const feedback = document.getElementById('exercise-update-feedback');

    let feedbackTimeout = null;

    initTagButtons();
    initExerciseCheckboxes();

    function initTagButtons() {
        document.querySelectorAll('#add-tags-btn, #add-tags-btn-secondary').forEach(button => {
            button.addEventListener('click', () => {
                const modal = document.querySelector('#tag-modal');
                if (!modal) return;

                modal.classList.remove('hidden');
                modal.classList.add('flex');
                document.querySelector('#tag_name')?.focus();
            });
        });
    }

    function initExerciseCheckboxes() {
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => toggleExercise(checkbox));
        });
    }

    async function toggleExercise(checkbox) {
        if (checkbox.dataset.loading === 'true') return;

        const lessonId = checkbox.dataset.lessonId;
        const exerciseId = checkbox.dataset.exerciseId;
        const requestedState = checkbox.checked;

        if (!lessonId || !exerciseId || !csrfToken) {
            restoreCheckbox(checkbox, requestedState);
            showFeedback(
                'Não foi possível identificar a aula ou validar a operação. Atualize a página e tente novamente.',
                'error'
            );
            return;
        }

        checkbox.dataset.loading = 'true';
        checkbox.disabled = true;

        updateCardStatus(checkbox, requestedState);
        hideFeedback();

        try {
            const response = await fetch(
                `/lessons/${lessonId}/exercises/${exerciseId}/toggle-applied/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        is_applied: requestedState
                    })
                }
            );

            const data = await parseJsonResponse(response);

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error
                    || data.message
                    || 'Não foi possível atualizar o exercício.'
                );
            }

            checkbox.checked = data.is_applied;
            updateCardStatus(checkbox, data.is_applied);

            updateProgress(
                data.applied_count,
                data.total_count,
                data.percentage
            );
        } catch (error) {
            console.error('Erro ao atualizar exercício aplicado:', error);

            restoreCheckbox(checkbox, requestedState);

            showFeedback(
                error.message || 'Não foi possível salvar a alteração. Tente novamente.',
                'error'
            );
        } finally {
            checkbox.disabled = false;
            checkbox.dataset.loading = 'false';
        }
    }

    async function parseJsonResponse(response) {
        const contentType = response.headers.get('content-type') || '';

        if (!contentType.includes('application/json')) {
            throw new Error(
                response.ok
                    ? 'O servidor retornou uma resposta inesperada.'
                    : 'Não foi possível concluir a operação no servidor.'
            );
        }

        try {
            return await response.json();
        } catch {
            throw new Error('O servidor retornou uma resposta inválida.');
        }
    }

    function updateProgress(appliedCount, totalCount, percentage) {
        const normalizedPercentage = Number.isFinite(Number(percentage))
            ? Math.min(100, Math.max(0, Number(percentage)))
            : 0;

        appliedCounters.forEach(counter => {
            counter.textContent = appliedCount;
        });

        totalCounters.forEach(counter => {
            counter.textContent = totalCount;
        });

        progressBars.forEach(bar => {
            bar.style.width = `${normalizedPercentage}%`;
            bar.setAttribute('aria-valuenow', normalizedPercentage);
        });

        progressTexts.forEach(text => {
            text.textContent = `${normalizedPercentage}%`;
        });
    }

    function updateCardStatus(checkbox, isApplied) {
        const card = checkbox.closest('[data-lesson-exercise-card]');
        if (!card) return;

        const badge = card.querySelector(
            '[data-applied-status-badge], .exercise-status-badge'
        );
        const dot = card.querySelector(
            '[data-applied-status-dot], .exercise-status-dot'
        );
        const text = card.querySelector(
            '[data-applied-status-text], .status-text'
        );

        if (badge) {
            badge.classList.toggle('bg-green-100', isApplied);
            badge.classList.toggle('text-green-800', isApplied);
            badge.classList.toggle('bg-gray-100', !isApplied);
            badge.classList.toggle('text-gray-600', !isApplied);
        }

        if (dot) {
            dot.classList.toggle('bg-green-600', isApplied);
            dot.classList.toggle('bg-gray-400', !isApplied);
        }

        if (text) {
            text.textContent = isApplied ? 'Aplicado' : 'Não aplicado';
        }

        card.classList.toggle('opacity-80', isApplied);
    }

    function restoreCheckbox(checkbox, requestedState) {
        const previousState = !requestedState;

        checkbox.checked = previousState;
        updateCardStatus(checkbox, previousState);
    }

    function showFeedback(message, type) {
        if (!feedback) return;

        window.clearTimeout(feedbackTimeout);

        feedback.textContent = message;
        feedback.classList.remove(
            'hidden',
            'border-red-200',
            'bg-red-50',
            'text-red-700',
            'border-green-200',
            'bg-green-50',
            'text-green-700'
        );

        if (type === 'success') {
            feedback.classList.add(
                'border-green-200',
                'bg-green-50',
                'text-green-700'
            );
            feedback.setAttribute('role', 'status');
        } else {
            feedback.classList.add(
                'border-red-200',
                'bg-red-50',
                'text-red-700'
            );
            feedback.setAttribute('role', 'alert');
        }

        feedbackTimeout = window.setTimeout(() => {
            hideFeedback();
        }, 6000);
    }

    function hideFeedback() {
        if (!feedback) return;

        window.clearTimeout(feedbackTimeout);
        feedback.textContent = '';
        feedback.classList.add('hidden');
    }
});