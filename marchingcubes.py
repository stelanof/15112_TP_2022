from cmu_112_graphics import *
from trianglepolygonising import *
import numpy as np
import math
from math import *

# File contains functions necessary for 3d projection and the marching cubes algorithm

# Rotation Matrices
def initializeX(app, theta):
    app.rotateX = np.matrix([[1,0,0],
                            [0, math.cos(theta), -math.sin(theta)],
                            [0, math.sin(theta), math.cos(theta)]])
def initializeY(app, theta):
    app.rotateY = np.matrix([[math.cos(theta),0,math.sin(theta)],
                            [0, 1, 0],
                            [-math.sin(theta), 0, math.cos(theta)]])
def initializeZ(app, theta):
    app.rotateZ = np.matrix([[math.cos(theta), -math.sin(theta), 0],
                            [math.sin(theta), math.cos(theta), 0],
                            [0,0,1]])

# Orthogonal Projection https://en.wikipedia.org/wiki/Projection_(linear_algebra)#Orthogonal_projection
def projectPoints(app):
    for i in range(app.totalpoints):
        m = np.transpose(app.points[i])
        rot = app.project * m
        v = rot.tolist()
        x,y = v[0][0], v[1][0]
        x = app.scale * x + app.width/2
        y = app.scale * y + app.height/2
        app.projectedPoints[i] = (x,y)

def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**.5

def binaryToDec(app, L):
    sum = 0
    for i in range(len(L)):
        if L[i] < app.surface:
            sum += (2**i)
    return sum

# Linear interpolation formula
def vertexlerp(app, p0, p1, s0, s1):
    if s1 - s0 != 0:
        t = (app.surface - s0) / (s1 - s0)
        return p0 + t * (p1 - p0)
    else:
        return (p0 + p1)/2

def getEdges(app, corners, state):
    edges = []
    for j in range(4):
        i = j
        i1 = (j + 1) % 4
        i2 = i + 4
        i3 = i1 + 4
        x0 = vertexlerp(app, corners[i][0], corners[i1][0], state[i], state[i1])
        y0 = vertexlerp(app, corners[i][1], corners[i1][1], state[i], state[i1])
        x1 = vertexlerp(app, corners[i2][0], corners[i3][0], state[i2], state[i3])
        y1 = vertexlerp(app, corners[i2][1], corners[i3][1], state[i2], state[i3])
        x2 = vertexlerp(app, corners[i][0], corners[i2][0], state[i], state[i2])
        y2 = vertexlerp(app, corners[i][1], corners[i2][1], state[i], state[i2])
        edges.append((x0,y0))
        edges.append((x1,y1))
        edges.append((x2,y2))
    return edges

def getCoords(zvalues):
    coords = []
    for j in range(4):
        i = j
        i1 = (j + 1) % 4
        i2 = i + 4
        i3 = i1 + 4
        z0 = (zvalues[i] + zvalues[i1]) / 2
        coords.append(z0)
        z1 = (zvalues[i2] + zvalues[i3]) / 2
        coords.append(z1)
        z2 = (zvalues[i] + zvalues[i2]) / 2
        coords.append(z2)
    return coords

# Marching cube algorithm
# https://people.eecs.berkeley.edu/~jrs/meshpapers/LorensenCline.pdf
# http://paulbourke.net/geometry/polygonise/
def drawTriangles(app, canvas):
    paintersTriangles = []
    for x in range(app.x - 1):
        for y in range(app.y - 1):
            for z in range(app.z - 1):
                corners, state, zvalues = getPoints(app, x, y, z)
                edges = getEdges(app, corners, state)
                coords = getCoords(zvalues)
                trianglenum = binaryToDec(app, state)
                points = app.triangle[trianglenum]
                color = f'#{255:02x}{115:02x}{115:02x}'
                color2 = 'gray'
                for i in range(0, len(points), 3):
                    if points[i] == -1:
                        break
                    j = points[i]
                    j1 = points[i + 1]
                    j2 = points[i + 2]
                    j = ((j % 4) * 3) + j//4
                    j1 = ((j1 % 4) * 3) + j1//4
                    j2 = ((j2 % 4) * 3) + j2//4
                    x0,y0 = edges[j]
                    x1,y1 = edges[j1]
                    x2,y2 = edges[j2]
                    z0 = coords[j]
                    z1 = coords[j1]
                    z2 = coords[j2]
                    z = (z0 + z1 + z2) / 3
                    paintersTriangles.append((z,((x0,y0),(x1,y1),(x2,y2))))
    # Painter's alogrithm
    # https://en.wikipedia.org/wiki/Painter%27s_algorithm
    paintersTriangles.sort()
    for (z,((x0,y0),(x1,y1),(x2,y2))) in paintersTriangles:
        c = z * 3/2 / app.z + 1
        r = 255
        g = int(c * 100)
        b = int(c * 100)
        if g > 255:
            g = 255
        if g < 0:
            g = 0
        if b > 255:
            b = 255
        if b < 0:
            b = 0
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_polygon(x0, y0, x1, y1, x2, y2,
                            fill = color, outline = color)
    

def getPoints(app, i, j, k):
    # Get 8 vertexes of each cube
    p0 = i * (app.x**2) + j * app.y + k
    p1 = p0 + 1
    p2 = p0 + app.y + 1
    p3 = p0 + app.y
    p4 = p0 + (app.y * app.z)
    p5 = p4 + 1
    p6 = p4 + app.y + 1
    p7 = p4 + app.y
    corners =  [app.projectedPoints[p0],
                app.projectedPoints[p1],
                app.projectedPoints[p2],
                app.projectedPoints[p3],
                app.projectedPoints[p4],
                app.projectedPoints[p5],
                app.projectedPoints[p6],
                app.projectedPoints[p7]]
    state = [app.state[p0],
            app.state[p1],
            app.state[p2],
            app.state[p3],
            app.state[p4],
            app.state[p5],
            app.state[p6],
            app.state[p7]]
    zvalues =[app.points[p0].tolist()[0][2],
            app.points[p1].tolist()[0][2],
            app.points[p2].tolist()[0][2],
            app.points[p3].tolist()[0][2],
            app.points[p4].tolist()[0][2],
            app.points[p5].tolist()[0][2],
            app.points[p6].tolist()[0][2],
            app.points[p7].tolist()[0][2]]
    return corners, state, zvalues

def updateSurface(app):
    w = app.functionimplement
    count = 0
    for i in range(app.x):
        for j in range(app.y):
            for k in range(app.z):
                tempfunc = w.replace('x', str(i)).replace('y', str(j)).replace('z', str(k))
                app.on[i][j][k] = eval(tempfunc)
                app.state[count] = app.on[i][j][k]
                app.points[count] = [i - app.x//2, app.y//2 - j, k - app.z//2]
                count += 1
    app.points = np.matrix(app.points)
    app.max = max(app.state)
    app.min = min(app.state)
    app.surface = (app.max + app.min) / 2
    app.change = 0.5
    app.points = app.points * app.rotateZ