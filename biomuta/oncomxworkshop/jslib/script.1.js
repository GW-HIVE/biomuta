var childList = {};
var isMain = {};
var nodeid2name = {};
var nodeid2index = {};
var treeJson = [];
var toggleCount = {};
var currentBatch = 1;
var batchSize = 100;
var batchCount = 0;
var datasetName = '';
var readMeFile = '';
var datasetId = '';
var resJson = {};
var filterHash = {};
var seen = {"category":{}, "species":{}, "filetype":{}};       


/////////////////////////////////////
$(document ).ready(function() {
  

	var sections = getSections();
  	$("#sectionscn").html(sections);
  	setPageCn(pageid);
});

///////////////////////////////////////////////////
$(document).on('click', '#closemodulemenu', function (event) {
        event.preventDefault();
        $("#sectionscn").css("display", "none");
});


///////////////////////////////////////////////////
$(document).on('click', '.filtercheckbox', function (event) {
	
	event.preventDefault();
	
	filterHash = {"category":{}, "species":{}, "filetype":{}};
	$("input[type=checkbox][name=category]:checked").each(function () {
		filterHash["category"][$(this).val()] = true;
	});

	$("input[type=checkbox][name=species]:checked").each(function () {
                filterHash["species"][$(this).val()] = true;
        });

	$("input[type=checkbox][name=filetype]:checked").each(function () {
                filterHash["filetype"][$(this).val()] = true;
        });	

	rndrGridContent();

});


///////////////////////////////////////////////////
$(document).on('click', '.readmelink', function (event) {
 
	event.preventDefault(); 
	var i = this.id.split("_")[1];
	var j = this.id.split("_")[2];

	$("html, body").animate({ scrollTop: 0 }, "0");
	

 
	var s = "padding:2px 20px 2px 20px;";
        var closebtn = '<input name=btn2 id=closewindow type=submit style="'+s+'" value="&times;">';
        var table = '<table width=100% style="font-size:13px;" border=0>' +
                        '<tr height=25><td align=right>'+ closebtn+'</td></tr>' +
                        '</table>';

        var s = 'position:absolute;left:0%;top:10px;width:95%;height:20px;';
        s += 'filter: alpha(opacity=100);opacity: 1.00;z-index:1003';
        var div1 = '<DIV id=popdiv1 style="'+s+'">'+table+'</DIV>';


        var s = 'position:absolute;left:5%;top:5%;width:90%;height:90%;overflow:auto;';
        s += 'background:#fff;filter: alpha(opacity=100);opacity: 1.00;z-index:1002;padding:10px;';
        var div2 = '<DIV id=popdiv2 style="'+s+'"></DIV>';

        var s = 'position:absolute;left:10%;width:80%;height:100%;top:10%;';
        s += 'background:#eee;filter: alpha(opacity=100);opacity: 1.00;z-index:1001;';
        var popdiv = '<DIV id=popdiv style="'+s+'">'+ div1 + div2+'</DIV>';

        var s = 'position:absolute;left:0px;top:0px;width:100%;height:3000px;background:#000;color:#fff;';
        s += 'filter: alpha(opacity=75);z-index:1000;';
        s += 'opacity: 0.75;';
        var bgdiv = '<DIV id=bgdiv style="'+s+'"></DIV>';

        $("body").append(bgdiv + popdiv);



	var readmeFile = '/csv/' + resJson[i]["datasets"][j]["readmefilename"];
	setReadmeContent(readmeFile, '#popdiv2');



});

///////////////////////////////////////
$(document).on('click', '#closewindow', function (event) {
        event.preventDefault();
        $("#popdiv1").remove();
        $("#popdiv2").remove();
        $("#popdiv").remove();
        $("#bgdiv").remove();

});

  
/////////////////////////////////////
$(document).on('click', '.section1', function (event) {
      event.preventDefault();
      pageid = this.id;
      setPageCn(pageid);
      var sections = getSections();
      $("#sectionscn").html(sections);
});


///////////////////////////////////
$(document).on('click', '#moduleicon', function (event) {
        event.preventDefault();

	$("#sectionscn").toggle();
	//$("#sectionscn").css("display", "block");
	//$("#sectionscn").toggle();

});

//////////////////////////////////////////
$(document).on('click', '.batchnavlink', function (event) {
        event.preventDefault();
        var emId = this.id;
        
	if(emId == 'next' && currentBatch != batchCount){
                currentBatch = currentBatch + 1;
        }
        else if (emId == 'prev' && currentBatch != 1){
                currentBatch = currentBatch - 1;
        }
        else if (emId == 'start'){
                currentBatch = 1;
        }
        else if (emId == 'end'){
                currentBatch = batchCount;
        }

	setBrowsePage();

});




////////////////////////////
function setPageCn(pageid){

	if(pageid == 'data'){
		setGridPage();
	}
	else if(pageid == 'view'){
                datasetId = window.location.href.trim().split("/").pop();
		setBrowsePage();
        }
	else{
         	fillStaticHtmlCn('/content/page.'+pageid+'.html', '#pagecn');
     	}
}



////////////////////////////
function setGridPage(){


        var url = htmlRoot + '/json/datasets.json'
        var reqObj = new XMLHttpRequest();
        reqObj.open("GET", url, true);
        reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.onreadystatechange = function() {
                if (reqObj.readyState == 4 && reqObj.status == 200) {
                        //console.log('response='+reqObj.responseText);
                        resJson = JSON.parse(reqObj.responseText);
			rndrGridContent();
                }
        };
        reqObj.send();

}


//////////////////////////////////////////
function rndrGridContent(){

	var iconHash = {"fasta":"fasta-icon.png", "csv":"csv-icon.png"};
	var gridDivs = '<div class="section group">';
	for (var i in resJson){
		var ii = parseInt(i) + 1;
		var cat = resJson[i]["title"];
		seen["category"][cat] = true;
		if("category" in filterHash && !(cat in filterHash["category"])){
			continue;
		}
		var datasets = resJson[i]["datasets"];
		var gridWidth = 250;
		var gridHeight = 140;
		for (var j in datasets){
			var jj = parseInt(j) + 1;
			var xPos = j*(gridWidth + 80);
			var fileType = datasets[j]["filetype"];
			var species = datasets[j]["species"];
			seen["filetype"][fileType] = true;
			seen["species"][species] = true;
                        if("filetype" in filterHash && !(fileType in filterHash["filetype"])){
                        	continue;
                	}
			if("species" in filterHash && !(species in filterHash["species"])){
                                continue;
                        }
			var miniTable = '';
			if ("minitable" in datasets[j]){
				miniTable = rndrMiniTable(datasets[j]["minitable"]);
			}
		
			var s = 'position:relative;text-align:center;border:1px solid #ccc;';
                        s += 'width:300px;height:300px;300px;margin:10px;padding:20px;background:#fff;';
                        var titleUrl = htmlRoot + '/view/'+ ii + '.' + jj;
                        gridDivs += '<div class="col span_1_of_3" style="'+s+'">';
	
			var s = 'position:absolute;;width:45%;height:15px;border:0px solid red;';
                        s += 'right:5%;top:0%;text-align:center;color:#333;';
                        s += 'padding:15px 0px 0px 0px;text-align:right;font-size:11px;';
                        var objId = ("object_id" in datasets[j] ? datasets[j]["object_id"] : "0000");
                        gridDivs += '<div style="'+s+'">';
                        gridDivs += (datasets[j]["status"] == 1 ? 'Object ' + objId :
                                                '<font color=red>in progress</font>');
                        gridDivs += '</div>';
                        var s = 'position:absolute;width:45%;height:15px;border:0px solid red;';
                        s += 'left:5%;top:0%;color:#333;text-align:left;';
                        s += 'padding:15px 0px 0px 0px;font-size:11px;';
                        gridDivs += '<div style="'+s+'"> Species - ';
                        gridDivs += datasets[j]["species"];
                        gridDivs += '</div>';

                        var s = 'position:absolute;left:15%;top:60px;width:70%;height:50px;font-size:18px;';
			s += 'font-weight:bold;color:#004065;vertical-align:bottom;';
                        s += 'border:0px solid red;';
			gridDivs += '<div style="'+s+'">';
			gridDivs += datasets[j]["title"];
			gridDivs += '</div>';
		
			var iconUrl = ghtmlRoot + '/imglib/' + iconHash[fileType];
			var s = 'position:absolute;left:10%;top:120px;width:80%;height:130px;font-size:18px;';
			s += 'font-size:12px;border:0px solid red;';
			gridDivs += '<div style="'+s+'">';
			gridDivs += miniTable;
			gridDivs += (miniTable == '' ? '<img src="'+iconUrl+'" height=90%>' : "");
			gridDivs += '</div>';
		
			var s = 'position:absolute;left:10%;top:250px;width:80%;height:40px;font-size:18px;';
                        s += 'font-size:12px;border:0px solid red;';
			gridDivs += '<div style="'+s+'">';
			gridDivs += datasets[j]["description"];
			gridDivs += '</div>';	
			var datasetName = datasets[j]["filename"];
		 	var url1 = htmlRoot + '/csv/'+datasetName
			
			var s = 'position:absolute;left:10%;top:300px;width:80%;height:20px;font-size:18px;';
                        s += 'font-size:13px;text-align:center;color:#004065;cursor:hand;border:0px solid red;';
			var linkId = "dataset_" + i + "_" + j;
			gridDivs += '<div style="'+s+'">';
			gridDivs += '<a href="'+url1+'"  download="'+datasetName+'">Download</a>';
			gridDivs += ' | <a id="'+linkId+'" class=readmelink>README</a>';
			gridDivs += '</div>';


			gridDivs += '</div>';
		}
	}
	gridDivs += '</div>';

	
	var filterTable = '<table border=0 style="font-size:13px;">';
	var style = 'font-size:14px;font-weight:bold;color:#777;';
	filterTable += '<tr><td colspan=2 style="'+style+'">Refine results by</td></tr>';
	var style = 'font-size:13px;font-weight:bold;';
	filterTable += '<tr height=40>';
	filterTable += '<td valign=bottom colspan=2 style="'+style+'">Dataset categories</td>';
	filterTable += '</tr>';
	for (var x in seen["category"]){
		var chkd = "checked";
		if ("category" in filterHash){
			chkd = (filterHash["category"][x] == true ? "checked" : "");
		}
		var chkbox = '<input class=filtercheckbox type=checkbox name=category '+chkd+' width=15 value="'+x+'">';
		filterTable += '<tr><td width=25 align=right>'+chkbox+'</td><td>'+x+'</td></tr>';
	}	
	
	var style = 'font-size:13px;font-weight:bold;';
        filterTable += '<tr height=40>';
        filterTable += '<td valign=bottom colspan=2 style="'+style+'">Species</td>';
        filterTable += '</tr>';
        for (var x in seen["species"]){
                var chkd = "checked";
                if ("species" in filterHash){
                        chkd = (filterHash["species"][x] == true ? "checked" : "");
                }
                var chkbox = '<input class=filtercheckbox type=checkbox name=species '+chkd+' width=15 value="'+x+'">';
                filterTable += '<tr><td width=25 align=right>'+chkbox+'</td><td>'+x+'</td></tr>';
        }

	var style = 'font-size:13px;font-weight:bold;';
	filterTable += '<tr height=40>';
	filterTable += '<td valign=bottom colspan=2 style="'+style+'">File types</td>';
	filterTable += '</tr>';
	for (var x in seen["filetype"]){
		var chkd = "checked";
                if ("filetype" in filterHash){
                        chkd = (filterHash["filetype"][x] == true ? "checked" : "");
                }
		var chkbox = '<input class=filtercheckbox type=checkbox name=filetype '+chkd+' width=15 value="'+x+'">';
		filterTable += '<tr><td width=25 align=right>'+chkbox+'</td><td>'+x+'</td></tr>';
	}
	filterTable += '</table>';

	var gridTable = '<table width=100% height=100% border=0>';
                      var style = 'padding:10px;border:1px solid #eee;background:#f8f8f8;';
                      gridTable += '<tr height=25>' 
	gridTable += '<td width=20% style="'+style+'" valign=top>' + filterTable + '</td>';
	gridTable += '<td>' + gridDivs + '</td>';
	gridTable += '</tr>';
	gridTable += '</table>';
	$("#pagecn").html(gridTable);
	return
}





////////////////////////////
function setBrowsePage(){

	
	var url = htmlRoot + '/json/datasets.json'
        var reqObj = new XMLHttpRequest();
	reqObj.open("GET", url, true);
	reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.onreadystatechange = function() {
                if (reqObj.readyState == 4 && reqObj.status == 200) {
			var objList = JSON.parse(reqObj.responseText);
			var style = 'width:100%;height:30px;';
			var datasetIdParts = datasetId.split(".");
			var id1 = parseInt(datasetIdParts[0]) - 1;
			var id2 = parseInt(datasetIdParts[1]) - 1;
			datasetName = objList[id1]["datasets"][id2]["filename"];
			readMeFile = objList[id1]["datasets"][id2]["readmefilename"];
			var fileType = objList[id1]["datasets"][id2]["filetype"];
			var datasetTitle = objList[id1]["datasets"][id2]["title"];
			var datasetDesc = objList[id1]["datasets"][id2]["description"];
                	var cn = '<table width=100% border=0>';
			cn += '<tr><td style="font-weight:bold;">'+datasetTitle+'</td></tr>';
			cn += '<tr><td >'+datasetDesc+'</td></tr>';
			cn += '<tr><td style="padding:0 0 40 0;" id=summarycn>&nbsp;</td></tr>';
			cn += '<tr><td id=tablecn></td></tr>';
			cn += '</table>';
			$("#pagecn").html(cn);
			if(fileType.toLowerCase() == "fasta"){
				var url1 = htmlRoot + '/csv/'+datasetName
				var url2 = htmlRoot + '/csv/'+readMeFile
				var lbl = 'Download ' + fileType.toUpperCase() + ' file';
        			var downloadLink1 = '<a href="'+url1+'"  download="'+datasetName+'">'+lbl+'</a>';
				var downloadLink2 = '<a href="'+url2+'" target=_>View README File</a>';
				var x = '<b>Downloads</b><br>';
				x += '<ul>';
				x += '<li>' + downloadLink1 + '</li>';
				x += '<li>' + downloadLink2 + '</li>';
				x += '</ul>';
				$("#tablecn").html(x);
			}
			else{
				setDatasetCn();
			}
		}
        };
        reqObj.send();
} 

////////////////////////////////////
function setDatasetCn(){




        var url = htmlRoot + '/csv/'+datasetName
        var reqObj = new XMLHttpRequest();
        reqObj.open("GET", url, true);
        reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.onreadystatechange = function() {
                if (reqObj.readyState == 4 && reqObj.status == 200) {
                        var lines = reqObj.responseText.split("\n");
			//var tableJson = [];
			//for (var i=0; i < lines.length; i ++){
			//	lines[i] = lines[i].replace(",", "\",\"");
			//	var jsonText = "[" + lines[i] + "]";
			//	console.log(jsonText);
			//	tableJson[i] = JSON.parse(jsonText);
				//tableJson[i] = lines[i].split(",")
			//}
                       	var tableJson = parseCSV(reqObj.responseText);
			rndrDataSummary(tableJson, "#summarycn");
                        rndrTable(tableJson, "#tablecn");
                }
        };
        reqObj.send();
}


//////////////////////////////////
function setHtmlContent(fileName, containerId){

        var url = htmlRoot + '/' + fileName;
        var reqObj = new XMLHttpRequest();
        reqObj.containerId = containerId;
        reqObj.open("GET", url, true);
        reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.onreadystatechange = function() {
                if (reqObj.readyState == 4 && reqObj.status == 200) {
                        $(reqObj.containerId).html(reqObj.responseText);
                }
                else{
                        var msg = fileName + ' does not exist!';
                        var table = '<table width=100%>' +
                                '<tr height=400><td style="color:red;" align=center> ' + msg + '</td></tr>' +
                                '</table>';
                        $(reqObj.containerId).html(table);
                }
        };
        reqObj.send();
}

//////////////////////////////////
function setReadmeContent(fileName, containerId){

        var url = htmlRoot + '/' + fileName;
        var reqObj = new XMLHttpRequest();
        reqObj.containerId = containerId;
        reqObj.open("GET", url, true);
        reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.onreadystatechange = function() {
                if (reqObj.readyState == 4 && reqObj.status == 200) {
                        $(reqObj.containerId).html('<pre>'+reqObj.responseText + '</pre>');
                }
                else{
                        var msg = fileName + ' does not exist!';
                        var table = '<table width=100%>' +
                                '<tr height=400><td style="color:red;" align=center> ' + msg + '</td></tr>' +
                                '</table>';
                        $(reqObj.containerId).html(table);
                }
        };
        reqObj.send();
}








///////////////////////
function getInputElement(emName, emClass, emValue, emObj){

	emValue = (emValue == 'None' ? '' : emValue); 
    	var elm = '';
	if (emObj.type == 'textarea'){
		elm += '<textarea name="'+emName+' class="'+emClass+'" rows="'+ emObj.rows + 
				'" cols="'+ emObj.cols +'" style="'
		elm +=  emObj.style +'">' + emValue+'</textarea>';
    	}
	else if (emObj.type == 'select'){
		var parts1 = emObj.list.split(",");
		elm += '<select name="'+emName+'" class="'+emClass+'" style="'+emObj.style+'">';
		for (var i=0; i < parts1.length; i++){
			var parts2 = parts1[i].split("=");
			var s = (parts2[0] == emValue ? 'selected' : '');
			elm += '<option value="'+parts2[0]+'" '+s+'>'+parts2[1]+'</option>';
		}
		elm += '</select>';
	}
	else if (emObj.type == 'checkbox'){
		var s = (emValue == 1 ? 'checked' : '');
		elm += '<input type="'+emObj.type+'" name="'+emName+'" '+s+' style="' +
                                        emObj.style+'" class="'+emClass+'" >';
	}
	else{
		elm += '<input type="'+emObj.type+'" name="'+emName+'" value="'+emValue+'" style="' + 
					emObj.style+'" class="'+emClass+'" >';
		
		
	}
	return elm;

}


///////////////////////////////////////////////
function rndrDataSummary(jsonObj, emId){

	var numOfRows = jsonObj.length - 1;

        var table = '<table style="font-size:13px;"  border=0>';
	table += '<tr><td style="font-style:italic;">Number of rows</td><td>: '+ numOfRows +'</td></tr>';
	table += '<tr><td style="font-style:italic;">Number of columns</td><td>: '+jsonObj[0].length+'</td></tr>';
        table += '</table>';
        $(emId).html(table);
        return
}



/////////////////////////////////////////////////////////////////////////////////////
function rndrTable(jsonObj, emId){


	batchCount = parseInt(jsonObj.length/batchSize) + 1;
	var batchInfo = currentBatch + ' of ' + batchCount;
	var navBtns = getBatchingBtns(batchInfo);

	var start = (currentBatch-1)*batchSize + 1;
        var end = start + batchSize;
        end = (end > batchSize*(batchCount-1) ? jsonObj.length : end);

	 
	var url1 = htmlRoot + '/csv/'+datasetName
	var downloadLink1 = '<a href="'+url1+'"  download="'+datasetName+'">Download table in CSV format</a>';
	var url2 = htmlRoot + '/csv/'+readMeFile
	var downloadLink2 = '<a href="'+url2+'" target=_>View README File</a>';
	var downloadLinks = downloadLink1 + ' | ' + downloadLink2;

 
        if (jsonObj.length == 0){
		$(emId).html('<table width=90% height=400><tr><td valign=middle align=center>' +
                        'Sorry, your search did not return any result.' +
                        '</td></tr></table>');
		return;
        }
	var navTable = '<table style="font-size:13px;" width=100% border=0>';
	navTable += '<tr height=25><td>'+downloadLinks+'</td><td align=right>'+navBtns+'</td></tr>';
       	navTable += '</table>'; 
	var table = '<table style="font-size:13px;" width=100% border=0>';
	table += '<tr class=evenrow height=25>';
	for (var j=0; j < jsonObj[0].length; j++){
		table += '<td  style="padding:0 20 0 0;" nowrap>' + jsonObj[0][j] + '</td>';
	}
	table += '<td width=100% ></td>';
	table += '</tr>';
	for (var i=start; i < end; i++){
		table +=  '<tr>';
		for (var j=0; j < jsonObj[i].length; j++){
			table += '<td  style="padding:0 20 0 0;" nowrap>' + jsonObj[i][j] + '</td>';
		}
		table += '<td width=100% ></td>';
		table += '</tr>';
	}
	table += '</table>';
        
	var cn = navTable; 
	cn += '<DIV style="width:1100px;height:600px;overflow:auto;border:1px solid #eee;">'+table+'</DIV>';
	cn += '' + navTable;
	$(emId).html(cn);
        return
}





//////////////////////////////////////////
function getBatchingBtns(batchInfo){

        var style21 = 'position:absolute;height:15;bottom:1px;background:#ccc;color:#fff;text-align:center;';
        var style22 = 'position:absolute;height:13;bottom:1px;text-align:center;color:#777;font-size:11px;';
        var btns = '<a id=start class=batchnavlink href=""> << </a>' +
                        '&nbsp;&nbsp;<a id=prev class=batchnavlink href=""> < </a>' +
                        '&nbsp;&nbsp;page '+batchInfo +
                        '&nbsp;&nbsp;<a id=next class=batchnavlink href=""> > </a>' +
                        '&nbsp;&nbsp;<a id=end class=batchnavlink href=""> >> </a>';
        return btns;
}



///////////////////////////////
function parseCSV(str) {
    var arr = [];
    var quote = false;  // true means we're inside a quoted field

    // iterate over each character, keep track of current row and column (of the returned array)
    for (var row = col = c = 0; c < str.length; c++) {
        var cc = str[c], nc = str[c+1];        // current character, next character
        arr[row] = arr[row] || [];             // create a new row if necessary
        arr[row][col] = arr[row][col] || '';   // create a new column (start with empty string) if necessary

        // If the current character is a quotation mark, and we're inside a
        // quoted field, and the next character is also a quotation mark,
        // add a quotation mark to the current column and skip the next character
        if (cc == '"' && quote && nc == '"') { arr[row][col] += cc; ++c; continue; }  

        // If it's just one quotation mark, begin/end quoted field
        if (cc == '"') { quote = !quote; continue; }

        // If it's a comma and we're not in a quoted field, move on to the next column
        if (cc == ',' && !quote) { ++col; continue; }

        // If it's a newline and we're not in a quoted field, move on to the next
        // row and move to column 0 of that new row
        if (cc == '\n' && !quote) { ++row; col = 0; continue; }

        // Otherwise, append the current character to the current column
        arr[row][col] += cc;
    }
    return arr;
}

