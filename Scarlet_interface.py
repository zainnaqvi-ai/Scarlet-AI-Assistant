import customtkinter as ctk
import speech_recognition as sr
import webbrowser
import requests
import wikipediaapi
from gtts import gTTS
import pygame
import os
import time
import threading
import math  # Used for calculating smooth pulsing animations

# =====================================================================
# 1. CONFIGURATION & SETUP
# =====================================================================
newsapi_key = "news api here"

recognizer = sr.Recognizer()

ASSISTANT_NAME = "scarlet"
WAKE_WORD = "scarlet"

# Initialize pygame mixer once at startup (not inside speak())
pygame.mixer.init()

# Initialize Wikipedia API client once at startup
wiki = wikipediaapi.Wikipedia(user_agent='Scarlet/1.0 (personal voice assistant project)', language='en')


# =====================================================================
# 2. HOLOGRAPHIC SCI-FI INTERFACE (Jarvis-style, fullscreen)
# =====================================================================
class ScarletApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup -- fullscreen, fills the entire screen
        self.title("Scarlet AI Arc Interface")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.attributes("-fullscreen", True)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#050912")

        # Escape key drops out of fullscreen so you're never trapped
        self.bind("<Escape>", lambda e: self.exit_fullscreen())

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.is_running = False
        self.hud_angle = 0
        self.pulse_counter = 0
        self.ray_counter = 0
        self.status_text = "CORE OFFLINE"
        self.status_color = "#005577"  # Dim blue when offline

        # --- Responsive Grid Layout ---
        # Row 2 (the canvas) gets all leftover space -- this is what guarantees
        # everything else (title, button, hint) always stays visible on screen
        # no matter the resolution, instead of relying on fixed pixel math.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # title
        self.grid_rowconfigure(1, weight=0)  # status
        self.grid_rowconfigure(2, weight=1)  # canvas -- stretches
        self.grid_rowconfigure(3, weight=0)  # button
        self.grid_rowconfigure(4, weight=0)  # hint

        # Top Header Title
        self.title_label = ctk.CTkLabel(
            self, text="S.C.A.R.L.E.T. INTERFACE",
            font=("Consolas", 30, "bold"), text_color="#00ffff"
        )
        self.title_label.grid(row=0, column=0, pady=(30, 5), sticky="n")

        # Sub-status text element
        self.status_label = ctk.CTkLabel(
            self, text="Awaiting Core Initialization...",
            font=("Consolas", 18), text_color="#00aacc"
        )
        self.status_label.grid(row=1, column=0, pady=(0, 8), sticky="n")

        # Container frame so the canvas can be centered and resized dynamically
        self.canvas_frame = ctk.CTkFrame(self, fg_color="#050912")
        self.canvas_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Vector Graphics Canvas for the Holographic HUD Circle.
        # Size is recalculated live from the frame's actual rendered size
        # (see on_canvas_resize), so it always fits regardless of screen size.
        self.canvas = ctk.CTkCanvas(
            self.canvas_frame, bg="#050912", highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas_render_size = 400  # safe default before first resize event
        self.canvas_frame.bind("<Configure>", self.on_canvas_resize)

        # High-Tech Initialize Button
        self.start_btn = ctk.CTkButton(
            self, text="INITIALIZE CORE", font=("Consolas", 18, "bold"),
            fg_color="#004466", hover_color="#006699", border_color="#00ffff",
            border_width=1, text_color="#00ffff", height=55, width=260, corner_radius=10,
            command=self.toggle_system
        )
        self.start_btn.grid(row=3, column=0, pady=(8, 15), sticky="n")

        # Hint label for exiting fullscreen
        self.hint_label = ctk.CTkLabel(
            self, text="Press ESC to exit fullscreen",
            font=("Consolas", 11), text_color="#335566"
        )
        self.hint_label.grid(row=4, column=0, pady=(0, 10), sticky="n")

        # Trigger the animation graphics engine loop
        self.update_animation()

    def on_canvas_resize(self, event):
        """Keeps the HUD circle perfectly centered and sized to fit whatever
        space is actually available, instead of a hardcoded guess."""
        size = max(min(event.width, event.height) - 20, 150)
        self.canvas_render_size = size

    def exit_fullscreen(self):
        self.attributes("-fullscreen", False)
        self.geometry(f"{900}x{700}+100+50")

    def update_animation(self):
        """Draws and updates the rotating vector rings + radiating rays at 60FPS."""
        self.canvas.delete("hud")  # Clear previous frame

        size = self.canvas_render_size
        # Center against the canvas's actual current rendered dimensions,
        # not just size/2, so the HUD stays centered even if the canvas
        # frame isn't perfectly square.
        cw = self.canvas.winfo_width() or size
        ch = self.canvas.winfo_height() or size
        cx, cy = cw / 2, ch / 2

        if self.is_running:
            # Spin speeds when the AI is active
            self.hud_angle = (self.hud_angle + 2) % 360
            self.pulse_counter += 0.07
            self.ray_counter += 0.05
            pulse_offset = math.sin(self.pulse_counter) * (size * 0.015)
        else:
            # Subtle slow idle motion when turned off
            self.hud_angle = (self.hud_angle + 0.3) % 360
            self.ray_counter += 0.01
            pulse_offset = 0

        outer_r = size * 0.47
        mid_r = size * 0.36
        inner_r = size * 0.27
        core_r = size * 0.18

        # 0. Radiating Jarvis-style light rays from the core outward
        ray_count = 24
        ray_pulse = math.sin(self.ray_counter) * 0.15 + 0.85  # gentle brightness breathing
        for i in range(ray_count):
            angle_deg = (i * (360 / ray_count)) + self.hud_angle * 0.4
            angle_rad = math.radians(angle_deg)
            inner_pt_r = core_r * 1.05
            outer_pt_r = outer_r * (0.92 if i % 2 == 0 else 0.75) * ray_pulse
            x1 = cx + inner_pt_r * math.cos(angle_rad)
            y1 = cy + inner_pt_r * math.sin(angle_rad)
            x2 = cx + outer_pt_r * math.cos(angle_rad)
            y2 = cy + outer_pt_r * math.sin(angle_rad)
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=self.status_color, width=1, tags="hud"
            )

        # 1. Outer Tech Dashed Ring (Clockwise)
        for i in range(4):
            start = (self.hud_angle + (i * 90)) % 360
            self.canvas.create_arc(
                cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r,
                start=start, extent=50,
                style="arc", outline=self.status_color, width=2, tags="hud"
            )

        # 2. Middle Solid Split Ring (Counter-Clockwise)
        for i in range(2):
            start = (-self.hud_angle * 1.5 + (i * 180)) % 360
            self.canvas.create_arc(
                cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r,
                start=start, extent=110,
                style="arc", outline=self.status_color, width=5, tags="hud"
            )

        # 3. Inner Measured Calibration Ring (Clockwise)
        for i in range(8):
            start = (self.hud_angle * 0.5 + (i * 45)) % 360
            self.canvas.create_arc(
                cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
                start=start, extent=15,
                style="arc", outline=self.status_color, width=1, tags="hud"
            )

        # 4. Deep Core Pulsing Power Sphere (glow effect via layered ovals)
        r1 = core_r + pulse_offset
        glow_color = "#00ffff" if self.is_running else self.status_color
        self.canvas.create_oval(
            cx - r1 - 6, cy - r1 - 6, cx + r1 + 6, cy + r1 + 6,
            outline=glow_color, width=1, tags="hud"
        )
        self.canvas.create_oval(
            cx - r1, cy - r1, cx + r1, cy + r1,
            outline=glow_color, width=3, tags="hud"
        )

        # 5. Core Interface Central Text Badge -- assistant name front and center
        self.canvas.create_text(
            cx, cy, text=ASSISTANT_NAME.upper(),
            fill="#ffffff" if self.is_running else "#777777",
            font=("Consolas", int(size * 0.07), "bold"), tags="hud"
        )
        self.canvas.create_text(
            cx, cy + size * 0.07, text=self.status_text,
            fill=self.status_color,
            font=("Consolas", int(size * 0.022), "bold"), tags="hud"
        )

        # Loop the drawing method frame roughly every 16ms (~60 FPS)
        self.after(16, self.update_animation)

    def toggle_system(self):
        """Handles activating and deactivating core systems safely."""
        if not self.is_running:
            self.is_running = True
            self.status_color = "#00ffff"  # Bright vibrant neon cyan
            self.status_text = "ACTIVE"
            self.status_label.configure(text="System online. Microphone listening...")
            self.start_btn.configure(text="SHUT DOWN CORE", fg_color="#330000", hover_color="#550000",
                                     border_color="#ff4444", text_color="#ff4444")

            # Offload listening tasks to an isolated background safety thread
            threading.Thread(target=self.run_assistant_loop, daemon=True).start()
        else:
            self.is_running = False
            self.status_color = "#005577"  # Back to dim offline colors
            self.status_text = "CORE OFFLINE"
            self.status_label.configure(text="Awaiting Core Initialization...")
            self.start_btn.configure(text="INITIALIZE CORE", fg_color="#004466", hover_color="#006699",
                                     border_color="#00ffff", text_color="#00ffff")
            self.shutdown()

    # =================================================================
    # 3. CORE VOICE ENGINE LOGIC (Thread-Safe integration)
    # =================================================================
    def speak(self, text):
        print(f"Scarlet: {text}")
        # Temporarily morph interface ring color to show she is talking
        old_text = self.status_text
        self.status_text = "SPEAKING"

        try:
            tts = gTTS(text=text, lang='en')
            tts.save('temp.mp3')
            pygame.mixer.music.load('temp.mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            try:
                os.remove('temp.mp3')
            except PermissionError:
                pass
        except Exception as e:
            print(f"[TTS ERROR] {e}")

        if self.is_running:
            self.status_text = old_text

    def search_wikipedia(self, query):
        try:
            for phrase in ["who is", "what is", "tell me about", "search wikipedia for", "wikipedia"]:
                query = query.lower().replace(phrase, "")
            query = query.strip()

            if not query:
                self.speak("Sir, please tell me what to search for.")
                return

            page = wiki.page(query)

            if page.exists():
                sentences = page.summary.split('. ')
                short_summary = '. '.join(sentences[:2]).strip()
                if not short_summary.endswith('.'):
                    short_summary += '.'
                self.speak(short_summary)
            else:
                self.speak("Sir, I couldn't find anything on that topic.")

        except Exception as e:
            print(f"[WIKIPEDIA ERROR] {e}")
            self.speak("Sir, I had trouble reaching Wikipedia.")

    def process_command(self, command):
        command = command.lower()
        if "open google" in command:
            self.speak("Opening Google, Sir.")
            webbrowser.open("https://google.com")
        elif "open youtube" in command:
            self.speak("Opening YouTube, Sir.")
            webbrowser.open("https://youtube.com")
        elif "designed" in command:
            self.speak("I was designed by 4 U M T students for Miss Maryam, namely Zain, Muhammad, Gujjar, and Adeel.")
        elif "news" in command:
            self.speak("Fetching headlines.")
            try:
                r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi_key}", timeout=5)
                if r.status_code == 200:
                    articles = r.json().get("articles", [])[:5]
                    for i, art in enumerate(articles, 1):
                        self.speak(f"Headline {i}: {art['title']}")
                else:
                    self.speak("Unable to reach news networks.")
            except Exception as e:
                print(f"[NEWS ERROR] {e}")
                self.speak("Unable to reach news networks.")
        elif "who is" in command or "what is" in command or "tell me about" in command or "wikipedia" in command:
            self.search_wikipedia(command)
        else:
            self.speak("Sir, I don't have a brain connected for that yet. Try asking me to open something, fetch news, or search Wikipedia.")

    def listen_for_wake_word(self):
        with sr.Microphone() as source:
            self.status_text = "LISTENING"
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                return None
        try:
            self.status_text = "PROCESSING"
            word = recognizer.recognize_google(audio, language='en-in')
            return word.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

    def listen_for_command(self):
        with sr.Microphone() as source:
            self.status_text = "HEARING CMD"
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                return None
        try:
            self.status_text = "PROCESSING"
            command = recognizer.recognize_google(audio, language='en-in')
            return command
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

    def run_assistant_loop(self):
        try:
            self.speak(f"Initializing {ASSISTANT_NAME}.")

            while self.is_running:
                self.status_text = "WAITING"
                heard_word = self.listen_for_wake_word()

                if heard_word is not None and WAKE_WORD in heard_word:
                    self.speak("Yes, Sir?")
                    user_command = self.listen_for_command()

                    if user_command is None:
                        self.speak("I didn't catch that, Sir.")
                        continue

                    if "exit" in user_command.lower() or "stop" in user_command.lower():
                        self.speak("Powering down, goodbye Sir.")
                        self.is_running = False
                        self.toggle_system()
                        break

                    self.process_command(user_command)
        except Exception as e:
            print(f"[FATAL ASSISTANT LOOP ERROR] {e}")
            self.status_text = "ERROR"
            try:
                self.speak("Sir, I hit a critical error and need to shut down.")
            except Exception:
                pass

    def shutdown(self):
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        print("[INFO] Scarlet hardware loop cleanly detached.")


# =====================================================================
# 4. INITIAL EXECUTION
# =====================================================================
if __name__ == "__main__":
    app = ScarletApp()
    app.mainloop()