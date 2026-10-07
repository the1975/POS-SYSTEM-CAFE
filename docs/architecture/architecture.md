# Monster Café

Sistem self-ordering dan operasional café berbasis web untuk mengelola proses pemesanan, pembayaran, kitchen, pickup, inventory, dan analytics dalam satu sistem terintegrasi.

## 1. Project Overview

Monster Café dirancang untuk menyelesaikan masalah operasional café yang masih bergantung pada proses manual, terutama:

- Pencatatan order
- Pembayaran
- Pengiriman order ke kitchen
- Monitoring status pesanan
- Pickup order
- Pengelolaan stock
- Penanganan order bermasalah
- Rekap penjualan
- Analisis operasional

Sistem menggunakan QR menu universal.

Customer cukup melakukan scan QR untuk membuka menu dan melakukan pemesanan tanpa membuat account.

Flow utama:

    Scan QR
       ↓
    Menu
       ↓
    Cart
       ↓
    Checkout
       ↓
    Payment
       ↓
    Order Confirmation
       ↓
    Kitchen
       ↓
    Ready
       ↓
    Pickup
       ↓
    Completed

---

# 2. Project Goals

Tujuan utama:

1. Membuat proses ordering lebih cepat.
2. Mengurangi kesalahan pencatatan order.
3. Memisahkan payment state dari order state.
4. Memberikan kitchen queue yang jelas.
5. Mempermudah pickup.
6. Menjaga stock tetap konsisten.
7. Menyediakan operational monitoring.
8. Menyediakan analytics untuk business decision.
9. Menjaga transaction integrity.
10. Membuat architecture yang cukup sederhana untuk MVP tetapi tidak asal-asalan secara engineering.

---

# 3. Core Principles

Monster Café mengikuti prinsip:

> Simple for customer, clear for staff, useful for owner.

Prioritas sistem:

    Data Integrity
         ↓
    Security
         ↓
    Business Rules
         ↓
    Usability
         ↓
    Visual Design

Visual yang bagus tidak boleh mengalahkan correctness.

---

# 4. User Roles

## Customer

Customer tidak membutuhkan account.

Customer dapat:

- Melihat menu
- Melihat product detail
- Menambahkan item ke cart
- Checkout
- Memilih payment method
- Melakukan pembayaran
- Tracking order
- Melakukan edit order jika masih diizinkan
- Melakukan cancellation jika masih diizinkan
- Menggunakan pickup token

---

## Order Controller / Shift Controller

Bertugas memonitor operational flow.

Dapat:

- Melihat active orders
- Melihat kitchen load
- Melihat exceptions
- Menangani order bermasalah
- Memantau payment issue
- Memantau stock issue
- Memantau late order
- Membantu cancellation/refund sesuai permission
- Memantau pickup backlog

Controller bukan middleman untuk setiap order.

Normal order harus berjalan otomatis.

Controller fokus pada exception.

---

## Kitchen

Dapat:

- Melihat confirmed orders
- Memulai preparation
- Melihat item
- Menandai item ready
- Melakukan remake
- Memberikan remake reason
- Melihat kitchen queue

Kitchen tidak dapat:

- Mengubah harga
- Mengubah total
- Mengubah payment
- Melakukan refund
- Menghapus order
- Mengubah customer data secara bebas

---

## Cashier

Dapat:

- Melihat waiting cash orders
- Menerima pembayaran cash
- Input cash received
- Melihat change
- Confirm payment

Cashier tidak boleh menentukan payment status secara sembarangan.

---

## Pickup Staff

Dapat:

- Melihat ready orders
- Scan pickup QR/token
- Verify order
- Menyerahkan order
- Complete pickup

Pickup harus menggunakan atomic verification agar satu order tidak dapat diambil dua kali.

---

## Admin / Owner

Dapat:

- Manage products
- Manage categories
- Manage inventory
- Manage users
- Monitor orders
- Melihat analytics
- Melakukan adjustment
- Melakukan refund sesuai permission
- Melakukan configuration

---

# 5. Ordering Model

Monster Café menggunakan universal QR menu.

Contoh:

    /menu

QR tidak terikat dengan meja.

Table bukan bagian dari core transaction model.

Customer tidak perlu:

- Login
- Register
- Memilih table

Customer cukup memberikan nama untuk kebutuhan human-readable operation.

Customer name bukan unique identifier.

Order number menjadi identifier utama yang digunakan customer dan staff.

Contoh:

    A127

Database menggunakan internal UUID sebagai primary key.

---

# 6. Customer Order Identity

Order memiliki:

- Internal order UUID
- Human-readable order number
- Customer name
- Secure tracking token
- Pickup token

Order number:

`A127`

Tracking token:

random secure token.

Database menyimpan hash tracking token.

Order number bukan credential.

---

# 7. Payment Model

Payment utama:

- QRIS
- Cash

Payment state:

    PENDING
    WAITING_CASH
    PAID
    FAILED
    REFUND_REQUESTED
    REFUND_PENDING
    REFUNDED
    REFUND_FAILED

Payment dan order state merupakan dua konsep berbeda.

---

# 8. QRIS Flow

    Checkout
       ↓
    Create Order
       ↓
    Create Payment
       ↓
    Payment Gateway
       ↓
    Customer Pays
       ↓
    Gateway Webhook
       ↓
    Backend Verify
       ↓
    Payment = PAID
       ↓
    Order = CONFIRMED
       ↓
    Kitchen

Browser customer boleh ditutup setelah pembayaran.

Payment tetap dapat dikonfirmasi melalui backend webhook.

Payment webhook harus idempotent.

---

# 9. Cash Flow

    Checkout
       ↓
    Select Cash
       ↓
    Order = PENDING / WAITING_CASH
       ↓
    Customer Goes to Cash Counter
       ↓
    Cashier Inputs Cash Received
       ↓
    Backend Calculates Change
       ↓
    Payment = PAID
       ↓
    Order = CONFIRMED
       ↓
    Kitchen

Cash order yang belum dibayar tidak boleh masuk kitchen.

---

# 10. Order State

Main order state:

    PENDING
    CONFIRMED
    PREPARING
    READY
    COMPLETED
    CANCELLED
    OVERDUE

Main flow:

    PENDING
       ↓
    CONFIRMED
       ↓
    PREPARING
       ↓
    READY
       ↓
    COMPLETED

Cancellation hanya boleh dilakukan sesuai current state dan business rules.

---

# 11. Item State

Order item memiliki state sendiri.

Contoh:

    Order A127

    Nasi Goreng    READY
    Es Teh         READY
    Kentang        REMAKE

Order belum dianggap fully READY jika masih terdapat item yang belum selesai.

---

# 12. Remake Model

Remake tidak membuat order baru.

Order tetap:

`A127`

Order item tetap:

`order_item_id`

Remake dibuat sebagai event:

`remake_event`

Contoh reason:

- Wrong menu
- Wrong size
- Wrong topping
- Wrong quantity
- Damaged
- Spilled
- Customer request
- Other

Remake dimasukkan kembali ke production flow.

---

# 13. Pickup Model

Pickup menggunakan:

`WAITING_PICKUP → COMPLETED`

Customer menunjukkan:

- Pickup QR
- Pickup token

Staff melakukan:

1. Verify
2. Grab
3. Handover
4. Complete

Pickup verification harus atomic.

Jika order sudah completed:

request pickup kedua harus ditolak.

---

# 14. Kitchen Queue

Queue MVP menggunakan FIFO.

Sistem tidak menyimpan:

`queue_position`

secara permanen.

Queue position dihitung secara relatif berdasarkan active orders.

Customer dapat melihat informasi seperti:

    12 pesanan sedang dikerjakan
    Posisi relatif #19
    Estimasi 15–20 menit

Raw internal queue tidak perlu seluruhnya ditampilkan kepada customer.

---

# 15. Kitchen Load

Kitchen load:

    NORMAL
    BUSY
    HIGH_LOAD
    CRITICAL

Load memengaruhi:

- Estimated preparation time
- Customer information
- Operational monitoring

Jika:

`CRITICAL`

sistem dapat menutup order baru sementara.

Menu tetap dapat dilihat.

Existing confirmed orders tetap diproses.

---

# 16. Inventory

MVP menggunakan product-level inventory.

Inventory memiliki:

- quantity_available
- quantity_reserved
- reorder_level

Stock flow:

    AVAILABLE
       ↓
    RESERVED
       ↓
    CONVERTED
       ↓
    SOLD / CONSUMED

Reservation dapat:

- ACTIVE
- CONVERTED
- EXPIRED
- CANCELLED

Reservation expiration dilakukan background worker.

---

# 17. Inventory Concurrency

Stock harus diperbarui secara atomic.

Contoh:

Stock:

    1 Nasi Goreng

Dua customer melakukan checkout secara bersamaan.

Backend harus memastikan hanya satu transaction yang berhasil reserve stock tersebut.

Database transaction dan locking digunakan jika diperlukan.

Frontend tidak pernah dipercaya untuk menentukan stock.

---

# 18. Operating Hours

Menu dapat diakses kapan saja.

Ordering hanya tersedia ketika café open.

Contoh configuration:

    Opening:
    09:00

    Closing:
    22:00

    Last Order:
    21:45

Jam tersebut harus configurable.

Emergency close juga harus tersedia untuk authorized staff/admin.

Ketika café ditutup:

- Order baru tidak diterima.
- Existing paid/confirmed orders tetap diproses.
- Unpaid reservations dapat expired/released sesuai rules.

---

# 19. Pricing

Pricing calculation:

    Product Price × Quantity
              ↓
           Subtotal
              ↓
           Discount
              ↓
             DPP
              ↓
             PPI
              ↓
            Total

Contoh:

    Subtotal     = Rp100.000
    Discount     = Rp10.000
    DPP          = Rp90.000
    PPI           = Rp9.000
    Total        = Rp99.000

Formula aktual harus mengikuti aturan bisnis dan konfigurasi yang digunakan.

Backend selalu menghitung ulang nilai financial.

---

# 20. Revenue vs Profit

Revenue bukan profit.

Gross profit:

    Revenue - COGS

Net profit membutuhkan:

    Gross Profit - Operating Expenses

Analytics harus membedakan:

- Revenue
- COGS
- Gross Profit
- Operating Expenses
- Net Profit

---

# 21. QRIS Fee

Payment gateway fee dianggap sebagai payment/business expense.

Customer total tidak otomatis berubah karena fee tersebut.

Contoh:

    Customer pays:
    Rp100.000

    Revenue:
    Rp100.000

    Payment fee:
    Rp2.000

    Net received:
    Rp98.000

Revenue tetap Rp100.000.

---

# 22. Order Editing

Customer dapat edit order sebelum order masuk preparation jika business rules mengizinkan.

Edit:

1. Validate current state.
2. Validate stock.
3. Recalculate price.
4. Create revision.
5. Update reservation.
6. Handle payment difference.
7. Return order to appropriate queue position.

Recommended MVP:

Maximum 1 edit.

Jika edit menyebabkan total naik:

Customer membayar difference sebelum order diproses kembali.

Jika total turun:

Difference masuk refund flow sesuai business rules.

---

# 23. Database Source of Truth

PostgreSQL adalah source of truth.

CSV bukan source of truth.

Frontend state bukan source of truth.

Analytics dashboard bukan source of truth.

Printer bukan source of truth.

Payment gateway adalah external payment authority, tetapi internal transaction state tetap harus direkonsiliasi ke database.

---

# 24. Architecture

Architecture:

    Customer / Staff
           ↓
        React
           ↓
        FastAPI
           ↓
      Service Layer
           ↓
     Repository Layer
           ↓
       PostgreSQL

External:

    FastAPI
       ├── Payment Gateway
       ├── Notification / SSE
       └── Printer

Background:

    Worker
       ├── Reservation Expiration
       ├── Payment Reconciliation
       ├── Notification Dispatch
       ├── Overdue Detection
       └── Daily Aggregation

---

# 25. Architecture Style

Monster Café menggunakan:

**Modular Monolith**

Bukan:

- Microservices
- Kubernetes
- Kafka
- Redis-heavy architecture

MVP tidak perlu distributed architecture sebelum benar-benar dibutuhkan.

Modular monolith memberikan:

- Simpler deployment
- Easier debugging
- Transaction consistency
- Lower infrastructure complexity
- Easier development

---

# 26. Technology Stack

## Frontend

- React
- JavaScript
- HTML
- CSS
- Optional Tailwind CSS
- Vite

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic

## Database

- PostgreSQL
- Managed PostgreSQL preferred

## Development

- Git
- GitHub
- GitHub Codespaces
- Acode

## Analytics

- Pandas
- Plotly
- Jupyter / Google Colab

---

# 27. Repository Structure

    monster-cafe/
    ├── frontend/
    ├── backend/
    ├── docs/
    ├── scripts/
    ├── .github/
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── LICENSE

---

# 28. Frontend Structure

    frontend/
    ├── src/
    │   ├── app/
    │   ├── components/
    │   │   ├── ui/
    │   │   ├── layout/
    │   │   ├── forms/
    │   │   └── feedback/
    │   ├── features/
    │   │   ├── menu/
    │   │   ├── cart/
    │   │   ├── checkout/
    │   │   ├── orders/
    │   │   ├── kitchen/
    │   │   ├── pickup/
    │   │   ├── controller/
    │   │   ├── admin/
    │   │   └── analytics/
    │   ├── pages/
    │   ├── services/
    │   ├── hooks/
    │   ├── stores/
    │   ├── utils/
    │   ├── types/
    │   ├── assets/
    │   └── main.jsx
    ├── public/
    ├── tests/
    ├── package.json
    └── README.md

---

# 29. Backend Structure

    backend/
    ├── app/
    │   ├── api/
    │   │   ├── customer/
    │   │   ├── staff/
    │   │   └── admin/
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── security.py
    │   │   ├── exceptions.py
    │   │   └── logging.py
    │   ├── db/
    │   │   ├── session.py
    │   │   ├── base.py
    │   │   └── dependencies.py
    │   ├── modules/
    │   │   ├── users/
    │   │   ├── products/
    │   │   ├── orders/
    │   │   ├── inventory/
    │   │   ├── payments/
    │   │   ├── kitchen/
    │   │   ├── pickup/
    │   │   ├── notifications/
    │   │   └── analytics/
    │   ├── workers/
    │   └── main.py
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   └── e2e/
    ├── alembic/
    │   └── versions/
    ├── pyproject.toml
    └── README.md

---

# 30. Backend Dependency Direction

Backend:

    API
     ↓
    Service
     ↓
    Repository
     ↓
    Database

API tidak boleh langsung menjalankan query kompleks.

Business logic tidak boleh tersebar di router.

Service menjadi pusat business rules.

Repository menangani persistence/query.

---

# 31. Database Tables

MVP menggunakan:

1. roles
2. users
3. categories
4. products
5. inventory
6. stock_reservations
7. stock_movements
8. orders
9. order_items
10. order_revisions
11. order_revision_items
12. payments
13. payment_events
14. order_status_history
15. remake_events
16. pickups
17. notifications
18. audit_logs

---

# 32. Order Database Model

Order memiliki:

- Internal UUID
- Unique order number
- Customer name
- Tracking token hash
- Status
- Subtotal
- Discount
- Tax
- Total
- Payment method
- Operational timestamps

Order item menyimpan historical snapshot:

- Product ID
- Product name snapshot
- Unit price
- Quantity
- Subtotal
- Item status

Historical order tidak berubah ketika product price berubah.

---

# 33. Revision Model

Order revision digunakan untuk menyimpan perubahan order.

Setiap revision memiliki:

- Order ID
- Revision number
- Subtotal
- Discount
- Tax
- Total
- Reason
- Created by
- Created at

`order_revision_items` menyimpan item snapshot pada revision tersebut.

---

# 34. Payment Model

Payment menyimpan:

- Order
- Provider
- Payment method
- Provider transaction ID
- Amount
- Status
- Paid time
- Expiration
- Timestamps

Payment event menyimpan webhook/event history.

Provider transaction ID harus unique jika tersedia.

---

# 35. Pickup Model

Pickup:

- One order
- One pickup record

State:

    WAITING_PICKUP
    COMPLETED

Pickup token disimpan dalam bentuk hash.

---

# 36. Notification Model

Notification dapat ditujukan kepada:

- Staff
- Admin
- Customer guest session

Customer guest tidak membutuhkan row pada `users`.

---

# 37. Audit Model

Audit log mencatat perubahan sensitif.

Contoh:

    User:
    admin-001

    Action:
    REFUND_PAYMENT

    Entity:
    payment

    Entity ID:
    uuid

    Old:
    PAID

    New:
    REFUND_PENDING

    Reason:
    Customer cancellation

---

# 38. Security

Security principles:

- Password hashing
- Secure random tokens
- Backend RBAC
- Rate limiting
- Input validation
- Parameterized queries
- HTTPS production
- Webhook signature verification
- Audit logging
- Secret management
- No secret in Git
- No secret in frontend bundle

Environment variables:

    DATABASE_URL
    PAYMENT_API_KEY
    PAYMENT_SECRET
    JWT_SECRET

`.env` tidak boleh di-commit.

`.env.example` boleh di-commit.

---

# 39. Client Trust Boundary

Client tidak dipercaya untuk:

- Price
- Total
- Discount
- Tax
- Stock
- Payment state
- Order state
- User role
- Refund permission
- Pickup validity

Client hanya mengirim request.

Backend mengambil keputusan.

---

# 40. Concurrency Requirements

Critical operations:

- Create order
- Stock reservation
- Payment confirmation
- Cash confirmation
- Pickup completion
- Refund
- Order editing

harus aman terhadap concurrent requests.

Contoh:

    User A → stock = 1
    User B → stock = 1

Tidak boleh:

    User A → success
    User B → success

jika hanya tersedia satu stock.

---

# 41. Idempotency

Idempotency digunakan pada:

- Checkout
- Payment
- Webhook
- Refund
- Pickup

Duplicate request harus menghasilkan satu side effect.

---

# 42. Failure Handling

## Server Down

Jangan tampilkan order success jika transaction belum persisted.

## Browser Closed

Backend tetap memproses transaction.

## Payment Success but Browser Closed

Webhook/reconciliation tetap memperbarui payment.

## Printer Failure

Order tetap valid.

Reprint dapat dilakukan.

## Notification Failure

Order tetap valid.

## Payment Provider Timeout

Jangan langsung menganggap failed jika final state belum diketahui.

---

# 43. Operating Exception Model

Normal flow:

    Order
      ↓
    Payment
      ↓
    Kitchen
      ↓
    Pickup
      ↓
    Complete

Exception flow:

    Order
      ↓
    Exception
      ↓
    Controller
      ↓
    Resolution
      ↓
    Normal Flow

Controller tidak memproses semua normal transaction secara manual.

---

# 44. Analytics

Analytics menggunakan data transaksi PostgreSQL.

Dashboard:

- Daily revenue
- Monthly revenue
- Orders
- Units sold
- Gross profit
- Top products
- Bottom products
- Peak hours
- Average order value
- Preparation time
- Pickup time
- Remake count
- Cancellation count
- Payment failure
- Kitchen load

Business loop:

    Data
      ↓
    Visualization
      ↓
    Insight
      ↓
    Decision

---

# 45. Daily Closing

Daily closing dapat merangkum:

- Completed orders
- Cancelled orders
- Revenue
- COGS
- Gross profit
- QRIS reconciliation
- Cash reconciliation
- Refunds

Revenue dan profit tidak boleh dicampur.

---

# 46. CSV Analytics

Export dapat dibuat menjadi:

    orders.csv
    order_items.csv
    operations.csv
    customer_analytics.csv

CSV digunakan untuk:

- Pandas
- Plotly
- Jupyter
- Colab
- Data analysis

Database tetap source of truth.

---

# 47. Customer Analytics

Jika analytics customer dikembangkan:

Customer identity tidak harus menggunakan account.

Data yang dikumpulkan harus sesuai kebutuhan bisnis dan privacy requirements.

Contoh analytical dimension:

- Order frequency
- Average order value
- Product preference
- Time of order

Jangan mengumpulkan personal data yang tidak diperlukan.

---

# 48. Performance

Target architecture harus mampu menangani burst request secara reasonable tanpa premature optimization.

Prioritas:

1. Database indexing
2. Efficient queries
3. Connection pooling
4. Pagination
5. Avoid N+1
6. Transaction boundaries
7. Rate limiting
8. Appropriate caching jika benar-benar dibutuhkan

Redis belum diperlukan untuk MVP.

---

# 49. Realtime

Target:

SSE.

Fallback MVP:

Polling 3–5 seconds.

Future:

WebSocket jika requirement benar-benar membutuhkan bidirectional realtime.

Jangan menambahkan WebSocket hanya karena terlihat lebih advanced.

---

# 50. Background Worker

Worker menangani:

- Reservation expiration
- Payment reconciliation
- Notification dispatch
- Overdue detection
- Daily aggregation
- Cleanup

Worker tidak boleh menjadi source of truth.

Worker hanya menjalankan background business operation terhadap database.

---

# 51. Testing Strategy

Testing terdiri dari:

## Unit Test

Menguji:

- Pricing
- Discount
- Tax
- State transition
- Stock calculation
- Change calculation
- Permission rules

## Integration Test

Menguji:

- Database
- Transaction
- Order creation
- Payment
- Inventory
- Webhook

## E2E Test

Menguji:

    Customer Order
         ↓
    Payment
         ↓
    Kitchen
         ↓
    Pickup
         ↓
    Completed

---

# 52. Critical Test Cases

Minimal test:

- Product unavailable
- Insufficient stock
- Concurrent checkout
- Duplicate checkout
- Duplicate webhook
- Payment failure
- Cash insufficient
- Duplicate cash confirmation
- Invalid pickup token
- Duplicate pickup
- Invalid state transition
- Unauthorized action
- Refund
- Order edit
- Reservation expiration
- Server failure
- Printer failure

---

# 53. Stress Testing

Stress scenario:

    10 concurrent users
    50 concurrent users
    100 concurrent users
    500 concurrent users

Yang diuji:

- API response
- Database connection
- Stock race
- Order creation
- Payment flow
- Queue processing

Capacity kitchen tetap merupakan operational constraint terpisah dari server capacity.

---

# 54. UI/UX Principles

Customer UI:

- Mobile first
- Minimal steps
- Clear pricing
- Clear payment state
- Clear order state
- Easy tracking
- Easy pickup

Staff UI:

- Action-oriented
- High information density
- Clear status
- Exception visibility
- Fast interaction

Admin UI:

- Data-oriented
- Analytics
- Management
- Configuration

Visual style:

- Clean
- Modern
- Professional
- Tech-oriented
- Minimal unnecessary animation

---

# 55. Responsive Design

Customer:

    Mobile → Tablet → Desktop

Staff:

    Tablet → Desktop → Mobile

Admin:

    Desktop → Tablet → Mobile

Customer ordering menjadi prioritas mobile-first.

---

# 56. Error UX

Error harus:

- Menjelaskan kondisi
- Tidak menyalahkan user
- Memberikan next action jika memungkinkan
- Tidak menampilkan technical stack trace
- Tidak membocorkan sensitive information

Contoh:

    "Pembayaran belum dapat dikonfirmasi.
     Silakan tunggu beberapa saat atau coba kembali."

Bukan:

    "500 INTERNAL SERVER ERROR SQLAlchemy Exception..."

---

# 57. Project Documentation

Dokumentasi:

    docs/
    ├── requirements/
    │   ├── functional-requirements.md
    │   └── business-rules.md
    ├── architecture/
    │   ├── architecture.md
    │   └── decisions.md
    ├── database/
    │   ├── erd.md
    │   └── database-design.md
    ├── ui-ux/
    │   ├── design-system.md
    │   ├── user-flow.md
    │   └── wireframes.md
    ├── api/
    │   └── api-design.md
    ├── testing/
    │   └── test-plan.md
    └── deployment/
        └── deployment.md

---

# 58. Development Workflow

Development mengikuti:

    1. Problem
    2. Stress Test
    3. Trade-off
    4. Decision
    5. Architecture
    6. ERD
    7. UI/UX
    8. API Design
    9. Implementation
    10. Testing
    11. Deploy

Coding tidak dimulai sebelum requirement dan architecture cukup jelas.

---

# 59. Implementation Rules

Implementasi harus:

- Mengikuti architecture.
- Mengikuti ERD.
- Mengikuti API contract.
- Mengikuti design system.
- Mengikuti business rules.
- Tidak membuat feature baru tanpa alasan.
- Tidak mengubah database schema sembarangan.
- Tidak memindahkan business logic ke frontend.
- Tidak menambahkan dependency tanpa kebutuhan.
- Tidak melakukan premature optimization.

---

# 60. Code Quality

Code harus:

- Readable
- Modular
- Testable
- Maintainable
- Consistent

Avoid:

- Giant files
- Giant functions
- Duplicate business logic
- Hidden side effects
- Hardcoded secrets
- Magic numbers
- Unnecessary abstractions

---

# 61. Git Rules

Commit harus menggambarkan perubahan.

Contoh:

    feat: add product API
    feat: add order creation
    fix: prevent duplicate pickup
    fix: validate cash payment
    refactor: simplify order service
    test: add inventory concurrency tests
    docs: update API design

Jangan menggunakan commit message seperti:

    update
    fix
    coba
    final
    final2
    fixbanget

---

# 62. Environment

Development menggunakan environment variables.

Contoh:

    DATABASE_URL=
    PAYMENT_API_KEY=
    PAYMENT_SECRET=
    JWT_SECRET=

Jangan memasukkan actual secret ke repository.

`.env.example` hanya berisi placeholder.

---

# 63. Deployment Philosophy

Target:

> Free infrastructure, production-minded architecture.

MVP tidak perlu infrastructure kompleks.

Prioritas:

- Reliable database
- Secure environment variables
- HTTPS
- Health check
- Logging
- Backup
- Simple deployment
- Easy rollback

---

# 64. Deployment Architecture

    User
      ↓
    Frontend Hosting
      ↓
    FastAPI Backend
      ↓
    Managed PostgreSQL

External:

    FastAPI
      ↓
    Payment Gateway

Realtime:

    FastAPI
      ↓
    SSE
      ↓
    Frontend

---

# 65. MVP Scope

MVP wajib memiliki:

### Customer

- QR menu
- Product browsing
- Cart
- Checkout
- QRIS
- Cash
- Order tracking
- Pickup token

### Staff

- Login
- Kitchen
- Cashier
- Pickup
- Controller

### Admin

- Product management
- Inventory
- Orders
- Basic analytics

### Backend

- REST API
- PostgreSQL
- Authentication
- RBAC
- Payment webhook
- Stock reservation
- Audit log

---

# 66. Future Scope

Feature yang dapat ditambahkan setelah MVP:

- Ingredient inventory
- BOM
- Supplier management
- Advanced loyalty
- Customer account
- Membership
- Advanced recommendation
- Advanced forecasting
- WebSocket
- Redis
- Queue infrastructure
- Microservices jika scale benar-benar membutuhkan
- Advanced BI
- Multi-branch support

Feature tersebut tidak menjadi alasan untuk overengineering MVP.

---

# 67. Explicit Non-Goals

MVP tidak bertujuan menjadi:

- Enterprise ERP
- Full accounting system
- Full CRM
- Multi-branch platform
- Microservices platform
- Advanced warehouse management
- Complex loyalty platform

Fokus MVP adalah café ordering dan operational workflow.

---

# 68. Definition of Done

Feature dianggap selesai jika:

- Requirement jelas.
- Business rule jelas.
- UI flow tersedia.
- API tersedia.
- Database sesuai.
- Backend validation tersedia.
- Authorization tersedia jika diperlukan.
- Error state tersedia.
- Test tersedia.
- Tidak merusak existing flow.
- Documentation diperbarui jika behavior berubah.

---

# 69. Final System Flow

    ┌──────────────────────┐
    │      CUSTOMER        │
    └──────────┬───────────┘
               │
               ▼
           React Menu
               │
               ▼
             Cart
               │
               ▼
           Checkout
               │
               ▼
          FastAPI Order
               │
               ▼
          PostgreSQL
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
      QRIS           Cash
        │             │
        ▼             ▼
   Payment Gateway   Cashier
        │             │
        └──────┬──────┘
               ▼
             PAID
               │
               ▼
           CONFIRMED
               │
               ▼
             KITCHEN
               │
               ▼
            PREPARING
               │
               ▼
              READY
               │
               ▼
             PICKUP
               │
               ▼
           COMPLETED
               │
               ▼
            ANALYTICS

---

# 70. Final Engineering Principle

Monster Café bukan sekadar website menu.

Sistem ini dirancang sebagai operational transaction system.

Karena itu:

    UI
     ↓
    API
     ↓
    Business Rules
     ↓
    Database
     ↓
    Operational Events
     ↓
    Analytics

harus konsisten.

Jika frontend terlihat benar tetapi database salah, sistem tetap salah.

Jika payment terlihat berhasil tetapi backend belum terverifikasi, sistem belum boleh menganggap transaction selesai.

Jika stock terlihat tersedia tetapi concurrent transaction membuat stock negatif, sistem salah.

Jika order terlihat READY tetapi satu item masih REMAKE, sistem salah.

Jika pickup berhasil dua kali untuk satu order, sistem salah.

Engineering decision selalu diprioritaskan berdasarkan correctness, security, consistency, lalu convenience.

---

# 71. Current Project Status

Requirement:

    LOCKED

Stress Test:

    COMPLETED

Business Rules:

    LOCKED

Architecture:

    LOCKED

ERD:

    LOCKED

Database Design:

    LOCKED

UI/UX Design System:

    DEFINED

User Flow:

    DEFINED

Wireframes:

    DEFINED

API Design:

    DEFINED

Next phase:

    IMPLEMENTATION

Implementation harus mengikuti seluruh dokumen yang sudah ditetapkan di atas.

Jangan mengubah architecture, database model, business rules, atau core UX tanpa melakukan review terhadap trade-off terlebih dahulu.