# BAMM
Robot delta interactivo capaz de jugar al mastermind.

## Requerimientos
- Software:
  - Python 2.7
  - Librerías de Python:
    - Pydynamixel (https://github.com/iandanforth/pydynamixel)
    - PySerial (http://pyserial.sourceforge.net/)
    - Kivy (versión 1.9.1+) (https://kivy.org)
- Hardware:
  - Arduino con Motor Shield (se ha usado Arduino Uno)
  - 3 servo motores (se ha usado AX-12+)
  - Módulo USB2Dynamixel para conectar servo motores al ordenador
  - Placa de fibra de vidrio con 7 pulsadores

## Manual de usuario

#### Arranque

1. Descargar todos los archivos de python y el programa de arduino
2. Conectar arduino y USB2Dynamixel al ordenador
3. Enviar el programa pulsadores.ino al arduino
4. Ejecutar donde has descargado los archivos

    $ sudo python deltaApp.py

5. Si es la primera vez que se inicia, pedirá buscar los Servos. En tal caso, hay que seguir las intrucciones referentes a settings.yaml
6. Ya se puede jugar. Es recomendable leer previamente las intrucciones de la interfaz

#### settings.yaml

#### ultimoCodigo

#### Interfaz

## Documentación
#### robot.py

###### (class) MastermindDirecte()
- (method) colorToCode(color)
  - Asigna un número correspondiente al color
  - Parámetros: (str) color
  - Return type: (int)
- (method) codeToColor(code)
  - Convierte el código numérico a una combinación de colores
  - Parámetros: (int) code
  - Return type: (str)
- (method) generate_initial_pool(choices, holes):
  - Crea una lista que contiene todas las posibles combinaciones numéricas en tuples
  - Parámetros: (int) choices, (int) holes
  - Return type: list
- (method) buscarRojas()
  - Busca cuantas 'rojas' hay en el código propuesto, es decir, bolitas del color correcto en el sitio correcto
  - Parámetros: None
  - Return type: None
- (method) buscarBlancas()
  - Busca cuentas 'blancas' hay en el código propuesto, es decir, bolitas del color correcto en el sitio incorrecto, sin repetir bolitas
  - Parámetros: None
  - Return type: None
- (method) get_feedback()
  - Devuelve una respuesta en forma de feedback de cuantas rojas y blancas se han calculado
  - Parámetros: None
  - Return type: (FeedBack)
- (method) is_match(feedback)
  - Compara True or False si los rojos y los blancos de nuestras suposiciones coinciden con los de usuario, que son feedback
  - Parámetros: (FeedBack) feedback
  - Return type: (bool)
- (method) filter_pool(feedback)
  - Filtra todas las combinaciones posibiles restantes y genera una nueva lista únicamente con las combinaciones que cumplen con el     feedback del usuario, sin contemplar el último codigo propuesto por el programa al usuario
  - Parámetros: (FeedBack) feedback
  - Return type: (tup)
- (method) make_guess(feedback, initime)
  - Renueva el código propuesto por el programa al usuario en base a su interacción. El nuevo código propuesto es aquel que consigue    reducir al máximo la lista de combinaciones posibles restantes dentro de un tiempo de 5 segundos
  - Parámetros: (FeedBack) feedback, (Time) initime
  - Return type: (tup)
- (method) play()
  - Juego por línea de comandos de terminal. El usuario se piensa un código y el programa ha de adivinarlo.
  - Parámetros: None
  - Return type: None

###### (class) MastermindInvers
- (method) colorToCode(color)
  - Asigna un número correspondiente al color
  - Parámetros: (str) color
  - Return type: (int)
- (method) codeToColor(code)
  - Convierte el código numérico a una combinación de colores
  - Parámetros: (int) code
  - Return type: (str)
- (method) buscarRojas()
  - Busca cuantas 'rojas' hay en el código propuesto, es decir, bolitas del color correcto en el sitio correcto
  - Parámetros: None
  - Return type: None
- (method) buscarBlancas()
  - Busca cuentas 'blancas' hay en el código propuesto, es decir, bolitas del color correcto en el sitio incorrecto, sin repetir bolitas
  - Parámetros: None
  - Return type: None
- (method) play()
  - Juego por línea de comandos de terminal. El programa se piensa un código aleatorio y el usuario ha de adivinarlo
  - Parámetros: None
  - Return type: None

###### (class) Robot
- (method) buscarServos()
  - Busca los servos, los inicia e inicializa el electroimán. La primera vez que se ejecuta guarda la configuración en un archivo settins.yaml para futuros usos, así no ha de volver a buscar y sólo carga la última configuración
  - Parámetros: None
  - Return type: None
- (method) validateInput(userInput, rangeMin, rangeMax)
  - Asegura que el valor introducido es un entero dentro de un intervalo
  - Parámetros: (any) userInput, (int) rangeMin, (int) rangeMax
  - Return type: (int) or None
- (method) getCurrentPosition()
  - Devuelve la posición actual en base [x,y,z] en la que se sitúa el robot
  - Parámetros: None
  - Return type: (list)
- (method) mover_robot(destination)
  - Mueve al robot al destino asignado por intervalos de diferentes velocidades para evitar movimientos bruscos
  - Parámetros: (tup) or (list) destination
  - Return type: None
- (method) poner_bolita(huecoColor, huecoRobot)
  - 
      1. El robot se mueve al hueco de color correspondiente
      2. Se enciende el electroimán y se baja el robot para coger al bolita
      3. Se vuelve a subir el robot
      4. Se mueve el robot al hueco del robot correspondiente
      5. Se baja el robot para dejar al bolita y se apaga el electroimán
      6. Se vuelve a subir el robot
  - Parámetros: (list) huecoColor, (list) huecoRobot
  - Return type: None
- (method) quitar_bolita(huecoColor, huecoRobot)
  - 
      1. El robot se mueve al hueco del robot correspondiente
      2. Se enciende el electroimán y se baja el robot para coger al bolita
      3. Se vuelve a subir el robot
      4. Se mueve el robot al hueco de color correspondiente
      5. Se baja el robot para dejar al bolita y se apaga el electroimán
      6. Se vuelve a subir el robot
  - Parámetros: (list) huecoColor, (list) huecoRobot
  - Return type: None
- (method) poner_bolitas(guess, previousGuess)
  - 
      1. Mira si huecoRobot[0] está vacío; si lo está, rellena el huecoRobot[0] y lo marca como ocupado
      2. Mira si huecoRobot[1] está vacío; si lo está, rellena el huecoRobot[1] y lo marca como ocupado
      3. Mira si huecoRobot[2] está vacío; si lo está, rellena el huecoRobot[2] y lo marca como ocupado
      4. Mira si huecoRobot[3] está vacío; si lo está, rellena el huecoRobot[3] y lo marca como ocupado
      5. Mira si huecoRobot[4] está vacío; si lo está, rellena el huecoRobot[4] y lo marca como ocupado
  - Parámetros: (list) guess, (list) previousGuess
  - Return type: None
- (method) quitar_bolitas(previousGuess, guess)
  - 
      1. Mira si huecoRobot[0] está vacío; si no lo está, quita la bolita | si la bolita ya es correcta, no hace nada
      2. Mira si huecoRobot[1] está vacío; si no lo está, quita la bolita | si la bolita ya es correcta, no hace nada
      3. Mira si huecoRobot[2] está vacío; si no lo está, quita la bolita | si la bolita ya es correcta, no hace nada
      4. Mira si huecoRobot[3] está vacío; si no lo está, quita la bolita | si la bolita ya es correcta, no hace nada
      5. Mira si huecoRobot[4] está vacío; si no lo está, quita la bolita | si la bolita ya es correcta, no hace nada
  - Parámetros: (list) previousGuess, (list) guess
  - Return type: None
- (method) celebrar()
  - Para celebrar que el robot ha ganado la partida, recorre una circumferencia en un plano
  - Parámetros: None
  - Return type: None

###### (class) Arduino
- (method) encender()
  - Activa el bloque de código 1 del arduino para encender el electroimán
  - Parámetros: None
  - Return type: None
- (method) apagar()
  - Activa el bloque de código 0 del arduino para apagar el electroimán
  - Parámetros: None
  - Return type: None
- (method) codigo2()
  - Activa el bloque de código 2 del arduino para escuchar la respuesta de los pulsadores en modo directo
  - Parámetros: None
  - Return type: (list)
- (method) codigo5()
  - Activa el bloque de código 3 del arduino para escuchar la respuesta de los pulsadores en modo inverso
  - Parámetros: None
  - Return type: (list)

###### (class) JuegoDirecto
- (method) play()
  - Juego por línea de comandos de terminal. El robot responde a la interacción del usuario. El usuario se piensa un código y el robot ha de adivinarlo
  - Parámetros: None
  - Return type: None

#### cinematica.py
- (function) directa(theta1, theta2, theta3)
  - Devuelve la posición del robot en base [x,y,x] respecto de los valores del ángulo de las brazos. Ángulo positivo hacia arriba, ángulo negativo hacia abajo
  - Parámetros: (float) theta1, (float) theta2, (float) theta3
  - Return type: (list)
- (function) angulos(x0,y0,z0)
  - Calcula el valor del ángulo de un brazo respecto del valor de la posición
  - Parámetros: (float) x0, (float) y0, (float) z0
  - Return type: (float)
- (function) inversa(x0,y0,z0)
  - Transforma con rotaciones los cálculos hechos para el valor del ángulo de un brazo y devuelve el ángulo de cada brazo
  - Parámetros: (float) x0, (float) y0, (float) z0
  - Return type: (list)
- (function) anguloaParametro(angulo)
  - Convierte el valor del ángulo en un parámetro entero de 0 a 1023
  - Parámetros: (float) angulo
  - Return type: (int)
- (function) parametroaAngulo(parametro)
  - Convierte el parámetro en un valor del ángulo
  - Parámetros: (int) parametro
  - Return type: (float)

#### deltaApp.py
###### (class) Delta()
- (method) jugar_p_directo()
  - Empieza el juego directo con un primer movimiento. Si el checkbox está marcado, el programa carga la última configuración guardada y primero limpia el tablero y luego empieza. Continúa cada turno del juego, requiere la respuesta del usuario por pulsadores. Siempre guarda la última configuracion del robot para siguientes inicios después de cada movimiento
  - Parámetros: None
  - Return type: None
- (method) continuar_p_directo()
  - Función complementaria de jugar_p_directo() que permite avanzar de turno
  - Parámetros: None
  - Return type: None
- (method) empezar_i_directo():
  - Empieza el juego directo con un primer movimiento. Si el checkbox está marcado, el programa carga la última configuración guardada y primero limpia el tablero y luego empieza. Sólo puede jugarse vía interfaz.
  - Parámetros: None
  - Return type: None
- (method) continuar_i_directo()
  - Continúa un turno del juego directo, requiere la respuesta del usuario por texto de interfaz. Siempre guarda la última configuración del robot para siguientes inicios después de cada movimiento
  - Parámetros: None
  - Return type: None
- (method) jugar_p_inverso()
  - Empieza el juego inverso con un primer movimiento. Si el checkbox está marcado, el programa carga la última configuración guardada y primero limpia el tablero y luego empieza. Continúa cada turno del juego, requiere la respuesta del usuario por pulsadores. Siempre guarda la última configuracion del robot para siguientes inicios después de cada movimiento
  - Parámetros: None
  - Return type: None
- (method) continuar_p_inverso()
  - Función complementaria de jugar_p_inversp() que permite avanzar de turno
  - Parámetros: None
  - Return type: None
- (method) empezar_i_inverso()
  - Empieza el juego inverso con un primer movimiento. Si el checkbox está marcado, el programa carga la última configuración guardada y primero limpia el tablero y luego empieza. Sólo puede jugarse vía interfaz.
  - Parámetros: None
  - Return type: None
- (method) continuar_i_inverso()
  - Continúa un turno del juego inverso, requiere la respuesta del usuario por texto de interfaz. Siempre guarda la última configuración del robot para siguientes inicios después de cada movimiento
  - Parámetros: None
  - Return type: None
- (method) respuesta_d_arduino(dt)
  - Escucha  y devuelve la respuesta de los pulsadores en modo de juego directo
  - Parámetros: (float) dt
  - Return type: (bool)
- (method) respuesta_i_arduino(dt)
  - Escucha  y devuelve la respuesta de los pulsadores en modo de juego inverso
  - Parámetros: (float) dt
  - Return type: (bool)
- (method) esperar(dt)
  - Espera 1 segundo
  - Parámetros: (float) dt
  - Return type: None
- (method) on_checkbox_active(checkbox, value)
  - Mira si el checkbox está marcado
  - Parámetros: (CheckBox) checkbox, (bool) value
  - Return type: (bool)

###### (class) Inverso()
- (method) empezar()
  - Complementa la función empezar del juego inverso. Se piensa un código aleatorio, el cual el usuario ha de adivinar
  - Parámetros: None
  - Return type: None
- (method) continuar(guess)
  - Complementa la función continuar al siguiente turno del juego inverso. Calcula la respuesta del robot ante el código propuestp por el usuario
  - Parámetros: (list) guess
  - Return type: (tup)

