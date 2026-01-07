
# 🎥 yt2notes
**Convert YouTube Videos into Structured Notion-Ready Notes & PDFs with AI.**

`yt2notes` is a Python-based tool that automates the process of watching long videos. It extracts transcripts, processes them through Google's **Gemini 2.5 Flash** to create structured, educational summaries, and exports them directly to Markdown (for Notion) and PDF.

---

## ✨ Features
- **Smart Extraction:** Automatically handles standard URLs, Shorts, and Embed links.
- **AI-Powered Structuring:** Uses Gemini 2.5 Flash to transform messy transcripts into professional, hierarchical notes.
- **Notion Optimized:** Outputs clean Markdown with clear headings and bullet points.
- **PDF Export:** Generates a ready-to-share PDF version of your notes instantly.
- **Large Video Support:** Automatically chunks long transcripts to stay within AI context limits.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Ayush-Zone/yt2notes
cd yt2notes
pip install youtube-transcript-api google-genai requests pdfitdown
