import io
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bulk_csv_import_success(client: AsyncClient):
    # Register org
    admin_email = f"dean_{uuid.uuid4().hex[:6]}@coep.ac.in"
    reg_payload = {
        "org_name": "COEP Tech University",
        "org_type": "COLLEGE",
        "org_domain": "coep.ac.in",
        "email": admin_email,
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    admin_token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Prepare valid CSV
    u1 = f"s1_{uuid.uuid4().hex[:6]}@coep.ac.in"
    u2 = f"s2_{uuid.uuid4().hex[:6]}@coep.ac.in"
    u3 = f"t1_{uuid.uuid4().hex[:6]}@coep.ac.in"

    csv_content = (
        "email,role,name\n"
        f"{u1},STUDENT,Student One\n"
        f"{u2},STUDENT,Student Two\n"
        f"{u3},TEACHER,Professor Alpha\n"
    )

    files = {"file": ("members.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

    upload_res = await client.post("/organizations/members/bulk", headers=headers, files=files)
    assert upload_res.status_code == 200
    data = upload_res.json()
    assert data["total_rows"] == 3
    assert data["valid_rows"] == 3
    assert data["invalid_rows"] == 0
    assert data["created_count"] == 3
    assert len(data["errors"]) == 0
    assert len(data["created_members"]) == 3


@pytest.mark.asyncio
async def test_bulk_csv_import_with_row_errors_and_sanitization(client: AsyncClient):
    # Register org
    admin_email = f"lead_{uuid.uuid4().hex[:6]}@reliance.in"
    reg_payload = {
        "org_name": "Reliance Digital BKC",
        "org_type": "COMPANY",
        "org_domain": "reliance.in",
        "email": admin_email,
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    admin_token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Pre-insert a member to test DB duplicate detection
    existing_email = f"emp_exist_{uuid.uuid4().hex[:6]}@reliance.in"
    await client.post(
        "/organizations/members",
        headers=headers,
        json={"email": existing_email, "role": "EMPLOYEE", "full_name": "Existing Emp"},
    )

    # Prepare CSV with:
    # 1. Valid row with CSV injection formula attempt in name
    # 2. Invalid email format
    # 3. Invalid role
    # 4. Prohibited PLATFORM_ADMIN role
    # 5. Intra-batch duplicate
    # 6. Database duplicate
    u_valid = f"valid_{uuid.uuid4().hex[:6]}@reliance.in"
    u_dup = f"dup_{uuid.uuid4().hex[:6]}@reliance.in"

    csv_content = (
        "email,role,full_name\n"
        f"{u_valid},EMPLOYEE,=cmd|' /C calc'!A0\n"
        "bad-email-format,EMPLOYEE,Bad Email Guy\n"
        f"role_bad_{uuid.uuid4().hex[:4]}@reliance.in,SUPER_HERO,Hero Person\n"
        f"plat_{uuid.uuid4().hex[:4]}@reliance.in,PLATFORM_ADMIN,Evil Admin\n"
        f"{u_dup},EMPLOYEE,First Dup\n"
        f"{u_dup},EMPLOYEE,Second Dup\n"
        f"{existing_email},EMPLOYEE,Already In DB\n"
    )

    files = {"file": ("bulk_test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    upload_res = await client.post("/organizations/members/bulk", headers=headers, files=files)
    assert upload_res.status_code == 200
    data = upload_res.json()

    assert data["total_rows"] == 7
    assert data["valid_rows"] == 2  # u_valid and First Dup
    assert data["created_count"] == 2
    assert data["invalid_rows"] == 5

    # Check errors list contains itemized reports
    err_messages = [e["error"] for e in data["errors"]]
    assert any("Invalid email format" in msg for msg in err_messages)
    assert any("Invalid role" in msg for msg in err_messages)
    assert any("PLATFORM_ADMIN" in msg for msg in err_messages)
    assert any("Duplicate email found within the same CSV upload" in msg for msg in err_messages)
    assert any("already registered" in msg for msg in err_messages)

    # Verify formula was sanitized with prepended quote
    created_names = [m["full_name"] for m in data["created_members"]]
    assert "'=cmd|' /C calc'!A0" in created_names


@pytest.mark.asyncio
async def test_bulk_csv_file_validation_errors(client: AsyncClient):
    admin_email = f"dean_{uuid.uuid4().hex[:6]}@iitb.ac.in"
    reg_payload = {
        "org_name": "IIT Bombay Powai",
        "org_type": "COLLEGE",
        "org_domain": "iitb.ac.in",
        "email": admin_email,
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    admin_token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Non-csv extension -> 400
    bad_ext_file = {"file": ("data.txt", io.BytesIO(b"email,role\ntest@test.com,STUDENT"), "text/plain")}
    res1 = await client.post("/organizations/members/bulk", headers=headers, files=bad_ext_file)
    assert res1.status_code == 400
    assert "must have a .csv extension" in res1.json()["detail"]

    # 2. Empty file -> 400
    empty_file = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    res2 = await client.post("/organizations/members/bulk", headers=headers, files=empty_file)
    assert res2.status_code == 400
    assert "empty" in res2.json()["detail"]

    # 3. Missing required 'role' header -> 400
    missing_header_file = {
        "file": ("no_role.csv", io.BytesIO(b"email,name\ntest@test.com,Student"), "text/csv")
    }
    res3 = await client.post("/organizations/members/bulk", headers=headers, files=missing_header_file)
    assert res3.status_code == 400
    assert "CSV must contain a 'role' column" in res3.json()["detail"]
