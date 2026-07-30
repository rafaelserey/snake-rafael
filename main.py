from __future__ import annotations

import random

from blessed import Terminal
from result import Result

from core import advance, available_positions, initial_state, speed_for_score
from models import Direction, GameError, GameState, Position


BOARD_WIDTH = 40
BOARD_HEIGHT = 18

SNAKE_HEAD = "█"
SNAKE_BODY = "█"
FRUIT = "🍎"
BORDER_HORIZONTAL = "-"
BORDER_VERTICAL = "|"


def random_position(
    width: int,
    height: int,
    forbidden: tuple[Position, ...] = (),
) -> Position:
    available = tuple(
        Position(x, y)
        for y in range(height)
        for x in range(width)
        if Position(x, y) not in forbidden
    )

    if not available:
        raise RuntimeError("Não existem posições livres no tabuleiro.")

    return random.choice(available)


def random_fruit(state: GameState) -> Position:
    positions = available_positions(state)

    if not positions:
        return state.fruit

    return random.choice(positions)


def key_to_direction(key: str) -> Direction | None:
    normalized_key = key.lower()
    key_name = getattr(key, "name", None)

    if normalized_key in ("w", "k") or key_name == "KEY_UP":
        return Direction.UP

    if normalized_key in ("d", "l") or key_name == "KEY_RIGHT":
        return Direction.RIGHT

    if normalized_key in ("s", "j") or key_name == "KEY_DOWN":
        return Direction.DOWN

    if normalized_key in ("a", "h") or key_name == "KEY_LEFT":
        return Direction.LEFT

    return None


def wants_to_quit(key: str) -> bool:
    return (
        key.lower() == "q"
        or getattr(key, "name", None) == "KEY_ESCAPE"
    )


def draw_border(term: Terminal, state: GameState) -> str:
    width = state.board.width
    height = state.board.height

    top = term.move_xy(0, 0) + "+" + BORDER_HORIZONTAL * width + "+"
    bottom = (
        term.move_xy(0, height + 1)
        + "+"
        + BORDER_HORIZONTAL * width
        + "+"
    )

    sides = "".join(
        term.move_xy(0, y)
        + BORDER_VERTICAL
        + term.move_xy(width + 1, y)
        + BORDER_VERTICAL
        for y in range(1, height + 1)
    )

    return top + sides + bottom


def draw_snake(term: Terminal, state: GameState) -> str:
    head, *body = state.snake.body

    head_output = (
        term.move_xy(head.x + 1, head.y + 1)
        + term.bold_green(SNAKE_HEAD)
    )

    body_output = "".join(
        term.move_xy(position.x + 1, position.y + 1)
        + term.green(SNAKE_BODY)
        for position in body
    )

    return head_output + body_output


def draw_fruit(term: Terminal, state: GameState) -> str:
    fruit = state.fruit

    return (
        term.move_xy(fruit.x + 1, fruit.y + 1)
        + term.bold_red(FRUIT)
    )


def draw_status(term: Terminal, state: GameState) -> str:
    status_y = state.board.height + 3

    text = (
        f"Pontuação: {state.score}  "
        f"Velocidade: {1 / speed_for_score(state.score):.1f}  "
        "W/↑: cima  S/↓: baixo  A/←: esquerda  D/→: direita  Q: sair"
    )

    return term.move_xy(0, status_y) + term.clear_eol + text


def render(term: Terminal, state: GameState) -> None:
    screen = (
        term.home
        + term.clear
        + draw_border(term, state)
        + draw_snake(term, state)
        + draw_fruit(term, state)
        + draw_status(term, state)
    )

    print(screen, end="", flush=True)


def show_game_over(
    term: Terminal,
    state: GameState,
    error: GameError | None,
) -> None:
    y = state.board.height + 5

    message = (
        error.value
        if error is not None
        else "O jogo foi interrompido."
    )

    print(
        term.move_xy(0, y)
        + term.clear_eol
        + term.bold(message)
    )

    print(
        term.move_xy(0, y + 1)
        + term.clear_eol
        + f"Pontuação final: {state.score}"
    )


def run_game(term: Terminal, initial: GameState) -> None:
    state = initial
    error: GameError | None = None

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while state.running:
            render(term, state)

            timeout = speed_for_score(state.score)
            key = term.inkey(timeout=timeout)

            if wants_to_quit(key):
                break

            direction = key_to_direction(key)

            replacement_fruit = random_fruit(state)

            result: Result[GameState, GameError] = advance(
                state=state,
                direction=direction,
                replacement_fruit=replacement_fruit,
            )

            if result.is_err():
                error = result.unwrap_err()
                break

            state = result.unwrap()

        render(term, state)
        show_game_over(term, state, error)

        term.inkey(timeout=3)


def main() -> None:
    term = Terminal()

    initial_fruit = random_position(
        width=BOARD_WIDTH,
        height=BOARD_HEIGHT,
        forbidden=(
            Position(BOARD_WIDTH // 2, BOARD_HEIGHT // 2),
            Position(BOARD_WIDTH // 2 - 1, BOARD_HEIGHT // 2),
            Position(BOARD_WIDTH // 2 - 2, BOARD_HEIGHT // 2),
        ),
    )

    result = initial_state(
        width=BOARD_WIDTH,
        height=BOARD_HEIGHT,
        fruit=initial_fruit,
    )

    if result.is_err():
        print(f"Não foi possível iniciar: {result.unwrap_err().value}")
        return

    run_game(term, result.unwrap())


if __name__ == "__main__":
    main()