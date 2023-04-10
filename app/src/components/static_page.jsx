import React, { Component } from "react";
import { Markup } from 'interweave';
import $ from "jquery";

import Headertwo from "./global/header_two";
import Alertdialog from './global/dialogbox';
import Loadingicon from "./global/loading_icon";


class StaticPage extends Component {
  
  state = {
    html:"",
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
    const svcUrl = "/biomuta/html/page."+this.props.pageId +".html";

    fetch(svcUrl, requestOptions).then((res) => res.text()).then(
        (result) => {
          //console.log("Result:",result.length);
          var tmpState = this.state;
          tmpState.isLoaded = true;
          if(result.indexOf("<biomutatag>") === -1){
            tmpState.dialog.status = true;
            tmpState.dialog.msg = "Page=" + this.props.pageId + " does NOT exist!";
          }
          else{
            tmpState.html = result.replace("<biomutatag>", "");
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



  render() {

    if (this.state.isLoaded === false){
      return <Loadingicon/>
    }


    return (
      <div>
        <Headertwo config={this.props.config} pageId={this.props.pageId}/>
        <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>
        <div className="pagecnwrapper">
          <div className="pagecn">
            <Markup content={this.state.html}/>
          </div>
          <div className="advcn">
            <img alt="" src={'/imglib/smhs_magazine.png'}/> <br/>
            <a className="reglinkblue" href="https://biochemistry.smhs.gwu.edu/">
              <br/>
              Visit the Department of Biochemistry and Molecular Medicine
            </a>
          </div>
        </div>
      </div>
    );
  }
}

export default StaticPage;
