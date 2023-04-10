import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";


class Alertdialog extends Component {

  render() {
    
    return (
      <div>
        <Dialog id="popupcn" style={{border:"1px dashed red"}}
          open={this.props.dialog.status}
          onClose={this.props.onClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            {"Alert!"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              {this.props.dialog.msg}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.props.onClose} color="primary" autoFocus>
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }
}

export default Alertdialog;
