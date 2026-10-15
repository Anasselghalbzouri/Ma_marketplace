/**
 * T-012 — routeur racine.
 *
 * Source : ENF-002 (mobile-first) + react-router-dom 7.
 *
 * Routes socle (T-012) :
 *  - `/`          : page d'accueil (hero + lien catalogue)
 *  - `/products`  : placeholder catalogue (câblé RTK Query, données T-028)
 *  - `/login`     : placeholder authentification (câblage T-014/T-016)
 *  - `*`          : 404 mobile
 *
 * Routes des modules M01–M11 : ajoutées par les tâches filles via
 * `createBrowserRouter` (lazy chunk par module).
 */

import type { ReactElement } from 'react';
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { HomePage } from '@/pages/HomePage';
import { CatalogPage } from '@/pages/CatalogPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { LoginPlaceholderPage } from '@/pages/LoginPlaceholderPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <AppShell>
        <HomePage />
      </AppShell>
    ),
  },
  {
    path: '/products',
    element: (
      <AppShell>
        <CatalogPage />
      </AppShell>
    ),
  },
  {
    path: '/login',
    element: (
      <AppShell>
        <LoginPlaceholderPage />
      </AppShell>
    ),
  },
  {
    path: '/login',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '*',
    element: (
      <AppShell>
        <NotFoundPage />
      </AppShell>
    ),
  },
]);

export function AppRouter(): ReactElement {
  return <RouterProvider router={router} />;
}