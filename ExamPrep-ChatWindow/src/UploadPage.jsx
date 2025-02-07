import axios from "axios";
import { useEffect, useState } from "react"

export const UploadPage = () =>{
    const [uploadFile, setUploadFile] = useState(null);
    const [files, setFiles] = useState([]);

    async function getData(){
            axios.get("http://localhost:5000/show-files").then((res)=>{setFiles(res.data)})
    }
    useEffect(()=>{
        getData();
    },[]);

    function handleChangeFile(event) {
        const file = event.target.files[0];
        // let formData = new FormData();
        // formData.append('file', file);
        //Make a request to server and send formData
        console.log(file);
        setUploadFile(file);
      }

    async function handleSubmit(e){
        e.preventDefault();
        await axios.post("http://localhost:5000/upload", {file: uploadFile},
            {
                headers : {
                    "Content-Type": "multipart/form-data"
                }
            }
        );
        alert("File Uploaded!");
        getData();
    }
    async function clearFiles(){
        await axios.get("http://localhost:5000/clear");
        alert("Files Removed!");
        getData();
    }
    return(
        <div>
            <h1>File Upload</h1>
                <input id='uploadFile' type="file" onChange={handleChangeFile} />
                <button  onClick={handleSubmit}>Upload</button>

            <br/>
            <h2 style={{marginLeft:"10px"}}> Uploaded Files</h2>
            <ul>
                {files.map((f,index)=>(
                    <li style={{color:'white'}}>{f}</li>
                ))}
            </ul>

            <button onClick={clearFiles}>Clear Files</button>
        </div>
    )
}