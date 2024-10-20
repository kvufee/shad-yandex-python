

class LifeGame(object):
    """
    Class for Game life
    """
    def __init__(self, ocean: list[list[int]]) -> None:
        self.ocean = ocean
        self.rows = len(ocean)
        self.cols = len(ocean[0]) if self.rows > 0 else 0

    def get_next_generation(self) -> list[list[int]]:
        next_ocean = [row[:] for row in self.ocean]

        for i in range(self.rows):
            for j in range(self.cols):
                current_cell = self.ocean[i][j]
                neighbours = self._get_neighbours(i, j)

                if current_cell == 2:
                    next_ocean[i][j] = self._update_fish(neighbours)
                elif current_cell == 3:
                    next_ocean[i][j] = self._update_shrimp(neighbours)
                elif current_cell == 0:
                    next_ocean[i][j] = self._spawn_life(neighbours)
        self.ocean = next_ocean
        return self.ocean

    def _get_neighbours(self, i: int, j: int) -> list[int]:
        neighbours = []
        for x in range(max(0, i - 1), min(self.rows, i + 2)):
            for y in range(max(0, j - 1), min(self.cols, j + 2)):
                if (x, y) != (i, j):
                    neighbours.append(self.ocean[x][y])
        return neighbours

    def _update_fish(self, neighbours: list[int]) -> int:
        fish_count = neighbours.count(2)
        if fish_count >= 4 or fish_count <= 1:
            return 0
        return 2

    def _update_shrimp(self, neighbours: list[int]) -> int:
        shrimp_count = neighbours.count(3)
        if shrimp_count >= 4 or shrimp_count <= 1:
            return 0
        return 3

    def _spawn_life(self, neighbours: list[int]) -> int:
        fish_count = neighbours.count(2)
        shrimp_count = neighbours.count(3)
        if fish_count == 3:
            return 2
        if shrimp_count == 3:
            return 3
        return 0
