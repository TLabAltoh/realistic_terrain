import bpy
import logging

from realistic_terrain import mesh
from realistic_terrain import erode
from realistic_terrain import noise
from realistic_terrain import material

bl_info = {
    "name": "realistic terrain",
    "author": "tlabaltoh",
    "version": (1, 4),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Terrain",
    "description": "Simulation of random terrain generation and rain erosion",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Terrain"
}

TAG = "[realistic_terrain] "

#
# Terrain
#

class TLAB_TERRAIN_MT_terrain(bpy.types.Menu):
    bl_label = "Terrain"
    
    def draw(self, context):
        self.layout.menu("TLAB_TERRAIN_MT_mesh")
        self.layout.menu("TLAB_TERRAIN_MT_erode")
        self.layout.menu("TLAB_TERRAIN_MT_noise")

#
# Main thread
#

menus = [
    TLAB_TERRAIN_MT_terrain,
    mesh.TLAB_TERRAIN_MT_mesh,
    erode.TLAB_TERRAIN_MT_erode,
    noise.TLAB_TERRAIN_MT_noise,
]

classes = [
    mesh.tlab_terrain_grid_settings,
    mesh.tlab_terrain_smooth_terrain_mesh,
    mesh.tlab_terrain_generate_terrain_mesh,

    erode.tlab_terrain_erode_settings,
    erode.tlab_terrain_process_erode,

    noise.tlab_terrain_noise_settings,
    noise.tlab_terrain_generate_noise,
    
    material.tlab_terrain_terrain_material_prop,
    material.tlab_terrain_generate_terrain_material,
    material.TLAB_TERRAIN_PT_terrain_material_panel,
]

properties = {
    bpy.types.Material:{
        "terrain_mat": bpy.props.PointerProperty(type = material.tlab_terrain_terrain_material_prop),
        "terrain_mat_registed": bpy.props.BoolProperty(default = False)
    }
}

def menu_fn(self, context):
    self.layout.separator()
    
    # Show UI
    if context.mode == 'OBJECT':
        self.layout.menu("TLAB_TERRAIN_MT_terrain")


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

    print(TAG, "addon enabled")


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

    print(TAG, "addon disabled")


if __name__ == "__main__":
    register()
