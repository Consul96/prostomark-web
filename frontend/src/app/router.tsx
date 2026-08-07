import { ComponentType, lazy, ReactNode, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { RoleRoute } from '../components/RoleRoute';
import { RouteFallback } from '../components/RouteFallback';
// Layouts stay eager: they are tiny, shared across their section, and keeping
// them in the main bundle avoids a second skeleton flash around page content.
import { AdminLayout } from '../layouts/AdminLayout';
import { AppLayout } from '../layouts/AppLayout';
import { PublicLayout } from '../layouts/PublicLayout';
import { MarkingLayout } from '../pages/app/marking/MarkingLayout';

/**
 * Route-level code splitting.
 *
 * Each page below is loaded on demand, so a user who opens the Dashboard does
 * NOT download the code for Analytics, Admin, the marking module, etc. Vite
 * emits a separate chunk per dynamic import; pages that live together
 * (e.g. the admin or marking screens) naturally form their own logical group.
 *
 * The pages use named exports, so we map them to the `default` shape React.lazy
 * expects. `withSuspense` wraps each element in a Suspense boundary that shows a
 * skeleton while the chunk downloads.
 */
function lazyPage<T extends Record<string, ComponentType<never>>>(
  loader: () => Promise<T>,
  name: keyof T,
) {
  return lazy(() => loader().then((mod) => ({ default: mod[name] as ComponentType<unknown> })));
}

function withSuspense(element: ReactNode): ReactNode {
  return <Suspense fallback={<RouteFallback />}>{element}</Suspense>;
}

// ── public ──────────────────────────────────────────────────────────────────
const HomePage = lazyPage(() => import('../pages/public/HomePage'), 'HomePage');
const PricingPage = lazyPage(() => import('../pages/public/PricingPage'), 'PricingPage');
const FAQPage = lazyPage(() => import('../pages/public/FAQPage'), 'FAQPage');
const LoginPage = lazyPage(() => import('../pages/public/LoginPage'), 'LoginPage');
const RegisterPage = lazyPage(() => import('../pages/public/RegisterPage'), 'RegisterPage');

// ── app ─────────────────────────────────────────────────────────────────────
const DashboardPage = lazyPage(() => import('../pages/app/DashboardPage'), 'DashboardPage');
const CalculatorPage = lazyPage(() => import('../pages/app/CalculatorPage'), 'CalculatorPage');
const AnalyticsPage = lazyPage(() => import('../pages/app/AnalyticsPage'), 'AnalyticsPage');
const ProductsPage = lazyPage(() => import('../pages/app/ProductsPage'), 'ProductsPage');
const DocumentsPage = lazyPage(() => import('../pages/app/DocumentsPage'), 'DocumentsPage');
const HistoryPage = lazyPage(() => import('../pages/app/HistoryPage'), 'HistoryPage');
const SettingsPage = lazyPage(() => import('../pages/app/SettingsPage'), 'SettingsPage');

// ── marking (Честный знак) ───────────────────────────────────────────────────
const MarkingDashboardPage = lazyPage(
  () => import('../pages/app/marking/MarkingDashboardPage'),
  'MarkingDashboardPage',
);
const MarkingClientsPage = lazyPage(() => import('../pages/app/marking/MarkingClientsPage'), 'MarkingClientsPage');
const MarkingApplicationsPage = lazyPage(
  () => import('../pages/app/marking/MarkingApplicationsPage'),
  'MarkingApplicationsPage',
);
const MarkingHistoryPage = lazyPage(() => import('../pages/app/marking/MarkingHistoryPage'), 'MarkingHistoryPage');
const MarkingSignAgentsPage = lazyPage(
  () => import('../pages/app/marking/MarkingSignAgentsPage'),
  'MarkingSignAgentsPage',
);
const MarkingPlaceholderPage = lazyPage(
  () => import('../pages/app/marking/MarkingPlaceholderPage'),
  'MarkingPlaceholderPage',
) as ComponentType<{ title: string; phase: string }>;

// ── admin ───────────────────────────────────────────────────────────────────
const AdminHomePage = lazyPage(() => import('../pages/admin/AdminHomePage'), 'AdminHomePage');
const AdminUsersPage = lazyPage(() => import('../pages/admin/AdminUsersPage'), 'AdminUsersPage');
const AdminCompaniesPage = lazyPage(() => import('../pages/admin/AdminCompaniesPage'), 'AdminCompaniesPage');
const AdminSubscriptionsPage = lazyPage(
  () => import('../pages/admin/AdminSubscriptionsPage'),
  'AdminSubscriptionsPage',
);
const AdminLogsPage = lazyPage(() => import('../pages/admin/AdminLogsPage'), 'AdminLogsPage');

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: withSuspense(<HomePage />) },
      { path: 'pricing', element: withSuspense(<PricingPage />) },
      { path: 'faq', element: withSuspense(<FAQPage />) },
      { path: 'login', element: withSuspense(<LoginPage />) },
      { path: 'register', element: withSuspense(<RegisterPage />) },
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
          { path: 'dashboard', element: withSuspense(<DashboardPage />) },
          { path: 'calculator', element: withSuspense(<CalculatorPage />) },
          {
            element: <RoleRoute allowed={['superadmin', 'manager']} />,
            children: [{ path: 'analytics', element: withSuspense(<AnalyticsPage />) }],
          },
          { path: 'products', element: withSuspense(<ProductsPage />) },
          { path: 'documents', element: withSuspense(<DocumentsPage />) },
          { path: 'history', element: withSuspense(<HistoryPage />) },
          { path: 'settings', element: withSuspense(<SettingsPage />) },
          {
            path: 'marking',
            element: <MarkingLayout />,
            children: [
              { index: true, element: withSuspense(<MarkingDashboardPage />) },
              { path: 'clients', element: withSuspense(<MarkingClientsPage />) },
              { path: 'applications', element: withSuspense(<MarkingApplicationsPage />) },
              {
                path: 'products',
                element: withSuspense(
                  <MarkingPlaceholderPage title="Товары и GTIN" phase="Phase 2 (Национальный каталог)" />,
                ),
              },
              {
                path: 'km-orders',
                element: withSuspense(<MarkingPlaceholderPage title="Заказы КМ" phase="Phase 3 (СУЗ)" />),
              },
              {
                path: 'application-reports',
                element: withSuspense(<MarkingPlaceholderPage title="Контроль нанесения" phase="Phase 4" />),
              },
              {
                path: 'circulation',
                element: withSuspense(<MarkingPlaceholderPage title="Ввод в оборот" phase="Phase 5" />),
              },
              { path: 'sign-agents', element: withSuspense(<MarkingSignAgentsPage />) },
              { path: 'history', element: withSuspense(<MarkingHistoryPage />) },
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
                  { index: true, element: withSuspense(<AdminHomePage />) },
                  { path: 'users', element: withSuspense(<AdminUsersPage />) },
                  { path: 'companies', element: withSuspense(<AdminCompaniesPage />) },
                  { path: 'subscriptions', element: withSuspense(<AdminSubscriptionsPage />) },
                  { path: 'logs', element: withSuspense(<AdminLogsPage />) },
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
