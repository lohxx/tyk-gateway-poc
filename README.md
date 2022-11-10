Poc para testar os recursos do gateway tyk

## Configurar

Para configurar esta poc, seu ambiente precisa ter os seguintes requisitos:
    1. docker
    2. docker-compose

Para iniciar a execução dos contêineres: docker compose up.

## Configurar APIs tyk.

Para interagir com nossa mock api é necessário criá-la no tyk, para isso basta executar o script python: `python utils.py setupapi`. Este script criará uma API chamada test e imprimirá as chaves que você pode usar para fazer chamadas.

``` bash
python utils.py setupapi
usuário criado, chave: 1caf9578da40e41bbb20cc34895932f56
usuário criado, chave: 15f48e1b975284942a02e7c94eba27159
```

## Fazendo chamadas

``` bash
curl 'http://localhost:8080/test/' -H 'Autorização: Basic 15f48e1b975284942a02e7c94eba27159'
```

``` bash
curl 'http://localhost:8080/test/' -H 'Autorização: Portador 15f48e1b975284942a02e7c94eba27159'
```

``` bash
curl 'http://localhost:8080/test/?api_key=1caf9578da40e41bbb20cc34895932f56'
```

## Testes quota e rate limit

Para testar o limite de taxa configurado, chame o comando cli `python utils.py callsratelimit`
Para testar as cotas configuradas, chame o comando cli `python utils.py callsquota`