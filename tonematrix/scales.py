"""Which pitch belongs to which row. Provided, do not modify.

Row 0 is the *top* row of the matrix and has the highest pitch; row
grid_size-1 is the bottom row and has the lowest pitch. Pitches walk up
chromatically like consecutive keys on a piano.
"""

# Frequency of the lowest note (A2 on a piano is 110 Hz, or standard middle C C4 is 261.63 Hz).
# Retaining your original root frequency (77.78 Hz ~ Eb2 / D#2):
_ROOT_HZ = 65.406 # C2, look up the frequency if u want to start at C4 etc. nvm its up there lol

# How many octaves before wrapping back down.
_OCTAVES = 4


# def frequency_for_row(row, grid_size):
#     """Return the frequency in hertz of the string on the given row.

#     Rows are numbered from the top, increasing chromatically by one piano key per row.
#     """
#     if not 0 <= row < grid_size:
#         raise ValueError(f"row {row} out of range for a {grid_size}-row matrix")

#     step = grid_size - 1 - row  # 0 at the bottom row (lowest pitch)
    
#     # Calculate semitones chromatically (1 semitone per step, wrapping every _OCTAVES * 12)
#     max_semitones = _OCTAVES * 12
#     semitones = step % max_semitones
    
#     return _ROOT_HZ * (2.0 ** (semitones / 12.0))

def frequency_for_row(row, grid_size):
    """Return the frequency in hertz for a row.

    Row 0 is the top row (highest pitch).
    Row grid_size-1 is the bottom row (C4, lowest pitch).
    Pitches increase chromatically by one semitone per row upward.
    """
    if not 0 <= row < grid_size:
        raise ValueError(
            f"row {row} out of range for a {grid_size}-row matrix"
        )

    # Bottom row is C4; each row upward adds one semitone.
    semitones = grid_size - 1 - row

    return _ROOT_HZ * (2.0 ** (semitones / 12.0))