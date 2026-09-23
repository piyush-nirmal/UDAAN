/* ================= PDF.JS SETUP ================= */
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

/* ================= STATE ================= */
let pdfDoc = null;
let totalPages = 0;
let scale = 1;
let currentFile = "";

/* ================= DOM READY ================= */
document.addEventListener("DOMContentLoaded", () => {
  const pagesContainer = document.getElementById("pdfPagesContainer");
  const totalPagesEl = document.getElementById("totalPages");
  const zoomLevel = document.getElementById("zoomLevel");
  const activeTitleEl = document.getElementById("activeReportTitle");

  const loadingEl = document.getElementById("pdfLoading");
  const errorEl = document.getElementById("pdfError");
  const retryBtn = document.getElementById("retryBtn");

  const zoomInBtn = document.getElementById("zoomIn");
  const zoomOutBtn = document.getElementById("zoomOut");
  const fullscreenBtn = document.getElementById("fullscreenBtn");

  /* ================= YEAR TABS ================= */
  document.querySelectorAll(".year-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      if (activeTitleEl) {
        activeTitleEl.textContent = `Annual Report ${tab.dataset.year}`;
      }

      scale = 1;
      loadPDF(tab.dataset.file);
    });
  });

  /* ================= ZOOM ================= */
  if (zoomInBtn) {
    zoomInBtn.onclick = () => {
      scale = Math.min(scale + 0.2, 3);
      applyZoom();
    };
  }

  if (zoomOutBtn) {
    zoomOutBtn.onclick = () => {
      scale = Math.max(scale - 0.2, 0.6);
      applyZoom();
    };
  }

  function applyZoom() {
    if (pagesContainer) {
      pagesContainer.style.transform = `scale(${scale})`;
    }
    if (zoomLevel) {
      zoomLevel.textContent = Math.round(scale * 100) + "%";
    }
  }

  /* ================= FULLSCREEN ================= */
  if (fullscreenBtn) {
    fullscreenBtn.onclick = () => {
      const viewer = document.getElementById("reportViewer");
      if (!document.fullscreenElement) {
        viewer.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    };
  }

  /* ================= RETRY ================= */
  if (retryBtn) {
    retryBtn.onclick = () => {
      if (currentFile) {
        loadPDF(currentFile);
      }
    };
  }

  /* ================= LOAD FIRST PDF ================= */
  const firstTab = document.querySelector(".year-tab.active") ||
                    document.querySelector(".year-tab");
  if (firstTab) {
    loadPDF(firstTab.dataset.file);
  } else {
    showLoading(false);
  }

  /* ================= FUNCTIONS ================= */

  async function loadPDF(file) {
    if (!file) {
      showError();
      showLoading(false);
      return;
    }

    currentFile = file;
    scale = 1;

    showLoading(true);
    hideError();
    clearPages();

    try {
      pdfDoc = await pdfjsLib.getDocument(file).promise;
      totalPages = pdfDoc.numPages;

      if (totalPagesEl) totalPagesEl.textContent = totalPages;

      await renderAllPages();
      applyZoom();
    } catch (err) {
      console.error("PDF load error:", err);
      showError();
    } finally {
      showLoading(false);
    }
  }

  async function renderAllPages() {
    if (!pdfDoc || !pagesContainer) return;

    for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: 1.3 });

      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.className = "rounded-lg bg-white";

      pagesContainer.appendChild(canvas);

      await page.render({
        canvasContext: ctx,
        viewport
      }).promise;
    }
  }

  function clearPages() {
    if (pagesContainer) {
      pagesContainer.innerHTML = "";
    }
  }

  function showLoading(show) {
    if (!loadingEl) return;
    loadingEl.classList.toggle("loading-hidden", !show);
  }

  function showError() {
    if (errorEl) errorEl.classList.remove("hidden");
  }

  function hideError() {
    if (errorEl) errorEl.classList.add("hidden");
  }
});