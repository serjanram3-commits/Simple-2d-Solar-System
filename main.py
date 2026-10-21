import pygame
import sys
import math
import random
from solar_flare import SolarFlareEvent
pygame.init()


class Planet:
    def __init__(self, name, color, distance, radius, speed, fun_fact, rotation_speed=0.05):
        self.name = name
        self.color = color
        self.distance = distance
        self.radius = radius
        self.speed = speed
        self.fun_fact = fun_fact
        self.angle = 0
        self.x = 0
        self.y = 0

        self.rotation_speed = rotation_speed
        self.rotation_angle = 0

        self.moon_angle = 0
        self.moon_speed = 0.08

        self.hovered = False
        self.selected = False

    def update(self, sun_x, sun_y, speed_multiplier):
        self.angle += self.speed * speed_multiplier
        self.x = sun_x + self.distance * math.cos(self.angle)
        self.y = sun_y + self.distance * math.sin(self.angle)

        self.rotation_angle += self.rotation_speed * speed_multiplier
        self.moon_angle += self.moon_speed * speed_multiplier

    def draw(self, screen, sun_x, sun_y, font):
        # orbit line
        pygame.draw.circle(screen, GRAY, (sun_x, sun_y), self.distance, width=1)

        px, py = int(self.x), int(self.y)

        # Saturn's rings
        if self.name == "Saturn":
            tilt = abs(math.cos(self.rotation_angle))
            ring_height = int(self.radius * 0.5 * tilt) + 4
            ring_rect = (px - self.radius * 2, py - ring_height // 2,
                         self.radius * 4, ring_height)
            pygame.draw.ellipse(screen, (200, 190, 150), ring_rect, width=3)

        # the planet itself
        pygame.draw.circle(screen, self.color, (px, py), self.radius)

        # Jupiter's Great Red Spot
        if self.name == "Jupiter":
            depth = math.cos(self.rotation_angle)
            if depth > 0:
                spot_x = px + int(self.radius * 0.85 * math.sin(self.rotation_angle))
                spot_y = py + int(self.radius * 0.15)
                spot_radius = max(1, int((self.radius // 4) * depth))
                pygame.draw.circle(screen, (180, 70, 50), (spot_x, spot_y), spot_radius)

        # Earth's land patches
        if self.name == "Earth":
            for offset in (0, 2.5):
                angle = self.rotation_angle + offset
                depth = math.cos(angle)
                if depth > 0:
                    land_x = px + int(self.radius * 0.85 * math.sin(angle))
                    land_y = py - int(self.radius * 0.2) + int(offset * 4)
                    land_radius = max(1, int((self.radius // 3) * depth))
                    pygame.draw.circle(screen, (70, 160, 70), (land_x, land_y), land_radius)

            # Earth's moon
            moon_distance = self.radius + 12
            moon_x = px + moon_distance * math.cos(self.moon_angle)
            moon_y = py + moon_distance * math.sin(self.moon_angle)
            moon_label = font.render("Moon", True, WHITE)
            screen.blit(moon_label, (int(moon_x) + 5, int(moon_y) - 10))
            pygame.draw.circle(screen, (200, 200, 200), (int(moon_x), int(moon_y)), 3)

        # hover / selection rings (drawn on top of everything else about the planet)
        if self.hovered:
            pygame.draw.circle(screen, WHITE, (px, py), self.radius + 4, width=2)
        if self.selected:
            pygame.draw.circle(screen, (255, 215, 0), (px, py), self.radius + 7, width=3)

        # the label
        label = font.render(self.name, True, WHITE)
        screen.blit(label, (px + self.radius + 4, py - 8))


def build_planets():
    # NOTE: distances/sizes/speeds are chosen to look good on screen, not to match real astronomical scale.
    return [
        Planet("Mercury", (169, 169, 169), 80, 6, 0.04,
        "Smallest planet; a year here is just 88 Earth days." ),
        Planet("Venus", (230, 200, 140), 115, 9, 0.03,
        "Second planet from the Sun; hottest planet in our solar system." ),
        Planet("Earth", (80, 140, 230), 150, 10, 0.025,
        "Our home planet; the only known celestial body to harbor life." ),
        Planet("Mars", (210, 100, 60), 190, 8, 0.02,
        "The Red Planet; has the largest volcano in the solar system known as \"Olympus Mons\"." ),
        Planet("Jupiter", (220, 180, 130), 260, 22, 0.012,
        "Largest planet; has a giant red spot that is a storm." ),
        Planet("Saturn", (230, 210, 160), 320, 18, 0.009,
        "Known for its prominent rings; the largest planet with rings." ),
        Planet("Uranus", (150, 220, 220), 370, 14, 0.006,
        "The seventh planet from the Sun; rotates on its side." ),
        Planet("Neptune", (90, 110, 220), 410, 14, 0.004,   
        "The farthest planet from the Sun; has the strongest winds." ),
    ]

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        test_width, _ = font.size(test_line)
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line != "":
                lines.append(current_line)
            current_line = word

    if current_line != "":
        lines.append(current_line)

    return lines

def draw_info_panel(screen, font, title, stat_lines, fact_text):
    MAX_TEXT_WIDTH = 300
    fact_lines = wrap_text("Fun fact: " + fact_text, font, MAX_TEXT_WIDTH)

    all_lines = [title] + stat_lines + [""] + fact_lines

    widest_line = 0
    for line in all_lines:
        line_width, _ = font.size(line)
        widest_line = max(widest_line, line_width)
    panel_width = min(widest_line, MAX_TEXT_WIDTH) + 20

    line_height = 22
    panel_height = 20 + len(all_lines) * line_height

    panel_x = 20
    panel_y = 20

    pygame.draw.rect(screen, (30, 30, 30), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), width=1)

    for i, line in enumerate(all_lines):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (panel_x + 10, panel_y + 10 + i * line_height))


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
SUN_FACT = "The Sun contains about 99.8% of the mass in our solar system."

sun_hovered = False
sun_selected = False

planets = build_planets()

NUM_STARS = 150
stars = []
for i in range(NUM_STARS):
    star_x = random.randint(0, WIDTH)
    star_y = random.randint(0, HEIGHT)
    stars.append((star_x, star_y))

# --- Interactivity state ---
paused = False
speed_multiplier = 1.0
selected_planet = None
solar_flare = SolarFlareEvent(SUN_X, SUN_Y, SUN_RADIUS, WIDTH, HEIGHT)
max_speed_time = 0.0
MAX_SPEED_EVENT_DELAY = 10.0

# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                planets = build_planets()
                paused = False
                speed_multiplier = 1.0
                selected_planet = None
                sun_selected = False
                max_speed_time = 0.0
                solar_flare.reset()
            if event.key == pygame.K_RIGHT:
                if not solar_flare.active:
                    speed_multiplier = min(4.0, speed_multiplier + 0.25)
            if event.key == pygame.K_LEFT:
                if not solar_flare.active:
                    speed_multiplier = max(0.1, speed_multiplier - 0.25)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not solar_flare.active:
                sun_dist = math.hypot(event.pos[0] - SUN_X, event.pos[1] - SUN_Y)

                if sun_dist <= SUN_RADIUS + 4:
                    sun_selected = True
                    selected_planet = None
                else:
                    clicked_planet = None
                    closest_dist = None
                    for planet in planets:
                        dist = math.hypot(event.pos[0] - planet.x, event.pos[1] - planet.y)
                        if dist <= planet.radius + 4:
                            if closest_dist is None or dist < closest_dist:
                                closest_dist = dist
                                clicked_planet = planet
                    selected_planet = clicked_planet
                    sun_selected = False

    # Update.  The clock gives the 4x countdown real seconds, rather than
    # tying it to a particular frame rate.
    dt = clock.tick(FPS) / 1000.0
    if not paused and not solar_flare.active:
        for planet in planets:
            planet.update(SUN_X, SUN_Y, speed_multiplier)

        if speed_multiplier >= 4.0:
            max_speed_time += dt
            if max_speed_time >= MAX_SPEED_EVENT_DELAY:
                bodies = [(planet.x, planet.y, planet.radius, planet.color)
                          for planet in planets]
                solar_flare.trigger(bodies)
                selected_planet = None
                sun_selected = False
        else:
            # The ten seconds must be continuous at 4x speed.
            max_speed_time = 0.0

    if solar_flare.active:
        solar_flare.update(dt)

    if solar_flare.completed:
        # A new solar system appears after the event has burned itself out.
        planets = build_planets()
        speed_multiplier = 1.0
        max_speed_time = 0.0
        solar_flare.reset()

    # Hover / selection state (checked every frame, independent of pause)
    mouse_pos = pygame.mouse.get_pos()
    for planet in planets:
        dist = math.hypot(mouse_pos[0] - planet.x, mouse_pos[1] - planet.y)
        planet.hovered = dist <= planet.radius + 4
        planet.selected = (planet is selected_planet)

    sun_dist = math.hypot(mouse_pos[0] - SUN_X, mouse_pos[1] - SUN_Y)
    sun_hovered = sun_dist <= SUN_RADIUS + 4

    # Draw
    screen.fill(BLACK)

    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)

    if not solar_flare.hides_solar_system:
        pygame.draw.circle(screen, YELLOW, (SUN_X, SUN_Y), SUN_RADIUS)
        if sun_hovered:
            pygame.draw.circle(screen, WHITE, (SUN_X, SUN_Y), SUN_RADIUS + 4, width=2)
        if sun_selected:
            pygame.draw.circle(screen, (255, 215, 0), (SUN_X, SUN_Y), SUN_RADIUS + 7, width=3)

        for planet in planets:
            planet.draw(screen, SUN_X, SUN_Y, FONT)

    solar_flare.draw(screen)

    # Status text (top-right)
    status_text = f"{'PAUSED' if paused else 'RUNNING'}  |  Speed: {speed_multiplier:.2f}x"
    status_surface = FONT.render(status_text, True, WHITE)
    screen.blit(status_surface, (WIDTH - 260, 20))

    if solar_flare.active:
        event_label = FONT.render("SOLAR EVENT IN PROGRESS", True, (255, 205, 100))
        screen.blit(event_label, (WIDTH - 260, 45))

    # Controls hint (bottom-left)
    controls_text = "SPACE: Pause   R: Reset   Left/Right: Speed   Click: Select   ESC: Quit"
    controls_surface = FONT.render(controls_text, True, GRAY)
    screen.blit(controls_surface, (20, HEIGHT - 30))

    
        # Info panel for whatever is currently selected
    if not solar_flare.active and selected_planet is not None:
        p = selected_planet
        period_seconds = (2 * math.pi / p.speed) / FPS
        velocity = p.distance * p.speed * FPS
        relative_size = p.radius ** 3
        stat_lines = [
            f"Distance from Sun: {p.distance} px",
            f"Orbital period: {period_seconds:.1f} sec (sim time)",
            f"Orbital velocity: {velocity:.1f} px/sec",
            f"Radius: {p.radius} px",
            f"Relative size (radius^3): {relative_size}",
        ]
        draw_info_panel(screen, FONT, p.name, stat_lines, p.fun_fact)

    elif not solar_flare.active and sun_selected:
        stat_lines = [
            f"Radius: {SUN_RADIUS} px",
            "Role: center of the solar system",
        ]
        draw_info_panel(screen, FONT, "Sun", stat_lines, SUN_FACT)

    pygame.display.flip()
pygame.quit()
sys.exit()
