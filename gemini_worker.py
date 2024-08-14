# gemini_worker.py
import pika
import json
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key='YOUR_GEMINI_API_KEY')
model = genai.GenerativeModel('gemini-1.0-pro-latest')

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='gemini_requests')
channel.queue_declare(queue='gemini_responses')

def callback(ch, method, properties, body):
    request = json.loads(body)
    prompt = request['prompt']

    # Generate response from Gemini
    response = model.generate_content(prompt)

    # Publish response back to RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps({'response': response.text})
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='gemini_requests', on_message_callback=callback)

print('Waiting for messages...')
channel.start_consuming()