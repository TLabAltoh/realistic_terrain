import bpy
import bmesh
import math
import numpy as np
from realistic_terrain import opensimplex as simplex

#
# Noise
#

class tlab_terrain_noise_settings(bpy.types.Operator):
    bl_idname = "tlab_terrain.noise_settings"
    bl_label = "Noise Settings"
    bl_description = "Noise Settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    maxHeight : bpy.props.FloatProperty(name = "maxHeight: ", default = 5.0, min = 0.0)

    noiseScale : bpy.props.FloatProperty(
        name = "noiseScale: ", 
        default = 0.5
    )
    
    frequency : bpy.props.FloatProperty(
        name = "frequency: ", 
        default = 2.5, 
        min = 0.0
    )

    lacunarity : bpy.props.FloatProperty(
        name = "lacunarity: ", 
        default = 2.5, 
        min = 0.0
    )

    octaves : bpy.props.IntProperty(
        name = "octaves: ", 
        default = 5,
        min = 1
    )

    weight : bpy.props.FloatProperty(
        name = "weight: ", 
        default = 1.0
    )

    falloffSteepness : bpy.props.FloatProperty(
        name = "falloffSteepness: ", 
        default = 1.0
    )

    falloffOffset : bpy.props.FloatProperty(
        name = "falloffOffset: ", 
        default = 1.0
    )

    waterLevel : bpy.props.FloatProperty(
        name = "waterLevel: ", 
        default = 0.0
    )

    falloff : bpy.props.BoolProperty(name = "falloff: ", default = True) 

    ridge : bpy.props.BoolProperty(name = "ridge: ", default = False) 

    offset : bpy.props.FloatVectorProperty(name = "offset: ", size=2, default = (0.0, 0.0)) 

    # liner interpolation.
    def fade(self, t):return 6*t**5-15*t**4+10*t**3
    def lerp(self, a,b,t):return a+self.fade(t)*(b-a)

    def octaved_ridge_noise(self, x, y, detail):
        noiseVal = 0.0
        amplitude = 1.0
        freq = self.noiseScale
        weight = 1

        for o in range(0, self.octaves):
            v = 1.0 - np.abs(simplex.noise2(x / freq / detail, y / freq / detail))
            v *= v
            v *= weight
            weight = np.clip(v * self.weight, 0.0, 1.0)
            noiseVal += v * amplitude
            
            freq /= self.frequency
            amplitude /= self.lacunarity

        return noiseVal

    def octaved_simplex_noise(self, x, y, detail):
        noiseVal = 0.0
        amplitude = 1.0
        freq = self.noiseScale

        for o in range(0, self.octaves):
            v = (simplex.noise2(x / freq / detail, y / freq / detail) + 1.0) / 2.0
            noiseVal += v * amplitude
            
            freq /= self.frequency
            amplitude /= self.lacunarity

        return noiseVal

    def falloff_map(self, x, y, detail):
        x = (x / (detail+1.0)) * 2.0 - 1.0
        y = (y / (detail+1.0)) * 2.0 - 1.0

        value = np.max([np.abs(x), np.abs(y)])

        a = self.falloffSteepness
        b = self.falloffOffset
        
        return 1 - (math.pow(value, a) / (math.pow(value, a) + math.pow((b - b * value), a)))

    def generate_ridge_noise(self, N):
        # N * N array all value is 0.
        offsetX = self.offset[0]
        offsetY = self.offset[1]
        h = np.zeros((N,N))
        if self.falloff :
            for x in range(h.shape[0]):
                for y in range(h.shape[1]):
                    h[x, y] = (self.octaved_simplex_noise(x + offsetX, y + offsetY, N) + self.octaved_ridge_noise(x + offsetX, y + offsetY, N)) / 2.0 * self.falloff_map(x, y, N)
        else:
            for x in range(h.shape[0]):
                for y in range(h.shape[1]):
                    h[x, y] = (self.octaved_simplex_noise(x + offsetX, y + offsetY, N) + self.octaved_ridge_noise(x + offsetX, y + offsetY, N)) / 2.0

        # return inverse lerp value multiplyed amplitude.
        return np.clip((h  - h.min()) / (h.max() - h.min()) * self.maxHeight, self.waterLevel, self.maxHeight)
    
    def generate_noise(self, N):
        # N * N array all value is 0.
        offsetX = self.offset[0]
        offsetY = self.offset[1]
        h = np.zeros((N,N))
        if self.falloff :
            for x in range(h.shape[0]):
                for y in range(h.shape[1]):
                    h[x, y] = self.octaved_simplex_noise(x + offsetX, y + offsetY, N) * self.falloff_map(x, y, N)
        else :
            for x in range(h.shape[0]):
                for y in range(h.shape[1]):
                    h[x, y] = self.octaved_simplex_noise(x + offsetX, y + offsetY, N)

        # return inverse lerp value multiplyed amplitude.
        return np.clip((h  - h.min()) / (h.max() - h.min()) * self.maxHeight, self.waterLevel, self.maxHeight)

    def apply_noise_to_mesh(self):
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
                return
            
            # get mesh data
            mesh_data = bmesh.from_edit_mesh(obj.data)
            #print("mesh_data: ", mesh_data)
            
            # perlin result
            perlin = self.generate_ridge_noise(int(sqrt)) if self.ridge else self.generate_noise(int(sqrt))
            
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
        #print("apply noise to terrain mesh")
        self.apply_noise_to_mesh()
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class tlab_terrain_generate_noise(bpy.types.Operator):
    bl_idname = "tlab_terrain.generate_noise"
    bl_label = "Generate Noise"
    bl_description = "Generate Noise"
    
    def execute(self, context):
        bpy.ops.tlab_terrain.noise_settings("INVOKE_DEFAULT")
        return {'FINISHED'}


class TLAB_TERRAIN_MT_noise(bpy.types.Menu):
    bl_label = "Noise"

    def draw(self, context):
        self.layout.operator("tlab_terrain.generate_noise", text="Generate Noise")