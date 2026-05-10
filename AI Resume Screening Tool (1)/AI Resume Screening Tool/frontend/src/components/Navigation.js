import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Menu,
  MenuItem,
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const Navigation = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          <Link to="/" style={{ textDecoration: 'none', color: 'white' }}>
            AI Resume Screening Tool
          </Link>
        </Typography>

        {user ? (
          <Box>
            <Button
              color="inherit"
              component={Link}
              to="/dashboard"
              sx={{ marginRight: 2 }}
            >
              Dashboard
            </Button>
            <Button
              color="inherit"
              component={Link}
              to="/upload"
              sx={{ marginRight: 2 }}
            >
              Upload Resume
            </Button>
            <Button
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ marginRight: 2 }}
            >
              {user.username}
            </Button>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem component={Link} to="/profile">
                Profile
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        ) : (
          <Box>
            <Button
              color="inherit"
              component={Link}
              to="/login"
              sx={{ marginRight: 1 }}
            >
              Login
            </Button>
            <Button
              color="inherit"
              component={Link}
              to="/register"
              variant="outlined"
            >
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
