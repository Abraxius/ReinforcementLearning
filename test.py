from stable_baselines3 import PPO
from CarRacingGym import CarRacingGymWrapper

# Gym-Environment initialisieren
env = CarRacingGymWrapper()

# Modell laden
model = PPO.load("ppo_car_racing")

# Umgebung zurücksetzen
obs, _ = env.reset()
print("Start: ", obs)

# Agenten fahren lassen
for _ in range(20000):
    #print("Vor Step")
    action, _ = model.predict(obs)  # Nächste Aktion berechnen
    #print("Aktion:", action)

    obs, reward, done, _, _ = env.step(action)
    print("Nach Step:", obs, "Reward:", reward, "Done:", done)

    env.render()

env.close()
