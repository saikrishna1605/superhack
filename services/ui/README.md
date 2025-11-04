# PulseOps AI - React UI

Modern React frontend for PulseOps AI platform.

## Features

### MSP Dashboard
- **Key Metrics**: Total clients, MRR, average health score, high-risk clients
- **Revenue Trends**: 30-day revenue visualization
- **Churn Risk Alerts**: Clients at risk with health scores
- **Upsell Opportunities**: AI-generated recommendations with potential value
- **Recent Clients**: Quick overview of newly onboarded clients

### IT Admin Dashboard
- **Cost Metrics**: Total software, monthly costs, utilization rates
- **Savings Opportunities**: Identify and act on cost optimization
- **Department Breakdown**: Pie chart of spending by department
- **Cost Anomalies**: Real-time alerts on unusual spending patterns
- **Low Utilization Software**: Table view with deactivation actions
- **AI Recommendations**: Smart suggestions for cost savings

### Design
- **Material-UI**: Modern, responsive design
- **Recharts**: Interactive data visualizations
- **Role-Based Access**: Separate dashboards for MSPs and IT admins
- **Real-Time Data**: Live updates via API integration

## Quick Start

### Installation
```bash
cd services/ui
npm install
```

### Development
```bash
# Start development server
npm start

# Application runs at http://localhost:3000
```

### Environment Configuration
Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000
```

### Demo Credentials
- **MSP User**: demo-msp@example.com / password123
- **IT Admin**: demo-it@example.com / password123

## Project Structure

```
ui/
├── public/
│   └── index.html
├── src/
│   ├── components/         # Reusable components
│   ├── pages/             # Page components
│   │   ├── Login.js       # Authentication
│   │   ├── MSPDashboard.js
│   │   ├── ITDashboard.js
│   │   ├── ClientDetails.js
│   │   └── SoftwareDetails.js
│   ├── services/
│   │   └── api.js         # API client
│   ├── utils/
│   │   └── formatters.js  # Utility functions
│   ├── App.js             # Main app component
│   ├── index.js           # Entry point
│   └── index.css          # Global styles
└── package.json
```

## Key Components

### MSP Dashboard Features
1. **Metric Cards**: Key performance indicators
2. **Revenue Chart**: Line chart showing 30-day trends
3. **Churn Risk List**: Clients requiring attention
4. **Upsell Cards**: Recommendations with potential value
5. **Recent Clients**: Grid view of new clients

### IT Dashboard Features
1. **Cost Metrics**: Software count, total cost, utilization
2. **Department Pie Chart**: Visual spend breakdown
3. **Anomaly Cards**: Recent cost anomalies with severity
4. **Utilization Table**: Actionable license deactivation
5. **Recommendations Grid**: AI-powered cost savings

## API Integration

The UI connects to the FastAPI backend:

```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

// Automatic token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Build for Production

```bash
# Create optimized build
npm run build

# Deploy to S3
npm run deploy

# Or manually
aws s3 sync build/ s3://pulseops-ui-bucket --delete
```

## Color Scheme

- **Primary**: #1976d2 (Blue)
- **Success**: #4caf50 (Green)
- **Warning**: #ff9800 (Orange)
- **Error**: #f44336 (Red)
- **IT Theme**: #2e7d32 (Dark Green)

## Charts & Visualizations

Using **Recharts** for data visualization:
- Line charts for trends
- Pie charts for distribution
- Bar charts for comparisons
- Responsive and interactive

## Authentication Flow

1. User enters credentials or uses quick demo login
2. API validates and returns JWT token
3. Token stored in localStorage
4. All subsequent requests include token
5. Redirect to role-appropriate dashboard

## Responsive Design

- Desktop: Full dashboard with all features
- Tablet: Responsive grid layout
- Mobile: Stacked cards and simplified views

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting for faster load times
- Lazy loading of routes
- Optimized bundle size
- Efficient re-rendering with React hooks