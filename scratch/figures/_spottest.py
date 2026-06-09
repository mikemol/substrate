import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import bpy
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)
B.reset()
B.scene(samples=128)
bpy.context.scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
# Tiny object so the corner-to-corner beams clear it and land on the walls.
B.sphere((0, 0, 0), 0.2, B.material("#888888", rough=0.5))
data = B.join_data()
B.driven_rig(data, direction=(0.8, -0.7, 0.55))
B.render("spot_test")
