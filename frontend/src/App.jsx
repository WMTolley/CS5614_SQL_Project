
import { useEffect, useState } from "react";
import "./App.css";
import Login from "./Login";
import Signup from "./Signup";

const tabs = ["Warehouses", "Warehouse Search", "Insert", "Insert Warehouse", "Update", "Delete", "Reset Password", "Admin Signup"];
const permissions = [1, 1, 3, 4, 4, 4, 1, -1]
function App() {


  const [token, setToken] = useState("");
  const [level, setLevel] = useState(-2); // -1 for admin, positive numbers for employees.
  const [signingUp, setSigningUp] = useState(false);

  console.log("App rendered. Token:", token);


  return (
    <div>
      {!token && !signingUp && <Login setToken={setToken} setSigningUp={setSigningUp} setLevel={setLevel}/>}
      {!token && signingUp && <Signup setSigningUp={setSigningUp}/>}
      {token && <Main token={token} level={level} setToken={setToken}/>}
    </div>
    
  );
}

function access(index, level) {
  const permission = permissions[index]
  if (level === -1) {
    return permission === -1;
  }
  return permission <= level && permission >= 0;

}

function accessTabs(level) {
  console.log(level)
  const filteredTabs = tabs.filter((element, index, array) => {
    const acc = access(index, level);
    console.log(acc)
    return acc;
  })

  return filteredTabs;
}

function Main({token, level, setToken}) {

  const [activeTab, setActiveTab] = useState("");
  const [warehouses, setWarehouses] = useState([]);

  useEffect(() => {
    if (activeTab == "") {
      setFirstTab();
    }
    if (level !== -1) {
      loadRecords();
    }

  }, [])

  function setFirstTab() {
    const tabs = accessTabs(level);
    setActiveTab(tabs[0])
  }

  async function loadRecords() {
    try {
      const response = await fetch(
        "http://localhost:8000/read", 
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        }
        
      );

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      
      const data = await response.json();
      setWarehouses(data["public warehouses"]);
      console.log(data["public warehouses"]);
    } catch (err) {
      console.log(err);
    }
  }

  async function logout() {
    const response = await fetch(
      "http://localhost:8000/auth/logout", 
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      }
    );
    
    setToken("")
  }
  return (
  <div className="app">
      <header className="header">
        <h1>Database Manager</h1>
        <p>Manage your database records</p>
      </header>

      <nav className="tabs">
        {accessTabs(level).map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>
      <main className="content">
        {activeTab === "Warehouses" && <ReadPanel warehouses={warehouses} onRefresh={loadRecords}/>}
        {activeTab === "Warehouse Search" && <SearchPanel token={token} warehouses={warehouses} />}
        {activeTab === "Insert" && <InsertPanel token={token} warehouses={warehouses} onRefresh={loadRecords}/>}
        {activeTab === "Insert Warehouse" && <AddWarehousePanel token={token} onRefresh={loadRecords} />}
        {activeTab === "Update" && <UpdatePanel token={token} onRefresh={loadRecords}/>}
        {activeTab === "Delete" && <DeletePanel token={token} warehouses={warehouses} onRefresh={loadRecords}/>}
        {activeTab === "Reset Password" && <ResetPasswordPanel token={token}/>}
        {activeTab === "Admin Signup" && <AdminSignupPanel token={token} />}
      </main>
      <button onClick={() => logout()}>Log Out</button>
    </div>)
}

// TODO: Make these separate files
function ReadPanel({warehouses, onRefresh}) {

  const cellStyle = {
    padding: '12px',
    border: '1px solid #ddd'
  };

  return (
    <section>
      <h2>View</h2>
      <p>View warehouses.</p>
      <button onClick={() => onRefresh()}>
        Refresh
      </button>

      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <h2>Warehouses</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
              <th style={cellStyle}>ID</th>
              <th style={cellStyle}>Name</th>
              <th style={cellStyle}>ZIP Code</th>
            </tr>
          </thead>
          <tbody>
            {warehouses.map((warehouse) => (
              <tr key={warehouse[0]} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={cellStyle}><strong>{warehouse[0]}</strong></td>
                <td style={cellStyle}><strong>{warehouse[1]}</strong></td>
                <td style={cellStyle}>{warehouse[2]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </section>
  );
}

function SearchPanel({token, warehouses}) {

  const [warehouseData, setWarehouseData] = useState([]);
  const [query, setQuery] = useState("");

  const cellStyle = {
    padding: '12px',
    border: '1px solid #ddd'
  };


  async function loadWarehouse() {
    try {

      const uriQuery = encodeURIComponent(query);
      const url = `http://localhost:8000/search?name=${uriQuery}`;
      console.log(url);
      const response = await fetch(url,
        {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      
      const rawData = await response.json();
      console.log(rawData);
      let data = [];

      for (const [key, value] of Object.entries(rawData.Items)) {
        if (value === null) continue;
        data.push({
          name: key,
          ids: value.toString(),
          quantity: value.length
        })
      }
      
      setWarehouseData(data);
      console.log(data);
    } catch (err) {
      console.log(err);
    }
  }
  

  return (
    <section>
      <h2>Search Items By Warehouse</h2>
      <p>Find items in the keyworded warehouse.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label>
          Select warehouse:
          <select 
            value={query} 
            onChange={(e) => setQuery(e.target.value)}
          >
            <option value="" disabled>Select...</option>
            {warehouses.map((warehouse) => (
              <option value={warehouse[1]}>{warehouse[1]}</option>
            ))}
          </select>
        </label>
        <button onClick={() => loadWarehouse()} type="submit">Search</button>
      </form>

      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <h2>Items</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
              <th style={cellStyle}>Name</th>
              <th style={cellStyle}>Quantity</th>
              <th style={cellStyle}>IDs</th>
            </tr>
          </thead>
          <tbody>
            {warehouseData.map((user) => (
              <tr key={user.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={cellStyle}><strong>{user.name}</strong></td>
                <td style={cellStyle}><strong>{user.quantity}</strong></td>
                <td style={cellStyle}>{user.ids}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function InsertPanel({token, warehouses, onRefresh}) {

  const [itemName, setItemName] = useState("");
  const [itemSerial, setItemSerial] = useState("");
  const [itemWarehouse, setItemWarehouse] = useState(1);

  const [message, setMessage] = useState("")

  async function addItem() {
    try {

      console.log(itemName);

      const url = `http://localhost:8000/insert`;

      const body = {
        name: itemName,
        serial_number: itemSerial,
        warehouse_id: itemWarehouse
      }

      const response = await fetch(url, {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const rawData = await response.json();
      setMessage(rawData.message)
      console.log(rawData)
    }
    catch (err) {
      console.log(err);
    }
  }


  return (
    <section>
      <h2>Insert Item</h2>
      <p>Add a new item to the specified warehouse.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="new-name" >Item Name</label>
        <input id="new-name" type="text" placeholder="Enter name" onChange={(e) => setItemName(e.target.value)}/>

        <label htmlFor="new-serial">Serial Number</label>
        <input id="new-serial" type="text" placeholder="Enter serial number" onChange={(e) => setItemSerial(e.target.value)}/>

        <label htmlFor="new-id">Warehouse</label>
        <label>
          Select warehouse:
          <select 
            value={itemWarehouse} 
            onChange={(e) => setItemWarehouse(e.target.value)}
          >
            <option value="" disabled>Select...</option>
            {warehouses.map((warehouse) => (
              <option value={warehouse[0]}>{warehouse[1]}</option>
            ))}
          </select>
        </label>

        <button type="submit" onClick={() => addItem()}>Insert Item</button>
      </form>
      {message}
    </section>
  );
}

function AddWarehousePanel({token, onRefresh}) {
  
  const [warehouseName, setWarehouseName] = useState("");
  const [message, setMessage] = useState("");

    async function addWarehouse() {
    try {
      const url = `http://localhost:8000/insert_warehouse`;

      const body = {
        name: warehouseName
      }

      const response = await fetch(url, {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)})

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const rawData = await response.json();

      console.log(rawData)
      setMessage(rawData.message)

      onRefresh();
    }
    catch (err) {
      console.log(err);
    }
  }

  return (
    <section>
      <h2>Insert Warehouse</h2>
      <p>Add a new blank warehouse.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="new-name" >Warehouse Name</label>
        <input id="new-name" type="text" placeholder="Enter name" onChange={(e) => setWarehouseName(e.target.value)}/>

        <button type="submit" onClick={() => addWarehouse()}>Insert Warehouse</button>
      </form>
      {message}
    </section>
  )
}

function UpdatePanel({token, onRefresh}) {

  const [warehouseID, setWarehouseID] = useState("")
  const [privacy, setPrivacy] = useState("")
  const [message, setMessage] = useState("")

  async function updateWarehouse() {
    try {

      const uriID = encodeURIComponent(warehouseID);

      const url = `http://localhost:8000/update_warehouse/${uriID}`;

      const body = {
        privacy: (privacy === "public")
      }

      const response = await fetch(url, {
      method: 'PUT',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)})

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const rawData = await response.json();

      console.log(rawData)
      setMessage(rawData.message)
      onRefresh();
    }
    catch (err) {
      console.log(err);
    }
  }

  return (
    <section>
      <h2>Update Warehouse Privacy</h2>
      <p>Set warehouse to private or public.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="update-id">Warehouse ID</label>
        <input id="update-id" type="number" placeholder="Enter record ID" onChange={(e) => setWarehouseID(e.target.value)}/>

        <label>
          Privacy:  
          <select 
            value={privacy} 
            onChange={(e) => setPrivacy(e.target.value)}
          >
            <option value="" disabled>Select...</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </label>

        <button type="submit" onClick={() => updateWarehouse()}>Set Privacy</button>
      </form>
      {message}
    </section>
  );
}


function DeletePanel({token, warehouses, onRefresh}) {

  const [warehouseID, setWarehouseID] = useState("");
  const [message, setMessage] = useState("");

  
  async function deleteWarehouse() {
    try {

      const uriID = encodeURIComponent(warehouseID);

      const url = `http://localhost:8000/delete/${uriID}`;

      const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
      })

      if (!response.ok) {
        setMessage("Cannot delete warehouse with items.");
        return;
      }

      const rawData = await response.json();

      console.log(rawData)
      setMessage(rawData.message)
      onRefresh();
    }
    catch (err) {
      console.log(err);
    }
  }


  return (
    <section>
      <h2>Delete Warehouse</h2>
      <p>Remove an empty warehouse from the database.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="delete-id">Record ID</label>
          <select 
            value={warehouseID} 
            onChange={(e) => setWarehouseID(e.target.value)}
          >
            <option value="" disabled>Select...</option>
            {warehouses.map((warehouse) => (
              <option value={warehouse[0]}>{warehouse[1]}</option>
            ))}
          </select>
        <button className="danger" type="submit" onClick={() => deleteWarehouse()}>
          Delete Record
        </button>
      </form>
      {message}
    </section>
  );
}

function ResetPasswordPanel({token}) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  async function resetPassword() {
    try {
      const url = `http://localhost:8000/auth/change-password`;

      const body = {
        old_password: oldPassword,
        new_password: newPassword
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      })

      const rawData = await response.json();
      console.log(rawData);

    }
    catch (err) {
      console.log(err);
    }
  }

  return (
    <section>
      <h2>Update Password</h2>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="oldPassword">Old Password</label>
        <input
          id="oldPassword"
          type="password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          required
        />
        <label htmlFor="password">New Password</label>
        <input
          id="newPassword"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
      
      <button type="submit" onClick={() => resetPassword()}>
        Change Password
      </button>
    </form>
    </section>
  )
}

function AdminSignupPanel({token}) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [employeeId, setEmployeeId] = useState("")

  const [message, setMessage] = useState("")

  async function createEmployeeAccount() {
    try {
      const url = `http://localhost:8000/admin/users`

      const body = {
        username: username,
        password: password,
        employee_id: employeeId,
        is_admin: false,
        customer_id: null // perhaps change later
      };

      const response = await fetch(url, {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
      })
      
      if (!response.ok) {
        setMessage("Could not create account.");
        return;
      }
      
      const rawData = await response.json();
      console.log(rawData);
      const newMessage = 'User created with ID ' + rawData.user_id;
      setMessage(newMessage);

    }
    catch (err) {
      console.log(err);
    }
  }

  return (
    <section>
      <h2>Create User Account</h2>
      <p>Create an account for an existing employee.</p>
      <form onSubmit={(e) => e.preventDefault()}>
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
        <label htmlFor="id">Employee ID</label>
        <input
          id="text"
          type="text"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          required
        />
      
      <button type="submit" onClick={() => createEmployeeAccount()}>
        Create Account
      </button>
    </form>
    {message}
    </section>
  )
}
export default App;
