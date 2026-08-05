# Interactive HTML Presentation Creator 🎨🚀

An Agent Skill that empowers AI agents to deconstruct research papers, technical articles, and textbook sections into stunning, interactive, single-file HTML slide decks.

Inspired by state-of-the-art command-center aesthetics, this skill turns dense technical topics into engaging visual experiences featuring live HTML5 canvas simulations, mathematical equations, and interactive controls.

---

## 📦 Installation

Add this skill to your AI coding agent using the `skills` CLI:

```bash
npx skills add <your-github-username>/<your-repo-name>
```

---

## ✨ Features

- 🎨 **Perplexity & Command-Center Aesthetic**: Sleek dark mode palette, `Space Grotesk` headings, `JetBrains Mono` code markers, and `32px` rounded card containers.
- ⚡ **Interactive Demonstrations**: Embedded HTML5 `<canvas>` simulations with interactive sliders, play/pause controls, and preset state buttons.
- 📐 **MathJax Math Rendering**: Native, beautifully rendered LaTeX equations ($E=mc^2$) integrated directly into slides.
- 📦 **Single-File Portable Output**: Compiles the entire presentation into a standalone `artifact/index.html` file with zero external dependencies required at runtime.
- 📱 **Responsive Grid Layout**: Adaptive multi-column grid layout built with modern Vanilla CSS.

---

## 🚀 How to Use

Once installed, prompt your AI agent with a research paper, article link, or technical concept:

> *"Read this paper on Transformer Architectures and generate an interactive HTML presentation explaining self-attention mechanism."*

The agent will read the source material and produce a complete slide deck in `artifact/index.html`.

---

## 🛠️ Design System & Tech Stack

| Component | Technology / Style |
| :--- | :--- |
| **Typography** | Space Grotesk (Sans-serif) & JetBrains Mono (Monospace) |
| **Math Engine** | MathJax v3 |
| **Graphics** | HTML5 2D Canvas API |
| **Styling** | Modern Vanilla CSS (Variables, Glassmorphism, Rounded 32px) |
| **Output Format** | Self-contained Single-file HTML (`artifact/index.html`) |

---

## 🙏 Acknowledgements & Inspiration

Special thanks to **[@username](https://github.com/username)** whose work and vision inspired the creation of this skill! 🌟

---

## 📄 License

MIT License. Feel free to use and customize for your own agent workflows!
