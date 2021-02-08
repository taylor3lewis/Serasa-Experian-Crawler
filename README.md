# Serasa Experian Crawler

Modelo de WebServices de APIs REST em Flask, Selenium e BeautifulSoup.

## Proposta geral
Projeto de API que inicia um Crawler para buscar informações na página YahooStocks. 

### Descrição do Teste
Desenvolver uma API REST para acionar a captação de um crawler (com simulação de navegador - selenium).
A API receberá uma requisição GET no endpoint /stocks e disparar o crawler para pegar todas os nomes (name), símbolos (symbol) e preços (price (intraday)) do site https://finance.yahoo.com/screener/new.

Nessa requisição deve ser passado o parâmetro "region" com o nome da região. Deve ser criado um cache com duração de 3 minutos e 13 segundos do resultado da busca.

#### O retorno deve ser um json na seguinte estrutura:
    {
        "simbolo": {
            "symbol": "simbolo",
            "name": "nome",
            "price": "100.00"
        },
    }

#### Exemplo buscando por Argentina:
    {
        "AMX.BA": {
            "symbol": "AMX.BA",
            "name": "América Móvil, S.A.B. de C.V.",
            "price": "2089.00"
        },
        ...
    }

## Documentação da Solução

#### Tecnologias Utilizadas:

- Python
- Flask
- Selenium
- BeautifulSoup

### Execução do projeto para Testes Locais

Fazer o Build:

    docker-compose build app

Rodar o container:

    docker-compose up app

Usar a URL localhost:5000

## Rotas

#### Lista as regiões aceitas
    
    GET
    localhost:5000/stocks-regions

Exemplo de retorno

    [
        "argentina", 
        "austria", 
        "australia", 
        "belgium",
        ...
    ]

.

#### Lista as ações de cada região 
    
    GET
    localhost:5000/stocks/<region>

Exemplo de Retorno para *stocks/argentina*

    {
        "AAPL.BA": {
            "symbol": "AAPL.BA",
            "name": "Apple Inc.",
            "price": "2,133.00"
        },
        "AAPLB.BA": {
            "symbol": "AAPLB.BA",
            "name": "APPLE INC",
            "price": "2,111.00"
        },
        ...
    }
