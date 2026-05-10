import React, { useState, useCallback } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { resumeService } from '../services';
import useResumeStore from '../store/resumeStore';

const ResumeUpload = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const { addResume } = useResumeStore();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) {
      setError('Please upload valid files (PDF or DOCX)');
      return;
    }

    setError('');
    setUploading(true);

    for (const file of acceptedFiles) {
      try {
        const response = await resumeService.uploadResume(file);
        setUploadedFiles((prev) => [...prev, response.data.resume]);
        addResume(response.data.resume);
        setSuccess(`${file.name} uploaded successfully!`);
      } catch (err) {
        setError(
          err.response?.data?.message || `Error uploading ${file.name}`
        );
      }
    }

    setUploading(false);
  }, [addResume]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        ['.docx'],
    },
  });

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Upload Resumes
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Card sx={{ mb: 4 }}>
        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'divider',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            transition: 'all 0.3s ease',
          }}
        >
          <input {...getInputProps()} />
          <Typography variant="h6" gutterBottom>
            {isDragActive
              ? 'Drop your resume files here...'
              : 'Drag and drop your resumes here'}
          </Typography>
          <Typography color="textSecondary" sx={{ mb: 2 }}>
            or click to select files
          </Typography>
          <Button variant="contained">Select Files</Button>
          <Typography variant="caption" sx={{ mt: 2, display: 'block' }}>
            Supported formats: PDF, DOCX (Max 5MB per file)
          </Typography>
        </Box>
      </Card>

      {uploading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography sx={{ mt: 1 }}>Uploading...</Typography>
        </Box>
      )}

      {uploadedFiles.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Uploaded Resumes ({uploadedFiles.length})
            </Typography>
            <List>
              {uploadedFiles.map((resume) => (
                <ListItem key={resume.id}>
                  <ListItemText
                    primary={resume.candidate_name}
                    secondary={`${resume.email || 'No email'} | ${resume.file_type?.toUpperCase()}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default ResumeUpload;
