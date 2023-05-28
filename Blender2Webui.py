from bpy.app.handlers import persistent
import bpy
import os
import shutil
import time
import tempfile
import base64
from base64 import b64encode
import requests
import json
import cv2
import numpy as np
from io import BytesIO
from random import uniform

IMAGE_FOLDER = "path/to/image/folder"#F:\\Output

#Alternative parameter
#"mask": "string",
#"mask_blur": 30,
# "inpainting_fill": 0,
# "inpaint_full_res": True,
# "inpaint_full_res_padding": 1,
# "inpainting_mask_invert": 1,
#"controlnet_mask": [],

DEFAULT_PARAMS = {

    "init_images": [],
    "resize_mode": 0,
    "denoising_strength": 0.7,
    "prompt": "masterpiece,best quality,with blue and white design on it,smooth line sneakers,with detailed,colorful,cartoon,octane render,artgerm,artstation,lightning,fill,star,2d texture,((symmetrical)),fabric,clear edge,not complicated pattern,fill in the blanks,successive",
    "negative_prompt": "worst quality, low quality, lowres, normal quality",
    "controlnet_input_image": [],
    "controlnet_module": "canny",
    "controlnet_model": "diff_control_sd15_canny_fp16 [ea6e3b9c]",
    "controlnet_weight": 1,
    "controlnet_resize_mode": "Scale to Fit (Inner Fit)",
    "controlnet_lowvram": True,
    "controlnet_processor_res": 512,
    "controlnet_threshold_a": 64,
    "controlnet_threshold_b": 64,
    "controlnet_guidance": 1.0,
    "guess_mode": True,
    "seed": -1,
    "subseed": -1,
    "subseed_strength": -1,
    "sampler_index": "Euler a",
    "batch_size": 3,
    "n_iter": 1,
    "steps": 25,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "restore_faces": False,
    "include_init_images": True,
    "override_settings": {},
    "override_settings_restore_afterwards": True
}
    

def create_texture():
    # Get the active object
    obj = bpy.context.active_object
    
    # Create new material if needed
    if not obj.active_material:
        mat = bpy.data.materials.new(name='New Material')
        mat.use_nodes = True
        obj.active_material = mat
    else:
        mat = obj.active_material

    # Create RGB color node and Generate random color
    found_color=any(node.type=='RGB' for node in mat.node_tree.nodes)
    if not found_color:
        purecolor_node = mat.node_tree.nodes.new(type='ShaderNodeRGB')
        purecolor_node.location = (-400, 0)
        color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1.0)
        purecolor_node.outputs[0].default_value = color
    else:
        found_color.outputs[0].default_value = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1.0)
        print("An RGB Node already exists in the material.")
    
    # Create image texture node
    target_label='ReferenceTexture'
    found_image_texture=next((node for node in mat.node_tree.nodes if node.type=='TEX_IMAGE'and node.label==target_label),None)
    if not found_image_texture:
        image_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        image_node.label = 'ReferenceTexture'
        image_node.location = (-200, 0)
        image_node.image = bpy.data.images.new(name='Baked Texture', width=1024, 
                                            height=1024, alpha=False,
                                            float_buffer=False, stereo3d=False, 
                                            is_data=False, tiled=False)
    else:
        print("An Image Texture Node already exists in the material.")
        if not found_image_texture.image:
            found_image_texture.image = bpy.data.images.new(name='Baked Texture', width=1024, 
                                            height=1024, alpha=False,
                                            float_buffer=False, stereo3d=False, 
                                            is_data=False, tiled=False)
            print("A new image has been created and assigned to the existing Image Texture node.")
    
    return mat

def create_normal_area():
    # Get the active object
    obj = bpy.context.active_object
    if not obj.active_material:
        print ("No material is assigned to the active object.")
        return
        # mat = bpy.data.materials.new(name='New Material')
        # mat.use_nodes = True
        # obj.active_material = mat
    else:
        mat = obj.active_material
    
    # Create normal map
    target_label='ReferenceTexture'
    found_image_texture=next((node for node in mat.node_tree.nodes if node.type=='TEX_IMAGE'and node.label==target_label), None)
    if not found_image_texture:
        return print("An Image Texture Node with the label 'ReferenceTexture' does not exist in the material.")
    else:
        found_image_texture.select=True
        mat.node_tree.nodes.active=found_image_texture
        bpy.ops.deepbump.colortonormals()
        #bpy.ops.deepbump.normalstoheight()

def bake_texture(mat):
    # Connect nodes
    purecolor_node = mat.node_tree.nodes['RGB']#(type=='ShaderNodeRGB')为啥找不到
    #image_node = mat.node_tree.nodes(lable='Image01')
    color_output = purecolor_node.outputs[0]
    emit_color_input = mat.node_tree.nodes.get("Principled BSDF").inputs.get("Base Color")
    mat.node_tree.links.new(color_output, emit_color_input)

    # Set up bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    #image_path = os.path.join(os.path.dirname(bpy.data.filepath), 'baked_texture.png')

    # bpy.data.scenes["Scene"].render.engine='CYCLES'
    # bpy.data.scenes["Scene"].cycles.feature_set = 'EXPERIMENTAL'
    # bpy.data.scenes["Scene"].cycles.bake_type = 'EMIT'

    # Bake texture
    bpy.ops.object.bake(type='DIFFUSE')
    
    # Save texture
    # image_node.image.save_render(image_path)

    # # Return the path to the baked texture
    # return image_path

def read_image(mat):
    
    # Define the target label
    target_label = 'ReferenceTexture'
    
    # Find the Image Texture node with the target label using a generator expression and next()
    found_node = next((node for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE' and node.label == target_label), None)
    
    if found_node:
        print(f"Found an Image Texture node with the label '{target_label}'.")

     # Get the image data from the Image Texture node
        image = found_node.image
        if image:
            print(f"Image Name: {image.name}")
            print(f"Image Filepath: {image.filepath}")
            print(f"Image Size: {image.size}")  # Returns a tuple of the form (width, height)
            print(f"Image Alpha: {image.alpha_mode}")
            print(f"Image Colorspace: {image.colorspace_settings.name}")
    
            # Convert the image data to a NumPy array
            width,height=image.size
            image_pixels=np.array(image.pixels[:]).reshape(height,width,4)
    
            # Convert the image data from a NumPy array to an OpenCV Image object
            origin_image=(image_pixels[:,:,:3]*255).astype(np.uint8)[::-1]# Extract the RGB channels and reverse the row order (OpenCV uses BGR)
            success, buffer = cv2.imencode('.png', origin_image)
            b64img = base64.b64encode(buffer).decode("utf-8")
            #print("Image Texture data encoded in Base64:")
            #print(b64img)
            return b64img
        else:
            print("No image is assigned to the Image Texture node.")
    else:
        print(f"An Image Texture node with the label '{target_label}' does not exist in the material.")
    
    return b64img

def read_file_image(path):
    img = cv2.imread(path)
    success, buffer = cv2.imencode('.png', img)
    b64img = base64.b64encode(buffer).decode("utf-8")
    return b64img

#def Create_temp_file():

def render_image(time:int,index:int):
    
    #Set the render settings
    bpy.context.scene.camera=bpy.data.objects['RenderCamera']
    bpy.context.scene.render.resolution_percentage=100
    bpy.context.scene.render.use_stamp_time=True
    bpy.context.scene.render.use_stamp_date=True
    bpy.context.scene.render.use_stamp_frame=True
    bpy.context.scene.render.use_stamp_filename=True
    
    #Define the output path and filename prefix
    output_path = IMAGE_FOLDER
    #timestamp = int(time.time())
    render_filename_prefix=f"{time}_{index}.png"
    #render_filename_prefix=f"{timestamp}_{index}.png"
    
    #Set the output image settings
    try:
        orig_render_file_format = bpy.context.scene.render.image_settings.file_format
        orig_render_color_mode = bpy.context.scene.render.image_settings.color_mode
        orig_render_color_depth =bpy.context.scene.render.image_settings.color_depth

        bpy.context.scene.render.image_settings.file_format='PNG'
        bpy.context.scene.render.image_settings.color_mode='RGBA'
        bpy.context.scene.render.image_settings.color_depth = '8'
        
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(f"{output_path}/Render_Image/{render_filename_prefix}")

        bpy.context.scene.render.image_settings.file_format = orig_render_file_format
        bpy.context.scene.render.image_settings.color_mode = orig_render_color_mode
        bpy.context.scene.render.image_settings.color_depth = orig_render_color_depth
    except:
        return print("Couldn't save rendered image")


def set_params_image(mat,params:dict): 
    #b64img=read_image(mat)
    b64_file_img=read_image(mat)
    #b64_file_img=read_file_image("E:/Master/Graduation_project/sd/stable-diffusion-webui/outputs/img2img-images/2023-02-23/00101-2954456484.png")
    b64_input_img=read_image(mat)#read_file_image("E:/Master/Graduation_project/Model_utility/Valid/00238-2079211147.png")
    params["controlnet_input_image"] = [b64_input_img]
    params["init_images"]=[b64_file_img]

def send_to_Webui_api(mat,params:dict):
    # create headers
    Headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Encoding":"gzip,deflate,br",
    "User-Agent":"Blender/"+bpy.app.version_string,
}
    #prepare server url
    server_url ="http://localhost:7860/controlnet/img2img"
    
    # prepare data for API
    #params = DEFAULT_PARAMS
    
    set_params_image(mat,params)
    
    # send API request to the server
    try:
        response = requests.post(url=server_url, json=params,headers=Headers,timeout=1000)
    except requests.exceptions.ConnectionError:
        return print(f"The Automatic1111 server couldn't be found.")
    except requests.exceptions.MissingSchema:
        return print(f"The url for your Automatic1111 server is invalid.")
    except requests.exceptions.ReadTimeout:
        return print("The Automatic1111 server timed out.")

# handle the response
    if response.status_code == 200:
        print("successed")
        return handle_api_success(response, IMAGE_FOLDER)
    else:
        print("failed")
        return handle_api_error(response)

def get_render_image(b64_img_data,filename):
    
    try:
        output_file=filename
    except:
        return print("Couldn't create a temp file to save image.")
    
    #decode base64 image
    try:
        img_binary=base64.b64decode(b64_img_data.replace("data:image/png;base64,",""))
    except:
        return print("Couldn't decode base64 image.")
    
    render_image_name="Decode_Image"
    timestamp = int(time.time())
    times=timestamp
    #save the image to the file
    try:
        output_file_prefix=f"{output_file}/Decoded_Image/{render_image_name}_{times}.png"
        with open(output_file_prefix,"wb")as f:
            f.write(img_binary)
            #img = cv2.imread(output_file_prefix)
    except:
        return print("Couldn't write to temp file.")
    
    img=bpy.data.images.load(output_file_prefix)
    node_tree= bpy.context.active_object.active_material.node_tree

    #Find or create an Image Texture node
    target_label='RenderTexture'
    found_image_texture=next((node for node in node_tree.nodes if node.type=='TEX_IMAGE'and node.label==target_label),None)
    #found_image_texture=any(node.type=='TEX_IMAGE'and node.label==target_label for node in mat.node_tree.nodes)
    if not found_image_texture:
        image_node = node_tree.nodes.new(type='ShaderNodeTexImage')
        image_node.label = 'RenderTexture'
        image_node.location = (-300, 300)
        #image_node.image = render_image
        image_node.image=img
        found_image_texture=image_node
    else:
        print("An Render Image Texture Node already exists in the material.")
        #found_image_texture.image=render_image
        found_image_texture.image=img
        print("A new image has been created and assigned to the existing Image Texture node.")
    
    # Connect nodes
    renderimg_node=found_image_texture
    img_output=renderimg_node.outputs['Color']
    
    principled_node=next((node for node in node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None)
    
    if not principled_node:
        print("Principled BSDF node not found.")
    else:
        base_color_socket=principled_node.inputs['Base Color']
        
    connected_links=[link for link in node_tree.links if link.from_node==renderimg_node 
                        and link.from_socket==img_output
                        and link.to_node==principled_node
                        and link.to_socket==base_color_socket]
    
    if not connected_links:
        node_tree.links.new(img_output, base_color_socket)
        print("Connected Image Texture node to Principled BSDF node.")
    else:
        print("Image Texture node is already connected to Principled BSDF node.")
    
    return times

def handle_api_success(response, filename):
    
    try:
        response_obj = response.json()
        #base64_img=response_obj["images"][0]
    except:
        print("Automatic1111 response content: ")
        print(response.content)
        return print("Received an unexpected response from the Automatic1111 server.")
    
    num_images=check_image_number(response)
    
    
    for i in range(num_images-1):
        base64_img=response_obj["images"][i]
        times=get_render_image(base64_img,filename)
        render_image(times,i)
    
    # try:
    #     output_file=filename
    # except:
    #     return print("Couldn't create a temp file to save image.")
    
    # #decode base64 image
    # try:
    #     img_binary=base64.b64decode(base64_img.replace("data:image/png;base64,",""))
    # except:
    #     return print("Couldn't decode base64 image.")
    
    # #save the image to the file
    # try:
    #     with open(f"{output_file}/_g001.png","wb")as file:
    #         file.write(img_binary)
    # except:
    #     return print("Couldn't write to temp file.")
    
    # #return the file
    # return output_file

def handle_api_error(response):
    if response.status_code == 404:
        try:
            response_obj = response.json()
            if response_obj.get('detail') and response_obj['detail'] == "Not Found":
                return print("It looks like the Automatic1111 server is running, but it's not in API mode.")
            elif response_obj.get('detail') and response_obj['detail'] == "Sampler not found":
                return print("The sampler you selected is not available.")
            else:
                return print(f"An error occurred in the Automatic1111 server. Full server response: {json.dumps(response_obj)}")
        except:
            return print("It looks like the Automatic1111 server is running, but it's not in API mode.")
    else:
        print(response.status_code)
        print(response.json())
        return print("An error occurred in the Automatic1111 server.")

def check_image_number(response)->int:
    #check Number of images
    data=json.loads(response.text)
    image_data_list=data.get('images',[])
    num_images=len(image_data_list)
    print(f"Number of images:{num_images}")
    return num_images

complete_mat=create_texture()
bake_texture(complete_mat)
send_to_Webui_api(complete_mat,DEFAULT_PARAMS)