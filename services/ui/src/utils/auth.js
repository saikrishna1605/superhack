// Simple authentication utility using localStorage as a mock database

const USERS_KEY = 'pulseops_users';
const CURRENT_USER_KEY = 'pulseops_current_user';
const AUTH_TOKEN_KEY = 'pulseops_token';

// Initialize with demo users if no users exist
const initializeUsers = () => {
  const users = getUsers();
  if (users.length === 0) {
    const demoUsers = [
      {
        id: '1',
        email: 'demo-msp@example.com',
        password: 'password123',
        name: 'MSP Admin Demo User',
        role: 'msp',
        company: 'Demo MSP Company',
        createdAt: new Date().toISOString()
      },
      {
        id: '2',
        email: 'demo-it@example.com',
        password: 'password123',
        name: 'IT Demo User',
        role: 'it_admin',
        company: 'Demo IT Company',
        createdAt: new Date().toISOString()
      }
    ];
    localStorage.setItem(USERS_KEY, JSON.stringify(demoUsers));
  }
};

// Get all users from localStorage
export const getUsers = () => {
  const users = localStorage.getItem(USERS_KEY);
  return users ? JSON.parse(users) : [];
};

// Save users to localStorage
const saveUsers = (users) => {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
};

// Generate a simple token
const generateToken = () => {
  return 'token_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
};

// Register a new user
export const registerUser = (userData) => {
  initializeUsers();
  const users = getUsers();
  
  // Check if email already exists
  const existingUser = users.find(u => u.email.toLowerCase() === userData.email.toLowerCase());
  if (existingUser) {
    return { success: false, error: 'Email already registered' };
  }
  
  // Create new user
  const newUser = {
    id: Date.now().toString(),
    email: userData.email,
    password: userData.password, // In production, this should be hashed
    name: userData.name,
    role: userData.role, // 'msp' or 'it_admin'
    company: userData.company,
    createdAt: new Date().toISOString()
  };
  
  users.push(newUser);
  saveUsers(users);
  
  return { success: true, user: { ...newUser, password: undefined } };
};

// Login user
export const loginUser = (email, password) => {
  initializeUsers();
  const users = getUsers();
  
  const user = users.find(u => 
    u.email.toLowerCase() === email.toLowerCase() && 
    u.password === password
  );
  
  if (!user) {
    return { success: false, error: 'Invalid email or password' };
  }
  
  // Generate token and save current user
  const token = generateToken();
  const userWithoutPassword = { ...user, password: undefined };
  
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
  
  return { 
    success: true, 
    token, 
    user: userWithoutPassword 
  };
};

// Logout user
export const logoutUser = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(CURRENT_USER_KEY);
};

// Get current user
export const getCurrentUser = () => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const user = localStorage.getItem(CURRENT_USER_KEY);
  
  if (token && user) {
    return { token, user: JSON.parse(user) };
  }
  
  return null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem(AUTH_TOKEN_KEY);
};

// Initialize users on module load
initializeUsers();
