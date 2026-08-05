document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
    const progressBars = document.querySelectorAll('.progress-bar');
    const progressTexts = document.querySelectorAll('.progress-text');
    const appliedCounters = document.querySelectorAll('.applied-count');
    const totalCounters = document.querySelectorAll('.total-exercises-count');
    const checkboxes = document.querySelectorAll('.exercise-applied-checkbox');

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
            return;
        }

        checkbox.dataset.loading = 'true';
        checkbox.disabled = true;

        updateCardStatus(checkbox, requestedState);

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

            const data = await response.json();

            if (!response.ok || !data.success)
                throw new Error(data.message || 'Erro ao atualizar exercício.');

            checkbox.checked = data.is_applied;

            updateCardStatus(checkbox, data.is_applied);

            updateProgress(
                data.applied_count,
                data.total_count,
                data.percentage
            );

        } catch (error) {
            console.error(error);
            restoreCheckbox(checkbox, requestedState);

        } finally {
            checkbox.disabled = false;
            checkbox.dataset.loading = 'false';
        }
    }

        function updateProgress(appliedCount, totalCount, percentage) {
        appliedCounters.forEach(counter => counter.textContent = appliedCount);
        totalCounters.forEach(counter => counter.textContent = totalCount);

        progressBars.forEach(bar => {
            bar.style.width = `${percentage}%`;
            bar.setAttribute('aria-valuenow', percentage);
        });

        progressTexts.forEach(text => {
            text.textContent = `${percentage}%`;
        });
    }

        function updateCardStatus(checkbox, isApplied) {
            const card = checkbox.closest('[data-lesson-exercise-card]');
            if (!card) return;

            const badge = card.querySelector('.exercise-status-badge');
            const dot = card.querySelector('.exercise-status-dot');
            const text = card.querySelector('.status-text');

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

            if (text)
                text.textContent = isApplied ? 'Aplicado' : 'Não aplicado';

            card.classList.toggle('opacity-80', isApplied);
        }

        function restoreCheckbox(checkbox, requestedState) {
            checkbox.checked = !requestedState;
            updateCardStatus(checkbox, !requestedState);
        }
    });