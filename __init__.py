import bpy
import bmesh
import math
import random
import time
import numpy as np
import os
import sys

addon_dirpath = os.path.dirname(__file__)
sys.path += [addon_dirpath]

import dx11_erosion

bl_info = {
    "name": "realistic terrain",
    "author": "tlabaltoh",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Terrain",
    "description": "Simulation of random terrain generation and rain erosion",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Terrain"
}

#
# Grid
#   

class GridSmooth(bpy.types.Operator):
    bl_idname = "grid.smooth"
    bl_label = "Grid Smooth"
    bl_description = "Smoothes the vertices of the grid"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            # enter edit mode.
            bpy.ops.object.mode_set(mode='EDIT')
            
            print("name: ", obj.name)
            print("object.data.name: ", obj.data.name)
            
            vertices = obj.data.vertices
            vertices_num = len(vertices)
            print("vertices num: ", vertices_num)
            
            mesh_data = bmesh.from_edit_mesh(obj.data)
            print("mesh_data: ", mesh_data)
            
            verts_smoothed = []
            
            # calc smooth z.
            for v in mesh_data.verts:
                connected_vert = []
                for e in v.link_edges:
                    v_other = e.other_vert(v)
                    connected_vert.append(v_other.co[2])
                    
                # print(connected_vert)
                # print(type(connected_vert[0]))
                smoothed = sum(connected_vert) / len(connected_vert)
                # print(smoothed)
                verts_smoothed.append(smoothed)
            
            # set smoothed z
            i = 0
            for v in mesh_data.verts:
                v.co[2] = verts_smoothed[i]
                i += 1
            
            # switch back to object mode.
            bpy.ops.object.mode_set(mode='OBJECT')
            
        return {"FINISHED"}

class GridSettings(bpy.types.Operator):  
    bl_idname = "grid.settings"
    bl_label = "Grid Settings"
    bl_description = "Grid Settings"
    bl_options = {'REGISTER', 'UNDO'}

    grid_size : bpy.props.FloatProperty(name = "size: ", default = 20.0)
    grid_res : bpy.props.IntProperty(name = "res: ", default = 50)

    def execute(self, context):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=self.grid_res, y_subdivisions=self.grid_res, size=self.grid_size, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CreateGrid(bpy.types.Operator):
    bl_idname = "grid.create"
    bl_label = "Grid Create"
    bl_description = "Create Grid Mesh"
    
    def execute(self, context):
        bpy.ops.grid.settings("INVOKE_DEFAULT")
        return {"FINISHED"}


class Grid(bpy.types.Menu):
    bl_label = "Grid"
    
    def draw(self, context):
        self.layout.operator("grid.create", text="Create")
        self.layout.operator("grid.smooth", text="Smooth")


#
# Erode
#

class ErodeSettings(bpy.types.Operator):  
    bl_idname = "erode.settings"
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
    bl_idname = "erode.process"
    bl_label = "Erode Process"
    bl_description = "Process Erode Simulation"
    
    def execute(self, context):
        bpy.ops.erode.settings("INVOKE_DEFAULT")
        return {"FINISHED"}


class Erode(bpy.types.Menu):
    bl_label = "Erode"
    
    def draw(self, context):
        self.layout.operator("erode.process", text="Process")


#
# Perlin
#

class PerlinSettings(bpy.types.Operator):
    bl_idname = "perlin.settings"
    bl_label = "Perlin Settings"
    bl_description = "Perlin Settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    maxHeight : bpy.props.IntProperty(name = "maxHeight: ", default = 5)
    maxDetail : bpy.props.IntProperty(name = "maxDetail: ", description="make it power of 2", default = 4)

    # liner interpolation.
    def fade(self, t):return 6*t**5-15*t**4+10*t**3
    def lerp(self, a,b,t):return a+self.fade(t)*(b-a)

    # return perlin noise
    def perlin(self, r, seed=np.random.randint(0,100)):
        np.random.seed(int(time.time()))

        # integer part use as index.
        ri = np.floor(r).astype(int)
        
        # make sure the minimum value is 0.
        ri[0] -= ri[0].min()
        ri[1] -= ri[1].min()
        
        # decimal part. this value is used as a complementary value.
        rf = np.array(r) % 1
        
        # create grid points and set gradient.
        # conversion 0, 1 to -1, 1.
        # the larger the map, the better the number of grids.
        # 2 columns (ri[0].max()+2) * (ri[1].max()+2) set.
        g = 2 * np.random.rand(ri[0].max()+2,ri[1].max()+2,2) - 1
        
        # four corners.
        # 4 dimention array.
        e = np.array([[[[0,0], [0,1], [1,0], [1,1]]]])
        
        # distance vector with each point of the four corners.
        # 3 dimention array to 5 dimention array.
        # 1 row 2 columns r.shape[1] * r.shape[2] * 4 set.
        er = (np.array([rf]).transpose(2,3,0,1) - e).reshape(r.shape[1],r.shape[2],4,1,2)
        
        # gradient of each grad.
        # switch row and columns.
        # 2 row 1 columns r.shape[1] * r.shape[2] * 4 set.
        gr = np.r_["3,4,0",g[ri[0],ri[1]],g[ri[0],ri[1]+1],g[ri[0]+1,ri[1]],g[ri[0]+1,ri[1]+1]].transpose(0,1,3,2).reshape(r.shape[1],r.shape[2],4,2,1)
        
        # calculate the inner product of er and gr.
        # @ is an operator that calculate the inner product of a mtrix defined by numpy.
        p = (er@gr).reshape(r.shape[1],r.shape[2],4).transpose(2,0,1)

        # lerp and return.
        # -1 to 1 --> 0 to 1
        return self.lerp(self.lerp(p[0], p[2], rf[0]), self.lerp(p[1], p[3], rf[0]), rf[1])

    """
    # mesh resolution
    numX = 256
    numY = 256

    maxHeight = 45
    # 
    maxDetail = 16
    scale = 0.5
    radius = 3

    # delete all objects.
    delete_all_objects()
    # create perlin noise map.
    map = create_perlin_noise(numX, maxDetail, maxHeight)
    """

    # return perlin noize
    def create_perlin_noise(self, N, maxDetail, maxHeight):        
        """
        # obviously useless code, but this is finr.
        # calculate the power of 2 for maxDetail.
        maxPower = 0
        while(maxDetail != 1):
            maxDetail = maxDetail / 2
            maxPower += 1
        """
        # N * N array all value is 0.
        y = np.zeros((N,N))

        # perlin noise is sampled at several frequencies and superimposed.
        for power in range(0,maxDetail):
            frequency = 2**power
            amp = 1 / frequency
            
            # arithmetic progression of the range 0 to frequency into N.
            x = np.linspace(0,frequency,N)
        
            # r is array that (2, N, N).
            r = np.array(np.meshgrid(x,x))
            y += self.perlin(r) * amp
        
        # return inverse lerp value multiplyed amplitude.
        return (y  - y.min()) / (y.max() - y.min()) * maxHeight

    def apply_perlin_mesh(self):
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
                return
            
            # get mesh data
            mesh_data = bmesh.from_edit_mesh(obj.data)
            print("mesh_data: ", mesh_data)
            
            # perlin result
            perlin = self.create_perlin_noise(int(sqrt), self.maxDetail, self.maxHeight)
            
            # set smoothed z
            i = 0
            for v in mesh_data.verts:
                x = int(i % sqrt)
                y = int(i / sqrt)
                v.co[2] = perlin[x, y]
                i += 1

            # switch back to object mode.
            bpy.ops.object.mode_set(mode='OBJECT')

    def execute(self, context):
        print("create perlin noise")
        self.apply_perlin_mesh()
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CreatePerlinNoise(bpy.types.Operator):
    bl_idname = "perlin.create"
    bl_label = "Create"
    bl_description = "Create Perlin Noise Grid"
    
    def execute(self, context):
        bpy.ops.perlin.settings("INVOKE_DEFAULT")
        return {'FINISHED'}


class Perlin(bpy.types.Menu):
    bl_label = "Perlin"

    def draw(self, context):
        self.layout.operator("perlin.create", text="Create")


#
# Terrain
#

class Terrain(bpy.types.Menu):
    bl_label = "Terrain"
    
    def draw(self, context):
        self.layout.menu("Grid", icon="MESH_DATA")
        self.layout.menu("Erode", icon="MESH_DATA")
        self.layout.menu("Perlin", icon="MESH_DATA")

#
# Main thread
#

menus = [
    Terrain,
    Grid,
    Erode,
    Perlin
]

classes = [
    GridSettings,
    CreateGrid,
    GridSmooth,
    ErodeSettings,
    ProcessErode,
    PerlinSettings,
    CreatePerlinNoise
]

def menu_fn(self, context):
    self.layout.separator()
    
    # Show UI
    if context.mode == 'OBJECT':
        self.layout.menu("Terrain")


def register():
    
    # Register menu
    for menu in menus:
        try:
            bpy.utils.register_class(menu)
        except ValueError as e:
            bpy.utils.unregister_class(menu)
            bpy.utils.register_class(menu)
            
    # Register class
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)
    
    bpy.types.VIEW3D_MT_editor_menus.append(menu_fn)
    
    print("[realistic-terrain] addon enabled")


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_fn)

    # Unregister menu
    for menu in menus:
        bpy.utils.unregister_class(menu)
        
    # Unregister class
    for cls in classes:
        bpy.utils.unregister_class(cls)

    print("[realistic-terrain] addon disabled")


if __name__ == "__main__":
    register()