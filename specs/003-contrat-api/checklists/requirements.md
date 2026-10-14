# Specification Quality Checklist: Contrat d'API et matrice d'autorisations (T-003)

**Purpose**: Valider la complétude et la qualité de la spécification avant de passer à la planification
**Created**: 2026-10-14
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain unresolved beyond the agreed maximum of three
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Trois marqueurs `[NEEDS CLARIFICATION]` ont été volontairement conservés (FR-016 panier visiteur
  H-01, FR-017 périmètre de la supervision administrateur F013/UC-023, FR-018 levée d'une mesure de
  modération), conformément à la limite de trois et à la demande explicite de l'architecte pour cette
  tâche. Ils ne bloquent pas `/speckit-plan` : une hypothèse par défaut est documentée pour chacun,
  alignée sur les statuts `allow_hyp`/HYPOTHÈSE déjà portés par `contracts/authorization-matrix.yaml`,
  et aucune n'est développée avant validation par @user au point de contrôle CP-1 (SC-008).
- Les écarts UML U-01 et U-02 (constats du plan de Compass) ne sont pas des `[NEEDS CLARIFICATION]` :
  ils sont traités comme des actions réservées mais signalées bloquées (FR-015, section « Capacités
  hors matrice §5 et actions réservées »), conformément à la demande explicite.
- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`.
