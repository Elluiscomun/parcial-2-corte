from flask import Flask, request, jsonify
import pika
import os

app = Flask(__name__)

@app.route("/api/message", methods=["POST"])
def create_message():
    data = request.get_json()
    content = data.get("content")
    if not content:
        return jsonify({"error": "No content provided"}), 400

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"))
        )
        channel = connection.channel()
        channel.queue_declare(queue=os.getenv("RABBITMQ_QUEUE", "messages"))
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("RABBITMQ_QUEUE", "messages"),
            body=content
        )
        connection.close()
        return jsonify({"status": "Message sent to RabbitMQ"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)