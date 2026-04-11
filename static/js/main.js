// MMSS System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            // Проверяем, что href не равен просто '#' (невалидный селектор)
            if (href && href !== '#' && href.length > 1) {
                e.preventDefault();
                try {
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                } catch (error) {
                    // Игнорируем ошибки невалидных селекторов
                    console.warn('Invalid selector:', href);
                }
            }
            // Если href === '#', просто предотвращаем переход, но не скроллим
        });
    });

    // Number input formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value && this.step) {
                const step = parseFloat(this.step);
                const value = parseFloat(this.value);
                if (step < 1) {
                    this.value = value.toFixed(2);
                } else {
                    this.value = Math.round(value);
                }
            }
        });
    });

    // Console log for debugging
    console.log('MMSS System UI Loaded');
    console.log('Version: 1.0.0');
});



