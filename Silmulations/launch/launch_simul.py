"""Simulation of a vertical rocket launch with temporal integration."""

import math


# Rocket and atmosphere parameters (SI units).
DRY_MASS = 500.0
FUEL_MASS = 1200.0
THRUST = 35_000.0
FLOW_RATE = 8.0
DRAG_COEFFICIENT = 0.5
FRONTAL_AREA = 1.0

SURFACE_GRAVITY = 9.80665
EARTH_RADIUS = 6_371_000.0
SEA_DENSITY = 1.225
SCALE_HEIGHT = 8500.0

TIME_STEP = 0.1
MAX_TIME = 1200.0


def simulate():
    """Return samples (time, altitude, velocity, fuel)."""
    time = 0.0
    altitude = 0.0
    velocity = 0.0
    fuel = FUEL_MASS
    samples = [(time, altitude, velocity, fuel)]

    while time < MAX_TIME:
        dt = min(TIME_STEP, MAX_TIME - time)
        if fuel > 0.0:
            dt = min(dt, fuel / FLOW_RATE)
            fuel_next = max(0.0, fuel - FLOW_RATE * dt)
            thrust = THRUST
        else:
            fuel_next = 0.0
            thrust = 0.0

        mass = DRY_MASS + (fuel + fuel_next) / 2.0
        gravity = SURFACE_GRAVITY * (
            EARTH_RADIUS / (EARTH_RADIUS + altitude)
        ) ** 2
        density = SEA_DENSITY * math.exp(-max(altitude, 0.0) / SCALE_HEIGHT)
        drag = (
            0.5
            * density
            * DRAG_COEFFICIENT
            * FRONTAL_AREA
            * velocity
            * abs(velocity)
        )
        acceleration = (thrust - drag) / mass - gravity

        altitude_next = altitude + velocity * dt + 0.5 * acceleration * dt**2
        velocity_next = velocity + acceleration * dt
        time += dt
        fuel = fuel_next

        # The ground acts as a limit during ascent and landing.
        if altitude_next <= 0.0:
            altitude_next = 0.0
            if velocity_next < 0.0:
                velocity_next = 0.0

        altitude, velocity = altitude_next, velocity_next
        samples.append((time, altitude, velocity, fuel))

        if time > 1.0 and fuel == 0.0 and altitude == 0.0 and velocity == 0.0:
            break

    return samples


def main():
    samples = simulate()
    apogee = max(samples, key=lambda sample: sample[1])
    burnout = FUEL_MASS / FLOW_RATE

    print("Vertical launch simulation")
    print(f"Burn time: {burnout:.1f} s")
    print(f"Maximum altitude: {apogee[1] / 1000:.2f} km")
    print(f"Time to apogee: {apogee[0]:.1f} s")
    print(f"Total simulated time: {samples[-1][0]:.1f} s")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("To view the graphs, install matplotlib: pip install matplotlib")
        return

    times = [sample[0] for sample in samples]
    altitudes = [sample[1] / 1000 for sample in samples]
    velocities = [sample[2] for sample in samples]

    figure, (altitude_axis, velocity_axis) = plt.subplots(2, 1, sharex=True)
    altitude_axis.plot(times, altitudes)
    altitude_axis.set_ylabel("Altitude (km)")
    altitude_axis.grid(True)
    velocity_axis.plot(times, velocities, color="tab:orange")
    velocity_axis.set_ylabel("Velocity (m/s)")
    velocity_axis.set_xlabel("Time (s)")
    velocity_axis.grid(True)
    figure.suptitle("Rocket launch simulation")
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
