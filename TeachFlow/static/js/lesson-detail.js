document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll(
        '.exercise-applied-checkbox'
    );

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            updateExerciseAppliedStatus(checkbox);
        });
    });

    function updateExerciseAppliedStatus(checkbox) {
        if (checkbox.dataset.submitting === 'true') {
            return;
        }

        const lessonId = checkbox.dataset.lessonId;
        const exerciseId = checkbox.dataset.exerciseId;
        const requestedState = checkbox.checked;
        const csrfToken = getCSRFToken();

        if (!lessonId || !exerciseId || !csrfToken) {
            revertCheckbox(checkbox, requestedState);
            console.error('Dados necessários para a requisição não foram encontrados.');
            return;
        }

        checkbox.dataset.submitting = 'true';
        checkbox.disabled = true;

        updateExerciseVisualStatus(checkbox, requestedState);

        fetch(
            `/lessons/${lessonId}/exercises/${exerciseId}/toggle-applied/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    is_applied: requestedState,
                }),
            }
        )
            .then(async (response) => {
                let data = {};

                try {
                    data = await response.json();
                } catch {
                    data = {};
                }

                if (!response.ok || !data.success) {
                    throw new Error(
                        data.message ||
                        'Não foi possível atualizar o exercício.'
                    );
                }

                checkbox.checked = data.is_applied;
                updateExerciseVisualStatus(
                    checkbox,
                    data.is_applied
                );

                updateProgressSummary({
                    appliedCount: data.applied_count,
                    totalCount: data.total_count,
                    percentage: data.percentage,
                });
            })
            .catch((error) => {
                console.error(
                    'Erro ao atualizar exercício:',
                    error
                );

                revertCheckbox(
                    checkbox,
                    requestedState
                );
            })
            .finally(() => {
                checkbox.dataset.submitting = 'false';
                checkbox.disabled = false;
            });
    }

    function updateExerciseVisualStatus(checkbox, isApplied) {
        const card = checkbox.closest(
            '[data-lesson-exercise-card]'
        );

        if (!card) {
            return;
        }

        const statusBadge = card.querySelector(
            '.exercise-status-badge'
        );
        const statusDot = card.querySelector(
            '.exercise-status-dot'
        );
        const statusText = card.querySelector(
            '.status-text'
        );

        if (!statusBadge || !statusDot || !statusText) {
            return;
        }

        statusBadge.classList.toggle(
            'bg-green-100',
            isApplied
        );
        statusBadge.classList.toggle(
            'text-green-800',
            isApplied
        );
        statusBadge.classList.toggle(
            'bg-gray-100',
            !isApplied
        );
        statusBadge.classList.toggle(
            'text-gray-600',
            !isApplied
        );

        statusDot.classList.toggle(
            'bg-green-600',
            isApplied
        );
        statusDot.classList.toggle(
            'bg-gray-400',
            !isApplied
        );

        statusText.textContent = (
            isApplied
                ? 'Aplicado'
                : 'Não aplicado'
        );
    }

    function updateProgressSummary({
        appliedCount,
        totalCount,
        percentage,
    }) {
        const appliedCountElement = document.querySelector(
            '.applied-count'
        );
        const totalCountElement = document.querySelector(
            '.total-exercises-count'
        );
        const progressBar = document.querySelector(
            '.progress-bar'
        );
        const progressText = document.querySelector(
            '.progress-text'
        );

        if (appliedCountElement) {
            appliedCountElement.textContent = appliedCount;
        }

        if (totalCountElement) {
            totalCountElement.textContent = totalCount;
        }

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }
    }

    function revertCheckbox(checkbox, requestedState) {
        checkbox.checked = !requestedState;

        updateExerciseVisualStatus(
            checkbox,
            !requestedState
        );
    }

    function getCSRFToken() {
        const csrfInput = document.querySelector(
            '[name="csrfmiddlewaretoken"]'
        );

        return csrfInput?.value || null;
    }
});