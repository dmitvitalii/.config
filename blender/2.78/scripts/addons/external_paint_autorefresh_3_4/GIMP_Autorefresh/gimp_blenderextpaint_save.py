import os
from gimpfu import *
from gimpenums import *
from urlparse import urlparse #for exporting when using .xcf images
   
def pluginFunction(img, drw):
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    SYNC_FILEPATH = appdir+"/sync.txt"

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
    #done saving the image, delete image copy
    pdb.gimp_image_delete(img_copy)

    #gimp is done saving the image, now let blender go
    try:
        syncf=open(SYNC_FILEPATH, 'w')
        syncf.write("blender")
        syncf.close()
    except: pass

register(
  "gimp_blenderextpaint_save",
  "Save the image (doesn't affect ignored layers), then let Blender reload it",
  "Save the image (doesn't affect ignored layers), then let Blender reload it",
  "See Blender script for developers",
  "See Blender script for developers",
  "",
  "<Image>/Filters/Blender-GIMP Autorefresh/Save",
  "*",
  [],
  [],
  pluginFunction
)
main()




