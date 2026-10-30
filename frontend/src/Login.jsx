
import { useState } from "react";

export default function Login({ setToken, setSigningUp }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onLogin() {
    const url = `http://localhost:8000/auth/login`

    const body = {
      username: username,
      password: password
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
    const data = await response.json();
    console.log(data)
    setToken(data.token)
  }
  
  function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!username || !password) {
      setError("Please enter your email and password.");
      return;
    }
    // Connect your real authentication service here.
    onLogin();

  }

  function onRegister() {
    setSigningUp(true);
  }

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Welcome back</h1>
        <p>Sign in to your account</p>

        <label htmlFor="username">Username</label>
        <input
          id="text"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p role="alert">{error}</p>}

        <button type="submit">Log In</button>
      </form>
      <button onClick={() => onRegister()} type="submit">Create an Account</button>
    </div>
  );
}
