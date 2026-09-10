# Module-06B — NAT/PAT nâng cao, NTP & Multicast

> 🧭 **Lộ trình:** [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) → `[Bạn đang ở đây] Module-06B` → Module-07 (Wireless)
>
> 📊 **Blueprint — Domain 3.4 IP Services (thuộc Infrastructure 30%):**
> · **3.4.a — Describe Network Time Protocol (NTP)**
> · **3.4.b — Configure and verify NAT/PAT**
> · **3.4.d — Describe multicast protocols, such as PIM and IGMP v2/v3**
>
> ⏱️ **Tuần 11 (nửa sau)** · 5 giờ

---

## ⭐ 0. Phạm vi — chú ý từ "Configure" vs "Describe"

| Chủ đề | Blueprint dùng từ | Nghĩa | Thời gian |
|---|---|---|---|
| ⭐ **NAT / PAT** | ⭐ **"Configure and verify"** | ⭐ **Cấu hình + verify + troubleshoot** | 2.5 giờ |
| 🟡 **NTP** | 🟡 **"Describe"** | Hiểu cơ chế + đọc output. ⭐ Nhưng **nên biết cấu hình** (rất dễ, và dùng hằng ngày) | 1 giờ |
| 🟡 **Multicast (PIM, IGMP v2/v3)** | 🟡 **"Describe"** | ⭐ **CHỈ hiểu khái niệm** — không cần cấu hình PIM | 1.5 giờ |
| 🟡 IPv6 First-Hop Security | *(không có trong blueprint ENCOR)* | Bổ trợ — đọc 10 phút | 10 phút |

> ⭐ **Tiết kiệm thời gian:** đừng dựng lab PIM-SM phức tạp. Đề chỉ hỏi
> *"PIM Dense vs Sparse khác gì"*, *"IGMPv2 vs v3 khác gì"*, *"RPF check là gì"*.
> ⭐ **Học bảng §4 là đủ.**

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-P0 §2.7 (NAT cơ bản) · Module-03 §2.7 (route-map) |
| **Lab** | ⭐ **Dùng lại LAB 06A** (R1, R2, SW1, R-ISP, PC1) |
| **RAM** | ~2.3 GB ✅ |
| **Thời lượng** | 2h lý thuyết · 2.5h lab · 0.5h quiz |

---

## 📘 2. NAT / PAT NÂNG CAO

### 2.1 Bốn thuật ngữ NAT — phải phân biệt chính xác

⭐ **Quy tắc đọc:** **Inside/Outside** = host đó thuộc mạng nào · **Local/Global** = nhìn từ phía nào.

| Thuật ngữ | Nghĩa | Ví dụ |
|---|---|---|
| ⭐ **Inside Local** | IP **thật** của host **nội bộ** (nhìn từ trong) | `10.1.10.100` |
| ⭐ **Inside Global** | IP host nội bộ **hóa trang thành** (nhìn từ ngoài) | `203.0.113.1` |
| ⭐ **Outside Global** | IP **thật** của host **bên ngoài** (nhìn từ ngoài) | `8.8.8.8` |
| ⭐ **Outside Local** | IP host bên ngoài **hiện ra với nội bộ** | `8.8.8.8` *(thường giống Outside Global)* |

⭐ **Khi nào Outside Local ≠ Outside Global:** khi dùng `ip nat outside source` —
tức là bạn **dịch cả IP của bên ngoài** để nội bộ thấy nó là IP khác.
Dùng khi 2 mạng có IP trùng nhau (VD sau khi sáp nhập công ty).

```
show ip nat translations
```
**Output mẫu:**
```
Pro  Inside global      Inside local       Outside local      Outside global
icmp 203.0.113.1:5      10.1.10.100:5      8.8.8.8:5          8.8.8.8:5
tcp  203.0.113.1:1035   10.1.10.100:1035   8.8.8.8:80         8.8.8.8:80
```
⭐ Đọc theo đúng 4 cột — đây là cách nhanh nhất hiểu NAT đang làm gì.

### 2.2 ⭐⭐ Thứ tự NAT vs Routing — bẫy đề quan trọng nhất

> ⭐ **Inside → Outside:** ⭐ **ROUTING TRƯỚC, NAT SAU**
> ⭐ **Outside → Inside:** ⭐ **NAT TRƯỚC, ROUTING SAU**

```
   ═══ INSIDE → OUTSIDE (host nội bộ ra Internet) ═══
   
   Gói vào  →  ACL input  →  Policy routing  →  ⭐ ROUTING  →  ⭐ NAT (local→global)
                                                     ↑
                                        ⭐ PHẢI CÓ ROUTE TỚI ĐÍCH
                                        trước khi NAT xảy ra!

   ═══ OUTSIDE → INSIDE (Internet vào server nội bộ) ═══
   
   Gói vào  →  ACL input  →  ⭐ NAT (global→local)  →  Policy routing  →  ⭐ ROUTING
                                    ↑
                        ⭐ NAT xảy ra TRƯỚC → routing dùng IP ĐÃ DỊCH
```

⭐ **Ba hệ quả thực tế phải nhớ:**

| # | Hệ quả | Chi tiết |
|:---:|---|---|
| **1** | 🔴 ⭐ **Thiếu default route = NAT vô nghĩa** | Inside→Outside: router **routing trước**. Không có route tới đích → **drop gói trước khi NAT kịp xảy ra** |
| **2** | ⭐ **ACL inbound trên interface outside dùng IP PUBLIC** | Outside→Inside: ACL input chạy **TRƯỚC** NAT → ACL phải khớp **Inside Global** (IP public), **không** phải IP private |
| **3** | ⭐ **ACL trên interface inside dùng IP PRIVATE** | Inside→Outside: ACL input chạy trước NAT → khớp **Inside Local** |

⭐ **Ví dụ hệ quả #2** — port forward web server `10.1.10.50` qua IP public `203.0.113.5`:
```
! ❌ SAI — ACL dùng IP private
ip access-list extended ACL-OUT-IN
 permit tcp any host 10.1.10.50 eq 80        ! ⚠️ ACL chạy TRƯỚC NAT → không khớp

! ✅ ĐÚNG — ACL dùng IP public (Inside Global)
ip access-list extended ACL-OUT-IN
 permit tcp any host 203.0.113.5 eq 80       ! ⭐ đúng
 deny   ip any any log
!
interface GigabitEthernet0/1
 ip access-group ACL-OUT-IN in
```

> ⭐ **Đây là một trong những lỗi khó tìm nhất khi làm port forwarding.** Cấu hình NAT đúng,
> ACL "trông đúng", mà không hoạt động — vì thứ tự xử lý.

### 2.3 Các kiểu NAT — bảng đầy đủ

| Kiểu | Ánh xạ | Lệnh | Dùng khi |
|---|---|---|---|
| ⭐ **Static NAT** | 1 private ↔ 1 public, **cố định 2 chiều** | `ip nat inside source static 10.1.10.50 203.0.113.5` | Server nội bộ cần IP public cố định |
| ⭐ **Static PAT**<br>*(port forwarding)* | 1 private:port ↔ 1 public:port | `ip nat inside source static tcp 10.1.10.50 80 203.0.113.5 80` | ⭐ Publish 1 dịch vụ, tiết kiệm IP public |
| **Dynamic NAT** | Nhiều private ↔ **pool** public, 1:1 | `ip nat pool P1 ...` + `ip nat inside source list 1 pool P1` | Ít dùng (tốn IP public) |
| ⭐ **PAT / Overload** | Nhiều private → **1 public**, phân biệt bằng **port** | `ip nat inside source list 1 interface Gi0/1 overload` | ⭐ Cái mọi mạng đang dùng |
| **PAT với pool** | Nhiều private → **pool** public + port | `ip nat inside source list 1 pool P1 overload` | Mạng lớn (>65k session) |
| ⭐ **NAT với route-map** | Theo **interface đi ra** | `ip nat inside source route-map RM1 interface Gi0/1 overload` | ⭐ **Dual-ISP** — cùng IP private NAT khác nhau theo ISP |
| **Outside source NAT** | Dịch IP **bên ngoài** | `ip nat outside source static 172.16.1.1 10.99.1.1` | 2 mạng trùng IP (sáp nhập công ty) |

#### Static NAT & Static PAT

```
! ═══ Static NAT — toàn bộ IP ═══
ip nat inside source static 10.1.10.50 203.0.113.5

! ═══ Static PAT — chỉ 1 port (⭐ port forwarding) ═══
ip nat inside source static tcp 10.1.10.50 80  203.0.113.5 80   extendable
ip nat inside source static tcp 10.1.10.50 443 203.0.113.5 443  extendable
ip nat inside source static udp 10.1.10.60 53  203.0.113.5 53   extendable

! ⭐ Port khác nhau — publish 2 server qua 1 IP public
ip nat inside source static tcp 10.1.10.50 80 203.0.113.5 8080  extendable
ip nat inside source static tcp 10.1.10.51 80 203.0.113.5 8081  extendable

! ═══ Dùng IP của interface (khi chỉ có 1 IP public) ═══
ip nat inside source static tcp 10.1.10.50 80 interface GigabitEthernet0/1 80
```

⭐ **`extendable`:** cho phép **cùng một Inside Local** có nhiều entry với các Inside Global khác nhau
(cần cho dual-ISP static NAT). Nhiều IOS tự thêm.

#### Dynamic NAT & PAT

```
! ═══ Pool ═══
ip nat pool POOL-PUBLIC 203.0.113.10 203.0.113.20 netmask 255.255.255.0
!  (hoặc: prefix-length 24)

! ═══ ACL chọn mạng nào được NAT ═══
ip access-list standard ACL-NAT
 permit 10.1.10.0 0.0.0.255
 permit 10.1.20.0 0.0.0.255

! ═══ Dynamic NAT (1:1, hết pool là hết) ═══
ip nat inside source list ACL-NAT pool POOL-PUBLIC

! ═══ ⭐ PAT với pool (nhiều host chung 1 IP + port) ═══
ip nat inside source list ACL-NAT pool POOL-PUBLIC overload

! ═══ ⭐ PAT với IP interface (phổ biến nhất) ═══
ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
```

⚠️ **Dynamic NAT hết pool:** host thứ N+1 **không NAT được** → **drop**. Log:
```
%NAT-4-ADDR_ALLOC_FAILURE: Address allocation failed; pool POOL-PUBLIC may be exhausted
```

#### ⭐⭐ NAT với route-map — giải pháp chuẩn cho dual-ISP

🔴 **Vấn đề:** với NAT thường (`ip nat inside source list ... interface Gi0/1 overload`),
router tạo **simple translation entry**. Khi failover sang ISP2, entry cũ vẫn còn →
⭐ **traffic bị NAT sai IP** → không hoạt động cho tới khi entry hết hạn (24 giờ!).

⭐ **Giải pháp: NAT dựa route-map** → tạo **fully-extended entry** (có cả outside address)
→ cùng một Inside Local có thể có **nhiều entry** cho nhiều ISP.

```
! ═══ ACL chọn mạng NAT ═══
ip access-list standard ACL-NAT
 permit 10.1.10.0 0.0.0.255

! ═══ Route-map: match ACL + ⭐ match INTERFACE ĐI RA ═══
route-map RM-NAT-ISP1 permit 10
 match ip address ACL-NAT
 match interface GigabitEthernet0/1              ! ⭐ ISP1
!
route-map RM-NAT-ISP2 permit 10
 match ip address ACL-NAT
 match interface GigabitEthernet0/2              ! ⭐ ISP2

! ═══ NAT theo route-map ═══
ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
```

⭐ **Cơ chế:** `match interface` làm NAT chỉ áp dụng khi gói **thật sự đi ra** interface đó.
Khi routing đổi sang ISP2 (nhờ IP SLA + track, Module-03), NAT tự dùng route-map ISP2.

⭐ **Kết hợp đầy đủ dual-ISP:**
| Lớp | Cấu hình |
|---|---|
| 1. Routing failover | IP SLA + track + floating static (Module-03 §2.4) |
| 2. ⭐ NAT failover | ⭐ NAT route-map theo interface (ở đây) |
| 3. Gateway HA cho LAN | HSRP + tracking (Module-06A) |

⚠️ **Vẫn nên clear NAT khi failover** để entry cũ không giữ traffic:
```
! Dùng EEM tự động (Module-12) hoặc tay:
clear ip nat translation *
```

#### NAT timeout

```
show ip nat translations verbose | include timeout
!
ip nat translation timeout 86400          ! mặc định 24h cho entry chung
ip nat translation tcp-timeout 86400      ! TCP: 24h
ip nat translation udp-timeout 300        ! UDP: 5 phút
ip nat translation icmp-timeout 60        ! ICMP: 60s
ip nat translation dns-timeout 60
ip nat translation finrst-timeout 60      ! sau FIN/RST
ip nat translation syn-timeout 60
ip nat translation max-entries 5000       ! ⭐ giới hạn tổng entry (chống cạn RAM)
ip nat translation max-entries host 10.1.10.100 100   ! giới hạn theo host
```

⭐ **`max-entries` là bảo vệ quan trọng:** 1 PC nhiễm malware có thể tạo **hàng chục nghìn** entry
→ ⭐ **router hết RAM**. Đặt giới hạn theo host.

### 2.4 🟡 NAT64 & NPTv6 (describe)

| | ⭐ **NAT64** | ⭐ **NPTv6** |
|---|---|---|
| Làm gì | ⭐ Dịch **IPv6 ↔ IPv4** | ⭐ Dịch **IPv6 prefix ↔ IPv6 prefix** |
| Có dịch port? | ✅ Stateful NAT64 có | ❌ **Không** — chỉ đổi prefix |
| Ánh xạ | Stateless (1:1) hoặc **Stateful (many:1)** | ⭐ **1:1, stateless** |
| Well-known prefix | ⭐ **`64:FF9B::/96`** | — |
| Kèm theo | ⭐ **DNS64** (tổng hợp AAAA từ A record) | — |
| Dùng khi | Client IPv6-only cần truy cập server IPv4 | Đổi prefix ISP mà không đổi IP nội bộ |

```
! NAT64 stateful (tham khảo)
nat64 prefix stateful 2001:DB8:64::/96
nat64 v4 pool POOL64 203.0.113.10 203.0.113.20
nat64 v6v4 list ACL-V6 pool POOL64 overload
interface Gi0/0
 nat64 enable
```

⭐ **Điểm quan trọng cho đề:** NPTv6 ⭐ **không phải NAT thật** — nó chỉ đổi prefix,
**giữ nguyên host portion**, **checksum-neutral**, **không có state**.
Triết lý IPv6 là *"không cần NAT"* — địa chỉ đủ dùng.

---

## 📘 3. NTP

### 3.1 Vì sao thời gian quan trọng (và vì sao blueprint có mục này)

| Thứ phụ thuộc thời gian đúng | Hậu quả nếu sai |
|---|---|
| ⭐ **Syslog timestamp** | ⭐ Không thể **tương quan sự cố** giữa các thiết bị → troubleshoot bất khả thi |
| ⭐ **Certificate (PKI/TLS)** | ⭐ Cert bị coi là **hết hạn / chưa hiệu lực** → SSH/HTTPS/802.1X fail |
| ⭐ **Kerberos / AD** | Chênh > 5 phút → ⭐ **không đăng nhập được** |
| **TACACS+ / RADIUS accounting** | Log sai giờ → không audit được |
| **DHCP lease** | Lease tính sai |
| **SNMP / NetFlow** | Dữ liệu đo sai thời điểm |
| ⭐ **Forensics / compliance** | ⭐ Log không có giá trị pháp lý |

🧠 ⭐ ***"Không có NTP thì log vô giá trị."*** Đó là lý do NTP nằm trong blueprint —
nó là **nền tảng của Network Assurance** (Module-11).

### 3.2 Stratum & kiến trúc

```
   Stratum 0  = ⭐ Reference clock (đồng hồ nguyên tử, GPS) — KHÔNG phải thiết bị mạng
        │
   Stratum 1  = Server nối TRỰC TIẾP vào stratum 0
        │
   Stratum 2  = Server sync với stratum 1
        │
   Stratum 3  = ...
        │
   Stratum 15 = ⭐ Mức thấp nhất còn DÙNG ĐƯỢC
   Stratum 16 = ⭐ KHÔNG ĐỒNG BỘ (unsynchronized) — không dùng được
```

| Thuộc tính | Giá trị |
|---|---|
| Transport | ⭐ **UDP port 123** |
| Stratum hợp lệ | **1–15** (⭐ **16 = chưa sync**) |
| Độ chính xác mong đợi | LAN: **< 1 ms** · WAN/Internet: **10–100 ms** |
| Multicast (nếu dùng) | 224.0.1.1 |
| **SNTP** | ⭐ Simple NTP — **chỉ làm client**, thuật toán đơn giản hơn, kém chính xác hơn |

### 3.3 Bốn chế độ NTP

| Chế độ | Lệnh | Nghĩa |
|---|---|---|
| ⭐ **Client/Server** | `ntp server <ip>` | ⭐ Tôi **đồng bộ theo** server đó (một chiều) |
| ⭐ **Peer (symmetric)** | `ntp peer <ip>` | ⭐ **Hai chiều** — cả hai có thể sync nhau |
| ⭐ **Master** | `ntp master <stratum>` | ⭐ Router **tự làm nguồn thời gian** (mặc định stratum 8) |
| Broadcast/Multicast | `ntp broadcast client` | Ít dùng |

### 3.4 Cấu hình NTP đầy đủ

```
! ═══ 1. Timezone (Việt Nam UTC+7) ═══
clock timezone ICT 7
!  (Việt Nam không có DST)

! ═══ 2. Authentication (⭐ nên có) ═══
ntp authenticate
ntp authentication-key 1 md5 NtpS3cret2026
ntp trusted-key 1

! ═══ 3. Server ═══
ntp server 10.1.1.10 key 1 prefer                  ! ⭐ prefer = ưu tiên server này
ntp server 10.1.1.11 key 1
ntp source Loopback0                                ! ⭐ IP nguồn cố định
ntp update-calendar                                 ! ⭐ đồng bộ cả hardware clock

! ═══ 4. Access control (⭐ chống NTP amplification attack) ═══
ip access-list standard ACL-NTP-PEER
 permit 10.1.1.10
 permit 10.1.1.11
ip access-list standard ACL-NTP-SERVE
 permit 10.0.0.0 0.255.255.255
!
ntp access-group peer ACL-NTP-PEER                  ! ai được sync 2 chiều với tôi
ntp access-group serve-only ACL-NTP-SERVE           ! ⭐ ai được xin giờ từ tôi
```

⭐ **4 loại `ntp access-group`** (từ **lỏng** tới **chặt**):

| Loại | Cho phép |
|---|---|
| `peer` | Sync 2 chiều + serve + query (lỏng nhất) |
| `serve` | Serve + query |
| ⭐ `serve-only` | ⭐ **Chỉ trả lời request giờ** — an toàn cho router làm NTP server nội bộ |
| `query-only` | Chỉ trả lời truy vấn control (chặt nhất) |

### 3.5 ⭐ Đọc output NTP

```
show ntp status
```
**Output mẫu:**
```
Clock is synchronized, stratum 3, reference is 10.1.1.10
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**10
ntp uptime is 125400 (1/100 of seconds), resolution is 4000
reference time is E8F3A2B1.7C3D4E5F (10:15:32.485 ICT Mon Sep 9 2026)
clock offset is 1.2345 msec, root delay is 12.34 msec
root dispersion is 25.67 msec, peer dispersion is 1.23 msec
loopfilter state is 'CTRL' (Normal Controlled Loop), drift is 0.000001234 s/s
system poll interval is 64, last update was 45 sec ago.
```

| Dòng | Nghĩa | Cần chú ý |
|---|---|---|
| ⭐ `Clock is synchronized` | ✅ Đã đồng bộ | ⚠️ `unsynchronized` = có vấn đề |
| ⭐ `stratum 3` | Cách nguồn 3 bước | ⚠️ **`stratum 16` = CHƯA SYNC** |
| ⭐ `reference is 10.1.1.10` | Đang sync với server nào | |
| ⭐ `clock offset` | Lệch bao nhiêu ms so với server | ⚠️ Lớn (>100 ms) = mạng tệ hoặc server xa |
| `root delay` | RTT tới stratum 1 | |
| `root dispersion` | Sai số tích lũy | ⚠️ Lớn = độ tin cậy thấp |
| `last update was 45 sec ago` | Cập nhật lần cuối | ⚠️ Lâu (>1024 s) = mất liên lạc |

```
show ntp associations
```
**Output mẫu:**
```
  address         ref clock       st   when   poll reach  delay  offset   disp
*~10.1.1.10      132.163.96.1     2     45     64   377  12.345   1.234  1.567
+~10.1.1.11      129.6.15.28      2     52     64   377  15.678   2.345  2.123
 ~10.1.1.12      0.0.0.0         16      -     64     0   0.000   0.000 16000.
 * sys.peer, # selected, + candidate, - outlier, x falseticker, ~ configured
```

⭐⭐ **BẢNG KÝ HIỆU — đề hay hỏi:**

| Ký hiệu | Nghĩa |
|:---:|---|
| ⭐ **`*`** | ⭐ **sys.peer** — server đang **THỰC SỰ được dùng** để đồng bộ |
| ⭐ **`#`** | **Selected** — tốt, nhưng khoảng cách quá xa để làm sys.peer |
| ⭐ **`+`** | **Candidate** — hợp lệ, sẵn sàng thay thế |
| **`-`** | **Outlier** — bị thuật toán clustering loại |
| ⭐ **`x`** | ⭐ **Falseticker** — ⭐ **server báo giờ SAI** (bị loại) |
| *(trống)* | **Rejected** — không dùng được (unreachable / stratum 16) |
| `~` | Configured (khai báo tay, không phải học động) |

| Cột | Nghĩa |
|---|---|
| `st` | ⭐ **Stratum của server đó**. `16` = server đó chưa sync |
| `when` | Bao lâu rồi từ lần nhận packet cuối (giây) |
| `poll` | Chu kỳ hỏi (giây) — tự điều chỉnh 64→1024 |
| ⭐ `reach` | ⭐ **Reachability register (bát phân)**. ⭐ **`377` = 8/8 lần gần nhất OK** (hoàn hảo). `0` = không tới được |
| `delay` / `offset` / `disp` | RTT / lệch giờ / độ phân tán (ms) |

⭐ **`reach 377`** là số **bát phân** = `11111111` binary = 8 lần poll gần nhất **đều thành công**.
Thấy `reach` thấp (VD `1`, `17`) = **mất gói NTP**.

**Các lệnh khác:**
```
show clock detail                          ! ⭐ giờ hiện tại + nguồn
show ntp status
show ntp associations
show ntp associations detail               ! ⭐ chi tiết từng peer
show ntp packets
show ntp config
debug ntp all                              ! ⚠️ chỉ lab
debug ntp packets
```

**Output mẫu `show clock detail`:**
```
10:20:15.485 ICT Mon Sep 9 2026
Time source is NTP                          ← ⭐ nguồn là NTP (tốt)
```
| `Time source` | Nghĩa |
|---|---|
| ⭐ **`NTP`** | ✅ Đồng bộ từ NTP |
| `user configuration` | ⚠️ Đặt tay bằng `clock set` — sẽ **drift** |
| `hardware calendar` | Từ đồng hồ phần cứng |
| ⭐ **(không có dòng này)** | ⚠️ **Chưa bao giờ được đặt** — dấu `*` trước giờ |

⭐ **Dấu `*` trước giờ** (VD `*10:20:15.485`) = ⭐ **thời gian KHÔNG đáng tin** (chưa sync).

---

## 📘 4. MULTICAST (describe)

### 4.1 Địa chỉ multicast — bảng phải nhớ

| Dải | Tên | Dùng cho |
|---|---|---|
| **224.0.0.0/4** | Toàn bộ multicast | `224.0.0.0` – `239.255.255.255` |
| ⭐ **224.0.0.0/24** | ⭐ **Local Network Control** | ⭐ **Link-local, TTL = 1, KHÔNG được route** |
| 224.0.1.0/24 | Internetwork Control | Được route (VD `224.0.1.1` = NTP) |
| ⭐ **232.0.0.0/8** | ⭐ **SSM** (Source-Specific Multicast) | ⭐ Không cần RP |
| 233.0.0.0/8 | GLOP | Gán theo ASN |
| ⭐ **239.0.0.0/8** | ⭐ **Administratively Scoped** | ⭐ **"Private" của multicast** (như RFC1918) |

⭐ **Các địa chỉ link-local phải thuộc:**

| Địa chỉ | Dùng cho |
|---|---|
| **224.0.0.1** | All hosts |
| **224.0.0.2** | All routers · ⭐ **HSRPv1** |
| ⭐ **224.0.0.5 / .6** | ⭐ **OSPF** (AllSPF / AllDR) |
| **224.0.0.9** | RIPv2 |
| ⭐ **224.0.0.10** | ⭐ **EIGRP** |
| **224.0.0.13** | ⭐ **PIM** |
| ⭐ **224.0.0.18** | ⭐ **VRRP** |
| ⭐ **224.0.0.22** | ⭐ **IGMPv3** |
| **224.0.0.102** | ⭐ **HSRPv2 / GLBP** |
| 224.0.1.39 / .40 | Auto-RP (Announce / Discovery) |

### 4.2 ⭐ Multicast MAC & vấn đề 32:1

```
   IP multicast:  1110 xxxx  xxxxxxxx  xxxxxxxx  xxxxxxxx    (32 bit)
                  └4 bit┘    └────── 28 bit group ──────┘
                            
   MAC multicast: 01:00:5E : 0 + 23 bit thấp nhất của IP
                  └ 25 bit cố định ┘  └── 23 bit ──┘
                  
   ⭐ 28 bit group  −  23 bit mang được  =  5 bit BỊ MẤT
   ⭐ → 2^5 = 32 IP multicast khác nhau ánh xạ về CÙNG 1 MAC → "32:1 overlap"
```

**Ví dụ:** `224.1.1.1` và `225.1.1.1` và `239.129.1.1` → **cùng MAC** `01:00:5E:01:01:01`

⚠️ **Hệ quả:** host đăng ký group A có thể **nhận cả traffic** của group B (cùng MAC)
→ NIC nhận, rồi **CPU host phải lọc bằng software** → tốn CPU vô ích.

⭐ **Bài học thiết kế:** khi chọn địa chỉ multicast nội bộ, ⭐ **tránh dùng các địa chỉ
có 23 bit thấp trùng nhau**. Dùng `239.x.x.x` và quy hoạch cẩn thận.

### 4.3 ⭐⭐ IGMP — v1 vs v2 vs v3

**IGMP = giao tiếp giữa HOST và ROUTER** ("tôi muốn nhận group này").

| | **IGMPv1** | ⭐ **IGMPv2** | ⭐ **IGMPv3** |
|---|---|---|---|
| RFC | 1112 | **2236** | **3376** |
| Join | ✅ | ✅ | ✅ |
| ⭐ **Leave Group** | ❌ **KHÔNG** (chờ timeout ~3 phút) | ⭐ ✅ **Có** — rời nhanh | ✅ |
| ⭐ **Querier election** | ❌ (dựa PIM DR) | ⭐ ✅ — ⭐ **IP THẤP NHẤT thắng** | ✅ |
| Group-Specific Query | ❌ | ✅ | ✅ |
| Max Response Time | ❌ | ✅ | ✅ |
| ⭐ **Source filtering** | ❌ | ❌ | ⭐ ✅ **INCLUDE / EXCLUDE source list** |
| Hỗ trợ **SSM** | ❌ | ❌ | ⭐ ✅ **BẮT BUỘC cho SSM** |
| Report gửi tới | Group address | Group address | ⭐ **224.0.0.22** |

#### 🔴⭐ BẪY ĐỀ: Querier election vs PIM DR election

> ⭐ **IGMP Querier: IP THẤP NHẤT thắng**
> ⭐ **PIM DR: IP CAO NHẤT thắng**

⚠️ **Ngược nhau!** Đây là bẫy đề kinh điển. (Và cả hai đều khác OSPF DR:
priority cao → **Router ID cao** nhất.)

#### ⭐ IGMPv3 source filtering — nền của SSM

| Chế độ | Nghĩa |
|---|---|
| ⭐ **INCLUDE** | *"Tôi muốn group G, **CHỈ từ** source S1, S2"* |
| ⭐ **EXCLUDE** | *"Tôi muốn group G, **TRỪ** source S3"* |

⭐ **Vì sao quan trọng:** cho phép **SSM** — host chỉ định rõ **(S, G)** →
⭐ **không cần RP**, và **chống được multicast spoofing** (kẻ khác gửi vào group G bị lọc).

#### IGMP Snooping (trên switch)

| Không có IGMP snooping | ⭐ Có IGMP snooping |
|---|---|
| Switch **flood** multicast ra **mọi port** trong VLAN (như broadcast) | ⭐ Switch **nghe IGMP** → chỉ gửi ra port **có host đăng ký** |
| ⚠️ Tốn băng thông, tốn CPU host | ⭐ Tiết kiệm lớn (video multicast) |

```
ip igmp snooping                            ! global (mặc định BẬT trên Catalyst)
ip igmp snooping vlan 10
ip igmp snooping vlan 10 querier            ! ⭐ khi VLAN không có router multicast
show ip igmp snooping
show ip igmp snooping groups
show mac address-table multicast
```

⚠️ **Bẫy thực tế:** VLAN **không có router multicast** → ⭐ **không có querier** →
IGMP snooping không học được gì → switch **flood**. Sửa: bật `ip igmp snooping vlan X querier`.

### 4.4 ⭐⭐ PIM — 4 chế độ

**PIM = giao tiếp giữa ROUTER và ROUTER** (xây cây phân phối multicast).

| Chế độ | Cơ chế | Ưu | Nhược | Dùng khi |
|---|---|---|---|---|
| **PIM-DM**<br>*(Dense Mode)* | ⭐ **Flood-and-Prune** — flood ra mọi nơi, ai không cần thì gửi Prune. **Flood lại mỗi 3 phút** | Đơn giản, không cần RP | ⚠️ **Rất tốn băng thông** | Hầu như **không dùng** |
| ⭐ **PIM-SM**<br>*(Sparse Mode)* | ⭐ **Explicit Join** — chỉ gửi tới nơi **có yêu cầu**. ⭐ **Cần RP** | ⭐ Hiệu quả | Phức tạp hơn (cần RP) | ⭐ **Chuẩn hiện nay** |
| **PIM Sparse-Dense** | Theo từng group: sparse nếu biết RP, dense nếu không | Linh hoạt | ⚠️ Nguy hiểm — group không có RP → dense flood | Legacy |
| ⭐ **PIM-SSM** | ⭐ **KHÔNG cần RP** — host chỉ rõ **(S,G)** qua **IGMPv3** | ⭐ Đơn giản nhất, ⭐ **bảo mật tốt nhất** | Cần IGMPv3 ở host | ⭐ **IPTV, streaming một-nhiều** |
| **Bidirectional PIM** | Cây 2 chiều, ⭐ **không tạo state (S,G)** | Ít state | Không tối ưu đường | Many-to-many (hội nghị) |

#### ⭐⭐ RPF Check — khái niệm cốt lõi nhất của multicast

> ⭐ **RPF (Reverse Path Forwarding) check:** khi router nhận gói multicast, nó hỏi:
> ***"Nếu tôi phải gửi gói UNICAST ngược về SOURCE này, tôi sẽ dùng interface nào?"***
> - Interface đó **=** interface gói vừa đến → ✅ **PASS** → forward
> - Interface đó **≠** interface gói vừa đến → 🔴 **FAIL** → ⭐ **DROP**

```
   Source 10.1.1.1
        │
        ├──── Gi0/0 ────▶ [Router]  ⭐ show ip route 10.1.1.1 → via Gi0/0
        │                              → Gói đến từ Gi0/0 → ✅ PASS
        │
        └──── Gi0/1 ────▶ [Router]  Gói đến từ Gi0/1
                                       nhưng route về source là Gi0/0
                                       → 🔴 RPF FAIL → DROP
```

⭐ **Vì sao cần:** multicast **không có TTL-based loop prevention hiệu quả** như unicast.
RPF check đảm bảo gói **chỉ đi XA source**, không bao giờ đi vòng lại → ⭐ **chống loop**.

```
show ip rpf 10.1.1.1                       ! ⭐ RPF interface cho source đó
show ip mroute count
show ip mroute | include RPF
debug ip mpacket                            ! ⚠️ thấy RPF failed
```

⚠️ **RPF failure hay xảy ra khi:** unicast routing **bất đối xứng** (traffic đi 1 đường, về 1 đường),
hoặc multicast đi qua tunnel mà unicast không.

#### ⭐ Hai loại cây phân phối

| Cây | Ký hiệu | Gốc cây | Đặc điểm |
|---|:---:|---|---|
| ⭐ **Shared Tree (RPT)** | ⭐ **`(*, G)`** | ⭐ **RP** (Rendezvous Point) | Ít state, ⭐ **đường có thể không tối ưu** |
| ⭐ **Source Tree (SPT)** | ⭐ **`(S, G)`** | ⭐ **Source** | ⭐ **Đường ngắn nhất**, nhiều state hơn |

```
   ═══ Ban đầu: SHARED TREE (*, G) ═══        ═══ Sau: SOURCE TREE (S, G) ═══
   
   Source ──▶ RP ──▶ Receiver                 Source ──────────▶ Receiver
              ↑                                        (đường trực tiếp,
        (đi vòng qua RP)                                 bỏ qua RP)
```

⭐ **SPT Switchover:** PIM-SM ban đầu dùng `(*, G)` qua RP, sau đó **tự chuyển sang** `(S, G)`
để đi đường ngắn nhất.

```
ip pim spt-threshold 0            ! ⭐ Cisco mặc định 0 = chuyển NGAY khi thấy gói đầu tiên
ip pim spt-threshold infinity     ! không bao giờ chuyển (luôn dùng shared tree)
```

**Đọc `show ip mroute`:**
```
show ip mroute
```
**Output mẫu:**
```
(*, 239.1.1.1), 00:05:23/stopped, RP 10.99.99.1, flags: SJC
  Incoming interface: GigabitEthernet0/0, RPF nbr 10.0.12.2
  Outgoing interface list:
    GigabitEthernet0/1, Forward/Sparse, 00:05:23/00:02:41

(10.1.1.1, 239.1.1.1), 00:03:12/00:02:47, flags: JT
  Incoming interface: GigabitEthernet0/0, RPF nbr 10.0.12.2
  Outgoing interface list:
    GigabitEthernet0/1, Forward/Sparse, 00:03:12/00:02:47
```
⭐ **Đọc:**
- ⭐ **`(*, 239.1.1.1)`** = shared tree, có `RP 10.99.99.1`
- ⭐ **`(10.1.1.1, 239.1.1.1)`** = source tree — ⭐ đã **SPT switchover**
- ⭐ **`Incoming interface`** = ⭐ **RPF interface** — gói phải đến từ đây
- ⭐ **`Outgoing interface list (OIL)`** = gửi ra đâu. ⭐ **OIL trống = `Null` = không có receiver**
- `flags`: `S`=Sparse · `J`=Join SPT · `C`=Connected receiver · `T`=**SPT bit đã set** · `D`=Dense

#### ⭐ RP Discovery — 3 cách

| Cách | Cơ chế | Ưu / Nhược |
|---|---|---|
| ⭐ **Static RP** | `ip pim rp-address 10.99.99.1` trên **mọi** router | ⭐ Đơn giản nhất · ⚠️ Không tự dự phòng |
| **Auto-RP** *(Cisco)* | Candidate RP → **224.0.1.39** → Mapping Agent → **224.0.1.40** | Tự động · ⚠️ Cisco-only |
| ⭐ **BSR** *(chuẩn, RFC 5059)* | Candidate RP → **BSR** → flood cho mọi router | ⭐ **Chuẩn mở**, đa vendor |
| **Anycast RP** | Nhiều RP cùng IP + MSDP đồng bộ | ⭐ HA cho RP |

#### PIM DR

Trên segment multi-access, ⭐ **PIM DR** gửi Join/Prune về RP thay cho cả segment.

| Bầu PIM DR | So sánh |
|---|---|
| 1 | ⭐ **DR priority CAO nhất** (mặc định 1) |
| 2 | ⭐ **IP CAO nhất** |

🔴 ⭐ **Nhớ ngược với IGMP Querier (IP THẤP nhất)!**

**Cấu hình PIM tối thiểu (tham khảo — không cần thuộc cho ENCOR):**
```
ip multicast-routing                            ! ⭐ bắt buộc, global
!
interface GigabitEthernet0/0
 ip pim sparse-mode                             ! ⭐ trên MỌI interface tham gia
 ip igmp version 3                              ! nếu dùng SSM
!
ip pim rp-address 10.99.99.1                    ! static RP
! hoặc SSM:
ip pim ssm default                              ! dùng dải 232.0.0.0/8
```

**Lệnh verify:**
```
show ip multicast
show ip pim interface
show ip pim neighbor                            ! ⭐ PIM neighbor + DR
show ip pim rp mapping                          ! ⭐ RP nào cho group nào
show ip mroute                                  ! ⭐⭐ cây phân phối
show ip mroute count                            ! ⭐ đếm gói/byte
show ip igmp groups                             ! ⭐ host nào đăng ký group nào
show ip igmp interface
show ip rpf <source>                            ! ⭐ RPF interface
```

---

## 📘 5. 🟡 IPv6 First-Hop Security (bổ trợ — không có trong blueprint ENCOR)

> ℹ️ IPv6 FHS thuộc **ENARSI/SCOR**, không phải ENCOR. Đọc để biết, **không cần luyện**.

| Tính năng | Chống tấn công gì |
|---|---|
| ⭐ **RA Guard** | ⭐ **Rogue Router Advertisement** — kẻ tấn công tự nhận là router IPv6 → MITM |
| ⭐ **DHCPv6 Guard** | Rogue DHCPv6 server |
| ⭐ **IPv6 Snooping / Device Tracking** | Xây **binding table** (IPv6 ↔ MAC ↔ port) — nền cho các tính năng khác |
| **IPv6 Source Guard** | Spoofed source address |
| **IPv6 Destination Guard** | Address scanning / NDP table exhaustion |
| **ND Inspection** | Neighbor Discovery spoofing (tương đương DAI của IPv4) |

⭐ **Tương ứng IPv4 ↔ IPv6:**

| IPv4 | IPv6 |
|---|---|
| DHCP Snooping | ⭐ **DHCPv6 Guard** + IPv6 Snooping |
| Dynamic ARP Inspection (DAI) | ⭐ **ND Inspection** |
| IP Source Guard | ⭐ **IPv6 Source Guard** |
| *(không có)* | ⭐ **RA Guard** — IPv6 có RA nên có nguy cơ riêng |

---

## 📖 6. HIỂU RÕ HƠN

### 6.1 Thứ tự NAT–Routing như thủ tục sân bay

**Đi ra nước ngoài (Inside → Outside):**
1. ⭐ **Kiểm tra vé & định tuyến TRƯỚC** — *"chuyến bay này đi đâu, cửa nào?"* (**ROUTING**)
2. Rồi mới **đổi hộ chiếu** sang hộ chiếu quốc tế (**NAT**)

→ ⭐ **Không có vé (không có route) thì bị chặn ngay ở cửa, chưa kịp đổi hộ chiếu.**
Đó là lý do ⭐ **thiếu default route = NAT vô nghĩa**.

**Từ nước ngoài về (Outside → Inside):**
1. ⭐ **Đổi hộ chiếu TRƯỚC** — quy về danh tính nội địa (**NAT**)
2. Rồi mới **định tuyến** về địa chỉ nhà (**ROUTING**)

→ ⭐ **Hải quan kiểm tra (ACL inbound) xảy ra TRƯỚC khi đổi hộ chiếu**
→ ⭐ **ACL phải dùng IP PUBLIC**, không phải IP private.

🧠 **Một câu để nhớ:** ⭐ ***"Ra: routing trước, NAT sau. Vào: NAT trước, routing sau.
Và ACL luôn chạy TRƯỚC NAT ở chiều vào — nên dùng IP public."***

### 6.2 NAT route-map cho dual-ISP — vì sao NAT thường không đủ

**NAT thường** tạo entry kiểu *"`10.1.10.100` → `203.0.113.1` (IP của ISP1)"* —
⭐ **entry này không ghi nhớ mình đi qua ISP nào**.

ISP1 chết → routing chuyển sang ISP2 → nhưng ⭐ **entry NAT cũ vẫn còn** (timeout 24 giờ!)
→ gói ra ISP2 nhưng **source IP vẫn là IP của ISP1** → ⭐ **ISP2 drop** (không phải IP của họ).

⭐ **NAT route-map** tạo **fully-extended entry** có ghi cả **outside address** →
⭐ **cùng một inside host có thể có 2 entry riêng cho 2 ISP** → chuyển đường là NAT theo đúng ISP.

🧠 **Một câu để nhớ:** *Dual-ISP cần **3 lớp**: routing failover (IP SLA + track),
**NAT failover (route-map)**, và gateway HA (HSRP). ⭐ Thiếu lớp NAT là lỗi phổ biến nhất —
vì routing failover xong mà traffic vẫn chết, rất khó hiểu.*

### 6.3 NTP stratum như tin truyền tai

- **Stratum 0** = ⭐ **người chứng kiến trực tiếp** (đồng hồ nguyên tử, GPS)
- **Stratum 1** = người nghe **trực tiếp** từ nhân chứng
- **Stratum 2** = người nghe từ stratum 1
- ...
- ⭐ **Stratum 16** = ⭐ **"tôi chẳng nghe từ ai cả"** = **không đáng tin, không dùng được**

⭐ Mỗi bước truyền tin thêm một chút **sai số** (`root dispersion`) —
đó là lý do stratum càng thấp càng chính xác.

🧠 **Một câu để nhớ:** ⭐ ***Thấy `stratum 16` là chưa sync. Thấy `*` trước giờ
trong `show clock` là giờ không đáng tin. Hai dấu hiệu đó phải nhận ra trong 1 giây.***

### 6.4 Multicast: unicast đi TỚI đích, multicast đi XA nguồn

| | **Unicast** | ⭐ **Multicast** |
|---|---|---|
| Router hỏi | *"Đích ở đâu?"* → forward **TỚI đích** | ⭐ *"Nguồn ở đâu?"* → forward **XA nguồn** |
| Chống loop | **TTL** giảm dần | ⭐ **RPF check** |
| Bảng | Routing table | ⭐ **mroute table** (`(*,G)` và `(S,G)`) |

⭐ **RPF check ví von:** dòng nước chảy **từ nguồn ra biển**.
Nếu bạn thấy nước chảy **ngược về phía nguồn** → chắc chắn **có vòng lặp** → chặn ngay.

🧠 **Một câu để nhớ:** ⭐ ***Multicast forward "away from source", và RPF check là cách
router kiểm tra "gói này có thật sự đến từ hướng nguồn không". Sai hướng = drop.***

### 6.5 Shared tree vs Source tree — bưu cục trung tâm vs giao trực tiếp

- ⭐ **Shared tree `(*, G)`:** mọi thứ **đi qua bưu cục trung tâm (RP)**.
  Đơn giản (chỉ cần biết địa chỉ bưu cục), ⭐ nhưng **đường có thể đi vòng rất xa**.
- ⭐ **Source tree `(S, G)`:** ⭐ **giao trực tiếp** từ người gửi tới người nhận.
  Đường ngắn nhất, nhưng router phải **nhớ từng cặp (người gửi, nhóm)** → nhiều state hơn.

⭐ **PIM-SM thông minh:** ⭐ **bắt đầu bằng shared tree** (để "làm quen"),
rồi ⭐ **tự chuyển sang source tree** (SPT switchover) khi biết source ở đâu.

🧠 **Một câu để nhớ:** *`(*, G)` = "gửi qua bưu cục". `(S, G)` = "giao tận tay".
⭐ SSM bỏ luôn bưu cục — host nói thẳng **"tôi muốn từ người này"** (IGMPv3),
nên **không cần RP** và **chống được spoofing**.*

---

## 🧪 7. LAB 06B

### 7.1 Chuẩn bị — dùng lại LAB 06A

```
                  ┌──────────────┐
                  │    R-ISP     │  Lo8: 8.8.8.8/32
                  └──┬────────┬──┘  Lo9: 9.9.9.9/32
      203.0.113.0/30 │        │ 198.51.100.0/30
                 Gi0/1│        │Gi0/1
                 ┌───┴──┐  ┌──┴───┐
                 │  R1  │  │  R2  │
                 └───┬──┘  └──┬───┘
                     │  SW1   │
                     └───┬────┘
                    [PC1] 10.1.10.100
                    [SRV] 10.1.10.50 (giả lập web server)
```

⭐ **Thay đổi trên R-ISP:** ⭐ **XÓA route về LAN private** để chứng minh NAT thật sự hoạt động.
```
R-ISP(config)# no ip route 10.1.10.0 255.255.255.0 203.0.113.1
R-ISP(config)# no ip route 10.1.20.0 255.255.255.0 198.51.100.1
```
⭐ Giờ R-ISP **không biết** mạng `10.1.10.0/24` → nếu PC1 ping được `8.8.8.8`
thì **chắc chắn là nhờ NAT**.

⭐ **Thêm SRV (giả lập web server)** — dùng VPCS thứ 2 hoặc 1 vIOS nhẹ:
```
! Nếu dùng VPCS:
SRV> ip 10.1.10.50/24 10.1.10.1
SRV> save
```

---

### Bước 1 — ⭐ PAT overload + chứng minh thứ tự NAT-Routing

#### 1a) Cấu hình PAT trên R1

```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  ip nat inside
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  ip nat inside
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip nat outside
R1(config-if)# exit
!
R1(config)# ip access-list standard ACL-NAT
R1(config-std-nacl)#  permit 10.1.10.0 0.0.0.255
R1(config-std-nacl)#  permit 10.1.20.0 0.0.0.255
R1(config-std-nacl)# exit
!
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
```

**Làm tương tự trên R2** (uplink `Gi0/1` = `198.51.100.1`).

#### 1b) Test & đọc bảng NAT

```
PC1> ping 8.8.8.8
! ✅ thành công (dù R-ISP KHÔNG có route về 10.1.10.0/24)
```
```
R1# show ip nat translations
```
**Output mẫu:**
```
Pro  Inside global      Inside local       Outside local      Outside global
icmp 203.0.113.1:7      10.1.10.100:7      8.8.8.8:7          8.8.8.8:7
```

⭐ **Điền bảng 4 thuật ngữ từ output này:**

| Thuật ngữ | Giá trị | Nghĩa |
|---|---|---|
| Inside Local | | |
| Inside Global | | |
| Outside Local | | |
| Outside Global | | |

<details><summary>Đáp án</summary>

| Thuật ngữ | Giá trị | Nghĩa |
|---|---|---|
| ⭐ **Inside Local** | `10.1.10.100` | IP **thật** của PC1 |
| ⭐ **Inside Global** | `203.0.113.1` | PC1 **hóa trang thành** IP này (= IP interface outside của R1) |
| **Outside Local** | `8.8.8.8` | Đích, nhìn từ nội bộ |
| **Outside Global** | `8.8.8.8` | Đích, nhìn từ ngoài (giống Outside Local vì không dùng `ip nat outside source`) |
</details>

```
R1# show ip nat statistics
```
**Output mẫu:**
```
Total active translations: 1 (0 static, 1 dynamic; 1 extended)
Peak translations: 3, occurred 00:02:11 ago
Outside interfaces:
  GigabitEthernet0/1
Inside interfaces:
  GigabitEthernet0/0.10, GigabitEthernet0/0.20
Hits: 24  Misses: 0
CEF Translated packets: 24, CEF Punted packets: 6
Expired translations: 2
Dynamic mappings:
-- Inside Source
[Id: 1] access-list ACL-NAT interface GigabitEthernet0/1 refcount 1
```
⭐ `Hits` tăng = NAT hoạt động · ⚠️ `Misses` cao = có traffic khớp ACL nhưng không NAT được.

**⭐ Chứng minh NAT thật sự cần thiết:**
```
R-ISP# ping 10.1.10.100
! ❌ FAIL — R-ISP không có route về mạng private
```
⭐ **PC1 ra được nhờ NAT, không phải nhờ routing.**

#### 1c) ⭐⭐ CHỨNG MINH: thiếu default route → NAT vô nghĩa

```
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.2
```
```
PC1> ping 8.8.8.8
! ❌ FAIL 100%
R1# show ip nat translations
! → TRỐNG (không có entry nào được tạo)
R1# show ip nat statistics | include Misses
! Hits: 24  Misses: 0                          ← Misses KHÔNG tăng
```

⭐⭐ **Bài học:** NAT **không được gọi tới** — vì ⭐ **routing xảy ra TRƯỚC NAT**
ở chiều inside→outside. Không có route → gói bị **drop trước khi NAT kịp làm gì**.

**Bật lại:**
```
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

#### 1d) 🧪 Bắt gói 2 bên NAT để nhìn thấy dịch địa chỉ

1. EVE-NG: **Capture** link `R1 Gi0/0` (inside) → Wireshark, filter `icmp`
2. EVE-NG: **Capture** link `R1 Gi0/1` (outside) → Wireshark, filter `icmp`
3. PC1 ping `8.8.8.8`

⭐ **Kết quả:**

| Bắt ở | Source IP | Nghĩa |
|---|---|---|
| **Inside** (`Gi0/0`) | `10.1.10.100` | ⭐ **Inside Local** |
| **Outside** (`Gi0/1`) | `203.0.113.1` | ⭐ **Inside Global** |

⭐ **Nhìn thấy NAT bằng mắt.** Đừng bỏ bước này.

✅ **Checkpoint bước 1:**

| Kiểm tra | Mong đợi |
|---|---|
| PC1 ping `8.8.8.8` OK dù R-ISP không có route về LAN | ⭐ ✅ |
| `show ip nat translations` có entry, đọc đúng 4 thuật ngữ | ⭐ ✅ |
| ⭐ Xóa default route → NAT **không tạo entry**, ping fail | ⭐⭐ ✅ |
| Bắt gói 2 bên → source IP **khác nhau** | ⭐ ✅ |

---

### Bước 2 — ⭐⭐ Static PAT (port forwarding) + bẫy ACL

#### 2a) Publish web server nội bộ

```
! ⭐ Port forward: Internet:80 → 10.1.10.50:80
R1(config)# ip nat inside source static tcp 10.1.10.50 80 interface GigabitEthernet0/1 80

! Publish thêm SSH qua port khác
R1(config)# ip nat inside source static tcp 10.1.10.50 22 interface GigabitEthernet0/1 2222
```

```
R1# show ip nat translations
```
**Output mẫu:**
```
Pro  Inside global         Inside local       Outside local      Outside global
tcp  203.0.113.1:80        10.1.10.50:80      ---                ---
tcp  203.0.113.1:2222      10.1.10.50:22      ---                ---
```
⭐ Static entry hiện **ngay lập tức** (không cần traffic) và **`---`** ở 2 cột outside
= **chờ kết nối từ bất kỳ ai**.

#### 2b) Test từ "Internet"

> 💡 VPCS không mở port TCP. Dùng **vIOS làm SRV** để test thật:
> trên SRV bật `ip http server`, rồi từ R-ISP `telnet 203.0.113.1 80`.

**Nếu SRV là vIOS:**
```
SRV(config)# ip http server
SRV(config)# interface Gi0/0
SRV(config-if)#  ip address 10.1.10.50 255.255.255.0
SRV(config)# ip route 0.0.0.0 0.0.0.0 10.1.10.1
```
```
R-ISP# telnet 203.0.113.1 80
Trying 203.0.113.1, 80 ... Open              ← ⭐ ✅ Port forward hoạt động
```
```
R1# show ip nat translations | include :80
tcp  203.0.113.1:80   10.1.10.50:80   203.0.113.2:38412   203.0.113.2:38412
```
⭐ Giờ 2 cột outside đã có giá trị (kết nối thật).

#### 2c) 🔴⭐⭐ BẪY ACL — dùng IP private là SAI

```
! ❌ SAI — ACL dùng IP PRIVATE
R1(config)# ip access-list extended ACL-OUT-IN
R1(config-ext-nacl)#  permit tcp any host 10.1.10.50 eq 80
R1(config-ext-nacl)#  permit icmp any any
R1(config-ext-nacl)#  deny   ip any any log
R1(config-ext-nacl)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  ip access-group ACL-OUT-IN in
```
```
R-ISP# telnet 203.0.113.1 80
! ❌ FAIL — Connection refused / timeout
```
```
R1# show access-lists ACL-OUT-IN
Extended IP access list ACL-OUT-IN
    10 permit tcp any host 10.1.10.50 eq www (0 matches)      ← ⭐ 0 MATCHES!
    20 permit icmp any any (5 matches)
    30 deny ip any any log (3 matches)                         ← ⭐ bị chặn ở đây
```

⭐⭐ **`0 matches` ở dòng permit** — ACL **không khớp** vì ở chiều **outside→inside**,
⭐ **ACL inbound chạy TRƯỚC NAT** → lúc đó gói vẫn có destination = **`203.0.113.1` (IP public)**,
chưa phải `10.1.10.50`.

```
! ✅ ĐÚNG — ACL dùng IP PUBLIC (Inside Global)
R1(config)# no ip access-list extended ACL-OUT-IN
R1(config)# ip access-list extended ACL-OUT-IN
R1(config-ext-nacl)#  permit tcp any host 203.0.113.1 eq 80       ! ⭐ IP PUBLIC
R1(config-ext-nacl)#  permit tcp any host 203.0.113.1 eq 2222
R1(config-ext-nacl)#  permit icmp any any
R1(config-ext-nacl)#  deny   ip any any log
```
```
R-ISP# telnet 203.0.113.1 80
Trying 203.0.113.1, 80 ... Open              ← ⭐ ✅ HOẠT ĐỘNG
R1# show access-lists ACL-OUT-IN
    10 permit tcp any host 203.0.113.1 eq www (2 matches)         ← ⭐ CÓ MATCH
```

> ⭐⭐ **Ghi vào `SO-TAY-LOI.md`:** ⭐ **ACL inbound trên interface OUTSIDE
> phải dùng IP PUBLIC (Inside Global)**, vì ACL chạy **TRƯỚC** NAT ở chiều outside→inside.

**Dọn dẹp:**
```
R1(config)# interface GigabitEthernet0/1
R1(config-if)#  no ip access-group ACL-OUT-IN in
```

✅ **Checkpoint bước 2:**

| Kiểm tra | Mong đợi |
|---|---|
| Static PAT entry hiện **ngay** trong `show ip nat translations` với `---` | ✅ |
| Từ "Internet" telnet vào port 80 → thành công | ✅ |
| ⭐⭐ ACL dùng **IP private** → `0 matches`, bị chặn | ⭐⭐ ✅ |
| ⭐ ACL dùng **IP public** → có match, hoạt động | ⭐ ✅ |

---

### Bước 3 — ⭐ Dynamic NAT với pool (và test cạn pool)

```
R1(config)# no ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
!
R1(config)# ip nat pool POOL-SMALL 203.0.113.10 203.0.113.11 netmask 255.255.255.252
R1(config)# ip nat inside source list ACL-NAT pool POOL-SMALL       ! ⚠️ KHÔNG có overload
```
> ⚠️ Pool chỉ có **2 IP** và **không overload** → chỉ 2 host NAT được cùng lúc.
> R-ISP cần route về pool: `ip route 203.0.113.8 255.255.255.248 203.0.113.1`

```
R-ISP(config)# ip route 203.0.113.8 255.255.255.248 203.0.113.1
```

**Test:**
```
PC1> ping 8.8.8.8            ! ✅ dùng 203.0.113.10
SRV> ping 8.8.8.8            ! ✅ dùng 203.0.113.11
! Host thứ 3 (nếu có) → ❌ FAIL
```
```
R1# show ip nat translations
Pro  Inside global      Inside local       Outside local      Outside global
---  203.0.113.10       10.1.10.100        ---                ---
---  203.0.113.11       10.1.10.50         ---                ---
R1# show ip nat statistics | include Misses|pool
! Hits: 40  Misses: 6                       ← ⭐ Misses TĂNG = có host không NAT được
R1# show logging | include NAT
%NAT-4-ADDR_ALLOC_FAILURE: Address allocation failed; pool POOL-SMALL may be exhausted
```
⭐⭐ **`Misses` tăng + log `ADDR_ALLOC_FAILURE`** = ⭐ **pool cạn**.
Đây là dấu hiệu nhận diện Dynamic NAT hết IP.

**⭐ Thêm `overload` → thành PAT với pool:**
```
R1(config)# no ip nat inside source list ACL-NAT pool POOL-SMALL
R1(config)# ip nat inside source list ACL-NAT pool POOL-SMALL overload
R1# clear ip nat translation *
```
→ Giờ **nhiều host chung 1 IP + port** → không còn cạn pool.

**Trả về PAT interface (đơn giản nhất):**
```
R1(config)# no ip nat inside source list ACL-NAT pool POOL-SMALL overload
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
R1# clear ip nat translation *
```

---

### Bước 4 — ⭐⭐ NAT route-map cho dual-ISP

#### 4a) Cấu hình R1 với 2 uplink

> 💡 Trong lab này R1 chỉ có 1 uplink tới R-ISP. Để mô phỏng dual-ISP,
> thêm `R1 Gi0/2` ↔ `R-ISP Gi0/3` với dải `192.0.2.0/30`.

```
! ═══ R-ISP ═══
R-ISP(config)# interface GigabitEthernet0/3
R-ISP(config-if)#  description ---> To R1 ISP2
R-ISP(config-if)#  ip address 192.0.2.2 255.255.255.252
R-ISP(config-if)#  no shutdown

! ═══ R1 ═══
R1(config)# interface GigabitEthernet0/2
R1(config-if)#  description ---> UPLINK ISP2
R1(config-if)#  ip address 192.0.2.1 255.255.255.252
R1(config-if)#  ip nat outside                             ! ⭐ cũng là outside
R1(config-if)#  no shutdown
```

#### 4b) Routing failover (Module-03) + NAT route-map

```
! ═══ IP SLA + track cho ISP1 ═══
R1(config)# ip sla 1
R1(config-ip-sla)#  icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R1(config-ip-sla-echo)#  frequency 5
R1(config-ip-sla-echo)# exit
R1(config)# ip sla schedule 1 life forever start-time now
R1(config)# track 1 ip sla 1 reachability
R1(config-track)#  delay down 3 up 10
R1(config-track)# exit
!
! ═══ Floating static ═══
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.2
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2 track 1        ! ISP1, AD 1
R1(config)# ip route 0.0.0.0 0.0.0.0 192.0.2.2 200              ! ISP2, AD 200
!
! ═══ ⭐ NAT ROUTE-MAP ═══
R1(config)# no ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
!
R1(config)# route-map RM-NAT-ISP1 permit 10
R1(config-route-map)#  match ip address ACL-NAT
R1(config-route-map)#  match interface GigabitEthernet0/1       ! ⭐ ISP1
R1(config-route-map)# exit
R1(config)# route-map RM-NAT-ISP2 permit 10
R1(config-route-map)#  match ip address ACL-NAT
R1(config-route-map)#  match interface GigabitEthernet0/2       ! ⭐ ISP2
R1(config-route-map)# exit
!
R1(config)# ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
R1(config)# ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
```

#### 4c) Test failover NAT

```
! Bình thường
PC1> ping 8.8.8.8            ! ✅
R1# show ip nat translations
! icmp 203.0.113.1:8   10.1.10.100:8   8.8.8.8:8   8.8.8.8:8      ← ⭐ IP của ISP1
R1# show ip route 0.0.0.0
! * 203.0.113.2                                                     ← ISP1
```

```
! ⭐ Cắt ISP1 (mô phỏng: shutdown Lo8 trên R-ISP để IP SLA fail)
R-ISP(config)# interface GigabitEthernet0/1
R-ISP(config-if)# shutdown
```
Chờ ~10 giây:
```
R1# show track 1
!   Reachability is Down
R1# show ip route 0.0.0.0
! * 192.0.2.2                                                       ← ⭐ ĐÃ CHUYỂN ISP2
!
! ⭐ Clear NAT để entry cũ không giữ traffic
R1# clear ip nat translation *
```
```
PC1> ping 8.8.8.8            ! ✅ hoạt động lại
R1# show ip nat translations
! icmp 192.0.2.1:9   10.1.10.100:9   8.8.8.8:9   8.8.8.8:9         ← ⭐ IP của ISP2!
```
⭐⭐ **NAT đã tự dùng IP của ISP2** — nhờ `match interface` trong route-map.

**⚠️ Test không clear NAT:**
```
R-ISP(config-if)# no shutdown       ! bật lại ISP1
! chờ track Up, route về ISP1
PC1> ping 8.8.8.8
```
→ Nếu entry cũ (IP ISP2) còn, gói ra ISP1 với source IP của ISP2 → có thể fail
cho tới khi entry hết hạn.

⭐ **Giải pháp production — dùng EEM tự động clear NAT khi track đổi trạng thái** (Module-12):
```
event manager applet CLEAR-NAT-ON-FAILOVER
 event track 1 state any
 action 1.0 cli command "enable"
 action 2.0 cli command "clear ip nat translation *"
 action 3.0 syslog msg "NAT translations cleared due to track 1 state change"
```

✅ **Checkpoint bước 4:**

| Kiểm tra | Mong đợi |
|---|---|
| Bình thường: NAT dùng **IP của ISP1** | ✅ |
| Cắt ISP1 → track `Down` → route chuyển ISP2 | ✅ |
| ⭐ Sau `clear ip nat translation *` → NAT dùng **IP của ISP2** | ⭐⭐ ✅ |
| Hiểu vì sao cần route-map (fully-extended entry) thay vì NAT thường | ⭐ ✅ |

**Dọn dẹp (giữ lại nếu muốn):**
```
R1(config)# no ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
R1(config)# no ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
R1(config)# ip nat inside source list ACL-NAT interface GigabitEthernet0/1 overload
R1# clear ip nat translation *
```

---

### Bước 5 — ⭐ NTP với authentication

#### 5a) R-ISP làm NTP master (giả lập NTP server công cộng)

```
R-ISP(config)# clock timezone UTC 0
R-ISP(config)# clock set 10:00:00 Sep 9 2026
R-ISP(config)# ntp master 3                              ! ⭐ stratum 3
R-ISP(config)# ntp authenticate
R-ISP(config)# ntp authentication-key 1 md5 NtpS3cret2026
R-ISP(config)# ntp trusted-key 1
```
```
R-ISP# show ntp status
! Clock is synchronized, stratum 3, reference is 127.127.1.1
```
⭐ `reference is 127.127.1.1` = **đồng hồ nội bộ của chính router** (khi làm `ntp master`).

#### 5b) R1, R2 làm NTP client

```
! ═══ R1 ═══
R1(config)# clock timezone ICT 7                          ! ⭐ Việt Nam UTC+7
R1(config)# ntp authenticate
R1(config)# ntp authentication-key 1 md5 NtpS3cret2026
R1(config)# ntp trusted-key 1
R1(config)# ntp server 203.0.113.2 key 1 prefer
R1(config)# ntp source GigabitEthernet0/1
R1(config)# ntp update-calendar
!
! ⭐ Bật timestamp cho log (rất quan trọng — Module-11)
R1(config)# service timestamps log datetime msec localtime show-timezone
R1(config)# service timestamps debug datetime msec localtime show-timezone
```
Làm tương tự R2 (`ntp server 198.51.100.2 key 1`).

#### 5c) Verify (chờ 1–3 phút để đồng bộ)

```
R1# show ntp status
```
**Output mẫu:**
```
Clock is synchronized, stratum 4, reference is 203.0.113.2
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**10
reference time is E8F3A2B1.7C3D4E5F (17:15:32.485 ICT Mon Sep 9 2026)
clock offset is 0.5432 msec, root delay is 3.21 msec
root dispersion is 12.34 msec, peer dispersion is 0.98 msec
system poll interval is 64, last update was 45 sec ago.
```
✅ ⭐ `Clock is synchronized` · ⭐ `stratum 4` (= master 3 + 1) · `reference is 203.0.113.2`

```
R1# show ntp associations
```
**Output mẫu:**
```
  address         ref clock       st   when   poll reach  delay  offset   disp
*~203.0.113.2    127.127.1.1      3     45     64   377   3.210   0.543  0.980
 * sys.peer, # selected, + candidate, - outlier, x falseticker, ~ configured
```
⭐ ⭐ **`*`** trước địa chỉ = ⭐ **sys.peer** (đang thực sự dùng) · ⭐ **`reach 377`** = 8/8 poll OK

```
R1# show clock detail
```
**Output mẫu:**
```
17:20:15.485 ICT Mon Sep 9 2026
Time source is NTP                              ← ⭐ nguồn là NTP
```
⭐ **Không có dấu `*`** trước giờ = ⭐ **thời gian đáng tin**.

#### 5d) ⚠️ Tái hiện 3 lỗi NTP

**Lỗi 1 — key lệch:**
```
R1(config)# ntp authentication-key 1 md5 WrongKey
R1# clear ntp ?               ! (không có lệnh clear ntp — chờ hoặc no ntp server rồi thêm lại)
R1(config)# no ntp server 203.0.113.2
R1(config)# ntp server 203.0.113.2 key 1 prefer
```
Chờ 1–2 phút:
```
R1# show ntp associations
!  ~203.0.113.2    0.0.0.0         16     -      64     0   0.000   0.000 16000.
!  ↑ KHÔNG có dấu * · st = 16 · reach = 0
R1# show ntp status
! Clock is unsynchronized, stratum 16, no reference clock       ← ⭐ STRATUM 16!
```
⭐⭐ **`stratum 16` + `reach 0` + không có `*`** = **không đồng bộ được**.

**Sửa:**
```
R1(config)# ntp authentication-key 1 md5 NtpS3cret2026
```

**Lỗi 2 — thiếu `ntp trusted-key`:**
```
R1(config)# no ntp trusted-key 1
```
→ Cùng triệu chứng: `stratum 16`, `reach 0`. ⭐ **Phải có CẢ BA:**
`ntp authenticate` + `ntp authentication-key` + `ntp trusted-key`.

**Sửa:** `ntp trusted-key 1`

**Lỗi 3 — chưa bao giờ sync:**
```
R2(config)# no ntp server 198.51.100.2
R2# show clock
! *17:25:30.123 ICT Mon Sep 9 2026        ← ⭐ DẤU * = giờ KHÔNG đáng tin
R2# show clock detail
! *17:25:30.123 ICT Mon Sep 9 2026
! Time source is user configuration        ← đặt tay, sẽ drift
```
⭐ **Dấu `*` trước giờ** là dấu hiệu nhận diện nhanh nhất.

**Sửa:** `ntp server 198.51.100.2 key 1`

#### 5e) ⭐ NTP access-group (chống NTP amplification)

```
R1(config)# ip access-list standard ACL-NTP-PEER
R1(config-std-nacl)#  permit 203.0.113.2
R1(config-std-nacl)# exit
R1(config)# ip access-list standard ACL-NTP-SERVE
R1(config-std-nacl)#  permit 10.0.0.0 0.255.255.255
R1(config-std-nacl)# exit
R1(config)# ntp access-group peer ACL-NTP-PEER
R1(config)# ntp access-group serve-only ACL-NTP-SERVE
```
⭐ Giờ R1 chỉ sync với `203.0.113.2`, và chỉ trả lời giờ cho mạng `10.0.0.0/8`.

✅ **Checkpoint bước 5:**

| Kiểm tra | Mong đợi |
|---|---|
| `show ntp status` → `Clock is synchronized, stratum 4` | ✅ |
| `show ntp associations` → có ⭐ **`*`** và ⭐ **`reach 377`** | ⭐ ✅ |
| `show clock detail` → `Time source is NTP`, **không có dấu `*`** | ⭐ ✅ |
| ⭐ Tái hiện key lệch → `stratum 16`, `reach 0`, không có `*` | ⭐⭐ ✅ |
| Hiểu phải có **cả 3** lệnh auth | ⭐ ✅ |
| Log có timestamp đầy đủ (`service timestamps log datetime msec localtime`) | ✅ |

---

### Bước 6 — 🚀 PIM-SM cơ bản (TÙY CHỌN — blueprint chỉ "describe")

> ⭐ **Bỏ qua bước này nếu bạn đang bám tiến độ.** Đề chỉ hỏi khái niệm.
> Làm nếu bạn muốn **thấy** `(*,G)` và `(S,G)` bằng mắt.

```
! ═══ Trên R1, R2, R-ISP ═══
ip multicast-routing
!
interface <mọi interface tham gia>
 ip pim sparse-mode
 ip igmp version 2
!
! ⭐ R-ISP làm RP
R-ISP(config)# interface Loopback99
R-ISP(config-if)#  ip address 10.99.99.1 255.255.255.255
R-ISP(config-if)#  ip pim sparse-mode
R-ISP(config)# ip pim rp-address 10.99.99.1
!
! ⭐ Trên MỌI router: khai RP (static)
R1(config)# ip pim rp-address 10.99.99.1
R2(config)# ip pim rp-address 10.99.99.1
! Và cần route tới 10.99.99.1 trên R1/R2
R1(config)# ip route 10.99.99.1 255.255.255.255 203.0.113.2
```

**Mô phỏng receiver — cho interface join group:**
```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  ip igmp join-group 239.1.1.1
```

**Mô phỏng source — ping multicast từ R-ISP:**
```
R-ISP# ping 239.1.1.1 repeat 10 source Loopback8
```

**Verify:**
```
R1# show ip pim neighbor
R1# show ip pim rp mapping
R1# show ip igmp groups
R1# show ip mroute
```
**Output mẫu `show ip mroute`:**
```
(*, 239.1.1.1), 00:02:15/stopped, RP 10.99.99.1, flags: SJCL
  Incoming interface: GigabitEthernet0/1, RPF nbr 203.0.113.2
  Outgoing interface list:
    GigabitEthernet0/0.10, Forward/Sparse, 00:02:15/00:02:44

(8.8.8.8, 239.1.1.1), 00:00:12/00:02:47, flags: LJT
  Incoming interface: GigabitEthernet0/1, RPF nbr 203.0.113.2
  Outgoing interface list:
    GigabitEthernet0/0.10, Forward/Sparse, 00:00:12/00:02:47
```
⭐ **Nhìn thấy cả `(*, G)` và `(S, G)`** — và flag `T` = đã **SPT switchover**.

```
R1# show ip rpf 8.8.8.8
! RPF information for ? (8.8.8.8)
!   RPF interface: GigabitEthernet0/1
!   RPF neighbor: ? (203.0.113.2)
!   RPF route/mask: 0.0.0.0/0
!   RPF type: unicast (static)
```
⭐ **Đây là RPF check** — router dùng bảng **unicast** để xác định interface hợp lệ cho multicast.

✅ **Checkpoint bước 6 (tùy chọn):** thấy được `(*,G)` với `RP`, `(S,G)` với flag `T`,
và `show ip rpf` chỉ ra RPF interface.

---

## 💡 8. THỰC CHIẾN ĐI LÀM

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| 🔴⭐ **Thứ tự NAT-Routing** | Bẫy đề | 🔴 Hai lỗi thật: (1) **thiếu default route** → NAT không được gọi · (2) ⭐ **ACL inbound trên outside interface dùng IP private** → port forward không hoạt động. Cả hai đều "config trông đúng" |
| ⭐ **ACL với NAT** | Ít nhắc | ⭐ Quy tắc: interface **inside** → dùng IP **private** · interface **outside** → dùng IP **public**. Vì ACL luôn chạy **trước** NAT ở chiều vào |
| 🔴⭐ **Dual-ISP NAT** | Không dạy | 🔴 ⭐ **NAT thường KHÔNG failover được.** Phải dùng **NAT route-map với `match interface`**. Đây là lỗi thiết kế dual-ISP phổ biến nhất — routing failover xong mà traffic vẫn chết |
| ⭐ **3 lớp dual-ISP** | Không dạy | ⭐ (1) Routing: **IP SLA + track** (M03) · (2) NAT: **route-map** (đây) · (3) Gateway: **HSRP + tracking** (M06A). Thiếu lớp nào cũng không hoạt động |
| ⭐ **`clear ip nat translation`** | Có lệnh | ⭐ Sau failover **phải clear** để entry cũ không giữ traffic. ⭐ Tự động bằng **EEM** trigger theo `event track` (Module-12) |
| ⭐ **`max-entries`** | Không dạy | ⭐ **BẮT BUỘC ở production.** 1 PC nhiễm malware tạo hàng chục nghìn entry → router hết RAM. Đặt `max-entries host <ip> 100` |
| **NAT timeout** | Mặc định 24h | ⭐ Giảm `tcp-timeout` xuống 3600 và `udp-timeout` 60 ở mạng nhiều session để giải phóng entry nhanh |
| ⭐ **Static NAT vs Static PAT** | Cả hai | ⭐ Ưu tiên **Static PAT** (port forward) — tiết kiệm IP public và **giảm bề mặt tấn công** (chỉ mở đúng port cần) |
| ⚠️ **Dynamic NAT** | Có trong sách | ⚠️ Gần như **không dùng** — tốn IP public, và cạn pool thì drop âm thầm. Luôn thêm `overload` |
| 🔴⭐ **NTP** | "Describe" | 🔴 ⭐ **Không có NTP thì log vô giá trị.** Đây là việc **đầu tiên** phải làm khi triển khai thiết bị mới — trước cả cấu hình routing |
| ⭐ **`service timestamps`** | Không nhắc | ⭐ Bắt buộc: `service timestamps log datetime msec localtime show-timezone`. Mặc định IOS chỉ có uptime — ⭐ **vô dụng để tương quan sự cố** |
| ⭐ **NTP auth** | Có lệnh | ⭐ Cần **cả 3 lệnh**: `ntp authenticate` + `ntp authentication-key` + `ntp trusted-key`. Thiếu 1 = không sync, và triệu chứng giống hệt key sai |
| ⭐ **`ntp access-group serve-only`** | Không nhắc | ⭐ Chống **NTP amplification DDoS** — router của bạn bị lợi dụng làm bộ khuếch đại. Đây là loại tấn công thật, đã gây sự cố lớn |
| ⭐ **`ntp source`** | Có lệnh | ⭐ Dùng loopback → IP nguồn cố định → dễ viết ACL trên NTP server |
| ⭐ **Kiến trúc NTP** | Không dạy | ⭐ Chuẩn: 2–3 router core làm **NTP server nội bộ** (sync với NTP công cộng hoặc GPS), mọi thiết bị khác sync với chúng. **Không** để 500 thiết bị đi ra Internet |
| ⭐ **`show clock` dấu `*`** | Không nhắc | ⭐ Dấu `*` = **giờ không đáng tin**. Nhìn thấy nó trên thiết bị production = có vấn đề NTP |
| 🟡 **Multicast** | "Describe" | ⭐ Thực tế gặp ở: **IPTV**, **video conference**, **stock market feed**, **PXE boot**, **wake-on-LAN**, **Windows deployment (WDS)**. Và ⭐ **IGMP snooping** — nếu tắt thì video multicast **flood cả VLAN** |
| ⭐ **IGMP snooping querier** | Không dạy | ⭐ VLAN **không có router multicast** → không có querier → snooping không học được → **flood**. Sửa: `ip igmp snooping vlan X querier` |
| ⭐ **RPF failure** | Khái niệm | ⭐ Nguyên nhân thật: **routing bất đối xứng**, multicast qua tunnel mà unicast không, hoặc thiếu route tới source. Chẩn đoán: `show ip rpf <source>` |
| ⭐ **PIM-SSM** | Có trong sách | ⭐ Xu hướng hiện nay cho **one-to-many** (IPTV): không cần RP, không cần MSDP, ⭐ **chống spoofing tốt nhất**. Nếu thiết kế mới → cân nhắc SSM |
| ⭐ **Địa chỉ multicast** | Bảng | ⭐ Dùng **`239.x.x.x`** cho nội bộ (như RFC1918). Và ⭐ **quy hoạch tránh 32:1 overlap** — đừng chọn địa chỉ có 23 bit thấp trùng nhau |

---

## 🎓 9. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | 🔴⭐ **Thứ tự NAT-Routing (inside→outside)** | ⭐ **ROUTING TRƯỚC, NAT SAU** → thiếu route = NAT không được gọi |
| 2 | 🔴⭐ **Thứ tự (outside→inside)** | ⭐ **NAT TRƯỚC, ROUTING SAU** |
| 3 | ⭐ ACL inbound trên interface **outside** dùng IP nào | ⭐ **IP PUBLIC (Inside Global)** — vì ACL chạy trước NAT |
| 4 | ⭐ ACL inbound trên interface **inside** dùng IP nào | ⭐ **IP PRIVATE (Inside Local)** |
| 5 | ⭐ 4 thuật ngữ NAT | ⭐ **Inside Local** (IP thật nội bộ) · **Inside Global** (sau NAT) · **Outside Global** (IP thật bên ngoài) · **Outside Local** |
| 6 | Khi nào Outside Local ≠ Outside Global | Khi dùng ⭐ **`ip nat outside source`** (2 mạng trùng IP) |
| 7 | ⭐ `overload` nghĩa là gì | ⭐ **PAT** — nhiều IP private → 1 IP public, phân biệt bằng **port** |
| 8 | Dynamic NAT cạn pool | ⭐ Host mới **bị drop**. Log `%NAT-4-ADDR_ALLOC_FAILURE`, `Misses` tăng |
| 9 | 🔴⭐ NAT thường có failover dual-ISP không | ❌ ⭐ **KHÔNG.** Phải dùng ⭐ **NAT route-map với `match interface`** |
| 10 | ⭐ `extendable` để làm gì | Cho phép cùng Inside Local có nhiều Inside Global (dual-ISP static NAT) |
| 11 | ⭐ **NAT64** vs **NPTv6** | ⭐ NAT64 = dịch **IPv6↔IPv4** (prefix `64:FF9B::/96`, cần **DNS64**) · ⭐ NPTv6 = dịch **prefix IPv6↔IPv6**, **1:1 stateless, không đổi port** |
| 12 | ⭐ NTP port | ⭐ **UDP 123** |
| 13 | ⭐ Stratum hợp lệ | ⭐ **1–15**. ⭐ **16 = KHÔNG ĐỒNG BỘ** |
| 14 | Stratum 0 là gì | ⭐ **Reference clock** (nguyên tử/GPS) — **không phải** thiết bị mạng |
| 15 | ⭐ 3 lệnh bắt buộc cho NTP auth | ⭐ `ntp authenticate` + `ntp authentication-key <n> md5 <key>` + `ntp trusted-key <n>` |
| 16 | ⭐ `*` trong `show ntp associations` | ⭐ **sys.peer** — server đang **thực sự** được dùng |
| 17 | ⭐ `x` trong `show ntp associations` | ⭐ **Falseticker** — server báo giờ **SAI** |
| 18 | ⭐ `reach 377` nghĩa là gì | ⭐ Số **bát phân** = `11111111` = **8/8 poll gần nhất OK** |
| 19 | ⭐ Dấu `*` trước giờ trong `show clock` | ⭐ **Thời gian KHÔNG đáng tin** (chưa sync) |
| 20 | `ntp master <stratum>` làm gì | Router **tự làm nguồn thời gian** (mặc định stratum 8) |
| 21 | ⭐ `ntp server` vs `ntp peer` | `server` = **một chiều** (tôi sync theo nó) · `peer` = **hai chiều** |
| 22 | SNTP khác NTP thế nào | ⭐ SNTP **chỉ làm client**, thuật toán đơn giản, **kém chính xác** hơn |
| 23 | ⭐ Dải multicast | ⭐ **224.0.0.0/4** (224.0.0.0 – 239.255.255.255) |
| 24 | ⭐ 224.0.0.0/24 đặc biệt gì | ⭐ **Link-local, TTL = 1, KHÔNG được route** |
| 25 | ⭐ 232.0.0.0/8 và 239.0.0.0/8 | ⭐ **232/8 = SSM** · ⭐ **239/8 = administratively scoped ("private")** |
| 26 | ⭐ Multicast MAC prefix | ⭐ **`01:00:5E`** + 0 + **23 bit thấp** của IP |
| 27 | ⭐ Tỉ lệ overlap IP→MAC | ⭐ **32:1** (28 bit group − 23 bit MAC = 5 bit mất → 2^5 = 32) |
| 28 | ⭐ IGMPv2 thêm gì so với v1 | ⭐ **Leave Group message** + **Querier election** + Group-Specific Query |
| 29 | ⭐ IGMPv3 thêm gì | ⭐ **Source filtering (INCLUDE/EXCLUDE)** → ⭐ **bắt buộc cho SSM**. Report tới **224.0.0.22** |
| 30 | 🔴⭐ **IGMP Querier election** | ⭐ **IP THẤP NHẤT thắng** |
| 31 | 🔴⭐ **PIM DR election** | ⭐ **Priority cao → IP CAO NHẤT thắng** — ⭐ **NGƯỢC với IGMP Querier!** |
| 32 | ⭐ PIM-DM cơ chế | ⭐ **Flood-and-Prune**, flood lại mỗi **3 phút**. Tốn băng thông |
| 33 | ⭐ PIM-SM cơ chế | ⭐ **Explicit Join**, ⭐ **cần RP** |
| 34 | ⭐ PIM-SSM cơ chế | ⭐ **KHÔNG cần RP**, dùng **(S,G)** trực tiếp, ⭐ **cần IGMPv3** |
| 35 | ⭐⭐ **RPF check là gì** | ⭐ *"Interface tôi dùng để **route UNICAST về source** có phải là interface gói vừa đến?"* Không → ⭐ **DROP**. Đây là cơ chế **chống loop** của multicast |
| 36 | ⭐ `(*, G)` vs `(S, G)` | ⭐ `(*,G)` = **shared tree**, gốc là **RP** · ⭐ `(S,G)` = **source tree (SPT)**, gốc là **source**, đường ngắn nhất |
| 37 | ⭐ SPT switchover | ⭐ PIM-SM chuyển từ `(*,G)` sang `(S,G)`. Cisco mặc định `spt-threshold 0` = **chuyển ngay** |
| 38 | ⭐ Flag `T` trong `show ip mroute` | ⭐ **SPT bit đã set** = đã chuyển sang source tree |
| 39 | ⭐ `Incoming interface` trong mroute | ⭐ **RPF interface** — gói **phải** đến từ đây |
| 40 | ⭐ OIL trống / `Null` | ⭐ **Không có receiver** → không forward |
| 41 | ⭐ 3 cách RP discovery | ⭐ **Static** (`ip pim rp-address`) · **Auto-RP** (Cisco, 224.0.1.39/.40) · ⭐ **BSR** (chuẩn mở) |
| 42 | ⭐ IGMP snooping làm gì | ⭐ Switch **nghe IGMP** → chỉ gửi multicast ra port có host đăng ký (thay vì flood) |
| 43 | ⭐ VLAN không có router multicast | ⭐ Không có querier → snooping không hoạt động → **flood**. Sửa: `ip igmp snooping vlan X querier` |

---

## 🐛 10. GỠ LỖI NHANH

### 10.1 Hộp lệnh vạn năng

```
! ═══ NAT ═══
show ip nat translations                    ! ⭐⭐ bảng NAT (4 cột)
show ip nat translations verbose            ! ⭐ + timeout, flags
show ip nat statistics                      ! ⭐⭐ Hits/Misses, interface inside/outside
show ip nat nvi statistics
show run | include ip nat                   ! ⭐ xem mọi lệnh NAT
show run interface <if> | include nat       ! ⭐ inside/outside đặt đúng chưa
clear ip nat translation *                  ! ⭐ xóa entry động
clear ip nat statistics
debug ip nat                                ! ⚠️ chỉ lab
debug ip nat detailed                       ! ⚠️

! ═══ NTP ═══
show clock detail                           ! ⭐⭐ giờ + nguồn + dấu * (không đáng tin)
show ntp status                             ! ⭐⭐ synchronized? stratum? reference?
show ntp associations                       ! ⭐⭐ dấu * # + - x, cột st và reach
show ntp associations detail
show ntp config
show ntp packets
debug ntp all                               ! ⚠️ chỉ lab
debug ntp authentication                    ! ⭐ hữu ích cho key mismatch

! ═══ MULTICAST ═══
show ip multicast
show ip pim interface
show ip pim neighbor                        ! ⭐ neighbor + DR
show ip pim rp mapping                      ! ⭐ RP nào cho group nào
show ip mroute                              ! ⭐⭐ (*,G) và (S,G), Incoming/OIL, flags
show ip mroute count                        ! ⭐ đếm gói/byte (có traffic thật không?)
show ip mroute active                       ! group đang có traffic
show ip igmp groups                         ! ⭐ host nào đăng ký group nào
show ip igmp interface                      ! ⭐ IGMP version, querier
show ip rpf <source-ip>                     ! ⭐⭐ RPF interface cho source đó
show ip igmp snooping                       ! (switch)
show ip igmp snooping groups                ! (switch)
show mac address-table multicast            ! (switch)
debug ip mpacket                            ! ⚠️ thấy RPF failed
debug ip igmp                               ! ⚠️
debug ip pim                                ! ⚠️
```

### 10.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

#### NAT

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | 🔴⭐ NAT config đúng, `show ip nat translations` **TRỐNG**, ping fail | 🔴 ⭐ **Thiếu default route** — routing xảy ra TRƯỚC NAT | ⭐ `show ip route 0.0.0.0` · `show ip nat statistics` (Hits **không tăng**) | Thêm default route |
| 2 | NAT không hoạt động, entry trống | ⭐ Thiếu `ip nat inside` hoặc `ip nat outside`, hoặc **đặt sai chiều** | ⭐ `show ip nat statistics` → xem `Inside interfaces` / `Outside interfaces` | Đặt đúng `ip nat inside`/`outside` |
| 3 | NAT không hoạt động | ACL không khớp subnet nguồn | `show access-lists ACL-NAT` (0 matches?) | Sửa ACL |
| 4 | 🔴⭐ **Port forward không hoạt động** | 🔴 ⭐ **ACL inbound trên outside interface dùng IP PRIVATE** | ⭐ `show access-lists` → dòng permit **`0 matches`** | ⭐ Đổi ACL sang **IP PUBLIC** (Inside Global) |
| 5 | Port forward: static entry có mà không kết nối được | Server nội bộ không có default gateway trỏ về router NAT · firewall trên server | `show ip nat translations` (có entry?) · ping từ router tới server | Sửa gateway server |
| 6 | ⭐ `Misses` cao trong `show ip nat statistics` | ⭐ **Dynamic NAT cạn pool** · hoặc traffic khớp ACL nhưng không NAT được | ⭐ `show logging \| inc ADDR_ALLOC_FAILURE` | Thêm `overload` · mở rộng pool |
| 7 | 🔴⭐ Dual-ISP: routing failover OK nhưng **traffic vẫn chết** | 🔴 ⭐ **NAT không failover** — entry cũ dùng IP của ISP chết | ⭐ `show ip nat translations` → xem Inside Global là IP ISP nào | ⭐ **NAT route-map với `match interface`** + `clear ip nat translation *` (tự động bằng EEM) |
| 8 | Router hết RAM / CPU cao, NAT entry rất nhiều | 1 host tạo quá nhiều session (malware/P2P) | ⭐ `show ip nat translations \| count` · `show ip nat statistics` | ⭐ `ip nat translation max-entries host <ip> 100` · giảm timeout |
| 9 | Traffic nội bộ ↔ nội bộ bị NAT ngoài ý muốn | ACL NAT quá rộng (permit any) | `show access-lists ACL-NAT` | ⭐ Thêm `deny` cho traffic nội bộ **trước** dòng permit |
| 10 | Sau khi sửa NAT config vẫn hành vi cũ | Entry cũ còn trong bảng | `show ip nat translations` | ⭐ `clear ip nat translation *` |

#### NTP

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 11 | ⭐ `Clock is unsynchronized, stratum 16` | ⭐ Không sync được: key lệch · server unreachable · ACL chặn UDP 123 | ⭐ `show ntp associations` (`reach 0`? `st 16`? không có `*`?) · `debug ntp authentication` | Sửa key/ACL/routing |
| 12 | ⭐ `reach 0` | Không nhận được packet NTP | `ping <ntp-server>` · `show access-lists` (UDP 123?) | Mở ACL · sửa routing |
| 13 | ⭐ Không có dấu `*`, chỉ có `+` hoặc trống | Server hợp lệ nhưng chưa được chọn làm sys.peer · hoặc bị loại | `show ntp associations detail` | Chờ (mất 1–5 phút) · thêm `prefer` |
| 14 | ⭐ Có dấu `x` (falseticker) | ⭐ Server đó **báo giờ sai** rõ rệt | `show ntp associations` | Bỏ server đó · dùng server khác |
| 15 | ⭐ Auth mismatch nhưng không rõ nguyên nhân | ⭐ Thiếu **1 trong 3** lệnh auth | ⭐ `show run \| inc ntp` → có đủ `authenticate`, `authentication-key`, `trusted-key`? | Thêm lệnh còn thiếu |
| 16 | ⭐ Dấu `*` trước giờ trong `show clock` | ⭐ **Chưa bao giờ sync** — giờ không đáng tin | `show clock detail` → `Time source is ...` | Cấu hình `ntp server` |
| 17 | Giờ đúng UTC nhưng sai giờ địa phương | Thiếu `clock timezone` | `show clock detail` | ⭐ `clock timezone ICT 7` |
| 18 | Log không có timestamp đầy đủ | Mặc định IOS chỉ có uptime | `show run \| inc service timestamps` | ⭐ `service timestamps log datetime msec localtime show-timezone` |
| 19 | ⭐ Router bị lợi dụng làm NTP amplifier | Không có `ntp access-group` | `show ntp associations` (có peer lạ?) | ⭐ `ntp access-group serve-only <acl>` |

#### Multicast

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 20 | ⭐ Multicast bị **flood cả VLAN** | ⭐ IGMP snooping tắt · hoặc ⭐ **VLAN không có querier** | ⭐ `show ip igmp snooping vlan X` · `show ip igmp interface` | Bật `ip igmp snooping` · ⭐ `ip igmp snooping vlan X querier` |
| 21 | ⭐ Receiver không nhận được multicast, `show ip mroute` có `(*,G)` nhưng **OIL trống** | Không có IGMP report từ receiver · IGMP version lệch | ⭐ `show ip igmp groups` · `show ip igmp interface` (version?) | Kiểm tra host · khớp `ip igmp version` |
| 22 | ⭐⭐ Gói multicast bị **drop**, `debug ip mpacket` báo **RPF failed** | ⭐ **RPF check fail** — routing bất đối xứng, hoặc thiếu route tới source | ⭐⭐ `show ip rpf <source>` → so với interface gói đến | Sửa unicast routing · thêm static mroute (`ip mroute`) |
| 23 | `show ip mroute` **trống** | Chưa bật `ip multicast-routing` · chưa có PIM trên interface | `show ip multicast` · `show ip pim interface` | `ip multicast-routing` + `ip pim sparse-mode` |
| 24 | PIM neighbor không lên | PIM chưa bật 2 đầu · ACL chặn `224.0.0.13` | `show ip pim neighbor` · `show ip pim interface` | Bật `ip pim sparse-mode` cả 2 đầu |
| 25 | `(*,G)` không tạo được trong PIM-SM | ⭐ Không biết RP · không có route tới RP | ⭐ `show ip pim rp mapping` · `show ip route <RP-ip>` | Khai `ip pim rp-address` · thêm route tới RP |
| 26 | Multicast chỉ đi được 1 hop | ⭐ Dùng địa chỉ trong **224.0.0.0/24** (link-local, **TTL 1**) | Kiểm tra địa chỉ group | ⭐ Dùng **239.x.x.x** |

### 10.3 ⭐ Quy trình troubleshoot NAT — 5 bước

```
1. INTERFACE inside/outside ĐÚNG CHƯA?
   show ip nat statistics
   → Đọc "Inside interfaces" và "Outside interfaces"
   ├─ Thiếu / sai chiều → sửa `ip nat inside` / `ip nat outside`
   └─ Đúng ↓
2. ⭐ CÓ ROUTE TỚI ĐÍCH CHƯA? (inside→outside: ROUTING TRƯỚC NAT)
   show ip route 0.0.0.0
   ├─ Không có → 🔴 NAT SẼ KHÔNG BAO GIỜ ĐƯỢC GỌI → thêm default route
   └─ Có ↓
3. ACL NAT CÓ KHỚP CHƯA?
   show access-lists ACL-NAT      → có match không?
   show ip nat statistics          → Hits có tăng? Misses cao?
   ├─ Hits = 0        → ACL không khớp → sửa ACL
   ├─ Misses cao      → pool cạn → thêm `overload`
   └─ Hits tăng ↓
4. ENTRY CÓ ĐÚNG KHÔNG?
   show ip nat translations
   → Đọc 4 cột: Inside Local / Inside Global / Outside Local / Outside Global
   ├─ Inside Global là IP của ISP ĐÃ CHẾT → 🔴 NAT không failover
   │                                        → NAT route-map + clear translation
   └─ Đúng ↓
5. ⭐ CÓ ACL NÀO CHẶN KHÔNG? (nhớ: ACL chạy TRƯỚC NAT ở chiều vào)
   show access-lists
   → Interface OUTSIDE inbound  → ACL phải dùng ⭐ IP PUBLIC
   → Interface INSIDE inbound   → ACL phải dùng ⭐ IP PRIVATE
```

---

## 📝 11. QUIZ TỰ KIỂM TRA

**Câu 1.** 🔴 Cấu hình NAT/PAT hoàn toàn đúng, `ip nat inside`/`outside` đúng chiều, ACL khớp.
Nhưng `show ip nat translations` **trống** và host nội bộ không ra được Internet. Nguyên nhân?

<details><summary>Xem đáp án</summary>

🔴 ⭐ **Thiếu default route (hoặc route tới đích).**

**Vì sao:** ở chiều **inside → outside**, thứ tự xử lý là ⭐ **ROUTING TRƯỚC, NAT SAU**.

```
Gói vào → ACL input → Policy routing → ⭐ ROUTING → ⭐ NAT (local→global) → ra
                                            ↑
                              Không có route → DROP TẠI ĐÂY
                              → NAT KHÔNG BAO GIỜ ĐƯỢC GỌI
```

**Chẩn đoán:**
```
show ip route 0.0.0.0
! % Network not in table                        ← ⭐ đây là câu trả lời

show ip nat statistics | include Hits
! Hits: 0  Misses: 0                            ← ⭐ CẢ HAI đều 0 = NAT chưa được gọi
```

⭐ **Dấu hiệu nhận diện:** `Hits = 0` **VÀ** `Misses = 0`.
- `Hits = 0`, `Misses > 0` → NAT được gọi nhưng thất bại (pool cạn)
- ⭐ `Hits = 0`, `Misses = 0` → ⭐ **NAT chưa được gọi lần nào** → vấn đề **routing** hoặc **interface inside/outside**

**Sửa:**
```
ip route 0.0.0.0 0.0.0.0 <next-hop>
```

⭐ Đây là lỗi mà bạn đã gặp ở Module-P0 LAB P0-6 §Thử nghiệm — giờ hiểu **vì sao**.
</details>

---

**Câu 2.** 🔴⭐ Bạn port-forward web server `10.1.10.50:80` qua IP public `203.0.113.1:80`.
NAT entry có, nhưng từ Internet không truy cập được. ACL inbound trên interface outside:
```
permit tcp any host 10.1.10.50 eq 80
deny ip any any log
```
Vì sao không hoạt động? Sửa thế nào?

<details><summary>Xem đáp án</summary>

🔴 ⭐ **ACL dùng IP PRIVATE, nhưng phải dùng IP PUBLIC.**

**Vì sao:** ở chiều **outside → inside**, thứ tự là:
```
Gói vào → ⭐ ACL INPUT → ⭐ NAT (global→local) → Policy routing → Routing
              ↑
    ⭐ ACL chạy TRƯỚC NAT
    → lúc này destination vẫn là 203.0.113.1 (IP PUBLIC)
    → KHÔNG khớp `host 10.1.10.50`
    → rơi xuống `deny ip any any` → DROP
```

**Chẩn đoán:**
```
show access-lists ACL-OUT-IN
! 10 permit tcp any host 10.1.10.50 eq www (0 matches)      ← ⭐ 0 MATCHES
! 20 deny ip any any log (5 matches)                        ← ⭐ bị chặn ở đây
```
⭐ **`0 matches` ở dòng permit + có match ở dòng deny** = ACL viết sai đối tượng.

**✅ Sửa — dùng IP public (Inside Global):**
```
ip access-list extended ACL-OUT-IN
 permit tcp any host 203.0.113.1 eq 80          ! ⭐ IP PUBLIC
 permit tcp any host 203.0.113.1 eq 443
 permit icmp any any
 deny   ip any any log
```

⭐ **QUY TẮC TỔNG QUÁT — thuộc lòng:**

| ACL inbound trên interface | Dùng IP nào |
|---|---|
| ⭐ **OUTSIDE** (hướng Internet) | ⭐ **IP PUBLIC** (Inside Global) |
| ⭐ **INSIDE** (hướng LAN) | ⭐ **IP PRIVATE** (Inside Local) |

⭐ **Lý do chung:** ⭐ **ACL input LUÔN chạy trước NAT** — nên nó thấy IP **trước khi dịch**.
Ở chiều vào từ Internet, IP trước khi dịch là **IP public**.
</details>

---

**Câu 3.** ⭐ Điền 4 thuật ngữ NAT từ output này. Khi nào Outside Local ≠ Outside Global?
```
tcp  203.0.113.1:1035   10.1.10.100:1035   8.8.8.8:80   8.8.8.8:80
```

<details><summary>Xem đáp án</summary>

| Cột | Giá trị | Thuật ngữ | Nghĩa |
|---|---|---|---|
| 1 | `203.0.113.1:1035` | ⭐ **Inside Global** | IP host nội bộ **hóa trang thành** (nhìn từ ngoài) |
| 2 | `10.1.10.100:1035` | ⭐ **Inside Local** | IP **thật** của host nội bộ |
| 3 | `8.8.8.8:80` | ⭐ **Outside Local** | IP host bên ngoài, **nhìn từ nội bộ** |
| 4 | `8.8.8.8:80` | ⭐ **Outside Global** | IP **thật** của host bên ngoài |

⭐ **Quy tắc đọc:**
- **Inside / Outside** = host đó **thuộc mạng nào**
- **Local / Global** = **nhìn từ phía nào** (Local = từ trong, Global = từ ngoài)

⭐ **Outside Local ≠ Outside Global khi nào:**

Khi dùng ⭐ **`ip nat outside source`** — tức bạn **dịch cả IP của bên ngoài** để nội bộ thấy nó là IP khác.

```
ip nat outside source static 172.16.1.1 10.99.1.1
```
→ Server bên ngoài thật là `172.16.1.1` (**Outside Global**),
nhưng host nội bộ thấy nó là `10.99.1.1` (**Outside Local**).

⭐ **Dùng khi nào:** ⭐ **2 mạng có IP trùng nhau** — VD sau khi **sáp nhập 2 công ty**
mà cả hai đều dùng `10.1.1.0/24`. Bạn dịch mạng bên kia thành dải khác để tránh xung đột.
</details>

---

**Câu 4.** 🔴⭐ Dual-ISP: IP SLA + track + floating static đã failover đúng (routing chuyển sang ISP2),
nhưng host nội bộ **vẫn không ra được Internet**. Vì sao? Giải pháp?

<details><summary>Xem đáp án</summary>

🔴 ⭐ **NAT không failover.**

**Vì sao:** với NAT thường (`ip nat inside source list ACL interface Gi0/1 overload`),
router tạo **simple translation entry** — entry này ⭐ **không ghi nhớ mình đi qua interface nào**.

Khi routing chuyển sang ISP2:
- Gói **ra interface ISP2** (`Gi0/2`)
- Nhưng ⭐ **entry NAT cũ vẫn còn** với Inside Global = IP của **ISP1**
- → source IP là IP của ISP1, gửi ra ISP2
- → ⭐ **ISP2 DROP** (đó không phải IP thuộc dải của họ — anti-spoofing)
- ⚠️ Và entry NAT mặc định timeout **24 giờ**!

**Chẩn đoán:**
```
show ip route 0.0.0.0
! * 192.0.2.2                                    ← ✅ routing ĐÃ chuyển ISP2

show ip nat translations
! icmp 203.0.113.1:8  10.1.10.100:8  ...        ← 🔴 vẫn IP của ISP1!
```

⭐ **Giải pháp — NAT route-map với `match interface`:**

```
ip access-list standard ACL-NAT
 permit 10.1.10.0 0.0.0.255
!
route-map RM-NAT-ISP1 permit 10
 match ip address ACL-NAT
 match interface GigabitEthernet0/1              ! ⭐ ISP1
!
route-map RM-NAT-ISP2 permit 10
 match ip address ACL-NAT
 match interface GigabitEthernet0/2              ! ⭐ ISP2
!
ip nat inside source route-map RM-NAT-ISP1 interface GigabitEthernet0/1 overload
ip nat inside source route-map RM-NAT-ISP2 interface GigabitEthernet0/2 overload
```

⭐ **Cơ chế:** route-map NAT tạo ⭐ **fully-extended entry** (có cả outside address)
→ ⭐ **cùng một inside host có 2 entry riêng cho 2 ISP** → NAT theo đúng interface đi ra.

⭐ **Và vẫn nên clear NAT khi failover** — tự động bằng **EEM** (Module-12):
```
event manager applet CLEAR-NAT-ON-FAILOVER
 event track 1 state any
 action 1.0 cli command "enable"
 action 2.0 cli command "clear ip nat translation *"
 action 3.0 syslog msg "NAT cleared - track 1 changed"
```

⭐ **BA LỚP của dual-ISP — thiếu lớp nào cũng không hoạt động:**

| Lớp | Cấu hình | Module |
|:---:|---|---|
| 1. **Routing** failover | IP SLA + track + floating static | M03 §2.4 |
| 2. ⭐ **NAT** failover | ⭐ **NAT route-map + `match interface`** | ⭐ Đây |
| 3. **Gateway HA** cho LAN | HSRP + object tracking | M06A |
</details>

---

**Câu 5.** ⭐ `show ntp status` báo `Clock is unsynchronized, stratum 16`.
Nêu 4 nguyên nhân và lệnh chẩn đoán.

<details><summary>Xem đáp án</summary>

⭐ **`stratum 16` = KHÔNG ĐỒNG BỘ** (stratum hợp lệ chỉ 1–15).

| # | Nguyên nhân | Lệnh chẩn đoán |
|:---:|---|---|
| 1 | ⭐ **Authentication mismatch** (key sai, hoặc thiếu 1 trong 3 lệnh) | ⭐ `show run \| inc ntp` (đủ `authenticate` + `authentication-key` + `trusted-key`?) · `debug ntp authentication` |
| 2 | ⭐ **Server unreachable** | ⭐ `show ntp associations` → `reach 0` · `ping <ntp-server>` |
| 3 | ⭐ **ACL chặn UDP 123** | `show access-lists` · `show ntp access-group` |
| 4 | ⭐ **Server đó cũng chưa sync** (`st 16`) | ⭐ `show ntp associations` → cột `st` của server = **16** |
| + | Chưa đủ thời gian (NTP cần 1–5 phút) | `show ntp associations` → `when` và `reach` |
| + | `ntp access-group` chặn chính server mình muốn sync | `show run \| inc ntp access-group` |

**Chẩn đoán chuẩn:**
```
show ntp associations
!   address         ref clock       st   when   poll reach  delay  offset   disp
!  ~10.1.1.10      0.0.0.0         16     -      64     0   0.000   0.000 16000.
!  ↑ KHÔNG có dấu *    ↑ st=16       ↑ reach=0
```

⭐ **Ba dấu hiệu cùng lúc:**
| Dấu hiệu | Nghĩa |
|---|---|
| ⭐ Không có dấu **`*`** | Không có server nào được chọn làm sys.peer |
| ⭐ **`st 16`** | Server đó cũng chưa sync (hoặc không phản hồi) |
| ⭐ **`reach 0`** | Không nhận được packet NTP nào |

⭐ **3 lệnh BẮT BUỘC cho NTP auth** (thiếu 1 = không sync, triệu chứng giống key sai):
```
ntp authenticate
ntp authentication-key 1 md5 <key>
ntp trusted-key 1
!
ntp server <ip> key 1
```

⭐ **Và kiểm tra `show clock`:** dấu **`*`** trước giờ = **thời gian không đáng tin**.
</details>

---

**Câu 6.** ⭐ Giải thích các ký hiệu trong `show ntp associations`: `*` `#` `+` `-` `x`.
Và `reach 377` nghĩa là gì?

<details><summary>Xem đáp án</summary>

| Ký hiệu | Nghĩa |
|:---:|---|
| ⭐ **`*`** | ⭐ **sys.peer** — server đang **THỰC SỰ được dùng** để đồng bộ đồng hồ |
| ⭐ **`#`** | **Selected** — chất lượng tốt, nhưng khoảng cách (distance) quá lớn để làm sys.peer |
| ⭐ **`+`** | **Candidate** — hợp lệ, sẵn sàng thay thế nếu sys.peer mất |
| **`-`** | **Outlier** — bị thuật toán **clustering** loại (lệch so với nhóm) |
| ⭐ **`x`** | ⭐ **Falseticker** — ⭐ **server báo giờ SAI rõ rệt** → bị loại hoàn toàn |
| *(trống)* | **Rejected** — không dùng được (unreachable, hoặc stratum 16) |
| `~` | **Configured** — khai báo bằng tay (không phải học động) |

⭐ **`reach 377` — số BÁT PHÂN:**

```
377 (bát phân) = 11111111 (binary) = 8 lần poll gần nhất ĐỀU THÀNH CÔNG
```

Reachability register là **8 bit**, mỗi bit = 1 lần poll:

| `reach` (oct) | Binary | Nghĩa |
|:---:|---|---|
| ⭐ **377** | `11111111` | ⭐ **8/8 OK — hoàn hảo** |
| 376 | `11111110` | Lần poll cũ nhất fail |
| 177 | `01111111` | Lần poll mới nhất fail |
| 17 | `00001111` | ⭐ Chỉ 4 lần gần nhất OK — **đang mất gói** |
| 1 | `00000001` | Chỉ 1 lần OK |
| ⭐ **0** | `00000000` | ⭐ **Không nhận được gì** |

⭐ **Cách dùng thực tế:** `reach` **thấp hoặc dao động** (VD 17, 177) = ⭐ **mất gói NTP**
→ kiểm tra mạng/ACL. `reach 377` ổn định = kết nối NTP tốt.

⭐ **Cột `st`** (stratum của server đó): **16** = server đó cũng chưa sync → vô dụng.
</details>

---

**Câu 7.** ⭐ Điền bảng: IGMPv1 vs v2 vs v3 khác nhau ở đâu? Ai thắng trong IGMP Querier election?
So sánh với PIM DR election.

<details><summary>Xem đáp án</summary>

| | **IGMPv1** | ⭐ **IGMPv2** | ⭐ **IGMPv3** |
|---|---|---|---|
| RFC | 1112 | **2236** | **3376** |
| Join group | ✅ | ✅ | ✅ |
| ⭐ **Leave Group message** | ❌ **KHÔNG** (chờ timeout ~3 phút) | ⭐ ✅ **Có** | ✅ |
| ⭐ **Querier election** | ❌ (dựa PIM DR) | ⭐ ✅ | ✅ |
| Group-Specific Query | ❌ | ✅ | ✅ |
| Max Response Time | ❌ | ✅ | ✅ |
| ⭐ **Source filtering** | ❌ | ❌ | ⭐ ✅ **INCLUDE / EXCLUDE** |
| Hỗ trợ **SSM** | ❌ | ❌ | ⭐ ✅ **BẮT BUỘC** |
| Report gửi tới | Group address | Group address | ⭐ **224.0.0.22** |

⭐ **Hai điểm quan trọng nhất:**
- ⭐ **v2 thêm Leave Group** → host rời group **nhanh** (v1 phải chờ timeout 3 phút → tốn băng thông)
- ⭐ **v3 thêm source filtering** → cho phép **SSM** (host nói *"tôi muốn G **từ source S**"*)
  → ⭐ **không cần RP** và ⭐ **chống multicast spoofing**

🔴⭐ **BẪY ĐỀ — hai election NGƯỢC NHAU:**

| Election | Ai thắng |
|---|---|
| ⭐ **IGMP Querier** | ⭐ **IP THẤP NHẤT** |
| ⭐ **PIM DR** | ⭐ Priority cao → **IP CAO NHẤT** |

⚠️ **Và cả hai đều khác OSPF DR** (priority cao → **Router ID cao nhất**, và **non-preemptive**).

🧠 **Mẹo nhớ:** ⭐ *"**I**GMP = **I**P thấp. **P**IM = **P**hải cao."*

**Verify:**
```
show ip igmp interface | include version|Querier
!   IGMP version is 2
!   IGMP querying router is 10.1.10.2 (this system)
show ip pim neighbor
!   (cột DR)
```
</details>

---

**Câu 8.** ⭐⭐ RPF check là gì? Nêu công thức kiểm tra và lệnh verify. Vì sao multicast cần nó?

<details><summary>Xem đáp án</summary>

⭐⭐ **RPF (Reverse Path Forwarding) check:**

> Khi router nhận gói multicast từ source S, nó hỏi:
> ⭐ ***"Nếu tôi phải gửi một gói UNICAST ngược về S, tôi sẽ dùng interface nào?"***
> - Interface đó **=** interface gói vừa đến → ✅ **PASS** → forward
> - Interface đó **≠** interface gói vừa đến → 🔴 **FAIL** → ⭐ **DROP**

```
Source 10.1.1.1
     │
     ├── Gi0/0 ──▶ [Router]   show ip route 10.1.1.1 → via Gi0/0
     │                        Gói đến từ Gi0/0 → ✅ PASS
     │
     └── Gi0/1 ──▶ [Router]   Gói đến từ Gi0/1
                              nhưng route về source là Gi0/0
                              → 🔴 RPF FAIL → DROP
```

⭐ **Vì sao multicast CẦN RPF:**

| | **Unicast** | ⭐ **Multicast** |
|---|---|---|
| Hướng forward | **TỚI đích** | ⭐ **XA nguồn** (away from source) |
| Chống loop | **TTL** giảm dần | ⭐ **RPF check** |

Multicast forward **ra nhiều interface cùng lúc** (fan-out) → nếu không có kiểm soát,
gói dễ **quay lại chính nó** → ⭐ **loop nhân bản theo cấp số nhân** (tệ hơn broadcast storm nhiều).

⭐ **RPF đảm bảo gói CHỈ đi xa nguồn, không bao giờ đi vòng lại** → chống loop.

**Lệnh verify:**
```
show ip rpf 10.1.1.1
! RPF information for ? (10.1.1.1)
!   RPF interface: GigabitEthernet0/0                 ← ⭐ interface hợp lệ
!   RPF neighbor: ? (10.0.12.2)
!   RPF route/mask: 10.1.1.0/24
!   RPF type: unicast (ospf 1)                        ← ⭐ dùng bảng UNICAST
!
show ip mroute
! (10.1.1.1, 239.1.1.1), ...
!   Incoming interface: GigabitEthernet0/0            ← ⭐ = RPF interface
!
debug ip mpacket                                       ! ⚠️ thấy "RPF failed"
```

⚠️ **RPF failure thường xảy ra khi:**
1. ⭐ **Unicast routing bất đối xứng** (traffic đi 1 đường, về 1 đường khác)
2. Multicast đi qua **tunnel** mà unicast route không qua tunnel
3. **Thiếu route** tới source
4. Sau khi routing thay đổi mà mroute chưa cập nhật

⭐ **Sửa:** sửa unicast routing cho đối xứng · hoặc dùng **static mroute**:
```
ip mroute 10.1.1.0 255.255.255.0 GigabitEthernet0/1
```
⭐ Lệnh này tạo bảng RPF **riêng cho multicast**, độc lập với bảng unicast.

🧠 ⭐ ***"Unicast đi TỚI đích. Multicast đi XA nguồn. RPF là cách router kiểm tra
gói có thật sự đến từ hướng nguồn hay không."***
</details>

---

**Câu 9.** ⭐ Phân biệt `(*, G)` và `(S, G)`. SPT switchover là gì? Đọc flag `T` nghĩa là gì?

<details><summary>Xem đáp án</summary>

| | ⭐ **`(*, G)`** — Shared Tree (RPT) | ⭐ **`(S, G)`** — Source Tree (SPT) |
|---|---|---|
| Gốc cây | ⭐ **RP** (Rendezvous Point) | ⭐ **Source** |
| Nghĩa | "Bất kỳ source nào cho group G, đi qua RP" | "Source S cụ thể cho group G" |
| Đường đi | ⚠️ **Có thể đi vòng** (qua RP) | ⭐ **Ngắn nhất** |
| State trên router | ⭐ **Ít** (1 entry/group) | Nhiều (1 entry/cặp source-group) |
| Ví von | ⭐ **Gửi qua bưu cục trung tâm** | ⭐ **Giao tận tay** |

```
   ═══ (*, G) — SHARED TREE ═══           ═══ (S, G) — SOURCE TREE ═══

   Source ──▶ RP ──▶ Receiver             Source ──────────▶ Receiver
              ↑                                  (trực tiếp, bỏ qua RP)
       (đi vòng qua RP)
```

⭐ **SPT Switchover:** PIM-SM ⭐ **bắt đầu bằng `(*, G)`** (để nhận gói đầu tiên và biết source ở đâu),
rồi ⭐ **tự chuyển sang `(S, G)`** để đi đường ngắn nhất, và gửi **Prune** về nhánh qua RP.

```
ip pim spt-threshold 0            ! ⭐ Cisco MẶC ĐỊNH — chuyển NGAY khi thấy gói đầu tiên
ip pim spt-threshold infinity     ! không bao giờ chuyển (luôn dùng shared tree)
```

⭐ **Flag `T` trong `show ip mroute` = SPT bit đã set** = ⭐ **đã chuyển sang source tree**.

**Đọc output:**
```
(*, 239.1.1.1), 00:05:23/stopped, RP 10.99.99.1, flags: SJC
  Incoming interface: Gi0/0, RPF nbr 10.0.12.2
  Outgoing interface list:
    Gi0/1, Forward/Sparse, 00:05:23/00:02:41

(10.1.1.1, 239.1.1.1), 00:03:12/00:02:47, flags: JT       ← ⭐ flag T
  Incoming interface: Gi0/0, RPF nbr 10.0.12.2
  Outgoing interface list:
    Gi0/1, Forward/Sparse, 00:03:12/00:02:47
```

⭐ **Các flag hay gặp:**

| Flag | Nghĩa |
|:---:|---|
| **`S`** | Sparse mode |
| **`D`** | Dense mode |
| **`J`** | Join SPT (sẽ chuyển sang source tree) |
| ⭐ **`T`** | ⭐ **SPT bit set** — đã dùng source tree |
| **`C`** | Connected — có receiver nối trực tiếp |
| **`L`** | Local — router này là receiver |
| **`P`** | Pruned |
| **`F`** | Register flag (source nối trực tiếp, đang register với RP) |

⭐ **Ba dòng phải đọc trong mroute:**
1. ⭐ **`Incoming interface`** = **RPF interface** — gói **phải** đến từ đây
2. ⭐ **`Outgoing interface list (OIL)`** = gửi ra đâu. ⭐ **`Null` = KHÔNG có receiver**
3. ⭐ **`flags`** — trạng thái cây

⭐ **SSM bỏ luôn RP:** host dùng IGMPv3 nói thẳng **`(S, G)`** →
⭐ chỉ có source tree, ⭐ **không cần `(*, G)`, không cần RP, không cần switchover**.
</details>

---

**Câu 10.** ⭐ Multicast bị **flood ra cả VLAN** dù switch có bật IGMP snooping. Nguyên nhân
phổ biến nhất và cách sửa?

<details><summary>Xem đáp án</summary>

⭐ **VLAN đó KHÔNG CÓ IGMP Querier.**

**Vì sao:** IGMP snooping hoạt động bằng cách ⭐ **nghe IGMP Report từ host**.
Nhưng host chỉ gửi Report khi ⭐ **được Query hỏi** — và **Query do router multicast gửi**.

⭐ VLAN **không có router multicast** (VD VLAN thuần L2, hoặc router chưa bật PIM)
→ ⭐ **không ai gửi Query** → host không gửi Report → snooping ⭐ **không học được gì**
→ switch ⭐ **flood multicast ra mọi port** (hành xử như broadcast).

**Chẩn đoán:**
```
show ip igmp snooping vlan 10
! Global IGMP Snooping configuration:
!   IGMP snooping              : Enabled                 ← ✅ đã bật
! Vlan 10:
!   IGMP snooping              : Enabled
!   IGMPv2 immediate leave     : Disabled
!   Explicit host tracking     : Enabled
!   Multicast router learning mode: pim-dvmrp
!   ⭐ (không thấy querier nào)

show ip igmp snooping groups
! → TRỐNG                                                ← ⭐ không học được group nào

show ip igmp snooping mrouter
! → TRỐNG                                                ← ⭐ không có router multicast
```

⭐ **Sửa — bật IGMP snooping querier trên switch:**
```
ip igmp snooping querier                                ! global
ip igmp snooping vlan 10 querier                        ! ⭐ per-VLAN
ip igmp snooping vlan 10 querier address 10.1.10.253    ! IP nguồn cho Query
```

**Verify sau khi sửa:**
```
show ip igmp snooping querier
! Vlan   IP Address    IGMP Version  Port
! 10     10.1.10.253   v2            Switch

show ip igmp snooping groups
! Vlan  Group           Type   Version  Port List
! 10    239.1.1.1      igmp   v2       Gi0/3            ← ⭐ đã học được

show mac address-table multicast
```

⭐ **Nguyên nhân khác (kiểm tra thêm):**

| Nguyên nhân | Chẩn đoán |
|---|---|
| IGMP snooping bị **tắt** ở global hoặc VLAN | `show ip igmp snooping` |
| Địa chỉ group nằm trong ⭐ **224.0.0.0/24** (link-local — **luôn** được flood theo thiết kế) | Kiểm tra địa chỉ group → dùng `239.x.x.x` |
| ⭐ **IGMP version lệch** giữa host và router | `show ip igmp interface \| inc version` |
| Traffic là multicast nhưng dùng **MAC unicast/broadcast** | `show mac address-table` |

⭐ **Bài học thực chiến:** đây là sự cố rất phổ biến khi triển khai **IPTV / video conference**
trên VLAN không có L3 multicast. Video 10 Mbps flood ra 48 port = **480 Mbps** rác trên backplane,
và mọi PC phải xử lý bằng CPU.
</details>

---

## 📚 12. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| ⭐ **Inside Local** | IP nội bộ cục bộ | ⭐ IP **thật** của host nội bộ |
| ⭐ **Inside Global** | IP nội bộ toàn cục | ⭐ IP host nội bộ **sau khi NAT** |
| ⭐ **Outside Global** | IP ngoài toàn cục | IP **thật** của host bên ngoài |
| ⭐ **Outside Local** | IP ngoài cục bộ | IP host ngoài **nhìn từ nội bộ**. Khác Outside Global khi dùng `ip nat outside source` |
| ⭐ **Static NAT** | NAT tĩnh | 1 private ↔ 1 public, cố định 2 chiều |
| ⭐ **Static PAT / Port forwarding** | PAT tĩnh / Chuyển tiếp cổng | ⭐ 1 private:port ↔ 1 public:port |
| **Dynamic NAT** | NAT động | Nhiều private ↔ pool public, 1:1. ⚠️ Cạn pool → drop |
| ⭐ **PAT / Overload** | Dịch địa chỉ theo cổng | ⭐ Nhiều private → 1 public + port |
| ⭐ **`extendable`** | Có thể mở rộng | Cho phép cùng Inside Local có nhiều Inside Global |
| ⭐ **NAT route-map** | NAT theo bản đồ route | ⭐ Tạo **fully-extended entry** → **failover dual-ISP** |
| **Fully-extended entry** | Entry đầy đủ | Có cả outside address → phân biệt được theo interface |
| ⭐ **`max-entries`** | Số entry tối đa | ⭐ Chống 1 host tạo quá nhiều session → cạn RAM |
| ⭐ **NAT64** | Dịch IPv6↔IPv4 | ⭐ Prefix `64:FF9B::/96`, cần **DNS64** |
| ⭐ **NPTv6** | Dịch prefix IPv6 | ⭐ **1:1 stateless**, **không đổi port**, checksum-neutral |
| **CGN / NAT444** | NAT cấp nhà mạng | ISP NAT nhiều lần |
| ⭐ **NTP** (Network Time Protocol) | Giao thức thời gian mạng | ⭐ **UDP 123** |
| ⭐ **Stratum** | Tầng | ⭐ 0 = reference clock · **1–15 = hợp lệ** · ⭐ **16 = KHÔNG SYNC** |
| **Reference clock** | Đồng hồ tham chiếu | Stratum 0 — nguyên tử/GPS |
| ⭐ **sys.peer** | Peer hệ thống | ⭐ Dấu **`*`** — server đang thực sự dùng |
| ⭐ **Falseticker** | Kẻ báo giờ sai | ⭐ Dấu **`x`** — server báo giờ sai rõ rệt |
| **Candidate / Outlier** | Ứng viên / Ngoại lai | Dấu `+` / `-` |
| ⭐ **Reachability register** | Thanh ghi khả năng tới | ⭐ Cột `reach`, **bát phân**. `377` = 8/8 OK |
| **Clock offset** | Độ lệch đồng hồ | Lệch bao nhiêu ms so với server |
| **Root delay / dispersion** | Độ trễ / phân tán gốc | RTT tới stratum 1 / sai số tích lũy |
| ⭐ **`ntp master`** | NTP chủ | Router tự làm nguồn thời gian (default stratum 8) |
| ⭐ **`ntp peer`** | NTP đồng cấp | **Hai chiều** (khác `ntp server` một chiều) |
| ⭐ **`ntp access-group serve-only`** | Chỉ phục vụ | ⭐ Chống **NTP amplification DDoS** |
| **SNTP** | NTP đơn giản | ⭐ **Chỉ làm client**, kém chính xác hơn |
| ⭐ **`service timestamps`** | Dấu thời gian dịch vụ | ⭐ Bắt buộc để log có giờ đầy đủ |
| ⭐ **Multicast** | Truyền đa hướng | ⭐ Dải **224.0.0.0/4** |
| ⭐ **Link-local multicast** | Multicast cục bộ liên kết | ⭐ **224.0.0.0/24**, TTL 1, **không route** |
| ⭐ **SSM** (Source-Specific Multicast) | Multicast theo nguồn | ⭐ Dải **232.0.0.0/8**, **không cần RP**, cần **IGMPv3** |
| ⭐ **Administratively scoped** | Phạm vi quản trị | ⭐ **239.0.0.0/8** — "private" của multicast |
| ⭐ **32:1 overlap** | Trùng lặp 32:1 | ⭐ 32 IP multicast → cùng 1 MAC (mất 5 bit) |
| ⭐ **IGMP** (Internet Group Management Protocol) | Giao thức quản lý nhóm | ⭐ **HOST ↔ ROUTER** |
| ⭐ **Leave Group** | Rời nhóm | ⭐ Thêm từ **IGMPv2** |
| ⭐ **IGMP Querier** | Bộ truy vấn IGMP | ⭐ **IP THẤP NHẤT thắng** |
| ⭐ **Source filtering (INCLUDE/EXCLUDE)** | Lọc theo nguồn | ⭐ **IGMPv3** — nền của SSM |
| ⭐ **IGMP Snooping** | Nghe lén IGMP | ⭐ Switch chỉ gửi multicast ra port có host đăng ký |
| ⭐ **IGMP Snooping Querier** | Bộ truy vấn trên switch | ⭐ Cần khi VLAN không có router multicast |
| ⭐ **PIM** (Protocol Independent Multicast) | Multicast độc lập giao thức | ⭐ **ROUTER ↔ ROUTER**. Multicast **224.0.0.13** |
| ⭐ **PIM Dense Mode** | Chế độ dày | ⭐ **Flood-and-Prune**, flood lại mỗi 3 phút |
| ⭐ **PIM Sparse Mode** | Chế độ thưa | ⭐ **Explicit Join**, **cần RP** |
| ⭐ **PIM-SSM** | PIM theo nguồn | ⭐ **Không cần RP**, dùng `(S,G)`, cần IGMPv3 |
| **Bidirectional PIM** | PIM hai chiều | Many-to-many, không tạo state `(S,G)` |
| ⭐ **PIM DR** | Router chỉ định PIM | ⭐ Priority cao → **IP CAO NHẤT** (ngược IGMP Querier!) |
| ⭐⭐ **RPF check** | Kiểm tra đường về | ⭐ *"Route unicast về source có dùng interface gói vừa đến?"* → không thì **DROP**. ⭐ **Chống loop** |
| ⭐ **RP** (Rendezvous Point) | Điểm hội tụ | Gốc của shared tree |
| ⭐ **`(*, G)` Shared Tree / RPT** | Cây chia sẻ | ⭐ Gốc là **RP**, ít state, đường có thể đi vòng |
| ⭐ **`(S, G)` Source Tree / SPT** | Cây nguồn | ⭐ Gốc là **source**, đường ngắn nhất |
| ⭐ **SPT switchover** | Chuyển sang cây nguồn | ⭐ Cisco mặc định `spt-threshold 0` = chuyển ngay. Flag **`T`** |
| ⭐ **OIL** (Outgoing Interface List) | Danh sách interface ra | ⭐ **`Null` = không có receiver** |
| **Auto-RP / BSR** | Tự động RP / Bootstrap Router | Auto-RP: Cisco (224.0.1.39/.40) · ⭐ BSR: chuẩn mở |
| **Anycast RP** | RP anycast | Nhiều RP cùng IP + MSDP → HA |
| **`ip mroute`** | Static mroute | ⭐ Bảng RPF riêng cho multicast, độc lập unicast |
| ⭐ **RA Guard** | Bảo vệ RA | ⭐ Chống **rogue Router Advertisement** (IPv6) |
| **DHCPv6 Guard / IPv6 Snooping / Source Guard** | Bảo vệ DHCPv6 / Nghe lén IPv6 / Bảo vệ nguồn | IPv6 FHS |

---

## 🎯 13. ĐÚC KẾT MODULE-06B

**3 điều rút ra:**

1. 🔴⭐ **Thứ tự NAT–Routing là gốc của 2 lỗi khó tìm nhất:**
   ⭐ **Inside→Outside: ROUTING TRƯỚC, NAT SAU** → thiếu default route = NAT **không được gọi**
   (dấu hiệu: `Hits = 0` **VÀ** `Misses = 0`).
   ⭐ **Outside→Inside: NAT TRƯỚC, ROUTING SAU** — nhưng ⭐ **ACL input LUÔN chạy TRƯỚC NAT**
   → ⭐ **ACL trên interface outside phải dùng IP PUBLIC**.

2. 🔴⭐ **Dual-ISP cần BA lớp, và lớp NAT là lớp hay bị quên nhất:**
   (1) routing failover — IP SLA + track (M03) · (2) ⭐ **NAT failover — route-map với `match interface`**
   (đây) · (3) gateway HA — HSRP + tracking (M06A). NAT thường **không failover được** vì entry
   không ghi nhớ interface đi ra.

3. ⭐ **NTP và Multicast là "describe" nhưng có 2 thứ phải nhận ra trong 1 giây:**
   ⭐ **`stratum 16`** = chưa sync · ⭐ **dấu `*` trước giờ** = giờ không đáng tin ·
   ⭐ **`reach 377`** = 8/8 OK. Và với multicast: ⭐ **RPF check** (*"route unicast về source
   có dùng interface gói vừa đến?"*) là khái niệm cốt lõi nhất, cùng với 🔴 ⭐ **IGMP Querier = IP THẤP,
   PIM DR = IP CAO** (ngược nhau).

🧠 **Một câu để nhớ:** *NAT là **thủ tục sân bay**: ra thì kiểm vé trước rồi đổi hộ chiếu,
vào thì đổi hộ chiếu rồi mới về nhà — và **hải quan luôn kiểm TRƯỚC khi đổi hộ chiếu**.
NTP là **nền của mọi log** — không có nó thì Module-11 vô nghĩa.
Multicast **đi XA nguồn**, không đi tới đích — và RPF check là cách nó chống loop.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | 🔴 ⭐ Thứ tự NAT–Routing cả 2 chiều? | ☐ |
| 2 | ⭐ ACL inbound trên interface outside / inside dùng IP nào? Vì sao? | ☐ |
| 3 | ⭐ 4 thuật ngữ NAT? Khi nào Outside Local ≠ Outside Global? | ☐ |
| 4 | Kể 7 kiểu NAT và lệnh tương ứng | ☐ |
| 5 | ⭐ Dấu hiệu Dynamic NAT cạn pool? | ☐ |
| 6 | 🔴 ⭐ Vì sao NAT thường không failover dual-ISP? Giải pháp? | ☐ |
| 7 | ⭐ 3 lớp của dual-ISP? | ☐ |
| 8 | ⭐ `max-entries` chống gì? | ☐ |
| 9 | ⭐ NAT64 vs NPTv6? | ☐ |
| 10 | ⭐ NTP port? Stratum hợp lệ? Stratum 16 nghĩa gì? | ☐ |
| 11 | ⭐ 3 lệnh bắt buộc cho NTP auth? | ☐ |
| 12 | ⭐ Ký hiệu `*` `#` `+` `-` `x` trong `show ntp associations`? | ☐ |
| 13 | ⭐ `reach 377` nghĩa gì? `reach 0`? | ☐ |
| 14 | ⭐ Dấu `*` trước giờ trong `show clock` nghĩa gì? | ☐ |
| 15 | `ntp server` vs `ntp peer` vs `ntp master`? | ☐ |
| 16 | ⭐ Vì sao cần `ntp access-group serve-only`? | ☐ |
| 17 | ⭐ Dải multicast? 224.0.0.0/24 · 232/8 · 239/8 đặc biệt gì? | ☐ |
| 18 | ⭐ Multicast MAC prefix? Tỉ lệ overlap và cách tính? | ☐ |
| 19 | ⭐ IGMPv1 vs v2 vs v3 khác gì? | ☐ |
| 20 | 🔴 ⭐ IGMP Querier vs PIM DR — ai thắng? (chú ý ngược nhau) | ☐ |
| 21 | ⭐ 4 chế độ PIM và cơ chế mỗi cái? | ☐ |
| 22 | ⭐⭐ RPF check là gì? Công thức? Vì sao cần? | ☐ |
| 23 | ⭐ `(*,G)` vs `(S,G)`? SPT switchover? Flag `T`? | ☐ |
| 24 | ⭐ 3 cách RP discovery? | ☐ |
| 25 | ⭐ IGMP snooping làm gì? Vì sao cần snooping querier? | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Cấu hình PAT overload, PC ping Internet dù ISP **không có route** về LAN | ✅ ☐ |
| 2 | ⭐ Đọc `show ip nat translations` và điền đúng **4 thuật ngữ** | ⭐ ☐ |
| 3 | ⭐⭐ **Xóa default route** → NAT **không tạo entry**, `Hits=0 Misses=0` → hiểu vì sao | ⭐⭐ ☐ |
| 4 | ⭐ Bắt gói 2 bên NAT (inside/outside) → source IP khác nhau | ⭐ ☐ |
| 5 | ⭐ Static PAT (port forward) 2 port, entry hiện ngay với `---` | ☐ |
| 6 | Test từ "Internet" telnet vào port đã forward → thành công | ☐ |
| 7 | 🔴⭐⭐ **Tái hiện bẫy ACL**: dùng IP **private** → `0 matches`, bị chặn | ⭐⭐ ☐ |
| 8 | ⭐ Sửa ACL sang IP **public** → có match, hoạt động | ⭐ ☐ |
| 9 | ⭐ Dynamic NAT với pool 2 IP → host thứ 3 fail, log `ADDR_ALLOC_FAILURE`, `Misses` tăng | ⭐ ☐ |
| 10 | Thêm `overload` → hết cạn pool | ☐ |
| 11 | ⭐⭐ **NAT route-map dual-ISP** với `match interface` (2 route-map) | ⭐⭐ ☐ |
| 12 | ⭐⭐ Test failover: cắt ISP1 → route chuyển ISP2 → `clear ip nat` → NAT dùng **IP ISP2** | ⭐⭐ ☐ |
| 13 | ⭐ Hiểu vì sao cần EEM tự động clear NAT khi failover | ☐ |
| 14 | ⭐ NTP: R-ISP làm `ntp master`, R1/R2 làm client với **MD5 auth** | ⭐ ☐ |
| 15 | ⭐ Verify `show ntp status` → `synchronized, stratum 4` | ⭐ ☐ |
| 16 | ⭐⭐ Verify `show ntp associations` → dấu **`*`** và **`reach 377`** | ⭐⭐ ☐ |
| 17 | ⭐ `show clock detail` → `Time source is NTP`, **không có dấu `*`** | ⭐ ☐ |
| 18 | ⭐⭐ Tái hiện **key lệch** → `stratum 16`, `reach 0`, mất dấu `*` | ⭐⭐ ☐ |
| 19 | ⭐ Tái hiện **thiếu `ntp trusted-key`** → cùng triệu chứng | ☐ |
| 20 | ⭐ Tái hiện **chưa sync** → thấy dấu `*` trước giờ | ☐ |
| 21 | Bật `service timestamps log datetime msec localtime show-timezone` và xem log | ☐ |
| 22 | ⭐ `ntp access-group serve-only` + `peer` | ☐ |
| 23 | 🚀 (Tùy chọn) PIM-SM: thấy `(*,G)` với RP và `(S,G)` với flag `T` | 🚀 ☐ |
| 24 | 🚀 (Tùy chọn) `show ip rpf <source>` → chỉ ra RPF interface | 🚀 ☐ |
| 25 | Cố ý phá 1 thứ NAT, tự tìm ra bằng **quy trình 5 bước §10.3** trong 10 phút | ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 3** (thiếu route → NAT không gọi),
> **mục 7–8** (bẫy ACL với NAT), **mục 11–12** (NAT route-map dual-ISP), và **mục 16, 18** (NTP).
> Bỏ hoàn toàn mục 23–24 (PIM) nếu bám tiến độ — blueprint chỉ hỏi khái niệm.
>
> ⚠️ **Kết thúc Module-06B = kết thúc khối Infrastructure (30% đề).**
> Đây là **50% giá trị** của cả kỳ thi. Nếu Phần B của Module-02 → 06B đều tick được,
> bạn đã nắm phần lớn nhất và khó nhất của ENCOR.

---

## 🔗 14. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *IP Services* — NAT, NTP, và phần multicast |
| **Cisco doc** ⭐⭐ | ***NAT Order of Operation*** — ⭐ tài liệu gốc về thứ tự NAT-Routing. Search: `cisco nat order of operation` |
| **Cisco doc** ⭐ | *IP Addressing: NAT Configuration Guide* — Static/Dynamic NAT, PAT, NAT với route-map |
| **Cisco doc** ⭐ | *Configuring NAT for High Availability* / *NAT Load-Balancing with Multiple ISPs* — ⭐ dual-ISP NAT |
| **Cisco doc** | *Verifying NAT Operation and Basic NAT Troubleshooting* |
| **Cisco doc** | *IPv6 NAT64 Stateful Configuration Guide* · RFC 6296 (NPTv6) |
| **Cisco doc** ⭐ | *Network Management Configuration Guide* → chương *Configuring NTP* |
| **Cisco doc** ⭐ | *Use NTP to Synchronize Clocks* — ⭐ giải thích stratum và các ký hiệu trong `show ntp associations` |
| **Cisco doc** ⭐ | *IP Multicast Routing Configuration Guide* — chương *Configuring Basic IP Multicast*, *PIM Sparse Mode* |
| **Cisco doc** ⭐⭐ | ***Multicast Quick-Start Configuration Guide*** — ⭐ tài liệu tốt nhất để hiểu RPF, `(*,G)`, `(S,G)` |
| **Cisco doc** | *IGMP Snooping Configuration* · *Source Specific Multicast (SSM)* |
| **RFC 5905** | NTPv4 |
| **RFC 2236 / 3376** | IGMPv2 / IGMPv3 |
| **RFC 7761** | PIM-SM (Protocol Specification) |
| **Cisco Live** ⭐ | Search `Cisco Live IP multicast deployment` · `Cisco Live NAT design best practices` |
| **NetworkLessons** ⭐ | Loạt bài *NAT/PAT*, *NTP*, *Multicast IGMP*, *PIM Sparse Mode*, *RPF Check* — nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module IP Services · Keith Barker: search `Keith Barker NAT`, `Keith Barker multicast RPF` |
| **Wireshark** | Filter `ntp` (UDP 123 — xem stratum, reference ID) · `igmp` · `pim`. ⭐ Bắt gói 2 bên NAT để **thấy** địa chỉ bị dịch |
| **Forum** | https://community.cisco.com — search `nat not working no default route`, `port forward acl public ip`, `nat dual isp route-map`, `ntp stratum 16`, `multicast rpf failed` |

---

**➡️ Tiếp theo:** Module-07 — Wireless Enterprise
*(RF cơ bản · 802.11 · AP mode · WLC deployment · CAPWAP · FlexConnect · Roaming — **Tuần 12–13**)*

> ⚠️ **Lưu ý về Module-07:** PC 16 GB **không dựng nổi** WLC + AP. Module-07 sẽ dùng
> **DevNet Sandbox** (Catalyst 9800 always-on) làm Plan B — đã ghi trong [ROADMAP §1](ROADMAP.md).
