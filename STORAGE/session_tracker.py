import csv
import os
from datetime import datetime
from collections import defaultdict

# Path to the data sheet
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workout_history.csv")

def ensure_file_exists():
    """Ensure the CSV file exists with the proper headers."""
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Username", "Exercise", "Reps/Seconds", "Score"])

def log_session(username, exercise, value, score):
    """
    Log a workout session to the Excel-compatible CSV datasheet.
    
    Args:
        username (str): The player's name
        exercise (str): The name of the exercise (e.g. 'Push-ups')
        value (int|float): Reps or hold duration in seconds
        score (int|float): The form accuracy score
    """
    if not username or username.strip() == "":
        username = "Guest"
        
    ensure_file_exists()
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_str, username, exercise, round(value, 2), round(score, 2)])
        
    print(f"\n  [✔] Session saved for {username} ({exercise}: {value} @ {round(score)} score)\n")

def print_leaderboard():
    """Reads the CSV file and prints a multi-player Leaderboard grouped by exercise."""
    if not os.path.exists(CSV_FILE_PATH):
        print("\n  [!] No workout history found for the Leaderboard yet. Get moving!")
        return

    # Dictionary: { "Push-ups": { "Username": max_reps } }
    exercise_records = defaultdict(lambda: defaultdict(float))
    
    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row.get("Username", "Unknown")
                exercise = row.get("Exercise", "Unknown")
                value = float(row.get("Reps/Seconds", 0))
                
                # Keep only the highest reps/duration per user per exercise
                if value > exercise_records[exercise][username]:
                    exercise_records[exercise][username] = value
                    
        # Print Leaderboard
        print("\n" + "="*50)
        print("                 🏆 LEADERBOARD 🏆                 ")
        print("="*50)
        
        if not exercise_records:
            print("  No entries found.")
        
        for exercise, user_scores in exercise_records.items():
            print(f"\n  -- {exercise} --")
            # Sort by highest value
            sorted_users = sorted(user_scores.items(), key=lambda item: item[1], reverse=True)
            for rank, (user, val) in enumerate(sorted_users, 1):
                suffix = "s" if "Plank" in exercise else "reps" # Quick guess based on name
                print(f"    {rank}. {user.ljust(15)} : {val} {suffix}")
                
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"\n  [!] Error reading leaderboard: {e}")
