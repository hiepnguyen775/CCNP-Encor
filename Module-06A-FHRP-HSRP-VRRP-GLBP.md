# Module-06A — FHRP: HSRP, VRRP, GLBP & Object Tracking

> 🧭 **Lộ trình:** [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) → `[Bạn đang ở đây] Module-06A` → [Module-06B](Module-06B-NAT-NTP-Multicast.md) → Module-07 (Wireless)
>
> 📊 **Blueprint:**
> · **3.4.c — Configure first hop redundancy protocols, such as HSRP and VRRP** (Infrastructure 30%)
> · **1.1.b — High availability techniques such as redundancy, FHRP, and SSO** (Architecture 15%)
>
> ⏱️ **Tuần 11 (nửa đầu)** · 5 giờ

---

## ⭐ 0. Phạm vi — HSRP/VRRP cấu hình, GLBP chỉ hiểu

| Protocol | ENCOR yêu cầu | Thời gian |
|---|---|---|
| ⭐ **HSRP** | ⭐ **Cấu hình + verify + troubleshoot** | 2 giờ |
| ⭐ **VRRP** | ⭐ **Cấu hình + verify** | 1 giờ |
| 🟡 **GLBP** | 🟡 **Hiểu khái niệm + so sánh** (blueprint ghi *"such as HSRP and VRRP"*) | 30 phút |
| ⭐ **Object tracking + IP SLA** | ⭐ Kết hợp với FHRP — **rất hay hỏi** | 1 giờ |
| 🟡 **SSO / NSF / StackWise** | 🟡 Khái niệm HA (mục 1.1.b) | 30 phút |

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ Module-03 §2.4 (IP SLA + object tracking) — **bắt buộc** · Module-P0 §2.3 (VLAN/SVI) |
| **Lab** | 2× vIOS (cặp FHRP) + 1× vIOS-L2 + 1–2× VPCS |
| **RAM** | 2×512 + 768 = **~1.8 GB** ✅ |
| **Thời lượng** | 2h lý thuyết · 2.5h lab · 0.5h quiz |

---

## 📘 2. LÝ THUYẾT

### 2.1 FHRP giải quyết vấn đề gì

```
   KHÔNG CÓ FHRP                          ⭐ CÓ FHRP
   ─────────────                          ─────────
   PC: default gateway = 10.1.1.1         PC: default gateway = 10.1.1.1 (VIRTUAL IP)
                                                        │
   ┌──────┐         ┌──────┐              ┌──────┐  ┌──────┐
   │ R1   │         │ R2   │              │ R1   │  │ R2   │
   │.1    │         │.2    │              │.2    │  │.3    │
   └──┬───┘         └──┬───┘              └──┬───┘  └──┬───┘
      │  R1 chết →     │                     └────┬────┘
      │  PC MẤT MẠNG   │                    Virtual IP .1 + Virtual MAC
      │  (phải sửa tay │                    → R1 chết, R2 tiếp nhận
      │   gateway trên │                      ⭐ PC KHÔNG BIẾT GÌ
      │   TỪNG PC)     │
```

⭐ **Vấn đề cốt lõi:** PC chỉ có **một** default gateway. Router đó chết = mất mạng,
và bạn **không thể** đổi gateway trên hàng trăm PC.

⭐ **Giải pháp FHRP:** hai router **cùng chia sẻ một Virtual IP + Virtual MAC**.
PC trỏ vào Virtual IP. Router nào đang Active thì trả lời ARP cho Virtual IP đó.

| Thành phần | Nghĩa |
|---|---|
| ⭐ **Virtual IP (VIP)** | IP mà PC dùng làm default gateway |
| ⭐ **Virtual MAC (vMAC)** | MAC gắn với VIP. ⭐ **Router failover không đổi vMAC** → PC không cần ARP lại |
| **Active / Master** | Router đang thực sự forward traffic |
| **Standby / Backup** | Router chờ tiếp nhận |

⭐ **Vì sao vMAC quan trọng:** nếu failover mà MAC đổi, mọi PC phải chờ ARP cache hết hạn
(mặc định 4 giờ trên Windows!) → mất mạng rất lâu. Dùng **vMAC không đổi** → PC hoàn toàn
không nhận ra có gì thay đổi.

---

### 2.2 ⭐⭐ BẢNG SO SÁNH 3 FHRP — bảng quan trọng nhất module

| | ⭐ **HSRP** | ⭐ **VRRP** | 🟡 **GLBP** |
|---|---|---|---|
| **Chuẩn** | ⭐ **Cisco độc quyền** | ⭐ **Open standard** (RFC 3768 v2, RFC 5798 v3) | ⭐ **Cisco độc quyền** |
| **Đa vendor** | ❌ | ⭐ ✅ | ❌ |
| **Group number** | v1: **0–255** · v2: **0–4095** | **1–255** | **0–1023** |
| ⭐ **Virtual MAC** | v1: `0000.0C07.AC**XX**`<br>v2: `0000.0C9F.F**XXX**` | ⭐ `0000.5E00.01**XX**` | `0007.B400.**XXYY**` |
| ⭐ **Multicast** | v1: **224.0.0.2**<br>v2: **224.0.0.102** | ⭐ **224.0.0.18** | **224.0.0.102** |
| ⭐ **Transport** | **UDP 1985** (v1/v2) | ⭐ **IP protocol 112** | **UDP 3222** |
| **Vai trò** | **Active** / **Standby** / Listen | ⭐ **Master** / **Backup** | ⭐ **AVG** / **AVF** |
| **Số router hoạt động** | ⭐ **1** (Active) | ⭐ **1** (Master) | ⭐ **tối đa 4** (AVF) |
| ⭐ **Load balancing** | ❌ Chỉ theo VLAN/group | ❌ Chỉ theo VLAN/group | ⭐ ✅ **Tự động trong 1 group** |
| **Priority** | **0–255**, default **100** | **1–254**, default **100** (255 = IP owner) | **1–255**, default **100** |
| 🔴 ⭐ **Preempt mặc định** | 🔴 ⭐ **TẮT** | 🔴 ⭐ **BẬT** | ⭐ **TẮT** (AVG) |
| **Timer (hello/hold)** | **3 s / 10 s** | **1 s / ~3.6 s** (adv/master-down) | **3 s / 10 s** |
| **Hỗ trợ IPv6** | ✅ HSRPv2 | ✅ VRRPv3 | ✅ |
| **Authentication** | Plain text / MD5 | v2: plain (v3: bỏ) | MD5 |
| **Object tracking** | ✅ | ✅ | ✅ |

#### 🔴⭐ HAI BẪY ĐỀ SỐ 1 CỦA MODULE NÀY

> **1. Preempt:** ⭐ **HSRP TẮT mặc định · VRRP BẬT mặc định.**
> → HSRP: router priority cao bật lên sau **KHÔNG** chiếm quyền Active (giống DR của OSPF!)
> → VRRP: router priority cao bật lên sau ⭐ **CHIẾM quyền Master ngay**

> **2. Virtual MAC:** thuộc lòng 3 tiền tố
> - **HSRPv1:** `0000.0C07.AC` + group (hex, 2 số)
> - **HSRPv2:** `0000.0C9F.F` + group (hex, 3 số)
> - ⭐ **VRRP:** `0000.5E00.01` + VRID (hex, 2 số)
> - **GLBP:** `0007.B400.` + group + AVF number

**Ví dụ tính vMAC:**

| Protocol | Group | vMAC |
|---|:---:|---|
| HSRPv1 | 1 | `0000.0C07.AC01` |
| HSRPv1 | 10 | `0000.0C07.AC0A` *(10 = 0x0A)* |
| HSRPv2 | 10 | `0000.0C9F.F00A` |
| ⭐ **VRRP** | **1** | ⭐ `0000.5E00.0101` |
| ⭐ **VRRP** | **10** | ⭐ `0000.5E00.010A` |

---

### 2.3 ⭐ HSRP chi tiết

#### 6 trạng thái HSRP

```
INITIAL ──▶ LEARN ──▶ LISTEN ──▶ SPEAK ──▶ STANDBY ──▶ ACTIVE
```

| State | Nghĩa |
|---|---|
| **Initial** | Chưa bắt đầu (interface vừa lên, HSRP vừa cấu hình) |
| **Learn** | ⭐ Chưa biết Virtual IP — đang **chờ Active router** nói cho biết (khi bạn không cấu hình VIP) |
| **Listen** | Biết VIP, **nghe hello**, nhưng **không phải** Active/Standby |
| **Speak** | Đang **gửi hello**, tham gia bầu Active/Standby |
| **Standby** | ⭐ Ứng viên tiếp theo — sẵn sàng thay Active |
| ✅ **Active** | ⭐ Đang **forward traffic** cho Virtual IP |

⭐ **Trên 1 segment có nhiều router HSRP:** chỉ **1 Active**, **1 Standby**, còn lại ở **Listen**.

#### HSRPv1 vs HSRPv2

| | **HSRPv1** | ⭐ **HSRPv2** |
|---|---|---|
| Group | 0–255 | ⭐ **0–4095** |
| vMAC | `0000.0C07.AC**XX**` | ⭐ `0000.0C9F.F**XXX**` |
| Multicast IPv4 | **224.0.0.2** | ⭐ **224.0.0.102** |
| Multicast IPv6 | — | `FF02::66` |
| ⭐ **Millisecond timer** | ❌ | ⭐ ✅ |
| ⭐ **IPv6** | ❌ | ⭐ ✅ |
| Group number trong hello | Không | ⭐ Có (dễ troubleshoot) |
| Tương thích | — | ⚠️ **KHÔNG** tương thích v1 |

```
interface Vlan10
 standby version 2                       ! ⭐ phải đặt TRƯỚC khi cấu hình group > 255
 standby 10 ip 10.1.10.1
```
⚠️ **Đổi version = HSRP reset** → có ngắt ngắn. Và ⭐ **cả 2 router phải cùng version**.

#### Cấu hình HSRP đầy đủ

```
interface Vlan10
 ip address 10.1.10.2 255.255.255.0
 !
 standby version 2                                    ! ⭐ nên dùng v2
 standby 10 ip 10.1.10.1                              ! ⭐ Virtual IP
 standby 10 priority 110                              ! CAO thắng (default 100)
 standby 10 preempt                                   ! 🔴 PHẢI GÕ — mặc định TẮT!
 standby 10 preempt delay minimum 60                  ! ⭐ chờ 60s sau reboot mới preempt
 standby 10 timers 1 3                                ! hello 1s / hold 3s
 standby 10 timers msec 200 msec 750                  ! ⭐ hoặc millisecond
 standby 10 authentication md5 key-string MyHsrpKey   ! ⭐ MD5
 standby 10 name VLAN10-GW                            ! tên (tiện quản lý)
 standby 10 track 1 decrement 30                      ! ⭐ object tracking
```

⭐ **`preempt delay minimum`** — cực quan trọng ở production:
sau khi router reboot, interface lên **trước khi** routing protocol hội tụ.
Nếu preempt ngay → nó thành Active mà **chưa có route** → ⭐ **black hole**.
`preempt delay minimum 60` cho nó 60 giây để OSPF/BGP hội tụ trước.

**Kiểm tra:**
```
show standby                              ! ⭐ chi tiết mọi group
show standby brief                        ! ⭐ bảng gọn — dùng nhiều nhất
show standby Vlan10 10
show standby all
debug standby                             ! ⚠️ chỉ lab
debug standby events                      ! ⚠️
```

**Output mẫu `show standby brief`:**
```
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Vl10        10   110 P Active  local           10.1.10.3       10.1.10.1
Vl20        20   90  P Standby 10.1.20.3       local           10.1.20.1
```
⭐ **Đọc:**
- Cột `P` = ⭐ **đã cấu hình preempt** (không có `P` = preempt tắt!)
- `State Active` + `Active local` = router này đang Active
- `Standby 10.1.10.3` = IP của router standby

**Output mẫu `show standby Vlan10 10`:**
```
Vlan10 - Group 10 (version 2)
  State is Active
    2 state changes, last state change 00:05:12
  Virtual IP address is 10.1.10.1
  Active virtual MAC address is 0000.0c9f.f00a           ← ⭐ vMAC (HSRPv2, group 10)
    Local virtual MAC address is 0000.0c9f.f00a (v2 default)
  Hello time 3 sec, hold time 10 sec
    Next hello sent in 1.024 secs
  Authentication MD5, key-string
  Preemption enabled, delay min 60 secs
  Active router is local
  Standby router is 10.1.10.3, priority 100 (expires in 9.056 sec)
  Priority 110 (configured 110)
    Track object 1 state Up decrement 30                 ← ⭐ tracking
  Group name is "VLAN10-GW" (cfgd)
```

---

### 2.4 ⭐ VRRP chi tiết

#### 3 trạng thái VRRP

```
INITIALIZE ──▶ BACKUP ──▶ MASTER
```
⭐ Chỉ **3 state** (HSRP có **6**). Và chỉ có **Master** / **Backup** — không có "Listen"/"Speak".

#### Đặc điểm VRRP

| Đặc điểm | Chi tiết |
|---|---|
| ⭐ **Preempt** | ⭐ **BẬT mặc định** (ngược HSRP!) |
| ⭐ **Priority 255** | ⭐ Dành cho **IP address owner** — router có IP interface = Virtual IP |
| Priority 0 | ⭐ Master dùng để **chủ động nhường quyền** (gửi advertisement priority 0 khi shutdown) |
| Advertisement interval | **1 s** |
| **Master Down Interval** | ⭐ `3 × adv + skew_time` ≈ **3.6 s** |
| Skew time | `(256 − priority) / 256` — router priority cao phát hiện nhanh hơn |
| ⭐ **Authentication** | VRRPv2: plain text · ⭐ **VRRPv3: BỎ auth** (dùng bảo mật L2/L3 thay) |

#### Cấu hình VRRP — 2 cú pháp

```
! ═══ Cú pháp CỔ ĐIỂN (VRRPv2, hay xuất hiện trong đề) ═══
interface Vlan10
 ip address 10.1.10.2 255.255.255.0
 vrrp 10 ip 10.1.10.1                                  ! ⭐ Virtual IP
 vrrp 10 priority 110
 vrrp 10 preempt                                        ! (mặc định đã BẬT)
 vrrp 10 timers advertise 1
 vrrp 10 authentication text MyVrrpKey
 vrrp 10 track 1 decrement 30
 vrrp 10 description VLAN10-GW

! ═══ Cú pháp MỚI (VRRPv3, hỗ trợ IPv6) ═══
fhrp version vrrp v3                                    ! ⭐ global
!
interface Vlan10
 vrrp 10 address-family ipv4
  address 10.1.10.1 primary
  priority 110
  preempt delay minimum 60
  timers advertise 1000                                 ! millisecond
  track 1 decrement 30
  exit-vrrp
 !
 vrrp 10 address-family ipv6
  address FE80::1 primary
  address 2001:DB8:10::1
  exit-vrrp
```

**Kiểm tra:**
```
show vrrp                                 ! chi tiết
show vrrp brief                           ! ⭐ bảng gọn
show vrrp interface Vlan10
show fhrp verbose                          ! ⭐ mọi FHRP trên router
debug vrrp all                             ! ⚠️ chỉ lab
```

**Output mẫu `show vrrp brief`:**
```
Interface          Grp Pri Time  Own Pre State   Master addr     Group addr
Vl10               10  110 3570       Y   Master 10.1.10.2       10.1.10.1
Vl20               20  100 3609       Y   Backup 10.1.20.3       10.1.20.1
```
⭐ **Đọc:** `Own` = IP address owner (priority 255) · `Pre` = **preempt** (`Y` = bật — **mặc định**) ·
`Time` = master down interval (ms)

---

### 2.5 🟡 GLBP — load balancing tự động

⭐ **Điểm khác biệt duy nhất đáng nhớ:** HSRP/VRRP chỉ có **1 router forward**.
GLBP cho ⭐ **tối đa 4 router cùng forward** trong **cùng một group**.

#### Cơ chế — AVG và AVF

```
                    ⭐ AVG (Active Virtual Gateway) — 1 per group
                    Nhiệm vụ: TRẢ LỜI ARP cho Virtual IP
                              nhưng trả về vMAC KHÁC NHAU cho từng host
                              
   PC1 ARP "10.1.1.1?" ──▶ AVG trả: vMAC1 (0007.B400.0A01) ──▶ PC1 dùng R1
   PC2 ARP "10.1.1.1?" ──▶ AVG trả: vMAC2 (0007.B400.0A02) ──▶ PC2 dùng R2
   PC3 ARP "10.1.1.1?" ──▶ AVG trả: vMAC1 ──▶ PC3 dùng R1
   PC4 ARP "10.1.1.1?" ──▶ AVG trả: vMAC2 ──▶ PC4 dùng R2
   
   ⭐ AVF (Active Virtual Forwarder) — tối đa 4/group, mỗi cái 1 vMAC
```

| Vai | Số lượng | Nhiệm vụ |
|---|:---:|---|
| ⭐ **AVG** | **1** / group | ⭐ Trả lời ARP cho VIP, **phân bổ vMAC** cho từng host. Cũng làm AVF |
| ⭐ **AVF** | ⭐ **tối đa 4** / group | ⭐ Forward traffic của các host đã được gán vMAC của mình |

⭐ **Bầu AVG:** priority CAO nhất (default 100), tie → **IP CAO nhất**.

#### 3 chế độ load balancing

| Chế độ | Cách chia | Dùng khi |
|---|---|---|
| ⭐ **`round-robin`** *(mặc định)* | Lần lượt từng host một vMAC | ⭐ Mặc định, phân bố đều nhất |
| **`weighted`** | Theo **weight** cấu hình (router mạnh nhận nhiều hơn) | Router có năng lực khác nhau |
| **`host-dependent`** | Hash theo **MAC của host** → host luôn dùng cùng 1 AVF | ⭐ Cần host luôn đi cùng đường (NAT/firewall stateful) |

```
interface Vlan10
 ip address 10.1.10.2 255.255.255.0
 glbp 10 ip 10.1.10.1
 glbp 10 priority 110                        ! bầu AVG
 glbp 10 preempt
 glbp 10 load-balancing round-robin          ! ⭐ chỉ AVG quyết định
 glbp 10 weighting 100 lower 80 upper 90     ! ⭐ weight + ngưỡng cho AVF
 glbp 10 weighting track 1 decrement 30
 glbp 10 authentication md5 key-string MyGlbpKey
```

**Kiểm tra:**
```
show glbp
show glbp brief                            ! ⭐ thấy cả AVG và từng AVF
show glbp Vlan10 10
```

**Output mẫu `show glbp brief`:**
```
Interface   Grp  Fwd Pri State    Address         Active router   Standby router
Vl10        10   -   110 Active   10.1.10.1       local           10.1.10.3
Vl10        10   1   -   Active   0007.b400.0a01  local           -
Vl10        10   2   -   Listen   0007.b400.0a02  10.1.10.3       -
```
⭐ **Đọc:**
- Dòng `Fwd = -` → vai trò **AVG** (Active = là AVG)
- Dòng `Fwd = 1`, `Fwd = 2` → ⭐ **các AVF**, mỗi cái có **vMAC riêng**
- ⭐ vMAC `0007.b400.0a01` = `0007.b400.` + group `0a` (10) + AVF `01`

⚠️ **Hạn chế của GLBP:** load balancing theo **host**, không theo **flow**.
Một host với traffic khổng lồ vẫn chỉ dùng 1 router. Và ⭐ **Cisco độc quyền**.

---

### 2.6 ⭐⭐ Object Tracking + FHRP — phần đề rất hay hỏi

#### 🔴 Vấn đề: FHRP chỉ theo dõi interface LOCAL

```
                       ┌── Uplink R1 CHẾT ──✂
                       │
   [PC]───[SW]───┬──[R1: HSRP Active, priority 110]───✂ Internet
                 │
                 └──[R2: HSRP Standby, priority 100]──── Internet ✅
```

⚠️ Interface **xuống LAN** của R1 vẫn `up` → HSRP thấy "mọi thứ ổn" → R1 **vẫn là Active**
→ ⭐ **traffic đi vào R1 rồi chết** — dù R2 hoàn toàn khỏe.

⭐ **Đây là lỗ hổng giống floating static route ở Module-03 §2.3.**

#### ⭐ Giải pháp: Object Tracking

**Hai kiểu tracking:**

| Kiểu | Lệnh | Theo dõi gì | Đánh giá |
|---|---|---|---|
| **Interface tracking** *(legacy)* | `standby 10 track Gi0/1 30` | Trạng thái **line-protocol** của interface | ⚠️ Chỉ biết interface up/down — **không biết đích còn sống** |
| ⭐ **Object tracking** | `track 1 interface Gi0/1 line-protocol`<br>`standby 10 track 1 decrement 30` | Object linh hoạt | ⭐ Khuyến nghị |
| ⭐⭐ **Object tracking + IP SLA** | `track 1 ip sla 1 reachability`<br>`standby 10 track 1 decrement 30` | ⭐ **PING THẬT tới đích** | ⭐⭐ **Chuẩn production** |
| **Route tracking** | `track 1 ip route 0.0.0.0 0.0.0.0 reachability` | Có default route trong RIB? | ⭐ Tốt và nhẹ |

#### ⭐ Cấu hình đầy đủ (kết hợp Module-03)

```
! ═══ 1. IP SLA — ping THẬT một đích trên Internet qua ĐÚNG uplink ═══
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1    ! ⭐ source-interface BẮT BUỘC
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now              ! ⭐ KHÔNG ĐƯỢC QUÊN

! ═══ 2. Track object ═══
track 1 ip sla 1 reachability
 delay down 3 up 10                                        ! ⭐ chống flapping

! (bổ sung) Track cả interface uplink
track 2 interface GigabitEthernet0/1 line-protocol

! (bổ sung) Track nhiều điều kiện — AND
track 10 list boolean and
 object 1
 object 2

! ═══ 3. Gắn vào HSRP ═══
interface Vlan10
 standby 10 ip 10.1.10.1
 standby 10 priority 110
 standby 10 preempt
 standby 10 track 10 decrement 30            ! ⭐ track fail → priority 110-30 = 80
```

⭐ **Cơ chế:** track `Down` → priority giảm **110 − 30 = 80** → thấp hơn R2 (100)
→ R2 **preempt** → R2 thành Active.

🔴 **Điều kiện bắt buộc:** ⭐ **R2 PHẢI có `preempt`** — nếu không, dù priority R1 giảm
thì R2 **vẫn không chiếm quyền** (HSRP preempt mặc định TẮT!).

#### ⭐ Tính decrement cho đúng

```
Priority R1 = 110 · Priority R2 = 100

decrement = 5   → 110-5  = 105 > 100 → ❌ KHÔNG failover
decrement = 10  → 110-10 = 100 = 100 → ⚠️ TIE (không đảm bảo)
decrement = 20  → 110-20 =  90 < 100 → ✅ Failover
decrement = 30  → 110-30 =  80 < 100 → ✅ Failover (⭐ có biên an toàn)
```

⭐ **Công thức:** `decrement > (priority_của_tôi − priority_của_router_kia)`.
Nên để **dư biên** — trong ví dụ trên, chọn 20–30 thay vì đúng 11.

**Kiểm tra:**
```
show track                                  ! ⭐ mọi track object
show track 1
show ip sla statistics 1                    ! ⭐ return code, successes
show standby Vlan10 10 | include Track|Priority
show standby brief
```

**Output mẫu `show track 1`:**
```
Track 1
  IP SLA 1 reachability
  Reachability is Up
    2 changes, last change 00:03:15
  Delay up 10 secs, down 3 secs
  Latest operation return code: OK
  Latest RTT (millisecs) 24
  Tracked by:
    HSRP Vlan10 10                           ← ⭐ xác nhận HSRP đang dùng track này
```

---

### 2.7 🟡 HA khác — SSO, NSF, StackWise (mục 1.1.b, describe)

| Kỹ thuật | Là gì | Bảo vệ khỏi |
|---|---|---|
| ⭐ **SSO** (Stateful Switchover) | 2 supervisor trong 1 chassis — **đồng bộ trạng thái**. Supervisor chính chết → phụ tiếp nhận **giữ nguyên state** | Lỗi supervisor |
| ⭐ **NSF** (Non-Stop Forwarding) | ⭐ **Data plane tiếp tục forward** trong lúc control plane restart | Downtime khi control plane khởi động lại |
| ⭐ **NSF + SSO** | Đi cùng nhau: SSO giữ state, NSF giữ forwarding | ⭐ Chuẩn HA trong chassis |
| **Graceful Restart** | Router nói với neighbor "tôi đang restart, đừng xóa route của tôi" | Hội tụ lại không cần thiết |
| ⭐ **StackWise** | Nhiều switch vật lý → ⭐ **1 switch logic** (1 control plane, 1 IP quản lý) | Lỗi 1 switch trong stack |
| ⭐ **StackWise Virtual / VSS** | 2 chassis lớn → 1 logic. ⭐ **Loại bỏ nhu cầu STP và FHRP** giữa 2 chassis | Lỗi 1 chassis |
| **MEC** (Multi-chassis EtherChannel) | EtherChannel trải trên 2 chassis của VSS/StackWise Virtual | Lỗi 1 chassis, không cần STP block |

⭐ **Điểm quan trọng:** với **StackWise Virtual / VSS**, 2 switch thành **1 thiết bị logic**
→ ⭐ **không cần FHRP** (chỉ có 1 gateway), và ⭐ **không cần STP block** (MEC thay thế).
Đây là hướng thiết kế campus hiện đại.

```
show redundancy states                     ! SSO state
show redundancy                            ! chi tiết
show switch                                ! StackWise
show switch stack-ports
```

---

## 📖 3. HIỂU RÕ HƠN

### 3.1 FHRP như số điện thoại tổng đài

PC được cho **một số hotline: `10.1.1.1`** (Virtual IP).

- **Không có FHRP:** hotline là số **di động cá nhân** của anh R1. Anh R1 nghỉ → không ai nghe.
  Muốn sửa → gọi từng khách hàng đổi số. Bất khả thi.
- ⭐ **Có FHRP:** hotline là **số tổng đài**. Anh R1 nghỉ → anh R2 nhấc máy.
  ⭐ **Khách hàng không biết gì cả**, vẫn gọi số cũ.

Và **Virtual MAC** = ⭐ **cái máy điện thoại vật lý** ở tổng đài. Đổi người nghe nhưng
**không đổi máy** → khách không phải quay số lại (không phải ARP lại).

🧠 **Một câu để nhớ:** *FHRP không làm router dự phòng nhanh hơn — nó làm **PC không cần biết**
có bao nhiêu router. Toàn bộ giá trị nằm ở chỗ đó.*

### 3.2 Preempt — "chiếm lại ghế" và vì sao HSRP tắt mặc định

**Preempt** = *"tôi có priority cao hơn, tôi **đòi lại ghế Active ngay**"*.

| | HSRP (⭐ **TẮT**) | VRRP (⭐ **BẬT**) |
|---|---|---|
| Triết lý | ⭐ **Ổn định trước** — đang chạy tốt thì đừng đổi | ⭐ **Tối ưu trước** — ai xứng đáng thì lên |
| Ví von | *"Ai đang ngồi thì cứ ngồi"* | *"Người có thâm niên cao vào là phải nhường ghế"* |
| Giống | ⭐ **DR/BDR của OSPF** (non-preemptive) | Ngược lại |

⚠️ **Hệ quả thực tế của HSRP tắt preempt:** bạn đặt R1 priority 110 (muốn nó Active),
nhưng R2 lên trước → **R2 thành Active** → R1 lên sau, priority cao hơn, mà ⭐ **vẫn là Standby**.
Bạn tưởng cấu hình sai.

🧠 **Một câu để nhớ:** ⭐ ***HSRP: không gõ `preempt` thì priority vô nghĩa.***
*VRRP: không cần gõ, nó tự preempt.*

### 3.3 ⭐ `preempt delay minimum` — bài học từ sự cố thật

Router R1 reboot. Thứ tự sự việc:

| Giây | Chuyện gì | Vấn đề |
|:---:|---|---|
| 0 | Router boot | |
| 30 | ⭐ **Interface LAN lên** → HSRP thấy priority 110 → **preempt → Active ngay** | ⚠️ |
| 30–90 | OSPF/BGP **đang hội tụ**, R1 ⭐ **chưa có route ra Internet** | 🔴 |
| — | ⭐ **Toàn bộ traffic của VLAN đi vào R1 → DROP** | 🔴 **BLACK HOLE 60 giây** |
| 90 | Routing hội tụ xong | Giờ mới ổn |

⭐ **Sửa:** `standby 10 preempt delay minimum 90` → R1 **chờ 90 giây** sau khi interface lên
mới được preempt → routing có thời gian hội tụ trước.

🧠 **Một câu để nhớ:** *"Interface up" ≠ "router sẵn sàng forward". `preempt delay minimum`
là khoảng lặng để router **hít một hơi** trước khi nhận trách nhiệm.*

### 3.4 GLBP như quầy thu ngân có người điều phối

**HSRP/VRRP:** siêu thị có 4 quầy nhưng ⭐ **chỉ mở 1 quầy**. 3 quầy kia là *"nhân viên đứng chờ"*.

⭐ **GLBP:** có ⭐ **một người điều phối (AVG)** đứng ở cửa.
Khách vào hỏi *"thanh toán ở đâu?"* → người điều phối chỉ **luân phiên** quầy 1, quầy 2, quầy 1, quầy 2…
→ ⭐ **cả 4 quầy đều mở**.

⚠️ **Hạn chế:** người điều phối chia theo **khách**, không theo **giỏ hàng**.
Một khách mua 500 món vẫn chỉ dùng 1 quầy → ⭐ **elephant flow** không chia được
(giống hạn chế của EtherChannel ở Module-02 §7.4).

🧠 **Một câu để nhớ:** *GLBP không chia **traffic**, nó chia **host**.
Và nó là Cisco-only — nên ở mạng đa vendor, cách load-balance thật là
**VRRP + nhiều group theo VLAN**, hoặc tốt hơn là **StackWise Virtual** (không cần FHRP nữa).*

### 3.5 Vì sao FHRP cần object tracking

FHRP nhìn được ⭐ **chỉ interface của chính nó xuống LAN**. Nó ⭐ **không biết gì** về
đường ra Internet.

**Ví von:** người gác cổng chỉ kiểm tra ⭐ **cánh cổng có mở không**.
Anh ta ⭐ **không biết** con đường phía sau cổng đã sập.
→ Vẫn hướng dẫn khách vào cổng của mình → khách đi vào rồi ⭐ **mắc kẹt**.

⭐ **Object tracking + IP SLA** = trang bị cho người gác cổng một cái **điện thoại**:
*"để tôi gọi thử đầu bên kia xem đường có thông"*. Không ai trả lời → hạ priority →
nhường ghế cho người kia.

🧠 **Một câu để nhớ:** ⭐ ***FHRP không có tracking = HA giả.***
*Đây là cùng một bài học với floating static ở Module-03: **interface up ≠ đích còn sống**.*

---

## 🧪 4. LAB 06A

### 4.1 Topology

```
                      Internet (giả lập)
                    ┌──────────────────┐
                    │     R-ISP        │  Lo8: 8.8.8.8/32
                    │  (AS/router ngoài)│  Lo9: 9.9.9.9/32
                    └───┬──────────┬───┘
       203.0.113.0/30   │          │   198.51.100.0/30
                    Gi0/1│          │Gi0/1
                    ┌───┴───┐  ┌───┴───┐
                    │  R1   │  │  R2   │
                    │HSRP   │  │HSRP   │
                    │pri 110│  │pri 100│
                    └───┬───┘  └───┬───┘
                  Gi0/0 │          │ Gi0/0
                        │          │
                    ┌───┴──────────┴───┐
                    │       SW1        │  VLAN 10, VLAN 20
                    └────────┬─────────┘
                             │ Gi0/3 (access VLAN 10)
                          [PC1]  10.1.10.100/24  GW 10.1.10.1
```

| Node | Interface | IP | Vai trò |
|---|---|---|---|
| **R1** | Gi0/0.10 | 10.1.10.2/24 | ⭐ HSRP Active VLAN 10 (pri 110) |
| | Gi0/0.20 | 10.1.20.2/24 | HSRP Standby VLAN 20 (pri 90) |
| | Gi0/1 | 203.0.113.1/30 | Uplink → R-ISP |
| **R2** | Gi0/0.10 | 10.1.10.3/24 | HSRP Standby VLAN 10 (pri 100) |
| | Gi0/0.20 | 10.1.20.3/24 | ⭐ HSRP Active VLAN 20 (pri 110) |
| | Gi0/1 | 198.51.100.1/30 | Uplink → R-ISP |
| **SW1** | Gi0/0, Gi0/1 | — | Trunk tới R1, R2 |
| | Gi0/3 | — | Access VLAN 10 → PC1 |
| **R-ISP** | Gi0/1, Gi0/2 | 203.0.113.2, 198.51.100.2 | Giả lập Internet |
| | Lo8 | 8.8.8.8/32 | Đích để IP SLA ping |

**RAM: 3× vIOS (1.5 GB) + 1× vIOS-L2 (768 MB) + VPCS ≈ 2.3 GB** ✅

> 💡 Dùng **router-on-a-stick** (sub-interface) trên R1/R2 để tiết kiệm interface —
> đúng như bạn đã làm ở Module-P0 LAB P0-2.

### 4.2 Config nền

**SW1:**
```
enable
configure terminal
hostname SW1
no ip domain lookup
!
vlan 10
 name USERS-A
vlan 20
 name USERS-B
vlan 999
 name NATIVE-UNUSED
exit
!
interface range GigabitEthernet0/0 - 1
 description ---> TRUNK to R1/R2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
!
interface GigabitEthernet0/3
 description ---> PC1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R1:**
```
enable
configure terminal
hostname R1
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> TRUNK to SW1
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 description ---> VLAN 10 gateway
 encapsulation dot1Q 10
 ip address 10.1.10.2 255.255.255.0
!
interface GigabitEthernet0/0.20
 description ---> VLAN 20 gateway
 encapsulation dot1Q 20
 ip address 10.1.20.2 255.255.255.0
!
interface GigabitEthernet0/1
 description ---> UPLINK to R-ISP
 ip address 203.0.113.1 255.255.255.252
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 203.0.113.2
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**R2:** giống R1, đổi:
- `Gi0/0.10` → `10.1.10.3/24`
- `Gi0/0.20` → `10.1.20.3/24`
- `Gi0/1` → `198.51.100.1/30`
- `ip route 0.0.0.0 0.0.0.0 198.51.100.2`

**R-ISP:**
```
enable
configure terminal
hostname R-ISP
no ip domain lookup
!
interface Loopback8
 ip address 8.8.8.8 255.255.255.255
interface Loopback9
 ip address 9.9.9.9 255.255.255.255
!
interface GigabitEthernet0/1
 description ---> To R1
 ip address 203.0.113.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description ---> To R2
 ip address 198.51.100.2 255.255.255.252
 no shutdown
!
! Route về LAN (để ping 2 chiều được trong lab — thực tế sẽ NAT, xem 06B)
ip route 10.1.10.0 255.255.255.0 203.0.113.1
ip route 10.1.20.0 255.255.255.0 198.51.100.1
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

**PC1 (VPCS):**
```
ip 10.1.10.100/24 10.1.10.1
save
```
⭐ Gateway = **`10.1.10.1`** = **Virtual IP**, không phải IP thật của R1/R2.

---

### Bước 1 — ⭐ HSRP cơ bản + chứng minh bẫy preempt

#### 1a) Cấu hình HSRP (cố ý CHƯA bật preempt)

```
! ═══ R1 ═══
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  standby version 2
R1(config-subif)#  standby 10 ip 10.1.10.1
R1(config-subif)#  standby 10 priority 110
R1(config-subif)#  standby 10 name VLAN10-GW
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  standby version 2
R1(config-subif)#  standby 20 ip 10.1.20.1
R1(config-subif)#  standby 20 priority 90
R1(config-subif)#  standby 20 name VLAN20-GW

! ═══ R2 ═══
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)#  standby version 2
R2(config-subif)#  standby 10 ip 10.1.10.1
R2(config-subif)#  standby 10 priority 100
R2(config-subif)#  standby 10 name VLAN10-GW
R2(config-subif)# exit
R2(config)# interface GigabitEthernet0/0.20
R2(config-subif)#  standby version 2
R2(config-subif)#  standby 20 ip 10.1.20.1
R2(config-subif)#  standby 20 priority 110
R2(config-subif)#  standby 20 name VLAN20-GW
```

#### 1b) Kiểm tra

```
R1# show standby brief
```
**Output mẫu:**
```
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Gi0/0.10    10   110   Active  local           10.1.10.3       10.1.10.1
Gi0/0.20    20   90    Standby 10.1.20.3       local           10.1.20.1
```
⭐ **Chú ý: cột `P` TRỐNG** → ⭐ **preempt CHƯA được bật**.

```
R1# show standby GigabitEthernet0/0.10 10
```
**Output mẫu (dòng quan trọng):**
```
GigabitEthernet0/0.10 - Group 10 (version 2)
  State is Active
  Virtual IP address is 10.1.10.1
  Active virtual MAC address is 0000.0c9f.f00a           ← ⭐ vMAC
  Hello time 3 sec, hold time 10 sec
  Preemption disabled                                     ← ⭐ TẮT!
  Active router is local
  Standby router is 10.1.10.3, priority 100
  Priority 110 (configured 110)
  Group name is "VLAN10-GW" (cfgd)
```

⭐ **Tính lại vMAC để xác nhận:**
`0000.0C9F.F` + group 10 = `0x00A` → ⭐ **`0000.0c9f.f00a`** ✅ (HSRPv2)

**Xem trên PC1:**
```
PC1> arp
! 00:00:0c:9f:f0:0a  10.1.10.1  expires in ...        ← ⭐ vMAC, không phải MAC R1
PC1> ping 8.8.8.8
! ✅ thành công
PC1> trace 8.8.8.8
! 1  10.1.10.1  ...        ← qua Virtual IP
```

#### 1c) ⭐⭐ CHỨNG MINH BẪY PREEMPT

```
! Cắt HSRP trên R1 để R2 lên Active
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)# shutdown
! chờ 10 giây
R2# show standby brief | include Gi0/0.10
Gi0/0.10    10   100   Active  local           unknown         10.1.10.1
```
✅ R2 thành **Active** (đúng — R1 mất).

```
! Bật lại R1
R1(config-subif)# no shutdown
! chờ 20 giây
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   110   Standby 10.1.10.3       local           10.1.10.1
```

⭐⭐ **KẾT QUẢ: R1 có priority 110 (cao hơn) nhưng vẫn là `Standby`!**
R2 (priority 100) ⭐ **vẫn là Active**.

🎓 **Đây chính là bẫy đề:** HSRP ⭐ **preempt TẮT mặc định** → priority **vô nghĩa** nếu không gõ `preempt`.

#### 1d) Bật preempt và xem lại

```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  standby 10 preempt
R1(config-subif)#  standby 10 preempt delay minimum 30       ! ⭐ chống black hole
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  standby 20 preempt
R1(config-subif)#  standby 20 preempt delay minimum 30

! ⭐ R2 CŨNG PHẢI bật preempt (để tracking ở bước 3 hoạt động)
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)#  standby 10 preempt
R2(config-subif)#  standby 10 preempt delay minimum 30
R2(config-subif)# exit
R2(config)# interface GigabitEthernet0/0.20
R2(config-subif)#  standby 20 preempt
R2(config-subif)#  standby 20 preempt delay minimum 30
```

```
R1# show standby brief
```
**Output mẫu:**
```
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Gi0/0.10    10   110 P Active  local           10.1.10.3       10.1.10.1
Gi0/0.20    20   90  P Standby 10.1.20.3       local           10.1.20.1
```
⭐ **Cột `P` đã xuất hiện** · R1 đã **chiếm lại** Active cho VLAN 10.

⭐ **Và load-balancing theo VLAN đã hoạt động:**

| VLAN | Active | Standby |
|:---:|---|---|
| **10** | ⭐ **R1** (pri 110) | R2 (pri 100) |
| **20** | ⭐ **R2** (pri 110) | R1 (pri 90) |

→ Traffic VLAN 10 đi qua R1, VLAN 20 đi qua R2 → ⭐ **cả 2 uplink đều được dùng**.
(HSRP/VRRP **không** load-balance trong 1 group — nhưng load-balance được **theo VLAN**.)

✅ **Checkpoint bước 1:**

| Kiểm tra | Mong đợi |
|---|---|
| PC1 ping `8.8.8.8` thành công qua Virtual IP | ✅ |
| `arp` trên PC1 hiện **vMAC** `00:00:0c:9f:f0:0a` | ⭐ ✅ |
| ⭐ Không có `preempt` → priority cao **vẫn là Standby** | ⭐ ✅ |
| Sau khi bật `preempt` → cột `P` xuất hiện, R1 chiếm lại Active | ⭐ ✅ |
| VLAN 10 Active = R1 · VLAN 20 Active = R2 | ⭐ ✅ |

---

### Bước 2 — ⭐ Test failover & đo downtime

**a) Ping liên tục từ PC1:**
```
PC1> ping 8.8.8.8 -c 200
```

**b) Cắt HSRP Active (R1) — cách 1: shutdown sub-interface**
```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)# shutdown
```
⭐ **Đếm số gói mất.**

```
R2# show standby brief | include Gi0/0.10
Gi0/0.10    10   100 P Active  local           unknown         10.1.10.1
R2# show logging | include HSRP
%HSRP-5-STATECHANGE: GigabitEthernet0/0.10 Grp 10 state Standby -> Active
```

**c) Bật lại và đo lại với timer nhanh:**
```
R1(config-subif)# no shutdown
! chờ ổn định (30s preempt delay)
!
! ⭐ Đặt timer nhanh — PHẢI đặt CẢ 2 ROUTER
R1(config-subif)# standby 10 timers msec 200 msec 750
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)# standby 10 timers msec 200 msec 750
```
Lặp lại bài đo.

⭐ **BẢNG KẾT QUẢ — điền vào:**

| Timer | Số gói ping mất | Downtime (~) |
|---|:---:|---|
| Mặc định (hello 3 s / hold 10 s) | | |
| ⭐ msec 200 / msec 750 | | |

**Kết quả mong đợi:** mặc định mất ~10 gói (10 s) · timer nhanh mất **1–2 gói** (<1 s).

> ⚠️ **Cảnh báo production:** timer millisecond tốn CPU. Với nhiều VLAN (VD 50 group HSRP)
> có thể làm CPU cao. ⭐ **Thay bằng BFD:**
> ```
> interface Gi0/0.10
>  bfd interval 300 min_rx 300 multiplier 3
>  standby bfd
> ```

**d) Trả timer về mặc định:**
```
R1(config-subif)# no standby 10 timers
R2(config-subif)# no standby 10 timers
```

---

### Bước 3 — ⭐⭐ Object Tracking + IP SLA (phần giá trị nhất)

#### 3a) 🔴 Tái hiện lỗ hổng: uplink chết mà HSRP không biết

```
! Cắt uplink của R1 (interface hướng Internet), KHÔNG cắt interface LAN
R1(config)# interface GigabitEthernet0/1
R1(config-if)# shutdown
```

```
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   110 P Active  local           10.1.10.3       10.1.10.1
```
⭐⭐ **R1 VẪN LÀ ACTIVE!** — vì interface LAN `Gi0/0.10` vẫn `up`.

```
PC1> ping 8.8.8.8
! ❌ FAIL 100%
```
🔴 **BLACK HOLE:** traffic đi vào R1, R1 không có đường ra → **drop hết**.
Trong khi R2 hoàn toàn khỏe.

```
R1# show ip route 0.0.0.0
! % Network not in table                    ← R1 mất default route
```

> ⭐ Đây **chính xác** là cùng một lỗ hổng với floating static route (Module-03 §2.3 bước 3).
> **Ghi vào `SO-TAY-LOI.md`.**

**Bật lại:**
```
R1(config-if)# no shutdown
```

#### 3b) ⭐ Vá lỗ hổng — IP SLA + Track (trên CẢ R1 và R2)

```
! ═══════════════ R1 ═══════════════
R1(config)# ip sla 1
R1(config-ip-sla)#  icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R1(config-ip-sla-echo)#  frequency 5
R1(config-ip-sla-echo)#  timeout 2000
R1(config-ip-sla-echo)# exit
R1(config)# ip sla schedule 1 life forever start-time now      ! ⭐ ĐỪNG QUÊN
!
! Track 1: IP SLA (ping thật)
R1(config)# track 1 ip sla 1 reachability
R1(config-track)#  delay down 3 up 10
R1(config-track)# exit
!
! Track 2: interface uplink
R1(config)# track 2 interface GigabitEthernet0/1 line-protocol
R1(config-track)# exit
!
! Track 3: có default route trong RIB không
R1(config)# track 3 ip route 0.0.0.0 0.0.0.0 reachability
R1(config-track)# exit
!
! ⭐ Track 10: kết hợp CẢ BA bằng boolean AND
R1(config)# track 10 list boolean and
R1(config-track)#  object 1
R1(config-track)#  object 2
R1(config-track)#  object 3
R1(config-track)# exit
!
! Gắn vào HSRP
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  standby 10 track 10 decrement 30            ! 110-30 = 80 < 100 ✅
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  standby 20 track 10 decrement 30
```

```
! ═══════════════ R2 ═══════════════ (đối xứng, source-interface là uplink của R2)
R2(config)# ip sla 1
R2(config-ip-sla)#  icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R2(config-ip-sla-echo)#  frequency 5
R2(config-ip-sla-echo)#  timeout 2000
R2(config-ip-sla-echo)# exit
R2(config)# ip sla schedule 1 life forever start-time now
!
R2(config)# track 1 ip sla 1 reachability
R2(config-track)#  delay down 3 up 10
R2(config-track)# exit
R2(config)# track 2 interface GigabitEthernet0/1 line-protocol
R2(config-track)# exit
R2(config)# track 3 ip route 0.0.0.0 0.0.0.0 reachability
R2(config-track)# exit
R2(config)# track 10 list boolean and
R2(config-track)#  object 1
R2(config-track)#  object 2
R2(config-track)#  object 3
R2(config-track)# exit
!
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)#  standby 10 track 10 decrement 30
R2(config-subif)# exit
R2(config)# interface GigabitEthernet0/0.20
R2(config-subif)#  standby 20 track 10 decrement 30
```

#### 3c) Verify tracking

```
R1# show ip sla statistics 1
```
**Output mẫu:**
```
IPSLA operation id: 1
        Latest RTT: 4 milliseconds
Latest operation return code: OK
Number of successes: 18
Number of failures: 0
Operation time to live: Forever                    ← ⭐ đúng
```

```
R1# show track
```
**Output mẫu:**
```
Track 1
  IP SLA 1 reachability
  Reachability is Up
  ...
  Tracked by:
    Track List 10

Track 2
  Interface GigabitEthernet0/1 line-protocol
  Line protocol is Up
  ...
  Tracked by:
    Track List 10

Track 3
  IP route 0.0.0.0 0.0.0.0 reachability
  Reachability is Up (RIB)
  ...
  Tracked by:
    Track List 10

Track 10
  List boolean and
  Boolean AND is Up
    2 changes, last change 00:02:11
    object 1 Up
    object 2 Up
    object 3 Up
  Tracked by:
    HSRP GigabitEthernet0/0.10 10                  ← ⭐ HSRP đang dùng
    HSRP GigabitEthernet0/0.20 20
```
⭐ **`Tracked by: HSRP ...`** xác nhận liên kết đã đúng.

```
R1# show standby GigabitEthernet0/0.10 10 | include Priority|Track
  Priority 110 (configured 110)
    Track object 10 state Up decrement 30
```

#### 3d) ⭐⭐ TEST LẠI — giờ có failover

```
! Ping liên tục
PC1> ping 8.8.8.8 -c 100

! Cắt uplink R1 (interface LAN VẪN UP)
R1(config)# interface GigabitEthernet0/1
R1(config-if)# shutdown
```

**Quan sát R1 sau ~5–8 giây:**
```
R1#
%TRACK-6-STATE: 2 interface Gi0/1 line-protocol Up -> Down
%TRACK-6-STATE: 10 list boolean and Up -> Down
%TRACK-6-STATE: 1 ip sla 1 reachability Up -> Down
%HSRP-5-STATECHANGE: GigabitEthernet0/0.10 Grp 10 state Active -> Speak
%HSRP-5-STATECHANGE: GigabitEthernet0/0.10 Grp 10 state Speak -> Standby
```

```
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   80  P Standby 10.1.10.3       local           10.1.10.1
```
⭐⭐ **Priority giảm từ 110 → 80** (110 − 30) → thấp hơn R2 (100) → R2 **preempt** → R1 thành **Standby**.

```
R2# show standby brief | include Gi0/0.10
Gi0/0.10    10   100 P Active  local           10.1.10.2       10.1.10.1
```
✅ **R2 là Active.**

```
PC1> ping 8.8.8.8
! ✅ 100% — hoạt động lại
PC1> trace 8.8.8.8
! 1  10.1.10.1 ...       ← vẫn Virtual IP, nhưng giờ là R2 trả lời
```

⭐ **PC1 hoàn toàn không biết gì đã xảy ra** — vẫn dùng cùng IP, cùng vMAC.

**Test hồi phục:**
```
R1(config-if)# no shutdown
```
Chờ ~15 giây (frequency 5 + delay up 10):
```
R1#
%TRACK-6-STATE: 10 list boolean and Down -> Up
%HSRP-5-STATECHANGE: GigabitEthernet0/0.10 Grp 10 state Standby -> Active
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   110 P Active  local           10.1.10.3       10.1.10.1
```
✅ Priority về 110, R1 lấy lại Active.

⭐ **BẢNG SO SÁNH — điền vào:**

| Kịch bản | HSRP **không** tracking | ⭐ HSRP **có** tracking + IP SLA |
|---|:---:|:---:|
| Interface LAN down | ✅ Failover | ✅ Failover |
| ⭐ **Uplink down (LAN vẫn up)** | 🔴 **KHÔNG** — black hole | ⭐ ✅ **Failover** |
| ⭐ **Đích Internet chết, link vẫn up** | 🔴 **KHÔNG** | ⭐ ✅ **Failover** (nhờ IP SLA) |
| Số gói mất khi failover | — | |

✅ **Checkpoint bước 3:**

| Kiểm tra | Mong đợi |
|---|---|
| ⭐ Tái hiện được **black hole** khi chưa có tracking | ⭐ ✅ |
| `show ip sla statistics 1` → `OK`, `time to live: Forever` | ✅ |
| `show track 10` → `Boolean AND is Up`, ⭐ `Tracked by: HSRP ...` | ⭐ ✅ |
| Cắt uplink → priority **110 → 80** → R2 preempt → Active | ⭐⭐ ✅ |
| PC1 vẫn dùng **cùng gateway + cùng vMAC**, không biết gì | ⭐ ✅ |
| Bật lại → priority về 110 → R1 lấy lại Active | ✅ |

#### 3e) ⚠️ Tái hiện 3 lỗi tracking kinh điển

**Lỗi 1 — decrement quá nhỏ**
```
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)# standby 10 track 10 decrement 5        ! 110-5 = 105 > 100
```
Cắt uplink R1:
```
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   105 P Active  local           10.1.10.3       10.1.10.1
```
⚠️ **Priority 105 vẫn > 100** → ⭐ **KHÔNG failover** → black hole trở lại.

**Sửa:** `standby 10 track 10 decrement 30`

**Lỗi 2 — ⭐ R2 không bật preempt**
```
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)# no standby 10 preempt
```
Cắt uplink R1:
```
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   80    Active  local           10.1.10.3       10.1.10.1
```
⭐⭐ **R1 priority chỉ còn 80 mà VẪN LÀ ACTIVE!** — vì R2 **không có preempt** nên
không chiếm quyền.

🔴 **Bài học:** ⭐ **tracking chỉ hoạt động khi router KIA có `preempt`.**
Đây là cặp đôi bắt buộc: **tracking (bên A) + preempt (bên B)**.

**Sửa:** `R2(config-subif)# standby 10 preempt`

**Lỗi 3 — ⭐ IP SLA thiếu `source-interface`**
```
R1(config)# ip sla 1
R1(config-ip-sla)# icmp-echo 8.8.8.8                     ! ⚠️ bỏ source-interface
R1(config)# no ip sla schedule 1
R1(config)# ip sla schedule 1 life forever start-time now
```
Cắt uplink R1 — nhưng R1 vẫn có route tới `8.8.8.8` qua... không, R1 mất default route.

Mô phỏng rõ hơn: giữ uplink R1 up nhưng cắt **phía sau** (trên R-ISP):
```
R-ISP(config)# interface Loopback8
R-ISP(config-if)# shutdown
```
→ IP SLA fail (đúng). Nhưng nếu R1 có **đường thứ 2** tới `8.8.8.8` (VD qua R2 nếu có routing nội bộ)
thì IP SLA **không phát hiện** được lỗi của uplink R1.

⭐ **Bài học (giống Module-03 §4.6):** thiếu `source-interface` → SLA ping theo bảng route
→ có thể đi đường khác → ⭐ **không bao giờ phát hiện lỗi của đúng uplink cần kiểm tra**.

**Sửa & dọn:**
```
R-ISP(config)# interface Loopback8
R-ISP(config-if)# no shutdown
R1(config)# ip sla 1
R1(config-ip-sla)# icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R1(config)# no ip sla schedule 1
R1(config)# ip sla schedule 1 life forever start-time now
```

---

### Bước 4 — ⭐ VRRP (và chứng minh preempt BẬT mặc định)

#### 4a) Chuyển VLAN 20 sang VRRP

```
! ═══ R1 ═══
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  no standby 20 ip 10.1.20.1
R1(config-subif)#  no standby 20 priority 90
R1(config-subif)#  no standby 20 preempt
R1(config-subif)#  no standby 20 track 10 decrement 30
R1(config-subif)#  no standby 20 name VLAN20-GW
R1(config-subif)#  !
R1(config-subif)#  vrrp 20 ip 10.1.20.1
R1(config-subif)#  vrrp 20 priority 90
R1(config-subif)#  vrrp 20 description VLAN20-GW-VRRP
R1(config-subif)#  vrrp 20 track 10 decrement 30

! ═══ R2 ═══
R2(config)# interface GigabitEthernet0/0.20
R2(config-subif)#  no standby 20 ip 10.1.20.1
R2(config-subif)#  no standby 20 priority 110
R2(config-subif)#  no standby 20 preempt
R2(config-subif)#  no standby 20 track 10 decrement 30
R2(config-subif)#  no standby 20 name VLAN20-GW
R2(config-subif)#  !
R2(config-subif)#  vrrp 20 ip 10.1.20.1
R2(config-subif)#  vrrp 20 priority 110
R2(config-subif)#  vrrp 20 description VLAN20-GW-VRRP
R2(config-subif)#  vrrp 20 track 10 decrement 30
```

#### 4b) Kiểm tra & tính vMAC

```
R2# show vrrp brief
```
**Output mẫu:**
```
Interface          Grp Pri Time  Own Pre State   Master addr     Group addr
Gi0/0.20           20  110 3570      Y   Master 10.1.20.3       10.1.20.1
```
⭐ **Cột `Pre` = `Y`** → ⭐ **preempt BẬT — mà bạn KHÔNG gõ lệnh nào!**

```
R2# show vrrp interface GigabitEthernet0/0.20
```
**Output mẫu:**
```
GigabitEthernet0/0.20 - Group 20
  State is Master
  Virtual IP address is 10.1.20.1
  Virtual MAC address is 0000.5e00.0114                  ← ⭐ vMAC VRRP
  Advertisement interval is 1.000 sec
  Preemption enabled                                      ← ⭐ BẬT mặc định
  Priority is 110
    Track object 10 state Up decrement 30
  Master Router is 10.1.20.3 (local), priority is 110
  Master Advertisement interval is 1.000 sec
  Master Down interval is 3.570 sec
```

⭐ **Tính vMAC:** `0000.5E00.01` + VRID 20 = `0x14` → ⭐ **`0000.5e00.0114`** ✅

#### 4c) ⭐⭐ CHỨNG MINH preempt BẬT mặc định

```
! Cắt VRRP Master (R2)
R2(config)# interface GigabitEthernet0/0.20
R2(config-subif)# shutdown
! chờ 5 giây
R1# show vrrp brief | include Gi0/0.20
Gi0/0.20           20  90  3609      Y   Master 10.1.20.2       10.1.20.1
```
R1 (priority 90) thành **Master** — đúng.

```
! Bật lại R2
R2(config-subif)# no shutdown
! chờ 5 giây
R2# show vrrp brief | include Gi0/0.20
Gi0/0.20           20  110 3570      Y   Master 10.1.20.3       10.1.20.1
```
⭐⭐ **R2 CHIẾM LẠI Master NGAY** — dù bạn **chưa gõ lệnh `preempt` nào**.

⭐ **So sánh trực tiếp với HSRP ở Bước 1c:** cùng kịch bản, HSRP **KHÔNG** chiếm lại,
VRRP **CHIẾM LẠI ngay**.

🎓 **Bảng kết luận — điền vào:**

| | HSRP | VRRP |
|---|:---:|:---:|
| Gõ lệnh preempt? | | |
| Router priority cao bật sau có chiếm quyền? | | |
| vMAC prefix | | |
| Multicast | | |
| Transport | | |
| Số state | | |
| Tên vai trò | | |

<details><summary>Đáp án</summary>

| | ⭐ **HSRP** | ⭐ **VRRP** |
|---|:---:|:---:|
| Gõ lệnh preempt? | ⭐ **PHẢI gõ** (`standby X preempt`) | ⭐ **KHÔNG cần** (bật mặc định) |
| Priority cao bật sau chiếm quyền? | ⭐ **KHÔNG** (nếu chưa gõ preempt) | ⭐ **CÓ, ngay** |
| vMAC prefix | `0000.0C07.AC` (v1) / `0000.0C9F.F` (v2) | ⭐ **`0000.5E00.01`** |
| Multicast | 224.0.0.2 (v1) / **224.0.0.102** (v2) | ⭐ **224.0.0.18** |
| Transport | **UDP 1985** | ⭐ **IP protocol 112** |
| Số state | **6** (Initial→Learn→Listen→Speak→Standby→Active) | ⭐ **3** (Initialize→Backup→Master) |
| Tên vai trò | **Active** / Standby / Listen | ⭐ **Master** / Backup |
</details>

#### 4d) 🚀 VRRPv3 (tùy chọn — hỗ trợ IPv6)

```
R1(config)# fhrp version vrrp v3
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  no vrrp 20 ip 10.1.20.1
R1(config-subif)#  vrrp 20 address-family ipv4
R1(config-subif-vrrp)#   address 10.1.20.1 primary
R1(config-subif-vrrp)#   priority 90
R1(config-subif-vrrp)#   preempt delay minimum 30
R1(config-subif-vrrp)#   track 10 decrement 30
R1(config-subif-vrrp)#  exit-vrrp
```
Làm tương tự R2 (priority 110).

```
R2# show vrrp
R2# show fhrp verbose                       ! ⭐ xem MỌI FHRP trên router
```

---

### Bước 5 — 🟡 GLBP (tùy chọn, nếu image hỗ trợ)

> ℹ️ vIOS có thể **không hỗ trợ GLBP**. Nếu `glbp` không có trong CLI thì **bỏ qua** —
> ENCOR chỉ yêu cầu **hiểu khái niệm** GLBP, không cấu hình.

```
! Tạo VLAN 30 để test GLBP (thêm vào SW1 và trunk)
! ═══ R1 ═══
R1(config)# interface GigabitEthernet0/0.30
R1(config-subif)#  encapsulation dot1Q 30
R1(config-subif)#  ip address 10.1.30.2 255.255.255.0
R1(config-subif)#  glbp 30 ip 10.1.30.1
R1(config-subif)#  glbp 30 priority 110
R1(config-subif)#  glbp 30 preempt
R1(config-subif)#  glbp 30 load-balancing round-robin

! ═══ R2 ═══
R2(config)# interface GigabitEthernet0/0.30
R2(config-subif)#  encapsulation dot1Q 30
R2(config-subif)#  ip address 10.1.30.3 255.255.255.0
R2(config-subif)#  glbp 30 ip 10.1.30.1
R2(config-subif)#  glbp 30 priority 100
R2(config-subif)#  glbp 30 preempt
```

```
R1# show glbp brief
```
**Output mẫu:**
```
Interface   Grp  Fwd Pri State    Address         Active router   Standby router
Gi0/0.30    30   -   110 Active   10.1.30.1       local           10.1.30.3
Gi0/0.30    30   1   -   Active   0007.b400.1e01  local           -
Gi0/0.30    30   2   -   Listen   0007.b400.1e02  10.1.30.3       -
```
⭐ **Đọc:**
- `Fwd = -` → ⭐ vai trò **AVG** (R1 là AVG)
- `Fwd = 1` và `Fwd = 2` → ⭐ **2 AVF** với **2 vMAC khác nhau**
- vMAC `0007.b400.1e01` = `0007.b400.` + group `1e` (30) + AVF `01`

**⭐ Chứng minh load balancing — cần ≥ 2 PC:**
Thêm PC2, PC3 vào VLAN 30, rồi trên mỗi PC:
```
PC2> arp
! 00:07:b4:00:1e:01  10.1.30.1        ← AVF 1 (R1)
PC3> arp
! 00:07:b4:00:1e:02  10.1.30.1        ← ⭐ AVF 2 (R2) — vMAC KHÁC!
```
⭐ **Cùng một Virtual IP `10.1.30.1` nhưng 2 PC nhận 2 vMAC khác nhau**
→ PC2 đi qua R1, PC3 đi qua R2 → ⭐ **cả 2 router cùng forward**.

✅ **Checkpoint bước 5:** thấy được `Fwd 1` và `Fwd 2` với 2 vMAC khác nhau,
và 2 PC nhận 2 vMAC khác nhau cho cùng 1 VIP.

---

### Bước 6 — 🚀 Authentication & bảo mật FHRP

```
! ⭐ HSRP MD5 — phải khớp CẢ 2 ROUTER
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  standby 10 authentication md5 key-string HsrpS3cret2026
R2(config)# interface GigabitEthernet0/0.10
R2(config-subif)#  standby 10 authentication md5 key-string HsrpS3cret2026
```

**⚠️ Test key lệch:**
```
R2(config-subif)# standby 10 authentication md5 key-string WrongKey
```
```
R1# show logging | include HSRP
%HSRP-4-BADAUTH: Bad authentication from 10.1.10.3, group 10, remote state Active
```
⭐⭐ **Cả 2 router cùng tưởng mình là Active** → ⭐ **có 2 Active cùng lúc** →
duplicate Virtual IP, MAC flapping trên switch → **sự cố L2**.

```
R1# show standby brief | include Gi0/0.10
Gi0/0.10    10   110 P Active  local           unknown         10.1.10.1
R2# show standby brief | include Gi0/0.10
Gi0/0.10    10   100 P Active  local           unknown         10.1.10.1
```
🔴 **Hai Active** — đây là triệu chứng kinh điển của auth mismatch (hoặc mất kết nối L2 giữa 2 router).

**Sửa:**
```
R2(config-subif)# standby 10 authentication md5 key-string HsrpS3cret2026
```

**Bảo mật thêm — chống HSRP hijack:**
```
! Chỉ cho phép HSRP từ IP của router đối tác
R1(config)# ip access-list extended ACL-HSRP-PROTECT
R1(config-ext-nacl)#  permit udp host 10.1.10.3 host 224.0.0.102 eq 1985
R1(config-ext-nacl)#  deny   udp any host 224.0.0.102 eq 1985 log
R1(config-ext-nacl)#  permit ip any any
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)#  ip access-group ACL-HSRP-PROTECT in
```
⭐ Kèm theo: bật **DHCP snooping / Dynamic ARP Inspection** trên switch (Module-10).

---

## 💡 5. THỰC CHIẾN ĐI LÀM

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| 🔴 ⭐ **HSRP preempt** | Bẫy đề | 🔴 **LUÔN gõ `preempt` trên MỌI router HSRP.** Không gõ = priority vô nghĩa = thiết kế HA của bạn không hoạt động như hình vẽ |
| 🔴 ⭐ **`preempt delay minimum`** | Ít nhắc | 🔴 **BẮT BUỘC ở production.** Router reboot → interface lên trước routing → preempt ngay → **black hole 60 s**. Đặt 60–120 s (dài hơn thời gian hội tụ IGP/BGP của bạn) |
| 🔴 ⭐ **Object tracking** | Có lệnh | 🔴 **FHRP không có tracking = HA GIẢ.** Uplink chết mà LAN up thì FHRP không biết → black hole. Đây là lỗi thiết kế phổ biến nhất về FHRP |
| ⭐ **Track cái gì** | Interface | ⭐ Kết hợp `boolean and`: **(1) IP SLA ping đích thật** + **(2) interface uplink** + **(3) có default route trong RIB**. Một cái không đủ |
| 🔴 ⭐ **IP SLA `source-interface`** | Ít nhắc | 🔴 **BẮT BUỘC.** Thiếu nó → SLA ping theo bảng route → có thể đi đường khác → **không bao giờ phát hiện lỗi uplink cần kiểm** |
| ⭐ **Tracking + preempt là cặp đôi** | Không dạy | ⭐ Tracking giảm priority router A **chỉ có tác dụng nếu router B có `preempt`**. Thiếu một trong hai = vô ích |
| ⭐ **Tính decrement** | Không dạy | ⭐ `decrement > (pri_mình − pri_kia)`, **để dư biên**. Pri 110 vs 100 → dùng **20–30**, không dùng 11 |
| ⭐ **Load balancing thực tế** | GLBP | ⭐ Thực tế dùng **HSRP/VRRP + nhiều group theo VLAN**: VLAN chẵn Active ở R1, VLAN lẻ Active ở R2. Đơn giản, đa vendor, dễ hiểu hơn GLBP |
| ⭐ **Chọn HSRP hay VRRP** | Cả hai | ⭐ Mạng **thuần Cisco** → HSRP (nhiều tính năng hơn, quen thuộc). Mạng **đa vendor** → **VRRP** (chuẩn mở). Đã dùng cái nào thì **đừng trộn** |
| ⚠️ **GLBP** | Có trong sách | ⚠️ Ít dùng thực tế: Cisco-only, chia theo **host** không theo flow, và phức tạp hơn. ⭐ Xu hướng hiện đại là **StackWise Virtual/VSS** (bỏ FHRP hoàn toàn) |
| ⭐ **StackWise Virtual / VSS** | Khái niệm | ⭐ 2 switch → 1 logic → ⭐ **không cần FHRP, không cần STP block** (dùng MEC). Đây là thiết kế campus hiện đại — biết để không đề xuất giải pháp lạc hậu |
| **Timer nhanh** | Có lệnh | ⚠️ msec timer tốn CPU, nhất là khi có **50+ group HSRP**. ⭐ Dùng **BFD** (`standby bfd`) — phát hiện ms mà không tăng gánh nặng |
| ⭐ **Authentication** | Có lệnh | ⭐ Bật **MD5** trên mọi group FHRP. Không có auth = ai cắm laptop vào VLAN cũng ⭐ **chiếm được gateway** (HSRP hijack) → man-in-the-middle |
| ⭐ **Hai Active cùng lúc** | Không dạy | ⭐ Triệu chứng: MAC flapping trên switch, ping gateway lúc được lúc không. Nguyên nhân: **auth mismatch**, **mất kết nối L2 giữa 2 router**, hoặc **VLAN không được trunk** |
| ⭐ **`standby name`** / `vrrp description` | Không nhắc | ⭐ Đặt tên cho group — `show standby brief` dễ đọc hơn nhiều khi có 30 VLAN |
| ⭐ **Version** | v1/v2 | ⭐ **Luôn dùng HSRPv2** (group > 255, millisecond timer, IPv6). ⚠️ Cả 2 router phải cùng version, và đổi version gây reset |
| ⭐ **Đồng bộ với STP** | Không dạy | ⭐ **Root bridge STP và HSRP Active nên là CÙNG một switch** cho mỗi VLAN. Lệch nhau → traffic đi zigzag qua link giữa 2 switch (suboptimal) |
| ⭐ **Tài liệu hóa** | Không có | ⭐ Bảng bắt buộc: VLAN nào, VIP nào, Active ở đâu, priority bao nhiêu, track object nào, decrement bao nhiêu. Và **khớp với bảng STP root** |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | 🔴⭐ **HSRP preempt mặc định** | 🔴 ⭐ **TẮT.** Router priority cao bật sau **KHÔNG** chiếm Active. Phải gõ `standby X preempt` |
| 2 | 🔴⭐ **VRRP preempt mặc định** | 🔴 ⭐ **BẬT.** Ngược HSRP hoàn toàn |
| 3 | ⭐ vMAC **HSRPv1** | ⭐ **`0000.0C07.AC` + group (hex 2 số)** |
| 4 | ⭐ vMAC **HSRPv2** | ⭐ **`0000.0C9F.F` + group (hex 3 số)** |
| 5 | ⭐ vMAC **VRRP** | ⭐ **`0000.5E00.01` + VRID (hex 2 số)** |
| 6 | vMAC **GLBP** | `0007.B400.` + group + AVF number |
| 7 | ⭐ Multicast **HSRPv1 / v2** | ⭐ **224.0.0.2** / **224.0.0.102** |
| 8 | ⭐ Multicast **VRRP** | ⭐ **224.0.0.18** |
| 9 | Multicast **GLBP** | **224.0.0.102** (giống HSRPv2) |
| 10 | ⭐ Transport: HSRP / VRRP / GLBP | ⭐ **UDP 1985** / ⭐ **IP protocol 112** / **UDP 3222** |
| 11 | ⭐ Số state: HSRP / VRRP | ⭐ **6** / ⭐ **3** |
| 12 | ⭐ 6 state HSRP theo thứ tự | **Initial → Learn → Listen → Speak → Standby → Active** |
| 13 | 3 state VRRP | **Initialize → Backup → Master** |
| 14 | ⭐ Tên vai trò: HSRP / VRRP / GLBP | ⭐ **Active-Standby** / ⭐ **Master-Backup** / ⭐ **AVG-AVF** |
| 15 | ⭐ Timer: HSRP / VRRP / GLBP | ⭐ **3/10 s** / ⭐ **1 s adv, ~3.6 s master-down** / 3/10 s |
| 16 | Group range: HSRPv1 / v2 / VRRP / GLBP | **0–255** / **0–4095** / **1–255** / **0–1023** |
| 17 | Priority default (cả 3) | ⭐ **100**. HSRP 0–255 · VRRP 1–254 · GLBP 1–255 |
| 18 | ⭐ VRRP priority **255** nghĩa gì | ⭐ Dành cho **IP address owner** (router có IP interface = Virtual IP) |
| 19 | VRRP priority **0** nghĩa gì | ⭐ Master **chủ động nhường quyền** (gửi khi shutdown) |
| 20 | ⭐ Protocol nào **load balance trong 1 group** | ⭐ **CHỈ GLBP** (tối đa 4 AVF). HSRP/VRRP chỉ load-balance **theo VLAN/group** |
| 21 | ⭐ Protocol nào **chuẩn mở** | ⭐ **CHỈ VRRP** (RFC 3768/5798). HSRP và GLBP là **Cisco độc quyền** |
| 22 | ⭐ GLBP: AVG làm gì | ⭐ **Trả lời ARP** cho VIP, phân bổ **vMAC khác nhau** cho từng host. 1 AVG/group |
| 23 | GLBP: bao nhiêu AVF | ⭐ **Tối đa 4**/group |
| 24 | 3 chế độ load-balancing GLBP | ⭐ **round-robin** (mặc định) · **weighted** · **host-dependent** |
| 25 | 🔴⭐ **FHRP có biết uplink chết không?** | 🔴 ⭐ **KHÔNG** — chỉ biết interface **local** của mình. Cần ⭐ **object tracking** |
| 26 | ⭐ Tracking hoạt động thế nào | ⭐ Track `Down` → **giảm priority** theo `decrement` → router kia **preempt** |
| 27 | 🔴⭐ Tracking cần điều kiện gì để hoạt động | 🔴 ⭐ **Router KIA phải có `preempt`**. Tracking + preempt là **cặp đôi bắt buộc** |
| 28 | ⭐ Tính decrement | ⭐ `decrement > (pri_mình − pri_kia)`. Pri 110 vs 100 → decrement **≥ 11**, nên dùng **20–30** |
| 29 | ⭐ `preempt delay minimum` để làm gì | ⭐ Chờ N giây sau khi interface up mới preempt → **cho routing hội tụ trước** → chống black hole |
| 30 | 🔴 IP SLA thiếu `source-interface` | 🔴 SLA ping theo bảng route → có thể đi đường khác → ⭐ **không phát hiện được lỗi uplink** |
| 31 | 🔴 Quên `ip sla schedule` | 🔴 SLA **không chạy** → track Down → priority giảm sai |
| 32 | ⭐ Triệu chứng **2 Active cùng lúc** | ⭐ **Auth mismatch** · **mất kết nối L2 giữa 2 router** · **VLAN chưa được trunk**. Hậu quả: MAC flapping |
| 33 | HSRPv1 và v2 có tương thích? | ❌ **KHÔNG.** Cả 2 router phải cùng version |
| 34 | ⭐ VRRPv3 có authentication? | ⭐ **KHÔNG** — RFC 5798 **bỏ** auth (dùng bảo mật L2/L3 thay) |
| 35 | ⭐ SSO / NSF là gì | ⭐ **SSO** = 2 supervisor đồng bộ **state** · ⭐ **NSF** = **data plane tiếp tục forward** khi control plane restart |
| 36 | ⭐ StackWise Virtual / VSS loại bỏ nhu cầu gì | ⭐ **FHRP** (1 gateway logic) và ⭐ **STP block** (dùng MEC) |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ HSRP ═══
show standby brief                          ! ⭐⭐ LỆNH ĐẦU TIÊN — chú ý cột P (preempt)
show standby                                ! chi tiết mọi group
show standby <interface> <group>            ! ⭐ chi tiết 1 group: vMAC, timer, auth, track
show standby all
show standby internal
debug standby                               ! ⚠️ chỉ lab
debug standby events                        ! ⚠️
debug standby errors                        ! ⭐ hữu ích cho auth mismatch

! ═══ VRRP ═══
show vrrp brief                             ! ⭐ chú ý cột Pre (Y = preempt)
show vrrp
show vrrp interface <if>
show fhrp verbose                           ! ⭐ MỌI FHRP trên router
debug vrrp all                              ! ⚠️

! ═══ GLBP ═══
show glbp brief                             ! ⭐ thấy cả AVG (Fwd -) và AVF (Fwd 1,2..)
show glbp
show glbp <if> <group>

! ═══ TRACKING + IP SLA ═══
show track                                  ! ⭐⭐ mọi object + "Tracked by"
show track <n>
show track brief
show ip sla summary                         ! ⭐
show ip sla statistics <n>                  ! ⭐ return code, successes, time to live
show ip sla configuration <n>
debug track                                 ! ⚠️
debug ip sla trace <n>                      ! ⚠️

! ═══ NỀN TẢNG (đừng bỏ) ═══
show ip interface brief                     ! interface up?
show interfaces trunk                       ! ⭐ VLAN có được trunk? (trên switch)
show vlan brief
show arp                                    ! ⭐ vMAC có đúng?
show mac address-table | include 0000.0c    ! ⭐ vMAC học ở port nào (MAC flapping?)
show logging | include HSRP|VRRP|GLBP|TRACK|BADAUTH
show ip route 0.0.0.0                       ! ⭐ router Active có đường ra?
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | 🔴⭐ Router priority **cao** mà vẫn là **Standby** | 🔴 ⭐ **HSRP preempt TẮT** (mặc định) | ⭐ `show standby brief` → **cột `P` trống** | ⭐ `standby X preempt` |
| 2 | 🔴⭐ **Cả 2 router đều Active** | ⭐ **Auth mismatch** · mất kết nối L2 · VLAN chưa trunk · sub-interface sai `encapsulation` | ⭐ `show logging \| inc BADAUTH` · `show standby brief` **trên cả 2** · `show interfaces trunk` | Khớp auth · sửa trunk/VLAN · kiểm tra L2 |
| 3 | ⭐ Switch báo **MAC flapping** cho vMAC | Hệ quả của lỗi #2 (2 Active) | ⭐ `show mac address-table \| inc 0000.0c` → vMAC ở **2 port** | Sửa lỗi #2 |
| 4 | 🔴⭐ Uplink chết mà **HSRP không failover** → **black hole** | 🔴 ⭐ **Không có object tracking** | ⭐ `show standby <if> <grp> \| inc Track` → **không có dòng Track** | ⭐ Cấu hình IP SLA + `track` + `standby X track N decrement M` |
| 5 | ⭐ Có tracking, track **Down**, mà **vẫn Active** | ⭐ **decrement quá nhỏ** (priority sau khi giảm vẫn > router kia) | ⭐ `show standby brief` → xem `Pri` sau khi giảm | Tăng decrement (`> pri_mình − pri_kia`) |
| 6 | 🔴⭐ Track Down, priority đã giảm, mà **router kia không lên Active** | 🔴 ⭐ **Router KIA không có `preempt`** | ⭐ `show standby brief` **trên router kia** → cột `P` trống | ⭐ Bật `preempt` trên **cả 2** router |
| 7 | ⭐ Track luôn `Down` ngay khi cấu hình | ⭐ Quên **`ip sla schedule`** | ⭐ `show ip sla statistics <n>` → `Operation time to live: 0`, successes = 0 | ⭐ `ip sla schedule <n> life forever start-time now` |
| 8 | 🔴⭐ Track luôn `Up` dù uplink đã chết | 🔴 ⭐ **Thiếu `source-interface`** → SLA ping đường khác | ⭐ `show ip sla configuration <n>` → không có source | ⭐ `icmp-echo <ip> source-interface <uplink>` |
| 9 | ⭐ Priority nhấp nháy / HSRP flap liên tục | Thiếu `delay down/up` trong track · uplink flapping · `frequency` quá ngắn | `show track <n>` → số `changes` cao · `show logging` | `delay down 3 up 10` · sửa uplink · tăng frequency |
| 10 | 🔴⭐ Sau khi router reboot, mạng chết ~60 s | 🔴 ⭐ **Thiếu `preempt delay minimum`** — preempt trước khi routing hội tụ | `show standby <if> <grp> \| inc Preempt` → không có `delay` | ⭐ `standby X preempt delay minimum 90` |
| 11 | PC không ping được gateway | PC trỏ IP **thật** của router thay vì **Virtual IP** · VLAN sai | `show arp` trên PC · `show standby brief` | Đặt gateway = **Virtual IP** |
| 12 | HSRP lên nhưng traffic không ra Internet | Router Active **không có default route** | ⭐ `show ip route 0.0.0.0` **trên router Active** | Sửa routing · thêm tracking để failover |
| 13 | Không thấy neighbor HSRP (`Standby unknown`) | VLAN chưa trunk giữa 2 router · sub-interface `encapsulation` sai · ACL chặn 224.0.0.102 | `show interfaces trunk` · `show run int <subif>` · `show access-lists` | Sửa trunk/VLAN/ACL |
| 14 | Đổi HSRP version xong mất neighbor | ⭐ **v1 và v2 KHÔNG tương thích** | `show standby <if> <grp>` → xem `(version X)` cả 2 | Đặt **cùng version** trên cả 2 |
| 15 | `standby 300 ip ...` báo lỗi | HSRPv1 chỉ hỗ trợ group **0–255** | `show standby <if> <grp> \| inc version` | `standby version 2` trước |
| 16 | Timer msec làm CPU cao | Quá nhiều group với msec timer | `show processes cpu sorted` (M01) | ⭐ Dùng **BFD** (`standby bfd`) thay msec timer |
| 17 | ⭐ Traffic đi "zigzag" giữa 2 switch | ⭐ **STP root và HSRP Active ở 2 switch khác nhau** | `show spanning-tree vlan X \| inc root` vs `show standby brief` | ⭐ Đặt STP root và HSRP Active **cùng một switch** cho mỗi VLAN |
| 18 | GLBP: chỉ 1 vMAC được dùng | Chỉ có 1 AVF up · load-balancing = `host-dependent` với ít host | `show glbp brief` → xem các dòng `Fwd` | Kiểm tra AVF thứ 2 · đổi `round-robin` |

### 7.3 ⭐ Quy trình troubleshoot FHRP — 5 bước

```
0. LỆNH ĐẦU TIÊN
   show standby brief    (hoặc show vrrp brief / show glbp brief)
   → Đọc: Grp · Pri · ⭐ CỘT P (preempt) · State · Active/Standby · Virtual IP
        ↓
1. STATE CÓ ĐÚNG NHƯ THIẾT KẾ?
   ├─ Router priority cao mà là Standby  → ⭐ CỘT P TRỐNG? → thiếu `preempt`
   ├─ CẢ 2 đều Active                    → ⭐ auth mismatch / L2 / trunk / encapsulation
   ├─ Standby = "unknown"                → không thấy neighbor → L2 / VLAN / ACL
   └─ State đúng → sang bước 2
        ↓
2. CÓ TRACKING CHƯA?
   show standby <if> <grp> | include Track
   ├─ KHÔNG có dòng Track → 🔴 HA GIẢ → cấu hình IP SLA + track
   └─ Có → sang bước 3
        ↓
3. TRACKING CÓ HOẠT ĐỘNG?
   show track
   ├─ Không có "Tracked by: HSRP..."     → chưa gắn vào FHRP
   ├─ Reachability Down ngay từ đầu       → ⭐ quên `ip sla schedule`?
   │                                         show ip sla statistics <n> → time to live = 0?
   ├─ Luôn Up dù uplink chết              → ⭐ thiếu `source-interface`
   └─ Up/Down đúng → sang bước 4
        ↓
4. TRACK DOWN MÀ KHÔNG FAILOVER?
   show standby brief   (xem Pri SAU KHI giảm)
   ├─ Pri sau giảm vẫn > router kia       → ⭐ decrement quá nhỏ
   └─ Pri sau giảm < router kia           → ⭐ ROUTER KIA CÓ `preempt` KHÔNG?
                                             (show standby brief TRÊN ROUTER KIA, cột P)
        ↓
5. FAILOVER OK NHƯNG TRAFFIC VẪN CHẾT?
   show ip route 0.0.0.0   TRÊN ROUTER ACTIVE MỚI
   → Router Active mới có đường ra không?
   → show ip nat translations (nếu có NAT — xem Module-06B)
```

> ⭐ **Hai cột phải nhìn đầu tiên trong `show standby brief`:**
> **cột `P`** (preempt — thiếu là nguyên nhân #1) và **cột `Pri`** (priority thật sau khi tracking giảm).

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** 🔴 Bạn đặt R1 priority 110, R2 priority 100 cho HSRP group 10. R2 lên trước.
R1 lên sau. Ai là Active? Vì sao? Sửa thế nào?

<details><summary>Xem đáp án</summary>

⭐ **R2 là Active** (priority 100), R1 là **Standby** (priority 110).

**Vì sao:** ⭐ **HSRP có preempt TẮT mặc định.**
R2 lên trước → thành Active. R1 lên sau, priority cao hơn, nhưng ⭐ **không được phép chiếm quyền**
→ đành làm Standby.

⭐ **Đây là hành vi giống DR/BDR của OSPF** (non-preemptive, Module-04A §2.9).

**Chẩn đoán:**
```
show standby brief
! Interface   Grp  Pri P State   Active          Standby         Virtual IP
! Gi0/0.10    10   110   Standby 10.1.10.3       local           10.1.10.1
!                      ↑ CỘT P TRỐNG = preempt TẮT
```

**Sửa:**
```
interface Gi0/0.10
 standby 10 preempt
 standby 10 preempt delay minimum 60          ! ⭐ nên có luôn
```

⚠️ **So sánh với VRRP:** VRRP có ⭐ **preempt BẬT mặc định** → cùng kịch bản,
R1 sẽ **chiếm lại Master ngay** mà không cần gõ lệnh gì.

🧠 ⭐ ***"HSRP: không gõ `preempt` thì priority vô nghĩa."***
</details>

---

**Câu 2.** ⭐ Tính Virtual MAC cho: HSRPv1 group 5 · HSRPv2 group 100 · VRRP group 20

<details><summary>Xem đáp án</summary>

| Protocol | Group | Group (hex) | ⭐ vMAC |
|---|:---:|:---:|---|
| **HSRPv1** | 5 | `05` | ⭐ **`0000.0C07.AC05`** |
| **HSRPv2** | 100 | `064` | ⭐ **`0000.0C9F.F064`** |
| ⭐ **VRRP** | 20 | `14` | ⭐ **`0000.5E00.0114`** |

**Ba tiền tố phải thuộc:**

| Protocol | Tiền tố | Phần group |
|---|---|---|
| **HSRPv1** | `0000.0C07.AC` | + group hex **2 số** |
| **HSRPv2** | `0000.0C9F.F` | + group hex **3 số** |
| ⭐ **VRRP** | ⭐ **`0000.5E00.01`** | + VRID hex **2 số** |
| **GLBP** | `0007.B400.` | + group hex + AVF number |

⭐ **Mẹo:** `0000.0C` là **OUI của Cisco** → HSRP và GLBP đều bắt đầu bằng Cisco OUI.
⭐ **`0000.5E`** là OUI của **IANA** → VRRP là **chuẩn mở** nên dùng OUI của IANA, không phải Cisco.

**Verify trong lab:**
```
show standby <if> <grp> | include virtual MAC
show vrrp interface <if> | include Virtual MAC
show arp                                          ! trên PC
```
</details>

---

**Câu 3.** ⭐ Điền bảng đầy đủ so sánh HSRP / VRRP / GLBP: chuẩn, group range, vMAC, multicast,
transport, timer, số state, tên vai trò, load balancing, preempt mặc định.

<details><summary>Xem đáp án</summary>

| | ⭐ **HSRP** | ⭐ **VRRP** | 🟡 **GLBP** |
|---|---|---|---|
| **Chuẩn** | Cisco | ⭐ **Open (RFC 3768/5798)** | Cisco |
| **Group** | v1: 0–255 · v2: **0–4095** | **1–255** | 0–1023 |
| ⭐ **vMAC** | `0000.0C07.AC`+grp (v1)<br>`0000.0C9F.F`+grp (v2) | ⭐ **`0000.5E00.01`+VRID** | `0007.B400.`+grp+AVF |
| ⭐ **Multicast** | **224.0.0.2** (v1)<br>**224.0.0.102** (v2) | ⭐ **224.0.0.18** | **224.0.0.102** |
| ⭐ **Transport** | **UDP 1985** | ⭐ **IP proto 112** | **UDP 3222** |
| ⭐ **Timer** | **3 s / 10 s** | **1 s adv / ~3.6 s** | 3 s / 10 s |
| ⭐ **Số state** | ⭐ **6** | ⭐ **3** | 6 |
| ⭐ **Vai trò** | ⭐ **Active / Standby** | ⭐ **Master / Backup** | ⭐ **AVG / AVF** |
| ⭐ **Load balance trong group** | ❌ | ❌ | ⭐ ✅ **tối đa 4** |
| 🔴⭐ **Preempt mặc định** | 🔴 ⭐ **TẮT** | 🔴 ⭐ **BẬT** | TẮT |
| Priority default | 100 (0–255) | 100 (1–254) | 100 (1–255) |
| IPv6 | v2 ✅ | v3 ✅ | ✅ |

⭐ **Ba điểm đề hỏi nhiều nhất:**
1. 🔴 **Preempt: HSRP TẮT, VRRP BẬT**
2. ⭐ **VRRP là protocol duy nhất chuẩn mở**
3. ⭐ **GLBP là protocol duy nhất load-balance được trong 1 group**
</details>

---

**Câu 4.** 🔴 HSRP có tracking, track object `Down`, priority đã giảm từ 110 xuống 80.
Router kia priority 100. Nhưng router kia **vẫn không lên Active**. Nguyên nhân?

<details><summary>Xem đáp án</summary>

🔴 ⭐ **Router KIA không có `preempt`.**

**Cơ chế:** tracking chỉ **giảm priority của router A**. Việc **chiếm quyền Active** là hành động
của **router B** — và nó chỉ làm được nếu **B có `preempt`**.

⭐ **Tracking + preempt là CẶP ĐÔI BẮT BUỘC:**
- Tracking (trên A) → giảm priority A
- Preempt (trên B) → B thấy priority mình cao hơn → chiếm quyền

Thiếu một trong hai = **vô ích hoàn toàn**.

**Chẩn đoán:**
```
! Trên router A (đang Active với priority 80)
show standby brief
! Gi0/0.10    10   80  P Active  local  ...        ← priority ĐÃ giảm đúng

! ⭐ Trên router B
show standby brief
! Gi0/0.10    10   100   Standby ...               ← ⭐ CỘT P TRỐNG!
```

**Sửa:**
```
! Trên router B
interface Gi0/0.10
 standby 10 preempt
 standby 10 preempt delay minimum 60
```

⭐ **Best practice:** ⭐ **bật `preempt` trên MỌI router HSRP**, không chỉ router priority cao.
Không có lý do gì để không bật.
</details>

---

**Câu 5.** ⭐ Priority R1 = 110, R2 = 100. Bạn muốn tracking làm R1 nhường quyền khi uplink chết.
Chọn `decrement` bao nhiêu? Giải thích cách tính.

<details><summary>Xem đáp án</summary>

⭐ **Công thức:** `decrement > (priority_của_tôi − priority_của_router_kia)`

```
110 − 100 = 10   →   decrement PHẢI > 10
```

| decrement | Priority sau giảm | Kết quả |
|:---:|:---:|:---:|
| 5 | 110 − 5 = **105** | ❌ 105 > 100 → **KHÔNG failover** |
| 10 | 110 − 10 = **100** | ⚠️ **TIE** — không đảm bảo (tie-break theo IP) |
| **20** | 110 − 20 = **90** | ✅ **Failover** |
| ⭐ **30** | 110 − 30 = **80** | ⭐ ✅ **Failover, có biên an toàn** |

⭐ **Nên chọn 20–30**, không chọn đúng 11.

**Vì sao cần dư biên:**
1. Sau này ai đó đổi priority R2 lên 105 → decrement 11 lại không đủ
2. Nếu có **nhiều track object** (VD track uplink 1 và uplink 2 riêng), tổng decrement phải
   vẫn đủ khi chỉ 1 cái fail
3. Dư biên làm cấu hình **rõ ràng về ý định** — 80 vs 100 là khác biệt rõ ràng

**Cấu hình:**
```
standby 10 track 10 decrement 30
```

**Verify:**
```
show standby <if> <grp> | include Priority|Track
!   Priority 110 (configured 110)
!     Track object 10 state Up decrement 30
! (khi track Down):
!   Priority 80 (configured 110)
!     Track object 10 state Down decrement 30
```
</details>

---

**Câu 6.** 🔴 HSRP hoạt động bình thường, PC ping được gateway. Nhưng uplink Internet của
router Active chết → PC **mất mạng hoàn toàn** dù router Standby còn khỏe. Vì sao? Sửa thế nào?

<details><summary>Xem đáp án</summary>

🔴 ⭐ **FHRP không có object tracking.**

**Vì sao:** FHRP chỉ theo dõi **interface LOCAL của chính nó** (interface hướng xuống LAN).
Uplink chết mà interface LAN vẫn `up` → ⭐ **HSRP thấy "mọi thứ ổn"** → router vẫn là Active
→ ⭐ **traffic đi vào rồi drop** = **BLACK HOLE**.

⭐ Đây **chính xác** là cùng một lỗ hổng với **floating static route** (Module-03 §2.3):
*"interface up ≠ đích còn sống"*.

**Chẩn đoán:**
```
show standby brief
! Gi0/0.10    10   110 P Active  local  ...          ← vẫn Active
show standby Gi0/0.10 10 | include Track
! (TRỐNG — không có dòng Track)                      ← ⭐ ĐÂY LÀ VẤN ĐỀ
show ip route 0.0.0.0
! % Network not in table                              ← router Active không có đường ra
```

⭐ **Sửa — 3 bước (kết hợp Module-03 §2.4):**

```
! 1. IP SLA — ping THẬT một đích Internet qua ĐÚNG uplink
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1     ! ⭐ source-interface BẮT BUỘC
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now               ! ⭐ ĐỪNG QUÊN

! 2. Track object — kết hợp nhiều điều kiện
track 1 ip sla 1 reachability
 delay down 3 up 10
track 2 interface GigabitEthernet0/1 line-protocol
track 3 ip route 0.0.0.0 0.0.0.0 reachability
!
track 10 list boolean and                                   ! ⭐ AND cả 3
 object 1
 object 2
 object 3

! 3. Gắn vào HSRP
interface GigabitEthernet0/0.10
 standby 10 track 10 decrement 30
```

🔴 **VÀ — bắt buộc: router KIA phải có `preempt`:**
```
! Trên router Standby
interface GigabitEthernet0/0.10
 standby 10 preempt
```

**Verify:**
```
show track 10                    ! ⭐ "Tracked by: HSRP ..." phải có
show ip sla statistics 1         ! return code OK, time to live Forever
show standby brief               ! ⭐ cột P có trên CẢ 2 router
```

🧠 ⭐ ***"FHRP không có tracking = HA giả."*** Đây là lỗi thiết kế FHRP phổ biến nhất ở production.
</details>

---

**Câu 7.** ⭐ `preempt delay minimum` để làm gì? Kể một sự cố thật mà nó phòng ngừa.

<details><summary>Xem đáp án</summary>

⭐ **`preempt delay minimum <giây>`** = *"sau khi interface lên, **chờ N giây** rồi mới được preempt."*

⭐ **Sự cố nó phòng ngừa — black hole sau khi router reboot:**

| Giây | Chuyện gì | Vấn đề |
|:---:|---|---|
| 0 | R1 (priority 110, có preempt) boot lại | |
| ~30 | ⭐ **Interface LAN lên** → HSRP thấy priority 110 → ⭐ **preempt ngay → Active** | ⚠️ |
| 30–90 | ⭐ **OSPF/BGP vẫn đang hội tụ** — R1 ⭐ **chưa có default route** | 🔴 |
| — | ⭐ **Toàn bộ traffic VLAN đi vào R1 → DROP** | 🔴 **BLACK HOLE ~60 giây** |
| ~90 | Routing hội tụ xong | Giờ mới ổn |

🔴 **Nghịch lý:** router **khỏe hơn** (priority cao) lại làm mạng **chết** —
vì nó nhận trách nhiệm **trước khi** sẵn sàng.

⭐ **Sửa:**
```
interface Gi0/0.10
 standby 10 preempt delay minimum 90        ! ⭐ dài hơn thời gian hội tụ IGP/BGP
```

⭐ **Chọn giá trị bao nhiêu:** phải **dài hơn thời gian hội tụ routing** của mạng bạn.
- OSPF nội bộ: 30–60 s là đủ
- ⭐ **BGP với ISP (nhận full table):** cần **120–300 s** (nhận 900k prefix mất vài phút)

**Các biến thể:**
```
standby 10 preempt delay minimum 90        ! chờ 90 s sau khi interface up
standby 10 preempt delay reload 120        ! ⭐ chờ 120 s sau khi ROUTER RELOAD
standby 10 preempt delay sync 60           ! chờ đồng bộ (dùng với redundancy)
```

**Verify:**
```
show standby Gi0/0.10 10 | include Preempt
!   Preemption enabled, delay min 90 secs
```

⭐ **Giải pháp tốt hơn nữa (kết hợp):** dùng cả `preempt delay minimum` **và**
`track 3 ip route 0.0.0.0 0.0.0.0 reachability` — router chỉ có priority cao khi
**thực sự có default route trong RIB**.
</details>

---

**Câu 8.** 🔴 Cả 2 router HSRP đều báo `State is Active`. Nêu 4 nguyên nhân và lệnh chẩn đoán.

<details><summary>Xem đáp án</summary>

🔴 **Hai router Active cùng lúc = chúng KHÔNG nghe thấy nhau.**
Mỗi router tưởng router kia đã chết → tự lên Active.

**4 nguyên nhân theo thứ tự kiểm tra:**

| # | Nguyên nhân | Lệnh chẩn đoán |
|:---:|---|---|
| 1 | ⭐ **Authentication mismatch** | ⭐ `show logging \| include BADAUTH` → `%HSRP-4-BADAUTH: Bad authentication from ...` |
| 2 | ⭐ **VLAN chưa được trunk** giữa 2 router | ⭐ `show interfaces trunk` **trên switch** → VLAN có trong `allowed`? |
| 3 | ⭐ **Sub-interface `encapsulation dot1Q` sai VLAN** | `show run interface <subif>` **cả 2 router** → so số VLAN |
| 4 | ⭐ **ACL chặn multicast HSRP** | `show access-lists` → có chặn `224.0.0.2`/`224.0.0.102` UDP 1985? |
| + | Mất kết nối L2 (link giữa 2 switch down, STP block sai) | `show interfaces status` · `show spanning-tree vlan X` |
| + | **Version lệch** (v1 vs v2) | `show standby <if> <grp> \| include version` cả 2 |

**Triệu chứng phụ — MAC flapping trên switch:**
```
SW1# show mac address-table | include 0000.0c
!  10   0000.0c9f.f00a   DYNAMIC   Gi0/0        ← vMAC ở port R1
!  10   0000.0c9f.f00a   DYNAMIC   Gi0/1        ← ⭐ VÀ ở port R2 → FLAPPING
SW1# show logging | include MACFLAP
%SW_MATM-4-MACFLAP_NOTIF: Host 0000.0c9f.f00a in vlan 10 is flapping between port Gi0/0 and port Gi0/1
```

**Hậu quả:** PC ping gateway **lúc được lúc không** · traffic đi zigzag · ARP không ổn định.

**Chẩn đoán nhanh nhất:**
```
! Chạy trên CẢ 2 ROUTER và so:
show standby brief
! Nếu CẢ HAI đều "Active" và cột "Standby" = "unknown" → chắc chắn không nghe thấy nhau

show logging | include HSRP|BADAUTH
debug standby errors                        ! ⚠️ chỉ lab — rất hữu ích cho auth
```

⭐ **Kiểm tra L2 trước tiên:** ping IP thật của router kia trong cùng VLAN.
```
R1# ping 10.1.10.3            ! IP thật của R2
```
- Ping **fail** → vấn đề **L2/trunk/VLAN**
- Ping **OK** → vấn đề **HSRP** (auth / version / group number)
</details>

---

**Câu 9.** ⭐ Protocol nào load-balance được trong **cùng một group**? Cơ chế thế nào?
Và cách thực tế để load-balance với HSRP/VRRP là gì?

<details><summary>Xem đáp án</summary>

⭐ **Chỉ GLBP** load-balance được trong cùng một group.

**Cơ chế GLBP:**

| Vai | Nhiệm vụ |
|---|---|
| ⭐ **AVG** (Active Virtual Gateway) — **1**/group | ⭐ **Trả lời ARP** cho Virtual IP, nhưng trả về ⭐ **vMAC KHÁC NHAU cho từng host** |
| ⭐ **AVF** (Active Virtual Forwarder) — ⭐ **tối đa 4**/group | Mỗi AVF có **1 vMAC riêng**, forward traffic của các host được gán vMAC đó |

```
PC1 ARP "10.1.1.1?" → AVG trả vMAC1 (0007.b400.0a01) → PC1 đi qua R1
PC2 ARP "10.1.1.1?" → AVG trả vMAC2 (0007.b400.0a02) → PC2 đi qua R2
```
⭐ **Cùng một Virtual IP, nhưng mỗi host nhận một vMAC khác nhau.**

**3 chế độ:** `round-robin` (mặc định) · `weighted` · `host-dependent`

⚠️ **Hạn chế GLBP:** chia theo **host**, không theo **flow** → 1 host với traffic khổng lồ
vẫn chỉ dùng 1 router (giống **elephant flow** ở EtherChannel, Module-02 §7.4).
Và ⭐ **Cisco độc quyền**.

⭐⭐ **CÁCH THỰC TẾ với HSRP/VRRP — load-balance THEO VLAN:**

```
! ═══ R1 ═══
interface Gi0/0.10
 standby 10 priority 110              ! ⭐ Active VLAN 10
 standby 10 preempt
interface Gi0/0.20
 standby 20 priority 90               ! Standby VLAN 20
 standby 20 preempt

! ═══ R2 ═══
interface Gi0/0.10
 standby 10 priority 90               ! Standby VLAN 10
 standby 10 preempt
interface Gi0/0.20
 standby 20 priority 110              ! ⭐ Active VLAN 20
 standby 20 preempt
```

| VLAN | Active | Uplink được dùng |
|:---:|---|---|
| 10, 30, 50 (chẵn) | ⭐ **R1** | Uplink R1 |
| 20, 40, 60 (lẻ) | ⭐ **R2** | Uplink R2 |

→ ⭐ **Cả 2 uplink đều có traffic**. Đơn giản, **đa vendor** (dùng được VRRP), dễ hiểu, dễ vận hành.

⭐ **Và nhớ:** đặt ⭐ **STP root cùng switch với HSRP Active** cho mỗi VLAN
(Module-02 §8 bước 4) — nếu lệch thì traffic đi zigzag qua link giữa 2 switch.

⭐ **Xu hướng hiện đại:** **StackWise Virtual / VSS** — 2 switch thành 1 logic →
⭐ **không cần FHRP** (1 gateway) và ⭐ **không cần STP block** (dùng MEC).
</details>

---

**Câu 10.** ⭐ SSO, NSF, StackWise Virtual là gì? StackWise Virtual loại bỏ nhu cầu dùng gì?

<details><summary>Xem đáp án</summary>

| Kỹ thuật | Là gì | Bảo vệ khỏi |
|---|---|---|
| ⭐ **SSO** (Stateful Switchover) | 2 supervisor trong **1 chassis**, ⭐ **đồng bộ TRẠNG THÁI**. Sup chính chết → sup phụ tiếp nhận **giữ nguyên state** (không mất session) | Lỗi supervisor |
| ⭐ **NSF** (Non-Stop Forwarding) | ⭐ **Data plane TIẾP TỤC forward** trong lúc control plane restart. Router nói với neighbor "đừng xóa route của tôi" | Downtime khi control plane restart |
| ⭐ **NSF + SSO** | Đi cùng nhau: SSO giữ state, NSF giữ forwarding → ⭐ **switchover gần như không mất gói** | Chuẩn HA trong chassis |
| ⭐ **StackWise** | Nhiều switch vật lý → ⭐ **1 switch logic** (1 control plane, 1 IP quản lý, 1 config) | Lỗi 1 switch trong stack |
| ⭐ **StackWise Virtual / VSS** | ⭐ **2 chassis lớn → 1 thiết bị logic** | Lỗi 1 chassis |
| **MEC** (Multi-chassis EtherChannel) | EtherChannel **trải trên 2 chassis** của VSS/StackWise Virtual | Lỗi 1 chassis, **không cần STP block** |

⭐⭐ **StackWise Virtual / VSS loại bỏ nhu cầu dùng:**

| Loại bỏ | Vì sao |
|---|---|
| ⭐ **FHRP (HSRP/VRRP/GLBP)** | ⭐ 2 chassis = **1 thiết bị logic** = **1 gateway duy nhất** → không cần Virtual IP nữa |
| ⭐ **STP blocking** | ⭐ Dùng **MEC** — EtherChannel trải 2 chassis, STP thấy **1 port logic** → **không có loop → không block** |
| Nhiều điểm quản lý | 1 IP, 1 config cho cả 2 chassis |

```
   ═══ THIẾT KẾ CŨ ═══              ⭐ ═══ STACKWISE VIRTUAL ═══

   [SW-A]  [SW-B]                    ╔═══ 1 SWITCH LOGIC ═══╗
     │  ╳    │   ← STP block         ║  [SW-A] ═══ [SW-B]   ║
     └───┬───┘                       ╚═══════╦══════════════╝
     [Access]                                ║ MEC (không block)
   + cần HSRP giữa SW-A/SW-B              [Access]
                                        ⭐ không cần HSRP
                                        ⭐ không cần STP block
```

⭐ **Ý nghĩa thiết kế:** đây là hướng campus hiện đại — **giảm độ phức tạp** thay vì
thêm protocol để vá. Biết điều này để **không đề xuất giải pháp lạc hậu** khi được hỏi ý kiến thiết kế.

```
show redundancy states                     ! SSO state
show redundancy                            ! chi tiết
show switch                                ! StackWise
show switch stack-ports
show stackwise-virtual                     ! StackWise Virtual
```
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| **FHRP** (First Hop Redundancy Protocol) | Giao thức dự phòng chặng đầu | HSRP · VRRP · GLBP |
| ⭐ **Virtual IP (VIP)** | IP ảo | ⭐ IP mà PC dùng làm default gateway |
| ⭐ **Virtual MAC (vMAC)** | MAC ảo | ⭐ **Không đổi khi failover** → PC không phải ARP lại |
| ⭐ **HSRP** (Hot Standby Router Protocol) | Giao thức router dự phòng nóng | ⭐ **Cisco**. UDP 1985. Active/Standby |
| ⭐ **VRRP** (Virtual Router Redundancy Protocol) | Giao thức dự phòng router ảo | ⭐ **Chuẩn mở** RFC 3768/5798. IP proto 112. Master/Backup |
| ⭐ **GLBP** (Gateway Load Balancing Protocol) | Giao thức cân bằng tải gateway | ⭐ **Cisco**. UDP 3222. AVG/AVF. ⭐ **Load-balance trong 1 group** |
| ⭐ **Active** (HSRP) | Đang hoạt động | Router forward traffic cho VIP |
| ⭐ **Standby** (HSRP) | Dự phòng | Ứng viên tiếp theo |
| **Listen** (HSRP) | Đang nghe | Không phải Active/Standby |
| **Speak** (HSRP) | Đang nói | Gửi hello, tham gia bầu |
| **Learn** (HSRP) | Đang học | Chưa biết VIP, chờ Active nói |
| ⭐ **Master** (VRRP) | Chủ | Tương đương Active của HSRP |
| ⭐ **Backup** (VRRP) | Dự phòng | Tương đương Standby |
| ⭐ **AVG** (Active Virtual Gateway) | Cổng ảo hoạt động | ⭐ GLBP — **trả lời ARP**, phân bổ vMAC. 1/group |
| ⭐ **AVF** (Active Virtual Forwarder) | Bộ chuyển tiếp ảo | ⭐ GLBP — **tối đa 4**/group, mỗi cái 1 vMAC |
| ⭐ **Priority** | Ưu tiên | Mặc định **100**. **CAO** thắng |
| 🔴 ⭐ **Preempt** | Chiếm quyền | 🔴 ⭐ **HSRP: TẮT** mặc định · ⭐ **VRRP: BẬT** mặc định |
| ⭐ **`preempt delay minimum`** | Trễ trước khi chiếm quyền | ⭐ Chờ routing hội tụ → **chống black hole sau reboot** |
| **`preempt delay reload`** | Trễ sau khi reload | Tính từ lúc router khởi động lại |
| **Hello time / Hold time** | Thời gian chào / giữ | HSRP: 3/10 s · GLBP: 3/10 s |
| **Advertisement interval** | Chu kỳ quảng bá | VRRP: 1 s |
| **Master Down Interval** | Khoảng chờ Master chết | VRRP: `3×adv + skew` ≈ 3.6 s |
| **Skew time** | Thời gian lệch | `(256−priority)/256` — priority cao phát hiện nhanh hơn |
| ⭐ **IP address owner** | Chủ sở hữu IP | ⭐ VRRP priority **255** — router có IP interface = VIP |
| ⭐ **Object tracking** | Theo dõi đối tượng | ⭐ Giảm priority khi điều kiện fail |
| ⭐ **`decrement`** | Lượng giảm | ⭐ `> (pri_mình − pri_kia)`, nên dư biên |
| ⭐ **`track list boolean and`** | Danh sách AND | ⭐ Kết hợp nhiều điều kiện track |
| ⭐ **IP SLA** | Thỏa thuận mức dịch vụ IP | ⭐ **Ping thật đích** — vá lỗ hổng "interface up ≠ đích sống" |
| ⭐ **`source-interface`** | Interface nguồn | 🔴 **BẮT BUỘC** — để SLA đi đúng uplink cần kiểm |
| **Round-robin / Weighted / Host-dependent** | Luân phiên / Theo trọng số / Theo host | ⭐ 3 chế độ load-balancing GLBP |
| ⭐ **Weighting** (GLBP) | Trọng lượng | Quyết định AVF nhận nhiều/ít host |
| **BADAUTH** | Xác thực sai | ⭐ Log khi auth FHRP mismatch |
| ⭐ **MAC flapping** | MAC nhấp nháy | ⭐ Triệu chứng của **2 Active cùng lúc** |
| ⭐ **Black hole** | Hố đen | ⭐ Traffic vào router Active rồi drop (không có đường ra) |
| ⭐ **SSO** (Stateful Switchover) | Chuyển đổi có trạng thái | ⭐ 2 supervisor đồng bộ **state** |
| ⭐ **NSF** (Non-Stop Forwarding) | Chuyển tiếp không ngừng | ⭐ **Data plane tiếp tục forward** khi control plane restart |
| **Graceful Restart** | Khởi động lại nhẹ nhàng | Neighbor không xóa route trong lúc restart |
| ⭐ **StackWise** | Xếp chồng switch | ⭐ Nhiều switch → 1 logic |
| ⭐ **StackWise Virtual / VSS** | Xếp chồng ảo | ⭐ 2 chassis → 1 logic. ⭐ **Loại bỏ nhu cầu FHRP + STP block** |
| ⭐ **MEC** (Multi-chassis EtherChannel) | EtherChannel đa chassis | ⭐ EtherChannel trải 2 chassis → không cần STP block |
| ⭐ **BFD** | Phát hiện chuyển tiếp 2 chiều | ⭐ Phát hiện lỗi ~ms mà không tốn CPU như msec timer |

---

## 🎯 10. ĐÚC KẾT MODULE-06A

**3 điều rút ra:**

1. 🔴⭐ **HSRP preempt TẮT mặc định, VRRP BẬT mặc định.**
   Với HSRP, ⭐ **không gõ `preempt` thì priority hoàn toàn vô nghĩa** —
   và đó là lỗi cấu hình FHRP phổ biến nhất. Kèm theo: ⭐ **luôn có `preempt delay minimum`**
   để router không nhận trách nhiệm trước khi routing hội tụ.

2. 🔴⭐ **FHRP không có object tracking = HA GIẢ.**
   FHRP chỉ thấy interface **local** của mình — uplink chết mà LAN còn up thì nó **không biết**
   → **black hole**. Đây là **cùng một lỗ hổng** với floating static route (Module-03).
   ⭐ Vá bằng **IP SLA + track (boolean and) + decrement đủ lớn** — và ⭐ **router KIA phải có `preempt`**.

3. ⭐ **Thuộc bảng so sánh 3 protocol.** Ba điểm đề hỏi nhiều nhất:
   ⭐ **VRRP là protocol duy nhất chuẩn mở** · ⭐ **GLBP là protocol duy nhất load-balance
   trong 1 group** · ⭐ **vMAC prefix** (`0000.0C07.AC` / `0000.0C9F.F` / **`0000.5E00.01`**).
   Và biết rằng ⭐ **StackWise Virtual loại bỏ nhu cầu FHRP hoàn toàn** — đó là hướng thiết kế hiện đại.

🧠 **Một câu để nhớ:** *FHRP không làm router dự phòng nhanh hơn — nó làm **PC không cần biết**
có bao nhiêu router. Nhưng nó chỉ **nhìn được cánh cổng của mình** — muốn nó biết **con đường phía sau
đã sập** thì phải cho nó một cái **điện thoại** (IP SLA), và cho người bên cạnh **quyền nhấc ghế** (preempt).*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | FHRP giải quyết vấn đề gì? Vì sao vMAC quan trọng? | ☐ |
| 2 | 🔴 ⭐ Preempt mặc định của HSRP và VRRP? | ☐ |
| 3 | ⭐ Tính vMAC: HSRPv1 grp 5 · HSRPv2 grp 100 · VRRP grp 20 | ☐ |
| 4 | ⭐ Điền đủ bảng so sánh HSRP/VRRP/GLBP (10 tiêu chí) | ☐ |
| 5 | 6 state HSRP theo thứ tự? 3 state VRRP? | ☐ |
| 6 | Multicast + transport của 3 protocol? | ☐ |
| 7 | ⭐ VRRP priority 255 và 0 nghĩa là gì? | ☐ |
| 8 | HSRPv1 vs v2 khác gì? Có tương thích không? | ☐ |
| 9 | ⭐ GLBP: AVG làm gì, AVF làm gì, tối đa mấy AVF? | ☐ |
| 10 | 3 chế độ load-balancing GLBP? Hạn chế của GLBP? | ☐ |
| 11 | 🔴 ⭐ FHRP có biết uplink chết không? Vì sao? | ☐ |
| 12 | ⭐ Object tracking hoạt động thế nào? | ☐ |
| 13 | 🔴 ⭐ Tracking cần điều kiện gì ở router kia? | ☐ |
| 14 | ⭐ Cách tính `decrement`? Vì sao nên dư biên? | ☐ |
| 15 | ⭐ `preempt delay minimum` phòng ngừa sự cố gì? | ☐ |
| 16 | 🔴 2 lỗi IP SLA dễ mắc nhất? | ☐ |
| 17 | 🔴 4 nguyên nhân "2 Active cùng lúc"? Triệu chứng phụ? | ☐ |
| 18 | ⭐ Cách thực tế load-balance với HSRP/VRRP? | ☐ |
| 19 | ⭐ Vì sao STP root và HSRP Active nên cùng switch? | ☐ |
| 20 | ⭐ SSO / NSF / StackWise Virtual? StackWise Virtual bỏ được nhu cầu gì? | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Dựng 2 router + 1 switch + PC, router-on-a-stick, VLAN 10/20 | ☐ |
| 2 | HSRPv2 group 10 và 20, load-balance theo VLAN (R1 Active V10, R2 Active V20) | ☐ |
| 3 | ⭐ PC ping Internet qua Virtual IP · `arp` trên PC hiện **vMAC** | ☐ |
| 4 | ⭐ Tính và verify vMAC khớp với công thức HSRPv2 | ☐ |
| 5 | 🔴⭐⭐ **Chứng minh bẫy preempt**: priority 110 mà vẫn Standby → cột `P` trống | ☐ |
| 6 | Bật `preempt` + `preempt delay minimum` → R1 chiếm lại Active, cột `P` xuất hiện | ☐ |
| 7 | ⭐ Đo downtime failover: timer mặc định vs `msec 200/750`, điền bảng | ☐ |
| 8 | 🔴⭐⭐ **Tái hiện BLACK HOLE**: cắt uplink R1 → R1 vẫn Active → PC mất mạng | ☐ |
| 9 | ⭐⭐ Cấu hình **IP SLA + track 1/2/3 + track 10 boolean and** trên **cả 2 router** | ☐ |
| 10 | Verify `show track 10` → `Boolean AND is Up` + ⭐ `Tracked by: HSRP ...` | ☐ |
| 11 | ⭐⭐ Test failover: cắt uplink → priority **110→80** → R2 preempt → PC ping lại được | ☐ |
| 12 | Test hồi phục: bật lại uplink → priority về 110 → R1 lấy lại Active | ☐ |
| 13 | ⭐ Tái hiện lỗi **decrement quá nhỏ** (5) → không failover | ☐ |
| 14 | 🔴⭐ Tái hiện lỗi **R2 không có preempt** → R1 priority 80 mà vẫn Active | ☐ |
| 15 | 🔴 Tái hiện lỗi **IP SLA thiếu `source-interface`** | ☐ |
| 16 | ⭐ Chuyển VLAN 20 sang **VRRP**, tính và verify vMAC `0000.5e00.0114` | ☐ |
| 17 | ⭐⭐ **Chứng minh VRRP preempt BẬT mặc định** (cột `Pre = Y` mà không gõ lệnh nào) | ☐ |
| 18 | ⭐ Điền bảng so sánh trực tiếp HSRP vs VRRP từ kết quả lab | ☐ |
| 19 | 🚀 VRRPv3 với `address-family ipv4` (tùy chọn) | ☐ |
| 20 | 🟡 GLBP: thấy `Fwd -` (AVG) + `Fwd 1/2` (AVF) với 2 vMAC khác nhau (nếu image hỗ trợ) | ☐ |
| 21 | 🟡 2 PC trong VLAN GLBP nhận **2 vMAC khác nhau** cho cùng 1 VIP | ☐ |
| 22 | ⭐ Bật HSRP **MD5 auth**, tái hiện **key lệch → 2 Active** → thấy log `BADAUTH` | ☐ |
| 23 | ⭐ Thấy **MAC flapping** trên switch khi có 2 Active | ☐ |
| 24 | Cố ý phá 1 thứ, tự tìm ra bằng **quy trình 5 bước §7.3** trong 10 phút | ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 5–6** (bẫy preempt),
> **mục 8–14** (black hole + tracking — phần giá trị nhất cho công việc thật),
> và **mục 17** (VRRP preempt mặc định). Đó là ba thứ đề hỏi nhiều nhất **và**
> ba lỗi thiết kế FHRP phổ biến nhất ở production.

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *First Hop Redundancy Protocols* — bảng so sánh HSRP/VRRP/GLBP |
| **Cisco doc** ⭐ | *First Hop Redundancy Protocols Configuration Guide* — chương *Configuring HSRP*, *Configuring VRRP*, *Configuring GLBP* |
| **Cisco doc** ⭐⭐ | *Hot Standby Router Protocol Features and Functionality* — ⭐ tài liệu kinh điển, giải thích state machine và vMAC |
| **Cisco doc** ⭐ | *Enhanced Object Tracking Configuration Guide* — ⭐ track + HSRP + IP SLA |
| **Cisco doc** ⭐ | *IP SLAs Configuration Guide* → *IP SLAs ICMP Echo Operations* |
| **Cisco doc** | *Understanding and Troubleshooting HSRP Problems* — ⭐ đúng bảng "2 Active cùng lúc" |
| **Cisco doc** | *GLBP Load Balancing* · *Configuring VRRPv3* |
| **Cisco doc** ⭐ | *High Availability Configuration Guide* → *Stateful Switchover (SSO)*, *Nonstop Forwarding (NSF)* |
| **Cisco doc** | *Cisco StackWise Virtual White Paper* — ⭐ hiểu vì sao nó thay thế FHRP |
| **RFC 5798** | VRRPv3 for IPv4 and IPv6 |
| **RFC 2281** | Cisco HSRP (informational) |
| **Cisco Live** ⭐ | Search `Cisco Live campus high availability design` · `Cisco Live FHRP best practices` |
| **NetworkLessons** ⭐ | Loạt bài *HSRP*, *VRRP*, *GLBP*, *HSRP with object tracking* — nhiều bài free |
| **Video** | CBT Nuggets ENCOR — module FHRP · Keith Barker: search `Keith Barker HSRP`, `Keith Barker GLBP` |
| **Wireshark** | Filter `hsrp` (UDP 1985 → 224.0.0.102) · `vrrp` (IP proto 112 → 224.0.0.18) · `glbp`. ⭐ **Xem vMAC và priority thật trong gói** |
| **Forum** | https://community.cisco.com — search `hsrp both active`, `hsrp preempt not working`, `hsrp track ip sla` |

---

**➡️ Tiếp theo:** Module-06B — NAT/PAT nâng cao, NTP, Multicast
*(NAT static/dynamic/PAT/port-forward · thứ tự NAT-routing · NAT64 · NTP + auth ·
Multicast: IGMP v2/v3 + PIM (describe) — **Tuần 11 nửa sau**)*
