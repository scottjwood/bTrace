#BEGIN GPL LICENSE BLOCK

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

#END GPL LICENCE BLOCK

bl_info = {
    'name': "bTrace",
    'author': "liero, crazycourier",
    'version': (0, 5, ),
    'blender': (2, 6, 0),
    'location': "View3D > Tools",
    'description': "Tools for converting objects particles into curves",
    'warning': "Still under development, bug reports appreciated",
    'wiki_url': "",
    'tracker_url': "",
    'category': "Mesh"
    }

# Simple script to convert mesh into curves.
# Script has four main functions:
# 1. Trace the verts of an object to create a curve
# 2. Connect each selected object by a single curve, the anchor points of
# the curve are hooked to the respective object centers
# 3. Trace the path of particles with a curve
# 4. Add random F-Curve noise to any object

from .bTrace_26 import *
import bpy
from bpy.props import *

classes = [TracerProperties,
    addTracerBrushPanel,
    addTracerMultiobjectPanel,
    addTracerParticlePanel,
    addTracerFcurvePanel,
    OBJECT_OT_brushtrace,
    OBJECT_OT_objecttrace,
    OBJECT_OT_particletrace,
    OBJECT_OT_fcnoise]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.curve_tracer = bpy.props.PointerProperty(type=TracerProperties)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.curve_tracer


if __name__ == "__main__":
    register()
