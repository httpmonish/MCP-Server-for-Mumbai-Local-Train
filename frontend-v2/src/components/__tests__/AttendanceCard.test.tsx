import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AttendanceCard } from "../AttendanceCard";
import * as academicHooks from "../../hooks/useAcademic";

describe("AttendanceCard Component", () => {
  it("renders critical alert badge when overall attendance is below 75%", () => {
    vi.spyOn(academicHooks, "useAttendance").mockReturnValue({
      data: {
        data: [
          { subject_name: "Operating Systems", total_conducted: 50, total_attended: 30, percentage: 60.0 },
          { subject_name: "Compiler Design", total_conducted: 50, total_attended: 35, percentage: 70.0 },
        ],
        source: "live",
        stale: false,
      },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      isFetching: false,
    } as any);

    render(<AttendanceCard />);

    expect(screen.getByText("Below 75% Criteria")).toBeDefined();
    expect(screen.getByText("65.0%")).toBeDefined();
    expect(screen.getByText("Operating Systems")).toBeDefined();
  });
});
