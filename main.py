# 9/02/2025
# TALLER FOURIER
# SANTIAGO MESA
# REDES Y TELECOMUNICACIONES
#
# Este programa genera una serie de Fourier para una señal digital de 8 bits
# utilizando la tasa de datos y el ancho de banda proporcionados por el usuario.
# La señal se descompone en armónicos y se visualiza en una gráfica 3D interactiva,
# así como en una gráfica de la señal reconstruida.

import matplotlib
matplotlib.use('TkAgg')  # Habilita backend interactivo
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import simpledialog


def mostrar_info():
    """
    Muestra por pantalla la información del programa.
    """
    print("\n============================")
    print("9/02/2025")
    print("TALLER FOURIER")
    print("SANTIAGO MESA")
    print("REDES Y TELECOMUNICACIONES")
    print("============================\n")


def serie_fourier(tasa_datos, ancho_banda, senal):
    """
    Calcula y grafica la serie de Fourier para una señal digital.
    """
    mostrar_info()
    print(f"Tasa de datos: {tasa_datos} bps")
    print(f"Ancho de banda: {ancho_banda} Hz")
    print(f"Señal de entrada: {senal}\n")

    periodo = 1 / tasa_datos  # Periodo de la señal
    frecuencia_fundamental = 1 / periodo  # Frecuencia fundamental (primer armónico)
    num_armonicos = int(ancho_banda // frecuencia_fundamental)  # Número de armónicos permitidos

    tiempo = np.linspace(0, periodo, 1000)  # Vector de tiempo para graficar
    senal_reconstruida = np.zeros_like(tiempo)  # Inicialización de la señal reconstruida

    # Configuración de la figura 3D
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=30, azim=45)  # Ángulo de vista inicial

    for n in range(1, num_armonicos + 1):
        coef_an = 2 / np.pi * np.sin(n * np.pi / 2)  # Coeficiente senoide
        coef_bn = 0  # Coeficiente cosenoide (0 para señales cuadradas)
        amplitud_cn = np.sqrt(coef_an ** 2 + coef_bn ** 2)  # Amplitud del armónico
        fase = np.arctan2(coef_bn, coef_an)  # Fase del armónico

        armonico = amplitud_cn * np.sin(2 * np.pi * n * frecuencia_fundamental * tiempo + fase)  # Cálculo del armónico
        senal_reconstruida += armonico  # Suma de los armónicos
        ax.plot(tiempo, [n] * len(tiempo), armonico, linestyle='dashed', alpha=0.6, label=f'Armónico {n}')

    # Configuración de la gráfica 3D
    ax.set_title("Armónicos de la señal en 3D")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Número de armónico")
    ax.set_zlabel("Amplitud")
    ax.legend()

    # Mostrar la gráfica interactiva
    plt.ion()
    plt.show()
    plt.ioff()

    # Gráfica de la señal reconstruida
    plt.figure(figsize=(12, 6))
    plt.plot(tiempo, senal_reconstruida, label='Suma de armónicos', color='black')
    plt.title("Señal reconstruida")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    plt.grid()
    plt.show()


def obtener_entrada_usuario():
    """
    Solicita al usuario los parámetros de entrada a través de una interfaz gráfica.
    Ofrece tres ejemplos predefinidos para quienes no sepan qué valores ingresar.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter

    opciones = [
        (100, 1000, "10101010"),
        (1000, 5000, "11001100"),
        (5000, 10000, "11110000")
    ]

    opcion = simpledialog.askinteger("Entrada",
                                     "Seleccione una opción:\n1: 100 bps, 1000 Hz, 10101010\n2: 1000 bps, 5000 Hz, 11001100\n3: 5000 bps, 10000 Hz, 11110000\n4: Ingresar valores manualmente",
                                     minvalue=1, maxvalue=4)

    if opcion in [1, 2, 3]:
        tasa_datos, ancho_banda, senal = opciones[opcion - 1]
    else:
        tasa_datos = simpledialog.askinteger("Entrada", "Ingrese la tasa de datos en bps:")
        ancho_banda = simpledialog.askinteger("Entrada", "Ingrese el ancho de banda en Hz:")
        senal = simpledialog.askstring("Entrada", "Ingrese la señal de 8 bits:")

    # Llamar a la función de Fourier con los datos seleccionados o ingresados
    serie_fourier(tasa_datos, ancho_banda, senal)


# Ejecutar la función de entrada del usuario
obtener_entrada_usuario()
