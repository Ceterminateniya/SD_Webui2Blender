import bpy
import random
from mathutils import Vector
import bmesh

def create_random_points_on_object(obj, point_count, seed):
    vertices = [v.co for v in obj.data.vertices]
    rng = random.Random(seed)
    random_points = rng.sample(vertices, point_count)
    return random_points

def create_surface_following_curve(points, target_object, curve_name="SurfaceFollowingCurve"):
    curve_data = bpy.data.curves.new(curve_name, 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_object = bpy.data.objects.new(curve_name, curve_data)
    bpy.context.collection.objects.link(curve_object)

    spline = curve_data.splines.new('BEZIER')
    spline.use_cyclic_u = True
    spline.bezier_points.add(len(points))

    for i, point in enumerate(points):
        bezier_point = spline.bezier_points[i]
        bezier_point.co = point
        bezier_point.handle_left_type = 'AUTO'
        bezier_point.handle_right_type = 'AUTO'

    # Add an extra point to the end to close the curve on the surface
    final_point = spline.bezier_points[-1]
    final_point.co = points[0]

    shrinkwrap_mod = curve_object.modifiers.new('Shrinkwrap', 'SHRINKWRAP')
    shrinkwrap_mod.target = target_object
    shrinkwrap_mod.wrap_method = 'NEAREST_SURFACEPOINT'
    return curve_object

def create_random_groups(points, min_group_size=3, max_group_size=4):
    random.shuffle(points)
    groups = []
    while points:
        group_size = random.randint(min_group_size, max_group_size)
        group = points[:group_size]
        groups.append(group)
        points = points[group_size:]
    return groups

def add_subdivision_modifier(obj, levels=2):
    subdiv_mod = obj.modifiers.new("Subdivision", "SUBSURF")
    subdiv_mod.levels = levels
    subdiv_mod.render_levels = levels
    return subdiv_mod

def add_solidify_modifier(obj, thickness=0.01):
    solidify_mod = obj.modifiers.new("Solidify", "SOLIDIFY")
    solidify_mod.thickness = thickness
    return solidify_mod

def curve_to_mesh(obj):
    mesh_data = bpy.data.meshes.new_from_object(obj)
    mesh_obj = bpy.data.objects.new(obj.name + "_mesh", mesh_data)
    mesh_obj.matrix_world = obj.matrix_world.copy()
    bpy.context.collection.objects.link(mesh_obj)
    return mesh_obj

def cut_model_with_curves(model, curve_objects):
    for curve_obj in curve_objects:
        mesh_obj = curve_to_mesh(curve_obj)
        boolean_mod = model.modifiers.new("BooleanCut", "BOOLEAN")
        boolean_mod.operation = "DIFFERENCE"
        boolean_mod.use_self = True
        boolean_mod.object = mesh_obj
        
        bpy.context.view_layer.objects.active = model
        bpy.ops.object.modifier_apply({"object": model}, modifier=boolean_mod.name)
        #bpy.data.objects.remove(mesh_obj)

# def cut_model_with_curves(model, curve_objects):
#     for curve_obj in curve_objects:
#         mesh_obj = curve_to_mesh(curve_obj)
#         boolean_mod = model.modifiers.new("Boolean", "BOOLEAN")
#         boolean_mod.operation = "DIFFERENCE"
#         boolean_mod.use_self = True
#         boolean_mod.object = mesh_obj
        
#         # Use the recommended way of applying the modifier
#         depsgraph = bpy.context.evaluated_depsgraph_get()
#         model_eval = model.evaluated_get(depsgraph)
#         mesh_from_eval = bpy.data.meshes.new_from_object(model_eval)
#         model.modifiers.remove(boolean_mod)
#         model.data = mesh_from_eval

def main():
    target_object = bpy.context.active_object
    seed = 42
    point_count = 24

    random_points = create_random_points_on_object(target_object, point_count, seed)
    random_groups = create_random_groups(random_points)

    curve_objects = []
    for i, group in enumerate(random_groups):
        curve_name = f"SurfaceFollowingCurve_{i}"
        curve_object = create_surface_following_curve(group, target_object, curve_name)
        add_subdivision_modifier(curve_object)  # Add the Subdivision Surface modifier
        add_solidify_modifier(curve_object)  # Add the Solidify modifier
        curve_objects.append(curve_object)

    cut_model_with_curves(target_object, curve_objects)

main()