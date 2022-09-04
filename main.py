# Be sure to install pygame via pip
import time

import pygame
import sys
import math
import random
from pygame.math import Vector2
from ElasticCollision.ec_game import momentum_trigonometry
import tkinter
from tkinter import *
from tkinter import font
import threading


class Speed:
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value


class PauseStatus:
    def __init__(self):
        self.paused = False


pause = PauseStatus()
pause.paused = True
speed_factor = Speed(0.1)
window_height = 1000
window_width = 1000

# TODO:
# planet trace


# volumic mass of materials (kg/m3)
materials = {
    "water": 1000,
    "gravel": 2000,
    "clay": 1900,
    "asphalt": 721,
    "cement": 1440,
    "concrete": 2400,
    "steel": 7850,
    "aluminium": 2739,
    "magnesium": 1738,
    "cobalt": 8746,
    "nickel": 8908,
    "tin": 7280,
    "lead": 11340,
    "zinc": 7208,
    "iron": 7850,
    "glass": 2580,
    "real blackhole (messes around)": 4 * 10 ** 17,
    "fake blackhole": 4 * 10 ** 7
}

materials_colors = {
    "water": (0, 255, 255),
    "gravel": (192, 192, 192),
    "clay": (255, 160, 122),
    "asphalt": (128, 128, 128),
    "cement": (143, 188, 143),
    "concrete": (47, 79, 79),
    "steel": (173, 216, 230),
    "aluminium": (176, 196, 222),
    "magnesium": (119, 136, 153),
    "cobalt": (65, 105, 225),
    "nickel": (95, 158, 160),
    "tin": (72, 61, 139),
    "lead": (119, 136, 153),
    "zinc": (46, 139, 87),
    "iron": (255, 69, 0),
    "glass": (224, 255, 255),
    "real blackhole (messes around)": (10, 10, 10),
    "fake blackhole": (10, 10, 10)
}

planets = []


class Planet:
    def __init__(self, x, y, r, material, name, vx=0, vy=0):
        self.x = float(x)
        self.y = float(y)
        self.r = float(r)  # in meters
        self.material = material
        self.mass = int(((4 / 3) * math.pi * (r ** 3)) * materials[material])
        self.name = name
        self.vx = vx
        self.vy = vy
        print(
            "Planet {} is {} m^3 and {} kg at x = {} and y = {}".format(self.name, int(((4 / 3) * math.pi * (r ** 3))),
                                                                        self.mass, self.x, self.y))


def gravity(m1, m2, d):
    G = 6.67 * (10 ** -11)
    if d == 0:
        return 0

    return G * ((m1 * m2) / (max(d, 1) ** 2))


def updatevector(planets_list, deltatime):
    for selected_planet in planets_list:
        reference_planets = planets_list.copy()
        reference_planets.remove(selected_planet)

        fx = 0
        fy = 0

        for reference_planet in reference_planets:
            norm = gravity(selected_planet.mass, reference_planet.mass, math.sqrt(
                (reference_planet.x - selected_planet.x) ** 2 + (reference_planet.y - selected_planet.y) ** 2))

            dir_x = reference_planet.x - selected_planet.x
            dir_y = reference_planet.y - selected_planet.y

            try:
                angle = math.atan(abs(dir_y) / abs(dir_x))

                if dir_x < 0 and dir_y < 0:
                    angle += math.pi
                elif dir_y < 0:
                    angle += 1.5 * math.pi
                elif dir_x < 0:
                    angle += math.pi / 2
                else:
                    angle += 0
            except ZeroDivisionError:
                angle = 1.5 * math.pi

            fx += norm * math.cos(angle)
            fy += norm * math.sin(angle)
        # a = F / m
        ax = fx / selected_planet.mass
        ay = fy / selected_planet.mass

        # deltav = deltat * a
        dvx = ax * deltatime
        dvy = ay * deltatime

        selected_planet.vx += dvx
        selected_planet.vy += dvy

        # initial_vector.combine()


def move_planets(planets_list, deltatime, scale_factor):
    collisions_list = []

    for i, selected_planet in enumerate(planets_list):
        # if touches edge
        if selected_planet.x > window_width:
            selected_planet.vx = abs(selected_planet.vx) * -0.7
        elif selected_planet.x < 0:
            selected_planet.vx = abs(selected_planet.vx) * 0.7

        if selected_planet.y > window_width:
            selected_planet.vy = abs(selected_planet.vy) * -0.7
        elif selected_planet.y < 0:
            selected_planet.vy = abs(selected_planet.vy) * 0.7

        # create a collisions list
        for j, reference_planet in enumerate(planets_list):
            if j != i:  # not same planet
                actual_d = math.sqrt(
                    (reference_planet.x - selected_planet.x) ** 2 + (reference_planet.y - selected_planet.y) ** 2)
                min_d = (reference_planet.r + selected_planet.r) * scale_factor
                potential_collision = min(i, j), max(i, j)
                if actual_d <= min_d and potential_collision not in collisions_list:
                    collisions_list.append(potential_collision)

    for collision in collisions_list:
        p1 = planets_list[collision[0]]
        p2 = planets_list[collision[1]]
        v1 = Vector2(p1.vx, p1.vy)
        v2 = Vector2(p2.vx, p2.vy)
        centre_1 = Vector2(p1.x, p1.y)
        centre_2 = Vector2(p2.x, p2.y)
        m1 = p1.mass
        m2 = p2.mass
        v1new, v2new = momentum_trigonometry(centre_1, centre_2, v1, v2, m1, m2)

        force_loose_factor = 1
        p1.vx, p1.vy = v1new.x * force_loose_factor, v1new.y * force_loose_factor
        p2.vx, p2.vy = v2new.x * force_loose_factor, v2new.y * force_loose_factor

    for selected_planet in planets_list:
        selected_planet.x += selected_planet.vx * deltatime * scale_factor
        selected_planet.y += selected_planet.vy * deltatime * scale_factor


def update_fps(clock, how="indirect"):
    if how == "direct":
        fps = str(round(clock.get_fps(), 3)) + " fps"
        return fps
    elif how == "indirect":
        fps = str(int(clock.get_fps())) + " fps"
    else:
        fps = "ERROR"
    fps_text = littlefont.render(fps, True, pygame.Color("coral"))
    return fps_text


def addplanet(x, y, ray, vx, vy, name, material, window_ref):
    if x == 0 or not x.isdigit():
        x = random.randrange(0, window_width)
    if y == 0 or not y.isdigit():
        y = random.randrange(0, window_height)
    if ray == 0 or not ray.isdigit():
        ray = random.randrange(150000, 1500000)
    if vx == 0 or not vx.isdigit():
        vx = 0
    if vy == 0 or not vy.isdigit():
        vy = 0
    if material.get() == "none":
        material_random = list(materials.keys())
        material_random.remove("real blackhole (messes around)")
        material_random.remove("fake blackhole")
        material.set(random.choice(list(material_random)))

    planets.append(Planet(int(x), int(y), int(ray), material.get(), name, vx=int(vx), vy=int(vy)))

    window_ref.destroy()


def live_control_pad():
    lcp = tkinter.Tk()
    big_font = tkinter.font.Font(family='Helvetica', size=20, weight='bold')
    lcp.title("Live Control Pad")
    lcp.geometry('500x500')
    lcp.configure(background="Black")

    lcp.columnconfigure(tuple(range(2)), weight=1)
    lcp.rowconfigure(tuple(range(30)), weight=1)

    Label(lcp, text="Welcome Live Control Pad !", bg="black", fg="white", font=big_font, anchor="center").grid(row=0,
                                                                                                               columnspan=3,
                                                                                                               sticky="we")

    speed_stringvar = StringVar()
    speed_stringvar.set("Speed : " + str(speed_factor.value))
    paused_strvar = StringVar()
    paused_strvar.set("Paused" if pause.paused else "Playing")

    Button(lcp, text=" - ", anchor="center", command=lambda: change_speed(speed_stringvar, -0.1)).grid(row=1, column=0,
                                                                                                       sticky="w")
    Button(lcp, text=" + ", anchor="center", command=lambda: change_speed(speed_stringvar, 0.1)).grid(row=1, column=2,
                                                                                                      sticky="e")
    Label(lcp, textvariable=speed_stringvar, bg="black", fg="white", anchor="center").grid(row=1, column=1, sticky="w")

    Button(lcp, text=" PAUSE ", anchor="center", command=lambda: setpause(True, paused_strvar)).grid(row=2, column=0,
                                                                                                     sticky="w")
    Button(lcp, text=" PLAY ", anchor="center", command=lambda: setpause(False, paused_strvar)).grid(row=2, column=2,
                                                                                                     sticky="e")
    Label(lcp, textvariable=paused_strvar, bg="black", fg="white", anchor="center").grid(row=2, column=1, sticky="w")

    Button(lcp, text="Apply", anchor="center", command=lambda: apply_lcp(speed_stringvar.get()[7:])).grid(row=3,
                                                                                                          column=0,
                                                                                                          columnspan=3,
                                                                                                          sticky="news")

    lcp.mainloop()


def setpause(paused, strvar):
    pause.paused = paused
    strvar.set("Paused" if pause.paused else "Playing")


def change_speed(strvar, to_add):
    if float(strvar.get()[7:]) <= 0.1 and (abs(to_add) / to_add) == -1 or (float(strvar.get()[7:]) < 0.1) and (
            abs(to_add) / to_add) == 1:
        to_add = 0.01 * (abs(to_add) / to_add)
    newSpeed = float(strvar.get()[7:]) + to_add
    if 0 < newSpeed <= 10:  # max = 10
        strvar.set("Speed : " + str(round(float(newSpeed), 2)))


def apply_lcp(new_speed):
    if 0 < float(new_speed) < 10:
        speed_factor.set(float(new_speed))


def thread1():
    # initialize it
    pygame.init()

    # configurations
    frames_per_second = 30

    # creating window
    screen = pygame.display.set_mode((window_width, window_height))

    # creating our frame regulator
    clock = pygame.time.Clock()

    # 1 metter = px
    scale = 0.00005

    letters = {x: pygame.key.key_code(x) for x in "abcdefghijklmnopqrstuvwxyz"}

    started = False
    planet_creating = False

    global littlefont
    littlefont = pygame.font.SysFont("Arial", 18)
    global bigfont
    bigfont = pygame.font.SysFont("Arial", 50)

    planet_got_added = False
    while True:
        if not planet_got_added and not pause.paused:
            # frame clock ticking

            deltaTime = clock.tick(frames_per_second) / 1000.0 * speed_factor.value

            screen.fill((0, 0, 0))

            screen.blit(update_fps(clock), (10, 0))

            updatevector(planets, deltaTime)
            move_planets(planets, deltaTime, scale)

            for planet in planets:
                pygame.draw.circle(screen, materials_colors[planet.material], (planet.x, planet.y), planet.r * scale)
                pygame.draw.line(screen, (255, 0, 0), (planet.x, planet.y), (planet.vx, planet.vy))
                img = littlefont.render(planet.name, True,
                                        pygame.Color((255, 255, 255)),
                                        )
                screen.blit(img, (planet.x - img.get_width() / 2, planet.y - img.get_height() / 2))

            pygame.display.flip()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    if not planet_creating:
                        planet_got_added = True
                        pos = pygame.mouse.get_pos()
                        window = tkinter.Tk()
                        window.title("Add new planet")
                        window.geometry('325x250')
                        window.configure(background="Black")
                        window.columnconfigure(0, weight=1)
                        window.columnconfigure(1, weight=3)

                        Label(window, text="Welcome to planet edition center !", bg="black", fg="white").grid(row=0,
                                                                                                              columnspan=3)

                        Label(window, text="x coordinate", bg="black", fg="white").grid(row=1, column=0, sticky="w")
                        Label(window, text="y coordinate", bg="black", fg="white").grid(row=2, column=0, sticky="w")
                        Label(window, text="Ray (influences weight)", bg="black", fg="white").grid(row=3, column=0,
                                                                                                   sticky="w")
                        Label(window, text="vx (0 = no movement)", bg="black", fg="white").grid(row=4, column=0,
                                                                                                sticky="w")
                        Label(window, text="vy (0 = no movement)", bg="black", fg="white").grid(row=5, column=0,
                                                                                                sticky="w")
                        Label(window, text="Name", bg="black", fg="white").grid(row=6, column=0, sticky="w")
                        Label(window, text="Material (list)", bg="black", fg="white").grid(row=7, column=0, sticky="w")

                        a1 = Entry(window)
                        a1.grid(row=1, column=1)
                        a1.insert(0, str(pos[0]))

                        b1 = Entry(window)
                        b1.grid(row=2, column=1)
                        b1.insert(0, str(pos[1]))

                        c1 = Entry(window)
                        c1.grid(row=3, column=1)
                        d1 = Entry(window)
                        d1.grid(row=4, column=1)
                        e1 = Entry(window)
                        e1.grid(row=5, column=1)
                        f1 = Entry(window)
                        f1.grid(row=6, column=1)

                        material_choice = StringVar(window)
                        material_choice.set("none")
                        OptionMenu(window, material_choice, *materials.keys()).grid(row=7, column=1)
                        Button(window, text="Create planet !",
                               command=lambda:
                               addplanet(a1.get(), b1.get(), c1.get(), d1.get(), e1.get(), f1.get(), material_choice,
                                         window)) \
                            .grid(row=8, column=0, columnspan=2)

                        window.mainloop()

        else:
            planet_got_added = False
            deltaTime = clock.tick(frames_per_second) / 1000.0 * speed_factor.value

            screen.fill((0, 0, 0))
            screen.blit(update_fps(clock), (10, 0))

            for planet in planets:
                pygame.draw.circle(screen, materials_colors[planet.material], (planet.x, planet.y), planet.r * scale)
                pygame.draw.line(screen, (255, 0, 0), (planet.x, planet.y), (planet.vx, planet.vy))
                img = littlefont.render(planet.name, True,
                                        pygame.Color((255, 255, 255)),
                                        )
                screen.blit(img, (planet.x - img.get_width() / 2, planet.y - img.get_height() / 2))

            pygame.display.flip()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    if not planet_creating:
                        planet_got_added = True
                        pos = pygame.mouse.get_pos()
                        window = tkinter.Tk()
                        window.title("Add new planet")
                        window.geometry('325x250')
                        window.configure(background="Black")
                        window.columnconfigure(0, weight=1)
                        window.columnconfigure(1, weight=3)

                        Label(window, text="Welcome to planet edition center !", bg="black", fg="white").grid(row=0,
                                                                                                              columnspan=3)

                        Label(window, text="x coordinate", bg="black", fg="white").grid(row=1, column=0, sticky="w")
                        Label(window, text="y coordinate", bg="black", fg="white").grid(row=2, column=0, sticky="w")
                        Label(window, text="Ray (influences weight)", bg="black", fg="white").grid(row=3, column=0,
                                                                                                   sticky="w")
                        Label(window, text="vx (0 = no movement)", bg="black", fg="white").grid(row=4, column=0,
                                                                                                sticky="w")
                        Label(window, text="vy (0 = no movement)", bg="black", fg="white").grid(row=5, column=0,
                                                                                                sticky="w")
                        Label(window, text="Name", bg="black", fg="white").grid(row=6, column=0, sticky="w")
                        Label(window, text="Material (list)", bg="black", fg="white").grid(row=7, column=0, sticky="w")

                        a1 = Entry(window)
                        a1.grid(row=1, column=1)
                        a1.insert(0, str(pos[0]))

                        b1 = Entry(window)
                        b1.grid(row=2, column=1)
                        b1.insert(0, str(pos[1]))

                        c1 = Entry(window)
                        c1.grid(row=3, column=1)
                        d1 = Entry(window)
                        d1.grid(row=4, column=1)
                        e1 = Entry(window)
                        e1.grid(row=5, column=1)
                        f1 = Entry(window)
                        f1.grid(row=6, column=1)

                        material_choice = StringVar(window)
                        material_choice.set("none")
                        OptionMenu(window, material_choice, *materials.keys()).grid(row=7, column=1)
                        Button(window, text="Create planet !",
                               command=lambda:
                               addplanet(a1.get(), b1.get(), c1.get(), d1.get(), e1.get(), f1.get(), material_choice,
                                         window)) \
                            .grid(row=8, column=0, columnspan=2)

                        window.mainloop()


t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=live_control_pad)

t1.start()
t2.start()
