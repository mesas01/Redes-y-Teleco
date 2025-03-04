import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Importar para la visualización 3D

# Paso 1: Obtener entradas del usuario
tasa_datos_bps = int(input("Ingrese la tasa de datos en bps (ej., 1000): "))  # Tasa de datos en bps
ancho_banda_hz = int(input("Ingrese el ancho de banda en Hz (ej., 5000): "))  # Ancho de banda en Hz
senal_8bits = input("Ingrese la señal de 8 bits (ej., 1 0 1 1 0 1 0 0): ")  # Señal de 8 bits como cadena de texto

# Convertir la señal de 8 bits de cadena a lista de enteros
senal_8bits = [int(bit) for bit in senal_8bits.split()]

# Paso 2: Calcular la frecuencia fundamental
T = len(senal_8bits) / tasa_datos_bps  # Período de la señal
frecuencia_fundamental = 1 / T  # Frecuencia fundamental

# Paso 3: Determinar el número de armónicos
num_armonicos = int(ancho_banda_hz / frecuencia_fundamental)

# Paso 4: Generar el eje de tiempo
tiempo = np.linspace(0, T, 1000)  # Eje de tiempo para graficar

# Paso 5: Análisis de Fourier
def serie_fourier(senal, tiempo, num_armonicos):
    coef_an = []  # Coeficientes de coseno
    coef_bn = []  # Coeficientes de seno
    amplitudes = []  # Amplitudes
    fases = []  # Desplazamientos de fase

    for n in range(1, num_armonicos + 1):
        # Calcular coeficientes a_n y b_n usando np.trapezoid
        coef_an.append((2 / T) * np.trapezoid(senal * np.cos(2 * np.pi * n * frecuencia_fundamental * tiempo), tiempo))
        coef_bn.append((2 / T) * np.trapezoid(senal * np.sin(2 * np.pi * n * frecuencia_fundamental * tiempo), tiempo))

        # Calcular amplitudes y fases
        amplitudes.append(np.sqrt(coef_an[-1]**2 + coef_bn[-1]**2))
        fases.append(np.arctan2(coef_bn[-1], coef_an[-1]))

    return coef_an, coef_bn, amplitudes, fases

# Convertir la señal de 8 bits en una señal continua para el análisis de Fourier
senal_continua = np.zeros_like(tiempo)
duracion_bit = T / len(senal_8bits)  # Duración de cada bit
tam_muestra = len(tiempo) / T  # Factor de escala

# Invertir el orden de los bits al mapear la señal continua
for i, bit in enumerate(reversed(senal_8bits)):  # Usar reversed para invertir el orden
    inicio = int(i * duracion_bit * tam_muestra)
    fin = int((i + 1) * duracion_bit * tam_muestra)
    senal_continua[inicio:fin] = bit

# Realizar el análisis de Fourier
coef_an, coef_bn, amplitudes, fases = serie_fourier(senal_continua, tiempo, num_armonicos)

# Paso 6: Reconstruir la señal
senal_reconstruida = np.zeros_like(tiempo)
for n in range(1, num_armonicos + 1):
    senal_reconstruida += amplitudes[n - 1] * np.cos(2 * np.pi * n * frecuencia_fundamental * tiempo + fases[n - 1])

# Paso 7: Graficar

# Graficar armónicos individuales
plt.figure(figsize=(12, 6))
for n in range(1, num_armonicos + 1):
    armonico = amplitudes[n - 1] * np.cos(2 * np.pi * n * frecuencia_fundamental * tiempo + fases[n - 1])
    plt.plot(tiempo, armonico)
plt.title('Armónicos Individuales')
plt.xlabel('Tiempo')
plt.ylabel('Amplitud')
plt.show()

# Graficar la señal reconstruida y la original
plt.figure(figsize=(12, 6))

# Graficar la señal original de 8 bits como función escalonada
tiempo_original = np.linspace(0, T, len(senal_8bits), endpoint=False)  # Puntos de tiempo para la señal original
plt.step(tiempo_original, senal_8bits, where='post', label='Señal Original', linewidth=2, color='blue')

# Graficar la señal reconstruida
plt.plot(tiempo, senal_reconstruida, label='Señal Reconstruida', color='red')

plt.title('Señal Original vs Señal Reconstruida')
plt.xlabel('Tiempo')
plt.ylabel('Amplitud')
plt.legend()
plt.grid(True)
plt.show()

# --- Gráfica 3D de los Armónicos ---
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Crear el gráfico 3D de los armónicos
for n in range(1, num_armonicos + 1):
    armonico = amplitudes[n - 1] * np.cos(2 * np.pi * n * frecuencia_fundamental * tiempo + fases[n - 1])
    ax.plot(tiempo, np.full_like(tiempo, n), armonico)  # Eje Y es el índice del armónico

# Etiquetas
ax.set_title("Representación 3D de los Armónicos")
ax.set_xlabel("Tiempo")
ax.set_ylabel("Índice del Armónico")
ax.set_zlabel("Amplitud")

plt.show()