# Case Scope

## meta
- case_id: 20260726-d3ctf-ghost
- created: 2026-07-26T04:31:40+07:00
- operator: local
- primary_skill: ctf-sandbox-orchestrator -> competition-web-runtime
- lead_role: lead
- specialist_roles: [cie, cpe, cre]

## auth
- status: granted
- basis: ctf_public
- evidence_of_auth: User supplied D3CTF challenge URL

## in_scope
- assets:
  - https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf
- surfaces:
  - web
  - api
  - frontend
- activities:
  - recon
  - exploit_validate
  - report

## out_of_scope
- assets:
  - Any host not required by the challenge path
- activities:
  - denial_of_service
  - phishing real users
  - unrelated data collection

## network_profile
- mode: authorized_target_only
- notes: |
    Only the challenge URL and first-party assets required by the served app are in scope.

## deliverables
- report: true
- field_journal: true
- diagrams: false
- timeline: true

## constraints
- timebox: active session
- stealth: low
- data_handling: no_user_pii

## signoff
- ready_for_act: true
- checklist:
  - [x] auth.status = granted
  - [x] in_scope.assets non-empty OR offline sample path set
  - [x] network_profile.mode chosen
  - [x] out_of_scope reviewed
