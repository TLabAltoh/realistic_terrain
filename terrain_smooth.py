import bpy
import bmesh
import numpy as np

print(("\n==============================" +
    " terrain_smooth" +
    "\n=============================="))

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
