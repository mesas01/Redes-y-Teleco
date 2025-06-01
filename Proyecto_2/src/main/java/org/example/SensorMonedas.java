package org.example;

import org.eclipse.paho.client.mqttv3.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class SensorMonedas {

    public static void main(String[] args) {
        // Dirección del broker MQTT (en este caso, el broker público de EMQX)
        String broker = "tcp://broker.emqx.io:1883";

        // Identificador único para este cliente MQTT (puede ser cualquier string)
        String clientId = "JavaBinanceClient";

        try {
            //instancia del cliente MQTT usando el broker y el clientId
            MqttClient client = new MqttClient(broker, clientId);

            // Configuro las opciones de conexión
            MqttConnectOptions options = new MqttConnectOptions();
            options.setAutomaticReconnect(true); // Si se cae la conexión, intenta reconectar automáticamente
            options.setCleanSession(true);       // No guarda sesiones anteriores

            // Me conecto al broker
            System.out.println("Conectando a broker...");
            client.connect(options);
            System.out.println("Conectado a broker MQTT");

            // bucle que publica precios de dos cripto
            while (true) {
                // Consulto el precio de Bitcoin (BTC) y lo envío al tópico crypto/btc
                publishPrice(client, "BTCUSDT", "crypto/btc");

                // Consulto el precio de Solana (SOL) y lo envío al tópico crypto/sol
                publishPrice(client, "SOLUSDT", "crypto/sol");

                // Espero 5 segundos antes de volver a consultar y publicar
                Thread.sleep(5000);
            }

        } catch (MqttException | InterruptedException e) {
            // Capturo cualquier error relacionado con MQTT o interrupciones del hilo
            e.printStackTrace();
        }
    }

    // Esta función se encarga de obtener el precio de una criptomoneda desde Binance y publicarlo en un tópico MQTT
    public static void publishPrice(MqttClient client, String symbol, String topic) {
        String price = getBinancePrice(symbol); // Obtengo el precio actual desde Binance (funcion mas abajo)

        if (price != null) {
            try {
                // Creo el mensaje MQTT con el precio en texto plano
                MqttMessage message = new MqttMessage(price.getBytes());
                message.setQos(0); // Nivel de calidad del servicio 0 (sin confirmación)

                // Publico el mensaje en el tópico MQTT correspondiente
                client.publish(topic, message);
                System.out.println("Publicado en " + topic + ": " + price);
            } catch (MqttException e) {
                System.err.println("Error al publicar en MQTT: " + e.getMessage());
            }
        } else {
            System.out.println("No se pudo obtener el precio para " + symbol);
        }
    }

    // Esta función realiza una consulta HTTP a la API de Binance para obtener el precio de una criptomoneda
    public static String getBinancePrice(String symbol) {
        try {
            // Construyo la URL de la API de Binance usando el símbolo solicitado (por ejemplo, BTCUSDT)
            URL url = new URL("https://api.binance.com/api/v3/ticker/price?symbol=" + symbol);

            // Abro una conexión HTTP
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET"); // Especifico que quiero hacer una consulta tipo GET

            // Leo la respuesta de Binance
            BufferedReader reader = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String response = reader.readLine(); // Leo solo una línea, ya que la respuesta es corta
            reader.close();

            // La respuesta tiene el formato: {"symbol":"BTCUSDT","price":"31547.23000000"}
            // Busco la posición del texto "price" y extraigo su valor
            int start = response.indexOf("\"price\":\"") + 9;
            int end = response.indexOf("\"", start);
            return response.substring(start, end); // Devuelvo solo el número como String

        } catch (Exception e) {
            // En caso de error (por ejemplo, si Binance no responde), imprimo el error y devuelvo null
            System.err.println("Error al consultar Binance: " + e.getMessage());
            return null;
        }
    }
}
