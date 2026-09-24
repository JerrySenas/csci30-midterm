
"""
Part 4
"""

from tonematrix.audio import SAMPLE_RATE, SAMPLES_PER_COLUMN
from tonematrix.scales import frequency_for_row
from tonematrix.string_instrument import StringInstrument

ON = "#"
OFF = "."


class ToneMatrix:
    def __init__(self, grid_size, sample_rate=SAMPLE_RATE,
                 samples_per_column=SAMPLES_PER_COLUMN):
        """Build an all-off grid_size x grid_size matrix.

        Set up:
          * self.grid          - flat list of grid_size ** 2 False values
          * self.instruments   - one StringInstrument per row, tuned with
                                  frequency_for_row(row, grid_size)
          * self.column        - the column the playhead is about to pluck
          * whatever bookkeeping you need for next_sample() and drag()

        Raise ValueError if grid_size < 1.
        """
        if grid_size < 1:
            raise ValueError

        self.grid_size = grid_size
        self.grid = [False] * grid_size**2
        self.instruments = [StringInstrument(frequency_for_row(row, grid_size)) for row in range(grid_size)]
        self.column = 0
        self.last_press = True
        self.times_sample_called = 0
        self.samples_per_column = samples_per_column
        
        self.lit_cells = [[] for row in range(grid_size)]

    ### indexing

    def index_of(self, row, col):
        """Map a (row, col) pair to its index in the flat list.

        Raise IndexError if the position is off the grid.
        """
        if row < 0 or col < 0 or row >= self.grid_size or col >= self.grid_size:
            raise IndexError
        return self.grid_size * row + col

    def is_on(self, row, col):
        """Provided, once index_of works."""
        return self.grid[self.index_of(row, col)]

    def set_cell(self, row, col, value):
        """Provided, once index_of works."""
        self.grid[self.index_of(row, col)] = bool(value)

    ### editing

    def press(self, row, col):
        """The user clicked this cell: toggle it.

        Also remember what the cell became, so that drag() can copy it.
        """
        cell = self.is_on(row, col)
        self.last_press = not cell

        if self.last_press:
            self.lit_cells[col].append(row)
        else:
            self.lit_cells[col].remove(row)

        self.set_cell(row, col, self.last_press)

    def drag(self, row, col):
        """The user dragged across this cell after a press().

        The cell takes on the same value the pressed cell ended up with: a
        drag that started by switching a cell on paints cells on, and a drag
        that started by switching one off erases.
        """
        if self.last_press:
            self.lit_cells[col].append(row)
        elif self.is_on(row, col):
            self.lit_cells[col].remove(row)
        self.set_cell(row, col, self.last_press)

    def clear(self):
        """Switch every cell off, without replacing the list."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.set_cell(row, col, False)

            self.lit_cells[row] = []

    ### playback

    def next_sample(self):
        """Return the next sample of audio, advancing time by one step.

        On the very first call, and on every samples_per_column-th call after
        that: pluck every lit cell in the current column, then move the
        playhead one column right, wrapping around.

        Every call, including those ones, returns the sum of next_sample()
        over all the instruments.
        """
        if self.times_sample_called == 0:
            self.pluck_column(self.column)
            self.column += 1
            if self.column == self.grid_size:
                self.column = 0

        sum = 0
        for instrument in self.instruments:
            sum += instrument.next_sample()

        self.times_sample_called += 1
        if self.times_sample_called == self.samples_per_column:
            self.times_sample_called = 0
        
        return sum


    def pluck_column(self, col):
        """Pluck the string of every lit row in this column."""
        # for row in range(self.grid_size):
        #     if self.is_on(row, col):
        #         self.instruments[row].pluck()
        for row in self.lit_cells[col]:
            self.instruments[row].pluck()

    ### resizing

    def resize(self, new_size):
        """Change the grid to new_size x new_size.

        Cells present in both the old and new grid keep their values; new
        cells start off. Instruments for rows that survive are reused as-is,
        rows beyond the old size get fresh instruments. The playhead resets
        to column 0 and the next call to next_sample() plucks immediately.

        Raise ValueError if new_size < 1.
        """
        if new_size < 1:
            raise ValueError

        new_grid = []
        if new_size < self.grid_size:
            for row in range(new_size):
                # self.index_of breaks if I do (row, new_size) so we gotta use this weird expression
                new_grid.extend(self.grid[ self.index_of(row, 0) : self.index_of(row, new_size - 1) + 1 ])
            self.grid = new_grid
            self.instruments = self.instruments[:new_size]
            self.lit_cells = self.lit_cells[:new_size]
            for col in self.lit_cells:
                for row in col[::-1]:
                    if row >= new_size:
                        col.remove(row)


        elif new_size > self.grid_size:
            size_diff = new_size - self.grid_size
            # Add pre-existing rows while extending them to new_size
            for row in range(self.grid_size):
                new_grid.extend(self.grid[ self.index_of(row, 0) : self.index_of(row, self.grid_size - 1) + 1 ])
                new_grid.extend([False] * size_diff)

            # Add the new rows
            new_grid.extend([False] * size_diff * new_size)
            self.grid = new_grid
            self.instruments.extend([ StringInstrument(frequency_for_row(self.grid_size + offset, new_size)) for offset in range(size_diff) ])
            self.lit_cells.extend([[] for _ in range(size_diff)])

        self.column = 0
        self.grid_size = new_size
        self.times_sample_called = 0

    ### serialization

    def to_text(self):
        """Render the grid as grid_size lines of '#' and '.'."""
        render = ""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.is_on(row, col):
                    render += ON
                else:
                    render += OFF
            # Add newline after each row except the last one
            if row != self.grid_size - 1:
                render += "\n"
        return render

    @classmethod
    def from_text(cls, text, **kwargs):
        """Build a matrix from the format to_text() produces. Provided."""
        rows = [line.strip() for line in text.strip().splitlines() if line.strip()]
        size = len(rows)
        if any(len(line) != size for line in rows):
            raise ValueError("pattern must be square")

        matrix = cls(size, **kwargs)
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                matrix.set_cell(r, c, ch == ON)
        return matrix

    def __str__(self):
        return self.to_text()
