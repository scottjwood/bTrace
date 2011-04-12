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
    TRbrush_resolution = bpy.props.IntProperty(name="Bevel Resolution", min=1, max=32, default=4, description="Adjust the Bevel resolution")
    TRbrush_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100., default=0.0125, description="Adjust the Bevel depth")
    
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
    TRobject_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100., default=0.005, description="Adjust the Bevel depth")
    
    # Particle Step Size    
    TRparticle_step = bpy.props.IntProperty(name="Step Size", min=1, max=15, default=5, description="Adjust the step size")
    
    # Particle Curve Setting
    TRparticle_resolution = bpy.props.IntProperty(name="Bevel Resolution", min=1, max=32, default=3, description="Adjust the Bevel resolution")
    TRparticle_depth = bpy.props.FloatProperty(name="Bevel Depth", min=0.0, max=100., default=0.005, description="Adjust the Bevel depth")
    
    # F-Curve Modifier Properties
    TRfcnoise_rot = bpy.props.BoolProperty(name="Rotation", default=False, description="Affect Rotation")
    TRfcnoise_loc = bpy.props.BoolProperty(name="Location", default=True, description="Affect Location")
    TRfcnoise_scale = bpy.props.BoolProperty(name="Scale", default=False, description="Affect Scale")
    
    TRfcnoise_amp = bpy.props.IntProperty(name="Amp", min=1, max=500, default=5, description="Adjust the amplitude")
    TRfcnoise_timescale = bpy.props.FloatProperty(name="Time Scale", min=1, max=500, default=50, description="Adjust the time scale")
    
    #  Add Keyframe setting for F-Curve
    TRfcnoise_key = bpy.props.BoolProperty(name="Add Keyframe", default=False, description="Keyframe is needed for tool, this adds a LocRotScale keyframe")

# Draw panel in Toolbar
class addTracerPanel(bpy.types.Panel):
    bl_label = "Curve Tracer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        bTrace=bpy.context.window_manager.curve_tracer
        
        # Box for Brush Trace
        row = self.layout.row()
        row.label("Brush Trace", icon="FORCE_MAGNETIC")
        box = self.layout.box()
        box.prop(bTrace, "TRbrushSplineType")
        box.prop(bTrace, "TRbrushHandleType")
        row = box.row(align=True)
        row.prop(bTrace, "TRbrush_resolution")
        row.prop(bTrace, "TRbrush_depth")
        box.prop(bTrace, "TRbrushDuplicate")
        box.operator("object.brushtrace", text="Trace it!", icon="FORCE_MAGNETIC")
        row = self.layout.row()
        
        
        # Box for Object Trace
        row = self.layout.row()
        row.label("Multi-Object Trace", icon="OUTLINER_OB_EMPTY")
        box = self.layout.box()
        box.prop(bTrace, "TRobjectHandleType")
        row = box.row(align=True)
        row.prop(bTrace, "TRobject_resolution")
        row.prop(bTrace, "TRobject_depth")
        box.operator("object.objecttrace", text="Connect the dots!", icon="OUTLINER_OB_EMPTY")
        row = self.layout.row()
                
        # Box for Particle Trace
        row = self.layout.row()
        row.label("Particle Trace", icon="PARTICLES")
        box = self.layout.box()
        box.prop(bTrace, "TRparticle_step")
        row = box.row(align=True)
        row.prop(bTrace, "TRparticle_resolution")
        row.prop(bTrace, "TRparticle_depth")
        box.label("Best if particle amount < 250")
        box.operator("object.particletrace", text="Chase 'em!", icon="PARTICLES")
        row = self.layout.row()
        
        # Box for F-Curve Noise
        row = self.layout.row()
        row.label("F-Curve Noise", icon="RNDCURVE")
        box = self.layout.box()
        row = box.row(align=True)
        row.prop(bTrace, "TRfcnoise_rot")
        row.prop(bTrace, "TRfcnoise_loc")
        row.prop(bTrace, "TRfcnoise_scale")
        row = box.row(align=True)
        row.prop(bTrace, "TRfcnoise_amp")
        row.prop(bTrace, "TRfcnoise_timescale")
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
        
        # This duplicates the Mesh
        if TRBrushDupli == True:
            bpy.ops.object.duplicate_move()
        
        # add noise to mesh
        def mover(obj):
            scale = 0.05 
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
            bpy.ops.curve.spline_type_set(type=TRbrushSpline) # Set spline type to custom property in panel
            bpy.ops.curve.handle_type_set(type=TRbrushHandle) # Set handle type to custom property in panel
            bpy.ops.object.editmode_toggle()
            obj.data.use_fill_front = obj.data.use_fill_back = False
            obj.data.bevel_resolution = TRbrushrez # Set resolution to custom property in panel
            obj.data.resolution_u = 12 
            obj.data.bevel_depth = TRbrushdepth # Set depth to custom property in panel
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
            if noise_vertices: 
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
        tracer.use_fill_front = False
        tracer.use_fill_back = False
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
    bl_description = "Creates a curve from each particle of a system."
    
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
                tracer = bpy.data.curves.new('tracer','CURVE')
                tracer.dimensions = '3D'
                spline = tracer.splines.new('BEZIER')
                spline.bezier_points.add((x.lifetime-1)//paso)
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
                tracer.use_fill_front = False
                tracer.use_fill_back = False
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

classes = [TracerProperties,
    addTracerPanel,
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