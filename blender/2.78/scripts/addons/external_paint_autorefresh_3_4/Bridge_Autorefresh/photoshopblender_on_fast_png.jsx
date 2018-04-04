//Note, visit http://www.adobe.com/devnet/photoshop/scripting.html for 
//scripting documentation and the Photoshop script listener plugin.

///////////////////////
//global helper object
///////////////////////
var blender_autorefresh_globals = {
    messaging_ok: false,
    tasks: []
};

///////////////////////
//autorefresh function
///////////////////////
function blenderAutorefreshFastPNG(runid){
    
    //files
    var appdir = "~/_blenderextpaint_autorefresh";
    var syncf = new File(appdir+"/sync.txt");
    var modef = new File(appdir+"/mode.txt");

    //mode and run id
    modef.open('r');
    var strings = modef.readln().split("  ");
    modef.close();
    var runid_from_file = parseInt(strings[0]);
    var current_mode = strings[1];
    if(runid_from_file != runid){
	//Bridge API says to return undefined to stop a task, but it doesn't seem 
        //to work, so do the following instead to manually stop the Bridge tasks.
	for(var i=0; i < blender_autorefresh_globals.tasks.length; i++){
            if(blender_autorefresh_globals.tasks[i].runid==runid){
                app.cancelTask(parseInt(blender_autorefresh_globals.tasks[i].taskid));
                blender_autorefresh_globals.tasks.splice(i,1); i--;
            }
        }
	return;
    }

    //Check the global messaging flag, if it's false it means Photoshop didn't process
    //the previous message yet, so return in this case but don't stop the task.
    if(blender_autorefresh_globals.messaging_ok == false){return;}
    
    //////////////////////////////////
    //currently painting in photoshop
    //////////////////////////////////
    if(current_mode == "extpaint_to_blender"){

	//sync with blender
	syncf.open('r');
	if(syncf.readln() != "extpaint"){
	    syncf.close();
	    return;
        }
	syncf.close();

     	//check for activity (by asking photoshop if the history brush got updated), if yes then save image
	blender_autorefresh_globals.messaging_ok = false;
	//keep initial message quick to prevent lag during photoshop activity
	////////////message string to check if the history brush got updated in photoshop, meaning the user edited the image///////////
	var b="app.activeDocument.activeHistoryState==app.activeDocument.activeHistoryBrushSource?1:0";
	/////////////////////////////////////////////////////////////////////////////////////////////////////////
	var message = new BridgeTalk();
	message.target = "photoshop";
	message.body = b;
	message.onResult = function(r){
	    if(parseInt(r.body) > 0){return;}
	    //image save message
	    /////////build a message string using code generated by photoshop script listener plugin (this code calls the needed script in Photoshop)/////////
	    var b1="var idAdobeScriptAutomationScripts = stringIDToTypeID( \"AdobeScriptAutomation Scripts\" );";
	    b1+="var desc22 = new ActionDescriptor();";
	    b1+="var idjsNm = charIDToTypeID( \"jsNm\" );";
	    b1+="desc22.putString( idjsNm, \"\"\"Blender Autorefresh Save Fast PNG\"\"\" );";
	    b1+="var idjsMs = charIDToTypeID( \"jsMs\" );";
	    b1+="desc22.putString( idjsMs, \"\"\"undefined\"\"\" );";
	    b1+="executeAction( idAdobeScriptAutomationScripts, desc22, DialogModes.NO );";
	    /////////////////////////////////////////////////////////////////////////////////////////////////////
	    var message1 = new BridgeTalk();
	    message1.target = "photoshop";
	    message1.body = b1;
            //No blender_autorefresh_globals.messaging_ok=true below since we consider this message+response
	    //to be sequential with the reset history brush message+response that goes afterwards.
	    message1.onResult = function(r){}
	    message1.send();
	}
	message.send();
	//send a message to photoshop telling it to reset the history brush
	/////////build a message string using code generated by photoshop script listener plugin (this code resets the history brush in Photoshop)//////////
	b="var idsetd = charIDToTypeID( \"setd\" );";
        b+="var desc38 = new ActionDescriptor();";
        b+="var idnull = charIDToTypeID( \"null\" );";
        b+="var ref46 = new ActionReference();"
        b+="var idHstS = charIDToTypeID( \"HstS\" );";
        b+="var idHstB = charIDToTypeID( \"HstB\" );";
        b+="ref46.putProperty( idHstS, idHstB );";
        b+="desc38.putReference( idnull, ref46 );";
        b+="var idT = charIDToTypeID( \"T   \" );";
        b+="var ref47 = new ActionReference();";
        b+="var idHstS = charIDToTypeID( \"HstS\" );";
        b+="var idCrnH = charIDToTypeID( \"CrnH\" );";
        b+="ref47.putProperty( idHstS, idCrnH );";
        b+="desc38.putReference( idT, ref47 );";
        b+="executeAction( idsetd, desc38, DialogModes.NO );";
	//////////////////////////////////////////////////////////////////////////////////////////////////////
	message = new BridgeTalk();
	message.target = "photoshop";
	message.body = b;
	message.onResult = function(r){blender_autorefresh_globals.messaging_ok = true;}
	message.send();

	//Note, don't need to add sync file code here to let blender go,
	//since that gets done in the photoshop script that gets called.
    }

    ////////////////////////////////
    //currently painting in blender
    ////////////////////////////////
    else if(current_mode == "blender_to_extpaint"){
	//sync with blender
	syncf.open('r');
	if(syncf.readln() != "extpaint"){
	    syncf.close();
	    return;
        }
	syncf.close();

	//image reload message
	blender_autorefresh_globals.messaging_ok = false;
	/////////build a message string using code generated by photoshop script listener plugin (this code calls the needed script in Photoshop)/////////////
	var b="var idAdobeScriptAutomationScripts = stringIDToTypeID( \"AdobeScriptAutomation Scripts\" );";
	b+="var desc22 = new ActionDescriptor();";
	b+="var idjsNm = charIDToTypeID( \"jsNm\" );";
	b+="desc22.putString( idjsNm, \"\"\"Blender Autorefresh Reload\"\"\" );";
	b+="var idjsMs = charIDToTypeID( \"jsMs\" );";
	b+="desc22.putString( idjsMs, \"\"\"undefined\"\"\" );";
	b+="executeAction( idAdobeScriptAutomationScripts, desc22, DialogModes.NO );";
	/////////////////////////////////////////////////////////////////////////////////////////////////////
	var message = new BridgeTalk();
	message.target = "photoshop";
	message.body = b;
	message.onResult = function(r){blender_autorefresh_globals.messaging_ok = true;}
	message.send();

	//Note, don't need to add sync file code here to let blender go,
	//since that gets done in the photoshop script that gets called.

    }//end if-else  
}

///////
//menu
///////
function blenderAutorefreshMenu(){
    this.menuID = "blender_autorefresh";
    this.menuCommandID = "blenderphotoshop_on_fast_png";
    //var menu_element = new MenuElement("menu", "Blender Autorefresh", "at the end of tools", menuID);
    var menu_command = new MenuElement("command", "On: fast PNG", "at the end of "+menuID, menuCommandID);
    
    ////////////////////
    //start autorefresh
    ////////////////////
    menu_command.onSelect = function(m){
        
	//files
	var appdir = "~/_blenderextpaint_autorefresh";
	var pausef = new File(appdir+"/pause.txt");
	var modef = new File(appdir+"/mode.txt");

	//pause time
	try{
	    pausef.open('r');
	    var pause_time = 1000.00*parseFloat(pausef.readln());
	    pausef.close();
	}catch(e){return;}

	//thread runid
	try{
	    modef.open('r');
	    var runid = parseInt(modef.readln().split("  ")[0]);
	    modef.close();
	}catch(e){return;}

	//Start autorefresh by scheduling a Bridge task that keeps sending messages to Photoshop.
	blender_autorefresh_globals.messaging_ok = true;
	var taskid = app.scheduleTask("blenderAutorefreshFastPNG("+runid+")", pause_time, true);
	blender_autorefresh_globals.tasks.push({runid: runid, taskid: taskid.toString()});
    }
}
blenderAutorefreshMenu();




