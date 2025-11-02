// Tests for UI components
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders without crashing', () => {
  render(<App />);
});

test('renders login page by default', () => {
  render(<App />);
  const loginElement = screen.getByText(/PulseOps AI/i);
  expect(loginElement).toBeInTheDocument();
});
