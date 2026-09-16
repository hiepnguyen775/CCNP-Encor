# LAB 02 — Tuần 4: STP · RSTP · Guards

> 📘 **Lý thuyết:** [Module-02](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md) —
> đọc **Phần 1** và **Phần 2 mục §3.1–3.2, §3.5** trước khi làm.
>
> ⏱️ **Thời gian:** ~6 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 4× vIOS-L2

---

## Lab này trả lời 6 câu hỏi

| # | Câu hỏi | Bước |
|:---:|---|:---:|
| 1 | Ai đang là Root Bridge, và switch quyết định điều đó bằng gì? | 2 |
| 2 | Làm sao **ép** một switch cụ thể làm Root? | 3 |
| 3 | Port nào bị chặn, và vì sao đúng port đó chứ không phải port khác? | 2 |
| 4 | RSTP nhanh hơn STP bao nhiêu — đo bằng số, không phải nghe nói | 4 |
| 5 | Cắm nhầm một switch lạ vào mạng thì chuyện gì xảy ra? | 5 |
| 6 | Root Guard và Loop Guard khác nhau ở đâu — thấy bằng mắt | 5 |

> Đây là **module nặng nhất của khối Layer 2**. Làm chắc ở đây thì Module-09 (thiết kế campus)
> sẽ rất nhẹ.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Switch boot lâu** | vIOS-L2 mất 3–5 phút mới lên. Đừng tưởng treo — cứ chờ |
| **Nối dây TRƯỚC khi start** | EVE-NG không cho nối khi node đang chạy |
| **Số liệu của bạn sẽ khác** | MAC, Bridge ID, cost sẽ khác output mẫu. Đối chiếu **cấu trúc**, đừng so từng số |
| **Có vòng lặp là cố ý** | Topology lab này **cố tình** có vòng — đó chính là thứ để quan sát STP |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 8. LAB — TUẦN 4: STP · RSTP · GUARDS

### LAB 02-1 — Topology chuẩn campus (4 switch)

#### Topology

```
              ╔═══════════════════════════════╗
              ║   TẦNG DISTRIBUTION           ║
              ║                               ║
              ║   [SW-D1]═══Gi0/3═══[SW-D2]   ║   ← link giữa 2 dist
              ║    │  │              │  │     ║
              ╚════│══│══════════════│══│═════╝
                   │  └──────┐  ┌────┘  │
              Gi0/1│    Gi0/2│  │Gi0/1  │Gi0/2
                   │         │  │       │
              ┌────┴─────────┴──┴───────┴────┐
              │  [SW-A1]        [SW-A2]      │  ← TẦNG ACCESS
              │   Gi0/3 → PC      Gi0/3 → PC │
              └──────────────────────────────┘
```

| Link | Đầu A | Đầu B | Ghi chú |
|---|---|---|---|
| 1 | SW-D1 Gi0/3 | SW-D2 Gi0/3 | Link giữa 2 distribution |
| 2 | SW-A1 Gi0/1 | SW-D1 Gi0/1 | Uplink A1 → D1 |
| 3 | SW-A1 Gi0/2 | SW-D2 Gi0/1 | Uplink A1 → D2 |
| 4 | SW-A2 Gi0/1 | SW-D1 Gi0/2 | Uplink A2 → D1 |
| 5 | SW-A2 Gi0/2 | SW-D2 Gi0/2 | Uplink A2 → D2 |
| 6 | SW-A1 Gi0/3 | PC1 (VPCS) | Access VLAN 10 |
| 7 | SW-A2 Gi0/3 | PC2 (VPCS) | Access VLAN 10 |

**RAM: 4× 768 MB = 3 GB** ✅ · Topology này **có vòng lặp** (cố ý) — đây là topology campus thật.

#### Bước 1 — Cấu hình nền (làm giống nhau, chỉ đổi hostname)

```
enable
configure terminal
!
hostname SW-D1                             ! đổi theo từng switch
no ip domain lookup
!
vlan 10
 name USERS
vlan 20
 name SERVERS
vlan 999
 name NATIVE-UNUSED                        ! native VLAN "rác"
exit
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

#### Bước 2 — Cấu hình trunk (mọi link switch–switch)

**Trên SW-D1:**
```
configure terminal
interface range GigabitEthernet0/1 - 3
 description ---> TRUNK
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
end
```

**Trên SW-D2:** giống hệt (Gi0/1–3).

**Trên SW-A1 và SW-A2:**
```
configure terminal
! Uplink
interface range GigabitEthernet0/1 - 2
 description ---> UPLINK TRUNK
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
!
! Port PC
interface GigabitEthernet0/3
 description ---> PC
 switchport mode access
 switchport access vlan 10
 no shutdown
end
write memory
```

✅ **Checkpoint:** `show interfaces trunk` trên mọi switch → mọi link switch–switch đều `trunking`,
allowed vlan `10,20`, native vlan `999`.

#### Bước 3 — Quan sát STP TRƯỚC khi can thiệp

```
SW-D1# show spanning-tree vlan 10
```

**Điền bảng — chạy lệnh trên cả 4 switch:**

| Switch | MAC address | Là Root? | Root Port | Port Blocking |
|---|---|:---:|---|---|
| SW-D1 | | | | |
| SW-D2 | | | | |
| SW-A1 | | | | |
| SW-A2 | | | | |

```
! Xem nhanh port nào bị block toàn mạng
SW-A1# show spanning-tree vlan 10 | include BLK|Altn|Desg|Root
```

⚠️ **Nhận xét bạn phải rút ra:** root hiện tại là switch có **MAC nhỏ nhất** —
rất có thể là một **switch ACCESS**, không phải distribution. **Đây là thiết kế sai.**

```
! Chứng minh: đếm số hop từ SW-A2 về root
SW-A2# show spanning-tree vlan 10 | include Root ID|Cost
```

#### Bước 4 — ⭐ Ép root đúng thiết kế + backup root

```
! SW-D1 — root chính cho VLAN 10, backup cho VLAN 20
SW-D1(config)# spanning-tree vlan 10 priority 4096
SW-D1(config)# spanning-tree vlan 20 priority 8192

! SW-D2 — root chính cho VLAN 20, backup cho VLAN 10
SW-D2(config)# spanning-tree vlan 20 priority 4096
SW-D2(config)# spanning-tree vlan 10 priority 8192
```

**Kiểm tra:**
```
SW-D1# show spanning-tree vlan 10 | include Root|priority
```
**Output mẫu:**
```
  Root ID    Priority    4106
             Address     0c:1a:2b:00:d1:00
             This bridge is the root
  Bridge ID  Priority    4106  (priority 4096 sys-id-ext 10)
```
✅ `4106 = 4096 + 10`.

```
SW-D1# show spanning-tree vlan 20 | include Root ID|This bridge
```
✅ VLAN 20: SW-D1 **không** là root (SW-D2 là root).

**Xác nhận load-balancing đã hoạt động:**
```
SW-A1# show spanning-tree vlan 10 | include Root FWD|Altn
SW-A1# show spanning-tree vlan 20 | include Root FWD|Altn
```
⭐ **Kết quả mong đợi:** Root Port của **VLAN 10** và **VLAN 20** là **2 port khác nhau**
→ cả 2 uplink đều có traffic.

✅ **Checkpoint bước 4:**

| Kiểm tra | Mong đợi |
|---|---|
| VLAN 10: root = SW-D1 | ✅ |
| VLAN 20: root = SW-D2 | ✅ |
| Trên SW-A1: Root Port của VLAN 10 ≠ Root Port của VLAN 20 | ⭐ ✅ Load-balance |
| Đúng 1 port block mỗi VLAN trên mỗi switch access | ✅ |

#### Bước 5 — Bảo vệ STP: 4 lớp Guard

**a) PortFast + BPDU Guard trên port PC:**
```
! SW-A1 và SW-A2
configure terminal
interface GigabitEthernet0/3
 spanning-tree portfast
 spanning-tree bpduguard enable
end
```

Hoặc cách thực chiến (bật mặc định toàn switch):
```
configure terminal
 spanning-tree portfast default
 spanning-tree portfast bpduguard default
end
```

**b) Root Guard trên port hướng xuống access (trên distribution):**
```
! SW-D1
configure terminal
interface range GigabitEthernet0/1 - 2
 description ---> DOWN to ACCESS - Root Guard
 spanning-tree guard root
end
```
Làm tương tự trên SW-D2.

**c) Loop Guard trên uplink (trên access):**
```
! SW-A1 và SW-A2
configure terminal
interface range GigabitEthernet0/1 - 2
 description ---> UPLINK - Loop Guard
 spanning-tree guard loop
end
```
Hoặc toàn cục: `spanning-tree loopguard default`

**d) UDLD + errdisable recovery + misconfig guard:**
```
configure terminal
 udld aggressive                                       ! link fiber
 spanning-tree etherchannel guard misconfig            ! chuẩn bị cho tuần 5
 errdisable recovery cause bpduguard
 errdisable recovery cause udld
 errdisable recovery interval 300
end
write memory
```

**Kiểm tra:**
```
show spanning-tree summary
```
**Output mẫu:**
```
Switch is in rapid-pvst mode
Root bridge for: VLAN0010
Extended system ID           is enabled
Portfast Default             is enabled
PortFast BPDU Guard Default  is enabled
Portfast BPDU Filter Default is disabled
Loopguard Default            is disabled
EtherChannel misconfig guard is enabled
UplinkFast                   is disabled
BackboneFast                 is disabled
```
⭐ Đọc bảng này để xác nhận mọi guard đã bật đúng.
Chú ý: `BPDU Filter Default is disabled` — **đúng, không được bật cái này**.

```
show errdisable recovery
show udld
show spanning-tree interface Gi0/1 detail | include guard|Guard
```

✅ **Checkpoint bước 5:** `show spanning-tree summary` cho thấy PortFast Default + BPDU Guard Default
đã bật, BPDU Filter Default **tắt**, misconfig guard bật.

#### Bước 6 — ⭐ TEST TỪNG GUARD (phần giá trị nhất)

Không test thì bạn chỉ *biết* guard tồn tại, chứ chưa *thấy* nó làm gì.

**Test 1 — BPDU Guard**

Mô phỏng "ai đó cắm switch vào port PC":
1. Trong EVE-NG, thêm 1 vIOS-L2 mới tên `SW-ROGUE`
2. Nối `SW-ROGUE Gi0/0` ↔ `SW-A1 Gi0/3` (port PC, đang có PortFast + BPDU Guard)
3. Trên SW-ROGUE: cấu hình `vlan 10`, `interface Gi0/0` → `switchport mode trunk` → `no shut`

**Trên SW-A1 quan sát:**
```
SW-A1#
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port GigabitEthernet0/3 with BPDU Guard enabled.
                             Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Gi0/3, putting Gi0/3 in err-disable state
```
```
SW-A1# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Gi0/3     PC                 err-disabled bpduguard
```
✅ **Checkpoint:** port bị `err-disable`, `Reason = bpduguard`. **Loop bị chặn trước khi hình thành.**

**Bật lại port:**
```
SW-A1(config)# interface Gi0/3
SW-A1(config-if)# shutdown
SW-A1(config-if)# no shutdown
```
(hoặc chờ 300 s để `errdisable recovery` tự bật lại)

---

**Test 2 — Root Guard**

Mô phỏng "switch access cố chiếm quyền root":
```
! Trên SW-A1 — cố tình đặt priority thấp nhất để chiếm root
SW-A1(config)# spanning-tree vlan 10 priority 0
```

**Trên SW-D1 (có Root Guard ở port hướng xuống) quan sát:**
```
SW-D1#
%SPANTREE-2-ROOTGUARD_BLOCK: Root guard blocking port GigabitEthernet0/1 on VLAN0010.
```
```
SW-D1# show spanning-tree inconsistentports
```
**Output mẫu:**
```
Name                 Interface              Inconsistency
-------------------- ---------------------- ------------------
VLAN0010             GigabitEthernet0/1     Root Inconsistent

Number of inconsistent ports (segments) in the system : 1
```
```
SW-D1# show spanning-tree vlan 10 | include ROOT_Inc|BKN
Gi0/1               Desg BKN*4         128.2    P2p *ROOT_Inc
```

⭐ **Bài học:** SW-A1 **không trở thành root được**. Port bị block cho tới khi hết Superior BPDU.

**Hoàn tác:**
```
SW-A1(config)# spanning-tree vlan 10 priority 32768
! Hoặc: no spanning-tree vlan 10 priority
```
Sau vài giây, kiểm tra lại — port tự hồi phục:
```
SW-D1# show spanning-tree inconsistentports
Number of inconsistent ports (segments) in the system : 0
```
✅ **Root Guard tự hồi phục**, không cần can thiệp tay.

---

**Test 3 — Đo hội tụ STP vs RSTP (bài lab quan trọng nhất tuần 4)**

**a) Chuyển về PVST+ (STP chậm) trên cả 4 switch:**
```
configure terminal
 spanning-tree mode pvst
end
```
Xác nhận: `show spanning-tree summary | include mode`

**b) Ping liên tục từ PC1 sang PC2, rồi cắt Root Port của SW-A1:**

Trên PC1 (VPCS):
```
PC1> ping 10.10.10.12 -c 100
```

Trên SW-A1, cắt Root Port đang forward (giả sử Gi0/1):
```
SW-A1(config)# interface GigabitEthernet0/1
SW-A1(config-if)# shutdown
```

**Đếm số gói ping mất.**

**c) Chuyển sang Rapid PVST+ và đo lại:**
```
! Trên CẢ 4 switch
configure terminal
 spanning-tree mode rapid-pvst
end
```
Bật lại Gi0/1, chờ ổn định, rồi lặp lại bài đo.

⭐ **BẢNG KẾT QUẢ — điền vào:**

| Mode | Số gói mất | Thời gian (~) | Ghi chú |
|---|:---:|---|---|
| PVST+ (802.1D) | | | Chờ Listening + Learning |
| Rapid PVST+ (802.1w) | | | Proposal/Agreement |

**Kết quả mong đợi:** PVST+ mất ~15–30 gói · Rapid PVST+ mất **1–3 gói**.

---

**Test 4 — Link type & tác động của duplex**

```
! Xem link type hiện tại
SW-A1# show spanning-tree vlan 10 | include P2p|Shr
```
Mọi link phải là `P2p` (vì full-duplex).

**Ép half-duplex để thấy nó biến thành shared:**
```
SW-A1(config)# interface GigabitEthernet0/1
SW-A1(config-if)# duplex half
SW-A1(config-if)# speed 100
```
```
SW-A1# show spanning-tree vlan 10 | include Gi0/1
```
→ Link type đổi thành **`Shr`**.

Đo lại hội tụ với Rapid PVST+ → **chậm lại** vì không handshake được.

**Hoàn tác:**
```
SW-A1(config-if)# duplex auto
SW-A1(config-if)# speed auto
```

⭐ **Bài học thực chiến:** một duplex mismatch không chỉ gây lỗi CRC — nó **phá luôn khả năng
hội tụ nhanh của RSTP** trên port đó.

---

**Test 5 — Bắt gói BPDU bằng Wireshark**

1. Trong EVE-NG: click phải link SW-A1↔SW-D1 → **Capture**
2. Trong Wireshark, filter: `stp`

⭐ **Điền bảng từ những gì bạn thấy trong gói BPDU:**

| Trường trong BPDU | Giá trị bạn thấy |
|---|---|
| Protocol Version Identifier (0=STP, 2=RSTP) | |
| BPDU Type | |
| Root Identifier (priority + MAC) | |
| Root Path Cost | |
| Bridge Identifier | |
| Port Identifier | |
| Message Age / Max Age / Hello / Forward Delay | |
| Flags (TC bit? Proposal? Agreement?) | |

**Thử nghiệm:** chuyển giữa `pvst` và `rapid-pvst` rồi bắt lại → xem trường **Version** đổi từ `0` → `2`.
Và trong RSTP, tìm gói có bit **Proposal/Agreement** lúc link vừa lên.

> ⭐ Đây là lúc lý thuyết §2.2 và §3.4 trở thành thứ bạn **nhìn thấy được**. Đừng bỏ bước này.

