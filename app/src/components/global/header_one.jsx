import React, { Component } from "react";
import Loadingicon from "./loading_icon";
import {Container,Navbar, Nav, NavItem, NavDropdown, MenuItem }   from 'react-bootstrap';
import $ from "jquery";




class Backendheader extends Component {

  state = {
  }


  getHeaderLinks = () => {

    var linkList = [];
    for (var i in this.props.config.menu){
      var obj = this.props.config.menu[i];
      if (obj.pageid === "home"){
        continue;
      }
      if (obj.children.length === 0){
        linkList.push(
          <Nav.Link href={obj.url} className="reglinkwhite" style={{marginRight:"20px"}}>
            {obj.label}
          </Nav.Link>
        );
      }
      else{
        var drpDownItemList = [];
        for (var j in obj.children){
          var o = obj.children[j];
          drpDownItemList.push(
            <NavDropdown.Item href={o.url} className="reglinkblue">
              {o.label}
            </NavDropdown.Item>
          );
        }
        linkList.push(
          <NavDropdown  className="reglinkwhite fgtext" 
            title={<span className="my-auto reglinkwhite">{obj.label}</span>}
            id="basic-nav-dropdown"
            style={{marginRight:"20px"}}>
            {drpDownItemList}
          </NavDropdown>
        );
      }
    }
    
    return linkList;
  }




  render() {

    
    var headerLinks = this.getHeaderLinks();

    return (
      <Navbar collapseOnSelect expand="lg" variant="dark" className="globalheader">
      <Container >
        <Navbar.Brand href="#home" className="navbarbrand" >
        <a href="/z-dashboard">
        <div className="globalheader_logo">
          <div className="globalheader_logo_img">
             <img alt="" src={process.env.PUBLIC_URL + '/imglib/gw_logo.png'}
                style={{width:"60px"}} />
            <img alt="" src={process.env.PUBLIC_URL + '/imglib/smhs_logo.png'}
                style={{width:"180px", margin:"0px 0px 0px 10px"}} />
          </div>
        </div>
        </a>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse id="responsive-navbar-nav" 
          style={{ paddingLeft:"20px", border:"0px solid green"}}>
          <Nav className="ms-auto reglinkwhite">{headerLinks}</Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
    );

  }
}





export default Backendheader;
