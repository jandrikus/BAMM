import math
pi=math.pi
p=pi/180
tan30 = math.tan(30*p)
sin30 = math.sin(30*p)
cos30 = math.cos(30*p)
sin120 = math.sin(120*p)
cos120 = math.cos(120*p)

e=12
f=22.357
re=32.2
rf=10

def directa(theta1, theta2, theta3):
    """
    angulos positivos hacia arriba, negativos hacia abajo
    """
    """
    x1=(0)+(0)
    y1=(-f*tan30/2)+(-rf*math.cos(theta1*p))+(e*tan30/2)
    z1=(0)+(-rf*math.sin(theta1*p))

    x2=(f*sin30/2)+(cos30*rf*math.cos(theta2*p)+sin30*rf*math.sin(theta2*p))-(e*tan30*cos30/2)
    y2=(f*sin30*tan30/2)+(0)
    z2=(0)+(sin30*rf*math.cos(theta2*p)-cos30*rf*math.sin(theta2*p))-(e*tan30*sin30/2)

    x3=(-f*sin30/2)+(-cos30*rf*math.cos(theta3*p)-sin30*rf*math.sin(theta3*p))+(e*tan30*cos30/2)
    y3=(f*sin30*tan30/2)+(0)
    z3=(0)+(sin30*rf*math.cos(theta3*p)-cos30*rf*math.sin(theta3*p))+(-sin30*e*tan30/2)
    """
    x1=0
    y1=((e-f)*tan30/2)-rf*math.cos(theta1*p)
    z1=+rf*math.sin(theta1*p)

    x2=(((f-e)*tan30/2)+rf*math.cos(theta2*p))*cos30
    y2=(((f-e)*tan30/2)+rf*math.cos(theta2*p))*sin30
    z2=+rf*math.sin(theta2*p)

    x3=-(((f-e)*tan30/2)+rf*math.cos(theta3*p))*cos30
    y3=(((f-e)*tan30/2)+rf*math.cos(theta3*p))*sin30
    z3=+rf*math.sin(theta3*p)


    w1=x1*x1+y1*y1+z1*z1
    w2=x2*x2+y2*y2+z2*z2
    w3=x3*x3+y3*y3+z3*z3

    d=x3*(y2-y1)-x2*(y3-y1)

    a1=(1/d)*((z2-z1)*(y3-y1)-(z3-z1)*(y2-y1))
    b1=(-1/(2*d))*((w2-w1)*(y3-y1)-(w3-w1)*(y2-y1))

    a2=-(1/d)*((z2-z1)*x3-(z3-z1)*x2)
    b2=(1/(2*d))*((w2-w1)*x3-(w3-w1)*x2)

    a=a1*a1+a2*a2+1
    b=2*(a1*b1+a2*(b2-y1)-z1)
    c=b1*b1+(b2-y1)*(b2-y1)+z1*z1-re*re

    #zSOL1=(-b+math.sqrt(b*b-4*a*c))/(2*a)
    zSOL2=(-b-math.sqrt(b*b-4*a*c))/(2*a)

    #xSOL1=a1*zSOL1+b1
    xSOL2=a1*zSOL2+b1

    #ySOL1=a2*zSOL1+b2
    ySOL2=a2*zSOL2+b2

    return [xSOL2, ySOL2, zSOL2]

def angulos(x0,y0,z0):
    x1,y1,z1 = x0, y0-e*tan30/2, z0
    x1p,y1p,z1p = 0, y1, z0
    fx1, fy1, fz1 = 0, -f*tan30/2, 0
    a = (x0*x0 + y1*y1 + z0*z0 +rf*rf - re*re - fy1*fy1)/(2*z0)
    b = (fy1-y1)/z0
    d = -(a+b*fy1)*(a+b*fy1)+rf*(b*b*rf+rf)
    jx1 = 0
    jy1 = (fy1 - a*b - math.sqrt(d))/(b*b + 1)
    jz1 = a + b*jy1
    return 180.0*math.atan(-jz1/(jy1-fy1))/pi + (180.0 if jy1>fy1 else 0.0)

def inversa(x0,y0,z0):
    angul=[angulos(x0,y0,z0)]
    angul+=[angulos(x0*cos120+y0*sin120, y0*cos120-x0*sin120,z0)]
    angul+=[angulos(x0*cos120-y0*sin120, y0*cos120+x0*sin120,z0)]
    return list(map(lambda x: anguloaParametro(x), angul))

def anguloaParametro(angulo):
    return 512-512*angulo/150

def parametroaAngulo(parametro):
    return 150-150*parametro/512
