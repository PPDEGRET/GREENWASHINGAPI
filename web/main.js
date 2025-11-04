const APP_URL = "http://localhost:8501";

document.addEventListener('DOMContentLoaded', () => {
    const openAppBtn = document.getElementById('open-app-btn');
    if (openAppBtn) {
        openAppBtn.addEventListener('click', () => {
            window.location.href = APP_URL;
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
