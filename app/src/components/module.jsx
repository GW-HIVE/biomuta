import React, { Component } from "react";
import { Markup } from 'interweave';
import $ from "jquery";

import Headertwo from "./global/header_two";
import Alertdialog from './global/dialogbox';
import Loadingicon from "./global/loading_icon";

import Searchbox from "./search_box";


class Module extends Component {
  
  state = {
    html:"",
    cn:"",
    isLoaded:false,
    resflag:0,
    dialog:{
      status:false, 
      msg:""
    }
  };

   componentDidMount() {
    var reqObj = {};
    const requestOptions = {
      method: 'GET', headers: { 'Content-Type': 'text/html' }
    };
    const svcUrl = "/html/page."+this.props.pageId +".html";

    fetch(svcUrl, requestOptions).then((res) => res.text()).then(
        (result) => {
          console.log("Result:",result);
          var tmpState = this.state;
          tmpState.isLoaded = true;
          if(result.indexOf("!DOCTYPE") !== -1){
            tmpState.dialog.status = true;
            tmpState.dialog.msg = "Page=" + this.props.pageId + " does NOT exist!";
          }
          else{
            //tmpState.html = result;
            tmpState.cn = <Markup content={result}/>;
          }
          this.setState(tmpState);
        },
        (error) => {
          console.log("Error:", error);
        }
    );
  }

  

  handleDialogClose = () => {
    var tmpState = this.state;
    tmpState.dialog.status = false;
    this.setState(tmpState);
    window.location.href = "/";
  }

  handleSearch = () =>{
    var tmpState = this.state;
    tmpState.cn = "Hi tehre";
    this.setState(tmpState);
  }

  render() {

    if (this.state.isLoaded === false){
      return <Loadingicon/>
    }
    

    return (
      <div>
        <Headertwo config={this.props.config} pageId={this.props.pageId}/>
        <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>
        <div className="pagecnwrapper">
          <Searchbox onclick={this.handleSearch}/>
          {this.state.cn}
        </div>
      </div>
    );
  }
}

export default Module;
