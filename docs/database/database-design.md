# Monster Café — Database Design

## 1. Overview

Database Monster Café menggunakan PostgreSQL sebagai source of truth untuk seluruh transaksi dan operasi utama sistem.

Database dirancang untuk mendukung:

- Self-ordering melalui QR
- POS/manual order oleh staff
- Guest customer tanpa account
- QRIS dan pembayaran cash
- Inventory dan stock reservation
- Kitchen production
- Pickup verification
- Order revision
- Remake
- Notification
- Audit log
- Analytics
- Concurrent transactions
- Idempotent payment processing

Prinsip utama:

> Database harus menjaga integritas transaksi meskipun terjadi concurrent request, payment retry, duplicate webhook, browser closure, atau kegagalan service.

---

## 2. Database Technology

### DBMS

PostgreSQL.

### ORM

SQLAlchemy 2.x.

### Migration

Alembic.

### Database Access

Frontend tidak berkomunikasi langsung dengan database.

Arsitektur:

    Frontend
       ↓
    FastAPI
       ↓
    Service Layer
       ↓
    Repository Layer
       ↓
    SQLAlchemy
       ↓
    PostgreSQL

---

## 3. Primary Key Strategy

Entity utama menggunakan UUID sebagai primary key internal.

Contoh: `id = UUID`

Keuntungan:

- Tidak mudah ditebak.
- Aman untuk identifier internal.
- Cocok untuk distributed request.
- Tidak mengekspos jumlah record secara langsung.
- Memisahkan internal identifier dari identifier customer.

Customer-facing order menggunakan `order_number`.

Contoh:

    A127
    A128
    A129

`order_number` harus UNIQUE.

---

## 4. Timestamp Strategy

Entity transaksi menggunakan timestamp untuk mengetahui lifecycle data.

Field umum:

`created_at`
`updated_at`

Field lifecycle:

`confirmed_at`
`preparing_at`
`ready_at`
`completed_at`
`cancelled_at`

Timestamp disimpan menggunakan UTC pada database.

Frontend mengubah timestamp ke timezone lokal ketika ditampilkan.

---

## 5. Roles and Users

### 5.1 roles

Menyimpan role internal.

Role MVP:

- ADMIN
- CONTROLLER
- KITCHEN
- CASHIER
- PICKUP

Role menentukan permission.

### 5.2 users

Hanya staff dan admin yang memiliki account.

Customer guest tidak dibuat sebagai user.

Relasi:

`roles 1 ──── N users`

Constraint:

`users.email UNIQUE`

User yang dinonaktifkan tidak boleh melakukan login atau action baru.

Historical data tetap mempertahankan `user_id`.

---

## 6. Product Structure

### 6.1 categories

Menyimpan kategori produk.

Relasi:

`categories 1 ──── N products`

Produk tidak dihapus secara fisik ketika sudah pernah digunakan dalam transaksi.

Gunakan `is_available` untuk mengontrol apakah produk dapat dipesan.

### 6.2 products

Menyimpan data produk saat ini.

Field penting:

`price`
`cost_price`
`is_available`

`price` digunakan sebagai harga aktif saat order dibuat.

`cost_price` digunakan untuk perhitungan HPP/gross profit.

---

## 7. Historical Product Snapshot

Data transaksi tidak boleh bergantung sepenuhnya pada data produk saat ini karena harga atau nama produk dapat berubah.

Contoh:

Hari ini:

`Nasi Goreng = Rp20.000`

Bulan depan:

`Nasi Goreng = Rp25.000`

Order lama tetap harus menunjukkan:

`Nasi Goreng = Rp20.000`

Karena itu `order_items` menyimpan:

`product_name_snapshot`
`unit_price`

Dengan demikian historical transaction tetap konsisten.

---

## 8. Inventory Design

Inventory MVP menggunakan product-level inventory.

Relasi:

`products 1 ──── 1 inventory`

Field utama:

`quantity_available`
`quantity_reserved`

Secara konsep:

`Total Physical Stock = quantity_available + quantity_reserved`

Total physical stock tidak disimpan sebagai field terpisah pada MVP.

---

## 9. Inventory Reservation

Stock reservation digunakan ketika customer melakukan checkout.

Flow:

`AVAILABLE → RESERVED → CONVERTED → SOLD`

Jika reservation timeout:

`RESERVED → EXPIRED → AVAILABLE`

Jika order dibatalkan:

`RESERVED → CANCELLED → AVAILABLE`

Reservation timeout MVP:

`7 menit`

Nilai timeout harus configurable dan tidak boleh hardcoded di banyak tempat.

---

## 10. Inventory Concurrency

Inventory merupakan area yang membutuhkan concurrency control.

Contoh:

Stock produk = `1`

Dua customer melakukan checkout bersamaan.

Request A membutuhkan `1`.

Request B membutuhkan `1`.

Sistem tidak boleh menghasilkan:

`quantity_available = -1`

atau menerima kedua order secara tidak konsisten.

Backend harus menggunakan database transaction dan mekanisme atomic update atau row locking.

Contoh konsep SQL:

    UPDATE inventory
    SET quantity_available = quantity_available - :quantity
    WHERE product_id = :product_id
      AND quantity_available >= :quantity;

Jika affected row = `0`:

`Stock tidak cukup.`

Transaction kemudian rollback.

---

## 11. Stock Movements

Setiap perubahan stok penting harus dapat ditelusuri.

Movement type:

- SALE
- RESERVATION
- RELEASE
- RESTOCK
- ADJUSTMENT
- WASTE
- REMAKE

`stock_movements` berfungsi sebagai audit trail perubahan inventory.

Perubahan stok tidak boleh dilakukan hanya dengan mengubah angka inventory tanpa mencatat movement yang relevan.

---

## 12. Order Lifecycle

Order lifecycle utama:

`PENDING → CONFIRMED → PREPARING → READY → COMPLETED`

Alternative:

`PENDING → CANCELLED`

atau:

`CONFIRMED → CANCELLED`

Jika customer tidak mengambil order:

`READY → OVERDUE`

`OVERDUE` bukan berarti order otomatis dibatalkan.

Staff mengikuti SOP pickup.

---

## 13. Payment Lifecycle

### QRIS

Flow:

`PENDING → Payment Gateway → Customer Payment → Webhook → PAID → Order CONFIRMED`

Browser customer boleh ditutup setelah payment dilakukan.

Backend tetap memproses payment melalui webhook atau reconciliation.

### Cash

Flow:

`PENDING → WAITING_CASH → Cashier menerima uang → PAID → Order CONFIRMED`

Order cash yang belum dibayar tidak boleh masuk kitchen.

---

## 14. Payment Idempotency

Payment processing harus idempotent.

Satu payment tidak boleh diproses berulang kali akibat webhook yang sama dikirim beberapa kali.

`payment_events.event_id` harus UNIQUE.

Jika event sudah pernah diproses:

`return existing result`

dan jangan menjalankan business logic kedua kali.

---

## 15. Payment Provider Transaction ID

`provider_transaction_id` digunakan untuk menghubungkan payment internal dengan payment provider.

Constraint:

`UNIQUE`

PostgreSQL memperbolehkan beberapa nilai NULL pada UNIQUE column.

Nilai ini dapat NULL sebelum provider memberikan transaction ID.

---

## 16. Payment Reconciliation

Jika webhook gagal diterima atau service mengalami downtime, sistem harus memiliki mekanisme reconciliation.

Contoh:

`Payment Gateway → Reconciliation Worker → Check payment status → Update local payment`

Tujuannya agar database lokal tidak selamanya menunjukkan:

`PENDING`

padahal payment provider sudah menunjukkan:

`PAID`

---

## 17. Order Revision

Customer dapat mengubah order selama masih diperbolehkan oleh business rules.

Contoh order awal:

- Nasi Goreng ×1
- Es Teh ×1

Customer melakukan edit:

- Nasi Goreng ×1
- Es Teh ×2

Revision baru dibuat.

Order tetap menggunakan `order_id` yang sama.

Revision menyimpan snapshot kondisi order pada saat perubahan.

---

## 18. Revision Number

Setiap order revision memiliki `revision_number`.

Contoh:

Order A127:

- Revision 1
- Revision 2
- Revision 3

Constraint:

`(order_id, revision_number) UNIQUE`

Revision number harus meningkat secara berurutan.

---

## 19. Order Edit and Queue

Jika order masih boleh diedit:

`Customer Edit → Validate → Recalculate → Check Stock → Update Revision → Requeue`

Order yang diedit dapat kembali ke bagian belakang antrean sesuai business rules.

Order tidak membuat `order_id` baru.

---

## 20. Order Total Calculation

Backend menjadi sumber kebenaran perhitungan transaksi.

Formula:

`Subtotal → Discount → DPP → Tax → Total`

Contoh:

- Subtotal = Rp100.000
- Discount = Rp10.000
- DPP = Rp90.000
- Tax = Rp9.000
- Total = Rp99.000

Formula pajak harus configurable sesuai aturan bisnis dan regulasi yang berlaku.

Frontend tidak boleh menentukan final total.

---

## 21. Discount Rules

Discount tidak boleh:

`< 0`

dan tidak boleh melebihi nilai transaksi yang eligible.

Contoh:

- Subtotal = Rp50.000
- Discount = Rp60.000

Tidak valid.

Backend harus menolak transaksi tersebut.

---

## 22. QRIS Fee

Payment processing fee bukan revenue tambahan.

Contoh:

Customer membayar:

`Rp100.000`

Payment fee:

`Rp700`

Revenue:

`Rp100.000`

Payment fee:

`Rp700`

Net received:

`Rp99.300`

Accounting detail dapat dikembangkan lebih lanjut pada financial module.

---

## 23. Pickup Security

Pickup menggunakan secure token.

Flow:

`Customer → Show QR / Token → Staff Scan → Backend Verify → Check Order Status → Atomic Pickup Completion`

Order hanya boleh diselesaikan jika berada pada status pickup yang diizinkan.

Token pickup tidak boleh disimpan dalam plaintext.

Database menyimpan:

`pickup_token_hash`

---

## 24. Pickup Concurrency

Dua staff tidak boleh berhasil mengambil order yang sama secara bersamaan.

Contoh:

Staff A scan A127.

Staff B scan A127.

Hanya satu request yang boleh berhasil.

Database transaction harus melakukan atomic state transition:

`WAITING_PICKUP → COMPLETED`

Request kedua harus mendapatkan response bahwa pickup sudah selesai.

---

## 25. Remake

Remake tidak membuat order baru.

Contoh:

Order A127
→ Nasi Goreng
→ Remake #1

`order_item_id` tetap sama.

Remake dicatat pada:

`remake_events`

Alasan harus tersedia agar dapat dianalisis.

---

## 26. Kitchen Item Status

Status item dapat digunakan untuk melacak kondisi setiap item.

Status:

- PENDING
- PREPARING
- READY
- REMAKE

Contoh order:

- Es Teh — READY
- Nasi Goreng — READY
- Kentang — REMAKE

Order hanya dapat menjadi `READY` jika seluruh item yang diperlukan telah siap.

---

## 27. Order Status vs Item Status

Order status dan item status memiliki fungsi berbeda.

Order status:

- PENDING
- CONFIRMED
- PREPARING
- READY
- COMPLETED

Item status:

- PENDING
- PREPARING
- READY
- REMAKE

Order tidak boleh dianggap `READY` hanya karena satu item selesai.

Semua item yang dibutuhkan harus selesai atau memenuhi aturan operasional yang telah ditentukan.

---

## 28. Audit Log

Action sensitif harus dicatat.

Contoh:

- REFUND
- CANCEL_ORDER
- MANUAL_PAYMENT_CONFIRMATION
- STOCK_ADJUSTMENT
- PRICE_CHANGE
- ORDER_MODIFICATION
- REMAKE

Audit log minimal menyimpan:

- user
- action
- entity
- entity_id
- old_value
- new_value
- timestamp

Audit log tidak boleh digunakan sebagai tempat menyimpan secret atau password.

---

## 29. Soft Delete

Data transaksi tidak boleh dihapus secara fisik hanya karena sudah tidak aktif.

Untuk product/category/user, gunakan status seperti:

`is_active`
`is_available`

Historical transaction harus tetap dapat dibaca.

Contoh:

Product: Nasi Goreng

Jika produk tidak dijual lagi:

`is_available = false`

bukan menghapus record product.

---

## 30. Referential Integrity

Foreign key digunakan untuk menjaga hubungan antar entity.

Contoh:

`order_items.order_id → orders.id`

`order_items.product_id → products.id`

`payments.order_id → orders.id`

`pickups.order_id → orders.id`

Foreign key tidak boleh menunjuk ke entity yang tidak ada.

---

## 31. Delete Strategy

Untuk transaksi:

- orders
- order_items
- payments
- payment_events
- order_status_history
- pickups
- audit_logs

tidak boleh dihapus secara sembarangan.

Historical transaction harus dipertahankan.

Penghapusan data operasional harus mengikuti policy retention dan audit.

---

## 32. Transaction Boundaries

Business operation penting harus menggunakan database transaction.

Contoh checkout:

`BEGIN → Validate products → Validate prices → Check inventory → Reserve stock → Create order → Create order items → Create payment → COMMIT`

Jika terjadi error:

`ROLLBACK`

Tidak boleh terjadi kondisi:

`Order berhasil tetapi Stock reservation gagal`

tanpa mekanisme recovery yang jelas.

---

## 33. Payment Confirmation Transaction

Ketika payment menjadi PAID:

`BEGIN → Validate payment event → Check idempotency → Update payment → Convert reservation → Update order → CONFIRMED → Create status history → Create notification/event → COMMIT`

Semua state penting harus konsisten.

---

## 34. Cash Payment Transaction

Ketika cashier menerima pembayaran cash:

`BEGIN → Check order → Check WAITING_CASH → Record payment → Calculate change → Set payment = PAID → Set order = CONFIRMED → Create status history → COMMIT`

Cash yang diterima harus cukup.

Contoh:

Total = Rp25.000

Cash = Rp20.000

Tidak valid.

---

## 35. Concurrency Principles

Database operations yang menyangkut:

- Inventory
- Payment
- Pickup
- Order status
- Order revision

harus memperhatikan concurrent request.

Prinsip:

`Read → Validate → Lock / Atomic Update → Write → Commit`

Jangan mengandalkan frontend untuk mencegah race condition.

---

## 36. Idempotency

Operation berikut harus dirancang idempotent:

- Checkout retry
- Payment webhook
- Payment confirmation
- Pickup completion
- Stock reservation recovery
- Notification dispatch

Tujuannya agar retry tidak menciptakan duplicate transaction.

---

## 37. Analytics

Analytics membaca data transaksi dari PostgreSQL.

Database transaksi tetap menjadi source of truth.

Analytics dapat menghitung:

- Revenue
- Orders
- Units Sold
- COGS
- Gross Profit
- Top Products
- Peak Hours
- Preparation Time
- Pickup Time
- Remake Rate
- Cancellation Rate
- Payment Failure Rate

Formula:

`Gross Profit = Revenue - COGS`

Revenue tidak sama dengan profit.

---

## 38. Analytics Isolation

Query analytics yang berat tidak boleh mengganggu transaksi utama.

Untuk MVP:

`PostgreSQL → Read queries / optimized queries → Analytics`

Jika skala meningkat, dapat dipertimbangkan:

- Read replica
- Materialized view
- Reporting database
- Data warehouse

Tidak diperlukan pada MVP.

---

## 39. CSV Export

CSV bukan source of truth.

CSV hanya digunakan sebagai export untuk analisis.

Contoh:

- `orders.csv`
- `order_items.csv`
- `operations.csv`
- `customer_analytics.csv`

Database tetap menjadi sumber data utama.

---

## 40. Query Performance Principles

Backend harus menghindari:

- N+1 query
- SELECT tanpa kebutuhan
- Query tanpa pagination
- Query analytics berat pada transaction endpoint
- Full table scan yang tidak diperlukan

Untuk list data gunakan pagination.

Contoh:

`GET /orders?page=1&limit=20`

atau cursor pagination jika diperlukan.

---

## 41. Connection Pooling

FastAPI menggunakan database connection pool melalui SQLAlchemy.

Tujuan:

- Menghindari membuka koneksi baru setiap request.
- Mengontrol jumlah koneksi.
- Meningkatkan efisiensi database.

Connection pool harus disesuaikan dengan kapasitas PostgreSQL dan deployment environment.

---

## 42. Database Security

Database credentials tidak boleh disimpan di source code.

Gunakan environment variables.

Contoh:

`DATABASE_URL=`

File `.env` tidak boleh masuk Git.

Yang boleh masuk repository:

`.env.example`

tanpa credential asli.

---

## 43. Sensitive Data

Jangan menyimpan:

- Plaintext password
- Plaintext tracking token
- Plaintext pickup token
- Payment secret
- API secret

Password harus menggunakan password hashing yang aman.

Token customer harus disimpan sebagai hash.

Secret payment disimpan melalui environment variable atau secret management.

---

## 44. Backend Authority

Frontend tidak boleh menentukan:

- price
- subtotal
- discount
- tax
- total
- payment status
- inventory availability
- role permission
- order status

Frontend hanya mengirim input.

Backend melakukan:

- validation
- calculation
- authorization
- database transaction

---

## 45. Data Consistency Rules

Invariant utama:

`quantity_available >= 0`

`quantity_reserved >= 0`

`order.total >= 0`

`payment.amount > 0`

`order_number UNIQUE`

`payment_events.event_id UNIQUE`

`provider_transaction_id UNIQUE`

`pickup.order_id UNIQUE`

`inventory.product_id UNIQUE`

`(order_id, revision_number) UNIQUE`

---

## 46. Order and Payment Consistency

Order tidak boleh menjadi `CONFIRMED` tanpa payment yang valid, kecuali order tersebut merupakan transaksi cash yang sudah dikonfirmasi cashier atau flow internal yang memang diizinkan.

Untuk QRIS:

`Payment PAID → Order CONFIRMED`

Untuk cash:

`Cash received → Payment PAID → Order CONFIRMED`

---

## 47. Failure Handling

Jika database transaction gagal:

`ROLLBACK`

Jika payment gateway gagal:

`payment = FAILED`

Jika webhook duplicate:

`ignore duplicate event`

Jika printer gagal:

`order tetap valid`

Jika browser customer ditutup:

`backend tetap memproses order/payment`

Jika pickup gagal:

`order tidak boleh dianggap COMPLETED`

---

## 48. Reservation Expiration Worker

Background worker mencari reservation yang:

`status = ACTIVE`

dan:

`expires_at < current_time`

Kemudian:

`ACTIVE → EXPIRED`

dan stok dikembalikan:

`quantity_reserved ↓`

`quantity_available ↑`

Operation harus transactional dan idempotent.

---

## 49. Background Worker Responsibilities

Worker dapat menangani:

- Reservation expiration
- Payment reconciliation
- Notification dispatch
- Overdue order detection
- Daily closing aggregation
- Cleanup

Worker bukan pengganti database transaction.

---

## 50. Database Backup

Database production harus memiliki backup strategy.

Minimum principle:

`Database → Automated Backup`

Backup tidak boleh dianggap sebagai pengganti audit log.

Recovery procedure harus dapat diuji.

---

## 51. Migration Strategy

Schema database dikelola menggunakan Alembic.

Contoh struktur:

    alembic/
    └── versions/
        ├── 001_initial_schema.py
        ├── 002_add_order_revisions.py
        └── 003_add_inventory_reservations.py

Migration harus:

- Versioned
- Reproducible
- Reviewable
- Tidak menghapus data production secara sembarangan

Jangan melakukan perubahan database manual tanpa migration jika perubahan tersebut perlu direproduksi pada environment lain.

---

## 52. Development Database

Environment development boleh menggunakan database yang berbeda dari production.

Contoh:

`Development → Neon development database`

`Production → Production PostgreSQL`

Credential masing-masing environment harus terpisah.

---

## 53. Database Environment Variables

Minimal:

`DATABASE_URL=`

Environment variable tambahan dapat digunakan sesuai deployment.

Jangan commit credential asli.

---

## 54. Final Database Principle

Database Monster Café dirancang dengan prinsip:

`Simple enough for MVP + Strong enough for real transactions`

Tidak menggunakan teknologi tambahan seperti:

- Redis
- Kafka
- Kubernetes
- Microservices
- Data Warehouse

pada tahap awal tanpa kebutuhan nyata.

PostgreSQL tetap menjadi pusat source of truth.

Architecture dapat dikembangkan ketika beban sistem benar-benar membutuhkan scaling tambahan.

---

## 55. Final Entity List

Database MVP terdiri dari 18 entity:

1. `roles`
2. `users`
3. `categories`
4. `products`
5. `inventory`
6. `stock_reservations`
7. `stock_movements`
8. `orders`
9. `order_items`
10. `order_revisions`
11. `order_revision_items`
12. `payments`
13. `payment_events`
14. `order_status_history`
15. `remake_events`
16. `pickups`
17. `notifications`
18. `audit_logs`

Dokumen ini menjadi referensi teknis database sebelum implementasi SQLAlchemy models dan Alembic migrations.