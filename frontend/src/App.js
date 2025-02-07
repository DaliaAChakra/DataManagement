import React, { useState } from "react";
import axios from "axios";
import CreateTable from "./components/CreateTable";
import ImportCSV from "./components/ImportCSV";
import "../src/styles/Login.css";
import "../src/styles/CreateTable.css";
import "../src/styles/ImportCSV.css";

const App = () => {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogin = async () => {
    setErrorMessage("");
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/token/", {
        username,
        password,
        email,
      });

      setToken(response.data.access);
      localStorage.setItem("userEmail", email);
    } catch (error) {
      console.error("Login failed", error);
      setErrorMessage("Invalid username or password. Please try again.");
    }
  };

  return (
    <div>
      {/* Login Section */}
      {!token ? (
        <div className="login-container">
          <div className="card">
            <h1 className="title">Data Management</h1>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
            <div className="form-group">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username*"
                className="input"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password*"
                className="input"
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="input"
              />
              <button onClick={handleLogin} className="login-button">
                Login
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="main-content">
          <div className="main-container">
            <div className="table-card">
              <CreateTable token={token} />
            </div>
            <div className="csv-card">
              <ImportCSV token={token} email={email} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
