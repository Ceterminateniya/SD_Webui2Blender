bl_info = {
    "name": "FZRandomizer",
    "author": "FruitZeus",
    "version": (3, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Object Data Properties",
    "description": "Randomize Characters & Mesh Objects",
    "warning": "",
    "doc_url": "www.youtube.com/fruitzeus",
    "category": "Mesh",
}

import bpy
import random
import csv
import json
import os

import datetime
import time

from bpy.props import PointerProperty

"""GLOBAL VARS"""
hostNameWarning = ""


def main(context, func):

    objs = context.selected_objects

    if func == "rand":
        """Send each object to be randomized"""
        a = 0
        while a < len(objs):
            randShapeKey(objs[a])
            a +=1
    elif func == "reset":
            
        a = 0
        
        while a < len(objs):
            resetSK(objs[a])
            a +=1
        
    else:
        a = 0
        
        while a < len(objs):
            setParams(objs[a])
            a +=1

    
    
def randShapeKey(obj):
    
    
    if obj.type == "MESH" or obj.type == "LATTICE":
        """randomize shapekey list here"""
        k = obj.data.shape_keys
        
         
        
        """randomize all shape keys"""
        if k != None:
            kb = k.key_blocks
            kNum = len(kb)
            a = 0
            while a < kNum:
                r = random.random()
                min = kb[a].slider_min
                max = kb[a].slider_max
                ans = min + ((max - min) * r)
                kb[a].value = ans
                a += 1
                
            print(kb[0].value)


def resetSK(obj):
    if obj.type == "MESH" or obj.type == "LATTICE":
        """randomize shapekey list here"""
        k = obj.data.shape_keys
        
        """randomize all shape keys"""
        if k != None:
            kb = k.key_blocks
            kNum = len(kb)
            a = 0
            while a < kNum:
                min = kb[a].slider_min
                max = kb[a].slider_max
                if min > 0:
                    ans = min
                elif max < 0:
                    ans = max
                else:
                    ans = 0
                kb[a].value = ans
                a += 1
                
            print(kb[0].value)

def setParams (obj):
    
    param = bpy.context.scene.sk_prefix
    
    if obj.type == "MESH":
        """randomize shapekey list here"""
        print (obj.data.shape_keys)
        k = obj.data.shape_keys.key_blocks
        kNum = len(k) 
        
        """randomly select 1 hair style"""
        if kNum > 0:
            a = 0
            
            """count applicable parameters"""
            paramNum = 0
            appParamList = []
            
            while a < kNum:
                
                keyName = k[a].name
                prefix = keyName[0:len(param)]
                
                """is prefix 'param'. If so, add it to list of Shape Keys to be in the randomizer"""
                
                if prefix == param:
                    appParamList.append(k[a])
                    print (keyName)
                a += 1
            
            """
            
            We've found all the parameters to be considered in the random pool.
            Now, reset all those parameters to 1 (which means they will be scaled to 0)
            & find the lucky parameter to remain as a value of 0 (which means is is at full scale)
            
            """
            
            a = 0
            paramNum = len(appParamList)
            if paramNum > 0:
                randParam = random.randint(0,paramNum-1)
                
                while a < paramNum:
                    appParamList[a].value = 1
                    a += 1
                appParamList[randParam].value = 0
                
                print ("The Random Parameter Selected Was " + appParamList[randParam].name)
            else:
                print ("No Parameters")
            



"""-------------------------------------TINY--TOOLS-------------------------------------"""

def collExists(name):
    allColl = bpy.data.collections
    
    x = 0
    hostExists = False
    
    while x < len(allColl):
        if allColl[x].name == name:
            hostExists = True
            x = len(allColl)
        else:
            hostExists = False
            x += 1
    
    return hostExists


def host():
    hostName = bpy.context.scene.char_collection
    exists = collExists(hostName)
    
    if exists == True:
        return (bpy.data.collections[hostName])
    else:
        return None
    

def setRootCollActive():
    scene_collection = bpy.context.view_layer.layer_collection
    bpy.context.view_layer.active_layer_collection = scene_collection

def collAtRoot(coll):
    """GET COLLECTIONS AT ROOT LAYER INITIALLY"""
    rootColls = bpy.context.view_layer.layer_collection.children
    
    exists = collExists(coll)
    
    atRoot = False
    
    if exists == True:
        """PROCEED"""
        
        
        for x in rootColls:
            if x.name == coll:
                atRoot = True
            else:
                """DO NOTHING"""       
    else:
        """DO NOTHING"""
    
    return atRoot
    
    
def freshConsole(lines):
    x = 0
    
    while x < lines:
        print("\n")
        x += 1
        
def uncheck_collection(collection_name, check):
    bpy.context.view_layer.layer_collection.children[collection_name].exclude = check
               
def appDataSheet(meta, overwrite):

    filepath = bpy.path.abspath("//") + bpy.context.scene.csv_doc_name

    # open the file in the write mode
    if overwrite == True:
        f = open(filepath, 'w', newline = '')
        
        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        writer.writerow(meta)

        # close the file
        f.close()
    else:
        f = open(filepath, 'a', newline = '')
        
        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        writer.writerow(meta)

        # close the file
        f.close()
    

def findMyColl(obj):
    
    for coll in bpy.data.collections:
        for x in coll.objects:
            if obj == x:
                print("coll found: " + coll.name)
                return coll
                
def setSubData(obj):
    coll = findMyColl(obj)
    obj['Sub Origin'] = coll.name
    
    return None

def listHostSubs():
    subs = []
    host = bpy.data.collections[bpy.context.scene.char_collection]
    
    for coll in host.children:
        subs.append(coll.name)
        
    return subs
        
def subTicketCounter(sub):
    
    """GIVEN AN ORIGIN SUB, FIND THE TOTAL TICKET IN POOL"""
    total = 0
    for obj in sub.objects:
        total += obj.fzRarity
    
    return total



def writeToJSONFile(fileName, data):
    
    folder_name = bpy.context.scene.metadataFolderName
    
    mdFolder = bpy.path.abspath("//") + folder_name
    
    if not os.path.exists(mdFolder):
        os.mkdir(mdFolder)
        
    filePathNameWExt = bpy.path.abspath("//") + folder_name + '/' +fileName + ".json"
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp, indent=4)
        
        
        
def flip_data_set(column):
    #take a 2D matrix and flip it on its side
    
    flipped = []
    
    rowLen = len(column[0])
    
    count = 0
    while count < rowLen:
        newRow = []
        for row in column:
            newRow.append(row[count])
             
        flipped.append(newRow)
        count += 1    
    
    return flipped

            

def openHost():
    
    name = bpy.context.scene.char_collection
    hostExists = collExists(name)
    
    if hostExists:
        uncheck_collection(name, False)
        coll = bpy.data.collections[name]
        coll.all_objects[0].select_set(True)
    

"""----------------------------GEOMETRY--NODES-------------------------------------"""


def make_subcoll_group(subcollection, linkMatGroups):
    

    subcoll_group = bpy.data.node_groups.new(subcollection, "GeometryNodeTree")

    groupIn = subcoll_group.nodes.new("NodeGroupInput")
    groupIn.location = (-500, 0)


    groupOut = subcoll_group.nodes.new("NodeGroupOutput")
    groupOut.location = (500,0)

    subcoll_group.inputs.new("NodeSocketGeometry", "Input")
    subcoll_group.inputs.new("NodeSocketInt", subcollection)
    subcoll_group.inputs.new("NodeSocketInt", "max_value")
    subcoll_group.inputs.new("NodeSocketBool", "Animated")
    subcoll_group.inputs.new("NodeSocketInt", "Frame Advance")

    subcoll_group.inputs[1].min_value = 1
    subcoll_group.inputs[1].max_value = len(bpy.data.collections[subcollection].objects)
    subcoll_group.inputs[1].default_value = 1
    
    subcoll_group.inputs[2].default_value = len(bpy.data.collections[subcollection].objects)

    join_node = subcoll_group.nodes.new(type="GeometryNodeJoinGeometry")
    join_node.location = (300,0)

    subcoll_group.outputs.new("NodeSocketGeometry", "Output")

    #LINKS
    #subcoll_group.links.new(groupIn.outputs[0], join_node.inputs[0])
    subcoll_group.links.new(join_node.outputs[0], groupOut.inputs[0])

    
    #SORTING ALPHABETICALLY
    unsorted = bpy.data.collections[subcollection].objects
    unsortedNames = []
    for obj in unsorted:
        unsortedNames.append(obj.name)
    
    sortedNames = sorted(unsortedNames)
    sortedObj = []
    
    for name in sortedNames:
        sortedObj.append(bpy.data.objects[name])

    count = 0
    
    
    
    
    for obj in unsorted:
        
        print ("MAKING " + subcollection + " Object Nodes: " + obj.name)
        hasLM = False
        objLM = None
        
        #does obj have linkmat
        lmCounter = 0
        for lmGroup in linkMatGroups:
            objs = lmGroup[1]
            for lmObj in objs:
                
                print("   comparing " + lmObj.name + " to " + obj.name)
                
                proxy_version = bpy.data.objects[obj.name + " Proxy"]
                if proxy_version == lmObj:
                    #FOUND ITS linkMatGroup
                    hasLM = True
                    objLM = lmCounter
            lmCounter += 1
                    
        
        print ("\n")
        obj_node = subcoll_group.nodes.new(type="GeometryNodeObjectInfo")
        obj_node.location = (-300, -300*(count+1))

        
        #FIND OBJ PROXY MIRROR
        
        obj_proxy = bpy.data.objects[obj.name + " Proxy"]
        
        obj_node.inputs[0].default_value = obj_proxy
        obj_node.transform_space = 'RELATIVE'
        #As Instance
        obj_node.inputs[1].default_value = True
        
        
        
        switch_node = subcoll_group.nodes.new(type="GeometryNodeSwitch")
        switch_node.location = (100, -300*(count+1))
        
        
        compare_node = subcoll_group.nodes.new(type="FunctionNodeCompare")
        compare_node.location = (-100, -300*(count+1) + 100)
        compare_node.operation = 'EQUAL'
        compare_node.data_type = 'INT'
        
        compare_node.inputs[3].default_value = count + 1
        
        if hasLM == True:
            #make a linkMat Nodes group here
            lm_node = subcoll_group.nodes.new(type="GeometryNodeGroup")
            
            #set a color
            lm_node.use_custom_color = True
            lm_node.color = (0.6, 0.02, 0.45)
            
            lm_node.node_tree = linkMatGroups[objLM][0]
            lm_node.location = (-100, -300*(count+1)-50)
            #lm_node.integer = objLM
            
            #LINKS
            subcoll_group.links.new(obj_node.outputs[3], lm_node.inputs[0])
            subcoll_group.links.new(lm_node.outputs[0], switch_node.inputs[15])
            subcoll_group.links.new(groupIn.outputs[3], lm_node.inputs[1])
            subcoll_group.links.new(groupIn.outputs[4], lm_node.inputs[2])
            
        else:
            
            #LINKS
            subcoll_group.links.new(obj_node.outputs[3], switch_node.inputs[15])
            
        #LINKS
        subcoll_group.links.new(compare_node.outputs[0], switch_node.inputs[1])
        subcoll_group.links.new(groupIn.outputs[1], compare_node.inputs[2])
        subcoll_group.links.new(switch_node.outputs[6], join_node.inputs[0])
        
        
        count += 1




    return bpy.data.node_groups[subcoll_group.name]


def make_linkMat_group_nodes():
    lmGroups = linkMats("Variants")
    count = 0
    
    all_lmGroups_nodes = []
    
    for lmGroup in lmGroups:
        all_lmGroups_nodes.append(make_linkMat_group_node(lmGroups[count], count))
        count += 1
    

    return (all_lmGroups_nodes)
        
        
def make_linkMat_group_node(lmGroup, groupNum):
    lmGroup_nodes = bpy.data.node_groups.new("LinkMat Group " + str(groupNum), "GeometryNodeTree")
    
    objs = lmGroup[0]
    matLib = lmGroup[1]
    lmMaterials = []
    
    for slot in matLib.material_slots:
        if slot.material != None:
            lmMaterials.append(slot.material)
    
    
    
    
    lmGroup_nodes.inputs.new("NodeSocketGeometry", "Geometry")
    lmGroup_nodes.inputs.new("NodeSocketBool", "Animated")
    lmGroup_nodes.inputs.new("NodeSocketInt", "Frame Advance")

    
    lmGroup_nodes.outputs.new("NodeSocketGeometry", "Geometry")
    
    groupIn = lmGroup_nodes.nodes.new("NodeGroupInput")
    groupOut = lmGroup_nodes.nodes.new("NodeGroupOutput")
    
    groupIn.location = (-500,0)
    groupOut.location = (300,0)
    
    
    set_mat_node = lmGroup_nodes.nodes.new("GeometryNodeSetMaterial")
    set_mat_node.location = (100,0)
    
    mat_index_node = lmGroup_nodes.nodes.new("GeometryNodeInputMaterialIndex")
    mat_index_node.location = (-500, -100)
    
    ind_compare_node = lmGroup_nodes.nodes.new("FunctionNodeCompare")
    ind_compare_node.location = (-100, -100)
    ind_compare_node.data_type = 'INT'
    ind_compare_node.operation = 'EQUAL'
 
 
 
     
    
    material_data_set = []
    #GENERATE MATERIALS DATA NODE
    
    data_count = 0
    while data_count < bpy.context.scene.var_gen:
        material_data_set.append(genRandomMaterial(matLib))
        data_count += 1
    
    
    
    
    
    data_set = lmGroup_nodes.nodes.new(type="GeometryNodeGroup")
    data_set.label = "Material Data"
    data_set.location = (-1000, -200)
    data_set.node_tree = make_data_group(material_data_set)
    
    data_switch = lmGroup_nodes.nodes.new(type="GeometryNodeSwitch")
    data_switch.location = (data_set.location[0]-200, - 200)
    data_switch.input_type = 'INT'

    scene_time_node = lmGroup_nodes.nodes.new(type="GeometryNodeInputSceneTime")
    scene_time_node.location = (data_set.location[0]-400, - 200)
 
    
    
    #MATERIAL SECTION
    previous_mat = None
    
    count = 0
    length = len(lmMaterials)
    for lmMaterial in lmMaterials:
        material_node = lmGroup_nodes.nodes.new(type="GeometryNodeInputMaterial")
        material_node.location = (-300,-200*count-500)
        material_node.label = lmMaterial.name
        material_node.material = lmMaterial
        
        
        switch_node = lmGroup_nodes.nodes.new(type="GeometryNodeSwitch")
        switch_node.location = (-100, -200*count-400)
        switch_node.input_type = 'MATERIAL'
        
        compare_node = lmGroup_nodes.nodes.new(type="FunctionNodeCompare")
        compare_node.location = (-500, -200*count-400)
        compare_node.data_type = 'INT'
        compare_node.inputs[3].default_value = count
        compare_node.operation = 'GREATER_THAN'
                
#        add_node = lmGroup_nodes.nodes.new(type="ShaderNodeMath")
#        add_node.location = (100, -200*count-500)
#        add_node.inputs[0].default_value = 0
#        add_node.inputs[1].default_value = 0
        
        if previous_mat == None:
            lmGroup_nodes.links.new(material_node.outputs[0], switch_node.inputs[23])
            previous_mat = switch_node
        else:
            lmGroup_nodes.links.new(material_node.outputs[0], switch_node.inputs[23])
            lmGroup_nodes.links.new(previous_mat.outputs[10], switch_node.inputs[22])
            previous_mat = switch_node

        #lmGroup_nodes.links.new(material_node.outputs[0], switch_node.inputs[21])
        lmGroup_nodes.links.new(compare_node.outputs[0], switch_node.inputs[1])
        lmGroup_nodes.links.new(data_set.outputs[0], compare_node.inputs[2])
        
        count += 1
        
        if count == length:
            #add_node.inputs[1].default_value = 1
            lmGroup_nodes.links.new(switch_node.outputs[10], set_mat_node.inputs[2])

    
    
    #LINKS
    lmGroup_nodes.links.new(groupIn.outputs[0], set_mat_node.inputs[0])
    lmGroup_nodes.links.new(set_mat_node.outputs[0], groupOut.inputs[0])
    lmGroup_nodes.links.new(mat_index_node.outputs[0], ind_compare_node.inputs[2])
    lmGroup_nodes.links.new(ind_compare_node.outputs[0], set_mat_node.inputs[1])
    
    lmGroup_nodes.links.new(scene_time_node.outputs[1], data_switch.inputs[4])
    lmGroup_nodes.links.new(data_switch.outputs[1], data_set.inputs[0])
    lmGroup_nodes.links.new(groupIn.outputs[2], data_switch.inputs[5])
    lmGroup_nodes.links.new(groupIn.outputs[1], data_switch.inputs[0])
    
    #NODES in 0
    #linkMat objs in 1
    
    #RETURN PACKAGE -- couldn't think of a better name lol
    ret_pack = [lmGroup_nodes, objs]
    return ret_pack








def make_hostcoll_group(hostcollection, proxy, genCodesList):
    
    obj = bpy.data.objects[proxy.name]

    mod = obj.modifiers.new('FZRandomizer', 'NODES')

    host = bpy.data.collections[hostcollection]
    hostcoll_group = bpy.data.node_groups.new("HOST " + hostcollection, "GeometryNodeTree")
    
    
    groupIn = hostcoll_group.nodes.new("NodeGroupInput")
    groupIn.location = (-800, 0)


    groupOut = hostcoll_group.nodes.new("NodeGroupOutput")
    groupOut.location = (700,0)

    hostcoll_group.inputs.new("NodeSocketGeometry", "Input")
    hostcoll_group.inputs.new("NodeSocketBool", "Use Generation")
    hostcoll_group.inputs[1].default_value = True
    hostcoll_group.outputs.new("NodeSocketGeometry", "Output")
    
    
    join_node = hostcoll_group.nodes.new(type="GeometryNodeJoinGeometry")
    join_node.location = (250,0)
    
    
    set_pos_node = hostcoll_group.nodes.new(type="GeometryNodeSetPosition")
    set_pos_node.location = (500,0)
    
    obj_node = hostcoll_group.nodes.new(type="GeometryNodeObjectInfo")
    obj_node.location = (250, -150)
    obj_node.inputs[0].default_value = bpy.data.objects["proxy"]



    scene_time_node = hostcoll_group.nodes.new(type="GeometryNodeInputSceneTime")
    scene_time_node.location = (groupIn.location[0], - 300)
    
    
    animatedSwitch_node =  hostcoll_group.nodes.new(type="GeometryNodeSwitch")
    animatedSwitch_node.location = (groupIn.location[0], - 400)
    animatedSwitch_node.input_type = 'INT'


    subtract_node = hostcoll_group.nodes.new(type="ShaderNodeMath")
    subtract_node.location = (groupIn.location[0], - 600)
    subtract_node.operation = 'SUBTRACT'
    subtract_node.inputs[1].default_value = 1
    
    stillsAnimated = hostcoll_group.inputs.new("NodeSocketBool", "Still / Animated")
    variantInput = hostcoll_group.inputs.new("NodeSocketInt", "Variant")

    #SUBCOLLECTIONS
    
    linkMatGroups = make_linkMat_group_nodes()
    
    inputCount = len(hostcoll_group.inputs)
    
    fulldata = flip_data_set(genCodesList)
    
    dataReadout = 0
    data_fullRead = len(fulldata[0]) * len(host.children)
    
    #ONE STRING SLICER TO RULE THEM ALL
    #for the string slicer to use
    slicer = make_string_slicer_group(100)
    
    count = 0
    for coll in host.children:
        subcoll = hostcoll_group.nodes.new(type="GeometryNodeGroup")
        subcoll.location = (0, -200*count)
        subcoll.node_tree = make_subcoll_group(coll.name, linkMatGroups)
        subcoll.label = subcoll.inputs[1].name
        
        
        data = fulldata[count]
        
        
        
        
        data_set = hostcoll_group.nodes.new(type="GeometryNodeGroup")
        data_set.label = subcoll.inputs[1].name
        data_set.location = (-500, -200*count-300)
        
        data_set.node_tree = make_string_data_group(data, slicer)
        #data_set.node_tree = make_data_group(data, dataReadout, data_fullRead)
        
        dataReadout += len(data)
        
        keyedValue = hostcoll_group.nodes.new(type="FunctionNodeInputInt")
        keyedValue.label = subcoll.inputs[1].name
        keyedValue.name = str(count)
        keyedValue.location = (-1500, -200*count-300)
        
        switch_node = hostcoll_group.nodes.new(type="GeometryNodeSwitch")
        switch_node.location = (-300, -200*count-300)
        switch_node.input_type = 'INT'
        

        
        hostIntInput = hostcoll_group.inputs.new("NodeSocketInt", subcoll.inputs[1].name)
        hostIntInput.min_value = 1
        hostIntInput.default_value = 1
        hostIntInput.max_value = subcoll.inputs[2].default_value
        
        #LINKS
        hostcoll_group.links.new(subcoll.outputs[0], join_node.inputs[0])
        hostcoll_group.links.new(subcoll.inputs[1], switch_node.outputs[1])
        
        hostcoll_group.links.new(groupIn.outputs[1], switch_node.inputs[0])
        hostcoll_group.links.new(groupIn.outputs[count + inputCount], switch_node.inputs[4])
        hostcoll_group.links.new(data_set.outputs[0], switch_node.inputs[5])
        
        hostcoll_group.links.new(subtract_node.outputs[0], data_set.inputs[0])
        
        hostcoll_group.links.new(groupIn.outputs[2], subcoll.inputs[3])
        hostcoll_group.links.new(groupIn.outputs[3], subcoll.inputs[4])
        
        count += 1
    
        
    #3.2 PATCH -- TURN OFF SET POS NODE
#    hostcoll_group.links.new(join_node.outputs[0], set_pos_node.inputs[0])
#    hostcoll_group.links.new(set_pos_node.outputs[0], groupOut.inputs[0])
    
    #3.2 PATCH --- BYPASS
    hostcoll_group.links.new(join_node.outputs[0], groupOut.inputs[0])
    
    #--------------------------
    
    
    hostcoll_group.links.new(obj_node.outputs[0], set_pos_node.inputs[3])
    hostcoll_group.links.new(scene_time_node.outputs[1], animatedSwitch_node.inputs[4])
    hostcoll_group.links.new(groupIn.outputs[3], animatedSwitch_node.inputs[5])
    hostcoll_group.links.new(groupIn.outputs[2], animatedSwitch_node.inputs[0])
    hostcoll_group.links.new(animatedSwitch_node.outputs[1], subtract_node.inputs[0])
    
    mod.node_group = hostcoll_group
    return hostcoll_group



def makeGeoProxy(genCodesList, ng):
    geoNodesProxyColl = bpy.data.collections['Geometry Nodes Proxy']
    
    proxy = geoNodesProxyColl.objects[0]
    
    bpy.context.scene.proxy_obj = proxy
    
    print (proxy)
    
#    frm = 1
#    for code in genCodesList:
#        print ("Frame " + str(frm) + ": ")
#        slotCount = 0
#        
#        for slot in code:
#            #GEONODES KEYFRAMES
##            print ("keying " + str(slot) + " in " + str(slotCount-1) + " of " + str(code))
##            datapath = 'modifiers["FZRandomizer"]["Input_' + str(slotCount) + '"]'
##            
##            bpy.data.objects["proxy"].modifiers["FZRandomizer"]["Input_" + str(slotCount)] = slot + 1
##            proxy.keyframe_insert(datapath, frame = frm) 
#            
#            #INTERNAL VALUE KEYFRAMES
#            print ("keying " + str(slot) + " in " + str(slotCount-1) + " of " + str(code))
#            datapath = 'nodes["'+str(slotCount)+'"].integer'
#            
#            ng.nodes[str(slotCount)].integer = slot + 1
#            ng.keyframe_insert(datapath, frame = frm) 
#            
#            #bpy.data.node_groups["HOST Sad Ones.081"].nodes["0"].integer
#            
#            
#            slotCount += 1
#        print ("\n\n")
#        frm += 1
    
    
def long_data_string(data_set):
    data_string = ''
    for data in data_set:
        dataPiece = f'{data:03d}'
        dataPiece += "_"
        
        data_string += dataPiece
    
    return (data_string)

def make_string_data_group(data_set, slicer):
    

    
    data_group = bpy.data.node_groups.new("STRING DATA GROUP", "GeometryNodeTree")
    
    
    groupIn = data_group.nodes.new("NodeGroupInput")
    groupIn.location = (-200, 0)


    groupOut = data_group.nodes.new("NodeGroupOutput")
    groupOut.location = (400,0)

    data_group.inputs.new("NodeSocketInt", "Input")
    data_group.outputs.new("NodeSocketInt", "Output")
    
    string_node = data_group.nodes.new("FunctionNodeInputString")
    
    slice_node = data_group.nodes.new(type="GeometryNodeGroup")
    slice_node.node_tree = slicer
    slice_node.location = (200, 0)
    
    #MAKE THE STRING DATA HERE
    #make the whole data set into a working data string
    data_string = long_data_string(data_set)
    
    string_node.string = data_string
    
    
    #links
    data_group.links.new(groupIn.outputs[0], slice_node.inputs[1])
    data_group.links.new(string_node.outputs[0], slice_node.inputs[0])
    data_group.links.new(slice_node.outputs[0], groupOut.inputs[0])
    
    
    return(data_group)

def make_string_slicer_group(depth):
    
    slicer_group = bpy.data.node_groups.new("SLICER GROUP", "GeometryNodeTree")
    
    slicer_group.inputs.new("NodeSocketString", "DATA")
    slicer_group.inputs.new("NodeSocketInt", "Input")
    slicer_group.outputs.new("NodeSocketInt", "SELECTION")
    
    groupIn = slicer_group.nodes.new("NodeGroupInput")
    groupIn.location = (-700, 0)
    
    slice_node = slicer_group.nodes.new("FunctionNodeSliceString")
    slice_node.location = (-300, 0)
    slice_node.inputs[2].default_value = 3
    
    multFour = slicer_group.nodes.new("ShaderNodeMath")
    multFour.location = (-500, 0)
    multFour.inputs[1].default_value = 4
    multFour.operation = 'MULTIPLY'


    groupOut = slicer_group.nodes.new("NodeGroupOutput")
    groupOut.location = (1000,0)
    
    
    slicer_group.links.new(groupIn.outputs[0], slice_node.inputs[0])
    slicer_group.links.new(groupIn.outputs[1], multFour.inputs[0])
    slicer_group.links.new(multFour.outputs[0], slice_node.inputs[1])
    
    previous = None
    count = 0
    while count < depth:
        
        print ("(" + str(count / depth*100) + ")%")
        yLocation = -count*200
        
        #compare
        compare_node = slicer_group.nodes.new("FunctionNodeCompare")
        compare_node.location = (-100, yLocation)
        compare_node.data_type = 'STRING'
        
        compare_node.inputs[9].default_value = f'{count:03d}'
        
        
        #multiply
        multiply_node = slicer_group.nodes.new("ShaderNodeMath")
        multiply_node.location = (100, yLocation)
        multiply_node.operation = 'MULTIPLY'
        multiply_node.inputs[1].default_value = count
        
        #add
        add_node = slicer_group.nodes.new("ShaderNodeMath")
        add_node.location = (300, yLocation)
        add_node.inputs[0].default_value = 0
        add_node.inputs[1].default_value = 0
        
        add_node.operation = 'ADD'
        
        
        #links
        
        slicer_group.links.new(slice_node.outputs[0], compare_node.inputs[8])
        slicer_group.links.new(compare_node.outputs[0], multiply_node.inputs[0])
        
        if previous != None:
            slicer_group.links.new(previous.outputs[0], add_node.inputs[0])
            slicer_group.links.new(multiply_node.outputs[0], add_node.inputs[1])
        else:
            slicer_group.links.new(multiply_node.outputs[0], add_node.inputs[0])
        
        previous = add_node
        
        
        
        count += 1
        
        if count == depth:

            #one final add node to add 1 to the count
            new_add_node = slicer_group.nodes.new("ShaderNodeMath")
            new_add_node.location = (300, yLocation-200)
            new_add_node.inputs[0].default_value = 0
            new_add_node.inputs[1].default_value = 1
            
            new_add_node.operation = 'ADD'

            slicer_group.links.new(add_node.outputs[0], new_add_node.inputs[0])
        
            slicer_group.links.new(new_add_node.outputs[0], groupOut.inputs[0])
        
    return (slicer_group)

def make_data_group(data_set, readout, fullread):


    data_group = bpy.data.node_groups.new("DATA GROUP", "GeometryNodeTree")
    
    
    groupIn = data_group.nodes.new("NodeGroupInput")
    groupIn.location = (-500, 0)


    groupOut = data_group.nodes.new("NodeGroupOutput")
    groupOut.location = (1000,0)

    data_group.inputs.new("NodeSocketInt", "Input")
    data_group.outputs.new("NodeSocketInt", "Output")
    
    

    
    
    
    previous_add = None
    
    count = 0
    length = len(data_set)
    
    print ("DATA TIME YO")
    for data in data_set:
        
        percent = readout / fullread * 100
        
        print ("(" + str(percent) + "%) " +"making int node")
        data_piece = data_group.nodes.new(type="FunctionNodeInputInt")
        data_piece.location = (0,-200*count-100)
        data_piece.label = str(count)
        data_piece.integer = data
        
        
        print ("(" + str(percent) + "%) " +"making switch node")
        switch_node = data_group.nodes.new(type="GeometryNodeSwitch")
        switch_node.location = (200, -200*count)
        switch_node.input_type = 'INT'
        
        
        print ("(" + str(percent) + "%) " +"making compare node")
        compare_node = data_group.nodes.new(type="FunctionNodeCompare")
        compare_node.location = (-200, -200*count)
        compare_node.data_type = 'INT'
        compare_node.inputs[3].default_value = count
        compare_node.operation = 'EQUAL'
        
        
        print ("(" + str(percent) + "%) " +"making add node")        
        add_node = data_group.nodes.new(type="ShaderNodeMath")
        add_node.location = (400, -200*count-100)
        add_node.inputs[0].default_value = 0
        add_node.inputs[1].default_value = 0
        
        
        print ("(" + str(percent) + "%) " +"making links")
        
        readout += 1
        
        if previous_add == None:
            data_group.links.new(switch_node.outputs[1], add_node.inputs[0])
            previous_add = add_node
        else:
            data_group.links.new(previous_add.outputs[0], add_node.inputs[0])
            data_group.links.new(switch_node.outputs[1], previous_add.inputs[1])
            previous_add = add_node

        data_group.links.new(data_piece.outputs[0], switch_node.inputs[5])
        data_group.links.new(compare_node.outputs[0], switch_node.inputs[0])
        data_group.links.new(groupIn.outputs[0], compare_node.inputs[2])
        
        count += 1
        
        if count == length:
            add_node.inputs[1].default_value = 1
            data_group.links.new(add_node.outputs[0], groupOut.inputs[0])
    
    

    
    return(data_group)


"""----------------------------MAJOR--FUNCTIONS-------------------------------------"""
              
            
def multiOBJ(context):
    
    freshConsole(5)
    print("-----------GENERATING VARIANTS------------")
    freshConsole(1)
    
    '''bpy.types.Scene.char_collection'''
    name = bpy.context.scene.char_collection
    generations = bpy.context.scene.var_gen
    
    
    warning = ""
    
    
    """CHECK AND SEE IF HOST NAME EXISTS"""
    allColl = bpy.data.collections
    
    
    hostExists = collExists(name)
    atRoot = collAtRoot(name)
    poss = 0
    
    if hostExists == True:
        bpy.context.view_layer.layer_collection.children[name].exclude = False
        poss = possibilities()
    else:
        warning = "Host name does not exist."
        poss = 0
    
    nonZeroPoss = True
    
    if warning != "Host name does not exist.":
        if poss == 0:
            nonZeroPoss = False
            warning = "Empty collection detected in " + name + " collection."
        
    uniquePossible = True
    
    if bpy.context.scene.unique_variants == True:
        if generations > poss:
            uniquePossible = False
            if warning != "Host name does not exist.":
                warning = "Not Enough Variation For " + str(bpy.context.scene.var_gen) + " Unique Generations."
            """LIST REASON HERE"""
        
        
        else:
            """REMOVE REASON"""
    
    
    """CONDITIONS LIST TO RUN MULTI GEN TOOL"""
    conditions = []
    conditions.append(hostExists)
    conditions.append(atRoot)
    conditions.append(uniquePossible)
    conditions.append(nonZeroPoss)
    
    
    clearToLaunch = True
    
    """ARE ALL CONDITIONS TRUE FOR MULTIGEN LAUNCH"""
    for x in conditions:
        if x == False:
            clearToLaunch = False
        else:
            """CLEAR TO LAUNCH IS TRUE BY THAT CONTITION"""
    
            
    if clearToLaunch == True:
        genCodesList = []
        proxyParametersList = []
        
        print("Gotta Check 1")
        print (genCodesList)
        
        buildChars(name, generations, genCodesList, proxyParametersList)
        
        print("Gotta Check 2")
        print (genCodesList)
        
        if bpy.context.scene.useProxySwap != True:
            if bpy.context.scene.autoSpawn == True:
                spawnVars()

    else:
        """HOST DID NOT EXIST"""
        print ('nope')
        bpy.context.scene.host_name_warning = warning




def buildChars(name, generations, genCodesList, proxyParametersList):
    
    genCSV = bpy.context.scene.gen_csv
    genJSON = bpy.context.scene.gen_json
    overwrite = bpy.context.scene.overwrite_csv
    
    """HOST EXISTS - CONTINUE"""
    hostExists = True
    

    host = bpy.data.collections[name]
    
    props = host.children
    
    folderName = 'Variants'
    varNames = 'Variant'
    
    assignNumberToAsset(host)
    
    """GENERATE VARIANTS FOLDER IF IT DOESNT ALREADY EXIST"""
    
    collCleaner(folderName)
    
    variantColl = bpy.context.blend_data.collections.new(name=folderName)
    bpy.context.scene.collection.children.link(variantColl)
    
    v = 0
    
    win = bpy.context.window_manager

    
    """PRIME ATTRIBUTES - SET ATTRIBUTE PROPERTIES FOR EACH ATTRIBUTE"""
    #send the host collection to prime all objects inside
    setAllSubOrigins(host)
    
    """BEGIN BUILDING CHARACTERS"""

    win.progress_begin(0, generations)
    
    
    while v < generations:
        #generate each character
        buildChar (host, props, varNames + " " + str(v+1), genCodesList, proxyParametersList)
        
        #linkmats if using Legacy Model
        if bpy.context.scene.useProxySwap == False:
            linkMats("Variant " + str(v + 1))

        win.progress_update(v)
        v += 1

        
    if bpy.context.scene.useProxySwap == True:
        
        
        ng = buildHostProxy(genCodesList)
        
        #MAKE PROXY KEYFRAMES
        #queueProxy(proxyParametersList)
        
        uncheck_collection("Variants", True)
        uncheck_collection(host.name, True)
        
        #bpy.context.space_data.context = 'MODIFIER'

        
        makeGeoProxy(genCodesList, ng)
        
        
        updateSceneGenCodes(genCodesList)

    v = 0
            
    win.progress_end()
    
    
    
    

    
    
    
    """IF NEEDED TO WRITE TO CSV DO HERE"""
    
    if genCSV == True:
    
        win.progress_begin(0, generations)
        
        print("Writing to CSV...")
        
        
        
        """DETERMINE HOW MANY COLUMNS AND COLUMN NAMES"""
        firstRow = ["Variant"]
        
        fCount = 0
        hostSubs = listHostSubs()
        
        #extraObjects = bpy.data.collections["Variant 1"].objects
        if bpy.context.scene.useProxySwap == False:
            while fCount < len(hostSubs):
                
                """Each Column"""
                firstRow.append(hostSubs[fCount] + " Name")
                firstRow.append(hostSubs[fCount] + " Material")
                firstRow.append(hostSubs[fCount] + " Tickets")
                firstRow.append(hostSubs[fCount] + ": Total Tickets")
                firstRow.append(hostSubs[fCount] + " Odds (% chance)")
                
                fCount += 1
        else:
            while fCount < len(hostSubs):
                
                """Each Column"""
                firstRow.append(hostSubs[fCount] + " Name")
#                firstRow.append(hostSubs[fCount] + " Material")
#                firstRow.append(hostSubs[fCount] + " Tickets")
#                firstRow.append(hostSubs[fCount] + ": Total Tickets")
#                firstRow.append(hostSubs[fCount] + " Odds (% chance)")
                
                fCount += 1
        
            
        """WRITE THE HEADER OF DOCUMENT"""
        appDataSheet(firstRow, overwrite)   
        
        """WRITE EACH ROW OF VARIANT DATA"""
        if bpy.context.scene.useProxySwap == False:
            while v < generations:
                variant_to_csv(str(v + 1))
                buildMetadata(v, proxyParametersList)
                win.progress_update(v)
                v += 1
        else:
            while v < generations:
                proxy_to_csv(v, proxyParametersList)
                #buildMetadata(v, proxyParametersList)
                
                win.progress_update(v)
                v += 1
        
        print("CSV Document generated.")
        
        
        
    """reset counter"""    
    v = 0
        
    """IF NEEDED TO WRITE TO CSV DO HERE"""
        
        
    if genJSON == True:
        while v < generations:
            buildMetadata(v, proxyParametersList)
            win.progress_update(v)
            v += 1

                
        print ("JSON generated.")
    
    win.progress_end()
    
    bpy.context.scene.host_name_warning = "Host Located: " + bpy.context.scene.char_collection
    
    print ("genCodes:")
    listPrinter(genCodesList)
    print ("proxyParameterList")
    listPrinter(proxyParametersList)



def listPrinter(array):
    #receive a 2D array
    for arr in array:
        print (arr)



    
def proxy_to_csv(proxy, proxyParametersList):
    print(proxyParametersList[proxy])
    """Look at the proxy number and find attributes"""
    """List attributes into csv"""
    
        
    
    
    dataEntry = [str(proxy + 1)]
    
    subs = listHostSubs()
    
    for sub in subs: 
        for obj in proxyParametersList[proxy]:
            
            """CHECK AND SEE IF THAT OBJECT IS FIRST IN LINE FOR DATA ENTRY"""
            """THIS IS ALPHABETIC ORDER OF SUBCOLLECTIONS, NOT OBJECT NAMES"""
            
            if obj['Sub Origin'] == sub:
                
                """ADD OBJECT NAME"""
                
                if obj.attribute_md.mdUseCustom == True:
                    dataEntry.append(obj.fzAttribute)    
                else:
                    dataEntry.append(obj.name)
                
                
#                """ADD MATERIAL NAME"""
#                if len(obj.material_slots) > 0:
#                    if obj.material_slots[0].material != None:
#                        dataEntry.append(obj.material_slots[0].material.name)
#                    else:
#                        dataEntry.append("No Material")
#                else:
#                    dataEntry.append("No Material")
#                
#                """ADD OBJECT TICKETS"""
#                dataEntry.append(obj.fzRarity)
#                
#                """ADD OBJECT SUB TOTAL TICKETS"""
#                subColl = bpy.data.collections[obj['Sub Origin']]
#                totalTickets = subTicketCounter(subColl)
#                dataEntry.append(totalTickets)
#                
#                """ADD OBJECT ODDS"""
#                objOdds = round(obj.fzRarity/totalTickets*100)
#                dataEntry.append(objOdds)
                
    appDataSheet(dataEntry, False)
    
    

def variant_to_csv(collName):
    
    
    
    dataEntry = [collName]
    
    subs = listHostSubs()
    
    for sub in subs: 
        for obj in bpy.data.collections[collName].objects:
            
            """CHECK AND SEE IF THAT OBJECT IS FIRST IN LINE FOR DATA ENTRY"""
            """THIS IS ALPHABETIC ORDER OF SUBCOLLECTIONS, NOT OBJECT NAMES"""
            
            if obj['Sub Origin'] == sub:
                
                """ADD OBJECT NAME"""
                dataEntry.append(obj.name)
                
                
                """ADD MATERIAL NAME"""
                if len(obj.material_slots) > 0:
                    if obj.material_slots[0].material != None:
                        dataEntry.append(obj.material_slots[0].material.name)
                    else:
                        dataEntry.append("No Material")
                else:
                    dataEntry.append("No Material")
                
                """ADD OBJECT TICKETS"""
                dataEntry.append(obj.fzRarity)
                
                """ADD OBJECT SUB TOTAL TICKETS"""
                subColl = bpy.data.collections[obj['Sub Origin']]
                totalTickets = subTicketCounter(subColl)
                dataEntry.append(totalTickets)
                
                """ADD OBJECT ODDS"""
                objOdds = round(obj.fzRarity/totalTickets*100)
                dataEntry.append(objOdds)
                
    appDataSheet(dataEntry, False)
            
            
            
#def hideVPR():
#         """set all objects in collection to off except winner"""
#    
#    a = 0
#    print ("Collection: " + props[x].name)
#    print ("Turn Off:")
#    while a < objCount:
#        props[x].objects[a].hide_render = hvpr
#        props[x].objects[a].hide_viewport = hvpr
##            print (props[x].objects[a].name)
#        a += 1
#    
    
    


def buildHostProxy(genCodesList):


    """Find The Host Collection"""    
    host = bpy.context.scene.char_collection
    


    
    
    
    
    """Duplicate all objs to Host Proxy"""
    for obj in bpy.data.collections[host].objects:
        dupToNewColl(obj, "Variants", True)
    
    subs = listHostSubs()
    
    subCount = 0
    for sub in subs: 
        subColl = bpy.context.blend_data.collections.new(name=subs[subCount] + " Proxy")
        bpy.data.collections["Variants"].children.link(subColl)
        
        """ALL OBJECTS FROM OG SUBCOLLECTION DUP TO NEW COLL INTO THIS BAD BOY"""
        objs = bpy.data.collections[subs[subCount]].objects
        for obj in objs:
            dupToNewColl(obj, subColl.name, True)
        subCount += 1
        

        
        
    """Find Children Collections"""
    """Duplicate all objs in each subcollection"""   
    
    
    """ADD ARMATURES TO PROXIES"""
    #NOT IMPLEMENTED YET
    #armatures_to_proxies()
    
    
    """NEW GEOMETRY NODES METHOD"""
    
    folderName = "Geometry Nodes Proxy" 
    collCleaner(folderName)
    

    variantColl = bpy.context.blend_data.collections.new(name=folderName)
    bpy.context.scene.collection.children.link(variantColl)
    
    bpy.ops.mesh.primitive_cube_add()
    #current_coll = findMyColl(bpy.context.selected_objects[0])

    # newly created cube will be automatically selected
    proxy = bpy.context.selected_objects[0]
    current_coll = findMyColl(proxy)
    # change name
    proxy.name = "proxy"
    
    #PUTS THE NEW GEOMETRY NODES PROXY INTO A GEO NODES PROXY COLLECTION
    variantColl.objects.link(proxy)
    
    #REMOVES IT FROM WHEREVER THE PROXY WAS SPAWNED INTO
    if current_coll != None:
        current_coll.objects.unlink(proxy)
    else:
        bpy.context.scene.collection.objects.unlink(proxy)
    
    #BRING BACK THE NODE GROUP
    ng = make_hostcoll_group(host, proxy, genCodesList)
    
     
    
    return ng
    
    
    
    
    
    
    
def swapVar(name, number):
    
    varCode = bpy.context.scene.metadataVariantVar
     
    codePosition = name.find(varCode)
    
    newName = name
    
    while codePosition != -1:
        
        front = newName[0:codePosition]
        print (front)
        end = newName[codePosition+len(varCode):]
        print (end)
        newName = front + number + end
        
        print (newName)
        
        codePosition = newName.find(varCode)
        
    return newName
    
    
    
    
    """METADATA FUNCTIONS"""
    
def buildMetadata(filename, proxyParametersList):
    """Accept a list of objects that make up a variant"""
    proxy = filename
    filename = str(proxy+1)
    scn = bpy.context.scene
    
    metadata = {}
    
    nested = []
    mdCount = 0
    for md in scn.md_list:
        if mdHasPeriod(md.mdName) == False:
            
            if md.mdName == bpy.context.scene.metadataAttributeName:
                
                """--------ATTRIBUTES--------------"""
                subs = listHostSubs()    
                attributes = []
                

                for sub in subs:
                    for obj in proxyParametersList[proxy]:
                        
                        """CHECK AND SEE IF THAT OBJECT IS FIRST IN LINE FOR DATA ENTRY"""
                        """THIS IS ALPHABETIC ORDER OF SUBCOLLECTIONS, NOT OBJECT NAMES"""
                        
                        if obj['Sub Origin'] == sub:
                            
                            """ADD OBJECT NAME"""
                            attribute = {}
                            
                            """ATTRIBUTE HAS SPECIFIC DISPLAY TYPE"""
                            if obj.attribute_md.mdDisplay != "string":
                                
                                """ATTRIBUTE USES CUSTOM DISPLAY TYPE"""
                                if obj.attribute_md.mdDisplay == "custom":
                                    attribute["display_type"] = obj.attribute_md.mdCustomDisplay
                                else:
                                    attribute["display_type"] = obj.attribute_md.mdDisplay
                            
                            attribute[scn.metadataTraitTypeName] = sub
                            if obj.attribute_md.mdUseCustom == False:
                                attribute[scn.metadataValueName] = (obj.name)
                            else:
                                attribute[scn.metadataValueName] = (obj.fzAttribute)
                            attributes.append(attribute)
                            
                            
                            #attributes[sub] = sub + " selection"
                """--------ATTRIBUTES-DONE-------------"""
                metadata[scn.metadataAttributeName] = attributes
            else:    
                metadata[md.mdName] = swapVar(md.mdValue, filename)
        else:
            nested.append(md)
        
#    metadata['Description'] = swapVar(scn.metadata_description, filename)
#    if scn.metadata_extUrl != "":
#        metadata['External URL'] = swapVar(scn.metadata_extUrl, filename)
#    metadata['Image'] = swapVar(scn.metadata_ipfs, filename)
#    metadata['Name'] = swapVar(scn.metadata_name, filename)
    



#    """--------ATTRIBUTES--------------"""
#    subs = listHostSubs()    
#    attributes = []
#    

#    for sub in subs:
#        for obj in proxyParametersList[proxy]:
#            
#            """CHECK AND SEE IF THAT OBJECT IS FIRST IN LINE FOR DATA ENTRY"""
#            """THIS IS ALPHABETIC ORDER OF SUBCOLLECTIONS, NOT OBJECT NAMES"""
#            
#            if obj['Sub Origin'] == sub:
#                
#                """ADD OBJECT NAME"""
#                attribute = {}
#                
#                """ATTRIBUTE HAS SPECIFIC DISPLAY TYPE"""
#                if obj.attribute_md.mdDisplay != "string":
#                    
#                    """ATTRIBUTE USES CUSTOM DISPLAY TYPE"""
#                    if obj.attribute_md.mdDisplay == "custom":
#                        attribute["display_type"] = obj.attribute_md.mdCustomDisplay
#                    else:
#                        attribute["display_type"] = obj.attribute_md.mdDisplay
#                
#                attribute[scn.metadataTraitTypeName] = sub
#                if obj.attribute_md.mdUseCustom == False:
#                    attribute[scn.metadataValueName] = (obj.name)
#                else:
#                    attribute[scn.metadataValueName] = (obj.fzAttribute)
#                attributes.append(attribute)
#                
#                
#                #attributes[sub] = sub + " selection"
#    """--------ATTRIBUTES-DONE-------------"""
    
    
    
    
    
    properties = {}
    
    """FIND HOW MANY NESTS OF METADATA EXIST"""
    originalNests = []
    
    #sort through all nested metadata and find only unique nests
    for md in nested:
        nestName = mdTextPrePeriod(md.mdName)

        foundNest = False
        for nest in originalNests:
            if nest == nestName:
                #this nest already exists - accounted for
                foundNest = True
        
        if foundNest == False:
            #found a new nest - add to original nest liust
            originalNests.append(mdTextPrePeriod(md.mdName))
    
    
    #look at each nest in unique nests
    for nest in originalNests:
        metadataNest = []
        
        
        subNestCount = 0
        suffixList = []
        
        
        """HOW MANY SUBNESTS EXIST"""
        for md in nested:
            
            """Trim nest name"""
            mdNest = mdTextPrePeriod(md.mdName)
            localMD = mdTextPostPeriod(md.mdName)
            #print (mdNest)
            #print (nest)
            
            """HOW MANY SUBNESTS EXIST"""
            if mdNest == nest:
                suffix = mdNumberSuffix(localMD)
                
                #does this suffix already exist?
                suffixExists = False
                for sfx in suffixList:
                    if sfx == suffix:
                        suffixExists = True
                        break
                #found a new suffix - add it to the list of suffixes
                if suffixExists == False:
                    suffixList.append(suffix)
            
                #look through all of the suffixes
                #if you find a suffix larger than the subNestCount
                #that is the new highest subNestCount
                for sfx in suffix:
                    subNest = int(sfx)
                    if subNest > subNestCount:
                        subNestCount = subNest
            
            #subNestCount is the amount of SUBNESTS for this overall nest
        
        
        
        """GENERATE SUBNESTS NESTS"""
        snCounter = 0
        while snCounter < subNestCount:
            
            nestValues = {}
              
            for md in nested:
                
                
                """Trim nest name"""
                mdNest = mdTextPrePeriod(md.mdName)
                localMD = mdTextPostPeriod(md.mdName)
                #print (mdNest)
                #print (nest)
                
                """WHAT SUBNEST IS MD IN"""
                mdSubNest = mdNumberSuffix(localMD)
                if mdNest == "properties":
                    properties[localMD] = swapVar(md.mdValue, filename)
                                   
                if mdSubNest == str(snCounter+1):    
                    if mdNest == nest:
                        if mdNest != "properties":
                            print("mdSubNest: " + str(mdSubNest))
                            print("snCounter: " + str(snCounter+1))
                            nestValues[mdStripSuffix(localMD)] = swapVar(md.mdValue, filename)
                        

                    
            
            if len(nestValues) > 0:      
                metadataNest.append(nestValues) 
                properties[nest] = metadataNest
            snCounter += 1
    
    if len(properties) > 0:
        metadata["properties"] = properties
        
    #print (str(len(originalNests)) + " nests.")
    #for nest in originalNests:
        #print (nest)
                
            
    
    
    writeToJSONFile(filename, metadata)
 
    
    
    
def mdHasPeriod(name):
    
    for char in name:
        if char == ".":
            return True
    return False
            

def mdTextPrePeriod(name):
    count = 0
    for char in name:
        if char == ".":
            return name[0:count]
        count += 1
            
    return False

def mdTextPostPeriod(name):
    count = 0
    for char in name:
        if char == ".":
            return name[count+1:]
        count += 1
            
    return False



def mdNumberSuffix(name):
    
    charCount = 0
    foundSuffix = False
    for char in reversed(name):
        if char == ".":
            foundSuffix = True
            break
        charCount += 1
    
    nameLen = len(name) - charCount
    
    suffix = name[nameLen:]
    
    if foundSuffix == True:
        return suffix
    else:
        return str(1)
    
def mdStripSuffix(name):
    
    charCount = 0
    foundSuffix = False
    for char in reversed(name):
        if char == ".":
            foundSuffix = True
            break
        charCount += 1
    
    nameLen = len(name) - charCount
    
    strip = name[:nameLen-1]
    
    if foundSuffix == True:
        return strip
    else:
        return name





def assignNumberToAsset(host):
    
    subcolls = host.children
    
    for sub in subcolls:
        obj_count = 0
        for obj in sub.objects:
            obj['assignment'] = obj_count
            obj_count += 1



"""----------------GEN-CODE-TOOLS---------------------"""

def updateSceneGenCodes(genCodes):
    codes = bpy.context.scene.genCodes
    
    #remove all old genCodes in list
    codes.clear()
    
    encrypted = encryptGenCodes(genCodes)
    
    for code in encrypted:
        #add a code slot
        newCode = codes.add()

        #make that code the code from the slot
        newCode.genCode = code


def encryptGenCodes(genCodes):
    
    
    encrypted = []
    for code in genCodes:
        
        cryptLine = ""
        
        x = 0
        
        for c in code:
            
            #if it's not the first code, add a '-' before adding code
            if x != 0:
                cryptLine += "-"
                
            #add code to cryptLine
            cryptLine += str(c)
            
            #iterate
            x += 1
        
        encrypted.append(cryptLine)
    
    return (encrypted)


def GenCodes():
    codes = bpy.context.scene.genCodes
    
    decrypted = []
    
    for code in codes:
        dcrCode = []
        
        splitCode = code.split('-')
        for c in splitCode:
            
            #single codes will return as string : convert to int
            dcr = int(c)
            
            #append int version of code
            dcrCode.append(dcr)
        
        decrypted.append(dcrCode)
    
    return (decrypted)

    
    
    
    
    

"""----------------------------------------------------------------------------"""
"""----------------------------------------------------------------------------"""
"""----------------------------------------------------------------------------"""
"""-----------------------LINKMAT-GROUPS------MATLIBS--------------------------"""
"""----------------------------------------------------------------------------"""
"""----------------------------------------------------------------------------"""
"""----------------------------------------------------------------------------"""



def linkMats(collName):
    """TAKE A LIST OF OBJECTS AND FIND MATERIALS THAT NEED TO LINK - LINKS THEM"""
    
    objs = bpy.data.collections[collName].all_objects
    
    #------
    matCode = "lm0_"
    
    #LIST OF ALL LINKMAT GROUPS STARTS EMPTY
    linkMatGroups = []
    
    #--POSSIBLE TO GEN UP TO 10 LINKMAT GROUPS
    groups = 10
    
    #FILL MATS WITH 10 EMPTY LINKMAT GROUPS
    x = 0
    while x < groups:
        lmGroup = []
        linkMatGroups.append(lmGroup)
        x += 1 
    
    
    for obj in objs:
        
        #is the obj name even long enough to be a linkmat?
        if len(obj.name) >= 4:
            
            #check and see if the first 4 characters match a linkmat group
            x = 0
            while x < groups:
                matCode = "lm" + str(x) + "_"
                if obj.name[0:4] == matCode:
                    
                    #---FOUND AN OBJECT THAT IS IN A LINKMAT GROUP
                    bpy.context.view_layer.objects.active = obj
                    #print (bpy.context.object.active_material.name)
                    
                    #PUTS OBJECT IN ACCORDING LINKMAT GROUP
                    linkMatGroups[x].append(obj)
                x += 1
    
    #WE NOW HAVE FILLED linkMatGroups[[],[],[],[],...] with lists of all objs in lms
    #print("Linked Materials:")
    
    x = 0
    
    #Individually send all 10 groups to be
    #linked in linkMat() <--- accepts a list of objects
    
    matLibContainers = []
    
    while x < groups:
        linkObjs = len(linkMatGroups[x])
        
        if linkObjs > 1:
            """HEY"""
            #print (linkMatGroups[x])
            matLibContainers.append(linkMat(linkMatGroups[x]))
            
        
        x += 1
    
    return matLibContainers
            
            

    #print("Linked Materials Printed...")
    
    
    
def linkMat(objs):
    
    mlExists = False
    matLib = None
    
    #USING GEOMETRY NODES METHOD / TURN OFF OLD LINKING METHODS
    geoBypass = True
    
    amt = len(objs)
    
    libName = "MATLIB"
    
    
    for obj in objs:
        if obj.name[4:10] == libName:
            mlExists = True
            matLib = obj
            
    #-------IF MATLIBRARY IS PRESENT----------
    if geoBypass != True:
        if mlExists == True:
            
            #print ("MATLIBRARY FOUND........")
            setMLMats(objs, matLib)
            
            return None
            
            
        #-------------OTHERWISE-----------------    
        else:
            #Randomly delegate one in the group to be the material giver
            matNum = random.randint(0,amt-1)
            setMats(objs, objs[matNum])
            
            return None
        
    #--------GEOMETRY-NODES-METHOD-----------
    
    matLibContainer = [objs, matLib]
    
    return matLibContainer

    
    
def setMLMats(objs, matLib):
    #HOW MANY MATERIALS IN MAT LIBRARY    
    libLen = len(matLib.material_slots)
    if libLen > 0:
        matNum = random.randint(0,libLen-1)
        transferMat = matLib.material_slots[matNum].material
        
        for obj in objs:
            #print("Object " + obj.name + ": " + str(len(obj.material_slots)))
            if len(obj.material_slots) > 0 and obj != matLib:
                #only transfer the data if the material link is set to the object
                if obj.material_slots[0].link == 'OBJECT':
                    obj.material_slots[0].material = transferMat
            
        #print ("Transfer Material Located: " + transferMat.name)

def setMats(objs, matObj):
    if len(matObj.material_slots) > 0:
        transferMat = matObj.material_slots[0].material
        for obj in objs:
            print("Object " + obj.name + ": " + str(len(obj.material_slots)))
            if len(obj.material_slots) > 0:
                #only transfer the data if the material link is set to the object
                if obj.material_slots[0].link == 'OBJECT':
                    obj.material_slots[0].material = transferMat
                else:
                    #save the material incase#
                    """tempMat = obj.material_slots[0].material"""
                    
                    #change slot to object#
                    obj.material_slots[0].link = 'OBJECT'
                    
                    #apply New material
                    obj.material_slots[0].material = transferMat
            
        #print ("Transfer Material Located: " + transferMat.name)
    

def setLMName(obj, slot, isLM):
    
    name = obj.name
    
    currentlyLM = False
    
    """SEE IF THE LM EXISTS"""
    x = 0
    while x < 10:
        prefix = "lm" + str(x) + "_"
        print (prefix)
        if name[0:4] == prefix:
            currentlyLM = True
            print ("Prefix Match")

        x += 1
    
    """IF IT DOES, REMOVE IT"""
    if currentlyLM == True:
        print ("currentlyLM True")
        l = len(name)
        newName = obj.name[4:]
        print (newName)
        obj.name = newName
        print (obj.name)
        

    
    
    """SET OBJ NAME TO LMx_ IF NEED TO"""
    if isLM == True:
        prefix = "lm" + str(slot) + "_"
        obj.name = prefix + obj.name
        
    
    

  
"""----------------------------------------------------------------"""
"""----------------------------------------------------------------"""
"""----------------------------------------------------------------"""
"""----------------------------------------------------------------"""
"""----------------------------------------------------------------"""


def possibilities():
    
    hostName = bpy.context.scene.char_collection
    
    poss = 1
    
    if collExists(hostName):
        
        """hostColl is the Main Collection"""
        
        hostColl = bpy.data.collections[hostName]
        
        
        """HOW MANY VARIABLE COLLECTIONS"""
        
        for x in hostColl.children:
            
            """COUNT OBJ IN VARIABLE COLLECTION"""
            objs = x.objects
            count = len(objs)
            
            poss = poss * count
        
        warning = "Host Located: " + hostName
        bpy.context.scene.host_name_warning = warning
        
    else:
        poss = 0
        
        warning = "Host name does not exist."
        bpy.context.scene.host_name_warning = warning    
            
        
    return poss
        
def genRandomCode(props, unique):
    
    genCode = []
    
    x = 0
    
    while x < len(props):
        """randomize each collection parameter"""
        
        """get count of objects in collection"""
        
        ticketPool = 0
        
        objCount = len(props[x].objects)
        
        for prop in props[x].objects:
            ticketPool += prop.fzRarity
        


        
        """pick a winner based on whether its random or no Dups"""
        
        """RANDOM / UNIQUE RAND SEL"""
        if ticketPool > 0:
            ticket = random.randint(0, ticketPool-1)
        else:
            ticket = 0
        #print (ticket)
        
        
        """find the owner of that ticket"""
        ticketCounter = 0
        
        

        propNum = 0
        for prop in props[x].objects:

            if ticket >= ticketCounter:
                if ticket < ticketCounter + prop.fzRarity:
                    #print ("Selected is " + prop.name + " with " + str(prop.fzRarity) + " tickets.")
                    selObj = propNum
                    

        
            ticketCounter += prop.fzRarity
            propNum += 1
            
        
        
        
        #print (selObj)
        genCode.append(selObj)
        x += 1
    
    
#    #verify the rules here
#    verifiedRules = True
#    
#    codeCount = 0
#    for code in genCode:
#        
#        coll = props[codeCount]
#        obj = coll.objects[code]
#        
#        rules = obj.rules_list
#        rulesLen = len(rules)
#        
#        
#        print ("Checking Code: " + str(codeCount))
#        for rule in rules:
#            print ("CHECKING A RULE")
#            rule_obj = rule.obj
#            rule_collection = findMyColl(rule_obj)
#            rule_collection_num = countSubCollections(rule_collection)
#            
#            question_obj = genCode[rule_collection_num]
#            
#            print ("comparing " + obj.name + " to " + rule_obj.name + ": " +  rule.object_rule)
#            print (rule_obj.name + " from collection " + str(rule_collection_num))
#            
#            if rule.object_rule == 'Never':
#                if question_obj == rule_obj['assignment']:
#                    print (str(question_obj) + " " + str(rule_obj['assignment']))
#                    print ("This one is in violation... Trying again")
#                    
#                    verifiedRules = False
#                    break
#                    
#                            
#            
#            print ('\n\n\n')
##            if rule.object_rule == "Never":
##                print ("--Rule: Never")
##                print (str(genCode[rule_collection_num]) + " compared to " + str(rule_obj['assignment']))
##                if genCode[rule_collection_num] == rule_obj['assignment']:
##                    verifiedRules = False
##            
##            if rule.object_rule == "Always":
##                print ("--Rule: Always")
##                print (str(genCode[rule_collection_num]) + " compared to " + str(rule_obj['assignment']))
##                if genCode[rule_collection_num] != rule_obj['assignment']:
##                    verifiedRules = False
##        
#        codeCount += 1
#    
#    
#            
#    if verifiedRules == True:
#        print (genCode)

    return genCode
    
    #readCode(genCode, unique)


def countSubCollections(collection):
    
    hostname = bpy.context.scene.char_collection
    host = bpy.data.collections[hostname]
    
    
    count = 0
    for coll in host.children:
        if coll == collection:
            return count
        count += 1
    

def genRandomMaterial(MATLIB):

    materials = []  
    matSequence = []
      
    for matSlot in MATLIB.material_slots:
        materials.append(matSlot.material)
    
    
    x = 0
    ticketPool = 0
    
    for mat in materials:
        ticketPool += mat.fzRarity
    


    
    """pick a winner based on whether its random or no Dups"""
    
    """RANDOM / UNIQUE RAND SEL"""
    if ticketPool > 0:
        ticket = random.randint(0, ticketPool-1)
    else:
        ticket = 0
    print (ticket)
    
    
    """find the owner of that ticket"""
    ticketCounter = 0
    matNum = 0
    selMat = None
    for mat in materials:

        if ticket >= ticketCounter:
            if ticket < ticketCounter + mat.fzRarity:
                print ("Selected material is " + mat.name + " with " + str(mat.fzRarity) + " tickets.")
                selMat = matNum
                
    
        ticketCounter += mat.fzRarity
        matNum += 1
            



    return selMat


def readCode(gc, unique):
    
    code = ""
    
    for x in gc:
        code = code + str(x)    
    
    if unique == False:
        print(code)

def consolidateCode(gc):
    
    code = ""
    
    for x in gc:
        code = code + "-" + str(x)  
    
    code = code[1:]  

    return(code)



    


def buildChar (host, props, folder, genCodesList, proxyParametersList):     

    x = 0
    
    """Hide Viewport Check Box Thingy"""
    hvpr = bpy.context.scene.hide_layers_bool
    
    
    characterParams = []
    
    
    """PUT ALL THE OBJECTS AT ROOT LEVEL INTO THE CHARACTER PARAMETERS"""
    while x < len(host.objects):
        characterParams.append(host.objects[x])
        x += 1
    
    
    x = 0
    
    """randomize each character"""    
    charsMade = len(genCodesList) + 1
    progress = "Building Variant " + str(charsMade) + ": "
    print(progress)
    
    if bpy.context.scene.unique_variants == True:
        

        
        verifiedRules = False
        while verifiedRules == False:
            codeIsUnique = False
            while codeIsUnique == False:
                genCode = genRandomCode(props, True)
                
                #satisfy rules here
                
                codeIsUnique = isUnique(genCode, genCodesList)
                verifiedRules = codeVerification(genCode, progress)
        
    else:    
        
        """Make 1 genCode and it doesnt matter what it is"""
        
        freshConsole(12)
        verifiedRules = False
        while verifiedRules == False:
            genCode = genRandomCode(props, False)
            
            verifiedRules = codeVerification(genCode, progress)
    
        freshConsole(12)
    
    """FOUND RANDOM CANDIDATE VIA genCode - GenCandidate NOW"""
    genCodesList.append(genCode)
    

    
    x = 0
    
    """BLANK LIST FOR NAMES TO GO IN CSV LIST"""
    
    
    for prop in props:
        
                
        """set all objects in collection to off except winner"""
        
#        hideVPR()
        
        winner = prop.objects[genCode[x]]
        winner.hide_render = False
        winner.hide_viewport = False  
        

        characterParams.append(winner)
#        print (winner.name)
        
        x +=1
    
    
    """DO PROXY SWAP"""
    
    if bpy.context.scene.useProxySwap == False:
        """Reset our counter to 0. Use this to loop through all of the selecter Character Parameters"""    
        x = 0
        cpCount = len(characterParams)
        
        variant = bpy.context.blend_data.collections.new(name=folder)
        bpy.data.collections['Variants'].children.link(variant)
        
        varRecipe = []
        
        while x < cpCount:
            dupToNewColl (characterParams[x], variant.name, False)
            x += 1
        reTargArmature (variant.name)
        proxyParametersList.append(characterParams)
        #bpy.context.view_layer.layer_collection.children['Variants'].children[variant.name].exclude = True
    else:
        
        proxyParametersList.append(characterParams)
        


def codeVerification(genCode, progress):
    objs = returnObjFromCode(genCode)

    
    
    print (progress + 'Verifying Rules In Selection:        ')
#    for obj in objs:
#        print (obj.name)
        
        
    for obj in objs:
        for rule in obj.rules_list:
            
            
            #NEVER
            if rule.object_rule == 'Never':
                print (progress + 'Rule test: ' + rule.obj.name)
                if rule.obj in objs:
                    print (progress + 'Verification Failed')
                    return False
                    
                    
            if rule.object_rule == 'Always':
                if rule.obj not in objs:
                    print (progress + 'Verification Failed')
                    return False
    
    
    print (progress + 'Verification Passed')
    return True
            

def returnObjFromCode(genCode):

    objs = []
    host_name = bpy.context.scene.char_collection
    host = bpy.data.collections[host_name]
    
    subs = host.children
    
    
    
    codeCount = 0
    
    for code in genCode:
        subcollection = subs[codeCount]
        
        obj = subcollection.objects[code]
        
        objs.append(obj)
        codeCount += 1
    
    return objs
        

def isUnique(code, codes):
    """CHECKS IF CODE EXISTS IN CODES"""
    """IF IT DOES, RETURN FALSE. IF NOT, RETURN TRUE"""
    for c in codes:
        
        if consolidateCode(c) == consolidateCode(code):
            #HERES THE PROBLEM#######
            print ("code: " +consolidateCode(code) + " - previously generated.")
            return False
    #print ("code: " +consolidateCode(code))
    return True
    


    
def dupToNewColl (obj, collName, proxy):
    """Receive an object, make a LINKED duplicate, place that duplicate in a specific collection"""
    
    """What collection is main object in"""
    fromColl = whatCollection(obj)
    
    if bpy.context.scene.instBool == True:
        ob_dup = obj.copy()
        
        if proxy == True:
            ob_dup.name = obj.name + " Proxy"
        else:
            ob_dup.name = obj.name + " " + collName
        """SET CUSTOM PROPERTY FROM ITS BIRTH ORIGIN"""
        
        
        #print (obj.name + " spawned a new: " + ob_dup.name)
        bpy.data.collections[collName].objects.link(ob_dup)
        
        return ob_dup
        
    if bpy.context.scene.instBool == False:
        

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        
        bpy.context.view_layer.objects.active = obj
        
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        dupName = bpy.context.active_object.name
        ob_dup = bpy.data.objects[dupName]
        if proxy == True:
            ob_dup.name = obj.name + " Proxy"
        else:
            ob_dup.name = obj.name + " " + collName
        
        """SET CUSTOM PROPERTY FROM ITS BIRTH ORIGIN"""
        #setSubData(ob_dup)
        
#        print (obj.name + " spawned a new: " + ob_dup.name)
        bpy.data.collections[collName].objects.link(ob_dup)
        fromColl.objects.unlink(ob_dup)
        
        return ob_dup


def verifyRules(genCode):
    print("----------------DA RULES--------")
    hostname = bpy.context.scene.char_collection
    host = bpy.data.collections[hostname]
    
    subCount = 0
    for sub in host.children:
        selected = sub.objects[genCode[subCount]]

        
        #print (selected.name)
        
        
        #check the rules for the selected object
        for rule in selected.rules_list:
            #does rule obj exist?
            
            rule_obj = None
            
            
            try:
                rule_obj = bpy.data.objects[rule.object_name]
            except Exception:
                print("Sorry this object was not found.")
            else:
                print (selected.name + " is " + rule.object_rule + " with " + rule.object_name + ".")
            
            
            if rule_obj != None:
                if rule.object_rule == "Always":
                    
                    
                    rule_obj_sub = findMyColl(rule_obj)
                    
                    second_count = 0
                    for sub_count_two in host.children:
                        if rule_obj_sub == sub_count_two:
                            
                            genCode[second_count] = rule_obj['assignment'] 
                                                       
                        second_count += 1
                if rule.object_rule == "Never":
                    rule_obj_sub = findMyColl(rule_obj)
                    for sub_count_two in host.children:
                        if rule_obj_sub == sub_count_two:
                            
                            #do something with
                            if rule_obj['assignment'] == genCode[second_count]:
                                print("You gotta pick another one bruh")
                        
                    
                    

        
        
        
        
        
        
        subCount += 1

                
                
                
                
                
                
                

def whatCollection(obj):
    for coll in bpy.data.collections:
        for o in coll.objects:
            if o.name == obj.name:
                return coll
            
    return None
    
    
def instToNewColl (collName, location):
    """Receive a collection. Instance That Collection to specific location"""


 
def reTargArmature(collName):
    
    """---------------LEGACY--METHOD-----------------"""
    """----------------------------------------------"""
    """----------------------------------------------"""
    """----------------------------------------------"""
    """----------------------------------------------"""
    
    """CHECK IF HAS ARMATURE - ASSIGN PROPER ARMATURE"""
    charData = bpy.data.collections[collName].objects
    
    x = 0
    
    """Are you MESH, ARMATURE, or OTHER"""
    
    meshList = []
    armList = []
    otherList = []
    latList = []
    
    while x < len(charData):
        if charData[x].type == 'MESH':
            meshList.append(charData[x])
        elif charData[x].type == 'ARMATURE':
            armList.append(charData[x])
        elif charData[x].type == 'LATTICE':
            latList.append(charData[x])
        else:
            otherList.append(charData[x])
        x += 1
    
    """ASSIGN ALL VIABLE MESH TO COLL ARMATURE"""
    
    x = 0
    
    while x < len(meshList):
        name = meshList[x].name
        mods = bpy.data.objects[name].modifiers
          
        a = 0
        while a < len(mods):
            if mods[a].type == 'ARMATURE':
#                print ("Found The Armmy")
                if len(armList) > 0:
                    mods[a].object = armList[0]
            if mods[a].type == 'LATTICE':
                if len(latList) > 0:
                    mods[a].object = latList[0]
            else:
                """"""
            a += 1
        x += 1
        
def armatures_to_proxies():
    #HERE WE TAKE THE PROXY FOLDER AND
    #FIND THE ARMATURE / POSE LIBRARY
    
    #THEN WE ADD EACH ARMATURE MODIFIER
    #TO EACH PROXY
    
    proxy_folder = bpy.data.collections['Variants']
        
    meshList = []
    armList = []
    otherList = []
    latList = []
    
    for subcoll in proxy_folder.children:
        for obj in subcoll.objects:
            if obj.type == 'MESH':
                meshList.append(obj)
            elif obj.type == 'ARMATURE':
                armList.append(obj)
            elif obj.type == 'LATTICE':
                latList.append(obj)
            else:
                otherList.append(obj)
    
    #ASSIGN ARMATURES TO ALL MESHES
    
    #BYPASS INSTANCING BOOLEAN FOR ONE SECOND
    instance_setting = bpy.context.scene.instBool
    
    bpy.context.scene.instBool = False
    
    if len(armList) > 0:
        pose_selector = dupToNewColl(armList[0], "Variants", True)
        pose_selector.name = "Pose Selector"
        for p in reversed(pose_selector.animation_data.nla_tracks):
            pose_selector.animation_data.nla_tracks.remove(p)
    
    bpy.context.scene.instBool = instance_setting
    
    for obj in meshList:


        #list of old Armature Modifiers that were left on obj GET RID OF AFTER AUDIT
        oldArms = []
        
        #look through objects modifiers
        #remove all existing armatures
        for mod in reversed(obj.modifiers):
            
            #found a modifier!
            if mod.type == 'ARMATURE':
                obj.modifiers.remove(mod)
        
        
        pose_mod = obj.modifiers.new('Pose Selector', 'ARMATURE')
        pose_mod.object = pose_selector
    
    for arm in armList:
        #find the action of the subcollection armature
        armAction = arm.animation_data.nla_tracks[0].strips[0].action
        track = pose_selector.animation_data.nla_tracks.new()
        track.strips.new("pose 1", 1, armAction)
    

    
def setAllSubOrigins(host):
    """RECEIVE A HOST COLLECTION - MAKE ALL OBJECTS INSIDE TO THEIR RESPECTIVE SUB DATA PROPERTIES"""
    for obj in host.all_objects:
        setSubData(obj)
    
def collCleaner(delCol):
    
    allColls = bpy.data.collections
    vFolderExists = False
    x = 0
    
    
    
    win = bpy.context.window_manager
    win.progress_begin(0, 100)
    
    while x < len(allColls):
        if allColls[x].name == delCol:
            vFolderExists = True
        else:
            """DO NOTHING"""
        x += 1
        
        
    win.progress_update(25)
    
    if vFolderExists:
        collection = bpy.data.collections.get(delCol)    
        collections = collection.children
        x = 0
        
        
        delContFolder = bpy.context.view_layer.layer_collection.children[delCol]
        delContFolder.exclude = False
        
        while x < len(collections):
            delContFolder.children[x].exclude = False
#            print (collections[x])
            x += 1
        objs = collection.all_objects
        
        win.progress_update(50)
        
        
        while len(objs) > 0:
            bpy.ops.object.select_all(action='DESELECT')
            objs[0].select_set(True)

#            print ('Removing ' + objs[0].name)
            bpy.data.objects.remove(objs[0])

    
        win.progress_update(75)  
            
#        print ('len(collections) = ' + str(len(collections)))
        
        x = 0
        while len(collections) > 0:
#            print(collections[0])
            bpy.data.collections.remove(collections[0])
            x+= 1
        bpy.data.collections.remove(collection) 
    else:
        """DO NOTHING"""

    win.progress_end()


def spawnVars():
    
    freshConsole(2)
    print("-----------SPAWN VARIANT INSTANCES------------")
    freshConsole(1)
    
    distConst = 0.2
    
    placeVector = [bpy.context.scene.spawnfloat_x, bpy.context.scene.spawnfloat_y, bpy.context.scene.spawnfloat_z]
    
    x = 0
    
    """CHECK AND SEE IF VARIANTS HAVE BEEN GENERATED YET"""
    varCollExists = collExists('Variants')
    
    
    if varCollExists == True:
        vars = len(bpy.data.collections['Variants'].children)
        varColl = bpy.data.collections['Variants'].children
        """THE NAME OF SPAWNS FOLDER - SPAWNS"""
        sName = 'SPAWNS'
        
        """EMPTY ANY OLD VERSIONS OF SPAWNS"""
        collCleaner(sName)
        
        """NEW COLLECTION FOR SPAWNS"""
        spawnsColl = bpy.context.blend_data.collections.new(name=sName)
        bpy.context.scene.collection.children.link(spawnsColl)
        
        
        """INSTANCE COLLECTION HERE"""
        
        setRootCollActive()
        
        while x < vars:
            bpy.ops.object.collection_instance_add(collection=varColl[x].name, align='WORLD', location=(placeVector[0] * (x+1), placeVector[1] * (x+1), placeVector[2] * (x+1)), scale=(1, 1, 1))
            x += 1
            inst = bpy.context.active_object
            inst.name = "Spawn " + str(x)
            bpy.context.scene.collection.objects.unlink(inst)
            bpy.data.collections[sName].objects.link(inst)
            print (inst.name)
        
        varFolder = bpy.context.view_layer.layer_collection.children['Variants']
        varFolder.exclude = True
    
    else:
        """NO VARS TO SPAWN - SORRY BUD"""

def vScrambler():
    """currently on or off"""
    if collExists('Variants'):
        state = bpy.context.view_layer.layer_collection.children['Variants'].exclude
        
        varFolder = bpy.context.view_layer.layer_collection.children['Variants']
        varFolder.exclude = False
        
        for coll in varFolder.children:
            coll.exclude = False
            
        objs = bpy.data.collections['Variants'].all_objects
        
        """send objs to the scrambler"""
        for obj in objs:
            randShapeKey(obj)
        
        varFolder.exclude = state

def queueProxy(proxyList):
    """Queue Proxy Dude"""
    
    """GET GEN CODES LIST IF PROXY HAS BEEN GENERATED"""
    
    variant_names = [variant.name for variant in bpy.data.collections["Variants"].all_objects]
    
    
    for variant_name in variant_names:
        obj = bpy.data.objects[variant_name]
        obj.hide_render = True
        obj.hide_viewport = True
        obj.keyframe_insert('hide_render', frame=0)
        obj.keyframe_insert('hide_viewport', frame=0)
    
    
    x = 0
    
    
    for proxy in proxyList:
        """MAKE THAT PROXY ON THE Nth KEYFRAME"""
        
        
        bpy.context.scene.frame_end = bpy.context.scene.var_gen
        
        for original_obj in proxy:
            print ("IM PRINTING PROXY:   " + original_obj.name)
            objName = original_obj.name + " Proxy"
            obj = bpy.data.objects[objName]
            
            frm = x
                
            obj.hide_render = False
            obj.hide_viewport = False
            obj.keyframe_insert('hide_render', frame=frm+1)
            obj.keyframe_insert('hide_viewport', frame=frm+1)
            
            obj.hide_render = True
            obj.hide_viewport = True
            obj.keyframe_insert('hide_render', frame=frm+2)
            obj.keyframe_insert('hide_viewport', frame=frm+2)
            
        x += 1
    
    
def queueBatch():
    print("I WILL QUEUE BATCH NOW")
    
    collName = 'SPAWNS'     
   
    
    
    
    if collExists(collName):
        scn = bpy.context.scene
    
        coll = bpy.data.collections[collName]
   
        queueLen = len(coll.objects)
   
        bpy.context.scene.frame_end = queueLen
        
        x = 0
        #ONLY USE FOR SPAWN COLLECTION
        while x < len(coll.objects):
           
            obj = coll.objects[x]
           
            frm = x
           
            obj.hide_render = True
            obj.hide_viewport = True
            obj.keyframe_insert('hide_render', frame=frm)
            obj.keyframe_insert('hide_viewport', frame=frm)

            obj.hide_render = False
            obj.hide_viewport = False
            obj.keyframe_insert('hide_render', frame=frm+1)
            obj.keyframe_insert('hide_viewport', frame=frm+1)

            obj.hide_render = True
            obj.hide_viewport = True
            obj.keyframe_insert('hide_render', frame=frm+2)
            obj.keyframe_insert('hide_viewport', frame=frm+2)
           
            x += 1    
            
def remSpawns():
    """REMOVES SPAWNS"""
    freshConsole(2)
    print("-----------REMOVED VARIANT INSTANCES------------")
    freshConsole(1)
    
    collCleaner('SPAWNS')
            

def setLMs(context, state):
    """DO STUFF HERE"""
    objs = context.selected_objects
    slot = bpy.context.scene.matgroup
    for obj in objs:
        setLMName(obj, slot, state)        

"""-----------------------CLASSES-------------------------------------"""

class FZR_Operator(bpy.types.Operator):
    """Randomize Shape Keys"""
    bl_idname = "object.fzr_operator"
    bl_label = "Shape Key Scrambler"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context, "rand")
        return {'FINISHED'}
    
class FZR_multiOBJ(bpy.types.Operator):
    """Randomize Shape Keys"""
    bl_idname = "object.fzr_multiobj_operator"
    bl_label = "GENERATE"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        multiOBJ(context)
        return {'FINISHED'}


"""-----------------------------METADATA SLOTS----------------------------------"""
class addMetadataSlot(bpy.types.Operator):
    bl_idname = "object.add_md_operator"
    bl_label = "+"
    
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        meta = bpy.context.scene.metadata_name
        if meta != "":
            addMDSlot(meta, "")
        return {'FINISHED'}
    
    
def addMDSlot(name, value):
    meta = bpy.context.scene.md_list
    
    currentMdSlots = len(meta)
    
    meta.add()
    
    newMeta = meta[currentMdSlots]
    
    newMeta.mdName = name
    newMeta.mdValue = value       

class remMetadataSlot(bpy.types.Operator):
    bl_idname = "object.remove_md_operator"
    bl_label = "-"
    
    slot : bpy.props.IntProperty(name="Metadata Slot", default = 0)
    
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        
        meta = bpy.context.scene.md_list
        meta.remove(self.slot)
        
        return {'FINISHED'}
    
    


            
"""---------------------------------------------------------------"""

"""-----------------------------RULES----------------------------------"""
class addObjectRule(bpy.types.Operator):
    bl_idname = "object.add_rule_operator"
    bl_label = "+"
    
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        
        rules = bpy.context.object.rules_list
        
        rules.add()
        
        return {'FINISHED'}
    
    
def addObjRule(name, rule):
    rules = bpy.context.object.rules_list
    
    currentRules = len(rules)
    
    rules.add()
    
    newRule = rules[currentRules]
    
    newRule.object_name = name
    newRule.object_rule = rule       

class remObjectRule(bpy.types.Operator):
    bl_idname = "object.remove_rule_operator"
    bl_label = "-"
    
    selection : bpy.props.IntProperty(name="Selection", default = 0)
    
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        rules = bpy.context.object.rules_list
        
        rules.remove(self.selection)
        return {'FINISHED'}
    
    

    
    
def remObjRule(name):
    rules = bpy.context.object.rules_list  
    rulesLen = len(rules)
    
    removedOne = False
    
    rule_back_count = rulesLen - 1
    
    for rule in reversed(rules):
        if rule.object_name == name:
            rules.remove(rule_back_count)
            removedOne = True
        rule_back_count -= 1

    
    if (removedOne):
        return
    
    if  name == "":
        rules.remove(rulesLen-1)
            
            
def resetRules():
    hst = host()
    
    if hst == None:
        print('Host does not exist.')
        return
    
    
    for child in hst.children:
        for obj in child.objects:
            
            #set object rules to none
            obj.rules_list.clear()

def resetRarity():
    hst = host()
    
    if hst == None:
        print('Host does not exist')
        return
    
    for child in hst.children:
        for obj in child.objects:
            
            #set object tickets back to 1
            obj.fzRarity = 1



"""---------------------------------------------------------------"""

class resetRarityOperator(bpy.types.Operator):
    "Reset's all object tickets to 1 in the host collection"
    bl_idname = "scene.fz_reset_rarity"
    bl_label = "Reset All Rarity"
    
    def execute(self, context):
        
        resetRarity()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        return context.window_manager.invoke_confirm(self, event)
        
class resetRulesOperator(bpy.types.Operator):
    "Remove all rules for all objects in the host collection"
    bl_idname = "scene.fz_reset_rules"
    bl_label = "Reset All Rules"
    
    level = bpy.props.EnumProperty(name = "Remove Rules For", items =[
        ("This Object","This Object",""),
        ("This Subcollection","This Subcollection",""),
        ("Host Collection","Host Collection","")])
        
    text = bpy.props.StringProperty(name = "Enter Text", default = "")
    
    def execute(self, context):
        
        l = self.text
        
        resetRules()
        print('reset')
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        return context.window_manager.invoke_confirm(self, event)

class renderVariants(bpy.types.Operator):
    """RENDER STILLS"""
    bl_idname = "scene.fz_rend_variants"
    bl_label = "Render Variants"
    bl_icon = 'RESTRICT_RENDER_OFF'
    
    def execute(self, context):
        
        fzConfig = bpy.context.scene.fz_output_config
        
        
        
        
        if fzConfig == 'Still Images':
            """RENDER STILLS"""
            
            scn = bpy.context.scene
            
            originalPath = scn.render.filepath
            originalStart = scn.frame_start
            originalStep = scn.frame_step
            originalEnd = scn.frame_end
            
            scn.frame_start = scn.fz_render_start
            scn.frame_end= scn.var_gen
            scn.frame_step = scn.fz_render_step
            
            bpy.context.scene.render.filepath = originalPath + '#.png'
            
            
            
            
            
            bpy.ops.render.render(animation=True, use_viewport=False)
            
            
            scn.render.filepath = originalPath
            scn.frame_start = originalStart
            scn.frame_end= originalEnd
            scn.frame_step = originalStep
            
        
        
        
        
        
        
        elif fzConfig == 'Animations':
            """RENDER ANIMATIONS"""
            
            proxy = bpy.context.scene.proxy_obj
            
            variants = bpy.context.scene.var_gen
            
            originalPath = bpy.context.scene.render.filepath
            
            v = bpy.data.scenes["Scene"].fz_render_start
            while v < variants:
                bpy.context.scene.render.filepath = originalPath + str(v) + '.mp4'
                
                proxy.modifiers["FZRandomizer"]["Input_4"] = v
                
                proxy.location = proxy.location
                
                bpy.ops.render.render(animation=True, use_viewport=False)
                
                v += bpy.data.scenes["Scene"].fz_render_step
                
            bpy.context.scene.render.filepath = originalPath
            
        
        else:
            self.bl_label = "Output Not Configured!"
        
        return{'FINISHED'}
    
    
class renderStills(bpy.types.Operator):
    """RENDER STILLS"""
    bl_idname = "scene.fz_rend_stills"
    bl_label = "Render Stills"
    
    def execute(self, context):
        proxy = bpy.context.scene.proxy_obj
        
        proxy.modifiers["FZRandomizer"]["Input_3"] = 0
        proxy.location = proxy.location
        
        bpy.context.scene.render.use_file_extension = True
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        bpy.context.scene.render.image_settings.color_depth = '16'
        
        bpy.context.scene.fz_output_config = "Still Images"

        return{'FINISHED'}
    
class renderAnimated(bpy.types.Operator):
    """RENDER STILLS"""
    bl_idname = "scene.fz_rend_anim"
    bl_label = "Render Animated"
    
    def execute(self, context):
        proxy = bpy.context.scene.proxy_obj
        
        proxy.modifiers["FZRandomizer"]["Input_3"] = 1
        proxy.location = proxy.location
        
        bpy.context.scene.render.use_file_extension = False
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        bpy.context.scene.render.ffmpeg.audio_codec = 'AAC' 
        
        
        bpy.context.scene.fz_output_config = "Animations"
               
        return{'FINISHED'}
    
class auto_anim_settings(bpy.types.Operator):
    """SET AUTO SETTINGS"""
    bl_idname = "scene.fz_auto_anim_settings"
    bl_label = "Automatic Animation Output Configuration"
        
    def execute(self, context):
        
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        bpy.context.scene.render.ffmpeg.audio_codec = 'AAC'        
        
        return{'FINISHED'}


class queueForBatchRender(bpy.types.Operator):
    """Queue Spawns For A Batch Render"""
    bl_idname = "object.queue_batch_operator"
    bl_label = "Queue For Batch Render"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        queueBatch()
        return {'FINISHED'}
    
class queueProxyForBatchRender(bpy.types.Operator):
    """Queue Proxy For A Batch Render"""
    bl_idname = "object.queue_proxy_batch_operator"
    bl_label = "Queue Proxy For Batch Render"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        queueProxy()
        return {'FINISHED'}


def collDims(col):
    objs = col.all_objects
    for obj in objs:
        print (obj.name)

class resetShapeKeys(bpy.types.Operator):
    """Set All Shape Keys To Zero"""
    bl_idname = "object.reset_shape_key_rand_operator"
    bl_label = "Reset Shape Keys"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        main(context, "reset")
        return {'FINISHED'}
    

class setLinkMatName(bpy.types.Operator):
    """Set Object Name To Reflect LinkMats"""
    bl_idname = "object.obj_lm_name_operator"
    bl_label = "Set LinkMat"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        setLMs(context, True)
        return {'FINISHED'}
    
class remLinkMatName(bpy.types.Operator):
    """Set Object Name To Reflect LinkMats"""
    bl_idname = "object.rem_obj_lm_name_operator"
    bl_label = "Rem LinkMat"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        setLMs(context, False)
        return {'FINISHED'}

class calcPoss(bpy.types.Operator):
    """Calculate All Possibilities"""
    bl_idname = "object.calc_poss_operator"
    bl_label = "Calculate Possibilities"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        bpy.context.scene.possibleGen = possibilities()
        return {'FINISHED'}
 

class selParam(bpy.types.Operator):
    """Set All Shape Keys To Zero"""
    bl_idname = "object.rand_sel_param_operator"
    bl_label = "Randomize Parameter"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        main(context, "selParam")
        return {'FINISHED'}

class spawnVariants(bpy.types.Operator):
    """Spawn Variants"""
    bl_idname = "object.spawn_var_operator"
    bl_label = "Spawn Variants"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        print ('SPAWNED ' + str(bpy.context.scene.var_gen) + ' VARIANTS...')
        spawnVars()
        return {'FINISHED'}

class removeSpawns(bpy.types.Operator):
    """Remove Spawns"""
    bl_idname = "object.rem_spawn_operator"
    bl_label = "Remove Spawns"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        print ('SPAWNED ' + str(bpy.context.scene.var_gen) + ' VARIANTS...')
        remSpawns()
        return {'FINISHED'}

class delVariants(bpy.types.Operator):
    """Delete Variants"""
    bl_idname = "object.del_var_operator"
    bl_label = "DELETE VARIANTS"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        print ('DELETED ' + str(bpy.context.scene.var_gen) + ' VARIANTS...')
        
        collCleaner('Variants')
        collCleaner('Geometry Nodes Proxy')
        
        openHost()
        
        return {'FINISHED'}

class variantScrambler(bpy.types.Operator):
    """Variants Scrambler"""
    bl_idname = "object.var_scrambler_operator"
    bl_label = "Variant Scrambler"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        vScrambler()
        return {'FINISHED'}

class genCodesList (bpy.types.PropertyGroup):
    
    genCode : bpy.props.StringProperty(name = "Code", default="")
    

class metadataList (bpy.types.PropertyGroup):
    mdName : bpy.props.StringProperty(name = "Name", default="metadata")
    mdValue : bpy.props.StringProperty(name = "Value", default="value")
    mdCustomDisplay : bpy.props.StringProperty(name = "Custom Display", default="")
    mdDisplay : bpy.props.EnumProperty(name = "Display Type", items=[
        ("string","string",""),
        ("number", "number", ""),
        ("date", "date", ""),
        ("boost_percentage","boost percentage",""),
        ("boost_number","boost number",""),
        ("custom", "custom", "")])
    
    mdUseCustom : bpy.props.BoolProperty(name = "Use Custom Attribute", default= False, description = "Record a custom value for this attribute.\nOtherwise object name is recorded as attribute value")
    
class rulesList (bpy.types.PropertyGroup):
    object_name : bpy.props.StringProperty(name = "Object Name", default="")
    obj : bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    
    object_rule : bpy.props.EnumProperty(name = "Object Rule",
    description = 'Rule for relation to other object',
    items = [("Never", "Never", "Never pair with active object"),
    ("Always", "Always", "Always pair with active object.\n\nCaution! - Always selection can result in longer solve times & can alter natural rarity")]
    )





class HB_collections (bpy.types.PropertyGroup):
    collection_name : bpy.props.StringProperty(name = "Collection Name", default="")

    
class HostBuilder_Panel(bpy.types.Panel):
    bl_label = "Host Builder"
    bl_idname = "OBJECT_PT_hostbuilder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FZRandomizer'
    
    def draw(self, context):
        layout = self.layout
        
#        obj = bpy.context.object
#        if len(obj.material_slots) > 0:
#            mat = bpy.context.object.active_material
#        objs = bpy.context.selected_objects
        scn = bpy.context.scene
        
        stage = scn.host_builder_stage
        
        if stage == 'Start':
            row = layout.row()
            row.operator("scene.build_host")
            
        elif stage == 'Host':
            row = layout.row()
            
            row.label(text=scn.hb_host_warning)
            
            row = layout.row()
            row.prop(scn, "host_builder_name", text = "")
            
            row = layout.row()
            
            row = layout.row()
            row.operator("scene.hb_next")
            row = layout.row()
            row.operator("scene.cancel_build_host")
            
        elif stage == 'Subcolls':
            
            subs = bpy.context.scene.host_builder_collections
            
            row = layout.row()
            row.label(text=bpy.context.scene.host_builder_name + " Subcollections: " + str(len(subs)))
            

            
            subCount = 0
            for sub in subs:
                row = layout.row(align = True)
                row.prop(sub, "collection_name", text = "")
                
                row.scale_x = .2
                row.operator("scene.rem_hb_collection", text = "x").rem_spot = subCount
                subCount += 1


            row = layout.row()
            row.operator("scene.add_hb_collection")
            

#            row = layout.row()
#            row.prop(scn, "hb_gen_assets")
            
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row.operator("scene.hb_finish")
            row = layout.row()
            row.operator("scene.cancel_build_host")
            
        
class hb_collection_add(bpy.types.Operator):
    bl_idname = "scene.add_hb_collection"
    bl_label = "Add Subcollection"
    
    def execute(self, context):
        bpy.context.scene.host_builder_collections.add()
        return{'FINISHED'}
    
class hb_collection_rem(bpy.types.Operator):
    bl_idname = "scene.rem_hb_collection"
    bl_label = "Remove Subcollection"
    
    rem_spot : bpy.props.IntProperty(name="remove", default = 0)
    
    def execute(self, context):
        bpy.context.scene.host_builder_collections.remove(self.rem_spot)
        return{'FINISHED'}

class hb_builder_start(bpy.types.Operator):
    bl_idname = "scene.build_host"
    bl_label = "Build A Host Collection"
    
    def execute(self, context):
        bpy.context.scene.host_builder_stage = 'Host'
        return {'FINISHED'}
    
class hb_builder_next(bpy.types.Operator):
    bl_idname = "scene.hb_next"
    bl_label = "Next"
    
    def execute(self, context):
        
        """DID THEY LEAVE THE HOST NAME FIELD EMPTY?"""
        nameField = bpy.context.scene.host_builder_name
        if nameField == "":
            bpy.context.scene.hb_host_warning = "Host name must be defined."
        
        else:
            bpy.context.scene.host_builder_stage = "Subcolls"
        
        return {'FINISHED'}
    
class hb_finish(bpy.types.Operator):
    bl_idname = "scene.hb_finish"
    bl_label = "Build"
    
    def execute(self, context):
        
        subs = bpy.context.scene.host_builder_collections
        
        warning = None
        
        for sub in subs:
            if sub.collection_name == bpy.context.scene.host_builder_name:
                warning = "Subcollections cannot share the host name!"
                
        if warning == None:
            make_host_structure()
        
        
        return{'FINISHED'}


class hb_cancel(bpy.types.Operator):
    bl_idname = "scene.cancel_build_host"
    bl_label = "Cancel"
    
    def execute(self, context):
        bpy.context.scene.host_builder_stage = 'Start'
        bpy.context.scene.host_builder_collections.clear()
        bpy.context.scene.hb_host_warning = "Host Name?"
        bpy.context.scene.host_builder_name = ""
        
        return {'FINISHED'}


def make_host_structure():
    
    hostName = bpy.context.scene.host_builder_name
    hostSubs = bpy.context.scene.host_builder_collections
    
    hostColl = bpy.context.blend_data.collections.new(name=hostName)
    bpy.context.scene.collection.children.link(hostColl)
    
    for sub in hostSubs:
        subColl = bpy.context.blend_data.collections.new(name=sub.collection_name)
        hostColl.children.link(subColl)
        
    
    """RESET DATA"""
    bpy.context.scene.char_collection = bpy.context.scene.host_builder_name    
    bpy.ops.scene.cancel_build_host()
 
    pass





class FZR_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "FZRandomizer 3.0"
    bl_idname = "OBJECT_PT_fzrandomizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FZRandomizer"


    
    def draw(self, context):
        
        
        layout = self.layout

        obj = bpy.context.object
        mat = bpy.context.object.active_material
        objs = bpy.context.selected_objects
        scn = bpy.context.scene
        
        if bpy.context.active_object != None:
            coll = whatCollection(bpy.context.active_object)
        
            
            
        
    



        row = layout.row()
        
        row.prop (scn, "char_collection")
        
        row = layout.row()
        


        
        row.scale_x = 1
        
        #row.prop (scn, "useProxySwap")
        
        
        row = layout.row()
            

        
        row = layout.row()
        if scn.useProxySwap:
            row.label(text="Engine: Proxy Swap")
        else:
            row.label(text="Engine: Legacy")
        row.scale_x = 0.5
        row.prop (scn, "unique_variants")
        
        row = layout.row()
        row.prop (scn, "var_gen")
        row = layout.row()
        
        row.operator("object.fzr_multiobj_operator")
        
        row = layout.row()
        
        row.operator("object.calc_poss_operator")
        row.label(text=str(round(bpy.context.scene.possibleGen)))

        

        
        
        row = layout.row()      
        row.operator("object.del_var_operator")
        row = layout.row()
        row.label(text=bpy.context.scene.host_name_warning)
        
        
        row = layout.row()
        row.label(text="")
        
        row = layout.row()
        row.label(text="Active Object: " + obj.name)
        
        row = layout.row()
        row.label(text="Selected Objects: " + str(len(objs)))
        

        row = layout.row()
        row.prop(scn, "useRarity",
            icon="TRIA_DOWN" if scn.useRarity else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )        
        row.label(text = "Rarity")
        
        
        
        objColl = whatCollection(obj)
        if scn.useRarity:
            if objColl != None:
                
                row = layout.row()
                row.label(text="Sub Collection: " + objColl.name)
                
                row = layout.row()
                row = layout.row()
                row.label(text="Active Object: " + obj.name)
                
            
                row.prop (obj, "fzRarity", text="Object Tickets")
                
                row = layout.row()
#                if len(obj.material_slots) > 0:
#                    row.label(text="Active Material: " + mat.name)
#                    row.prop (mat, "fzRarity", text="Material Tickets")
                
                ticketPool = 0
                for x in objColl.objects:
                    ticketPool += x.fzRarity
                

                
                row = layout.row()
                row.label(text="Object Rarity: " + str(obj.fzRarity) + "/" + str(ticketPool))
                row.label(text=str(round(obj.fzRarity/ticketPool*100)) + "% chance")
                
                row = layout.row()
                row.operator("scene.fz_reset_rarity")

#                if len(obj.material_slots) > 0:
#                    ticketPool = 0
#                    x = 0
#                    for slot in obj.material_slots:
#                        ticketPool += obj.material_slots[x].material.fzRarity
#                        x += 1
#                    
#                    row = layout.row()
#                    
#                    row.label(text="Material Rarity: " + str(mat.fzRarity) + "/" + str(ticketPool))
#                    row.label(text=str(round(mat.fzRarity/ticketPool*100)) + "% chance")                
#                    
#                    row = layout.row()
#                    row.label(text="")
        

        
        """RULES COLLAPSE"""
        row = layout.row()
        row.prop(scn, "expandRules",
            icon="TRIA_DOWN" if scn.expandRules else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label (text="Rules")
        if scn.expandRules:
            row = layout.row()
            rules = obj.rules_list
            
            ruleCount = 0
            for rule in rules:
                row = layout.row(align=True)
                row.prop (obj.rules_list[ruleCount], "obj", text="")
                if obj.rules_list[ruleCount].object_rule == "Always":
                    row.prop (obj.rules_list[ruleCount], "object_rule", text="", icon='ERROR')
                else:
                    row.prop (obj.rules_list[ruleCount], "object_rule", text="")
                row.scale_x = .2
                row.operator("object.remove_rule_operator",text="x").selection = ruleCount
                ruleCount += 1

            
            
            row = layout.row(align=True)
            row.scale_x = 5.0
            #row.prop (scn, "rule_text")
            
            row.scale_x = 1.0
            row.operator("object.add_rule_operator", text="+ New Rule")
            #row.operator("object.remove_rule_operator")
            
            row = layout.row()
            row.operator("scene.fz_reset_rules")
        
        """METADATA COLLAPSE"""
        row = layout.row()
        row.prop(scn, "useMetadata",
            icon="TRIA_DOWN" if scn.useMetadata else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text = "Metadata")
        

        
        if scn.useMetadata:
            row = layout.row()
            
            row = layout.row()
            row.prop(scn, "gen_csv")
            
            if scn.gen_csv:
                row = layout.row()
                row.scale_x = 2.0
                row.prop(scn, "csv_doc_name")
                row.scale_x = 1.0
                row.prop(scn, "overwrite_csv")
            
            row = layout.row()
            
            row.prop(scn, "gen_json")
            
            if scn.gen_json:
                row = layout.row()
                mdListLen = len(scn.md_list) 
                
                row.label(text = "JSON Fields: " + str(mdListLen))
                row = layout.row()
                
                mdCount = 0
                for md in scn.md_list:
                    row = layout.row(align = True)
                    row.label(text = scn.md_list[mdCount].mdName)
                    row.scale_x = 2.0
                    
                    if scn.md_list[mdCount].mdName == scn.metadataAttributeName:
                        row.label(text="[" + scn.metadataAttributeName + "]")
                    else:
                        row.prop (scn.md_list[mdCount], "mdValue", text = "")
                    
                    row.scale_x = .4
                    row.operator("object.remove_md_operator", text="x").slot = mdCount
                    
                    
                    mdCount += 1
                
                row = layout.row(align=True)
                row.scale_x = 5.0
                row.prop (scn, "metadata_name", text = "Field Name")
                
                row.scale_x = 1.0
                row.operator("object.add_md_operator")

                row = layout.row()
                row = layout.row()
                row = layout.row()
            row = layout.row()
            
            row.label(text=scn.metadataAttributeName + ":")
            
            if objColl != None:
                row = layout.row()
                row.label(text = objColl.name + ": " + obj.name)

                row = layout.row()
                row.prop (obj.attribute_md, "mdUseCustom")
                
                if obj.attribute_md.mdUseCustom == True:
                    row = layout.row()
                    row.prop (obj, "fzAttribute", text = "Value")
                    row = layout.row()
                    
                    if obj.attribute_md.mdDisplay == "custom":
                        row.prop (obj.attribute_md, "mdDisplay")
                        row = layout.row()
                        row.prop (obj.attribute_md, "mdCustomDisplay", text="Display Type")
                    else:
                        row.prop (obj.attribute_md, "mdDisplay")            
        
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()

            row.prop(scn, "expandSettings",
                icon="TRIA_DOWN" if scn.expandSettings else "TRIA_RIGHT",
                icon_only=True, emboss=False
            )
            row.label(text = "Settings")
            

            
            if scn.expandSettings:
                row = layout.row()
                row.prop (context.scene, "metadataVariantVar")
                row = layout.row()
                row.prop (context.scene, "metadataAttributeName")
                row = layout.row()
                row.prop (context.scene, "metadataTraitTypeName")
                row = layout.row()
                row.prop (context.scene, "metadataValueName")
                
                row = layout.row()
                row.prop (context.scene, "metadataFolderName")

        """OUTPUT COLLAPSE"""
        row = layout.row()
        row.prop(scn, "output_settings",
            icon="TRIA_DOWN" if scn.output_settings else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text="Output")        
        if bpy.context.scene.output_settings:

            row = layout.row()
            
            row.prop(context.scene.render, "filepath")
            
            layout.use_property_split = True
            
            col = layout.column(align=True)
            
            col.prop(context.scene, "fz_render_start", text = 'Start Variant')
            col.prop(context.scene, "fz_render_step", text = 'Variant Step')
            
            row = layout.row()
            row.label(text="Output Configuration: " + bpy.context.scene.fz_output_config)

            row = layout.row(align=True)
            row.operator("scene.fz_rend_stills", text="Still Images")
            row.operator("scene.fz_rend_anim", text="Animations")
            
            row = layout.row()
            
            row.operator("scene.fz_rend_variants", icon = 'RESTRICT_RENDER_OFF')
            
        
        
            
        



class PT_LEGACY_TOOLKIT(bpy.types.Panel):
    bl_label = "Legacy Tools"
    bl_idname = "OBJECT_PT_legacy_fzr"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FZRandomizer"
    
    bl_options = {'DEFAULT_CLOSED'}


    
    def draw(self, context):
        
        
        layout = self.layout

        obj = bpy.context.object
        mat = bpy.context.object.active_material
        objs = bpy.context.selected_objects
        scn = bpy.context.scene
        
        row = layout.row()
        row.label(text="Generation Method: ")
        row.prop(scn, "useProxySwap")
        
        row = layout.row()
        if scn.useProxySwap:
            row.label(text="Proxy Swap")
        else:
            row.label(text="Legacy")
        
        
        """SHAPEKEYS COLLAPSE"""
        row = layout.row()
        row.prop(scn, "skexpanded",
            icon="TRIA_DOWN" if scn.skexpanded else "TRIA_RIGHT",
            icon_only=True, emboss=False
            
        )
        row.label(text = "Shape Key Tools")

        if scn.skexpanded:
            
            row = layout.row()
            row.prop (context.scene, "sk_prefix")
            
            sub = row.row(align = True)
            sub.scale_x = 1.5
            sub.operator("object.rand_sel_param_operator")

            row = layout.row()
            row.label(text="")

            row = layout.row()
            row.operator("object.var_scrambler_operator")
                            
            row = layout.row()
            row.operator("object.fzr_operator")

            
            row = layout.row()
            row.operator("object.reset_shape_key_rand_operator")
        
        
        
        """SPAWN TOOLS COLLAPSE"""
        
        row = layout.row()
        row.prop(scn, "spawnexpanded",
            icon="TRIA_DOWN" if scn.spawnexpanded else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text="Spawn Tools")
        
        if scn.spawnexpanded:
        
            row = layout.row(align = True) 
            row.prop (scn, "spawnfloat_x")
            row.prop (scn, "spawnfloat_y")
            row.prop (scn, "spawnfloat_z")
            
            
            
            row = layout.row()
            row.operator("object.spawn_var_operator") 
            row.operator("object.rem_spawn_operator")      
        
            row = layout.row()
            row.prop (scn, "autoSpawn")
            row.scale_x = .8
            row.prop (scn, "instBool")
            
            row = layout.row()
            row.operator("object.queue_batch_operator")  
#            row = layout.row()
#            row.operator("object.queue_proxy_batch_operator")            
            row = layout.row()
            row.label (text="")
        
        
        """LINKMAT COLLAPSE"""
        row = layout.row()

        row.prop(scn, "expanded",
            icon="TRIA_DOWN" if scn.expanded else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text = "Advanced Material Options")
        
        if scn.expanded:
            
            row = layout.row()
            row.prop (context.scene, "matgroup")       
            row = layout.row()
            row.operator("object.obj_lm_name_operator")
            row = layout.row()
            row.operator("object.rem_obj_lm_name_operator")
            
            row = layout.row()
            
            row.label(text = "")
        
        
        

hb_classes = {

hb_builder_start,
hb_collection_add,
hb_collection_rem,
hb_cancel,
hb_builder_next,
hb_finish,
genCodesList

}
            

legacy_classes = {

    PT_LEGACY_TOOLKIT,
    spawnVariants,
    removeSpawns,
    setLinkMatName,
    remLinkMatName,
    variantScrambler,
    delVariants,
    resetShapeKeys,
    selParam
    

}

reset_classes = {
    resetRulesOperator,
    resetRarityOperator

}
output_classes = {

    renderStills,
    renderAnimated,
    auto_anim_settings,
    renderVariants,



}

def register():
    bpy.utils.register_class(FZR_Operator)
    bpy.utils.register_class(queueProxyForBatchRender)
    bpy.utils.register_class(FZR_multiOBJ)    
    bpy.utils.register_class(queueForBatchRender)
    bpy.utils.register_class(calcPoss)
    bpy.utils.register_class(FZR_Panel)
    bpy.utils.register_class(HostBuilder_Panel)
    bpy.utils.register_class(metadataList)
    bpy.utils.register_class(rulesList)
    bpy.utils.register_class(HB_collections)
    bpy.utils.register_class(remMetadataSlot)
    bpy.utils.register_class(addMetadataSlot)
    bpy.utils.register_class(remObjectRule)
    bpy.utils.register_class(addObjectRule)
    
    
    for cls in hb_classes:
        bpy.utils.register_class(cls)
        
    for cls in legacy_classes:
        bpy.utils.register_class(cls)
        
    for cls in output_classes:
        bpy.utils.register_class(cls)
    
    for cls in reset_classes:
        bpy.utils.register_class(cls)

    
    bpy.types.Object.fzRarity = bpy.props.IntProperty(name = "Tickets", default=1, min=1)
    bpy.types.Object.fzAttribute = bpy.props.StringProperty(name = "Attribute", default = "", description = "Attribute name for the active object")
    bpy.types.Object.fzDisplayType = bpy.props.StringProperty(name = "Display Type", default = "string", description = "Attribute display type.")
    
    
    
    bpy.types.Material.fzRarity = bpy.props.IntProperty(name = "Tickets", default=1, min=1)
    
    bpy.types.Scene.expanded = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.autoSpawn = bpy.props.BoolProperty(name = "Auto Spawn", default=False)
    bpy.types.Scene.skexpanded = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.spawnexpanded = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.spawnfloat_x = bpy.props.FloatProperty(name = "", default=0)
    bpy.types.Scene.spawnfloat_y = bpy.props.FloatProperty(name = "", default=0)
    bpy.types.Scene.spawnfloat_z = bpy.props.FloatProperty(name = "", default=0)
    bpy.types.Scene.instBool = bpy.props.BoolProperty(name = "Instance", default=True)
    bpy.types.Scene.useRarity = bpy.props.BoolProperty(name = "Rarity", default=False)
    bpy.types.Scene.useMetadata = bpy.props.BoolProperty(name = "Metadata", default=False)
    bpy.types.Scene.gen_csv = bpy.props.BoolProperty(name = "Write To CSV", default=False)
    bpy.types.Scene.gen_json = bpy.props.BoolProperty(name = "Write To JSON", default=False)
    bpy.types.Scene.overwrite_csv = bpy.props.BoolProperty(name = "Overwrite", default=True)
    bpy.types.Scene.useProxySwap = bpy.props.BoolProperty(name = "Proxy Swap", default=True)
    
    bpy.types.Scene.expandSettings = bpy.props.BoolProperty(default = False)
    bpy.types.Scene.expandRules = bpy.props.BoolProperty(name="Rules", default = False)
    
    
    bpy.types.Scene.possibleGen = bpy.props.FloatProperty(name = "Possibilities", default = 0)
    bpy.types.Scene.metadataVariantVar = bpy.props.StringProperty(default = "__VAR", name = "Metadata Incremental Variable")
    bpy.types.Scene.metadataAttributeName = bpy.props.StringProperty(default = "attributes", name = "Attributes Default")
    bpy.types.Scene.metadataTraitTypeName = bpy.props.StringProperty(default = "trait_type", name = "Traits Type Default")
    bpy.types.Scene.metadataValueName = bpy.props.StringProperty(default = "value", name = "Value Default")
    
    bpy.types.Scene.metadataFolderName = bpy.props.StringProperty(default = "metadata", name = "Export Folder Name")
    
    
    
    
    
    
    
    bpy.types.Scene.sk_prefix = bpy.props.StringProperty \
      (
      name = "Prefix",
      default = "hair_",
      description = "Define the prefix of the Shape Key group to be randomized.",
      )
     
    bpy.types.Scene.hide_layers_bool = bpy.props.BoolProperty \
      (
      name = "Hide VP/R",
      default = True,
      description = "Define the prefix of the Shape Key group to be randomized.",
      )
      
    bpy.types.Scene.unique_variants = bpy.props.BoolProperty \
      (
      name = "Unique",
      default = False,
      description = "Variants generated are to be individually unique",
      )
      
    """The Collection Name"""
    bpy.types.Scene.char_collection = bpy.props.StringProperty \
      (
      name = "Host",
      default = "Character",
      description = "Name of the collection to be randomized.",
      )

    bpy.types.Scene.csv_doc_name = bpy.props.StringProperty \
      (
      name = "CSV Name",
      default = "variant_data.csv",
      description = "Name of the csv to be written. CSV document is saved at the root of this project folder.",
      )


    """HOST NAME WARNING"""
    bpy.types.Scene.host_name_warning = bpy.props.StringProperty \
      (
      name = "Host Name Warning",
      default = "",
      description = "Host Name Warning.",
      )

    """Variants"""
    
    bpy.types.Scene.var_gen = bpy.props.IntProperty \
      (
      name = "Variants",
      default = 10,
      min = 1,
      description = "Number of total variants to generate.",
      )

    bpy.types.Scene.matgroup = bpy.props.IntProperty \
      (
      name = "LinkMat Group",
      default = 0,
      description = "Number of total variants to generate.",
      )
      
      
    
    bpy.types.Scene.genCodes = bpy.props.CollectionProperty(type = genCodesList)
      
      
    bpy.types.Scene.proxy_obj = PointerProperty(name="Proxy", type=bpy.types.Object)
      
      
    """ALL METADATA SLOTS"""

    bpy.types.Scene.metadata_name = bpy.props.StringProperty(name = "Name", default="Name")
    
    bpy.types.Scene.md_list = bpy.props.CollectionProperty(type = metadataList)
    
    bpy.types.Object.rules_list = bpy.props.CollectionProperty(type = rulesList)
      
    bpy.types.Scene.rule_text = bpy.props.StringProperty(name = "Rule", default="")
    
    bpy.types.Scene.output_settings = bpy.props.BoolProperty(name = "Output", default=True)
    
    bpy.types.Object.attribute_md = bpy.props.PointerProperty(type = metadataList)
      
      
      
    """HOST BUILDER STUFF"""
      
    bpy.types.Scene.host_builder_name = bpy.props.StringProperty(name = "Host Name", default = "")
    bpy.types.Scene.host_builder_collections = bpy.props.CollectionProperty(type = HB_collections)
    
    bpy.types.Scene.host_builder_stage = bpy.props.EnumProperty(name = "Host Builder Stage",
        items = [("Start", "Start", ""),
            ("Host", "Host", ""),
            ("Subcolls", "Subcolls", "")]
            )
    
    bpy.types.Scene.hb_host_warning = bpy.props.StringProperty(name = "Host Warning", default = "Host Name?")
    bpy.types.Scene.hb_gen_assets = bpy.props.BoolProperty(name = "Generate Assets Collection", default = True)
    
    bpy.types.Scene.fz_output_config = bpy.props.StringProperty(name = "Output Configuration", default = "")
    
    
    
    bpy.types.Scene.fz_render_start = bpy.props.IntProperty(name="Start Variant", default = 1, options = {'HIDDEN'}, min = 1)
    bpy.types.Scene.fz_render_step = bpy.props.IntProperty(name="Start Variant", default = 1, options = {'HIDDEN'}, min = 1)
    
      

def unregister():
    bpy.utils.unregister_class(FZR_Operator)
    bpy.utils.unregister_class(FZR_multiOBJ)
    bpy.utils.unregister_class(queueProxyForBatchRender)
    bpy.utils.unregister_class(calcPoss)
    bpy.utils.unregister_class(queueForBatchRender)
    bpy.utils.unregister_class(FZR_Panel)
    bpy.utils.unregister_class(HostBuilder_Panel)
    bpy.utils.unregister_class(metadataList)
    bpy.utils.unregister_class(rulesList)
    bpy.utils.unregister_class(HB_collections)
    bpy.utils.unregister_class(remMetadataSlot)
    bpy.utils.unregister_class(addMetadataSlot)
    bpy.utils.unregister_class(remObjectRule)
    bpy.utils.unregister_class(addObjectRule)
    
    for cls in hb_classes:
        bpy.utils.unregister_class(cls)

    for cls in legacy_classes:
        bpy.utils.unregister_class(cls)

    for cls in output_classes:
        bpy.utils.unregister_class(cls)
        
    for cls in reset_classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.fzRarity
    del bpy.types.Object.fzAttribute
    del bpy.types.Object.fzDisplayType
    del bpy.types.Material.fzRarity
    del bpy.types.Scene.sk_prefix
    del bpy.types.Scene.possibleGen
    del bpy.types.Scene.char_collection
    del bpy.types.Scene.csv_doc_name
    del bpy.types.Scene.host_name_warning
    del bpy.types.Scene.var_gen
    del bpy.types.Scene.hide_layers_bool
    del bpy.types.Scene.unique_variants
    del bpy.types.Scene.matgroup
    del bpy.types.Scene.expanded
    del bpy.types.Scene.skexpanded
    del bpy.types.Scene.spawnexpanded
    del bpy.types.Scene.spawnfloat_x
    del bpy.types.Scene.spawnfloat_y
    del bpy.types.Scene.spawnfloat_z
    del bpy.types.Scene.instBool
    del bpy.types.Scene.autoSpawn
    del bpy.types.Scene.useRarity
    del bpy.types.Scene.useMetadata
    del bpy.types.Scene.expandSettings
    del bpy.types.Scene.expandRules
    del bpy.types.Scene.gen_csv
    del bpy.types.Scene.gen_json
    del bpy.types.Scene.overwrite_csv
    del bpy.types.Scene.useProxySwap
    del bpy.types.Scene.metadataVariantVar
    del bpy.types.Scene.metadataAttributeName
    del bpy.types.Scene.metadataTraitTypeName
    del bpy.types.Scene.metadataValueName
    del bpy.types.Scene.metadataFolderName
    
    del bpy.types.Scene.proxy_obj
    
    del bpy.types.Scene.genCodes
    
    del bpy.types.Scene.metadata_name 
    del bpy.types.Scene.md_list
    del bpy.types.Object.rulesList
    del bpy.types.Scene.rule_text
    del bpy.types.Scene.output_settings
    
    del bpy.types.Object.attribute_md

    del bpy.types.Scene.host_builder_stage
    del bpy.types.Scene.hb_host_warning
    del bpy.types.Scene.hb_gen_assets
    
    del bpy.types.Scene.fz_output_config
    
    del bpy.types.Scene.fz_render_start
    del bpy.types.Scene.fz_render_step
    
if __name__ == "__main__":
    register()
    
    
