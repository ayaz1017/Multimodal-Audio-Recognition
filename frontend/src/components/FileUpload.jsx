import './FileUpload.css';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt } from 'react-icons/fa';

function FileUpload({ onFileSelect, acceptedFiles, isLoading }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    accept: acceptedFiles,
    disabled: isLoading,
  });

  return (
    <div
      {...getRootProps()}
      className={`file-upload ${isDragActive ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
    >
      <input {...getInputProps()} />
      <FaCloudUploadAlt className="upload-icon" />
      <h3>Drop your file here</h3>
      <p>or click to select a file</p>
      <small>Supported formats: {Object.keys(acceptedFiles).join(', ')}</small>
    </div>
  );
}

export default FileUpload;
