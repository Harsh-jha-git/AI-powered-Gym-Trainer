import os
import threading
import time

try:
    from dotenv import load_dotenv
    # Load API Key from .env file if it exists
    load_dotenv()
except ImportError:
    # If dotenv is not installed, we'll just use standard os.environ
    pass

class AICoach:
    def __init__(self, api_key=None):
        """
        Initialize the AI Coach with Llama-3 via Groq.
        """
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        self.client = None
        
        try:
            from groq import Groq
            if self.api_key:
                self.client = Groq(api_key=self.api_key)
            else:
                print("  [AI Coach Warning] GROQ_API_KEY not found. Running in demo mode.")
        except ImportError:
            print("  [AI Coach Error] 'groq' library not found. Running in demo mode.")

        self._tip_in_progress = False
        self.last_tip = "Ready to start? Let's go!"

    def get_coaching_tip_async(self, metrics, callback):
        """
        Fetch a coaching tip from Llama-3 in a background thread.
        """
        if self._tip_in_progress:
            return # Avoid concurrent calls
            
        thread = threading.Thread(target=self._generate_tip, args=(metrics, callback))
        thread.daemon = True
        thread.start()

    def _generate_tip(self, metrics, callback):
        self._tip_in_progress = True
        
        # Varied fallback tips for when the AI is slow or offline
        fallbacks = [
            "Keep those movements smooth and controlled!",
            "Excellant form! Push through the remaining reps.",
            "Stay steady and focus on the contraction.",
            "Great consistency! You're making real progress.",
            "Remember to breathe and maintain stability.",
            "Perfect rhythm! Let's get that next rep."
        ]
        
        try:
            # If no client or API key, skip LLM call and use a random fallback tip
            if not self.client:
                import random
                time.sleep(1.2) # simulate thinking
                tip = random.choice(fallbacks)
                self.last_tip = tip
                callback(tip)
                return

            # Enhanced prompt including Temporal Metrics
            temporal_summary = metrics.get('temporal_summary', 'Normal movement.')
            
            prompt = f"""
            You are a professional AI Fitness Coach. 
            Based on the following data from an AI Pose Detector and Temporal Trend Analyzer,
            give a SHORT, encouraging, and highly specific coaching tip to the user.
            
            Current Performance:
            - Exercise: {metrics.get('exercise', 'Unknown')}
            - Total Reps/Duration: {metrics.get('count', 0)}
            - Average Form Score: {metrics.get('score', 0)}/100
            - Temporal Posture Analysis (LSTM-based): {temporal_summary}
            - Last Automated Feedback: {metrics.get('feedback', 'No feedback yet')}
            
            Guidelines:
            - Keep it under 20 words.
            - Reference their stability or consistency if mentioned in temporal analysis.
            - Focus on improving form or maintaining intensity.
            - Be encouraging but direct.
            
            Your tip:
            """
            
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",  # Top tier Llama model
                max_tokens=60,
                # Try to use timeout in a generic way if possible, or omit if strictly using Groq client
            )
            
            tip = chat_completion.choices[0].message.content.strip().replace('"', '')
            self.last_tip = tip
            callback(tip)
            
        except Exception as e:
            # print(f"  [AI Coach Error] {e}")
            import random
            self.last_tip = random.choice(fallbacks)
            callback(self.last_tip)
        finally:
            self._tip_in_progress = False
