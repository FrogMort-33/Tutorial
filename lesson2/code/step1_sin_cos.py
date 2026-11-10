# ======================================================================
# LESSON 2 - STEP 1: SIN, COS AND TURNING ONE CORNER (no window yet)
# ----------------------------------------------------------------------
# Goal: check the maths of rotation with plain numbers, BEFORE we
# draw anything. This script only PRINTS. Read the output slowly and
# compare it with the diagrams in the lesson.
#
# Three new ideas:
#
#   1. An ANGLE says how far round something has turned.
#        0 degrees   = not turned at all
#        90 degrees  = a quarter turn
#        180 degrees = a half turn
#        360 degrees = a full turn (back where it started)
#
#   2. Python's maths tools want angles in RADIANS, not degrees.
#      We never work in radians ourselves - we just convert:
#           angle_in_radians = math.radians(angle_in_degrees)
#
#   3. cos and sin tell you where a point lands on a circle of
#      radius 1 after turning by an angle:
#           across (x) = cos(angle)
#           away   (z) = sin(angle)
#
# Run:  python step1_sin_cos.py
# ======================================================================

import math          # Python's built-in maths tools: sin, cos, radians


def tidy(number):
    """Round a number to 3 places so it is easy to read.

    Computers sometimes give tiny leftovers like 6.123e-17 (which means
    0.00000000000000006123 - really just 0) or -0.0 (minus zero, which
    is the same as 0). This turns both into a plain 0.0.
    """
    number = round(number, 3)
    if number == 0:
        number = 0.0
    return number


# ----------------------------------------------------------------------
# PART A: a table of cos and sin for some easy angles
# ----------------------------------------------------------------------
print("PART A: cos and sin for some angles")
print("-----------------------------------")
print("degrees   radians     cos (across)   sin (away)")

for angle_degrees in [0, 30, 45, 60, 90, 180, 270, 360]:
    # Step 1: degrees -> radians (Python needs radians)
    angle_radians = math.radians(angle_degrees)

    # Step 2: ask Python for cos and sin of that angle
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    # tidy() rounds to 3 places (see the top of the file).
    # Radians get 4 places so you can see 3.1416 (that's pi).
    print(str(angle_degrees).rjust(5),
          str(round(angle_radians, 4)).rjust(10),
          str(tidy(cos_a)).rjust(12),
          str(tidy(sin_a)).rjust(12))

print()


# ----------------------------------------------------------------------
# PART B: the rotate_y() function
# ----------------------------------------------------------------------
# This turns ONE 3D point around the y axis (the up-down line through
# the middle of the shape). Picture a chicken on a vertical spit.
#
#   new_x = (x * cos_a) - (z * sin_a)
#   new_y = y                           <- up/down NEVER changes
#   new_z = (x * sin_a) + (z * cos_a)
#
# Seen from ABOVE, a positive angle turns the point ANTICLOCKWISE
# (from +x right, round towards +z away).
#
# The point must be in SHAPE coordinates (measured from the shape's own
# centre), so that it turns around the shape's centre.
def rotate_y(point_3d, angle_degrees):
    """Turn one (x, y, z) point around the y axis by angle_degrees."""
    x, y, z = point_3d

    # Work out cos and sin ONCE, then reuse them.
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    # The rotation rule - read each line from the inside brackets out.
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)

    return (new_x, new_y, new_z)


# ----------------------------------------------------------------------
# PART C: turn corner 5 by hand, showing every step
# ----------------------------------------------------------------------
# Corner 5 is the top-right-front corner of the cube: (1, 1, -1)
# in SHAPE coordinates (from the cube's own centre).
corner_5 = (1, 1, -1)

print("PART C: turning corner 5 = (1, 1, -1)")
print("-------------------------------------")

for angle_degrees in [0, 30, 45, 90]:
    x, y, z = corner_5
    cos_a = math.cos(math.radians(angle_degrees))
    sin_a = math.sin(math.radians(angle_degrees))

    # Each bracket worked out separately, so you can check it by hand.
    x_times_cos = (x * cos_a)
    z_times_sin = (z * sin_a)
    x_times_sin = (x * sin_a)
    z_times_cos = (z * cos_a)

    new_x = (x_times_cos - z_times_sin)
    new_z = (x_times_sin + z_times_cos)

    print("angle =", angle_degrees, "degrees   cos =", tidy(cos_a),
          "  sin =", tidy(sin_a))
    print("   new_x = (x * cos) - (z * sin) = (", tidy(x_times_cos), ") - (",
          tidy(z_times_sin), ") =", tidy(new_x))
    print("   new_y = y                     =", y)
    print("   new_z = (x * sin) + (z * cos) = (", tidy(x_times_sin), ") + (",
          tidy(z_times_cos), ") =", tidy(new_z))

    # Check: a turning point stays the SAME distance from the centre.
    # Distance across the floor = square root of ((x * x) + (z * z)).
    # Before turning it is root(2) = 1.414, and it should stay 1.414.
    distance = math.sqrt((new_x * new_x) + (new_z * new_z))
    print("   distance from the centre (seen from above) =", tidy(distance))
    print()

# Same answers using the function from PART B:
print("rotate_y(corner_5, 30) gives",
      tuple(tidy(n) for n in rotate_y(corner_5, 30)))

# ----------------------------------------------------------------------
# TRY THIS:
#   * Add 120 and 135 to the list in PART A. Which signs (+ or -) do
#     cos and sin have? Check on the unit circle diagram.
#   * In PART C, turn corner 5 by 180. Which corner's place does it land
#     in? (Hint: look at the cube_points list from Lesson 1.)
#   * Turn corner 5 by 360. Did it come back to (1, 1, -1)?
# ----------------------------------------------------------------------
