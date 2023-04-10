import React, { Component } from "react";

class Loadingicon extends Component {
  
  render() {
    const s = {
      width:"40%",
      margin:"40px 30% 40px 30%"
    }
    return (
      <img alt="" src={process.env.PUBLIC_URL + '/imglib/loading.gif'} style={s} /> 
      );
  }
}

export default Loadingicon;
