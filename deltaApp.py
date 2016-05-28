from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.widget import Widget
from kivy.clock import Clock
import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import cinematica
import itertools
import collections
import time
import serial as arduinoSerial
import copy
import math
from robot import *

class Inverso(MastermindInvers):
    def empezar(self):
        """
        Complementa la funcion empezar del juego inverso
        Se piensa un codigo aleatorio el cual el usuario ha de adivinar
        """
        self.codigo = [randint(0,4) for i in range(5)]
        print 'ready'
        print self.codigo

    def continuar(self, guess):
        """
        Complementa la funcion continuar el siguiente turno del juego inverso
        Calcula la respuesta del robot ante el codigo propuesta por el usuario
        """
        self.guess = copy.copy(guess)
        self.codigoPrueba = copy.copy(self.codigo)
        self.rojas = 0
        self.blancas = 0
        self.buscarRojas()
        self.buscarBlancas()
        return self.rojas, self.blancas

class Delta(MastermindDirecte, TabbedPanel):
    text_input = ObjectProperty(None)
    colors = ['Plata', 'Azul', 'Verde', 'Blanco', 'Rojo']
    #red = (255, 0, 0, 1) azul = (0, 100, 250, 1) amari = (255, 255, 0, 1) white = (255, 255, 255, 1) gris = (128, 128, 128, 1)
    colorsrgba = [(128, 128, 128, 1),(0, 100, 250, 1),(255, 255, 0, 1),(255, 255, 255, 1),(255, 0, 0, 1)]
    robot=Robot()
    robot.buscarServos()
    inv = Inverso()

    def jugar_p_directo(self):
        """
        Empieza el juego directo con un primer movimiento
        Si el programa tiene una configuracion cargada, primero limpia el tablero y luego empieza
        Dentro del while:
        Continua un turno del juego, requiere la respuesta del usuario por pulsadores
        Siempre guarda la ultima configuracion del robot para siguientes inicios
        """
        self.linea = 1
        choices, holes = 5, 5
    	self.pool = self.generate_initial_pool(choices, holes)#genera una lista con todas las posibilidades sin repetir
    	self.guess = [0,0,1,1,1]
        self.ids.textprueba.text = "Try this:"
        huecoX = 'hueco'+str(self.linea)
        for y in range(5):
            huecoXY=huecoX+str(y)
            self.ids[huecoXY].background_color = self.colorsrgba[self.guess[y]]
        Clock.schedule_once(self.esperar(), 1)
        checkbox = self.ids.checkbox
        checkbox.bind(active=on_checkbox_active)
        if checkbox.active == True:
            ######################################## cargamos la ultima configuracion
            ultimoCodigo = open('ultimoCodigo', 'r')
            ultimo = ultimoCodigo.readline().split('|')
            codigo = [int(i) for i in ultimo[:-1]]
            huecos = ultimo[5].split(',')
            huecos.reverse()
            matrizOcupados = [int(i) for i in huecos]
            for i in range(5):
                for e in range(5):
                    p=matrizOcupados.pop()
                    self.robot.listaHuecosColores[i][e][3]=p
            for i in range(5):
                p=matrizOcupados.pop()
                self.robot.listaHuecosRobot[i][3]=p
            ultimoCodigo.close()
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            self.robot.quitar_bolitas(codigo, self.guess)
            self.robot.poner_bolitas(self.guess, codigo)
            self.robot.mover_robot([0, 0, -24])
        else:
            print 'No hay archivo ultimoCodigo = No hay bolitas puestas'
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            ultimo = [None, None, None, None, None]
            self.robot.poner_bolitas(self.guess, ultimo)
            self.robot.mover_robot([0, 0, -24])
        ######################################### Guardamos la ultima combinacion y la matriz de huecos
        ultimoCodigo = open('ultimoCodigo', 'w')
        s=''
        for listaHuecosColor in self.robot.listaHuecosColores:
            for listaHuecoColor in listaHuecosColor:
                s+='{0},'.format(listaHuecoColor[3])
        for listaHuecoRobot in self.robot.listaHuecosRobot:
            s+='{0},'.format(listaHuecoRobot[3])
        ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.guess[0],self.guess[1],self.guess[2],self.guess[3],self.guess[4],s[:-1]))
        ultimoCodigo.close()
        continuar = Clock.create_trigger(self.continuar_p_directo)
        continuar() #1 intento
        continuar() #2 intento
        continuar() #3 intento
        continuar() #4 intento
        continuar() #5 intento
        continuar() #6 intento

    def continuar_p_directo(self):
        """
        ######################################### respuesta del arduino
        self.pulsadores = Arduino()
        respuesta = self.pulsadores.codigo2()
        correct = respuesta[0]
        close = respuesta[1]
        ########################################## termina respuesta
        """
        self.linea+=1
        Clock.schedule_interval(self.respuesta_d_arduino, 1)# respuesta del arduino
        respuesta = self.respuesta_d
        correct = respuesta[0]
        close = respuesta[1]
        feedback = self.Feedback(correct, close)
        if self.linea >1:
            self.ids['textrojo'+str(self.linea-1)].text = str(correct)
            self.ids['textblanco'+str(self.linea-1)].text = str(close)
        if feedback.correct == 5:
            print "\nHe ganado!!"
            self.ids.textprueba.text = "He ganado! (juas) (juas)"
            self.ids.jugar_p_directo.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_directo.text='Reiniciar (interfaz)'
            self.robot.celebrar()
            return None
        Clock.schedule_once(self.esperar(), 1)
        try:
            initime = time.time()
            self.previousPool = copy.copy(self.pool)
            self.pool = list(self.filter_pool(feedback)) #renueva la lista de posibles combinaciones restantes en base a la interaccion del usuario
            print "{0} posibles opciones restantes. Pensando...\n".format(len(self.pool))
            self.previousGuess = copy.copy(self.guess)
            self.guess = list(self.make_guess(feedback, initime))
            huecoX = 'hueco'+str(self.linea)
            for y in range(5):
                huecoXY=huecoX+str(y)
                self.ids[huecoXY].background_color = self.colorsrgba[self.guess[y]]
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            print self.previousGuess
            print self.guess
            self.robot.quitar_bolitas(self.previousGuess, self.guess)
            self.robot.poner_bolitas(self.guess, self.previousGuess)
            self.robot.mover_robot([0, 0, -24])
            ######################################### Guardamos la ultima combinacion y la matriz de huecos
            ultimoCodigo = open('ultimoCodigo', 'w')
            s=''
            for listaHuecosColor in self.robot.listaHuecosColores:
                for listaHuecoColor in listaHuecosColor:
                    s+='{0},'.format(listaHuecoColor[3])
            for listaHuecoRobot in self.robot.listaHuecosRobot:
                s+='{0},'.format(listaHuecoRobot[3])
            ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.guess[0],self.guess[1],self.guess[2],self.guess[3],self.guess[4],s[:-1]))
            ultimoCodigo.close()
        except:
            self.ids.textprueba.text = "Te has equivocado. Cambia tu respuesta y vuelve a intentarlo. Si persiste, reinicia."
            self.ids.jugar_p_directo.text = 'Reiniciar (pulsadores)'
            self.ids.empezar_i_directo.text='Reiniciar (interfaz)'
            self.ids.continuar_i_directo.text ='No tocar (interfaz)'
            self.pool = copy.copy(self.previousPool)

    def empezar_i_directo(self):
        self.linea = 1
        choices, holes = 5, 5
    	self.pool = self.generate_initial_pool(choices, holes)#genera una lista con todas las posibilidades sin repetir
    	self.guess = []
    	for i in range(holes):
            self.guess =[0,0,1,1,1]
        print "Try this: {0}".format(self.codeToColor(self.guess))
        self.ids.textprueba.text = "Try this:"#genera una combinacion cualquiera primera
        huecoX = 'hueco'+str(self.linea)
        for y in range(5):
            huecoXY=huecoX+str(y)
            self.ids[huecoXY].background_color = self.colorsrgba[self.guess[y]]
        Clock.schedule_once(self.esperar(), 1)
        checkbox = self.ids.checkbox
        checkbox.bind(active=on_checkbox_active)
        if checkbox.active == True:
            ######################################## cargamos la ultima configuracion
            ultimoCodigo = open('ultimoCodigo', 'r')
            ultimo = ultimoCodigo.readline().split('|')
            codigo = [int(i) for i in ultimo[:-1]]
            huecos = ultimo[5].split(',')
            huecos.reverse()
            matrizOcupados = [int(i) for i in huecos]
            for i in range(5):
                for e in range(5):
                    p=matrizOcupados.pop()
                    self.robot.listaHuecosColores[i][e][3]=p
            for i in range(5):
                p=matrizOcupados.pop()
                self.robot.listaHuecosRobot[i][3]=p
            ultimoCodigo.close()
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            self.robot.quitar_bolitas(codigo, self.guess)
            self.robot.poner_bolitas(self.guess, codigo)
            self.robot.mover_robot([0, 0, -24])
        else:
            print 'No hay archivo ultimoCodigo = No hay bolitas puestas'
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            ultimo = [None, None, None, None, None]
            self.robot.poner_bolitas(self.guess, ultimo)
            self.robot.mover_robot([0, 0, -24])
        ######################################### Guardamos la ultima combinacion y la matriz de huecos
        ultimoCodigo = open('ultimoCodigo', 'w')
        s=''
        for listaHuecosColor in self.robot.listaHuecosColores:
            for listaHuecoColor in listaHuecosColor:
                s+='{0},'.format(listaHuecoColor[3])
        for listaHuecoRobot in self.robot.listaHuecosRobot:
            s+='{0},'.format(listaHuecoRobot[3])
        ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.guess[0],self.guess[1],self.guess[2],self.guess[3],self.guess[4],s[:-1]))
        ultimoCodigo.close()

    def continuar_i_directo(self):
        """
        Continua un turno del juego, requiere la respuesta del usuario por texto de interfaz
        Siempre guarda la ultima configuracion del robot para siguientes inicios
        """
        self.linea+=1
        correct = int(self.ids.reds.text)
        close = int(self.ids.whites.text)
        feedback = self.Feedback(correct, close)
        if self.linea >1:
            self.ids['textrojo'+str(self.linea-1)].text = str(correct)
            self.ids['textblanco'+str(self.linea-1)].text = str(close)
        if feedback.correct == 5:
            print "\nHe ganado!!"
            self.ids.textprueba.text = "He ganado! (juas) (juas)"
            self.ids.jugar_p_directo.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_directo.text='Reiniciar (interfaz)'
            self.robot.celebrar()
            return None
        Clock.schedule_once(self.esperar(), 1)
        try:
            initime = time.time()
            self.previousPool = copy.copy(self.pool)
            self.pool = list(self.filter_pool(feedback)) #renueva la lista de posibles combinaciones restantes en base a la interaccion del usuario
            print "{0} posibles opciones restantes. Pensando...\n".format(len(self.pool))
            self.previousGuess = copy.copy(self.guess)
            self.guess = list(self.make_guess(feedback, initime))
            huecoX = 'hueco'+str(self.linea)
            for y in range(5):
                huecoXY=huecoX+str(y)
                self.ids[huecoXY].background_color = self.colorsrgba[self.guess[y]]
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            print self.previousGuess
            print self.guess
            self.robot.quitar_bolitas(self.previousGuess, self.guess)
            self.robot.poner_bolitas(self.guess, self.previousGuess)
            self.robot.mover_robot([0, 0, -24])
            ######################################### Guardamos la ultima combinacion y la matriz de huecos
            ultimoCodigo = open('ultimoCodigo', 'w')
            s=''
            for listaHuecosColor in self.robot.listaHuecosColores:
                for listaHuecoColor in listaHuecosColor:
                    s+='{0},'.format(listaHuecoColor[3])
            for listaHuecoRobot in self.robot.listaHuecosRobot:
                s+='{0},'.format(listaHuecoRobot[3])
            ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.guess[0],self.guess[1],self.guess[2],self.guess[3],self.guess[4],s[:-1]))
            ultimoCodigo.close()
        except:
            self.ids.textprueba.text = "Te has equivocado. Cambia tu respuesta y vuelve a intentarlo. Si persiste, reinicia."
            self.ids.jugar_p_directo.text = 'Reiniciar (pulsadores)'
            self.ids.empezar_i_directo.text='Reiniciar (interfaz)'
            self.ids.continuar_i_directo.text ='Reintentar (interfaz)'
            self.pool = copy.copy(self.previousPool)

    def jugar_p_inverso(self):
        """
        Empieza el juego inverso con un primer movimiento
        Requiere la respuesta del usuario por pulsadores
        Dentro del while:
        Continua un turno del juego, requiere la respuesta del usuario por pulsadores
        """
        self.linea2 = 0
        self.inv.empezar()
        self.linea2+=1
        Clock.schedule_interval(self.respuesta_i_arduino, 1)# respuesta del arduino
        guess2 = self.respuesta_i_arduino
        print guess2
        """
        ######################################### respuesta del arduino
        print 'hola'
        self.pulsadores = Arduino()
        guess2 = self.pulsadores.codigo5()
        print guess2
        """
        rojas2, blancas2 = self.inv.continuar(guess2)
        print rojas2, blancas2
        self.nuevas = [None, None, None, None, None]
        for i in range(rojas2):
            self.nuevas[i]=4
        for i in range(blancas2):
            self.nuevas[i+rojas2]=3
        self.viejas = [None, None, None, None, None]
        huecoX = '2hueco'+str(self.linea2)
        for y in range(5):
            huecoXY=huecoX+str(y)
            print guess2[y]
            self.ids[huecoXY].background_color = self.colorsrgba[guess2[y]]
        Clock.schedule_once(self.esperar(), 1)
        checkbox = self.ids.checkbox
        checkbox.bind(active=on_checkbox_active)
        if checkbox.active == True:
            ######################################## cargamos la ultima configuracion
            ultimoCodigo = open('ultimoCodigo', 'r')
            ultimo = ultimoCodigo.readline().split('|')
            codigo = [int(i) for i in ultimo[:-1]]
            huecos = ultimo[5].split(',')
            huecos.reverse()
            matrizOcupados = [int(i) for i in huecos]
            for i in range(5):
                for e in range(5):
                    p=matrizOcupados.pop()
                    self.robot.listaHuecosColores[i][e][3]=p
            for i in range(5):
                p=matrizOcupados.pop()
                self.robot.listaHuecosRobot[i][3]=p
            ultimoCodigo.close()
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            self.robot.quitar_bolitas(codigo, self.nuevas)
            self.robot.poner_bolitas(self.nuevas, codigo)
            self.robot.mover_robot([0, 0, -24])
        else:
            print 'No hay archivo ultimoCodigo = No hay bolitas puestas'
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            ultimo = [None, None, None, None, None]
            self.robot.poner_bolitas(self.nuevas, ultimo)
            self.robot.mover_robot([0, 0, -24])
        self.ids['2textrojo'+str(self.linea2)].text = str(rojas2)
        self.ids['2textblanco'+str(self.linea2)].text = str(blancas2)
        if rojas2 == 5:
            self.ids.textprueba2.text = "Has ganado! (jo) (jo)"
            self.ids.jugar_p_inverso.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_inverso.text='Reiniciar (interfaz)'
            return None
        continuar = Clock.create_trigger(self.continuar_p_inverso)
        continuar() #2 intento
        continuar() #3 intento
        continuar() #4 intento
        continuar() #5 intento
        continuar() #6 intento
        continuar() #7 intento

    def continuar_p_inverso(self):
        self.linea2+=1
        Clock.schedule_interval(self.respuesta_i_arduino, 1)# respuesta del arduino
        guess2 = self.respuesta_i_arduino
        print guess2
        """
        ######################################### respuesta del arduino
        print 'hola'
        self.pulsadores = Arduino()
        guess2 = self.pulsadores.codigo5()
        print guess2
        """
        rojas2, blancas2 = self.inv.continuar(guess2)
        print rojas2, blancas2
        self.viejas = copy.copy(self.nuevas)
        self.nuevas = [None, None, None, None, None]
        for i in range(rojas2):
            self.nuevas[i]=4
        for i in range(blancas2):
            self.nuevas[i+rojas2]=3
        huecoX = '2hueco'+str(self.linea2)
        for y in range(5):
            huecoXY=huecoX+str(y)
            print guess2[y]
            self.ids[huecoXY].background_color = self.colorsrgba[guess2[y]]
        Clock.schedule_once(self.esperar(), 1)
        #########################################aqui ha de venir el movimiento de bolitas!!!!
        print self.viejas
        print self.nuevas
        self.robot.quitar_bolitas(self.viejas, self.nuevas)
        self.robot.poner_bolitas(self.nuevas, self.viejas)
        self.robot.mover_robot([0, 0, -24])
        ######################################### Guardamos la ultima combinacion y la matriz de huecos
        ultimoCodigo = open('ultimoCodigo', 'w')
        s=''
        for listaHuecosColor in self.robot.listaHuecosColores:
            for listaHuecoColor in listaHuecosColor:
                s+='{0},'.format(listaHuecoColor[3])
        for listaHuecoRobot in self.robot.listaHuecosRobot:
            s+='{0},'.format(listaHuecoRobot[3])
        ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.nuevas[0],self.nuevas[1],self.nuevas[2],self.nuevas[3],self.nuevas[4],s[:-1]))
        ultimoCodigo.close()
        self.ids['2textrojo'+str(self.linea2)].text = str(rojas2)
        self.ids['2textblanco'+str(self.linea2)].text = str(blancas2)
        if rojas2 == 5:
            self.ids.textprueba2.text = "Has ganado! (jo) (jo)"
            self.ids.jugar_p_inverso.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_inverso.text='Reiniciar (interfaz)'
            return None

    def empezar_i_inverso(self):
        """
        Empieza el juego inverso con un primer movimiento
        Requiere la respuesta del usuario por por texto de interfaz
        """
        self.linea2 = 0
        self.inv.empezar()
        self.linea2+=1
        guess2 = self.ids.codigo.text
        guess2 = guess2.split()
        guess2 = [int(i) for i in guess2]
        print guess2
        rojas2, blancas2 = self.inv.continuar(guess2)
        print rojas2, blancas2
        self.nuevas = [None, None, None, None, None]
        for i in range(rojas2):
            self.nuevas[i]=4
        for i in range(blancas2):
            self.nuevas[i+rojas2]=3
        self.viejas = [None, None, None, None, None]
        huecoX = '2hueco'+str(self.linea2)
        for y in range(5):
            huecoXY=huecoX+str(y)
            print guess2[y]
            self.ids[huecoXY].background_color = self.colorsrgba[guess2[y]]
        Clock.schedule_once(self.esperar(), 1)
        checkbox = self.ids.checkbox
        checkbox.bind(active=on_checkbox_active)
        if checkbox.active == True:
            ######################################## cargamos la ultima configuracion
            ultimoCodigo = open('ultimoCodigo', 'r')
            ultimo = ultimoCodigo.readline().split('|')
            codigo = [int(i) for i in ultimo[:-1]]
            huecos = ultimo[5].split(',')
            huecos.reverse()
            matrizOcupados = [int(i) for i in huecos]
            for i in range(5):
                for e in range(5):
                    p=matrizOcupados.pop()
                    self.robot.listaHuecosColores[i][e][3]=p
            for i in range(5):
                p=matrizOcupados.pop()
                self.robot.listaHuecosRobot[i][3]=p
            ultimoCodigo.close()
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            self.robot.quitar_bolitas(codigo, self.nuevas)
            self.robot.poner_bolitas(self.nuevas, codigo)
            self.robot.mover_robot([0, 0, -24])
        else:
            print 'No hay archivo ultimoCodigo = No hay bolitas puestas'
            #########################################aqui ha de venir el movimiento de bolitas!!!!
            ultimo = [None, None, None, None, None]
            self.robot.poner_bolitas(self.nuevas, ultimo)
            self.robot.mover_robot([0, 0, -24])
        self.ids['2textrojo'+str(self.linea2)].text = str(rojas2)
        self.ids['2textblanco'+str(self.linea2)].text = str(blancas2)
        if rojas2 == 5:
            self.ids.textprueba2.text = "Has ganado! (jo) (jo)"
            self.ids.jugar_p_inverso.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_inverso.text='Reiniciar (interfaz)'
            return None

    def continuar_i_inverso(self):
        """
        Continua un turno del juego, requiere la respuesta del usuario por texto de interfaz
        """
        self.linea2+=1
        guess2 = self.ids.codigo.text
        guess2 = guess2.split()
        guess2 = [int(i) for i in guess2]
        print guess2
        rojas2, blancas2 = self.inv.continuar(guess2)
        print rojas2, blancas2
        self.viejas = copy.copy(self.nuevas)
        self.nuevas = [None, None, None, None, None]
        for i in range(rojas2):
            self.nuevas[i]=4
        for i in range(blancas2):
            self.nuevas[i+rojas2]=3
        huecoX = '2hueco'+str(self.linea2)
        for y in range(5):
            huecoXY=huecoX+str(y)
            print guess2[y]
            self.ids[huecoXY].background_color = self.colorsrgba[guess2[y]]
        Clock.schedule_once(self.esperar(), 1)
        #########################################aqui ha de venir el movimiento de bolitas!!!!
        print self.viejas
        print self.nuevas
        self.robot.quitar_bolitas(self.viejas, self.nuevas)
        self.robot.poner_bolitas(self.nuevas, self.viejas)
        self.robot.mover_robot([0, 0, -24])
        ######################################### Guardamos la ultima combinacion y la matriz de huecos
        ultimoCodigo = open('ultimoCodigo', 'w')
        s=''
        for listaHuecosColor in self.robot.listaHuecosColores:
            for listaHuecoColor in listaHuecosColor:
                s+='{0},'.format(listaHuecoColor[3])
        for listaHuecoRobot in self.robot.listaHuecosRobot:
            s+='{0},'.format(listaHuecoRobot[3])
        ultimoCodigo.write('{0}|{1}|{2}|{3}|{4}|{5}'.format(self.nuevas[0],self.nuevas[1],self.nuevas[2],self.nuevas[3],self.nuevas[4],s[:-1]))
        ultimoCodigo.close()
        self.ids['2textrojo'+str(self.linea2)].text = str(rojas2)
        self.ids['2textblanco'+str(self.linea2)].text = str(blancas2)
        if rojas2 == 5:
            self.ids.textprueba2.text = "Has ganado! (jo) (jo)"
            self.ids.jugar_p_inverso.text='Reiniciar (pulsadores)'
            self.ids.empezar_i_inverso.text='Reiniciar (interfaz)'
            return None

    def respuesta_d_arduino(self, dt):
        respuesta = arduino.readline()
        if len(respuesta)==3:
            respuesta=[int(i) for i in respuesta.split('|')]
            self.respuesta_d = respuesta
            return False

    def respuesta_i_arduino(self, dt):
        respuesta = arduino.readline()
        if len(respuesta)==11:
            respuesta=[int(i) for i in respuesta[1:-1].split('|')]
            self.respuesta_i = respuesta
            return False

    def esperar(self, dt):
        return None

    def on_checkbox_active(checkbox, value):
        if value:
            return True
        else:
            return False

class DeltaApp(App):
    def build(self):
        juego = Delta()
        return juego

if __name__ == '__main__':
    try:
        arduino = arduinoSerial.Serial('/dev/ttyACM0', 115200)
    except:
        print "No se encuentra Arduino"
        exit()
    DeltaApp().run()
    arduino.close()
