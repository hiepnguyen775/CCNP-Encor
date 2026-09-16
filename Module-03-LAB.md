# LAB 03 — Tuần 6: Routing nền tảng

> 📘 **Lý thuyết:** [Module-03](Module-03-IP-Routing-Nen-tang.md) —
> đọc **Phần 1** và **Phần 2 mục §3.1–3.4** trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 2 GB · 🧰 **Cần:** EVE-NG + 4× vIOS

---

## Lab này trả lời 5 câu hỏi

| # | Câu hỏi | LAB |
|:---:|---|:---:|
| 1 | Có nhiều đường tới cùng một đích — router chọn đường nào, theo thứ tự nào? | 03-1 |
| 2 | Vì sao route `/32` luôn thắng route `/24`, dù AD cao hơn? | 03-1 |
| 3 | Đường "vẫn up" nhưng thực ra đã chết — làm sao router tự phát hiện? | 03-2 |
| 4 | Floating static và IP SLA khác nhau ở chỗ nào? | 03-2 |
| 5 | Nối hai giao thức định tuyến lại thì loop xảy ra thế nào, chặn bằng gì? | 03-3 |

> **LAB 03-2 (IP SLA + Object Tracking) là bài thực chiến nhất module này** — bạn sẽ dùng
> lại đúng kỹ thuật đó ở Module-06A (HSRP tracking) và Module-11 (đo chất lượng đường).

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Ba lab dùng CHUNG một topology** | Dựng một lần ở §4.1, dùng cho cả 3 lab. Đừng xóa giữa chừng |
| **Số liệu của bạn sẽ khác** | Metric, uptime, số entry sẽ khác output mẫu. Đối chiếu **cấu trúc**, đừng so từng số |
| **LAB 03-2 cần kiên nhẫn** | IP SLA có `frequency` và `delay` — thay đổi không xảy ra tức thì. Chờ đúng số giây rồi mới xem |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---



## 4.1 Topology chung cho cả module

```
                  10.0.12.0/30
        R1 ═══════════════════════ R2
        ║  Gi0/0            Gi0/0  ║
        ║                          ║
  Gi0/1 ║  10.0.13.0/30            ║ Gi0/1
        ╚══════════ R3 ════════════╝
                 10.0.23.0/30

  Gi0/2 (R1) ──▶ 198.51.100.0/30 ──▶ R-ISP2  (dự phòng)
  Loopback0:  R1 = 1.1.1.1/32 · R2 = 2.2.2.2/32 · R3 = 3.3.3.3/32
  Loopback1:  R2 = 172.16.2.0/24 (mạng "khách hàng" để redistribute)
              R3 = 172.16.3.0/24
```

| Node | Image | RAM | Vai trò |
|---|---|:---:|---|
| R1 | vIOS | 512 MB | Router chính, làm ASBR khi redistribute |
| R2 | vIOS | 512 MB | |
| R3 | vIOS | 512 MB | |
| R-ISP2 | vIOS | 512 MB | Giả lập ISP dự phòng (chỉ dùng ở LAB 03-2) |

**RAM tổng: 2 GB** ✅

---

### LAB 03-1 — Đọc bảng định tuyến & chứng minh 3 bước chọn đường

#### Bước 1 — Cấu hình nền

**R1:**
```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 description ---> To R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To R3
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R2:**
```
enable
configure terminal
hostname R2
no ip domain lookup
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
!
interface Loopback1
 description ---> Mang "khach hang" de redistribute
 ip address 172.16.2.1 255.255.255.0
!
interface GigabitEthernet0/0
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R3:**
```
enable
configure terminal
hostname R3
no ip domain lookup
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
interface Loopback1
 ip address 172.16.3.1 255.255.255.0
!
interface GigabitEthernet0/0
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Bước 2 — Bật OSPF area 0

```
! R1
router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 10000
 network 1.1.1.1 0.0.0.0 area 0
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.13.0 0.0.0.3 area 0

! R2 — CHÚ Ý: chưa quảng bá Loopback1 (172.16.2.0) vào OSPF
router ospf 1
 router-id 2.2.2.2
 auto-cost reference-bandwidth 10000
 network 2.2.2.2 0.0.0.0 area 0
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0

! R3 — cũng chưa quảng bá Loopback1
router ospf 1
 router-id 3.3.3.3
 auto-cost reference-bandwidth 10000
 network 3.3.3.3 0.0.0.0 area 0
 network 10.0.13.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
```

✅ **Checkpoint:** `show ip ospf neighbor` trên mỗi router → **2 neighbor `FULL`**.

#### Bước 3 — ⭐ Đọc bảng định tuyến đầy đủ

```
R1# show ip route
```
**Output mẫu:**
```
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2

Gateway of last resort is not set

      1.0.0.0/32 is subnetted, 1 subnets
C        1.1.1.1 is directly connected, Loopback0
      2.0.0.0/32 is subnetted, 1 subnets
O        2.2.2.2 [110/11] via 10.0.12.2, 00:03:22, GigabitEthernet0/0
      3.0.0.0/32 is subnetted, 1 subnets
O        3.3.3.3 [110/11] via 10.0.13.2, 00:03:22, GigabitEthernet0/1
      10.0.0.0/8 is variably subnetted, 6 subnets, 2 masks
C        10.0.12.0/30 is directly connected, GigabitEthernet0/0
L        10.0.12.1/32 is directly connected, GigabitEthernet0/0
C        10.0.13.0/30 is directly connected, GigabitEthernet0/1
L        10.0.13.1/32 is directly connected, GigabitEthernet0/1
O        10.0.23.0/30 [110/20] via 10.0.13.2, 00:03:22, GigabitEthernet0/1
                              [110/20] via 10.0.12.2, 00:03:22, GigabitEthernet0/0
```

⭐ **Bảng giải mã — điền vào để tự kiểm tra:**

| Thành phần trong output | Nghĩa |
|---|---|
| `C` | |
| `L` | |
| `O` | |
| `[110/11]` | |
| `via 10.0.12.2` | |
| `00:03:22` | |
| `variably subnetted, 6 subnets, 2 masks` | |
| `10.0.23.0/30` có **2 dòng via** | |
| `Gateway of last resort is not set` | |

<details><summary>Đáp án</summary>

| Thành phần | Nghĩa |
|---|---|
| `C` | **Connected** — subnet cắm trực tiếp |
| `L` | **Local** — chính IP của interface, luôn `/32` |
| `O` | **OSPF intra-area** (trong cùng area 0) |
| `[110/11]` | **[AD 110 / Metric 11]** |
| `via 10.0.12.2` | **Next-hop** |
| `00:03:22` | Route học được cách đây 3 phút 22 giây |
| `variably subnetted, 6 subnets, 2 masks` | Dải `10.0.0.0/8` bị chia thành 6 subnet với 2 loại mask (`/30` và `/32`) |
| 2 dòng `via` | ⭐ **ECMP** — 2 đường cùng metric 20 → chia tải |
| `Gateway of last resort is not set` | Chưa có default route |
</details>

**Chú ý:** `172.16.2.0/24` và `172.16.3.0/24` **KHÔNG có** trong bảng route của R1
— vì chưa được quảng bá vào OSPF. Chúng ta sẽ dùng chúng ở LAB 03-3.

#### Bước 4 — ⭐ Chứng minh Longest Prefix Match thắng AD

**a) Xem route hiện tại tới `2.2.2.2`:**
```
R1# show ip route 2.2.2.2
```
**Output mẫu:**
```
Routing entry for 2.2.2.2/32
  Known via "ospf 1", distance 110, metric 11, type intra area
  Last update from 10.0.12.2 on GigabitEthernet0/0, 00:04:11 ago
  Routing Descriptor Blocks:
  * 10.0.12.2, from 2.2.2.2, 00:04:11 ago, via GigabitEthernet0/0
      Route metric is 11, traffic share count is 1
```

**b) Thêm static route với prefix NGẮN HƠN nhưng AD TỐT HƠN:**
```
R1(config)# ip route 2.0.0.0 255.0.0.0 10.0.13.2
!            └── /8, AD 1 (tốt hơn OSPF 110 rất nhiều)
```

**c) Kiểm tra route nào được dùng cho `2.2.2.2`:**
```
R1# show ip route 2.2.2.2
```
**Output mẫu:**
```
Routing entry for 2.2.2.2/32
  Known via "ospf 1", distance 110, metric 11, type intra area
  ...
  * 10.0.12.2, from 2.2.2.2, ... via GigabitEthernet0/0
```

⭐ **KẾT QUẢ: vẫn dùng OSPF `/32` (AD 110), KHÔNG dùng static `/8` (AD 1).**

**Xác nhận bằng traceroute:**
```
R1# traceroute 2.2.2.2 source 1.1.1.1
```
→ Đi qua `10.0.12.2` (R2 trực tiếp), **không** qua `10.0.13.2` (R3).

**Xác nhận thêm bằng CEF (kiến thức Module-01):**
```
R1# show ip cef 2.2.2.2
2.2.2.2/32           10.0.12.2            GigabitEthernet0/0
```

⭐ **Bài học:** `/32` (32 bit khớp) **cụ thể hơn** `/8` (8 bit khớp) → longest prefix thắng,
**AD không được xét tới**.

**d) Chứng minh ngược lại — cùng prefix thì AD thắng:**
```
R1(config)# ip route 2.2.2.2 255.255.255.255 10.0.13.2
!            └── CÙNG /32 với route OSPF, AD 1
```
```
R1# show ip route 2.2.2.2
```
**Output mẫu:**
```
Routing entry for 2.2.2.2/32
  Known via "static", distance 1, metric 0
  Routing Descriptor Blocks:
  * 10.0.13.2
```
⭐ **Giờ static thắng** (AD 1 < 110) — vì **cùng prefix `/32`** nên mới xét tới AD.

**Xác nhận OSPF route vẫn tồn tại nhưng không vào RIB:**
```
R1# show ip ospf database router 2.2.2.2
R1# show ip route ospf | include 2.2.2.2
```
→ LSDB vẫn có thông tin, nhưng route **không vào bảng route**.

**e) Dọn dẹp:**
```
R1(config)# no ip route 2.0.0.0 255.0.0.0 10.0.13.2
R1(config)# no ip route 2.2.2.2 255.255.255.255 10.0.13.2
```

✅ **Checkpoint LAB 03-1 — bảng bạn tự điền:**

| Cấu hình | Route được dùng | AD | Vì sao |
|---|---|:---:|---|
| Chỉ OSPF `/32` | | | |
| + static `/8` AD 1 | | | |
| + static `/32` AD 1 | | | |

<details><summary>Đáp án</summary>

| Cấu hình | Route được dùng | AD | Vì sao |
|---|---|:---:|---|
| Chỉ OSPF `/32` | OSPF via 10.0.12.2 | 110 | Route duy nhất |
| + static `/8` AD 1 | ⭐ **Vẫn OSPF `/32`** | 110 | **Longest prefix** `/32` > `/8`, AD không được xét |
| + static `/32` AD 1 | ⭐ **Static** via 10.0.13.2 | 1 | **Cùng prefix `/32`** → xét AD → 1 < 110 |
</details>

---

### LAB 03-2 — ⭐ IP SLA + Object Tracking (lab thực chiến nhất module)

**Mục tiêu:** làm dual-ISP failover **thật sự hoạt động** — không phải chỉ dựa vào interface up/down.

#### Bước 1 — Thêm R-ISP2 và mở rộng topology

Thêm 1 node vIOS tên `R-ISP2`, nối `R1 Gi0/2` ↔ `R-ISP2 Gi0/0`.

> 💡 Trong lab này ta dùng **R2 làm "ISP1"** và **R-ISP2 làm "ISP2"**, đích cần tới là
> loopback `8.8.8.8` được tạo trên **R3** (mô phỏng "Internet").

**Cấu hình R3 — tạo đích "Internet":**
```
R3(config)# interface Loopback8
R3(config-if)#  description ---> Gia lap server tren Internet
R3(config-if)#  ip address 8.8.8.8 255.255.255.255
R3(config-if)# exit
R3(config)# router ospf 1
R3(config-router)#  network 8.8.8.8 0.0.0.0 area 0
```

**Cấu hình R-ISP2:**
```
enable
configure terminal
hostname R-ISP2
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> To R1 (backup path)
 ip address 198.51.100.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description ---> To R3
 ip address 10.0.34.1 255.255.255.252
 no shutdown
!
! Route tĩnh về mạng R1 và tới 8.8.8.8
ip route 1.1.1.1 255.255.255.255 198.51.100.1
ip route 8.8.8.8 255.255.255.255 10.0.34.2
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**Nối thêm** `R-ISP2 Gi0/1` ↔ `R3 Gi0/2`, và cấu hình trên R3:
```
R3(config)# interface GigabitEthernet0/2
R3(config-if)#  description ---> To R-ISP2
R3(config-if)#  ip address 10.0.34.2 255.255.255.252
R3(config-if)#  no shutdown
R3(config-if)# exit
R3(config)# ip route 198.51.100.0 255.255.255.252 10.0.34.1
R3(config)# ip route 1.1.1.1 255.255.255.255 10.0.34.1
```

**Cấu hình R1 — interface tới ISP2:**
```
R1(config)# interface GigabitEthernet0/2
R1(config-if)#  description ---> To ISP2 (backup)
R1(config-if)#  ip address 198.51.100.1 255.255.255.252
R1(config-if)#  no shutdown
```

#### Bước 2 — Cấu hình floating static THÔNG THƯỜNG (để thấy điểm yếu)

```
! Trên R1 — tạm thời tắt OSPF learning cho 8.8.8.8 để test static
R1(config)# ip route 8.8.8.8 255.255.255.255 10.0.12.2           ! qua ISP1 (R2), AD 1
R1(config)# ip route 8.8.8.8 255.255.255.255 198.51.100.2 200    ! qua ISP2, AD 200
```

> ℹ️ OSPF cũng học được `8.8.8.8` (AD 110). Static AD 1 sẽ thắng → đúng ý ta muốn test.

**Kiểm tra:**
```
R1# show ip route 8.8.8.8
```
**Output mẫu:**
```
Routing entry for 8.8.8.8/32
  Known via "static", distance 1, metric 0
  * 10.0.12.2
```
```
R1# traceroute 8.8.8.8 source 1.1.1.1
  1 10.0.12.2 ...        ← qua R2 (ISP1)
```

#### Bước 3 — ⭐ TÁI HIỆN LỖ HỔNG: đích chết mà route vẫn còn

```
! Trên R2 — mô phỏng "ISP1 nhận link nhưng mạng bên trong ISP chết"
! Cắt đường của R2 đi tới R3 (nơi có 8.8.8.8)
R2(config)# interface GigabitEthernet0/1
R2(config-if)# shutdown
```

**Nhưng link R1↔R2 VẪN UP.** Kiểm tra trên R1:
```
R1# show ip interface brief | include 0/0
GigabitEthernet0/0         10.0.12.1       YES manual up                    up
```
✅ Interface vẫn `up/up`.

```
R1# show ip route 8.8.8.8
```
**Output mẫu:**
```
Routing entry for 8.8.8.8/32
  Known via "static", distance 1, metric 0
  * 10.0.12.2                                 ← ⚠️ VẪN LÀ ISP1!
```

```
R1# ping 8.8.8.8 source 1.1.1.1
```
**Output mẫu:**
```
Sending 5, 100-byte ICMP Echos to 8.8.8.8, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
```

🔴 **ĐÂY LÀ LỖ HỔNG:** ping **fail 100%**, nhưng floating static **không failover** vì
interface `Gi0/0` vẫn `up` và next-hop `10.0.12.2` vẫn reachable.
**Traffic đi vào hố đen.** Route dự phòng ISP2 (AD 200) **không được kích hoạt**.

> ⭐ Đây chính là điểm yếu tôi nói ở Module-P0 §6 (bảng Thực chiến). Giờ bạn **tự tay tái hiện được nó**.
> Ghi vào `SO-TAY-LOI.md`.

**Hoàn tác để sang bước sau:**
```
R2(config)# interface GigabitEthernet0/1
R2(config-if)# no shutdown
```

#### Bước 4 — ⭐ VÁ LỖ HỔNG bằng IP SLA + Track

```
R1(config)# no ip route 8.8.8.8 255.255.255.255 10.0.12.2
R1(config)# exit
```

```
R1# configure terminal
!
! ═══ 1. IP SLA: ping thật 8.8.8.8 qua đường ISP1 ═══
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0
 frequency 5
 timeout 2000
 threshold 1000
!
ip sla schedule 1 life forever start-time now       ! KHÔNG ĐƯỢC QUÊN DÒNG NÀY
!
! ═══ 2. Track object theo dõi kết quả SLA ═══
track 1 ip sla 1 reachability
 delay down 3 up 5
!
! ═══ 3. Static route CÓ TRACK ═══
ip route 8.8.8.8 255.255.255.255 10.0.12.2 track 1        ! ISP1, chỉ tồn tại khi track UP
ip route 8.8.8.8 255.255.255.255 198.51.100.2 200         ! ISP2, dự phòng
!
end
write memory
```

#### Bước 5 — Kiểm tra IP SLA hoạt động

**a) SLA có chạy không:**
```
R1# show ip sla statistics 1
```
**Output mẫu:**
```
IPSLAs Latest Operation Statistics

IPSLA operation id: 1
        Latest RTT: 3 milliseconds
Latest operation start time: 10:15:32 UTC Mon Sep 9 2026
Latest operation return code: OK
Number of successes: 24
Number of failures: 0
Operation time to live: Forever
```
✅ **Checkpoint:** `return code: OK` · `Number of successes` **tăng dần** · `failures: 0`.

⚠️ Nếu `Number of successes: 0` và `Operation time to live: 0` → **bạn quên
`ip sla schedule 1 life forever start-time now`**.

**b) Track object:**
```
R1# show track 1
```
**Output mẫu:**
```
Track 1
  IP SLA 1 reachability
  Reachability is Up
    1 change, last change 00:02:15
  Delay up 5 secs, down 3 secs
  Latest operation return code: OK
  Latest RTT (millisecs) 3
  Tracked by:
    STATIC-IP-ROUTING 0
```
✅ **Checkpoint:** `Reachability is Up` · `Tracked by: STATIC-IP-ROUTING 0`.

**c) Route đang dùng đường nào:**
```
R1# show ip route 8.8.8.8
```
**Output mẫu:**
```
Routing entry for 8.8.8.8/32
  Known via "static", distance 1, metric 0
  * 10.0.12.2                                 ← ISP1 (đường chính)
```

#### Bước 6 — ⭐⭐ TEST FAILOVER THẬT (tình huống đã làm floating static thất bại)

```
! Ping liên tục để đếm gói mất
R1# ping 8.8.8.8 source 1.1.1.1 repeat 100
```

Ở console khác (hoặc dừng ping rồi làm), trên **R2** — tái hiện đúng lỗi ở Bước 3:
```
R2(config)# interface GigabitEthernet0/1
R2(config-if)# shutdown
```

**Quan sát trên R1 sau ~5–10 giây:**
```
R1#
%TRACK-6-STATE: 1 ip sla 1 reachability Up -> Down
```

```
R1# show track 1
```
**Output mẫu:**
```
Track 1
  IP SLA 1 reachability
  Reachability is Down                        ← đã phát hiện!
    2 changes, last change 00:00:08
  Latest operation return code: Timeout
```

```
R1# show ip route 8.8.8.8
```
**Output mẫu:**
```
Routing entry for 8.8.8.8/32
  Known via "static", distance 200, metric 0
  * 198.51.100.2                              ← ĐÃ CHUYỂN SANG ISP2!
```

```
R1# traceroute 8.8.8.8 source 1.1.1.1
  1 198.51.100.2 ...       ← qua R-ISP2
  2 10.0.34.2 ...          ← rồi tới R3
```

```
R1# ping 8.8.8.8 source 1.1.1.1
Success rate is 100 percent (5/5)             ← HOẠT ĐỘNG LẠI
```

🎉 **Đây là kết quả mà floating static thuần KHÔNG làm được.**

**Test hồi phục:**
```
R2(config)# interface GigabitEthernet0/1
R2(config-if)# no shutdown
```
Chờ ~10 giây (5 s frequency + 5 s delay up):
```
R1#
%TRACK-6-STATE: 1 ip sla 1 reachability Down -> Up
R1# show ip route 8.8.8.8
  * 10.0.12.2                                 ← quay về ISP1
```

⭐ **BẢNG SO SÁNH — điền vào:**

| Kịch bản | Floating static thuần | Floating static + IP SLA track |
|---|:---:|:---:|
| Interface local `down` | ✅ Failover | ✅ Failover |
| Next-hop unreachable | ✅ Failover | ✅ Failover |
| ⭐ **Đích chết, link vẫn up** | ❌ **KHÔNG** | ⭐ ✅ **Failover** |
| Thời gian phát hiện | — | ~8 s (frequency 5 + delay down 3) |
| Số gói mất khi failover | — | |

✅ **Checkpoint LAB 03-2:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ip sla statistics 1` → `return code: OK`, successes tăng | ✅ |
| `show track 1` → `Reachability is Up`, `Tracked by: STATIC-IP-ROUTING` | ✅ |
| Bình thường: route dùng ISP1 (`distance 1`) | ✅ |
| ⭐ Cắt đường **phía sau** ISP1 (link vẫn up) → track `Down` → route chuyển ISP2 (`distance 200`) | ⭐ ✅ |
| Bật lại → track `Up` → route quay về ISP1 | ✅ |
| Tái hiện được lỗ hổng của floating static thuần ở Bước 3 | ⭐ ✅ |

#### 🧪 Thử nghiệm thêm

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| Quên `ip sla schedule` | `no ip sla schedule 1` | `show ip sla stat 1` → successes = 0, track Down → route mất luôn! | ⭐ Lỗi kinh điển. **Luôn kiểm tra `Operation time to live`** |
| Bỏ `delay` | `track 1 ip sla 1 reachability` (không có delay) | Nhấp nháy link → route flap liên tục | Vì sao cần `delay down/up` |
| `delay up` ngắn hơn `down` | `delay down 10 up 1` | Route quay lại quá nhanh, chưa ổn định | ⭐ Nên `up` **lớn hơn** `down` |
| Đổi frequency | `frequency 1` | Phát hiện nhanh hơn nhưng tốn CPU/traffic | Cân bằng giữa nhanh và tải |
| Track nhiều SLA | `track 10 list boolean and` + `object 1` + `object 2` | Chỉ Down khi **cả 2** đích fail | Chống false-positive (1 đích chết ≠ ISP chết) |
| SLA sai source | Bỏ `source-interface` | SLA có thể ping qua đường ISP2 → không phát hiện lỗi ISP1! | ⭐ **`source-interface` là bắt buộc** để SLA đi đúng đường cần kiểm tra |

> ⭐ **Thử nghiệm cuối cùng là quan trọng nhất.** Nếu không chỉ định `source-interface`
> (hoặc `source-ip`), IP SLA sẽ ping theo **bảng route hiện tại** — nghĩa là khi ISP1 chết,
> nó có thể ping qua ISP2 và báo "OK" → **track không bao giờ Down**. Lỗi này rất khó tìm.

---

### LAB 03-3 — Redistribution + Route tag

**Mục tiêu:** đưa mạng static/connected vào OSPF, hiểu E1 vs E2, và dùng tag chống loop.

#### Bước 1 — Redistribute connected (Loopback1) vào OSPF

Nhớ rằng `172.16.2.0/24` (R2) và `172.16.3.0/24` (R3) chưa có trong OSPF.

```
! Trên R2
R2(config)# router ospf 1
R2(config-router)#  redistribute connected subnets
```

**Kiểm tra trên R1:**
```
R1# show ip route 172.16.2.0
```
**Output mẫu:**
```
Routing entry for 172.16.2.0/24
  Known via "ospf 1", distance 110, metric 20, type extern 2, forward metric 10
  Last update from 10.0.12.2 on GigabitEthernet0/0, 00:00:15 ago
  Routing Descriptor Blocks:
  * 10.0.12.2, from 2.2.2.2, 00:00:15 ago, via GigabitEthernet0/0
      Route metric is 20, traffic share count is 1
```

⭐ **Đọc output:**
- `metric 20` → **seed metric mặc định khi redistribute vào OSPF = 20** ✅
- `type extern 2` → **E2 là mặc định** ✅
- `forward metric 10` → cost nội bộ để tới ASBR (R2)

```
R1# show ip route ospf | include E2
O E2     172.16.2.0/24 [110/20] via 10.0.12.2, 00:01:22, GigabitEthernet0/0
```
⭐ Ký hiệu **`O E2`**.

⚠️ **Cảnh báo — `redistribute connected` là con dao hai lưỡi:**
```
R2# show ip route | include L|C
```
`redistribute connected` đưa **MỌI** subnet connected vào OSPF — kể cả những cái bạn không muốn.
Cách đúng là dùng **route-map lọc**:
```
R2(config)# ip prefix-list PL-CUSTOMER permit 172.16.2.0/24
R2(config)# route-map RM-CONN-TO-OSPF permit 10
R2(config-route-map)#  match ip address prefix-list PL-CUSTOMER
R2(config-route-map)# exit
R2(config)# router ospf 1
R2(config-router)#  no redistribute connected subnets
R2(config-router)#  redistribute connected subnets route-map RM-CONN-TO-OSPF
```
✅ Giờ chỉ `172.16.2.0/24` được đưa vào OSPF.

#### Bước 2 — ⭐ E1 vs E2: chứng minh khác biệt

**a) Cả R2 và R3 cùng redistribute một mạng chung** để tạo tình huống "2 ASBR":

```
! Trên R2
R2(config)# ip route 192.168.99.0 255.255.255.0 Null0
R2(config)# router ospf 1
R2(config-router)#  redistribute static subnets

! Trên R3 — cùng mạng đó
R3(config)# ip route 192.168.99.0 255.255.255.0 Null0
R3(config)# router ospf 1
R3(config-router)#  redistribute static subnets
```

**b) Xem R1 nhìn thấy gì (E2 — mặc định):**
```
R1# show ip route 192.168.99.0
```
**Output mẫu:**
```
Routing entry for 192.168.99.0/24
  Known via "ospf 1", distance 110, metric 20, type extern 2, forward metric 10
  Routing Descriptor Blocks:
  * 10.0.13.2, from 3.3.3.3, ... via GigabitEthernet0/1
    10.0.12.2, from 2.2.2.2, ... via GigabitEthernet0/0
      Route metric is 20, traffic share count is 1
```
⭐ **Cả 2 ASBR đều metric 20** → R1 **ECMP** qua cả hai. Metric E2 **không tính** đường nội bộ.

**c) Làm cho R2 "xa hơn" R1, rồi xem E2 có phân biệt được không:**
```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip ospf cost 500              ! làm đường tới R2 rất đắt
```
```
R1# show ip route 192.168.99.0
```
→ **Vẫn metric 20 cho cả hai!** Chỉ có `forward metric` khác nhau.
⚠️ Với E2, R1 **có thể** vẫn chọn cả 2 (hoặc chọn theo forward metric tùy IOS version)
— nhưng **metric E2 bản thân nó không phản ánh khoảng cách nội bộ**.

**d) Chuyển sang E1 và xem lại:**
```
! Trên CẢ R2 và R3
router ospf 1
 no redistribute static subnets
 redistribute static subnets metric-type 1
```
```
R1# show ip route 192.168.99.0
```
**Output mẫu:**
```
Routing entry for 192.168.99.0/24
  Known via "ospf 1", distance 110, metric 30, type extern 1
  Routing Descriptor Blocks:
  * 10.0.13.2, from 3.3.3.3, ... via GigabitEthernet0/1
      Route metric is 30, traffic share count is 1
```
⭐ **Giờ metric = 30** (20 external + 10 internal tới R3), và **chỉ có 1 next-hop**
— R1 chọn **ASBR gần hơn (R3)** vì đường tới R2 có cost 500.

```
R1# show ip route ospf | include E1
O E1     192.168.99.0/24 [110/30] via 10.0.13.2, ...
```

⭐ **BẢNG KẾT LUẬN — điền vào:**

| | **E2** | **E1** |
|---|---|---|
| Metric R1 thấy | | |
| Metric có tính đường nội bộ? | | |
| R1 phân biệt được ASBR gần/xa? | | |
| Ký hiệu | | |

<details><summary>Đáp án</summary>

| | **E2** (mặc định) | **E1** |
|---|---|---|
| Metric R1 thấy | **20** (không đổi toàn domain) | **30** = 20 external + 10 internal |
| Metric có tính đường nội bộ? | ❌ Không | ⭐ **Có** |
| R1 phân biệt được ASBR gần/xa? | ⚠️ Không (qua metric) | ⭐ **Có** — chọn ASBR gần nhất |
| Ký hiệu | `O E2` | `O E1` |

**Kết luận thực chiến:** có **nhiều điểm ra (nhiều ASBR)** → dùng **E1** để traffic ra điểm gần nhất.
</details>

**Dọn dẹp:**
```
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no ip ospf cost
```

#### Bước 3 — ⭐ Route tag

**a) Đánh tag khi redistribute:**
```
! Trên R2
R2(config)# route-map RM-STATIC-TO-OSPF permit 10
R2(config-route-map)#  set tag 100
R2(config-route-map)#  set metric 50
R2(config-route-map)#  set metric-type type-1
R2(config-route-map)# exit
R2(config)# router ospf 1
R2(config-router)#  no redistribute static subnets metric-type 1
R2(config-router)#  redistribute static subnets route-map RM-STATIC-TO-OSPF
```

**b) Xem tag trên R1:**
```
R1# show ip route 192.168.99.0
```
**Output mẫu:**
```
Routing entry for 192.168.99.0/24
  Known via "ospf 1", distance 110, metric 50, type extern 1
  Tag 100                                      ← TAG!
  Routing Descriptor Blocks:
  ...
```

```
R1# show ip ospf database external 192.168.99.0
```
**Output mẫu:**
```
                LS Type: AS External Link
                Link State ID: 192.168.99.0 (External Network Number)
                Advertising Router: 2.2.2.2
                LS Seq Number: 80000001
                Metric Type: 1 (Comparable directly to link state metric)
                MTID: 0
                Metric: 50
                Forward Address: 0.0.0.0
                External Route Tag: 100                ← TAG trong LSA type 5
```

⭐ **Tag được mang trong LSA type 5** — nghĩa là mọi router trong domain OSPF đều thấy được nó.
Đây là cơ chế cho phép chống loop ở điểm redistribute khác.

**c) Dùng tag để lọc — chặn route có tag 100:**
```
! Trên R3 — mô phỏng "điểm redistribute thứ 2", chặn route đã từ đây ra
R3(config)# route-map RM-BLOCK-TAG100 deny 5
R3(config-route-map)#  match tag 100
R3(config-route-map)# exit
R3(config)# route-map RM-BLOCK-TAG100 permit 10
R3(config-route-map)#  set tag 200
R3(config-route-map)# exit
```

**Kiểm tra route-map hoạt động:**
```
R3# show route-map RM-BLOCK-TAG100
```
**Output mẫu:**
```
route-map RM-BLOCK-TAG100, deny, sequence 5
  Match clauses:
    tag 100
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
route-map RM-BLOCK-TAG100, permit, sequence 10
  Match clauses:
  Set clauses:
    tag 200
  Policy routing matches: 0 packets, 0 bytes
```
⭐ Chú ý: `sequence 10` **không có `Match clauses`** → khớp mọi thứ (catch-all).

#### Bước 4 — ⚠️ Tái hiện lỗi redistribute vào EIGRP thiếu metric

> ℹ️ Chỉ để **thấy hành vi**, không phải để học cấu hình EIGRP.

```
! Trên R2 — bật EIGRP tối thiểu rồi redistribute OSPF vào, KHÔNG chỉ định metric
R2(config)# router eigrp 100
R2(config-router)#  network 10.0.23.0 0.0.0.3
R2(config-router)#  redistribute ospf 1              ! ⚠️ THIẾU METRIC
```
```
R2# show ip eigrp topology | include 1.1.1.1|10.0.13
```
→ **Không có route nào từ OSPF xuất hiện.** Không có thông báo lỗi.

```
R2# show ip protocols | section eigrp
```
→ Xem phần `Redistributing` — có khai báo nhưng route không vào.

**Sửa:**
```
R2(config)# router eigrp 100
R2(config-router)#  redistribute ospf 1 metric 10000 100 255 1 1500
```
→ Giờ route xuất hiện.

⭐ **Bài học:** redistribute vào **EIGRP/RIP bắt buộc chỉ định metric**
(hoặc `default-metric`). Vào **OSPF/BGP thì không cần**. **Ghi vào `SO-TAY-LOI.md`.**

**Dọn dẹp:**
```
R2(config)# no router eigrp 100
```

✅ **Checkpoint LAB 03-3:**

| Kiểm tra | Mong đợi |
|---|---|
| `redistribute connected subnets` → R1 thấy `O E2` metric **20** | ✅ |
| Dùng route-map + prefix-list để chỉ redistribute 1 subnet | ✅ |
| Chuyển sang `metric-type 1` → metric đổi thành **20 + internal cost** | ⭐ ✅ |
| E1 phân biệt được ASBR gần/xa, E2 thì không | ⭐ ✅ |
| `show ip route <prefix>` hiện dòng `Tag 100` | ✅ |
| `show ip ospf database external` hiện `External Route Tag: 100` | ⭐ ✅ |
| Tái hiện được lỗi redistribute vào EIGRP thiếu metric | ✅ |

---
