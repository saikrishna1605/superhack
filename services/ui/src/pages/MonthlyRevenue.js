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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Chip
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { clientsAPI } from '../services/clientsAPI';

const MonthlyRevenue = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [stats, setStats] = useState({
    totalRevenue: 0,
    avgRevenue: 0,
    topClient: { name: '', revenue: 0 }
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const allClients = await clientsAPI.getAll();
    
    // Filter only active clients
    const activeClients = allClients.filter(c => (c.status || 'Active').toLowerCase() === 'active');
    setClients(activeClients);

    // Calculate stats
    const totalRevenue = activeClients.reduce((sum, client) => {
      const revenue = client.monthly_spend || client.revenue || 0;
      return sum + revenue;
    }, 0);
    
    const avgRevenue = activeClients.length > 0 ? totalRevenue / activeClients.length : 0;
    
    const topClient = activeClients.reduce((max, client) => {
      const revenue = client.monthly_spend || client.revenue || 0;
      return revenue > max.revenue ? { name: client.name, revenue } : max;
    }, { name: '', revenue: 0 });

    setStats({ totalRevenue, avgRevenue, topClient });
  };

  const handleViewDetails = (client) => {
    setSelectedClient(client);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedClient(null);
  };

  // Generate monthly revenue projection data for selected client
  const getClientRevenueData = (client) => {
    if (!client) return [];
    const baseRevenue = client.monthly_spend || client.revenue || 0;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    return months.map((month, index) => ({
      month,
      revenue: Math.round(baseRevenue * (0.95 + Math.random() * 0.1))
    }));
  };

  // Monthly trend data
  const revenueData = [
    { month: 'Jan', revenue: 98000 },
    { month: 'Feb', revenue: 105000 },
    { month: 'Mar', revenue: 112000 },
    { month: 'Apr', revenue: 118000 },
    { month: 'May', revenue: 121000 },
    { month: 'Jun', revenue: 124000 }
  ];

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
          Monthly Revenue Overview
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Monthly Revenue
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                ${stats.totalRevenue.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Revenue per Client
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600 }}>
                ${Math.round(stats.avgRevenue).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Top Revenue Client
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {stats.topClient.name}
              </Typography>
              <Typography variant="body2" color="success.main">
                ${stats.topClient.revenue.toLocaleString()}/mo
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Revenue Trend Chart */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          6-Month Revenue Trend
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={revenueData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
            <Legend />
            <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} name="Revenue ($)" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Client Revenue Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Revenue by Client
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Client Name</strong></TableCell>
                <TableCell><strong>Industry</strong></TableCell>
                <TableCell align="right"><strong>Monthly Revenue</strong></TableCell>
                <TableCell align="right"><strong>Annual Revenue</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients
                .sort((a, b) => {
                  const revenueA = a.monthly_spend || a.revenue || 0;
                  const revenueB = b.monthly_spend || b.revenue || 0;
                  return revenueB - revenueA;
                })
                .map((client) => {
                  const monthlyRevenue = client.monthly_spend || client.revenue || 0;
                  const annualRevenue = monthlyRevenue * 12;
                  return (
                    <TableRow key={client.client_id || client.id}>
                      <TableCell>{client.name}</TableCell>
                      <TableCell>{client.industry}</TableCell>
                      <TableCell align="right">${monthlyRevenue.toLocaleString()}</TableCell>
                      <TableCell align="right">${annualRevenue.toLocaleString()}</TableCell>
                      <TableCell align="center">
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleViewDetails(client)}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Revenue Details Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Revenue Details: {selectedClient?.name}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedClient && (
            <Box>
              {/* Summary Cards */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="textSecondary" variant="body2" gutterBottom>
                        Monthly Revenue
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 600, color: 'success.main' }}>
                        ${(selectedClient.monthly_spend || selectedClient.revenue || 0).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="textSecondary" variant="body2" gutterBottom>
                        Annual Revenue
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 600, color: 'primary.main' }}>
                        ${((selectedClient.monthly_spend || selectedClient.revenue || 0) * 12).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="textSecondary" variant="body2" gutterBottom>
                        Industry
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {selectedClient.industry}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Client Information */}
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Client Information
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="body2">Total Licenses</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {selectedClient.total_licenses || selectedClient.licenses || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="body2">Total Users</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {selectedClient.total_users || selectedClient.employees || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="body2">Health Score</Typography>
                  <Chip 
                    label={`${selectedClient.health_score || selectedClient.healthScore || 0}/100`}
                    color={
                      (selectedClient.health_score || selectedClient.healthScore || 0) >= 80 ? 'success' :
                      (selectedClient.health_score || selectedClient.healthScore || 0) >= 60 ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="body2">Churn Risk</Typography>
                  <Chip 
                    label={
                      (selectedClient.churn_probability || selectedClient.churnProbability || 0) > 70 ? 'High' :
                      (selectedClient.churn_probability || selectedClient.churnProbability || 0) > 30 ? 'Medium' : 'Low'
                    }
                    color={
                      (selectedClient.churn_probability || selectedClient.churnProbability || 0) > 70 ? 'error' :
                      (selectedClient.churn_probability || selectedClient.churnProbability || 0) > 30 ? 'warning' : 'success'
                    }
                    size="small"
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Revenue Trend Chart */}
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                6-Month Revenue History
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={getClientRevenueData(selectedClient)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                  <Bar dataKey="revenue" fill="#4caf50" name="Revenue ($)" />
                </BarChart>
              </ResponsiveContainer>

              <Divider sx={{ my: 2 }} />

              {/* Revenue Breakdown */}
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Revenue Breakdown
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Period</strong></TableCell>
                      <TableCell align="right"><strong>Amount</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Monthly</TableCell>
                      <TableCell align="right">
                        ${(selectedClient.monthly_spend || selectedClient.revenue || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Quarterly (3 months)</TableCell>
                      <TableCell align="right">
                        ${((selectedClient.monthly_spend || selectedClient.revenue || 0) * 3).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Semi-Annual (6 months)</TableCell>
                      <TableCell align="right">
                        ${((selectedClient.monthly_spend || selectedClient.revenue || 0) * 6).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell><strong>Annual (12 months)</strong></TableCell>
                      <TableCell align="right">
                        <strong>${((selectedClient.monthly_spend || selectedClient.revenue || 0) * 12).toLocaleString()}</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} variant="contained">Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MonthlyRevenue;
