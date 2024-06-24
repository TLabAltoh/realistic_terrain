import bpy
import bmesh
import math
import numpy as np

import os
addon_dirpath = os.path.dirname(__file__)

from realistic_terrain import dx11_erosion

#
# Erode
#

class tlab_terrain_erode_settings(bpy.types.Operator):  
    bl_idname = "tlab_terrain.erode_settings"
    bl_label = "Erode Settings"
    bl_description = "Erode Settings"
    bl_options = {'REGISTER', 'UNDO'}

    # erode settings
    size : bpy.props.FloatProperty(name = "size: ", default = 20.0)
    elevationm_size : bpy.props.FloatProperty(name = "elevationm_size: ", default = 10.0);

    numErosionIterations : bpy.props.IntProperty(name = "numErosionIterations: ", default = 50000);
    erosionBrushRadius : bpy.props.IntProperty(name = "erosionBrushRadius: ", default = 3);

    maxLifetime : bpy.props.IntProperty(name = "maxLifetime: ", default = 30)
    inertia : bpy.props.FloatProperty(name = "inertia: ", default = 0.3)
    sedimentCapacityFactor : bpy.props.FloatProperty(name = "sedimentCapacityFactor: ", default = 3.0)
    minSedimentCapacity : bpy.props.FloatProperty(name = "minSedimentCapacity: ", default = 0.01)
    depositSpeed : bpy.props.FloatProperty(name = "depositSpeed: ", default = 0.3)
    erodeSpeed : bpy.props.FloatProperty(name = "erodeSpeed", default = 0.3)

    evaporateSpeed : bpy.props.FloatProperty(name = "evaporateSpeed: ", default = 0.01)
    gravity : bpy.props.FloatProperty(name = "gravity: ", default = 4.0)
    startSpeed : bpy.props.FloatProperty(name = "startSpeed: ", default = 1.0)
    startWater : bpy.props.FloatProperty(name = "startWater: ", default = 1.0)
    # end of erode settings

    def execute(self, context):
        print("Process Erode")
        # for each selected object
        for obj in bpy.context.selected_objects:
            # enter edit mode.
            bpy.ops.object.mode_set(mode='EDIT')
            
            # object name
            #print("name: ", obj.name)
            #print("object.data.name: ", obj.data.name)
            
            # vertices count
            vertices = obj.data.vertices
            vertices_count = len(vertices)
            #print("len(vertices): ", vertices_count)
            
            # vertices sqrt check
            sqrt = math.sqrt(vertices_count)
            #print("math.sqrt(vertices_count): ", sqrt)
            if (sqrt != int(sqrt)):
                print("[error] the number of vertices is not n squared.")
                bpy.ops.object.mode_set(mode='OBJECT')
                return
            
            # get mesh data
            mesh_data = bmesh.from_edit_mesh(obj.data)
            #print("mesh_data: ", mesh_data)
            
            # np input buffer
            z = []
            for v in mesh_data.verts:
                z.append(v.co[2])
                
            input = np.array(z)
            
            result = dx11_erosion.erosion(
                        int(sqrt),
                        self.size,
                        self.elevationm_size,
                        self.numErosionIterations,
                        self.erosionBrushRadius,
                        self.maxLifetime,
                        self.inertia,
                        self.sedimentCapacityFactor,
                        self.minSedimentCapacity,
                        self.depositSpeed,
                        self.erodeSpeed,
                        self.evaporateSpeed,
                        self.gravity,
                        self.startSpeed,
                        self.startWater,
                        input,
                        addon_dirpath)
            
            # set smoothed z
            i = 0
            for v in mesh_data.verts:
                v.co[2] = result[i]
                i += 1

            # switch back to object mode.
            bpy.ops.object.mode_set(mode='OBJECT')

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class tlab_terrain_process_erode(bpy.types.Operator):
    bl_idname = "tlab_terrain.process_erode"
    bl_label = "Erode Process"
    bl_description = "Process Erode Simulation"
    
    def execute(self, context):
        bpy.ops.tlab_terrain.erode_settings("INVOKE_DEFAULT")
        return {"FINISHED"}


class TLAB_TERRAIN_MT_erode(bpy.types.Menu):
    bl_label = "Erode"
    
    def draw(self, context):
        self.layout.operator("tlab_terrain.process_erode", text="Process")