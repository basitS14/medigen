let currentSlide = 0;
const totalSlides = document.querySelectorAll('.slide').length;

function showSlide(index) {
    const slides = document.querySelector('.slides');
    currentSlide = (index + totalSlides) % totalSlides; // Wrap around

    slides.style.transform = `translateX(-${currentSlide * 100}%)`;
}

function changeSlide(direction) {
    showSlide(currentSlide + direction);
}

// Automatically change slide every 3 seconds
setInterval(() => {
    showSlide(currentSlide + 1);
}, 3000);

// Show the first slide on page load
showSlide(currentSlide);
