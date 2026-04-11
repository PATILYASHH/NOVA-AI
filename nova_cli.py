"""
NOVA - Terminal Interface
Talk to NOVA directly from your terminal. No Telegram needed.
Can also start Telegram bot from here.

Usage:
    python nova_cli.py          → Interactive terminal chat
    python nova_cli.py --bot    → Start Telegram bot
    python nova_cli.py --setup  → First-time setup wizard
"""

import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    print("""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║     ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ║
    ║     ████╗  ██║██╔═══██╗██║   ██║██╔══██╗║
    ║     ██╔██╗ ██║██║   ██║██║   ██║███████║║
    ║     ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║║
    ║     ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║║
    ║     ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝║
    ║                                          ║
    ║     Self-Evolving AI Agent               ║
    ╚══════════════════════════════════════════╝
    """)


def check_setup() -> dict:
    """Check if NOVA is properly set up"""
    status = {
        "env": os.path.exists(os.path.join(BASE_DIR, ".env")),
        "personality": os.path.exists(os.path.join(BASE_DIR, "self", "identity", "personality.md")),
        "emotions": os.path.exists(os.path.join(BASE_DIR, "self", "identity", "emotions.json")),
        "traits": os.path.exists(os.path.join(BASE_DIR, "self", "identity", "traits.json")),
        "knowledge": os.path.exists(os.path.join(BASE_DIR, "self", "knowledge", "learned.json")),
        "claude": shutil.which("claude") is not None,
        "deps": True,
    }

    # Check dependencies
    try:
        import telegram
        import psutil
        import dotenv
    except ImportError:
        status["deps"] = False

    return status


def run_setup():
    """First-time setup wizard"""
    clear_screen()
    print_banner()
    print("  First-Time Setup\n")

    # Step 1: Check dependencies
    print("  [1/4] Checking dependencies...")
    try:
        import telegram
        import psutil
        print("    Dependencies OK")
    except ImportError:
        print("    Installing dependencies...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt -q")
        print("    Done!")

    # Step 2: Create .env
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        print("\n  [2/4] Telegram Setup")
        print("    Get a bot token from @BotFather on Telegram")
        token = input("    Bot Token: ").strip()
        print("    Get your chat ID from @userinfobot on Telegram")
        chat_id = input("    Chat ID: ").strip()
        name = input("    Your Name: ").strip() or "User"

        with open(env_path, 'w') as f:
            f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
            f.write(f"AUTHORIZED_CHAT_IDS={chat_id}\n")
            f.write(f"OWNER_NAME={name}\n")
        print("    .env created!")
    else:
        print("\n  [2/4] .env already exists - skipping")

    # Step 3: Create personality files from examples
    print("\n  [3/4] Setting up identity...")
    copies = [
        ("self/identity/personality.example.md", "self/identity/personality.md"),
        ("self/identity/emotions.example.json", "self/identity/emotions.json"),
        ("self/identity/traits.example.json", "self/identity/traits.json"),
        ("self/knowledge/learned.example.json", "self/knowledge/learned.json"),
    ]
    for src, dst in copies:
        src_path = os.path.join(BASE_DIR, src)
        dst_path = os.path.join(BASE_DIR, dst)
        if not os.path.exists(dst_path) and os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"    Created {dst}")
        else:
            print(f"    {dst} already exists")

    # Step 4: Create required directories
    print("\n  [4/4] Creating directories...")
    dirs = ["logs", "logs/commands", "logs/daily", "memory/RM", "memory/RAM", "memory/ROM",
            "memory/vector_db", "self/diary", "self/performance", "self/daily_errors",
            "self/fix_proposals", "self/improvements", "projects", "intelligence/data",
            "schedules"]
    for d in dirs:
        os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)
    print("    All directories created!")

    print("\n  Setup complete! You can now:")
    print("    python nova_cli.py        → Chat with NOVA in terminal")
    print("    python nova_cli.py --bot  → Start Telegram bot")
    print()
    input("  Press Enter to continue...")


def run_terminal_chat():
    """Interactive terminal chat with NOVA"""
    clear_screen()
    print_banner()
    print("  Terminal Mode - Chat with NOVA directly")
    print("  Type 'quit' or 'exit' to leave")
    print("  Type 'bot' to switch to Telegram mode")
    print("  " + "─" * 40)
    print()

    try:
        from core.personality import Personality
        personality = Personality()
        greeting = personality.get_greeting()
        print(f"  NOVA: {greeting}\n")
    except Exception as e:
        print(f"  [Error loading NOVA brain: {e}]")
        print("  NOVA: Hey! I'm having trouble loading fully, but I can still chat.\n")
        personality = None

    while True:
        try:
            user_input = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  NOVA: Later! I'll be here.\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print("\n  NOVA: See you! I'll be here when you need me.\n")
            break

        if user_input.lower() == "bot":
            print("\n  Switching to Telegram mode...\n")
            run_telegram_bot()
            return

        if user_input.lower() == "status":
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
                print(f"\n  System: CPU {cpu}% | RAM {mem.percent}% | Disk {disk.percent}%\n")
            except Exception:
                print("\n  Couldn't get system info.\n")
            continue

        # Get response from NOVA
        if personality:
            try:
                context = {"time_of_day": __import__('datetime').datetime.now().strftime("%I:%M %p")}
                try:
                    import psutil
                    context["system_state"] = {
                        "cpu_percent": psutil.cpu_percent(interval=0),
                        "memory_percent": psutil.virtual_memory().percent,
                    }
                except Exception:
                    pass

                print("  NOVA: ...", end="\r")
                response = personality.generate_response(user_input, context)
                # Clear the "..." and print response
                print(f"  NOVA: {response}\n")
            except Exception as e:
                print(f"  NOVA: Had a brain glitch: {str(e)[:100]}\n")
        else:
            print("  NOVA: I'm not fully loaded. Try restarting.\n")


def run_telegram_bot():
    """Start the Telegram bot"""
    clear_screen()
    print_banner()
    print("  Starting Telegram Bot...\n")

    # Check .env
    if not os.path.exists(os.path.join(BASE_DIR, ".env")):
        print("  No .env file found! Run setup first:")
        print("    python nova_cli.py --setup")
        return

    try:
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n\n  NOVA Telegram bot stopped.")
    except Exception as e:
        print(f"\n  Error: {e}")
        print("  Try: python nova_cli.py --setup")


def show_menu():
    """Show main menu"""
    clear_screen()
    print_banner()

    status = check_setup()
    needs_setup = not all(status.values())

    if needs_setup:
        print("  Status: Some setup needed\n")
        for key, ok in status.items():
            icon = "OK" if ok else "MISSING"
            print(f"    {key:15s} [{icon}]")
        print()

    print("  What would you like to do?\n")
    print("    [1] Chat with NOVA (Terminal)")
    print("    [2] Start Telegram Bot")
    print("    [3] Setup / Reconfigure")
    print("    [4] System Status")
    print("    [5] Exit")
    print()

    choice = input("  Choose [1-5]: ").strip()

    if choice == "1":
        if needs_setup and not status["claude"]:
            print("\n  Claude CLI not found! Install it first.")
            print("  https://docs.anthropic.com/en/docs/claude-code")
            input("  Press Enter...")
            return True
        run_terminal_chat()
    elif choice == "2":
        if not status["env"]:
            print("\n  Run setup first! (Option 3)")
            input("  Press Enter...")
            return True
        run_telegram_bot()
    elif choice == "3":
        run_setup()
    elif choice == "4":
        print()
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
            print(f"    CPU:  {cpu}%")
            print(f"    RAM:  {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)")
            print(f"    Disk: {disk.percent}% ({disk.free // (1024**3)}GB free)")
        except Exception:
            print("    Couldn't get system info.")

        # Vector memory stats
        try:
            from core.vector_memory import VectorMemory
            vm = VectorMemory()
            stats = vm.get_stats()
            print(f"\n    Vector Memory:")
            print(f"      Conversations: {stats.get('conversations', 0)}")
            print(f"      Knowledge:     {stats.get('knowledge', 0)}")
            print(f"      Tasks:         {stats.get('tasks', 0)}")
        except Exception:
            pass

        print()
        input("  Press Enter...")
    elif choice == "5":
        print("\n  Bye!\n")
        return False

    return True


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--setup" in args:
        run_setup()
    elif "--bot" in args:
        run_telegram_bot()
    elif "--chat" in args:
        run_terminal_chat()
    else:
        # Interactive menu
        running = True
        while running:
            running = show_menu()
