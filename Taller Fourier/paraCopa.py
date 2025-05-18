import smtplib
import schedule
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configuración del correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = ("gptproyecto2"
                "@gmail.com")
EMAIL_PASSWORD = "vabs vyrn zqkr dtap"  # Usa una contraseña de aplicación de Google
EMAIL_RECEIVER = "purchaseconf@copaair.com"

# Lista de archivos adjuntos (modificar rutas si es necesario)
ATTACHMENTS = [
    r"C:\users\mesas\OneDrive - Pontificia Universidad Javeriana\Desktop\docs/cedula.pdf",  # Documento de identificación
    r"C:\users\mesas\OneDrive - Pontificia Universidad Javeriana\Desktop\docs/Estado de cuenta.pdf",  # Extracto bancario
    r"C:\users\mesas\OneDrive - Pontificia Universidad Javeriana\Desktop\docs/Transaccion.pdf"
    # Comprobante de transacción
]


def send_email():
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "Problema con Transacción - Reserva AO4SC5"

        # Cuerpo del mensaje
        body = """\
Hola, soy Juan Sebastián Hurtado, y ya solicito por favor desde otro correo una respuesta ya que ha sido imposible contactarme desde el principal. Me ha rebotado la transacción con ustedes, tengo 3 personas que viajan hoy y me han estado dando largas una y otra vez.

Adjunto de nuevo los documentos en PDF. Díganme qué más necesitan para validar porque además hice otro intento con otras tarjetas y también me las rechazó.

# Reserva: AO4SC5

**PASAJEROS:**  
- Santiago Mesa  
- Juliana Lugo  
- Josue Vega  

**Documentos adjuntos:**  
- **IDENTIFICACIÓN PDF**  
- **EXTRACTO BANCARIO PDF**  
- **TRANSACCIÓN PDF**  
"""

        msg.attach(MIMEText(body, "plain"))

        # Adjuntar los archivos
        for file_path in ATTACHMENTS:
            if os.path.exists(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(part)
            else:
                print(f"Advertencia: No se encontró el archivo {file_path}")

        # Conectar con el servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
        server.quit()

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


# Configurar el envío cada 1 minuto
schedule.every(1).minutes.do(send_email)

print("El script está en ejecución...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera 60 segundos antes de revisar nuevamente
