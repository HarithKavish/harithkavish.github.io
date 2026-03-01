document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });

                // Update active nav link
                document.querySelectorAll('.main-nav a').forEach(link => {
                    link.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });

    // Add hover effects for planet cards
    const planetCards = document.querySelectorAll('.planet-card, .dwarf-planet-card, .moon-card, .asteroid-card, .comet-card, .space-station-card');
    planetCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.querySelector('.planet-icon, .dwarf-icon, .moon-icon, .asteroid-icon, .comet-icon, .station-icon').style.transform = 'scale(1.2)';
        });

        card.addEventListener('mouseleave', function() {
            this.querySelector('.planet-icon, .dwarf-icon, .moon-icon, .asteroid-icon, .comet-icon, .station-icon').style.transform = 'scale(1)';
        });
    });

    // Add animation to planet circles
    const circles = document.querySelectorAll('.circle');
    circles.forEach(circle => {
        circle.style.animationDelay = circle.getAttribute('data-delay') + 's';
    });

    // Add parallax effect for sections
    window.addEventListener('scroll', function() {
        const scrollPosition = window.pageYOffset;
        const sections = document.querySelectorAll('.main-content .section-header');

        sections.forEach((section, index) => {
            const speed = 0.5;
            const offset = 100;
            const yPos = -(scrollPosition + (index * offset) - window.innerHeight / speed);
            section.style.transform = `translateY(${yPos}px)`;
        });
    });

    // Add interactive solar system diagram
    const diagramImage = document.querySelector('.diagram-image');
    diagramImage.addEventListener('click', function() {
        const circles = document.querySelectorAll('.circle');
        circles.forEach((circle, index) => {
            const name = circle.getAttribute('data-name');
            const card = document.querySelector(`.planet-card[data-name="${name}"]`);
            if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    });
});