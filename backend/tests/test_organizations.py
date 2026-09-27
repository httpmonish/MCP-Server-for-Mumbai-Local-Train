import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_organization_success(client: AsyncClient):
    reg_payload = {
        "org_name": "VJTI Mumbai Engineering",
        "org_type": "COLLEGE",
        "org_domain": "vjti.ac.in",
        "email": f"dean_{uuid.uuid4().hex[:6]}@vjti.ac.in",
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    token = reg_res.json()["tokens"]["access_token"]

    # GET /organizations/me
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.get("/organizations/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "VJTI Mumbai Engineering"
    assert data["type"] == "COLLEGE"
    assert data["domain"] == "vjti.ac.in"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_update_my_organization_by_admin(client: AsyncClient):
    reg_payload = {
        "org_name": "Initial Tech Corp",
        "org_type": "COMPANY",
        "org_domain": "initial.com",
        "email": f"hr_{uuid.uuid4().hex[:6]}@initial.com",
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # PATCH /organizations/me
    patch_res = await client.patch(
        "/organizations/me",
        headers=headers,
        json={"name": "Updated Tech Corp Global", "domain": "techcorp.global"},
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert patch_data["name"] == "Updated Tech Corp Global"
    assert patch_data["domain"] == "techcorp.global"


@pytest.mark.asyncio
async def test_add_and_list_members(client: AsyncClient):
    # 1. Register Org Admin
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@spit.ac.in"
    reg_payload = {
        "org_name": "SPIT Mumbai",
        "org_type": "COLLEGE",
        "org_domain": "spit.ac.in",
        "email": admin_email,
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    admin_token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Add Member (Teacher)
    teacher_email = f"prof_{uuid.uuid4().hex[:6]}@spit.ac.in"
    add_res1 = await client.post(
        "/organizations/members",
        headers=headers,
        json={
            "email": teacher_email,
            "role": "TEACHER",
            "full_name": "Prof. Sharma",
            "password": "TeacherPass123!",
        },
    )
    assert add_res1.status_code == 201
    assert add_res1.json()["email"] == teacher_email
    assert add_res1.json()["role"] == "TEACHER"
    assert add_res1.json()["full_name"] == "Prof. Sharma"

    # 3. Add Member (Student)
    student_email = f"stud_{uuid.uuid4().hex[:6]}@spit.ac.in"
    add_res2 = await client.post(
        "/organizations/members",
        headers=headers,
        json={
            "email": student_email,
            "role": "STUDENT",
            "full_name": "Aarav Patel",
        },
    )
    assert add_res2.status_code == 201
    student_id = add_res2.json()["id"]

    # 4. List Members
    list_res = await client.get("/organizations/members", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 3  # Admin + Teacher + Student
    emails = [item["email"] for item in list_data["items"]]
    assert admin_email in emails
    assert teacher_email in emails
    assert student_email in emails

    # 5. Filter by role
    role_filter_res = await client.get("/organizations/members?role=STUDENT", headers=headers)
    assert role_filter_res.status_code == 200
    student_items = role_filter_res.json()["items"]
    assert all(item["role"] == "STUDENT" for item in student_items)

    # 6. Search by name
    search_res = await client.get("/organizations/members?search=Aarav", headers=headers)
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1
    assert search_res.json()["items"][0]["full_name"] == "Aarav Patel"

    # 7. Delete Member (Student)
    del_res = await client.delete(f"/organizations/members/{student_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify removal
    post_del_res = await client.get("/organizations/members?search=Aarav", headers=headers)
    assert post_del_res.status_code == 200
    assert post_del_res.json()["total"] == 0


@pytest.mark.asyncio
async def test_member_guards_and_constraints(client: AsyncClient):
    admin_email = f"head_{uuid.uuid4().hex[:6]}@tech.in"
    reg_payload = {
        "org_name": "Security Labs",
        "org_type": "COMPANY",
        "org_domain": "tech.in",
        "email": admin_email,
        "password": "SecurePassword123!",
    }
    reg_res = await client.post("/auth/register", json=reg_payload)
    admin_id = reg_res.json()["user"]["id"]
    admin_token = reg_res.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Attempt to add member with PLATFORM_ADMIN role -> 422 or 400
    plat_res = await client.post(
        "/organizations/members",
        headers=headers,
        json={
            "email": f"hacker_{uuid.uuid4().hex[:6]}@tech.in",
            "role": "PLATFORM_ADMIN",
        },
    )
    assert plat_res.status_code in (400, 422)

    # 2. Attempt admin self-deletion -> 400
    self_del_res = await client.delete(f"/organizations/members/{admin_id}", headers=headers)
    assert self_del_res.status_code == 400
    assert "cannot delete their own account" in self_del_res.json()["detail"]

    # 3. Non-admin forbidden from adding members
    emp_email = f"emp_{uuid.uuid4().hex[:6]}@tech.in"
    add_emp_res = await client.post(
        "/organizations/members",
        headers=headers,
        json={
            "email": emp_email,
            "role": "EMPLOYEE",
            "password": "EmpPassword123!",
        },
    )
    assert add_emp_res.status_code == 201

    # Login as employee
    login_res = await client.post(
        "/auth/login",
        json={"email": emp_email, "password": "EmpPassword123!"},
    )
    emp_token = login_res.json()["tokens"]["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Employee tries to add another member -> 403
    emp_add_attempt = await client.post(
        "/organizations/members",
        headers=emp_headers,
        json={"email": f"other_{uuid.uuid4().hex[:6]}@tech.in", "role": "EMPLOYEE"},
    )
    assert emp_add_attempt.status_code == 403
