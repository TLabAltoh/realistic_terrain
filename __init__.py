import bpy
import logging
import os
import sys

addon_dirpath = os.path.dirname(__file__)
sys.path += [addon_dirpath]

import grid
import erode
import perlin
import material

bl_info = {
    "name": "realistic terrain",
    "author": "tlabaltoh",
    "version": (1, 1),
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
    grid.Grid,
    erode.Erode,
    perlin.Perlin,
]

classes = [
    grid.GridSettings,
    grid.CreateGrid,
    grid.GridSmooth,

    erode.ErodeSettings,
    erode.ProcessErode,

    perlin.PerlinSettings,
    perlin.CreatePerlinNoise,
    
    material.TerrainMaterial,
    material.TerrainMaterialPanel,
    material.CreateTerrainMaterial
]

properties = {
    bpy.types.Material:{
        "terrain_mat": bpy.props.PointerProperty(type = material.TerrainMaterial),
        "terrain_mat_registed": bpy.props.BoolProperty(default = False)
    }
}

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
    
    # Register custom properties
    for typ, t in properties.items():
        for attr, prop in t.items():
            if hasattr(typ, attr):
                logging.warning(' * warning: overwrite\t%s\t%s', typ, attr)
            try:
                setattr(typ, attr, prop)
            except:  # pylint: disable=bare-except
                logging.warning(' * warning: register\t%s\t%s', typ, attr)

    print("[realistic-terrain] addon enabled")


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_fn)

    # Unregister menu
    for menu in menus:
        bpy.utils.unregister_class(menu)
        
    # Unregister class
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Unregister custom properties
    for typ, t in properties.items():
        for attr in t.keys():
            if hasattr(typ, attr):
                delattr(typ, attr)

    print("[realistic-terrain] addon disabled")


if __name__ == "__main__":
    register()