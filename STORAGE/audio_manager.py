"""
Audio Manager for AI Exercise Detector
=======================================
Provides threaded Text-to-Speech coaching and sound effects.
Runs all audio in a background thread so the video feed never stutters.

Features:
  - Voice coaching with male/female selection
  - Satisfying 'ding' sound on perfect reps
  - Smart cooldown to avoid repetitive speech
  - Mute/unmute toggle
"""

import threading
import queue
import time
import winsound
import pyttsx3


class AudioManager:
    """Threaded audio manager for voice coaching and sound effects."""

    # Cooldown between speaking the same feedback (seconds)
    SPEECH_COOLDOWN = 3.0

    # Cooldown between any speech (seconds)
    MIN_SPEECH_GAP = 1.5

    def __init__(self):
        """
        Initialize the audio manager.
        """
        self.muted = False

        # Speech tracking
        self._last_spoken_text = ""
        self._last_spoken_time = 0
        self._last_rep_count = {}  # track per-exercise rep counts

        # Thread-safe queue for speech requests
        self._speech_queue = queue.Queue()

        # Start the TTS worker thread (daemon so it dies with the app)
        self._tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self._tts_thread.start()

        # Sound effect thread (separate so ding doesn't block speech)
        self._sound_queue = queue.Queue()
        self._sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self._sound_thread.start()

    def _tts_worker(self):
        """Background worker that processes speech requests sequentially."""
        # In a background thread on Windows, we must initialize COM for OneCore voices
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass
            
        # pyttsx3 engine must be created in the same thread that uses it
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)  # Slightly faster than default
        engine.setProperty('volume', 0.9)

        # Set female voice
        self._set_female_voice(engine)

        while True:
            try:
                text = self._speech_queue.get(timeout=1.0)
                if text is None:
                    break  # Shutdown signal
                if not self.muted:
                    engine.say(text)
                    engine.runAndWait()
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

    def _sound_worker(self):
        """Background worker that plays sound effects."""
        while True:
            try:
                sound_type = self._sound_queue.get(timeout=1.0)
                if sound_type is None:
                    break
                if not self.muted:
                    if sound_type == 'ding':
                        self._play_ding()
                    elif sound_type == 'exercise_switch':
                        self._play_switch_sound()
                self._sound_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

    def _set_female_voice(self, engine):
        """Set engine voice to female, including OneCore voices."""
        import winreg

        # --- Step 1: Check standard SAPI voices (what pyttsx3 sees) ---
        voices = engine.getProperty('voices')
        for voice in voices:
            name = voice.name.lower()
            if any(k in name for k in ['zira', 'heera', 'eva', 'hazel']):
                engine.setProperty('voice', voice.id)
                print(f"    [Audio] Using voice: {voice.name}")
                return

        # --- Step 2: Try to use OneCore voices directly ---
        try:
            onecore_key = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, onecore_key) as oc:
                i = 0
                while True:
                    try:
                        token_name = winreg.EnumKey(oc, i)
                        i += 1

                        # Read the voice display name
                        with winreg.OpenKey(oc, token_name) as token:
                            display_name = winreg.QueryValueEx(token, "")[0].lower()

                        # Check if this is the gender we want
                        if any(k in display_name for k in ['heera', 'zira', 'eva', 'hazel']):
                            # Set voice ID using OneCore path
                            voice_id = f"HKEY_LOCAL_MACHINE\\{onecore_key}\\{token_name}"
                            engine.setProperty('voice', voice_id)
                            print(f"    [Audio] Using OneCore voice: {display_name.title()}")
                            return

                    except OSError:
                        break
        except Exception:
            pass

        # --- Step 3: Fallback ---
        engine.setProperty('rate', 175)
        print("    [Audio] Using default voice")

    def speak_feedback(self, text):
        """
        Queue feedback text to be spoken, with smart deduplication.

        Won't speak if:
          - The app is muted
          - The same text was spoken recently (within SPEECH_COOLDOWN)
          - Any speech happened too recently (within MIN_SPEECH_GAP)
        """
        if self.muted or not text:
            return

        current_time = time.time()

        # Don't speak if too recent
        if current_time - self._last_spoken_time < self.MIN_SPEECH_GAP:
            return

        # Don't repeat the same text within cooldown
        if text == self._last_spoken_text and \
           current_time - self._last_spoken_time < self.SPEECH_COOLDOWN:
            return

        # Queue it
        self._last_spoken_text = text
        self._last_spoken_time = current_time

        # Clear any pending messages (only speak the latest)
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
            except queue.Empty:
                break

        self._speech_queue.put(text)

    def play_rep_sound(self, exercise_name, rep_count):
        """
        Play a 'ding' sound when a new rep is completed.

        Args:
            exercise_name: Name of the current exercise
            rep_count: Current rep count
        """
        if self.muted:
            return

        last_count = self._last_rep_count.get(exercise_name, 0)
        if rep_count > last_count:
            self._last_rep_count[exercise_name] = rep_count
            self._sound_queue.put('ding')

    def play_exercise_switch_sound(self):
        """Play a sound when switching to a new exercise."""
        if not self.muted:
            self._sound_queue.put('exercise_switch')

    def announce_exercise(self, exercise_name):
        """Announce which exercise was detected."""
        if not self.muted:
            self._speech_queue.put(f"Detected: {exercise_name}")

    def toggle_mute(self):
        """Toggle mute state. ::
        Returns the new mute state."""
        self.muted = not self.muted
        return self.muted

    def reset_tracking(self, exercise_name=None):
        """Reset rep tracking for an exercise (or all)."""
        if exercise_name:
            self._last_rep_count[exercise_name] = 0
        else:
            self._last_rep_count.clear()
        self._last_spoken_text = ""

    def _play_ding(self):
        """Play a satisfying 'ding' sound using Windows system beep."""
        try:
            # High-pitched short beep = satisfying ding
            winsound.Beep(1200, 150)  # 1200 Hz, 150ms
        except Exception:
            pass

    def _play_switch_sound(self):
        """Play a two-tone sound for exercise switch."""
        try:
            winsound.Beep(800, 100)
            winsound.Beep(1000, 100)
        except Exception:
            pass

    def shutdown(self):
        """Clean shutdown of audio threads."""
        self._speech_queue.put(None)
        self._sound_queue.put(None)


# --- Standalone test ---
if __name__ == '__main__':
    print("Testing AudioManager...")
    print()

    # Test female voice
    print("  Testing FEMALE voice...")
    mgr = AudioManager()
    time.sleep(0.5)
    mgr.speak_feedback("Testing female voice. Push through the pain!")
    time.sleep(3)

    # Test ding sound
    print("  Testing ding sound...")
    mgr.play_rep_sound("test", 1)
    time.sleep(1)
    mgr.play_rep_sound("test", 2)
    time.sleep(1)

    # Test exercise switch
    print("  Testing exercise switch sound...")
    mgr.play_exercise_switch_sound()
    time.sleep(1)

    # Test announcement
    print("  Testing exercise announcement...")
    mgr.announce_exercise("Bicep Curls")
    time.sleep(3)

    # Test mute
    print("  Testing mute toggle...")
    muted = mgr.toggle_mute()
    print(f"    Muted: {muted}")
    mgr.speak_feedback("You should NOT hear this!")
    time.sleep(1)

    muted = mgr.toggle_mute()
    print(f"    Muted: {muted}")
    mgr.speak_feedback("Unmuted! Great workout!")
    time.sleep(3)

    mgr.shutdown()
    print()
    print("  All tests complete!")
