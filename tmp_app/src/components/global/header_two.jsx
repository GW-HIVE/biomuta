import React, { Component } from "react";
import Loadingicon from "./loading_icon";
import {Container,Navbar, Nav, NavItem, NavDropdown, MenuItem }   from 'react-bootstrap';
import $ from "jquery";



class Backendheader extends Component {

  
  getNavLinks = () => {

    var navObjList = [];
    for (var i in this.props.config.menu){
        var obj = this.props.config.menu[i];
        if (obj.pageid === this.props.pageId){
          navObjList = navObjList.concat(obj.nav);
          navObjList = navObjList.concat({"pageid":obj.pageid, "url":obj.url, "label":obj.label});
          break;
        }
        for (var j in obj.children){
          var o = obj.children[j];
          if (o.pageid === this.props.pageId){
            navObjList = navObjList.concat(o.nav);
            navObjList = navObjList.concat({"pageid":o.pageid, "url":o.url, "label":o.label});
            break;
          }
        }
    }


    var linkList = [];
    for (var i in navObjList){
        var obj = navObjList[i];
        if (i == 0){
          linkList.push(<a className="reglinkblue" href={obj.url}>{obj.label}</a>); 
        }
        else{
          linkList.push(<span> / </span>);
          linkList.push(<a className="reglinkblue" href={obj.url}>{obj.label}</a>);
      }
    }
    return linkList;

  }

  render() {

    var navLinks = this.getNavLinks();

    var sList = [
      {width:"80%", margin:"40px 10% 0px 10%", borderBottom:"1px solid #ddd"},
      {width:"60%", color:"#033C5A", fontSize:"30px",fontWeight:"bold"},
      {width:"60%", fontSize:"12px",fontWeight:"normal"},
      {width:"40%", color:"#033C5A", fontSize:"14px", textAlign:"right"},
      {width:"60px"}
    ];
    return (
      <div className="leftblock" style={sList[0]}>
        <div class="leftblock" style={sList[1]}> 
          The HIVE Lab<br/>
          <div className="leftblock" style={sList[2]}>
            {navLinks}
          </div>
        </div>
        <div class="leftblock" style={sList[3]}> 
          <img alt="" src={'/imglib/hive_logo.png'} style={sList[4]}/> <br/>
          High-performance Integrated Virtual Environment
        </div>
      </div>
    );

  }
}





export default Backendheader;
