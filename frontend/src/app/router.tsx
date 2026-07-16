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
import { MarkingLayout } from '../pages/app/marking/MarkingLayout';
import { MarkingDashboardPage } from '../pages/app/marking/MarkingDashboardPage';
import { MarkingClientsPage } from '../pages/app/marking/MarkingClientsPage';
import { MarkingApplicationsPage } from '../pages/app/marking/MarkingApplicationsPage';
import { MarkingHistoryPage } from '../pages/app/marking/MarkingHistoryPage';
import { MarkingSignAgentsPage } from '../pages/app/marking/MarkingSignAgentsPage';
import { MarkingPlaceholderPage } from '../pages/app/marking/MarkingPlaceholderPage';
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
          {
            path: 'marking',
            element: <MarkingLayout />,
            children: [
              { index: true, element: <MarkingDashboardPage /> },
              { path: 'clients', element: <MarkingClientsPage /> },
              { path: 'applications', element: <MarkingApplicationsPage /> },
              { path: 'products', element: <MarkingPlaceholderPage title="Товары и GTIN" phase="Phase 2 (Национальный каталог)" /> },
              { path: 'km-orders', element: <MarkingPlaceholderPage title="Заказы КМ" phase="Phase 3 (СУЗ)" /> },
              { path: 'application-reports', element: <MarkingPlaceholderPage title="Контроль нанесения" phase="Phase 4" /> },
              { path: 'circulation', element: <MarkingPlaceholderPage title="Ввод в оборот" phase="Phase 5" /> },
              { path: 'sign-agents', element: <MarkingSignAgentsPage /> },
              { path: 'history', element: <MarkingHistoryPage /> },
            ],
          },
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
