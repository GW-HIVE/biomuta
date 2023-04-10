import React, { Component } from "react";
import { SocialIcon } from 'react-social-icons';


class Footer extends Component {
  render() {
    return (
    <section className="border">
      <footer className="text-center text-lg-start bg-light text-muted">
        <section className="globalfooter" >
          <div className="leftblock" style={{width:"24%",margin:"30px 38% 20px 38%"}}>
            <img alt="" src={process.env.PUBLIC_URL + '/imglib/smhs_full.png'}
            style={{width:"100%"}}/>
          </div>
      </section>

    </footer>
  </section>

    );
  }
}

export default Footer;
