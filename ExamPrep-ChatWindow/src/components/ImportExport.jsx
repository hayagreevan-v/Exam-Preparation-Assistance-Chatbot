import { useState } from "react";
import axios from "axios";

const ImportExport = ({messages, setMessages}) =>{
    const [file, setFile] = useState([]); 
    const handleChangeFile = (event) =>{
        setFile(event.target.files[0]);
    } 
    const handleImport = () =>{
        axios.post("http://localhost:5000/import-chat",{file:file},
        {
            headers:{
                "Content-Type": "multipart/form-data"
            }
        }).then((res) => setMessages(res.data.chat));
    }

    const handleExport = async() =>{
        const res = await axios.get("http://localhost:5000/export-chat",{responseType:"blob"});
        const jsonBlob = new Blob([res.data],{type:"application/json"});
        // window.URL.createObjectURL(jsonBlob);
        // Create a temporary URL for the Blob
        const url = window.URL.createObjectURL(jsonBlob);

        // Create a temporary <a> element to trigger the download
        const tempLink = document.createElement("a");
        tempLink.href = url;
        tempLink.setAttribute(
          "download",
          `export.json`
        ); // Set the desired filename for the downloaded file

        // Append the <a> element to the body and click it to trigger the download
        document.body.appendChild(tempLink);
        tempLink.click();

        // Clean up the temporary elements and URL
        document.body.removeChild(tempLink);
        window.URL.revokeObjectURL(url);

        console.log(res.data);

    }

    return(
        <div className="file-upload">
            <h2>Import Chat</h2>
            <input type="file" onChange={handleChangeFile}></input>
            <button onClick={handleImport}> Import</button>
            <br/>
            <h2>Export Chat</h2>
            <button style={{alignSelf:"center"}} onClick={handleExport}>Export</button>
        </div>
    )
}

export default ImportExport;