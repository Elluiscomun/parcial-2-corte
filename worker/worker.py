import pika
import os
import json
import time
from datetime import datetime

def callback(ch, method, properties, body):
    try:
        message = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp} - {message}\n"
        
        with open("/app/data/messages.log", "a") as f:
            f.write(log_entry)
            
        print(f" [x] Received and logged: {message}")
    except Exception as e:
        print(f"Error processing message: {str(e)}")

def main():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"))
            )
            channel = connection.channel()
            
            channel.queue_declare(queue=os.getenv("RABBITMQ_QUEUE", "messages"))
            
            channel.basic_consume(
                queue=os.getenv("RABBITMQ_QUEUE", "messages"),
                on_message_callback=callback,
                auto_ack=True
            )
            
            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connection failed, retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Worker stopped")
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()