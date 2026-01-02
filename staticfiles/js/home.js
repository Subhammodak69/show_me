// Simple Carousel Logic
const slides = document.querySelectorAll('.carousel-slide');
let currentSlide = 0;

function showSlide(idx) {
    slides.forEach((s, i) => {
        s.classList.toggle('active', i === idx);
    });
}

document.getElementById('prev').onclick = () => {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
}

document.getElementById('next').onclick = () => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
};

// Optional: Auto-slide (every 3s)
setInterval(() => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}, 3000);

// Initial display
showSlide(currentSlide);
