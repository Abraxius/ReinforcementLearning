from stable_baselines3 import PPO
import matplotlib.pyplot as plt
import numpy as np
from CarRacingGym import CarRacingGymWrapper

# Gym-Environment initialisieren
env = CarRacingGymWrapper()

# PPO-Agent mit MLP-Policy (für numerische Daten)
model = PPO("MlpPolicy", env, verbose=1, device="cpu")

# Liste zum Speichern der Rewards
reward_history = []
timesteps = []

# Anzahl der Trainingsschritte
total_timesteps = 500000
log_interval = 1000  # Alle 1000 Schritte Training
plot_interval = 10000  # Alle 100000 Schritte das Diagramm aktualisieren

# Initialisiere Matplotlib-Figur (aber öffne sie nur einmal!)
plt.ion()  # Interaktiver Modus (verhindert neue Fenster)
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlabel("Timesteps")
ax.set_ylabel("Reward")
ax.set_title("Training Rewards")
line, = ax.plot([], [], label="Reward-Verlauf")
ax.legend()

# Training mit Logging
for i in range(1, total_timesteps // log_interval + 1):
    model.learn(total_timesteps=log_interval, reset_num_timesteps=False)

    # Evaluierung: Teste das Modell nach jedem Abschnitt
    obs, _ = env.reset()
    total_reward = 0
    for _ in range(1000):  # Teste für 1000 Frames
        action, _ = model.predict(obs)
        obs, reward, done, _, _ = env.step(action)
        total_reward += reward
        if done:
            break

    reward_history.append(total_reward)
    timesteps.append(i * log_interval)

    # Alle 100000 Timesteps das Diagramm aktualisieren, aber KEIN neues Fenster öffnen
    if (i * log_interval) % plot_interval == 0:
        line.set_xdata(timesteps)
        line.set_ydata(reward_history)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1)

# Speichern des trainierten Modells
model.save("ppo_car_racing")

# Letzten Stand des Plots zeigen und interaktiven Modus beenden
plt.ioff()
plt.show()
