# Monster Café — User Flow

## 1. Overview

Dokumen ini mendefinisikan alur pengguna Monster Café dari awal sampai selesai.

User utama:

- Customer
- Order Controller
- Kitchen
- Cashier
- Pickup Staff
- Admin

Flow harus mengikuti business rules dan architecture yang sudah ditetapkan.

Prinsip utama:

> User mengikuti alur sederhana, sedangkan kompleksitas transaksi ditangani oleh backend.

---

## 2. Customer Flow Overview

Alur utama customer:

QR Scan
→ Menu
→ Product Detail
→ Cart
→ Checkout
→ Payment
→ Order Confirmation
→ Order Tracking
→ Ready
→ Pickup
→ Completed

Customer tidak membutuhkan account atau login.

---

## 3. Customer — Open Menu

Flow:

1. Customer scan QR code café.
2. Browser membuka universal menu.
3. System mengecek operating status.
4. Jika ordering sedang dibuka, customer dapat memilih produk.
5. Jika ordering ditutup, menu tetap dapat dilihat tetapi checkout tidak tersedia.

Universal QR tidak terikat pada meja.

---

## 4. Customer — Browse Menu

Customer dapat:

- Melihat kategori.
- Melihat produk.
- Melihat harga.
- Melihat availability.
- Membuka detail produk.
- Menambahkan produk ke cart.

Jika produk unavailable:

`Habis`

Customer tidak dapat menambahkannya ke cart.

---

## 5. Customer — Product Detail

Flow:

Menu
→ Product
→ Product Detail

Customer melihat:

- Nama produk
- Foto
- Deskripsi
- Harga
- Quantity
- Customization jika tersedia

Primary action:

`Tambah ke Keranjang`

Setelah berhasil:

`Produk ditambahkan ke keranjang.`

---

## 6. Customer — Cart

Customer dapat:

- Melihat item.
- Menambah quantity.
- Mengurangi quantity.
- Menghapus item.
- Kembali ke menu.
- Melanjutkan checkout.

Cart kosong:

`Keranjang masih kosong.`

Checkout tidak tersedia jika tidak ada item.

---

## 7. Customer — Checkout

Flow:

Cart
→ Checkout

System melakukan validation terhadap:

- Product availability
- Current price
- Quantity
- Stock
- Operating hours
- Discount eligibility

Backend menghitung ulang:

`Subtotal`

`Discount`

`Tax`

`Total`

Frontend tidak menentukan final transaction value.

---

## 8. Customer — Customer Name

Customer mengisi nama.

Nama customer:

- Tidak harus UNIQUE.
- Digunakan untuk human-readable identification.
- Dapat muncul pada order dan pickup.

Contoh:

`Nama: Leonardo`

Dua customer dapat memiliki nama yang sama.

Identitas transaksi tetap menggunakan `order_number` dan secure tracking token.

---

## 9. Customer — Checkout Validation

Jika semua valid:

`Checkout → Create Order`

Jika stock berubah dan tidak cukup:

`Checkout → Error → Return to Cart`

Contoh:

`Maaf, Nasi Goreng sudah habis.`

Cart tidak boleh dianggap berhasil checkout jika transaction belum berhasil dipersist.

---

## 10. Customer — Order Creation

Backend membuat:

- Order
- Order items
- Stock reservation
- Payment record
- Initial order status

Order mendapatkan:

`order_number`

Contoh:

`A127`

Internal database tetap menggunakan internal ID.

---

## 11. Customer — Payment Selection

Customer memilih:

- QRIS
- Cash

### QRIS

Flow:

`Checkout → QRIS → Payment Gateway`

### Cash

Flow:

`Checkout → Cash → Waiting for Cash Payment`

Cash order belum masuk kitchen sampai pembayaran dikonfirmasi.

---

## 12. Customer — QRIS Payment

Flow:

1. Customer memilih QRIS.
2. Backend membuat payment request.
3. Customer diarahkan ke payment interface.
4. Customer melakukan pembayaran.
5. Payment provider memproses transaksi.
6. Provider mengirim webhook.
7. Backend memverifikasi webhook.
8. Payment menjadi `PAID`.
9. Order menjadi `CONFIRMED`.
10. Order masuk kitchen queue.

Browser customer boleh ditutup setelah payment dilakukan.

Backend tetap memproses payment.

---

## 13. Customer — QRIS Payment Success

Setelah payment terkonfirmasi:

Customer melihat:

`Pembayaran berhasil`

`Order A127`

`Pesanan sedang diproses`

Customer dapat membuka:

`Lihat Status Pesanan`

---

## 14. Customer — QRIS Payment Pending

Jika payment belum dapat diverifikasi:

Status:

`Menunggu konfirmasi pembayaran`

Customer tidak boleh mendapatkan status:

`Order Confirmed`

sebelum backend memiliki confirmation yang valid.

System dapat melakukan reconciliation jika webhook belum diterima.

---

## 15. Customer — QRIS Payment Failed

Jika payment gagal:

`Payment = FAILED`

Customer mendapat informasi:

`Pembayaran gagal.`

Customer dapat mencoba metode pembayaran kembali sesuai business rules.

Reservation stock mengikuti expiration/cancellation policy.

---

## 16. Customer — Cash Payment

Flow:

1. Customer memilih cash.
2. Order dibuat dengan status payment `WAITING_CASH`.
3. Customer pergi ke cash counter.
4. Cashier mencari order.
5. Cashier menerima uang.
6. System menghitung kembalian.
7. Cashier mengonfirmasi pembayaran.
8. Payment menjadi `PAID`.
9. Order menjadi `CONFIRMED`.
10. Order masuk kitchen queue.

---

## 17. Customer — Cash Insufficient

Contoh:

Total:

`Rp35.000`

Cash:

`Rp30.000`

System menolak confirmation.

Tampilkan:

`Uang yang diterima belum mencukupi.`

Cashier meminta customer menambah pembayaran.

Order tetap:

`WAITING_CASH`

---

## 18. Customer — Order Confirmation

Setelah payment berhasil:

System menampilkan:

- Order number
- Customer name
- Total
- Payment status
- Order status
- Tracking action

Contoh:

`A127`

`Leonardo`

`Rp45.000`

`PAID`

`CONFIRMED`

---

## 19. Customer — Order Tracking

Customer dapat membuka tracking page tanpa login.

Tracking membutuhkan secure tracking token.

Order number bukan credential.

Tracking menampilkan:

- Order number
- Current status
- Items
- Payment
- Kitchen load
- Queue context
- Estimated waiting time
- Pickup information

---

## 20. Customer — Queue Information

Customer tidak perlu melihat internal queue implementation.

Contoh informasi:

`12 pesanan sedang dikerjakan`

`18 pesanan menunggu`

`Posisi sekitar #19`

`Estimasi 15–20 menit`

Informasi harus bersifat contextual.

Jangan menjanjikan waktu yang tidak dapat dijamin.

---

## 21. Customer — Preparing

Ketika order mulai diproses:

`CONFIRMED → PREPARING`

Customer melihat:

`Pesanan sedang disiapkan.`

Jika tersedia:

`Estimasi 15–20 menit`

---

## 22. Customer — Ready

Ketika semua item order sudah siap:

`PREPARING → READY`

Customer mendapat notification:

`Pesanan A127 siap diambil.`

Tracking page menunjukkan:

`READY — Siap diambil`

---

## 23. Customer — Pickup

Customer pergi ke pickup counter.

Customer menunjukkan:

- Pickup QR
- Pickup token
- Order information

Staff melakukan verification.

Flow:

`Show QR → Scan → Verify → Grab → Handover`

---

## 24. Customer — Pickup Complete

Setelah staff menyerahkan order:

`READY → COMPLETED`

Customer melihat:

`Pesanan selesai.`

Order tidak dapat digunakan kembali untuk pickup.

---

## 25. Customer — Pickup Token Invalid

Jika token tidak valid:

`Token pickup tidak valid.`

Pickup tidak dilakukan.

Order tetap pada status sebelumnya.

Tidak boleh mengubah order menjadi completed.

---

## 26. Customer — Pickup Already Completed

Jika order sudah diambil:

`Pesanan ini sudah selesai diambil.`

System menolak second pickup.

---

## 27. Customer — Customer Cancellation

Customer dapat membatalkan order hanya sebelum status yang tidak lagi mengizinkan cancellation.

Contoh:

`PENDING → CANCELLED`

Jika payment sudah terjadi, refund mengikuti business rules.

Setelah order masuk `PREPARING`, customer tidak dapat membatalkan secara normal.

Exception dapat dilakukan oleh staff/controller/admin sesuai permission.

---

## 28. Customer — Order Edit

Customer dapat mengedit order jika masih berada pada tahap yang diperbolehkan.

Flow:

`Open Tracking → Edit Order → Modify Items → Validate → Recalculate → Confirm`

System melakukan:

- Price validation
- Stock validation
- Discount recalculation
- Tax recalculation
- Total recalculation

---

## 29. Customer — Edit Price Increase

Jika perubahan meningkatkan total:

`New Total > Old Total`

Customer harus membayar selisih.

Order belum boleh diproses sebagai revision final sebelum payment difference berhasil.

---

## 30. Customer — Edit Price Decrease

Jika perubahan menurunkan total:

`New Total < Old Total`

Selisih dapat menjadi refund sesuai payment method dan business rules.

Revision harus tetap menyimpan historical snapshot.

---

## 31. Customer — Edit Stock Failure

Jika item baru tidak tersedia:

`Edit → Stock Validation → Failed`

Tampilkan:

`Item tersebut sudah tidak tersedia.`

Perubahan tidak boleh merusak order sebelumnya.

Original order tetap valid.

---

## 32. Customer — Edit Revision

Order tetap menggunakan:

`order_id yang sama`

System membuat:

`revision_number baru`

Contoh:

`A127 Revision 1`

kemudian:

`A127 Revision 2`

Historical revision tetap tersimpan.

---

## 33. Customer — Browser Closed

Jika browser ditutup:

Order tetap berada di backend.

Untuk QRIS:

Payment tetap dapat diproses melalui webhook/reconciliation.

Untuk order yang sudah confirmed:

Kitchen tetap memproses order.

Customer dapat kembali menggunakan tracking link/token.

---

## 34. Customer — Connection Lost

Jika koneksi hilang sebelum backend mengonfirmasi transaction:

Frontend tidak boleh menampilkan:

`Order berhasil`

sebagai fakta.

Frontend harus menunjukkan:

`Tidak dapat memastikan status transaksi.`

Customer dapat melakukan retry/check status.

Backend harus menggunakan idempotency agar retry tidak membuat duplicate order.

---

# 35. Kitchen Flow

Kitchen flow:

`Login → Kitchen Dashboard → New Order → Start Preparing → Prepare → Ready`

---

## 36. Kitchen — New Order

Ketika order confirmed:

Kitchen menerima order baru.

Tampilkan:

- Order number
- Items
- Quantity
- Notes
- Time
- Priority/status

Payment detail tidak perlu menjadi fokus utama.

---

## 37. Kitchen — Start Preparing

Kitchen memilih:

`Mulai`

Order:

`CONFIRMED → PREPARING`

System mencatat:

`preparing_at`

Order masuk active preparation.

---

## 38. Kitchen — Item Preparation

Kitchen dapat memproses item satu per satu.

Contoh:

A127:

`Nasi Goreng ×1 → READY`

`Es Teh ×1 → READY`

`Kentang ×1 → REMAKE`

Order belum `READY` sampai seluruh item memenuhi kondisi siap.

---

## 39. Kitchen — Item Ready

Kitchen menandai item:

`PREPARING → READY`

System menyimpan status item.

Jika seluruh item siap:

`Order → READY`

---

## 40. Kitchen — Remake

Jika terjadi masalah:

`Item → REMAKE`

Kitchen memilih reason:

- Wrong menu
- Wrong size
- Wrong topping
- Wrong quantity
- Damaged / spilled
- Customer changed request
- Other

System membuat `remake_event`.

Order item tetap menggunakan `order_item_id` yang sama.

---

## 41. Kitchen — Remake Production

Remake kembali ke production queue.

Flow:

`REMAKE → Production → PREPARING → READY`

Remake tidak membuat order baru.

---

## 42. Kitchen — Product Unavailable

Jika product tiba-tiba tidak tersedia:

Kitchen tidak boleh mengubah price atau payment.

Masalah diteruskan ke Controller.

Controller dapat melakukan:

- Replace item
- Partial refund
- Full refund
- Contact customer

sesuai business rules.

---

## 43. Controller Flow

Controller flow:

`Login → Dashboard → Monitor → Detect Exception → Resolve → Monitor`

Controller bukan middleman untuk setiap order.

Normal order harus berjalan otomatis.

Controller fokus pada exception.

---

## 44. Controller Dashboard

Controller melihat:

- Active orders
- Kitchen load
- Waiting orders
- Ready orders
- Pickup backlog
- Payment issue
- Stock issue
- Remake
- Late orders

---

## 45. Controller — Exception Handling

Action Center menampilkan:

`Payment Issue`

`Stock Issue`

`Late Order`

`Remake`

`Pickup Backlog`

`Critical Kitchen Load`

Controller memilih issue.

System menampilkan detail dan available actions.

---

## 46. Controller — Kitchen Overload

Kitchen load:

`NORMAL`

`BUSY`

`HIGH LOAD`

`CRITICAL`

Jika CRITICAL:

Controller dapat menutup ordering sementara.

Existing confirmed orders tetap diproses.

---

## 47. Controller — Manual Emergency Close

Controller/admin dapat melakukan emergency close.

Flow:

`Open → Emergency Close → Confirm`

New order ditolak.

Existing paid/confirmed order tetap diproses.

---

## 48. Controller — Order Issue

Jika order mengalami masalah:

Controller membuka order.

Tampilkan:

- Order
- Customer
- Items
- Payment
- Status
- Timeline
- Revision
- Remake
- Available actions

Controller melakukan action berdasarkan permission.

---

# 49. Cashier Flow

Cashier flow:

`Login → Payment Queue → Open Order → Receive Cash → Calculate Change → Confirm`

---

## 50. Cashier — Find Cash Order

Cashier dapat mencari berdasarkan:

- Order number
- Customer name

Order number menjadi identifier utama.

Customer name bukan unique.

---

## 51. Cashier — Receive Cash

Cashier memasukkan:

`Cash Received`

System menghitung:

`Change = Cash Received - Total`

Jika cash kurang:

`Cannot Confirm`

---

## 52. Cashier — Confirm Cash Payment

Jika cash cukup:

Cashier memilih:

`Konfirmasi Pembayaran`

Backend melakukan transaction:

`Payment → PAID`

`Order → CONFIRMED`

`Reservation → CONVERTED`

Kemudian order masuk kitchen.

---

# 53. Pickup Staff Flow

Pickup flow:

`Login → Pickup Dashboard → Scan → Verify → Grab → Handover → Complete`

---

## 54. Pickup — Scan

Staff scan QR/token customer.

Backend memverifikasi:

- Token
- Order existence
- Pickup existence
- Order status
- Payment status
- Completion status

---

## 55. Pickup — Verification Success

Jika valid:

Tampilkan:

`A127`

`Leonardo`

`3 Items`

`PAID`

`READY`

Staff mengambil order dari staging area.

---

## 56. Pickup — Handover

Staff menyerahkan order.

Kemudian memilih:

`Selesaikan Pickup`

Backend melakukan atomic transition:

`WAITING_PICKUP → COMPLETED`

---

## 57. Pickup — Duplicate Scan

Jika order sudah completed:

`Pickup sudah selesai.`

Second request tidak boleh membuat perubahan.

---

# 58. Admin Flow

Admin flow:

`Login → Dashboard → Manage → Monitor → Analyze`

Admin dapat:

- Manage users
- Manage products
- Manage categories
- Manage inventory
- View orders
- View sales
- View analytics
- Configure system

---

## 59. Admin — Product Management

Flow:

`Products → Add/Edit → Validate → Save`

Product dapat:

- Created
- Updated
- Disabled
- Re-enabled

Historical orders tidak berubah ketika product information berubah.

---

## 60. Admin — Inventory

Admin dapat:

- View stock
- Restock
- Adjustment
- View stock movement
- View reservation

Stock adjustment harus memiliki reason.

Contoh:

`Adjustment: Damaged stock`

---

## 61. Admin — Refund

Refund merupakan sensitive action.

Flow:

`Open Payment → Request Refund → Reason → Confirm → Process`

Refund harus dicatat pada:

- Payment
- Audit log
- Relevant status history

Refund tidak boleh dilakukan tanpa authorization.

---

## 62. Admin — User Management

Admin dapat:

- Create user
- Assign role
- Disable user
- Re-enable user

Role change harus dicatat pada audit log.

---

# 63. Operating Hours Flow

System memiliki configurable operating hours.

Contoh:

`Open: 09:00`

`Last Order: 21:45`

`Close: 22:00`

---

## 64. Before Opening

Menu dapat diakses.

Ordering belum tersedia.

Customer melihat:

`Ordering dibuka pukul 09:00.`

---

## 65. During Opening

Customer dapat melakukan order selama:

- Operating hours aktif
- Ordering tidak emergency closed
- Product tersedia
- Kitchen capacity memungkinkan

---

## 66. Last Order

Setelah last-order cutoff:

New order ditolak.

Existing confirmed order tetap diproses.

---

## 67. Closing

Ketika café tutup:

- New order disabled.
- Existing confirmed orders tetap diproses.
- Unpaid reservation dapat expired/released sesuai policy.
- Worker menjalankan closing tasks.

---

# 68. Notification Flow

Notification dapat berasal dari:

- Order confirmation
- Payment confirmation
- Preparing
- Ready
- Pickup
- Exception

Flow:

`Event → Notification Service → Delivery → Read`

---

## 69. Customer Notification

Customer dapat menerima:

`Pembayaran berhasil`

`Pesanan sedang disiapkan`

`Pesanan siap diambil`

Jika browser/session aktif, notification dapat muncul secara realtime.

Tracking page tetap menjadi fallback.

---

## 70. Staff Notification

Staff dapat menerima:

`New Order`

`Payment Confirmed`

`Remake`

`Critical Load`

`Pickup Backlog`

Notification harus dapat dibaca dari dashboard.

---

# 71. Analytics Flow

Analytics flow:

`Transaction Data → Aggregation → Visualization → Insight → Decision`

---

## 72. Daily Analytics

Dashboard dapat menampilkan:

- Orders
- Revenue
- COGS
- Gross Profit
- Units Sold
- Top Products
- Peak Hours
- Remake
- Cancellation
- Payment Failure

---

## 73. Daily Closing Flow

Closing:

`Orders → Payment Reconciliation → Revenue → COGS → Gross Profit → Cash/QRIS Reconciliation`

Revenue:

`Customer Transaction Value`

Gross profit:

`Revenue - COGS`

---

# 74. Background Worker Flow

Worker menjalankan scheduled/background jobs.

Tasks:

- Reservation expiration
- Payment reconciliation
- Notification dispatch
- Overdue detection
- Daily aggregation
- Cleanup

Worker tidak menggantikan database transaction.

---

# 75. Reservation Expiration Flow

Worker menemukan:

`ACTIVE`

dan:

`expires_at < now`

Flow:

`ACTIVE → EXPIRED`

Kemudian:

`quantity_reserved ↓`

`quantity_available ↑`

Operation harus transactional dan idempotent.

---

# 76. Payment Reconciliation Flow

Worker mencari payment yang masih:

`PENDING`

atau membutuhkan verification.

Flow:

`Local Payment → Provider Status → Compare → Update`

Jika provider:

`PAID`

maka local payment dapat menjadi:

`PAID`

sesuai verification rules.

---

# 77. Overdue Order Flow

Worker mencari order:

`READY`

yang belum diambil melewati operational threshold.

Flow:

`READY → OVERDUE`

Order tidak otomatis dibatalkan.

Staff mengikuti SOP.

---

# 78. Failure Flow

Jika server mengalami error:

Backend tidak boleh menganggap transaction berhasil tanpa persistence confirmation.

Jika database unavailable:

`Request → Failure`

Frontend menampilkan error/retry state.

---

# 79. Printer Failure Flow

Jika printer gagal:

Order tetap valid.

Database menjadi source of truth.

Staff dapat melakukan:

`Reprint`

Printer failure tidak boleh membatalkan order.

---

# 80. Payment Gateway Failure Flow

Jika payment gateway tidak tersedia:

Customer melihat:

`Pembayaran sementara tidak dapat diproses.`

Order tidak boleh menjadi `PAID` tanpa valid confirmation.

System dapat retry atau reconciliation sesuai provider capability.

---

# 81. Database Failure Flow

Jika database gagal:

Tidak boleh ada fake success.

Contoh:

Checkout request gagal persist:

`Order belum dikonfirmasi.`

Frontend dapat retry menggunakan idempotency key.

---

# 82. Duplicate Request Flow

Jika customer mengirim request yang sama dua kali:

Backend memeriksa idempotency key.

Jika transaction sebelumnya sudah berhasil:

Backend mengembalikan hasil transaction sebelumnya.

Tidak membuat order kedua.

---

# 83. Duplicate Webhook Flow

Jika payment provider mengirim webhook dua kali:

Backend memeriksa:

`payment_events.event_id`

Jika sudah ada:

`Ignore duplicate`

Tidak menjalankan payment transition dua kali.

---

# 84. Duplicate Pickup Flow

Jika dua staff scan order bersamaan:

Backend melakukan atomic state transition.

Request pertama:

`WAITING_PICKUP → COMPLETED`

Request kedua:

`Already completed`

Hanya satu request yang berhasil.

---

# 85. High Traffic Flow

Saat banyak customer melakukan request bersamaan:

Frontend
→ FastAPI
→ Connection Pool
→ PostgreSQL

Database menangani transactional consistency.

Capacity kitchen tetap menjadi operational constraint.

System tidak harus menolak customer hanya karena request traffic meningkat jika backend masih mampu menangani load.

---

# 86. Kitchen Capacity Flow

Kitchen capacity berbeda dari server capacity.

Server dapat menerima:

`100 users`

tetapi kitchen mungkin hanya mampu memproses:

`30 active orders`

Jika kitchen overload:

`Kitchen Load → HIGH / CRITICAL`

System dapat memperpanjang ETA atau menutup new order sementara.

---

# 87. Final Customer Flow

Customer:

`Scan QR`

↓

`Browse Menu`

↓

`Add Product`

↓

`Cart`

↓

`Checkout`

↓

`Enter Name`

↓

`Choose Payment`

↓

`Pay`

↓

`Order Confirmed`

↓

`Kitchen Preparation`

↓

`Ready`

↓

`Pickup Verification`

↓

`Handover`

↓

`Completed`

---

# 88. Final Staff Flow

Staff:

`Login`

↓

`Dashboard`

↓

`Normal Operation`

atau

`Exception`

↓

`Kitchen / Cashier / Pickup / Controller`

↓

`Resolve`

↓

`Update Status`

↓

`Audit`

---

# 89. Final System Flow

Monster Café secara keseluruhan:

`Customer`

↓

`Frontend`

↓

`FastAPI`

↓

`PostgreSQL`

↓

`Payment / Worker / Notification`

↓

`Kitchen`

↓

`Pickup`

↓

`Completed Order`

↓

`Analytics`

↓

`Business Insight`

↓

`Business Decision`

---

# 90. UX Principle

Normal flow harus otomatis.

Exception flow harus terlihat.

Customer harus mendapatkan informasi yang cukup.

Staff harus mendapatkan action yang jelas.

Backend harus menjadi authority.

Database harus menjadi source of truth.

User interface tidak boleh mengorbankan transaction integrity demi visual simplicity.

---

# 91. Final Rule

Jika terjadi konflik antara:

- Visual convenience
- Business rule
- Data integrity
- Security

Prioritas:

`Data Integrity`

↓

`Security`

↓

`Business Rules`

↓

`Usability`

↓

`Visual Design`

UI/UX harus mengikuti architecture, database design, requirements, dan business rules yang sudah dikunci sebelumnya.