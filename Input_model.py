from bpy.app.handlers import persistent
import bpy
import os
import math

# class ModelImporter:
#     @staticmethod
#     def import_model(file_path, position=(0, 0, 0), rotation=(0, 0, 0),scale=(0.6,0.6,0.6)):
#         # Check if file exists
#         if not os.path.exists(file_path):
#             print(f"No file found at: {file_path}")
#             return

#         # Import the model
#         _, ext = os.path.splitext(file_path)
#         if ext.lower() == ".obj":
#             bpy.ops.import_scene.obj(filepath=file_path)
#         elif ext.lower() == ".glb":
#             bpy.ops.import_scene.glb(filepath=file_path)
#         else:
#             print(f"Unsupported file extension: {ext}")
#             return

#         # Set position and rotation
#         for obj in bpy.context.selected_objects:
#             obj.location = position
#             obj.rotation_euler = rotation
            
            
def import_model(file_path, position=(0, 0, 0), rotation=(0, 0, 0),scale=(0.6,0.6,0.6)):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"No file found at: {file_path}")
        return
    
    # Import the model
    _, ext = os.path.splitext(file_path)
    if ext.lower() == ".obj":
        bpy.ops.import_scene.obj(filepath=file_path)
    elif ext.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=file_path)
    else:
        print(f"Unsupported file extension: {ext}")
        return

    # Set position and rotation
    for obj in bpy.context.selected_objects:
        obj.location = position
        obj.rotation_euler = rotation
        obj.scale = scale
        
    #using quad remesher to remesh the model
    bpy.data.scenes["Scene"].qremesher.target_count=50000
    bpy.ops.qremesher.remesh()
    print("remeshed successfully")
    
# Usage
file_path = "/path/to/your/model.obj"#E:\\Master\\Graduation_project\\shap-e\\shap_e\\examples\\1.obj
position = (-0.145884, -1.84163, 1.85771)  # X, Y, Z
rotation = (math.radians(73.6377), math.radians(7.79891), math.radians(231.503))  # In radians
scale = (0.6,0.6,0.6)
import_model(file_path, position, rotation, scale)