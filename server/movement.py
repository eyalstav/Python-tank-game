from math import *
def move_forward(vel,x,y,a):
    if a < 0:
        positive_angle = 360 - abs(a)
    else:
        positive_angle = a

    x -= vel * sin(radians(positive_angle))
    y -= vel * cos(radians(positive_angle))

    return x,y

def move_back(vel,x,y,a):
    if a < 0:
        positive_angle = 360 - abs(a)
    else:
        positive_angle = a

    x += vel * sin(radians(positive_angle))
    y += vel * cos(radians(positive_angle))

    return x,y