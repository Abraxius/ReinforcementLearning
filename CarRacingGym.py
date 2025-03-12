import gymnasium as gym
from gymnasium import spaces
import numpy as np
from CarRacing import CarRacingEnv  # Importiere dein PyGame-Environment

class CarRacingGymWrapper(gym.Env):
    def __init__(self):
        super(CarRacingGymWrapper, self).__init__()
        self.env = CarRacingEnv()  # Dein PyGame Environment

        # **Neue Observation: (x, y, Winkel, Geschwindigkeit) + 5 Sensorwerte**
        low = np.array([0, 0, -180, -5] + [0] * 5, dtype=np.float32)  # Sensorwerte min. 0 (direkt vor Hindernis)
        high = np.array([1000, 1000, 180, 5] + [200] * 5, dtype=np.float32)  # Sensor max. 200 Pixel Sichtweite

        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

        # Aktionen: Gas, Bremse, Links, Rechts (diskret)
        self.action_space = spaces.MultiBinary(4)  # 4 Buttons (0 oder 1)

    def reset(self, seed=None, options=None):
        state = self.env.reset()
        sensor_data = self.env.car.get_sensors(self.env.track)  # **Sensoren abrufen**
        full_state = np.array(list(state) + sensor_data, dtype=np.float32)
       # print(f"Full State Length 1: {len(full_state)}")  # Debugging
        
        return full_state, {}

    def step(self, action):
        state, reward, done = self.env.step(action)
        #sensor_data = self.env.car.get_sensors(self.env.track)  # **Sensorwerte abrufen**
        full_state = np.array(list(state), dtype=np.float32) #+sensor_data
        truncated = False  # Falls du ein Zeitlimit hast, setze dies auf True
       # print(f"Full State Length 2: {len(full_state)}")  # Debugging
        return full_state, reward, done, truncated, {}

    def render(self):
        self.env.render()

    def close(self):
        self.env.close()
