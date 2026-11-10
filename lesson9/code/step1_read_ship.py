# ======================================================================
# LESSON 9 - STEP 1: READ A SHAPE FROM A TEXT FILE
# ----------------------------------------------------------------------
# Goal: open ship.obj, read it one line at a time, and turn the text
# into the two lists every lesson has used since Lesson 1:
#
#     points  = the corners,  e.g. (0.0, 0.0, 2.0)
#     faces   = which corners make each face,  e.g. (0, 3, 1)
#
# There is NO window in this step. Everything is printed, so you can
# watch each line of the file turn into numbers (lesson Part 2).
#
# What happens to each line of the file:
#
#   "v  0.0  0.6 -1.0"
#      -> .split()  -> ["v", "0.0", "0.6", "-1.0"]     4 pieces of text
#      -> float()   -> (0.0, 0.6, -1.0)                 3 real numbers
#
#   "f 1 4 2"
#      -> .split()  -> ["f", "1", "4", "2"]
#      -> int()     -> 1, 4, 2
#      -> minus 1   -> (0, 3, 1)      .obj counts from 1, Python from 0
#
# This step does only the FIRST of Lesson 9's five changes
# (subtract 1). Step 2 does all five, inside a function load_obj().
#
# Run:  python step1_read_ship.py
#       (ship.obj must be in the same folder as this script)
# ======================================================================

import os

# ---- Where is the file? -----------------------------------------------
# __file__ is the full path of THIS script, for example
#     C:/course/lesson9/code/step1_read_ship.py
# os.path.dirname() cuts off the last part, leaving the folder:
#     C:/course/lesson9/code
# os.path.join() glues the folder and the file name together with the
# right slash for your computer:
#     C:/course/lesson9/code/ship.obj
# So the script finds ship.obj even if you run it from another folder.
CODE_FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CODE_FOLDER, "ship.obj")

points = []     # will hold (x, y, z) for each corner
faces = []      # will hold (corner, corner, corner, ...) for each face

# ---- Read the file, one line at a time ---------------------------------
# "with open(...) as file:" opens the file and closes it again for us
# when the indented block ends.
# "for line in file:" hands us one line of text each time round.
line_number = 0
with open(FILE_PATH) as file:
    for line in file:
        line_number = (line_number + 1)

        # .split() cuts the line at every run of spaces and throws the
        # spaces away:  "v  0.0  0.6 -1.0"  ->  ["v", "0.0", "0.6", "-1.0"]
        # An empty line gives an empty list: [].
        parts = line.split()

        # Empty line, or a comment line starting with "#": skip it.
        # "continue" jumps straight to the next line of the file.
        if len(parts) == 0:
            print("line", line_number, ": (empty)  -> skip")
            continue
        # .startswith("#") is True when the first piece BEGINS with #,
        # so "#" and "#hello" are both caught.
        if parts[0].startswith("#"):
            print("line", line_number, ": comment  -> skip")
            continue

        # ---- A CORNER line: "v x y z" ----------------------------------
        if parts[0] == "v":
            # parts[1], parts[2], parts[3] are still TEXT, like "0.6".
            # float() turns text into a real number:  "0.6" -> 0.6
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            points.append( (x, y, z) )
            # len(points) - 1 is the Python number of the corner we just
            # added: the first v line becomes corner 0.
            print("line", line_number, ":", parts, " -> corner",
                  (len(points) - 1), "=", (x, y, z))

        # ---- A FACE line: "f a b c ..." ---------------------------------
        elif parts[0] == "f":
            corners = []
            # parts[1:] means "every piece from number 1 to the end":
            # ["f", "1", "4", "2"][1:]  ->  ["1", "4", "2"]
            for word in parts[1:]:
                # int() turns text into a whole number: "4" -> 4.
                # CHANGE 1 (lesson Part 3): .obj counts corners from 1,
                # Python counts list items from 0, so subtract 1.
                corners.append( (int(word) - 1) )
            # tuple() freezes the list into a tuple, like Lesson 3's
            # face tuples:  [0, 3, 1] -> (0, 3, 1)
            faces.append(tuple(corners))
            print("line", line_number, ":", parts, " -> face",
                  (len(faces) - 1), "=", tuple(corners))

        # ---- Anything else: skip (step 2 explains which lines) ---------
        else:
            print("line", line_number, ": '" + parts[0] + "' line  -> skip")

# ---- Show what we built ------------------------------------------------
print()
print("points =", points)
print("faces  =", faces)
print()
print(len(points), "corners and", len(faces), "faces")

# ---- The worked example from the lesson ----------------------------------
# The file line "f 1 4 2" is face 0. Its corners in Python are 0, 3, 1:
#   corner 0 = the nose, corner 3 = the top fin, corner 1 = the left wing.
nose_number, top_number, left_number = faces[0]
print()
print("face 0 uses corners", faces[0])
print("   corner", nose_number, "=", points[nose_number], " (the nose)")
print("   corner", top_number, "=", points[top_number], " (the top fin)")
print("   corner", left_number, "=", points[left_number], " (the left wing)")

# ----------------------------------------------------------------------
# What you should see at the end:
#   points = [(0.0, 0.0, 2.0), (-1.5, 0.0, -1.0), (1.5, 0.0, -1.0),
#             (0.0, 0.6, -1.0), (0.0, -0.6, -1.0)]
#   faces  = [(0, 3, 1), (0, 2, 3), (0, 1, 4), (0, 4, 2), (1, 3, 2, 4)]
#   5 corners and 5 faces
#
# TRY THIS:
#   * Change FILE_PATH to "teapot.obj". How many corners and faces?
#     (Expect 3,644 and 6,320, and a LOT of printing. Comment out the
#     two print() lines inside the v and f parts first.)
#   * Take the "- 1" out. Which corner number does face 4 ask for that
#     does not exist? What happens if you try points[5]?
#   * Add a 6th corner to ship.obj, under the nose: "v 0.0 -1.0 1.5".
#     Run again. Is it read? (It is, but no face uses it, so step 2
#     would never draw it.)
# ----------------------------------------------------------------------
