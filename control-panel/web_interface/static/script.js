const slider = document.getElementById('carouselSlider');
const images = document.querySelectorAll('.carousel-image');
const imageCount = images.length;

function updateCarousel(index) {
    images.forEach((image, i) => {
        const offset = (i - index) * 100; 
        const opacity = i === index ? 1 : 0.5; 
        const blur = i === index ? '0px' : '5px'; 
        // Apply CSS transforms and opacity
        image.style.transform = `translateY(${offset}px)`;
        image.style.opacity = opacity;
        image.style.filter = `blur(${blur})`;
        image.style.zIndex = i === index ? 10 : 1;
    });
}

slider.addEventListener('input', function() {
    const index = this.value - 1;
    updateCarousel(index);
});

updateCarousel(slider.value - 1);
