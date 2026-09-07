'use strict';







function successRatio(runs) {
  if (!runs.length) return 1;
  const ok = runs.filter((r) => r.status === 'completed').length;
  return ok / runs.length;
}


function errorBudget(runs, target) {
  const allowed = 1 - Number(target || 0.99);
  if (allowed <= 0) return 0;
  const failed = runs.filter((r) => r.status === 'failed' || r.status === 'rejected').length;
  const burned = runs.length ? failed / runs.length : 0;
  return Math.max(0, 1 - burned / allowed);
}


function attainment(workflowName, runs, policy) {
  const scoped = runs.filter((r) => r.workflowName === workflowName);
  const ratio = successRatio(scoped);
  const target = Number((policy && policy.target) || 0.99);
  return {
    workflowName,
    runs: scoped.length,
    successRatio: Number(ratio.toFixed(4)),
    target,
    meeting: ratio >= target,
    errorBudgetRemaining: Number(errorBudget(scoped, target).toFixed(4)),
    ackWindowMins: Number((policy && policy.ackWindowMins) || 30),
  };
}


function ackWithinWindow(incident, ackWindowMins) {
  if (!incident || incident.acknowledgedAt == null) return false;
  const windowMs = Number(ackWindowMins || 30) * 60_000;
  return incident.acknowledgedAt - incident.openedAt <= windowMs;
}

module.exports = { successRatio, errorBudget, attainment, ackWithinWindow };
