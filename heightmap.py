from cmu_112_graphics import *
from trianglepolygonising import *
from marchingcubes import *
import numpy as np
import math, decimal

# File contains functions to edit the height map

# Height Map idea inspired by Adi Kambhampaty
# https://www.youtube.com/watch?v=Au4fr04Hw3A&feature=youtu.be

def updateState(app):
    values = []
    for i in range(app.sidelength):
        for j in range(app.sidelength):
            value = 0
            for r in range(app.pixellength):
                for c in range(app.pixellength):
                    v1 = app.pixellength * i + r
                    v2 = app.pixellength * j + c
                    value += app.hmapzvalue[v1][v2]
            value /= app.pixelsper
            values.append(value)
    for i in range(len(values)):
        v = values[i]
        count = 0
        while v >= 1:
            v -= 1
            app.state[i + count * app.sidelength**2] = 1
            count += 1
        app.state[i + count * app.sidelength**2] = v

def updateColor(app, x, y):
    for i in range(app.size):
        for j in range(app.size):
            x0 = j * app.resolution + app.width/4
            y0 = i * app.resolution + 10
            x1 = (j + 1) * app.resolution + app.width/4
            y1 = (i + 1) * app.resolution + 10
            if distance(x0, y0, x, y) <= app.radius or distance(x1, y1, x, y) <= app.radius:
                if app.increase and app.hmapzvalue[i][j] < app.maxzvalue:
                    app.hmapzvalue[i][j] += 0.1
                if not app.increase and app.hmapzvalue[i][j] > app.minzvalue:
                    app.hmapzvalue[i][j] -= 0.1

def drawMap(app, canvas):
    for i in range(app.size):
        for j in range(app.size):
            x0 = j * app.resolution + app.width/4
            y0 = i * app.resolution + 10
            x1 = (j + 1) * app.resolution + app.width/4
            y1 = (i + 1) * app.resolution + 10
            value = app.hmapzvalue[i][j]
            state = int(value)
            if state == 0:
                state = 1
            midpoint = int((value % state) * 10)
            if value < app.maxzvalue:
                rgb = colorBlender(app.colors[state - 1], app.colors[state], 10, midpoint)
            else:
                rgb = app.colors[-1]
            color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            canvas.create_rectangle(x0, y0, x1, y1,
                                    fill = color, outline = color)
            
# From 15-112 hw1, http://www.cs.cmu.edu/~112/notes/hw1.html
def colorBlender(rgb1, rgb2, midpoints, n):
    if (n < 0):
        return None
    elif ((n-midpoints) > 1):
        return None
    else:
        r1 = rgb1[0]
        r2 = rgb2[0]
        rd = r1-r2
        rm = rd/(midpoints+1)
        rx = r1 - (rm*n)
        rf = roundHalfUp(rx)
        g1 = rgb1[1]
        g2 = rgb2[1]
        gd = g1-g2
        gm = gd/(midpoints+1)
        gx = g1 - (gm*n)
        gf = roundHalfUp(gx)
        b1 = rgb1[2]
        b2 = rgb2[2]
        bd = b1-b2
        bm = bd/(midpoints+1)
        bx = b1 - (bm*n)
        bf = roundHalfUp(bx)
        return (rf,gf,bf)

# From CMU 15-112, http://www.cs.cmu.edu/~112/index.html
def roundHalfUp(d): #helper-fn
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def resetMap(app):
    app.hmapzvalue = [ [1] * app.size for _ in range(app.size) ]
    app.state = []
    for i in range(app.sidelength):
        for j in range(app.sidelength):
            for k in range(app.sidelength):
                if i == 0:
                    app.state.append(1)
                else:
                    app.state.append(0)

def drawCircle(app, canvas):
    x,y = app.mousepos
    if app.width/4 <= x <= 3*app.width/4 and 10 <= y <= app.width/2 + 10:
        canvas.create_oval(x - app.radius, y - app.radius,
                           x + app.radius, y + app.radius,
                           fill = None, outline = app.buttonoutline, width = 2)

def drawColors(app, canvas):
    value = 1
    count = 0
    while value <= app.maxzvalue:
        state = int(value)
        midpoint = int((value % state) * 10)
        if value < app.maxzvalue:
            rgb = colorBlender(app.colors[state - 1], app.colors[state], 10, midpoint)
        else:
            rgb = app.colors[-1]
        color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        canvas.create_rectangle(app.width/4 - 15, app.width/16 + 365 - 5*count, app.width/4 - 10, app.width/16 + 370 - 5*count,
                                fill = color, outline = color)
        value += 0.1
        count += 1
    canvas.create_text(app.width/4 - 25, app.width/16 + 10,
                       text = '8', font = 'Arial 8', fill = app.textcolor, anchor = 'n')
    canvas.create_text(app.width/4 - 25, app.width/16 + 10 + 70*5,
                       text = '1', font = 'Arial 8', fill = app.textcolor)