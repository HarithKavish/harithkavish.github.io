document.addEventListener('DOMContentLoaded', function() {
    // Animation for planet cards on scroll
    const cards = document.querySelectorAll('.planet-card, .dwarf-planet-card, .moon-card');

    function animateCards() {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const windowHeight = window.innerHeight;

            if (rect.top < windowHeight - 100 && rect.bottom > 100) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    }

    // Initialize animations
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    // Animation on scroll
    window.addEventListener('scroll', animateCards);
    animateCards();

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add hover effects for visual feedback
    const images = document.querySelectorAll('.planet-image, .dwarf-image, .moon-image');
    images.forEach(image => {
        image.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.03)';
        });

        image.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});