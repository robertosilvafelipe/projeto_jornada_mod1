import pika
import redis
import json
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Conexão com o RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Conexão com o Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Configurações do Azure Blob Storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=<STORAGE_ACCOUNT_NAME>;AccountKey=<SUA_CHAVE_AQUI>==;EndpointSuffix=core.windows.net"
container_name = "dadosclientes"
blob_name = "dadosclientes.txt"

# Cliente do Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Função para salvar dados no Azure Blob quando fraude for detectada
def salvar_dados_fraude(mensagem):
    blob_client = container_client.get_blob_client(blob_name)
    try:
        # Verifica se o blob já existe e obtém o conteúdo atual
        download_stream = blob_client.download_blob()
        conteudo_existente = download_stream.readall().decode('utf-8')
        novo_conteudo = conteudo_existente + "\n" + json.dumps(mensagem)
    except Exception as e:
        novo_conteudo = json.dumps(mensagem)
    
    # Salva o novo conteúdo no blob
    blob_client.upload_blob(novo_conteudo, overwrite=True)
    print("Dados de fraude salvos no Azure Blob Storage.")

# Função para verificar a fraude com base na mudança de endereço
def verificar_fraude(endereco, timestamp, mensagem):
    endereco_anterior = json.loads(redis_client.get('endereco_cliente') or '{}')
    ultimo_timestamp = endereco_anterior.get('timestamp')
    
    #verifica a alteração do endereço para detectar a fraude
    if ultimo_timestamp:
        ultimo_timestamp = datetime.strptime(ultimo_timestamp, "%Y-%m-%dT%H:%M:%S %z")
        if (endereco_anterior.get('city') != endereco['city'] or
            endereco_anterior.get('state') != endereco['state']):
            print("Possível fraude detectada devido à mudança de endereço em curto intervalo de tempo!")
            salvar_dados_fraude(mensagem)
    
    endereco['timestamp'] = timestamp.strftime("%Y-%m-%dT%H:%M:%S %z")
    redis_client.set('endereco_cliente', json.dumps(endereco), ex=20)

# Função de callback para processar a mensagem recebida
def callback(ch, method, properties, body):
    mensagem = json.loads(body)
    endereco = mensagem.get('endereco', '').split(', ')
    if len(endereco) == 3:
        cidade, uf, _ = endereco
        datatrasancao = datetime.strptime(mensagem.get('datatrasancao'), "%Y-%m-%dT%H:%M:%S %z")
        verificar_fraude({'city': cidade, 'state': uf}, datatrasancao, mensagem)
        
        # Verifica se os dados do cliente estão no cache
        cliente_id = mensagem.get('_id', '')
        redis_key = f'dados_cliente:{cliente_id}'
        cliente_cache = redis_client.get(redis_key)
        if cliente_cache:
            print("Dados do cliente encontrados no cache:", cliente_cache.decode())
        else:
            print("Dados do cliente não encontrados no cache. Salvando no cache...")
            redis_client.set(redis_key, json.dumps(mensagem), ex=20)
    else:
        print("Endereço inválido:", mensagem.get('endereco'))
        
    print("Mensagem processada:", mensagem)

# Configurando a fila e o consumo de mensagens
channel.queue_declare(queue='fila_processa_eventos')
channel.basic_consume(queue='fila_processa_eventos', on_message_callback=callback, auto_ack=True)

# Iniciando o consumo de mensagens
print('Aguardando mensagens. Para sair pressione CTRL+C')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print('Encerrando a conexão...')
    connection.close()
