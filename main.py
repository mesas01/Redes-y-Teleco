# TALLER FOURIER - Redes y Telecomunicaciones
# Autor: Santiago Mesa
#
# Este programa genera una señal cuadrada digital basada en una entrada de 8 bits 
# y calcula su serie de Fourier para reconstruirla visualmente.
#
# Explicación matemática paso a paso (para dummies):
# 1. Tomamos una señal digital, representada por bits (1 o 0).
# 2. Cada bit se convierte en un pulso cuadrado (1 = nivel alto, 0 = nivel bajo).
# 3. Para reconstruir esta señal cuadrada usando la Serie de Fourier, sumamos ondas
#    senoidales (armónicos), teniendo en cuenta que cuantos más armónicos sumamos, más
#    se parece la señal reconstruida a la original cuadrada.
# 4. Los armónicos usados son únicamente impares, porque los armónicos pares no aportan
#    nada a la reconstrucción de una señal cuadrada simétrica.
# 5. Finalmente, se visualiza la señal original y la reconstruida.

import matplotlib
matplotlib.use('TkAgg')  # Backend interactivo para gráficas en ventanas separadas
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog

def mostrar_info():
    # Imprime información general del taller
    print("\n============================")
    print("TALLER FOURIER")
    print("SANTIAGO MESA")
    print("REDES Y TELECOMUNICACIONES")
    print("============================\n")

def generar_senal_cuadrada(senal, periodo_bit, tiempo):
    # Genera una señal cuadrada a partir de una cadena de bits
    senal_cuadrada = np.zeros_like(tiempo)  # Inicializa la señal en cero
    for i, bit in enumerate(senal):
        valor = 1 if bit == '1' else -1  # Define valor del pulso: 1 para bit=1, -1 para bit=0
        # Establece el nivel constante en el intervalo del bit correspondiente
        senal_cuadrada[(tiempo >= i * periodo_bit) & (tiempo < (i + 1) * periodo_bit)] = valor
    return senal_cuadrada

def serie_fourier(tasa_datos, ancho_banda, senal):
    # Muestra información del taller y parámetros usados
    mostrar_info()
    print(f"Tasa de datos: {tasa_datos} bps")
    print(f"Ancho de banda: {ancho_banda} Hz")
    print(f"Señal de entrada: {senal}\n")

    # Calcula periodo de cada bit y periodo total
    periodo_bit = 1 / tasa_datos
    periodo_total = periodo_bit * len(senal)

    # Frecuencia fundamental basada en el periodo total
    frecuencia_fundamental = 1 / periodo_total

    # Calcula número máximo de armónicos según ancho de banda
    num_armonicos = int(ancho_banda // frecuencia_fundamental)

    # Vector de tiempo para graficar la señal
    tiempo = np.linspace(0, periodo_total, 1000)

    # Construye la señal cuadrada original
    senal_cuadrada = generar_senal_cuadrada(senal, tiempo, periodo_bit)
    senal_reconstruida = np.zeros_like(tiempo)

    # Figura para mostrar los armónicos en 3D
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=30, azim=45)

    # Calcula y suma armónicos para reconstruir la señal cuadrada
    for n in range(1, num_armonicos + 1):
        if n % 2 == 0:
            continue  # La señal cuadrada solo usa armónicos impares
        Cn = (4 / (np.pi * n))  # Amplitud de los armónicos para señal cuadrada
        armonico = Cn * np.sin(2 * np.pi * n * frecuencia_fundamental * tiempo)
        senal_reconstruida += armonico
        ax.plot(tiempo, [n] * len(tiempo), armonico, linestyle='dashed', alpha=0.6, label=f'Armónico {n}')

    # Configuración gráfica 3D
    ax.set_title("Armónicos en 3D")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Número de armónico")
    ax.set_zlabel("Amplitud")
    ax.legend()
    plt.show(block=False)

    # Grafica comparación señal cuadrada vs reconstruida
    plt.figure(figsize=(12, 6))
    plt.plot(tiempo, senal_cuadrada, label='Señal cuadrada original', color='blue', linewidth=2)
    plt.plot(tiempo, senal_reconstruida, label='Señal reconstruida (Fourier)', color='red', linestyle='--')
    plt.title("Comparación señal cuadrada vs reconstrucción Fourier")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    plt.grid()
    plt.show()

def generar_senal_cuadrada(senal, tiempo, periodo_bit):
    # Genera la señal cuadrada real que representa cada bit
    senal_cuadrada = np.zeros_like(tiempo)
    for i, bit in enumerate(senal):
        valor = 1 if bit == '1' else -1
        inicio = i * periodo_bit
        fin = (i + 1) * periodo_bit
        senal_cuadrada[(tiempo >= inicio) & (tiempo < fin)] = valor
    return senal_cuadrada

def obtener_entrada_usuario():
    # Ventana para obtener parámetros del usuario
    root = tk.Tk()
    root.withdraw()
    opciones = [
        (100, 1000, "10101010"),
        (1000, 5000, "11001100"),
        (5000, 10000, "11110000")
    ]

    opcion = simpledialog.askinteger("Entrada",
                                     "Seleccione una opción:\n"
                                     "1: 100 bps, 1000 Hz, 10101010\n"
                                     "2: 1000 bps, 5000 Hz, 11001100\n"
                                     "3: 5000 bps, 10000 Hz, 11110000\n"
                                     "4: Ingresar valores manualmente",
                                     minvalue=1, maxvalue=4)

    # Selecciona opción predefinida o permite ingreso manual
    if opcion in [1, 2, 3]:
        tasa_datos, ancho_banda, senal = opciones[opcion - 1]
    else:
        tasa_datos = simpledialog.askinteger("Entrada", "Ingrese la tasa de datos en bps:")
        ancho_banda = simpledialog.askinteger("Entrada", "Ingrese el ancho de banda en Hz:")
        senal = simpledialog.askstring("Entrada", "Ingrese la señal de 8 bits:")

    serie_fourier(tasa_datos, ancho_banda, senal)

# Ejecución principal del programa
obtener_entrada_usuario()