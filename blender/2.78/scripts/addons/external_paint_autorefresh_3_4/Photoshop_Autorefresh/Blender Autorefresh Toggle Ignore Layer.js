(function (){
    try{
	var layer = app.activeDocument.activeLayer;
	if(layer.name.substring(0,6)=="ignore"){layer.name = layer.name.substring(7);}
	else{layer.name = "ignore "+layer.name;}
    }
    catch(e){}
})();




