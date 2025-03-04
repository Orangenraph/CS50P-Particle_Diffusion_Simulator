import numpy as np

class PhysicsEngine:
    def __init__(self):
        pass

    @staticmethod
    def calculate_water_viscosity(T):
        ''' Calculates water viscosity from Temperatur in Pa * s'''
        T_kelvin = T + 273.15
        A = 2.414e-5  # mPa·s
        B = 247.8  # K (Temperatur constant)
        C = 140  # K (Temperatur constant)
        viscosity = A * 10 ** (B / (T_kelvin - C))
        return viscosity * 10**3 # Convert mPa·s to Pa·s

    @staticmethod
    def calculate_concentration_grid(particles, grid_width, grid_height, x_max, y_max):
        '''Calculates the particle concentration distribution over a 2D grid '''
        cell_width = x_max / grid_width
        cell_height = y_max / grid_height

        grid = np.zeros((grid_width, grid_height))

        for particle in particles:
            # Ensure the particle position is within the valid range
            if 0 <= particle.x < x_max and 0 <= particle.y < y_max:
                grid_x = min(int(particle.x / cell_width), grid_width - 1)
                grid_y = min(int(particle.y / cell_height), grid_height - 1)
                grid[grid_x, grid_y] += 1

        return grid

    @staticmethod
    def apply_langevin_dynamics(particle, viscosity, temperature, dt):
        ''' Applies Langevin dynamics to update the particle's position and velocity '''
        T_kelvin = temperature + 273.15 # Convert temperature to Kelvin
        kB = 1.38064852e-23  # Boltzmann constant
        gamma = 6 * np.pi * viscosity * particle.radius * 0.1 # Calculate damping coefficient using Stokes' law
        scaling_factor = 1e12 # Scaling factor for the simulation to ensure reasonable motion

        # Calculate thermal noise term
        noise_amplitude = np.sqrt(2 * gamma * kB * T_kelvin / particle.mass * dt) * scaling_factor

        # Random force in x and y directions
        random_force_x = noise_amplitude * np.random.normal(0, 1)
        random_force_y = noise_amplitude * np.random.normal(0, 1)

        # Deterministic force
        deterministic_force_x = -gamma * particle.vx
        deterministic_force_y = -gamma * particle.vy

        # Update velocity using Langevin dynamics
        particle.vx += (deterministic_force_x / particle.mass + random_force_x / particle.mass) * dt
        particle.vy += (deterministic_force_y / particle.mass + random_force_y / particle.mass) * dt

        # Update position
        particle.x += particle.vx * dt
        particle.y += particle.vy * dt