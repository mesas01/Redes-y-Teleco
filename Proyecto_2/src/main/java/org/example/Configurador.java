package org.example;

import org.eclipse.paho.client.mqttv3.*;

public class Configurador {
    public static void main(String[] args) {
        String broker = "tcp://broker.emqx.io:1883";
        String clientId = "JavaConfigClient";
        String topic = "config/monitor01";

        // definir la configuración deseada
        String moneda = "btc";         // o "sol"
        float umbralMin = 104550.0f;    // umbral inferior
        float umbralMax = 104600.0f;    // umbral superior
        int duracion = 5;              // duración del buzzer

        // mensaje en el formato requerido por el ESP32
        String payload = moneda + "," + umbralMin + "," + umbralMax + "," + duracion;

        try {
            // Crear cliente MQTT
            MqttClient client = new MqttClient(broker, clientId);
            MqttConnectOptions options = new MqttConnectOptions();
            options.setCleanSession(true);

            // Conectar al broker
            client.connect(options);
            System.out.println("Conectado a broker MQTT");

            // Publicar el mensaje
            MqttMessage message = new MqttMessage(payload.getBytes());
            message.setQos(0); // QoS 0: sin garantía de entrega
            client.publish(topic, message);

            System.out.println("Configuración enviada a " + topic + ": " + payload);

            client.disconnect();
            System.out.println("Desconectado correctamente");

        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
