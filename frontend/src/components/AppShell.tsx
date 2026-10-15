/**
 * T-012 — coquille applicative.
 *
 * Contient : header + slot principal. Conçu pour 360 px minimum (ENF-002).
 * Pas de sidebar en V1 mobile : tous les modules métier rendent dans `<main>`.
 */

import type { ReactElement, ReactNode } from 'react';
import { Header } from './Header';

export function AppShell({ children }: { children: ReactNode }): ReactElement {
  return (
    <div className="app-shell">
      <Header />
      <main className="app-main" id="main-content">
        {children}
      </main>
      <footer className="border-t border-ink-300 bg-surface px-4 py-3 text-center text-xs text-ink-500">
        {new Date().getFullYear()} — {`T-012 socle frontend`}
      </footer>
    </div>
  );
}