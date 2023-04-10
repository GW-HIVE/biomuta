import $ from "jquery";
import React from 'react';
import { Link } from "react-router-dom";




export function verifyReqObj (reqObj, fieldDef){
    var errorList = [];
    for (var f in fieldDef){
      if(!(f in reqObj) === true){
          errorList.push(<li>field "{f}" missing in request</li>);
      }
      else if (reqObj[f].toString() === "" ){
          errorList.push(<li key={"error_in_" + f}>field "{f}" cannot be empty value</li>);
      }
      else if (typeof(reqObj[f]) !== fieldDef[f]["emtype"] ){
        errorList.push(<li>field "{f}" type mismatch</li>);
      }
    }
    if (errorList.length === 0){
        return errorList;
    }
    console.log(errorList);
    return (<ul> {errorList} </ul>);
}

export function getStarList(starCount){

  var starList = [];
  for (var j =1; j <= 5; j++){
    var fg = (j <= starCount ? "#F5B041" : "#cccccc");
    var s = {cursor:"pointer",marginRight:"1px",fontSize:"15px", color:fg};
    starList.push(<i key={"s_"+j} className="material-icons" style={s}>star </i>)
  }
  return starList;
}


export function filterObjectList(objList, filterList) {

    var retObj = {filterinfo:{}, passedobjlist:[]};
    for (var i in objList) {
      var obj = objList[i];
      var passCount = 0;
      for (var name in obj.categories) {
        if (["tags","protein"].indexOf(name) !== -1){
          continue;
        }
        var value = obj.categories[name].toLowerCase(); 
        var combo = name + "|" + value;
        if (!(name in retObj.filterinfo)) {
            retObj.filterinfo[name] = {};
        }
        if(true){
            if (!(value in retObj.filterinfo[name])){
              retObj.filterinfo[name][value] = 1;
            }
            else{
              retObj.filterinfo[name][value] += 1;
            }
        }
        if (filterList.indexOf(combo) !== -1) {
          passCount += 1;
        }
      }
      //if (passCount === this.state.filterlist.length){
      if (filterList.length > 0) {
        if (passCount > 0) {
            retObj.passedobjlist.push(obj);
        }
      } else {
        retObj.passedobjlist.push(obj);
      }
    }

    return retObj;
}



export function shortText(txt, txtLen) {
  var shortText = "";
  var parts = txt.split(" ");
  for (var j in parts) {
    if (shortText.length < txtLen) {
      shortText += parts[j] + " ";
    } else {
      shortText += " ...";
      break;
    }
  }
  return shortText;
}



export function rndrSearchResults(objList, startIdx, endIdx) {

  
  if (objList.length === 0){
    return (
    <div className="row" style={{color:"red", padding:"0px 0px 100px 20px"}}>
      No results found!
      </div>);
  }

  var bcoPrefix = 'GLYG_';
  var dsPrefix = 'DS_';

  var cardList = [];
  for (var i=startIdx - 1; i <= endIdx -1;  i++){
    var obj = objList[i];
    
    var moleculeType = ("molecule" in obj["categories"] ? obj["categories"]["molecule"] : "");
    var speciesType = ("species" in obj["categories"] ? obj["categories"]["species"] : "");
    var fileType = ("file_type" in obj["categories"] ? obj["categories"]["file_type"] : "");
    var statusType = ("status" in obj["categories"] ? obj["categories"]["status"] : "");

    var objId = bcoPrefix + "0000".substring(0, 10 - String(obj["bcoid"]).length) + String(obj["_id"]);
    objId = obj["bcoid"].replace(bcoPrefix, dsPrefix);
    var titleText = statusType + ' ' + moleculeType.toLowerCase();
    titleText += ' dataset ' + objId + ' in ';
    titleText += fileType.toUpperCase() + ' format.';
    titleText += ' [' + speciesType + ']';

    var imgCn = (
      <div className="leftblock" style={{width:"50%", margin:"20px 25% 0px 25%"}}>     
        <img className="card-img-top" src={"/imglib/" + obj.iconfilename}/>
      </div>
    );
    if ("minitable" in obj){
      imgCn = (
        <div className="leftblock" style={{width:"80%", margin:"20px 10% 0px 10%"}}>     
          {rndrMiniTable(obj.minitable)}
        </div>
      );
    }

    cardList.push(
      <div className="col-md-4">
        <div className="card mb-4 box-shadow" style={{minWidth:"350px"}}>
            <div className="leftblock" 
              style={{width:"90%", textAlign:"center",  fontSize:"15px", margin:"20px 5% 0px 5%"}}>
              {titleText}
            </div>
            <div className="leftblock" 
              style={{width:"90%", textAlign:"center", margin:"20px 5% 0px 5%"}}>
              <Link className="reglink" to={objId} style={{fontWeight:"bold"}}>
                {obj.title}
              </Link>
            </div>
            {imgCn}
            <div className="card-body">
              <p className="card-text" style={{textAlign:"center"}}>{shortText(obj.description, 900)}</p>
                <div className="leftblock" 
                style={{width:"100%",textAlign:"center", margin:"20px 0px 20px 0px"}}>
                  <Link className="reglink" to={objId}>
                    View Details
                  </Link> 
                </div>
                
            </div>
          </div>
        </div>
    );
  }
  return (<div className="row">{cardList}</div>);
}



export function sortReleaseList(tmpList, reversedFlag){        

    var factorList = [10000, 1000, 1];
    var relDict = {};
    for (var i in tmpList){
        var rel = tmpList[i]
        var parts = (rel.indexOf(".") !== -1 ? rel.split(".") : rel.split("_"));
        var ordr = 0;
        for (var j in parts){
            ordr += factorList[j]*parseInt(parts[j]);
        }
        relDict[ordr] = rel;
    }

    var releaseList = [];
    var keyList = Object.keys(relDict).sort().reverse();
    for (var i in keyList){
        var ordr = keyList[i];
        releaseList.push(relDict[ordr]);
    }
    
    return releaseList;

}

export function rndrMiniTable(inObj){

  var s = "";
  var rowList = [];
  var cellList = [];
  for (var j in inObj["headers"]){
    s = {textAlign:"center",fontWeight:"bold",padding:"5px 0px 0px 0px", border:"1px solid #ccc"};
    cellList.push(<td key={"cell_"+j} style={s}>{inObj["headers"][j]}</td>);
  }
  rowList.push(<tr style={{height:"30px"}}>{cellList}</tr>);
  for (var i =0; i < inObj["content"].length; i ++){
    cellList = [];
    for (var j in inObj["content"][i]){
      s = {textAlign:"center",padding:"5px 0px 0px 0px", border:"1px solid #ccc"};
      cellList.push(<td key={"cell_"+i+j} style={s}>{inObj["content"][i][j]}</td>);
    }
    rowList.push(<tr key={"row_"+i} style={{height:"30px"}}>{cellList}</tr>);
  }
  s = {width:"100%",fontSize:"16px",border:"1px solid #ccc"};
  return (
    <table style={s} align="center" cellSpacing="1">
      <tbody>{rowList}</tbody>
    </table>
  );
}


