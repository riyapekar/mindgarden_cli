# 🌱 MindGarden

**MindGarden** is a calming, minimalist Python application designed to help users reflect, track emotions, and cultivate mental clarity through journaling and self-awareness.

---

## 🧠 Overview

MindGarden offers a simple yet elegant interface to:

- Record daily reflections and gratitude
- Track emotional states (inspired by Plutchik's Wheel)
- Visualize your mental wellness over time (optional)
- Encourage mindful self-growth

Ideal for personal use or as a base for mental health-focused apps and bots.

---

## ✨ Features

- 📓 Text-based journaling system
- 🌈 Emotion tracker with Plutchik model
- 🧘‍♀️ Clean, distraction-free CLI or GUI (e.g. Tkinter)
- 📊 Data saved locally as JSON or CSV
- 🛡️ Privacy-first — no internet connection required

---

## 🛠️ Tech Stack

- **Language:** Python 3+
- **Optional GUI:** Tkinter or PyQt (if enabled)
- **Data Storage:** JSON / CSV files
- **Dependencies:** See [`requirements.txt`](requirements.txt)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mindgarden.git
cd mindgarden

Set up a Virtual Environment (optional but recommended).
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies.
pip install -r requirements.txt

Project Structure.
mindgarden/
├── main.py                  # Entry point
├── journal.py               # Handles entries and formatting
├── emotion_tracker.py       # Tracks and maps emotions
├── data/
│   └── entries.json         # User reflections
├── ui/
│   └── gui.py               # Optional GUI module
├── README.md
└── requirements.txt

📬 Contributing
I welcome contributions!
Fork the repository
Create a new branch (git checkout -b feature/my-feature)
Commit your changes (git commit -m 'Add new feature')
Push and open a PR

📜 License
GNU License — see [LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html) file.

🌼 Philosophy
“Your mind is a garden. Your thoughts are the seeds. You can grow flowers or you can grow weeds.”
— Anonymous
MindGarden is built to help you grow peace, presence, and purpose.

🔗 Contact
Created with ❤️ by @valpekar

Have ideas or feedback? Open an issue or discussion!
