
import { useEffect, useState } from "react";
import "./App.css";
import Login from "./Login";
import Signup from "./Signup";

const tabs = ["Warehouses", "Warehouse Search", "Insert", "Update", "Delete", "Admin Signup"];
const permissions = [1, 1, 3, 4, 4, -1]
function App() {


  const [token, setToken] = useState("");
  const [level, setLevel] = useState(-2); // -1 for admin, positive numbers for employees.
  const [signingUp, setSigningUp] = useState(false);

  console.log("App rendered. Token:", token);


  return (
    <div>
      {!token && !signingUp && <Login setToken={setToken} setSigningUp={setSigningUp} setLevel={setLevel}/>}
      {!token && signingUp && <Signup setSigningUp={setSigningUp}/>}
      {token && <Main token={token} level={level}/>}
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

function Main({token, level}) {

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
        {activeTab === "Insert" && <InsertPanel token={token} onRefresh={loadRecords}/>}
        {activeTab === "Update" && <UpdatePanel token={token} onRefresh={loadRecords}/>}
        {activeTab === "Delete" && <DeletePanel token={token} warehouses={warehouses} onRefresh={loadRecords}/>}
        {activeTab === "Admin Signup" && <AdminSignupPanel token={token} />}
      </main>
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

function InsertPanel({token, onRefresh}) {

  const [itemName, setItemName] = useState("");
  const [itemSerial, setItemSerial] = useState("");

  const [warehouseName, setWarehouseName] = useState("");
  const [message, setMessage] = useState("")

  async function addItem() {
    try {

      console.log(itemName);
      const uriName = encodeURIComponent(itemName);
      const uriSerial = encodeURIComponent(itemSerial);

      const url = `http://localhost:8000/insert`;

      const body = {
        name: itemName,
        serial_number: itemSerial,
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

  async function addWarehouse() {
    try {

      const uriName = encodeURIComponent(warehouseName);

      const url = `http://localhost:8000/insert_warehouse`;

      const body = {
        name: warehouseName
      }

      const response = await fetch(url, {
      method: 'POST',
      headers: {
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
      <h2>Insert Item</h2>
      <p>Add a new item to warehouse 1.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="new-name" >Item Name</label>
        <input id="new-name" type="text" placeholder="Enter name" onChange={(e) => setItemName(e.target.value)}/>

        <label htmlFor="new-serial">Serial Number</label>
        <input id="new-serial" type="text" placeholder="Enter serial number" onChange={(e) => setItemSerial(e.target.value)}/>

        <button type="submit" onClick={() => addItem()}>Insert Item</button>
      </form>

      <h2>Insert Warehouse</h2>
      <p>Add a new blank warehouse.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="new-name" >Warehouse Name</label>
        <input id="new-name" type="text" placeholder="Enter name" onChange={(e) => setWarehouseName(e.target.value)}/>

        <button type="submit" onClick={() => addWarehouse()}>Insert Warehouse</button>
      </form>
      {message}
    </section>
  );
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
      <p>Modify an existing record.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="update-id">Warehouse ID</label>
        <input id="update-id" type="number" placeholder="Enter record ID" onChange={(e) => setWarehouseID(e.target.value)}/>

        <label>
          Select warehouse:
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


function AdminSignupPanel({token}) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [employeeId, setEmployeeId] = useState("")

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
        <label htmlFor="id">Username</label>
        <input
          id="text"
          type="text"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          required
        />
      
      <button type="submit" onClick={() => createEmployeeAccount()}>
        Delete Record
      </button>
    </form>
    </section>
  )
}

export default App;
