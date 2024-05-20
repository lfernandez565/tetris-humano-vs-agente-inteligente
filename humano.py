import sys, random # Importa los módulos sys para interactuar con el intérprete de Python y random para la generación de números aleatorios.

# Importaciones de PyQt5 para la interfaz gráfica de usuario (GUI):
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel # Componentes de la ventana y layout.
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal # Core de Qt para eventos y señales.
from PyQt5.QtGui import QPainter, QColor # Herramientas de pintura y color para la GUI.

# Importación del modelo de Tetris
from tetris_model import BOARD_DATA, Shape # BOARD_DATA maneja el estado del tablero de juego, Shape define las formas de los tetrominos.

class Tetris(QMainWindow):
    # Constructor de la clase Tetris.
    def __init__(self):
        super().__init__() # Inicializa la clase base QMainWindow.
        self.isStarted = False # Indica si el juego ha comenzado.
        self.isPaused = False # Indica si el juego está pausado.
        self.nextMove = None # Almacena el siguiente movimiento que se realizará.
        self.lastShape = Shape.shapeNone # Almacena la última forma de tetromino que se jugó.

        self.initUI() # Llama al método para inicializar la interfaz de usuario.

    # Definimos la configuración inicial de la interfaz de usuario (UI).
    def initUI(self):
        self.gridSize = 25 # Tamaño de la cuadrícula del tablero de Tetris.
        self.speed = 250 # Velocidad inicial del juego.

        self.timer = QBasicTimer()  # Temporizador para controlar la velocidad de caída de los tetrominos.
        self.setFocusPolicy(Qt.StrongFocus) # Establece la política de enfoque para capturar eventos de teclado.

        # Crea el tablero de Tetris y lo añade al layout.
        hLayout = QHBoxLayout()
        self.tboard = Board(self, self.gridSize)
        hLayout.addWidget(self.tboard)

        # Crea un panel lateral y lo añade al layout.
        self.sidePanel = SidePanel(self, self.gridSize)
        hLayout.addWidget(self.sidePanel)

        # Barra de estado para mostrar mensajes.
        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.start() # Inicia el juego.

        self.center() # Centra la ventana en la pantalla.
        self.setWindowTitle('Jugador Humano - Alumno: Luis David Fernández - C.I: 22.818.565') # Establece el título de la ventana.
        self.show() # Muestra la ventana.

        # Ajusta el tamaño fijo de la ventana basado en el ancho y alto de los componentes.
        self.setFixedSize(self.tboard.width() + self.sidePanel.width(),
                          self.sidePanel.height() + self.statusbar.height())

    # Esta función calcula el centro de la pantalla del usuario y mueve la ventana principal del juego de Tetris a esa posición central.
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    # Esta función se encarga de verificar si el juego está actualmente pausado y, de ser así, simplemente sale de la función sin realizar ninguna acción. 
    # Si el juego no está pausado, procede a establecer el estado del juego como iniciado, reinicia la puntuación a cero, y limpia el tablero de datos, 
    # lo que sugiere que elimina todas las piezas y posiblemente los rastros de juegos anteriores.
    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.tboard.score = 0
        BOARD_DATA.clear()

        self.tboard.msg2Statusbar.emit(str(self.tboard.score))

        BOARD_DATA.createNewPiece()
        self.timer.start(self.speed, self)


    # Esta función alterna entre pausar y reanudar el juego de Tetris. Si el juego está en curso, se detiene el temporizador y se muestra un mensaje de pausa 
    # en la barra de estado. Si el juego está pausado, se reinicia el temporizador para reanudar el juego.
    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.tboard.msg2Statusbar.emit("Pausa")
        else:
            self.timer.start(self.speed, self)

        self.updateWindow()

    # Esta función actualiza los componentes de la ventana del juego de Tetris, incluyendo el tablero principal y el panel lateral.
    def updateWindow(self):
        self.tboard.updateData()
        self.sidePanel.updateData()
        self.update()

    # Esta función se ejecuta cada vez que el temporizador del juego emite una señal. Maneja la lógica del juego,
    # como la caída de las piezas, las rotaciones y los movimientos laterales, y actualiza la ventana del juego.
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.nextMove:
                k = 0
                while BOARD_DATA.currentDirection != self.nextMove[0] and k < 4:
                    BOARD_DATA.rotateRight() # Rota la pieza hacia la derecha.
                    k += 1
                k = 0
                while BOARD_DATA.currentX != self.nextMove[1] and k < 5:
                    if BOARD_DATA.currentX > self.nextMove[1]:
                        BOARD_DATA.moveLeft() # Mueve la pieza hacia la izquierda.
                    elif BOARD_DATA.currentX < self.nextMove[1]:
                        BOARD_DATA.moveRight() # Mueve la pieza hacia la derecha.
                    k += 1
            lines = BOARD_DATA.moveDown() # Hace que la pieza actual caiga una posición hacia abajo.
            self.tboard.score += lines
            if self.lastShape != BOARD_DATA.currentShape:
                self.nextMove = None
                self.lastShape = BOARD_DATA.currentShape
            self.updateWindow() # Actualiza la ventana del juego para reflejar los cambios.
        else:
            super(Tetris, self).timerEvent(event) # Llama al controlador de temporizador de la clase base.


    # Esta función responde a las pulsaciones de teclas del Humano durante el juego, permitiendo pausar el juego y controlar las piezas de Tetris.
    def keyPressEvent(self, event):
        if not self.isStarted or BOARD_DATA.currentShape == Shape.shapeNone:
            super(Tetris, self).keyPressEvent(event)
            return

        key = event.key()
        
        if key == Qt.Key_P:
            self.pause()
            return
            
        if self.isPaused:
            return
        elif key == Qt.Key_Left:
            BOARD_DATA.moveLeft()
        elif key == Qt.Key_Right:
            BOARD_DATA.moveRight()
        elif key == Qt.Key_Up:
            BOARD_DATA.rotateLeft()
        elif key == Qt.Key_Space:
            self.tboard.score += BOARD_DATA.dropDown()
        else:
            super(Tetris, self).keyPressEvent(event)

        self.updateWindow()


# Las funciones drawSquare y drawSquare1 se utilizan para dibujar un cuadrado en una ubicación específica. El cuadrado se rellena con un color según el valor proporcionado.
# Se dibujan bordes claros y oscuros para darle una apariencia tridimensional.
def drawSquare(painter, x, y, val, s):
    colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

    if val == 0:
        return

    color = QColor(colorTable[val])
    painter.fillRect(int(x + 1), int(y + 1), int(s - 2), int(s - 2), color)

    painter.setPen(color.lighter())
    painter.drawLine(int(x), int(y + s - 1), int(x), int(y))
    painter.drawLine(int(x), int(y), int(x + s - 1), int(y))

    painter.setPen(color.darker())
    painter.drawLine(int(x + 1), int(y + s - 1), int(x + s - 1), int(y + s - 1))
    painter.drawLine(int(x + s - 1), int(y + s - 1), int(x + s - 1), int(y + 1))


def drawSquare1(painter, x, y, val, s):
    colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

    if val == 0:
        return

    color = QColor(colorTable[val])
    painter.fillRect(int(x + 1), int(y + 1), int(s - 2), int(s - 2), color)

    painter.setPen(color.lighter())
    painter.drawLine(int(x), int(y + s - 1), int(x), int(y))
    painter.drawLine(int(x), int(y), int(x + s - 1), int(y))

    painter.setPen(color.darker())
    painter.drawLine(int(x + 1), int(y + s - 1), int(x + s - 1), int(y + s - 1))
    painter.drawLine(int(x + s - 1), int(y + s - 1), int(x + s - 1), int(y + 1))


# Representa un panel lateral en la interfaz gráfica del juego de Tetris. Este panel muestra la siguiente pieza que aparecerá en el tablero.
class SidePanel(QFrame):
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * BOARD_DATA.height)
        self.move(gridSize * BOARD_DATA.width, 0)
        self.gridSize = gridSize

    def updateData(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        minX, maxX, minY, maxY = BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 3 * self.gridSize
        dx = (self.width() - (maxX - minX) * self.gridSize) / 2

        val = BOARD_DATA.nextShape.shape
        for x, y in BOARD_DATA.nextShape.getCoords(0, 0, -minY):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)


class SidePanel1(QFrame):
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * BOARD_DATA.height)
        self.move(gridSize * BOARD_DATA.width, 0)
        self.gridSize = gridSize

    def updateData(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        minX, maxX, minY, maxY = BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 3 * self.gridSize
        dx = (self.width() - (maxX - minX) * self.gridSize) / 2

        val = BOARD_DATA.nextShape.shape
        for x, y in BOARD_DATA.nextShape.getCoords(0, 0, -minY):
            drawSquare1(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)


# fundamental para representar visualmente el juego de Tetris. Se encarga de dibujar los bloques en el tablero y mostrar la pieza actual en movimiento. 
# Además, proporciona información relevante al jugador, como la puntuación acumulada.
class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)
    speed = 10

    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * BOARD_DATA.width, gridSize * BOARD_DATA.height)
        self.gridSize = gridSize
        self.initBoard()

    def initBoard(self):
        self.score = 0
        BOARD_DATA.clear()

    def paintEvent(self, event):
        painter = QPainter(self)

        for x in range(BOARD_DATA.width):
            for y in range(BOARD_DATA.height):
                val = BOARD_DATA.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        for x, y in BOARD_DATA.getCurrentShapeCoord():
            val = BOARD_DATA.currentShape.shape
            drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        painter.setPen(QColor(0x777777))
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())

    def updateData(self):
        self.msg2Statusbar.emit("Nro. de Líneas: " + str(self.score) + " | Puntos Acumulados: " + str(self.score * 100))
        self.update()


class Board1(QFrame):
    msg2Statusbar = pyqtSignal(str)
    speed = 10

    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * BOARD_DATA.width, gridSize * BOARD_DATA.height)
        self.gridSize = gridSize
        self.initBoard1()

    def initBoard(self):
        self.score = 0
        BOARD_DATA.clear()

    def paintEvent(self, event):
        painter = QPainter(self)

        for x in range(BOARD_DATA.width):
            for y in range(BOARD_DATA.height):
                val = BOARD_DATA.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        for x, y in BOARD_DATA.getCurrentShapeCoord():
            val = BOARD_DATA.currentShape.shape
            drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        painter.setPen(QColor(0x777777))
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())

    def updateData(self):
        self.msg2Statusbar.emit(str(self.score))
        self.update()

# Crea una instancia de la aplicación PyQt5, inicializa el juego de Tetris (Tetris) y comienza la ejecución de la aplicación.
if __name__ == '__main__':
    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())