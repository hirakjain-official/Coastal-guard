// App UI helpers: toasts, simple modal, image preview
(function () {
  window.showToast = function (message, type = 'info', timeout = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const span = document.createElement('span');
    span.textContent = message;
    const btn = document.createElement('button');
    btn.className = 'toast-close';
    btn.innerHTML = '&times;';
    btn.onclick = () => toast.remove();

    toast.appendChild(span);
    toast.appendChild(btn);
    container.appendChild(toast);

    setTimeout(() => toast.remove(), timeout);
  };

  // Image preview for uploads
  window.bindImagePreview = function (inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener('change', () => {
      const file = input.files && input.files[0];
      if (!file) {
        preview.innerHTML = '';
        return;
      }
      const allowed = ['image/jpeg', 'image/png', 'image/webp'];
      if (!allowed.includes(file.type)) {
        showToast('Unsupported image type. Use JPG/PNG/WEBP.', 'warning');
        input.value = '';
        preview.innerHTML = '';
        return;
      }
      if (file.size > 8 * 1024 * 1024) {
        showToast('Image too large. Max 8MB.', 'warning');
        input.value = '';
        preview.innerHTML = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
      };
      reader.readAsDataURL(file);
    });
  };
})();

