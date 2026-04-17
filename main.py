#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║        AKURA (අකුර)  —  Professional Sinhala Voice Typer        ║
║              Commercial-Grade Windows Desktop App                ║
║                                                                  ║
║  Engine  : Google Speech Recognition API (language='si-LK')      ║
║  UI      : CustomTkinter (dark theme, rounded, purple accent)    ║
║  Hotkey  : Ctrl + Shift + S  (global toggle)                     ║
║  Inject  : Clipboard injection -> prevents Unicode clashes       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import math
import time
import queue
import threading
import logging
import datetime
import tkinter as tk
from typing import Optional, List

try:
    import requests
    import customtkinter as ctk
    import speech_recognition as sr
    import sounddevice as sd
    import numpy as np
    from pynput import keyboard
    import pyperclip
except ImportError as exc:
    sys.exit(f"[FATAL] Missing dependency: {exc}\nRun: pip install -r requirements.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("Akura")

APP_NAME    = "Akura"
APP_VER     = "2.0.0"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SPLASH_W, SPLASH_H = 360, 230

# Horizontal Floating Toolbar Dimensions
MAIN_W             = 780
MAIN_H_CLOSED      = 92
MAIN_H_PREVIEW     = 360
MAIN_H_SETT        = 440

HOTKEY_COMBO   = "<ctrl>+<shift>+s"
HOTKEY_DISPLAY = "Ctrl + Shift + S"

C = {
    "bg":          "#0F1117",
    "surface":     "#161929",
    "card":        "#1E2235",
    "border":      "#2A2F4E",
    "accent":      "#7C3AED",
    "accent_h":    "#8B5CF6",
    "accent_d":    "#5B21B6",
    "sky":         "#4FC3F7",
    "success":     "#4CAF50",
    "warning":     "#FF9800",
    "error":       "#EF5350",
    "idle":        "#5A607A",
    "text":        "#EAEAEA",
    "muted":       "#8A8FA8",
    "dim":         "#454B6B",
    "wave_bar":    "#8B5CF6",
    "wave_bg":     "#0D1020",
}

STATUS_DEF = {
    "IDLE":       ("Idle",        C["card"], C["idle"],    "🎙"),
    "LISTENING":  ("Rec",         C["success"], C["bg"], "🔴"),
    "PROCESSING": ("Proc",        C["warning"], C["bg"], "⚙"),
    "ERROR":      ("Err",         C["error"],   C["bg"], "⚠"),
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ═══════════════════════════════════════════════════════════════════════════════
# §1  SPLASH SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._load_error  = None
        self._load_done   = threading.Event()
        self._progress    = 0.0

        self._cfg_window()
        self._build_ui()
        self._start_load()
        self.after(60, self._animate)

    def _cfg_window(self):
        self.title("")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=C["bg"])
        self.resizable(False, False)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{SPLASH_W}x{SPLASH_H}+{(sw-SPLASH_W)//2}+{(sh-SPLASH_H)//2}")
        
        ico_path = resource_path("icon.ico")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=20, border_width=1, border_color=C["border"])
        outer.place(relx=0, rely=0, relwidth=1, relheight=1)
        ctk.CTkFrame(outer, fg_color=C["accent"], corner_radius=0, height=6).pack(fill="x")
        ctk.CTkLabel(outer, text="අකුර", font=ctk.CTkFont("Segoe UI", 56, "bold"), text_color=C["accent"]).pack(pady=(22, 0))
        ctk.CTkLabel(outer, text="AKURA  ·  Sinhala Voice Typer", font=ctk.CTkFont("Segoe UI", 12), text_color=C["muted"]).pack(pady=(2, 0))
        ctk.CTkLabel(outer, text=f"v{APP_VER}", font=ctk.CTkFont("Segoe UI", 10), text_color=C["dim"]).pack(pady=(1, 14))
        ctk.CTkFrame(outer, fg_color=C["border"], height=1).pack(fill="x", padx=32)
        self._msg = ctk.CTkLabel(outer, text="Initializing Akura...", font=ctk.CTkFont("Segoe UI", 11), text_color=C["muted"])
        self._msg.pack(pady=(14, 8))
        self._bar = ctk.CTkProgressBar(outer, width=300, height=6, corner_radius=3, fg_color=C["card"], progress_color=C["accent"])
        self._bar.set(0)
        self._bar.pack()
        self._pct = ctk.CTkLabel(outer, text="0 %", font=ctk.CTkFont("Segoe UI", 9), text_color=C["dim"])
        self._pct.pack(pady=(4, 0))

    def _start_load(self):
        def _load():
            try:
                log.info("Checking internet connectivity for Google Speech...")
                time.sleep(0.4)
                requests.get("https://www.google.com", timeout=4)
                for _ in range(5):
                    time.sleep(0.1)
            except Exception as exc:
                self._load_error = exc
            finally:
                self._load_done.set()
        threading.Thread(target=_load, daemon=True, name="InitLoader").start()

    def _animate(self):
        if not self._load_done.is_set():
            self._progress = min(self._progress + 0.015, 0.88)
            self._bar.set(self._progress)
            self._pct.configure(text=f"{int(self._progress * 100)} %")
            self.after(40, self._animate)
        else:
            self._progress = min(self._progress + 0.08, 1.0)
            self._bar.set(self._progress)
            self._pct.configure(text=f"{int(self._progress * 100)} %")
            if self._progress >= 1.0:
                self._msg.configure(text="Ready!  Launching…")
                self.after(420, self._open_main)
            else:
                self.after(28, self._animate)

    def _open_main(self):
        if self._load_error:
            self.withdraw()
            _fatal_dialog(f"No Internet Connection.\n\nAkura requires the internet for Google Voice Typing.\n{self._load_error}")
            self.destroy()
            return
        for alpha in (0.85, 0.65, 0.45, 0.25, 0.05):
            self.attributes("-alpha", alpha)
            self.update()
            time.sleep(0.035)
        self.withdraw()
        AkuraApp(self)


# ═══════════════════════════════════════════════════════════════════════════════
# §2  SETTINGS PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=C["card"], corner_radius=12, border_width=1, border_color=C["border"], **kw)
        if hasattr(parent.master, '_lang_var'):
            self._lang_var = parent.master._lang_var
        self._device_map: dict = {}
        self._mic_var   = ctk.StringVar()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="⚙  Settings & Info", font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C["muted"]).pack(anchor="w", padx=16, pady=(10, 6))

        tabs = ctk.CTkTabview(self, fg_color=C["surface"], segmented_button_selected_color=C["accent"],
                              segmented_button_unselected_color=C["card"], text_color=C["text"], corner_radius=10)
        tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tabs.add("🎙  Audio")
        tabs.add("ℹ  Help")
        
        tab_a = tabs.tab("🎙  Audio")
        ctk.CTkLabel(tab_a, text="Microphone Input", font=ctk.CTkFont("Segoe UI", 11), text_color=C["muted"]).pack(anchor="w", padx=8, pady=(10, 4))
        
        devices = self._enum_devices()
        self._device_map = devices
        names = list(devices.keys())
        self._mic_var.set(names[0] if names else "Default System Microphone")

        ctk.CTkOptionMenu(
            tab_a, values=names or ["Default System Microphone"], variable=self._mic_var,
            fg_color=C["card"], button_color=C["accent"], button_hover_color=C["accent_h"], dropdown_fg_color=C["card"],
            text_color=C["text"], font=ctk.CTkFont("Segoe UI", 11)
        ).pack(fill="x", padx=8, pady=(0, 6))

        tab_h = tabs.tab("ℹ  Help")
        ins = (
            "• Press Ctrl+Shift+S (or click Start) to record.\n"
            "• Speak naturally, and text will be typed where your cursor is.\n"
            "• IMPORTANT: Active Internet Connection is REQUIRED.\n"
        )
        ctk.CTkLabel(tab_h, text=ins, justify="left", font=ctk.CTkFont("Segoe UI", 10), text_color=C["text"]).pack(anchor="w", padx=8, pady=(12, 4))
        
        ctk.CTkLabel(tab_h, text="© Created by pethum.io", font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C["accent"]).pack(side="bottom", pady=8)

    @staticmethod
    def _enum_devices() -> dict:
        out = {"Default System Microphone": None}
        try:
            mics = sd.query_devices()
            for i, info in enumerate(mics):
                if info.get("max_input_channels", 0) > 0:
                    out[info.get("name", f"Device {i}")] = i
        except Exception as exc:
            log.warning(f"Device enumeration failed: {exc}")
        return out

    def get_device_index(self) -> Optional[int]:
        return self._device_map.get(self._mic_var.get())


# ═══════════════════════════════════════════════════════════════════════════════
# §3  ERROR DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, detail: str):
        super().__init__(parent)
        self.title("Akura — Error")
        self.geometry("450x260")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.attributes("-topmost", True)
        self.grab_set()

        outer = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=16, border_width=1, border_color=C["error"])
        outer.place(relx=0, rely=0, relwidth=1, relheight=1)
        ctk.CTkFrame(outer, fg_color=C["error"], corner_radius=0, height=5).pack(fill="x")
        ctk.CTkLabel(outer, text=title, font=ctk.CTkFont("Segoe UI", 14, "bold"), text_color=C["text"]).pack(anchor="w", padx=22, pady=(18, 6))
        ctk.CTkLabel(outer, text=detail, justify="left", wraplength=390, font=ctk.CTkFont("Segoe UI", 11), text_color=C["muted"]).pack(anchor="w", padx=22)
        ctk.CTkButton(outer, text="  OK  ", width=90, height=34, fg_color=C["error"], hover_color="#C62828", font=ctk.CTkFont("Segoe UI", 12, "bold"), corner_radius=8, command=self.destroy).pack(pady=20, side="bottom")


# ═══════════════════════════════════════════════════════════════════════════════
# §4  MAIN APP (Horizontal Toolbar)
# ═══════════════════════════════════════════════════════════════════════════════

class HotkeyListener:
    def __init__(self, toggle_cb):
        self._cb       = toggle_cb
        self._listener = None

    def start(self):
        self._listener = keyboard.GlobalHotKeys({HOTKEY_COMBO: self._cb})
        self._listener.daemon = True
        self._listener.start()
        log.info(f"HotkeyListener: armed ({HOTKEY_COMBO})")

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass


class AkuraApp(ctk.CTkToplevel):
    MAX_PHRASES = 4

    def __init__(self, root: ctk.CTk):
        super().__init__(root)
        self.main_root   = root

        self._recording  = False
        self._view_mode  = "CLOSED"  # CLOSED, PREVIEW, SETTINGS
        self._phrases: List[str] = []
        self._lang_var   = ctk.StringVar(value="🌐 සිංහල")

        self._result_q   = queue.Queue()
        self.recognizer  = sr.Recognizer()
        
        self._kb = keyboard.Controller()
        self._hotkey = HotkeyListener(self._toggle_recording)

        self._cfg_window()
        self._build_ui()
        self._hotkey.start()
        self.after(200, self._poll_results)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _cfg_window(self):
        self.title(f"{APP_NAME}  ·  Floating Bar")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=C["bg"])
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        # Default positioning to bottom-center
        self.geometry(f"{MAIN_W}x{MAIN_H_CLOSED}+{(sw-MAIN_W)//2}+{sh - MAIN_H_CLOSED - 60}")
        
        ico_path = resource_path("icon.ico")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)

    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color=C["bg"])
        wrap.pack(fill="both", expand=True)

        self._build_toolbar(wrap)
        self._build_preview(wrap)
        self._settings_panel = SettingsPanel(wrap)

        self._hide_panels()

    def _build_toolbar(self, p):
        # A sleek horizontal frame sitting exactly inside the bounds
        bar = ctk.CTkFrame(p, fg_color=C["surface"], corner_radius=14, border_width=1, border_color=C["border"], height=68)
        bar.pack(fill="x", padx=12, pady=12)
        bar.pack_propagate(False)

        # 1. Logo
        lg = ctk.CTkFrame(bar, fg_color="transparent")
        lg.pack(side="left", padx=(16, 8))
        ctk.CTkLabel(lg, text="අකුර", font=ctk.CTkFont("Segoe UI", 26, "bold"), text_color=C["accent"]).pack(side="left")

        # 2. Status Pill
        self._pill = ctk.CTkFrame(bar, fg_color=C["card"], corner_radius=12, border_width=1, border_color=C["border"], width=80, height=36)
        self._pill.pack(side="left", padx=8)
        self._pill.pack_propagate(False)
        self._pill_icon = ctk.CTkLabel(self._pill, text="🎙", font=ctk.CTkFont("Segoe UI", 12), text_color=C["idle"])
        self._pill_icon.place(relx=0.25, rely=0.5, anchor="center")
        self._pill_lbl  = ctk.CTkLabel(self._pill, text="Idle", font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C["idle"])
        self._pill_lbl.place(relx=0.65, rely=0.5, anchor="center")

        # 3. Language Selector
        self._lang_menu = ctk.CTkOptionMenu(bar, values=["🌐 සිංහල", "🌐 English", "🌐 தமிழ்"], variable=self._lang_var, width=100, height=38, corner_radius=10, fg_color=C["card"], button_color=C["card"], button_hover_color=C["border"], dropdown_fg_color=C["card"], text_color=C["text"], font=ctk.CTkFont("Segoe UI", 12))
        self._lang_menu.pack(side="left", padx=8)

        # 4. Main Toggle 
        self._main_btn = ctk.CTkButton(bar, text="🎙  Start Listening", height=42, corner_radius=10, font=ctk.CTkFont("Segoe UI", 13, "bold"), fg_color=C["accent"], hover_color=C["accent_h"], command=self._toggle_recording)
        self._main_btn.pack(side="left", expand=True, fill="x", padx=8)

        # 5. Preview Toggle
        self._trans_btn = ctk.CTkButton(bar, text="▼ Preview", width=80, height=36, corner_radius=8, font=ctk.CTkFont("Segoe UI", 11, "bold"), fg_color=C["card"], hover_color=C["border"], text_color=C["muted"], command=self._toggle_transcript)
        self._trans_btn.pack(side="left", padx=8)
        
        # 6. Settings Toggle
        self._settings_btn = ctk.CTkButton(bar, text="⚙", width=36, height=36, corner_radius=8, font=ctk.CTkFont("Segoe UI", 16), fg_color=C["card"], hover_color=C["border"], text_color=C["muted"], command=self._toggle_settings)
        self._settings_btn.pack(side="right", padx=(0, 16))

    def _build_preview(self, p):
        self._preview_frame = ctk.CTkFrame(p, fg_color=C["surface"], corner_radius=14, border_width=1, border_color=C["border"])
        
        top = ctk.CTkFrame(self._preview_frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(top, text="TRANSCRIPTION PREVIEW", font=ctk.CTkFont("Segoe UI", 9, "bold"), text_color=C["dim"]).pack(side="left")
        ctk.CTkButton(top, text="Clear", width=68, height=26, fg_color=C["card"], hover_color=C["border"], text_color=C["muted"], font=ctk.CTkFont("Segoe UI", 10), corner_radius=6, command=self._clear_preview).pack(side="right")
        
        self._preview = ctk.CTkTextbox(self._preview_frame, fg_color=C["card"], text_color=C["text"], font=ctk.CTkFont("Segoe UI", 13), corner_radius=10, border_width=0, wrap="word", state="disabled")
        self._preview.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._preview_show_placeholder()

    def _hide_panels(self):
        self._settings_panel.pack_forget()
        self._preview_frame.pack_forget()

    def _toggle_settings(self):
        if self._view_mode == "SETT":
            self._hide_panels()
            self.geometry(f"{MAIN_W}x{MAIN_H_CLOSED}")
            self._view_mode = "CLOSED"
        else:
            self._hide_panels()
            self._settings_panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            self.geometry(f"{MAIN_W}x{MAIN_H_SETT}")
            self._view_mode = "SETT"
            self._trans_btn.configure(text="▼ Preview", text_color=C["muted"])

    def _toggle_transcript(self):
        if self._view_mode == "PREVIEW":
            self._hide_panels()
            self.geometry(f"{MAIN_W}x{MAIN_H_CLOSED}")
            self._view_mode = "CLOSED"
            self._trans_btn.configure(text="▼ Preview", text_color=C["muted"])
        else:
            self._hide_panels()
            self._preview_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            self.geometry(f"{MAIN_W}x{MAIN_H_PREVIEW}")
            self._view_mode = "PREVIEW"
            self._trans_btn.configure(text="▲ Hide", text_color=C["accent"])

    def _set_status(self, state: str):
        label, pill_c, text_c, icon = STATUS_DEF.get(state, STATUS_DEF["IDLE"])
        self._pill_lbl.configure(text=label, text_color=text_c)
        self._pill_icon.configure(text=icon, text_color=text_c)
        self._pill.configure(fg_color=pill_c, border_color=pill_c if state != "IDLE" else C["border"])

    def _preview_show_placeholder(self):
        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")
        self._preview.insert("end", "Transcribed text will drop down and appear here…\n")
        self._preview.configure(state="disabled")

    def _append_phrase(self, text: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._phrases.append((ts, text))
        if len(self._phrases) > self.MAX_PHRASES:
            self._phrases.pop(0)
        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")
        for t, ph in self._phrases:
            self._preview.insert("end", f"[{t}]  ")
            self._preview.insert("end", ph + "\n\n")
        self._preview.see("end")
        self._preview.configure(state="disabled")

    def _clear_preview(self):
        self._phrases.clear()
        self._preview_show_placeholder()

    def _inject(self, text: str):
        try:
            pyperclip.copy(text)
            time.sleep(0.05)
            self._kb.press(keyboard.Key.shift)
            self._kb.press(keyboard.Key.insert)
            self._kb.release(keyboard.Key.insert)
            self._kb.release(keyboard.Key.shift)
            time.sleep(0.05)
        except Exception as exc:
            log.warning(f"Text injection failed: {exc}")

    def _toggle_recording(self):
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        dev_idx = self._settings_panel.get_device_index()
        
        # Get Language
        lang_str = self._lang_var.get()
        if "English" in lang_str:
            lang_code = "en-US"
        elif "தமிழ்" in lang_str:
            lang_code = "ta-LK"
        else:
            lang_code = "si-LK"

        def _setup_and_listen():
            RATE = 16000
            CHUNK = 2000
            VAD_THRESH = 20
            SILENCE_LIMIT = 0.45
            
            frames = []
            silent_chunks = 0
            stream = None
            
            try:
                self._result_q.put(("status", "LISTENING"))
                stream = sd.InputStream(samplerate=RATE, channels=1, dtype='int16', blocksize=CHUNK, device=dev_idx)
                stream.start()
                
                while self._recording:
                    data, overflow = stream.read(CHUNK)
                    data_flat = data.flatten()
                    
                    rms = float(np.sqrt(np.mean(data_flat.astype(np.float32)**2)))
                    
                    if rms > VAD_THRESH:
                        silent_chunks = 0
                        frames.append(data_flat)
                    elif len(frames) > 0:
                        silent_chunks += 1
                        frames.append(data_flat)
                        
                    if silent_chunks > (SILENCE_LIMIT * RATE / CHUNK) and len(frames) > 0:
                        audio_np = np.concatenate(frames)
                        frames = []
                        silent_chunks = 0
                        
                        if len(audio_np) > RATE * 0.3:
                            audio_bytes = audio_np.tobytes()
                            audio_data = sr.AudioData(audio_bytes, RATE, 2)
                            
                            def _do_transcribe(ad):
                                self._result_q.put(("status", "PROCESSING"))
                                try:
                                    text = self.recognizer.recognize_google(ad, language=lang_code)
                                    if text and text.strip():
                                        self._result_q.put(("text", text.strip()))
                                except sr.UnknownValueError:
                                    pass
                                except Exception as e:
                                    log.warning(f"Google error: {e}")
                                finally:
                                    if self._recording:
                                        self._result_q.put(("status", "LISTENING"))
                                        
                            threading.Thread(target=_do_transcribe, args=(audio_data,), daemon=True).start()
            except Exception as e:
                self._result_q.put(("error_dialog", ("🎙 Recording Error", str(e))))
                self._result_q.put(("stop", None))
            finally:
                if stream:
                    stream.stop()
                    stream.close()

        self._listen_thread = threading.Thread(target=_setup_and_listen, daemon=True)
        self._listen_thread.start()

        self._recording = True
        self._main_btn.configure(text="■  Stop", fg_color=C["error"], hover_color="#C62828")
        log.info("Recording started.")

    def _stop_recording(self):
        self._recording = False
        self._set_status("IDLE")
        self._main_btn.configure(text="🎙  Start Listening", fg_color=C["accent"], hover_color=C["accent_h"])
        log.info("Recording stopped.")

    def _poll_results(self):
        try:
            while True:
                kind, payload = self._result_q.get_nowait()
                if kind == "text":
                    self._append_phrase(payload)
                    self._inject(payload + " ")
                elif kind == "status":
                    self._set_status(payload)
                elif kind == "error":
                    self._set_status("ERROR")
                    log.error(f"Background SR error: {payload}")
                elif kind == "error_dialog":
                    self._set_status("ERROR")
                    ErrorDialog(self, *payload)
                elif kind == "stop":
                    self._stop_recording()
        except queue.Empty:
            pass
        self.after(200, self._poll_results)

    def _on_close(self):
        self._stop_recording()
        self._hotkey.stop()
        self.after(250, lambda: self.main_root.destroy())


def _fatal_dialog(msg: str):
    import tkinter.messagebox as mb
    root = tk.Tk()
    root.withdraw()
    mb.showerror("Akura — Fatal Error", msg)
    root.destroy()

def main():
    log.info(f"Starting {APP_NAME} v{APP_VER} (Google SR)")
    splash = SplashScreen()
    splash.mainloop()

if __name__ == "__main__":
    main()
