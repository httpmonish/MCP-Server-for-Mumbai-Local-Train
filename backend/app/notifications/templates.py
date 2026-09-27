import html
from typing import Any, Dict, Tuple


def render_attendance_alert(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Render attendance below threshold notification.
    Returns (title, plain_text_body, html_body).
    """
    percentage = payload.get("percentage", 0.0)
    min_required = payload.get("min_required", 75.0)
    shortage_count = payload.get("shortage_count", 0)
    policy_name = html.escape(str(payload.get("policy_name") or "Statutory Attendance Policy"))

    title = f"⚠️ Attendance Alert: {percentage:.1f}% (Below Required {min_required:.1f}%)"
    
    plain_body = (
        f"Your current attendance has fallen to {percentage:.1f}%, which is below the mandatory "
        f"minimum threshold of {min_required:.1f}% under '{policy_name}'.\n\n"
        f"Shortage count: {shortage_count} sessions.\n"
        f"Please attend upcoming scheduled sessions to restore compliance."
    )

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #e53e3e; margin-top: 0;">⚠️ Attendance Threshold Warning</h2>
        <p>Your current attendance is <strong>{percentage:.1f}%</strong>, which is below the required <strong>{min_required:.1f}%</strong> policy threshold.</p>
        <div style="background-color: #fff5f5; padding: 12px; border-radius: 6px; margin: 16px 0; border-left: 4px solid #e53e3e;">
            <p style="margin: 0; color: #c53030;"><strong>Policy:</strong> {policy_name}</p>
            <p style="margin: 4px 0 0 0; color: #c53030;"><strong>Shortage:</strong> {shortage_count} sessions deficit</p>
        </div>
        <p style="color: #718096; font-size: 14px;">TransitPulse Automated Telemetry Alert</p>
    </div>
    """
    return title, plain_body, html_body


def render_commute_risk_alert(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Render commute delay risk alert.
    """
    slot_title = html.escape(str(payload.get("slot_title") or "Scheduled Class"))
    origin = html.escape(str(payload.get("origin_station") or "Origin"))
    dest = html.escape(str(payload.get("destination_station") or "Destination"))
    start_time = html.escape(str(payload.get("scheduled_start") or ""))
    est_arrival = html.escape(str(payload.get("estimated_arrival") or ""))
    margin = payload.get("arrival_margin_minutes", 0)
    risk_status = html.escape(str(payload.get("risk_status") or "AT_RISK"))

    title = f"🚆 Commute Delay Alert: {slot_title} ({risk_status})"

    plain_body = (
        f"Commute telemetry alert for your upcoming event '{slot_title}' scheduled at {start_time}.\n\n"
        f"Route: {origin} -> {dest}\n"
        f"Estimated Final Arrival: {est_arrival}\n"
        f"Arrival Margin: {margin} minutes\n"
        f"Commute Risk Status: {risk_status}\n\n"
        f"Please consider alternative transport or departing immediately."
    )

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #dd6b20; margin-top: 0;">🚆 Commute Feasibility Alert</h2>
        <p>Commute telemetry indicates a potential delay for <strong>{slot_title}</strong>.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 6px 0; color: #718096;">Route:</td><td style="font-weight: 600;">{origin} &rarr; {dest}</td></tr>
            <tr><td style="padding: 6px 0; color: #718096;">Scheduled Start:</td><td style="font-weight: 600;">{start_time}</td></tr>
            <tr><td style="padding: 6px 0; color: #718096;">Estimated Arrival:</td><td style="font-weight: 600; color: #c05621;">{est_arrival} (Margin: {margin}m)</td></tr>
        </table>
        <p style="color: #718096; font-size: 14px;">TransitPulse Real-Time Intelligence</p>
    </div>
    """
    return title, plain_body, html_body


def render_class_reminder(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Render 30-minute upcoming class reminder.
    """
    slot_title = html.escape(str(payload.get("slot_title") or "Upcoming Class"))
    start_time = html.escape(str(payload.get("start_time") or ""))
    location = html.escape(str(payload.get("location_name") or "Main Campus"))
    station = html.escape(str(payload.get("station_code") or "Nearest Station"))

    title = f"⏰ Reminder: {slot_title} starts in 30 minutes ({start_time})"

    plain_body = (
        f"Your scheduled session '{slot_title}' starts at {start_time}.\n\n"
        f"Venue: {location} (Nearest Station: {station})\n\n"
        f"Have a productive session!"
    )

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #3182ce; margin-top: 0;">⏰ Class Reminder</h2>
        <p><strong>{slot_title}</strong> starts in approximately 30 minutes at <strong>{start_time}</strong>.</p>
        <p style="color: #4a5568;"><strong>Location:</strong> {location} ({station})</p>
        <p style="color: #718096; font-size: 14px;">TransitPulse Schedule Engine</p>
    </div>
    """
    return title, plain_body, html_body
