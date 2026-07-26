/* ----------------------------------------------------
   UDAAN Society Home Page Interactive Scripts
   ---------------------------------------------------- */

// ==========================================
// 1. Hero Image Slider Component
// ==========================================
let currentSlide = 0;

const slides = [
  {
    title: "Empowering Futures, One Child at a Time.",
    highlight: "One Child",
    description: "UDAAN Society is appointed an Implementation Support Agency under Jal Jeevan Mission – Har Ghar Jal Project of Govt. of India by State Water and Sanitation Mission, Uttar Pradesh for two Districts namely Aligarh & Bulandshahr.",
    image: "/static/assets/image1.jpeg",
  },
  {
    title: "Recharging Groundwater, Securing Lives.",
    highlight: "Securing Lives",
    description: "UDAAN Society is working as a District Implementation Partner (DIP) under this project in Banda district of Uttar Pradesh and mobilizing the village community to reduce the wastage of water and recharge the groundwater.",
    image: "/static/assets/image2.jpeg",
  },
  {
    title: "Protecting Childhood, Restoring Hope.",
    highlight: "Restoring Hope",
    description: "CHILDLINE 1098 is a 24-hour emergency phone outreach service that spells hope for millions of vulnerable children across India.",
    image: "/static/assets/image3.jpeg",
  },
  {
    title: "Advocating Rights, Empowering Women.",
    highlight: "Empowering Women",
    description: "AALI (Association for Advocacy and Legal Initiatives Trust) is a women-led and women-run organization that works to protect and advance the human rights of women.",
    image: "/static/assets/image4.jpeg",
  },
  {
    title: "Uplifting Livelihoods, Fostering Independence.",
    highlight: "Fostering Independence",
    description: "UDAAN Society is working as an Implementation Agency for Aligarh Nagar Nigam for economic empowerment of street level vendors under Prime Minister Svanidhi Yojana since 2021.",
    image: "/static/assets/image5.webp",
  },
];

function changeSlide(direction) {
  currentSlide += direction;
  if (currentSlide < 0) currentSlide = slides.length - 1;
  if (currentSlide >= slides.length) currentSlide = 0;
  updateSlide();
}

function goToSlide(index) {
  currentSlide = index;
  updateSlide();
}

function updateSlide() {
  const heroContent = document.querySelector(".hero-content");
  if (!heroContent) return;

  // Smooth fade-out transitions
  heroContent.style.opacity = "0";
  heroContent.style.transform = "translateY(15px)";

  const slideImg = document.getElementById("hero-slide-image");
  if (slideImg) {
    slideImg.style.opacity = "0";
  }

  setTimeout(() => {
    // Update texts
    const h1 = heroContent.querySelector("h1");
    const p = heroContent.querySelector("p");
    const slide = slides[currentSlide];

    if (h1) {
      if (slide.highlight) {
        const regex = new RegExp(`(${slide.highlight})`, 'gi');
        h1.innerHTML = slide.title.replace(regex, `<span class="text-[#024b24] font-extrabold">$1</span>`).replace(", ", ",<br>");
      } else {
        h1.textContent = slide.title;
      }
    }
    if (p) p.textContent = slide.description;

    if (slideImg) {
      slideImg.src = slide.image;
      slideImg.style.opacity = "1";
    }

    // Fade-in back
    heroContent.style.opacity = "1";
    heroContent.style.transform = "translateY(0)";

    // Update navigation indicator dots
    document.querySelectorAll(".carousel-dot").forEach((dot, index) => {
      if (index === currentSlide) {
        dot.classList.add("bg-[#024b24]", "w-8");
        dot.classList.remove("bg-gray-300", "w-2.5");
      } else {
        dot.classList.remove("bg-[#024b24]", "w-8");
        dot.classList.add("bg-gray-300", "w-2.5");
      }
    });
  }, 250);
}

// ==========================================
// 2. Testimonial Slider & Modal Components
// ==========================================
let currentTestimonialIndex = 0;

function moveTestimonial(direction) {
  const track = document.getElementById('testimonialTrack');
  if (!track) return;
  
  const cards = track.querySelectorAll('.flex-shrink-0');
  if (cards.length === 0) return;

  const cardWidth = cards[0].offsetWidth;
  const gap = 32; // Matches gap-8 in Tailwind (32px)
  const totalWidth = cardWidth + gap;

  // Responsive visible count
  let visibleCards = 3;
  if (window.innerWidth <= 768) visibleCards = 1;
  else if (window.innerWidth <= 1024) visibleCards = 2;

  const maxIndex = Math.max(0, cards.length - visibleCards);
  currentTestimonialIndex += direction;

  // Clamp limits
  if (currentTestimonialIndex < 0) currentTestimonialIndex = 0;
  if (currentTestimonialIndex > maxIndex) currentTestimonialIndex = maxIndex;

  const translateX = -(currentTestimonialIndex * totalWidth);
  track.style.transform = `translateX(${translateX}px)`;
}

// Testimonial Modal Handlers
function openTestimonialModal(author, role, text) {
  const modal = document.getElementById('testimonial-modal');
  const modalText = document.getElementById('modal-text');
  const modalAuthor = document.getElementById('modal-author');
  const modalRole = document.getElementById('modal-role');

  if (!modal || !modalText || !modalAuthor || !modalRole) return;

  modalAuthor.textContent = author;
  modalRole.textContent = role;
  modalText.textContent = text;

  modal.classList.remove('hidden');
  // Trigger reflow for transition
  void modal.offsetWidth;
  modal.classList.add('opacity-100');
  modal.querySelector('div').classList.remove('scale-95');
}

function closeTestimonialModal(event, force = false) {
  const modal = document.getElementById('testimonial-modal');
  if (!modal) return;

  if (force || event.target === modal) {
    modal.classList.remove('opacity-100');
    modal.querySelector('div').classList.add('scale-95');
    setTimeout(() => {
      modal.classList.add('hidden');
    }, 300);
  }
}

// ==========================================
// 3. Document Loaded Setup
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  // Initialize Hero slider
  updateSlide();
  
  // Auto-advance slides every 6 seconds
  setInterval(() => changeSlide(1), 6000);

  // Re-align testimonial slider on window resize
  window.addEventListener('resize', () => {
    moveTestimonial(0);
  });
});
