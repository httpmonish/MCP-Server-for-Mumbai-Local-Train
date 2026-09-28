import { describe, it, expect } from 'vitest';
import {
  fetchCorridorTelemetry,
  fetchTrainSchedule,
  calculateAttendanceRisk,
  generateDelayToken,
} from '../../lib/services/telemetryService';

describe('Interactive Suburban Telemetry & MCP Service Layer', () => {
  it('fetches corridor telemetry with real station clearance nodes', async () => {
    const data = await fetchCorridorTelemetry('central-main', 'DOWN');
    expect(data.corridor).toBe('central-main');
    expect(data.stations.length).toBeGreaterThanOrEqual(4);
    expect(data.stations[0].code).toBe('CSMT');
    expect(data.activeRake.trainNumber).toContain('95401');
  });

  it('generates 12-coach matrix with FOB alignment for schedule rakes', async () => {
    const rakes = await fetchTrainSchedule('TNA', 'CSMT', 'central-main');
    expect(rakes.length).toBeGreaterThanOrEqual(3);
    const fastRake = rakes[0];
    expect(fastRake.coachMatrix.length).toBe(12);
    expect(fastRake.coachMatrix[0].fobAlignmentText).toContain('staircase');
  });

  it('calculates deterministic attendance debarment risk for delayed train', async () => {
    const risk = await calculateAttendanceRisk('COMMUTER_98401', '95201', '09:30 AM');
    expect(risk.status).toBe('DEBARMENT_RISK');
    expect(risk.simulatedPercentage).toBe(74.3);
    expect(risk.willReachOnTime).toBe(false);
    expect(risk.contingencyProtocol).toBe('ISSUE_CR_DELAY_TOKEN');
  });

  it('calculates safe attendance status for on-time train', async () => {
    const risk = await calculateAttendanceRisk('COMMUTER_98401', '95401', '09:30 AM');
    expect(risk.status).toBe('SAFE');
    expect(risk.simulatedPercentage).toBe(75.4);
    expect(risk.willReachOnTime).toBe(true);
    expect(risk.contingencyProtocol).toBe('SPRINT_MATUNGA_WALK');
  });

  it('generates cryptographic SHA-256 Central Railway delay token', async () => {
    const token = await generateDelayToken(
      { name: 'Aditya Sharma', rollNumber: '211080042', college: 'VJTI Mumbai', hodEmail: 'hod.computers@vjti.ac.in' },
      { trainNumber: '#95201 SLOW', corridor: 'Central Main Line', delayMinutes: 6, failurePoint: 'Sig S-44' }
    );
    expect(token.tokenUuid).toContain('CR-TMS');
    expect(token.verificationSha256.length).toBe(32);
    expect(token.studentName).toBe('Aditya Sharma');
    expect(token.hodEmail).toBe('hod.computers@vjti.ac.in');
  });
});
