# Portfolio Video Demonstration Script (60–90 Seconds)

## Objective
Demonstrate an end-to-end multi-source data extraction pipeline running across a deployed web dashboard and an autonomous Claude Desktop MCP session.

---

## Segment Breakdown

### 0:00 – 0:20: The Problem & Web Dashboard
- **Visual:** Open the deployed dashboard on Vercel (`https://your-dashboard.vercel.app`).
- **Action:**
  1. Show the attendance card: point out a subject with `< 75%` showing an amber/rose alert badge.
  2. Select "Thane" to "Byculla" in the suburban train tracker: click "Find Trains" and showcase live departure countdown badges (`in 6 mins`, `in 18 mins`, `FAST`).
- **Talking Point:**
  > *"Academic portals lock student attendance behind slow, authenticated legacy interfaces with zero open APIs. I built this platform to scrape and normalize academic data alongside Mumbai suburban train schedules with sub-15ms Redis caching."*

### 0:20 – 0:45: Demonstrating Resilience & Degradation
- **Visual:** Switch to terminal or DevTools Network tab.
- **Action:**
  1. Trigger an attendance fetch while blocking upstream portal connectivity (or show cached sync timestamp).
  2. Point out the amber banner: `⚠️ Showing cached records from [timestamp] — live portal unreachable`.
- **Talking Point:**
  > *"Instead of returning a 500 error when the college server is down, the orchestrator implements the Cache-Aside pattern with atomic PostgreSQL upserts, serving historical records with a stale-data flag."*

### 0:45 – 1:15: Model Context Protocol (MCP) in Claude Desktop
- **Visual:** Bring Claude Desktop to the foreground.
- **Action:**
  1. Prompt Claude:
     > *"Check my attendance for semester 5. If my attendance is below 75% in any subject, find the next train from Thane to Byculla so I can make my 9:00 AM lecture."*
  2. Watch Claude trigger `get_student_attendance` followed by `get_next_train`.
  3. Show the synthesized output: Claude alerts on the low-attendance subject and recommends the exact Fast train departing Thane at 08:22 AM.
- **Talking Point:**
  > *"By wrapping this backend as an official Model Context Protocol server over stdio, LLMs can autonomously reason across disconnected proprietary sources in real time."*

### 1:15 – 1:30: Engineering Wrap-Up
- **Visual:** Display GitHub repository showing CI badges, test suite coverage (`pytest`), and Docker configuration.
- **Talking Point:**
  > *"The entire codebase is containerized, runs automated CI with Playwright and PostgreSQL in GitHub Actions, and is architected to degrade gracefully under failure."*
