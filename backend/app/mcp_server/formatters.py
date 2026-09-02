try:
    from backend.mcp_server.formatters import format_attendance_report, format_exam_schedule, format_train_schedule
except ImportError:
    from mcp_server.formatters import format_attendance_report, format_exam_schedule, format_train_schedule

__all__ = ["format_attendance_report", "format_exam_schedule", "format_train_schedule"]
