# Monster Café — UI/UX Design System

## 1. Overview

Design system Monster Café dibuat untuk menghasilkan interface yang:

- Clean
- Modern
- Profesional
- Tech-oriented
- Mudah digunakan
- Cepat dipahami
- Responsive
- Tidak berlebihan dalam animasi
- Cocok untuk customer maupun staff

Design system harus menjaga konsistensi visual antara:

- Customer ordering
- Order tracking
- Kitchen
- Controller
- Cashier
- Pickup
- Admin
- Analytics

Prinsip utama:

> Interface harus membantu pengguna menyelesaikan pekerjaan, bukan membuat pengguna mengagumi interface.

---

## 2. Design Principles

### 2.1 Clarity First

Informasi paling penting harus langsung terlihat.

Customer harus mudah memahami:

- Produk
- Harga
- Cart
- Total
- Payment
- Status order
- Pickup information

Staff harus mudah memahami:

- Order yang harus dikerjakan
- Order yang bermasalah
- Payment issue
- Stock issue
- Remake
- Pickup backlog

---

### 2.2 Action-Oriented

Setiap halaman harus memiliki primary action yang jelas.

Contoh customer:

`Tambah ke Keranjang`

`Checkout`

`Bayar Sekarang`

Contoh kitchen:

`Mulai`

`Selesai`

`Remake`

Contoh pickup:

`Verifikasi`

`Serahkan Pesanan`

---

### 2.3 Minimal Cognitive Load

Jangan menampilkan informasi yang tidak diperlukan pada saat user sedang melakukan task.

Contoh:

Kitchen tidak perlu melihat:

- Customer analytics
- Gross profit
- Payment gateway detail

Customer tidak perlu melihat:

- Internal stock movement
- HPP
- Audit log
- Internal staff notes

---

### 2.4 Consistency

Komponen yang memiliki fungsi sama harus memiliki tampilan dan behaviour yang konsisten.

Contoh:

- Semua primary button memiliki visual yang sama.
- Semua status menggunakan pola badge yang konsisten.
- Semua form memiliki pola validation yang sama.
- Semua modal memiliki struktur yang sama.

---

### 2.5 Progressive Disclosure

Informasi detail ditampilkan ketika diperlukan.

Contoh:

Dashboard staff menampilkan:

`A127 — READY`

Ketika dibuka:

- Customer name
- Items
- Payment
- Timeline
- Notes
- Remake history

---

## 3. Visual Direction

Visual Monster Café menggunakan gaya:

`Modern Café + Professional POS + Technology`

Karakter visual:

- Clean
- Dark-friendly
- High contrast
- Rounded but not excessive
- Clear hierarchy
- Subtle depth
- Minimal decoration

Hindari:

- Glassmorphism berlebihan
- Gradient berlebihan
- Animasi berlebihan
- Neon yang terlalu kuat
- Card bertumpuk terlalu banyak
- Font terlalu dekoratif
- UI yang terlihat seperti game

---

## 4. Color System

Color system harus menggunakan semantic color.

### Primary

Digunakan untuk:

- Primary CTA
- Active navigation
- Important interactive elements
- Selected state

Primary color dapat menggunakan warna brand Monster Café.

### Neutral

Digunakan untuk:

- Background
- Surface
- Border
- Text
- Disabled state

Hierarchy:

- Background
- Surface
- Elevated surface
- Border
- Primary text
- Secondary text
- Muted text

### Success

Digunakan untuk:

- Payment berhasil
- Order ready
- Pickup completed
- Stock available
- Successful action

### Warning

Digunakan untuk:

- Kitchen busy
- Stock hampir habis
- Order terlambat
- Pending action

### Error

Digunakan untuk:

- Payment failed
- Stock unavailable
- Invalid input
- Failed request
- Critical system issue

### Info

Digunakan untuk:

- Informasi
- Processing
- Guidance
- System notification

---

## 5. Semantic Color Rules

Warna tidak boleh menjadi satu-satunya cara menyampaikan informasi.

Contoh status:

`PAID`

harus memiliki:

- Color
- Label
- Optional icon

Bukan hanya warna hijau.

Contoh:

`✓ PAID`

---

## 6. Typography

Typography harus mudah dibaca pada mobile dan desktop.

Gunakan satu font family utama untuk seluruh aplikasi.

Hierarchy:

### Display

Digunakan untuk:

- Landing section
- Important headline

### Heading 1

Digunakan untuk:

- Page title

### Heading 2

Digunakan untuk:

- Section title

### Heading 3

Digunakan untuk:

- Card title
- Product title

### Body

Digunakan untuk:

- Description
- Normal information

### Small

Digunakan untuk:

- Metadata
- Timestamp
- Supporting information

### Caption

Digunakan untuk:

- Secondary labels
- Helper text

---

## 7. Typography Rules

Jangan menggunakan terlalu banyak font size dalam satu halaman.

Gunakan hierarchy yang konsisten.

Primary information:

- Larger
- Higher contrast
- Semibold/bold

Secondary information:

- Smaller
- Lower contrast

Contoh product card:

`Nasi Goreng`

`Nasi goreng spesial dengan telur.`

`Rp25.000`

Harga harus lebih mudah ditemukan daripada description.

---

## 8. Spacing System

Gunakan spacing scale yang konsisten.

Recommended base:

`4px`

Scale:

- 4px
- 8px
- 12px
- 16px
- 20px
- 24px
- 32px
- 40px
- 48px
- 64px

Gunakan spacing yang lebih kecil untuk hubungan elemen yang dekat.

Gunakan spacing yang lebih besar untuk memisahkan section.

---

## 9. Border Radius

Gunakan rounded corner secara moderat.

Recommended:

- Small component: 6–8px
- Input/button: 8–10px
- Card: 12–16px
- Modal: 16–20px
- Large container: 20–24px

Hindari semua komponen menjadi terlalu bulat.

---

## 10. Shadows

Shadow digunakan untuk menunjukkan hierarchy.

Gunakan shadow secara subtle.

Contoh penggunaan:

- Floating action
- Modal
- Dropdown
- Elevated card

Jangan memberikan shadow besar pada semua card.

---

## 11. Buttons

Button memiliki tiga hierarchy utama.

### Primary

Untuk action utama.

Contoh:

`Checkout`

`Bayar Sekarang`

`Mulai Memasak`

### Secondary

Untuk action alternatif.

Contoh:

`Kembali`

`Edit`

`Lihat Detail`

### Destructive

Untuk action berisiko.

Contoh:

`Batalkan Order`

`Refund`

`Hapus Produk`

Destructive action harus membutuhkan confirmation jika memiliki dampak besar.

---

## 12. Button States

Setiap button harus memiliki state:

- Default
- Hover
- Focus
- Active
- Disabled
- Loading

Loading state tidak boleh memungkinkan user mengirim request yang sama berkali-kali.

Contoh:

`Bayar Sekarang`

menjadi:

`Memproses...`

selama request berlangsung.

---

## 13. Inputs

Input harus memiliki:

- Label
- Input field
- Optional helper text
- Error message

Contoh:

`Nama`

`[ Leonardo ]`

Jika error:

`Nama wajib diisi.`

Jangan hanya menggunakan placeholder sebagai label.

---

## 14. Form Validation

Validation dilakukan di:

1. Frontend untuk feedback cepat.
2. Backend untuk keamanan dan integritas.

Frontend validation bukan pengganti backend validation.

Contoh:

Customer mengirim quantity `-1`.

Frontend dapat menolak.

Tetapi backend juga wajib menolak.

---

## 15. Product Card

Product card minimal menampilkan:

- Product image
- Product name
- Short description
- Price
- Availability
- Primary action

Contoh:

`Nasi Goreng`

`Nasi goreng spesial`

`Rp25.000`

`+ Tambah`

Jika unavailable:

`Habis`

dan action tidak dapat digunakan.

---

## 16. Product Detail

Product detail menampilkan:

- Product image
- Product name
- Description
- Price
- Quantity
- Optional customization
- Add to cart

Primary action:

`Tambah ke Keranjang`

---

## 17. Cart

Cart harus menunjukkan:

- Product
- Quantity
- Unit price
- Subtotal
- Remove/edit action
- Total

Contoh:

`Nasi Goreng × 2`

`Rp25.000 × 2`

`Rp50.000`

Total harus terlihat jelas.

Primary action:

`Checkout`

---

## 18. Checkout

Checkout harus sederhana.

Urutan informasi:

1. Customer name
2. Order items
3. Subtotal
4. Discount
5. Tax
6. Total
7. Payment method
8. Confirmation

Primary action:

`Lanjutkan Pembayaran`

Backend tetap menghitung final total.

---

## 19. Payment UI

### QRIS

Tampilkan:

- Total
- Payment status
- QR/payment interface
- Expiration jika tersedia
- Processing state

Status:

`Menunggu pembayaran`

Setelah berhasil:

`Pembayaran berhasil`

### Cash

Tampilkan:

- Total
- Cash received
- Change
- Confirmation

Contoh:

`Total: Rp25.000`

`Uang diterima: Rp50.000`

`Kembalian: Rp25.000`

---

## 20. Order Success

Setelah order berhasil, customer harus mendapatkan confirmation yang jelas.

Tampilkan:

- Order number
- Customer name
- Payment status
- Total
- Order status
- Pickup information

Contoh:

`A127`

`Pesanan berhasil dibuat`

Primary action:

`Lihat Status Pesanan`

---

## 21. Order Tracking

Customer harus dapat melihat:

- Order number
- Current status
- Items
- Payment status
- Queue context
- Estimated waiting time
- Pickup information

Contoh:

`A127`

`Sedang diproses`

`12 pesanan sedang dikerjakan`

`Estimasi 15–20 menit`

Jangan menampilkan angka queue yang membingungkan tanpa konteks.

---

## 22. Order Status UI

Status utama:

- PENDING
- CONFIRMED
- PREPARING
- READY
- COMPLETED
- CANCELLED
- OVERDUE

Contoh visual:

`✓ Pembayaran berhasil`

`● Sedang disiapkan`

`✓ Pesanan siap diambil`

Status harus mudah dipahami customer.

---

## 23. Kitchen UI

Kitchen membutuhkan interface yang berbeda dari customer.

Prioritas informasi:

1. Order number
2. Item
3. Quantity
4. Status
5. Special instruction
6. Timer
7. Remake indicator

Harga dan informasi finansial tidak perlu menjadi fokus utama kitchen.

---

## 24. Kitchen Order Card

Contoh:

`A127`

`Nasi Goreng × 1`

`Es Teh × 2`

`Kentang × 1`

Action:

`Mulai`

Setelah preparation:

`Selesai`

Jika masalah:

`Remake`

---

## 25. Kitchen Queue

Queue harus mudah dipindai secara visual.

Contoh:

`NOW`

A127

A128

A129

Kemudian:

`NEXT`

A130

A131

Jangan menggunakan terlalu banyak informasi pada satu card.

---

## 26. Remake UI

Ketika item remake:

Tampilkan:

`REMAKE`

`Kentang`

Reason:

`Damaged / Spilled`

Action:

`Masukkan ke produksi`

Remake tidak membuat order baru.

---

## 27. Controller Dashboard

Controller melihat operational overview.

Informasi utama:

- Active orders
- Kitchen load
- Orders waiting
- Orders ready
- Pickup backlog
- Payment issue
- Stock issue
- Remake
- Late orders

Dashboard harus fokus pada exception.

---

## 28. Action Center

Action Center menampilkan hal yang membutuhkan perhatian.

Contoh:

`⚠ Payment issue`

`⚠ Stock issue`

`⚠ Order terlambat`

`⚠ Remake`

`⚠ Pickup backlog`

Normal order tidak perlu memenuhi dashboard dengan alert.

---

## 29. Kitchen Load

Kitchen load menggunakan semantic level:

- NORMAL
- BUSY
- HIGH LOAD
- CRITICAL

Customer dapat melihat informasi sederhana:

`Dapur normal`

atau:

`Dapur sedang ramai`

atau:

`Waktu tunggu lebih lama dari biasanya`

Staff dapat melihat detail yang lebih lengkap.

---

## 30. Critical Load

Ketika kitchen mencapai CRITICAL:

New order dapat ditutup sementara.

Menu tetap dapat diakses.

Customer melihat:

`Pesanan sementara ditutup`

Existing confirmed orders tetap diproses.

Critical state tidak membatalkan order yang sudah dibayar.

---

## 31. Cashier UI

Cashier fokus pada:

- Cash payment
- Payment confirmation
- Cash received
- Change
- Payment status

Contoh:

`A127`

`Total: Rp37.000`

`Cash received: Rp50.000`

`Change: Rp13.000`

Primary action:

`Konfirmasi Pembayaran`

---

## 32. Pickup UI

Pickup menggunakan flow:

`VERIFY → GRAB → HANDOVER`

Staff memindai QR/token customer.

System menampilkan:

- Order number
- Customer name
- Items
- Payment status
- Pickup status

Setelah barang diberikan:

`Selesaikan Pickup`

---

## 33. Pickup Verification

Pickup verification harus jelas.

Contoh:

`A127`

`Leonardo`

`3 Items`

`PAID`

`READY`

Jika valid:

`Pesanan terverifikasi`

Jika sudah diambil:

`Pesanan sudah selesai diambil`

Jika token invalid:

`Token pickup tidak valid`

---

## 34. Admin UI

Admin dapat mengakses:

- Overview
- Sales
- Products
- Inventory
- Operations
- Finance
- Insights
- User management

Admin UI tidak boleh mencampur semua informasi dalam satu dashboard tanpa hierarchy.

---

## 35. Analytics UI

Analytics harus berfokus pada decision making.

KPI utama:

- Revenue
- Orders
- Units sold
- Gross profit
- Average order value
- Top products
- Peak hours
- Remake rate
- Cancellation rate

Contoh:

`Revenue`

`Rp4.250.000`

`Orders`

`127`

`Gross Profit`

`Rp1.850.000`

---

## 36. Charts

Chart digunakan jika membantu memahami data.

Recommended:

- Line chart untuk trend revenue
- Bar chart untuk product performance
- Bar/area chart untuk peak hours
- Donut chart hanya untuk simple composition

Jangan menggunakan chart hanya untuk dekorasi.

---

## 37. Tables

Table digunakan untuk data yang membutuhkan scanning atau comparison.

Contoh:

Product performance:

| Product | Units | Revenue | Gross Profit |
|---|---:|---:|---:|
| Nasi Goreng | 120 | Rp3.000.000 | Rp1.200.000 |
| Es Teh | 150 | Rp1.125.000 | Rp750.000 |

Mobile dapat mengubah table menjadi card/list jika table terlalu lebar.

---

## 38. Navigation

### Customer

Customer tidak membutuhkan complex navigation.

Flow utama:

`Menu → Cart → Checkout → Payment → Tracking`

### Staff

Staff navigation:

- Dashboard
- Kitchen
- Orders
- Pickup
- Notifications

### Admin

Admin navigation:

- Dashboard
- Orders
- Products
- Inventory
- Sales
- Analytics
- Users
- Settings

---

## 39. Responsive Design

Customer interface harus mobile-first.

Target utama:

- Smartphone
- Tablet

Staff interface:

- Tablet
- Desktop

Admin:

- Desktop
- Tablet

Semua halaman harus tetap usable pada screen kecil.

---

## 40. Mobile Rules

Pada mobile:

- Primary CTA mudah dijangkau.
- Cart harus mudah dibuka.
- Text tidak terlalu kecil.
- Tap target cukup besar.
- Horizontal scrolling dihindari jika tidak diperlukan.
- Form tidak terlalu panjang.
- Informasi penting berada di atas.

---

## 41. Desktop Rules

Desktop dapat menggunakan:

- Sidebar
- Multi-column layout
- Larger tables
- Dashboard grids

Gunakan ruang tambahan untuk hierarchy, bukan sekadar memperbesar semua elemen.

---

## 42. Loading State

Setiap data asynchronous harus memiliki loading state.

Contoh:

`Memuat menu...`

`Memuat order...`

`Memproses pembayaran...`

Gunakan skeleton atau spinner sesuai konteks.

Jangan menampilkan halaman kosong ketika data sedang dimuat.

---

## 43. Empty State

Empty state harus menjelaskan kondisi dan optional next action.

Contoh cart:

`Keranjang masih kosong.`

`Pilih menu untuk mulai memesan.`

Primary action:

`Lihat Menu`

---

## 44. Error State

Error harus menjelaskan:

- Apa yang terjadi.
- Apakah data aman.
- Apa yang dapat dilakukan user.

Contoh:

`Pembayaran belum dapat diverifikasi.`

`Pesanan Anda tetap tersimpan. Silakan tunggu beberapa saat atau coba cek kembali status pembayaran.`

Jangan hanya menampilkan:

`Error 500`.

---

## 45. Offline / Connection Issue

Jika koneksi terputus:

Customer melihat:

`Koneksi terputus`

Staff melihat:

`Connection lost`

Jika action penting belum berhasil dipersist:

Jangan tampilkan:

`Order berhasil`

sebelum backend mengonfirmasi persistence.

---

## 46. Notification

Customer notification dapat digunakan untuk:

- Payment success
- Order confirmed
- Preparing
- Ready
- Pickup reminder

Namun notification bukan satu-satunya source of truth.

Customer tetap dapat melihat status melalui tracking page.

---

## 47. Sound Notification

Staff interface dapat menggunakan sound notification untuk:

- New order
- Payment confirmation
- Remake
- Critical issue
- Pickup request

Sound harus dapat dimute.

---

## 48. Modal

Modal digunakan untuk:

- Confirmation
- Important detail
- Destructive action
- Payment confirmation

Jangan menggunakan modal untuk setiap interaction kecil.

Contoh destructive confirmation:

`Batalkan order A127?`

`Order yang sudah dibatalkan tidak dapat diproses kembali.`

Actions:

`Kembali`

`Batalkan Order`

---

## 49. Toast

Toast digunakan untuk feedback singkat.

Contoh:

`Produk ditambahkan ke keranjang.`

`Perubahan berhasil disimpan.`

`Pickup berhasil diselesaikan.`

Toast tidak boleh digunakan untuk informasi penting yang membutuhkan user action.

---

## 50. Accessibility

Interface harus memperhatikan:

- Keyboard navigation
- Focus state
- Color contrast
- Semantic HTML
- Accessible labels
- Screen reader compatibility
- Adequate tap target

Jangan mengandalkan warna saja untuk status.

---

## 51. UX Security

Security-sensitive action harus memiliki feedback yang jelas.

Contoh:

Pickup token invalid:

`Token pickup tidak valid.`

Unauthorized staff action:

`Anda tidak memiliki izin untuk melakukan tindakan ini.`

Session expired:

`Sesi Anda telah berakhir. Silakan login kembali.`

Jangan menampilkan internal security details kepada user.

---

## 52. Animation

Animation digunakan secara minimal.

Tujuan animation:

- Feedback
- Transition
- Loading
- State change

Hindari:

- Animasi terus-menerus
- Parallax berlebihan
- Excessive hover effect
- Animation yang memperlambat task

Customer ordering harus terasa cepat.

Staff interface harus terasa responsif dan utilitarian.

---

## 53. Component Architecture

Frontend component dibagi menjadi:

### UI Components

- Button
- Input
- Badge
- Card
- Modal
- Toast
- Dropdown
- Tabs
- Table
- Skeleton

### Layout Components

- Header
- Sidebar
- Bottom navigation
- Page container
- Section
- Dashboard layout

### Feature Components

- ProductCard
- CartItem
- OrderCard
- PaymentPanel
- KitchenTicket
- PickupScanner
- ActionCenter
- AnalyticsCard

Feature component tidak boleh mencampurkan terlalu banyak business logic.

---

## 54. Design Token Principle

Design system harus menggunakan centralized tokens.

Contoh:

- Colors
- Typography
- Spacing
- Radius
- Shadows
- Breakpoints
- Z-index

Tujuannya agar perubahan visual dapat dilakukan secara konsisten.

---

## 55. Customer UX Flow

Primary customer flow:

`QR Scan`

↓

`Menu`

↓

`Product Detail`

↓

`Cart`

↓

`Checkout`

↓

`Choose Payment`

↓

`Payment`

↓

`Order Confirmation`

↓

`Order Tracking`

↓

`Ready`

↓

`Pickup`

↓

`Completed`

---

## 56. Staff UX Flow

### Controller

`Login → Dashboard → Monitor → Handle Exception`

### Kitchen

`Login → Kitchen Queue → Start → Prepare → Ready`

### Cashier

`Login → Payment Queue → Receive Cash → Confirm`

### Pickup

`Login → Pickup Queue → Scan → Verify → Handover`

---

## 57. Admin UX Flow

`Login → Dashboard → Manage → Analyze → Configure`

Admin memiliki akses lebih luas tetapi interface tetap harus memprioritaskan task utama.

---

## 58. Information Hierarchy

Setiap halaman harus memiliki hierarchy:

1. Page purpose
2. Primary information
3. Primary action
4. Secondary information
5. Optional detail

Contoh kitchen:

1. Order number
2. Items
3. Current status
4. Timer
5. Action
6. Metadata

---

## 59. Error Prevention

UI harus membantu mencegah kesalahan sebelum terjadi.

Contoh:

- Disable checkout jika cart kosong.
- Disable payment confirmation jika cash kurang.
- Disable unavailable product.
- Confirmation untuk cancel/refund.
- Show change calculation sebelum confirm cash payment.
- Show stock availability sebelum checkout.

Backend tetap melakukan validation.

---

## 60. Design System Rule

Semua implementasi UI harus mengikuti dokumen ini.

Jika implementasi membutuhkan perubahan design system:

1. Identifikasi alasan.
2. Evaluasi impact.
3. Update design system.
4. Baru implementasikan perubahan.

Jangan membuat visual pattern baru hanya karena satu halaman membutuhkan komponen tertentu.

---

## 61. Final UI/UX Principle

Monster Café harus terasa:

> Cepat untuk customer, jelas untuk staff, dan informatif untuk owner.

Customer harus dapat memesan tanpa kebingungan.

Kitchen harus dapat bekerja tanpa terganggu informasi yang tidak relevan.

Controller harus dapat melihat exception dengan cepat.

Cashier harus dapat memproses payment tanpa kesalahan.

Pickup staff harus dapat memverifikasi order dengan cepat.

Admin harus dapat memahami kondisi bisnis dari data.

Design system ini menjadi dasar implementasi UI/UX Monster Café sebelum pembuatan wireframe dan frontend.