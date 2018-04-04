(function (){
    var doc = app.activeDocument;
    var active_layer = doc.activeLayer;
    //files
    var appdir = "~/_blenderextpaint_autorefresh";
    var UV_FILEPATH = appdir+"/uv.png";

    //save photoshop settings, add a new layer
    var ruler_units = app.preferences.rulerUnits;
    var type_units = app.preferences.typeUnits;
    app.preferences.rulerUnits = Units.PIXELS;
    app.preferences.typeUnits = TypeUnits.PIXELS;
    var wf = doc.width.value/512.00 * 100.00;
    var hf = doc.height.value/512.00 * 100.00;
    doc.artLayers.add();

    ////////////code generated by photoshop script listener plugin to place the uv image into the layer above currently active layer////////////////
    var idPlc = charIDToTypeID( "Plc " );
    var desc135 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
    desc135.putPath( idnull, new File(UV_FILEPATH) );
    var idFTcs = charIDToTypeID( "FTcs" );
    var idQCSt = charIDToTypeID( "QCSt" );
    var idQcsa = charIDToTypeID( "Qcsa" );
    desc135.putEnumerated( idFTcs, idQCSt, idQcsa );
    var idOfst = charIDToTypeID( "Ofst" );
    var desc136 = new ActionDescriptor();
    var idHrzn = charIDToTypeID( "Hrzn" );
    var idPxl = charIDToTypeID( "#Pxl" );
    desc136.putUnitDouble( idHrzn, idPxl, 0.000000 );
    var idVrtc = charIDToTypeID( "Vrtc" );
    var idPxl = charIDToTypeID( "#Pxl" );
    desc136.putUnitDouble( idVrtc, idPxl, 0.000000 );
    var idOfst = charIDToTypeID( "Ofst" );
    desc135.putObject( idOfst, idOfst, desc136 );
    var idWdth = charIDToTypeID( "Wdth" );
    var idPrc = charIDToTypeID( "#Prc" );
    desc135.putUnitDouble( idWdth, idPrc, wf );
    var idHght = charIDToTypeID( "Hght" );
    var idPrc = charIDToTypeID( "#Prc" );
    desc135.putUnitDouble( idHght, idPrc, hf );
    executeAction( idPlc, desc135, DialogModes.NO );
    ////////////code generated by photoshop script listener plugin to rasterize the placed layer (need to do this after placing)////////////////
    var idrasterizeLayer = stringIDToTypeID( "rasterizeLayer" );
    var desc137 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
    var ref92 = new ActionReference();
    var idLyr = charIDToTypeID( "Lyr " );
    var idOrdn = charIDToTypeID( "Ordn" );
    var idTrgt = charIDToTypeID( "Trgt" );
    ref92.putEnumerated( idLyr, idOrdn, idTrgt );
    desc137.putReference( idnull, ref92 );
    executeAction( idrasterizeLayer, desc137, DialogModes.NO );

    //restore photoshop settings
    doc.activeLayer.name = "ignore uv";
    doc.activeLayer = active_layer;
    app.preferences.rulerUnits = ruler_units;
    app.preferences.typeUnits = type_units;
})();




