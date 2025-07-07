import os
import sys
import json
import datetime
import time
from cryptography.fernet import Fernet
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from flask import Flask, render_template, request, redirect
from model.mood import MOODS
# --- New imports for AI analysis ---
from dotenv import load_dotenv
import google.generativeai as genai

# --- Setup ---
console = Console()
DATA_DIR = os.path.expanduser("~/.mindgarden")
KEY_FILE = os.path.join(DATA_DIR, "key.key")
DATA_FILE = os.path.join(DATA_DIR, "journal.json")

# --- Load .env and Google AI key ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- Utilities ---
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as f:
        return f.read()

def encrypt(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt(data, key):
    f = Fernet(key)
    return f.decrypt(data.encode()).decode()

def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            # If the data is not a list, return an empty list or wrap it in a list
            return []

def save_entries(entries):
    with open(DATA_FILE, 'w') as f:
        json.dump(entries, f, indent=2)

# --- AI Analysis Function ---
def analyze_entries(entries, key):
    # Decrypt and concatenate all user reflections, moods, and gratitude
    texts = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        try:
            mood = decrypt(entry["mood"], key)
            gratitude = decrypt(entry["gratitude"], key)
            reflection = decrypt(entry["reflection"], key)
            texts.append(f"Mood: {mood}\nGratitude: {gratitude}\nReflection: {reflection}")
        except Exception:
            continue
    if not texts:
        return "No valid entries to analyze."
    prompt = (
        "You are a helpful, positive psychologist AI. "
        "Given the following journal entries, analyze the user's tendencies and provide a 4-sentence summary of their patterns and how they can improve their life. "
        "Be gentle, supportive, and actionable.\n\n"
        + "\n---\n".join(texts)
    )
    try:
        # Use Gemini 2.5 Flash model explicitly
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI analysis failed: {e}"

# --- CLI Features ---
def breathing_timer():
    console.print("\n[bold blue]Box Breathing Exercise (4x2, 4 rounds)[/bold blue]")
    for round_num in range(1, 5):
        console.print(f"[green]Round {round_num} of 4[/green]")
        for phase in ["Inhale", "Hold", "Exhale", "Hold"]:
            console.print(f"{phase}...")
            for i in range(4, 0, -1):
                console.print(f"[dim]{i}..[/dim]", end=" ", style="cyan")
                time.sleep(1)
            console.print("")
    console.print("Done! Repeat as needed.\n")

def new_entry():
    key = load_key()
    entries = load_entries()
    now = datetime.datetime.now().isoformat()
    mood = Prompt.ask("How are you feeling today?")
    prompt = Prompt.ask("What's one thing you're grateful for today?")
    thoughts = Prompt.ask("Any thoughts or reflections you'd like to add?")
    entry = {
        "timestamp": now,
        "date": str(datetime.date.today()),
        "mood": encrypt(mood, key),
        "gratitude": encrypt(prompt, key),
        "reflection": encrypt(thoughts, key)
    }
    entries.append(entry)
    save_entries(entries)
    console.print(":white_check_mark: Entry saved and encrypted successfully!\n")

def view_entries():
    key = load_key()
    entries = load_entries()
    if not entries:
        console.print(":warning: No journal entries found.")
        return
    table = Table(title="MindGarden Journal")
    table.add_column("Date", style="cyan")
    table.add_column("Mood")
    table.add_column("Gratitude")
    table.add_column("Reflection")
    for entry in entries:
        # Skip entries that are not dictionaries to avoid AttributeError
        if not isinstance(entry, dict):
            continue
        # Format date and time
        date_str = entry.get("date", "")
        timestamp = entry.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        table.add_row(
            date_str,
            decrypt(entry['mood'], key),
            decrypt(entry['gratitude'], key),
            decrypt(entry['reflection'], key)
        )
    console.print(table)

def analyze_journal_cli():
    key = load_key()
    entries = load_entries()
    console.print("\n[bold blue]Analyzing your journal entries with Google AI...[/bold blue]")
    analysis = analyze_entries(entries, key)
    console.print(f"\n[green]AI Analysis:[/green] {analysis}\n")

# --- CLI Main ---
def cli_main():
    ensure_data_dir()
    console.print("\n:herb: [bold green]Welcome to MindGarden[/bold green]")
    while True:
        console.print("\n[1] New Entry\n[2] View Entries\n[3] Breathing Exercise\n[4] Analyze My Journal\n[5] Exit")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
        if choice == "1":
            new_entry()
        elif choice == "2":
            view_entries()
        elif choice == "3":
            breathing_timer()
        elif choice == "4":
            analyze_journal_cli()
        elif choice == "5":
            console.print(":sunny: Goodbye! Keep growing.\n")
            break

# --- Web Interface ---
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    key = load_key()
    entries = load_entries()
    decrypted = [
        {
            "date": entry.get("date", ""),
            "mood": decrypt(entry["mood"], key),
            "gratitude": decrypt(entry["gratitude"], key),
            "reflection": decrypt(entry["reflection"], key)
        } for entry in reversed(entries) if isinstance(entry, dict)
    ]
    analysis = analyze_entries(entries, key)
    return render_template("index.html", entries=decrypted, analysis=analysis)

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        key = load_key()
        entries = load_entries()
        now = datetime.datetime.now().isoformat()
        mood = encrypt(request.form["mood"], key)
        gratitude = encrypt(request.form["gratitude"], key)
        reflection = encrypt(request.form["reflection"], key)
        entry = {
            "timestamp": now,
            "date": str(datetime.date.today()),
            "mood": mood,
            "gratitude": gratitude,
            "reflection": reflection
        }
        entries.append(entry)
        save_entries(entries)
        return redirect("/")
    return render_template("new.html", moods=MOODS)

@app.route("/breathing")
def breathing_web():
    return render_template("breathing.html")

@app.route("/analyze")
def analyze_web():
    key = load_key()
    entries = load_entries()
    decrypted = [
        # Only process entries that are dictionaries to avoid AttributeError
        {
            "date": (datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M") if entry.get("timestamp") else entry.get("date", "")),
            "mood": decrypt(entry["mood"], key),
            "gratitude": decrypt(entry["gratitude"], key),
            "reflection": decrypt(entry["reflection"], key)
        } for entry in reversed(entries) if isinstance(entry, dict)
    ]
    analysis = analyze_entries(entries, key)
    return render_template("index.html", entries=decrypted, analysis=analysis)

# --- Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        app.run(debug=True, port=5001)
    else:
        cli_main()
