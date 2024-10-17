from orbitronomy.orbitCalcs import SimpleOrbit
from collections import namedtuple
from scipy.constants import G, pi
from math import e
import tkinter as tk
from tkinter import messagebox

# Starship stats
# Isp in seconds = 350
# Wet mass in kg = 1300000
# Thrust in newtons = 12300


SOLAR_MASS = 1.9885 * 10 ** 30 # kg
STANDARD_GRAVITY = G * SOLAR_MASS

attributes = ['name', 'semiMajorAxis', 'perihelion', 'eccentricity', 'inclination', 'longitudeOfAscendingNode', 'argumentOfPerihelion', 'color']
Body = namedtuple('Body',attributes)

planets = {
    # SemiMajorAxis, Perihelion, Eccentricity, Inclination, LongitudeOfAscendingNode, ArgumentOfPerihelion
    'Earth': Body('earth', 1.000001018063, 0.983292404575649, 0.0167086, 1.57869, 348.73936, 114.20783, 'blue'),
    'Mars' : Body('mars', 1.523680550622, 1.381369928817, 0.0934, 1.63, 49.57854, 286.5, 'orange')
}

def hohmann_transfer(origin:Body, target:Body):
    origin_aphelion = origin.semiMajorAxis * (1 + origin.eccentricity)
    target_aphelion = target.semiMajorAxis * (1 + target.eccentricity)
    origin_radius = (origin.perihelion + origin_aphelion) / 2
    target_radius = (target.perihelion + target_aphelion) / 2
    target_radius = target_aphelion   
    transfer_aphelion = max(origin_radius, target_radius)
    transfer_perihelion = min(origin_radius, target_radius)

    return Body(
        'transfer',
        (origin_radius + target_radius) / 2,
        origin_radius,
        (transfer_aphelion - transfer_perihelion) / (transfer_aphelion + transfer_perihelion),
        0,
        0,
        0,
        'gray'
    )

def calculate_period(body):
    "returns periods in seconds"
    answer = body.semiMajorAxis * 149597870691
    answer **= 3
    answer /= STANDARD_GRAVITY
    answer **= 0.5
    answer *= 2 * pi
    return answer

def calculate_dv(origin:Body,target:Body):
    r1 = origin.semiMajorAxis * 149597870691 * (1 + origin.eccentricity)
    r2 = target.semiMajorAxis * 149597870691 * (1 + target.eccentricity)
    a = (STANDARD_GRAVITY / r1) ** 0.5
    b = ((2 * r2) / (r1 + r2)) ** 0.5 - 1
    return int(a * b)

# def calculate_burned_fuel_mass(dv, isp, mass):
#     answer = dv / (isp * STANDARD_GRAVITY)
#     answer = mass * e ** -answer
#     print(isp * STANDARD_GRAVITY)
#     return answer

def calculate(isp,mass,thrust,origin,target):
    origin = planets[origin.get()]
    target = planets[target.get()]
    info = f'origin: {origin.name}\n'
    info += f'taget: {target.name}\n'
    transfer_orbit = hohmann_transfer(origin, target)
    for i, j in [*zip(attributes, transfer_orbit)][1:-1]:
        info += f'{i}: {j}\n'
    dv = calculate_dv(origin,target)
    info += f'Δv: {dv} m/s\n'
    #info += f'fuel burned: {calculate_burned_fuel_mass(dv,isp,mass)} kg\n'
    

    messagebox.showinfo("Results",info)

def visualize_orbit(origin:Body, target:Body):
    orbit: SimpleOrbit = SimpleOrbit(plot_title="Hohmann Transfer",name="Hohmann Transfer")

    orbit.faceColor('black')
    orbit.paneColor('black')
    orbit.gridColor('#222831')
    orbit.orbitTransparency(0.5)
    orbit.labelColor('black')
    orbit.tickColor('black') 
    orbit.plotStyle(background_color="dark_background")

    orbit.calculateOrbit(plot_steps=1000, data=[origin, target, hohmann_transfer(origin,target)], n_orbits=1, trajectory=True)

    orbit.animateOrbit(dpi=250, font_size="xx-small")

def main():
    root = tk.Tk()
    root.title("Hohmann Transfer Calculator")

    frame = tk.Frame(root)
    frame.pack(padx=10,pady=10)

    labels = ["Isp (In sec)","Wet mass (In kg)","Thrust (In N)"]
    entries = []
    for i, text in enumerate(labels):
        label = tk.Label(frame, text=text)
        label.grid(row=i, column=0, sticky='e', padx=5, pady=5)

        entry = tk.Entry(frame)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    origin = tk.StringVar(root)
    target = tk.StringVar(root)
    origin.set('Earth')
    target.set('Mars')
    origin_menu = tk.OptionMenu(root, origin, *planets.keys())
    target_menu = tk.OptionMenu(root, target, *planets.keys())
    
    command = lambda:calculate(*[float(i.get()) for i in entries], origin, target)
    calc_button = tk.Button(frame, text='Calculate', command=command)
    calc_button.grid(row=len(labels) + 2, column=0, padx=5, pady=5)
    command = lambda:visualize_orbit(planets[origin.get()], planets[target.get()])
    visualize_button = tk.Button(frame, text='Visualize', command=command)
    visualize_button.grid(row=len(labels) + 2, column=1, padx=5, pady=5)

    root.mainloop()

main()