import bpy
import bmesh
import time
import math
import numpy as np

#
# Perlin
#

class PerlinSettings(bpy.types.Operator):
    bl_idname = "tlab_terrain.perlin_settings"
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
    bl_idname = "tlab_terrain.perlin_create"
    bl_label = "Create"
    bl_description = "Create Perlin Noise Grid"
    
    def execute(self, context):
        bpy.ops.tlab_terrain.perlin_settings("INVOKE_DEFAULT")
        return {'FINISHED'}


class Perlin(bpy.types.Menu):
    bl_label = "Perlin"

    def draw(self, context):
        self.layout.operator("tlab_terrain.perlin_create", text="Create")