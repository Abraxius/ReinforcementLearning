import pygame
import math
import numpy as np
import random

# Konstanten
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
GRID_SIZE = 50  # Größe der Rasterzellen
TRACK_WIDTH = 3  # Breite der Straße in Rasterzellen
CAR_SIZE = (50, 25)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)

# was hat er für eine observatin? erhöhe das field of view, damit er mehr sieht
class Car:
    def __init__(self, start_x, start_y):
        self.x, self.y = start_x * GRID_SIZE + (GRID_SIZE/2), start_y * GRID_SIZE + (GRID_SIZE/2) # Start auf der Straße
        self.angle = 0  # Richtung in Grad
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.friction = 0.02
        self.turn_speed = 3
        self.image = pygame.Surface(CAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, *CAR_SIZE))
        self.visited_cells = set()
        self.prev_x = self.x
        self.prev_y = self.y

    def get_sensors(self, track):
        """Simuliert Sensoren, die erkennen, wie weit die nächste Straße oder das nächste Hindernis entfernt ist."""
        sensor_angles = [-45, -20, 0, 20, 45]  # Sensoren in verschiedene Richtungen
        sensor_distances = []  # Liste mit allen Sensorwerten
    
        max_distance = 200  # Maximale Reichweite der Sensoren
    
        for angle_offset in sensor_angles:
            sensor_angle = self.angle + angle_offset  # Berechne den Sensorwinkel
            rad = math.radians(sensor_angle)
    
            # Sensorstrahl: Geht solange weiter, bis er auf Gras trifft
            for d in range(0, max_distance, 10):  # Schrittweise um 10 Pixel
                sensor_x = self.x + d * math.cos(rad)
                sensor_y = self.y + d * math.sin(rad)
    
                # Falls das Auto außerhalb der Straße ist, speichere die Distanz
                if not track.is_on_track(sensor_x, sensor_y):
                    sensor_distances.append(d)  # Speichere, wie weit das Hindernis entfernt ist
                    break
            else:
                sensor_distances.append(max_distance)  # Falls nichts gefunden, max. Distanz speichern
    
        return sensor_distances  # Gibt eine Liste von Distanzen zurück
    
    def update(self, action):
        gas, brake, left, right = action
        if gas:
            self.speed += self.acceleration
        if brake:
            self.speed -= self.acceleration * 1.5
        self.speed = max(-self.max_speed / 2, min(self.speed, self.max_speed))
        if left:
            self.angle -= self.turn_speed
        if right:
            self.angle += self.turn_speed
        self.speed *= (1 - self.friction)
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))

    def get_grid_position(self):
        return int(self.x // GRID_SIZE), int(self.y // GRID_SIZE)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class RaceTrack:
    def __init__(self):
        self.track_cells, self.start_position = self.generate_track()

    def generate_track(self):
        import random
        track_cells = set()
        
        # Use screen dimensions to ensure track stays within bounds
        # Assuming SCREEN_WIDTH and SCREEN_HEIGHT are defined elsewhere
        max_grid_x = SCREEN_WIDTH // GRID_SIZE - 1
        max_grid_y = SCREEN_HEIGHT // GRID_SIZE - 1
        
        # Define track parameters
        min_width = 8
        max_width = min(15, max_grid_x - 2)  # Ensure it fits within screen
        min_height = 8
        max_height = min(15, max_grid_y - 2)  # Ensure it fits within screen
        track_thickness = 1  # Width of track wall in cells
        
        # Randomly determine track size
        width = random.randint(min_width, max_width)
        height = random.randint(min_height, max_height)
        
        # Calculate maximum possible offsets that keep track on screen
        max_offset_x = max_grid_x - width
        max_offset_y = max_grid_y - height
        
        # Calculate offsets ensuring the track stays on screen
        offset_x = random.randint(1, max(1, max_offset_x))
        offset_y = random.randint(1, max(1, max_offset_y))
        
        # Create outer border (this forms a closed loop)
        for i in range(offset_x, width + offset_x + 1):
            # Top and bottom borders
            for j in range(track_thickness):
                track_cells.add((i, offset_y + j))  # Top border
                track_cells.add((i, offset_y + height - j))  # Bottom border
                
        for i in range(offset_y, height + offset_y + 1):
            # Left and right borders
            for j in range(track_thickness):
                track_cells.add((offset_x + j, i))  # Left border
                track_cells.add((offset_x + width - j, i))  # Right border
        
        start_position = random.choice(list(track_cells))
        
        return track_cells, start_position

    def draw(self, screen):
        for x, y in self.track_cells:
            pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        for x, y in self.track_cells:
            pygame.draw.rect(screen, BLUE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def is_on_track(self, x, y):
        return (int(x // GRID_SIZE), int(y // GRID_SIZE)) in self.track_cells

    def get_distance_to_track(self, x, y):
        return min(
            math.sqrt((x - (grid_x * GRID_SIZE + GRID_SIZE / 2)) ** 2 +
                      (y - (grid_y * GRID_SIZE + GRID_SIZE / 2)) ** 2)
            for grid_x, grid_y in self.track_cells
        )

    def is_far_off_track(self, x, y):
        # Berechnet die minimale Distanz zur Straße
        min_distance = self.get_distance_to_track(x, y)
        return min_distance > GRID_SIZE  # Falls das Auto mehr als 2 Felder entfernt ist, ist es "tot"
    
class CarRacingEnv:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.track = RaceTrack()
        self.car = Car(*self.track.start_position)
        self.total_reward = 0  # Gesamt-Reward initialisieren
        self.steps = 0  # Zähler für Schritte

    def reset(self):
        self.track = RaceTrack()
        self.car = Car(*self.track.start_position)
        self.total_reward = 0  # Gesamt-Reward zurücksetzen
        self.steps = 0  # Zähler für Schritte
        #print("reset")
        return (self.car.x, self.car.y, self.car.angle, self.car.speed)


    def step(self, action):
        self.car.update(action)
        self.steps += 1  # Schrittzähler erhöhen
    
        # Sensoren auslesen
        sensor_data = self.car.get_sensors(self.track)
        #print(f"Sensor Data Length: {len(sensor_data)}")  # Debug-Ausgabe
        
        # Grundstrafe pro Frame (-0.1 für jedes Frame)
        reward = -0.1
    
        grid_pos = self.car.get_grid_position()
        done = False
    
        total_track_cells = len(self.track.track_cells)  # Anzahl aller Straßenzellen
    
        # Prüfen, ob das Auto sich noch auf der Straße befindet
        if self.track.is_on_track(self.car.x, self.car.y):
            if grid_pos not in self.car.visited_cells:
                total_track_cells = len(self.track.track_cells)
    
                # Belohnung für das Entdecken einer neuen Rasterzelle (+1000/N)
                reward += 1000 / total_track_cells
    
                self.car.visited_cells.add(grid_pos)
    
            # Falls ALLE Straßen-Raster entdeckt wurden, ist das Spiel gewonnen
            if len(self.car.visited_cells) == total_track_cells:
                print("Alle Straßenraster entdeckt! Spiel gewonnen!")
                done = True
        else:
            # Falls das Auto zu weit von der Strecke entfernt ist, gibt es eine hohe Strafe & Reset
            if self.track.is_far_off_track(self.car.x, self.car.y):
                reward -= 1000
                done = True
            else:
                reward -= 1.0  # Strafe für leichtes Verlassen der Strecke
    
        # Falls das Auto zu lange fährt, beende das Spiel
        if self.steps > 1000:
            done = True
    
        self.total_reward += reward  # Gesamt-Reward aktualisieren
    
        # **NEU:** Sensorwerte an die Observation anhängen
        return (self.car.x, self.car.y, self.car.angle, self.car.speed, *sensor_data), reward, done

    
    def render(self):
        for event in pygame.event.get():  # Verhindert PyGame-Freezing
            if event.type == pygame.QUIT:
                pygame.quit()
    
        self.screen.fill(GREEN)
        self.track.draw(self.screen)
        self.car.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)  # FPS-Limit, verhindert CPU-Überlastung

    def close(self):
        pygame.quit()

if __name__ == "__main__":
    env = CarRacingEnv()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        action = [keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]]
        env.step(action)
        env.render()
    env.close()