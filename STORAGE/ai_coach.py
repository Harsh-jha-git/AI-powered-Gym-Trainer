import google.generativeai as genai
import os
import threading

class AICoach:
    def __init__(self, api_key):
        """
        Initialize the AI Coach with Gemini 1.5 Flash.
        """
        genai.configure(api_key=api_key)
        # Try fallback models if the primary one is not found
        models_to_try = [
            'gemini-1.5-flash',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-pro'
        ]
        
        self.model = None
        for model_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Quick check if it's valid (will throw if invalid)
                break
            except Exception:
                continue
                
        if not self.model:
            print("  [AI Coach Error] Could not initialize any Gemini model.")
            self.model = genai.GenerativeModel('gemini-pro') # Final desperate fallback
            
        self._tip_in_progress = False
        self.last_tip = "Ready to start? Let's go!"

    def get_coaching_tip_async(self, metrics, callback):
        """
        Fetch a coaching tip from Gemini in a background thread to avoid stuttering.
        
        Args:
            metrics (dict): Performance data (exercise, reps, score, last_feedback)
            callback (function): Function to call with the generated text tip
        """
        if self._tip_in_progress:
            return  # Avoid concurrent calls
            
        thread = threading.Thread(target=self._generate_tip, args=(metrics, callback))
        thread.daemon = True
        thread.start()

    def _generate_tip(self, metrics, callback):
        self._tip_in_progress = True
        try:
            prompt = f"""
            You are a professional AI Fitness Coach. 
            Based on the following real-time data from an AI Pose Detector, give a SHORT, encouraging, 
            and highly specific coaching tip to the user.
            
            Current Performance:
            - Exercise: {metrics.get('exercise', 'Unknown')}
            - Total Reps/Duration: {metrics.get('count', 0)}
            - Average Form Score: {metrics.get('score', 0)}/100
            - Last Automated Feedback: {metrics.get('feedback', 'No feedback yet')}
            
            Guidelines:
            - Keep it under 20 words.
            - Focus on improving form or maintaining intensity.
            - Be encouraging but direct.
            - Don't sound robotic.
            
            Your tip:
            """
            
            response = self.model.generate_content(prompt)
            tip = response.text.strip().replace('"', '')
            self.last_tip = tip
            callback(tip)
            
        except Exception as e:
            print(f"  [AI Coach Error] {e}")
            self.last_tip = "Keep it up, you're doing great!"
        finally:
            self._tip_in_progress = False
