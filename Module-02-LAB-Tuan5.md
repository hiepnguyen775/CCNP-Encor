# LAB 02 — Tuần 5: MST · EtherChannel

> 📘 **Lý thuyết:** [Module-02](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md) —
> đọc **Phần 2 mục §3.3 (MST)** và **§3.5 (EtherChannel)** trước khi làm.
>
> ⏱️ **Thời gian:** ~6 giờ · 💾 **RAM:** 3 GB · 🧰 **Cần:** EVE-NG + 4× vIOS-L2
>
> 👉 **Dùng lại topology của [LAB Tuần 4](Module-02-LAB-Tuan4.md)** — không cần dựng mới.

---

## Lab này trả lời 5 câu hỏi

| # | Câu hỏi | Phần |
|:---:|---|:---:|
| 1 | MST gom nhiều VLAN vào một cây bằng cách nào? | 02-2A |
| 2 | Ba thứ phải giống nhau để hai switch cùng một MST region là gì? | 02-2A |
| 3 | Sai một ký tự trong tên region thì chuyện gì xảy ra? | 02-2A |
| 4 | Gộp 2 cáp thành 1 đường — STP có còn chặn nữa không? | 02-2B |
| 5 | Vì sao EtherChannel lên `(I)` individual lại nguy hiểm hơn `(s)` suspended? | 02-2B |

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Làm LAB Tuần 4 trước** | Lab này dùng lại đúng topology 4 switch đó |
| **MST rất kén chính tả** | Tên region **phân biệt hoa–thường**. Sai 1 ký tự = 2 region khác nhau |
| **Đổi MST làm mạng hội tụ lại** | Bình thường. Chờ vài giây rồi mới xem kết quả |
| **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) |

---

## 🧪 9. LAB — TUẦN 5: MST · ETHERCHANNEL

### LAB 02-2A — MST

Dùng lại topology LAB 02-1 (4 switch).

#### Bước 1 — Thêm VLAN để thấy giá trị của MST

```
! Trên CẢ 4 switch
configure terminal
vlan 10
 name USERS-A
vlan 20
 name USERS-B
vlan 30
 name USERS-C
vlan 40
 name SERVERS-A
vlan 50
 name SERVERS-B
vlan 60
 name SERVERS-C
exit
!
! Cho phép trên mọi trunk
interface range GigabitEthernet0/1 - 3
 switchport trunk allowed vlan 10,20,30,40,50,60
end
```

**Xem gánh nặng của Rapid PVST+ với 6 VLAN:**
```
SW-D1# show spanning-tree summary totals
```
**Output mẫu:**
```
Switch is in rapid-pvst mode
...
Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
6 vlans                       6         0        0         18         24
```
⭐ **6 VLAN = 6 instance STP.** Hình dung 500 VLAN → 500 instance.

#### Bước 2 — Chuyển sang MST

```
! Làm GIỐNG NHAU trên CẢ 4 switch — không được sai 1 ký tự
configure terminal
!
spanning-tree mode mst
!
spanning-tree mst configuration
 name CAMPUS-01
 revision 1
 instance 1 vlan 10,20,30
 instance 2 vlan 40,50,60
 exit
!
end
write memory
```

#### Bước 3 — Ép root cho từng instance (load-balance)

```
! SW-D1: root MST1, backup MST2
SW-D1(config)# spanning-tree mst 1 priority 4096
SW-D1(config)# spanning-tree mst 2 priority 8192

! SW-D2: root MST2, backup MST1
SW-D2(config)# spanning-tree mst 2 priority 4096
SW-D2(config)# spanning-tree mst 1 priority 8192
```

#### Bước 4 — Kiểm tra

**a) ⭐ Lệnh đầu tiên khi troubleshoot MST — xác nhận region:**
```
SW-D1# show spanning-tree mst configuration
```
**Output mẫu:**
```
Name      [CAMPUS-01]
Revision  1     Instances configured 3

Instance  Vlans mapped
--------  ---------------------------------------------------------------------
0         1-9,11-19,21-29,31-39,41-49,51-59,61-4094
1         10,20,30
2         40,50,60
-------------------------------------------------------------------------------
```

**b) So sánh digest giữa các switch — cách nhanh nhất để phát hiện lệch region:**
```
SW-D1# show spanning-tree mst configuration digest
```
**Output mẫu:**
```
Name      [CAMPUS-01]
Revision  1     Instances configured 3
Digest    0x1A2B3C4D5E6F708192A3B4C5D6E7F809
Pre-std Digest  0x...
```
⭐ **Chạy lệnh này trên cả 4 switch. `Digest` PHẢI GIỐNG NHAU HOÀN TOÀN.**
Lệch 1 ký tự = lệch region = cây bị chia đôi.

**Điền bảng:**

| Switch | Name | Revision | Digest (8 ký tự đầu) | Cùng region? |
|---|---|:---:|---|:---:|
| SW-D1 | | | | |
| SW-D2 | | | | |
| SW-A1 | | | | |
| SW-A2 | | | | |

**c) Xem cây từng instance:**
```
SW-D1# show spanning-tree mst
```
**Output mẫu:**
```
##### MST0    vlans mapped:   1-9,11-19,21-29,31-39,41-49,51-59,61-4094
Bridge        address 0c1a.2b00.d100  priority  32768 (32768 sysid 0)
Root          this switch for the CIST
Operational   hello time 2, forward delay 15, max age 20, txholdcount 6
Configured    hello time 2, forward delay 15, max age 20, max hops 20

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi0/1            Desg FWD 20000     128.2    P2p
Gi0/2            Desg FWD 20000     128.3    P2p
Gi0/3            Desg FWD 20000     128.4    P2p

##### MST1    vlans mapped:   10,20,30
Bridge        address 0c1a.2b00.d100  priority  4097  (4096 sysid 1)
Root          this switch for MST1

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi0/1            Desg FWD 20000     128.2    P2p
Gi0/2            Desg FWD 20000     128.3    P2p
Gi0/3            Desg FWD 20000     128.4    P2p

##### MST2    vlans mapped:   40,50,60
Bridge        address 0c1a.2b00.d100  priority  8194  (8192 sysid 2)
Root          0c1a.2b00.d200  priority 4098  cost 20000
              port Gi0/3
```

⭐ **Đọc output này:**
- `priority 4097 (4096 sysid 1)` → priority 4096 + **instance ID 1** (không phải VLAN ID như PVST+!)
- MST1: `Root this switch` → SW-D1 là root
- MST2: `Root 0c1a.2b00.d200` → SW-D2 là root ✅ load-balance thành công
- `Cost 20000` → MST dùng **long path cost** mặc định (1 Gbps = 20000)

> ⭐ **Bẫy đề:** trong MST, `sysid` là **Instance ID**, không phải VLAN ID.
> MST1 priority 4096 → hiện **4097**. Trong PVST+ thì VLAN 10 priority 4096 → hiện **4106**.

**d) Xem giảm gánh nặng:**
```
SW-D1# show spanning-tree summary totals
```
**Output mẫu:**
```
Switch is in mst mode (IEEE Standard)
...
Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
3 msts                        2         0        0          7          9
```
⭐ **Từ "6 vlans" xuống "3 msts"** (MST0 + MST1 + MST2). Với 500 VLAN thì vẫn là 3 msts.

**e) Xem port role cho 1 instance cụ thể:**
```
SW-A1# show spanning-tree mst 1
SW-A1# show spanning-tree mst 2
SW-A1# show spanning-tree mst interface GigabitEthernet0/1
```

✅ **Checkpoint LAB 02-2A:**

| Kiểm tra | Mong đợi |
|---|---|
| `show spanning-tree mst configuration digest` giống nhau trên cả 4 switch | ⭐ ✅ |
| MST1 root = SW-D1 · MST2 root = SW-D2 | ✅ |
| Trên SW-A1: Root Port của MST1 ≠ Root Port của MST2 | ⭐ ✅ Load-balance |
| `show spanning-tree summary totals` báo `3 msts` (không phải `6 vlans`) | ✅ |
| Ping PC1↔PC2 vẫn hoạt động | ✅ |

#### Bước 5 — ⭐ Tái hiện lỗi MST kinh điển (làm để nhớ mãi)

**Lỗi: thiếu 1 VLAN trong mapping trên 1 switch**

```
! Trên SW-A2 — cố ý làm SAI: bỏ VLAN 30 khỏi instance 1
SW-A2(config)# spanning-tree mst configuration
SW-A2(config-mst)# instance 1 vlan 10,20
SW-A2(config-mst)# exit
```

**Quan sát:**
```
SW-A2# show spanning-tree mst configuration digest
```
→ **Digest ĐÃ ĐỔI** → SW-A2 ra khỏi region.

```
SW-A2# show spanning-tree mst | include Boun|Bound
```
→ Port uplink của SW-A2 giờ là **boundary port**.

```
SW-A2# show spanning-tree mst 1
```
→ Cây MST1 nhìn khác hoàn toàn so với 3 switch kia.

⭐ **Bài học:** chỉ thiếu **1 VLAN** trong mapping → switch ra khỏi region → topology thay đổi.
Đây là lỗi số 1 khi triển khai MST ở production. **Ghi vào `SO-TAY-LOI.md`.**

**Sửa lại:**
```
SW-A2(config)# spanning-tree mst configuration
SW-A2(config-mst)# instance 1 vlan 10,20,30
SW-A2(config-mst)# exit
```
Xác nhận digest quay về giống 3 switch kia.

**Lỗi 2: lệch revision number**
```
SW-A1(config)# spanning-tree mst configuration
SW-A1(config-mst)# revision 2                    ! cố ý sai
SW-A1(config-mst)# exit
```
→ Digest cũng đổi → cùng hậu quả. Sửa về `revision 1`.

---

### LAB 02-2B — EtherChannel

#### Bước 1 — L2 EtherChannel với LACP

Gộp 2 link giữa SW-D1 và SW-D2. Hiện tại chỉ có Gi0/3 — thêm link thứ 2:

1. Trong EVE-NG: **Stop** SW-D1 và SW-D2 (không nối được dây khi node đang chạy)
2. Nối thêm: `SW-D1 Gi0/4` ↔ `SW-D2 Gi0/4`
3. Start lại

> 💡 Khi Add node, nhớ đặt **Ethernets = 6** để có đủ port. Nếu đã tạo với 4 port,
> phải xóa node và tạo lại (hoặc dùng cặp port khác đang rỗi).

**Cấu hình SW-D1:**
```
configure terminal
!
! === Bước 1: xóa cấu hình cũ trên member port (quan trọng) ===
default interface GigabitEthernet0/3
!
! === Bước 2: chỉ gõ channel-group trên member port ===
interface range GigabitEthernet0/3 - 4
 description ---> ETHERCHANNEL to SW-D2
 channel-protocol lacp
 channel-group 1 mode active
 no shutdown
!
! === Bước 3: MỌI cấu hình khác gõ trên Port-channel ===
interface Port-channel1
 description ---> Po1 to SW-D2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60
 switchport trunk native vlan 999
 switchport nonegotiate
 no shutdown
!
end
write memory
```

**Cấu hình SW-D2:** giống hệt (dùng `channel-group 1 mode active`).

> 💡 `default interface Gi0/3` xóa toàn bộ cấu hình interface về mặc định — rất tiện khi làm lại.

#### Bước 2 — Kiểm tra

**a) ⭐ Lệnh quan trọng nhất:**
```
SW-D1# show etherchannel summary
```
**Output mong đợi:**
```
Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------------------
1      Po1(SU)         LACP      Gi0/3(P)    Gi0/4(P)
```
✅ **Checkpoint:** `Po1(SU)` và **cả 2 port đều `(P)`**.

⚠️ Nếu thấy `(I)`, `(s)`, `(u)`, `(D)` → xem bảng §6.7 và §10.2.

**b) Thấy partner không:**
```
SW-D1# show lacp neighbor
```
**Output mẫu:**
```
Flags:  S - Device is requesting Slow LACPDUs
        F - Device is requesting Fast LACPDUs
        A - Device is in Active mode       P - Device is in Passive mode

Channel group 1 neighbors
Partner's information:
                  LACP port                        Oper    Port     Port
Port      Flags   Priority  Dev ID          Age    Key     Number   State
Gi0/3     SA      32768     0c1a.2b00.d200  12s    0x1     0x104    0x3D
Gi0/4     SA      32768     0c1a.2b00.d200  15s    0x1     0x105    0x3D
```
✅ Thấy `Dev ID` của SW-D2 → LACP bắt tay thành công.
`Flags SA` = **S**low LACPDU + **A**ctive mode.

**c) STP giờ chỉ thấy 1 port logic:**
```
SW-D1# show spanning-tree mst 1 | include Po1|Gi0/3|Gi0/4
```
**Output mẫu:**
```
Po1              Desg FWD 10000     128.65   P2p
```
⭐ **Chỉ có `Po1`, không còn `Gi0/3`/`Gi0/4` riêng lẻ.** Và cost = **10000** thay vì 20000
(2 link 1G gộp lại = 2 Gbps → cost giảm một nửa).

**d) Interface Port-channel dùng như interface thường:**
```
SW-D1# show interfaces Port-channel1
SW-D1# show interfaces trunk
```
→ `Po1` xuất hiện như 1 trunk bình thường.

#### Bước 3 — ⭐ Test failover (giá trị nhất)

**a) Ping liên tục PC1 → PC2** (đường đi qua Po1):
```
PC1> ping 10.10.10.12 -c 200
```

**b) Cắt 1 member link:**
```
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# shutdown
```

**c) Đếm gói mất:**
```
SW-D1# show etherchannel summary
```
```
1      Po1(SU)         LACP      Gi0/3(D)    Gi0/4(P)
```
⭐ `Po1` **vẫn `(SU)`** — bundle còn sống, chỉ mất 1 member.

⭐ **BẢNG SO SÁNH — điền vào:**

| Tình huống | Số gói ping mất | Có Topology Change? |
|---|:---:|:---:|
| Cắt 1 member của EtherChannel | | |
| (so sánh với LAB 02-1) Cắt Root Port khi **không** có EtherChannel, Rapid PVST+ | | |

**Kết quả mong đợi:** cắt member EtherChannel mất **0–1 gói** và **KHÔNG có TC**
(vì STP không thấy gì thay đổi — `Po1` vẫn up). Đây là ưu điểm lớn nhất của EtherChannel
so với dựa vào STP.

**Kiểm tra không có TC:**
```
SW-A1# show spanning-tree mst 1 detail | include topology change
```

**d) Bật lại:**
```
SW-D1(config-if)# no shutdown
```

#### Bước 4 — Tái hiện các lỗi EtherChannel (làm để nhớ)

**Lỗi 1 — `passive + passive` không bundle**
```
SW-D1(config)# interface range Gi0/3 - 4
SW-D1(config-if-range)# channel-group 1 mode passive
! Trên SW-D2 cũng passive
```
```
show etherchannel summary
```
→ Port thành `(s)` **suspended** hoặc bundle không lên.
**Bài học:** phải có ít nhất 1 bên `active`. Sửa: đưa 1 bên về `active`.

---

**Lỗi 2 — ⚠️ Trộn `on` với LACP (nguy hiểm nhất)**
```
SW-D1(config)# interface range Gi0/3 - 4
SW-D1(config-if-range)# channel-group 1 mode on          ! static
! SW-D2 vẫn để mode active (LACP)
```
```
SW-D2# show etherchannel summary
```
→ SW-D2 báo `Gi0/3(I) Gi0/4(I)` — **individual**.

⚠️ **Nguy hiểm:** SW-D1 gộp 2 port thành 1 (không gửi BPDU riêng), SW-D2 coi là 2 port riêng
→ **có thể tạo loop**.

**Xem misconfig guard bảo vệ:**
```
SW-D2# show spanning-tree summary | include misconfig
EtherChannel misconfig guard is enabled
```
Nếu loop hình thành, guard này sẽ err-disable port.

**Sửa:** đưa cả 2 bên về cùng protocol (`active`/`active`).

---

**Lỗi 3 — Tham số lệch giữa member port**
```
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# switchport trunk allowed vlan 10          ! cố ý khác Gi0/4
```
```
show etherchannel summary
```
→ `Gi0/3(u)` — **unsuitable for bundling**.

```
SW-D1# show interfaces Gi0/3 etherchannel | include reason|Reason
! hoặc xem log
SW-D1# show logging | include EC5|ETHERCHANNEL
%EC-5-CANNOT_BUNDLE2: Gi0/3 is not compatible with Gi0/4 and will be suspended
                      (trunk vlan mismatch)
```
⭐ **Log nói thẳng nguyên nhân: `trunk vlan mismatch`.**

**Sửa:**
```
SW-D1(config)# default interface GigabitEthernet0/3
SW-D1(config)# interface GigabitEthernet0/3
SW-D1(config-if)# channel-group 1 mode active
```
→ Rồi cấu hình lại **trên `interface Port-channel1`**, không trên member.

**Bài học:** đây là lý do quy tắc *"chỉ gõ `channel-group` trên member, mọi thứ khác trên Port-channel"*.

#### Bước 5 — LACP nâng cao & load-balancing

```
! LACP rate fast — phát hiện lỗi trong 3 s thay vì 90 s
SW-D1(config)# interface range GigabitEthernet0/3 - 4
SW-D1(config-if-range)# lacp rate fast
! ⚠️ Phải đặt CẢ 2 BÊN
```
```
SW-D1# show lacp neighbor | include Flags|Gi0
```
→ Flag đổi từ `SA` (Slow+Active) sang **`FA`** (Fast+Active).

```
! min-links: bundle chỉ up khi có ≥ 2 link
SW-D1(config)# interface Port-channel1
SW-D1(config-if)# port-channel min-links 2
```
Test: shutdown 1 member → **cả Po1 xuống** (`Po1(SM)` = minimum links not met).

> ⭐ **Vì sao dùng min-links:** nếu bạn có 4×10G = 40G và 3 link chết, 1 link 10G còn lại
> sẽ **bị dội 40G traffic** → drop nghiêm trọng. Thà cho bundle xuống để traffic đi đường khác.

**Hoàn tác:**
```
SW-D1(config-if)# no port-channel min-links
```

```
! Load-balancing
SW-D1# show etherchannel load-balance
SW-D1(config)# port-channel load-balance src-dst-ip
SW-D1# show etherchannel load-balance
```

#### Bước 6 — 🚀 L3 EtherChannel (nâng cao)

Nếu image hỗ trợ `ip routing`:
```
! Trên SW-D1
configure terminal
ip routing
!
default interface range GigabitEthernet0/3 - 4
!
interface range GigabitEthernet0/3 - 4
 no switchport                          ! TRƯỚC channel-group
 channel-group 2 mode active
 no shutdown
!
interface Port-channel2
 no switchport
 ip address 10.99.99.1 255.255.255.252
 no shutdown
end
```
Trên SW-D2: `ip address 10.99.99.2 255.255.255.252`

**Kiểm tra:**
```
SW-D1# show etherchannel summary
```
→ `Po2(RU)` — **R** = Layer3, **U** = in use.

```
SW-D1# ping 10.99.99.2
SW-D1# show spanning-tree mst 1 | include Po2
```
→ **`Po2` KHÔNG xuất hiện trong STP** (vì là L3, không tham gia STP).

✅ **Checkpoint LAB 02-2B:**

| Kiểm tra | Mong đợi |
|---|---|
| `show etherchannel summary` → `Po1(SU)` + cả 2 port `(P)` | ✅ |
| `show lacp neighbor` thấy Dev ID của switch đối diện | ✅ |
| STP chỉ thấy `Po1`, không thấy member riêng lẻ | ⭐ ✅ |
| Cắt 1 member: mất 0–1 gói ping, **không có TC** | ⭐ ✅ |
| Tái hiện được `(s)`, `(I)`, `(u)` và giải thích từng cái | ✅ |
| L3 EtherChannel: `Po2(RU)`, ping được, không có trong STP | ✅ |

