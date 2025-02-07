import React, { useState } from "react";
import axios from "axios";
import { AiFillFileAdd } from "react-icons/ai";

const ImportCSV = ({ token }) => {
  const [csvFile, setCsvFile] = useState(null);
  const [tableName, setTableName] = useState("");

  const handleCSVUpload = async () => {
    if (!csvFile || !tableName) {
      console.error("CSV file or table name is missing.");
      return;
    }

    const formData = new FormData();
    formData.append("file", csvFile);

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/import_csv/${tableName}/`,
        formData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      console.log("CSV Imported:", response.data);
    } catch (error) {
      console.error("Error importing CSV:", error);
    }
  };

  return (
    <div>
      <h2 className="card-header">Import CSV</h2>

      <label htmlFor="file-import" className="file-import-label">
        Choose CSV File
        <AiFillFileAdd size={20} />
      </label>
      <input
        type="file"
        accept=".csv"
        id="file-import"
        onChange={(e) => setCsvFile(e.target.files[0])}
        className="file-import"
      />

      <input
        type="text"
        value={tableName}
        onChange={(e) => setTableName(e.target.value)}
        placeholder="Table Name"
        className="card-input"
      />

      <button onClick={handleCSVUpload} className="import-btn">
        Import CSV File
      </button>
    </div>
  );
};

export default ImportCSV;
