# 🎙️ Akura (අකුර) - AI Sinhala Voice Typer

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)

**Akura (අකුර)** is a lightweight, AI-powered Sinhala Voice Typing tool for Windows. It allows you to type in Sinhala across any application just by speaking, making it the perfect solution for those who find traditional keyboard layouts difficult.

**Akura (අකුර)** යනු පරිගණකයේ ඕනෑම මෘදුකාංගයක ඉතා පහසුවෙන් සිංහලෙන් ටයිප් කිරීමට නිර්මාණය කරන ලද AI හඬ හඳුනාගැනීමේ (Voice Recognition) මෙවලමකි. සාම්ප්‍රදායික යතුරුපුවරු හැසිරවීමට අපහසු අයට මෙය කදිම විසඳුමකි.

---

## ✨ Features | විශේෂාංග

* **🎙️ High Accuracy Speech-to-Text:** Powered by advanced recognition engines for precise Sinhala transcription.
    * *(ඉතා ඉහළ නිරවද්‍යතාවයකින් යුතුව සිංහල කථනය හඳුනාගැනීමේ හැකියාව.)*
* **🌐 Multilingual Support:** Seamlessly switch between Sinhala, English, and Tamil from the main toolbar.
    * *(සිංහල, ඉංග්‍රීසි, සහ දෙමළ භාෂා තුනෙන්ම පහසුවෙන් Voice Type කිරීමේ හැකියාව.)*
* **⌨️ System-Wide Typing:** Works seamlessly in any active window (MS Word, Browsers, Notepad, etc.).
    * *(පරිගණකයේ ඕනෑම තැනක Cursor එක ඇති තැන ස්වයංක්‍රීයව ටයිප් වේ.)*
* **🚀 Global Hotkey:** Start/Stop listening instantly using `Ctrl + Shift + S`.
    * *(යතුරුපුවරුවේ Shortcut එකක් මඟින් ඉතා ඉක්මනින් ක්‍රියාත්මක කළ හැක.)*
* **🎨 Modern & Minimal UI:** A clean, horizontal floating toolbar interface (ParakeetAI-style) built with CustomTkinter. Features sliding Accordion previews!
    * *(භාවිතා කිරීමට ඉතා පහසු, කුඩා Floating Toolbar එකක් ලෙස දිස්වන නවීන මුහුණත.)*
* **🆓 No API Key Required:** Works out of the box for free!
    * *(කිසිදු ගෙවීමකින් තොරව සම්පූර්ණයෙන්ම නොමිලේ පාවිච්චි කළ හැක.)*

---

## 🛠️ Tech Stack | තාක්ෂණික මෙවලම්

* **Language:** Python 🐍
* **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Speech Engine:** SpeechRecognition (Google Web Speech API)
* **Automation:** Pynput & Pyperclip for clipboard keystroke injection.

---

## 🚀 Getting Started | ආරම්භ කරමු

### Prerequisites
Make sure you have **Python 3.8+** installed.
*(ඔබේ පරිගණකයේ Python 3.8 හෝ ඊට ඉහළ සංස්කරණයක් ස්ථාපනය කර තිබිය යුතුය.)*

### Installation | ස්ථාපනය කරන ආකාරය

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Pethumshyam6611/akura-sinhala-voice-typer.git
    cd akura-sinhala-voice-typer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```
*(Alternatively, you can build the application into a standalone `.exe` using PyInstaller).*

---

## ⌨️ How to Use | පාවිච්චි කරන්නේ කොහොමද?

1.  Open the **Akura** application. It will launch as a horizontal floating bar.
2.  Choose your language (Sinhala, English, or Tamil).
3.  Press the **"▶ Start Listening"** button or use the hotkey `Ctrl + Shift + S`.
4.  Click on any text area (e.g., MS Word, Web Browser).
5.  Speak naturally, and it will be typed automatically! ✍️

1.  **Akura** මෘදුකාංගය විවෘත කරන්න. එය පාවෙන කුඩා Toolbar එකක් ලෙස තිරයේ දිස්වනු ඇත.
2.  ඔබේ භාෂාව තෝරන්න (සිංහල, English, හෝ தமிழ்).
3.  **"Start Listening"** බටනය ක්ලික් කරන්න හෝ `Ctrl + Shift + S` shortcut එක ඔබන්න.
4.  ඔබට ලිවීමට අවශ්‍ය ස්ථානය (උදා: MS Word) මත ක්ලික් කරන්න.
5.  දැන් කතා කරන්න. එය ස්වයංක්‍රීයව ටයිප් වනු ඇත!

---

## 🛡️ License | බලපත්‍රය

This project is licensed under the **MIT License**.
*(මෙම ව්‍යාපෘතිය MIT බලපත්‍රය යටතේ නිකුත් කර ඇත.)*

---

## 👨‍💻 Developed By | නිර්මාණය කළේ

**Pethum Shyam (Build Diary)**  
Founder of "Build Diary" - Exploring tech and software engineering.

* **YouTube:** [Build Diary](https://youtube.com/@builddiary)
* **TikTok:** [Build Diary](https://tiktok.com/@builddiary)
* **GitHub:** [@pethumshyam](https://github.com/pethumshyam)

---

> Built with ❤️ for the Sri Lankan Community.
