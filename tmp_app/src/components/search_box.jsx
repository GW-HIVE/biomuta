import React, { Component } from "react";
import Paper from '@material-ui/core/Paper';
import InputBase from '@material-ui/core/InputBase';


class Searchbox extends Component {
  
  render() {

    var sList = [
      {width:"100%", background:"#eee", "padding":"30px", margin:"0px 0px 40px 0px"},
      {width:"100%", background:"#eee", fontSize:"24px", margin:"0px 0px 10px 0px"},
      {width:"80%", background:"#eee"},
      {width:"10%", background:"#eee"}
    ];
    return (
        <div className="leftblock" style={sList[0]}>
          <div className="leftblock moduletitle" style={sList[1]}>
            BioMuta - single-nucleotide variations (SNVs) in cancer	
          </div>
          <div className="leftblock" style={sList[2]}>
            <input type="text" className="form-control" defaultValue="P01116"/>      
          </div>
          <div className="leftblock" style={sList[3]}>
            <button type="button" className="btn btn-light" onClick={this.props.onclick}>Search</button>
          </div>
        </div>
    );
  }
}

export default Searchbox;
