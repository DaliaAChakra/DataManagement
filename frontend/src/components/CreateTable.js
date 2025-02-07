import React, { useState, useEffect } from "react";
import axios from "axios";
import { MdDelete } from "react-icons/md";

const CreateTable = ({ token }) => {
  const [tableName, setTableName] = useState("");
  const [fields, setFields] = useState([
    { name: "", type: "", is_unique: false },
  ]);
  const [searchQuery, setSearchQuery] = useState("");
  const [tables, setTables] = useState([]);
  const [showAll, setShowAll] = useState(false);
  const [selectedTable, setSelectedTable] = useState(null);
  const [records, setRecords] = useState([]);
  const [newRecord, setNewRecord] = useState({});
  const [message, setMessage] = useState({ type: "", text: "" });

  const fieldTypes = ["VARCHAR(255)", "INTEGER", "DATE", "BOOLEAN"];

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/list_tables/",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTables(response.data.tables);
    } catch (error) {
      console.error("Error fetching tables:", error);
      setMessage({
        type: "error",
        text: "Error fetching tables. Please try again.",
      });
    }
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setSelectedTable(null);
  };

  const filteredTables = tables.filter((table) =>
    table.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTableClick = async (tableName) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/get_table_fields/${tableName}/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSelectedTable(response.data.fields);
    } catch (error) {
      console.error("Error fetching table fields:", error);
      setMessage({
        type: "error",
        text: "Error fetching table fields. Please try again.",
      });
    }
  };

  const handleAddField = () => {
    setFields([...fields, { name: "", type: "", is_unique: false }]);
  };

  const handleFieldChange = (index, event) => {
    const values = [...fields];
    values[index][event.target.name] = event.target.value;
    setFields(values);
  };

  const handleDeleteField = (index) => {
    const values = [...fields];
    values.splice(index, 1);
    setFields(values);
  };

  const handleUniqueChange = (index) => {
    const values = [...fields];
    values[index].is_unique = !values[index].is_unique;
    setFields(values);
  };

  const handleCreateTable = async () => {
    try {
      await axios.post(
        "http://127.0.0.1:8000/api/create_table/",
        { name: tableName, fields },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchTables();
      setMessage({ type: "success", text: "Table created successfully!" });
    } catch (error) {
      console.error("Error creating table:", error);
      setMessage({
        type: "error",
        text: "Error creating table. Please try again.",
      });
    }
  };

  const handleDeleteTable = async () => {
    try {
      await axios.delete(
        `http://127.0.0.1:8000/api/delete_table/${tableName}/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchTables();
      setMessage({ type: "success", text: "Table deleted successfully!" });
    } catch (error) {
      console.error("Error deleting table:", error);
      setMessage({
        type: "error",
        text: "Error deleting table. Please try again.",
      });
    }
  };

  const handleAddRecord = async () => {
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/add_record/${tableName}/`,
        newRecord,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecords([...records, response.data.record]);
      setNewRecord({});
      setMessage({ type: "success", text: "Record added successfully!" });
    } catch (error) {
      console.error("Error adding record:", error);
      setMessage({
        type: "error",
        text: "Error adding record. Please try again.",
      });
    }
  };

  const handleRecordChange = (field, event) => {
    setNewRecord({ ...newRecord, [field]: event.target.value });
  };

  return (
    <div>
      <h2 className="card-header">Create Table</h2>

      {message.text && (
        <div
          className={`message ${
            message.type === "error" ? "error" : "success"
          }`}
        >
          {message.text}
        </div>
      )}

      <input
        type="text"
        value={tableName}
        onChange={(e) => setTableName(e.target.value)}
        placeholder="Table Name"
        className="card-input"
      />

      <div className="fields-container">
        {fields.map((field, index) => (
          <div key={index} className="field-row">
            <input
              type="text"
              name="name"
              value={field.name}
              onChange={(e) => handleFieldChange(index, e)}
              placeholder="Field Name"
              className="card-input"
            />
            <select
              name="type"
              value={field.type}
              onChange={(e) => handleFieldChange(index, e)}
              className="card-input"
            >
              <option value="">Select Type</option>
              {fieldTypes.map((type, i) => (
                <option key={i} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={field.is_unique}
                onChange={() => handleUniqueChange(index)}
              />
              Unique
            </label>
            <button
              onClick={() => handleDeleteField(index)}
              className="delete-field-btn"
            >
              <MdDelete size={20} color="#dc3545" />
            </button>
          </div>
        ))}
      </div>

      <button onClick={handleAddField} className="add-field-btn">
        Add Field
      </button>
      <button onClick={handleCreateTable} className="create-table-btn">
        Create Table
      </button>
      <button onClick={handleDeleteTable} className="delete-table-btn">
        Delete Table
      </button>

      {/* Search Tables */}
      <h2 className="card-header">Search Tables</h2>
      <input
        type="text"
        value={searchQuery}
        onChange={handleSearchChange}
        placeholder="Search Tables"
        className="card-input"
      />

      <button onClick={() => setShowAll(!showAll)} className="toggle-show-btn">
        {showAll ? "Show Less" : "Show All"}
      </button>

      <ul className="table-list">
        {showAll ? (
          tables.map((table, index) => (
            <li
              key={index}
              className="table-item"
              onClick={() => handleTableClick(table)}
            >
              {table}
            </li>
          ))
        ) : searchQuery && filteredTables.length === 1 ? (
          filteredTables.map((table, index) => (
            <li
              key={index}
              className="table-item"
              onClick={() => handleTableClick(table)}
            >
              {table}
            </li>
          ))
        ) : searchQuery ? (
          <li className="table-item">Table doesn't exist</li>
        ) : null}
      </ul>

      {/* Display table fields if selected */}
      {selectedTable && (
        <div className="table-fields">
          <h3>Table Fields:</h3>
          <ul>
            {selectedTable.map((field, index) => (
              <li key={index}>
                {field.name} ({field.type})
              </li>
            ))}
          </ul>

          {/* Add Record Form */}
          <h3>Add Record</h3>
          <div className="record-form">
            {selectedTable.map((field, index) => (
              <div key={index} className="record-field">
                <input
                  type="text"
                  value={newRecord[field.name] || ""}
                  onChange={(e) => handleRecordChange(field.name, e)}
                  placeholder={`Enter ${field.name}`}
                  className="card-input"
                />
              </div>
            ))}
            <button onClick={handleAddRecord} className="add-record-btn">
              Add Record
            </button>
          </div>

          {/* Display added records */}
          <h3>Records</h3>
          <ul>
            {records.map((record, index) => (
              <li key={index}>
                {Object.entries(record)
                  .map(([key, value]) => `${key}: ${value}`)
                  .join(", ")}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CreateTable;
