import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pishock import PiShockAPI

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CONFIG_PATH = "config.json"

def prompt_user_for_input(prompt, default_value, value_type=int):
    user_input = input(f"{prompt} (default {default_value}): ")
    if not user_input:
        return default_value
    try:
        return value_type(user_input)
    except ValueError:
        print(f"Invalid input. Using default value {default_value}.")
        return default_value

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
else:
    print("First time setup: Please provide the following details to configure PiShock.")
    config = {
        "username": input("Enter your PiShock username: "),
        "api_key": input("Enter your PiShock API key: "),
        "share_code": input("Enter your PiShock share code: "),
        "operation": prompt_user_for_input("Enter default operation (0=shock, 1=vibrate, 2=beep)", 0),
        "duration": prompt_user_for_input("Enter default duration (seconds)", 1),
        "intensity": prompt_user_for_input("Enter default intensity (1-100)", 50)
    }

    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file)

# Initialize PiShock API
api = PiShockAPI(config["username"], config["api_key"])
shocker = api.shocker(config["share_code"], name="PD2Demange")

def log_action(action, duration, intensity=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if intensity is not None:
        print(f"[{current_time}] Action: {action.capitalize()} | Duration: {duration}s | Intensity: {intensity}%")
    else:
        print(f"[{current_time}] Action: {action.capitalize()} | Duration: {duration}s")

@app.route("/trigger", methods=["GET"])
def trigger_shock():
    try:
        op = int(request.args.get("op", config["operation"]))
        duration = int(request.args.get("duration", config["duration"]))  # Default to 1 second
        intensity = int(request.args.get("intensity", config["intensity"]))  # Default to 50%

        # Validate parameters
        if not (1 <= duration <= 15):
            return jsonify({"error": "Duration must be between 1 and 15 seconds."}), 400
        if not (1 <= intensity <= 100):
            return jsonify({"error": "Intensity must be between 1 and 100."}), 400

        if op == 0:
            shocker.shock(duration=duration, intensity=intensity)
            action = "shock"
            log_action(action, duration, intensity)
        elif op == 1:
            shocker.vibrate(duration=duration, intensity=intensity)
            action = "vibrate"
            log_action(action, duration, intensity)
        elif op == 2:
            shocker.beep(duration=duration)
            action = "beep"
            log_action(action, duration)
        else:
            return jsonify({"error": "Invalid operation. Use 0 for shock, 1 for vibrate, or 2 for beep."}), 400

        return jsonify({"message": f"{action.capitalize()} request sent successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=3000)
