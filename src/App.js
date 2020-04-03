import React, { Component } from "react";
import { authEndpoint, clientId, redirectUri, scopes } from "./config";
import hash from "./hash";
import Player from "./Player";
import logo from "./logo.svg";
import "./App.css";

//TODO in the future i may come back and use this wrapper to the spotify API
//var Spotify = require('spotify-web-api-js');
//var s = new Spotify();

class App extends Component {
  constructor() {
    super();
    this.state = {
      token: null,
      item: {
        album: {
          images: [{ url: "" }]
        },
        name: "",
        artists: [{ name: "" }],
        duration_ms: 0
      },
      is_playing: "Paused",
      progress_ms: 0
    };
    //this.spotifyApi = new SpotifyWebApi(); //wrapper spotify API. May come back to this
    this.getCurrentlyPlaying = this.getCurrentlyPlaying.bind(this);
  }
  componentDidMount() {
    //set the spotify user token
    let _token = hash.access_token;

    if (_token) {
      this.setState({
        token: _token
      });

      //this.spotifyApi.setAccessToken(_token); //TODO in the future may come back and use this wrapper lib for spotify calls
      this.getCurrentlyPlaying(_token);

    }
  }

  //this one seems to work but in the future i want to try to use the spotify-api wrapper functions with preset token
  getCurrentlyPlaying(token) {
    fetch('https://api.spotify.com/v1/me/player', { 
      method: 'get', 
      headers: new Headers({
        'Authorization': "Bearer " + token, 
      })
    })
    .then((response) => {
       console.log(response);
       return response.json();
    })
    .then((data) => {
      console.log(data);

      this.setState({
        item: data.item,
        is_playing: data.is_playing,
        progress_ms: data.progress_ms,
      });
    })
    .catch((error) => {
      console.log(error);
    });
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          {!this.state.token && (
            <a
              className="btn btn--loginApp-link"
              href={`${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join(
                "%20"
              )}&response_type=token&show_dialog=true`}
            >
              Login to Spotify
            </a>
          )}
          {this.state.token && (
            <Player
              item={this.state.item}
              is_playing={this.state.is_playing}
              progress_ms={this.progress_ms}
            />
          )}
        </header>
      </div>
    );
  }
}

export default App;
