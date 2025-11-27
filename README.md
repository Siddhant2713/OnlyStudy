---
title: OnlyStudies
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: app.py
pinned: false
---

# OnlyStudies 🎓✨

Turn Text into Educational Animations in Minutes.

OnlyStudies is an AI-powered platform that converts simple text descriptions into high-quality, 3-minute educational videos. It automates the entire animation pipeline—from scriptwriting to rendering—making complex concepts like Quantum Entanglement or Bubble Sort easy to understand through visual storytelling.

## 🚀 Key Features
- **Automated Video Pipeline**: Generates a complete 3-minute lesson without human intervention.
- **Intelligent Structuring**: Enforces a proven pedagogical format (Theory, Analogy, Example).
- **Smart Stitching**: Solves the AI "context window" limit by generating 3 separate scenes and stitching them into one seamless MP4.
- **Sleek UX**: A dark-mode, responsive interface with real-time terminal logs and Lottie loading animations.

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Python)
- **AI Logic**: Google Gemini 1.5 Pro (via google-generativeai)
- **Animation Engine**: Manim Community Edition
- **Video Processing**: FFmpeg & MoviePy

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- FFmpeg installed and added to your system PATH.
- LaTeX (Optional but recommended for math formulas).

### Steps
1. Clone the Repository
2. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Set Up API Keys
   Create a `.env` file based on `.env.example` and add your `GOOGLE_API_KEY`.
4. Run the App
   ```bash
   streamlit run app.py
   ```
