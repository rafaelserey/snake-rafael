from __future__ import annotations

from result import Err, Ok, Result

from models import (
    Board,
    Direction,
    GameError,
    GameState,
    Position,
    Snake,
)


OPPOSITE_DIRECTIONS: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.RIGHT: Direction.LEFT,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
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


def select_direction(
    current_direction: Direction,
    requested_direction: Direction | None,
) -> Direction:
    """Retorna uma direção válida sem permitir inversão imediata."""
    if requested_direction is None:
        return current_direction

    if requested_direction == OPPOSITE_DIRECTIONS[current_direction]:
        return current_direction

    return requested_direction





def next_head(
    snake: Snake,
    requested_direction: Direction | None,
) -> tuple[Position, Direction]:
    new_direction = select_direction(
        current_direction=snake.direction,
        requested_direction=requested_direction,
    )

    new_head = snake.head.move(new_direction)

    return new_head, new_direction


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
    direction: Direction | None,
    replacement_fruit: Position,
) -> Result[GameState, GameError]:


    new_head, new_direction = next_head(
        snake=state.snake,
        requested_direction=direction,
    )

    if not state.board.contains(new_head):
        return Err(GameError.WALL_COLLISION)

    ate_fruit = has_eaten_fruit(
        head=new_head,
        fruit=state.fruit,
    )

    new_body = move_body(
        body=state.snake.body,
        new_head=new_head,
        grow=ate_fruit,
    )

    if has_self_collision(new_body):
        return Err(GameError.SELF_COLLISION)

    new_fruit = (
        replacement_fruit
        if ate_fruit
        else state.fruit
    )

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
