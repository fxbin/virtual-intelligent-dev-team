  const slides = Array.from(document.querySelectorAll('.slide'));
  const stageViewport = document.getElementById('stageViewport');
  const overviewWall = document.getElementById('overviewWall');
  const dotNav = document.getElementById('dotNav');
  let current = 0;
  let controlsTimer = null;

  function setMode(mode, slideIndex = current) {
    document.body.dataset.mode = mode;
    if (mode === 'present') {
      show(slideIndex);
      requestAnimationFrame(scaleStage);
    } else {
      document.body.classList.remove('controls-visible');
      document.exitFullscreen?.().catch(() => {});
      requestAnimationFrame(scaleOverviewPreviews);
    }
  }

  function show(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, slideIndex) => slide.classList.toggle('active', slideIndex === current));
    Array.from(dotNav.children).forEach((dot, dotIndex) => dot.classList.toggle('active', dotIndex === current));
  }

  function next() { show((current + 1) % slides.length); }
  function prev() { show((current - 1 + slides.length) % slides.length); }

  function scaleStage() {
    const scale = Math.min(window.innerWidth / 1600, window.innerHeight / 900);
    stageViewport.style.transform = `translate(-50%, -50%) scale(${scale})`;
  }

  function scaleOverviewPreviews() {
    document.querySelectorAll('.overview-preview').forEach((preview) => {
      const slide = preview.querySelector('.slide');
      if (slide) slide.style.setProperty('--preview-scale', preview.clientWidth / 1600);
    });
  }

  function buildOverview() {
    slides.forEach((slide, index) => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'overview-card';
      card.setAttribute('aria-label', `打开第 ${index + 1} 页：${slide.dataset.title}`);

      const preview = document.createElement('div');
      preview.className = 'overview-preview';
      const clone = slide.cloneNode(true);
      clone.classList.remove('active');
      preview.appendChild(clone);

      const meta = document.createElement('div');
      meta.className = 'overview-card-meta';
      meta.innerHTML = `<span>${String(index + 1).padStart(2, '0')}</span><span>${slide.dataset.role}</span>`;

      card.append(preview, meta);
      card.addEventListener('click', () => setMode('present', index));
      overviewWall.appendChild(card);

      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'dot-button';
      dot.setAttribute('aria-label', `跳转到第 ${index + 1} 页`);
      dot.addEventListener('click', () => show(index));
      dotNav.appendChild(dot);
    });
  }

  document.getElementById('startPresentation').addEventListener('click', () => setMode('present', 0));
  document.getElementById('overviewButton').addEventListener('click', () => setMode('overview'));
  document.getElementById('prevButton').addEventListener('click', prev);
  document.getElementById('nextButton').addEventListener('click', next);
  document.getElementById('fullscreenButton').addEventListener('click', () => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
  });

  document.addEventListener('keydown', (event) => {
    const mode = document.body.dataset.mode;
    if (event.key === 'Escape' || event.key.toLowerCase() === 'o') {
      if (mode === 'present') setMode('overview');
      return;
    }
    if (mode !== 'present' && event.key === 'Enter') {
      setMode('present', current);
      return;
    }
    if (mode !== 'present') return;
    if (event.key === 'ArrowRight' || event.key === ' ' || event.key === 'PageDown') {
      event.preventDefault();
      next();
    } else if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
      event.preventDefault();
      prev();
    } else if (event.key === 'Home') {
      show(0);
    } else if (event.key === 'End') {
      show(slides.length - 1);
    } else if (event.key.toLowerCase() === 'f') {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    }
  });

  function revealControls() {
    if (document.body.dataset.mode !== 'present') return;
    document.body.classList.add('controls-visible');
    window.clearTimeout(controlsTimer);
    controlsTimer = window.setTimeout(() => document.body.classList.remove('controls-visible'), 1800);
  }

  document.addEventListener('pointermove', revealControls, { passive: true });
  document.addEventListener('pointerdown', revealControls, { passive: true });

  window.addEventListener('resize', () => {
    if (document.body.dataset.mode === 'present') scaleStage();
    else scaleOverviewPreviews();
  });

  buildOverview();
  show(0);
  scaleOverviewPreviews();
