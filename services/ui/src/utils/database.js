// LocalStorage-based backend simulation
// This provides persistent data storage that works across page refreshes

const CLIENTS_KEY = 'pulseops_clients';
const LICENSES_KEY = 'pulseops_licenses';

// Initialize with demo data if not exists
const initializeData = () => {
  if (!localStorage.getItem(CLIENTS_KEY)) {
    const defaultClients = [
      { id: 1, name: 'TechCorp Inc', industry: 'Technology', licenses: 45, revenue: 12500, status: 'Active', healthScore: 92, churnRisk: 15, employees: 150, activeUsers: 42, usageRate: 93, since: '2022-01-15', contact: 'John Smith', email: 'john.smith@techcorp.com', phone: '+1 (555) 123-4567' },
      { id: 2, name: 'DataSystems LLC', industry: 'Finance', licenses: 32, revenue: 8900, status: 'Active', healthScore: 78, churnRisk: 72, employees: 95, activeUsers: 25, usageRate: 78, since: '2021-06-20', contact: 'Sarah Johnson', email: 'sarah.johnson@datasystems.com', phone: '+1 (555) 234-5678' },
      { id: 3, name: 'CloudNet Solutions', industry: 'IT Services', licenses: 56, revenue: 15200, status: 'Active', healthScore: 85, churnRisk: 68, employees: 200, activeUsers: 48, usageRate: 86, since: '2020-11-10', contact: 'Michael Chen', email: 'michael.chen@cloudnet.com', phone: '+1 (555) 345-6789' },
      { id: 4, name: 'MediaPro Studios', industry: 'Media', licenses: 28, revenue: 7800, status: 'Active', healthScore: 95, churnRisk: 8, employees: 85, activeUsers: 27, usageRate: 96, since: '2023-03-12', contact: 'Emily Rodriguez', email: 'emily.r@mediapro.com', phone: '+1 (555) 456-7890' },
      { id: 5, name: 'FinTech Partners', industry: 'Finance', licenses: 41, revenue: 11200, status: 'Active', healthScore: 88, churnRisk: 25, employees: 120, activeUsers: 38, usageRate: 89, since: '2021-09-05', contact: 'David Park', email: 'david.park@fintechpartners.com', phone: '+1 (555) 567-8901' },
      { id: 6, name: 'HealthCare Plus', industry: 'Healthcare', licenses: 38, revenue: 9600, status: 'Active', healthScore: 91, churnRisk: 12, employees: 110, activeUsers: 35, usageRate: 92, since: '2022-07-18', contact: 'Dr. Lisa Martinez', email: 'lisa.martinez@healthcareplus.com', phone: '+1 (555) 678-9012' },
      { id: 7, name: 'EduTech Solutions', industry: 'Education', licenses: 52, revenue: 13400, status: 'Active', healthScore: 82, churnRisk: 45, employees: 175, activeUsers: 44, usageRate: 85, since: '2020-04-22', contact: 'Robert Williams', email: 'robert.w@edutech.com', phone: '+1 (555) 789-0123' },
      { id: 8, name: 'RetailMax Corp', industry: 'Retail', licenses: 44, revenue: 10800, status: 'Active', healthScore: 76, churnRisk: 85, employees: 140, activeUsers: 31, usageRate: 70, since: '2021-12-08', contact: 'Jennifer Taylor', email: 'jen.taylor@retailmax.com', phone: '+1 (555) 890-1234' },
      { id: 9, name: 'AutoDrive Systems', industry: 'Automotive', licenses: 35, revenue: 9200, status: 'Active', healthScore: 89, churnRisk: 18, employees: 105, activeUsers: 32, usageRate: 91, since: '2022-05-14', contact: 'James Anderson', email: 'james.anderson@autodrive.com', phone: '+1 (555) 901-2345' },
      { id: 10, name: 'GreenEnergy Co', industry: 'Energy', licenses: 29, revenue: 8100, status: 'Active', healthScore: 93, churnRisk: 10, employees: 90, activeUsers: 28, usageRate: 97, since: '2023-01-20', contact: 'Maria Garcia', email: 'maria.garcia@greenenergy.com', phone: '+1 (555) 012-3456' },
      { id: 11, name: 'LogiTrans Inc', industry: 'Logistics', licenses: 47, revenue: 12800, status: 'Active', healthScore: 84, churnRisk: 35, employees: 160, activeUsers: 41, usageRate: 87, since: '2021-08-30', contact: 'Christopher Lee', email: 'chris.lee@logitrans.com', phone: '+1 (555) 123-7890' },
      { id: 12, name: 'SecureBank Ltd', industry: 'Banking', licenses: 61, revenue: 16500, status: 'Active', healthScore: 90, churnRisk: 15, employees: 220, activeUsers: 58, usageRate: 95, since: '2020-02-15', contact: 'Patricia Brown', email: 'patricia.brown@securebank.com', phone: '+1 (555) 234-8901' },
      { id: 13, name: 'TravelHub Global', industry: 'Travel', licenses: 33, revenue: 8700, status: 'Active', healthScore: 79, churnRisk: 62, employees: 98, activeUsers: 26, usageRate: 79, since: '2022-11-03', contact: 'Daniel Kim', email: 'daniel.kim@travelhub.com', phone: '+1 (555) 345-9012' },
      { id: 14, name: 'FoodChain Supplies', industry: 'Food & Beverage', licenses: 39, revenue: 10200, status: 'Active', healthScore: 87, churnRisk: 28, employees: 115, activeUsers: 36, usageRate: 92, since: '2021-04-17', contact: 'Amanda White', email: 'amanda.white@foodchain.com', phone: '+1 (555) 456-0123' },
      { id: 15, name: 'BuildPro Construction', industry: 'Construction', licenses: 42, revenue: 11600, status: 'Active', healthScore: 81, churnRisk: 48, employees: 130, activeUsers: 37, usageRate: 88, since: '2020-09-25', contact: 'Thomas Wilson', email: 'thomas.wilson@buildpro.com', phone: '+1 (555) 567-1234' },
      { id: 16, name: 'LegalEase Partners', industry: 'Legal', licenses: 26, revenue: 7200, status: 'Active', healthScore: 94, churnRisk: 9, employees: 75, activeUsers: 25, usageRate: 96, since: '2023-02-08', contact: 'Jessica Moore', email: 'jessica.moore@legalease.com', phone: '+1 (555) 678-2345' },
      { id: 17, name: 'InsureTech Global', industry: 'Insurance', licenses: 54, revenue: 14100, status: 'Active', healthScore: 83, churnRisk: 38, employees: 180, activeUsers: 47, usageRate: 87, since: '2021-10-12', contact: 'Kevin Davis', email: 'kevin.davis@insuretech.com', phone: '+1 (555) 789-3456' },
      { id: 18, name: 'PharmaCare Inc', industry: 'Pharmaceutical', licenses: 49, revenue: 13800, status: 'Active', healthScore: 92, churnRisk: 14, employees: 165, activeUsers: 46, usageRate: 94, since: '2022-06-20', contact: 'Dr. Michelle Thompson', email: 'michelle.thompson@pharmacare.com', phone: '+1 (555) 890-4567' },
      { id: 19, name: 'RealEstate Ventures', industry: 'Real Estate', licenses: 37, revenue: 9800, status: 'Active', healthScore: 86, churnRisk: 32, employees: 108, activeUsers: 34, usageRate: 92, since: '2020-12-01', contact: 'Brian Jackson', email: 'brian.jackson@realestate.com', phone: '+1 (555) 901-5678' },
      { id: 20, name: 'ConsultPro Services', industry: 'Consulting', licenses: 31, revenue: 8400, status: 'Active', healthScore: 88, churnRisk: 22, employees: 92, activeUsers: 29, usageRate: 94, since: '2022-08-15', contact: 'Nicole Harris', email: 'nicole.harris@consultpro.com', phone: '+1 (555) 012-6789' },
    ];
    localStorage.setItem(CLIENTS_KEY, JSON.stringify(defaultClients));
  }
};

// Client CRUD operations
export const clientsDB = {
  getAll: () => {
    initializeData();
    const clients = localStorage.getItem(CLIENTS_KEY);
    return clients ? JSON.parse(clients) : [];
  },

  getById: (id) => {
    const clients = clientsDB.getAll();
    return clients.find(c => c.id === parseInt(id));
  },

  create: (clientData) => {
    const clients = clientsDB.getAll();
    const newClient = {
      ...clientData,
      id: Math.max(...clients.map(c => c.id), 0) + 1,
      status: 'Active',
    };
    clients.push(newClient);
    localStorage.setItem(CLIENTS_KEY, JSON.stringify(clients));
    return newClient;
  },

  update: (id, clientData) => {
    const clients = clientsDB.getAll();
    const index = clients.findIndex(c => c.id === parseInt(id));
    if (index !== -1) {
      clients[index] = { ...clients[index], ...clientData };
      localStorage.setItem(CLIENTS_KEY, JSON.stringify(clients));
      return clients[index];
    }
    return null;
  },

  delete: (id) => {
    const clients = clientsDB.getAll();
    const filtered = clients.filter(c => c.id !== parseInt(id));
    localStorage.setItem(CLIENTS_KEY, JSON.stringify(filtered));
    return true;
  },

  // Dashboard statistics
  getStats: () => {
    const clients = clientsDB.getAll();
    return {
      totalClients: clients.length,
      totalRevenue: clients.reduce((sum, c) => sum + c.revenue, 0),
      totalLicenses: clients.reduce((sum, c) => sum + c.licenses, 0),
      highRiskClients: clients.filter(c => c.churnRisk > 70).length,
      avgHealthScore: Math.round(clients.reduce((sum, c) => sum + c.healthScore, 0) / clients.length),
    };
  },
};

// Initialize data on module load
initializeData();
