import React from 'react';
import { Container, Typography, Paper, Box, AppBar, Toolbar, IconButton } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SoftwareDetails = ({ user, onLogout }) => {
  const navigate = useNavigate();

  return (
    <Box>
      <AppBar position="static" sx={{ backgroundColor: '#2e7d32' }}>
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => navigate(-1)}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Software Details
          </Typography>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5">Software License Details</Typography>
          <Typography color="text.secondary">
            Detailed license usage, user activity, and optimization recommendations will be displayed here.
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default SoftwareDetails;