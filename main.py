# TALLER FOURIER - Redes y Telecomunicaciones
# Autor: Santiago Mesa
#
# Este programa calcula la serie de Fourier de una señal digital de 8 bits.
# Se basa en la tasa de datos y el ancho de banda proporcionados por el usuario.
#
# **Proceso Matemático:**
# 1. Se calcula la frecuencia fundamental (primer armónico) a partir de la tasa de datos.
# 2. Se determina el número de armónicos permitidos según el ancho de banda.
# 3. Se calculan los coeficientes de Fourier a_n y b_n con base en la señal de entrada.
# 4. Se calcula la amplitud Cn y el ángulo de desfase para cada armónico.
# 5. Se genera la señal reconstruida sumando los armónicos.
# 6. Se visualizan los armónicos y la señal reconstruida en gráficas 2D y 3D.

import matplotlib

matplotlib.use('TkAgg')  # Habilita backend interactivo para que la gráfica se abra en una nueva ventana
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import simpledialog


def mostrar_info():
    """
    Muestra información general del taller en la consola.
    """
    print("\n============================")
    print("TALLER FOURIER")
    print("SANTIAGO MESA")
    print("REDES Y TELECOMUNICACIONES")
    print("============================\n")


def calcular_coeficientes(senal):
    """
    Calcula los coeficientes de Fourier a_n y b_n para la señal de 8 bits.
    """
    N = len(senal)  # Longitud de la señal de entrada
    a_n = np.zeros(N)  # Inicializa coeficientes a_n
    b_n = np.zeros(N)  # Inicializa coeficientes b_n

    for n in range(1, N + 1):  # Itera sobre los armónicos
        for k in range(N):  # Itera sobre los valores de la señal
            bit = 1 if senal[k] == '1' else -1  # Convierte '1' en 1 y '0' en -1
            a_n[n - 1] += bit * np.cos(2 * np.pi * n * k / N)  # Cálculo del coeficiente a_n
            b_n[n - 1] += bit * np.sin(2 * np.pi * n * k / N)  # Cálculo del coeficiente b_n
        a_n[n - 1] *= (2 / N)  # Normalización de coeficientes
        b_n[n - 1] *= (2 / N)  # Normalización de coeficientes

    return a_n, b_n  # Retorna los coeficientes calculados


def serie_fourier(tasa_datos, ancho_banda, senal):
    """
    Genera la serie de Fourier para la señal de entrada y la visualiza.
    """
    mostrar_info()
    print(f"Tasa de datos: {tasa_datos} bps")
    print(f"Ancho de banda: {ancho_banda} Hz")
    print(f"Señal de entrada: {senal}\n")

    periodo = 1 / tasa_datos  # Cálculo del periodo de la señal
    frecuencia_fundamental = 1 / periodo  # Determina la frecuencia fundamental
    num_armonicos = min(len(senal), int(ancho_banda // frecuencia_fundamental))  # Número de armónicos permitidos

    tiempo = np.linspace(0, periodo, 1000)  # Genera un vector de tiempo
    senal_reconstruida = np.zeros_like(tiempo)  # Inicializa la señal reconstruida
    a_n, b_n = calcular_coeficientes(senal)  # Obtiene los coeficientes de Fourier

    fig = plt.figure(figsize=(12, 6))  # Crea la figura para la gráfica 3D
    ax = fig.add_subplot(111, projection='3d')  # Configura la gráfica en 3D
    ax.view_init(elev=30, azim=45)  # Define la vista inicial de la gráfica

    for n in range(1, num_armonicos + 1):  # Itera sobre los armónicos
        Cn = np.sqrt(a_n[n - 1] ** 2 + b_n[n - 1] ** 2)  # Calcula la amplitud del armónico
        fase = np.arctan2(b_n[n - 1], a_n[n - 1])  # Calcula el desfase del armónico
        armonico = Cn * np.sin(2 * np.pi * n * frecuencia_fundamental * tiempo + fase)  # Genera el armónico
        senal_reconstruida += armonico  # Suma los armónicos a la señal reconstruida
        ax.plot(tiempo, [n] * len(tiempo), armonico, linestyle='dashed', alpha=0.6, label=f'Armónico {n}')

    ax.set_title("Armónicos de la señal en 3D")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Número de armónico")
    ax.set_zlabel("Amplitud")
    ax.legend()
    plt.show(block=False)  # Abre la gráfica en una nueva ventana sin bloquear ejecución

    plt.figure(figsize=(12, 6))  # Crea la figura para la gráfica de señal reconstruida
    plt.plot(tiempo, senal_reconstruida, label='Suma de armónicos', color='black')  # Plotea la señal reconstruida
    plt.title("Señal reconstruida")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    plt.grid()
    plt.show()


def obtener_entrada_usuario():
    """
    Solicita al usuario los parámetros de entrada a través de una interfaz gráfica.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    opciones = [(100, 1000, "10101010"), (1000, 5000, "11001100"), (5000, 10000, "11110000")]  # Opciones predefinidas
    opcion = simpledialog.askinteger("Entrada",
                                     "Seleccione una opción:\n1: 100 bps, 1000 Hz, 10101010\n2: 1000 bps, 5000 Hz, 11001100\n3: 5000 bps, 10000 Hz, 11110000\n4: Ingresar valores manualmente",
                                     minvalue=1, maxvalue=4)  # Solicita la opción al usuario
    if opcion in [1, 2, 3]:
        tasa_datos, ancho_banda, senal = opciones[opcion - 1]  # Asigna valores predefinidos
    else:
        tasa_datos = simpledialog.askinteger("Entrada", "Ingrese la tasa de datos en bps:")  # Solicita tasa de datos
        ancho_banda = simpledialog.askinteger("Entrada", "Ingrese el ancho de banda en Hz:")  # Solicita ancho de banda
        senal = simpledialog.askstring("Entrada", "Ingrese la señal de 8 bits:")  # Solicita la señal de entrada
    serie_fourier(tasa_datos, ancho_banda, senal)  # Llama a la función para calcular la serie de Fourier


obtener_entrada_usuario()  # Ejecuta la función principal para solicitar datos y visualizar gráficos
