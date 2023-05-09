import React from 'react';
class Square extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        value: "statebtn",
        some:123,
      };
      console.log('in struct')
    }

    handlerClick(){
        console.log("click..")
        this.setState({"value": "clcikbtn"})
        console.log("sprops:", this.props, this.state)
    }
  
    render() {
      return (
        <>
        
        this is a test page
        <button
          className="square"
          onClick={this.handlerClick.bind(this)}
        >
          {this.state.value}
        </button>

        </>
      );
    }
  }

export default Square