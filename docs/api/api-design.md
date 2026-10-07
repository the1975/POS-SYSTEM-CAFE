# Monster Café — API Design

## 1. Overview

Dokumen ini mendefinisikan rancangan REST API untuk sistem Monster Café.

API menjadi penghubung antara:

Customer / Staff / Admin
        ↓
Frontend React
        ↓
FastAPI
        ↓
Service Layer
        ↓
Repository Layer
        ↓
PostgreSQL

API bertanggung jawab terhadap:

- Validasi request
- Authentication
- Authorization
- Business rules
- Transaction processing
- Order management
- Payment processing
- Inventory management
- Kitchen operations
- Pickup verification
- Notifications
- Analytics

Frontend tidak boleh menjadi sumber kebenaran untuk:

- Harga
- Total pembayaran
- Stock
- Payment status
- Order status
- Permission
- Refund
- Role

Semua keputusan tersebut harus divalidasi oleh backend.

---

# 2. API Principles

API menggunakan prinsip:

- RESTful resource design
- JSON request/response
- HTTP status code yang sesuai
- Stateless request
- Backend sebagai source of truth
- Transaction integrity
- Idempotency untuk operasi sensitif
- RBAC untuk staff/admin
- Pagination untuk collection
- Filtering dan sorting bila diperlukan
- Consistent error response
- Audit logging untuk sensitive actions

---

# 3. Base URL

Development:

`/api/v1`

Production:

`https://<domain>/api/v1`

Semua endpoint aplikasi menggunakan prefix:

`/api/v1`

Contoh:

`GET /api/v1/products`

---

# 4. HTTP Methods

## GET

Mengambil data.

Contoh:

`GET /api/v1/products`

## POST

Membuat resource atau menjalankan operation.

Contoh:

`POST /api/v1/orders`

## PATCH

Mengubah sebagian resource.

Contoh:

`PATCH /api/v1/orders/{order_id}`

## PUT

Digunakan hanya jika replacement penuh memang diperlukan.

## DELETE

Digunakan secara terbatas.

Data transaksi tidak boleh dihapus secara hard delete hanya karena user meminta delete.

Untuk order yang sudah masuk proses transaksi, gunakan status:

`CANCELLED`

---

# 5. Authentication

Customer MVP tidak membutuhkan account.

Customer menggunakan:

- Order number
- Tracking token
- Pickup token

Order number bukan credential.

Tracking token harus bersifat random dan tidak mudah ditebak.

Database menyimpan:

`tracking_token_hash`

bukan raw tracking token.

---

# 6. Staff Authentication

Staff dan admin menggunakan authentication.

Contoh:

`POST /api/v1/auth/login`

Request:

    {
      "email": "staff@example.com",
      "password": "********"
    }

Response:

    {
      "access_token": "********",
      "token_type": "bearer",
      "user": {
        "id": "uuid",
        "name": "Staff",
        "role": "KITCHEN"
      }
    }

Password tidak pernah dikembalikan API.

---

# 7. Authorization

Role:

- ORDER_CONTROLLER
- KITCHEN
- CASHIER
- PICKUP
- ADMIN
- OWNER

Authorization harus dilakukan backend.

Frontend hanya menyembunyikan UI berdasarkan role untuk usability.

Frontend bukan security boundary.

---

# 8. Standard Response

## Success

Contoh:

    {
      "success": true,
      "data": {},
      "message": "Request successful"
    }

## Collection

    {
      "success": true,
      "data": [],
      "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 100,
        "total_pages": 5
      }
    }

## Error

    {
      "success": false,
      "error": {
        "code": "ORDER_NOT_FOUND",
        "message": "Order tidak ditemukan.",
        "details": null
      }
    }

---

# 9. HTTP Status Codes

Gunakan:

`200 OK`

Request berhasil.

`201 Created`

Resource baru berhasil dibuat.

`202 Accepted`

Request diterima tetapi proses asynchronous.

`204 No Content`

Berhasil tanpa response body.

`400 Bad Request`

Request tidak valid.

`401 Unauthorized`

Belum authenticated atau credential invalid.

`403 Forbidden`

Authenticated tetapi tidak memiliki permission.

`404 Not Found`

Resource tidak ditemukan.

`409 Conflict`

Conflict karena state atau concurrency.

`422 Unprocessable Entity`

Validation request gagal.

`429 Too Many Requests`

Rate limit tercapai.

`500 Internal Server Error`

Unexpected server error.

`503 Service Unavailable`

Service atau dependency sedang tidak tersedia.

---

# 10. API Modules

Endpoint utama dikelompokkan menjadi:

    /auth
    /products
    /categories
    /orders
    /payments
    /inventory
    /kitchen
    /pickup
    /notifications
    /analytics
    /users
    /health

---

# 11. Health API

## GET /health

Digunakan untuk health check.

Response:

    {
      "status": "ok",
      "service": "monster-cafe-api"
    }

Health check tidak membutuhkan authentication.

Health check dapat dikembangkan untuk mengecek dependency database jika diperlukan.

---

# 12. Category API

## GET /categories

Mengambil kategori aktif.

Response:

    {
      "success": true,
      "data": [
        {
          "id": "uuid",
          "name": "Food",
          "description": "Main food",
          "sort_order": 1
        }
      ]
    }

---

## GET /categories/{category_id}

Mengambil detail category.

---

## POST /categories

Role:

- ADMIN
- OWNER

Request:

    {
      "name": "Food",
      "description": "Main food",
      "sort_order": 1
    }

---

## PATCH /categories/{category_id}

Mengubah category.

---

# 13. Product API

## GET /products

Customer dapat mengambil product yang tersedia.

Query parameter:

`category_id`

`search`

`page`

`page_size`

`sort`

Contoh:

`GET /api/v1/products?category_id=food&search=nasi&page=1&page_size=20`

Response:

    {
      "success": true,
      "data": [
        {
          "id": "uuid",
          "name": "Nasi Goreng",
          "description": "Nasi goreng spesial",
          "price": 25000,
          "image_url": "/images/nasi-goreng.jpg",
          "is_available": true
        }
      ],
      "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 1,
        "total_pages": 1
      }
    }

`cost_price` tidak boleh dikembalikan ke customer.

---

## GET /products/{product_id}

Mengambil detail product.

---

## POST /products

Role:

- ADMIN
- OWNER

Request:

    {
      "category_id": "uuid",
      "name": "Nasi Goreng",
      "description": "Nasi goreng spesial",
      "price": 25000,
      "cost_price": 15000,
      "image_url": "/images/nasi-goreng.jpg",
      "is_available": true
    }

---

## PATCH /products/{product_id}

Mengubah product.

Perubahan harga hanya dapat dilakukan oleh role yang memiliki permission.

Historical order tidak ikut berubah.

Order lama menggunakan:

- product_name_snapshot
- unit_price

---

# 14. Customer Order API

## POST /orders

Membuat order baru.

Request:

    {
      "customer_name": "Leonardo",
      "items": [
        {
          "product_id": "uuid",
          "quantity": 2
        },
        {
          "product_id": "uuid",
          "quantity": 1
        }
      ],
      "payment_method": "QRIS"
    }

Backend harus:

1. Validate product.
2. Validate availability.
3. Read current price.
4. Calculate subtotal.
5. Calculate discount.
6. Calculate tax.
7. Calculate total.
8. Check stock.
9. Create order.
10. Create order items.
11. Create stock reservation.
12. Create payment record.
13. Commit transaction.
14. Return order information.

Frontend tidak boleh mengirim total sebagai trusted value.

---

# 15. Create Order Response

Response:

    {
      "success": true,
      "data": {
        "order_id": "uuid",
        "order_number": "A127",
        "customer_name": "Leonardo",
        "status": "PENDING",
        "payment_method": "QRIS",
        "subtotal": 57000,
        "discount_amount": 0,
        "tax_amount": 5700,
        "total": 62700,
        "tracking_token": "random-secure-token"
      }
    }

Raw tracking token hanya diberikan pada saat pembuatan order.

Database menyimpan hash token.

---

# 16. Idempotency Create Order

Checkout harus mendukung idempotency key.

Header:

`Idempotency-Key: <unique-client-key>`

Tujuan:

Mencegah duplicate order ketika:

- User double click.
- Network retry.
- Browser retry request.
- Mobile connection unstable.

Request dengan idempotency key yang sama tidak boleh membuat duplicate transaction.

---

# 17. Get Customer Order

## GET /orders/{order_id}

Untuk internal authenticated staff atau customer dengan valid tracking token.

Customer harus menyediakan tracking token melalui mekanisme yang aman.

Response:

    {
      "success": true,
      "data": {
        "order_number": "A127",
        "customer_name": "Leonardo",
        "status": "PREPARING",
        "payment_status": "PAID",
        "items": [
          {
            "name": "Nasi Goreng",
            "quantity": 2,
            "status": "PREPARING"
          }
        ],
        "total": 62700
      }
    }

---

# 18. Customer Order Tracking

## GET /orders/{order_id}/tracking

Response harus fokus pada informasi customer.

Contoh:

    {
      "order_number": "A127",
      "status": "PREPARING",
      "orders_ahead": 12,
      "kitchen_load": "HIGH_LOAD",
      "estimated_wait_min": 15,
      "estimated_wait_max": 20,
      "items": [
        {
          "name": "Nasi Goreng",
          "quantity": 2,
          "status": "READY"
        },
        {
          "name": "Es Teh",
          "quantity": 1,
          "status": "PREPARING"
        }
      ]
    }

Informasi internal yang tidak perlu tidak dikirim ke customer.

---

# 19. Update Order

## PATCH /orders/{order_id}

Digunakan untuk customer edit order jika business rules mengizinkan.

Customer dapat mengubah order sebelum item masuk preparation.

Request:

    {
      "items": [
        {
          "product_id": "uuid",
          "quantity": 2
        }
      ]
    }

Backend harus:

1. Validate current order state.
2. Validate edit limit.
3. Validate stock.
4. Recalculate price.
5. Create revision.
6. Preserve previous revision.
7. Update stock reservation atomically.
8. Handle payment difference if applicable.
9. Move order to appropriate queue state.
10. Commit transaction.

---

# 20. Order Revision

Setiap perubahan order harus mempertahankan history.

Contoh:

    Revision 1
    Nasi Goreng ×1
    Total Rp25.000

          ↓ edit

    Revision 2
    Nasi Goreng ×2
    Es Teh ×1
    Total Rp57.000

Previous revision tidak dihapus.

---

# 21. Cancel Order

## POST /orders/{order_id}/cancel

Customer dapat melakukan cancellation jika state mengizinkan.

Backend memeriksa:

- Current order status
- Payment status
- Cancellation rule
- Refund requirement

Response:

    {
      "success": true,
      "data": {
        "order_number": "A127",
        "status": "CANCELLED",
        "refund_status": "REFUND_PENDING"
      }
    }

Cancellation setelah preparation membutuhkan authorization staff/controller sesuai business rules.

---

# 22. Staff Orders API

## GET /staff/orders

Role:

- ORDER_CONTROLLER
- CASHIER
- KITCHEN
- PICKUP
- ADMIN
- OWNER

Query:

`status`

`payment_status`

`date`

`page`

`page_size`

`search`

Contoh:

`GET /api/v1/staff/orders?status=READY&page=1&page_size=20`

---

# 23. Staff Order Detail

## GET /staff/orders/{order_id}

Mengembalikan informasi operasional yang dibutuhkan staff.

Response dapat mencakup:

- Order number
- Customer name
- Items
- Item status
- Payment
- Total
- Timeline
- Pickup status
- Exception status

Sensitive data tetap mengikuti role permission.

---

# 24. Payment API

## POST /payments

Biasanya dipanggil oleh backend melalui order/payment flow.

Customer tidak boleh menentukan:

- Paid status
- Provider transaction ID
- Payment confirmation

---

# 25. Create QRIS Payment

## POST /payments/qris

Request:

    {
      "order_id": "uuid"
    }

Backend:

1. Validate order.
2. Validate amount.
3. Validate payment method.
4. Create provider transaction.
5. Store provider transaction ID.
6. Return payment instructions.

Response:

    {
      "success": true,
      "data": {
        "payment_id": "uuid",
        "payment_status": "PENDING",
        "payment_url": "provider-generated-url",
        "expires_at": "2026-10-07T12:00:00"
      }
    }

---

# 26. Payment Webhook

## POST /payments/webhook

Endpoint dipanggil payment provider.

Webhook harus:

- Validate signature.
- Validate event.
- Validate transaction reference.
- Check event idempotency.
- Update payment.
- Update order if appropriate.
- Convert stock reservation.
- Record payment event.
- Record order status history.
- Trigger notification.
- Commit transaction.

Webhook tidak boleh membuat duplicate payment state.

---

# 27. Payment Event Idempotency

`payment_events.event_id` harus UNIQUE.

Jika webhook event yang sama masuk dua kali:

Request kedua tidak boleh menjalankan business logic dua kali.

---

# 28. QRIS Payment State

Flow:

    PENDING
       ↓
    PAID

Failure:

    PENDING
       ↓
    FAILED

Refund:

    PAID
       ↓
    REFUND_REQUESTED
       ↓
    REFUND_PENDING
       ↓
    REFUNDED

Refund failure:

    REFUND_PENDING
       ↓
    REFUND_FAILED

---

# 29. Cash Payment

## POST /payments/{payment_id}/cash-confirm

Role:

- CASHIER
- ADMIN
- OWNER

Request:

    {
      "cash_received": 100000
    }

Backend menghitung change.

Response:

    {
      "success": true,
      "data": {
        "payment_status": "PAID",
        "amount": 62700,
        "cash_received": 100000,
        "change": 37300
      }
    }

Backend tidak menerima `change` sebagai trusted input.

---

# 30. Cash Validation

Jika:

`cash_received < total`

Response:

    {
      "success": false,
      "error": {
        "code": "INSUFFICIENT_CASH",
        "message": "Jumlah uang tidak mencukupi."
      }
    }

Order tetap:

`WAITING_CASH`

---

# 31. Refund API

## POST /payments/{payment_id}/refund

Role:

- ADMIN
- OWNER

Request:

    {
      "amount": 62700,
      "reason": "Stock unavailable"
    }

Backend wajib:

- Validate payment state.
- Validate refundable amount.
- Validate authorization.
- Create refund state.
- Record audit log.
- Communicate with payment provider if applicable.
- Prevent duplicate refund.

---

# 32. Inventory API

## GET /inventory

Role:

- ORDER_CONTROLLER
- ADMIN
- OWNER

Response:

    {
      "success": true,
      "data": [
        {
          "product_id": "uuid",
          "product_name": "Nasi Goreng",
          "quantity_available": 25,
          "quantity_reserved": 5,
          "reorder_level": 10
        }
      ]
    }

---

# 33. Stock Adjustment

## POST /inventory/{product_id}/adjust

Role:

- ADMIN
- OWNER

Request:

    {
      "quantity": -5,
      "reason": "Damaged stock"
    }

Backend harus:

- Lock inventory row.
- Validate resulting stock.
- Update inventory.
- Create stock movement.
- Create audit log.

Semua dilakukan dalam satu database transaction.

---

# 34. Stock Reservation

Stock flow:

    AVAILABLE
        ↓
    RESERVED
        ↓
    CONVERTED
        ↓
    SOLD / CONSUMED

Jika reservation expired:

    RESERVED
        ↓
    EXPIRED
        ↓
    AVAILABLE

Reservation tidak dianggap sebagai final sale.

---

# 35. Kitchen API

## GET /kitchen/orders

Role:

- KITCHEN
- ORDER_CONTROLLER
- ADMIN
- OWNER

Query:

`status`

`page`

`page_size`

Example:

`GET /api/v1/kitchen/orders?status=CONFIRMED`

---

# 36. Start Preparing

## POST /kitchen/orders/{order_id}/start

Role:

- KITCHEN
- ORDER_CONTROLLER
- ADMIN
- OWNER

Backend:

1. Validate order status.
2. Validate payment.
3. Validate stock/order state.
4. Update order status.
5. Create order status history.
6. Update item statuses if applicable.
7. Commit transaction.

Order:

`CONFIRMED → PREPARING`

---

# 37. Mark Item Ready

## POST /kitchen/order-items/{order_item_id}/ready

Role:

- KITCHEN
- ORDER_CONTROLLER
- ADMIN
- OWNER

Request tidak perlu menerima quantity sebagai trusted value jika seluruh item quantity dianggap selesai.

Backend menentukan apakah item sudah selesai berdasarkan item state.

Jika semua order items ready:

`PREPARING → READY`

Jika belum:

Order tetap:

`PREPARING`

---

# 38. Remake API

## POST /kitchen/order-items/{order_item_id}/remake

Request:

    {
      "reason": "DAMAGED",
      "notes": "Minuman tumpah saat preparation"
    }

Reason dapat berupa:

- WRONG_MENU
- WRONG_SIZE
- WRONG_TOPPING
- WRONG_QUANTITY
- DAMAGED
- SPILLED
- CUSTOMER_REQUEST
- OTHER

Backend membuat:

`remake_event`

dan memasukkan item kembali ke production flow.

Order item tidak dibuat sebagai order baru.

---

# 39. Pickup API

## GET /pickup/orders

Role:

- PICKUP
- ORDER_CONTROLLER
- ADMIN
- OWNER

Hanya menampilkan order yang relevan untuk pickup.

Default:

`READY`

---

# 40. Pickup Verification

## POST /pickup/verify

Request:

    {
      "pickup_token": "secure-random-token"
    }

Backend:

1. Hash token.
2. Search matching pickup.
3. Validate pickup state.
4. Validate order state.
5. Return order summary.

Response:

    {
      "success": true,
      "data": {
        "order_number": "A127",
        "customer_name": "Leonardo",
        "status": "READY",
        "payment_status": "PAID",
        "items": [
          {
            "name": "Nasi Goreng",
            "quantity": 2
          }
        ]
      }
    }

---

# 41. Complete Pickup

## POST /pickup/{pickup_id}/complete

Role:

- PICKUP
- ORDER_CONTROLLER
- ADMIN
- OWNER

Backend menggunakan atomic update.

Valid transition:

`WAITING_PICKUP → COMPLETED`

Jika sudah completed:

Return:

`409 Conflict`

Pickup tidak boleh dilakukan dua kali.

---

# 42. Notification API

## GET /notifications

Role:

Authenticated staff/admin.

Query:

`is_read`

`type`

`page`

`page_size`

---

# 43. Mark Notification Read

## POST /notifications/{notification_id}/read

Mengubah:

`is_read = true`

dan:

`read_at = current timestamp`

---

# 44. Realtime Updates

Target architecture menggunakan SSE.

Endpoint contoh:

## GET /events/orders/{order_id}

Digunakan customer untuk menerima update order.

Event contoh:

    order.updated

    {
      "order_number": "A127",
      "status": "READY"
    }

Customer dapat menerima:

- Payment update
- Order status
- Item status
- Ready notification
- Important operational message

---

# 45. Staff Realtime Events

Contoh:

## GET /events/staff

Event:

- New order
- Payment confirmed
- Kitchen status changed
- Order ready
- Exception created
- Stock issue

---

# 46. Polling Fallback

Jika SSE belum tersedia pada MVP, frontend dapat menggunakan polling.

Recommended interval:

`3–5 seconds`

Polling harus dihentikan ketika:

- User meninggalkan halaman.
- Order sudah completed.
- Browser tidak aktif dalam waktu lama.
- Tidak ada kebutuhan update.

Polling tidak boleh menghasilkan request berlebihan.

---

# 47. Controller API

## GET /controller/dashboard

Mengembalikan operational summary.

Contoh:

    {
      "active_orders": 24,
      "preparing_orders": 12,
      "ready_orders": 5,
      "exceptions": 3,
      "kitchen_load": "HIGH_LOAD"
    }

---

# 48. Action Center

## GET /controller/exceptions

Mengambil exception aktif.

Contoh:

    {
      "data": [
        {
          "id": "uuid",
          "type": "STOCK_ISSUE",
          "order_number": "A124",
          "priority": "HIGH",
          "status": "OPEN"
        }
      ]
    }

Exception dapat berupa:

- Payment issue
- Stock issue
- Late order
- Remake
- Pickup backlog
- System issue

---

# 49. Resolve Exception

## POST /controller/exceptions/{exception_id}/resolve

Request:

    {
      "resolution": "Replace unavailable item"
    }

Backend harus mencatat action pada audit log.

---

# 50. Analytics API

## GET /analytics/summary

Role:

- ADMIN
- OWNER

Query:

`start_date`

`end_date`

Response:

    {
      "revenue": 18200000,
      "orders": 542,
      "units_sold": 1280,
      "gross_profit": 7100000,
      "average_order_value": 33579
    }

---

# 51. Analytics Top Products

## GET /analytics/products/top

Query:

`start_date`

`end_date`

`limit`

Response:

    {
      "data": [
        {
          "product_id": "uuid",
          "product_name": "Es Teh",
          "units_sold": 150,
          "revenue": 1050000
        }
      ]
    }

---

# 52. Analytics Peak Hours

## GET /analytics/peak-hours

Response:

    {
      "data": [
        {
          "hour": 12,
          "orders": 84
        },
        {
          "hour": 13,
          "orders": 92
        }
      ]
    }

---

# 53. Analytics Operational Metrics

## GET /analytics/operations

Metrics:

- Average preparation time
- Average pickup waiting time
- Remake count
- Cancellation count
- Payment failure count
- Overdue order count

Contoh:

    {
      "average_preparation_minutes": 12.4,
      "average_pickup_wait_minutes": 4.8,
      "remake_count": 8,
      "cancelled_orders": 5,
      "payment_failures": 3,
      "overdue_orders": 2
    }

---

# 54. CSV Export

Analytics export dapat menggunakan endpoint:

`GET /analytics/export/orders`

`GET /analytics/export/order-items`

`GET /analytics/export/operations`

CSV digunakan untuk:

- Pandas
- Jupyter
- Colab
- External analysis

CSV bukan source of truth.

PostgreSQL tetap menjadi source of truth.

---

# 55. User API

## GET /users

Role:

- ADMIN
- OWNER

Digunakan untuk staff management.

Response tidak pernah mengembalikan password hash.

---

# 56. Create User

## POST /users

Request:

    {
      "name": "Kitchen Staff",
      "email": "kitchen@example.com",
      "password": "********",
      "role_id": "uuid"
    }

Backend:

- Hash password.
- Validate role.
- Validate email uniqueness.
- Create user.
- Create audit log.

---

# 57. Update User

## PATCH /users/{user_id}

Dapat digunakan untuk:

- Name
- Role
- Active status

Password update sebaiknya menggunakan endpoint khusus.

---

# 58. API Validation

Semua request harus divalidasi menggunakan schema.

Validation meliputi:

- Required fields
- Data type
- Range
- Enum
- UUID
- Quantity
- Price rules
- State transition
- Permission

Contoh quantity:

`quantity >= 1`

Tidak boleh menerima:

`quantity = 0`

atau:

`quantity = -1`

---

# 59. Price Validation

Frontend boleh mengirim:

`product_id`

`quantity`

Frontend tidak dipercaya untuk:

`unit_price`

`subtotal`

`discount`

`tax`

`total`

Backend mengambil harga dari database dan menghitung ulang.

---

# 60. Discount Validation

Backend memastikan:

`discount_amount <= eligible_subtotal`

Total tidak boleh menjadi negatif.

Contoh:

    subtotal = 100000
    discount = 10000
    taxable_amount = 90000
    tax = 9000
    total = 99000

Formula aktual harus mengikuti business rules yang telah ditetapkan.

---

# 61. Payment Security

Payment status tidak boleh diubah oleh frontend.

Contoh request berbahaya:

    {
      "payment_status": "PAID"
    }

Request tersebut harus ditolak.

Payment status hanya dapat berubah melalui trusted backend flow:

- Cashier confirmation
- Payment gateway webhook
- Authorized refund flow

---

# 62. Order State Validation

Valid transition:

    PENDING
       ↓
    CONFIRMED
       ↓
    PREPARING
       ↓
    READY
       ↓
    COMPLETED

Cancellation:

    PENDING → CANCELLED

atau sesuai authorization:

    CONFIRMED → CANCELLED

Exception state:

    PREPARING → OVERDUE

sesuai operational rule.

Backend harus menolak state transition yang tidak valid.

---

# 63. Concurrency

Operasi berikut harus atomic:

- Stock reservation
- Stock release
- Cash payment confirmation
- Pickup completion
- Payment processing
- Order state transition

Database transaction dan row-level locking digunakan jika diperlukan.

Contoh:

Dua customer membeli stock terakhir secara bersamaan.

Backend harus memastikan hanya request yang valid yang memperoleh stock.

---

# 64. Transaction Boundary

Contoh create order:

    BEGIN

    Validate products
    Lock inventory
    Check stock
    Reserve stock
    Create order
    Create order items
    Create payment
    Create history

    COMMIT

Jika salah satu gagal:

    ROLLBACK

Tidak boleh menghasilkan:

Order berhasil dibuat tetapi stock reservation gagal.

---

# 65. Idempotency

Operation yang membutuhkan idempotency:

- Create order
- Payment creation
- Payment webhook
- Cash confirmation
- Refund
- Pickup completion

Tujuan:

Mencegah duplicate side effect akibat retry.

---

# 66. Rate Limiting

Rate limiting diterapkan terutama pada:

- Login
- Order creation
- Payment endpoint
- Tracking endpoint
- Pickup verification
- Public API

Public endpoint tidak boleh dapat digunakan untuk request flooding tanpa batas.

---

# 67. Error Codes

Gunakan error code yang konsisten.

Contoh:

`PRODUCT_NOT_FOUND`

`PRODUCT_UNAVAILABLE`

`INSUFFICIENT_STOCK`

`ORDER_NOT_FOUND`

`ORDER_INVALID_STATE`

`ORDER_EDIT_NOT_ALLOWED`

`PAYMENT_NOT_FOUND`

`PAYMENT_ALREADY_PAID`

`PAYMENT_FAILED`

`INSUFFICIENT_CASH`

`REFUND_NOT_ALLOWED`

`PICKUP_TOKEN_INVALID`

`PICKUP_ALREADY_COMPLETED`

`FORBIDDEN_ACTION`

`IDEMPOTENCY_CONFLICT`

`RATE_LIMITED`

---

# 68. Logging

Backend harus mencatat error dan operational events tanpa menyimpan secret.

Jangan log:

- Password
- Access token
- Tracking token
- Pickup token
- Payment secret
- API secret

Sensitive data harus dimasking jika memang diperlukan untuk debugging.

---

# 69. Audit Logging

Sensitive action wajib masuk `audit_logs`.

Contoh:

- Product price change
- Inventory adjustment
- Refund
- Order cancellation by staff
- Role change
- User activation/deactivation
- Manual payment action
- Critical order modification

Audit log minimal mencatat:

- User
- Action
- Entity
- Entity ID
- Old value
- New value
- Timestamp
- IP jika tersedia

---

# 70. Pagination

Collection endpoint menggunakan pagination.

Default:

`page = 1`

`page_size = 20`

Maximum:

`page_size = 100`

Backend harus membatasi maximum page size.

---

# 71. Search

Search digunakan pada endpoint yang membutuhkan lookup.

Contoh:

`GET /staff/orders?search=A127`

atau:

`GET /staff/orders?search=Leonardo`

Search harus menggunakan indexed field jika query menjadi besar.

---

# 72. Sorting

Sorting harus menggunakan field yang diizinkan.

Contoh:

`sort=created_at`

`sort=-created_at`

Frontend tidak boleh bebas mengirim arbitrary database column untuk mencegah query abuse.

---

# 73. API Security Rules

Backend wajib:

- Validate authentication.
- Validate authorization.
- Validate input.
- Recalculate financial values.
- Validate state transition.
- Validate ownership/access.
- Use parameterized database queries.
- Use HTTPS production.
- Rate limit public endpoints.
- Hash credentials/tokens.
- Protect webhook.
- Log sensitive actions.

---

# 74. API Performance Rules

Backend harus menghindari:

- N+1 query
- Query tanpa index pada high-volume field
- Full table scan untuk request normal
- Unlimited pagination
- Excessive polling
- Large unnecessary response payload
- Long-running transaction

Response hanya mengirim data yang dibutuhkan client.

---

# 75. API and Database Relationship

API:

    Router
       ↓
    Schema Validation
       ↓
    Service
       ↓
    Repository
       ↓
    SQLAlchemy
       ↓
    PostgreSQL

Router tidak boleh mengandung business logic kompleks.

Repository tidak boleh menentukan business rules.

Service menjadi pusat business logic.

---

# 76. Example Service Flow

Create Order:

    Router
      ↓
    Validate Schema
      ↓
    Order Service
      ↓
    Product Repository
      ↓
    Inventory Repository
      ↓
    Order Repository
      ↓
    Payment Repository
      ↓
    Commit Transaction
      ↓
    Response

---

# 77. API Documentation

FastAPI menyediakan interactive documentation.

Development:

`/docs`

Alternative:

`/redoc`

Production access dapat dibatasi sesuai deployment/security requirements.

API documentation harus mencerminkan endpoint aktual.

---

# 78. API Versioning

Current:

`/api/v1`

Breaking changes menggunakan versi baru.

Contoh:

`/api/v2`

Jangan mengubah behavior breaking secara diam-diam pada `/api/v1`.

---

# 79. Background Worker Responsibilities

Background worker digunakan untuk pekerjaan yang tidak perlu blocking request utama.

Contoh:

- Expired stock reservation
- Payment reconciliation
- Notification dispatch
- Overdue detection
- Daily closing aggregation
- Cleanup

Request utama tetap harus cepat.

---

# 80. Payment Reconciliation

Jika payment provider dan server sempat tidak sinkron:

Background worker melakukan reconciliation.

Contoh:

    Local:
    PENDING

    Provider:
    PAID

Worker dapat memperbaiki state setelah validasi.

Reconciliation harus idempotent.

---

# 81. Reservation Expiration

Worker mencari:

`ACTIVE`

dengan:

`expires_at < current_time`

Kemudian:

1. Lock reservation.
2. Release reserved stock.
3. Update reservation.
4. Record stock movement.
5. Update order jika diperlukan.
6. Commit.

---

# 82. API Failure Principles

Jika database gagal:

Jangan return success.

Jika payment provider timeout:

Jangan langsung menganggap payment gagal jika status belum diketahui.

Jika browser customer tertutup:

Transaction tetap berjalan di backend.

Jika printer gagal:

Order tetap valid.

Jika notification gagal:

Order tetap valid.

Source of truth tetap:

PostgreSQL + verified payment state.

---

# 83. API Acceptance Criteria

API dianggap siap jika:

- Endpoint memiliki schema validation.
- Authorization berjalan pada backend.
- Price dihitung backend.
- Stock divalidasi backend.
- Payment state tidak dapat dimanipulasi frontend.
- Order state transition tervalidasi.
- Sensitive operation memiliki audit log.
- Payment webhook idempotent.
- Checkout idempotent.
- Pickup completion atomic.
- Stock reservation atomic.
- Error response konsisten.
- Pagination tersedia untuk collection besar.
- Rate limiting diterapkan pada public/sensitive endpoint.
- Tidak ada secret di response atau log.
- API documentation tersedia.

---

# 84. MVP Endpoint Summary

## Authentication

    POST /auth/login
    POST /auth/logout
    GET  /auth/me

## Products

    GET    /products
    GET    /products/{id}
    POST   /products
    PATCH  /products/{id}

## Categories

    GET    /categories
    GET    /categories/{id}
    POST   /categories
    PATCH  /categories/{id}

## Customer Orders

    POST   /orders
    GET    /orders/{id}
    GET    /orders/{id}/tracking
    PATCH  /orders/{id}
    POST   /orders/{id}/cancel

## Staff Orders

    GET    /staff/orders
    GET    /staff/orders/{id}

## Payments

    POST   /payments/qris
    POST   /payments/webhook
    POST   /payments/{id}/cash-confirm
    POST   /payments/{id}/refund

## Inventory

    GET    /inventory
    POST   /inventory/{product_id}/adjust

## Kitchen

    GET    /kitchen/orders
    POST   /kitchen/orders/{id}/start
    POST   /kitchen/order-items/{id}/ready
    POST   /kitchen/order-items/{id}/remake

## Pickup

    GET    /pickup/orders
    POST   /pickup/verify
    POST   /pickup/{id}/complete

## Notifications

    GET    /notifications
    POST   /notifications/{id}/read

## Controller

    GET    /controller/dashboard
    GET    /controller/exceptions
    POST   /controller/exceptions/{id}/resolve

## Analytics

    GET    /analytics/summary
    GET    /analytics/products/top
    GET    /analytics/peak-hours
    GET    /analytics/operations
    GET    /analytics/export/orders
    GET    /analytics/export/order-items
    GET    /analytics/export/operations

## Users

    GET    /users
    POST   /users
    PATCH  /users/{id}

## Health

    GET    /health

## Realtime

    GET    /events/orders/{order_id}
    GET    /events/staff

---

# 85. Final API Architecture

Monster Café API mengikuti:

    React
      ↓
    FastAPI Router
      ↓
    Pydantic Schema
      ↓
    Service Layer
      ↓
    Repository Layer
      ↓
    SQLAlchemy
      ↓
    PostgreSQL

External integrations:

    FastAPI
       ├── Payment Gateway
       ├── SSE / Notification
       └── Printer / Operational Services

Background:

    Worker
       ├── Reservation Expiration
       ├── Payment Reconciliation
       ├── Notification Dispatch
       ├── Overdue Detection
       └── Daily Aggregation

Prinsip utama:

    Client meminta.
    Backend memvalidasi.
    Service menjalankan business rules.
    Database menjaga integrity.
    External service dikonfirmasi.
    Response dikirim setelah state yang relevan berhasil dipastikan.