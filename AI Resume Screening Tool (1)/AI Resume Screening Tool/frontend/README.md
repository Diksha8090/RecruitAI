# AI Resume Screening Tool - Frontend

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure API
Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:5000/api
```

### 3. Start Development Server
```bash
npm start
```

The application will open at `http://localhost:3000`

## Features

- **User Authentication**: Register and login
- **Resume Upload**: Upload PDF and DOCX files
- **Resume Management**: View and manage uploaded resumes
- **AI Analysis**: Analyze resumes using LLM-based screening
- **Dashboard**: Overview of resumes and analysis results

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Navigation.js
│   ├── pages/
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   └── ResumeUpload.js
│   ├── services/
│   │   ├── apiClient.js
│   │   └── index.js
│   ├── store/
│   │   ├── authStore.js
│   │   └── resumeStore.js
│   ├── App.js
│   └── index.js
├── package.json
└── README.md
```

## Key Technologies

- **React 18**: UI framework
- **Material-UI (MUI)**: Component library
- **Zustand**: State management
- **Axios**: HTTP client
- **React Router**: Navigation
- **React Dropzone**: File upload
- **Recharts**: Data visualization (for future analytics)

## Available Pages

- `/login` - User login
- `/register` - User registration
- `/dashboard` - Main dashboard
- `/upload` - Resume upload page
