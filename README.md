# Particle Diffusion Simulator

## Overview
This is a sophisticated particle diffusion simulation built using Pygame and NumPy, demonstrating particle behavior under Langevin dynamics with interactive features and visualization techniques.

## Features
- Realistic particle movement using Langevin dynamics
- Temperature-dependent viscosity simulation
- Particle concentration heatmap
- Monte Carlo Pi estimation
- Interactive simulation controls

## Prerequisites
- Python 3.8+
- Pygame
- NumPy
  
## Simulation Controls
- `R`: Restart simulation
- `S`: Speed up time
- `T`: Increase temperature (+5°C)
- `M`: Increase particle mass (+0.5)
- `V`: Reduce viscosity
- `C`: Toggle particle collisions
- `H`: Toggle heatmap
- `P`: Toggle Monte Carlo Pi estimation

## Physics Highlights
- Implements Langevin dynamics for particle movement
- Calculates water viscosity based on temperature
- Uses thermal noise and damping in particle dynamics
- Applies Stokes' law for damping coefficient calculation

## Visualization
- Real-time particle tracking
- Concentration heatmap
- Monte Carlo Pi estimation visualization
- Particle trajectory rendering

## Performance Optimization
- Spatial grid-based collision detection
- Efficient Monte Carlo point tracking

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Author
Raphael Zährer, Connect with me on [LinkedIn](https://www.linkedin.com/in/raphael-z%C3%A4hrer-57b7682b3/)
