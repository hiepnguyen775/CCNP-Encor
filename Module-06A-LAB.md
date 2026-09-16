# LAB 06A — Tuần 11: HSRP · VRRP · GLBP · Object Tracking

> 📘 **Lý thuyết:** [Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md) —
> đọc **Phần 1** và **Phần 2 mục §3.2 (bảng so sánh 3 FHRP), §3.3 (HSRP), §3.6 (object tracking)** trước khi làm.
>
> ⏱️ **Thời gian:** ~7 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 3–4× vIOS + 1× vIOS-L2

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Hai router cùng làm gateway — client biết đi theo ai? | 1 |
| 2 | Vì sao đặt priority cao hơn mà router **vẫn không** lên Active? | 1 |
| 3 | Router chính chết — client mất mạng **bao nhiêu giây**? Đo bằng số | 2 |
| 4 | Gateway còn sống nhưng **đường ra Internet đã chết** — FHRP có biết không? | 3 |
| 5 | VRRP khác HSRP ở chỗ nào — thấy bằng thực nghiệm | 4 |
| 6 | Ai cũng có thể giả làm gateway — chặn bằng gì? | 6 |

> ⭐ **Bước 3 (Object Tracking + IP SLA) là phần giá trị nhất module.**
> Nó vá đúng lỗ hổng chết người của FHRP: ⭐ **HSRP chỉ biết "router kia còn sống không",
> nó KHÔNG biết "đường ra Internet còn thông không".**

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Bẫy preempt ở bước 1 là CỐ Ý** | Bạn sẽ đặt priority cao mà router **không** lên Active. Đó là bài học, không phải lỗi |
| **Đo downtime cần chuẩn bị** | Bước 2 dùng `ping ... repeat 1000` từ client rồi **đếm số dấu chấm**. Mỗi dấu `.` ≈ 2 giây timeout |
| **IP SLA cần thời gian** | Bước 3 có `frequency` và `delay` — chờ đúng số giây rồi mới xem `show track` |
| **GLBP có thể không chạy** | Bước 5 tùy chọn — nhiều image vIOS không hỗ trợ GLBP. Không sao, blueprint chỉ yêu cầu *hiểu* |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

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
  Active virtual MAC address is 0000.0c9f.f00a           ← vMAC
  Hello time 3 sec, hold time 10 sec
  Preemption disabled                                     ← TẮT!
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
! 00:00:0c:9f:f0:0a  10.1.10.1  expires in ...        ← vMAC, không phải MAC R1
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
R1(config-subif)#  standby 10 preempt delay minimum 30       ! chống black hole
R1(config-subif)# exit
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)#  standby 20 preempt
R1(config-subif)#  standby 20 preempt delay minimum 30

! R2 CŨNG PHẢI bật preempt (để tracking ở bước 3 hoạt động)
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
! Đặt timer nhanh — PHẢI đặt CẢ 2 ROUTER
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
R1(config)# ip sla schedule 1 life forever start-time now      ! ĐỪNG QUÊN
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
! Track 10: kết hợp CẢ BA bằng boolean AND
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
Operation time to live: Forever                    ← đúng
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
    HSRP GigabitEthernet0/0.10 10                  ← HSRP đang dùng
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
  Virtual MAC address is 0000.5e00.0114                  ← vMAC VRRP
  Advertisement interval is 1.000 sec
  Preemption enabled                                      ← BẬT mặc định
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
R2# show fhrp verbose                       ! xem MỌI FHRP trên router
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
! 00:07:b4:00:1e:02  10.1.30.1        ← AVF 2 (R2) — vMAC KHÁC!
```
⭐ **Cùng một Virtual IP `10.1.30.1` nhưng 2 PC nhận 2 vMAC khác nhau**
→ PC2 đi qua R1, PC3 đi qua R2 → ⭐ **cả 2 router cùng forward**.

✅ **Checkpoint bước 5:** thấy được `Fwd 1` và `Fwd 2` với 2 vMAC khác nhau,
và 2 PC nhận 2 vMAC khác nhau cho cùng 1 VIP.

---

### Bước 6 — 🚀 Authentication & bảo mật FHRP

```
! HSRP MD5 — phải khớp CẢ 2 ROUTER
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
