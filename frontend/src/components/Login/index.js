import React, { Component } from 'react';

class Login extends Component {
  constructor(props) {
    super(props);
    this.state = {
      input: ""
    };
  }

  handleInputChange = (event) => {
    this.setState({ input: event.target.value });
  };

  handleLogin = () => {
    const { input } = this.state;
    const { setUsername } = this.props;
    if (input.trim()) {
      setUsername(input.trim());
    } else {
      alert("Please enter a username.");
    }
  };

  render() {
    const { input } = this.state;

    return (
      <div className="login-container">
        <h1>Login</h1>
        <input
          type="text"
          placeholder="Enter your username"
          value={input}
          onChange={this.handleInputChange}
        />
        <button onClick={this.handleLogin}>Login</button>
      </div>
    );
  }
}

export default Login;