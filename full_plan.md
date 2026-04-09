# Food Delivery System Backend - Comprehensive Project Plan

This document serves as the single source of truth for the Food Delivery System (Foodizz) project. It contains every nitty-gritty detail about the project's architecture, OOP implementation, roles, use cases, dependencies, and file structures. You can use this document as a primary reference to rebuild or present the project later.

## 1. Project Overview & Objectives
The system is a comprehensive backend for a food delivery platform (similar to Zomato, Swiggy, or UberEats) that manages the entire lifecycle of a food order—from menu browsing and ordering to live delivery tracking and post-order customer support. 

**Objectives:**
- Build a highly scalable, modular system using clean Object-Oriented Programming (OOP) principles.
- Implement explicit role-based access control (RBAC) across five distinct actors.
- Fully cover real-world delivery system edge cases, particularly through a dedicated Customer Support and Ticketing module.
- Deliver production-grade API structures utilizing FastAPI, SQLAlchemy, and JWT Authentication.

---

## 2. System Actors & Roles
The platform caters to five primary actors, all of which authenticate securely via JWT.

| Actor | Role Description | Key Responsibilities |
| --- | --- | --- |
| **Customer** | End-user who orders food | Browse menus, place/cancel orders, track delivery, apply coupons, rate restaurants, raise complaints. |
| **Restaurant Owner** | Business owner handling orders | Update menu items, accept/reject incoming orders, update preparation status. |
| **Delivery Agent** | Field personnel for order delivery | Accept delivery assignments, update GPS location, mark orders delivered, trigger emergency alerts. |
| **Customer Support** | Internal support personnel | Handle complaint tickets, process payment refunds, escalate tickets, update user profiles. |
| **Admin** | Top-level system management | Manage all system users, oversee platform operations, review escalated tickets, view reports. |

---

## 3. Core OOP Concepts Applied
This system is heavily based on robust OOP paradigms, demonstrated specifically in the business and logic layers:

- **Inheritance:** 
  The foundation of user management revolves around a `UserAccount` base class. `Customer`, `DeliveryAgent`, `RestaurantOwner`, and `CustomerSupport` all inherit common attributes (`userId`, `name`, `email`, `password`) and methods (`login()`, `logout()`) from `UserAccount`.
- **Encapsulation:**
  Internal states of classes like `SupportTicket` and `Order` are hidden from external access. State transitions (e.g., OPEN → IN_PROGRESS → RESOLVED) are strictly managed by specific gateway methods (like `ticket.updateStatus()`) ensuring valid object states.
- **Abstraction:**
  A `Customer` seamlessly calls a backend method such as `raiseComplaint()`. The intricate logic of ticket creation, agent assignment, and backend routing is isolated and hidden.
- **Polymorphism:**
  Through the ORM logic, any `UserAccount` reference can hold the specialized logic of its derived actor class. The same login flow polymorphically directs the distinct users to their appropriate dashboards and authorization scopes.

---

## 4. Class Hierarchies & Data Relationships (ER Overview)

### 4.1 Base and Derived Objects
- **`UserAccount` (Base)** -> Inherited by -> **`Customer`**, **`RestaurantOwner`**, **`DeliveryAgent`**, **`CustomerSupport`**.

### 4.2 Supporting Entities
- **`Order`**: Tracks order lifecycle (`PENDING`, `CONFIRMED`, `OUT_FOR_DELIVERY`, `DELIVERED`). Linked to `Customer`, `RestaurantOwner`, and `DeliveryAgent`.
- **`Payment`**: Handles financial transactions. Linked 1-to-1 to an `Order`. Includes payment methods, status, and transaction refs.
- **`SupportTicket`**: Core of the Customer Support module. Linked to an `Order` or `Payment` and handled by a `CustomerSupport` agent.
- **`MenuItem`**: Belongs to a `RestaurantOwner`.

### 4.3 Data Cardinality
- `Customer` (1) ---> (Many) `Order`
- `Customer` (1) ---> (Many) `SupportTicket`
- `Order` (1) ---> (1) `Payment`
- `Order` (1) ---> (Many) `MenuItem`
- `Order` (Many) ---> (1) `DeliveryAgent` (Assigned for delivery)
- `CustomerSupport` (1) ---> (Many) `SupportTicket`

---

## 5. Detailed Use Cases & Flows

### 5.1 The Order Placement & Fulfillment Flow
1. **Browse & Cart**: Customer views `MenuItem`s and adds them to their cart. 
2. **Order Placement**: Customer applies coupon (if applicable), inputs address, and confirms. The `Order` object is created (`status = PENDING`).
3. **Payment**: `Payment` is processed. If successful, `Order` status becomes `CONFIRMED`. *If failed, a `SupportTicket` is generated automatically.*
4. **Restaurant Action**: Owner gets notified, accepts order, prepares it (`status = PREPARING`).
5. **Delivery Flow**: The system locates and assigns a `DeliveryAgent`. The Agent picks up the food (`status = OUT_FOR_DELIVERY`), and upon completion marks it `DELIVERED`. Customer brings closure by supplying a `Rating`.

### 5.2 The Customer Support Lifecycle (The Edge-Case Engine)
1. **Issue Encounter**: Customer faces a problem (payment fail, missing item, wrong order) and submits an in-app form linked to order/transaction ID.
2. **Ticket Initialization**: `SupportTicket` object initialized (`status = OPEN`).
3. **Assignment**: System automatically searches for a `CustomerSupport` agent with `availabilityStatus = AVAILABLE` and assigns them.
4. **Resolution**: Support Agent switches ticket to `IN_PROGRESS`. They can trigger functions like `payment.refund()`, adjust profiles, or update the order's backend state.
5. **Escalation**: If complex (e.g. platform error), agent escalates to `Admin`.
6. **Closure**: Resolved tickets are set to `RESOLVED` and the Customer is updated. 

### 5.3 Delivery Agent Emergency Flow
1. **Trigger**: Agent experiences an emergency (vehicle breakdown, accident) and triggers `sendEmergencyUpdate()`.
2. **Alerts**: System instantly alerts `Admin` and `CustomerSupport`. Customer receives an automated delay notification.
3. **Re-assignment**: Admin easily detaches the current Agent and maps the pending `Order` to a new `DeliveryAgent` to uphold service levels.

---

## 6. Codebase File Structure & Components

```text
foodizz/
├── app/
│   ├── main.py.......... FastAPI application instance, app configuration, and router aggregation
│   ├── database.py...... SQLAlchemy DB connection setup (Engine, SessionLocal, Base)
│   ├── models.py........ System's single source of truth for OOP schemas mapped to DB tables
│   ├── schemas.py....... Pydantic models handling request/response validations
│   ├── crud.py.......... Centralized location for database queries & mutations (Create, Read, Update, Delete)
│   ├── auth.py.......... Password hashing, login, and JWT Token issuance/verification
│   ├── dependencies.py.. Core dependency injections (e.g., get_db, get_current_user_by_role)
│   ├── seed.py.......... Script pre-loaded with mock data (restaurants, admins) for immediate demo use
│   └── tests/........... PyTest suite handling unit and integration scenarios
│       ├── test_auth.py
│       ├── test_order.py
│       └── test_support.py
├── README.md............ Developer onboarding and quickstart guide
├── requirements.txt..... Production dependencies (FastAPI, uvicorn, SQLAlchemy, passlib, etc)
├── plan.txt............. Dev sprint breakdown roadmap
└── detail.txt........... Advanced System Architecture documentation
```

---

## 7. Dependencies & Tech Stack

### Framework & Services
- **Language**: Python 3.10+
- **Web Framework**: FastAPI (blazing fast, built-in OpenAPI `/docs` for dynamic visual demos, highly asynchronous)
- **Database Backend**: SQLite/MySQL/PostgreSQL (configured via SQLAlchemy). 
- **Server**: Uvicorn (ASGI web server)

### Package Dependencies (`requirements.txt`)
- `fastapi` - Core REST framework
- `uvicorn` - Web server execution
- `sqlalchemy` - Extensive Object Relational Mapper for OOP Models
- `passlib[bcrypt]` - Secure password encryption
- `python-jose[cryptography]` - JWT implementation
- `pytest` - Professional unit testing infrastructure

---

## 8. Strategy for Rollout & Scaling

**Phase 1: Skeleton Structure & Fundamentals**
Setting up `main.py`, the `database.py` connection, and bringing the skeleton FASTApi app to port 8000. 

**Phase 2: Database and OOP Modeling (`models.py`)**
Transcribing all the UML relationships outlined in Section 4 into precise SQLAlchemy Python Classes. Handling standard foreign-key linkages and enumerations.

**Phase 3: Authentication Layer (`auth.py`)**
Constructing the `UserAccount` foundation. Establishing JWT signing to securely segregate Customers from Restaurant Owners from Support Personnel.

**Phase 4: API Endpoint Implementation (`routers/`, `crud.py`)**
Linking URL routes to database interactions. Handling complex workflows like updating cart logic, applying discounts, processing simulated payments, and the full backend resolution of a Support Ticket.

**Phase 5: Automated Testing & Polish (`tests/`, `seed.py`)**
Designing integration tests mapping exact end-to-end user journeys (e.g., Order -> Failed Payment -> Auto-Ticket Generation -> Support Agent Resolution). Filling the database via `seed.py` so project evaluators have immediate data populated during viva presentations.

---

*This document fully describes the system architecture and implementation blueprint. It successfully demonstrates deep advanced programming and MVC methodologies applied directly to a highly-practical, enterprise-grade problem domain.*
