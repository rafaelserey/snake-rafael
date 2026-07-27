from __future__ import annotations

from result import Err, Ok, Result

from models import (
    Board,
    Direction,
    GameError,
    GameState,
    Position,
    Snake,
    Turn,
)


LEFT_TURNS: dict[Direction, Direction] = {
    Direction.UP: Direction.LEFT,
    Direction.LEFT: Direction.DOWN,
    Direction.DOWN: Direction.RIGHT,
    Direction.RIGHT: Direction.UP,
}

RIGHT_TURNS: dict[Direction, Direction] = {
    Direction.UP: Direction.RIGHT,
    Direction.RIGHT: Direction.DOWN,
    Direction.DOWN: Direction.LEFT,
    Direction.LEFT: Direction.UP,
}


def initial_state(
    width: int,
    height: int,
    fruit: Position,
) -> Result[GameState, GameError]:
    if width < 10 or height < 5:
        return Err(GameError.INVALID_BOARD)

    center = Position(width // 2, height // 2)

    snake = Snake(
        body=(
            center,
            Position(center.x - 1, center.y),
            Position(center.x - 2, center.y),
        ),
        direction=Direction.RIGHT,
    )

    if fruit in snake.body:
        return Err(GameError.INVALID_FRUIT)

    return Ok(
        GameState(
            board=Board(width, height),
            snake=snake,
            fruit=fruit,
            score=0,
            running=True,
        )
    )


def turn_direction(direction: Direction, turn: Turn) -> Direction:
    match turn:
        case Turn.LEFT:
            return LEFT_TURNS[direction]

        case Turn.RIGHT:
            return RIGHT_TURNS[direction]

        case Turn.NONE:
            return direction


def wrap_position(position: Position, board: Board) -> Position:
    return Position(
        x=position.x % board.width,
        y=position.y % board.height,
    )


def next_head(
    snake: Snake,
    board: Board,
    turn: Turn,
) -> tuple[Position, Direction]:
    new_direction = turn_direction(snake.direction, turn)
    moved_head = snake.head.move(new_direction)
    wrapped_head = wrap_position(moved_head, board)

    return wrapped_head, new_direction


def has_self_collision(body: tuple[Position, ...]) -> bool:
    head, *tail = body
    return head in tail


def has_eaten_fruit(head: Position, fruit: Position) -> bool:
    return head == fruit


def move_body(
    body: tuple[Position, ...],
    new_head: Position,
    grow: bool,
) -> tuple[Position, ...]:
    if grow:
        return (new_head,) + body

    return (new_head,) + body[:-1]


def speed_for_score(score: int) -> float:
    """
    Retorna o intervalo entre atualizações.

    Quanto menor o intervalo, maior a velocidade.
    A velocidade possui um limite para o jogo continuar jogável.
    """
    return max(0.05, 0.18 - score * 0.01)


def available_positions(state: GameState) -> tuple[Position, ...]:
    occupied = set(state.snake.body)

    return tuple(
        Position(x, y)
        for y in range(state.board.height)
        for x in range(state.board.width)
        if Position(x, y) not in occupied
    )


def stop_game(state: GameState) -> GameState:
    return GameState(
        board=state.board,
        snake=state.snake,
        fruit=state.fruit,
        score=state.score,
        running=False,
    )


def advance(
    state: GameState,
    turn: Turn,
    replacement_fruit: Position,
) -> Result[GameState, GameError]:
    """
    Avança o jogo em um passo.

    Essa função é pura:
    - não lê teclado;
    - não imprime;
    - não usa números aleatórios;
    - não altera o estado recebido.
    """

    new_head, new_direction = next_head(
        state.snake,
        state.board,
        turn,
    )

    ate_fruit = has_eaten_fruit(new_head, state.fruit)

    new_body = move_body(
        body=state.snake.body,
        new_head=new_head,
        grow=ate_fruit,
    )

    if has_self_collision(new_body):
        return Err(GameError.SELF_COLLISION)

    new_fruit = replacement_fruit if ate_fruit else state.fruit

    if new_fruit in new_body:
        return Err(GameError.INVALID_FRUIT)

    new_snake = Snake(
        body=new_body,
        direction=new_direction,
    )

    return Ok(
        GameState(
            board=state.board,
            snake=new_snake,
            fruit=new_fruit,
            score=state.score + int(ate_fruit),
            running=True,
        )
    )