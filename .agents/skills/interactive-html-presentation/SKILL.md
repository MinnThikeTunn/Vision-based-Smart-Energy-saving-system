---
name: interactive-html-presentation
description: Read and analyze a research paper, technical write-up, or textbook section, and deconstruct it to generate a stunning, interactive, single-file HTML presentation. The presentation features custom canvas animations, mathematical equations (MathJax), responsive grid layouts, and a clean minimalist command-center design aesthetic. Use this skill whenever a user provides a research paper, article, or topic and asks to create a presentation, slide deck, talk, or interactive explanation of it.
---

# Interactive HTML Presentation Creator

This skill guides the model to read a research paper, article, or technical topic and generate a self-contained, interactive HTML slide deck explaining it. The aesthetic and functionality are inspired by premium technical presentations (like "Less is More") featuring custom canvas animations, mathematical rendering, responsive grid layouts, and a minimalist sci-fi command-center vibe.

---

## Design Principles (Perplexity Aesthetic)

To ensure the output looks highly premium and state-of-the-art:
1. **High-End Minimalist Aesthetics**:
   - **Typography**: Space Grotesk (sans-serif) for headings and text, JetBrains Mono (monospace) for technical codes, stats, and markers. Headings (`h1`, `h2`) should use `font-weight: 900` or `font-black` with tight letter-spacing.
   - **Rounded Containers**: Use `border-radius: 32px` on all major panels, cards, stages, and frame elements.
   - **Generous Whitespace**: Keep sections breathable with increased paddings (e.g., `padding: 10vh 10vw 12vh`).
   - **Micro-Animations**: Add subtle transition delays, hover transforms (`transform: translateY(-2px)`), scale effects on sliders, and fading glow effects.
2. **Accented Identity**:
   - Dynamic colors per slide (Amber, Blue, Purple, Green) mapped via `data-accent="..."` attributes to change `--accent` and `--accent-rgb`.
3. **Interactive Demonstrations**:
   - Limit raw prose to 2-3 lines (`lead` class). Let interactive HTML5 `<canvas>` elements and sliders tell the technical story.
   - For complex animations (e.g., pathing, matrix multiplication, rotations), include:
     - Preset buttons (e.g. "Slow convergence", "Optimal step", "Divergence").
     - Play/Pause toggles.
     - Single-step progress buttons.

## Output & Artifact Management

1. **Save Output Exclusively to Artifact Directory**:
   - Always generate and compile the presentation into a single, self-contained `index.html` file (or designated `.html` file).
   - You MUST write and save this file EXCLUSIVELY into the project's `artifact/` directory within the workspace root (`artifact/index.html`).
   - Do NOT save presentation files to the workspace root, `source/`, or any other directory outside of `artifact/`.


---

## Technical Architecture

### 1. Style & Core Boilerplate
The presentation must compile into a single `index.html` file using this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Presentation Title</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <!-- MathJax Configuration -->
  <script>
    window.MathJax = { tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']] }, options: { renderActions: { addMenu: [0, '', ''] } } };
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

  <style>
    :root {
      --bg: #07090e;
      --bg2: #0a0e15;
      --panel: #0c1119;
      --line: #19212f;
      --line2: #2a3547;
      --text: #e9eef5;
      --dim: #9aa7bc;
      --mute: #5d6a81;
      --mute2: #3a4559;
      --amber: #f5a623;
      --blue: #6db0f5;
      --purple: #a78bfa;
      --green: #46d07f;
      --red: #fb7185;
      --accent: var(--blue);
      --accent-rgb: 109, 176, 245;
    }
    
    html, body {
      margin: 0; padding: 0; height: 100%;
      background: var(--bg); color: var(--text);
      font-family: "Space Grotesk", sans-serif; overflow: hidden;
    }
    .deck { position: fixed; inset: 0; }
    
    #frame {
      position: fixed; inset: 16px; border: 1px solid var(--line);
      border-radius: 32px; pointer-events: none; z-index: 40;
    }
    #frame i { position: absolute; width: 15px; height: 15px; border-color: var(--line2); border-style: solid; }
    #frame i.f-tl { top: -1px; left: -1px; border-width: 1.5px 0 0 1.5px; border-top-left-radius: 32px; }
    #frame i.f-tr { top: -1px; right: -1px; border-width: 1.5px 1.5px 0 0; border-top-right-radius: 32px; }
    #frame i.f-bl { bottom: -1px; left: -1px; border-width: 0 0 1.5px 1.5px; border-bottom-left-radius: 32px; }
    #frame i.f-br { bottom: -1px; right: -1px; border-width: 0 1.5px 1.5px 0; border-bottom-right-radius: 32px; }
    
    .slide {
      position: absolute; inset: 0; display: flex; flex-direction: column;
      justify-content: center; padding: 10vh 10vw 12vh; opacity: 0;
      transform: translateY(8px); transition: opacity .42s ease, transform .42s ease;
      pointer-events: none; overflow: hidden;
    }
    .slide.active { opacity: 1; transform: none; pointer-events: auto; }
    .slide::before {
      content: ""; position: absolute; inset: 0; z-index: 0; pointer-events: none;
      background-image:
        linear-gradient(rgba(var(--accent-rgb), 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(var(--accent-rgb), 0.02) 1px, transparent 1px);
      background-size: 60px 60px;
      mask-image: radial-gradient(ellipse 80% 75% at 50% 50%, #000 45%, transparent 100%);
      -webkit-mask-image: radial-gradient(ellipse 80% 75% at 50% 50%, #000 45%, transparent 100%);
    }
    
    .slide > * { position: relative; z-index: 1; }
    
    .slide[data-accent="amber"] { --accent: var(--amber); --accent-rgb: 245, 166, 35; }
    .slide[data-accent="blue"] { --accent: var(--blue); --accent-rgb: 109, 176, 245; }
    .slide[data-accent="purple"] { --accent: var(--purple); --accent-rgb: 167, 139, 250; }
    .slide[data-accent="green"] { --accent: var(--green); --accent-rgb: 70, 208, 127; }

    .kicker {
      font-family: "JetBrains Mono", monospace; font-size: clamp(10px, 1.05vw, 13.5px);
      font-weight: 500; letter-spacing: 0.3em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 2.2vh; display: inline-flex; align-items: center; gap: 12px;
    }
    .kicker::before { content: ""; width: 8px; height: 8px; background: var(--accent); box-shadow: 0 0 9px var(--accent); border-radius: 50%; }
    
    .rule { height: 1px; background: var(--line); width: 100%; max-width: 60vw; margin: 0 0 4vh; position: relative; }
    .rule::before { content: ""; position: absolute; left: 0; top: 0; width: 64px; height: 1px; background: var(--accent); }
    
    h1 { font-weight: 900; font-size: clamp(44px, 8.5vw, 112px); line-height: 0.95; letter-spacing: -0.04em; margin: 0 0 3vh; }
    h2 { font-weight: 900; font-size: clamp(28px, 4.6vw, 60px); line-height: 1.02; letter-spacing: -0.03em; margin: 0 0 3vh; }
    .lead { font-size: clamp(16px, 1.6vw, 24px); line-height: 1.6; color: var(--dim); max-width: 32ch; }
    .footer-note { font-family: "JetBrains Mono", monospace; font-size: clamp(10px, 0.95vw, 13px); color: var(--mute); letter-spacing: 0.04em; margin-top: 4vh; }
    
    .cols2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4vw; align-items: center; }
    .cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2vw; }
    
    .card {
      background: linear-gradient(180deg, var(--panel) 0%, var(--bg2) 100%);
      border: 1px solid var(--line); border-radius: 32px; padding: 3vh 2.2vw; position: relative;
      transition: border-color 0.3s ease, transform 0.3s ease;
    }
    .card:hover { border-color: rgba(var(--accent-rgb), 0.4); transform: translateY(-2px); }
    
    .stagewrap { height: 54vh; }
    .stage {
      position: relative; background: var(--bg2); border: 1px solid var(--line); border-radius: 32px; overflow: hidden; width: 100%; height: 100%;
    }
    .stage canvas { display: block; width: 100%; height: 100%; }
    .stage .cap { position: absolute; top: 16px; left: 20px; font-family: "JetBrains Mono", monospace; font-size: clamp(9px, 0.9vw, 12px); letter-spacing: 0.2em; text-transform: uppercase; color: var(--mute); z-index: 2; }
    
    .ctl { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; margin-top: 2.2vh; }
    button.btn {
      font-family: "JetBrains Mono", monospace; font-size: clamp(10px, 1.05vw, 13.5px); letter-spacing: 0.1em; text-transform: uppercase;
      background: transparent; color: var(--accent); border: 1px solid var(--accent); padding: 8px 18px; border-radius: 32px; cursor: pointer; transition: all .2s;
    }
    button.btn:hover { background: rgba(var(--accent-rgb), 0.12); transform: scale(1.03); }
    button.btn.on { background: rgba(var(--accent-rgb), 0.16); }

    input[type=range] {
      -webkit-appearance: none; appearance: none; width: clamp(120px, 13vw, 210px); height: 2px; background: var(--line2); outline: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 15px; height: 15px; border-radius: 50%; background: var(--accent); cursor: pointer; transform: scale(1.1); box-shadow: 0 0 9px rgba(var(--accent-rgb), 0.6); transition: transform 0.15s;
    }
    input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.3); }
    
    #progress { position: fixed; left: 0; bottom: 0; height: 3px; background: var(--accent); width: 0; z-index: 50; transition: width .42s ease; box-shadow: 0 0 8px var(--accent); }
    #counter { position: fixed; right: 40px; top: 35px; font-family: "JetBrains Mono", monospace; font-size: 13px; color: var(--mute); letter-spacing: 0.12em; z-index: 50; }
    #counter b { color: var(--accent); }
    
    @media print {
      html, body { overflow: visible; height: auto; background: #fff; }
      .deck { position: static; }
      #progress, #counter, #frame { display: none !important; }
      .slide { position: relative; opacity: 1 !important; transform: none !important; page-break-after: always; height: 100vh; }
    }
  </style>
</head>
<body>
  <div id="frame">
    <i class="f-tl"></i><i class="f-tr"></i><i class="f-bl"></i><i class="f-br"></i>
  </div>

  <div class="deck" id="deck">
    <!-- Slides go here -->
  </div>

  <div id="progress"></div>
  <div id="counter">Slide <b>1</b> / 1</div>
</body>
</html>
```

### 2. Slide Navigation Logic (with Swipe Support)
Inject robust sliding logic to handle keyboard, swipe gestures, and window resizing properly:

```javascript
const slides = Array.from(document.querySelectorAll('.slide'));
let currentIdx = 0;

function showSlide(index) {
  if (index < 0 || index >= slides.length) return;
  slides[currentIdx].classList.remove('active');
  currentIdx = index;
  slides[currentIdx].classList.add('active');
  
  const progress = document.getElementById('progress');
  progress.style.width = `${((currentIdx + 1) / slides.length) * 100}%`;
  
  const counter = document.getElementById('counter');
  counter.innerHTML = `Slide <b>${currentIdx + 1}</b> / ${slides.length}`;
  
  const currentSlide = slides[currentIdx];
  const accent = getComputedStyle(currentSlide).getPropertyValue('--accent').trim();
  progress.style.background = accent;
  progress.style.boxShadow = `0 0 8px ${accent}`;
  
  window.dispatchEvent(new CustomEvent('slideChanged', { detail: { index: currentIdx, id: currentSlide.id } }));
}

// Key listeners
window.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === 'Space') {
    showSlide(currentIdx + 1);
  } else if (e.key === 'ArrowLeft') {
    showSlide(currentIdx - 1);
  }
});

// Swipe support
let touchstartX = 0;
let touchendX = 0;
window.addEventListener('touchstart', e => { touchstartX = e.changedTouches[0].screenX; }, false);
window.addEventListener('touchend', e => {
  touchendX = e.changedTouches[0].screenX;
  handleGesture();
}, false);

function handleGesture() {
  if (touchendX < touchstartX - 50) showSlide(currentIdx + 1); // Swipe left
  if (touchendX > touchstartX + 50) showSlide(currentIdx - 1); // Swipe right
}

showSlide(0);
```

### 3. Dynamic Canvas Life-cycle Control
To prevent browser performance lag, canvases should only compute animations when their slide is active:

```javascript
let animationFrameId = null;
let isAnimating = false;

function startLoop() {
  if (isAnimating) return;
  isAnimating = true;
  loop();
}

function stopLoop() {
  isAnimating = false;
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
}

function loop() {
  if (!isAnimating) return;
  // draw/update logic
  animationFrameId = requestAnimationFrame(loop);
}

window.addEventListener('slideChanged', (e) => {
  if (e.detail.id === 'interactive-slide-id') {
    startLoop();
  } else {
    stopLoop();
  }
});
```
