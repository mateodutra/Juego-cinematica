# -*- coding: utf-8 -*-
import pygame
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator)
import pylab
import time
from math import sqrt
import pickle


import sys
import os

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()


screen = pygame.display.set_mode((800,600))

dt = 0.1 #Paso de funcion generada (no del sensor)
fs = int(1/dt)
estado_grafica = "ready"
estado_jugador = "en espera"
estado_datos = 0

#Fondo, título e ícono
background_resource = resource_path('recursos/Background.png')
background = pygame.image.load(background_resource)
pygame.display.set_caption("El Imitador")
icon_resource = resource_path('recursos/Icon.png')
icon = pygame.image.load(icon_resource)
pygame.display.set_icon(icon)

#Fuente
font_inicio = pygame.font.Font('recursos/MilkyNice.ttf',32)
font_nivel = pygame.font.Font('recursos/CaviarDreams.ttf',32)
font_terminado = pygame.font.Font('recursos/CaviarDreams.ttf',26)

#Selector de nivel
dificultad = 0
grafica = 0
fondo_nivel_resource = resource_path('recursos/Fondo_nivel.png')
fondo_nivel = pygame.image.load(fondo_nivel_resource)
fondo_terminado_resource = resource_path('recursos/Fondo_terminado.png')
fondo_terminado = pygame.image.load(fondo_terminado_resource)
mouseX = 0
mouseY = 0

#Player
playerImg_resource = resource_path('recursos/Player.png')
playerImg = pygame.image.load(playerImg_resource)
playerX = 10
playerY = 370

#Simulacion
simulacionImg_resource = resource_path('recursos/Player_simulacion.png')
simulacionImg = pygame.image.load(simulacionImg_resource)
simulacionX = 1000
simulacionY = 370

#Estrellas
estrella_vacia_resource = resource_path('recursos/Estrella_vacia.png')
estrella_vacia = pygame.image.load(estrella_vacia_resource)
estrella_completa_resource = resource_path('recursos/Estrella_completa.png')
estrella_completa = pygame.image.load(estrella_completa_resource)
estrella_pro_resource = resource_path('recursos/Estrella_pro.png')
estrella_pro = pygame.image.load(estrella_pro_resource)
estrella_vacia_chica_resource = resource_path('recursos/Estrella_vacia_chica.png')
estrella_vacia_chica = pygame.image.load(estrella_vacia_chica_resource)
estrella_completa_chica_resource = resource_path('recursos/Estrella_completa_chica.png')
estrella_completa_chica = pygame.image.load(estrella_completa_chica_resource)
estrella_pro_chica_resource = resource_path('recursos/Estrella_pro_chica.png')
estrella_pro_chica = pygame.image.load(estrella_pro_chica_resource)

def guardar_datos(datos):
    fichero_binario = open("recursos/Puntajes","wb")
    pickle.dump(datos, fichero_binario)
    fichero_binario.close()
    
def abrir_datos():
    fichero = open("recursos/Puntajes","rb")
    datos = pickle.load(fichero)
    return datos
    

def GeneradorGraficas(dificultad,fs):
#Nivel 1 de dificultad. En este nivel solamente habrán movimientos con 
#velocidad constante.
    t_f = 5  
    N = fs*t_f
    t = np.linspace(0,t_f,N)
    if dificultad == 1:
        x = []
        x_i = np.random.random()*98 + 2
        x = MRU_x(t,x,x_i)
        t = np.linspace(5,t_f+5,N)
        return t,x
   #Nivel 2 de dificultad. En este nivel solamente hay movimientos con
#aceleración constante. Hay 4 tipos de movimientos equiprobables, en
#función del signo de la aceleración y el de la velocidad inicial.
    if dificultad ==2:
        x = []
        movimiento = random.choice(["a y v pos","a y v neg",
                                    "a pos y v neg","a neg y v pos"])
        if movimiento == "a y v pos" or movimiento == "a neg y v pos":
            x_i = np.random.random()*18 + 2
            x = MRUA_x(movimiento,t,x,x_i)
            t = np.linspace(5,t_f+5,N)
            return t,x
        elif movimiento == "a y v neg" or movimiento == "a pos y v neg":
            #Para este movimiento se comenzará quieto, von v_i=0
            x_i = np.random.random()*20 + 80
            x = MRUA_x(movimiento,t,x,x_i)
            t = np.linspace(5,t_f+5,N)
            return t,x
#Nivel 3 de dificultad. Se compone por 3 movimientos seguidos de dificultad
#1, 2 o por reposo. Se recupera de cada parte la posición final para "pegar"
#los movimientos sin saltos.
    if dificultad == 3:
        x = []
        mov = random.choice(["reposo","MRU","MRUA"])
        if mov == "reposo":
            x_i = np.random.random()*98 + 2
            x = reposo_x(t,x,x_i)
        elif mov == "MRU":
            t,x = GeneradorGraficas(1,fs)
        elif mov == "MRUA":
            t,x = GeneradorGraficas(2,fs)
        for k in range(2):
            x_i = x[len(x)-1]
            t = np.linspace(0,t_f,N)
            if mov == "reposo":
                mov = random.choice(["MRU","MRUA"])
            elif mov == "MRU":
                mov = random.choice(["reposo","MRUA"])
            elif mov == "MRUA":
                mov = random.choice(["reposo","MRU"])
            if mov == "reposo":
                x = reposo_x(t,x,x_i)
            elif mov == "MRU":
                x = MRU_x(t,x,x_i)
            elif mov == "MRUA":
                if x_i <= 50:
                    movimiento = random.choice(["a y v pos","a neg y v pos"])
                    x = MRUA_x(movimiento,t,x,x_i)
                else:
                    movimiento = random.choice(["a y v neg","a pos y v neg"])
                    x = MRUA_x(movimiento,t,x,x_i)
        t_f = 15
        N = t_f*fs
        t = np.linspace(5,t_f+5,N)
        return t,x
                

def MRU_x(t,x,x_i):
    t_f = t[len(t)-1]
    if x_i < 50:
        x_f = np.random.random()*25 + 75
    else:
        x_f = np.random.random()*23 + 2
    v = (x_f - x_i)/t_f
    for k in range(len(t)):
        x.append(x_i + v*t[k])
    return x
    

def MRUA_x(movimiento,t,x,x_i):
    t_f = t[len(t)-1]
    if movimiento == "a y v pos":
        #Para este movimiento se comenzará quieto, con v_i=0
        x_f = np.random.random()*20 + 80
        a = (x_f-x_i)*2/t_f**2
        for k in range(len(t)):
            x.append(x_i + 0.5*a*t[k]**2)
        return x
    elif movimiento == "a y v neg":
        #Para este movimiento se comenzará quieto, von v_i=0
        x_f = np.random.random()*20 + 2
        a = (x_f-x_i)*2/t_f**2
        for k in range(len(t)):
            x.append(x_i + 0.5*a*t[k]**2)
        return x
    elif movimiento == "a pos y v neg":
        #Movimiento con forma de U
        v_i = -np.random.random()*10 - 20
        a = -2*v_i/t_f #Para hacer v=0 en t_f/2
        for k in range(len(t)):
           x.append(x_i+v_i*t[k]+0.5*a*t[k]**2)
        return x
    elif movimiento == "a neg y v pos":
        #U invertida
        v_i = np.random.random()*10 + 20
        a = -2*v_i/t_f #Para hacer v=0 en t_f/2
        for k in range(len(t)):
            x.append(x_i+v_i*t[k]+0.5*a*t[k]**2)
        return x
    

    
def reposo_x(t,x,x_i):
    for k in range(len(t)):
        x.append(x_i)
    return x


def Puntaje(t,x,t_sensor,x_sensor):
    distancia = 0 
    j = 0
    n = 0
    i = 0
    while i < len(t_sensor):
        while t_sensor[i] < 5:
            i += 1
        while t_sensor[i] > t[j]:
            j += 1
        distancia += (x_sensor[i]-x[j])**2
        n += 1
        i += 1
    distancia = sqrt(distancia/n)
    if distancia < 1.5:
        puntaje = 4
    elif 1.5 < distancia < 3.5:
        puntaje = 3
    elif 3.5 < distancia < 6:
        puntaje = 2
    elif 6 < distancia < 10:
        puntaje = 1
    else:
        puntaje = 0
    distancia = int(distancia*100)/100
    return puntaje, distancia



def player(x,y):
    screen.blit(playerImg,(x,y))
    
def simulacion(x,y):
    screen.blit(simulacionImg, (x,y))
    
def textos_dificultad(datos):
    nombre = datos[0]
    nombre = nombre[1]
    inicio_text = font_inicio.render("SELECCIONA UN NIVEL DE DIFICULTAD", True, (255,255,255))
    screen.blit(inicio_text,(90,220))
    screen.blit(fondo_nivel,(95,310))
    facil_text = font_nivel.render("FÁCIL", True, (255,255,255))
    screen.blit(facil_text, (125,317))
    screen.blit(fondo_nivel,(330,310))
    medio_text = font_nivel.render("MEDIO", True, (255,255,255))
    screen.blit(medio_text, (355,317))
    dificil_text = font_nivel.render("DIFÍCIL", True, (255,255,255))
    screen.blit(fondo_nivel,(565,310))
    screen.blit(dificil_text, (590,317))
    nombre_text = font_inicio.render("BIENVENID@ "+nombre, True, (255,255,255))
    screen.blit(nombre_text,(200,125))

def textos_finalizo():
    simulacion_text = font_terminado.render("VER SIMULACIÓN", True, (255,255,255))
    intentar_nuevamente_text = font_terminado.render("VOLVER A INTENTAR", True, (255,255,255))
    graficar_velocidad_text = font_terminado.render("GRAFICAR V=f(t)", True, (255,255,255))
    volver_text = font_terminado.render("VOLVER AL MENÚ", True, (255,255,255))
    #Simulacion
    screen.blit(fondo_terminado,(500,30))
    screen.blit(simulacion_text, (525,42))
    #Volver a intentar
    screen.blit(fondo_terminado,(500,120))
    screen.blit(intentar_nuevamente_text, (508,132))
    #Graficar velocidad
    screen.blit(fondo_terminado,(500,210))
    screen.blit(graficar_velocidad_text,(520,222))
    #Volver al menú
    screen.blit(fondo_terminado, (500,300))
    screen.blit(volver_text, (525,312))



def estrellas(puntaje,distancia):
    if puntaje == 0:
        screen.blit(estrella_vacia,(150,375))
        screen.blit(estrella_vacia,(325,375))
        screen.blit(estrella_vacia,(500,375))
    if puntaje == 1:
        screen.blit(estrella_completa,(150,375))
        screen.blit(estrella_vacia,(325,375))
        screen.blit(estrella_vacia,(500,375))
    if puntaje == 2:
        screen.blit(estrella_completa,(150,375))
        screen.blit(estrella_completa,(325,375))
        screen.blit(estrella_vacia,(500,375))
    if puntaje == 3:
        screen.blit(estrella_completa,(150,375))
        screen.blit(estrella_completa,(325,375))
        screen.blit(estrella_completa,(500,375))
    if puntaje == 4:
        screen.blit(estrella_pro,(150,375))
        screen.blit(estrella_pro,(325,375))
        screen.blit(estrella_pro,(500,375))
    distancia_text = font_inicio.render("DISTANCIA MEDIA: "+str(distancia)+"m",True, (255,255,255))
    screen.blit(distancia_text,(210,535))

def estrellas_chicas(datos):
    puntaje_facil = datos[1]
    puntaje_facil = puntaje_facil[1]
    puntaje_medio = datos[3]
    puntaje_medio = puntaje_medio[1]
    puntaje_dificil = datos[5]
    puntaje_dificil = puntaje_dificil[1]
    estrellas_chicas_img(puntaje_facil,117)
    estrellas_chicas_img(puntaje_medio,352)
    estrellas_chicas_img(puntaje_dificil,587)


def estrellas_chicas_img(puntaje,x_primera_estrella):
    if puntaje == 0:
        screen.blit(estrella_vacia_chica,(x_primera_estrella,360))
        screen.blit(estrella_vacia_chica,(x_primera_estrella+35,360))
        screen.blit(estrella_vacia_chica,(x_primera_estrella+70,360))
    if puntaje == 1:
        screen.blit(estrella_completa_chica,(x_primera_estrella,360))
        screen.blit(estrella_vacia_chica,(x_primera_estrella+35,360))
        screen.blit(estrella_vacia_chica,(x_primera_estrella+70,360))
    if puntaje == 2:
        screen.blit(estrella_completa_chica,(x_primera_estrella,360))
        screen.blit(estrella_completa_chica,(x_primera_estrella+35,360))
        screen.blit(estrella_vacia_chica,(x_primera_estrella+70,360))
    if puntaje == 3:
        screen.blit(estrella_completa_chica,(x_primera_estrella,360))
        screen.blit(estrella_completa_chica,(x_primera_estrella+35,360))
        screen.blit(estrella_completa_chica,(x_primera_estrella+70,360))
    if puntaje == 4:
        screen.blit(estrella_pro_chica,(x_primera_estrella,360))
        screen.blit(estrella_pro_chica,(x_primera_estrella+35,360))
        screen.blit(estrella_pro_chica,(x_primera_estrella+70,360))
        


def graficaImg(t,x):
    fig = pylab.figure(figsize=[6,2.85],
                           dpi = 133)
    ax = fig.gca()
    ax.plot(t,x)
    ax.set_title("$x = f(t)$",fontsize=14)
    ax.set_xlabel("$t(s)$",fontsize=12)
    ax.set_ylabel("$x(m)$",fontsize=12)
    plt.xlim([0,t[len(t)-1]])
    plt.ylim([0,max(x)+10])
    ax.grid(True)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    ax.set_aspect(0.03)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()    
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    plt.close()
    return surf


def graficaImg_tiemporeal(t,x,t_mouse,x_mouse):
    fig = pylab.figure(figsize=[6,2.85],
                           dpi = 133)
    ax = fig.gca()
    ax.plot(t,x,t_mouse,x_mouse)
    ax.set_title("$x = f(t)$",fontsize=14)
    ax.set_xlabel("$t(s)$",fontsize=12)
    ax.set_ylabel("$x(m)$",fontsize=12)
    plt.xlim([0,t[len(t)-1]])
    plt.ylim([0,max(x)+10])
    ax.grid(True)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    ax.set_aspect(0.03)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()    
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    plt.close()
    return surf


def graficaImg_multiple(t,x,t_mouse,x_mouse):
    fig = pylab.figure(figsize=[6,5],
                           dpi = 75)
    ax = fig.gca()
    ax.plot(t,x,t_mouse,x_mouse)
    ax.set_title("$x = f(t)$",fontsize=14)
    ax.set_xlabel("$t(s)$",fontsize=12)
    ax.set_ylabel("$x(m)$",fontsize=12)
    plt.xlim([5,t[len(t)-1]])
    plt.ylim([0,max(x)+10])
    ax.grid(True)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    ax.set_aspect(0.03)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()    
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    plt.close()
    return surf


def graficaImg_simulacion(t_simulacion,x_simulacion,t_mouse_simulacion,x_mouse_simulacion,t_f,x_max):
    fig = pylab.figure(figsize=[6,2.85],
                           dpi = 133)
    ax = fig.gca()
    ax.plot(t_simulacion,x_simulacion,t_mouse_simulacion,x_mouse_simulacion)
    ax.set_title("$x = f(t)$",fontsize=14)
    ax.set_xlabel("$t(s)$",fontsize=12)
    ax.set_ylabel("$x(m)$",fontsize=12)
    plt.xlim([0,t_f])
    plt.ylim([0,x_max+10])
    ax.grid(True)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    ax.set_aspect(0.03)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()    
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    plt.close()
    return surf

def grafica_con_velocidad(t,x,t_mouse,x_mouse,t_v,v,t_v_mouse,v_mouse):
    fig, axs = plt.subplots(2,1,
            figsize=[8,5],dpi = 100)
    axs[0].plot(t,x,t_mouse,x_mouse)
    axs[0].set_xlabel("$t(s)$",fontsize=12)
    axs[0].set_ylabel("$x(m)$",fontsize=12)
    axs[0].set_xlim([5,t[-1]])
    axs[0].set_ylim([0,max(x)+10])
    axs[0].grid(True)
    axs[0].xaxis.set_minor_locator(AutoMinorLocator())
    axs[0].yaxis.set_minor_locator(AutoMinorLocator())
    axs[0].tick_params(which='major', width=2)
    axs[0].tick_params(which='minor', width=1.2)
    axs[0].tick_params(which='major', length=9)
    axs[0].tick_params(which='minor', length=4)
 #   ax1.set_aspect(0.04)
    
    axs[1].plot(t_v,v,t_v_mouse,v_mouse)
    axs[1].set_xlabel("$t(s)$",fontsize=12)
    axs[1].set_ylabel("$v(m/s)$",fontsize=12)
    axs[1].set_xlim([5,t_v[-1]])
    axs[1].set_ylim([-40,40])
    axs[1].grid(True)
    axs[1].xaxis.set_minor_locator(AutoMinorLocator())
    axs[1].yaxis.set_minor_locator(AutoMinorLocator())
    axs[1].tick_params(which='major', width=2)
    axs[1].tick_params(which='minor', width=1.2)
    axs[1].tick_params(which='major', length=9)
    axs[1].tick_params(which='minor', length=4)
#    ax2.set_aspect(0.04)
    
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()    
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    screen.blit(surf,(0,0))
    plt.close()

    volver_text = font_nivel.render("VOLVER", True, (255,255,255))
    screen.blit(fondo_nivel,(330,525))
    screen.blit(volver_text,(345,532))
try:
    datos = abrir_datos()
except:
    estado_datos = "en espera"
    nombre = ""
    caracter = ""

running = True
while running:
    screen.blit(background,(0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        if pygame.mouse.get_pressed()[0]:
            mouseX = pygame.mouse.get_pos()[0]
            mouseY = pygame.mouse.get_pos()[1]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                caracter = "delete"
            else:
                caracter = event.unicode
    #Creo datos del jugador        
    if estado_datos == "en espera":
        if caracter == "delete":
            nombre = nombre[0:-1]
        else:
            nombre += caracter
        nombre_text = font_inicio.render("INGRESE SU NOMBRE:" + nombre,True,(255,255,255))
        screen.blit(nombre_text,(90,200))
        caracter = ""
        continuar_text = font_nivel.render("CONTINUAR", True, (255,255,255))
        screen.blit(fondo_terminado,(275,325))
        screen.blit(continuar_text,(310,332))
        if 275 < mouseX < 525 and 325 < mouseY < 375:
            datos = [("Nombre:",nombre),
            ("Puntaje fácil:",0),
            ("Distancia fácil:",1000),
            ("Puntaje medio:",0),
            ("Distancia medio:",1000),
            ("Puntaje difícil:",0),
            ("Distancia difícil:",1000),
            ("Cantidad de partidas",0)]
            guardar_datos(datos)
            estado_datos = 0
            mouseX = 0

    #Selector de dificultad        
    if dificultad == 0 and estado_datos != "en espera":
        textos_dificultad(datos)
        estrellas_chicas(datos)
        if 95 < mouseX < 235 and 310 < mouseY < 360:
            dificultad = 1
            aux = mouseX
            t,x = GeneradorGraficas(dificultad,fs)
            surf = graficaImg(t,x)
            estado_grafica = "generada"
        if 330 < mouseX < 470 and 310 < mouseY < 360:
            dificultad = 2
            aux = mouseX
            t,x = GeneradorGraficas(dificultad,fs)
            surf = graficaImg(t,x)
            estado_grafica = "generada"
        if 565 < mouseX < 705 and 310 < mouseY < 360:
            dificultad = 3
            aux = mouseX 
            t,x = GeneradorGraficas(dificultad,fs)
            surf = graficaImg(t,x)
            estado_grafica = "generada"     

    #Espera para comenzar a jugar
    if estado_grafica == "generada" and estado_jugador == "en espera":
        screen.blit(surf, (0,0))
        inicio_text = font_inicio.render("PRESIONA EL CLICK PARA COMENZAR", True, (255,255,255))
        screen.blit(inicio_text,(120,400))
        if mouseX != aux:
            estado_jugador = "ready"
            t_mouse = []
            x_mouse = []
            t_f = t[len(t)-1]
            t1 = time.time()

    #Juego
    if estado_jugador == "ready":        
        if 0 < (pygame.mouse.get_pos()[0]-80)/7+5 < 100:
            playerX = pygame.mouse.get_pos()[0] - 80
        elif (pygame.mouse.get_pos()[0]-80)/7+5 < 0:
            playerX = -35
        else:
            playerX = 665
        t_mouse.append(time.time()-t1)
        x_mouse.append(playerX/7 + 5)
        surf = graficaImg_tiemporeal(t, x, t_mouse, x_mouse)
        screen.blit(surf, (0,0))
        x_text = int(x_mouse[-1]*100)/100
        text_x = font_nivel.render("x="+str(x_text)+"m",True,(0,0,0))
        screen.blit(text_x,(10,10))
        try:
            v_text = (x_mouse[-1]-x_mouse[-2])/(t_mouse[-1]-t_mouse[-2])
            v_text = int(v_text*100)/100
            text_v = font_nivel.render("v="+str(v_text)+"m/s",True,(0,0,0))
            screen.blit(text_v,(10,40))
        except:
            pass
        if time.time()-t1 >= t_f:
            estado_jugador = "finalizo"
            mouseX = 0
            surf = graficaImg_multiple(t, x, t_mouse, x_mouse)
            puntaje, distancia = Puntaje(t,x,t_mouse,x_mouse)
            n = datos[7]
            n = n[1]
            datos[7] = ("Cantidad de partidas:",n+1)
            distancia_facil = datos[2]
            distancia_facil = distancia_facil[1]
            distancia_medio = datos[4]
            distancia_medio = distancia_medio[1]
            distancia_dificil = datos[6]
            distancia_dificil = distancia_dificil[1]
            if dificultad == 1 and distancia < distancia_facil:
                datos[1] = ("Puntaje fácil:",puntaje)
                datos[2] = ("Distancia fácil:",distancia)
            elif dificultad == 2 and distancia < distancia_medio:
                datos[3] = ("Puntaje medio:",puntaje)
                datos[4] = ("Distancia medio:",distancia)
            elif dificultad == 3 and distancia < distancia_dificil:
                datos[5] = ("Puntaje dificil:",puntaje)
                datos[6] = ("Distancia difícil:",distancia)
            guardar_datos(datos)


    #Post juego
    if estado_jugador == "finalizo":
        screen.blit(surf, (0,0))
        playerX = 1000
        estrellas(puntaje,distancia)
        textos_finalizo()
        #Eleccion simulacion
        if 500 < mouseX < 750 and 30 < mouseY < 80:
            estado_jugador = "Ver simulacion"
            k_simulacion = 1
            k_mouse = 1
            simulacionX = x_mouse[k_mouse]
            playerX = x[k_simulacion]
            t1 = time.time()
            t_simulacion = [t[0]]
            x_simulacion = [x[0]]
            t_mouse_simulacion = [t_mouse[0]]
            x_mouse_simulacion = [x_mouse[0]]
            x_max = max(x)
        #Eleccion jugar de nuevo
        if 500 < mouseX < 750 and 120 < mouseY < 170:
            estado_jugador = "en espera"
            aux = mouseX
            playerX = 10
            surf = graficaImg(t, x)
        #Eleccion ver velocidad
        if 500< mouseX < 750 and 210 < mouseY < 260:
            v = []
            t_v = []
            k = 4
            while k < len(t):
                v.append((x[k]-x[k-1])/(t[k]-t[k-1]))
                t_v.append(t[k])
                k += 1
            v_mouse = []
            t_v_mouse = []
            k = 4
            while k < len(t_mouse):
                v_mouse.append((x_mouse[k]-x_mouse[k-4])/(t_mouse[k]-t_mouse[k-4]))
                t_v_mouse.append(t_mouse[k-2])
                k += 1
            mouseX = 0
            estado_jugador = "Ver velocidad"
        #Eleccion volver al menú
        if 500 < mouseX < 750 and 300 < mouseY < 350:
            dificultad = 0
            estado_grafica = "ready"
            estado_jugador = "en espera"
            playerX = 10
            mouseX = 0
    
    #Simulacion
    if estado_jugador == "Ver simulacion":
        if time.time() - t1 >= t_mouse[k_mouse] and k_mouse < len(t_mouse)-1:
            k_mouse += 1
            t_mouse_simulacion.append(t_mouse[k_mouse])
            x_mouse_simulacion.append(x_mouse[k_mouse])
        if time.time() - t1 >= t[k_simulacion] and k_simulacion < len(t)-1:
            k_simulacion += 1
            t_simulacion.append(t[k_simulacion])
            x_simulacion.append(x[k_simulacion])
        surf = graficaImg_simulacion(t_simulacion, x_simulacion, 
                                     t_mouse_simulacion, x_mouse_simulacion,t_f,x_max)
        screen.blit(surf, (0,0))
        playerX = x_mouse_simulacion[len(x_mouse_simulacion)-1]*7
        simulacionX = x_simulacion[len(x_simulacion)-1]*7
        simulacion(simulacionX,simulacionY)
        if k_simulacion >= len(t)-1 and k_mouse >= len(t_mouse)-1:
            surf = graficaImg_multiple(t, x, t_mouse, x_mouse)
            mouseX = 0
            estado_jugador = "finalizo"

    #Ver velocidad
    if estado_jugador == "Ver velocidad":
        grafica_con_velocidad(t, x, t_mouse, x_mouse, t_v, v, t_v_mouse, v_mouse)
        if 330 < mouseX < 470 and 525 < mouseY < 575:
            estado_jugador = "finalizo"

    player(playerX,playerY)
    pygame.display.update()
    