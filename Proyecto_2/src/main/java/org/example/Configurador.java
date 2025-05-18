package org.example;

import org.eclipse.paho.client.mqttv3.*;

public class Configurador {
    public static void main(String[] args) {
        String broker = "tcp://broker.emqx.io:1883";
        String clientId = "JavaConfigClient";
        String topic = "config/monitor01";

        // Aunque se enviará, el ESP32 ya usa el estado del switch
        String monedaDummy = "btc";        // Solo por formato
        float umbral = 102974.0f;           // Precio mínimo para activar buzzer
        int duracion = 5;                  // Duración del buzzer en segundos

        String payload = monedaDummy + "," + umbral + "," + duracion;

        try {
            MqttClient client = new MqttClient(broker, clientId);
            MqttConnectOptions options = new MqttConnectOptions();
            options.setCleanSession(true);

            client.connect(options);
            System.out.println("Conectado a broker MQTT");

            MqttMessage message = new MqttMessage(payload.getBytes());
            message.setQos(0);
            client.publish(topic, message);

            System.out.println("Configuración enviada a " + topic + ": " + payload);

            client.disconnect();
            System.out.println("Desconectado correctamente");

        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
