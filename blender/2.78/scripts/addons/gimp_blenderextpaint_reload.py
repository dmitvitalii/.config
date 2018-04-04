import os
from gimpfu import *
from gimpenums import *
from urlparse import urlparse #for getting exported filepath when using .xcf images

def pluginFunction(img, drw):
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    PLACE_FILEPATH = appdir+"/place.txt"
    SYNC_FILEPATH = appdir+"/sync.txt"
    
    if pdb.gimp_image_is_valid(img)==False: return

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
    
    ##############
    #image reload
    ##############
    active_layer = pdb.gimp_image_get_active_layer(img)
    #check if need to place image into current layer or load into new layer
    try:
        placef=open(PLACE_FILEPATH, 'r')
        place = True if float(placef.readline().rstrip())>0 else False
        placef.close()
    except: place = False
    #import blender image into buffer. buffer gets deleted later
    img_to_copy = pdb.gimp_file_load(image_filepath, image_filepath)
    pdb.gimp_selection_all(img_to_copy)
    buffer_name = pdb.gimp_edit_named_copy(img_to_copy.layers[0], "blenderextpaintbuffer")
    pdb.gimp_image_delete(img_to_copy)
    #in case the user has some active selection in gimp, save the selection
    try: saved_selection = pdb.gimp_image_get_selection(img)
    except: pass
    #check the "place" setting, load the image
    if place==True:
        pdb.gimp_selection_all(img)
        pdb.gimp_edit_clear(active_layer)
        pdb.gimp_selection_none(img)
        sel = pdb.gimp_edit_named_paste(active_layer, buffer_name, 1)
        pdb.gimp_floating_sel_anchor(sel)
    else:
        drw = pdb.gimp_file_load_layer(img, image_filepath)
        pdb.gimp_image_insert_layer(img, drw, None, -1)
    #restore selection, delete buffer
    try: pdb.gimp_image_select_item(img, 2, saved_selection)
    except: pass
    pdb.gimp_buffer_delete(buffer_name)
    #re-render
    pdb.gimp_image_resize(img, img.width, img.height, 0, 0) 

    #let blender go
    try:
        syncf=open(SYNC_FILEPATH, 'w')
        syncf.write("blender")
        syncf.close()
    except: pass

register(
  "gimp_blenderextpaint_reload",
  "Reload the image (doesn't affect ignored layers)",
  "Reload the image (doesn't affect ignored layers)",
  "See Blender script for developers",
  "See Blender script for developers",
  "",
  "<Image>/Filters/Blender-GIMP Autorefresh/Reload",
  "*",
  [],                        
  [],
  pluginFunction
)
main()




