# LAB P0 — Tuần 1: Switching (VLAN · Inter-VLAN · STP)

> 📘 **Lý thuyết:** [Module-P0](Module-P0-Nen-tang-Ready-for-ENCOR.md) —
> đọc **Phần 1** và **Phần 2 mục §3.3, §3.4** trước khi làm.
>
> ⏱️ **Thời gian:** ~5 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 3× vIOS-L2 + 1× vIOS

---

## Ba lab này trả lời 4 câu hỏi

| # | Câu hỏi | LAB |
|:---:|---|:---:|
| 1 | VLAN cách ly máy tính bằng cách nào? Trunk chở nhiều VLAN ra sao? | P0-1 |
| 2 | Hai VLAN muốn nói chuyện với nhau thì phải đi qua đâu? | P0-2 |
| 3 | Mạng có vòng lặp thì chuyện gì xảy ra, và STP chặn nó thế nào? | P0-3 |
| 4 | Làm sao ép một switch cụ thể làm Root Bridge? | P0-3 |

> Đây là **nền của Module-02**. Làm chắc ở đây thì Module-02 (STP nâng cao, MST, EtherChannel)
> sẽ nhẹ hơn rất nhiều.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Gõ tay, đừng copy cả khối** | Lần đầu hãy gõ từng dòng. Khi lab đã chạy đúng rồi thì copy lại cho nhanh — nhưng lần đầu phải gõ |
| **Số liệu của bạn sẽ khác** | MAC address, thời gian, cost sẽ khác output mẫu. Đối chiếu **cấu trúc và từ khóa**, đừng so từng con số |
| **Lỗi là chuyện bình thường** | Mỗi lần mất > 15 phút vì một lỗi → ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

# LAB P0-1 — VLAN + Trunk (2 switch)

**Mục tiêu:** PC cùng VLAN nói được với nhau qua 2 switch; khác VLAN thì không.

#### Topology

```
        VLAN 10 = SALES        VLAN 20 = IT
              
   [PC1]──Gi0/1  SW1  Gi0/0 ══════ Gi0/0  SW2  Gi0/1──[PC3]
   V10                    TRUNK                        V10
   [PC2]──Gi0/2                    Gi0/2──[PC4]
   V20                                     V20
```

| Thiết bị | Image | RAM | Interface | Cấu hình |
|---|---|:---:|---|---|
| SW1 | vIOS-L2 | 768 MB | Gi0/0 | Trunk → SW2 |
| | | | Gi0/1 | Access VLAN 10 → PC1 |
| | | | Gi0/2 | Access VLAN 20 → PC2 |
| SW2 | vIOS-L2 | 768 MB | Gi0/0 | Trunk → SW1 |
| | | | Gi0/1 | Access VLAN 10 → PC3 |
| | | | Gi0/2 | Access VLAN 20 → PC4 |
| PC1–PC4 | **VPCS** hoặc Linux nhẹ | 0–128 MB | e0 | IP tĩnh |

**Tổng RAM: ~1.8 GB** ✅

> 💡 **Không có image PC?** Trong EVE-NG có node **VPCS** (Virtual PC Simulator) — siêu nhẹ, gần như
> không ăn RAM, đủ để ping. Đây là cách chuẩn để làm PC trong lab.
> Nếu cũng không có VPCS: dùng thêm 1 vIOS làm "PC" (cấu hình IP + default gateway, dùng `ping`).

#### Bảng địa chỉ

| Thiết bị | IP | Mask | VLAN |
|---|---|---|:---:|
| PC1 | 10.10.10.11 | /24 | 10 |
| PC3 | 10.10.10.13 | /24 | 10 |
| PC2 | 10.10.20.12 | /24 | 20 |
| PC4 | 10.10.20.14 | /24 | 20 |

#### Bước 1 — Dựng topology trong EVE-NG

1. Add new lab: `LAB-P0-1-VLAN-Trunk`
2. Add node: 2× vIOS-L2, RAM 768, Ethernets **4**
3. Add node: 4× VPCS
4. Nối dây theo bảng trên (**nối trước khi start node** — EVE-NG không cho nối khi node đang chạy)
5. Start all nodes, chờ vIOS-L2 boot (2–4 phút, switch boot lâu hơn router)

#### Bước 2 — Cấu hình SW1

```
enable
configure terminal
!
hostname SW1
no ip domain lookup
!
! === Tạo VLAN ===
vlan 10
 name SALES
vlan 20
 name IT
exit
!
! === Trunk về SW2 ===
interface GigabitEthernet0/0
 description ---> TRUNK to SW2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport nonegotiate
 no shutdown
!
! === Access port ===
interface GigabitEthernet0/1
 description ---> PC1 (VLAN 10)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface GigabitEthernet0/2
 description ---> PC2 (VLAN 20)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

#### Bước 3 — Cấu hình SW2

```
enable
configure terminal
!
hostname SW2
no ip domain lookup
!
vlan 10
 name SALES
vlan 20
 name IT
exit
!
interface GigabitEthernet0/0
 description ---> TRUNK to SW1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport nonegotiate
 no shutdown
!
interface GigabitEthernet0/1
 description ---> PC3 (VLAN 10)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface GigabitEthernet0/2
 description ---> PC4 (VLAN 20)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
!
end
write memory
```

#### Bước 4 — Cấu hình PC (VPCS)

Trên console VPCS của PC1:
```
ip 10.10.10.11/24
save
```
PC2: `ip 10.10.20.12/24` · PC3: `ip 10.10.10.13/24` · PC4: `ip 10.10.20.14/24`

#### Bước 5 — Kiểm tra

**a) VLAN đã tạo và port gán đúng chưa:**
```
SW1# show vlan brief
```
**Output mẫu:**
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/3
10   SALES                            active    Gi0/1
20   IT                               active    Gi0/2
1002 fddi-default                     act/unsup
```
✅ **Checkpoint:** Gi0/1 nằm ở VLAN 10, Gi0/2 ở VLAN 20. **Gi0/0 KHÔNG xuất hiện** vì nó là trunk.

**b) Trunk đã lên chưa — lệnh quan trọng nhất của lab này:**
```
SW1# show interfaces trunk
```
**Output mẫu:**
```
Port        Mode             Encapsulation  Status        Native vlan
Gi0/0       on               802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/0       10,20

Port        Vlans allowed and active in management domain
Gi0/0       10,20

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/0       10,20
```
✅ **Checkpoint:** `Status = trunking` · `Vlans allowed = 10,20` · cả 4 bảng đều thấy 10,20.

**c) Ping test:**

| Từ | Đến | Mong đợi | Vì sao |
|---|---|:---:|---|
| PC1 | PC3 (10.10.10.13) | ✅ **Được** | Cùng VLAN 10, đi qua trunk |
| PC2 | PC4 (10.10.20.14) | ✅ **Được** | Cùng VLAN 20 |
| PC1 | PC2 (10.10.20.12) | ❌ **Không được** | Khác VLAN, chưa có router |
| PC1 | PC4 | ❌ Không được | Khác VLAN |

> ⭐ **Ping PC1→PC2 KHÔNG được là ĐÚNG, không phải lỗi.** Đây chính là bản chất của VLAN:
> tách broadcast domain. Muốn nói chuyện giữa VLAN thì cần **routing** — làm ở LAB P0-2.

#### ⚠️ Nếu trunk không lên — kiểm tra theo thứ tự

| # | Kiểm tra | Lệnh | Nguyên nhân thường gặp |
|:---:|---|---|---|
| 1 | Interface up/up? | `show ip int br` | Thiếu `no shutdown` |
| 2 | Cả 2 đầu đều `mode trunk`? | `show run int Gi0/0` | 1 đầu là access → lệch |
| 3 | Native VLAN 2 đầu có khớp? | `show int trunk` | Lệch → log cảnh báo, VLAN native bị lẫn |
| 4 | `allowed vlan` có chứa VLAN cần? | `show int trunk` | Quên `allowed vlan 10,20` |
| 5 | VLAN có tồn tại trên CẢ 2 switch? | `show vlan brief` | ⭐ **Lỗi phổ biến nhất:** tạo VLAN 20 trên SW1 mà quên SW2 |

#### 🧪 Thử nghiệm — làm để hiểu

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| Xóa VLAN 20 khỏi SW2 | SW2: `no vlan 20` | PC2 ping PC4 fail. `show int trunk` bảng 3 mất VLAN 20 | VLAN phải tồn tại ở **mọi switch** trên đường đi |
| Lệch native VLAN | SW1: `switchport trunk native vlan 99` | Console báo `%CDP-4-NATIVE_VLAN_MISMATCH` | Đề ENCOR hỏi về lỗi này |
| Bắt gói trên trunk | Click phải link SW1↔SW2 → **Capture** | Wireshark thấy **802.1Q header** với VLAN ID | ⭐ Tận mắt thấy cái tag 4 byte |
| Bắt gói trên access port | Capture link SW1↔PC1 | **Không có** 802.1Q header | Access port gửi frame không tag |
| Đổi allowed vlan | SW1: `switchport trunk allowed vlan 10` | PC2↔PC4 chết, PC1↔PC3 vẫn sống | `allowed vlan` lọc thật, không phải trang trí |

---

# LAB P0-2 — Inter-VLAN Routing (2 cách)

**Mục tiêu:** cho VLAN 10 và VLAN 20 nói chuyện được với nhau.

#### Cách A — Router-on-a-stick

Giữ nguyên LAB P0-1, thêm 1 router:

```
   [PC1 V10]──SW1──Gi0/0═══TRUNK═══Gi0/0──R1
   [PC2 V20]──/                            (Gi0/0.10 + Gi0/0.20)
```

**Cấu hình SW1 — biến Gi0/3 thành trunk về router:**
```
configure terminal
interface GigabitEthernet0/3
 description ---> TRUNK to R1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 switchport nonegotiate
 no shutdown
end
write memory
```

**Cấu hình R1 — sub-interface:**
```
enable
configure terminal
!
hostname R1
no ip domain lookup
!
interface GigabitEthernet0/0
 description ---> TRUNK to SW1
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 description ---> Gateway VLAN 10 SALES
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 description ---> Gateway VLAN 20 IT
 encapsulation dot1Q 20
 ip address 10.10.20.1 255.255.255.0
!
end
write memory
```

**Trên PC thêm default gateway** (VPCS):
```
! PC1
ip 10.10.10.11/24 10.10.10.1
save
! PC2
ip 10.10.20.12/24 10.10.20.1
save
```

**Kiểm tra:**
```
R1# show ip interface brief
```
**Output mẫu:**
```
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES manual up                    up
GigabitEthernet0/0.10      10.10.10.1      YES manual up                    up
GigabitEthernet0/0.20      10.10.20.1      YES manual up                    up
```

```
R1# show ip route
```
**Output mẫu (phần quan trọng):**
```
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
C        10.10.10.0/24 is directly connected, GigabitEthernet0/0.10
L        10.10.10.1/32 is directly connected, GigabitEthernet0/0.10
C        10.10.20.0/24 is directly connected, GigabitEthernet0/0.20
L        10.10.20.1/32 is directly connected, GigabitEthernet0/0.20
```

✅ **Checkpoint:**

| Kiểm tra | Mong đợi |
|---|---|
| PC1 ping 10.10.10.1 (gateway của mình) | ✅ được |
| PC1 ping 10.10.20.1 (gateway VLAN khác) | ✅ được |
| **PC1 ping PC2 (10.10.20.12)** | ✅ **được** ← mục tiêu của lab |
| `show ip route` trên R1 | Có 2 route `C` cho 2 VLAN |

⚠️ **Nếu PC1 ping PC2 không được:**

| Kiểm tra | Cách |
|---|---|
| PC đã có default gateway chưa? | VPCS: `show ip` → phải thấy dòng GATEWAY |
| Sub-interface có `encapsulation dot1Q <đúng VLAN>`? | `show run int Gi0/0.10` |
| Trunk SW1↔R1 có allow VLAN 10,20? | `show int trunk` trên SW1 |
| Sub-interface up/up? | `show ip int br` — nếu interface cha down thì con cũng down |

#### Cách B — SVI trên switch L3 (chuẩn production)

> ℹ️ vIOS-L2 hỗ trợ L3 hạn chế. Nếu lệnh `ip routing` không có, làm cách A là đủ cho Module-P0.
> Module-02 sẽ làm SVI kỹ hơn.

```
! Trên SW1 (nếu image hỗ trợ)
configure terminal
ip routing                          ! Bật routing — thiếu dòng này SVI không route
!
interface Vlan10
 ip address 10.10.10.1 255.255.255.0
 no shutdown
!
interface Vlan20
 ip address 10.10.20.1 255.255.255.0
 no shutdown
!
end
```

**So sánh 2 cách — bảng đề ENCOR hay hỏi:**

| | Router-on-a-stick | SVI (switch L3) |
|---|---|---|
| Thiết bị | Router + switch L2 | Multilayer switch |
| Điểm nghẽn | ⚠️ Mọi traffic inter-VLAN qua **1 link trunk** | Không — chuyển mạch trong ASIC |
| Tốc độ | Chậm (CPU router) | Rất nhanh (hardware) |
| Chi phí | Rẻ | Switch L3 đắt hơn |
| Thực tế | Mạng rất nhỏ / lab | ⭐ **Chuẩn của mọi campus** |

---

# LAB P0-3 — Quan sát & điều khiển STP (3 switch có vòng)

**Mục tiêu:** nhìn thấy STP làm việc, và tự ép root bridge theo ý muốn.

#### Topology — CÓ VÒNG LẶP (cố ý)

```
              SW1
            /     \
      Gi0/1         Gi0/2
        /             \
   Gi0/1               Gi0/1
    SW2 ───Gi0/2────Gi0/2─── SW3
```

| Link | Đầu A | Đầu B |
|---|---|---|
| 1 | SW1 Gi0/1 | SW2 Gi0/1 |
| 2 | SW1 Gi0/2 | SW3 Gi0/1 |
| 3 | SW2 Gi0/2 | SW3 Gi0/2 |

**RAM: 3× 768 MB = 2.3 GB** ✅

#### Bước 1 — Cấu hình tối thiểu cả 3 switch

```
! Làm giống nhau trên SW1, SW2, SW3 (chỉ đổi hostname)
enable
configure terminal
hostname SW1
no ip domain lookup
!
vlan 10
 name TEST
exit
!
interface range GigabitEthernet0/1 - 2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10
 switchport nonegotiate
 no shutdown
!
line con 0
 exec-timeout 0 0
 logging synchronous
end
write memory
```

#### Bước 2 — Ai đang là Root Bridge?

```
SW1# show spanning-tree vlan 10
```
**Output mẫu:**
```
VLAN0010
  Spanning tree enabled protocol ieee
  Root ID    Priority    32778
             Address     0c:1a:2b:00:01:00
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     0c:1a:2b:00:01:00
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
Gi0/2               Desg FWD 4         128.3    P2p
```

**Cách đọc output này — quan trọng:**

| Dòng | Nghĩa |
|---|---|
| `Priority 32778` | = 32768 (mặc định) + 10 (VLAN ID). ⭐ **Không phải ai đó đổi priority** |
| `This bridge is the root` | Switch này đang là Root Bridge |
| `Cost 4` | Link Gigabit = cost 4 (802.1D short mode) |
| `Role Desg` | Designated Port — được forward |
| `Sts FWD` | State = Forwarding |
| `Type P2p` | Point-to-point (full-duplex) |

**Chạy lệnh trên cả 3 switch, ghi vào bảng:**

| Switch | MAC address | Là root? | Port role |
|---|---|---|---|
| SW1 | | | |
| SW2 | | | |
| SW3 | | | |

✅ **Checkpoint:** Đúng **1 switch** báo `This bridge is the root`, và đó là switch có **MAC nhỏ nhất**
(vì priority cả 3 đều mặc định).

**Tìm port bị block:**
```
SW2# show spanning-tree vlan 10 | include BLK|Altn
```
**Output mẫu:**
```
Gi0/2               Altn BLK 4         128.3    P2p
```
✅ Có đúng **1 port ở trạng thái BLK/Altn** trong toàn mạng → vòng lặp đã bị phá.

#### Bước 3 — Ép SW1 làm Root Bridge

```
SW1(config)# spanning-tree vlan 10 priority 4096
```

Chờ ~30 giây rồi kiểm tra lại:
```
SW1# show spanning-tree vlan 10
```
**Output mẫu (đã đổi):**
```
  Root ID    Priority    4106
             Address     0c:1a:2b:00:01:00
             This bridge is the root
  Bridge ID  Priority    4106  (priority 4096 sys-id-ext 10)
```

> 💡 `4106 = 4096 + 10`. Luôn nhớ cộng VLAN ID.

**Xác nhận từ switch khác:**
```
SW2# show spanning-tree vlan 10
```
Phải thấy `Root ID Address` = MAC của SW1, và **không** còn dòng `This bridge is the root`.

✅ **Checkpoint:** SW1 là root · SW2 và SW3 đều trỏ Root ID về MAC của SW1 · vẫn có đúng 1 port BLK.

#### Bước 4 — 🚀 Đo thời gian hội tụ (bài quan trọng nhất)

**a) Với STP thường:**

1. Xác nhận mode: `show spanning-tree summary | include mode`
2. Từ 1 PC (hoặc dùng `ping` liên tục giữa 2 switch), chạy ping **không dừng**
3. Trên switch đang có Root Port hoạt động → `shutdown` port đó
4. **Đếm số gói ping mất**

**Kết quả mong đợi:** mất khoảng **15 gói** (~30 giây, direct failure = 2× forward delay).

**b) Chuyển sang Rapid PVST+ rồi đo lại:**

```
! Làm trên CẢ 3 switch
configure terminal
spanning-tree mode rapid-pvst
end
```

Lặp lại bài đo. **Kết quả mong đợi:** mất **1–3 gói** (vài giây).

**Ghi vào bảng:**

| Mode | Số gói ping mất | Thời gian hội tụ |
|---|:---:|---|
| PVST+ (802.1D) | | |
| Rapid PVST+ (802.1w) | | |

> ⭐ **Đây là bài lab giá trị nhất của Module-P0.** Bạn vừa **tự tay đo được** con số 30s vs vài giây
> mà sách chỉ ghi lý thuyết. Con số bạn tự đo sẽ không bao giờ quên.

#### 🧪 Thử nghiệm thêm

| Thử nghiệm | Gõ gì | Quan sát | Bài học |
|---|---|---|---|
| Ép root bằng macro | `spanning-tree vlan 10 root primary` | `show run \| inc priority` → IOS tự đặt 24586 | Macro tính priority thấp hơn root hiện tại |
| Priority không phải bội 4096 | `spanning-tree vlan 10 priority 5000` | IOS báo lỗi | Priority chỉ nhận bội số 4096 |
| Đổi cost để đổi Root Port | `int Gi0/1` → `spanning-tree cost 100` | Root Port chuyển sang port khác | Cost điều khiển đường đi |
| Bắt gói BPDU | Capture 1 link trunk | Wireshark → filter `stp` → thấy BPDU mỗi 2s | ⭐ Nhìn thấy Bridge ID, cost, timer thật |
| Root Guard | Port hướng SW3: `spanning-tree guard root` → rồi ép SW3 priority 0 | SW3 không lên được root, port thành `ROOT_Inc` | Cơ chế bảo vệ root |

