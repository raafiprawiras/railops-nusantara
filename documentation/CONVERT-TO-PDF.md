# Konversi Manual ke PDF

## Opsi 1: Pandoc (Recommended)

```bash
# Install pandoc (https://pandoc.org/installing.html)
# Windows: choco install pandoc
# Linux: sudo apt install pandoc
# Mac: brew install pandoc

# Konversi user manual ke PDF
pandoc documentation/user-manual.md -o documentation/manual-penggunaan.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=2.5cm \
  -V fontsize=11pt

# Konversi semua dokumentasi
pandoc documentation/user-manual.md documentation/architecture.md \
  documentation/database.md documentation/api-and-routes.md \
  -o documentation/dokumentasi-lengkap.pdf \
  --pdf-engine=xelatex \
  --toc
```

## Opsi 2: VS Code Extension

1. Install extension "Markdown PDF" di VS Code
2. Buka file .md
3. Ctrl+Shift+P → "Markdown PDF: Export (pdf)"

## Opsi 3: Browser Print

1. Buka file .md di GitHub atau VS Code preview
2. Ctrl+P → Save as PDF

## Opsi 4: Python (tanpa LaTeX)

```bash
pip install md2pdf
md2pdf documentation/user-manual.md documentation/manual-penggunaan.pdf
```

## Catatan

- Diagram Mermaid mungkin tidak render di PDF tanpa plugin khusus
- Gunakan screenshot aktual untuk menggantikan placeholder [Screenshot: ...]
- Format print-friendly sudah tersedia di halaman laporan (/reports/*)
