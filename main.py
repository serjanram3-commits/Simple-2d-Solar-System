import pygame
import sys
import math
import random

pygame.init()


def lighten_color(color, amount):
    r, g, b = color
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return (r, g, b)


class Planet:
    def __init__(self, name, color, distance, radius, speed, rotation_speed=0.05):
        self.name = name
        self.color = color
        self.distance = distance
        self.radius = radius
        self.speed = speed
        self.angle = 0
        self.x = 0
        self.y = 0
 
        self.rotation_speed = rotation_speed
        self.rotation_angle = 0

        # Only used by Earth, but harmless to have on every planet
        self.moon_angle = 0
        self.moon_speed = 0.08

    def update(self, sun_x, sun_y):
        self.angle += self.speed
        self.x = sun_x + self.distance * math.cos(self.angle)
        self.y = sun_y + self.distance * math.sin(self.angle)

        self.rotation_angle += self.rotation_speed
        self.moon_angle += self.moon_speed

    def draw(self, screen, sun_x, sun_y, font):
        # orbit line
        pygame.draw.circle(screen, GRAY, (sun_x, sun_y), self.distance, width=1)

        px, py = int(self.x), int(self.y)

        # Saturn's rings, squished based on rotation to fake a "tilting" 3D look
        if self.name == "Saturn":
            tilt = abs(math.cos(self.rotation_angle))
            ring_height = int(self.radius * 0.5 * tilt) + 4
            ring_rect = (px - self.radius * 2, py - ring_height // 2,
                         self.radius * 4, ring_height)
            pygame.draw.ellipse(screen, (200, 190, 150), ring_rect, width=3)

        # the planet itself
        pygame.draw.circle(screen, self.color, (px, py), self.radius)

        # Jupiter's Great Red Spot: only visible on the "front" half,
        # to fake it rotating around behind the planet
        if self.name == "Jupiter":
            depth = math.cos(self.rotation_angle)
            if depth > 0:
                spot_x = px + int(self.radius * 0.85 * math.sin(self.rotation_angle))
                spot_y = py + int(self.radius * 0.15)
                spot_radius = max(1, int((self.radius // 4) * depth))
                pygame.draw.circle(screen, (180, 70, 50), (spot_x, spot_y), spot_radius)

        # Earth's land patches: same front/back visibility trick, two patches
        # at different rotation offsets so they appear at different times
        if self.name == "Earth":
            for offset in (0, 2.5):
                angle = self.rotation_angle + offset
                depth = math.cos(angle)
                if depth > 0:
                    land_x = px + int(self.radius * 0.5 * math.sin(angle))
                    land_y = py - int(self.radius * 0.2) + int(offset * 4)
                    land_radius = max(2, int((self.radius // 3) * (0.5 + 0.5 * depth)))
                    pygame.draw.circle(screen, (70, 160, 70), (land_x, land_y), land_radius)

            # Earth's moon, orbiting Earth the same way planets orbit the Sun
            moon_distance = self.radius + 12
            moon_x = px + moon_distance * math.cos(self.moon_angle)
            moon_y = py + moon_distance * math.sin(self.moon_angle)
            pygame.draw.circle(screen, (200, 200, 200), (int(moon_x), int(moon_y)), 3)
            moon_label = font.render("Moon", True, WHITE)
            screen.blit(moon_label, (int(moon_x) + 5, int(moon_y) - 8))

        # the label
        label = font.render(self.name, True, WHITE)
        screen.blit(label, (px + self.radius + 4, py - 8))


# --- Window setup ---
WIDTH = 1400
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Solar System Simulation")

FONT = pygame.font.SysFont("arial", 16)

clock = pygame.time.Clock()
FPS = 60

BLACK = (0, 0, 0)
YELLOW = (255, 220, 60)
GRAY = (70, 70, 70)
WHITE = (255, 255, 255)

SUN_X = WIDTH // 2
SUN_Y = HEIGHT // 2
SUN_RADIUS = 40

planets = [
    Planet("Mercury", (169, 169, 169), 80, 6, 0.04),
    Planet("Venus", (230, 200, 140), 115, 9, 0.03),
    Planet("Earth", (80, 140, 230), 150, 10, 0.025),
    Planet("Mars", (210, 100, 60), 190, 8, 0.02),
    Planet("Jupiter", (220, 180, 130), 260, 22, 0.012),
    Planet("Saturn", (230, 210, 160), 320, 18, 0.009),
    Planet("Uranus", (150, 220, 220), 370, 14, 0.006),
    Planet("Neptune", (90, 110, 220), 410, 14, 0.004),
]

NUM_STARS = 150
stars = []
for i in range(NUM_STARS):
    star_x = random.randint(0, WIDTH)
    star_y = random.randint(0, HEIGHT)
    stars.append((star_x, star_y))

# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    for planet in planets:
        planet.update(SUN_X, SUN_Y)

    screen.fill(BLACK)

    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)

    pygame.draw.circle(screen, YELLOW, (SUN_X, SUN_Y), SUN_RADIUS)

    for planet in planets:
        planet.draw(screen, SUN_X, SUN_Y, FONT)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()