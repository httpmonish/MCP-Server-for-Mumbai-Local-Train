import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cross_tenant_strict_isolation(client: AsyncClient):
    # 1. Register Tenant A (College A)
    admin_a_email = f"admin_a_{uuid.uuid4().hex[:6]}@college-a.edu"
    reg_a = await client.post(
        "/auth/register",
        json={
            "org_name": "College A Mumbai",
            "org_type": "COLLEGE",
            "org_domain": "college-a.edu",
            "email": admin_a_email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_a.status_code == 201
    token_a = reg_a.json()["tokens"]["access_token"]
    org_a_id = reg_a.json()["organization"]["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Add member to College A
    stud_a_email = f"student_a_{uuid.uuid4().hex[:6]}@college-a.edu"
    add_stud_a = await client.post(
        "/organizations/members",
        headers=headers_a,
        json={"email": stud_a_email, "role": "STUDENT", "full_name": "College A Student"},
    )
    assert add_stud_a.status_code == 201
    stud_a_id = add_stud_a.json()["id"]

    # 2. Register Tenant B (Company B)
    admin_b_email = f"admin_b_{uuid.uuid4().hex[:6]}@company-b.com"
    reg_b = await client.post(
        "/auth/register",
        json={
            "org_name": "Company B Tech",
            "org_type": "COMPANY",
            "org_domain": "company-b.com",
            "email": admin_b_email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_b.status_code == 201
    token_b = reg_b.json()["tokens"]["access_token"]
    org_b_id = reg_b.json()["organization"]["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Add member to Company B
    emp_b_email = f"employee_b_{uuid.uuid4().hex[:6]}@company-b.com"
    add_emp_b = await client.post(
        "/organizations/members",
        headers=headers_b,
        json={"email": emp_b_email, "role": "EMPLOYEE", "full_name": "Company B Employee"},
    )
    assert add_emp_b.status_code == 201
    emp_b_id = add_emp_b.json()["id"]

    # 3. VERIFICATION: Admin A lists members -> sees only College A
    list_a = await client.get("/organizations/members", headers=headers_a)
    assert list_a.status_code == 200
    emails_in_a = [m["email"] for m in list_a.json()["items"]]
    assert admin_a_email in emails_in_a
    assert stud_a_email in emails_in_a
    assert admin_b_email not in emails_in_a
    assert emp_b_email not in emails_in_a

    # 4. VERIFICATION: Admin B lists members -> sees only Company B
    list_b = await client.get("/organizations/members", headers=headers_b)
    assert list_b.status_code == 200
    emails_in_b = [m["email"] for m in list_b.json()["items"]]
    assert admin_b_email in emails_in_b
    assert emp_b_email in emails_in_b
    assert admin_a_email not in emails_in_b
    assert stud_a_email not in emails_in_b

    # 5. ATTACK: Admin A attempts IDOR deletion of Member B (from Company B)
    attack_del = await client.delete(f"/organizations/members/{emp_b_id}", headers=headers_a)
    assert attack_del.status_code == 404
    assert "not found" in attack_del.json()["detail"].lower()

    # Verify Member B was NOT deleted
    check_b = await client.get("/organizations/members", headers=headers_b)
    assert emp_b_email in [m["email"] for m in check_b.json()["items"]]

    # 6. ATTACK: Admin B attempts IDOR deletion of Member A (from College A)
    attack_del_rev = await client.delete(f"/organizations/members/{stud_a_id}", headers=headers_b)
    assert attack_del_rev.status_code == 404

    # Verify Member A was NOT deleted
    check_a = await client.get("/organizations/members", headers=headers_a)
    assert stud_a_email in [m["email"] for m in check_a.json()["items"]]

    # 7. VERIFICATION: GET /organizations/me returns respective tenant
    org_me_a = await client.get("/organizations/me", headers=headers_a)
    assert org_me_a.json()["id"] == org_a_id
    assert org_me_a.json()["name"] == "College A Mumbai"

    org_me_b = await client.get("/organizations/me", headers=headers_b)
    assert org_me_b.json()["id"] == org_b_id
    assert org_me_b.json()["name"] == "Company B Tech"
