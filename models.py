from typing import NamedTuple
from enum import Enum


class Position(NamedTuple):
    x: int
    y: int

    def move(self, direction: "Direction") -> "Position":
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)


class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


class Turn(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class GameError(Enum):
    SELF_COLLISION = "a cobra colidiu com ela mesma"
    INVALID_FRUIT = "fruta foi posicionada em posição inválida"
    INVALID_BOARD = "tabuleiro dimensionado em posições inválidas"


class Board(NamedTuple):
    width: int
    height: int

    def contains(self, position: Position) -> bool:
        return (
            0 <= position.x < self.width
            and 0 <= position.y < self.height
        )


class Snake(NamedTuple):
    body: tuple[Position, ...]
    direction: Direction

    @property
    def head(self) -> Position:
        return self.body[0]


class GameState(NamedTuple):
    board: Board
    snake: Snake
    fruit: Position
    score: int
    running: bool