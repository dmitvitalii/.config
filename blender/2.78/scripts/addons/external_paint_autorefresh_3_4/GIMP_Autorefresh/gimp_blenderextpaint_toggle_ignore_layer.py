from gimpfu import *
from gimpenums import *
   
def pluginFunction(img, drw):
    layername = pdb.gimp_item_get_name(drw)
    if layername.startswith("ignore"):
        pdb.gimp_item_set_name(drw, layername[7:])
    else: pdb.gimp_item_set_name(drw, "ignore "+layername)
  
register(
  "gimp_blenderextpaint_toggle_ignore_layer",
  "Ignore or unignore current layer",
  "Ignore or unignore current layer",
  "See Blender script for developers",
  "See Blender script for developers",
  "",
  "<Image>/Filters/Blender-GIMP Autorefresh/Toggle Ignore Layer",
  "*",
  [],
  [],
  pluginFunction
)
main()




