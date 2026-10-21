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
        self.phase = None
        self.timer = 0

        self.grow_duration = 90      # frames (~1.5 sec at 60 FPS)
        self.explode_duration = 90
        self.fade_duration = 90

        self.particles = []

        # A reusable transparent surface for fading/glowing effects
        self.overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    def trigger(self):
        if not self.active:
            self.active = True
            self.phase = "growing"
            self.timer = 0
            self.particles = []

    def reset(self):
        self.active = False
        self.phase = None
        self.timer = 0
        self.particles = []

    def update(self):
        if not self.active:
            return

        self.timer += 1

        if self.phase == "growing":
            if self.timer >= self.grow_duration:
                self.phase = "exploding"
                self.timer = 0
                self._spawn_particles()

        elif self.phase == "exploding":
            for p in self.particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["alpha"] = max(0, p["alpha"] - (255 / self.explode_duration))

            if self.timer >= self.explode_duration:
                self.phase = "fading"
                self.timer = 0

        elif self.phase == "fading":
            if self.timer >= self.fade_duration:
                self.reset()

    def _spawn_particles(self):
        self.particles = []
        for i in range(80):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 9)
            self.particles.append({
                "x": self.sun_x,
                "y": self.sun_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.randint(2, 4),
                "alpha": 255
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
            radius = int(self.base_radius + t * self.base_radius * 2.5)
            color = self._lerp_color((255, 220, 60), (255, 255, 255), t)
            pygame.draw.circle(self.overlay, color, (self.sun_x, self.sun_y), radius)

        elif self.phase == "exploding":
            t = self.timer / self.explode_duration

            # shrinking bright core (the Sun "collapsing")
            core_radius = max(0, int(self.base_radius * 3.5 * (1 - t)))
            if core_radius > 0:
                pygame.draw.circle(self.overlay, (255, 255, 255), (self.sun_x, self.sun_y), core_radius)

            # expanding shockwave ring
            shockwave_radius = int(t * max(self.screen_width, self.screen_height) * 0.6)
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

        elif self.phase == "fading":
            t = self.timer / self.fade_duration

            # white flash, fading out over the whole screen
            flash_alpha = max(0, int(200 * (1 - t)))
            self.overlay.fill((255, 255, 255, flash_alpha))

            # Sun gradually returns to its normal size and color, on top of the flash
            radius = int(self.base_radius * 3.5 * (1 - t) + self.base_radius * t)
            color = self._lerp_color((255, 255, 255), (255, 220, 60), t)
            pygame.draw.circle(self.overlay, color, (self.sun_x, self.sun_y), radius)

        screen.blit(self.overlay, (0, 0))