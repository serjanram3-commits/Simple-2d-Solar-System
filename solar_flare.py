import pygame
import math
import random


class SolarFlareEvent:
    def __init__(self, sun_x, sun_y, sun_radius, screen_width, screen_height):
        self.sun_x = sun_x
        self.sun_y = sun_y
        self.base_radius = sun_radius
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.active = False
        self.completed = False
        self.phase = None
        self.timer = 0.0

        # Seconds, so the sequence keeps its intended pace on slower PCs.
        self.grow_duration = 2.0
        self.explode_duration = 2.8
        self.fade_duration = 2.2
        self.blackout_duration = 0.8

        self.particles = []
        self.debris = []

        # A reusable transparent surface for fading/glowing effects
        self.overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    @property
    def hides_solar_system(self):
        return self.active and self.phase in ("exploding", "fading", "blackout")

    def trigger(self, bodies):
        if not self.active:
            self.active = True
            self.completed = False
            self.phase = "growing"
            self.timer = 0.0
            self.particles = []
            self.debris = []
            self.bodies = bodies

    def reset(self):
        self.active = False
        self.completed = False
        self.phase = None
        self.timer = 0.0
        self.particles = []
        self.debris = []

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt

        if self.phase == "growing":
            if self.timer >= self.grow_duration:
                self.phase = "exploding"
                self.timer = 0.0
                self._spawn_particles()

        elif self.phase == "exploding":
            for p in self.particles:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["alpha"] = max(0, p["alpha"] - (255 / self.explode_duration) * dt)
            for piece in self.debris:
                piece["x"] += piece["vx"] * dt
                piece["y"] += piece["vy"] * dt
                piece["alpha"] = max(0, piece["alpha"] - 75 * dt)

            if self.timer >= self.explode_duration:
                self.phase = "fading"
                self.timer = 0.0

        elif self.phase == "fading":
            if self.timer >= self.fade_duration:
                self.phase = "blackout"
                self.timer = 0.0

        elif self.phase == "blackout":
            if self.timer >= self.blackout_duration:
                self.active = False
                self.phase = "complete"
                self.completed = True

    def _spawn_particles(self):
        self.particles = []
        for i in range(320):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(180, 720)
            self.particles.append({
                "x": self.sun_x,
                "y": self.sun_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.randint(2, 8),
                "alpha": 255
            })

        # Each planet becomes a spray of coloured fragments thrown outwards
        # from the Sun, making the destruction affect the entire system.
        for x, y, radius, color in self.bodies:
            direction = math.atan2(y - self.sun_y, x - self.sun_x)
            for _ in range(max(10, radius * 2)):
                angle = direction + random.uniform(-0.75, 0.75)
                speed = random.uniform(180, 620)
                self.debris.append({
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.randint(2, max(3, radius // 2)),
                    "color": color,
                    "alpha": 255,
                })

    def _lerp_color(self, color_a, color_b, t):
        t = max(0, min(1, t))
        r = int(color_a[0] + (color_b[0] - color_a[0]) * t)
        g = int(color_a[1] + (color_b[1] - color_a[1]) * t)
        b = int(color_a[2] + (color_b[2] - color_a[2]) * t)
        return (r, g, b)

    def draw(self, screen):
        if not self.active:
            return

        self.overlay.fill((0, 0, 0, 0))  # clear to fully transparent

        if self.phase == "growing":
            t = self.timer / self.grow_duration
            radius = int(self.base_radius + t * self.base_radius * 3.5)
            color = self._lerp_color((255, 220, 60), (255, 255, 255), t)
            pygame.draw.circle(self.overlay, color, (self.sun_x, self.sun_y), radius)
            # A restless corona makes the Sun look unstable before it ruptures.
            for i in range(36):
                angle = i * (2 * math.pi / 36) + self.timer * 5
                ray_start = radius * 0.75
                ray_end = radius + random.randint(18, 60) * t
                start = (self.sun_x + int(math.cos(angle) * ray_start),
                         self.sun_y + int(math.sin(angle) * ray_start))
                end = (self.sun_x + int(math.cos(angle) * ray_end),
                       self.sun_y + int(math.sin(angle) * ray_end))
                pygame.draw.line(self.overlay, (255, 170, 45, 190), start, end, width=2)

        elif self.phase == "exploding":
            t = self.timer / self.explode_duration

            # shrinking bright core (the Sun "collapsing")
            core_radius = max(0, int(self.base_radius * 6 * (1 - t)))
            if core_radius > 0:
                pygame.draw.circle(self.overlay, (255, 255, 255), (self.sun_x, self.sun_y), core_radius)

            # expanding shockwave ring
            shockwave_radius = int(t * max(self.screen_width, self.screen_height) * 0.9)
            shockwave_alpha = max(0, int(255 * (1 - t)))
            pygame.draw.circle(
                self.overlay,
                (255, 240, 200, shockwave_alpha),
                (self.sun_x, self.sun_y),
                shockwave_radius,
                width=6
            )

            # particles flying outward
            for p in self.particles:
                color = (255, 200, 100, int(p["alpha"]))
                pygame.draw.circle(self.overlay, color, (int(p["x"]), int(p["y"])), p["size"])

            for piece in self.debris:
                color = (*piece["color"], int(piece["alpha"]))
                pygame.draw.circle(self.overlay, color, (int(piece["x"]), int(piece["y"])), piece["size"])

            # The opening moment is an overwhelming stellar flash.
            flash_alpha = max(0, int(230 * (1 - t * 7)))
            if flash_alpha:
                self.overlay.fill((255, 245, 210, flash_alpha))

        elif self.phase == "fading":
            t = self.timer / self.fade_duration

            # The universe burns out into darkness before the fresh scene resets.
            darkness = min(255, int(255 * t))
            self.overlay.fill((0, 0, 0, darkness))

        elif self.phase == "blackout":
            self.overlay.fill((0, 0, 0, 255))

        screen.blit(self.overlay, (0, 0))
