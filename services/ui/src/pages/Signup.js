import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Divider
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import BusinessIcon from '@mui/icons-material/Business';
import ComputerIcon from '@mui/icons-material/Computer';
import { registerUser } from '../utils/auth';

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
    role: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.name || !formData.email || !formData.password || !formData.company || !formData.role) {
      setError('All fields are required');
      return false;
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const result = registerUser({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        company: formData.company,
        role: formData.role
      });
      
      if (result.success) {
        // Show success and redirect to login
        alert('Account created successfully! Please login with your credentials.');
        navigate('/login');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An error occurred during registration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (role) => {
    setFormData({
      ...formData,
      role: role
    });
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box display="flex" alignItems="center" justifyContent="center" mb={3}>
          <PersonAddIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" fontWeight={600}>
            Create Account
          </Typography>
        </Box>
        
        <Typography variant="body2" color="text.secondary" align="center" mb={3}>
          Join PulseOps AI to optimize your software management
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Full Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            margin="normal"
            required
            autoComplete="name"
          />

          <TextField
            fullWidth
            label="Email Address"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            margin="normal"
            required
            autoComplete="email"
          />

          <TextField
            fullWidth
            label="Company Name"
            name="company"
            value={formData.company}
            onChange={handleChange}
            margin="normal"
            required
            autoComplete="organization"
          />

          <TextField
            fullWidth
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            margin="normal"
            required
            autoComplete="new-password"
            helperText="Minimum 6 characters"
          />

          <TextField
            fullWidth
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            margin="normal"
            required
            autoComplete="new-password"
          />

          <FormControl fullWidth margin="normal" required>
            <InputLabel>Account Type</InputLabel>
            <Select
              name="role"
              value={formData.role}
              onChange={handleChange}
              label="Account Type"
            >
              <MenuItem value="msp">MSP (Managed Service Provider)</MenuItem>
              <MenuItem value="it_admin">IT Team / Administrator</MenuItem>
            </Select>
          </FormControl>

          <Divider sx={{ my: 2 }}>OR</Divider>

          <Typography variant="body2" align="center" mb={2}>
            Quick Select Account Type:
          </Typography>

          <Grid container spacing={2} mb={3}>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={formData.role === 'msp' ? 'contained' : 'outlined'}
                onClick={() => handleQuickSelect('msp')}
                startIcon={<BusinessIcon />}
                sx={{ py: 2 }}
              >
                MSP Account
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={formData.role === 'it_admin' ? 'contained' : 'outlined'}
                onClick={() => handleQuickSelect('it_admin')}
                startIcon={<ComputerIcon />}
                sx={{ py: 2 }}
              >
                IT Account
              </Button>
            </Grid>
          </Grid>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            sx={{ mt: 2, mb: 2, py: 1.5 }}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </Button>

          <Box textAlign="center" mt={2}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Link to="/login" style={{ textDecoration: 'none', color: '#1976d2', fontWeight: 600 }}>
                Login here
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Demo Accounts Info */}
      <Paper elevation={1} sx={{ p: 2, mt: 3, bgcolor: 'info.light' }}>
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          Demo Accounts Available:
        </Typography>
        <Typography variant="body2">
          • MSP: demo-msp@example.com / password123
        </Typography>
        <Typography variant="body2">
          • IT Team: demo-it@example.com / password123
        </Typography>
      </Paper>
    </Container>
  );
};

export default Signup;
