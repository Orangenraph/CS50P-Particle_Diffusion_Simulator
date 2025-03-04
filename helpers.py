import pygame
import numpy as np


def draw_heatmap(concentration_grid, x_axis, y_axis, screen):
    ''' Heat mapo of particle concentration '''
    cell_width = x_axis / concentration_grid.shape[0]
    cell_height = y_axis / concentration_grid.shape[1]

    max_concentration = np.max(concentration_grid) if np.max(concentration_grid) > 0 else 1 # to avoid 0 division

    for i in range(concentration_grid.shape[0]):
        for j in range(concentration_grid.shape[1]):
            if concentration_grid[i, j] > 0:
                # Normalize concentration and select color (blue to red)
                normalized = concentration_grid[i, j] / max_concentration
                color = (int(255 * normalized), 0, int(255 * (1 - normalized)))

                s = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
                s.fill((color[0], color[1], color[2], 50)) # Alpha for transparent
                screen.blit(s, (i * cell_width, j * cell_height))

def draw_stats(particles, simulation_time, viscosity,mass, temperatur, VISCOSITY_FACTOR, COLLISION_ENABLED, HEATMAP_ENABLED,MONTECARLO_ENABLED, screen, X_axe, pi_approxi, accuracy):
    """Shows all Stats in Simulation - left-right corner """
    font = pygame.font.SysFont('Times New Roman', 16)

    # Left corner
    info_lines = [
        f"Particles: {len(particles)}",
        f"Time: {round(simulation_time, 2)}s",
        f"Temperatur: {temperatur}°C",
        f"Mass: {mass}",
        f"Viscosity: {round((viscosity * VISCOSITY_FACTOR), 5) }",
        f"Pi Approximation: {round(pi_approxi, 7)}",
        f"Accuracy: {round(accuracy, 2)}%",
        f"",
        f"Collisions: {'ON' if COLLISION_ENABLED else 'OFF'}",
        f"Heatmap: {'ON' if HEATMAP_ENABLED else 'OFF'}",
        f"Monte Carlo Pi: {'ON' if MONTECARLO_ENABLED else 'OFF'}"
    ]
    y_info = 20
    for line in info_lines:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, y_info))
        y_info += 20

    # Right Corner
    button_lines = [
        f"Press R - Restart",
        f"Press S - Speed up Time",
        f"Press T - +5°C",
        f"Press M - +0.5 Mass",
        f"Press V - *0.05 Viscosity",
        f"",
        f"Press C - Collision On/Off",
        f"Heatmap H - Heatmap On/Off",
        f"Press P - Monte Carlo On/Off"
    ]
    y_button = 20
    for line in button_lines:
        text = font.render(line, True, (255, 255, 255))
        text_width, _ = font.size(line)
        screen.blit(text, (X_axe - text_width - 10, y_button))
        y_button += 20



CELL_SIZE = 4 * 2
grid = {}

def update_spatial_grid(particles):
    """Organizes particles in a spatial grid"""
    global grid
    grid = {}
    for p in particles:
        cell_x = int(p.x // CELL_SIZE)
        cell_y = int(p.y // CELL_SIZE)
        if (cell_x, cell_y) not in grid:
            grid[(cell_x, cell_y)] = []
        grid[(cell_x, cell_y)].append(p)

def get_nearby_cells(cell_x, cell_y):
    """Returns neighboring cells (including the current cell)"""
    return [
        (cell_x + dx, cell_y + dy)
        for dx in [-1, 0, 1]
        for dy in [-1, 0, 1]
    ]


def check_collisions_optimized(particle):
    """Checks collisions only with particles in neighboring cells"""
    cell_x = int(particle.x // CELL_SIZE)
    cell_y = int(particle.y // CELL_SIZE)
    collisions = False

    # checks neighbor cells
    for nearby_cell in get_nearby_cells(cell_x, cell_y):
        if nearby_cell in grid:
            for other in grid[nearby_cell]:
                if particle != other and particle.check_collision_with(other):
                    collisions = True
    return collisions

def draw_monte_carlo_pi(screen, MC_OFFSET_X, MC_OFFSET_Y, MC_QUADRAT_SIZE):
    '''Draws square and quarter of circle to calucalte monte carlo pi calculation'''

    #Draws square:
    pygame.draw.rect(screen, (255,255,255), (MC_OFFSET_X, MC_OFFSET_Y, MC_QUADRAT_SIZE, MC_QUADRAT_SIZE), 1)

    # Corrected rectangle for the quarter circle
    circle_rect = (MC_OFFSET_X - MC_QUADRAT_SIZE, MC_OFFSET_Y, 2 * MC_QUADRAT_SIZE, 2 * MC_QUADRAT_SIZE)
    pygame.draw.arc(screen, (255,255,255), circle_rect, 0, np.pi / 2, 1)

def check_monte_carlo_status(particle,MC_OFFSET_X, MC_OFFSET_Y, MC_QUADRAT_SIZE, mc_points_total, mc_points_inside):
    ''' Checks wheter a particle is in or outside the circle'''
    in_square = (MC_OFFSET_X <= particle.x <= MC_OFFSET_X + MC_QUADRAT_SIZE and MC_OFFSET_Y <= particle.y <= MC_OFFSET_Y + MC_QUADRAT_SIZE)

    # checks if its in square, should 100% be case
    if in_square:
        mc_points_total += 1

        # Calculate the normalized distance to the origin of the quarter circle
        norm_x = (particle.x - MC_OFFSET_X) / MC_QUADRAT_SIZE
        norm_y = (particle.y - (MC_OFFSET_Y + MC_QUADRAT_SIZE)) / MC_QUADRAT_SIZE

        # Check whether the point is in the quarter circle
        # mc_points_inside
        if norm_x ** 2 + norm_y ** 2 <= 1:
            mc_points_inside += 1
            particle.inside_circle = True
            particle.color = (255,255,255) # White
        else:
            particle.inside_circle = False
            particle.color = (255, 0, 0)  # Red
    return mc_points_total, mc_points_inside

def estimate_pi(mc_points_total, mc_points_inside):
    '''Calculates pi using Monte Carlo'''
    pi_approxi = 4 * mc_points_inside / mc_points_total
    accuracy = (1 - (abs(pi_approxi - np.pi) / 0.8584)) * 100
    return pi_approxi, accuracy
