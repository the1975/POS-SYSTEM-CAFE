# Monster Café — Wireframes

## 1. Overview

Dokumen ini mendefinisikan struktur layout dan wireframe awal untuk interface Monster Café.

Wireframe digunakan untuk menentukan:

- Hierarchy informasi
- Posisi komponen
- Primary action
- Navigation
- Responsive behavior
- Customer flow
- Staff workflow
- Admin workflow

Wireframe bukan final visual design.

Implementasi visual mengikuti `design-system.md`, sedangkan behavior mengikuti `user-flow.md`, business rules, architecture, dan database design.

---

# 2. Customer Interface

## 2.1 Customer Menu

### Mobile

    ┌──────────────────────────────┐
    │ Monster Café          🛒 2   │
    ├──────────────────────────────┤
    │                              │
    │        MONSTER CAFÉ          │
    │      Good Food, Good Mood    │
    │                              │
    ├──────────────────────────────┤
    │ Search menu...               │
    ├──────────────────────────────┤
    │ [All] [Food] [Drink] [Snack] │
    ├──────────────────────────────┤
    │                              │
    │ ┌──────────────────────────┐ │
    │ │       Product Image      │ │
    │ ├──────────────────────────┤ │
    │ │ Nasi Goreng              │ │
    │ │ Nasi goreng spesial      │ │
    │ │ Rp25.000          [+]    │ │
    │ └──────────────────────────┘ │
    │                              │
    │ ┌──────────────────────────┐ │
    │ │       Product Image      │ │
    │ ├──────────────────────────┤ │
    │ │ Es Teh                   │ │
    │ │ Teh manis dingin         │ │
    │ │ Rp7.000           [+]    │ │
    │ └──────────────────────────┘ │
    │                              │
    └──────────────────────────────┘

### Desktop

    ┌───────────────────────────────────────────────────────────────┐
    │ Monster Café                           Search       🛒 Cart 2 │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │              MONSTER CAFÉ                                    │
    │           Good Food, Good Mood                               │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ [All] [Food] [Drink] [Snack]                                 │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
    │ │ Product      │  │ Product      │  │ Product      │         │
    │ │ Image        │  │ Image        │  │ Image        │         │
    │ │              │  │              │  │              │         │
    │ │ Nasi Goreng  │  │ Es Teh       │  │ Kentang      │         │
    │ │ Rp25.000     │  │ Rp7.000      │  │ Rp15.000     │         │
    │ │ [+]          │  │ [+]          │  │ [+]          │         │
    │ └──────────────┘  └──────────────┘  └──────────────┘         │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

---

# 3. Product Detail

    ┌──────────────────────────────┐
    │ ← Back                       │
    ├──────────────────────────────┤
    │                              │
    │       Product Image          │
    │                              │
    ├──────────────────────────────┤
    │ Nasi Goreng                  │
    │ Rp25.000                     │
    │                              │
    │ Nasi goreng spesial dengan   │
    │ telur dan topping pilihan.   │
    │                              │
    ├──────────────────────────────┤
    │ Quantity                     │
    │          [ − ]  1  [ + ]    │
    │                              │
    │ Customization                │
    │ [ Optional selection ]       │
    │                              │
    ├──────────────────────────────┤
    │ Rp25.000                     │
    │ [ Tambah ke Keranjang ]      │
    └──────────────────────────────┘

Primary action harus mudah ditemukan.

---

# 4. Cart

    ┌──────────────────────────────┐
    │ ← Menu                       │
    │ Keranjang                    │
    ├──────────────────────────────┤
    │                              │
    │ Nasi Goreng             ×2   │
    │ Rp25.000 × 2                 │
    │ Subtotal              Rp50K  │
    │                              │
    │ Es Teh                  ×1   │
    │ Rp7.000                      │
    │ Subtotal               Rp7K  │
    │                              │
    ├──────────────────────────────┤
    │ Subtotal              Rp57K  │
    │ Discount               Rp0   │
    │ Tax                   Rp5.7K │
    │                              │
    │ TOTAL                 Rp62.7K│
    ├──────────────────────────────┤
    │ [ Checkout ]                 │
    └──────────────────────────────┘

Pada mobile, tombol checkout dapat dibuat sticky di bagian bawah.

---

# 5. Checkout

    ┌──────────────────────────────┐
    │ Checkout                     │
    ├──────────────────────────────┤
    │ Customer                     │
    │ [ Leonardo               ]   │
    │                              │
    ├──────────────────────────────┤
    │ Your Order                   │
    │                              │
    │ Nasi Goreng ×2       Rp50K   │
    │ Es Teh ×1             Rp7K   │
    │                              │
    ├──────────────────────────────┤
    │ Subtotal             Rp57K   │
    │ Discount              Rp0    │
    │ Tax                  Rp5.7K  │
    │                              │
    │ TOTAL                Rp62.7K │
    ├──────────────────────────────┤
    │ Payment Method               │
    │                              │
    │ ( ) QRIS                     │
    │ ( ) Cash                     │
    │                              │
    ├──────────────────────────────┤
    │ [ Lanjutkan Pembayaran ]     │
    └──────────────────────────────┘

---

# 6. QRIS Payment

    ┌──────────────────────────────┐
    │ Pembayaran QRIS              │
    ├──────────────────────────────┤
    │                              │
    │ Order A127                   │
    │                              │
    │ TOTAL                        │
    │ Rp62.700                     │
    │                              │
    │       ┌──────────────┐       │
    │       │              │       │
    │       │   QR CODE    │       │
    │       │              │       │
    │       └──────────────┘       │
    │                              │
    │ Menunggu pembayaran...       │
    │                              │
    │ Payment status diproses      │
    │ oleh backend/payment gateway.│
    │                              │
    └──────────────────────────────┘

### QRIS Success

    ┌──────────────────────────────┐
    │ ✓ Pembayaran Berhasil        │
    ├──────────────────────────────┤
    │                              │
    │ Order                        │
    │ A127                         │
    │                              │
    │ Rp62.700                     │
    │                              │
    │ Pesanan sedang diproses.     │
    │                              │
    │ [ Lihat Status Pesanan ]     │
    └──────────────────────────────┘

---

# 7. Cash Payment

    ┌──────────────────────────────┐
    │ Pembayaran Cash              │
    ├──────────────────────────────┤
    │                              │
    │ Order A127                   │
    │                              │
    │ TOTAL                        │
    │ Rp62.700                     │
    │                              │
    │ Bayar di Cash Counter        │
    │                              │
    │ Status: Menunggu pembayaran  │
    │                              │
    │ Silakan tunjukkan Order      │
    │ Number kepada cashier.       │
    │                              │
    │ [ Lihat Status Pesanan ]     │
    └──────────────────────────────┘

Cash order tidak masuk kitchen sebelum pembayaran dikonfirmasi.

---

# 8. Order Confirmation

    ┌──────────────────────────────┐
    │ ✓ Pesanan Berhasil           │
    ├──────────────────────────────┤
    │                              │
    │ Order                        │
    │ A127                         │
    │                              │
    │ Customer                     │
    │ Leonardo                     │
    │                              │
    │ Payment                      │
    │ PAID                         │
    │                              │
    │ Status                       │
    │ CONFIRMED                    │
    │                              │
    │ Total                        │
    │ Rp62.700                     │
    │                              │
    │ [ Lihat Status Pesanan ]     │
    └──────────────────────────────┘

---

# 9. Order Tracking

    ┌──────────────────────────────┐
    │ Monster Café                 │
    │ Order A127                   │
    ├──────────────────────────────┤
    │                              │
    │        SEDANG DIPROSES       │
    │                              │
    │ ✓ Pembayaran                 │
    │ ✓ Dikonfirmasi               │
    │ ● Sedang disiapkan           │
    │ ○ Siap diambil               │
    │                              │
    ├──────────────────────────────┤
    │ Kitchen Load                 │
    │ Sedang ramai                 │
    │                              │
    │ 12 pesanan sedang dikerjakan │
    │ Estimasi 15–20 menit         │
    ├──────────────────────────────┤
    │ Your Order                   │
    │                              │
    │ Nasi Goreng ×2               │
    │ Es Teh ×1                    │
    │                              │
    │ Total Rp62.700               │
    ├──────────────────────────────┤
    │ Pickup                       │
    │ Tunggu sampai order READY.   │
    └──────────────────────────────┘

---

# 10. Order Ready

    ┌──────────────────────────────┐
    │ ✓ PESANAN SIAP               │
    ├──────────────────────────────┤
    │                              │
    │ Order                        │
    │ A127                         │
    │                              │
    │ Leonardo                     │
    │                              │
    │ Pesanan Anda sudah siap      │
    │ diambil.                     │
    │                              │
    │ ┌──────────────────────────┐ │
    │ │        PICKUP QR         │ │
    │ │                          │ │
    │ │       PICKUP TOKEN       │ │
    │ │                          │ │
    │ └──────────────────────────┘ │
    │                              │
    │ Tunjukkan QR kepada staff.   │
    └──────────────────────────────┘

---

# 11. Customer Pickup Complete

    ┌──────────────────────────────┐
    │ ✓ Pesanan Selesai            │
    ├──────────────────────────────┤
    │                              │
    │ Order A127                   │
    │                              │
    │ Pesanan telah diserahkan.    │
    │                              │
    │ Terima kasih telah memesan   │
    │ di Monster Café.             │
    │                              │
    │ [ Kembali ke Menu ]          │
    └──────────────────────────────┘

---

# 12. Staff Desktop Layout

    ┌───────────────────────────────────────────────────────────────┐
    │ Monster Café Staff                         User / Notification│
    ├───────────────┬───────────────────────────────────────────────┤
    │               │                                               │
    │ Dashboard     │ Page Title                                    │
    │               │                                               │
    │ Kitchen       │ Main Content                                  │
    │ Orders        │                                               │
    │ Pickup        │                                               │
    │               │                                               │
    │ Analytics     │                                               │
    │               │                                               │
    │ Settings      │                                               │
    │               │                                               │
    └───────────────┴───────────────────────────────────────────────┘

Sidebar digunakan pada desktop.

Pada mobile/tablet, sidebar dapat berubah menjadi drawer atau compact navigation.

---

# 13. Controller Dashboard

    ┌───────────────────────────────────────────────────────────────┐
    │ Dashboard                                                     │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
    │ │ Active     │ │ Preparing  │ │ Ready      │ │ Exceptions │ │
    │ │ 24         │ │ 12         │ │ 5          │ │ 3          │ │
    │ └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Action Center                                                 │
    │                                                               │
    │ ⚠ Payment Issue       A122                      [ Resolve ]  │
    │ ⚠ Stock Issue         A124                      [ Resolve ]  │
    │ ⚠ Late Order          A118                      [ Resolve ]  │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Kitchen Load                                                  │
    │                                                               │
    │ NORMAL / BUSY / HIGH LOAD / CRITICAL                          │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

Controller berfokus pada exception, bukan menjadi middleman setiap order.

---

# 14. Kitchen Interface

    ┌───────────────────────────────────────────────────────────────┐
    │ Kitchen                              Load: HIGH LOAD         │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ NOW                                                           │
    │                                                               │
    │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
    │ │ A127         │ │ A128         │ │ A129         │           │
    │ │              │ │              │ │              │           │
    │ │ Nasi ×1      │ │ Nasi ×2      │ │ Mie ×1       │           │
    │ │ Es Teh ×2    │ │ Kopi ×1      │ │ Es Teh ×1    │           │
    │ │              │ │              │ │              │           │
    │ │ 08:42        │ │ 08:39        │ │ 08:37        │           │
    │ │              │ │              │ │              │           │
    │ │ [ Mulai ]    │ │ [ Mulai ]    │ │ [ Mulai ]    │           │
    │ └──────────────┘ └──────────────┘ └──────────────┘           │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ NEXT                                                          │
    │                                                               │
    │ A130              A131              A132                      │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

Kitchen card memprioritaskan:

1. Order number
2. Item
3. Quantity
4. Status
5. Timer
6. Action

---

# 15. Kitchen Order Detail

    ┌───────────────────────┐
    │ A127                  │
    ├───────────────────────┤
    │ Nasi Goreng ×1        │
    │ ✓ READY               │
    │                       │
    │ Es Teh ×2             │
    │ ● PREPARING           │
    │                       │
    │ Kentang ×1            │
    │ ○ PENDING             │
    ├───────────────────────┤
    │ [ Tandai Item Ready ] │
    │ [ Remake ]            │
    └───────────────────────┘

---

# 16. Kitchen Remake

    ┌──────────────────────────────┐
    │ Remake Item                  │
    ├──────────────────────────────┤
    │ Order: A127                  │
    │ Item: Kentang                │
    │                              │
    │ Reason                       │
    │ [ Wrong menu             ▼ ] │
    │                              │
    │ Notes                        │
    │ [ _______________________ ]  │
    │                              │
    │ [ Cancel ] [ Confirm Remake ]│
    └──────────────────────────────┘

Remake tetap menggunakan order dan order item yang sama.

---

# 17. Cashier Dashboard

    ┌───────────────────────────────────────────────────────────────┐
    │ Cashier                                                       │
    ├───────────────────────────────────────────────────────────────┤
    │ Search Order                                                  │
    │ [ A127 / Customer Name                     ] [ Search ]      │
    ├───────────────────────────────────────────────────────────────┤
    │ Waiting Cash                                                  │
    │                                                               │
    │ A127       Leonardo       Rp62.700        [ Open ]           │
    │ A128       Andi           Rp45.000        [ Open ]           │
    │ A129       Rina           Rp30.000        [ Open ]           │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

Customer name bukan unique identifier.

Order number adalah identifier utama untuk operasional.

---

# 18. Cash Payment

    ┌──────────────────────────────┐
    │ Cash Payment — A127          │
    ├──────────────────────────────┤
    │ Customer                     │
    │ Leonardo                     │
    │                              │
    │ Total                        │
    │ Rp62.700                     │
    │                              │
    │ Cash Received                │
    │ [ Rp100.000               ]  │
    │                              │
    │ Change                       │
    │ Rp37.300                     │
    │                              │
    │ [ Confirm Payment ]          │
    └──────────────────────────────┘

Jika cash kurang:

    Cash Received: Rp50.000
    Total: Rp62.700

    ⚠ Uang belum mencukupi.

Confirmation harus disabled sampai cash mencukupi.

---

# 19. Pickup Dashboard

    ┌───────────────────────────────────────────────────────────────┐
    │ Pickup                                                        │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ [ Scan Pickup QR ]                                            │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Ready for Pickup                                              │
    │                                                               │
    │ A127       Leonardo        3 items             [ Verify ]     │
    │ A128       Andi            2 items             [ Verify ]     │
    │ A129       Rina            4 items             [ Verify ]     │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

---

# 20. Pickup Verification

    ┌──────────────────────────────┐
    │ Pickup Verification          │
    ├──────────────────────────────┤
    │                              │
    │ ✓ VALID ORDER                │
    │                              │
    │ A127                         │
    │ Leonardo                     │
    │                              │
    │ 3 Items                      │
    │                              │
    │ Nasi Goreng ×2               │
    │ Es Teh ×1                    │
    │                              │
    │ Payment: PAID                │
    │ Status: READY                │
    │                              │
    │ [ Selesaikan Pickup ]        │
    └──────────────────────────────┘

---

# 21. Invalid Pickup

    ┌──────────────────────────────┐
    │ ✕ Pickup Tidak Valid         │
    ├──────────────────────────────┤
    │                              │
    │ Token pickup tidak valid.    │
    │                              │
    │ Silakan periksa kembali      │
    │ QR atau token customer.      │
    │                              │
    │ [ Tutup ]                    │
    └──────────────────────────────┘

Tidak boleh mengubah status order.

---

# 22. Already Completed Pickup

    ┌──────────────────────────────┐
    │ Pickup Selesai                │
    ├──────────────────────────────┤
    │                              │
    │ Order A127 sudah diambil.   │
    │                              │
    │ Pickup kedua tidak dapat     │
    │ dilakukan.                   │
    │                              │
    │ [ Tutup ]                    │
    └──────────────────────────────┘

---

# 23. Admin Dashboard

    ┌───────────────────────────────────────────────────────────────┐
    │ Admin Dashboard                                               │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
    │ │ Revenue    │ │ Orders     │ │ Gross      │ │ Avg Order  │ │
    │ │ Rp4.2M     │ │ 127        │ │ Profit     │ │ Rp33K      │ │
    │ │            │ │            │ │ Rp1.8M     │ │            │ │
    │ └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Revenue Trend                                                 │
    │                                                               │
    │        ───╮                                                  │
    │     ───  ╰───╮                                              │
    │  ───         ╰────                                          │
    │                                                               │
    ├──────────────────────────────┬────────────────────────────────┤
    │ Top Products                 │ Peak Hours                     │
    │                              │                                │
    │ Nasi Goreng    120           │ 12:00 █████████               │
    │ Es Teh         150           │ 13:00 █████████████           │
    │ Kentang         80           │ 18:00 ████████                │
    └──────────────────────────────┴────────────────────────────────┘

---

# 24. Product Management

    ┌───────────────────────────────────────────────────────────────┐
    │ Products                              [ + Add Product ]      │
    ├───────────────────────────────────────────────────────────────┤
    │ Search products...                                            │
    ├───────────────────────────────────────────────────────────────┤
    │ Product       Category      Price       Status      Action    │
    │                                                               │
    │ Nasi Goreng   Food          Rp25.000    Available   [ Edit ]  │
    │ Es Teh        Drink          Rp7.000    Available   [ Edit ]  │
    │ Kentang       Snack         Rp15.000    Unavailable [ Edit ] │
    └───────────────────────────────────────────────────────────────┘

---

# 25. Product Form

    ┌──────────────────────────────┐
    │ Add Product                  │
    ├──────────────────────────────┤
    │ Name                         │
    │ [ Nasi Goreng             ]  │
    │                              │
    │ Category                     │
    │ [ Food                    ▼ ]│
    │                              │
    │ Description                  │
    │ [ _______________________ ]  │
    │                              │
    │ Price                        │
    │ [ Rp25.000                ]  │
    │                              │
    │ Cost Price                   │
    │ [ Rp15.000                ]  │
    │                              │
    │ Availability                 │
    │ [ ✓ Available ]              │
    │                              │
    │ [ Cancel ] [ Save Product ]  │
    └──────────────────────────────┘

---

# 26. Inventory

    ┌───────────────────────────────────────────────────────────────┐
    │ Inventory                                                     │
    ├───────────────────────────────────────────────────────────────┤
    │ Product       Available    Reserved    Reorder    Status     │
    │                                                               │
    │ Nasi Goreng   25           5           10         OK         │
    │ Es Teh        8            4           10         LOW        │
    │ Kentang       0            3           10         OUT        │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

Inventory MVP menggunakan product-level stock.

---

# 27. Stock Adjustment

    ┌──────────────────────────────┐
    │ Stock Adjustment             │
    ├──────────────────────────────┤
    │ Product                      │
    │ [ Nasi Goreng             ▼ ]│
    │                              │
    │ Adjustment                   │
    │ [ -5                     ]   │
    │                              │
    │ Reason                       │
    │ [ Damaged stock           ]  │
    │                              │
    │ [ Cancel ] [ Confirm ]       │
    └──────────────────────────────┘

Adjustment wajib memiliki reason.

---

# 28. Analytics Dashboard

    ┌───────────────────────────────────────────────────────────────┐
    │ Analytics                                                     │
    ├───────────────────────────────────────────────────────────────┤
    │ Period: [ This Month ▼ ]                                      │
    ├───────────────────────────────────────────────────────────────┤
    │                                                               │
    │ Revenue        Orders        Gross Profit       AOV           │
    │ Rp18.2M        542           Rp7.1M             Rp33.5K       │
    │                                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Revenue Trend                                                 │
    │                                                               │
    │        ───╮                                                  │
    │     ───  ╰────╮                                             │
    │  ───          ╰────                                          │
    │                                                               │
    ├──────────────────────────────┬────────────────────────────────┤
    │ Top Products                 │ Peak Hours                     │
    │                              │                                │
    │ Nasi Goreng                  │ 12:00 ██████████               │
    │ Es Teh                       │ 13:00 █████████████            │
    │ Kentang                      │ 18:00 ████████                 │
    └──────────────────────────────┴────────────────────────────────┘

Analytics berfokus pada:

- Revenue
- Orders
- Units sold
- Gross profit
- Average order value
- Top products
- Peak hours
- Remake rate
- Cancellation rate
- Payment failure

---

# 29. Orders Table

    ┌───────────────────────────────────────────────────────────────┐
    │ Orders                                                        │
    ├───────────────────────────────────────────────────────────────┤
    │ Search order...                                               │
    ├───────────────────────────────────────────────────────────────┤
    │ Order │ Customer │ Total │ Payment │ Status │ Action         │
    │                                                               │
    │ A127  │ Leonardo │ 62.7K │ PAID    │ READY  │ [ Detail ]     │
    │ A128  │ Andi     │ 45K   │ PAID    │ PREP.  │ [ Detail ]     │
    │ A129  │ Rina     │ 30K   │ CASH    │ PENDING│ [ Detail ]     │
    └───────────────────────────────────────────────────────────────┘

Pada mobile, table dapat berubah menjadi card/list.

---

# 30. Order Detail — Staff

    ┌────────────────────────────────────────┐
    │ Order A127                             │
    ├────────────────────────────────────────┤
    │ Customer                               │
    │ Leonardo                               │
    │                                        │
    │ Status                                 │
    │ READY                                  │
    │                                        │
    │ Payment                                │
    │ PAID — QRIS                            │
    ├────────────────────────────────────────┤
    │ Items                                  │
    │                                        │
    │ Nasi Goreng ×2          Rp50.000       │
    │ Es Teh ×1                Rp7.000       │
    │                                        │
    │ Total                    Rp62.700      │
    ├────────────────────────────────────────┤
    │ Timeline                               │
    │                                        │
    │ 09:10 Payment                         │
    │ 09:11 Confirmed                       │
    │ 09:15 Preparing                       │
    │ 09:25 Ready                           │
    └────────────────────────────────────────┘

---

# 31. Notifications

## Staff Notification Center

    ┌────────────────────────────────────────┐
    │ Notifications                          │
    ├────────────────────────────────────────┤
    │ 🔴 Payment issue — A122               │
    │    Payment needs verification.         │
    │                                        │
    │ 🟡 Stock issue — A124                │
    │    Product unavailable.                │
    │                                        │
    │ 🔵 New order — A127                  │
    │    New confirmed order.                │
    │                                        │
    │ 🟢 Ready — A118                      │
    │    Order ready for pickup.             │
    └────────────────────────────────────────┘

---

# 32. Empty State

## Empty Cart

    ┌──────────────────────────────┐
    │                              │
    │             🛒               │
    │                              │
    │ Keranjang masih kosong       │
    │                              │
    │ Pilih menu untuk mulai       │
    │ memesan.                     │
    │                              │
    │ [ Lihat Menu ]               │
    │                              │
    └──────────────────────────────┘

## Empty Orders

    ┌──────────────────────────────┐
    │ Belum ada pesanan            │
    │                              │
    │ Pesanan Anda akan muncul     │
    │ di sini setelah checkout.    │
    └──────────────────────────────┘

---

# 33. Loading State

## Menu Loading

    ┌──────────────────────────────┐
    │ Monster Café                 │
    ├──────────────────────────────┤
    │                              │
    │ ████████████████████████     │
    │ ██████████████               │
    │                              │
    │ ████████████████████████     │
    │ ██████████████               │
    │                              │
    │ ████████████████████████     │
    │ ██████████████               │
    └──────────────────────────────┘

Loading state harus memberikan feedback bahwa data sedang diproses.

---

# 34. Error State

## Generic Error

    ┌──────────────────────────────┐
    │ ✕ Terjadi Kesalahan          │
    ├──────────────────────────────┤
    │                              │
    │ Data belum dapat dimuat.     │
    │                              │
    │ Periksa koneksi dan coba     │
    │ kembali.                     │
    │                              │
    │ [ Coba Lagi ]                │
    └──────────────────────────────┘

Error message harus menjelaskan kondisi dan next action jika tersedia.

---

# 35. Connection Lost

    ┌──────────────────────────────┐
    │ ⚠ Koneksi Terputus           │
    ├──────────────────────────────┤
    │                              │
    │ Tidak dapat terhubung ke     │
    │ server.                      │
    │                              │
    │ Status transaksi belum dapat │
    │ dipastikan.                  │
    │                              │
    │ [ Coba Lagi ]                │
    └──────────────────────────────┘

Jangan menampilkan success sebelum backend mengonfirmasi persistence.

---

# 36. Critical Kitchen Load

## Customer

    ┌──────────────────────────────┐
    │ Dapur Sedang Sangat Ramai   │
    ├──────────────────────────────┤
    │                              │
    │ Waktu tunggu saat ini lebih  │
    │ lama dari biasanya.          │
    │                              │
    │ Pesanan baru sementara       │
    │ tidak tersedia.              │
    │                              │
    │ Pesanan yang sudah           │
    │ dikonfirmasi tetap diproses. │
    │                              │
    │ [ Kembali ke Menu ]          │
    └──────────────────────────────┘

---

# 37. Confirmation Modal

## Cancel Order

    ┌──────────────────────────────┐
    │ Batalkan Order?              │
    ├──────────────────────────────┤
    │                              │
    │ Apakah Anda yakin ingin      │
    │ membatalkan order A127?      │
    │                              │
    │ Tindakan ini dapat memicu    │
    │ proses refund sesuai         │
    │ payment rules.               │
    │                              │
    │ [ Kembali ] [ Batalkan ]     │
    └──────────────────────────────┘

Destructive action membutuhkan confirmation.

---

# 38. Toast

Contoh toast:

    ┌──────────────────────────────────┐
    │ ✓ Produk ditambahkan ke cart.    │
    └──────────────────────────────────┘

Toast digunakan untuk feedback singkat.

Toast tidak digunakan untuk informasi penting yang membutuhkan tindakan user.

---

# 39. Mobile Staff Navigation

    ┌──────────────────────────────┐
    │ Kitchen                      │
    ├──────────────────────────────┤
    │                              │
    │ Main Content                 │
    │                              │
    │                              │
    │                              │
    ├──────────────────────────────┤
    │ Dashboard │ Kitchen │ Pickup│
    └──────────────────────────────┘

Navigation mobile hanya menampilkan fungsi yang paling sering digunakan.

---

# 40. Responsive Behavior

## Customer

Prioritas:

`Mobile → Tablet → Desktop`

Customer ordering harus mobile-first.

## Staff

Prioritas:

`Tablet → Desktop → Mobile`

Staff membutuhkan ruang lebih besar untuk operational information.

## Admin

Prioritas:

`Desktop → Tablet → Mobile`

Analytics dan management table lebih nyaman pada layar besar.

---

# 41. Customer Navigation

Customer tidak membutuhkan navigation kompleks.

Primary flow:

    Menu
      ↓
    Product
      ↓
    Cart
      ↓
    Checkout
      ↓
    Payment
      ↓
    Tracking
      ↓
    Pickup

---

# 42. Staff Navigation

Staff navigation:

    Dashboard
       │
       ├── Kitchen
       │
       ├── Orders
       │
       ├── Pickup
       │
       └── Notifications

Role menentukan halaman/action yang dapat digunakan.

---

# 43. Admin Navigation

Admin navigation:

    Dashboard
       │
       ├── Orders
       ├── Products
       ├── Inventory
       ├── Sales
       ├── Analytics
       ├── Users
       └── Settings

---

# 44. Information Hierarchy

Setiap halaman mengikuti hierarchy:

1. Page purpose
2. Primary information
3. Primary action
4. Secondary information
5. Optional detail

Contoh Kitchen:

1. Order number
2. Items
3. Quantity
4. Current status
5. Timer
6. Action
7. Metadata

---

# 45. Primary Action Rules

Setiap halaman harus memiliki primary action yang jelas.

Contoh:

Customer:

`Checkout`

Payment:

`Bayar`

Kitchen:

`Mulai`

Cashier:

`Konfirmasi Pembayaran`

Pickup:

`Selesaikan Pickup`

Admin:

`Save`

---

# 46. Wireframe Rules

Wireframe harus mengikuti aturan berikut:

- Tidak ada unnecessary decoration.
- Primary action harus jelas.
- Informasi penting berada pada visual hierarchy tertinggi.
- Customer flow harus sesingkat mungkin.
- Staff flow harus action-oriented.
- Admin flow harus data-oriented.
- Mobile customer menggunakan layout satu kolom sebagai default.
- Staff dapat menggunakan multi-column pada tablet/desktop.
- Error, loading, dan empty state harus dirancang sejak awal.
- Tidak ada screen yang bergantung pada warna saja untuk menyampaikan status.
- Security-sensitive action membutuhkan confirmation atau authorization sesuai kebutuhan.

---

# 47. Final Customer Wireframe Flow

    QR Scan
       ↓
    Menu
       ↓
    Product Detail
       ↓
    Add to Cart
       ↓
    Cart
       ↓
    Checkout
       ↓
    Customer Name
       ↓
    Payment
       ↓
    Order Confirmation
       ↓
    Order Tracking
       ↓
    Preparing
       ↓
    Ready
       ↓
    Pickup QR
       ↓
    Verification
       ↓
    Handover
       ↓
    Completed

---

# 48. Final Staff Wireframe Flow

    Login
       ↓
    Dashboard
       ↓
    ┌───────────────┬───────────────┬───────────────┐
    │               │               │               │
    Kitchen       Cashier         Pickup        Controller
    │               │               │               │
    Prepare        Payment        Verify         Monitor
    │               │               │               │
    Ready          Confirm        Handover       Resolve
    │               │               │               │
    └───────────────┴───────────────┴───────────────┘
                       ↓
                    Completed

---

# 49. Final Admin Wireframe Flow

    Login
       ↓
    Dashboard
       ↓
    ┌───────────┬───────────┬────────────┬────────────┐
    │           │           │            │            │
    Orders    Products   Inventory    Analytics    Users
    │           │           │            │            │
    Monitor    Manage     Manage       Analyze      Manage
    │           │           │            │            │
    └───────────┴───────────┴────────────┴────────────┘

---

# 50. Final UX Structure

Monster Café memiliki tiga kelompok interface utama:

## Customer

Fokus:

- Browse
- Order
- Pay
- Track
- Pickup

## Staff

Fokus:

- Process
- Monitor
- Resolve
- Verify
- Handover

## Admin

Fokus:

- Manage
- Monitor
- Analyze
- Configure

---

# 51. Final Wireframe Principle

Wireframe Monster Café harus menghasilkan interface yang:

- Cepat dipahami.
- Cepat digunakan.
- Minim langkah yang tidak diperlukan.
- Memiliki hierarchy informasi yang jelas.
- Konsisten dengan design system.
- Konsisten dengan business rules.
- Tidak mengorbankan security dan data integrity.

Wireframe adalah blueprint sebelum frontend implementation.

Setelah wireframe disetujui, tahap berikutnya adalah membuat frontend berdasarkan:

`Requirements`
→ `Architecture`
→ `Database Design`
→ `Design System`
→ `User Flow`
→ `Wireframes`
→ `Implementation`