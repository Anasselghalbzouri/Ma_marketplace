/**
 * T-012 — tests des composants d'\u00e9tat (LoadingState, ErrorState, EmptyState).
 *
 * Objectif : accessibilit\u00e9 (role, aria-live, aria-label) et libell\u00e9s
 * localis\u00e9s par d\u00e9faut via t().
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import type { ReactElement } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import { EmptyState, ErrorState, LoadingState } from '@/components/States';

function withI18n(node: ReactElement): ReactElement {
  return <I18nextProvider i18n={i18n}>{node}</I18nextProvider>;
}

describe('States components', () => {
  it('LoadingState expose role="status" et aria-live="polite"', () => {
    render(withI18n(<LoadingState />));
    const el = screen.getByRole('status');
    expect(el).toHaveAttribute('aria-live', 'polite');
    expect(el.textContent).toContain('Chargement');
  });

  it('LoadingState accepte un libell\u00e9 explicite', () => {
    render(withI18n(<LoadingState label="Patientez\u2026" />));
    const el = screen.getByRole('status');
    expect(el.textContent).toContain('Patientez');
  });

  it('ErrorState rend un titre et un bouton "R\u00e9essayer"', () => {
    const onRetry = () => undefined;
    render(withI18n(<ErrorState title="Oups" detail="X" onRetry={onRetry} />));
    const alert = screen.getByRole('alert');
    expect(alert.textContent).toContain('Oups');
    expect(alert.textContent).toContain('X');
    expect(screen.getByRole('button', { name: /R\u00e9essayer/i })).toBeInTheDocument();
  });

  it('EmptyState rend un message et une action', () => {
    render(withI18n(
      <EmptyState
        title="Vide"
        action={<a href="/x">Aller</a>}
      />,
    ));
    expect(screen.getByText('Vide')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Aller' })).toBeInTheDocument();
  });
});