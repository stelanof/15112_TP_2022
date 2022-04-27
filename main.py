from cmu_112_graphics import *
from opensimplex import OpenSimplex
from trianglepolygonising import *
from metaballClass import *
from marchingcubes import *
from heightmap import *
import numpy as np
import math

# Metaballs inspired by
# http://jamie-wong.com/2014/08/19/metaballs-and-marching-squares/

# Height Map idea inspired by Adi Kambhampaty
# https://www.youtube.com/watch?v=Au4fr04Hw3A&feature=youtu.be

# Marching cube algorithm
# https://people.eecs.berkeley.edu/~jrs/meshpapers/LorensenCline.pdf
# http://paulbourke.net/geometry/polygonise/
# https://youtu.be/M3iI2l0ltbE

# Perlin Noise help from
# https://en.wikipedia.org/wiki/Perlin_noise
# https://www.redblobgames.com/maps/terrain-from-noise/

###############################################################################
# Title Screen
###############################################################################
def title_timerFired(app):
    for metaball in app.balls:
        metaball.move()
        if metaball.x - metaball.r <= 0 or metaball.x + metaball.r >= app.width:
            metaball.changeX()
        if metaball.y - metaball.r <= 0 or metaball.y + metaball.r >= app.height:
            metaball.changeY()
    updateValues(app)

def title_mousePressed(app, event):
    if (9*app.width/16 <= event.x <= 13*app.width/16 and
        10*app.height/16 <= event.y <= 12*app.height/16):
        app.mode = 'sandboxSplash'
    if (3*app.width/16 <= event.x <= 7*app.width/16 and
        10*app.height/16 <= event.y <= 12*app.height/16):
        app.mode = 'aboutScreenOne'
    if (app.width - 75 <= event.x <= app.width - 25 and
        25 <= event.y <= 75):
        if app.colormode == 'light':
            app.colormode = 'dark'
            app.bgcolor = app.bgdark
            app.buttonfill = app.buttonfilldark
            app.buttonoutline = app.buttonoutlinedark
            app.buttonselected = app.buttonselecteddark
            app.textcolor = app.textdark
        else:
            app.colormode = 'light'
            app.bgcolor = app.bglight
            app.buttonfill = app.buttonfilllight
            app.buttonoutline = app.buttonoutlinelight
            app.buttonselected = app.buttonselectedlight
            app.textcolor = app.textlight

def title_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    drawLines(app, canvas)
    
    # Title
    canvas.create_text(app.width/2, app.height/3,
                    text = 'MARCHING CUBES 112', font = 'Courier 50 bold', fill= app.textcolor)
    canvas.create_text(app.width/2, app.height/3 + 50,
                       text = 'A TERRAIN VISUALIZATION TOOL', font = 'Courier 20 bold', fill = app.textcolor)
    
    # About
    canvas.create_rectangle(3*app.width/16, 10*app.height/16, 7*app.width/16, 12*app.height/16,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/16, 11*app.height/16,
                    text = 'ABOUT', font = 'Courier 24 bold', fill = app.textcolor)

    # Sandbox
    canvas.create_rectangle(9*app.width/16, 10*app.height/16, 13*app.width/16, 12*app.height/16,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(11*app.width/16, 11*app.height/16,
                    text = 'SANDBOX', font = 'Courier 24 bold', fill = app.textcolor)

    # Color Mode
    x0,y0 = app.width - 75, 25
    x1,y1 = app.width - 25, 75
    cx = (x0 + x1)/2
    cy = (y0 + y1)/2
    if app.colormode == 'light':
        canvas.create_image(cx, cy, image=ImageTk.PhotoImage(app.imagelight))
    elif app.colormode == 'dark':
        canvas.create_image(cx, cy, image=ImageTk.PhotoImage(app.imagedark))
        
###############################################################################
# Sandbox Splash Screen
###############################################################################
def sandboxSplash_timerFired(app):
    for metaball in app.balls:
        metaball.move()
        if metaball.x - metaball.r <= 0 or metaball.x + metaball.r >= app.width:
            metaball.changeX()
        if metaball.y - metaball.r <= 0 or metaball.y + metaball.r >= app.height:
            metaball.changeY()
    updateValues(app)

def sandboxSplash_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'title'

    # 2d
    if (3*app.width/16 <= event.x <= 7*app.width/16 and
        7*app.height/16 <= event.y <= 9*app.height/16):
        app.mode = 'heightMap'
        app.surface = 0.05
        app.resolution = app.width/2 / app.size
        app.state = []
        for i in range(app.sidelength):
            for j in range(app.sidelength):
                for k in range(app.sidelength):
                    if i == 0:
                        app.state.append(1)
                    else:
                        app.state.append(0)

    # 3d
    if (9*app.width/16 <= event.x <= 13*app.width/16 and
        7*app.height/16 <= event.y <= 9*app.height/16):
        app.mode = 'selectFunction'
        app.color1 = app.buttonfill
        app.color2 = app.buttonfill
        app.color3 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonselected
    
def sandboxSplash_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    drawLines(app, canvas)

    # 2d
    canvas.create_rectangle(3*app.width/16, 7*app.height/16, 7*app.width/16, 9*app.height/16,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/16, app.height/2,
                    text = '2D HEIGHT MAP', font = 'Courier 20 bold', fill = app.textcolor)

    # 3d
    canvas.create_rectangle(9*app.width/16, 7*app.height/16, 13*app.width/16, 9*app.height/16,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(11*app.width/16, app.height/2,
                    text = '3D VISUALIZE', font = 'Courier 20 bold', fill = app.textcolor)

    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

###############################################################################
# About Screen
###############################################################################
def aboutScreenOne_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'title'

    # Next
    if (7*app.width/8 <= event.x <= 31*app.width/32 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'aboutScreenTwo'

def aboutScreenOne_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)

    # Images
    if app.colormode == 'light':
        canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.aboutlight1))
    if app.colormode == 'dark':
        canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.aboutdark1))

    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

    # Next
    canvas.create_rectangle(7*app.width/8, 29*app.height/32, 31*app.width/32, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(59*app.width/64, 30*app.height/32,
                       text = 'Next', font = 'Courier 15 bold', fill = app.textcolor)

def aboutScreenTwo_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'aboutScreenOne'

    # Next
    if (7*app.width/8 <= event.x <= 31*app.width/32 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'title'

def aboutScreenTwo_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)

    # Images
    if app.colormode == 'light':
        canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.aboutlight2))
    if app.colormode == 'dark':
        canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.aboutdark2))

    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

    # Next
    canvas.create_rectangle(7*app.width/8, 29*app.height/32, 31*app.width/32, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(59*app.width/64, 30*app.height/32,
                       text = 'Title', font = 'Courier 15 bold', fill = app.textcolor)

###############################################################################
# Select 3d Function
###############################################################################
def selectFunction_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'sandboxSplash'
        app.functionstr = ''
    if (app.width/8 <= event.x <= 7*app.width/8 and
        80 <= event.y <= 130):
        app.color1 = app.buttonselected
        app.color2 = app.buttonfill
        app.color3 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonfill
        app.functionimplement = app.func1
    if (app.width/8 <= event.x <= 7*app.width/8 and
        155 <= event.y <= 205):
        app.color2 = app.buttonselected
        app.color1 = app.buttonfill
        app.color3 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonfill
        app.functionimplement = app.func2
    if (app.width/8 <= event.x <= 7*app.width/8 and
        230 <= event.y <= 280):
        app.color3 = app.buttonselected
        app.color1 = app.buttonfill
        app.color2 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonfill
        app.functionimplement = app.func3
    if (app.width/8 <= event.x <= 7*app.width/8 and
        305 <= event.y <= 355):
        app.color4 = app.buttonselected
        app.color1 = app.buttonfill
        app.color3 = app.buttonfill
        app.color2 = app.buttonfill
        app.color5 = app.buttonfill
        app.functionimplement = app.func4
    if (app.width/8 <= event.x <= 7*app.width/8 and
        455 <= event.y <= 505):
        app.color1 = app.buttonfill
        app.color2 = app.buttonfill
        app.color3 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonselected
        app.functionimplement = app.functionstr
    if (3*app.width/8 <= event.x <= 5*app.width/8 and
        14*app.height/16 <= event.y <= 31*app.height/32):
        try: updateSurface(app)
        except: return
        projectPoints(app)
        app.mode = 'visualizeMarching'

def selectFunction_keyPressed(app, event):
    variables = {'(', ')', '*', '+', '-', '/'}
    no = {'Backspace', 'Enter', 'Return', 'Escape', 'Tab', 'Up', 'Left', 'Right', 'Down'}
    if event.key == 'Backspace':
        app.functionstr = app.functionstr[:len(app.functionstr) - 1]
    if len(app.functionstr) >= 50 or event.key.isalpha() and event.key.isupper() or event.key in no:
        return
    elif event.key == 'Space':
        app.functionstr += ' '
    elif event.key.isalnum() or event.key in variables:
        app.functionstr += event.key
    app.color1 = app.buttonfill
    app.color2 = app.buttonfill
    app.color3 = app.buttonfill
    app.color4 = app.buttonfill
    app.color5 = app.buttonselected
    app.functionimplement = app.functionstr

def selectFunction_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

    # Preset Functions
    canvas.create_text(app.width/2, 50,
                       text = "Select a terrain function you'd like to visualize:",
                       font = 'Courier 24 bold', fill = app.textcolor)
    # 1
    canvas.create_rectangle(app.width/8, 80, 7*app.width/8, 130,
                            fill = app.color1, outline = app.buttonoutline)
    canvas.create_text(app.width/2, 105,
                       text = app.func1,
                       font = 'Courier 15 bold', fill = app.textcolor)
    # 2
    canvas.create_rectangle(app.width/8, 155, 7*app.width/8, 205,
                            fill = app.color2, outline = app.textcolor)
    canvas.create_text(app.width/2, 180,
                       text = app.func2,
                       font = 'Courier 15 bold', fill = app.textcolor)
    # 3
    canvas.create_rectangle(app.width/8, 230, 7*app.width/8, 280,
                            fill = app.color3, outline = app.textcolor)
    canvas.create_text(app.width/2, 255,
                       text = app.func3,
                       font = 'Courier 15 bold', fill = app.textcolor)
    # 4
    canvas.create_rectangle(app.width/8, 305, 7*app.width/8, 355,
                            fill = app.color4, outline = app.textcolor)
    canvas.create_text(app.width/2, 330,
                       text = app.func4,
                       font = 'Courier 15 bold', fill = app.textcolor)

    # Input Own Function
    canvas.create_text(app.width/2, 425,
                       text = "Or, type out your own function to visualize:",
                       font = 'Courier 24 bold', fill = app.textcolor)
    canvas.create_rectangle(app.width/8, 455, 7*app.width/8, 505,
                            fill = app.color5, outline = app.buttonoutline)
    canvas.create_text(app.width/8 + 10, 480,
                       text = f'f(x,y,z) = {app.functionstr}', anchor = 'w',
                       font = 'Courier 15 bold', fill = app.textcolor)
    
    # Visualize
    canvas.create_rectangle(3*app.width/8, 14*app.height/16, 5*app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(app.width/2, 59*app.height/64,
                       text = 'Visualize Mesh', font = 'Courier 20 bold', fill = app.textcolor)

###############################################################################
# 3d Marching Visualization
###############################################################################
def visualizeMarching_mouseDragged(app, event):
    for i in range(len(app.projectedPoints)):
        x,y = app.projectedPoints[i]
        z = app.points[i].tolist()[0][2]
        if distance(event.x, event.y, x, y) < app.scale/2:
            if not app.removing and app.state[i] < app.max and z >= 0:
                app.state[i] += app.change
            elif app.removing and app.state[i] > app.min and z >= 0:
                app.state[i] -= app.change

def visualizeMarching_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.functionimplement = app.functionstr
        app.color1 = app.buttonfill
        app.color2 = app.buttonfill
        app.color3 = app.buttonfill
        app.color4 = app.buttonfill
        app.color5 = app.buttonselected
        app.mode = 'selectFunction'

def visualizeMarching_keyPressed(app, event):
    if event.key == 'w' and app.surface < app.max:
        app.surface += app.change
    if event.key == 's' and app.surface > app.min:
        app.surface -= app.change
    if event.key == 'p':
        app.removing = not app.removing
    if event.key == 'r':
        count = 0
        for i in range(app.x):
            for j in range(app.y):
                for k in range(app.z):
                    app.points[count] = [i - app.x//2, app.y//2 - j, k - app.z//2]
                    count += 1
        app.points = app.points * app.rotateZ
    if event.key == 'Right':
        initializeY(app, -app.theta)
        app.points = app.points * app.rotateY
    if event.key == 'Left': # Good
        initializeY(app, app.theta)
        app.points = app.points * app.rotateY
    if event.key == 'Up':
        initializeX(app, -app.theta)
        app.points = app.points * app.rotateX
    if event.key == 'Down': # Good
        initializeX(app, app.theta)
        app.points = app.points * app.rotateX
    projectPoints(app)

def visualizeMarching_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

    drawTriangles(app,canvas)

    canvas.create_text(app.width/2, 25,
                       text = f'Surface level is {app.surface}', font = 'Courier 20 bold', fill = app.textcolor)
    if not app.removing:
        canvas.create_text(app.width/2, 60,
                        text = 'Increasing Points Value', font = 'Courier 15 bold', 
                        anchor = 's', fill = 'green')
    if app.removing:
        canvas.create_text(app.width/2, 60,
                        text = 'Decreasing Points Value', font = 'Courier 15 bold', 
                        anchor = 's', fill = '#FFA4A4')

    # Controls
    canvas.create_text(app.width/2, app.height - 15,
                       text = 'Drag and hold mouse to change state of points',
                       anchor = 's', font = 'Courier 20 bold', fill = app.textcolor)
    canvas.create_text(app.width/2, app.height - 45,
                       text = 'Use arrow keys to rotate terrain',
                       anchor = 's', font = 'Courier 20 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8 - 10, 45,
                       text = 'Commands',
                       font = 'Courier 20 bold', fill = app.textcolor)
    canvas.create_line(3*app.width/4 + 10, 60, app.width - 30, 60,
                       fill = app.textcolor, width = 2)
    canvas.create_text(7*app.width/8 - 10, 80,
                       text = 'W: Increase Surface Level',
                       font = 'Courier 12 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8 - 10, 100,
                       text = 'S: Decrease Surface Level',
                       font = 'Courier 12 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8 - 10, 120,
                       text = 'P: Toggle Adding/Removing',
                       font = 'Courier 12 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8 - 10, 140,
                       text = 'R: Reset Rotation',
                       font = 'Courier 12 bold', fill = app.textcolor)

###############################################################################
# Height Map
###############################################################################
def heightMap_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'sandboxSplash'
        app.resolution = 15
        resetMap(app)
    if (3*app.width/8 <= event.x <= 5*app.width/8 and
        14*app.height/16 <= event.y <= 31*app.height/32):
        app.mode = 'marching'
        updateState(app)
        projectPoints(app)
    x,y = app.mousepos
    if app.width/4 <= x <= 3*app.width/4 and 10 <= y <= app.width/2 + 10:
        updateColor(app, event.x, event.y)
        updateState(app)

def heightMap_mouseDragged(app, event):
    app.mousepos = (event.x, event.y)
    x,y = app.mousepos
    if app.width/4 <= x <= 3*app.width/4 and 10 <= y <= app.width/2 + 10:
        updateColor(app, event.x, event.y)
        updateState(app)

def heightMap_mouseMoved(app, event):
    app.mousepos = (event.x, event.y)

# With help from https://www.redblobgames.com/maps/terrain-from-noise/
perlin = OpenSimplex()
def noise(x, y):
    return perlin.noise2(x, y) * 0.5 + 1

def randomPerlin(app):
    posx = random.uniform(-100, 100)
    posy = random.uniform(-100, 100)
    a = random.uniform(0,1)
    b = random.uniform(0,1)
    c = random.uniform(0,1)
    for i in range(app.size):
        for j in range(app.size):
            x = (j + posx)/app.size - 0.5
            y = (i + posy)/app.size - 0.5
            height = a*noise(x, y) + b*noise(2*x + 10, 2*y + 3.4) + c*noise(4*x + 4.3, 4*y + 9.1)
            height = (height/(a + b + c))**3
            app.hmapzvalue[i][j] = height * 3 + 1

def heightMap_keyPressed(app, event):
    if event.key == 'w' and app.radius < app.maxradius:
        app.radius += 5
    if event.key == 's' and app.radius > app.minradius:
        app.radius -= 5
    if event.key == 'Space':
        app.increase = not app.increase
    if event.key == 'r':
        resetMap(app)
    if event.key == 'p':
        randomPerlin(app)

def heightMap_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)

    # Visualize
    canvas.create_rectangle(3*app.width/8, 14*app.height/16, 5*app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(app.width/2, 59*app.height/64,
                       text = 'Visualize Mesh', font = 'Courier 20 bold', fill = app.textcolor)

    # Height Map                   
    drawMap(app, canvas)
    canvas.create_rectangle(app.width/4, 10, 3*app.width/4, app.width/2 + 10,
                            fill = None, outline = app.buttonoutline)
    if app.increase:
        canvas.create_text(7*app.width/8, app.width/2,
                        text = 'Increasing Height', font = 'Courier 15 bold', 
                        anchor = 's', fill = 'green')
    if not app.increase:
        canvas.create_text(7*app.width/8, app.width/2,
                        text = 'Decreasing Height', font = 'Courier 15 bold', 
                        anchor = 's', fill = '#FFA4A4')

    # UI
    drawColors(app, canvas)
    canvas.create_text(7*app.width/8, 45,
                       text = 'Commands',
                       font = 'Courier 20 bold', fill = app.textcolor)
    canvas.create_line(3*app.width/4 + 20, 60, app.width - 20, 60,
                       fill = app.textcolor, width = 2)
    canvas.create_text(7*app.width/8, 80,
                       text = 'W: Increase Radius',
                       font = 'Courier 15 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8, 100,
                       text = 'S: Decrease Radius',
                       font = 'Courier 15 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8, 120,
                       text = 'Space: Toggle Remove',
                       font = 'Courier 15 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8, 140,
                       text = 'R: Reset Height Map',
                       font = 'Courier 15 bold', fill = app.textcolor)
    canvas.create_text(7*app.width/8, 160,
                       text = 'P: Create Random Map',
                       font = 'Courier 15 bold', fill = app.textcolor)
    drawCircle(app, canvas)

###############################################################################
# Visualize Height Map
###############################################################################
def marching_mousePressed(app, event):
    # Back
    if (app.width/32 <= event.x <= app.width/8 and
        29*app.height/32 <= event.y <= 31*app.height/32):
        app.mode = 'heightMap'

def marching_keyPressed(app, event):
    if event.key == 'Right':
        initializeY(app, -app.theta)
        app.points = app.points * app.rotateY
    if event.key == 'Left': # Good
        initializeY(app, app.theta)
        app.points = app.points * app.rotateY
    if event.key == 'Up':
        initializeX(app, -app.theta)
        app.points = app.points * app.rotateX
    if event.key == 'Down': # Good
        initializeX(app, app.theta)
        app.points = app.points * app.rotateX
    if event.key == 'r':
        count = 0
        for i in range(app.sidelength):
            for j in range(app.sidelength):
                for k in range(app.sidelength):
                    app.points[count] = [i - app.sidelength//2, app.sidelength//2 - j, k - app.sidelength//2]
                    count += 1
        app.points = app.points * app.rotateZ
    projectPoints(app)

def marching_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = app.bgcolor)
    # Back
    canvas.create_rectangle(app.width/32, 29*app.height/32, app.width/8, 31*app.height/32,
                            fill = app.buttonfill, outline = app.buttonoutline)
    canvas.create_text(5*app.width/64, 30*app.height/32,
                       text = 'Back', font = 'Courier 15 bold', fill = app.textcolor)
    drawTriangles(app, canvas)
    canvas.create_text(app.width/2, 15,
                       text = 'Use arrow keys to rotate terrain',
                       anchor = 'n', font = 'Courier 20 bold', fill = app.textcolor)
    canvas.create_text(app.width/2, 50,
                       text = 'Click R to reset view',
                       anchor = 'n', font = 'Courier 20 bold', fill = app.textcolor)

###############################################################################
# Shared Commands
###############################################################################
def appStarted(app):
    app.mode = 'title'
    ###########################################################################
    # Title
    app.resolution = 15
    app.rows = app.height // app.resolution + 1
    app.cols = app.width // app.resolution + 1
    app.dots = [ [0] * (app.cols) for i in range(app.rows)]
    app.polygonise = edgeList()
    app.balls = []
    for _ in range(8):
        temp = Ball()
        app.balls.append(temp)

    updateValues(app)

    # Light Mode / Dark Mode
    app.bglight = '#FFFED2'
    app.buttonfilllight = '#fff3d2'
    app.buttonoutlinelight = 'black'
    app.buttonselectedlight = '#ebffd2'
    app.textlight = 'black'

    app.bgdark = '#070712'
    app.buttonfilldark = 'black'
    app.buttonoutlinedark = 'white'
    app.buttonselecteddark = '#081207'
    app.textdark = 'white'

    app.bgcolor = app.bglight
    app.buttonfill = app.buttonfilllight
    app.buttonoutline = app.buttonoutlinelight
    app.buttonselected = app.buttonselectedlight
    app.textcolor = app.textlight
    app.colormode = 'light'

    ###########################################################################
    # 3d Visualization
    app.functionstr = ''
    app.func1 = '(x - 4)**2 + (y-4)**2 + (z - 4)**2'
    app.func2 = 'x + sin(y*z*pi/12)'
    app.func3 = 'sin((y-z)*pi/4)**2 + x'
    app.func4 = '(x - y)**3 + z'
    app.color1 = app.buttonfill
    app.color2 = app.buttonfill
    app.color3 = app.buttonfill
    app.color4 = app.buttonfill
    app.color5 = app.buttonselected
    app.functionimplement = app.functionstr
    
    # Initialize size
    app.x, app.y, app.z = 9,9,9 # Increasing = better resolution, runs slower
    app.totalpoints = app.x * app.y * app.z
    app.surface = 0.05
    # Initialize points
    app.on = [ [ [0] * app.z for y in range(app.y)] for x in range(app.x)]
    app.points = [ [0] for points in range(app.totalpoints)]
    app.state = []
    count = 0
    for i in range(app.x):
        for j in range(app.y):
            for k in range(app.z):
                app.state.append(app.on[i][j][k])
                app.points[count] = [i - app.x//2, app.y//2 - j, k - app.z//2]
                count += 1
    app.points = np.matrix(app.points)
    app.change = 0.5 # Change depending on what you want

    # Rotation
    app.scale = 50
    # Orthogonal projection matrices
    # Derived from https://en.wikipedia.org/wiki/Projection_(linear_algebra)
    app.project = np.matrix([[1,0,0],[0,1,0]])
    app.projectedPoints = [0] * app.totalpoints

    # Rotation Matrices
    app.theta = math.pi/30
    initializeX(app, app.theta)
    initializeY(app, app.theta)

    initializeZ(app, math.pi/2)
    app.points = app.points * app.rotateZ

    # Triangle polygonisation of marching cubes
    app.triangle = triangleList()

    app.removing = False
    ###########################################################################
    # 2d Height Map
    app.increase = True
    app.sidelength = app.x
    app.pixelsper = 9
    app.pixellength = int(app.pixelsper**0.5)
    app.size = app.sidelength * app.pixellength
    app.hmapzvalue = [ [1] * app.size for size in range(app.size) ]
    app.sideresolution = app.width/2 / app.sidelength
    app.maxzvalue = app.sidelength - 1
    app.minzvalue = 1
    app.minradius = 20
    app.maxradius = 80
    app.radius = 40
    app.mousepos = (0, 0)
    # Colors
    app.level1 = (0, 11, 64)
    app.level2 = (3, 28, 152)
    app.level3 = (101, 178, 255)
    app.level4 = (27, 213, 58)
    app.level5 = (8, 98, 23)
    app.level6 = (64, 64, 64)
    app.level7 = (162, 162, 162)
    app.level8 = (255, 255, 255)
    app.colors = [app.level1, app.level2, app.level3, app.level4, app.level5, app.level6, app.level7, app.level8]
    ###########################################################################
    # Images

    # Light Mode/Dark Mode
    # Image from https://icon-icons.com/icon/sun-day-weather-symbol/73146
    app.image1 = app.loadImage('lightmode.png')
    app.imagelight = app.scaleImage(app.image1, 1/10)
    # Image from https://icon-icons.com/icon/moon-dark-mode-night-mode/190939
    app.image2 = app.loadImage('darkmode.png')
    app.imagedark = app.scaleImage(app.image2, 1/12)

    # About Screen
    app.image3 = app.loadImage('aboutlight1.png')
    app.aboutlight1 = app.scaleImage(app.image3, 1/2)
    app.image4 = app.loadImage('aboutlight2.png')
    app.aboutlight2 = app.scaleImage(app.image4, 1/2)
    app.image5 = app.loadImage('aboutdark1.png')
    app.aboutdark1 = app.scaleImage(app.image5, 1/2)
    app.image6 = app.loadImage('aboutdark2.png')
    app.aboutdark2 = app.scaleImage(app.image6, 1/2)



runApp(width=1000,height=600)