document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for anchor links (if any were added)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Lightbox functionality
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const closeBtn = document.querySelector('.close-btn');

    document.querySelectorAll('[data-lightbox]').forEach(img => {
        img.addEventListener('click', function () {
            lightbox.style.display = 'block';
            lightboxImg.src = this.src;
            lightboxCaption.innerHTML = this.alt;
        });
    });

    closeBtn.addEventListener('click', () => {
        lightbox.style.display = 'none';
    });

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            lightbox.style.display = 'none';
        }
    });

    // Share button dynamic URL (replace YOUR_PAGE_URL with actual page URL)
    const shareButtons = document.querySelectorAll('.share-btn');
    const currentUrl = encodeURIComponent(window.location.href);

    shareButtons.forEach(button => {
        let href = button.getAttribute('href');
        button.setAttribute('href', href.replace(/YOUR_PAGE_URL/g, currentUrl));
    });

    // Optional: Add a simple "back to top" button (not in original, but a common 'little feature')
    // const backToTopBtn = document.createElement('button');
    // backToTopBtn.textContent = '↑';
    // backToTopBtn.classList.add('back-to-top');
    // document.body.appendChild(backToTopBtn);

    // window.addEventListener('scroll', () => {
    //     if (window.pageYOffset > 300) { // Show button after scrolling 300px
    //         backToTopBtn.style.display = 'block';
    //     } else {
    //         backToTopBtn.style.display = 'none';
    //     }
    // });

    // backToTopBtn.addEventListener('click', () => {
    //     window.scrollTo({
    //         top: 0,
    //         behavior: 'smooth'
    //     });
    // });
});
