import re
import os

filepath = "/Users/anandkumarmishra/Downloads/UDAAN/templates/campaigns/start_campaign.html"
with open(filepath, "r") as f:
    content = f.read()

# 1. Add Cropper CSS/JS
if "cropper.min.css" not in content:
    content = content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" />\n<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>'
    )

# 2. Add Cropper Modal HTML before <script>
if "cropper-modal" not in content:
    modal_html = """
        <!-- Cropper Modal -->
        <div id="cropper-modal" class="fixed inset-0 z-50 hidden flex items-center justify-center bg-slate-900/80 p-4">
          <div class="bg-white rounded-3xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
            <div class="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <h3 class="text-lg font-bold text-slate-900"><i class="fa-solid fa-crop-simple text-blue-600 mr-2"></i> Crop Campaign Cover</h3>
              <button type="button" onclick="closeCropper()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-xl"></i></button>
            </div>
            <div class="p-4 bg-slate-100 flex-grow relative overflow-hidden flex flex-col items-center justify-center" style="min-height: 300px;">
              <p class="text-xs font-bold text-slate-500 text-center mb-2">Adjust the image so the important subject is inside the frame (16:9 ratio)</p>
              <div class="w-full max-w-2xl h-[50vh] sm:h-[60vh] bg-slate-200 rounded-xl overflow-hidden border-2 border-slate-300">
                <img id="cropper-image" src="" alt="Crop Preview" class="max-w-full hidden">
              </div>
            </div>
            <div class="p-4 border-t border-slate-200 bg-white flex justify-between items-center gap-4">
              <button type="button" onclick="resetCropper()" class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50"><i class="fa-solid fa-rotate-left mr-1"></i> Reset</button>
              <div class="flex gap-3">
                <button type="button" onclick="closeCropper()" class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50">Cancel</button>
                <button type="button" onclick="applyCrop()" class="btn-primary-blue text-white px-6 py-2.5 rounded-xl text-xs font-bold transition">Apply Crop</button>
              </div>
            </div>
          </div>
        </div>
"""
    content = content.replace("    </div>\n\n  </div>", modal_html + "\n    </div>\n\n  </div>")

# 3. Change Account Number Validation inputs
content = content.replace(
    '<input type="text" id="input-bank-acc-confirm" placeholder="Re-enter Account Number"',
    '<input type="password" id="input-bank-acc-confirm" oninput="checkAccountMatch()" placeholder="Re-enter Account Number"'
)
content = content.replace(
    '<input type="password" id="input-bank-acc" placeholder="Account Number"',
    '<input type="password" id="input-bank-acc" oninput="checkAccountMatch()" placeholder="Account Number"'
)

# 4. Add account match message
if "acc-match-msg" not in content:
    content = content.replace(
        'id="input-bank-acc-confirm" oninput="checkAccountMatch()" placeholder="Re-enter Account Number" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none bg-slate-50/50" required />',
        'id="input-bank-acc-confirm" oninput="checkAccountMatch()" placeholder="Re-enter Account Number" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none bg-slate-50/50" required />\n                <p id="acc-match-msg" class="text-[11px] font-bold mt-1 hidden"></p>'
    )

# 5. Fix Document and Gallery functions, Cropper logic, IFSC
# We will inject the new JS logic at the end of the file.
js_injections = """
  let cropperInstance = null;
  let finalCroppedBlob = null;
  let selectedDocs = [];
  
  function checkAccountMatch() {
    const acc = document.getElementById('input-bank-acc').value;
    const conf = document.getElementById('input-bank-acc-confirm').value;
    const msg = document.getElementById('acc-match-msg');
    const btn = document.getElementById('btn-submit');
    if (!acc || !conf) {
      msg.classList.add('hidden');
      return;
    }
    msg.classList.remove('hidden');
    if (acc === conf) {
      msg.innerText = "✓ Account numbers match";
      msg.className = "text-[11px] font-bold mt-1 text-emerald-600";
      if(btn) btn.disabled = false;
    } else {
      msg.innerText = "✗ Account numbers do not match";
      msg.className = "text-[11px] font-bold mt-1 text-rose-600";
      if(btn) btn.disabled = true;
    }
  }

  function handlePatientPhotoUpload(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(evt) {
        const modal = document.getElementById('cropper-modal');
        const img = document.getElementById('cropper-image');
        img.src = evt.target.result;
        img.classList.remove('hidden');
        modal.classList.remove('hidden');
        
        if (cropperInstance) cropperInstance.destroy();
        cropperInstance = new Cropper(img, {
          aspectRatio: 16 / 9,
          viewMode: 1,
          autoCropArea: 1,
          responsive: true,
          guides: true,
          center: true,
          highlight: false,
          background: true,
          minCropBoxWidth: 300
        });
      };
      reader.readAsDataURL(file);
    }
  }

  function closeCropper() {
    document.getElementById('cropper-modal').classList.add('hidden');
    if (cropperInstance) cropperInstance.destroy();
    document.getElementById('input-patient-photo').value = ""; // reset
  }

  function resetCropper() {
    if (cropperInstance) cropperInstance.reset();
  }

  function applyCrop() {
    if (cropperInstance) {
      const canvas = cropperInstance.getCroppedCanvas({
        minWidth: 1200,
        minHeight: 675,
        fillColor: '#fff',
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high',
      });
      canvas.toBlob(function(blob) {
        finalCroppedBlob = blob;
        
        // Show preview
        const url = URL.createObjectURL(blob);
        let previewImg = document.getElementById('preview-photo');
        if(!previewImg) {
            // create preview if doesn't exist
            const tag = document.getElementById('photo-preview-tag');
            if (tag) tag.innerHTML = `<img src="${url}" class="h-24 object-cover rounded mt-2 border border-blue-200"> <br> <span class="text-blue-700">✓ Cropped Image Selected</span>`;
            tag.classList.remove('hidden');
        } else {
            previewImg.src = url;
            const tag = document.getElementById('photo-preview-tag');
            if (tag) tag.classList.remove('hidden');
        }
        
        closeCropper();
      }, 'image/jpeg', 0.9);
    }
  }

  function handleGalleryPhotosUpload(e) {
    const files = e.target.files;
    const container = document.getElementById('gallery-preview-container');
    if (!container) return;
    container.innerHTML = '';
    if (files.length > 0) {
      container.classList.remove('hidden');
      Array.from(files).forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(evt) {
          const div = document.createElement('div');
          div.className = "relative rounded-xl overflow-hidden h-16 border border-slate-200 bg-slate-100 shadow-sm";
          div.innerHTML = `<img src="${evt.target.result}" class="w-full h-full object-contain"><span class="absolute bottom-0 inset-x-0 bg-slate-900/70 text-white text-[9px] text-center font-bold truncate px-1">#${index+1}</span>`;
          container.appendChild(div);
        };
        reader.readAsDataURL(file);
      });
    } else {
      container.classList.add('hidden');
    }
  }

  function handleDocsUpload(e) {
    const files = e.target.files;
    const container = document.getElementById('docs-preview-container');
    if (!container) return;
    
    // Convert FileList to Array and add to selectedDocs
    const newFiles = Array.from(files);
    selectedDocs = [...selectedDocs, ...newFiles];
    renderDocsPreview();
  }

  function removeDoc(index) {
    selectedDocs.splice(index, 1);
    renderDocsPreview();
  }

  function renderDocsPreview() {
    const container = document.getElementById('docs-preview-container');
    container.innerHTML = '';
    if (selectedDocs.length > 0) {
      container.classList.remove('hidden');
      selectedDocs.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = "flex items-center justify-between p-2 rounded-xl border border-slate-200 bg-slate-50 text-xs font-semibold text-slate-700";
        item.innerHTML = `<span class="flex items-center gap-2 truncate"><i class="fa-solid fa-file-pdf text-rose-500"></i> ${file.name}</span>
                          <div class="flex items-center gap-2">
                             <span class="text-[10px] text-slate-400 bg-white px-2 py-0.5 rounded border">${(file.size/1024).toFixed(0)} KB</span>
                             <button type="button" onclick="removeDoc(${index})" class="text-rose-500 hover:text-rose-700"><i class="fa-solid fa-xmark"></i></button>
                          </div>`;
        container.appendChild(item);
      });
    } else {
      container.classList.add('hidden');
    }
  }

  function checkIFSC() {
    const ifscInput = document.getElementById('input-ifsc');
    if (!ifscInput) return;
    const code = ifscInput.value.trim().toUpperCase();
    if (!code) return;
    const btn = document.getElementById('btn-submit');
    if(btn) btn.disabled = true; // wait for check
    
    fetch(`/api/verify-ifsc/?code=${code}`)
      .then(r => r.json())
      .then(data => {
        const status = document.getElementById('ifsc-status');
        const branch = document.getElementById('ifsc-branch-info');
        if (data.valid) {
          if (status) {
            status.innerText = "✓ IFSC Verified";
            status.className = "text-xs font-bold text-emerald-600";
            status.classList.remove('hidden');
          }
          if (branch) {
             branch.innerHTML = `Bank: <b>${data.bank_name}</b><br>Branch: <b>${data.branch}</b><br>City: <b>${data.city}</b>, <b>${data.state}</b>`;
             branch.className = "text-[11px] text-emerald-700 mt-2 bg-emerald-50 p-2 rounded border border-emerald-100";
          }
          if(btn) btn.disabled = false;
        } else {
          if (status) {
             status.innerText = "✗ Invalid IFSC";
             status.className = "text-xs font-bold text-rose-600";
             status.classList.remove('hidden');
          }
          if (branch) {
             branch.innerText = data.message || "Could not verify IFSC.";
             branch.className = "text-[11px] text-rose-600 mt-1";
          }
        }
      })
      .catch(() => {
        alert("IFSC verification server error");
        if(btn) btn.disabled = false;
      });
  }
"""

# Replace the specific functions entirely
content = re.sub(r'function handlePatientPhotoUpload\(e\) \{.*?\n  \}', '', content, flags=re.DOTALL)
content = re.sub(r'function handleGalleryPhotosUpload\(e\) \{.*?\n  \}', '', content, flags=re.DOTALL)
content = re.sub(r'function handleDocsUpload\(e\) \{.*?\n  \}', '', content, flags=re.DOTALL)
content = re.sub(r'function checkIFSC\(\) \{.*?\n  \}', '', content, flags=re.DOTALL)

# Modify submitMedicalFundraiser to use selectedDocs and finalCroppedBlob
content = content.replace(
    "if (photoEl && photoEl.files[0]) formData.append('image', photoEl.files[0]);",
    "if (finalCroppedBlob) formData.append('image', finalCroppedBlob, 'cover.jpg');\n      else if (photoEl && photoEl.files[0]) formData.append('image', photoEl.files[0]);"
)

content = content.replace(
    "const docEl = document.getElementById('input-supporting-docs');\n      if (docEl && docEl.files) {\n        for (let i = 0; i < docEl.files.length; i++) {\n          formData.append('documents', docEl.files[i]);\n        }\n      }",
    "if (selectedDocs.length > 0) {\n        for (let i = 0; i < selectedDocs.length; i++) {\n          formData.append('documents', selectedDocs[i]);\n        }\n      }"
)

# Insert the new JS logic before submitMedicalFundraiser
content = content.replace("function submitMedicalFundraiser() {", js_injections + "\n\n  function submitMedicalFundraiser() {")

with open(filepath, "w") as f:
    f.write(content)
print("Updated frontend UI")
