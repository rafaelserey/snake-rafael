# Snake funcional para terminal

Jogo Snake executado no terminal, implementado em Python com a arquitetura **Functional Core, Imperative Shell**.

## Arquitetura

### Functional Core

O arquivo `core.py` contém as regras do jogo. Suas funções recebem valores como entrada e retornam novos valores, sem modificar o estado anterior.

O núcleo não lê o teclado, não imprime no terminal e não gera números aleatórios. A função `advance`, por exemplo, recebe o estado atual, a direção solicitada e uma possível nova posição para a fruta, retornando um novo estado ou um erro por meio de `Result`.

Os tipos definidos em `models.py` usam `NamedTuple`, mantendo os dados imutáveis. Assim, cada atualização cria um novo `GameState` em vez de alterar o estado existente.

### Imperative Shell

O arquivo `main.py` contém as operações que dependem do ambiente externo, como:

- leitura do teclado;
- geração aleatória da fruta;
- desenho no terminal;
- controle do laço principal do jogo;
- espera entre as atualizações.

A shell coleta essas informações e as envia ao núcleo funcional. Depois, utiliza o estado retornado pelo núcleo para renderizar a próxima tela.

## Requisitos

- Biblioteca `blessed`
- Biblioteca `result`

## Como executar

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install blessed result
```

Execute o jogo:

```bash
python main.py
```

## Controles

- `W` ou seta para cima: mover para cima
- `S` ou seta para baixo: mover para baixo
- `A` ou seta para esquerda: mover para esquerda
- `D` ou seta para direita: mover para direita
- `Q` ou `Esc`: sair

