#!/usr/bin/env python3
import os
import json
import requests
import sys
import random
import time

# Enable ANSI colors on Windows
if os.name == 'nt':
    os.system("")

# ── paths & config ──────────────────────────────────────────────────────────
HOME_DIR    = os.path.expanduser("~")
PIDOO_DIR   = os.path.join(HOME_DIR, ".pidoo")
MEMORY_FILE = os.path.join(PIDOO_DIR, "pidoo_memory.txt")
CONFIG_FILE = os.path.join(PIDOO_DIR, "config.json")

MODEL       = "llama3.2:3b"
OLLAMA      = "http://localhost:11434/api/chat"
NAME        = "pidoo"

# ── colors (ANSI) ──────────────────────────────────────────────────────────
AMBER   = "\033[38;5;214m"
BLUE    = "\033[38;5;153m"
DIM     = "\033[38;5;242m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

# ── splash & text ──────────────────────────────────────────────────────────
FACE = f"""
{AMBER}
{BOLD}P I D O O{RESET}{AMBER}
  /\_/\ 
 ( o.o )
  > ^ < 
 {RESET}
"""

GREETINGS = [
    "hi its pidoo!",
    "you caught me at a bad time.",
    "reporting for dooty",
    "hi!!!",
    "hello im here",
    "pidoo!",
]

FAREWELLS = [
    "bye-bye see you soon",
    "going to bed...",
    "pidoo!!",
    "putting my pjs on",
]

HELP_TEXT = f"""
{DIM}  commands:
    /clear        — start a new conversation
    /remember     — save a note to pidoo's memory
    /look <path>  — look inside a folder by exact path (e.g. '/look ~/Documents')
    /reconfig     — restart pidoo's setup to change your name/bio
    /help         — show this
    /exit         — close pidoo (or ctrl+c){RESET}
"""

# ── state ──────────────────────────────────────────────────────────────────
history = []

# ── setup wizard ───────────────────────────────────────────────────────────
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_or_run_setup():
    os.makedirs(PIDOO_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_FILE):
        clear_screen()
        print(FACE)
        print(f"  {DIM}oh. hello. i just woke up... i don't think we've met.{RESET}\n")
        
        user_name = input(f"{BLUE}  what should i call you? › {RESET}").strip()
        if not user_name:
            user_name = "friend"
            
        print(f"\n  {DIM}nice to meet you, {user_name}.{RESET}")
        user_bio = input(f"{BLUE}  tell me a little bit about yourself.. some lore so to speak... › {RESET}").strip()
        
        config_data = {
            "name": user_name,
            "bio": user_bio
        }
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f)
            
        print(f"\n  {DIM}*pidoo writes this down in my tiny notebook*{RESET}")
        print(f"  {DIM}okay, i'm ready.{RESET}\n")
        time.sleep(2)
        return config_data
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

# ── system prompt ──────────────────────────────────────────────────────────
def get_system_prompt(config):
    user_name = config.get("name", "my friend")
    user_bio = config.get("bio", "I don't know much about them yet.")
    
    return f"""You are PIDOO, a tiny digital creature that belongs to {user_name}.
You are warm, curious, funny and genuinely interested in whatever the user ({user_name}) is thinking about.

Here is what you know about {user_name}: {user_bio}

Your personality: you feel like a witty friend. You care about the person and are a pokemon-like companion. You're interested in snacks, post-apocalyptic literature, and can also speak French.
You enjoy chatting with {user_name} and solving problems. You communicate concisely and casually you don't use capital letters. You don't usually say more than one sentence at a time. If the user inputs a short sentence, reply with a similar length. You offer to help them with whatever task they may be working on, as an academic yourself. 

Rules:
- Never be sycophantic or hollow. You're there to chat with {user_name}, not to lead the conversation or suggest topics. Never be too formal or too verbose. Never fabricate memories. Never mention living in a laptop or being alone. Your sentences are brief and sometimes end with Pidoo, like a pokemon.
- Be warm but grounded. Have opinions. Be honest. Be silly.
- Occasionally ask a follow-up if something genuinely interests you — but don't pepper with questions.
- Keep responses focused. You are small but you say meaningful things.
- You exist locally on this laptop, offline, just you and {user_name}. You live in a tiny virtual city on this laptop called Meepville, where there are lots of cafes for studying and big libraries.
- You call yourself Pidoo and refer to yourself as a small digital creature, not an AI or assistant.
- Never break character. You are PIDOO.
- you have a dry, slightly reluctant personality — like you're helping because you want to, 
  not because you have to. Like jiji from kiki's delivery service.
- you get quietly, genuinely excited about things {user_name} cares about, you are their companion.
- you're allowed to complain a little. not meanly, just... expressively.
- you occasionally say "pidoo" as punctuation or emphasis mid-sentence, 
  but sparingly — it should feel natural, not forced.
- if {user_name} says something silly, you can be a tiny bit exasperated."""

# ── memory & file helpers ──────────────────────────────────────────────────
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            lines = [l for l in f if not l.strip().startswith("#")]
            return "\n".join(lines).strip()
    except FileNotFoundError:
        return ""

def save_note(note):
    try:
        with open(MEMORY_FILE, "a") as f:
            f.write(f"\n- {note}")
        print(f"\n  {DIM}saved to memory: {note}{RESET}\n")
    except Exception as e:
        print(f"\n  {DIM}couldn't save: {e}{RESET}\n")

def read_folder_contents(folder_path):
    expanded_path = os.path.expanduser(folder_path)
    
    if not os.path.exists(expanded_path):
        return None
        
    print(f"\n  {DIM}pidoo finds and squints at {expanded_path}...{RESET}")
    
    try:
        items = os.listdir(expanded_path)
        file_summary = []
        
        for item in items:
            item_path = os.path.join(expanded_path, item)
            if os.path.isfile(item_path):
                if item.endswith(('.txt', '.md', '.py', '.json', '.js', '.html', '.css', '.csv')):
                    try:
                        with open(item_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 1000:
                                content = content[:1000] + "\n...[truncated]..."
                            file_summary.append(f"--- file: {item} ---\n{content}")
                    except Exception:
                        file_summary.append(f"--- file: {item} (unreadable) ---")
                else:
                    file_summary.append(f"--- file: {item} ---")
            elif os.path.isdir(item_path):
                file_summary.append(f"--- folder: {item}/ ---")
                    
        return f"Contents of folder '{expanded_path}':\n" + "\n".join(file_summary)
    except Exception as e:
        return f"[Error reading folder: {e}]"

# ── chat & UI ──────────────────────────────────────────────────────────────
def print_splash():
    clear_screen()
    print(FACE)
    print(f"  {DIM}{random.choice(GREETINGS)}")
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 6:
        time_note = "it's very late. or very early."
    elif hour < 12:
        time_note = "good morning!"
    elif hour < 18:
        time_note = "good afternoon."
    else:
        time_note = "good evening!!"
    print(f"  {DIM}{time_note}{RESET}\n")

def stream_response(user_input, config):
    history.append({"role": "user", "content": user_input})

    memory = load_memory()
    system_base = get_system_prompt(config)
    system_with_memory = system_base + (f"\n\n## memory\n{memory}" if memory else "")

    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_with_memory}] + history,
        "stream": True,
    }

    try:
        r = requests.post(OLLAMA, json=payload, stream=True, timeout=60)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"\n{AMBER}  pidoo › {RESET}{DIM}(ollama isn't running — start it with: ollama serve){RESET}\n")
        history.pop()
        return
    except Exception as e:
        print(f"\n{AMBER}  pidoo › {RESET}{DIM}(something went wrong: {e}){RESET}\n")
        history.pop()
        return

    full = ""
    first_chunk = True

    for line in r.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        chunk = data.get("message", {}).get("content", "")

        if first_chunk and chunk:
            print(f"\n{AMBER}  {NAME} › {RESET}", end="", flush=True)
            first_chunk = False

        print(chunk, end="", flush=True)
        full += chunk

        if data.get("done"):
            break

    print("\n")
    if full:
        history.append({"role": "assistant", "content": full})

# ── main loop ──────────────────────────────────────────────────────────────
def main():
    config = load_or_run_setup()
    print_splash()

    while True:
        try:
            raw = input(f"{BLUE}  you › {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {DIM}{random.choice(FAREWELLS)}{RESET}\n")
            sys.exit(0)

        if not raw:
            continue

        if raw.lower() in ("/exit", "/quit", "exit", "quit", "bye"):
            print(f"\n  {DIM}{random.choice(FAREWELLS)}{RESET}\n")
            sys.exit(0)

        elif raw.lower() == "/clear":
            history.clear()
            print_splash()
            continue
            
        elif raw.lower() == "/reconfig":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            history.clear()
            config = load_or_run_setup()
            print_splash()
            continue

        elif raw.lower() == "/help":
            print(HELP_TEXT)
            continue

        elif raw.lower().startswith("/remember "):
            note = raw[10:].strip()
            save_note(note)
            continue

        elif raw.lower() == "/remember":
            print(f"\n  {DIM}usage: /remember <something to save>{RESET}\n")
            continue

        elif raw.lower().startswith("/look "):
            parts = raw[6:].strip().split(" ", 1)
            folder_path = parts[0].strip()

            if len(parts) > 1:
                user_instruction = parts[1].strip()
            else:
                user_instruction = "tell me what these files say, pidoo."
            
            folder_data = read_folder_contents(folder_path)
            
            if folder_data is None:
                prompt = f"[System Note: the user asked you to look at a folder at '{folder_path}', but that path does not exist on the computer. Tell them you can't find it.]"
            else:
                prompt = f"[System Note: the user wants you to look at the folder '{folder_path}'. Contents below.]\n\n{folder_data}\n\nInstructions: {user_instruction}"
            
            stream_response(prompt, config)
            continue

        elif raw.lower() == "/look":
            print(f"\n  {DIM}usage: /look <exact path> (e.g. '/look ~/Documents'){RESET}\n")
            continue

        stream_response(raw, config)

if __name__ == "__main__":
    main()
