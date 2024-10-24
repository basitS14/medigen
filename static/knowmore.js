let currentSlide = 0;
const slideInterval = 3000; // 3 seconds

function moveSlide(step) {
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;
    currentSlide = (currentSlide + step + totalSlides) % totalSlides;
    const slider = document.querySelector('.slider');
    slider.style.transform = `translateX(-${currentSlide * 100}%)`;
}

// Move to the next slide every 3 seconds
setInterval(() => moveSlide(1), slideInterval);
