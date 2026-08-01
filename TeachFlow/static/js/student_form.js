document.addEventListener('DOMContentLoaded', () => {
    const birthDateInput = document.getElementById('birth_date_input');

    if (!birthDateInput || typeof flatpickr === 'undefined') {
        return;
    }

    function createValidDate(day, month, year) {
        const parsedDay = Number(day);
        const parsedMonth = Number(month);
        const parsedYear = Number(year);

        if (
            !Number.isInteger(parsedDay) ||
            !Number.isInteger(parsedMonth) ||
            !Number.isInteger(parsedYear)
        ) {
            return undefined;
        }

        const date = new Date(
            parsedYear,
            parsedMonth - 1,
            parsedDay
        );

        const isValidDate =
            date.getFullYear() === parsedYear &&
            date.getMonth() === parsedMonth - 1 &&
            date.getDate() === parsedDay;

        return isValidDate ? date : undefined;
    }

    function parseBirthDate(dateString) {
        if (!dateString) {
            return undefined;
        }

        const normalizedValue = dateString.trim();

        // Formato digitado pelo usuário: dd/mm/aaaa
        const brazilianDateMatch = normalizedValue.match(
            /^(\d{2})\/(\d{2})\/(\d{4})$/
        );

        if (brazilianDateMatch) {
            return createValidDate(
                brazilianDateMatch[1],
                brazilianDateMatch[2],
                brazilianDateMatch[3]
            );
        }

        // Formato interno enviado ao Django: aaaa-mm-dd
        const isoDateMatch = normalizedValue.match(
            /^(\d{4})-(\d{2})-(\d{2})$/
        );

        if (isoDateMatch) {
            return createValidDate(
                isoDateMatch[3],
                isoDateMatch[2],
                isoDateMatch[1]
            );
        }

        return undefined;
    }

    function applyDateMask(event) {
        const input = event.currentTarget;
        const digits = input.value.replace(/\D/g, '').slice(0, 8);

        let maskedValue = digits;

        if (digits.length > 2) {
            maskedValue = `${digits.slice(0, 2)}/${digits.slice(2)}`;
        }

        if (digits.length > 4) {
            maskedValue =
                `${digits.slice(0, 2)}/` +
                `${digits.slice(2, 4)}/` +
                `${digits.slice(4)}`;
        }

        input.value = maskedValue;
    }

    flatpickr(birthDateInput, {
        locale: 'pt',
        dateFormat: 'Y-m-d',
        altInput: true,
        altFormat: 'd/m/Y',
        allowInput: true,
        maxDate: 'today',
        disableMobile: true,
        monthSelectorType: 'dropdown',
        static: true,

        parseDate(dateString) {
            return parseBirthDate(dateString);
        },

        onReady(selectedDates, dateStr, instance) {
            const wrapper = instance.element.closest('.flatpickr-wrapper');

            if (wrapper) {
                wrapper.classList.add('block', 'w-full');
            }

            if (!instance.altInput) {
                return;
            }

            instance.altInput.classList.add('w-full');
            instance.altInput.placeholder = 'dd/mm/aaaa';
            instance.altInput.inputMode = 'numeric';
            instance.altInput.maxLength = 10;

            instance.altInput.addEventListener('input', applyDateMask);

            instance.altInput.addEventListener('blur', () => {
                const typedValue = instance.altInput.value.trim();

                if (!typedValue) {
                    instance.clear();
                    return;
                }

                if (typedValue.length !== 10) {
                    return;
                }

                const parsedDate = parseBirthDate(typedValue);

                if (parsedDate) {
                    instance.setDate(parsedDate, true);
                }
            });
        },
    });
});