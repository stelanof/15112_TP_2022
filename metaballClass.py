import random

# File contains a class and commands for metaball animation seen in the title screens

class Ball:
    def __init__(self):
        self.x = random.randint(200,800)
        self.y = random.randint(150,450)
        self.r = random.randint(20,50)
        self.dx = random.randint(-5,5)
        self.dy = random.randint(-5,5)
        while self.dx == 0:
            self.dx = random.randint(-5,5)
        while self.dy == 0:
            self.dy = random.randint(-5,5)

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def changeX(self):
        self.dx *= -1
    
    def changeY(self):
        self.dy *= -1

def distanceValue(x0, y0, x1, y1, r):
    dist = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
    return r/dist

def updateValues(app):
    for i in range(len(app.dots)):
        for j in range(len(app.dots[0])):
            x,y = j * app.resolution, i * app.resolution
            sum = 0
            for ball in app.balls:
                if x == ball.x and y == ball.y:
                    sum += 1
                else:
                    sum += distanceValue(x, y, ball.x, ball.y, ball.r)
            app.dots[i][j] = sum

def lerp(s0, s1, p0, p1):
    if s1 - s0 != 0:
        t = (1 - s0) / (s1 - s0)
        return p0 + t * (p1 - p0)
    else:
        return (p0 + p1)/2

def binary(L):
    sum = 0
    for i in range(len(L)):
        if L[i] >= 1:
            sum += 2**(3 - i)
    return sum

def drawLines(app , canvas):
    w = 3
    r = app.resolution
    for i in range(len(app.dots) - 1):
        for j in range(len(app.dots[0]) - 1):
            x0,y0 = j * app.resolution, i * app.resolution
            x1,y1 = (j + 1) * app.resolution, i * app.resolution
            x2,y2 = (j + 1) * app.resolution, (i + 1) * app.resolution
            x3,y3 = j * app.resolution, (i + 1) * app.resolution            

            s0 = app.dots[i][j]
            s1 = app.dots[i][j + 1]
            s2 = app.dots[i + 1][j + 1]
            s3 = app.dots[i + 1][j]

            p0 = (lerp(s0, s1, x0, x1), y0)
            p1 = (x1, lerp(s1, s2, y1, y2))
            p2 = (lerp(s2, s3, x2, x3), y2)
            p3 = (x0, lerp(s3, s0, y3, y0))

            edges = [0, p0, p1, p2, p3]
            num = binary([s0,s1,s2,s3])
            for k in range(0, 15, 2):
                if app.polygonise[num][k] == -1:
                    break
                x0,y0 = edges[app.polygonise[num][k]]
                x1,y1 = edges[app.polygonise[num][k + 1]]
                canvas.create_line(x0, y0, x1, y1, fill = '#FF9090', width = w)