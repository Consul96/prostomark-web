import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { RoleRoute } from '../components/RoleRoute';
import { AdminLayout } from '../layouts/AdminLayout';
import { AppLayout } from '../layouts/AppLayout';
import { PublicLayout } from '../layouts/PublicLayout';
import { CalculatorPage } from '../pages/app/CalculatorPage';
import { AnalyticsPage } from '../pages/app/AnalyticsPage';
import { DashboardPage } from '../pages/app/DashboardPage';
import { DocumentsPage } from '../pages/app/DocumentsPage';
import { HistoryPage } from '../pages/app/HistoryPage';
import { ProductsPage } from '../pages/app/ProductsPage';
import { SettingsPage } from '../pages/app/SettingsPage';
import { AdminCompaniesPage } from '../pages/admin/AdminCompaniesPage';
import { AdminHomePage } from '../pages/admin/AdminHomePage';
import { AdminLogsPage } from '../pages/admin/AdminLogsPage';
import { AdminSubscriptionsPage } from '../pages/admin/AdminSubscriptionsPage';
import { AdminUsersPage } from '../pages/admin/AdminUsersPage';
import { FAQPage } from '../pages/public/FAQPage';
import { HomePage } from '../pages/public/HomePage';
import { LoginPage } from '../pages/public/LoginPage';
import { PricingPage } from '../pages/public/PricingPage';
import { RegisterPage } from '../pages/public/RegisterPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'pricing', element: <PricingPage /> },
      { path: 'faq', element: <FAQPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <RoleRoute allowed={['superadmin', 'manager']} />,
        children: [{ path: '/analytics', element: <Navigate to="/app/analytics" replace /> }],
      },
      {
        path: '/app',
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="dashboard" replace /> },
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'calculator', element: <CalculatorPage /> },
          {
            element: <RoleRoute allowed={['superadmin', 'manager']} />,
            children: [{ path: 'analytics', element: <AnalyticsPage /> }],
          },
          { path: 'products', element: <ProductsPage /> },
          { path: 'documents', element: <DocumentsPage /> },
          { path: 'history', element: <HistoryPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
      {
        element: <RoleRoute allowed={['superadmin']} />,
        children: [
          {
            path: '/admin',
            element: <AppLayout />,
            children: [
              {
                element: <AdminLayout />,
                children: [
                  { index: true, element: <AdminHomePage /> },
                  { path: 'users', element: <AdminUsersPage /> },
                  { path: 'companies', element: <AdminCompaniesPage /> },
                  { path: 'subscriptions', element: <AdminSubscriptionsPage /> },
                  { path: 'logs', element: <AdminLogsPage /> },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
