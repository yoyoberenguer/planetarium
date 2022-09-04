# Planetarium
> A full python simulation of gravitational interaction between planets of different mass and size, colliding in an elastic way.

Hi ! Here is an initially little project that became kinda bigger due to the time it took in order to resolve all the problems (especially with threading and collisions).

![image](https://user-images.githubusercontent.com/72820204/188311953-ee312954-b415-4add-8e9d-1ec2c086a01e.png)


It's fully in python, easily editable and easily usable.

## Installation
* First download main.py
* Then install these requirements after having pyhton 3.10 installed (it should work with numerous previous versions but I haven't tested them yet)
```py
pip install pygame
pip install ElasticCollision
```
* The project also uses sys, math, random, tkinter and threading : pre-installed libs

## Usage
When you launch the program, the simulation is automatically on pause : here are some example steps to make a simple simulation :
* Click anywhere on the simulatin screen (big black square)
* A new window should appear : there you can choose setting for the planet to add : x, y, ray, material, initial velocity...
* Then click on "Create planet" and a new planet will appear (any field let blank will complete automatically with random value)
* After adding a few planets you can click on play on the Live Control Pad and the simulation should start
* You are also able to change the time speed with "+" and "-" button at the top of the LCP
* Click apply after all changes on LCP except for "play" and "pause"

## Functionning
At each frame, each planet's speed vector is edited according to all gravitational interactions with all other planets using newton laws. Every time a collision happens, elastic collision rules are applied (no energy is lost). The program is multi-threaded : thread-1 is for the simultation and thread-2 is for the LCP (otherwise tkinter (that hanles LCP) stops pygame (that handles the simulation))

## Demo
> Here is a little demo of the program on my computer

https://user-images.githubusercontent.com/72820204/188311897-6b51b95d-b95d-4d1d-b9d6-a4aaf4af0c97.mp4

