import os
from gimpfu import *
from gimpenums import *
   
def pluginFunction(img, drw):
    #set filepaths
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    UV_FILEPATH = appdir+"/uv.png"

    try:
        uv_layer = pdb.gimp_file_load_layer(img, UV_FILEPATH)
        pdb.gimp_image_insert_layer(img, uv_layer, None, 0)
        pdb.gimp_item_set_name(uv_layer, "ignore uv")
        pdb.gimp_layer_scale(uv_layer, img.width, img.height, False)
        pdb.gimp_image_set_active_layer(img, drw)
        #re-render
        pdb.gimp_image_resize(img, img.width, img.height, 0, 0)
    except: pass

register(
  "gimp_blenderextpaint_uv_import",
  "Import UVs",
  "Import UVs",
  "See Blender script for developers",
  "See Blender script for developers",
  "",
  "<Image>/Filters/Blender-GIMP Autorefresh/UV Import",
  "*",
  [],                        
  [],
  pluginFunction
)
main()




