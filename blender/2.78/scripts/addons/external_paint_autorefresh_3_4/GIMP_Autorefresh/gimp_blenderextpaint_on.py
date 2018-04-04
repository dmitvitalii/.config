import os
import time
from gimpfu import *
from gimpenums import *
from urlparse import urlparse #for exporting when using .xcf images
   
def pluginFunction(img, drw):

    #set filepaths
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    PAUSE_FILEPATH = appdir+"/pause.txt"
    SYNC_FILEPATH = appdir+"/sync.txt"
    MODE_FILEPATH = appdir+"/mode.txt"
    PLACE_FILEPATH = appdir+"/place.txt"

    #get pause time
    try:
        pausef=open(PAUSE_FILEPATH, 'r')
        pause_time = float(pausef.readline().rstrip())
        pausef.close()
    except: return

    #get thread run id
    try:
        modef=open(MODE_FILEPATH, 'r')
        runid = int(modef.readline().rstrip().split()[0])
        modef.close()
    except: return

    #The prev_layer variable is used when user is painting in blender while gimp reloads the image. We want 
    #gimp to keep reloading into the same layer, so keep track of the layer with the prev_layer variable.
    prev_layer = None
  
    #autorefresh loop
    while True:
        if pdb.gimp_image_is_valid(img)!=True: return

        ####################################################################################################
        #Get the image filepath. First try to get the image export filepath, in case the user is working
        #with a .xcf image that has been exported. If there is no export filepath, use image save filepath.
        ####################################################################################################
        try:
            #below returns None if image hasn't been exported
            image_filepath = pdb.gimp_image_get_exported_uri(img)
            #for some reason the generated url starts with a leading '/'
            #(ex. '/C://path'), and gimp_file_save doesn't agree with that
            if image_filepath: image_filepath = urlparse(image_filepath).path.lstrip('/')
            else: image_filepath = pdb.gimp_image_get_filename(img)
        except: image_filepath = pdb.gimp_image_get_filename(img)

        modef=open(MODE_FILEPATH, 'r')
        [runid_from_file, current_mode] = modef.readline().rstrip().split()
        modef.close()
        if int(runid_from_file)!=runid:
            return

        ############################
        #currently painting in gimp
        ############################
        if current_mode=="extpaint_to_blender":
            prev_layer = None

            #sync with blender, check that blender isn't reloading the image
            syncf=open(SYNC_FILEPATH, 'r')
            if syncf.readline().rstrip() != "extpaint":
                syncf.close()
                time.sleep(pause_time); continue
            syncf.close()

            #check for activity (that user updated the image)
            if not pdb.gimp_image_is_dirty(img): time.sleep(pause_time); continue
            pdb.gimp_image_clean_all(img)

            ##########################################################################
            #image save (using a copy of the actual image so we can do stuff with it)
            ##########################################################################
            img_copy = pdb.gimp_image_duplicate(img)
            all_layers_ignored=True     
            #do depth-first search to skip ignored layers and layer groups
            item_stack=img_copy.layers[:]
            while len(item_stack) > 0:
                item=item_stack.pop()
                #visit
                if pdb.gimp_item_get_name(item).startswith("ignore"):
                    pdb.gimp_item_set_visible(item, False)
                    continue
                #add sub-items to stack
                if not pdb.gimp_item_is_group(item):
                    all_layers_ignored=False
                    continue
                for sub_item in item.layers: item_stack.append(sub_item)
            if not all_layers_ignored:
                drw = pdb.gimp_image_merge_visible_layers(img_copy, 0)
                try: pdb.gimp_file_save(img_copy, drw, image_filepath, image_filepath)
                except: pass    
            #done saving the image copy, now can delete the copy
            pdb.gimp_image_delete(img_copy)

            #gimp is done saving the image, now let blender go
            try:
                syncf=open(SYNC_FILEPATH, 'w')
                syncf.write("blender")
                syncf.close()
            except: pass            

        ###############################
        #currently painting in blender
        ###############################
        elif current_mode=="blender_to_extpaint":

            #sync with blender, check that blender isn't painting the image
            syncf=open(SYNC_FILEPATH, 'r')
            if syncf.readline().rstrip() != "extpaint":
                syncf.close()
                time.sleep(pause_time); continue
            syncf.close()    

            ##############
            #image reload
            ##############
            active_layer = pdb.gimp_image_get_active_layer(img)
            #check if need to place image into current layer or load into new layer
            try:
                placef=open(PLACE_FILEPATH, 'r')
                place = True if float(placef.readline().rstrip())>0 else False
                placef.close()
            except: place=False
            #import blender image into buffer. buffer gets deleted later
            img_to_copy = pdb.gimp_file_load(image_filepath, image_filepath)
            pdb.gimp_selection_all(img_to_copy)
            buffer_name = pdb.gimp_edit_named_copy(img_to_copy.layers[0], "blenderextpaintbuffer")
            pdb.gimp_image_delete(img_to_copy)
            #in case the user has some active selection in gimp, save the selection
            try: saved_selection = pdb.gimp_image_get_selection(img)
            except: pass
            #initial reload
            if pdb.gimp_item_is_valid(prev_layer)!=True and place==True:
                pdb.gimp_selection_all(img)
                pdb.gimp_edit_clear(active_layer)
                pdb.gimp_selection_none(img)
                sel = pdb.gimp_edit_named_paste(active_layer, buffer_name, 1)
                pdb.gimp_floating_sel_anchor(sel)
                prev_layer = active_layer
            elif pdb.gimp_item_is_valid(prev_layer)!=True and place!=True:
                drw = pdb.gimp_file_load_layer(img, image_filepath)
                pdb.gimp_image_insert_layer(img, drw, None, -1)
                prev_layer = drw
            #reload after the initial reload
            else:
                pdb.gimp_selection_all(img)
                pdb.gimp_edit_clear(prev_layer)
                pdb.gimp_selection_none(img)
                sel = pdb.gimp_edit_named_paste(prev_layer, buffer_name, 1)
                pdb.gimp_floating_sel_anchor(sel)
            #restore selection, delete buffer
            try: pdb.gimp_image_select_item(img, 2, saved_selection)
            except: pass
            pdb.gimp_buffer_delete(buffer_name)
            #re-render
            pdb.gimp_image_resize(img, img.width, img.height, 0, 0)  

            #gimp is done reloading the image, now let blender go
            syncf=open(SYNC_FILEPATH, 'w')
            syncf.write("blender")
            syncf.close()

        ####################################################
        #exit if wrong mode, otherwise pause and keep going
        ####################################################
        else: return
        time.sleep(pause_time)
    
register(
  "gimp_blenderextpaint_on",
  "Activate autorefresh in GIMP",
  "Activate autorefresh in GIMP",
  "See Blender script for developers",
  "See Blender script for developers",
  "",
  "<Image>/Filters/Blender-GIMP Autorefresh/On",
  "*",
  [],                        
  [],
  pluginFunction
)
main()




