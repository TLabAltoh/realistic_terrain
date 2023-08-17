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

class ErodeSettings(bpy.types.Operator):  
    bl_idname = "talb_terrain.erode_settings"
    bl_label = "Erode Settings"
    bl_description = "Erode Settings"
    bl_options = {'REGISTER', 'UNDO'}

    """
    #
    # definition of cpp side
    #
    
    # default value
    int m_mapSize = 255;
    float m_size = 20;
    float m_elevationm_size = 10;

    int m_numErosionIterations = 50000;
    int m_erosionBrushRadius = 3;

    int m_maxLifetime = 30;
    float m_inertia = 0.3f;
    float m_sedimentCapacityFactor = 3.0f;
    float m_minSedimentCapacity = .01f;
    float m_depositSpeed = 0.3f;
    float m_erodeSpeed = 0.3f;

    float m_evaporateSpeed = .01f;
    float m_gravity = 4;
    float m_startSpeed = 1;
    float m_startWater = 1;


    # cpp erode()
       float maxSize
     , float size
     , float elevationm_size
     , int numErosionIterations
     , int erosionBrushRadius
     , int maxLifetime
     , float inertia
     , float sedimentCapacityFactor
     , float minSedimentCapacity
     , float depositSpeed
     , float erodeSpeed
     , float evaporateSpeed
     , float gravity
     , float startSpeed
     , float startWater)
    """

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
            print("name: ", obj.name)
            print("object.data.name: ", obj.data.name)
            
            # vertices count
            vertices = obj.data.vertices
            vertices_count = len(vertices)
            print("len(vertices): ", vertices_count)
            
            # vertices sqrt check
            sqrt = math.sqrt(vertices_count)
            print("math.sqrt(vertices_count): ", sqrt)
            if (sqrt != int(sqrt)):
                print("[error] the number of vertices is not n squared.")
                bpy.ops.object.mode_set(mode='OBJECT')
                return
            
            # get mesh data
            mesh_data = bmesh.from_edit_mesh(obj.data)
            print("mesh_data: ", mesh_data)
            
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


class ProcessErode(bpy.types.Operator):
    bl_idname = "talb_terrain.erode_process"
    bl_label = "Erode Process"
    bl_description = "Process Erode Simulation"
    
    def execute(self, context):
        bpy.ops.talb_terrain.erode_settings("INVOKE_DEFAULT")
        return {"FINISHED"}


class Erode(bpy.types.Menu):
    bl_label = "Erode"
    
    def draw(self, context):
        self.layout.operator("talb_terrain.erode_process", text="Process")