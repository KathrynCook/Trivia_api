import React, { Component } from 'react';
import '../stylesheets/Header.css';

class Header extends Component {
  navTo(uri) {
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className='App-header'>
        <h1
          onClick={() => {
            this.navTo('');
          }}
        >
          Udatrivia
        </h1>
        <h2
          onClick={() => {
            this.navTo('');
          }}
        >
          Trivia Questions
        </h2>
        <h2
          onClick={() => {
            this.navTo('/add');
          }}
        >
          Add a Question
        </h2>
        <h2
          onClick={() => {
            this.navTo('/play');
          }}
        >
          Trivia Quiz
        </h2>
      </div>
    );
  }
}

export default Header;
