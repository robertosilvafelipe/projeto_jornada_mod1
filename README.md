# projeto_jornada_mod1
Sistema que detecta possíveis transações bancárias fraudulentas de forma assíncrona, usando análise de dados de transações e armazenamento em cache para acesso rápido a dados usados com frequência. Se uma transação for definida como fraudulenta, será ser possível fazer o download de um relatório em um dispositivo de armazenamento. 


#Requisitos

Linux
#PIP
apt-get install pip

#Docker
sudo apt-get install docker.io

#Python
sudo apt-get install python3

#Biblioteca Pika
sudo pip install pika

#azure-storage-blob
sudo pip install azure-storage-blob

Windows

PIP
=> https://beebom.com/how-install-pip-windows/

Docker
=> https://gist.github.com/sidneyroberto/5f0b837c2d27f791fc494c164d2a7d74

Pika
pip install pika

#azure-storage-blob
sudo pip install azure-storage-blob


#Executar o rabbbitMQ
docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management


##Acessar o RABBIT MQ localmente
#http://localhost:15672/
#user: guest
#senha: guest

#Executar o RedisCache 
docker run -it --rm --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest


#Deploy a storage account usando o template ARM. 
Altere o nome do storage account e a região; O mesmo já vem pronto para receber os dados do projeto. 
![image](https://github.com/robertosilvafelipe/projeto_jornada_mod1/assets/101230256/d2477c96-e9a9-480f-8281-d0a4ff6af311)

#importe o arquivo template do storage account

#Dados Storage ACcount 
"Template_Storage.json"
![image](https://github.com/robertosilvafelipe/projeto_jornada_mod1/assets/101230256/cc1ed638-3680-4e56-b7e2-e54689f3f989)


##Alterar os dados de conexáo da storageaccount criada para gravaçãoi
File: Consumer.py

# Configurações do Azure Blob Storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=<STG_NAME>;AccountKey=<SUA_CH?AVE_AQUI>;EndpointSuffix=core.windows.net"
container_name = "dadosclientes" (Não alterar o nome do container) 
blob_name = "dadosclientes.txt"
