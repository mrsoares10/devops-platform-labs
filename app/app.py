import threading
import time
from flask import Flask, jsonify
import prometheus_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

state = {
    "hunger": 50,
    "happiness": 50,
    "energy": 50
}

hunger_gauge = prometheus_client.Gauge("tamagotchi_hunger", "Hunger level")
happiness_gauge = prometheus_client.Gauge("tamagotchi_happiness", "Happiness level")
energy_gauge = prometheus_client.Gauge("tamagotchi_energy", "Energy level")

app = Flask(__name__)

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})

@app.route("/status")
def status():
    return jsonify(state)

@app.route("/feed", methods=["POST"])
def feed():
    state["hunger"] = min(100, state["hunger"] + 10)
    hunger_gauge.set(state["hunger"])
    logger.info("Tamagotchi fed, hunger: %s", state["hunger"])
    return jsonify(state)

@app.route("/play", methods=["POST"])
def play():
    state["happiness"] = min(100, state["happiness"] + 10)
    happiness_gauge.set(state["happiness"])
    logger.info("Tamagotchi played, happiness: %s", state["happiness"])
    return jsonify(state)

@app.route("/sleep", methods=["POST"])
def sleep():
    state["energy"] = min(100, state["energy"] + 10)
    energy_gauge.set(state["energy"])
    logger.info("Tamagotchi slept, energy: %s", state["energy"])
    return jsonify(state)

@app.route("/metrics")
def metrics():
    return prometheus_client.generate_latest(), 200, {"Content-Type": prometheus_client.CONTENT_TYPE_LATEST}

def decay():
    while True:
        time.sleep(300)
        state["hunger"] = max(0, state["hunger"] - 5)
        state["happiness"] = max(0, state["happiness"] - 5)
        state["energy"] = max(0, state["energy"] - 5)
        hunger_gauge.set(state["hunger"])
        happiness_gauge.set(state["happiness"])
        energy_gauge.set(state["energy"])
        logger.info("Tamagotchi stats decayed, hunger: %s, happiness: %s, energy: %s", state["hunger"], state["happiness"], state["energy"])
        if state["hunger"] == 0:
            logger.warning("Tamagotchi is starving!")

thread = threading.Thread(target=decay, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
