# ======================================================================
# LESSON 6 - STEP 1: MATRICES BY HAND (no window, just printed numbers)
# ----------------------------------------------------------------------
# Goal: build Lesson 2B's three turns as GRIDS of numbers (matrices),
# and PROVE that they give exactly the same answers as the old
# rotate_x, rotate_y and rotate_z functions.
#
# There is no pygame window in this step. Run it and read what it
# prints. Every number it prints is also worked out by hand on the
# lesson page, so you can tick them off one by one.
#
# What is new:
#
#   1. A MATRIX is a tuple of 3 rows, and each row is a tuple of
#      3 numbers. turn_30[2][0] means "row 2, column 0".
#
#   2. matrix_times_point(matrix, point): each ROW of the matrix is
#      dotted with the point (Lesson 3's dot product) to make one new
#      number. 3 rows -> 3 new numbers -> the new point.
#
#   3. tip_matrix, turn_matrix, roll_matrix: Lesson 2B's three rules,
#      packed into grids. cos and sin are worked out ONCE, when the
#      grid is built, not once for every point.
#
#   4. combine(first, second): ONE grid that does "first, then second".
#
#   5. spin_matrix([tip, turn, roll]): tip, then turn, then roll, as
#      one grid (Lesson 2B's order). It replaces rotate_all. It takes a
#      LIST of 3 angles, like Lesson 5's thing["angles"].
#
# Run:  python step1_matrix_by_hand.py
# ======================================================================

import math


# ---- The OLD way: Lesson 2B's three turns, unchanged -------------------
# We keep them here ONLY to check the new matrices against them.
def rotate_x(point_3d, angle_degrees):
    """TIP one point around the x axis (+y swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = x
    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_y(point_3d, angle_degrees):
    """TURN one point around the y axis (+x swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_z(point_3d, angle_degrees):
    """ROLL one point around the z axis (+x swings toward +y)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    new_z = z
    return (new_x, new_y, new_z)


# ---- The dot product (from Lesson 3, unchanged) ------------------------
def dot(arrow_1, arrow_2):
    """Multiply x by x, y by y, z by z, then add the three together."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


# ======================================================================
# NEW: MATRICES
# ======================================================================

# ---- NEW: the do-nothing matrix (the IDENTITY) -------------------------
# 1s down the diagonal (top-left to bottom-right), 0s everywhere else.
# Row 0 says "keep ALL of x and none of y or z", and so on.
# Any point that goes through it comes out exactly the same.
DO_NOTHING = (
    (1, 0, 0),     # row 0 -> new_x = (1 * x) + (0 * y) + (0 * z) = x
    (0, 1, 0),     # row 1 -> new_y = (0 * x) + (1 * y) + (0 * z) = y
    (0, 0, 1),     # row 2 -> new_z = (0 * x) + (0 * y) + (1 * z) = z
)


def matrix_times_point(matrix, point_3d):
    """NEW: put one point through a matrix.

    Each ROW of the matrix is dotted with the point:
        new_x = row 0 . point
        new_y = row 1 . point
        new_z = row 2 . point

    Worked example (lesson Part 1): turn_matrix(30) x corner 5 (1, 1, -1)
        new_x = (0.866 * 1) + (0 * 1) + (-0.5 * -1)  = 1.366
        new_y = (0 * 1)     + (1 * 1) + (0 * -1)     = 1
        new_z = (0.5 * 1)   + (0 * 1) + (0.866 * -1) = -0.366
    """
    row_0, row_1, row_2 = matrix
    new_x = dot(row_0, point_3d)
    new_y = dot(row_1, point_3d)
    new_z = dot(row_2, point_3d)
    return (new_x, new_y, new_z)


def tip_matrix(angle_degrees):
    """NEW: Lesson 2B's TIP (rotate_x) as a grid.

    The old rule, written with all three letters in every line:
        new_x = (1 * x) + (0 * y)     + (0 * z)
        new_y = (0 * x) + (cos_a * y) + (-sin_a * z)
        new_z = (0 * x) + (sin_a * y) + (cos_a * z)
    The numbers in front of x, y and z ARE the grid.
    """
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (1, 0,     0         ),   # x is the skewer: it never changes
        (0, cos_a, (-sin_a)  ),
        (0, sin_a, cos_a     ),
    )


def turn_matrix(angle_degrees):
    """NEW: Lesson 2's TURN (rotate_y) as a grid.
        new_x = (cos_a * x) + (0 * y) + (-sin_a * z)
        new_y = (0 * x)     + (1 * y) + (0 * z)
        new_z = (sin_a * x) + (0 * y) + (cos_a * z)
    """
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, 0, (-sin_a)),
        (0,     1, 0       ),     # y is the skewer: it never changes
        (sin_a, 0, cos_a   ),
    )


def roll_matrix(angle_degrees):
    """NEW: Lesson 2B's ROLL (rotate_z) as a grid.
        new_x = (cos_a * x) + (-sin_a * y) + (0 * z)
        new_y = (sin_a * x) + (cos_a * y)  + (0 * z)
        new_z = (0 * x)     + (0 * y)      + (1 * z)
    """
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, (-sin_a), 0),
        (sin_a, cos_a,    0),
        (0,     0,        1),     # z is the skewer: it never changes
    )


def column(matrix, column_number):
    """NEW: read one COLUMN of a matrix, top to bottom, as a point.
    Column 0 is where the +x arrow (1, 0, 0) lands, column 1 is where
    +y lands, column 2 is where +z lands (lesson Part 3)."""
    row_0, row_1, row_2 = matrix
    return (row_0[column_number], row_1[column_number], row_2[column_number])


def combine(first, second):
    """NEW: ONE matrix that does 'first', then 'second'.

    The idea (lesson Part 4): a matrix's columns are where the three
    axis arrows land. So take each arrow where 'first' left it (its
    column) and put it through 'second'. Those three answers are the
    columns of the joined matrix.

    Worked example: combine(tip_matrix(30), turn_matrix(30))
        column 0 of tip = (1, 0, 0)
        turn_matrix(30) x (1, 0, 0) = (0.866, 0, 0.5)  -> new column 0
    """
    new_col_0 = matrix_times_point(second, column(first, 0))
    new_col_1 = matrix_times_point(second, column(first, 1))
    new_col_2 = matrix_times_point(second, column(first, 2))
    # We worked out COLUMNS, but a matrix is stored as ROWS, so we read
    # them back across: row 0 is the first number of each column, etc.
    return (
        (new_col_0[0], new_col_1[0], new_col_2[0]),
        (new_col_0[1], new_col_1[1], new_col_2[1]),
        (new_col_0[2], new_col_1[2], new_col_2[2]),
    )


def spin_matrix(angles):
    """NEW: tip, then turn, then roll (Lesson 2B's order) as ONE grid.
    angles is a list of 3 angles in degrees: [tip, turn, roll].
    This does the same job as Lesson 2B's rotate_all, but you build it
    once and then use it on as many points as you like."""
    tip_then_turn = combine(tip_matrix(angles[0]), turn_matrix(angles[1]))
    return combine(tip_then_turn, roll_matrix(angles[2]))


# ======================================================================
# Printing helpers (only to make the output easy to read)
# ======================================================================
def show_point(point_3d):
    """(1.36602540, 1, -0.3660254) -> '(1.366, 1.0, -0.366)'.
    round(..., 3) keeps 3 decimal places, like the lesson page.
    The '+ 0' turns a '-0.0' into a plain '0.0'."""
    x, y, z = point_3d
    return ("(" + str(round(x, 3) + 0) + ", " + str(round(y, 3) + 0) +
            ", " + str(round(z, 3) + 0) + ")")


def show_matrix(name, matrix):
    """Print a matrix as 3 lines, one row per line."""
    print(name)
    for row in matrix:
        print("    ", show_point(row))


def check(label, new_answer, old_answer):
    """Print both answers and say if they match.
    'Match' means every number is within 0.000001 of the other one.
    (Computers store numbers like 0.866 with a tiny rounding error, so
    two ways of getting the same answer can differ in the 15th place.)"""
    same = True
    for k in range(3):
        if abs(new_answer[k] - old_answer[k]) > 0.000001:
            same = False
    if same:
        result = "MATCH"
    else:
        result = "DIFFERENT!"
    print(label)
    print("    matrix:", show_point(new_answer))
    print("    old:   ", show_point(old_answer), "  ->", result)


# ======================================================================
# THE CHECKS (each one is worked by hand on the lesson page)
# ======================================================================
corner_5 = (1, 1, -1)       # top-right-front, SHAPE coordinates

print("=== Part 2: the do-nothing grid ===")
check("DO_NOTHING x corner 5", matrix_times_point(DO_NOTHING, corner_5), corner_5)

print()
print("=== Part 3: turn by 30 as a grid ===")
turn_30 = turn_matrix(30)
show_matrix("turn_matrix(30):", turn_30)
check("turn_matrix(30) x corner 5", matrix_times_point(turn_30, corner_5),
      rotate_y(corner_5, 30))
print("column 0 = where +x lands:", show_point(column(turn_30, 0)))

print()
print("=== Part 3: tip and roll by 30 ===")
check("tip_matrix(30) x corner 5", matrix_times_point(tip_matrix(30), corner_5),
      rotate_x(corner_5, 30))
check("roll_matrix(30) x corner 5", matrix_times_point(roll_matrix(30), corner_5),
      rotate_z(corner_5, 30))

print()
print("=== Part 4: tip then turn, as ONE grid ===")
tip_turn = combine(tip_matrix(30), turn_matrix(30))
show_matrix("combine(tip_matrix(30), turn_matrix(30)):", tip_turn)
check("joined grid x corner 5", matrix_times_point(tip_turn, corner_5),
      rotate_y(rotate_x(corner_5, 30), 30))

print()
print("=== Part 4: all three, spin_matrix([30, 30, 30]) ===")
spin = spin_matrix([30, 30, 30])
show_matrix("spin_matrix([30, 30, 30]):", spin)
old = rotate_z(rotate_y(rotate_x(corner_5, 30), 30), 30)
check("spin_matrix x corner 5", matrix_times_point(spin, corner_5), old)

print()
print("=== Part 4: order matters (90 degrees) ===")
a = combine(tip_matrix(90), turn_matrix(90))
b = combine(turn_matrix(90), tip_matrix(90))
check("tip 90, then turn 90", matrix_times_point(a, corner_5),
      rotate_y(rotate_x(corner_5, 90), 90))
check("turn 90, then tip 90", matrix_times_point(b, corner_5),
      rotate_x(rotate_y(corner_5, 90), 90))

print()
print("=== Part 5: the camera's grid (Lesson 4's worked example) ===")
# You stand at (2, 0, 1), turned left 30, looking level. Corner 5 is
# at WORLD (1, 1, 4). Subtracting gives (-1, 1, 3) (lesson Part 5).
camera_matrix = combine(turn_matrix(-30), tip_matrix(-0))
show_matrix("camera_matrix:", camera_matrix)
check("camera_matrix x (-1, 1, 3)", matrix_times_point(camera_matrix, (-1, 1, 3)),
      rotate_x(rotate_y((-1, 1, 3), -30), -0))

# ----------------------------------------------------------------------
# TRY THIS:
#   * Change every 30 to 45. Do all the checks still say MATCH?
#   * Print turn_matrix(0). Which grid from Part 2 is it?
#   * Make a 'stretch_x' grid ((2, 0, 0), (0, 1, 0), (0, 0, 1)) and put
#     corner 5 through it. Then try combine(stretch_x, turn_30) and
#     combine(turn_30, stretch_x) on corner 5. Same answer?
#   * Print combine(turn_matrix(30), turn_matrix(-30)). Which grid is
#     it, and why? (Turning left 30 then right 30 ...)
# ----------------------------------------------------------------------
