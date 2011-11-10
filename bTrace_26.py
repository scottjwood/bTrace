'''
BEGIN GPL LICENSE BLOCK

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

END GPL LICENCE BLOCK
'''

bl_info = {
    "name": "bTrace",
    "author": "Liero 'Original Author' | crazycourier 'Contributor'",
    "version": (0, 5, ),
    "blender": (2, 5, 6),
    "api": 36064,
    "category": "Mesh",
    "location": "View3D > Tools",
    "warning": "Still under development, bug reports appreciated",
    "wiki_url": "",
    "tracker_url": ""
   }

'''
Simple script to convert mesh into curves.
Script has four main functions:
1. Trace the verts of an object to create a curve
2. Connect each selected object by a single curve, the anchor points of
the curve are hooked to the respective object centers
3. Trace the path of particles with a curve
4. Add random F-Curve noise to any object
'''

import bpy
from bpy.props import *


class TracerProperties(bpy.types.PropertyGroup):
    enabled = bpy.props.IntProperty(default=0)
    
    # Brush Spline properties
    TRbrushSplineType = bpy.props.EnumProperty(name="Spline",
        items=(("POLY", "Poly", "Use Poly spline type"),
            ("NURBS", "Nurbs", "Use Nurbs spline type"),
            ("BEZIER", "Bezier", "Use Bezier spline type")),
        description="Choose which type of spline to use when curve is created",
        default="BEZIER")
    
    # Brush Handle properties
    TRbrushHandleType = bpy.props.EnumProperty(name="Handle",
        items=(("ALIGNED", "Aligned", "Use Aligned Handle Type"),
            ("AUTOMATIC", "Automatic", "Use Auto Handle Type"),
            ("FREE_ALIGN", "Free Align", "Use Free Handle Type"),
            ("VECTOR", "Vector", "Use Vector Handle Type")),
        description="Choose which type of handle to use when curve is created",
        default="VECTOR")
    # Brush Curve Settings
    TRbrush_resolution = bpy.props.IntProperty(name="Bevel Resolution", description="Adjust the Bevel resolution" , min=1, max=32, default=4)
    TRbrush_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100.0, default=0.125, description="Adjust the Bevel depth")
    TRbrush_noise = bpy.props.FloatProperty(name="Noise", min=0.0, max=50.0, default=0.00, description="Adjust noise added to mesh before adding curve")
    
    # Option to Duplicate Mesh
    TRbrushDuplicate = bpy.props.BoolProperty(name="Apply to copy of object", default=False, description="Apply curve to a copy of object")
    
    # Object Handle properties    
    TRobjectHandleType = bpy.props.EnumProperty(name="Handle",
        items=(("FREE", "Free", "Use Free Handle Type"),
            ("AUTO", "Auto", "Use Auto Handle Type"),
            ("ALIGNED", "Aligned", "Use Aligned Handle Type"),
            ("VECTOR", "Vector", "Use Vector Handle Type")),
        description="Choose which type of handle to use when curve is created",
        default="VECTOR")
    
    # Object Curve Settings
    TRobject_resolution = bpy.props.IntProperty(name="Bevel Resolution", min=1, max=32, default=3, description="Adjust the Bevel resolution")
    TRobject_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100., default=0.125, description="Adjust the Bevel depth")
    
    # Particle Step Size    
    TRparticle_step = bpy.props.IntProperty(name="Step Size", min=1, max=15, default=5, description="Adjust the step size")
    
    # Particle Curve Setting
    TRparticle_resolution = bpy.props.IntProperty(name="Bevel Resolution", min=1, max=32, default=3, description="Adjust the Bevel resolution")
    TRparticle_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100., default=0.125, description="Adjust the Bevel depth")
    
    # F-Curve Modifier Properties
    TRfcnoise_rot = bpy.props.BoolProperty(name="Rotation", default=False, description="Affect Rotation")
    TRfcnoise_loc = bpy.props.BoolProperty(name="Location", default=True, description="Affect Location")
    TRfcnoise_scale = bpy.props.BoolProperty(name="Scale", default=False, description="Affect Scale")
    
    TRfcnoise_amp = bpy.props.IntProperty(name="Amp", min=1, max=500, default=5, description="Adjust the amplitude")
    TRfcnoise_timescale = bpy.props.FloatProperty(name="Time Scale", min=1, max=500, default=50, description="Adjust the time scale")
    
    #  Add Keyframe setting for F-Curve
    TRfcnoise_key = bpy.props.BoolProperty(name="Add Keyframe", default=False, description="Keyframe is needed for tool, this adds a LocRotScale keyframe")

# attempt to make controls dynamic
def curveBevelControl():
    bTrace=bpy.context.window_manager.curve_tracer
    obj.data.bevel_depth = bTrace.TRbrush_depth
    
    
    
# Draw Brush panel in Toolbar
class addTracerBrushPanel(bpy.types.Panel):
    bl_label = "bTrace: Brush"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        bTrace=bpy.context.window_manager.curve_tracer
        
        # Box for Brush Trace
        box = self.layout.box()
        box.prop(bTrace, "TRbrushSplineType")
        box.prop(bTrace, "TRbrushHandleType")
        col = box.column(align=True)
        col.prop(bTrace, "TRbrush_resolution")
        col.prop(bTrace, "TRbrush_depth")
        col.prop(bTrace, "TRbrush_noise")
        box.prop(bTrace, "TRbrushDuplicate")
        box.operator("object.brushtrace", text="Trace it!", icon="FORCE_MAGNETIC")
        row = self.layout.row()
        
 # Draw Multi-Object panel in Toolbar
class addTracerMultiobjectPanel(bpy.types.Panel):
    bl_label = "bTrace: Multi-object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        bTrace=bpy.context.window_manager.curve_tracer
        
        # Box for Object Trace
        box = self.layout.box()
        box.prop(bTrace, "TRobjectHandleType")
        col = box.column(align=True)
        col.prop(bTrace, "TRobject_resolution")
        col.prop(bTrace, "TRobject_depth")
        box.operator("object.objecttrace", text="Connect the dots!", icon="OUTLINER_OB_EMPTY")
        row = self.layout.row()

# Draw Particle panel in Toolbar
class addTracerParticlePanel(bpy.types.Panel):
    bl_label = "bTrace: Particle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        bTrace=bpy.context.window_manager.curve_tracer        
        # Box for Particle Trace
        box = self.layout.box()
        col = box.column(align=True)
        col.prop(bTrace, "TRparticle_resolution")
        col.prop(bTrace, "TRparticle_depth")
        col.prop(bTrace, "TRparticle_step")
        box.operator("object.particletrace", text="Chase 'em!", icon="PARTICLES")
        row = self.layout.row()

# Draw F-Curve panel in Toolbar
class addTracerFcurvePanel(bpy.types.Panel):
    bl_label = "bTrace: F-Curve Noise"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        bTrace=bpy.context.window_manager.curve_tracer        
        
        box = self.layout.box()
        row = box.row(align=True)
        row.prop(bTrace, "TRfcnoise_rot")
        row.prop(bTrace, "TRfcnoise_loc")
        row.prop(bTrace, "TRfcnoise_scale")
        col = box.column(align=True)
        col.prop(bTrace, "TRfcnoise_amp")
        col.prop(bTrace, "TRfcnoise_timescale")
        box.prop(bTrace, "TRfcnoise_key")
        box.operator("object.fcnoise", text="Make Some Noise!", icon="RNDCURVE")
        

################## ################## ################## ############
## Brush Trace
## creates a curve with a modulated radius joining points of a mesh
## this emulates some brush traces - maybe work on a copy of object
################## ################## ################## ############

class OBJECT_OT_brushtrace(bpy.types.Operator):
    bl_idname = "object.brushtrace"
    bl_label = "Brush Trace"
    bl_description = "Creates a curve with a modulated radius joining points of a mesh."
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        import bpy, random, mathutils
        from mathutils import Vector
        
        noise_vertices = False # add pre-noise to geometry  
        modular_curve = True    # modulate the resulting curve
        TRbrushHandle = bpy.context.window_manager.curve_tracer.TRbrushHandleType # Get Handle selection
        TRbrushSpline = bpy.context.window_manager.curve_tracer.TRbrushSplineType # Get Spline selection
        TRBrushDupli = bpy.context.window_manager.curve_tracer.TRbrushDuplicate # Get duplicate check setting
        TRbrushrez = bpy.context.window_manager.curve_tracer.TRbrush_resolution # Get Bevel resolution 
        TRbrushdepth = bpy.context.window_manager.curve_tracer.TRbrush_depth # Get Bevel Depth
        TRbrushnoise = bpy.context.window_manager.curve_tracer.TRbrush_noise # Get Bevel Depth
        
        # This duplicates the Mesh
        if TRBrushDupli == True:
            bpy.ops.object.duplicate_move()
        
        # add noise to mesh
        def mover(obj):
            scale = TRbrushnoise 
            for v in obj.data.vertices:
                for u in range(3):
                    v.co[u] += scale*(random.random()*2-1)
        
        # continuous edge through all vertices
        def draw(obj):
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='EDGE_FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
            ver = obj.data.vertices
            bpy.ops.object.mode_set()
            li = []
            p1 = int(random.random()*(1+len(ver)))
            for v in ver: li.append(v.index)
            li.remove(p1)
            for z in range(len(li)):
                x = 999
                for px in li:
                    d = ver[p1].co - ver[px].co
                    if d.length < x:
                        x = d.length
                        p2 = px
                ver[p1].select = ver[p2].select = True
                bpy.ops.object.editmode_toggle()
                bpy.context.tool_settings.mesh_select_mode = [True, False, False]
                bpy.ops.mesh.edge_face_add()
                bpy.ops.object.editmode_toggle()
                ver[p1].select = ver[p2].select = False
                li.remove(p2)
                p1 = p2
        
        # convert edges to curve and add a material
        def curve(obj):
            bpy.ops.object.mode_set()
            bpy.ops.object.convert(target='CURVE')
            bpy.ops.object.editmode_toggle()
            # Set spline type to custom property in panel
            bpy.ops.curve.spline_type_set(type=TRbrushSpline) 
            # Set handle type to custom property in panel
            bpy.ops.curve.handle_type_set(type=TRbrushHandle) 
            bpy.ops.object.editmode_toggle()
            obj.data.fill_mode = 'FULL'
            # Set resolution to custom property in panel
            obj.data.bevel_resolution = TRbrushrez 
            obj.data.resolution_u = 12 
            # Set depth to custom property in panel
            obj.data.bevel_depth = TRbrushdepth 
            
            if 'TraceMat' not in bpy.data.materials:
                TraceMat = bpy.data.materials.new('TraceMat')
                TraceMat.diffuse_color = ([.02]*3)
                TraceMat.specular_intensity = 0
            obj.data.materials.append(bpy.data.materials.get('TraceMat'))
        
        # modulate curve radius
        def modular(obj):
            scale = 3
            for u in obj.data.splines:
                for v in u.bezier_points:
                    v.radius = scale*round(random.random(),3)
        
        # start
        obj = bpy.context.object
        if obj and obj.type == 'MESH':
            mover(obj)
            draw (obj)
            curve(obj)
            if modular_curve: 
                modular(obj)
        
        return{"FINISHED"}


################## ################## ################## ############
## Object Trace
## join selected objects with a curve + hooks to each node
## possible handle types: 'FREE' 'AUTO' 'VECTOR' 'ALIGNED'
################## ################## ################## ############


class OBJECT_OT_objecttrace(bpy.types.Operator):
    bl_idname = "object.objecttrace"
    bl_label = "Object Trace"
    bl_description = "Join selected objects with a curve and add hooks to each node."
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        import bpy
        lista = []
        TRobjectHandle = bpy.context.window_manager.curve_tracer.TRobjectHandleType # Get Handle selection
        TRobjectrez = bpy.context.window_manager.curve_tracer.TRobject_resolution # Get Bevel resolution 
        TRobjectdepth = bpy.context.window_manager.curve_tracer.TRobject_depth # Get Bevel Depth
        
        # list objects
        for a in bpy.context.selected_objects:
            lista.append(a)
            a.select = False

        # trace the origins
        tracer = bpy.data.curves.new('tracer','CURVE')
        tracer.dimensions = '3D'
        spline = tracer.splines.new('BEZIER')
        spline.bezier_points.add(len(lista)-1)
        curva = bpy.data.objects.new('curva',tracer)
        bpy.context.scene.objects.link(curva)

        # render ready curve
        tracer.resolution_u = 64
        tracer.bevel_resolution = TRobjectrez # Set  belel resolution from Panel options
        tracer.fill_mode = 'FULL'
        tracer.bevel_depth = TRobjectdepth # Set bevel depth from Panel options
        mat = bpy.data.materials.new('blue')
        mat.diffuse_color = [0,.5,1]
        mat.use_shadeless = True
        tracer.materials.append(mat)

        # move nodes to objects
        for i in range(len(lista)):
            p = spline.bezier_points[i]
            p.co = lista[i].location
            p.handle_right_type=TRobjectHandle
            p.handle_left_type=TRobjectHandle

        bpy.context.scene.objects.active = curva
        bpy.ops.object.mode_set()

        # place hooks
        for i in range(len(lista)):
            lista[i].select = True
            curva.data.splines[0].bezier_points[i].select_control_point = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.hook_add_selob()
            bpy.ops.object.editmode_toggle()
            curva.data.splines[0].bezier_points[i].select_control_point = False
            lista[i].select = False

        for a in lista : a.select = True
    
        return{"FINISHED"}


################## ################## ################## ############
## Particle Trace
## particle tracer - creates a curve from each particle of a system
## simple setting: Start/End = 1 | Amount<250 | play with Effectors
################## ################## ################## ############

class OBJECT_OT_particletrace(bpy.types.Operator):
    bl_idname = "object.particletrace"
    bl_label = "Particle Trace"
    bl_description = "Creates a curve from each particle of a system. Keeping particle amount under 250 will make this run faster."
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        import bpy
        
        paso = bpy.context.window_manager.curve_tracer.TRparticle_step    # step size in frames
        TRparticlerez = bpy.context.window_manager.curve_tracer.TRparticle_resolution # Get Bevel resolution 
        TRparticledepth = bpy.context.window_manager.curve_tracer.TRparticle_depth # Get Bevel Depth
        
        obj = bpy.context.object
        if obj.particle_systems:
            ps = obj.particle_systems[0]
            mat = bpy.data.materials.new('mat')
            mat.diffuse_color = [1,.5,0]
            mat.emit = 0.5
            for x in ps.particles:
                tracer = bpy.data.curves.new('tracer','CURVE') #
                tracer.dimensions = '3D'
                spline = tracer.splines.new('BEZIER')
                spline.bezier_points.add((x.lifetime-1)//paso) #add point to spline based on 
                curva = bpy.data.objects.new('path.000',tracer)
                bpy.context.scene.objects.link(curva)
                for t in list(range(int(x.lifetime))):
                    bpy.context.scene.frame_set(t+x.birth_time)
                    if not t%paso:            
                        p = spline.bezier_points[t//paso]
                        p.co = x.location
                        p.handle_right_type='AUTO'
                        p.handle_left_type='AUTO'            
                tracer.materials.append(mat)
                tracer.bevel_resolution = TRparticlerez # get resolution from panel
                tracer.fill_mode = 'FULL'
                tracer.bevel_depth = TRparticledepth # get depth from panel
        return{"FINISHED"}


################## ################## ################## ############
## F-Curve Noise
## will add noise modifiers to each selected object f-curves
## change type to: 'rotation' | 'location' | 'scale' | '' to effect all
## first record a keyframe for this to work (to generate the f-curves)
################## ################## ################## ############

class OBJECT_OT_fcnoise(bpy.types.Operator):
    bl_idname = "object.fcnoise"
    bl_label = "F-curve Noise"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        import bpy, random
        
        bTrace = bpy.context.window_manager.curve_tracer
        TR_amp = bTrace.TRfcnoise_amp
        TR_timescale = bTrace.TRfcnoise_amp
        TR_addkeyframe = bTrace.TRfcnoise_key
        
        # This sets properties for Loc, Rot and Scale if they're checked in the Tools window
        noise_rot = 'rotation'
        noise_loc = 'location'
        noise_scale = 'scale'
        if not bTrace.TRfcnoise_rot:
            noise_rot = 'none'
        if not bTrace.TRfcnoise_loc:
            noise_loc = 'none'
        if not bTrace.TRfcnoise_scale:
            noise_scale = 'none'
            
        type = noise_loc, noise_rot, noise_scale # Add settings from panel for type of keyframes
        amplitude = TR_amp
        time_scale = TR_timescale
        
        # Add keyframes, this is messy and should only add keyframes for what is checked
        if TR_addkeyframe == True:
            bpy.ops.anim.keyframe_insert(type="LocRotScale") 
        
        for obj in bpy.context.selected_objects:
            if obj.animation_data:
                for c in obj.animation_data.action.fcurves:
                    if c.data_path.startswith(type):
                        # clean modifiers
                        for m in c.modifiers : c.modifiers.remove(m)
                        # add noide modifiers
                        n = c.modifiers.new('NOISE')
                        n.strength = amplitude
                        n.scale = time_scale
                        n.phase = int(random.random() * 999)
        return{"FINISHED"}

## Start Atoms Curve script modifications
## Atom has contributed a significant amount of code to the community. You can see more
## of his work here: http://blenderartists.org/forum/showthread.php?214197-Atom-s-Link-Page
import bpy
import threading
import time

from mathutils import Vector

# Global busy flag.
isBusy = False
lastFrame = -1

############################################################################
# Colorized logging class.
############################################################################
import platform

import logging
import logging.handlers

log_file_name = 'atoms_frame_change.log'

# Set up a specific logger with our desired output level
bt_logger = logging.getLogger('FrameChangeLogger')
bt_logger.setLevel(logging.DEBUG)

# The rotating file handler keeps only the last line (actually 32 bytes) written to the log.
# The last line is examined for the thread name displayed by the loggin formatter,
# which is used to determine if we are rendering.
handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=32, backupCount=0)
f  = logging.Formatter('(%(threadName)-10s) %(message)s')
handler.setFormatter(f)
bt_logger.addHandler(handler)

if platform.system() == "Windows":
    # For windows we need to use ctypes win32.dll
    import ctypes

class console:
    PREFIX = "  "
    CONSOLE_PREFIX = ""
    CONSOLE_SEPARATOR = ""
    CONSOLE_HANDLE = None
    CONSOLE_COLOR_CLEAR = None
    DEBUG = True
    LOGGING = True
    
    # Windows API colors.
    STD_OUTPUT_HANDLE = -11
    FOREGROUND_BLUE_DRK    = 0x0001 # text color contains dark blue.
    FOREGROUND_GREEN_DRK    = 0x0002 # text color contains green.
    FOREGROUND_CYAN_DRK    = 0x0003 # text color contains cyan.
    FOREGROUND_RED_DRK    = 0x0004 # text color contains red.
    FOREGROUND_PLUM = 0x0005 # text color contains purple.
    FOREGROUND_GOLD    = 0x0006 # text color contains gold.
    FOREGROUND_WHITE    = 0x0007 # text color contains white.
    FOREGROUND_GREY    = 0x0008 # text color contains grey.
    FOREGROUND_BLUE    = 0x0009 # text color contains blue.
    FOREGROUND_IVORY    = 0x000f # text color contains ivory.
    FOREGROUND_YELLOW    = 0x000e # text color contains yellow.
    FOREGROUND_PINK    = 0x000d # text color contains pink.
    FOREGROUND_RED    = 0x000c # text color contains red.
    FOREGROUND_CYAN    = 0x000b # text color contains cyan.
    FOREGROUND_GREEN    = 0x000a # text color contains green.
    
    # Linux ANSII colors.
    HEADER = '[95m'
    OKBLUE = '[94m'
    OKGREEN = '[92m'
    WARNING = '[93m'
    FAIL = '[91m'
    ENDC = '[0m'
            
    def get_csbi_attributes(handle):
        # Based on IPython's winconsole.py, written by Alexander Belchenko
        import struct
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
        assert res
    
        (bufx, bufy, curx, cury, wattr,
        left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        return wattr
    
    def __init__(self):
        if (platform.system() == "Linux") or (platform.system() == "Darwin"):
            pass

        if platform.system() == "Windows":
            self.CONSOLE_HANDLE = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
            try:
                self.CONSOLE_COLOR_CLEAR = get_csbi_attributes(self.CONSOLE_HANDLE)
            except:
                pass

    def display(self, passedItem=""):
        if self.DEBUG == True:
            if platform.system() == "Windows":
                # Turn on colorization.
                # Pick a color based upon the contents of passedItem.
                color_to_use = self.FOREGROUND_GREY
                if "begin" in passedItem.lower():
                    color_to_use = self.FOREGROUND_BLUE 
                if "end" in passedItem.lower():
                    color_to_use = self.FOREGROUND_BLUE 
                if "frame" in passedItem.lower():
                    color_to_use = self.FOREGROUND_GREEN_DRK
                if "registry" in passedItem.lower():
                    color_to_use = self.FOREGROUND_CYAN 
                if "update" in passedItem.lower():
                    color_to_use = self.FOREGROUND_IVORY
                if "deferred" in passedItem.lower():
                    color_to_use = self.FOREGROUND_PLUM
                if "?" in passedItem.lower():
                    color_to_use = self.FOREGROUND_CYAN_DRK
                if "warning" in passedItem.lower():
                    color_to_use = self.FOREGROUND_GOLD 
                if "error" in passedItem.lower():
                    color_to_use = self.FOREGROUND_RED 
                ctypes.windll.kernel32.SetConsoleTextAttribute(self.CONSOLE_HANDLE, color_to_use)
            else:
                # Pick a color based upon the contents of passedItem.
                color_to_use = ""
                if "error" in passedItem.lower():
                    color_to_use = self.WARNING 
                if "warning" in passedItem.lower():
                    color_to_use = self.HEADER 
                if "begin" in passedItem.lower():
                    color_to_use = self.OKBLUE 
                if "end" in passedItem.lower():
                    color_to_use = self.OKBLUE 
                if "frame" in passedItem.lower():
                    color_to_use = self.OKGREEN 
                           
            if self.LOGGING == True:
                thread_name = "(" + self.returnThreadingName() + ") "
                if platform.system() == "Windows":
                    print(thread_name + self.CONSOLE_PREFIX + self.CONSOLE_SEPARATOR + passedItem)
                else:
                    #Linux or OSX.
                    print(color_to_use + thread_name + self.CONSOLE_PREFIX + self.CONSOLE_SEPARATOR + passedItem)

            if platform.system() == "Windows":
                # Turn off colorization.
                #ctypes.windll.kernel32.SetConsoleTextAttribute(self.CONSOLE_HANDLE, self.CONSOLE_COLOR_CLEAR)
                pass

    def returnThreadingName (self):
        bt_logger.debug("")
    
        # Read the results back in.
        myFile = open(log_file_name)
        block = myFile.read()
        msg = str(block)
        myFile.close()
        
        n = msg.find(")")
        result = msg[1:n]
        
        return result
                    
    def addToPrefix (self):
        self.CONSOLE_PREFIX = self.PREFIX + self.CONSOLE_PREFIX
        
    def removeFromPrefix (self):
        lCP = int(len(self.CONSOLE_PREFIX))
        lPI = int(len (self.PREFIX))
        if lPI > lCP:
            #Just blank the prefix.
            self.CONSOLE_PREFIX = ""
        else:
            #Chop off from the right by length of passed item.
            n = lCP-lPI
            self.CONSOLE_PREFIX = self.CONSOLE_PREFIX[lPI:]


# Create an instance of the color log class for the entire script to use for display.
btLog = console()

# Put your main frame change code here.
def frameRefesh (passedFrame):
    btLog.display("Update on frame #" + str(passedFrame))
    startPercent = passedFrame/2.0
    endPercent = startPercent + 20.0
    updateTaperCurve ("cu_taper", startPercent, endPercent, 0.2, 0.025)

def updateTaperCurve (passedCurveName, passedPositionPercent, passedTailPercent, passedSlopeStart, passedSlopeEnd): 
    # NOTE: 
    #   passedCurveName is the name of the curve, not the name of the curve object.
    #   passedPositionPercent is where the Taper is going to start along any given curve. (derived by tracking an empty along a curve)
    #   passedTailPercent is where the Taper is going to end along any given curve.
    #   passedSlopeStart is in the range of 0.0 to 1.0. It repesents the slope of the starting point of the taper.
    #   passedSlopeEnd is in the range of 0.0 to 1.0. It represents the slope of the end point of the taper.
    
    # This code relies on the passed curve to have six points that were created by makeTaperCurve.
    spline = bpy.data.curves[passedCurveName].splines[0]
    if len(spline.bezier_points) == 6:
        # 6 points, this curve may have been made by us.
        # We should probably do more bounds checking in here, but lets assume our provided values will keep us in range.
        
        s1 = (passedPositionPercent/100.0)
        p = spline.bezier_points[1]
        p.co = Vector((s1,0.0,0.0))
        
        s2 = s1 + passedSlopeStart          
        p = spline.bezier_points[2]
        p.co = Vector((s2,1.0,0.0))

        e1 = (passedTailPercent/100.0)
        if e1 > 0.99: e1 = 0.99
        p = spline.bezier_points[3]
        p.co = Vector((e1,1.0,0.0))
        
        e2 = e1 + passedSlopeEnd          
        p = spline.bezier_points[4]
        p.co = Vector((e2,0.0,0.0))
                
    else:
        btLog.display("Spline from [" + passedCurveName + "] was not created by makeTaperCurve.")
   
def makeTaperCurve (passedTaperName):
    cu_taper = bpy.data.curves.new("cu_"+passedTaperName,'CURVE')
    cu_taper.dimensions = '2D'
    spline = cu_taper.splines.new('BEZIER')
    spline.bezier_points.add(5)
    taper = bpy.data.objects.new(passedTaperName,cu_taper)
    bpy.data.scenes[0].objects.link(taper)

    #Let's create six points in this curve.
    for n in range(6):
        p = spline.bezier_points[n]
        if n == 0:myLocation = Vector((0.0,0.0,0.0))
        
        # Slope defines shape.
        if n == 1:myLocation = Vector((0.1,0.0,0.0)) # Hook #1 here.
        if n == 2:myLocation = Vector((0.2,1.0,0.0)) # Hook #1 here.
        
        # Slope defines shape.
        if n == 3:myLocation = Vector((0.8,1.0,0.0)) # Hook #2 here.
        if n == 4:myLocation = Vector((0.9,0.0,0.0)) # Hook #2 here.
        
        if n == 5:myLocation = Vector((1.0,0.0,0.0))
        p.co = myLocation
        p.handle_right_type='VECTOR'
        p.handle_left_type='VECTOR'
     
def isRendering ():
    # An attempt trying to detect if we are currently rendering.
    thread_name = btLog.returnThreadingName()
    if thread_name[0:5].lower() == "dummy":
        # Blender launches a dummy thread when rendering.
        return True
    else:
        return False
    '''
    try:
        # If this line generates an error, then we are probably rendering
        name = bpy.context.scene.name
        return False
    except:
        return True   
    '''
  
# Used for a deferred refresh when rendering.
def thread_review(lock, passedFrame,passedSleepTime):
    global isBusy, lastFrame
    
    lastFrame = passedFrame
    time.sleep(passedSleepTime) # Feel free to alter time in seconds as needed.   
    btLog.display("WARNING:" + "DEFERRED refresh for frame:" + str(passedFrame))
    isBusy = True
    frameRefesh(passedFrame)
    isBusy = False  

def frameChange(passedFrame):
    global isBusy, lastFrame
    
    if isBusy == False:
        r = isRendering()
        if r == False:
            # We are probably not rendering.
            if passedFrame != lastFrame:
                # Only process when frames are different.
                isBusy = True
                btLog.display("FRAME:" + str(passedFrame))
                frameRefesh(passedFrame)
                lastFrame = passedFrame
                isBusy = False
        else:
            # When blender is rendering, it launches a "Dummy" thread wich has limited functionality.
            # So the goal here is to abandon this limited thread as quickly as possible.
            # We launch a full-independent thread to handle this refresh in a deferred state. (0.1 seconds is not very long when rendering)
            btLog.display("DEFERRED rendering frame:" + str(passedFrame))
            lock = threading.Lock()
            lock_holder = threading.Thread(target=thread_review, args=(lock,passedFrame,0.1), name='FrameChange_RENDERING_'+ str(int(passedFrame)))
            lock_holder.setDaemon(True)
            lock_holder.start()
    else:
        btLog.display("BUSY frame:" + str(passedFrame))
    return 0.0

bpy.app.driver_namespace['frameChange'] = frameChange                      
    

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