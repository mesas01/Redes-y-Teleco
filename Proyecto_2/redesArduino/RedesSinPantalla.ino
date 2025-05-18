#include <WiFi.h>
#include <PubSubClient.h>

// WiFi
const char* ssid = "SMN";
const char* password = "12345678";
const char* mqtt_broker = "broker.emqx.io";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient client(espClient);

// Pines
const int BUZZER = 33;
const int LED_ROJO = 32;
const int LED_VERDE = 27;
const int LED_AMARILLO = 25;
const int BOTON = 23;

// Estado
float ultimoPrecio = 0.0;
float umbralMin_btc = 30000.0;
float umbralMax_btc = 31000.0;
float umbralMin_sol = 90.0;
float umbralMax_sol = 110.0;
int duracionAlarma = 4;

bool buzzerActivo = false;
unsigned long inicioBuzzer = 0;
String monedaActiva = "btc";
bool botonPresionado = false;

void setup() {
  Serial.begin(115200);

  pinMode(BUZZER, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(BOTON, INPUT_PULLUP);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi conectado");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Fallo WiFi");
    return;
  }

  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callbackMQTT);
  conectarMQTT();
}

void loop() {
  if (!client.connected()) {
    conectarMQTT();
  }
  client.loop();

  if (digitalRead(BOTON) == LOW && !botonPresionado) {
    monedaActiva = (monedaActiva == "btc") ? "sol" : "btc";
    resuscribirse();
    botonPresionado = true;
    Serial.println("🔁 Moneda cambiada a: " + monedaActiva);
  }

  if (digitalRead(BOTON) == HIGH) {
    botonPresionado = false;
  }

  float umbralMin = (monedaActiva == "btc") ? umbralMin_btc : umbralMin_sol;
  float umbralMax = (monedaActiva == "btc") ? umbralMax_btc : umbralMax_sol;

  if (buzzerActivo && millis() - inicioBuzzer >= duracionAlarma * 1000) {
    digitalWrite(BUZZER, LOW);
    buzzerActivo = false;
    Serial.println("🔕 Buzzer apagado");
  }

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
      Serial.println("🚨 Buzzer activado");
    }
  } else {
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_VERDE, LOW);
    digitalWrite(LED_AMARILLO, HIGH);
  }

  delay(50);
}

void conectarMQTT() {
  String clientId = "ESP32Monitor-" + String(WiFi.macAddress());
  if (client.connect(clientId.c_str())) {
    Serial.println("✅ MQTT conectado");
    client.subscribe("config/monitor01");
    resuscribirse();
  } else {
    Serial.print("❌ Error MQTT: ");
    Serial.println(client.state());
  }
}

void resuscribirse() {
  client.unsubscribe("crypto/btc");
  client.unsubscribe("crypto/sol");
  client.subscribe(("crypto/" + monedaActiva).c_str());
  Serial.println("📡 Suscrito a: crypto/" + monedaActiva);
}

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  String mensaje = "";
  for (int i = 0; i < length; i++) mensaje += (char)payload[i];
  String topico(topic);

  if (topico.startsWith("crypto/")) {
    ultimoPrecio = mensaje.toFloat();
    Serial.printf("📩 Precio (%s): %.5f\n", monedaActiva.c_str(), ultimoPrecio);
  }

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
      Serial.printf("⚙️ Config BTC: min = %.5f, max = %.5f, alarma = %ds\n", umbralMin_btc, umbralMax_btc, duracionAlarma);
    } else if (moneda == "sol") {
      umbralMin_sol = nuevoMin;
      umbralMax_sol = nuevoMax;
      Serial.printf("⚙️ Config SOL: min = %.5f, max = %.5f, alarma = %ds\n", umbralMin_sol, umbralMax_sol, duracionAlarma);
    }
  }
}
