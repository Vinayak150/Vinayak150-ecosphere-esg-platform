#!/usr/bin/env python3
"""Seed EcoSphere with realistic demo data spanning the past 12 months.

Usage:
    cd backend
    python -m scripts.seed_data          # seed if empty / top-up counts
    python -m scripts.seed_data --reset  # clear demo data and re-seed
"""

from __future__ import annotations

import argparse
import random
import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from itertools import product

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.auth.models import (
    ActivityLog,
    Department,
    Employee,
    Organization,
    Role,
    User,
    UserRole,
)
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.environmental.models import (
    CarbonTransaction,
    EmissionFactor,
    EnvironmentalGoal,
    GoalStatus,
    ProductEsgProfile,
    TransactionStatus,
)
from app.modules.gamification.models import (
    Badge,
    BadgeStatus,
    Challenge,
    ChallengeDifficulty,
    ChallengeParticipation,
    ChallengeStatus,
    EmployeeBadge,
    ParticipationApproval,
    Reward,
    RewardRedemption,
    RewardStatus,
)
from app.modules.governance.models import (
    AcknowledgementStatus,
    Audit,
    AuditStatus,
    ComplianceIssue,
    ComplianceIssueStatus,
    ComplianceSeverity,
    Policy,
    PolicyAcknowledgement,
    PolicyStatus,
)
from app.modules.social.models import (
    ApprovalStatus,
    CsrActivity,
    CSRActivityStatus,
    EmployeeParticipation,
)
from app.shared.models.base import EntityStatus, UserStatus

random.seed(42)

TODAY = date.today()
START_DATE = TODAY - timedelta(days=365)
DEFAULT_PASSWORD = "Employee123!"

# ---------------------------------------------------------------------------
# Reference data (no lorem ipsum)
# ---------------------------------------------------------------------------

EXTRA_DEPARTMENTS = [
    ("human-resources", "Human Resources", "HR"),
    ("finance", "Finance & Accounting", "FIN"),
    ("engineering", "Engineering & R&D", "ENG"),
    ("sustainability", "Sustainability Office", "SUS"),
    ("facilities", "Facilities Management", "FAC"),
]

FIRST_NAMES = [
    "Aisha", "Ravi", "Mei", "Carlos", "Fatima", "James", "Priya", "Oliver",
    "Yuki", "Amara", "Lucas", "Sofia", "Noah", "Elena", "Arjun", "Chloe",
    "Daniel", "Hana", "Marcus", "Leila", "Ethan", "Ingrid", "Raj", "Nina",
    "Thomas", "Zara", "Benjamin", "Keiko", "Andre", "Maya", "Henry", "Lina",
    "Samuel", "Anika", "Victor", "Grace", "Omar", "Clara", "David", "Isabella",
    "Michael", "Aaliyah", "William", "Emily", "Joseph", "Hannah", "Alexander",
    "Olivia", "Christopher", "Sophia",
]

LAST_NAMES = [
    "Patel", "Chen", "Garcia", "Johnson", "Kim", "Williams", "Singh", "Brown",
    "Martinez", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Moore", "Lee", "Walker", "Hall", "Allen", "Young",
    "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker",
    "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips",
    "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez",
    "Morris", "Rogers", "Reed", "Cook", "Morgan",
]

DESIGNATIONS = [
    "Sustainability Analyst", "ESG Coordinator", "Operations Manager",
    "Manufacturing Engineer", "Supply Chain Specialist", "HR Business Partner",
    "Financial Controller", "Environmental Technician", "Quality Assurance Lead",
    "Facilities Supervisor", "Data Analyst", "Compliance Officer",
    "Product Manager", "Research Scientist", "Logistics Coordinator",
    "Energy Manager", "CSR Program Lead", "Internal Auditor",
    "Procurement Specialist", "Safety Officer",
]

EMISSION_FACTORS = [
    ("Grid Electricity", "Energy", "kWh", Decimal("0.4500"), "Regional grid mix average"),
    ("Natural Gas Combustion", "Energy", "m³", Decimal("1.9600"), "Facility heating and boilers"),
    ("Diesel Fleet Fuel", "Transport", "L", Decimal("2.6800"), "Company vehicle diesel"),
    ("Petrol Fleet Fuel", "Transport", "L", Decimal("2.3100"), "Company vehicle petrol"),
    ("Business Air Travel", "Travel", "km", Decimal("0.2550"), "Short-haul flight emissions"),
    ("Refrigerant R-410A Leakage", "Refrigerants", "kg", Decimal("2088.0000"), "HVAC maintenance"),
    ("Waste to Landfill", "Waste", "kg", Decimal("0.5800"), "Non-recycled office waste"),
    ("Recycled Paper Consumption", "Procurement", "kg", Decimal("0.9200"), "Office paper lifecycle"),
    ("Steam Generation", "Energy", "kg", Decimal("0.1830"), "Industrial process steam"),
    ("Liquefied Petroleum Gas", "Energy", "kg", Decimal("3.0100"), "Canteen and backup generators"),
]

CARBON_ACTIVITIES = [
    "Monthly electricity consumption — {dept}",
    "Natural gas heating — {dept}",
    "Fleet diesel refuel — {dept}",
    "Business travel — {dept}",
    "Waste disposal run — {dept}",
    "HVAC refrigerant top-up — {dept}",
    "Steam usage — production line",
    "LPG backup generator test — {dept}",
    "Office paper procurement — {dept}",
    "Petrol fleet refuel — {dept}",
]

CSR_TEMPLATES = [
    ("Beach Cleanup Drive", "Environment", "Volunteer shoreline litter removal and recycling sort."),
    ("Tree Plantation Week", "Environment", "Native species planting across company campuses."),
    ("STEM Mentorship Program", "Education", "Employees mentor students in local schools."),
    ("Food Bank Sorting Shift", "Community", "Sort and pack donations for regional food banks."),
    ("Digital Literacy Workshop", "Education", "Teach basic computer skills to seniors."),
    ("Blood Donation Camp", "Health", "Organize on-site blood donation with Red Cross partners."),
    ("Park Restoration Project", "Environment", "Trail maintenance and invasive species removal."),
    ("Coding for Nonprofits", "Technology", "Build websites for local charities."),
    ("Winter Clothing Drive", "Community", "Collect coats and blankets for shelters."),
    ("River Water Quality Survey", "Environment", "Citizen science sampling with environmental NGO."),
    ("Inclusive Hiring Fair", "Diversity", "Support job seekers with disabilities at career fair."),
    ("Solar Panel Awareness Day", "Environment", "Community workshop on residential solar adoption."),
    ("Elder Care Companion Visits", "Community", "Weekly visits to assisted living facilities."),
    ("Urban Garden Build", "Environment", "Construct raised beds for community food garden."),
    ("Disaster Relief Packing", "Community", "Assemble hygiene kits for flood-affected regions."),
]

POLICY_TITLES = [
    ("Code of Business Conduct", "2.1"),
    ("Anti-Bribery and Corruption Policy", "1.4"),
    ("Data Privacy and Protection Policy", "3.0"),
    ("Health and Safety Policy", "4.2"),
    ("Environmental Management Policy", "2.0"),
    ("Whistleblower Protection Policy", "1.1"),
    ("Equal Opportunity Employment Policy", "3.3"),
    ("Information Security Policy", "5.0"),
    ("Supplier Code of Conduct", "2.5"),
    ("Conflict of Interest Policy", "1.3"),
    ("Remote Work Policy", "2.0"),
    ("Travel and Expense Policy", "3.1"),
    ("Records Retention Policy", "1.0"),
    ("Social Media Usage Policy", "1.2"),
    ("Sustainability Reporting Policy", "1.0"),
    ("Anti-Harassment Policy", "2.2"),
    ("Gift and Hospitality Policy", "1.1"),
    ("Intellectual Property Policy", "2.0"),
    ("Crisis Communication Policy", "1.0"),
    ("Carbon Reduction Targets Policy", "1.0"),
    ("Water Stewardship Policy", "1.0"),
    ("Waste Minimization Policy", "1.2"),
    ("Community Engagement Policy", "1.0"),
    ("Board Governance Charter", "3.0"),
    ("ESG Disclosure Policy", "1.0"),
]

AUDIT_TITLES = [
    "ISO 14001 Environmental Management Review",
    "ISO 45001 Occupational Health & Safety Audit",
    "Energy Efficiency Compliance Check",
    "Waste Handling and Disposal Audit",
    "Supplier ESG Due Diligence Review",
    "GHG Inventory Verification",
    "Water Usage and Discharge Audit",
    "Hazardous Materials Storage Inspection",
    "Carbon Offset Procurement Review",
    "Renewable Energy Contract Audit",
    "Fleet Emissions Data Quality Review",
    "Refrigerant Management Compliance Audit",
    "Sustainability KPI Data Integrity Check",
    "CSR Program Effectiveness Review",
    "Policy Acknowledgement Compliance Audit",
]

CHALLENGE_TEMPLATES = [
    ("Bike to Work Week", "Transport", "Cycle to office at least 3 days this week.", 75, "EASY"),
    ("Zero-Waste Lunch Challenge", "Waste", "Pack a waste-free lunch for 5 consecutive days.", 50, "EASY"),
    ("Energy Audit at Home", "Energy", "Complete a home energy assessment and share findings.", 100, "MEDIUM"),
    ("Plastic-Free July Sprint", "Waste", "Avoid single-use plastics for 7 days.", 80, "MEDIUM"),
    ("Green Commute Month", "Transport", "Use public transit or carpool for 10 trips.", 120, "MEDIUM"),
    ("Water Conservation Challenge", "Water", "Reduce personal water use by 20% for 2 weeks.", 90, "MEDIUM"),
    ("Sustainable Procurement Quiz", "Education", "Score 90%+ on the sustainable buying quiz.", 40, "EASY"),
    ("Office Energy Shutdown", "Energy", "Ensure lights and equipment off after hours for 2 weeks.", 60, "EASY"),
    ("Community Tree Planting", "Community", "Plant 5 trees in a community greening event.", 150, "HARD"),
    ("Carbon Footprint Calculator", "Education", "Calculate and document your monthly carbon footprint.", 70, "EASY"),
    ("Meatless Monday Month", "Lifestyle", "Skip meat every Monday for 4 weeks.", 55, "EASY"),
    ("E-Waste Recycling Drive", "Waste", "Recycle 3 personal electronic devices responsibly.", 85, "MEDIUM"),
    ("Solar Awareness Ambassador", "Energy", "Host a lunch-and-learn on renewable energy.", 130, "HARD"),
    ("Paperless Office Week", "Waste", "Use only digital documents for one full week.", 65, "EASY"),
    ("Green Team Innovation", "Innovation", "Propose one actionable sustainability improvement.", 200, "EXPERT"),
    ("Local Farmers Market Visit", "Lifestyle", "Shop at a local farmers market 4 times.", 45, "EASY"),
    ("LED Bulb Replacement", "Energy", "Replace 5 incandescent bulbs with LEDs at home.", 50, "EASY"),
    ("Sustainable Fashion Month", "Lifestyle", "No fast-fashion purchases for 30 days.", 110, "HARD"),
    ("River Cleanup Volunteer", "Community", "Participate in a river or park cleanup event.", 140, "HARD"),
    ("Composting Starter", "Waste", "Start home composting and maintain for 3 weeks.", 95, "MEDIUM"),
    ("Green Reading Club", "Education", "Read and discuss an ESG book with colleagues.", 60, "EASY"),
    ("Renewable Energy Switch", "Energy", "Switch home utility to a green energy tariff.", 180, "EXPERT"),
    ("Sustainable Commute Streak", "Transport", "30-day streak of non-car commuting.", 250, "EXPERT"),
    ("Biodiversity Photo Challenge", "Environment", "Document 10 local species on company grounds.", 70, "MEDIUM"),
    ("ESG Lunch & Learn Host", "Education", "Organize an ESG awareness session for your team.", 160, "HARD"),
]

BADGE_DEFINITIONS = [
    ("Green Starter", "Complete your first approved challenge", {"rule": "approved_challenges", "threshold": 1}, "🌱"),
    ("Eco Explorer", "Earn 100 XP from challenges", {"rule": "total_xp", "threshold": 100}, "🌍"),
    ("Sustainability Champion", "Earn 500 XP from challenges", {"rule": "total_xp", "threshold": 500}, "🏆"),
    ("Challenge Veteran", "Complete 5 approved challenges", {"rule": "approved_challenges", "threshold": 5}, "⭐"),
    ("Challenge Master", "Complete 10 approved challenges", {"rule": "approved_challenges", "threshold": 10}, "🎖️"),
    ("Carbon Crusher", "Complete 3 transport challenges", {"rule": "approved_challenges", "threshold": 3}, "🚲"),
    ("Waste Warrior", "Complete 3 waste reduction challenges", {"rule": "approved_challenges", "threshold": 3}, "♻️"),
    ("Energy Saver", "Complete 3 energy challenges", {"rule": "approved_challenges", "threshold": 3}, "⚡"),
    ("Water Guardian", "Earn 200 XP", {"rule": "total_xp", "threshold": 200}, "💧"),
    ("Community Hero", "Complete 2 community challenges", {"rule": "approved_challenges", "threshold": 2}, "🤝"),
    ("Green Commuter", "Earn 150 XP", {"rule": "total_xp", "threshold": 150}, "🚌"),
    ("Paperless Pro", "Earn 250 XP", {"rule": "total_xp", "threshold": 250}, "📱"),
    ("Tree Hugger", "Earn 300 XP", {"rule": "total_xp", "threshold": 300}, "🌳"),
    ("Solar Advocate", "Earn 400 XP", {"rule": "total_xp", "threshold": 400}, "☀️"),
    ("Recycling Ranger", "Earn 350 XP", {"rule": "total_xp", "threshold": 350}, "🔄"),
    ("Climate Scholar", "Complete 7 challenges", {"rule": "approved_challenges", "threshold": 7}, "📚"),
    ("Eco Innovator", "Earn 600 XP", {"rule": "total_xp", "threshold": 600}, "💡"),
    ("Green Leader", "Earn 750 XP", {"rule": "total_xp", "threshold": 750}, "👑"),
    ("Planet Protector", "Earn 1000 XP", {"rule": "total_xp", "threshold": 1000}, "🛡️"),
    ("CSR Ally", "Complete 4 challenges", {"rule": "approved_challenges", "threshold": 4}, "💚"),
    ("Sustainability Scout", "Earn 50 XP", {"rule": "total_xp", "threshold": 50}, "🔍"),
    ("Monthly MVP", "Earn 800 XP", {"rule": "total_xp", "threshold": 800}, "📅"),
    ("Quarterly Star", "Complete 8 challenges", {"rule": "approved_challenges", "threshold": 8}, "✨"),
    ("Annual Achiever", "Earn 900 XP", {"rule": "total_xp", "threshold": 900}, "🎯"),
    ("First Steps", "Earn 25 XP", {"rule": "total_xp", "threshold": 25}, "👣"),
    ("Rising Star", "Complete 2 challenges", {"rule": "approved_challenges", "threshold": 2}, "🌟"),
    ("Team Player", "Earn 175 XP", {"rule": "total_xp", "threshold": 175}, "🧑‍🤝‍🧑"),
    ("Green Thumb", "Earn 225 XP", {"rule": "total_xp", "threshold": 225}, "🌿"),
    ("Eco Mentor", "Complete 6 challenges", {"rule": "approved_challenges", "threshold": 6}, "🎓"),
    ("Sustainability Icon", "Earn 1200 XP", {"rule": "total_xp", "threshold": 1200}, "🏅"),
    ("Zero Waste Hero", "Earn 450 XP", {"rule": "total_xp", "threshold": 450}, "🗑️"),
    ("Clean Commute", "Earn 275 XP", {"rule": "total_xp", "threshold": 275}, "🛴"),
    ("Green Office", "Earn 325 XP", {"rule": "total_xp", "threshold": 325}, "🏢"),
    ("Nature Lover", "Earn 375 XP", {"rule": "total_xp", "threshold": 375}, "🦋"),
    ("Policy Pro", "Earn 125 XP", {"rule": "total_xp", "threshold": 125}, "📋"),
    ("Audit Ace", "Earn 425 XP", {"rule": "total_xp", "threshold": 425}, "🔎"),
    ("Compliance Star", "Earn 475 XP", {"rule": "total_xp", "threshold": 475}, "✅"),
    ("ESG Pioneer", "Earn 1100 XP", {"rule": "total_xp", "threshold": 1100}, "🚀"),
    ("Impact Maker", "Complete 12 challenges", {"rule": "approved_challenges", "threshold": 12}, "💫"),
    ("Legacy Builder", "Earn 1500 XP", {"rule": "total_xp", "threshold": 1500}, "🏛️"),
]

REWARD_ITEMS = [
    ("Reusable Water Bottle", "Insulated stainless steel 750ml bottle with company logo.", 50, 40),
    ("Organic Cotton Tote Bag", "Fair-trade cotton tote for daily use.", 40, 60),
    ("Bamboo Cutlery Set", "Portable bamboo fork, knife, spoon, and carrying pouch.", 35, 50),
    ("Desk Plant — Succulent", "Low-maintenance succulent in a recycled pot.", 60, 25),
    ("Solar Power Bank", "10000mAh solar-charging portable battery.", 120, 15),
    ("Bike Service Voucher", "$50 voucher at partner bike shop.", 150, 20),
    ("Public Transit Pass", "One-month regional transit pass.", 200, 10),
    ("Fair-Trade Coffee Bundle", "1kg organic fair-trade coffee beans.", 80, 30),
    ("Yoga Mat — Recycled", "Eco-friendly yoga mat from recycled materials.", 100, 18),
    ("Seed Starter Kit", "Herb seed kit with biodegradable pots.", 45, 35),
    ("LED Desk Lamp", "Energy-efficient adjustable LED lamp.", 90, 22),
    ("Recycled Notebook Set", "Set of 3 A5 notebooks from recycled paper.", 30, 70),
    ("Charity Donation — $25", "Company donates $25 to employee-chosen charity.", 75, 100),
    ("Extra PTO Half-Day", "Half-day paid time off for volunteering.", 250, 8),
    ("Green Team Hoodie", "Organic cotton hoodie — sustainability edition.", 180, 12),
    ("Farmers Market Gift Card", "$30 gift card for local farmers market.", 70, 25),
    ("Compost Bin — Countertop", "Compact kitchen compost collector.", 55, 20),
    ("Rain Barrel Voucher", "$40 voucher toward rain barrel purchase.", 110, 10),
    ("Tree Dedication Certificate", "Company plants a tree in your name.", 65, 50),
    ("Eco Workshop Pass", "Admission to external sustainability workshop.", 130, 15),
    ("Reusable Coffee Cup", "Ceramic travel mug with silicone lid.", 45, 45),
    ("Beeswax Wrap Set", "Set of 3 reusable food wraps.", 40, 30),
    ("Solar Garden Light", "Decorative solar-powered garden light.", 85, 18),
    ("Recycled Backpack", "Daypack made from recycled PET bottles.", 160, 10),
    ("Wellness Session", "One-hour guided mindfulness session.", 140, 12),
]

PRODUCT_PROFILES = [
    ("EcoPack Shipping Box", Decimal("72.50"), Decimal("85.00"), Decimal("78.00")),
    ("GreenLine Office Chair", Decimal("65.00"), Decimal("70.00"), Decimal("82.00")),
    ("SolarCharge Power Station", Decimal("45.00"), Decimal("90.00"), Decimal("88.00")),
    ("BioClean Surface Spray", Decimal("80.00"), Decimal("95.00"), Decimal("75.00")),
    ("ReNew Laptop Sleeve", Decimal("58.00"), Decimal("80.00"), Decimal("80.00")),
    ("PureFlow Water Filter", Decimal("55.00"), Decimal("88.00"), Decimal("85.00")),
    ("TerraTile Flooring", Decimal("68.00"), Decimal("75.00"), Decimal("70.00")),
    ("HarvestBlend Snack Bar", Decimal("78.00"), Decimal("60.00"), Decimal("72.00")),
]

COMPLIANCE_DESCRIPTIONS = [
    "Missing signed waste transfer documentation for Q3 disposal.",
    "Refrigerant logbook entries incomplete for Building C HVAC units.",
    "Supplier ESG questionnaire not returned within agreed 30-day window.",
    "Emergency eyewash station inspection overdue in manufacturing wing.",
    "Fleet fuel consumption records missing for 2 vehicles in September.",
    "Fire extinguisher annual service certificate expired in warehouse.",
    "Water discharge monitoring report not filed with local authority.",
    "Hazardous material SDS sheets outdated for 3 cleaning products.",
    "Carbon offset retirement certificates not uploaded to ESG portal.",
    "Energy meter calibration certificates expired for main substation.",
    "Policy acknowledgement rate below 90% in Logistics department.",
    "Contractor safety induction records missing for 4 active vendors.",
    "Spill containment kit inspection not completed after scheduled date.",
    "GHG Scope 2 emission factor source documentation needs update.",
    "Recycling contamination rate exceeded 15% threshold last quarter.",
    "Noise level assessment overdue for new production equipment.",
    "First-aid kit restocking log incomplete for 2 office floors.",
    "Renewable energy certificate chain-of-custody gap identified.",
    "Employee grievance response exceeded 14-day SLA in two cases.",
    "Environmental permit renewal application not submitted 60 days ahead.",
    "Lighting retrofit project energy savings not verified post-install.",
    "Stormwater drainage inspection photos not archived in compliance system.",
    "PPE inventory audit found 12 items past replacement date.",
    "Scope 3 business travel data has 8% gap vs. expense reports.",
    "Biodiversity impact assessment pending for campus expansion zone.",
    "Anti-bribery training completion at 78% — below 95% target.",
    "Backup generator emissions test results not recorded.",
    "Confined space entry permits missing post-work sign-off signatures.",
    "Solar panel inverter maintenance schedule not followed in Q4.",
    "Community complaint about dust emissions not closed within 30 days.",
    "Data retention policy not applied to archived ESG spreadsheets.",
    "Lift truck battery charging area ventilation check overdue.",
    "Chemical storage secondary containment inspection failed.",
    "Board ESG committee meeting minutes not published within 10 days.",
    "Employee whistleblower hotline test call not documented this quarter.",
]

MONTH_WEIGHTS = [
    1.15, 1.12, 1.08, 1.05, 1.00, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, 0.72,
]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def weighted_month_date(month_index: int) -> date:
    """Return a date within month_index (0 = oldest month in range)."""
    month_start = START_DATE.replace(day=1) + timedelta(days=month_index * 30)
    month_end = min(month_start + timedelta(days=27), TODAY)
    return random_date(month_start, month_end)


def dt_for(day: date, hour: int = 9) -> datetime:
    return datetime(day.year, day.month, day.day, hour, random.randint(0, 59), tzinfo=UTC)


def slugify(value: str) -> str:
    return value.lower().replace(" & ", "-").replace(" ", "-").replace("'", "")


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def clear_demo_data(session: Session) -> None:
    tables = [
        "reward_redemptions",
        "employee_badges",
        "challenge_participation",
        "employee_participation",
        "policy_acknowledgements",
        "compliance_issues",
        "audits",
        "carbon_transactions",
        "environmental_goals",
        "product_esg_profiles",
        "csr_activities",
        "challenges",
        "badges",
        "rewards",
        "policies",
        "activity_logs",
        "emission_factors",
    ]
    for table in tables:
        session.execute(text(f"DELETE FROM {table}"))

    admin_user = session.scalars(
        select(User).where(User.email == "admin@ecosphere.local")
    ).first()
    admin_employee = session.scalars(
        select(Employee).where(Employee.email == "admin@ecosphere.local")
    ).first()

    seed_user_ids = session.scalars(
        select(User.id).where(User.email != "admin@ecosphere.local")
    ).all()
    if seed_user_ids:
        session.execute(delete(UserRole).where(UserRole.user_id.in_(seed_user_ids)))
        session.execute(delete(User).where(User.id.in_(seed_user_ids)))

    seed_employee_ids = session.scalars(
        select(Employee.id).where(Employee.email != "admin@ecosphere.local")
    ).all()
    if seed_employee_ids:
        session.execute(delete(Employee).where(Employee.id.in_(seed_employee_ids)))

    # Remove seed-added departments (keep migration defaults)
    migration_slugs = {"operations", "manufacturing", "logistics"}
    session.execute(
        delete(Department).where(Department.slug.notin_(migration_slugs))
    )

    if admin_user and admin_employee:
        admin_employee.department_id = None
        session.add(admin_employee)

    session.flush()
    print("Cleared existing demo data.")


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------


def get_organization(session: Session) -> Organization:
    org = session.scalars(select(Organization).limit(1)).first()
    if org is None:
        raise RuntimeError("No organization found. Run alembic upgrade head first.")
    return org


def ensure_departments(session: Session, org: Organization) -> list[Department]:
    existing = list(
        session.scalars(
            select(Department)
            .where(Department.organization_id == org.id)
            .order_by(Department.name)
        ).all()
    )
    existing_slugs = {d.slug for d in existing}

    for slug, name, code in EXTRA_DEPARTMENTS:
        if slug not in existing_slugs:
            dept = Department(
                organization_id=org.id,
                slug=slug,
                name=name,
                code=code,
                status=EntityStatus.ACTIVE,
            )
            session.add(dept)
            existing.append(dept)

    session.flush()
    departments = list(
        session.scalars(
            select(Department)
            .where(Department.organization_id == org.id)
            .order_by(Department.name)
        ).all()
    )
    if len(departments) < 8:
        raise RuntimeError(f"Expected 8 departments, found {len(departments)}")
    print(f"  Departments: {len(departments)}")
    return departments[:8]


def seed_employees(
    session: Session, org: Organization, departments: Sequence[Department]
) -> list[Employee]:
    admin = session.scalars(
        select(Employee).where(Employee.email == "admin@ecosphere.local")
    ).first()
    employees: list[Employee] = [admin] if admin else []

    employee_role = session.scalars(select(Role).where(Role.slug == "employee")).first()
    password_hash = hash_password(DEFAULT_PASSWORD)

    target = 50
    needed = target - len(employees)

    for i in range(needed):
        first = FIRST_NAMES[i % len(FIRST_NAMES)]
        last = LAST_NAMES[i % len(LAST_NAMES)]
        email = f"{first.lower()}.{last.lower()}{i + 1}@ecosphere.local"
        dept = departments[i % len(departments)]
        designation = DESIGNATIONS[i % len(DESIGNATIONS)]

        user = User(
            email=email,
            password_hash=password_hash,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        session.flush()

        if employee_role:
            session.add(UserRole(user_id=user.id, role_id=employee_role.id))

        emp = Employee(
            organization_id=org.id,
            department_id=dept.id,
            user_id=user.id,
            first_name=first,
            last_name=last,
            email=email,
            designation=designation,
            status=EntityStatus.ACTIVE,
        )
        session.add(emp)
        employees.append(emp)

    session.flush()

    # Assign department heads
    for idx, dept in enumerate(departments):
        head = employees[(idx % (len(employees) - 1)) + 1]  # skip admin
        dept.head_id = head.id
        session.add(dept)

    session.flush()
    print(f"  Employees: {len(employees)}")
    return employees


def seed_emission_factors(session: Session) -> list[EmissionFactor]:
    factors = []
    for name, source, unit, co2, desc in EMISSION_FACTORS:
        factor = EmissionFactor(
            name=name,
            source_type=source,
            unit=unit,
            co2_factor=co2,
            description=desc,
            status=EntityStatus.ACTIVE,
        )
        session.add(factor)
        factors.append(factor)
    session.flush()
    print(f"  Emission factors: {len(factors)}")
    return factors


def seed_environmental_goals(
    session: Session, departments: Sequence[Department]
) -> list[EnvironmentalGoal]:
    goals = []
    statuses = [
        GoalStatus.COMPLETED,
        GoalStatus.IN_PROGRESS,
        GoalStatus.IN_PROGRESS,
        GoalStatus.OVERDUE,
        GoalStatus.IN_PROGRESS,
        GoalStatus.COMPLETED,
        GoalStatus.NOT_STARTED,
        GoalStatus.IN_PROGRESS,
    ]
    for idx, dept in enumerate(departments):
        target = Decimal(str(random.randint(800, 2500)))
        progress_pct = [Decimal("100"), Decimal("72"), Decimal("58"), Decimal("35"),
                        Decimal("81"), Decimal("100"), Decimal("12"), Decimal("64")][idx]
        current = (target * progress_pct / Decimal("100")).quantize(Decimal("0.01"))
        goal = EnvironmentalGoal(
            department_id=dept.id,
            title=f"Reduce {dept.name} carbon emissions by 15%",
            target_value=target,
            current_value=current,
            deadline=TODAY + timedelta(days=random.randint(30, 180)),
            status=statuses[idx],
        )
        session.add(goal)
        goals.append(goal)
    session.flush()
    print(f"  Environmental goals: {len(goals)}")
    return goals


def seed_product_profiles(session: Session) -> list[ProductEsgProfile]:
    profiles = []
    for name, carbon, recycle, supplier in PRODUCT_PROFILES:
        profile = ProductEsgProfile(
            product_name=name,
            carbon_score=carbon,
            recyclability=recycle,
            supplier_score=supplier,
            notes=f"Lifecycle assessment completed for {name}.",
            status=EntityStatus.ACTIVE,
        )
        session.add(profile)
        profiles.append(profile)
    session.flush()
    print(f"  Product ESG profiles: {len(profiles)}")
    return profiles


def seed_carbon_transactions(
    session: Session,
    departments: Sequence[Department],
    factors: Sequence[EmissionFactor],
    count: int = 100,
) -> None:
    transactions = []
    for i in range(count):
        month_idx = i % 12
        tx_date = weighted_month_date(month_idx)
        dept = departments[i % len(departments)]
        factor = factors[i % len(factors)]
        weight = MONTH_WEIGHTS[month_idx]
        quantity = Decimal(str(round(random.uniform(50, 500) * weight, 2)))
        emission = (quantity * factor.co2_factor).quantize(Decimal("0.0001"))
        activity = CARBON_ACTIVITIES[i % len(CARBON_ACTIVITIES)].format(dept=dept.name)

        tx = CarbonTransaction(
            department_id=dept.id,
            emission_factor_id=factor.id,
            activity_name=activity,
            quantity=quantity,
            unit=factor.unit,
            calculated_emission=emission,
            transaction_date=tx_date,
            status=TransactionStatus.ACTIVE,
            created_at=dt_for(tx_date),
            updated_at=dt_for(tx_date),
        )
        session.add(tx)
        transactions.append(tx)
    session.flush()
    print(f"  Carbon transactions: {len(transactions)}")


def seed_csr_activities(
    session: Session, departments: Sequence[Department], count: int = 30
) -> list[CsrActivity]:
    activities = []
    for i in range(count):
        title, category, desc = CSR_TEMPLATES[i % len(CSR_TEMPLATES)]
        suffix = f" — Wave {i // len(CSR_TEMPLATES) + 1}" if i >= len(CSR_TEMPLATES) else ""
        start = weighted_month_date(i % 12)
        end = start + timedelta(days=random.randint(7, 45))
        if end > TODAY:
            status = CSRActivityStatus.ACTIVE
        elif i % 7 == 0:
            status = CSRActivityStatus.CANCELLED
        else:
            status = CSRActivityStatus.COMPLETED

        activity = CsrActivity(
            title=title + suffix,
            category=category,
            department_id=departments[i % len(departments)].id,
            description=desc,
            start_date=start,
            end_date=min(end, TODAY + timedelta(days=30)),
            points=random.choice([10, 15, 20, 25, 30, 40, 50]),
            evidence_required=i % 3 == 0,
            status=status,
            created_at=dt_for(start),
            updated_at=dt_for(min(end, TODAY)),
        )
        session.add(activity)
        activities.append(activity)
    session.flush()
    print(f"  CSR activities: {len(activities)}")
    return activities


def seed_csr_participations(
    session: Session,
    employees: Sequence[Employee],
    activities: Sequence[CsrActivity],
    count: int = 200,
) -> None:
    participatable = [a for a in activities if a.status in (CSRActivityStatus.ACTIVE, CSRActivityStatus.COMPLETED)]
    pairs = list(product(range(len(employees)), range(len(participatable))))
    random.shuffle(pairs)
    pairs = pairs[:count]

    approval_weights = [ApprovalStatus.APPROVED] * 2 + [ApprovalStatus.PENDING] * 5 + [ApprovalStatus.REJECTED] * 3
    created = 0
    for emp_idx, act_idx in pairs:
        emp = employees[emp_idx]
        activity = participatable[act_idx]
        approval = random.choice(approval_weights)
        join_date = random_date(activity.start_date, min(activity.end_date, TODAY))
        participation = EmployeeParticipation(
            employee_id=emp.id,
            csr_activity_id=activity.id,
            proof_file=f"csr-proof/{emp.id}/{activity.id}.pdf" if activity.evidence_required else None,
            approval_status=approval,
            points_earned=activity.points if approval == ApprovalStatus.APPROVED else 0,
            completion_date=join_date if approval == ApprovalStatus.APPROVED else None,
            rejection_reason="Insufficient evidence provided" if approval == ApprovalStatus.REJECTED else None,
            created_at=dt_for(join_date),
            updated_at=dt_for(join_date),
        )
        session.add(participation)
        created += 1
    session.flush()
    print(f"  CSR participations: {created}")


def seed_policies(session: Session, count: int = 25) -> list[Policy]:
    policies = []
    for i in range(count):
        title, version = POLICY_TITLES[i % len(POLICY_TITLES)]
        effective = weighted_month_date(i % 12)
        status = PolicyStatus.ACTIVE if i < 20 else random.choice([PolicyStatus.INACTIVE, PolicyStatus.ARCHIVED])
        policy = Policy(
            title=title,
            version=version,
            description=f"Corporate policy governing {title.lower()} for all employees and contractors.",
            effective_date=effective,
            status=status,
            created_at=dt_for(effective),
            updated_at=dt_for(effective),
        )
        session.add(policy)
        policies.append(policy)
    session.flush()
    print(f"  Policies: {len(policies)}")
    return policies


def seed_policy_acknowledgements(
    session: Session,
    employees: Sequence[Employee],
    policies: Sequence[Policy],
) -> None:
    active_policies = [p for p in policies if p.status == PolicyStatus.ACTIVE]
    created = 0
    for policy in active_policies:
        for emp in employees:
            if random.random() < 0.82:
                ack_date = random_date(policy.effective_date, TODAY)
                ack = PolicyAcknowledgement(
                    employee_id=emp.id,
                    policy_id=policy.id,
                    acknowledged_at=dt_for(ack_date),
                    status=AcknowledgementStatus.ACKNOWLEDGED,
                    created_at=dt_for(ack_date),
                    updated_at=dt_for(ack_date),
                )
            else:
                ack = PolicyAcknowledgement(
                    employee_id=emp.id,
                    policy_id=policy.id,
                    status=AcknowledgementStatus.PENDING,
                )
            session.add(ack)
            created += 1
    session.flush()
    print(f"  Policy acknowledgements: {created}")


def seed_audits(
    session: Session,
    departments: Sequence[Department],
    employees: Sequence[Employee],
    count: int = 15,
) -> list[Audit]:
    auditor_pool = [e for e in employees if e.designation and "Audit" in e.designation] or employees[1:6]
    audits = []
    statuses_cycle = [
        AuditStatus.COMPLETED, AuditStatus.COMPLETED, AuditStatus.COMPLETED,
        AuditStatus.IN_PROGRESS, AuditStatus.PLANNED, AuditStatus.COMPLETED,
        AuditStatus.COMPLETED, AuditStatus.IN_PROGRESS, AuditStatus.COMPLETED,
        AuditStatus.PLANNED, AuditStatus.COMPLETED, AuditStatus.COMPLETED,
        AuditStatus.CANCELLED, AuditStatus.COMPLETED, AuditStatus.IN_PROGRESS,
    ]
    for i in range(count):
        title = AUDIT_TITLES[i % len(AUDIT_TITLES)]
        audit_date = weighted_month_date(i % 12)
        audit = Audit(
            department_id=departments[i % len(departments)].id,
            title=title,
            auditor_id=auditor_pool[i % len(auditor_pool)].id,
            audit_date=audit_date,
            status=statuses_cycle[i],
            created_at=dt_for(audit_date),
            updated_at=dt_for(audit_date),
        )
        session.add(audit)
        audits.append(audit)
    session.flush()
    print(f"  Audits: {len(audits)}")
    return audits


def seed_compliance_issues(
    session: Session,
    audits: Sequence[Audit],
    employees: Sequence[Employee],
    count: int = 35,
) -> None:
    severities = [ComplianceSeverity.LOW, ComplianceSeverity.MEDIUM, ComplianceSeverity.HIGH, ComplianceSeverity.CRITICAL]
    status_pool = (
        [ComplianceIssueStatus.CLOSED] * 18
        + [ComplianceIssueStatus.OPEN] * 8
        + [ComplianceIssueStatus.IN_PROGRESS] * 5
        + [ComplianceIssueStatus.OVERDUE] * 4
    )
    owners = [e for e in employees if e.designation and "Compliance" in e.designation] or employees[1:8]

    for i in range(count):
        found_date = weighted_month_date(i % 12)
        due = found_date + timedelta(days=random.randint(14, 60))
        status = status_pool[i % len(status_pool)]
        if status == ComplianceIssueStatus.OVERDUE:
            due = TODAY - timedelta(days=random.randint(5, 30))

        issue = ComplianceIssue(
            audit_id=audits[i % len(audits)].id if i % 4 != 3 else None,
            owner_id=owners[i % len(owners)].id,
            severity=severities[i % len(severities)],
            description=COMPLIANCE_DESCRIPTIONS[i % len(COMPLIANCE_DESCRIPTIONS)],
            due_date=due,
            status=status,
            created_at=dt_for(found_date),
            updated_at=dt_for(min(due, TODAY)),
        )
        session.add(issue)
    session.flush()
    print(f"  Compliance issues: {count}")


def seed_challenges(session: Session, count: int = 25) -> list[Challenge]:
    challenges = []
    status_flow = [
        ChallengeStatus.ACTIVE, ChallengeStatus.ACTIVE, ChallengeStatus.ACTIVE,
        ChallengeStatus.ACTIVE, ChallengeStatus.ACTIVE, ChallengeStatus.UNDER_REVIEW,
        ChallengeStatus.COMPLETED, ChallengeStatus.COMPLETED, ChallengeStatus.ARCHIVED,
        ChallengeStatus.DRAFT,
    ]
    for i in range(count):
        title, category, desc, xp, diff = CHALLENGE_TEMPLATES[i % len(CHALLENGE_TEMPLATES)]
        deadline = TODAY + timedelta(days=random.randint(14, 120))
        if i % 5 == 0:
            deadline = TODAY - timedelta(days=random.randint(1, 30))

        month_idx = i % 12
        created_day = weighted_month_date(month_idx)
        status = status_flow[i % len(status_flow)] if deadline >= TODAY else ChallengeStatus.COMPLETED

        challenge = Challenge(
            title=title,
            category=category,
            description=desc,
            xp=xp,
            difficulty=ChallengeDifficulty[diff],
            evidence_required=i % 4 == 0,
            deadline=deadline,
            status=status,
            created_at=dt_for(created_day),
            updated_at=dt_for(created_day),
        )
        session.add(challenge)
        challenges.append(challenge)
    session.flush()
    print(f"  Challenges: {len(challenges)}")
    return challenges


def seed_challenge_participations(
    session: Session,
    employees: Sequence[Employee],
    challenges: Sequence[Challenge],
    count: int = 200,
) -> list[ChallengeParticipation]:
    joinable = [
        c for c in challenges
        if c.status in (ChallengeStatus.ACTIVE, ChallengeStatus.UNDER_REVIEW, ChallengeStatus.COMPLETED)
    ]
    pairs = list(product(range(1, len(employees)), range(len(joinable))))
    random.shuffle(pairs)
    pairs = pairs[:count]

    approval_weights = (
        [ParticipationApproval.APPROVED] * 2
        + [ParticipationApproval.SUBMITTED] * 2
        + [ParticipationApproval.PENDING] * 4
        + [ParticipationApproval.REJECTED] * 2
    )
    participations: list[ChallengeParticipation] = []
    for emp_idx, ch_idx in pairs:
        emp = employees[emp_idx]
        challenge = joinable[ch_idx]
        approval = random.choice(approval_weights)
        join_date = random_date(
            max(START_DATE, challenge.created_at.date() if challenge.created_at else START_DATE),
            min(TODAY, challenge.deadline),
        )
        proof = (
            f"challenge-proof/{emp.id}/{challenge.id}.pdf"
            if challenge.evidence_required and approval != ParticipationApproval.PENDING
            else None
        )
        xp_awarded = challenge.xp if approval == ParticipationApproval.APPROVED else 0

        participation = ChallengeParticipation(
            employee_id=emp.id,
            challenge_id=challenge.id,
            progress=100 if approval != ParticipationApproval.PENDING else random.randint(10, 60),
            proof_file=proof,
            approval_status=approval,
            xp_awarded=xp_awarded,
            completion_date=join_date if approval == ParticipationApproval.APPROVED else None,
            rejection_reason="Evidence did not meet requirements" if approval == ParticipationApproval.REJECTED else None,
            created_at=dt_for(join_date),
            updated_at=dt_for(join_date),
        )
        session.add(participation)
        participations.append(participation)
    session.flush()
    print(f"  Challenge participations: {len(participations)}")
    return participations


def seed_badges(session: Session, count: int = 40) -> list[Badge]:
    badges = []
    for i in range(count):
        name, desc, rule, icon = BADGE_DEFINITIONS[i % len(BADGE_DEFINITIONS)]
        badge = Badge(
            name=name if i < len(BADGE_DEFINITIONS) else f"{name} Tier {(i // len(BADGE_DEFINITIONS)) + 1}",
            description=desc,
            unlock_rule=rule,
            icon=icon,
            status=BadgeStatus.ACTIVE if i < 36 else BadgeStatus.INACTIVE,
            created_at=dt_for(START_DATE),
            updated_at=dt_for(TODAY),
        )
        session.add(badge)
        badges.append(badge)
    session.flush()
    print(f"  Badges: {len(badges)}")
    return badges


def seed_rewards(session: Session, count: int = 25) -> list[Reward]:
    rewards = []
    for i in range(count):
        name, desc, points, stock = REWARD_ITEMS[i % len(REWARD_ITEMS)]
        reward = Reward(
            name=name,
            description=desc,
            points_required=points,
            stock=stock,
            status=RewardStatus.ACTIVE if stock > 0 else RewardStatus.OUT_OF_STOCK,
            created_at=dt_for(START_DATE),
            updated_at=dt_for(TODAY),
        )
        session.add(reward)
        rewards.append(reward)
    session.flush()
    print(f"  Rewards: {len(rewards)}")
    return rewards


def seed_employee_badges(
    session: Session,
    employees: Sequence[Employee],
    badges: Sequence[Badge],
    participations: Sequence[ChallengeParticipation],
) -> None:
    xp_by_employee: dict[uuid.UUID, int] = {}
    approved_by_employee: dict[uuid.UUID, int] = {}
    for p in participations:
        if p.approval_status == ParticipationApproval.APPROVED:
            xp_by_employee[p.employee_id] = xp_by_employee.get(p.employee_id, 0) + p.xp_awarded
            approved_by_employee[p.employee_id] = approved_by_employee.get(p.employee_id, 0) + 1

    active_badges = [b for b in badges if b.status == BadgeStatus.ACTIVE]
    awarded_pairs: set[tuple[uuid.UUID, uuid.UUID]] = set()
    created = 0

    for emp in employees:
        total_xp = xp_by_employee.get(emp.id, 0)
        approved = approved_by_employee.get(emp.id, 0)
        for badge in active_badges:
            rule = badge.unlock_rule or {}
            rule_type = rule.get("rule")
            threshold = rule.get("threshold", 0)
            met = False
            if rule_type == "total_xp" and total_xp >= int(threshold):
                met = True
            elif rule_type == "approved_challenges" and approved >= int(threshold):
                met = True
            if met and (emp.id, badge.id) not in awarded_pairs:
                earned_day = random_date(START_DATE, TODAY)
                session.add(
                    EmployeeBadge(
                        employee_id=emp.id,
                        badge_id=badge.id,
                        earned_at=dt_for(earned_day),
                        created_at=dt_for(earned_day),
                        updated_at=dt_for(earned_day),
                    )
                )
                awarded_pairs.add((emp.id, badge.id))
                created += 1
    session.flush()
    print(f"  Employee badges awarded: {created}")


def seed_reward_redemptions(
    session: Session,
    employees: Sequence[Employee],
    rewards: Sequence[Reward],
    participations: Sequence[ChallengeParticipation],
) -> None:
    xp_by_employee: dict[uuid.UUID, int] = {}
    for p in participations:
        if p.approval_status == ParticipationApproval.APPROVED:
            xp_by_employee[p.employee_id] = xp_by_employee.get(p.employee_id, 0) + p.xp_awarded

    affordable_rewards = [r for r in rewards if r.status == RewardStatus.ACTIVE and r.stock > 0]
    created = 0
    for emp in employees[1:25]:
        available = xp_by_employee.get(emp.id, 0)
        if available < 40:
            continue
        reward = random.choice(affordable_rewards)
        if available < reward.points_required or reward.stock <= 0:
            continue
        redeem_day = random_date(START_DATE, TODAY)
        session.add(
            RewardRedemption(
                reward_id=reward.id,
                employee_id=emp.id,
                redeemed_points=reward.points_required,
                redeemed_at=dt_for(redeem_day),
                created_at=dt_for(redeem_day),
                updated_at=dt_for(redeem_day),
            )
        )
        reward.stock -= 1
        if reward.stock <= 0:
            reward.status = RewardStatus.OUT_OF_STOCK
        session.add(reward)
        available -= reward.points_required
        xp_by_employee[emp.id] = available
        created += 1
    session.flush()
    print(f"  Reward redemptions: {created}")


def seed_activity_logs(session: Session, employees: Sequence[Employee]) -> None:
    actions = [
        ("CREATE", "challenge"),
        ("APPROVE", "challenge_participation"),
        ("CREATE", "csr_activity"),
        ("ACKNOWLEDGE", "policy"),
        ("UPDATE", "environmental_goal"),
        ("CREATE", "carbon_transaction"),
        ("CLOSE", "compliance_issue"),
        ("REDEEM", "reward"),
    ]
    for i in range(40):
        emp = employees[1 + (i % (len(employees) - 1))]
        action, entity = actions[i % len(actions)]
        log_date = weighted_month_date(i % 12)
        session.add(
            ActivityLog(
                employee_id=emp.id,
                action=action,
                entity=entity,
                entity_id=uuid.uuid4(),
                metadata_={"seed": True, "index": i},
                created_at=dt_for(log_date, hour=10 + (i % 8)),
                updated_at=dt_for(log_date, hour=10 + (i % 8)),
            )
        )
    session.flush()
    print("  Activity logs: 40")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_seed(reset: bool = False) -> None:
    session = SessionLocal()
    try:
        if reset:
            clear_demo_data(session)
            session.commit()

        org = get_organization(session)
        print("Seeding EcoSphere demo data...")
        departments = ensure_departments(session, org)
        employees = seed_employees(session, org, departments)
        factors = seed_emission_factors(session)
        seed_environmental_goals(session, departments)
        seed_product_profiles(session)
        seed_carbon_transactions(session, departments, factors, count=100)
        csr_activities = seed_csr_activities(session, departments, count=30)
        seed_csr_participations(session, employees, csr_activities, count=200)
        policies = seed_policies(session, count=25)
        seed_policy_acknowledgements(session, employees, policies)
        audits = seed_audits(session, departments, employees, count=15)
        seed_compliance_issues(session, audits, employees, count=35)
        challenges = seed_challenges(session, count=25)
        participations = seed_challenge_participations(session, employees, challenges, count=200)
        badges = seed_badges(session, count=40)
        rewards = seed_rewards(session, count=25)
        seed_employee_badges(session, employees, badges, participations)
        seed_reward_redemptions(session, employees, rewards, participations)
        seed_activity_logs(session, employees)

        session.commit()
        print("\nSeed complete. Demo login for employees: *@ecosphere.local / Employee123!")
        print("Admin login unchanged: admin@ecosphere.local / ChangeMe123!")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed EcoSphere with realistic demo data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing demo data before seeding",
    )
    args = parser.parse_args()
    run_seed(reset=args.reset)


if __name__ == "__main__":
    main()
