from dataclasses import dataclass, field
from abc import ABC, abstractmethod


DISCOUNT_PERCENTS = 15


@dataclass(frozen=True)
class Item:
    # note: you might want to change the order of fields
    cost: int
    title: str
    item_id: int

    def __post_init__(self) -> None:
        assert self.title, "Title cannot be empty"
        assert self.cost > 0, "Cost must be positive"


# You may set `# type: ignore` on this class
# It is [a really old issue](https://github.com/python/mypy/issues/5374)
# But seems to be solved
@dataclass
class Position(ABC):
    item: Item

    @property
    @abstractmethod
    def cost(self) -> float:
        pass


@dataclass
class CountedPosition(Position):
    count: int = field(default=1)

    @property
    def cost(self) -> float:
        return self.item.cost * self.count


@dataclass
class WeightedPosition(Position):
    weight: float = field(default=1)

    @property
    def cost(self) -> float:
        return self.item.cost * self.weight


@dataclass
class Order:
    order_id: int
    positions: list[Position]
    have_promo: bool = False

    def __post_init__(self) -> None:
        total_cost = sum(position.cost for position in self.positions)
        if self.have_promo:
            total_cost -= (total_cost * DISCOUNT_PERCENTS) / 100
        self.cost = int(total_cost)
