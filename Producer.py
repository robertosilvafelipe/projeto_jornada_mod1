import pika
import json

# Conexão com o RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declara o exchange do tipo Fanout chamado "exchange_transacoes"
channel.exchange_declare(exchange='exchange_transacoes', exchange_type='fanout')

# Declaração da fila
channel.queue_declare(queue='fila_processa_eventos')

# Faz o bind da fila ao exchange
channel.queue_bind(exchange='exchange_transacoes', queue='fila_processa_eventos', routing_key='routing_key')

# Função para enviar eventos para a fila
def enviar_evento_from_json(file_path):
    # Abre o arquivo JSON e carrega os dados
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Envia cada evento para a fila
    for evento in data:
        channel.basic_publish(exchange='exchange_transacoes', routing_key='routing_key', body=json.dumps(evento))
        print(f"Evento '{evento}' enviado para a fila")

# Exemplo de uso
enviar_evento_from_json('dados.json')

# Fechar conexão após o envio 
connection.close()