/* ================= PDF.JS SETUP ================= */
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

/* ================= STATE ================= */
let pdfDoc = null;
let currentFile = "";
let baseScale = 1.3;
let currentZoom = 1.0;

/* ================= DOM READY ================= */
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("pdfPagesContainer");
  const totalPagesEl = document.getElementById("totalPages");
  const zoomLevel = document.getElementById("zoomLevel");

  const loadingEl = document.getElementById("pdfLoading");
  const errorEl = document.getElementById("pdfError");
  const retryBtn = document.getElementById("retryBtn");
  const activeTitle = document.getElementById("activeReportTitle");

  /* ================= YEAR TABS ================= */
  document.querySelectorAll(".year-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".year-tab").forEach(t =>
        t.classList.remove("active")
      );
      tab.classList.add("active");
      
      const year = tab.dataset.year;
      if(activeTitle) activeTitle.textContent = `FY ${year} Audited Report`;

      // Reset zoom
      currentZoom = 1.0;
      updateZoomTransform();

      loadPDF(tab.dataset.file);
    });
  });

  /* ================= TOOLBAR ================= */
  const zoomInBtn = document.getElementById("zoomIn");
  if(zoomInBtn) {
    zoomInBtn.onclick = () => {
      if(currentZoom < 2.5) {
        currentZoom += 0.2;
        updateZoomTransform();
      }
    };
  }

  const zoomOutBtn = document.getElementById("zoomOut");
  if(zoomOutBtn) {
    zoomOutBtn.onclick = () => {
      if (currentZoom > 0.6) {
        currentZoom -= 0.2;
        updateZoomTransform();
      }
    };
  }

  const fullscreenBtn = document.getElementById("fullscreenBtn");
  if(fullscreenBtn) {
    fullscreenBtn.onclick = () => {
      const viewer = document.getElementById("reportViewer");
      if (!document.fullscreenElement) {
        viewer.requestFullscreen().catch(err => {
          console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
      } else {
        document.exitFullscreen();
      }
    };
  }
  
  if(retryBtn) {
    retryBtn.onclick = () => {
      if(currentFile) loadPDF(currentFile);
    };
  }

  /* ================= LOAD FIRST PDF ================= */
  const firstTab = document.querySelector(".year-tab.active");
  if (firstTab) {
    loadPDF(firstTab.dataset.file);
  }

  /* ================= FUNCTIONS ================= */

  function updateZoomTransform() {
    container.style.transform = `scale(${currentZoom})`;
    if(zoomLevel) {
      zoomLevel.textContent = Math.round(currentZoom * 100) + "%";
    }
  }

  async function loadPDF(file) {
    currentFile = file;
    showLoading(true);
    hideError();
    
    // Clear existing pages
    container.innerHTML = "";
    container.style.transform = `scale(1)`;
    if(zoomLevel) zoomLevel.textContent = "100%";

    try {
      pdfDoc = await pdfjsLib.getDocument(file).promise;
      const numPages = pdfDoc.numPages;
      if(totalPagesEl) totalPagesEl.textContent = numPages;

      // Create canvas for each page immediately so scrollbar appears
      for (let i = 1; i <= numPages; i++) {
        const pageWrapper = document.createElement("div");
        pageWrapper.className = "bg-white shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] rounded-sm overflow-hidden flex items-center justify-center";
        pageWrapper.style.minHeight = "800px"; // Placeholder height
        pageWrapper.style.width = "auto";
        
        const canvas = document.createElement("canvas");
        canvas.style.display = "block";
        pageWrapper.appendChild(canvas);
        container.appendChild(pageWrapper);
        
        // Render asynchronously
        renderSinglePage(i, canvas, pageWrapper);
      }
      
    } catch (err) {
      console.error("PDF load error:", err);
      showError();
    } finally {
      showLoading(false);
    }
  }

  async function renderSinglePage(pageNum, canvas, wrapper) {
    try {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: baseScale });
      
      // High DPI (Retina) support for crystal clear rendering
      const outputScale = window.devicePixelRatio || 1;
      
      canvas.width = Math.floor(viewport.width * outputScale);
      canvas.height = Math.floor(viewport.height * outputScale);
      canvas.style.width = Math.floor(viewport.width) + "px";
      canvas.style.height = Math.floor(viewport.height) + "px";
      
      // Remove placeholder height now that we know the aspect ratio
      wrapper.style.minHeight = "auto";

      const transform = outputScale !== 1
        ? [outputScale, 0, 0, outputScale, 0, 0]
        : null;

      const renderContext = {
        canvasContext: canvas.getContext("2d"),
        transform: transform,
        viewport: viewport
      };

      await page.render(renderContext).promise;
    } catch (err) {
      console.error(`Error rendering page ${pageNum}:`, err);
    }
  }

  function showLoading(show) {
    if(show) {
      loadingEl.classList.remove("hidden");
    } else {
      loadingEl.classList.add("hidden");
    }
  }

  function showError() {
    errorEl.classList.remove("hidden");
  }

  function hideError() {
    errorEl.classList.add("hidden");
  }
});
