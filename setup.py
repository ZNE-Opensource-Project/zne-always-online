import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
VALID_STATUSES = ["online", "dnd", "idle", "invisible", "mobile"]


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        f.write("\n")


def _clean_token(raw):
    return raw.strip().strip('"').strip("'")


def setup():
    print("=== ZNE Always Online Setup Wizard ===\n")

    config = load_config()

    token = _clean_token(input("Enter your token here: "))
    if not token:
        print("Token is required.")
        return

    tokens = [token]

    add_more = input("Do you have any other accounts you wanna keep online? Y/N: ").strip().lower()
    if add_more == "y":
        while True:
            other_token = _clean_token(input("Enter your other token here (write Done if completed): "))
            if other_token.lower() == "done":
                break
            if other_token:
                tokens.append(other_token)

    print("\nAvailable status icons: online, dnd, idle, invisible, mobile")
    status_icon = input("Enter your desired status icon (press Enter for default 'online'): ").strip()
    if not status_icon:
        status_icon = "online"
    if status_icon not in VALID_STATUSES:
        print(f"Invalid status icon '{status_icon}', defaulting to 'online'.")
        status_icon = "online"

    status_msg = input("Enter your desired status message (press Enter for default): ").strip()
    if not status_msg:
        status_msg = "Running ZNE Always online 1.0!"

    config["token"] = tokens[0]
    config["tokens"] = tokens
    config["status_msg"] = status_msg
    config["status_icon"] = status_icon
    config["current_statuschanger"] = "None"

    save_config(config)
    print("\nSetup complete! Configuration saved to config.json")


if __name__ == "__main__":
    setup()
