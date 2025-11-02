import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Select,
  MenuItem,
  Alert,
  Snackbar
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PersonOffIcon from '@mui/icons-material/PersonOff';
import { clientsAPI } from '../services/clientsAPI';

const InactiveClients = () => {
  const navigate = useNavigate();
  const [inactiveClients, setInactiveClients] = useState([]);
  const [stats, setStats] = useState({
    totalInactive: 0,
    potentialRevenueLoss: 0
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const allClients = await clientsAPI.getAll();
    
    // Filter inactive clients
    const inactive = allClients.filter(c => (c.status || 'Active').toLowerCase() === 'inactive');
    
    // Calculate stats
    const totalInactive = inactive.length;
    const potentialRevenueLoss = inactive.reduce((sum, client) => {
      return sum + (client.monthly_spend || client.revenue || 0);
    }, 0);

    setInactiveClients(inactive);
    setStats({ totalInactive, potentialRevenueLoss });
  };

  const handleStatusChange = async (clientId, newStatus) => {
    try {
      await clientsAPI.update(clientId, { status: newStatus });
      setSnackbar({ 
        open: true, 
        message: `Client status updated to ${newStatus}`, 
        severity: 'success' 
      });
      // Reload data to refresh the list
      loadData();
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'Failed to update client status', 
        severity: 'error' 
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(-1)}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Inactive Clients
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#f5f5f5' }}>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PersonOffIcon sx={{ color: '#757575', fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Inactive Clients
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: '#757575' }}>
                    {stats.totalInactive}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Clients marked as inactive
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Lost Monthly Revenue
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#f44336' }}>
                ${Math.round(stats.potentialRevenueLoss).toLocaleString()}/mo
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Revenue from inactive clients
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Inactive Clients Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          All Inactive Clients
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Client Name</TableCell>
                <TableCell>Industry</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell align="right">Monthly Spend</TableCell>
                <TableCell align="right">Health Score</TableCell>
                <TableCell align="center">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {inactiveClients.length > 0 ? (
                inactiveClients.map((client) => {
                  const revenue = client.monthly_spend || client.revenue || 0;
                  const healthScore = client.health_score || client.healthScore || 0;
                  
                  return (
                    <TableRow 
                      key={client.id}
                      hover
                    >
                      <TableCell>{client.name}</TableCell>
                      <TableCell>{client.industry}</TableCell>
                      <TableCell align="center">
                        <Select
                          value={(client.status || 'Inactive').toLowerCase()}
                          onChange={(e) => {
                            // Capitalize first letter for API
                            const newStatus = e.target.value.charAt(0).toUpperCase() + e.target.value.slice(1);
                            handleStatusChange(client.id, newStatus);
                          }}
                          size="small"
                          sx={{
                            minWidth: 120,
                            '& .MuiSelect-select': {
                              py: 0.5,
                            }
                          }}
                        >
                          <MenuItem value="active">
                            <Chip
                              label="Active"
                              size="small"
                              sx={{
                                backgroundColor: '#4caf50',
                                color: 'white',
                                fontWeight: 600,
                                width: '100%'
                              }}
                            />
                          </MenuItem>
                          <MenuItem value="inactive">
                            <Chip
                              label="Inactive"
                              size="small"
                              sx={{
                                backgroundColor: '#757575',
                                color: 'white',
                                fontWeight: 600,
                                width: '100%'
                              }}
                            />
                          </MenuItem>
                        </Select>
                      </TableCell>
                      <TableCell align="right">
                        <Typography fontWeight={600}>
                          ${revenue.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          color={healthScore >= 80 ? 'success.main' : healthScore >= 60 ? 'warning.main' : 'error.main'}
                        >
                          {healthScore}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Button
                          size="small"
                          variant="outlined"
                          sx={{ 
                            borderColor: '#757575',
                            color: '#757575',
                            '&:hover': {
                              borderColor: '#424242',
                              backgroundColor: 'rgba(117, 117, 117, 0.04)'
                            }
                          }}
                          onClick={() => navigate(`/msp/clients/${client.id}`)}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No inactive clients found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default InactiveClients;
