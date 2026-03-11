import random
import time # Para el time.sleep

# Códigos sacados por defecto que implementan el color
ROJO = '\u001B[31m'
AZUL = '\u001B[34m'
VERDE = '\u001B[32m'
AMARILLO = '\u001B[33m'
RESET = '\u001B[0m'

def HLF_start():
    # Imprime el mensaje de bienvenida al usuario
    print("🚢 Empieza el juego de Hundir la Flota 🚢")
    print("¿Serás capaz de hundir la flota de Trump? ¡Empiezas tú!")
    
    # Inicia un bucle infinito para que el juego no se cierre tras una partida
    while True:
        # Pide al usuario que elija una opción y elimina espacios en blanco (.strip())
        entrada = input("🎮 1=Jugar | 0=Salir: ").strip()  
        
        if entrada == "1":                         
            # Si el usuario elige 1, instancia la clase Partida
            partida = Partida()
            # Llama al método principal para iniciar la lógica del juego
            resultado = partida.jugar()
            
            # Si el método jugar devuelve algo que evalúe como False (ej. None o False), sale del bucle
            if not resultado:  
                break
            # Si la partida termina normalmente, pregunta si quiere otra
            print("¿Nueva partida?")  
            
        elif entrada == "0":                       
            # Si el usuario elige 0, se despide y rompe el bucle para cerrar el programa
            print("¡Gracias por jugar! 👋")
            break
        
class Barco:
    def __init__(self, vidas):
        # Define cuántas celdas ocupa el barco (su resistencia)
        self.vidas = int(vidas)
        # Lista vacía para almacenar las posiciones (ej. [0,1], [0,2]) que ocupa en el tablero
        self.coordenadas = []
        
    def esta_vivo(self):
        # Devuelve True si aún le quedan vidas, False si ha sido hundido
        return self.vidas > 0
    
    def recibir_disparo(self):
        # Verifica si el barco aún tiene "salud" antes de procesar el daño
        if self.vidas > 0:
            self.vidas -= 1 # Resta una vida por el impacto
            
            # Si tras el impacto llega a 0, el barco se ha hundido por completo
            if self.vidas == 0:
                return "HUNDIDO"
            # Si aún le quedan vidas, solo ha sido alcanzado
            return "TOCADO"
        
        # Mensaje de control por si se dispara a un barco que ya no tiene vidas
        return "Ya estaba hundido"
    
Acorazado = Barco(4)
Submarino = Barco(3)
Crucero = Barco(2)
Suubmarino = Barco(1)

# Funcion para imprimir tablero
def imprimir_tablero(tablero):
    for fila in tablero:
        for i in fila:
            print(f"[{i}]",end=" ")
        print("")
        
class Partida:
    def __init__(self):
        # Inicializa los atributos principales de la sesión de juego
        self.humano = None
        self.trump = None
        self.turno_actual = "Humano"  # El jugador humano siempre comienza
        self.estado_general = "EN_CURSO"  # Controla si el bucle de juego debe seguir

    def crear_jugadores_y_tableros(self):
        # Instancia a los dos competidores
        self.humano = Player("Humano", "Humano")
        self.trump = Player("Computer", "Trump")
        
        # Asigna los dos tableros necesarios a cada jugador (Propio y de Disparos)
        self.humano.tablero_propio = Board("Humano", False)
        self.humano.tablero_disparos = Board("Humano", True)
        self.trump.tablero_propio = Board("Trump", False)
        self.trump.tablero_disparos = Board("Trump", True)
        
        # Genera las flotas de barcos para ambos
        self.humano.barcos = self.crear_barcos_iniciales()
        self.trump.barcos = self.crear_barcos_iniciales()
        
        # Posiciona los barcos aleatoriamente en los tableros correspondientes
        self.humano.tablero_propio.colocar_barcos_aleatorio(self.humano.barcos)
        self.trump.tablero_propio.colocar_barcos_aleatorio(self.trump.barcos)
        
        print("🚢 ¡Barcos colocados! Mira tu flota y empieza a jugar.")

    def crear_barcos_iniciales(self):
        # Define la composición de la flota: 4 de 1, 3 de 2, 2 de 3 y 1 de 4 celdas
        barcos = []
        barcos.extend([Barco(1) for _ in range(4)])
        barcos.extend([Barco(2) for _ in range(3)])
        barcos.extend([Barco(3) for _ in range(2)])
        barcos.append(Barco(4))
        return barcos
    
    def flota_hundida(self, jugador):
        # Verifica si todos los barcos del jugador han sido destruidos
        return all(not barco.esta_vivo() for barco in jugador.barcos)

    def obtener_barco_en_coordenada(self, jugador, x, y):
        # Busca qué barco específico ocupa una casilla impactada para restarle vida
        for barco in jugador.barcos:
            if (x, y) in barco.coordenadas and barco.esta_vivo():
                return barco
        return None

    def mostrar_tableros_lado_a_lado(self): 
        # Renderiza visualmente ambos tableros del humano en la consola
        propio = self.humano.tablero_propio.celda
        disparos = self.humano.tablero_disparos.celda

        print("═" * 84)
        print("TUS TABLEROS ")
        print("═" * 84)

        for i in range(10):
            # Formatea las filas de ambos tableros para que aparezcan en paralelo
            linea_propio = "".join([f"[{self.celda_a_str(c)}]" for c in propio[i]])      
            linea_disp = "".join([f"[{self.celda_a_str(c)}]" for c in disparos[i]])        
            print(f"{i:2} {linea_propio:>11}   {linea_disp:>11} {i:2}")
        print(" " + " ".join([f"{j:2}" for j in range(10)]) + "      " + " ".join([f"{j:2}" for j in range(10)]))

        print("═" * 84)
        
    def celda_a_str(self, c):  
        # Evita que se desalineen las celdas vacias al volver a imprimir el tablero actualizado.
        if c == ' ': return ' '
        return str(c)

    def disparo_humano(self):
        self.mostrar_tableros_lado_a_lado()
        entrada = input("TURNO HUMANO, Coords (fila,col 0-9) o '0' SALIR: ").strip()
        
        if entrada == "0":
            print("¡Gracias por jugar!")
            self.estado_general = "FINALIZADA"  
            return False
        
        partes = entrada.split(',')
        if len(partes) != 2:
            print("❌ Formato: fila,col ej: 5,3")
            return True
        
        try:
            fila = int(partes[0].strip())
            col = int(partes[1].strip())
        except ValueError:
            print("❌ Números enteros: fila,col ej: 5,3")
            return True
        
        # Validaciones de rango y repetición
        if not (0 <= fila <= 9 and 0 <= col <= 9):
            print("❌ Coords inválidas (0-9)")
            return True
        
        if self.humano.tablero_disparos.celda[fila][col] != ' ':
            print("❌ Ya disparaste ahí")
            return True
        
        # Comprobación de impacto en el tablero de Trump
        if self.trump.tablero_propio.celda[fila][col] == 'B':
            self.humano.tablero_disparos.celda[fila][col] = ROJO +'X'+ RESET
            print("🎯 ¡TOCADO!")
            barco = self.obtener_barco_en_coordenada(self.trump, fila, col)
            if barco:
                resultado = barco.recibir_disparo()
                if resultado == "HUNDIDO":
                    print("💥 ¡BARCO HUNDIDO!")
            return True # Repite turno tras acierto
        else:
            self.humano.tablero_disparos.celda[fila][col] = AZUL + 'A'+ RESET
            print("💧 AGUA")
            return False # Cambia turno al fallar

    def disparo_trump(self):
        # Lógica de ataque de la IA
        print("😈 Trump está preparando a su ejército 😈")
        time.sleep(3) # Añade una pausa
        
        if self.estado_general != "EN_CURSO":
            return False
            
        # Busca una coordenada aleatoria que no haya sido atacada antes
        while True:
            fila = random.randint(0, 9) 
            col = random.randint(0, 9)
            if self.trump.tablero_disparos.celda[fila][col] == ' ':  
                break
        
        print(f"Trump dispara a ({fila},{col})")
        
        # Procesa el impacto en el tablero del humano
        if self.humano.tablero_propio.celda[fila][col] == 'B':
            self.trump.tablero_disparos.celda[fila][col] = ROJO + 'X' + RESET     
            self.humano.tablero_propio.celda[fila][col] = ROJO + 'X' + RESET         
            print(f"😈 Trump dispara {fila},{col} → 🎯 ¡TOCADO!")
            barco = self.obtener_barco_en_coordenada(self.humano, fila, col)
            if barco:
                resultado = barco.recibir_disparo()
                if resultado == "HUNDIDO":
                    print("💥 ¡BARCO HUNDIDO!")
            return True
        else:
            self.trump.tablero_disparos.celda[fila][col] = AZUL + 'A'+ RESET      
            self.humano.tablero_propio.celda[fila][col] = AZUL + 'A'+ RESET       
            print(f"🇺🇸 Trump dispara {fila},{col} → 💧 AGUA")
            return False

    def jugar(self):
        # Orquestador principal de la partida
        self.crear_jugadores_y_tableros()
        
        while self.estado_general == "EN_CURSO":
            # Verifica condiciones de fin de juego antes de cada turno
            if self.flota_hundida(self.trump):  
                print("🏆 ¡HAS HUNDIDO TODA LA FLOTA DE TRUMP! ¡VICTORIA!")
                return False
            if self.flota_hundida(self.humano):  
                print("💥 Trump ha hundido tu flota. ¡DERROTA!")
                return False
                
            # Ejecuta el turno correspondiente
            if self.turno_actual == "Humano":
                if not self.disparo_humano():
                    self.turno_actual = "Trump"
            else:
                if not self.disparo_trump():
                    self.turno_actual = "Humano"
        
        return False
    
    
class Player:
    def __init__(self, tipo, nombre):
        # Diferencia si es un jugador real o la IA (ej. para decidir si pide input por consola)
        self.tipo = tipo  # "Humano" o "Computer"
        
        # El nombre personalizado del jugador
        self.nombre = nombre
        
        # Lista donde se guardarán las instancias de la clase 'Barco' que pertenecen a este jugador
        self.barcos = []
        
        # Guardará la matriz (tablero) donde el jugador tiene colocados sus propios barcos
        self.tablero_propio = None
        
        # Guardará el tablero donde el jugador marca los disparos que hace al enemigo (para no repetir)
        self.tablero_disparos = None
        
class Board:
    def __init__(self, owner, es_tablero_disparos=False):
        # Crea una matriz de 10x10 llena de espacios vacíos ' '
        self.celda = [[' ' for _ in range(10)] for _ in range(10)]
        self.owner = owner  # Jugador al que pertenece este tablero
        self.es_tablero_disparos = es_tablero_disparos # Diferencia si es el mapa propio o el de ataques
        # Conjunto (set) para verificar rápidamente si una casilla ya tiene un barco
        self.coordenadas_ocupadas = set()

    def colocar_barco(self, barco, orientacion, x, y):
        coords = []
        # --- Lógica para colocación Horizontal ---
        if orientacion == 'H':
            # Evita que el barco se salga por la derecha (límite 10)
            if y + barco.vidas > 10: return False
            for j in range(y, y + barco.vidas):
                # Si alguna casilla ya está ocupada, aborta la colocación
                if (x, j) in self.coordenadas_ocupadas: return False
                coords.append((x, j))
        # --- Lógica para colocación Vertical ---
        else:  # 'V'
            # Evita que el barco se salga por la parte inferior
            if x + barco.vidas > 10: return False
            for i in range(x, x + barco.vidas):
                if (i, y) in self.coordenadas_ocupadas: return False
                coords.append((i, y))
        
        # Si las comprobaciones anteriores pasan, se "dibuja" el barco
        for (i, j) in coords:
            self.celda[i][j] = 'B' # 'B' representa un barco en el tablero
            self.coordenadas_ocupadas.add((i, j)) # Registra la coordenada como ocupada
        barco.coordenadas = coords # Actualiza el objeto Barco con su ubicación
        return True

    def colocar_barcos_aleatorio(self, lista_barcos):
        # Intenta colocar cada barco de la lista en una posición al azar
        for barco in lista_barcos:
            colocado = False
            while not colocado:
                orientacion = random.choice(['H', 'V'])
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                # Llama a colocar_barco; si devuelve False (colisión o fuera de rango), el bucle repite
                colocado = self.colocar_barco(barco, orientacion, x, y)
                
HLF_start()