import React, { Component } from "react";
import Searchbox from "./search_box";
import Resultfilter from "./result_filter";
import { filterObjectList, rndrSearchResults} from './util';
import Paginator from "./paginator";
import * as LocalConfig from "./local_config";
import Loadingicon from "./loading_icon";
import Alertdialog from './dialogbox';
import $ from "jquery";


class SearchResults extends Component {  
  
  state = {
    filterlist: [],
    pageIdx:1,
    pageBatchSize:5,
    pageStartIdx:1,
    pageEndIdx:5,
    dialog:{
      status:false, 
      msg:""
    }
  };

  componentDidMount() {
    this.handleSearch();
  }


  handleDialogClose = () => {
    var tmpState = this.state;
    tmpState.dialog.status = false;
    this.setState(tmpState);
  }

  
  handleKeyPress = (e) => {
    if(e.key === "Enter"){
      e.preventDefault();
      this.handleSearch();
    }
  }
 

   handleSearch = () => {
    var queryValue = $("#query").val();
    queryValue = (queryValue === undefined ? "" : queryValue);
    var reqObj = {query:queryValue};

    this.handleFilterReset();

    const requestOptions = { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqObj)
    };
    const svcUrl = LocalConfig.apiHash.dataset_search;

    fetch(svcUrl, requestOptions)
      .then((res) => res.json())
      .then(
        (result) => {
          var tmpState = this.state;
          tmpState.response = result;
          tmpState.isLoaded = true;          
          if (tmpState.response.status === 0){
            tmpState.dialog.status = true;
            tmpState.dialog.msg = tmpState.response.error;
          }
          this.setState(tmpState);
          //console.log("Request:",svcUrl);
          console.log("Ajax response:", result);
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      );
  }


  handleFilterReset = () => {
    $('input[name="filtervalue"]:checkbox:checked').prop("checked", false);
    this.setState({ filterlist: [] });
  };

  handleFilterApply = () => {
    $("#filtercn").toggle();
    var tmpList = $('input[name="filtervalue"]:checkbox:checked')
      .map(function () {
        return $(this).val();
      })
      .get(); // <----
    
    this.setState({ filterlist: tmpList });
    
  };

  handleFilterIcon = () => {
    $("#filtercn").toggle();
  };

  



  handlePaginatorClick = (e) => {
    if(e.target.id.indexOf("_disabled") !== -1){
      return;
    }
    var pageIdx = parseInt(e.target.id.split("_")[2]);
    var tmpState = this.state;
    if(e.target.id.indexOf("_next_") !== -1){
      tmpState.pageStartIdx = tmpState.pageEndIdx + 1;
      tmpState.pageEndIdx += tmpState.pageBatchSize;
      pageIdx = tmpState.pageStartIdx;
    }
    else if(e.target.id.indexOf("_prev_") !== -1){
      tmpState.pageStartIdx -= tmpState.pageBatchSize;
      tmpState.pageEndIdx = tmpState.pageStartIdx + tmpState.pageBatchSize - 1;
      pageIdx = tmpState.pageStartIdx;
    }
    tmpState.pageIdx = pageIdx;
    this.setState(tmpState);

  }

  render() {
  
    if (!("response" in this.state)){
      return <Loadingicon/>
    }

    const objList = (this.state.response.recordlist !== undefined ? this.state.response.recordlist : []);
    
    //var filObj = filterObjectList(objList, []);
    var filObj = filterObjectList(objList, this.state.filterlist);
    var filterInfo = filObj.filterinfo;
    var passedObjList = filObj.passedobjlist;
    var passedCount = passedObjList.length;

    var batchSize = 20;
    var pageCount = parseInt(passedObjList.length/batchSize) + 1;
    pageCount = (objList.length > 0 ? pageCount : 0);


    var startIdx = batchSize * (parseInt(this.state.pageIdx) - 1) + 1;
    var endIdx = startIdx + batchSize;
    endIdx = (endIdx > passedCount ? passedCount : endIdx);

    var filterHideFlag = (objList.length > 0 ? "block" : "none");

    var tmpList = [];
    for (var i in this.state.filterlist){
        var h = "<b>" + this.state.filterlist[i].split("|")[1] + "</b>";
        tmpList.push(h);
    }
    var resultSummary = "<b>" + passedObjList.length + "</b> results found";
    resultSummary += (tmpList.length > 0 ? ", after fileters: '" + tmpList.join("', '") + "'." : "."); 

   //return (<div>{this.state.pageStartIdx} {this.state.pageEndIdx}</div>);

    return (
      <div>
      <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>

      <div className="pagecn">
        
        <div className="leftblock" style={{width:"100%", margin:"20px 0px 0px 0px"}}>
          <Searchbox onSearch={this.handleSearch} onKeyPress={this.handleKeyPress}/>
        </div>
        <div className="leftblock" style={{width:"100%", margin:"5px 0px 0px 0px",display:filterHideFlag}}>
          <Resultfilter
            filterinfo={filterInfo}
            resultcount={objList.length}
            resultSummary={resultSummary}
            handleSearchIcon={this.handleSearchIcon}
            handleFilterIcon={this.handleFilterIcon}
            handleFilterApply={this.handleFilterApply}
            handleFilterReset={this.handleFilterReset}
          />
        </div>
      
        <div className="leftblock" 
          style={{width:"100%", margin:"60px 0px 0px 0px",
          borderBottom:"1px solid #ccc"}}>
          <Paginator 
            paginatorId={"top"}
            pageCount={pageCount}
            pageStartIdx={this.state.pageStartIdx}
            pageEndIdx={this.state.pageEndIdx}
            onClick={this.handlePaginatorClick}
          />
        </div>

        <div className="leftblock" 
          style={{margin:"20px 0px 0px 0px"}}>
          {rndrSearchResults(passedObjList, startIdx, endIdx)}
        </div>

        <div className="leftblock" 
          style={{width:"100%", 
          margin:"0px 0px 0px 0px",
          padding:"5px 0px 0px 0px",
          borderTop:"1px solid #ccc"}}>
          <Paginator 
            paginatorId={"bottom"}
            pageCount={pageCount}
            pageStartIdx={this.state.pageStartIdx}
            pageEndIdx={this.state.pageEndIdx}
            onClick={this.handlePaginatorClick}
          />
        </div>

      </div>
      
      </div>
    );
  }
}

export default SearchResults;
