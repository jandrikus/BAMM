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
  - Placa de fibra de vídreo con 7 pulsadores

## Manual de usuario
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
- (method) def generate_initial_pool(choices, holes):
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
###### (class) Robot
###### (class) Arduino
###### (class) JuegoDirecto
