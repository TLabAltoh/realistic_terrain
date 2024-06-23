import bpy

#
# Material
#

def _getNodeWithLabel(mat, label):
    result = [ node for node in mat.node_tree.nodes if node.label == label]
    if(len(result) > 0):
        return result[0]
    else:
        return None

labelKey = "label"
attrKey = "attr"

colorRamps = [
    {labelKey:"gradient_lerp0", attrKey:"gradient_colorRamp0"},
    {labelKey:"gradient_lerp1", attrKey:"gradient_colorRamp1"},
    {labelKey:"height_lerp", attrKey:"height_lerp"}
]

bsdfColors = [
    {labelKey:"color_g0", attrKey:"color_g0"},
    {labelKey:"color_g1", attrKey:"color_g1"},
    {labelKey:"color_s0", attrKey:"color_s0"}
]

noiseTextures = [
    {labelKey:"noise_texture_G0", "scale":"noise_scale_g0", "detail":"noise_detail_g0"},
    {labelKey:"noise_texture_G1", "scale":"noise_scale_g1", "detail":"noise_detail_g1"},
    {labelKey:"noise_texture_S0", "scale":"noise_scale_s0", "detail":"noise_detail_s0"},
]

def _updateColorRamp(prop, context, labelKey, attrKey, eleIndex):
    mat = prop.id_data
    node = _getNodeWithLabel(mat, labelKey)
    if node != None:
        value = getattr(mat.terrain_mat, attrKey)
        node.color_ramp.elements[eleIndex].position = value
    return

def _updateColor(prop, context, labelKey, attrKey):
    mat = prop.id_data
    node = _getNodeWithLabel(mat, labelKey)
    if node != None:
        values = getattr(mat.terrain_mat, attrKey)
        node.inputs["Base Color"].default_value = (values[0], values[1], values[2], 1.000)
    return

def _updateNoiseScale(prop, context, labelKey, attrKey, inputKey):
    mat = prop.id_data
    node = _getNodeWithLabel(mat, labelKey)
    if node != None:
        value = getattr(mat.terrain_mat, attrKey)
        node.inputs[inputKey].default_value = value
    return


class TerrainMaterial(bpy.types.PropertyGroup):
    """ Material
    """
    # ColorRamp
    gradient_colorRamp0_ele0: bpy.props.FloatProperty(
        name = "Gradient",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 0.677,
        update = lambda prop,context: _updateColorRamp(prop,context,"gradient_lerp0","gradient_colorRamp0_ele0",0)
    )

    gradient_colorRamp0_ele1: bpy.props.FloatProperty(
        name = "Gradient",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 1.000,
        update = lambda prop,context: _updateColorRamp(prop,context,"gradient_lerp0","gradient_colorRamp0_ele1",1)
    )

    gradient_colorRamp1_ele0: bpy.props.FloatProperty(
        name = "Gradient",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 0.677,
        update = lambda prop,context: _updateColorRamp(prop,context,"gradient_lerp1","gradient_colorRamp1_ele0",0)
    )

    gradient_colorRamp1_ele1: bpy.props.FloatProperty(
        name = "Gradient",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 1.000,
        update = lambda prop,context: _updateColorRamp(prop,context,"gradient_lerp1","gradient_colorRamp1_ele1",1)
    )

    height_colorRamp_ele0: bpy.props.FloatProperty(
        name = "Height",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 0.677,
        update = lambda prop,context: _updateColorRamp(prop,context,"height_lerp","height_colorRamp_ele0",0)
    )

    height_colorRamp_ele1: bpy.props.FloatProperty(
        name = "Height",
        description = "",
        precision = 3,
        min = 0,
        max = 1,
        step = 0.01,
        default = 1.000,
        update = lambda prop,context: _updateColorRamp(prop,context,"height_lerp","height_colorRamp_ele1",1)
    )

    # BSDF G0
    color_g0: bpy.props.FloatVectorProperty(
        name = "Grass Color G0",
        description = "",
        subtype = "COLOR",
        size = 3,
        min = 0,
        max = 1,
        precision = 3,
        step = 0.1,
        default = [0.072, 1.000, 0.053],
        update = lambda prop,context: _updateColor(prop, context, "color_g0", "color_g0")
    )

    noise_scale_g0: bpy.props.FloatProperty(
        name = "Noise Scale G0",
        description = "",
        precision = 3,
        step = 0.1,
        default = 5.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_G0", "noise_scale_g0", "Scale")
    )

    noise_detail_g0: bpy.props.FloatProperty(
        name = "Noise Detail G0",
        description = "",
        precision = 3,
        step = 0.1,
        default = 15.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_G0", "noise_detail_g0", "Detail")
    )

    # BSDF G1
    color_g1: bpy.props.FloatVectorProperty(
        name = "Grass Color G1",
        description = "",
        subtype = "COLOR",
        size = 3,
        min = 0,
        max = 1,
        precision = 3,
        step = 0.1,
        default = [0.610, 0.610, 0.610],
        update = lambda prop,context: _updateColor(prop, context, "color_g1", "color_g1")
    )

    noise_scale_g1: bpy.props.FloatProperty(
        name = "Noise Scale G1",
        description = "",
        precision = 3,
        step = 0.1,
        default = 5.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_G1", "noise_scale_g1", "Scale")
    )

    noise_detail_g1: bpy.props.FloatProperty(
        name = "Noise Detail G1",
        description = "",
        precision = 3,
        step = 0.1,
        default = 15.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_G1", "noise_detail_g1", "Detail")
    )

    # BSDF S0
    color_s0: bpy.props.FloatVectorProperty(
        name = "Grass Color S0",
        description = "",
        subtype = "COLOR",
        size = 3,
        min = 0,
        max = 1,
        precision = 3,
        step = 0.1,
        default = [0.672, 0.328, 0.112],
        update = lambda prop,context: _updateColor(prop, context, "color_s0", "color_s0")
    )

    noise_scale_s0: bpy.props.FloatProperty(
        name = "Noise Scale S0",
        description = "",
        precision = 3,
        step = 0.1,
        default = 20.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_S0", "noise_scale_s0", "Scale")
    )

    noise_detail_s0: bpy.props.FloatProperty(
        name = "Noise Detail S0",
        description = "",
        precision = 3,
        step = 0.1,
        default = 15.0,
        update = lambda prop,context: _updateNoiseScale(prop, context, "noise_texture_S0", "noise_detail_s0", "Detail")
    )


class CreateTerrainMaterial(bpy.types.Operator):
  bl_idname = "tlab_terrain.material_create"
  bl_label = "create new"
  
  def apply_mat(self, obj):
    name = obj.name
    m_name = "terrain-" + name
    
    if m_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[m_name])
        obj.active_material_index = len(obj.data.materials) - 1
        return
    
    material = bpy.data.materials.new("terrain-" + name)
    material.use_nodes = True
    material.terrain_mat_registed = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Delete Default BSDF Node
    BSDF = nodes["Principled BSDF"]
    nodes.remove(BSDF)
    
    # Global
    tex_coord = nodes.new("ShaderNodeTexCoord") # Texture Coordinate
    tex_coord.location = (-2860.0, -2100.0)
    geometry = nodes.new("ShaderNodeNewGeometry") # Geometry
    geometry.location = (-2600.0, 420)
    
    #
    # Create ColorRamp
    #
    
    # Gradient Lerp 0
    separate_Grad0 = nodes.new("ShaderNodeSeparateXYZ") # Separate XYZ
    separate_Grad0.location = (-2420.0, 420.0)
    
    colorRamp_Grad0 = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_Grad0.label = "gradient_lerp0"
    colorRamp_Grad0.location = (-2260.0, 420.0)
    colorRamp_Grad0.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorRamp_Grad0.color_ramp.elements[0].position = 0.886
    colorRamp_Grad0.color_ramp.elements[1].color = (0, 0, 0, 1)
    colorRamp_Grad0.color_ramp.elements[1].position = 1.000
    
    links.new(geometry.outputs["Normal"], separate_Grad0.inputs["Vector"])
    links.new(separate_Grad0.outputs["Z"], colorRamp_Grad0.inputs["Fac"])
    
    # Gradient Lerp 0
    separate_Grad1 = nodes.new("ShaderNodeSeparateXYZ") # Separate XYZ
    separate_Grad1.location = (-2440.0, -280.0)
    
    colorRamp_Grad1 = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_Grad1.label = "gradient_lerp1"
    colorRamp_Grad1.location = (-2260.0, -280.0)
    colorRamp_Grad1.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorRamp_Grad1.color_ramp.elements[0].position = 0.886
    colorRamp_Grad1.color_ramp.elements[1].color = (0, 0, 0, 1)
    colorRamp_Grad1.color_ramp.elements[1].position = 1.000
    
    links.new(geometry.outputs["Normal"], separate_Grad1.inputs["Vector"])
    links.new(separate_Grad1.outputs["Z"], colorRamp_Grad1.inputs["Fac"])
    
    # Height Lerp
    separate_Height = nodes.new("ShaderNodeSeparateXYZ") # Separate XYZ
    separate_Height.location = (120.0, 720.0)
    
    colorRamp_Height = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_Height.label = "height_lerp"
    colorRamp_Height.location = (280.0, 740.0)
    colorRamp_Height.color_ramp.elements[0].color = (0, 0, 0, 1)
    colorRamp_Height.color_ramp.elements[0].position = 0.677
    colorRamp_Height.color_ramp.elements[1].color = (1, 1, 1, 1)
    colorRamp_Height.color_ramp.elements[1].position = 1.000
    
    links.new(tex_coord.outputs["Generated"], separate_Height.inputs["Vector"])
    links.new(separate_Height.outputs["Z"], colorRamp_Height.inputs["Fac"])
    
    #
    # Create BSDF Node
    #
    
    # BSDF Glass 0
    p_BSDF_G0 = nodes.new("ShaderNodeBsdfPrincipled") # Principled BSDF
    p_BSDF_G0.label = "color_g0"
    p_BSDF_G0.location = (-1980.0, 420.0)
    p_BSDF_G0.inputs["Base Color"].default_value = (0.072, 1.000, 0.053, 1.000)
    p_BSDF_G0.inputs["Roughness"].default_value = 1.000
    
    # BSDF Glass 1
    p_BSDF_G1 = nodes.new("ShaderNodeBsdfPrincipled") # Principled BSDF
    p_BSDF_G1.label = "color_g1"
    p_BSDF_G1.location = (-1980.0, -280.0)
    p_BSDF_G1.inputs["Base Color"].default_value = (0.610, 0.610, 0.610, 1.000)
    p_BSDF_G1.inputs["Roughness"].default_value = 1.000
    
    # BSDF Soil
    p_BSDF_S0 = nodes.new("ShaderNodeBsdfPrincipled")
    p_BSDF_S0.label = "color_s0"
    p_BSDF_S0.location = (-1980.0, -980.0)
    p_BSDF_S0.inputs["Base Color"].default_value = (0.672, 0.328, 0.112, 1.000)
    p_BSDF_S0.inputs["Roughness"].default_value = 1.000

    #
    # Create Displacement Node
    #
    
    # Displacement Glass 0
    mapping_G0 = nodes.new("ShaderNodeMapping") # Mapping
    mapping_G0.location = (-1560.0, -2100.0)

    noiseTexture_G0 = nodes.new("ShaderNodeTexNoise") # Noise Texture
    noiseTexture_G0.label = "noise_texture_G0"
    noiseTexture_G0.location = (-1400.0, -2100.0)
    noiseTexture_G0.inputs["Scale"].default_value = 5.0
    noiseTexture_G0.inputs["Detail"].default_value = 15.0
    
    colorRamp_G0 = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_G0.location = (-1240.0, -2100.0)
    
    displacement_G0 = nodes.new("ShaderNodeDisplacement") # Displacement
    displacement_G0.location = (-960.0, -2100.0)
    
    links.new(tex_coord.outputs["UV"], mapping_G0.inputs["Vector"])
    links.new(mapping_G0.outputs["Vector"], noiseTexture_G0.inputs["Vector"])
    links.new(noiseTexture_G0.outputs["Fac"], colorRamp_G0.inputs["Fac"])
    links.new(colorRamp_G0.outputs["Color"], displacement_G0.inputs["Height"])
    
    # Displacement Glass 1
    mapping_G1 = nodes.new("ShaderNodeMapping") # Mapping
    mapping_G1.location = (-1560.0, -2460.0)
    
    noiseTexture_G1 = nodes.new("ShaderNodeTexNoise") # Noise Texture
    noiseTexture_G1.label = "noise_texture_G1"
    noiseTexture_G1.location = (-1400.0, -2460.0)
    noiseTexture_G1.inputs["Scale"].default_value = 5.0
    noiseTexture_G1.inputs["Detail"].default_value = 15.0
    
    colorRamp_G1 = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_G1.location = (-1240.0, -2460.0)
    
    displacement_G1 = nodes.new("ShaderNodeDisplacement") # Displacement
    displacement_G1.location = (-960.0, -2460.0)
    
    links.new(tex_coord.outputs["UV"], mapping_G1.inputs["Vector"])
    links.new(mapping_G1.outputs["Vector"], noiseTexture_G1.inputs["Vector"])
    links.new(noiseTexture_G1.outputs["Fac"], colorRamp_G1.inputs["Fac"])
    links.new(colorRamp_G1.outputs["Color"], displacement_G1.inputs["Height"])
    
    # Displacement Soil
    mapping_S0 = nodes.new("ShaderNodeMapping") # Mapping
    mapping_S0.location = (-1560.0, -2840.0)
    
    noiseTexture_S0 = nodes.new("ShaderNodeTexNoise") # Noise Texture
    noiseTexture_S0.label = "noise_texture_S0"
    noiseTexture_S0.location = (-1400.0, -2840.0)
    noiseTexture_S0.inputs["Scale"].default_value = 20.0
    noiseTexture_S0.inputs["Detail"].default_value = 15.0
    
    colorRamp_S0 = nodes.new("ShaderNodeValToRGB") # ColorRamp
    colorRamp_S0.location = (-1240.0, -2840.0)
    
    displacement_S0 = nodes.new("ShaderNodeDisplacement") # Displacement
    displacement_S0.location = (-960.0, -2840.0)
    
    links.new(tex_coord.outputs["UV"], mapping_S0.inputs["Vector"])
    links.new(mapping_S0.outputs["Vector"], noiseTexture_S0.inputs["Vector"])
    links.new(noiseTexture_S0.outputs["Fac"], colorRamp_S0.inputs["Fac"])
    links.new(colorRamp_S0.outputs["Color"], displacement_S0.inputs["Height"])
    
    #
    # Mix Displacement
    #
    
    # Mix Glass Displacement 0
    mix_G0 = nodes.new("ShaderNodeMix") # Mix
    mix_G0.location = (-220.0, -2000.0)
    links.new(colorRamp_Grad0.outputs["Color"], mix_G0.inputs["Factor"])
    links.new(displacement_G0.outputs["Displacement"], mix_G0.inputs["A"])
    links.new(displacement_S0.outputs["Displacement"], mix_G0.inputs["B"])
    
    # Mix Glass Displacement 1
    mix_G1 = nodes.new("ShaderNodeMix") # Mix
    mix_G1.location = (-220.0, -2340.0)
    links.new(colorRamp_Grad1.outputs["Color"], mix_G1.inputs["Factor"])
    links.new(displacement_G1.outputs["Displacement"], mix_G1.inputs["A"])
    links.new(displacement_S0.outputs["Displacement"], mix_G1.inputs["B"])
    
    # Mix Displacement
    mix = nodes.new("ShaderNodeMix") # Mix
    mix.location = (940.0, 260.0)
    links.new(colorRamp_Height.outputs["Color"], mix.inputs["Factor"])
    links.new(mix_G0.outputs["Result"], mix.inputs["A"])
    links.new(mix_G1.outputs["Result"], mix.inputs["B"])
    
    #
    # Mix Shader
    #
    
    # Mix Glass 0 BSDF
    mix_shader_G0 = nodes.new("ShaderNodeMixShader") # Shader Mix
    mix_shader_G0.location = (-1020.0, 460.0)
    links.new(colorRamp_Grad0.outputs["Color"], mix_shader_G0.inputs["Fac"])
    links.new(p_BSDF_G0.outputs["BSDF"], mix_shader_G0.inputs[1]) # Shader
    links.new(p_BSDF_S0.outputs["BSDF"], mix_shader_G0.inputs[2]) # Shader
    
    # Mix Glass 1 BSDF
    mix_shader_G1 = nodes.new("ShaderNodeMixShader") # Shader Mix
    mix_shader_G1.location = (-1020.0, 300.0)
    links.new(colorRamp_Grad1.outputs["Color"], mix_shader_G1.inputs["Fac"])
    links.new(p_BSDF_G1.outputs["BSDF"], mix_shader_G1.inputs[1]) # Shader
    links.new(p_BSDF_S0.outputs["BSDF"], mix_shader_G1.inputs[2]) # Shader

    # Mix BSDF
    mix_shader = nodes.new("ShaderNodeMixShader") # Shader Mix
    mix_shader.location = (940.0, 500.0)
    links.new(colorRamp_Height.outputs["Color"], mix_shader.inputs["Fac"])
    links.new(mix_shader_G0.outputs["Shader"], mix_shader.inputs[1]) # Shader
    links.new(mix_shader_G1.outputs["Shader"], mix_shader.inputs[2]) # Shader
    
    #
    # Output Result
    #
    
    # Material Output
    outputs = nodes["Material Output"] # Material Output
    outputs.location = (1220, 420)
    links.new(mix_shader.outputs["Shader"], outputs.inputs["Surface"])
    links.new(mix.outputs["Result"], outputs.inputs["Displacement"])
    
    obj.data.materials.append(material)
    obj.active_material_index = len(obj.data.materials) - 1

    for face in obj.data.polygons:
        face.material_index = obj.active_material_index

  def execute(self, context):
    self.apply_mat(context.active_object)
    return{'FINISHED'}


class TerrainMaterialPanel(bpy.types.Panel):
    bl_idname = "tlab_terrain.material_prop"
    bl_label = "Terrain Material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.active_material

    def draw(self, context):

        mat = context.active_object.active_material
        terrain_mat = mat.terrain_mat

        layout = self.layout

        if mat.terrain_mat_registed == False:
            col = layout.column()
            col.label(text="Terrain material not selected")
            col = layout.column()
            col.operator("tlab_terrain.material_create", text = "Create New")
        else:
            col = layout.column()
            col.label(text="ColorRamp")
            col = layout.column()
            r = col.row()
            r.prop(terrain_mat, "gradient_colorRamp0_ele0", text = "Gradient G0 ele0")
            r = col.row()
            r.prop(terrain_mat, "gradient_colorRamp0_ele1", text = "Gradient G0 ele1")
            col = layout.column()
            r = col.row()
            r.prop(terrain_mat, "gradient_colorRamp1_ele0", text = "Gradient G1 ele0")
            r = col.row()
            r.prop(terrain_mat, "gradient_colorRamp1_ele1", text = "Gradient G1 ele1")
            col = layout.column()
            r = col.row()
            r.prop(terrain_mat, "height_colorRamp_ele0", text = "Height ele0")
            r = col.row()
            r.prop(terrain_mat, "height_colorRamp_ele1", text = "Height ele1")

            col = layout.column()
            col.label(text="Grass 0 Settings")
            col = layout.column()
            col.prop(terrain_mat, "color_g0", text = "")
            col = layout.column()
            col.prop(terrain_mat, "noise_scale_g0", text = "Noise Scale")
            col = layout.column()
            col.prop(terrain_mat, "noise_detail_g0", text = "Noise Detail")

            col = layout.column()
            col.label(text="Grass 1 Settings")
            col = layout.column()
            col.prop(terrain_mat, "color_g1", text = "")
            col = layout.column()
            col.prop(terrain_mat, "noise_scale_g1", text = "Noise Scale")
            col = layout.column()
            col.prop(terrain_mat, "noise_detail_g1", text = "Noise Detail")

            col = layout.column()
            col.label(text="Soil 0 Settings")
            col = layout.column()
            col.prop(terrain_mat, "color_s0", text = "")
            col = layout.column()
            col.prop(terrain_mat, "noise_scale_s0", text = "Noise Scale")
            col = layout.column()
            col.prop(terrain_mat, "noise_detail_s0", text = "Noise Detail")
