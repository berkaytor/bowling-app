import React, { Component } from 'react';
import './App.css';
import Game from './components/Game';
import Login from './components/Login';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      game: -1,
      error: null
    };
  }

  setUsername = async (username) => {
    try {
      const response = await fetch('http://localhost:8000/games', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: username })
      });

      if (response.ok) {
        const data = await response.json();
        this.setState({ username, error: null, game: data.game.id });
      } else {
        this.setState({ error: "Failed to login. Please try again." });
      }
    } catch (error) {
      console.error("Error:", error);
      this.setState({ error: "An error occurred. Please try again." });
    }
  };

  render() {
    const { username, error, game } = this.state;

    return (
      <div className="App">
        <header className="App-header">
          <h1 className="Title">Bowling Score Tracker</h1>
        </header>
        
        {error && <p className="Error">{error}</p>}
        {username ? (
          <div>
            <p className="Intro">
              Enter your score in after each bowl
            </p>
            <p className="Intro">
              {username} in Game #{game}
            </p>            
            <Game game_id={game}/>
          </div>
        ) : (
          <Login setUsername={this.setUsername} />
        )}
      </div>
    );
  }
}

export default App;