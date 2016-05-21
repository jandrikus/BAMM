import itertools
import collections
import time
import serial as arduinoSerial
import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import math
import cinematica
import copy
from random import randint

class MastermindDirecte():

    colors = ['Rojo', 'Azul', 'Amarillo', 'Blanco', 'Plateado']
    Feedback = collections.namedtuple('Feedback', ['correct', 'close'])

    def colorToCode(self,color):
        """
        asigna un numero correspondiente al color
        """
        code = self.colors.index(color)
        return code

    def codeToColor(self,code):
        """
        convierte el codgo numerico a combinacion de colores
        """
        colors2=""
        for i in code:
            colors2 += self.colors[i]+"-"
        return colors2[:-1]

    def generate_initial_pool(self,choices, holes):
        """
        crea una lista que contiene todas las posibles combinaciones numericas en tuples
        """
        lista =[]
        for i in range(holes):
            listaJ=[]
            for j in range(choices):
                listaJ+=[j]
            lista += [listaJ]
        return list(itertools.product(*lista)) #todas las posibles combinaciones sin repetir

    def buscarRojas(self):
        for i in range(5):
            if self.codigoPrueba[i] == self.guessPrueba[i]:
                self.rojas+=1
                self.codigoPrueba[i]=None
                self.guessPrueba[i]=None
        for i in range(self.rojas):
            self.codigoPrueba.remove(None)
            self.guessPrueba.remove(None)

    def buscarBlancas(self):
        for i in self.guessPrueba:
            if i in self.codigoPrueba:
                self.blancas+=1
                self.codigoPrueba.remove(i)

    def get_feedback(self):
        self.buscarRojas()
        self.buscarBlancas()
        return self.Feedback(self.rojas, self.blancas) #namedtuple con los ROJOS y BLANCOS de las suposiciones del programa

    def is_match(self,feedback):#possible = una a una cada combinacion posible de la lista pool; feedback = ROJAS y BLANCAS del usuario
        return feedback == self.get_feedback() #compara si los rojos y los blancos de nuestras suposiciones coinciden con los de usuario

    def filter_pool(self, feedback):
        for possible in self.pool: #cada combinacion restante posible
            self.rojas = 0
            self.blancas = 0
            self.codigoPrueba = list(copy.copy(possible))
            self.guessPrueba = list(copy.copy(self.guess))
            if self.is_match(feedback) and (possible != self.guess): #si los rojos y blancos de usuario y programa coinciden y no es igual a guess (porque ya sabemos que guess no es buena!!), entonces:
                yield possible #entrega la combinacion posible basada en las nuevas condiciones

    def make_guess(self, feedback, initime):#renueva el guess en base a la interaccion del usuario
        min_length = float('infinity')
        best_choice = None
        deadtime = time.time()+5 #pone tiempo limite de 5 segundos para calcular otra combinacion
        for possible in self.pool:#miramos las combinaciones restantes posibles de la lista de opciones que hemos renovado
            length = len(list(self.filter_pool(feedback))) #cantidad de combinaciones que quedan si una combinacion dada cualquiera fuera aquella que el usuario ha rechazado!
            if min_length > length:
                min_length = length
                best_choice = possible #vamos elegiendo la combinacion para la cual quedan menos combinaciones posibles
            if time.time() > deadtime:
                print "...he tardado {0} segundos".format(deadtime-initime)
                return best_choice
        print "...he tardado {0} segundos".format(time.time()-initime)
        return best_choice

    def play(self):
        choices = int(raw_input("Cantidad de colores? "), 10)
        holes = int(raw_input("Cantidad de huecos?  "), 10)
        self.pool = self.generate_initial_pool(choices, holes)#genera una lista con todas las posibilidades sin repetir
        self.guess = []
        for i in range(holes):
            if i < (holes/2):
                self.guess +=[0]
            else:
                self.guess +=[1]
        while True:
            print "Try this: {0}".format(self.codeToColor(self.guess))
            correct = int(raw_input("    # Bolita rojas?   "))
            close = int(raw_input("    # Bolitas blancas? "))
            feedback = self.Feedback(correct, close)
            if feedback.correct == holes:
                break
            initime = time.time()
            self.pool = list(self.filter_pool(feedback))#renueva la lista de posibles combinaciones restantes en base a la interaccion del usuario
            print "{0} posibles opciones restantes. Pensando...\n".format(len(self.pool))
            self.guess = self.make_guess(feedback, initime)
        print "\nGanaste!"

class MastermindInvers():

    colors = ['Rojo', 'Azul', 'Amarillo', 'Blanco', 'Plateado']

    def colorToCode(self,color):
        code = self.colors.index(color)
        return code

    def codeToColor(self,code):
        colors2=""
        for i in code:
            colors2 += self.colors[i]+"-"
        return colors2[:-1]

    def buscarRojas(self):
        for i in range(5):
            if self.codigoPrueba[i] == self.guess[i]:
                self.rojas+=1
                self.codigoPrueba[i]=None
                self.guess[i]=None
        for i in range(self.rojas):
            self.codigoPrueba.remove(None)
            self.guess.remove(None)

    def buscarBlancas(self):
        for i in self.guess:
            if i in self.codigoPrueba:
                self.blancas+=1
                self.codigoPrueba.remove(i)

    def play(self):
        self.codigo = [randint(0,5) for i in range(5)]
        self.guess = raw_input("Combinacion? a,b,c,d,e ")
        self.guess = self.guess.split()
        self.guess = [int(i) for i in self.guess]
        while True:
            self.codigoPrueba = copy.copy(self.codigo)
            self.rojas = 0
            self.blancas = 0
            self.buscarRojas()
            self.buscarBlancas()
            if self.rojas == 5:
                break
            print 'Rojas: {0}\nBlancas: {1}'.format(self.rojas, self.blancas)
            self.guess = raw_input("Combinacion? a,b,c,d,e ")
            self.guess = self.guess.split()
            self.guess = [int(i) for i in self.guess]

class Robot():

    """
    metodos: buscarServos, validateInput, getCurrentPosition, mover_robot, poner_bolita, quitar_bolita
    atributos: iman
    """
    listaHuecosColores = [
                            [[-6, -3.6, -27.4, 1], [-5.9, -0.1, -27.4, 1], [-6, 3.2, -27.4, 1], [-5.9, 6, -27.4, 1], [-5.9, 9.2, -27.4, 1]],
                            [[-3, -3.4, -27.6, 1], [-2.8, -0, -27.4, 1], [-3, 3, -27.4, 1], [-3, 6, -27.4, 1], [-3, 9, -27.4, 1]],
                            [[0, -3.6, -27.4, 1], [0.2, -0.5, -27.4, 1], [0.4, 3.2, -27.4, 1], [0.4, 6.4, -27.4, 1], [0.2, 9.2, -27.4, 1]],
                            [[3.2, -3.6, -27.4, 1], [3.3, -0.3, -27.4, 1], [3.6, 3.1, -27.4, 1], [3.6, 6.1, -27.4, 1], [3.3, 9.2, -27.4, 1]],
                            [[6.2, -3.6, -27.4, 1], [6.5, -0.5, -27.4, 1], [6.6, 3, -27.4, 1], [6.6, 6.1, -27.4, 1], [6.5, 9, -27.4, 1]]
        ]
    listaHuecosRobot = [
                            [-6, -9.8, -27.3, 0],
                            [-2.8, -9.6, -27.3, 0],
                            [0.1, -9.5, -27.3, 0],
                            [3, -9.5, -27.3, 0],
                            [6.4, -9.5, -27.3, 0]
        ]
    """
    en listaHuecosColores cada indice es un color llamado listaHuecosColor,
    dentro de listaHuecosColor cada indice es un hueco llamado listaHuecoColor,
    dentro de listaHuecoColor -> [x, y, z, ocupado/vacio]
    en listaHuecosRobot cada indice es un hueco llamado listaHuecoColor,
    dentro de listaHuecoColor -> [x, y, z, ocupado/vacio]
    1 significa ocupado
    0 significa vacio
    """

    def buscarServos(self):
        #busca los servos, los inicia e inicializa tambien el iman
        self.iman = Arduino()
        parser = optparse.OptionParser()
        parser.add_option("-c", "--clean", action="store_true", dest="clean", default=False, help="Ignore the settings.yaml file if it exists and prompt for new settings.")
        (options, args) = parser.parse_args()
        # Look for a settings.yaml file
        settingsFile = 'settings.yaml'
        if not options.clean and os.path.exists(settingsFile):
            with open(settingsFile, 'r') as fh:
                self.settings = yaml.load(fh)
        # If we were asked to bypass, or don't have settings
        else:
            self.settings = {}
            self.settings['port'] = '/dev/ttyUSB0'
            # Baud rate
            baudRate = None
            while not baudRate:
                brTest = raw_input("Enter baud rate [Default: 1000000 bps]:")
                if not brTest:
                    baudRate = 1000000
                else:
                    baudRate = self.validateInput(brTest, 9600, 1000000)
            self.settings['baudRate'] = baudRate
            # Servo ID
            highestServoId = None
            while not highestServoId:
                hsiTest = raw_input("Please enter the highest ID of the connected servos: ")
                highestServoId = self.validateInput(hsiTest, 1, 255)
            self.settings['highestServoId'] = highestServoId
            highestServoId = self.settings['highestServoId']
            # Establish a serial connection to the dynamixel network.
            # This usually requires a USB2Dynamixel
            serial = dynamixel.SerialStream(port=self.settings['port'], baudrate=self.settings['baudRate'], timeout=1)
            # Instantiate our network object
            net = dynamixel.DynamixelNetwork(serial)
            # Ping the range of servos that are attached
            print "Scanning for Dynamixels..."
            net.scan(1, highestServoId)
            self.settings['servoIds'] = []
            print "Found the following Dynamixels IDs: "
            for dyn in net.get_dynamixels():
                print dyn.id
                self.settings['servoIds'].append(dyn.id)
            # Make sure we actually found servos
            if not self.settings['servoIds']:
                print 'No Dynamixels Found!'
                sys.exit(0)
            # Save the output settings to a yaml file
            with open(settingsFile, 'w') as fh:
                yaml.dump(self.settings, fh)
                print("Your settings have been saved to 'settings.yaml'. \nTo " +"change them in the future either edit that file or run " + "this example with -c.")
        # Establish a serial connection to the dynamixel network.
        # This usually requires a USB2Dynamixel
        serial = dynamixel.SerialStream(port=self.settings['port'], baudrate=self.settings['baudRate'], timeout=1)

        # Instantiate our network object
        self.net = dynamixel.DynamixelNetwork(serial)

        # Populate our network with dynamixel objects
        for servoId in self.settings['servoIds']:
            newDynamixel = dynamixel.Dynamixel(servoId, self.net)
            self.net._dynamixel_map[servoId] = newDynamixel
            #net._dynamixel_map es un diccionario que contiene los motores accesibles con el codigo id

    def validateInput(self,userInput, rangeMin, rangeMax):
        try:
            inTest = int(userInput)
            if (inTest < rangeMin) or (inTest > rangeMax):
                    print "ERROR: Value out of range [" + str(rangeMin) + '-' + str(rangeMax) + "]"
                    return None
        except ValueError:
            print("ERROR: Please enter an integer")
            return None
        return inTest

    def getCurrentPosition(self):
        pos1 = cinematica.parametroaAngulo(self.net._dynamixel_map[6].current_position)
        pos2 = cinematica.parametroaAngulo(self.net._dynamixel_map[4].current_position)
        pos3 = cinematica.parametroaAngulo(self.net._dynamixel_map[3].current_position)
        return cinematica.directa(pos1, pos2, pos3)

    def mover_robot(self, destination):
        #mueve el robot a la 'destination' con la 'speed' indicad
        ################################### nos aseguramos que 'destination' sea transforme a lista, para evitar errores de si fuese string o tuple
        destino = []
        for i in destination:
            destino += [i]
        destino = list(map(lambda x: float(x), destino))
        ################################### preparamos la parametrizacion del movimiento
        origen = self.getCurrentPosition()
        distancia = math.sqrt((destino[0]-origen[0])*(destino[0]-origen[0])+(destino[1]-origen[1])*(destino[1]-origen[1])+(destino[2]-origen[2])*(destino[2]-origen[2]))
        director = [(destino[0]-origen[0]),(destino[1]-origen[1]),(destino[2]-origen[2])]
        dx = 0
        velocidades=[200, 400, 600, 200, 50]
        factores=[0.05, 0.25, 0.75, 0.9, 1]
        i=0
        ################################### para evitar movimientos indeseados, pasaremos por 3 punto(s) intermedios a distintas velocidades
        while dx<=distancia:
            x=origen[0]+(factores[i])*director[0]
            y=origen[1]+(factores[i])*director[1]
            z=origen[2]+(factores[i])*director[2]

            parametros_needed = cinematica.inversa(x,y,z)
            posicion1 = int(parametros_needed[0])
            posicion2 = int(parametros_needed[1])
            posicion3 = int(parametros_needed[2])

            #servo principal segun base de referencia
            self.net._dynamixel_map[6].moving_speed = velocidades[i]
            self.net._dynamixel_map[6].torque_enable = True
            self.net._dynamixel_map[6].torque_limit = 1000
            self.net._dynamixel_map[6].max_torque = 1023
            self.net._dynamixel_map[6].goal_position = posicion1

            #servo a la derecha del principal
            self.net._dynamixel_map[4].moving_speed = velocidades[i]
            self.net._dynamixel_map[4].torque_enable = True
            self.net._dynamixel_map[4].torque_limit = 1000
            self.net._dynamixel_map[4].max_torque = 1023
            self.net._dynamixel_map[4].goal_position = posicion2

            #servo a la izquierda del principal
            self.net._dynamixel_map[3].moving_speed =velocidades[i]
            self.net._dynamixel_map[3].torque_enable = True
            self.net._dynamixel_map[3].torque_limit = 1000
            self.net._dynamixel_map[3].max_torque = 1023
            self.net._dynamixel_map[3].goal_position = posicion3

            #mueve los servos a la vez
            self.net.synchronize()

            dx+=distancia/4
            try:
                if distancia*(factores[i]-factores[i-1])>4:
                    time.sleep(0.1)
                else:
                    time.sleep(0.05)
            except IndexError:
                #factores[i-1] no existe porque i=0
                if distancia*factores[i]>4:
                    time.sleep(0.1)
                else:
                    time.sleep(0.05)
            i+=1
        """
        parametros_needed = cinematica.inversa(destino[0],destino[1],destino[2])
        posicion1 = int(parametros_needed[0])
        posicion2 = int(parametros_needed[1])
        posicion3 = int(parametros_needed[2])

        #servo principal segun base de referencia
        self.net._dynamixel_map[6].moving_speed = speed
        self.net._dynamixel_map[6].torque_enable = True
        self.net._dynamixel_map[6].torque_limit = 1000
        self.net._dynamixel_map[6].max_torque = 1023
        self.net._dynamixel_map[6].goal_position = posicion1

        #servo a la derecha del principal
        self.net._dynamixel_map[4].moving_speed = speed
        self.net._dynamixel_map[4].torque_enable = True
        self.net._dynamixel_map[4].torque_limit = 1000
        self.net._dynamixel_map[4].max_torque = 1023
        self.net._dynamixel_map[4].goal_position = posicion2

        #servo a la izquierda del principal
        self.net._dynamixel_map[3].moving_speed =speed
        self.net._dynamixel_map[3].torque_enable = True
        self.net._dynamixel_map[3].torque_limit = 1000
        self.net._dynamixel_map[3].max_torque = 1023
        self.net._dynamixel_map[3].goal_position = posicion3

        #mueve los servos a la vez
        self.net.synchronize()
        """

    def poner_bolita(self,huecoColor, huecoRobot):
        """
        1. mover a hueco de color
        2. encender y bajar
        3. subir
        4. mover a hueco de robot
        5. bajar y apagar
        6. subir
        """
        ############################################## movemos el robot al huecoColor
        self.mover_robot(huecoColor)
        time.sleep(0.1)
        ############################################## encedemos el electroiman y lo bajamos
        huecoColor2 = list(copy.copy(huecoColor)) #creamos una copia y la convertimos en lista para poderla editar
        huecoColor2[2]-=2.7 #le restamos 1 a la coordenada z para que coja la bola
        self.iman.encender()#encendemos el iman
        self.mover_robot(huecoColor2)#movemos el robot a la posicion inferior
        time.sleep(0.1)
        ############################################## subimos el electroiman (mantenemos el iman encendido)
        huecoColor2[2]+=2.7#devolvemos la coordenada z original
        self.mover_robot(huecoColor2)
        time.sleep(0.1)
        ############################################## movemos el robot al huecoRobot, el cual ya hemos verificado que este vacio
        self.mover_robot(huecoRobot)
        time.sleep(0.1)
        ############################################## bajamos el electroiman y lo apagamos
        huecoRobot2 = list(copy.copy(huecoRobot))
        huecoRobot2[2]-=2.7
        self.mover_robot(huecoRobot2)
        self.iman.apagar()
        time.sleep(0.3)
        ############################################## subimos el electroiman (ya apagado)
        huecoRobot2[2]+=2.7#devolvemos la coordenada z original
        self.mover_robot(huecoRobot2)
        time.sleep(0.1)

    def quitar_bolita(self, huecoColor, huecoRobot):
        """
        1. mover a hueco de robot
        2. encender y bajar
        3. subir
        4. mover a hueco de color
        5. bajar y apagar
        6. subir
        """
        ############################################## movemos el robot al huecoRobot
        self.mover_robot(huecoRobot)
        time.sleep(0.1)
        ############################################## encedemos el electroiman y lo bajamos
        huecoRobot2 = list(copy.copy(huecoRobot))
        self.iman.encender()
        huecoRobot2[2]-=2.5
        self.mover_robot(huecoRobot2)
        time.sleep(0.1)
        ############################################## subimos el electroiman (mantenemos el iman encendido)
        huecoRobot2[2]+=2.5#devolvemos la coordenada z original
        self.mover_robot(huecoRobot2)
        time.sleep(0.1)
        ############################################## movemos el robot al huecoColor, el cual ya hemos verificado que este vacio
        self.mover_robot(huecoColor)
        time.sleep(0.1)
        ############################################## bajamos el electroiman y lo apagamos
        huecoColor2 = list(copy.copy(huecoColor))
        huecoColor2[2]-=2.5
        self.mover_robot(huecoColor2)
        self.iman.apagar()
        time.sleep(0.3)
        ############################################## subimos el electroiman (ya apagado)
        huecoColor2[2]+=2.5#devolvemos la coordenada z original
        self.mover_robot(huecoColor2)
        time.sleep(0.1)

    def poner_bolitas(self, guess, previousGuess):
        """
        1. rellena el huecoRobot[0] y lo marca como ocupado
        2. rellena el huecoRobot[1] y lo marca como ocupado
        3. rellena el huecoRobot[2] y lo marca como ocupado
        4. rellena el huecoRobot[3] y lo marca como ocupado
        5. rellena el huecoRobot[4] y lo marca como ocupado
        """
        listaHuecosRobotIndice = 0
        for bolita in guess:
            ######################################## lista de los huecos del color de la bolita
            listaHuecosColor=self.listaHuecosColores[bolita]
            if self.listaHuecosRobot[listaHuecosRobotIndice][3] == 0:
                ######################################## cogemos la posicion de un hueco de color ocupado y lo marcamos como vacio
                i=0
                a=False
                for listaHuecoColor in listaHuecosColor:
                    if listaHuecoColor[3] == 1 and a==False:
                        huecoColor = listaHuecoColor[:3]
                        self.listaHuecosColores[bolita][i][3]=0
                        a=True
                    i+=1
                ######################################## cogemos la posicion del huecoRobot respectivo al indice, pensando que estan todos vacios ya
                huecoRobot = self.listaHuecosRobot[listaHuecosRobotIndice][:3]
                ######################################## ponemos la bolita
                self.poner_bolita(huecoColor, huecoRobot)
                ######################################## marcamos el huecoRobot como ocupado (y el huecoColor como vacio, hecho cuando cogimos su posicion)
                self.listaHuecosRobot[listaHuecosRobotIndice][3]=1
                ######################################## aumentamos el indice para ir al siguiente hueco
            listaHuecosRobotIndice+=1

    def quitar_bolitas(self, previousGuess, guess):
        """
        1. Mira si huecoRobot[0] esta vacio; si no lo esta, quita la bolita | si la bolita ya es correcta, no hace nada
        2. Mira si huecoRobot[1] esta vacio; si no lo esta, quita la bolita | si la bolita ya es correcta, no hace nada
        3. Mira si huecoRobot[2] esta vacio; si no lo esta, quita la bolita | si la bolita ya es correcta, no hace nada
        4. Mira si huecoRobot[3] esta vacio; si no lo esta, quita la bolita | si la bolita ya es correcta, no hace nada
        5. Mira si huecoRobot[4] esta vacio; si no lo esta, quita la bolita | si la bolita ya es correcta, no hace nada
        """
        listaHuecosRobotIndice = 0
        for bolita in previousGuess:
            if self.listaHuecosRobot[listaHuecosRobotIndice][3] == 1 and bolita!=guess[listaHuecosRobotIndice]:
                ######################################## lista de los huecos del color de la bolita
                listaHuecosColor=self.listaHuecosColores[bolita]
                ######################################## cogemos la posicion de un hueco de color vacio y lo marcamos como ocupado
                i=0
                a=False
                for listaHuecoColor in listaHuecosColor:
                    print listaHuecoColor[3]
                    if listaHuecoColor[3] == 0 and a==False:
                        huecoColor = listaHuecoColor[:3]
                        self.listaHuecosColores[bolita][i][3]=1
                        a=True
                    i+=1
                ######################################## cogemos la posicion del huecoRobot respectivo al indice
                huecoRobot = self.listaHuecosRobot[listaHuecosRobotIndice][:3]
                ######################################## quitamos la bolita
                self.quitar_bolita(huecoColor, huecoRobot)
                ######################################## marcamos el huecoRobot como libre (y el huecoColor como vacio, hecho cuando cogimos su posicion)
                self.listaHuecosRobot[listaHuecosRobotIndice][3]=0
                ######################################## aumentamos el indice para ir al siguiente hueco
            listaHuecosRobotIndice+=1

class Arduino():
    def __init__(self):
        self.arduino=arduinoSerial.Serial('/dev/ttyACM0', 115200)
    def encender(self):
        self.arduino.write('1')
    def apagar(self):
        self.arduino.write('0')
    def codigo2(self):
        a=True
        self.arduino.write('2')
        respuesta=''
        while a:
            try:
                respuesta += arduino.read()
                print respuesta
                if len(respuesta)==3:
                    a=False
            except:
                print 'El arduino no lee nada coherente con lo deseado'
        respuesta=[int(i) for i in respuesta.split('|')]
        return respuesta
    def codigo5(self):
        a=True
        self.arduino.write('3')
        respuesta=''
        while a:
            try:
                respuesta += arduino.read()
                print respuesta
                if len(respuesta)==9:
                    a=False
            except:
                print 'El arduino no lee nada coherente con lo deseado'
        respuesta=[int(i) for i in respuesta.split('|')]
        return respuesta

class JuegoDirecto(MastermindDirecte):
    robot=Robot()
    def play(self):
        self.robot.buscarServos()
        choices = int(raw_input("Cantidad de colores? "), 10)
        holes = int(raw_input("Cantidad de huecos?  "), 10)
        self.pool = self.generate_initial_pool(choices, holes)#genera una lista con todas las posibilidades sin repetir
        self.guess = []
        for i in range(holes):
            self.guess +=[0]
        self.previousGuess = []
        while True:
            print "Try this: {0}".format(self.codeToColor(self.guess))
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            self.robot.quitar_bolitas(self.previousGuess)
            self.robot.poner_bolitas(self.guess)
            ######################################### YA ESTA
            correct = int(raw_input("    # Bolita rojas?   "))
            close = int(raw_input("    # Bolitas blancas? "))
            feedback = self.Feedback(correct, close)
            if feedback.correct == holes:
                break
            initime = time.time()
            self.pool = list(self.filter_pool(self.pool, self.guess, feedback)) #renueva la lista de posibles combinaciones restantes en base a la interaccion del usuario
            print "{0} posibles opciones restantes. Pensando...\n".format(len(self.pool))
            self.previousGuess = self.guess
            self.guess = self.make_guess(self.pool, feedback, initime)
        print "\nGanaste!"
