#include <WiFi.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <PubSubClient.h>

// ------------------ CONFIGURACIONES DE RED Y MQTT ------------------
const char* ssid = "SMN";                    // Nombre de la red WiFi
const char* password = "12345678";           // Contraseña de la red WiFi
const char* mqtt_broker = "broker.emqx.io";  // Servidor MQTT público
const int mqtt_port = 1883;                   // Puerto MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// ------------------ CONFIGURACIÓN DE LA PANTALLA LCD ------------------
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Dirección I2C y tamaño de pantalla

// ------------------ PINES ------------------
const int BUZZER = 33;
const int LED_ROJO = 32;
const int LED_VERDE = 27;
const int LED_AMARILLO = 25;
const int BOTON = 23;

// ------------------ ESTADO DEL SISTEMA ------------------
float ultimoPrecio = 0.0;
float umbralMin_btc = 30000.0;   // Umbral mínimo BTC
float umbralMax_btc = 31000.0;   // Umbral máximo BTC
float umbralMin_sol = 90.0;      // Umbral mínimo SOL
float umbralMax_sol = 110.0;     // Umbral máximo SOL
int duracionAlarma = 4;          // Duración del buzzer en segundos

bool buzzerActivo = false;
unsigned long inicioBuzzer = 0;
String monedaActiva = "btc";     // Moneda inicial: BTC
bool botonPresionado = false;    // Para controlar rebote del botón

// ------------------ CONFIGURACIÓN INICIAL ------------------
void setup() {
  Serial.begin(115200);

  pinMode(BUZZER, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(BOTON, INPUT_PULLUP);

  Wire.begin(21, 22);  // Pines I2C del ESP32 (SDA=21, SCL=22)
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Iniciando...");

  // Conexión a WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  lcd.setCursor(0, 1);
  lcd.print("WiFi...");
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    lcd.print(".");
    intentos++;
  }

  lcd.clear();
  if (WiFi.status() == WL_CONNECTED) {
    lcd.setCursor(0, 0);
    lcd.print("WiFi conectado");
    Serial.println("WiFi conectado");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    lcd.print("Fallo WiFi");
    Serial.println("Fallo WiFi");
    return;
  }

  // Conexión a MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callbackMQTT);
  conectarMQTT();
}

// ------------------ BUCLE PRINCIPAL ------------------
void loop() {
  if (!client.connected()) {
    conectarMQTT();
  }
  client.loop();

  // Cambiar de moneda con el botón (entre BTC y SOL)
  if (digitalRead(BOTON) == LOW && !botonPresionado) {
    monedaActiva = (monedaActiva == "btc") ? "sol" : "btc";
    resuscribirse();
    botonPresionado = true;
    Serial.println("Moneda cambiada a: " + monedaActiva);
  }
  if (digitalRead(BOTON) == HIGH) {
    botonPresionado = false;
  }

  // Selecciona umbrales según la moneda activa
  float umbralMin = (monedaActiva == "btc") ? umbralMin_btc : umbralMin_sol;
  float umbralMax = (monedaActiva == "btc") ? umbralMax_btc : umbralMax_sol;

  // Apaga el buzzer si ya se cumplió el tiempo de alarma
  if (buzzerActivo && millis() - inicioBuzzer >= duracionAlarma * 1000) {
    digitalWrite(BUZZER, LOW);
    buzzerActivo = false;
    Serial.println("Buzzer apagado");
  }

  // Control de LEDs según el valor del precio
  if (ultimoPrecio < umbralMin) {
    digitalWrite(LED_ROJO, HIGH);
    digitalWrite(LED_VERDE, LOW);
    digitalWrite(LED_AMARILLO, LOW);
  } else if (ultimoPrecio > umbralMax) {
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_VERDE, HIGH);
    digitalWrite(LED_AMARILLO, LOW);
    if (!buzzerActivo) {
      digitalWrite(BUZZER, HIGH);
      inicioBuzzer = millis();
      buzzerActivo = true;
      Serial.println("Buzzer activado");
    }
  } else {
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_VERDE, LOW);
    digitalWrite(LED_AMARILLO, HIGH);
  }

  delay(50);
}

// ------------------ CONECTAR A MQTT ------------------
void conectarMQTT() {
  String clientId = "ESP32Monitor-" + String(WiFi.macAddress());
  if (client.connect(clientId.c_str())) {
    Serial.println("MQTT conectado");
    client.subscribe("config/monitor01");  // Suscribirse a config remota
    resuscribirse();
  } else {
    Serial.print("Error MQTT: ");
    Serial.println(client.state());
  }
}

// ------------------ CAMBIAR DE TOPIC CUANDO CAMBIA MONEDA ------------------
void resuscribirse() {
  client.unsubscribe("crypto/btc");
  client.unsubscribe("crypto/sol");
  client.subscribe(("crypto/" + monedaActiva).c_str());
  Serial.println("Suscrito a: crypto/" + monedaActiva);
}

// ------------------ CUANDO LLEGA UN MENSAJE MQTT ------------------
void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String mensaje = "";
  for (int i = 0; i < length; i++) mensaje += (char)payload[i];
  String topico(topic);

  if (topico.startsWith("crypto/")) {
    ultimoPrecio = mensaje.toFloat();
    Serial.printf("Precio recibido (%s): %f\n", monedaActiva.c_str(), ultimoPrecio);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Moneda: " + monedaActiva);
    lcd.setCursor(0, 1);
    lcd.print("Precio: ");
    lcd.print(ultimoPrecio);
  }

  // Recibe configuración remota para umbrales
  if (topico == "config/monitor01") {
    int p1 = mensaje.indexOf(',');
    int p2 = mensaje.indexOf(',', p1 + 1);
    int p3 = mensaje.indexOf(',', p2 + 1);

    String moneda = mensaje.substring(0, p1);
    float nuevoMin = mensaje.substring(p1 + 1, p2).toFloat();
    float nuevoMax = mensaje.substring(p2 + 1, p3).toFloat();
    duracionAlarma = mensaje.substring(p3 + 1).toInt();

    if (moneda == "btc") {
      umbralMin_btc = nuevoMin;
      umbralMax_btc = nuevoMax;
      Serial.printf("Config BTC: min = %.5f, max = %.5f, alarma = %ds\n", umbralMin_btc, umbralMax_btc, duracionAlarma);
    } else if (moneda == "sol") {
      umbralMin_sol = nuevoMin;
      umbralMax_sol = nuevoMax;
      Serial.printf("Config SOL: min = %.5f, max = %.5f, alarma = %ds\n", umbralMin_sol, umbralMax_sol, duracionAlarma);
    }
  }
}
