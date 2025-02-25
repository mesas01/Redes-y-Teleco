# TALLER FOURIER - Redes y Telecomunicaciones
# Autor: Santiago Mesa
#
# Este programa calcula la serie de Fourier de una señal digital de 8 bits.
# Se basa en la tasa de datos y el ancho de banda proporcionados por el usuario.
# La señal se representa correctamente como una señal cuadrada.

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog


def mostrar_info():
    print("\n============================")
    print("TALLER FOURIER")
    print("SANTIAGO MESA")
    print("REDES Y TELECOMUNICACIONES")
    print("============================\n")


def generar_senal_cuadrada(senal, tiempo, periodo_bit):
    """Genera una señal cuadrada digital a partir de los bits dados."""
    senal_cuadrada = np.zeros_like(tiempo)
    for i, bit in enumerate(senal):
        valor = 1 if bit == '1' else -1
        senal_cuadrada[(tiempo >= i * periodo_bit) & (tiempo < (i + 1) * periodo_bit)] = valor
    return senal_cuadrada


def serie_fourier(tasa_datos, ancho_banda, senal):
    mostrar_info()
    print(f"Tasa de datos: {tasa_datos} bps")
    print(f"Ancho de banda: {ancho_banda} Hz")
    print(f"Señal de entrada: {senal}\n")

    periodo_bit = 1 / tasa_datos
    periodo_total = periodo_bit * len(senal)
    frecuencia_fundamental = 1 / periodo_total
    num_armonicos = int(ancho_banda // frecuencia_fundamental)

    tiempo = np.linspace(0, periodo_total, 1000)
    senal_cuadrada = generar_senal_cuadrada(senal, tiempo, periodo_bit)
    senal_reconstruida = np.zeros_like(tiempo)

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=30, azim=45)

    for n in range(1, num_armonicos + 1):
        if n % 2 == 0:
            continue  # Ignora armónicos pares para señal cuadrada ideal
        Cn = 4 / (np.pi * n)
        armonico = Cn * np.sin(2 * np.pi * n * frecuencia_fundamental * tiempo)
        senal_reconstruida += armonico
        ax.plot(tiempo, [n] * len(tiempo), armonico, linestyle='dashed', alpha=0.6, label=f'Armónico {n}')

    ax.set_title("Armónicos de la señal cuadrada en 3D")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Número de armónico")
    ax.set_zlabel("Amplitud")
    ax.legend()
    plt.show(block=False)

    plt.figure(figsize=(12, 6))
    plt.plot(tiempo, senal_cuadrada, label='Señal cuadrada original', color='blue', linewidth=2)
    plt.plot(tiempo, senal_reconstruida, label='Señal reconstruida (Fourier)', color='red', linestyle='--')
    plt.title("Comparación señal cuadrada vs reconstrucción")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    plt.grid()
    plt.show()


def obtener_entrada_usuario():
    root = tk.Tk()
    root.withdraw()
    opciones = [(100, 1000, "10101010"), (1000, 5000, "11001100"), (5000, 10000, "11110000")]
    opcion = simpledialog.askinteger("Entrada",
                                     "Seleccione una opción:\n1: 100 bps, 1000 Hz, 10101010\n2: 1000 bps, 5000 Hz, 11001100\n3: 5000 bps, 10000 Hz, 11110000\n4: Ingresar valores manualmente",
                                     minvalue=1, maxvalue=4)
    if opcion in [1, 2, 3]:
        tasa_datos, ancho_banda, senal = opciones[opcion - 1]
    else:
        tasa_datos = simpledialog.askinteger("Entrada", "Ingrese la tasa de datos en bps:")
        ancho_banda = simpledialog.askinteger("Entrada", "Ingrese el ancho de banda en Hz:")
        senal = simpledialog.askstring("Entrada", "Ingrese la señal de 8 bits:")
    serie_fourier(tasa_datos, ancho_banda, senal)


obtener_entrada_usuario()
