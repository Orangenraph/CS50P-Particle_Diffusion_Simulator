import pygame
import sys
import numpy as np

from physics_engine import PhysicsEngine
from helpers import draw_heatmap, draw_stats, check_collisions_optimized, update_spatial_grid, draw_monte_carlo_pi, \
    check_monte_carlo_status, estimate_pi

'''Pygames Settings'''
pygame.init()
screen_width, screen_height  = 900, 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Particle Diffusion Simulation")
clock = pygame.time.Clock()
FPS = 120
physics = PhysicsEngine()

''' Colors '''
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

'''Particle Settings'''
num_particles = 1000
RADIUS = 2
PARTICLE_COLOR = WHITE

TRACKING_PARTICLES = 3
TRACKED_COLOR = (236,83,83)
TRAJECTORY_COLOR = (128,0,0)

''' Simulation Settings'''
TEMPERATURE = 25 # Celsius
DT = 0.1  #delta Time
MASS = 1
VISCOSITY_FACTOR = 1.0  # for scaling die VISCOSITY

COLLISION_ENABLED = False
HEATMAP_ENABLED = True
MONTECARLO_ENABLED = True

'''Coordinate system'''
X_AXIS = screen_width
Y_AXIS = screen_height
grid_size = 20

'''Monte Carlo Settings'''
mc_points_inside = 0
mc_points_total = 0
MC_QUADRAT_SIZE = screen_width
MC_OFFSET_X = 0 # X-Position square
MC_OFFSET_Y = 0 # Y-Position square


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = RADIUS
        self.color = WHITE

        # Langevin specifc
        self.vx = 0
        self.vy = 0
        self.mass = MASS
        self.trajectory = []
        self.tracked = False # Flag
        self.position = (x, y)


    def move_langevin_dynamics(self):
        ''' apply langevin dynamics to move particles '''
        viscosity = physics.calculate_water_viscosity(TEMPERATURE) * VISCOSITY_FACTOR
        physics.apply_langevin_dynamics(self, viscosity, TEMPERATURE, DT)

        # tracking particles
        if self.tracked:
            self.trajectory.append((self.x, self.y))
            if len(self.trajectory) > 500:
                self.trajectory.pop(0)

        self.handle_collision()

    def handle_collision(self):
        '''checks if particles touches border'''
        if self.x - self.radius < 0:  # left
            self.x = 0 + self.radius
            self.vx = -self.vx * 0.8  # Reflection with energy loss
        if self.x + self.radius > 0 + X_AXIS:  # right
            self.x = 0 + X_AXIS - self.radius
            self.vx = -self.vx * 0.8
        if self.y + self.radius > 0 + Y_AXIS:  # bottom
            self.y = 0 + Y_AXIS - self.radius
            self.vy = -self.vy * 0.8
        if self.y - self.radius < 0:  # top
            self.y = 0 + self.radius
            self.vy = -self.vy * 0.8

    def check_collision_with(self, other_particle):
        """Checks for collisions between particles and reacts to them"""
        # calculates distance between particles
        dx = self.x - other_particle.x
        dy = self.y - other_particle.y
        distance = np.sqrt(dx** 2 + dy** 2)

        # if collision
        if distance < self.radius + other_particle.radius:
            # calc. normal vector for collision
            if distance > 0:
                nx = dx / distance
                ny = dy / distance
            else:
                # provide zero division
                nx, ny = 1, 0

            # relative v in normal vector
            vx_rel = self.vx - other_particle.vx
            vy_rel = self.vy - other_particle.vy
            v_rel_dot_n = vx_rel * nx + vy_rel * ny

            # only react if particle move to each other
            if v_rel_dot_n < 0:
                # elasticity
                e = 0.9

                # Pulse change
                j = -(1 + e) * v_rel_dot_n / (1 / self.mass + 1 / other_particle.mass)

                self.vx += j * nx / self.mass
                self.vy += j * ny / self.mass
                other_particle.vx -= j * nx / other_particle.mass
                other_particle.vy -= j * ny / other_particle.mass

                # Move particles slightly apart to avoid overlapping
                overlap = (self.radius + other_particle.radius - distance) / 2
                self.x += overlap * nx
                self.y += overlap * ny
                other_particle.x -= overlap * nx
                other_particle.y -= overlap * ny
                return True

        return False

    def draw(self):
        ''' Draws all particles in the simulation, purely optical function '''
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        if self.tracked and len(self.trajectory) > 1:
            pygame.draw.lines(screen, TRAJECTORY_COLOR, False, [(int(x), int(y)) for x, y in self.trajectory], 1)

def main():
    run_simulation(num_particles)

def run_simulation(n , online=True, simulation_time=0):
    '''Centerpiece, contains everything to run the simulation'''
    global TEMPERATURE, MASS, VISCOSITY_FACTOR, num_particles, COLLISION_ENABLED,HEATMAP_ENABLED, MONTECARLO_ENABLED, mc_points_total, mc_points_inside, DT

    # lists particles
    particles = [Particle((X_AXIS / 2), (Y_AXIS / 2)) for _ in range(n)]

    # picks random particle to follow
    for i in range(min(TRACKING_PARTICLES, n)):
        particles[i].tracked = True
        particles[i].color = TRACKED_COLOR

    # loops as long as online is True
    while online:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                online = False

            # Pressing a button
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    TEMPERATURE += 5
                elif event.key == pygame.K_s:
                    DT *= 1.1
                elif event.key == pygame.K_m:
                    MASS += 0.5
                    for p in particles:
                        p.mass = MASS
                elif event.key == pygame.K_v:
                    VISCOSITY_FACTOR *= 0.05
                elif event.key == pygame.K_c:
                    if COLLISION_ENABLED:
                        COLLISION_ENABLED = False
                    else:
                        COLLISION_ENABLED = True
                elif event.key == pygame.K_h:
                    if HEATMAP_ENABLED:
                        HEATMAP_ENABLED = False
                    else:
                        HEATMAP_ENABLED = True
                elif event.key == pygame.K_p:
                    if MONTECARLO_ENABLED:
                        MONTECARLO_ENABLED = False
                    else:
                        MONTECARLO_ENABLED = True
                elif event.key == pygame.K_r:
                    main()
                    return


        # updates & draws particles
        simulation_time += DT
        screen.fill(BLACK) # Background

        # check heatmap flag
        if HEATMAP_ENABLED:
            concentration_grid = physics.calculate_concentration_grid(particles, grid_size, grid_size, X_AXIS, Y_AXIS)
            draw_heatmap(concentration_grid, X_AXIS, Y_AXIS, screen)

        # check monte carlo vis. flag
        if MONTECARLO_ENABLED:
            draw_monte_carlo_pi(screen, MC_OFFSET_X, MC_OFFSET_Y, MC_QUADRAT_SIZE)

        # Border
        pygame.draw.rect(screen, RED, (0, 0, X_AXIS, Y_AXIS), 2)

        update_spatial_grid(particles)

        for particle in particles:
            particle.move_langevin_dynamics()
            # check collision flag
            if COLLISION_ENABLED:
                check_collisions_optimized(particle)
            # check montecarlo flag
            if MONTECARLO_ENABLED:
                mc_points_total, mc_points_inside = check_monte_carlo_status(particle,MC_OFFSET_X, MC_OFFSET_Y, MC_QUADRAT_SIZE, mc_points_total, mc_points_inside)
                pi_approxi, accuracy = estimate_pi(mc_points_total, mc_points_inside)
            particle.draw()

        # visualize
        draw_stats(particles,simulation_time,physics.calculate_water_viscosity(TEMPERATURE),MASS, TEMPERATURE,VISCOSITY_FACTOR, COLLISION_ENABLED, HEATMAP_ENABLED,MONTECARLO_ENABLED, screen, X_AXIS, pi_approxi, accuracy)
        pygame.display.flip()  # .flip -> updates full screen / .update -> updates part of screen
        clock.tick(FPS)

    # Exit
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()