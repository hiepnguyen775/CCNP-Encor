# LAB 05B — Tuần 10: BGP Path Selection & Filtering

> 📘 **Lý thuyết:** [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) —
> đọc **Phần 1** và **Phần 2 mục §3.1 (13 bước), §3.2 (bảng điều khiển hướng traffic)** trước khi làm.
>
> ⏱️ **Thời gian:** ~8 giờ · 💾 **RAM:** 4 GB · 🧰 **Cần:** EVE-NG + 4–5× vIOS
>
> 👉 **Dùng lại topology của [LAB 05A](Module-05A-LAB.md)**, thêm một link để có **2 đường**.

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Trong 13 bước, **bước nào đang thực sự quyết định** path của tôi? | 1 |
| 2 | Muốn đổi hướng traffic **ĐI RA** — dùng thuộc tính nào? | 4 (LocPref) |
| 3 | Muốn tác động hướng traffic **ĐI VÀO** — dùng gì, và vì sao chỉ là *gợi ý*? | 3 (prepend) |
| 4 | Community `no-export` làm gì mà `no-advertise` không làm? | 7 |
| 5 | Bốn cách filtering — cái nào dùng khi nào? | 8 |
| 6 | `aggregate-address` gộp route — có mất thông tin gì không? | 9 |

> ⭐ **Cách làm lab này cho đúng:** mỗi bước chỉ đổi **MỘT** thuộc tính, rồi chạy
> `show ip bgp <prefix>` và **tự chỉ ra bước nào trong 13 bước vừa quyết định**.
> Đổi nhiều thứ cùng lúc thì bạn sẽ không biết cái nào có tác dụng.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Sau mỗi thay đổi phải `soft reset`** | `clear ip bgp * soft in` (hoặc `out`). ⭐ **Đừng dùng `clear ip bgp *`** — nó đánh sập peering |
| **BGP chậm** | Chờ **10–30 giây** sau soft reset rồi mới xem kết quả |
| **Chỉ đổi MỘT thứ mỗi lần** | Đây là nguyên tắc sống còn của lab này |
| **Ghi lại baseline** | Bước 1 lưu output `show ip bgp` gốc. Mỗi bước sau đều so với nó |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 4. LAB 05B

### 4.1 Mở rộng topology — thêm link R4↔R3 để có 2 đường

```
                    ┌──── R2 (AS 65002) ────┐
                    │  10.0.12.0/30          │ 10.0.23.0/30
                    │                        │
       R1 (AS 65001)┤                        ├R3 (AS 65003)
                    │                        │
                    │  10.0.14.0/30          │ 10.0.34.0/30
                    └──── R4 (AS 65004) ────┘
```

⭐ **Giờ R1 có 2 đường tới `10.3.3.0/24` (mạng của AS 65003):**

| Đường | Qua | AS-path | Độ dài |
|---|---|---|:---:|
| **A** | R2 (AS 65002) | `65002 65003` | **2** |
| **B** | R4 (AS 65004) | `65004 65003` | **2** |

⭐ **AS-path bằng nhau (2)** → tie ở bước 4 → rơi xuống các bước sau
→ **hoàn hảo để thực hành thao tác path selection.**

**Thêm link trong EVE-NG:**
1. **Stop** R3 và R4 (không nối dây khi node đang chạy)
2. Nối `R4 Gi0/0` ↔ `R3 Gi0/1`
3. Start lại

**Cấu hình:**
```
! ═══ R4 ═══
R4(config)# interface GigabitEthernet0/0
R4(config-if)#  description ---> eBGP to AS65003 (R3)
R4(config-if)#  ip address 10.0.34.1 255.255.255.252
R4(config-if)#  no shutdown
R4(config-if)# exit
R4(config)# router bgp 65004
R4(config-router)#  neighbor 10.0.34.2 remote-as 65003
R4(config-router)#  neighbor 10.0.34.2 description ---> AS65003 R3

! ═══ R3 ═══
R3(config)# interface GigabitEthernet0/1
R3(config-if)#  description ---> eBGP to AS65004 (R4)
R3(config-if)#  ip address 10.0.34.2 255.255.255.252
R3(config-if)#  no shutdown
R3(config-if)# exit
R3(config)# router bgp 65003
R3(config-router)#  neighbor 10.0.34.1 remote-as 65004
R3(config-router)#  neighbor 10.0.34.1 description ---> AS65004 R4
```

---

### Bước 1 — ⭐ Xác định baseline: bước nào đang quyết định?

```
R1# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
BGP routing table entry for 10.3.3.0/24, version 12
Paths: (2 available, best #1, table default)
  Advertised to update-groups:
     1
  Refresh Epoch 1
  65002 65003
    10.0.12.2 from 10.0.12.2 (2.2.2.2)
      Origin IGP, localpref 100, valid, external, best
      rx pathid: 0, tx pathid: 0x0
  Refresh Epoch 1
  65004 65003
    10.0.14.2 from 10.0.14.2 (4.4.4.4)
      Origin IGP, localpref 100, valid, external
      rx pathid: 0, tx pathid: 0
```

⭐ **Phân tích theo 13 bước — điền bảng:**

| Bước | Path A (qua R2) | Path B (qua R4) | Phân định? |
|:---:|---|---|:---:|
| 0. Next-hop reachable | `10.0.12.2` ✅ | `10.0.14.2` ✅ | Tie |
| **1. Weight** | 0 | 0 | Tie |
| **2. Local Pref** | 100 | 100 | Tie |
| **3. Locally originated** | Không | Không | Tie |
| **4. AS-path length** | **2** (`65002 65003`) | **2** (`65004 65003`) | ⭐ **Tie** |
| **5. Origin** | `i` | `i` | Tie |
| **6. MED** | (không đặt = 0) | (không đặt = 0) | Tie |
| **7. eBGP > iBGP** | eBGP | eBGP | Tie |
| **8. IGP metric** | — | — | Tie |
| **10. Oldest eBGP path** | ? | ? | ⭐ **Có thể phân định** |
| **11. Router ID neighbor** | **2.2.2.2** | **4.4.4.4** | ⭐ **2.2.2.2 THẤP hơn → thắng** |

⭐ **Kết luận:** path A (qua R2) thắng ở **bước 10 (oldest)** hoặc **bước 11 (Router ID 2.2.2.2 < 4.4.4.4)**.

**Xác nhận bằng traceroute:**
```
R1# traceroute 10.3.3.1 source 10.1.1.1
  1 10.0.12.2 ...        ← qua R2 (AS 65002)
  2 10.0.23.2 ...        ← tới R3
```

**Xem cả 2 path trong dạng bảng:**
```
R1# show ip bgp | include 10.3.3.0
 *>  10.3.3.0/24      10.0.12.2                              0 65002 65003 i
 *   10.3.3.0/24      10.0.14.2                              0 65004 65003 i
```
⭐ `*>` = valid + best (qua R2) · `*` = valid nhưng **không best** (qua R4).

✅ **Checkpoint bước 1:** thấy **2 path**, xác định được **bước nào** đang quyết định.

---

### Bước 2 — ⭐⭐ Bước 11: Router ID (chứng minh tie-break)

**Test:** đổi Router ID của R4 xuống thấp hơn R2 → path B phải thắng.

```
R4(config)# router bgp 65004
R4(config-router)# bgp router-id 1.1.1.4        ! thấp hơn 2.2.2.2
R4(config-router)# exit
R4# clear ip bgp *                               ! (lab thôi — production dùng soft)
```
```
R1# clear ip bgp *
R1# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
Paths: (2 available, best #2, table default)
  ...
  65004 65003
    10.0.14.2 from 10.0.14.2 (1.1.1.4)
      Origin IGP, localpref 100, valid, external, best      ← giờ path này best
```
⭐ **Path B thắng** vì Router ID `1.1.1.4` < `2.2.2.2`.

> ⚠️ **Lưu ý:** bước **10 (oldest eBGP path)** đứng **TRƯỚC** bước 11. Nên nếu 1 path lên trước
> thì nó có thể thắng ở bước 10. Đó là lý do phải `clear ip bgp *` **cả 2 phiên cùng lúc**
> để kết quả phụ thuộc Router ID.

**Trả về:**
```
R4(config-router)# bgp router-id 4.4.4.4
R4# clear ip bgp *
R1# clear ip bgp *
```

---

### Bước 3 — ⭐⭐ Bước 4: AS-path prepend (điều khiển INBOUND)

**Mục tiêu:** làm cho AS 65003 (R3) **không** chọn đường qua R4 để tới `10.1.1.0/24` của tôi.

**a) Xem baseline trên R3:**
```
R3# show ip bgp 10.1.1.0
```
**Output mẫu:**
```
Paths: (2 available, best #?, table default)
  65002 65001
    10.0.23.1 from 10.0.23.1 (2.2.2.2)
      Origin IGP, localpref 100, valid, external
  65004 65001
    10.0.34.1 from 10.0.34.1 (4.4.4.4)
      Origin IGP, localpref 100, valid, external, best
```
→ AS-path đều dài 2, R3 chọn theo tie-break.

**b) ⭐ R1 prepend khi quảng bá cho R4 (AS 65004):**
```
R1(config)# route-map RM-PREPEND-TO-AS65004 permit 10
R1(config-route-map)#  set as-path prepend 65001 65001 65001
R1(config-route-map)# exit
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.14.2 route-map RM-PREPEND-TO-AS65004 out
R1(config-router)# exit
R1# clear ip bgp 10.0.14.2 soft out             ! soft out (đổi outbound policy)
```

**c) Xem trên R4:**
```
R4# show ip bgp 10.1.1.0
```
**Output mẫu:**
```
  65001 65001 65001 65001
    10.0.14.1 from 10.0.14.1 (1.1.1.1)
      Origin IGP, localpref 100, valid, external, best
```
⭐ **AS-path dài 4** (thay vì 1).

**d) ⭐ Xem trên R3 — kết quả mong muốn:**
```
R3# show ip bgp 10.1.1.0
```
**Output mẫu:**
```
Paths: (2 available, best #1, table default)
  65002 65001
    10.0.23.1 from 10.0.23.1 (2.2.2.2)
      Origin IGP, localpref 100, valid, external, best      ← giờ chọn qua R2
  65004 65001 65001 65001 65001
    10.0.34.1 from 10.0.34.1 (4.4.4.4)
      Origin IGP, localpref 100, valid, external
```
⭐⭐ **AS-path qua R4 giờ dài 5** (`65004` + 4 lần `65001`) vs qua R2 dài 2
→ **bước 4 phân định** → R3 chọn qua R2.

```
R3# traceroute 10.1.1.1 source 10.3.3.1
  1 10.0.23.1 ...        ← qua R2, không qua R4 nữa
```

✅ **Traffic INBOUND vào AS 65001 đã đổi hướng** — bằng cách áp route-map chiều **`out`**.

**e) ⭐ Chứng minh "inbound chỉ là gợi ý":**

R3 có thể **ghi đè** bằng Weight (bước 1 > bước 4):
```
R3(config)# router bgp 65003
R3(config-router)# neighbor 10.0.34.1 weight 500      ! ưu tiên R4 bất chấp AS-path dài
R3# clear ip bgp 10.0.34.1 soft in
R3# show ip bgp 10.1.1.0
```
**Output mẫu:**
```
  65004 65001 65001 65001 65001
    10.0.34.1 from 10.0.34.1 (4.4.4.4)
      Origin IGP, localpref 100, weight 500, valid, external, best   ← THẮNG dù AS-path dài
```
⭐⭐ **Weight (bước 1) thắng AS-path (bước 4)** → prepend của R1 **vô hiệu**.

🧠 **Đây chính là bằng chứng: "Outbound tôi quyết, inbound tôi xin".**

**Dọn dẹp:**
```
R3(config-router)# no neighbor 10.0.34.1 weight
R3# clear ip bgp 10.0.34.1 soft in
R1(config)# router bgp 65001
R1(config-router)#  no neighbor 10.0.14.2 route-map RM-PREPEND-TO-AS65004 out
R1# clear ip bgp 10.0.14.2 soft out
```

---

### Bước 4 — ⭐⭐ Bước 2: Local Preference (điều khiển OUTBOUND)

**Mục tiêu:** R1 ưu tiên đi qua **R4** để tới `10.3.3.0/24` (thay vì R2 như baseline).

```
R1(config)# ip prefix-list PL-AS65003 seq 5 permit 10.3.3.0/24
R1(config)# ip prefix-list PL-AS65003 seq 10 permit 10.3.4.0/24
!
R1(config)# route-map RM-PREFER-R4 permit 10
R1(config-route-map)#  match ip address prefix-list PL-AS65003
R1(config-route-map)#  set local-preference 200
R1(config-route-map)# exit
R1(config)# route-map RM-PREFER-R4 permit 20         ! CATCH-ALL
R1(config-route-map)# exit
!
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.14.2 route-map RM-PREFER-R4 in     ! chiều IN
R1(config-router)# exit
R1# clear ip bgp 10.0.14.2 soft in                   ! soft in
```

**Kiểm tra:**
```
R1# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
Paths: (2 available, best #2, table default)
  65002 65003
    10.0.12.2 from 10.0.12.2 (2.2.2.2)
      Origin IGP, localpref 100, valid, external
  65004 65003
    10.0.14.2 from 10.0.14.2 (4.4.4.4)
      Origin IGP, localpref 200, valid, external, best      ← LocPref 200 THẮNG
```
```
R1# show ip bgp | include 10.3.3.0
 *   10.3.3.0/24      10.0.12.2                    100        0 65002 65003 i
 *>  10.3.3.0/24      10.0.14.2                    200        0 65004 65003 i
```
⭐ Cột `LocPrf` = **200** vs **100** → path qua R4 best.

```
R1# traceroute 10.3.3.1 source 10.1.1.1
  1 10.0.14.2 ...        ← qua R4
  2 10.0.34.2 ...        ← tới R3
```

⭐ **Chú ý:** Local Preference (bước 2) thắng **dù AS-path bằng nhau** —
nó đứng **trước** bước 4 nên phân định sớm hơn.

**⭐ Test: Weight thắng Local Preference**
```
R1(config)# route-map RM-WEIGHT-R2 permit 10
R1(config-route-map)#  match ip address prefix-list PL-AS65003
R1(config-route-map)#  set weight 1000
R1(config-route-map)# exit
R1(config)# route-map RM-WEIGHT-R2 permit 20
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.12.2 route-map RM-WEIGHT-R2 in
R1# clear ip bgp 10.0.12.2 soft in
```
```
R1# show ip bgp | include 10.3.3.0
 *>  10.3.3.0/24      10.0.12.2                    100     1000 65002 65003 i    ← Weight thắng
 *   10.3.3.0/24      10.0.14.2                    200        0 65004 65003 i
```
⭐⭐ **Weight 1000 (bước 1) thắng Local Preference 200 (bước 2)** — dù LocPref cao hơn!

**Dọn dẹp:**
```
R1(config-router)# no neighbor 10.0.12.2 route-map RM-WEIGHT-R2 in
R1(config-router)# no neighbor 10.0.14.2 route-map RM-PREFER-R4 in
R1# clear ip bgp * soft in
```

✅ **Checkpoint bước 3–4 — điền bảng (bảng vàng của module):**

| Kỹ thuật | Áp chiều | Điều khiển traffic | Bước | Ghi chú |
|---|:---:|---|:---:|---|
| Weight | | | | |
| Local Preference | | | | |
| AS-path prepend | | | | |
| MED | | | | |

<details><summary>Đáp án</summary>

| Kỹ thuật | Áp chiều | Điều khiển traffic | Bước | Ghi chú |
|---|:---:|---|:---:|---|
| ⭐ **Weight** | ⭐ **`in`** | ⭐ **OUTBOUND** | **1** | Chỉ 1 router. CAO thắng |
| ⭐ **Local Preference** | ⭐ **`in`** | ⭐ **OUTBOUND** | **2** | Cả AS. CAO thắng |
| ⭐ **AS-path prepend** | ⭐ **`out`** | ⭐ **INBOUND** | **4** | Gợi ý. THẤP (ngắn) thắng |
| ⭐ **MED** | ⭐ **`out`** | ⭐ **INBOUND** | **6** | Gợi ý yếu nhất. THẤP thắng |

🧠 *"Nhận route vào → quyết định đi ra. Gửi route ra → gợi ý người ta đi vào."*
</details>

---

### Bước 5 — ⭐ Bước 6: MED

**Mục tiêu:** dùng MED để gợi ý AS 65003 vào AS 65001 qua đường nào.

⚠️ **Nhắc lại:** MED mặc định **chỉ so giữa path từ CÙNG một AS kề**.
Ở đây R3 nhận 2 path từ **2 AS khác nhau** (65002 và 65004) → ⭐ **MED KHÔNG được so sánh**.

**a) Chứng minh MED không có tác dụng khi khác AS:**
```
R1(config)# route-map RM-MED-HIGH permit 10
R1(config-route-map)#  set metric 500
R1(config-route-map)# exit
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.14.2 route-map RM-MED-HIGH out
R1# clear ip bgp 10.0.14.2 soft out
```
```
R3# show ip bgp 10.1.1.0
```
→ Path qua R4 có `metric 500`, path qua R2 có metric 0 (hoặc trống).
Nhưng ⭐ **R3 vẫn có thể chọn path qua R4** — vì MED **không được so** giữa 2 AS khác nhau.

**b) ⭐ Bật `always-compare-med` trên R3:**
```
R3(config)# router bgp 65003
R3(config-router)# bgp always-compare-med
R3# clear ip bgp * soft in
R3# show ip bgp 10.1.1.0
```
**Output mẫu:**
```
  65002 65001
    10.0.23.1 from 10.0.23.1 (2.2.2.2)
      Origin IGP, localpref 100, valid, external, best      ← MED 0 < 500
  65004 65001
    10.0.34.1 from 10.0.34.1 (4.4.4.4)
      Origin IGP, metric 500, localpref 100, valid, external
```
⭐ **Giờ MED được so** → path qua R2 (MED 0) thắng path qua R4 (MED 500).

**c) ⭐ Bật `deterministic-med` (nên có ở production):**
```
R3(config-router)# bgp deterministic-med
```
→ Nhóm path theo AS **trước** khi so → kết quả **nhất quán** không phụ thuộc thứ tự học route.

**Dọn dẹp:**
```
R3(config-router)# no bgp always-compare-med
R1(config-router)# no neighbor 10.0.14.2 route-map RM-MED-HIGH out
R1# clear ip bgp 10.0.14.2 soft out
R3# clear ip bgp * soft in
```

✅ **Checkpoint bước 5:** hiểu được **MED chỉ so cùng AS kề** — và đó là lý do
MED **gần như vô dụng** trong kịch bản dual-ISP (2 ISP khác nhau).

---

### Bước 6 — ⭐ Bước 5: Origin

**Mục tiêu:** chứng minh `network` (origin `i`) thắng `redistribute` (origin `?`).

```
! R3 chuyển 10.3.4.0/24 từ 'network' sang 'redistribute connected'
R3(config)# router bgp 65003
R3(config-router)#  no network 10.3.4.0 mask 255.255.255.0
R3(config-router)#  redistribute connected
```
```
R1# show ip bgp | include 10.3.4.0
 *>  10.3.4.0/24      10.0.12.2                    0        0 65002 65003 ?
```
⭐ **Origin đổi từ `i` sang `?`** (incomplete).

**Tạo tình huống so sánh — R3 quảng bá cùng prefix bằng 2 nguồn khác origin:**
```
! Trên R3: giữ cả redistribute (?) và thêm lại network (i) cho 10.3.4.0/24
R3(config-router)# network 10.3.4.0 mask 255.255.255.0
```
```
R3# show ip bgp 10.3.4.0
```
→ Route local, không so được. Nhưng trên R1 bạn thấy origin cuối cùng là `i`
(vì `network` **ưu tiên hơn** `redistribute` cho cùng prefix).

**Dọn dẹp:**
```
R3(config-router)# no redistribute connected
```

⭐ **Bài học thực chiến:** ⭐ **luôn dùng `network` thay `redistribute`** khi quảng bá vào BGP —
origin `i` **tốt hơn** `?` trong path selection (bước 5), và `redistribute` dễ leak route ngoài ý muốn.

---

### Bước 7 — ⭐⭐ BGP Community

#### 7a) `no-export` — route không ra khỏi AS

```
! R3 gắn no-export cho 10.3.4.0/24 khi quảng bá cho R2 (AS 65002)
R3(config)# ip bgp-community new-format
R3(config)# ip prefix-list PL-INTERNAL permit 10.3.4.0/24
!
R3(config)# route-map RM-NO-EXPORT permit 10
R3(config-route-map)#  match ip address prefix-list PL-INTERNAL
R3(config-route-map)#  set community no-export
R3(config-route-map)# exit
R3(config)# route-map RM-NO-EXPORT permit 20             ! catch-all
R3(config-route-map)# exit
!
R3(config)# router bgp 65003
R3(config-router)#  neighbor 10.0.23.1 send-community    ! KHÔNG ĐƯỢC QUÊN
R3(config-router)#  neighbor 10.0.23.1 route-map RM-NO-EXPORT out
R3(config-router)# exit
R3# clear ip bgp 10.0.23.1 soft out
```

**Kiểm tra trên R2 — nhận được community:**
```
R2# show ip bgp 10.3.4.0
```
**Output mẫu:**
```
BGP routing table entry for 10.3.4.0/24, version 15
Paths: (1 available, best #1, table default)
  Not advertised to any peer                              ← KHÔNG quảng bá cho ai
  Refresh Epoch 1
  65003
    10.0.23.2 from 10.0.23.2 (3.3.3.3)
      Origin IGP, localpref 100, valid, external, best
      Community: no-export                                ← COMMUNITY!
```
⭐⭐ **`Not advertised to any peer`** + **`Community: no-export`**

**Kiểm tra trên R1 — KHÔNG nhận được prefix:**
```
R1# show ip bgp | include 10.3.4.0
! → TRỐNG
```
⭐ **R2 không quảng bá `10.3.4.0/24` cho R1** vì community `no-export`.

**So sánh — prefix khác vẫn tới được R1:**
```
R1# show ip bgp | include 10.3.3.0
 *>  10.3.3.0/24      10.0.12.2                              0 65002 65003 i    ← ✅ vẫn có
```

**Lệnh lọc theo community:**
```
R2# show ip bgp community no-export
R2# show ip bgp community
```

#### 7b) ⚠️ Tái hiện lỗi: quên `send-community`

```
R3(config)# router bgp 65003
R3(config-router)# no neighbor 10.0.23.1 send-community
R3# clear ip bgp 10.0.23.1 soft out
```
```
R2# show ip bgp 10.3.4.0 | include Community
! → TRỐNG — không có community
R1# show ip bgp | include 10.3.4.0
 *>  10.3.4.0/24      10.0.12.2                              0 65002 65003 i    ← ⚠️ prefix LỌT RA!
```
⭐⭐ **Không có `send-community` → community không được gửi → policy vô hiệu → prefix lọt ra ngoài AS.**

> 🔴 **Ghi vào `SO-TAY-LOI.md`:** `set community` mà không có `neighbor x send-community`
> = dán nhãn mà không gửi = **không có tác dụng gì**, và **không có thông báo lỗi**.

**Sửa:**
```
R3(config-router)# neighbor 10.0.23.1 send-community
R3# clear ip bgp 10.0.23.1 soft out
```

#### 7c) `no-advertise` — chặn hoàn toàn

```
R3(config)# route-map RM-NO-EXPORT permit 10
R3(config-route-map)#  set community no-advertise
R3# clear ip bgp 10.0.23.1 soft out
```
```
R2# show ip bgp 10.3.4.0 | include Community|Not advertised
!       Not advertised to any peer
!       Community: no-advertise
```
→ Với `no-advertise`, R2 **không quảng bá cho bất kỳ ai** — kể cả iBGP peer (nếu có).

**Trả về `no-export`:**
```
R3(config)# route-map RM-NO-EXPORT permit 10
R3(config-route-map)#  set community no-export
R3# clear ip bgp 10.0.23.1 soft out
```

#### 7d) Community tự định nghĩa + match

```
! R3 gắn community 65003:100 cho 10.3.3.0/24
R3(config)# ip prefix-list PL-TAG permit 10.3.3.0/24
R3(config)# route-map RM-TAG-OUT permit 10
R3(config-route-map)#  match ip address prefix-list PL-TAG
R3(config-route-map)#  set community 65003:100
R3(config-route-map)# exit
R3(config)# route-map RM-TAG-OUT permit 20
R3(config)# router bgp 65003
R3(config-router)#  neighbor 10.0.23.1 send-community
R3(config-router)#  neighbor 10.0.23.1 route-map RM-TAG-OUT out
R3# clear ip bgp 10.0.23.1 soft out
```

```
! R2 đọc community và áp Local Preference
R2(config)# ip bgp-community new-format
R2(config)# ip community-list standard CL-FROM-AS65003 permit 65003:100
!
R2(config)# route-map RM-READ-COMM permit 10
R2(config-route-map)#  match community CL-FROM-AS65003
R2(config-route-map)#  set local-preference 300
R2(config-route-map)# exit
R2(config)# route-map RM-READ-COMM permit 20             ! catch-all
R2(config)# router bgp 65002
R2(config-router)#  neighbor 10.0.23.2 route-map RM-READ-COMM in
R2# clear ip bgp 10.0.23.2 soft in
```

**Kiểm tra:**
```
R2# show ip bgp 10.3.3.0
```
**Output mẫu:**
```
  65003
    10.0.23.2 from 10.0.23.2 (3.3.3.3)
      Origin IGP, localpref 300, valid, external, best     ← LocPref 300 do community
      Community: 65003:100
```
```
R2# show ip bgp community 65003:100
R2# show ip community-list
```
⭐ **Đây là cách 2 AS "hợp tác" bằng community** — AS 65003 gắn nhãn,
AS 65002 đọc nhãn và tự áp policy. Đây là cách ISP thật cho khách hàng
điều khiển traffic (VD: gắn `65001:80` → ISP đặt LocPref 80).

**Dọn dẹp:**
```
R2(config-router)# no neighbor 10.0.23.2 route-map RM-READ-COMM in
R3(config-router)# no neighbor 10.0.23.1 route-map RM-TAG-OUT out
R3(config-router)# no neighbor 10.0.23.1 route-map RM-NO-EXPORT out
R2# clear ip bgp * soft in
R3# clear ip bgp * soft out
```

✅ **Checkpoint bước 7:**

| Kiểm tra | Mong đợi |
|---|---|
| `set community no-export` + `send-community` → R2 thấy `Community: no-export` và `Not advertised to any peer` | ⭐ ✅ |
| R1 **không** nhận được prefix đó | ⭐ ✅ |
| ⭐ Bỏ `send-community` → community mất → prefix **lọt ra** R1 | ⭐ ✅ |
| `no-advertise` chặn mạnh hơn `no-export` | ✅ |
| Community tự định nghĩa + `match community` → áp LocPref 300 | ⭐ ✅ |

---

### Bước 8 — ⭐⭐ Filtering

#### 8a) Prefix-list

```
! R1 chỉ nhận 10.3.3.0/24 từ R2, chặn 10.3.4.0/24 và các prefix khác của AS65003
R1(config)# ip prefix-list PL-FROM-R2 seq 5  permit 10.3.3.0/24
R1(config)# ip prefix-list PL-FROM-R2 seq 10 permit 10.2.2.0/24
R1(config)# ip prefix-list PL-FROM-R2 seq 15 permit 2.2.2.2/32
R1(config)# ip prefix-list PL-FROM-R2 seq 20 deny 0.0.0.0/0 le 32     ! deny phần còn lại
!
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.12.2 prefix-list PL-FROM-R2 in
R1# clear ip bgp 10.0.12.2 soft in
```
```
R1# show ip bgp neighbors 10.0.12.2 routes
```
**Output mẫu:**
```
     Network          Next Hop            Metric LocPrf Weight Path
 *>  2.2.2.2/32       10.0.12.2                0             0 65002 i
 *>  10.2.2.0/24      10.0.12.2                0             0 65002 i
 *   10.3.3.0/24      10.0.12.2                              0 65002 65003 i

Total number of prefixes 3
```
⭐ Chỉ 3 prefix qua được (thay vì 6).

```
R1# show ip prefix-list detail PL-FROM-R2
```
**Output mẫu:**
```
ip prefix-list PL-FROM-R2:
   count: 4, range entries: 1, sequences: 5 - 20
   seq 5 permit 10.3.3.0/24 (hit count: 1, refcount: 1)
   seq 10 permit 10.2.2.0/24 (hit count: 1, refcount: 1)
   seq 15 permit 2.2.2.2/32 (hit count: 1, refcount: 1)
   seq 20 deny 0.0.0.0/0 le 32 (hit count: 3, refcount: 1)
```
⭐ **`hit count`** cho biết mỗi dòng khớp bao nhiêu lần — cách nhanh nhất verify filter.

#### 8b) 🔴 Tái hiện lỗi: `permit 0.0.0.0/0` không phải catch-all

```
R1(config)# no ip prefix-list PL-FROM-R2
R1(config)# ip prefix-list PL-FROM-R2 seq 5  deny 10.3.4.0/24
R1(config)# ip prefix-list PL-FROM-R2 seq 10 permit 0.0.0.0/0        ! ⚠️ THIẾU "le 32"
R1# clear ip bgp 10.0.12.2 soft in
```
```
R1# show ip bgp neighbors 10.0.12.2 routes
! Total number of prefixes 0            ← MẤT HẾT!
```
⭐⭐ **`permit 0.0.0.0/0` chỉ cho phép ĐÚNG default route** → mọi prefix khác bị
**implicit deny** → **mất hết route**.

**Sửa:**
```
R1(config)# ip prefix-list PL-FROM-R2 seq 10 permit 0.0.0.0/0 le 32   ! thêm "le 32"
R1# clear ip bgp 10.0.12.2 soft in
R1# show ip bgp neighbors 10.0.12.2 routes
! Total number of prefixes 5            ← ✅ chỉ thiếu 10.3.4.0/24 (bị deny đúng ý)
```

> 🔴 **Ghi vào `SO-TAY-LOI.md`:** catch-all của prefix-list là **`permit 0.0.0.0/0 le 32`**,
> **KHÔNG** phải `permit 0.0.0.0/0`.

**Dọn dẹp:**
```
R1(config-router)# no neighbor 10.0.12.2 prefix-list PL-FROM-R2 in
R1# clear ip bgp 10.0.12.2 soft in
```

#### 8c) ⭐ AS-path ACL (filter-list) + regex

**Test các regex trước:**
```
R1# show ip bgp regexp ^$
```
**Output mẫu:**
```
     Network          Next Hop            Metric LocPrf Weight Path
 *>  1.1.1.1/32       0.0.0.0                  0         32768 i
 *>  10.1.1.0/24      0.0.0.0                  0         32768 i
 *>  10.1.2.0/24      0.0.0.0                  0         32768 i
```
⭐ **`^$`** = AS-path rỗng = route sinh **trong AS của mình**.

```
R1# show ip bgp regexp ^65002$
```
→ Chỉ route **sinh tại AS 65002** (AS-path đúng 1 phần tử).

```
R1# show ip bgp regexp _65003_
```
→ Mọi route **đi qua** AS 65003.

```
R1# show ip bgp regexp ^65004_
```
→ Route **từ AS kề 65004**.

**Áp filter-list — chỉ nhận route sinh tại AS kề (không nhận transit):**
```
R1(config)# ip as-path access-list 10 permit ^65002$
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.12.2 filter-list 10 in
R1# clear ip bgp 10.0.12.2 soft in
```
```
R1# show ip bgp neighbors 10.0.12.2 routes
```
**Output mẫu:**
```
     Network          Next Hop            Metric LocPrf Weight Path
 *>  2.2.2.2/32       10.0.12.2                0             0 65002 i
 *>  10.2.2.0/24      10.0.12.2                0             0 65002 i

Total number of prefixes 2
```
⭐ Chỉ nhận route **của chính AS 65002** — route transit từ AS 65003 bị chặn.

**Test chặn AS cụ thể:**
```
R1(config)# no ip as-path access-list 10
R1(config)# ip as-path access-list 10 deny _65003_
R1(config)# ip as-path access-list 10 permit .*          ! catch-all
R1# clear ip bgp 10.0.12.2 soft in
R1# show ip bgp neighbors 10.0.12.2 routes
```
→ Chặn mọi route đi qua AS 65003, cho qua phần còn lại.

**⚠️ Test thiếu catch-all `.*`:**
```
R1(config)# no ip as-path access-list 10
R1(config)# ip as-path access-list 10 deny _65003_
!             (thiếu permit .*)
R1# clear ip bgp 10.0.12.2 soft in
R1# show ip bgp neighbors 10.0.12.2 routes
! Total number of prefixes 0            ← mất hết
```
⭐ AS-path ACL cũng có **implicit deny** — catch-all là **`permit .*`**.

**Dọn dẹp:**
```
R1(config-router)# no neighbor 10.0.12.2 filter-list 10 in
R1(config)# no ip as-path access-list 10
R1# clear ip bgp 10.0.12.2 soft in
```

#### 8d) Route-map — lọc + sửa attribute cùng lúc

```
R1(config)# ip prefix-list PL-BLOCK permit 10.3.4.0/24
R1(config)# ip as-path access-list 20 permit _65003_
!
R1(config)# route-map RM-COMBO-IN deny 5
R1(config-route-map)#  match ip address prefix-list PL-BLOCK       ! chặn prefix này
R1(config-route-map)# exit
R1(config)# route-map RM-COMBO-IN permit 10
R1(config-route-map)#  match as-path 20
R1(config-route-map)#  set local-preference 150                     ! route qua AS65003 → LocPref 150
R1(config-route-map)#  set community 65001:999 additive
R1(config-route-map)# exit
R1(config)# route-map RM-COMBO-IN permit 20                         ! CATCH-ALL
R1(config-route-map)# exit
!
R1(config)# router bgp 65001
R1(config-router)#  neighbor 10.0.12.2 route-map RM-COMBO-IN in
R1# clear ip bgp 10.0.12.2 soft in
```
```
R1# show route-map RM-COMBO-IN
```
**Output mẫu:**
```
route-map RM-COMBO-IN, deny, sequence 5
  Match clauses:
    ip address prefix-lists: PL-BLOCK
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
route-map RM-COMBO-IN, permit, sequence 10
  Match clauses:
    as-path (as-path filter): 20
  Set clauses:
    local-preference 150
    community 65001:999 additive
  Policy routing matches: 0 packets, 0 bytes
route-map RM-COMBO-IN, permit, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```
⭐ Chú ý `sequence 20` **không có `Match clauses`** → catch-all.

```
R1# show ip bgp | include 10.3.3.0|10.3.4.0
 *   10.3.3.0/24      10.0.12.2                    150        0 65002 65003 i    ← LocPref 150
 *>  10.3.3.0/24      10.0.14.2                              0 65004 65003 i
!     (10.3.4.0/24 từ R2 bị chặn)
```

**Dọn dẹp:**
```
R1(config-router)# no neighbor 10.0.12.2 route-map RM-COMBO-IN in
R1# clear ip bgp 10.0.12.2 soft in
```

✅ **Checkpoint bước 8 — điền bảng catch-all (cực quan trọng):**

| Công cụ | Catch-all đúng | Nếu thiếu |
|---|---|---|
| Prefix-list | | |
| AS-path ACL | | |
| Route-map | | |

<details><summary>Đáp án</summary>

| Công cụ | Catch-all đúng | Nếu thiếu |
|---|---|---|
| ⭐ **Prefix-list** | ⭐ **`permit 0.0.0.0/0 le 32`** ⚠️ (**không phải** `permit 0.0.0.0/0`) | 🔴 Chặn hết |
| ⭐ **AS-path ACL** | ⭐ **`permit .*`** | 🔴 Chặn hết |
| ⭐ **Route-map** | ⭐ **`route-map X permit <seq cao>`** (không có `match`) | 🔴 Chặn hết |

⭐ **Cả ba đều có implicit deny.** Đây là lỗi gây downtime phổ biến nhất khi làm filter BGP.
</details>

---

### Bước 9 — ⭐ `aggregate-address`

```
! R1 gộp 10.1.1.0/24 và 10.1.2.0/24 thành 10.1.0.0/22
R1(config)# router bgp 65001
R1(config-router)#  aggregate-address 10.1.0.0 255.255.252.0
```

**a) Không có `summary-only` — quảng bá cả aggregate + prefix con:**
```
R2# show ip bgp | include 10.1
 *>  10.1.0.0/22      10.0.12.1                              0 65001 i      ← aggregate
 *>  10.1.1.0/24      10.0.12.1                0             0 65001 i      ← prefix con
 *>  10.1.2.0/24      10.0.12.1                0             0 65001 i
```
⚠️ 3 route — không giảm gì.

**b) ⭐ Thêm `summary-only`:**
```
R1(config-router)# aggregate-address 10.1.0.0 255.255.252.0 summary-only
```
```
R1# show ip bgp | include 10.1
 *>  10.1.0.0/22      0.0.0.0                            32768 i           ← aggregate
 s>  10.1.1.0/24      0.0.0.0                  0         32768 i           ← s = suppressed
 s>  10.1.2.0/24      0.0.0.0                  0         32768 i
```
⭐⭐ **`s`** = **suppressed** — vẫn trong BGP table nhưng **KHÔNG quảng bá**.

```
R2# show ip bgp | include 10.1
 *>  10.1.0.0/22      10.0.12.1                              0 65001 i      ← CHỈ 1 route
```
⭐ **3 route → 1 route.**

**c) ⭐ Discard route Null0:**
```
R1# show ip route 10.1.0.0 255.255.252.0
```
**Output mẫu:**
```
Routing entry for 10.1.0.0/22
  Known via "bgp 65001", distance 200, metric 0, type locally generated
  Routing Descriptor Blocks:
  * directly connected, via Null0
```
⭐ Giống OSPF summarization (Module-04B §2.3) — chống loop.

**d) ⭐ `as-set` — giữ chống loop:**

Trước tiên xem AS-path của aggregate:
```
R2# show ip bgp 10.1.0.0
```
**Output mẫu (không có `as-set`):**
```
  65001, (aggregated by 65001 1.1.1.1)
    10.0.12.1 from 10.0.12.1 (1.1.1.1)
      Origin IGP, localpref 100, valid, external, atomic-aggregate, best
```
⭐ **`atomic-aggregate`** = cảnh báo *"route này đã bị gộp, **mất chi tiết AS-path**"*.

**Test aggregate với route học từ AS khác:**
```
! R1 gộp cả 10.3.0.0/22 (route học từ AS 65003) — mô phỏng leak
R1(config-router)# aggregate-address 10.3.0.0 255.255.252.0 summary-only
```
```
R2# show ip bgp 10.3.0.0
!   65001, (aggregated by 65001 1.1.1.1)        ← ⚠️ AS-path chỉ có 65001!
!         atomic-aggregate
```
⚠️ **AS-path chỉ có `65001`** — mất `65003` → ⭐ **route có thể quay lại AS 65003 → LOOP**.

**Thêm `as-set`:**
```
R1(config-router)# aggregate-address 10.3.0.0 255.255.252.0 summary-only as-set
```
```
R2# show ip bgp 10.3.0.0
```
**Output mẫu:**
```
  65001 {65002,65003}, (aggregated by 65001 1.1.1.1)      ← AS_SET!
    10.0.12.1 from 10.0.12.1 (1.1.1.1)
      Origin IGP, localpref 100, valid, external, best
```
⭐⭐ **`{65002,65003}`** = **AS_SET** — giữ được thông tin AS đã đi qua → ⭐ **chống loop hoạt động lại**.

**Verify chống loop:**
```
R3# show ip bgp | include 10.3.0.0
! → KHÔNG có (R3 thấy 65003 trong AS_SET → từ chối) ✅
```

**Dọn dẹp:**
```
R1(config-router)# no aggregate-address 10.3.0.0 255.255.252.0 summary-only as-set
R1(config-router)# no aggregate-address 10.1.0.0 255.255.252.0 summary-only
```

✅ **Checkpoint bước 9:**

| Kiểm tra | Mong đợi |
|---|---|
| Không có `summary-only` → quảng bá **cả** aggregate + prefix con | ✅ |
| Có `summary-only` → prefix con hiện ⭐ **`s`**, peer chỉ thấy **1 route** | ⭐ ✅ |
| Có **discard route Null0** cho aggregate | ✅ |
| Không có `as-set` → AS-path mất chi tiết + có `atomic-aggregate` | ⭐ ✅ |
| Có `as-set` → AS-path có **`{65002,65003}`**, chống loop hoạt động | ⭐ ✅ |

---
