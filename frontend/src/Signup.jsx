import { useState } from "react";

export default function Signup ({onSignup}) {

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");

    

  async function loadWarehouse() {
    try {

      const url = `http://localhost:8000/auth/signup`;

      const body = {
        name: name,
        email: email,
        phone: phone,
        username: username,
        password: password
      }
      // console.log(url);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      
      const rawData = await response.json();
      console.log(rawData);
      
    } catch (err) {
      console.log(err);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    setError("");
    
    if (!email || !password) {
      setError("Please enter required fields.");
      return;
    }

    // Connect your real authentication service here.
    loadWarehouse();
  }

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Welcome!</h1>
        <p>Enter credientals to create an account.</p>

        <label htmlFor="name">Name</label>
        <input
          id="text"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label htmlFor="phone">Phone</label>
        <input
          id="phone"
          type="number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
        />

        <label htmlFor="phone">Username</label>
        <input
          id="username"
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

        <button type="submit">Log in</button>
      </form>
    </div>
  );

}