# Module-08 — Virtualization & Overlay

> 🧭 **Lộ trình:** [Module-07B](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md) → `[Bạn đang ở đây] Module-08` → Module-09 (Architecture & QoS)
>
> 📊 **Blueprint — Domain 2.0 Virtualization (10% đề) — TRỌN VẸN một domain trong một module:**
> · **2.1 — Describe device virtualization technologies** (2.1.a hypervisor type 1 & 2 · 2.1.b virtual machine · 2.1.c virtual switching)
> · 🔴 ⭐⭐ **2.2 — CONFIGURE AND VERIFY data path virtualization technologies** (2.2.a VRF · 2.2.b GRE and IPsec tunneling)
> · **2.3 — Describe network virtualization concepts** (2.3.a LISP · 2.3.b VXLAN)
>
> ⏱️ **Tuần 14** · 10 giờ

---

## ⭐ 0. Phạm vi

### 0.1 Bảng "Configure" vs "Describe" — quyết định bạn học sâu tới đâu

| Chủ đề | Blueprint dùng từ | ⭐ Nghĩa | Thời gian |
|---|---|---|---|
| Hypervisor type 1 / 2 | 🟡 *Describe* | ⭐ **Chỉ khái niệm.** ⭐ Bạn làm DevOps Proxmox → **phần này gần như miễn phí** | 20 phút |
| Virtual machine | 🟡 *Describe* | Khái niệm | 15 phút |
| ⭐ Virtual switching | 🟡 *Describe* | ⭐ Hiểu vSwitch khác switch vật lý chỗ nào · ⭐ **3 kiểu gán VLAN (EST/VST/VGT)** | 45 phút |
| 🔴 ⭐⭐ **VRF** | 🔴 ⭐⭐ ***Configure and verify*** | ⭐⭐ **Cấu hình + verify + troubleshoot.** ⭐ **Phải lab** | 2.5 giờ |
| 🔴 ⭐⭐ **GRE** | 🔴 ⭐⭐ ***Configure and verify*** | ⭐⭐ **Phải lab** — kể cả bẫy recursive routing & MTU | 2 giờ |
| 🔴 ⭐⭐ **IPsec** | 🔴 ⭐⭐ ***Configure and verify*** | ⭐⭐ **Phải lab.** ⭐ Trọng tâm: **GRE over IPsec** | 2.5 giờ |
| 🟡 **LISP** | 🟡 *Describe* | ⭐ **Vai trò từng thành phần + luồng map-request.** ⭐ **KHÔNG cần cấu hình** | 1 giờ |
| 🟡 **VXLAN** | 🟡 *Describe* | ⭐ **VNI 24-bit, VTEP, UDP 4789, underlay/overlay.** ⭐ **KHÔNG cần cấu hình** | 1 giờ |

> 🔴 ⭐⭐ **Đây là module "nửa nạc nửa mỡ" — và đó chính là bẫy.**
> ⭐ **VRF + GRE + IPsec phải gõ được bằng tay** (2.2 nói *"Configure and verify"*).
> ⭐ **LISP + VXLAN chỉ cần nói được bằng lời** (2.3 nói *"Describe"*).
> 🔴 ⭐ **Sai lầm điển hình: dành 3 ngày mê mẩn VXLAN EVPN** (rất hot, rất hay) —
> rồi vào phòng thi **không cấu hình nổi GRE over IPsec**. ⭐ **Đừng làm vậy.**

### 0.2 ⭐ Lợi thế riêng của bạn ở module này

> ⭐ Bạn **vận hành cụm ảo hóa Proxmox** → mục **2.1 (hypervisor, VM, vSwitch)** bạn **đã làm hằng ngày**.
> ⭐ Chỉ cần **dịch từ vựng** sang cách Cisco/VMware gọi. Module này sẽ **đối chiếu song song** giúp bạn (§2).
>
> ⭐ **Ngược lại, hãy cẩn thận:** biết vSwitch Linux bridge **không** có nghĩa là biết
> ⭐ **VXLAN** hay ⭐ **LISP** — đó là hai thứ hoàn toàn khác, ở tầng khác. Đừng chủ quan.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-03 (bảng định tuyến, AD, static, redistribute) · Module-04A (OSPF cơ bản — sẽ chạy OSPF qua tunnel) · Module-P0 §2.7 (NAT, ACL) |
| **Lab** | ⭐ **Quay lại EVE-NG!** 4 router: `R1` (site A) · `R2` (site B) · `R-ISP` (Internet) · `R3` (site A, cho VRF) |
| **Image** | ⭐ **vIOS 512 MB** cho phần VRF + GRE.<br>🔴 ⭐ **Phần IPsec:** nhiều image vIOS **thiếu feature crypto** → nếu `crypto isakmp policy` báo lỗi, đổi **R1 + R2 sang CSR1000v (3 GB mỗi con)**. Xem §1.1 |
| **RAM** | ⭐ **~2 GB** (4× vIOS) · ⭐ **~7 GB** nếu phải dùng 2× CSR1000v cho IPsec ✅ vẫn nằm trong ngân sách 10 GB |
| **Thời lượng** | 4h lý thuyết · 5h lab · 1h quiz |

### 1.1 ⭐ Xử lý trước vấn đề crypto trên vIOS

```
! KIỂM TRA TRƯỚC KHI LÀM BƯỚC IPsec — gõ trên R1:
R1(config)# crypto isakmp policy 10
```

| Kết quả | ⭐ Nghĩa | ⭐ Làm gì |
|---|---|---|
| Vào được `config-isakmp` | ✅ Image có crypto | ⭐ Làm lab bình thường với vIOS |
| `% Invalid input detected` | 🔴 Image thiếu feature crypto | ⭐ **Đổi R1 & R2 sang CSR1000v** (3 GB/con), giữ R-ISP là vIOS |

⭐ **Kiểm tra thêm:** `show version | include Security|securityk9` — có `securityk9` là có crypto.

> ⭐ **Nếu máy không kham nổi 2× CSR1000v:** ⭐ **vẫn làm được LAB VRF và GRE đầy đủ** (là 2/3 nội dung
> "configure and verify"), rồi ⭐ **đọc kỹ cấu hình IPsec ở §6 và gõ chay để thuộc lệnh**.
> ⭐ Đề ENCOR hỏi IPsec chủ yếu ở mức *"dòng nào sai"*, *"phase 1 hay phase 2 hỏng"* — đọc kỹ vẫn ăn điểm được.

---

## 📘 2. DEVICE VIRTUALIZATION (blueprint 2.1)

### 2.1 ⭐ Hypervisor Type 1 vs Type 2

```
   ═══ TYPE 1 (bare metal) ═══          ═══ TYPE 2 (hosted) ═══

   ┌─────┬─────┬─────┐                  ┌─────┬─────┐
   │ VM  │ VM  │ VM  │                  │ VM  │ VM  │
   ├─────┴─────┴─────┤                  ├─────┴─────┤
   │  HYPERVISOR  │                  │ HYPERVISOR│
   ├─────────────────┤                  ├───────────┴──────┐
   │   PHẦN CỨNG     │                  │  HỆ ĐIỀU HÀNH │
   └─────────────────┘                  ├──────────────────┤
                                         │   PHẦN CỨNG      │
   Chạy THẲNG trên phần cứng          └──────────────────┘
                                         Chạy TRÊN một OS khác
```

| | ⭐ **Type 1 (bare metal / native)** | ⭐ **Type 2 (hosted)** |
|---|---|---|
| Chạy trên | ⭐ **Phần cứng trực tiếp** | ⭐ **Một hệ điều hành chủ** |
| Hiệu năng | ⭐ **Cao** (ít lớp trung gian) | Thấp hơn |
| Ví dụ | ⭐ **VMware ESXi · Microsoft Hyper-V · KVM · ⭐ Proxmox VE · Citrix XenServer** | ⭐ **VMware Workstation · VirtualBox · Parallels · VMware Fusion** |
| Dùng ở đâu | ⭐ **Data center, production** | ⭐ **Máy cá nhân, lab, dev** |

> ⭐ **Nhìn ngay vào lab của bạn:** ⭐ **VMware Workstation = Type 2** (chạy trên Windows).
> Bên trong nó là **EVE-NG**, và EVE-NG lại dùng **KVM = Type 1** để chạy các node.
> ⭐ Còn cụm **Proxmox** bạn quản lý ở công ty = ⭐ **Type 1** (Debian + KVM/QEMU).
> ⭐ **Đó là toàn bộ mục 2.1.a.** Bạn đã biết rồi.

⭐ **Vài thuật ngữ đi kèm hay bị hỏi:**

| Thuật ngữ | Nghĩa |
|---|---|
| **VMM** (Virtual Machine Monitor) | Tên kỹ thuật khác của hypervisor |
| ⭐ **Guest / Host** | Máy ảo / máy vật lý chứa nó |
| ⭐ **Overcommit** | Cấp cho các VM **tổng cộng nhiều hơn** tài nguyên vật lý thật có |
| ⭐ **Snapshot** | Chụp trạng thái VM tại một thời điểm |
| ⭐ **Live migration / vMotion** | ⭐ Chuyển VM đang chạy sang host khác **không tắt máy**. 🔴 ⭐ **Đây là lý do DC cần VXLAN** (§8) |
| **Container** | ⭐ Chia sẻ **kernel** của host, không có OS riêng → nhẹ hơn VM rất nhiều. *(Docker, LXC)* |

### 2.2 ⭐ Virtual Machine — thành phần

| Thành phần ảo | Tương ứng vật lý |
|---|---|
| **vCPU** | Nhân CPU |
| **vRAM** | Thanh RAM |
| **vDisk** (VMDK / QCOW2 / raw) | Ổ cứng |
| ⭐ **vNIC** | ⭐ **Card mạng** — ⭐ **có MAC address riêng**, cắm vào **vSwitch** |

> ⭐ **Điểm mạng học quan trọng nhất:** ⭐ **mỗi vNIC có một MAC riêng và nó xuất hiện trong
> bảng MAC của switch vật lý** (nếu traffic ra ngoài).
> 🔴 ⭐ **Hệ quả thực tế:** một host vật lý cắm 1 sợi cáp có thể làm switch học **hàng chục MAC trên một port** —
> ⭐ **đây là lý do KHÔNG bật `switchport port-security maximum 1` trên port nối host ảo hóa.**

### 2.3 ⭐⭐ Virtual Switching (2.1.c) — phần đề hỏi nhiều nhất của mục 2.1

```
        ┌──────────────── HOST VẬT LÝ (hypervisor) ────────────────┐
        │                                                          │
        │   [VM1]      [VM2]      [VM3]                            │
        │    │vNIC      │vNIC      │vNIC                           │
        │    └────┬─────┴────┬─────┘                               │
        │      ┌──┴──────────┴──┐                                  │
        │      │  vSWITCH    │  (phần mềm, chạy trong hypervisor)│
        │      └────────┬───────┘                                  │
        │            uplink (pNIC vật lý)                        │
        └────────────────┼─────────────────────────────────────────┘
                         │  thường là TRUNK 802.1Q
                 ┌───────┴────────┐
                 │ SWITCH VẬT LÝ  │
                 └────────────────┘
```

#### ⭐⭐ vSwitch KHÁC switch vật lý ở đâu — bảng phải nhớ

| | Switch vật lý | ⭐ **vSwitch** |
|---|---|---|
| ⭐ **Chạy STP?** | ✅ Có | 🔴 ⭐⭐ **KHÔNG** — và **không cần** |
| ⭐ Vì sao không cần STP | — | ⭐⭐ **vSwitch KHÔNG BAO GIỜ forward giữa hai uplink** → ⭐ **về mặt kiến trúc không thể tạo loop** |
| ⭐ **Học MAC từ uplink?** | ✅ Có | 🔴 ⭐ **KHÔNG** — nó **đã biết trước** MAC của các VM cắm vào nó |
| Xử lý gói lạ (unknown unicast) | Flood | ⭐ **Drop** (nếu không phải MAC của VM nào) |
| ⭐ Chạy giao thức mạng (CDP/LLDP, LACP…) | Đầy đủ | ⭐ Hạn chế — tùy loại vSwitch |
| ⭐ **Cấu hình ở đâu** | Trên chính switch | ⭐ Trong hypervisor / trình quản lý tập trung |

> 🔴 ⭐⭐ **Câu hỏi đề rất hay ra:** *"Vì sao vSwitch không cần STP?"*
> ⭐ **Vì nó không bao giờ chuyển tiếp frame từ uplink này sang uplink khác** →
> ⭐ **không thể tạo vòng lặp**. (Nó chỉ chuyển VM↔VM và VM↔uplink.)

#### ⭐ Các loại vSwitch

| Loại | Nền tảng | Ghi chú |
|---|---|---|
| ⭐ **vSS** (vSphere Standard Switch) | VMware | ⭐ Cấu hình **trên từng host** — 50 host thì sửa 50 lần |
| ⭐ **vDS** (vSphere Distributed Switch) | VMware | ⭐ **Cấu hình một chỗ, áp cho cả cụm** — cần license cao hơn |
| ⭐ **Linux bridge** (`vmbr0`) | ⭐ **KVM / Proxmox** | ⭐ Cái bạn đang dùng |
| ⭐ **Open vSwitch (OVS)** | KVM/Proxmox/nhiều nơi | Nhiều tính năng hơn (OpenFlow, VXLAN, LACP thật) |
| **Hyper-V Virtual Switch** | Microsoft | External / Internal / Private |
| **Nexus 1000v** | Cisco (đã EOL) | ⭐ vSwitch nói **NX-OS** — Cisco từng bán để mạng-network quản được lớp ảo |

#### ⭐⭐ Ba kiểu gán VLAN — EST / VST / VGT (đề hay hỏi)

| Kiểu | Ai gắn thẻ 802.1Q | Port switch vật lý | ⭐ Dùng khi |
|---|---|---|---|
| ⭐ **EST** — External Switch Tagging | ⭐ **Switch vật lý** | ⭐ **Access port** | Host chỉ cần **một** VLAN. vSwitch để VLAN ID = **0** |
| ⭐⭐ **VST** — Virtual Switch Tagging | ⭐⭐ **vSwitch** | ⭐⭐ **TRUNK** | ⭐⭐ **Phổ biến nhất.** Mỗi port group gán một VLAN ID (1–4094) |
| ⭐ **VGT** — Virtual Guest Tagging | ⭐ **Chính VM (guest OS)** | ⭐ **Trunk** | ⭐ VM cần **nhiều VLAN** (VD: một VM firewall/router ảo). VMware: port group VLAN **4095** |

> ⭐ **Đối chiếu Proxmox cho bạn:**
> · ⭐ **VST** = bridge bật **"VLAN aware"**, rồi đặt **VLAN Tag** trên từng vNIC của VM
> · ⭐ **EST** = bridge thường, không tag gì, port switch để access
> · ⭐ **VGT** = bridge VLAN-aware + để trống tag + đặt **VLAN range** cho phép → VM tự tag
>
> ⭐ **Kiến thức Cisco bạn cần thêm:** ⭐ **port nối host ảo hóa gần như luôn là trunk**, và ⭐ **native VLAN
> phải khớp** với cấu hình quản lý của host. 🔴 ⭐ **Native VLAN lệch = mất quản lý host** —
> đây là lỗi làm sập cụm thật sự.

⭐ **Vài thuật ngữ nâng cao (chỉ cần biết tên):**

| | Nghĩa |
|---|---|
| ⭐ **SR-IOV** | VM nói **thẳng** với card mạng vật lý, bỏ qua vSwitch → nhanh, nhưng ⭐ **mất live migration và mất khả năng giám sát** |
| **PCI Passthrough** | Gán hẳn một thiết bị PCI cho VM |
| **DPDK** | Tăng tốc xử lý gói trong không gian người dùng |
| ⭐ **NFV** (Network Functions Virtualization) | ⭐ Chạy **router/firewall/LB dưới dạng VM** thay vì hộp cứng. VD: **CSR1000v/Cat8000v** chính là NFV |

---

## 📘 3. ⭐⭐ VRF (blueprint 2.2.a — CONFIGURE AND VERIFY)

### 3.1 VRF là gì

> ⭐⭐ **VRF (Virtual Routing and Forwarding)** = ⭐ **chia MỘT router thật thành NHIỀU router logic**,
> mỗi cái có ⭐ **bảng định tuyến RIÊNG**, hoàn toàn cách ly nhau.

```
        ═══ MỘT ROUTER VẬT LÝ ═══

   ┌──────────────────────────────────────┐
   │  VRF "KHACH-A"                    │   Gi0/1 ──► 10.10.10.0/24
   │  · bảng route riêng                  │
   │  · OSPF process riêng                │
   ├──────────────────────────────────────┤
   │  VRF "KHACH-B"                    │   Gi0/2 ──► 10.10.10.0/24  TRÙNG IP!
   │  · bảng route riêng                  │
   ├──────────────────────────────────────┤
   │  GLOBAL routing table (mặc định)  │   Gi0/0 ──► ra Internet
   └──────────────────────────────────────┘

   Ba bảng route hoàn toàn ĐỘC LẬP. Không thấy nhau. Trùng IP vẫn OK.
```

| ⭐ Đặc điểm | Chi tiết |
|---|---|
| ⭐⭐ **Bảng route riêng** | Mỗi VRF có `show ip route vrf <tên>` riêng |
| ⭐⭐ **IP trùng nhau được** | ⭐ **Đây là siêu năng lực của VRF.** Hai khách hàng đều dùng `10.10.10.0/24` — không sao |
| ⭐ **Interface thuộc về đúng MỘT VRF** | Gán interface vào VRF thì nó **rời khỏi** global table |
| ⭐ **Routing protocol chạy riêng** | OSPF/EIGRP/BGP đều có phiên bản "per-VRF" |
| ⭐ **Mặc định KHÔNG nói chuyện được với nhau** | ⭐ Muốn thông nhau phải **cố ý** làm route leaking |
| ⭐ **Là ảo hóa tầng CONTROL PLANE** | ⭐ Nó chia **bảng định tuyến**, không chia CPU/RAM |

#### ⭐ VRF-lite vs VRF (MPLS L3VPN)

| | ⭐ **VRF-lite** | **VRF trong MPLS L3VPN** |
|---|---|---|
| Cần MPLS? | ❌ **Không** | ✅ Có |
| Cần MP-BGP? | ❌ Không | ✅ Có |
| ⭐ **Route Distinguisher (RD)** | Cấu hình cho đủ, ⭐ **không thực sự dùng để làm gì** | ⭐ **Bắt buộc** — làm route unique giữa các khách hàng |
| ⭐ **Route Target (RT)** | ⭐ **Không dùng** | ⭐ **Bắt buộc** — điều khiển import/export route |
| Truyền VRF qua nhiều router | ⭐ Phải **trunk/subinterface từng chặng** (*"VRF-lite hop-by-hop"*) | ⭐ MPLS lo hết |
| ⭐ Cái ENCOR hỏi | ⭐⭐ **CHÍNH LÀ CÁI NÀY** | Chỉ cần biết tên |

> ⭐ **Nhớ:** ⭐ **ENCOR = VRF-lite.** Không cần học MPLS. ⭐ **RD chỉ cần gõ cho đúng cú pháp.**

### 3.2 ⭐⭐ Cấu hình VRF — hai cú pháp, đừng lẫn

```
! ═══════ CÚ PHÁP CŨ (legacy, chỉ IPv4) ═══════
ip vrf KHACH-A
 rd 65001:1
!
interface GigabitEthernet0/1
 ip vrf forwarding KHACH-A          ! chú ý có chữ "ip" ở đầu
 ip address 10.10.10.1 255.255.255.0

! ═══════ CÚ PHÁP MỚI (multiprotocol — IPv4 + IPv6) ═══════
vrf definition KHACH-A
 rd 65001:1
 !
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 exit-address-family
!
interface GigabitEthernet0/1
 vrf forwarding KHACH-A             ! KHÔNG có chữ "ip" ở đầu
 ip address 10.10.10.1 255.255.255.0
```

> 🔴 ⭐⭐ **BẪY SỐ 1 CỦA VRF — nhớ kỹ, đề ra và đời cũng gặp:**
> ⭐ **Gán interface vào VRF sẽ XÓA SẠCH địa chỉ IP đang có trên interface đó!**
>
> ```
> R1(config-if)# vrf forwarding KHACH-A
> % Interface GigabitEthernet0/1 IPv4 disabled and address(es) removed due to
>   enabling VRF KHACH-A
> ```
> ⭐ **Luôn gán VRF TRƯỚC, đặt IP SAU.** 🔴 ⭐ Làm ngược trên thiết bị production đang chạy =
> **mất kết nối tới chính con router đó** nếu bạn đang SSH qua interface ấy.

⭐ **Chuyển cú pháp cũ sang mới:** `vrf upgrade-cli multi-af-mode common-policies vrf <tên>`

### 3.3 ⭐⭐ Định tuyến bên trong VRF — mọi lệnh đều phải "khai báo VRF"

```
! ═══ Static route trong VRF ═══
ip route vrf KHACH-A 0.0.0.0 0.0.0.0 10.10.10.254
ip route vrf KHACH-A 192.168.50.0 255.255.255.0 10.10.10.254

! ═══ OSPF trong VRF — process RIÊNG cho mỗi VRF ═══
router ospf 10 vrf KHACH-A                  ! chú ý từ khóa "vrf"
 router-id 1.1.1.1
 network 10.10.10.0 0.0.0.255 area 0
!
router ospf 20 vrf KHACH-B                  ! process khác, VRF khác
 router-id 1.1.1.2
 network 10.10.10.0 0.0.0.255 area 0        ! CÙNG mạng — không xung đột!

! ═══ EIGRP trong VRF (named mode) ═══
router eigrp CTY
 address-family ipv4 unicast vrf KHACH-A autonomous-system 100
  network 10.10.10.0 0.0.0.255
 exit-address-family

! ═══ BGP trong VRF ═══
router bgp 65001
 address-family ipv4 vrf KHACH-A
  neighbor 10.10.10.254 remote-as 65100
  neighbor 10.10.10.254 activate
 exit-address-family
```

### 3.4 ⭐⭐ Verify VRF — mọi lệnh show/ping/traceroute cũng phải khai VRF

```
show vrf                                    ! liệt kê VRF + interface thuộc về nó
show vrf detail                             ! chi tiết RD, address-family
show ip route vrf KHACH-A                   ! bảng route CỦA RIÊNG VRF đó
show ip route                               ! bảng GLOBAL — sẽ KHÔNG thấy route của VRF
show ip interface brief vrf KHACH-A
show ip protocols vrf KHACH-A
show ip arp vrf KHACH-A
show ip cef vrf KHACH-A

! PING & TRACEROUTE — BẮT BUỘC khai vrf, nếu không nó dùng bảng GLOBAL
ping vrf KHACH-A 10.10.10.100
traceroute vrf KHACH-A 10.10.10.100
telnet 10.10.10.100 /vrf KHACH-A
ssh -vrf KHACH-A -l admin 10.10.10.100
copy running-config tftp://10.10.10.5/cfg vrf KHACH-A
```

> 🔴 ⭐⭐ **BẪY SỐ 2 CỦA VRF — thủ phạm của 90% ca "VRF không hoạt động":**
> ⭐ **Quên gõ `vrf <tên>` trong lệnh ping/show.**
>
> ```
> R1# ping 10.10.10.100
> .....                                ! 🔴 THẤT BẠI — vì đang ping từ bảng GLOBAL
> Success rate is 0 percent (0/5)
>
> R1# ping vrf KHACH-A 10.10.10.100
> !!!!!                                ! ✅ THÀNH CÔNG
> Success rate is 100 percent (5/5)
> ```
> ⭐ **VRF không hỏng. Lệnh của bạn hỏng.** ⭐ Đây là điều đầu tiên phải kiểm tra khi troubleshoot VRF.

### 3.5 ⭐ Route leaking — khi cần cho 2 VRF nói chuyện

⭐ Mặc định các VRF **hoàn toàn cách ly**. Muốn thông nhau (VD: mọi khách hàng cùng dùng chung một
DNS server / Internet gateway), có 3 cách:

| Cách | Lệnh | Ghi chú |
|---|---|---|
| ⭐ **Static route leaking** | `ip route vrf A 8.8.8.8 255.255.255.255 <next-hop> global`<br>`ip route 10.10.10.0 255.255.255.0 <intf> vrf A` | ⭐ **Đơn giản nhất cho VRF-lite.** Từ khóa ⭐ **`global`** = trỏ sang bảng global |
| ⭐ **MP-BGP với Route Target** | `import ipv4 unicast map …` / RT import-export | ⭐ Chuẩn mực, mở rộng tốt — nhưng cần MP-BGP |
| **Nối cáp vật lý** | Cắm 2 port của cùng router vào nhau, mỗi port một VRF | ⭐ "Thô nhưng chạy". Tốn port. Từng rất phổ biến |

> ⭐ **Cho ENCOR:** ⭐ **biết rằng route leaking cần cấu hình CỐ Ý** là đủ.
> ⭐ Nhớ từ khóa **`global`** trong static route — đề có thể hỏi dòng đó nghĩa gì.

### 3.6 ⭐ VRF dùng để làm gì ngoài đời

| Tình huống | Vì sao dùng VRF |
|---|---|
| ⭐ **Tách khách hàng / phòng ban** | Mỗi bên một bảng route, IP trùng cũng được |
| ⭐⭐ **Tách mạng quản lý (Management VRF)** | ⭐ **Rất phổ biến.** `Mgmt-vrf` trên switch Cisco — quản lý thiết bị không lẫn với traffic dữ liệu. ⭐ Đây cũng là lý do trên nhiều switch bạn phải gõ `ping vrf Mgmt-vrf` |
| ⭐ **Cách ly mạng camera / IoT / máy POS** | Tách hẳn khỏi mạng văn phòng ở tầng route, mạnh hơn ACL |
| ⭐ **Mạng khách (guest)** | Đưa khách vào VRF riêng, chỉ leak ra Internet |
| ⭐ **Nền tảng của SD-Access** | ⭐⭐ **VN (Virtual Network) trong SD-Access chính là VRF** — Module-09 |
| ⭐ **Chống sự cố lan** | Lỗi routing ở VRF này không ảnh hưởng VRF kia |

---

## 📘 4. ⭐⭐ GRE (blueprint 2.2.b — CONFIGURE AND VERIFY)

### 4.1 GRE là gì và giải quyết vấn đề gì

> ⭐⭐ **GRE (Generic Routing Encapsulation)** — RFC 2784. ⭐ Bọc gói của bạn vào **một gói IP mới**
> để nó **đi qua một mạng không hiểu nó** (thường là Internet).

```
   TRƯỚC KHI BỌC:      [ IP gốc: 10.1.1.5 → 10.2.2.5 ][ dữ liệu ]

   SAU KHI BỌC GRE:
   [ IP mới: 203.0.113.1 → 203.0.113.2 ][ GRE 4B ][ IP gốc ][ dữ liệu ]
     └─ 20 byte ─┘                        └ 4B ┘
     TỔNG OVERHEAD = 24 BYTE
```

| ⭐ Đặc điểm của GRE | Chi tiết |
|---|---|
| ⭐⭐ **Overhead** | ⭐ **24 byte** (20 IP mới + 4 GRE) → ⭐ **tunnel IP MTU mặc định = 1476** |
| 🔴 ⭐⭐ **KHÔNG mã hóa** | ⭐ **GRE hoàn toàn TRONG SUỐT.** Ai bắt gói đọc được hết. ⭐ **Đây là lý do phải ghép với IPsec** |
| ⭐⭐ **Chở được multicast & broadcast** | ⭐⭐ **Đây là lý do GRE tồn tại!** ⭐ IPsec thuần **không** chở được → ⭐ **không chạy được OSPF/EIGRP qua IPsec thuần** |
| ⭐ **Chở được nhiều protocol** | IPv4, IPv6, thậm chí IPX (chữ *Generic*) |
| ⭐ **Là point-to-point** | Một tunnel nối đúng 2 đầu. *(mGRE — multipoint — dùng trong DMVPN)* |
| ⭐ **Stateless** | Không kiểm tra đầu kia còn sống, ⭐ **trừ khi bật `keepalive`** |

> 🔴 ⭐⭐ **Câu chốt phải thuộc:**
> ⭐ **GRE chở được routing protocol nhưng KHÔNG mã hóa.**
> ⭐ **IPsec mã hóa nhưng KHÔNG chở được multicast.**
> ⭐⭐ **→ Ghép cả hai: GRE over IPsec.** ⭐ **Đây là ý chính của cả mục 2.2.b.**

### 4.2 ⭐⭐ Cấu hình GRE

```
! ═══════════ TRÊN R1 (site A) ═══════════
interface Tunnel0
 description GRE toi Site-B
 ip address 172.16.0.1 255.255.255.252     ! mạng RIÊNG của tunnel (không phải mạng LAN)
 tunnel source GigabitEthernet0/0          ! interface (hoặc IP) phía WAN của MÌNH
 tunnel destination 203.0.113.2            ! IP PUBLIC của đầu kia
 tunnel mode gre ip                        ! mặc định — không gõ cũng được
 keepalive 10 3                            ! nên bật: gửi mỗi 10s, mất 3 lần thì down
!
! ═══════════ TRÊN R2 (site B) ═══════════
interface Tunnel0
 ip address 172.16.0.2 255.255.255.252     ! cùng subnet /30 với đầu kia
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.1            ! ĐẢO NGƯỢC lại
 keepalive 10 3
```

⭐ **Bốn thứ phải khớp giữa hai đầu:**

| # | Yêu cầu |
|:---:|---|
| 1 | ⭐ **`tunnel source` của A = `tunnel destination` của B** (và ngược lại) |
| 2 | ⭐ Hai địa chỉ tunnel **cùng subnet** (thường /30 hoặc /31) |
| 3 | ⭐ ⭐ **Hai đầu phải ping được nhau bằng IP WAN THẬT** trước khi tunnel lên |
| 4 | ⭐ Cùng `tunnel mode` |

### 4.3 🔴 ⭐⭐ BẪY LỚN NHẤT CỦA GRE — Recursive Routing

```
   KỊCH BẢN GÂY LỖI:

   ① Tunnel0 lên, R1 chạy OSPF QUA tunnel với R2
   ② Ai đó advertise luôn mạng WAN (203.0.113.0/24) vào OSPF đang chạy qua tunnel
   ③ R1 học được route tới 203.0.113.2  ...  QUA CHÍNH TUNNEL0
   ④ Nhưng để gửi gói qua Tunnel0, R1 phải biết đường tới 203.0.113.2
   ⑤ VÒNG LẶP: "muốn đi tới đích, phải đi qua tunnel; muốn qua tunnel, phải biết đường tới đích"
   ⑥ Router phát hiện và TỰ TẮT tunnel:

   %TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing
```

⭐ **Triệu chứng đặc trưng:** ⭐ **tunnel lên rồi xuống, lên rồi xuống, lặp mãi (flapping).**

| ✅ Ba cách sửa | Chi tiết |
|---|---|
| ⭐⭐ **Đừng advertise mạng WAN vào giao thức chạy qua tunnel** | ⭐ **Cách đúng nhất.** Chỉ advertise **mạng LAN** vào OSPF-qua-tunnel |
| ⭐ **Static route tới tunnel destination** | `ip route 203.0.113.2 255.255.255.255 <next-hop-ISP>` → AD 1, luôn thắng OSPF (AD 110) |
| ⭐ **Tách miền định tuyến** | Underlay dùng static/default route ra ISP · overlay (qua tunnel) dùng OSPF |

> ⭐⭐ **Nguyên tắc vàng để không bao giờ dính lỗi này:**
> 🔴 ⭐ ***"Đường tới tunnel destination TUYỆT ĐỐI không được đi qua tunnel."***
> ⭐ Nói cách khác: ⭐ **underlay và overlay phải là hai miền định tuyến TÁCH BIỆT.**

### 4.4 ⭐⭐ Vấn đề MTU & MSS — bẫy lớn thứ hai

```
   MTU vật lý 1500
   − 24 byte GRE            → tunnel IP MTU = 1476
   − 52 byte nữa nếu có IPsec → ~1400 là con số an toàn thực tế
```

| 🔴 Triệu chứng kinh điển | Giải thích |
|---|---|
| ⭐⭐ **Ping OK, SSH OK, nhưng web/HTTPS/file-transfer bị TREO GIỮA CHỪNG** | ⭐ Gói nhỏ qua được, ⭐ **gói lớn bị drop** vì vượt MTU và bị đặt cờ DF |
| ⭐ "Trang web load một nửa rồi đứng" | ⭐ **Dấu hiệu nhận dạng MTU số 1** |

```
! CÁCH SỬA CHUẨN — gõ CẢ HAI DÒNG, TRÊN CẢ HAI ĐẦU:
interface Tunnel0
 ip mtu 1400                    ! giới hạn kích thước gói IP qua tunnel
 ip tcp adjust-mss 1360         ! DÒNG QUAN TRỌNG NHẤT
```

| Lệnh | Làm gì |
|---|---|
| ⭐ `ip mtu 1400` | Router **tự phân mảnh** gói IP lớn hơn 1400 trước khi bọc |
| ⭐⭐ `ip tcp adjust-mss 1360` | ⭐⭐ Router **sửa trường MSS trong gói TCP SYN đi qua** → ⭐ **bảo hai đầu tự gửi gói nhỏ ngay từ đầu** → **không cần phân mảnh chút nào** |

> ⭐ **Vì sao 1360?** `1400 (ip mtu) − 20 (IP header) − 20 (TCP header) = 1360`.
> ⭐ **Vì sao `adjust-mss` quan trọng hơn `ip mtu`?** Vì phân mảnh **rất tốn CPU** và nhiều firewall
> **chặn thẳng gói phân mảnh**. ⭐ `adjust-mss` giải quyết vấn đề **từ gốc** — nó ngăn gói lớn được tạo ra.
>
> 🔴 ⭐ **`adjust-mss` chỉ tác dụng với TCP.** UDP lớn (VD một số VPN, video) vẫn cần `ip mtu`.

### 4.5 ⭐ Verify GRE

```
show interface tunnel0                     ! up/up? MTU bao nhiêu? có drop không?
show ip interface brief | include Tunnel
show ip route                              ! có route nào trỏ qua Tunnel0 không
ping 172.16.0.2                            ! ping đầu kia của tunnel
ping 172.16.0.2 df-bit size 1400           ! test MTU thật của tunnel
debug tunnel                               ! ⚠️ chỉ dùng trong lab
```

⭐ **Đọc `show interface tunnel0` — 4 dòng cần nhìn:**
```
Tunnel0 is up, line protocol is up          "up/up" = OK (nhưng chưa chắc thông!)
  Internet address is 172.16.0.1/30
  MTU 17916 bytes, BW 100 Kbit/sec          MTU của interface tunnel
  Tunnel source 203.0.113.1 (GigabitEthernet0/0), destination 203.0.113.2
  Tunnel protocol/transport GRE/IP
  Tunnel transport MTU 1476 bytes         ← 1500 − 24. ĐÂY mới là con số quan trọng
  Keepalive set (10 sec), retries 3
```

> 🔴 ⭐⭐ **Bẫy "up/up giả":** ⭐ **nếu KHÔNG bật `keepalive`, interface Tunnel sẽ hiện `up/up`
> ngay cả khi đầu kia đã CHẾT HẲN** — vì GRE là stateless, router chỉ cần biết
> "tunnel source hợp lệ và có route tới destination" là báo up.
> ⭐ **Luôn bật `keepalive`** để tunnel phản ánh đúng thực tế.

---

## 📘 5. ⭐⭐ IPsec (blueprint 2.2.b — CONFIGURE AND VERIFY)

### 5.1 ⭐ Ba việc IPsec làm

| Việc | Nghĩa | Thuật toán |
|---|---|---|
| ⭐ **Confidentiality** (bí mật) | Mã hóa — người khác không đọc được | AES, 3DES *(DES/3DES đã lỗi thời)* |
| ⭐ **Integrity** (toàn vẹn) | Không bị sửa trên đường | SHA-1, ⭐ **SHA-256/384** *(MD5 lỗi thời)* |
| ⭐ **Authentication** (xác thực) | Đúng là đối tác chứ không phải kẻ giả mạo | ⭐ **Pre-shared key** hoặc **chứng thư RSA** |
| *(kèm theo)* **Anti-replay** | Chống phát lại gói cũ | Số thứ tự |

### 5.2 ⭐⭐ ESP vs AH · Tunnel mode vs Transport mode

| | ⭐⭐ **ESP** (Encapsulating Security Payload) | **AH** (Authentication Header) |
|---|---|---|
| **IP protocol** | ⭐ **50** | 51 |
| ⭐ **Mã hóa?** | ✅ **CÓ** | 🔴 ⭐ **KHÔNG** — chỉ xác thực |
| Toàn vẹn? | ✅ | ✅ |
| ⭐ Qua NAT được? | ⭐ Có (với **NAT-T**) | 🔴 ⭐ **KHÔNG** — AH ký cả IP header, NAT sửa header là hỏng |
| ⭐ Dùng cái nào | ⭐⭐ **Gần như luôn dùng ESP** | ⭐ Hầu như không dùng |

| | ⭐⭐ **Tunnel mode** | ⭐ **Transport mode** |
|---|---|---|
| Làm gì với IP header gốc | ⭐ **Bọc thêm IP header MỚI** | ⭐ **Giữ nguyên IP header gốc** |
| Overhead | Lớn hơn | Nhỏ hơn |
| ⭐ Dùng khi | ⭐⭐ **Site-to-site VPN thuần IPsec** (crypto map) | ⭐⭐ **GRE over IPsec** — vì GRE **đã** thêm IP header rồi, không cần thêm nữa |

> ⭐⭐ **Nhớ cặp này:** ⭐ **IPsec thuần → tunnel mode.** ⭐ **GRE over IPsec → transport mode.**
> *(Tunnel mode vẫn chạy được với GRE, chỉ là tốn thêm 20 byte vô ích.)*

### 5.3 ⭐⭐ Hai phase của IKE

```
   PHASE 1 (IKE SA / ISAKMP SA)  ── UDP 500 ──  "Xây một đường hầm AN TOÀN để ĐÀM PHÁN"
      · Xác thực lẫn nhau (PSK hoặc chứng thư)
      · Trao đổi khóa Diffie-Hellman
      · Kết quả: một kênh mã hóa để nói chuyện tiếp
      · Chế độ: Main mode (6 gói, an toàn hơn) / Aggressive mode (3 gói, nhanh hơn)
                          ↓
   PHASE 2 (IPsec SA)             ── Quick mode ──  "Thỏa thuận đường hầm CHỞ DỮ LIỆU"
      · Chốt transform-set (mã hóa + hash)
      · Chốt "traffic nào được đi qua" (interesting traffic / proxy ID)
      · Kết quả: 2 SA MỘT CHIỀU (một vào, một ra) → dữ liệu bắt đầu chảy
```

⭐⭐ **NĂM THAM SỐ CỦA PHASE 1 PHẢI KHỚP TUYỆT ĐỐI GIỮA HAI ĐẦU:**

| # | Tham số | Ví dụ |
|:---:|---|---|
| 1 | ⭐ **Encryption** | `aes 256` |
| 2 | ⭐ **Hash** | `sha256` |
| 3 | ⭐ **Authentication** | `pre-share` |
| 4 | ⭐ **DH group** | `group 14` |
| 5 | ⭐ **Lifetime** | `86400` *(thực tế bên nào ngắn hơn sẽ được dùng)* |

⭐ **Mẹo nhớ 5 tham số: "HAGLE"** = **H**ash · **A**uthentication · **G**roup (DH) · **L**ifetime · **E**ncryption.

| | ⭐ **IKEv1** | ⭐ **IKEv2** |
|---|---|---|
| Số gói bắt tay | Nhiều (Main mode 6 gói) | ⭐ **Ít hơn** (4 gói) |
| Cấu hình | Phức tạp hơn | ⭐ Gọn hơn |
| ⭐ Xác thực bất đối xứng | ❌ | ⭐ ✅ (mỗi bên dùng cách khác nhau) |
| Chống DoS, NAT-T, EAP | Hạn chế | ⭐ Tốt hơn |
| ⭐ Nên dùng | — | ⭐ **IKEv2 nếu thiết bị hỗ trợ** |

⭐ **NAT-T (NAT Traversal):** khi có NAT giữa hai đầu, IPsec **tự bọc ESP vào UDP 4500** để đi qua NAT.
⭐ **Nhớ 2 port: UDP 500 (IKE) và UDP 4500 (NAT-T).**

### 5.4 ⭐ Cấu hình IPsec — CÁCH CŨ (crypto map, IPsec thuần)

```
! ═══ ① PHASE 1 — ISAKMP policy ═══
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 86400
!
crypto isakmp key MatKhauChungRatDai address 203.0.113.2

! ═══ ② PHASE 2 — transform-set ═══
crypto ipsec transform-set TSET esp-aes 256 esp-sha256-hmac
 mode tunnel                                  ! IPsec thuần → TUNNEL mode
!
! ═══ ③ INTERESTING TRAFFIC — traffic nào được mã hóa ═══
ip access-list extended VPN-TRAFFIC
 permit ip 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255
!
! ═══ ④ Ghép lại thành crypto map ═══
crypto map CMAP 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set TSET
 match address VPN-TRAFFIC
!
! ═══ ⑤ ÁP LÊN INTERFACE WAN — hay quên nhất ═══
interface GigabitEthernet0/0
 crypto map CMAP
```

> 🔴 ⭐⭐ **ACL "interesting traffic" PHẢI ĐỐI XỨNG GƯƠNG giữa hai đầu:**
> · R1: `permit ip 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255`
> · ⭐ R2: `permit ip 10.2.0.0 0.0.255.255 10.1.0.0 0.0.255.255` ← ⭐ **đảo ngược source/dest**
> 🔴 ⭐ **Không đối xứng → Phase 2 thất bại** với lỗi *proxy identity mismatch*.

🔴 ⭐ **Nhược điểm lớn của crypto map:** ⭐ **không chở được multicast → không chạy được OSPF/EIGRP qua nó.**
⭐ **Đó chính là lý do có §6.**

### 5.5 ⭐ Vài lệnh cấu hình phụ hay gặp

```
! Loại trừ traffic VPN khỏi NAT (CỰC KỲ hay quên — Module-06B!)
ip access-list extended NAT-ACL
 deny   ip 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255    ! DENY traffic VPN TRƯỚC
 permit ip 10.1.0.0 0.0.255.255 any                     ! rồi mới NAT phần còn lại
!
ip nat inside source list NAT-ACL interface Gi0/0 overload

! Bật/tắt NAT-T (thường mặc định đã bật)
crypto isakmp nat-traversal 20

! Dead Peer Detection — phát hiện đầu kia chết
crypto isakmp keepalive 10 3 periodic
```

> 🔴 ⭐⭐ **Lỗi phối hợp NAT–VPN kinh điển:** VPN "lên" (`show crypto isakmp sa` = `QM_IDLE`) nhưng
> ⭐ **không ping được qua**. Nguyên nhân: ⭐ **traffic đi VPN bị NAT trước** → source IP đổi thành IP public →
> **không còn khớp ACL interesting traffic** → không được mã hóa → rơi ra Internet.
> ⭐ **Sửa: `deny` traffic VPN trong NAT ACL, đặt TRƯỚC dòng `permit`.**
> ⭐ *(Liên hệ Module-06B §2.2 — thứ tự NAT và routing.)*

---

## 📘 6. ⭐⭐ GRE OVER IPsec — trọng tâm thực chiến của mục 2.2.b

### 6.1 Vì sao phải ghép

| | GRE thuần | IPsec thuần (crypto map) | ⭐⭐ **GRE over IPsec** |
|---|:---:|:---:|:---:|
| ⭐ Mã hóa | 🔴 ❌ | ✅ | ⭐ ✅ |
| ⭐⭐ Chở multicast → **chạy OSPF/EIGRP** | ✅ | 🔴 ❌ | ⭐⭐ ✅ |
| Chở non-IP | ✅ | ❌ | ✅ |
| Cấu hình định tuyến động | ✅ | 🔴 Phải khai từng subnet trong ACL | ⭐ ✅ |
| ⭐ **Kết luận** | Thiếu bảo mật | Thiếu định tuyến động | ⭐⭐ **Đủ cả hai** |

> ⭐⭐ **Một câu tóm tắt cả mục 2.2.b:**
> ⭐ **"GRE cho routing đi qua, IPsec cho nó đi qua an toàn."**

### 6.2 ⭐⭐ Cấu hình GRE over IPsec — CÁCH HIỆN ĐẠI (IPsec profile)

> ⭐ **Đây là cách nên học và nên dùng.** Gọn hơn crypto map rất nhiều, và ⭐ **không cần ACL interesting traffic**
> (vì "traffic đáng quan tâm" chính là **toàn bộ những gì đi qua tunnel").

```
!═══════════════════ TRÊN R1 ═══════════════════

! ─── ① Phase 1 ───
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
!
crypto isakmp key MatKhauChungRatDai address 203.0.113.2

! ─── ② Phase 2: transform-set + TRANSPORT MODE ───
crypto ipsec transform-set TSET esp-aes 256 esp-sha256-hmac
 mode transport                              ! GRE over IPsec → TRANSPORT
!
! ─── ③ IPsec PROFILE (thay cho crypto map) ───
crypto ipsec profile IPSEC-PROF
 set transform-set TSET

! ─── ④ Gắn profile vào TUNNEL, không gắn vào interface vật lý ───
interface Tunnel0
 ip address 172.16.0.1 255.255.255.252
 ip mtu 1400                                 ! nhớ MTU
 ip tcp adjust-mss 1360                      ! nhớ MSS
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel mode gre ip
 tunnel protection ipsec profile IPSEC-PROF  ! DÒNG THẦN KỲ
 keepalive 10 3

! ─── ⑤ OSPF chạy QUA tunnel (chỉ advertise LAN, KHÔNG advertise WAN) ───
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0           ! mạng tunnel
 network 10.1.0.0 0.0.255.255 area 0         ! LAN site A
 ! TUYỆT ĐỐI KHÔNG advertise 203.0.113.0/24 vào đây (recursive routing! §4.3)

! ─── ⑥ Route tới đầu kia bằng underlay (static/default ra ISP) ───
ip route 0.0.0.0 0.0.0.0 203.0.113.254
```

⭐ **Trên R2 làm y hệt, chỉ đảo:** `ip address 172.16.0.2` · `tunnel destination 203.0.113.1` ·
`crypto isakmp key … address 203.0.113.1` · `network 10.2.0.0 …`

> ⭐⭐ **Ba lợi ích của `tunnel protection ipsec profile` so với crypto map:**
> 1. ⭐ **Không cần ACL interesting traffic** — mọi thứ qua tunnel đều được bảo vệ
> 2. ⭐ **Không cần gắn gì lên interface vật lý**
> 3. ⭐ **Định tuyến động chạy tự nhiên** — chỉ cần thêm mạng vào OSPF

### 6.3 ⭐⭐ Verify GRE over IPsec — theo đúng thứ tự này

```
! ─── BƯỚC 1: Underlay có thông không? ───
ping 203.0.113.2                        ! Không thông → dừng lại, sửa routing/ISP trước

! ─── BƯỚC 2: PHASE 1 lên chưa? ───
show crypto isakmp sa
   dst           src           state     conn-id status
   203.0.113.2   203.0.113.1   QM_IDLE   1001  ACTIVE
   "QM_IDLE" = Phase 1 ĐÃ XONG và đang chờ. ĐÂY LÀ TRẠNG THÁI TỐT.
   "MM_NO_STATE" / "MM_KEY_EXCH" = Phase 1 ĐANG HỎNG → sai PSK hoặc lệch policy

! ─── BƯỚC 3: PHASE 2 lên chưa, và CÓ ĐANG CHẢY DỮ LIỆU không? ───
show crypto ipsec sa
   local  ident (addr/mask/prot/port): (203.0.113.1/255.255.255.255/47/0)
                                                                    47 = GRE
   #pkts encaps: 152, #pkts encrypt: 152      ← PHẢI TĂNG khi bạn ping
   #pkts decaps: 149, #pkts decrypt: 149      ← PHẢI TĂNG
   #send errors 0, #recv errors 0

! ─── BƯỚC 4: Tóm tắt nhanh ───
show crypto session
show crypto session detail
   Session status: UP-ACTIVE
   IKEv1 SA: ... Active
   IPSEC FLOW: permit 47 host 203.0.113.1 host 203.0.113.2
     Active SAs: 2, origin: crypto map / tunnel protection

! ─── BƯỚC 5: Tunnel & routing ───
show interface tunnel0
show ip ospf neighbor                   ! neighbor qua tunnel phải FULL
show ip route ospf                      ! có học được LAN của site kia không
ping 10.2.1.1 source 10.1.1.1           ! ping từ LAN sang LAN — bài test cuối cùng
```

> 🔴 ⭐⭐ **Bảng chẩn đoán nhanh — thuộc bảng này là troubleshoot được IPsec:**
>
> | Quan sát | ⭐ Kết luận |
> |---|---|
> | ⭐ `show crypto isakmp sa` **trống rỗng** | ⭐ Phase 1 **chưa bắt đầu** — chưa có traffic kích hoạt, hoặc không tới được peer |
> | 🔴 ⭐ State = **`MM_NO_STATE`** | ⭐ **Phase 1 hỏng** → sai **pre-shared key** hoặc **lệch ISAKMP policy** |
> | ✅ ⭐ State = **`QM_IDLE`** | ⭐ **Phase 1 OK** |
> | ⭐ Phase 1 OK nhưng `show crypto ipsec sa` không có SA | ⭐ **Phase 2 hỏng** → lệch **transform-set** hoặc **ACL không đối xứng** |
> | 🔴 ⭐⭐ **`encaps` tăng nhưng `decaps` = 0** | ⭐⭐ **Mình gửi được, đối phương không trả lời** → ⭐ **firewall chặn chiều về**, hoặc đầu kia sai cấu hình, hoặc **route ngược thiếu** |
> | 🔴 ⭐ **`decaps` tăng nhưng `encaps` = 0** | ⭐ Ngược lại — mình nhận được mà không gửi → ⭐ **traffic của mình không khớp ACL / không vào tunnel** |
> | ⭐ Cả hai đều tăng nhưng ping vẫn fail | ⭐ **Không còn là vấn đề VPN** → routing, ACL sau tunnel, hoặc firewall của host đích |

### 6.4 ⭐ Biết tên: DMVPN & các anh em

| Công nghệ | Ý tưởng | ENCOR hỏi? |
|---|---|---|
| ⭐ **DMVPN** | ⭐ **mGRE + NHRP + IPsec** — hub-and-spoke tự động, ⭐ **spoke tự dựng tunnel tạm với nhau** khi cần | ⭐ **Biết tên + ý tưởng là đủ** *(học sâu ở ENARSI/ENSDWI)* |
| **GETVPN** | Mã hóa mà **giữ nguyên IP header** — dùng trên mạng riêng MPLS | Biết tên |
| **FlexVPN** | Khung IKEv2 thống nhất của Cisco | Biết tên |
| ⭐ **SD-WAN (Viptela)** | ⭐ Overlay tự động + chính sách tập trung → ⭐ **Module-09** | ⭐ Có — ở mức khái niệm |

⭐ **Ba thành phần của DMVPN cần nhớ:** ⭐ **mGRE** (một interface tunnel nối **nhiều** peer) ·
⭐ **NHRP** (bảng ánh xạ "IP tunnel ↔ IP public", hub làm *NHS*) · ⭐ **IPsec** (bảo vệ).

---

## 📘 7. 🟡 LISP (blueprint 2.3.a — DESCRIBE)

### 7.1 ⭐ Vấn đề LISP giải quyết

> 🔴 ⭐⭐ **Ý tưởng cốt lõi — nếu chỉ nhớ một câu về LISP thì nhớ câu này:**
> ⭐⭐ **Địa chỉ IP hiện nay đang gánh HAI vai cùng lúc: "ANH LÀ AI" và "ANH Ở ĐÂU".**
> ⭐ **LISP tách hai vai đó ra.**

| | Nghĩa | LISP gọi là |
|---|---|---|
| ⭐ **"Anh là AI"** | Danh tính của host — không đổi dù đi đâu | ⭐⭐ **EID** (Endpoint Identifier) |
| ⭐ **"Anh Ở ĐÂU"** | Vị trí trong mạng — router nào đang phục vụ | ⭐⭐ **RLOC** (Routing Locator) |

⭐ **Vì sao cần tách:** khi một máy chuyển chỗ (VM migration, người dùng đi lại), ⭐ **IP phải đổi**
→ đứt session. ⭐ **Hoặc** phải nhồi thêm route /32 vào bảng định tuyến toàn cầu → ⭐ **bảng route phình vô hạn**.

### 7.2 ⭐⭐ Các thành phần LISP — bảng phải học thuộc

| Thành phần | Tên đầy đủ | ⭐ Làm gì |
|---|---|---|
| ⭐⭐ **ITR** | Ingress Tunnel Router | ⭐ **Router LỐI VÀO — nhận gói từ host, tra cứu, BỌC (encapsulate)** |
| ⭐⭐ **ETR** | Egress Tunnel Router | ⭐ **Router LỐI RA — MỞ GÓI (decapsulate), giao cho host. Và ĐĂNG KÝ EID của mình với MS** |
| ⭐ **xTR** | — | ⭐ Một router làm **cả ITR lẫn ETR** (thực tế hầu hết là xTR) |
| ⭐⭐ **MS** | Map Server | ⭐ **NHẬN ĐĂNG KÝ** từ các ETR — "tôi phụ trách các EID này" |
| ⭐⭐ **MR** | Map Resolver | ⭐ **NHẬN CÂU HỎI** từ ITR — "EID này ở RLOC nào?" |
| ⭐ **MS/MR** | — | ⭐ Thường **chạy chung trên một thiết bị** |
| **PITR / PETR** | Proxy ITR / ETR | ⭐ Cầu nối giữa **thế giới LISP** và **thế giới không-LISP** (Internet thường) |
| **ALT** | Alternative Logical Topology | Cơ chế phân tán map cũ — ⭐ chỉ cần biết tên |
| ⭐ **Map-Cache** | — | ⭐ Bộ nhớ đệm trên ITR, lưu các ánh xạ EID→RLOC đã tra được |

⭐ **Mẹo nhớ:** ⭐ **I**ngress = **I**n (vào, bọc lại) · ⭐ **E**gress = **E**xit (ra, mở ra).
⭐ **Map SERVER = nơi ĐĂNG KÝ** (register) · ⭐ **Map RESOLVER = nơi HỎI** (resolve).

### 7.3 ⭐⭐ Luồng hoạt động

```
   Host A (EID 10.1.1.10)                          Host B (EID 10.2.2.20)
        │                                                    │
      [ ITR ]                                            [ ETR ]
     RLOC 1.1.1.1                                      RLOC 2.2.2.2
        │                                                    │
        │  ⓪ ETR ĐĂNG KÝ TRƯỚC: "10.2.2.0/24 → RLOC 2.2.2.2"  ──►[ MS ]
        │
        │  ① Host A gửi gói tới 10.2.2.20 → tới ITR
        │  ② ITR xem Map-Cache: chưa có
        │  ③ ITR gửi MAP-REQUEST tới [ MR ] ──► MR chuyển tới MS ──► MS chuyển tới ETR
        │  ④ ETR trả MAP-REPLY thẳng về ITR: "10.2.2.0/24 ở RLOC 2.2.2.2"
        │  ⑤ ITR LƯU VÀO MAP-CACHE (lần sau khỏi hỏi)
        │  ⑥ ITR BỌC gói:  [IP: 1.1.1.1→2.2.2.2][UDP 4341][IP gốc: 10.1.1.10→10.2.2.20]
        │  ⑦ Gói đi qua mạng underlay bình thường
        │  ⑧ ETR MỞ GÓI, giao cho Host B
        ▼
```

| ⭐ Port | Dùng cho |
|---|---|
| ⭐⭐ **UDP 4341** | ⭐ **Data plane** — gói dữ liệu đã bọc LISP |
| ⭐⭐ **UDP 4342** | ⭐ **Control plane** — Map-Request, Map-Reply, Map-Register |

> ⭐⭐ **Đặc điểm quyết định của LISP — đề rất hay hỏi:**
> ⭐ **LISP là mô hình "PULL" (kéo về khi cần), không phải "PUSH".**
>
> | | ⭐ **BGP / IGP truyền thống** | ⭐⭐ **LISP** |
> |---|---|---|
> | Mô hình | ⭐ **PUSH** — đẩy **TẤT CẢ** route cho mọi router | ⭐ **PULL** — chỉ **hỏi khi cần** |
> | Bảng route | ⭐ Ai cũng phải giữ **toàn bộ** | ⭐ Chỉ giữ **map-cache** những gì đang dùng |
> | Analogy | ⭐ **Cuốn danh bạ điện thoại** — ai cũng cầm một cuốn dày | ⭐⭐ **DNS** — cần thì tra, tra xong thì cache |
>
> ⭐ **"LISP là DNS cho vị trí mạng"** — đây là câu tóm tắt tốt nhất.

### 7.4 ⭐ LISP dùng ở đâu

| Use case | Chi tiết |
|---|---|
| ⭐⭐ **SD-Access control plane** | ⭐⭐ **ĐÂY LÀ LÝ DO ENCOR DẠY LISP.** ⭐ Trong SD-Access, **Control Plane Node chạy LISP MS/MR**, Edge node là xTR. ➡️ **Module-09** |
| **Mobility** | Host đổi chỗ mà **giữ nguyên IP** — chỉ cần đăng ký RLOC mới với MS |
| **Multihoming** | Một site có nhiều đường ra, mỗi đường một RLOC |
| **Giảm kích thước bảng route** | Không cần đẩy /32 vào bảng toàn cầu |
| **IPv6 transition** | EID IPv6 chạy trên RLOC IPv4 (hoặc ngược lại) |

> ⭐ **Cho ENCOR chỉ cần:** ⭐ **EID vs RLOC** · ⭐ **vai trò ITR/ETR/xTR/MS/MR** · ⭐ **luồng map-request** ·
> ⭐ **mô hình PULL** · ⭐ **LISP = control plane của SD-Access**. ⭐ **KHÔNG cần cấu hình.**

---

## 📘 8. 🟡 VXLAN (blueprint 2.3.b — DESCRIBE)

### 8.1 ⭐ Vấn đề VXLAN giải quyết

| 🔴 Vấn đề của VLAN truyền thống | ⭐ VXLAN giải quyết thế nào |
|---|---|
| ⭐⭐ **VLAN ID chỉ 12 bit → tối đa 4094** — quá ít cho data center nhiều khách hàng | ⭐⭐ **VNI 24 bit → ~16 TRIỆU segment** |
| ⭐ Muốn kéo L2 giữa 2 nơi phải **trunk VLAN xuyên suốt** — dễ loop, phụ thuộc STP | ⭐ **L2 chạy TRÊN mạng L3 đã định tuyến** — không cần STP xuyên fabric |
| 🔴 ⭐ **VM live-migration** đòi hỏi cùng VLAN/subnet ở cả nguồn và đích | ⭐ **VXLAN kéo L2 đi bất cứ đâu trong fabric** → VM di chuyển thoải mái |
| ⭐ STP chặn link → **lãng phí đường** | ⭐ Underlay định tuyến → ⭐ **dùng được TẤT CẢ đường (ECMP)** |

### 8.2 ⭐⭐ VXLAN hoạt động thế nào

```
   VXLAN = "MAC-in-UDP" — bọc frame Ethernet vào một gói UDP

   Frame gốc:  [ Eth: MAC-A → MAC-B ][ IP ][ dữ liệu ]
                            ↓ VTEP bọc lại
   [Eth ngoài][IP ngoài: VTEP1→VTEP2][UDP 4789][VXLAN 8B (có VNI 24-bit)][Frame gốc]
      14B          20B                   8B              8B
   TỔNG OVERHEAD = 50 BYTE
```

| ⭐ Khái niệm | Nghĩa |
|---|---|
| ⭐⭐ **VNI / VNID** | ⭐ **VXLAN Network Identifier — 24 bit → 16.777.216 segment.** ⭐ Vai trò như VLAN ID nhưng nhiều gấp 4000 lần |
| ⭐⭐ **VTEP** | ⭐ **VXLAN Tunnel Endpoint** — thiết bị **bọc và mở gói**. Có thể là **switch vật lý** (leaf) hoặc **vSwitch trong hypervisor** |
| ⭐⭐ **Port** | ⭐ **UDP 4789** (chuẩn IANA) |
| ⭐ **Overhead** | ⭐ **50 byte** → 🔴 ⭐ **underlay PHẢI tăng MTU** (thường bật **jumbo frame 9216**) |
| ⭐⭐ **Underlay** | ⭐ **Mạng vật lý đã ĐỊNH TUYẾN** — thường **spine-leaf** chạy OSPF/IS-IS + ECMP |
| ⭐⭐ **Overlay** | ⭐ **Mạng ảo L2 chạy TRÊN underlay** |

> 🔴 ⭐⭐ **Nhớ 3 con số của VXLAN:** ⭐ **VNI = 24 bit (16 triệu)** · ⭐ **UDP 4789** · ⭐ **overhead 50 byte**.
> ⭐ Và ⭐ **so sánh với GRE: 24 byte** — VXLAN nặng gấp đôi vì nó bọc **cả frame Ethernet**, không chỉ gói IP.

### 8.3 ⭐ Control plane của VXLAN — hai thế hệ

| | ⭐ **Flood-and-Learn** (đời đầu) | ⭐⭐ **EVPN** (MP-BGP EVPN — hiện đại) |
|---|---|---|
| Học MAC thế nào | ⭐ **Flood** ra mọi VTEP rồi học như switch thường | ⭐⭐ **MP-BGP quảng bá MAC/IP** — biết trước, không cần flood |
| Xử lý BUM traffic *(Broadcast, Unknown unicast, Multicast)* | Multicast trong underlay, hoặc ingress replication | ⭐ Giảm mạnh nhờ **ARP suppression** |
| Hiệu quả | 🔴 Tốn băng thông | ⭐ **Tốt hơn hẳn** |
| ⭐ Hiện dùng | Ít | ⭐⭐ **Chuẩn de-facto của DC hiện đại** |

⭐ **Cho ENCOR:** biết ⭐ **"VXLAN cần một control plane, và cái hiện đại là MP-BGP EVPN"** là đủ.
⭐ **Không cần cấu hình EVPN** — đó là địa hạt của CCNP Data Center.

### 8.4 ⭐⭐ VXLAN vs GRE vs VLAN — bảng so sánh phải nhớ

| | ⭐ **VLAN** | ⭐ **GRE** | ⭐⭐ **VXLAN** |
|---|---|---|---|
| Bọc cái gì | (không bọc — chỉ gắn thẻ) | ⭐ **Gói IP** | ⭐⭐ **Cả FRAME Ethernet** |
| Vận chuyển bằng | 802.1Q tag 4 byte | ⭐ **IP protocol 47** | ⭐⭐ **UDP 4789** |
| ⭐ Số segment | ⭐ **4094** (12 bit) | (không áp dụng) | ⭐⭐ **16 triệu** (24 bit) |
| Overhead | 4 byte | ⭐ **24 byte** | ⭐ **50 byte** |
| Chở được L2? | ✅ (chính nó) | 🔴 ⭐ **Không** (chỉ L3) — *trừ khi dùng GRE bridging* | ⭐⭐ **✅ CÓ** |
| Dùng ở đâu | Campus LAN | ⭐ **WAN site-to-site** | ⭐⭐ **Data center fabric, SD-Access** |

> 🔴 ⭐⭐ **Bẫy đề:** *"GRE và VXLAN đều là overlay, khác nhau gì?"*
> ⭐ **GRE bọc gói IP (L3), overhead 24 byte, dùng cho WAN.**
> ⭐⭐ **VXLAN bọc frame Ethernet (L2), overhead 50 byte, VNI 24-bit, dùng cho DC/fabric.**

### 8.5 ⭐⭐ Bộ ba của SD-Access — nối sang Module-09

> ⭐⭐ **Đây là câu quan trọng nhất kết nối Module-08 với Module-09. Học thuộc:**

| Tầng | Công nghệ | Vai trò |
|---|---|---|
| ⭐⭐ **Control plane** | ⭐ **LISP** | ⭐ "Host này ở đâu?" — map EID ↔ RLOC |
| ⭐⭐ **Data plane** | ⭐ **VXLAN** | ⭐ Chở gói đi qua fabric, mang theo VNI **và** SGT |
| ⭐⭐ **Policy plane** | ⭐ **TrustSec (SGT)** | ⭐ "Ai được nói chuyện với ai" — Module-10 |

⭐ **Và:** ⭐ **VN (Virtual Network) trong SD-Access = VRF** (§3) — đó là lý do §3 nằm cùng module với §7, §8.

> ⭐ **Câu thần chú:** ⭐⭐ ***"SD-Access = LISP (điều khiển) + VXLAN (dữ liệu) + TrustSec (chính sách),
> chạy trên nền VRF."*** ⭐ Nhớ câu này là bạn đã cầm sẵn nửa số điểm phần SD-Access ở Module-09.

---

## 📖 9. HIỂU RÕ HƠN

### 9.1 VRF là "nhiều công ty thuê chung một tòa nhà"

⭐ Một tòa nhà (**router vật lý**), nhiều công ty thuê (**VRF**):
- ⭐ Mỗi công ty có **danh bạ nội bộ riêng** (bảng route riêng)
- ⭐ Công ty A có **"phòng 101"**, công ty B **cũng có "phòng 101"** — ⭐ **không xung đột** vì hai danh bạ tách biệt
- ⭐ Nhân viên A **không thể** gọi sang phòng của B (mặc định cách ly)
- ⭐ Muốn hai bên nói chuyện → phải ⭐ **cố ý bắc một đường dây** (route leaking)
- ⭐ Và bạn phải **nói rõ mình đang tra danh bạ của công ty nào** → ⭐ **đó chính là `ping vrf KHACH-A`**

🔴 ⭐ **Quên nói tên công ty (quên `vrf`) → bạn đang tra nhầm danh bạ tòa nhà (global table) → không thấy ai cả.**

### 9.2 GRE là "phong bì", IPsec là "hộp niêm phong"

- ⭐ **GRE = cho lá thư vào PHONG BÌ** và ghi địa chỉ mới bên ngoài.
  ⭐ Bưu điện (Internet) chỉ nhìn phong bì, không cần hiểu bên trong viết gì.
  🔴 ⭐ **Nhưng phong bì TRONG SUỐT** — ai cầm cũng đọc được.
- ⭐ **IPsec = HỘP KIM LOẠI NIÊM PHONG.** An toàn tuyệt đối,
  🔴 ⭐ **nhưng hộp này chỉ nhận bưu phẩm gửi cho MỘT người cụ thể** — không gửi được **thư báo chung cho cả khu phố** (multicast).
- ⭐⭐ **GRE over IPsec = cho phong bì vào hộp niêm phong.**
  ⭐ Vừa gửi được thư báo chung (routing protocol), vừa không ai đọc trộm được.

⭐ **Và "transport mode" nghĩa là:** ⭐ **phong bì đã có địa chỉ rồi, hộp không cần ghi địa chỉ lần nữa** —
⭐ đỡ tốn 20 byte.

### 9.3 Recursive routing là "muốn tới nhà phải đi qua chính nhà đó"

⭐ Bạn hỏi đường tới nhà bạn X. Người ta chỉ: ⭐ *"đi theo con đường tắt qua nhà X"*.
⭐ Nhưng muốn dùng con đường tắt đó, bạn **phải tới được nhà X trước**. ⭐ **Vòng luẩn quẩn.**

⭐ Router thông minh hơn bạn — nó phát hiện vòng lặp và ⭐ **tự đóng con đường tắt lại**:
`%TUN-5-RECURDOWN`.

⭐ **Cách tránh duy nhất:** ⭐ **đường tới nhà X phải học từ NGUỒN KHÁC** (đường lớn = underlay),
⭐ **không được học từ chính con đường tắt** (overlay).

### 9.4 LISP là DNS, BGP là danh bạ giấy

- ⭐ **BGP/IGP = phát cho mọi người một cuốn danh bạ dày cộp**, ai cũng phải giữ **toàn bộ** thông tin,
  ⭐ và mỗi khi có một số điện thoại đổi thì **in lại cho tất cả** (**PUSH**).
- ⭐⭐ **LISP = DNS.** ⭐ Bạn **không giữ** danh bạ nào cả. Cần gọi ai thì ⭐ **hỏi tổng đài** (Map Resolver),
  ⭐ được trả lời thì **ghi nhớ tạm** (map-cache), lần sau khỏi hỏi (**PULL**).
- ⭐ **Lợi ích:** người ta chuyển nhà (VM migration) thì ⭐ **chỉ cần báo tổng đài** — không cần in lại danh bạ toàn cầu.

### 9.5 VXLAN là "gửi cả cái phòng qua đường bưu điện"

- ⭐ **GRE** gửi **một lá thư** (gói IP) qua bưu điện.
- ⭐⭐ **VXLAN** gửi **cả một căn phòng có địa chỉ nội bộ riêng** (nguyên frame Ethernet + VNI).
  ⭐ Bên nhận mở ra và ⭐ **đặt căn phòng đó vào đúng tầng của mình** — hai máy ở hai data center
  ⭐ **cảm giác như đang cắm chung một switch**, dù thực tế cách nhau hàng nghìn km và ở giữa toàn router.

⭐ **Vì gửi cả căn phòng nên hộp phải to hơn** → ⭐ **50 byte overhead, và underlay phải bật jumbo frame.**

---

## 🧪 10. LAB 08 — VRF + GRE + IPsec

### 10.1 Topology

```
        ┌─ SITE A ─────────────┐                    ┌─ SITE B ─────────────┐
        │                      │                    │                      │
   Lo10 │ 10.1.1.1/24 ┌──────┐ │ Gi0/0              │ Gi0/0 ┌──────┐       │ Lo10
   Lo20 │ 10.10.10.1  │  R1  │─┼─203.0.113.1        203.0.113.2─│  R2  │───┼─10.2.2.1/24
   Lo30 │ 10.10.10.1  │      │ │       ╲              ╱         └──────┘   │
        │ (TRÙNG!) └──────┘ │        ╲            ╱                     │
        └──────────────────────┘         ╲          ╱                      └──────────────┘
                                      ┌───────────────┐
                                      │    R-ISP      │  đóng vai "Internet"
                                      │ 203.0.113.254 │  KHÔNG biết gì về 10.x
                                      └───────────────┘
```

| Node | Image | RAM | Vai trò |
|---|---|:---:|---|
| **R1** | vIOS *(hoặc CSR1000v nếu cần crypto)* | 512 MB / 3 GB | Site A — VRF + đầu tunnel |
| **R2** | vIOS *(hoặc CSR1000v)* | 512 MB / 3 GB | Site B — đầu tunnel kia |
| **R-ISP** | vIOS | 512 MB | ⭐ "Internet" — **cố ý không biết mạng 10.x** |

⭐ **Tổng RAM: ~1.5 GB (vIOS) hoặc ~6.5 GB (2× CSR1000v)** ✅

### 10.2 Bảng nối dây

| Từ | Interface | Tới | Interface | Mạng |
|---|---|---|---|---|
| R1 | Gi0/0 | R-ISP | Gi0/0 | 203.0.113.0/30 *(R1=.1, ISP=.254 dùng /24 cho tiện)* |
| R2 | Gi0/0 | R-ISP | Gi0/1 | 203.0.113.0/24 |

⭐ **Đơn giản hóa:** dùng chung subnet `203.0.113.0/24` cho cả hai link, R-ISP có 2 interface trong đó.
*(Không "đúng chuẩn" nhưng ⭐ **giữ lab gọn và không ảnh hưởng bài học**.)*

---

### Bước 0 — ⭐ Cấu hình nền (underlay)

```
!═══════ R-ISP ═══════ (đóng vai Internet: CHỈ biết mạng public)
hostname R-ISP
interface GigabitEthernet0/0
 ip address 203.0.113.254 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 203.0.113.253 255.255.255.0
 no shutdown
! CỐ Ý KHÔNG cấu hình route nào tới 10.0.0.0/8
!    → Chứng minh traffic 10.x chỉ đi được nhờ TUNNEL

!═══════ R1 ═══════
hostname R1
interface GigabitEthernet0/0
 ip address 203.0.113.1 255.255.255.0
 no shutdown
interface Loopback10
 ip address 10.1.1.1 255.255.255.0        ! LAN site A
!
ip route 0.0.0.0 0.0.0.0 203.0.113.254    ! default ra "Internet"

!═══════ R2 ═══════
hostname R2
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.0
 no shutdown
interface Loopback10
 ip address 10.2.2.1 255.255.255.0        ! LAN site B
!
ip route 0.0.0.0 0.0.0.0 203.0.113.253
```

✅ **Checkpoint 0:**
```
R1# ping 203.0.113.2
!!!!!                                      ! ✅ underlay thông

R1# ping 10.2.2.1 source 10.1.1.1
.....                                      ! ✅ ĐÚNG như mong đợi — PHẢI THẤT BẠI
                                           ! vì ISP không biết mạng 10.x
```
> 💡 ⭐ **Vì sao bước này quan trọng:** bạn vừa **chứng minh xuất phát điểm**.
> ⭐ Mọi thứ hoạt động sau đây **chỉ có thể là nhờ tunnel**, không phải nhờ may mắn.

---

### Bước 1 — ⭐⭐ VRF-lite và sức mạnh "IP trùng nhau"

```
!═══════ TRÊN R1 ═══════
vrf definition KHACH-A
 rd 65001:1
 address-family ipv4
 exit-address-family
!
vrf definition KHACH-B
 rd 65001:2
 address-family ipv4
 exit-address-family
!
! HAI interface, CÙNG một dải IP, khác VRF
interface Loopback20
 vrf forwarding KHACH-A                   ! GÁN VRF TRƯỚC
 ip address 10.10.10.1 255.255.255.0      ! ĐẶT IP SAU
 description LAN cua KHACH-A
!
interface Loopback30
 vrf forwarding KHACH-B                   ! VRF khác
 ip address 10.10.10.1 255.255.255.0      ! IP GIỐNG HỆT — VÀ NÓ CHẠY!
 description LAN cua KHACH-B
```

✅ **Checkpoint 1.1 — ⭐ chứng kiến điều "không thể":**
```
R1# show ip interface brief | include Loopback
Loopback10   10.1.1.1     YES manual up  up
Loopback20   10.10.10.1   YES manual up  up      
Loopback30   10.10.10.1   YES manual up  up      CÙNG IP, KHÔNG BÁO LỖI!
```

> 💡 ⭐⭐ **Dừng lại và ngẫm 30 giây.** Trên một router bình thường, đặt cùng IP lên 2 interface sẽ báo:
> `% 10.10.10.1 overlaps with Loopback20`.
> ⭐ **Ở đây không báo gì cả** — vì hai interface **sống trong hai vũ trụ khác nhau**.
> ⭐ **Đây chính là toàn bộ ý nghĩa của VRF.**

✅ **Checkpoint 1.2 — ba bảng route độc lập:**
```
R1# show vrf
  Name        Default RD    Protocols   Interfaces
  KHACH-A     65001:1       ipv4        Lo20
  KHACH-B     65001:2       ipv4        Lo30

R1# show ip route | include 10.10.10
                                          KHÔNG CÓ GÌ — global table không thấy

R1# show ip route vrf KHACH-A | include 10.10.10
C     10.10.10.0/24 is directly connected, Loopback20      chỉ thấy của mình

R1# show ip route vrf KHACH-B | include 10.10.10
C     10.10.10.0/24 is directly connected, Loopback30      cũng chỉ thấy của mình
```

✅ **Checkpoint 1.3 — ⭐⭐ tái hiện BẪY SỐ 2 (bẫy quan trọng nhất của VRF):**
```
R1# ping 10.10.10.1
!!!!!            ! ⚠️ Thành công NHƯNG... nó ping vào đâu?

! Thử ping một địa chỉ KHÁC trong VRF, từ global:
R1# ping 10.10.10.99
.....            ! THẤT BẠI

R1# ping vrf KHACH-A 10.10.10.99
.....            ! (vẫn fail vì không có host thật, nhưng hãy so sánh cách nó gửi gói)
```
> 💡 🔴 ⭐⭐ **Bài học:** ⭐ **quên `vrf` = đang dùng bảng global = KHÔNG BAO GIỜ tới được VRF.**
> ⭐ Đây là nguyên nhân của 90% ca *"tôi cấu hình VRF rồi mà không ping được"*.

✅ **Checkpoint 1.4 — ⭐ tái hiện BẪY SỐ 1 (mất IP khi gán VRF):**
```
R1(config)# interface Loopback40
R1(config-if)# ip address 192.168.99.1 255.255.255.0    ! đặt IP TRƯỚC (cố ý làm sai)
R1(config-if)# vrf forwarding KHACH-A                   ! rồi mới gán VRF

% Interface Loopback40 IPv4 disabled and address(es) removed due to enabling VRF KHACH-A

R1(config-if)# do show ip interface brief | include Loopback40
Loopback40    unassigned    YES unset  up  up         IP ĐÃ BAY MẤT
```
> 💡 🔴 ⭐⭐ **Ghi ngay vào `SO-TAY-LOI.md`.** ⭐ Trên production, nếu bạn đang SSH qua interface đó
> thì bạn **vừa tự cắt kết nối tới thiết bị**. ⭐ **Luôn: VRF trước, IP sau.**

---

### Bước 2 — ⭐⭐ GRE tunnel giữa hai site

```
!═══════ R1 ═══════
interface Tunnel0
 description GRE toi Site-B
 ip address 172.16.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 keepalive 10 3

!═══════ R2 ═══════
interface Tunnel0
 description GRE toi Site-A
 ip address 172.16.0.2 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.1
 keepalive 10 3
```

✅ **Checkpoint 2.1:**
```
R1# show ip interface brief | include Tunnel
Tunnel0   172.16.0.1   YES manual up  up      up/up

R1# ping 172.16.0.2
!!!!!                                          tunnel thông
```

✅ **Checkpoint 2.2 — ⭐ đọc thông số tunnel:**
```
R1# show interface tunnel0 | include MTU|Tunnel source|transport
  MTU 17916 bytes, BW 100 Kbit/sec
  Tunnel source 203.0.113.1 (GigabitEthernet0/0), destination 203.0.113.2
  Tunnel transport MTU 1476 bytes         ← 1500 − 24 = GRE overhead
```
> 💡 ⭐ **Con số 1476 là bằng chứng vật lý cho lý thuyết §4.1.** ⭐ Nhìn thấy nó một lần là nhớ mãi.

Giờ chạy **OSPF qua tunnel** để hai LAN thấy nhau:
```
!═══════ R1 ═══════
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0        ! mạng tunnel
 network 10.1.1.0 0.0.0.255 area 0        ! LAN site A
 ! CHÚ Ý: KHÔNG có 203.0.113.0 ở đây!

!═══════ R2 ═══════
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0
 network 10.2.2.0 0.0.0.255 area 0
```

✅ **Checkpoint 2.3 — ⭐⭐ bài test quyết định:**
```
R1# show ip ospf neighbor
Neighbor ID   Pri  State     Dead Time  Address      Interface
2.2.2.2         0  FULL/  -  00:00:35   172.16.0.2   Tunnel0

R1# show ip route ospf
O   10.2.2.0/24 [110/1001] via 172.16.0.2, 00:01:12, Tunnel0

R1# ping 10.2.2.1 source 10.1.1.1
!!!!!                                    THÀNH CÔNG!
```
> 💡 ⭐⭐ **So sánh với Checkpoint 0** — cùng lệnh ping đó, lúc nãy **thất bại hoàn toàn**.
> ⭐ **R-ISP vẫn KHÔNG hề biết gì về mạng 10.x** — nó chỉ thấy các gói IP giữa 203.0.113.1 và 203.0.113.2.
> ⭐ **Đó chính là ý nghĩa của overlay.**

⭐ **Kiểm chứng thêm (rất đáng làm):**
```
R-ISP# show ip route | include 10\.
                                         TRỐNG. ISP hoàn toàn không biết mạng 10.x
```

---

### Bước 3 — 🔴 ⭐⭐ CỐ Ý TÁI HIỆN RECURSIVE ROUTING

> ⭐ **Đây là bước giá trị nhất của cả LAB.** ⭐ **Đừng bỏ qua.** Lab hỏng dạy nhiều hơn lab chạy.

```
! Trên CẢ R1 VÀ R2 — cố ý advertise mạng WAN vào OSPF-qua-tunnel:
router ospf 1
 network 203.0.113.0 0.0.0.255 area 0     ! DÒNG GÂY THẢM HỌA
```

✅ **Checkpoint 3.1 — quan sát vụ nổ (chờ ~30–60 giây):**
```
%TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing
%LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel0, changed state to down
%OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel0 from FULL to DOWN
%LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel0, changed state to up
%TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing
   ...LẶP MÃI. Đây là "tunnel flapping".
```

✅ **Checkpoint 3.2 — nhìn vào NGUYÊN NHÂN (bắt lúc tunnel đang up):**
```
R1# show ip route 203.0.113.2
Routing entry for 203.0.113.0/24
  Known via "ospf 1", distance 110, metric 1001
   * 172.16.0.2, from 2.2.2.2, via Tunnel0      ← NHÌN DÒNG NÀY!

"Muốn tới 203.0.113.2 → đi qua Tunnel0"
Nhưng Tunnel0 cần biết đường tới 203.0.113.2 để hoạt động
→ VÒNG LẶP. Router phát hiện và tự tắt tunnel.
```

✅ **Checkpoint 3.3 — sửa bằng CẢ HAI cách, hiểu vì sao mỗi cách có tác dụng:**

```
! CÁCH 1 (đúng nhất) — gỡ mạng WAN khỏi OSPF-qua-tunnel:
router ospf 1
 no network 203.0.113.0 0.0.0.255 area 0
```
```
! CÁCH 2 — static route AD thấp hơn "đè" lên OSPF:
ip route 203.0.113.2 255.255.255.255 203.0.113.254
!    AD 1  <  AD 110 của OSPF → static LUÔN THẮNG
!    Và /32 dài hơn /24 → longest-prefix cũng thắng (Module-03!)
```

✅ **Xác nhận đã ổn:**
```
R1# show ip route 203.0.113.2
   phải trỏ ra GigabitEthernet0/0, KHÔNG được trỏ ra Tunnel0

R1# show interface tunnel0 | include line protocol
Tunnel0 is up, line protocol is up        ổn định, không flap nữa
```

> 💡 🔴 ⭐⭐ **Bài học một câu — ghi vào `SO-TAY-LOI.md`:**
> ⭐ ***"Đường tới tunnel destination KHÔNG BAO GIỜ được đi qua chính tunnel đó."***

---

### Bước 4 — ⭐⭐ MTU & MSS

✅ **Checkpoint 4.1 — tìm ra ngưỡng MTU thật của tunnel:**
```
R1# ping 172.16.0.2 df-bit size 1400
!!!!!                                    ✅ qua được

R1# ping 172.16.0.2 df-bit size 1476
!!!!!                                    ✅ vẫn qua — đây là ĐÚNG giới hạn

R1# ping 172.16.0.2 df-bit size 1477
Packet sent with the DF bit set
.....                                    THẤT BẠI
   Bạn vừa TỰ TAY tìm ra con số 1476 = 1500 − 24 (GRE overhead)
```

✅ **Checkpoint 4.2 — áp cấu hình chuẩn (⭐ trên CẢ HAI đầu):**
```
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
```
```
R1# show interface tunnel0 | include MTU
  MTU 17916 bytes ...
  IP MTU 1400 bytes
  Tunnel transport MTU 1476 bytes
```

> 💡 ⭐ **Vì sao vẫn nên đặt 1400 dù tunnel chịu được 1476?**
> ⭐ Vì lát nữa thêm **IPsec** sẽ ăn thêm ~50–60 byte. ⭐ **Đặt 1400 ngay từ đầu là an toàn cho cả hai trường hợp** —
> đây cũng là con số các nhà mạng và nhà tích hợp dùng mặc định ngoài đời.

---

### Bước 5 — ⭐⭐ Thêm IPsec: biến GRE thành GRE over IPsec

> 🔴 ⚠️ **Nếu vIOS báo `% Invalid input` ở lệnh `crypto isakmp policy` → xem §1.1**,
> đổi R1/R2 sang **CSR1000v**, hoặc **bỏ qua bước này và đọc kỹ cấu hình** (vẫn nắm được để thi).

```
!═══════ TRÊN R1 ═══════
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
!
crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.2
!
crypto ipsec transform-set TSET esp-aes 256 esp-sha256-hmac
 mode transport                                ! TRANSPORT cho GRE over IPsec
!
crypto ipsec profile IPSEC-PROF
 set transform-set TSET
!
interface Tunnel0
 tunnel protection ipsec profile IPSEC-PROF    ! dòng duy nhất cần thêm vào tunnel

!═══════ TRÊN R2 ═══════ (giống hệt, chỉ đổi địa chỉ peer)
crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.1
   ! phần còn lại y hệt R1
```

✅ **Checkpoint 5.1 — Phase 1:**
```
R1# ping 172.16.0.2                       ! tạo traffic để kích hoạt VPN
!!!!!

R1# show crypto isakmp sa
dst           src           state     conn-id status
203.0.113.2   203.0.113.1   QM_IDLE   1001  ACTIVE
                            "QM_IDLE" = Phase 1 XONG. ĐÂY LÀ TRẠNG THÁI TỐT.
```

✅ **Checkpoint 5.2 — ⭐⭐ Phase 2 và bằng chứng dữ liệu đang được mã hóa:**
```
R1# show crypto ipsec sa | include ident|encaps|decaps|encrypt|decrypt
   local  ident (addr/mask/prot/port): (203.0.113.1/255.255.255.255/47/0)
   remote ident (addr/mask/prot/port): (203.0.113.2/255.255.255.255/47/0)
                                                                    47 = GRE!
    #pkts encaps: 58, #pkts encrypt: 58
    #pkts decaps: 56, #pkts decrypt: 56

! BÀI TEST QUYẾT ĐỊNH — ping rồi xem số có TĂNG không:
R1# ping 10.2.2.1 source 10.1.1.1 repeat 20
!!!!!!!!!!!!!!!!!!!!

R1# show crypto ipsec sa | include encaps|decaps
    #pkts encaps: 78    (58 + 20)
    #pkts decaps: 76    (56 + 20)
```

> 💡 ⭐⭐ **`encaps` và `decaps` CÙNG TĂNG = VPN thật sự đang chở dữ liệu.**
> ⭐ Đây là bằng chứng mạnh hơn nhiều so với việc chỉ nhìn `QM_IDLE`.
> ⭐ **`prot 47` (GRE) trong ident** chính là bằng chứng bạn đang chạy ⭐ **GRE over IPsec**,
> chứ không phải IPsec thuần.

```
R1# show crypto session
Interface: Tunnel0
Session status: UP-ACTIVE
Peer: 203.0.113.2 port 500
  IKEv1 SA: local 203.0.113.1/500 remote 203.0.113.2/500 Active
  IPSEC FLOW: permit 47 host 203.0.113.1 host 203.0.113.2
        Active SAs: 2, origin: crypto map
```

✅ **Checkpoint 5.3 — ⭐ OSPF vẫn chạy (đây là điều IPsec thuần không làm được):**
```
R1# show ip ospf neighbor
2.2.2.2   0  FULL/  -  00:00:33  172.16.0.2  Tunnel0
```
> 💡 ⭐⭐ **Đây là câu trả lời sống động cho câu hỏi "vì sao phải GRE over IPsec".**
> ⭐ Nếu dùng **IPsec thuần (crypto map)**, ⭐ **OSPF sẽ KHÔNG chạy được** vì multicast `224.0.0.5`
> không đi qua được. ⭐ **Bạn vừa nhìn thấy tận mắt lý do tồn tại của cả mục 2.2.b.**

---

### Bước 6 — 🔴 ⭐⭐ CỐ Ý PHÁ IPsec (bắt buộc làm)

**Phá 1 — sai pre-shared key:**
```
R1(config)# no crypto isakmp key CCNP-ENCOR-2026 address 203.0.113.2
R1(config)# crypto isakmp key SAI-MAT-KHAU address 203.0.113.2
R1# clear crypto isakmp
R1# clear crypto sa
R1# ping 172.16.0.2
```
✅ **Quan sát:**
```
R1# show crypto isakmp sa
dst           src           state           conn-id status
203.0.113.2   203.0.113.1   MM_NO_STATE   1002  ACTIVE (deleted)
                            "MM_NO_STATE" = PHASE 1 THẤT BẠI
```
> 💡 ⭐⭐ **Ghi nhớ cặp đối lập này — đề hỏi rất nhiều:**
> ⭐ **`QM_IDLE` = Phase 1 THÀNH CÔNG** · 🔴 ⭐ **`MM_NO_STATE` / `MM_KEY_EXCH` = Phase 1 ĐANG HỎNG**

⭐ **Sửa lại key rồi `clear crypto isakmp` — xác nhận quay về `QM_IDLE`.**

**Phá 2 — lệch transform-set:**
```
R2(config)# crypto ipsec transform-set TSET esp-aes 128 esp-sha256-hmac
!                                             128 thay vì 256
R1# clear crypto sa
```
✅ **Quan sát:** ⭐ **Phase 1 vẫn `QM_IDLE` ✅ nhưng `show crypto ipsec sa` KHÔNG có SA nào active**,
⭐ `encaps`/`decaps` **đứng yên**.
> 💡 ⭐⭐ **Bài học:** ⭐ **Phase 1 OK mà không có dữ liệu chảy → lỗi ở PHASE 2** (transform-set / ACL).
> ⭐ Đây là cách khoanh vùng nhanh nhất khi troubleshoot IPsec.

**Phá 3 — tắt tunnel protection ở một đầu:**
```
R2(config-if)# no tunnel protection ipsec profile IPSEC-PROF
```
✅ **Quan sát:** ⭐ tunnel vẫn có thể hiện up (GRE stateless) nhưng ⭐ **traffic không qua được** —
một đầu mã hóa, đầu kia không hiểu.
> 💡 ⭐ **Bài học:** ⭐ **`tunnel protection` phải có ở CẢ HAI đầu.**

---

## 🚀 11. LAB NÂNG CAO

### 11.1 🚀 ⭐ Tunnel nằm TRONG VRF (rất hay gặp ngoài đời)

⭐ **Tình huống:** interface WAN nằm trong VRF `INTERNET`, nhưng traffic của tunnel là mạng nội bộ.

```
interface Tunnel0
 ip address 172.16.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel vrf INTERNET              ! "hãy TÌM ĐƯỜNG tới destination trong VRF INTERNET"
```
> ⭐⭐ **Phân biệt hai lệnh dễ lẫn — đề có thể hỏi:**
> · ⭐ **`vrf forwarding X`** trên Tunnel0 = ⭐ **traffic BÊN TRONG tunnel thuộc VRF X** (overlay)
> · ⭐ **`tunnel vrf X`** = ⭐ **đường đi TỚI tunnel destination nằm trong VRF X** (underlay)
>
> ⭐ **Mẹo nhớ:** ⭐ *"`tunnel vrf` nói về VỎ, `vrf forwarding` nói về RUỘT."*

### 11.2 🚀 ⭐ Route leaking giữa VRF và global

```
! Cho VRF KHACH-A đi ra Internet (bảng global)
ip route vrf KHACH-A 0.0.0.0 0.0.0.0 203.0.113.254 global
!                                                   từ khóa quan trọng
! Chiều về: từ global trỏ ngược vào VRF
ip route 10.10.10.0 255.255.255.0 Loopback20
```
✅ **Test:** `ping vrf KHACH-A 203.0.113.254` → phải thành công.
⭐ **Nhớ:** ⭐ **route leaking phải làm CẢ HAI CHIỀU** mới thông.

### 11.3 🚀 ⭐ OSPF chạy trong VRF

```
router ospf 100 vrf KHACH-A
 router-id 1.1.1.100
 network 10.10.10.0 0.0.0.255 area 0
!
show ip ospf 100                          ! process riêng
show ip route vrf KHACH-A ospf
show ip ospf neighbor vrf KHACH-A
```

### 11.4 🚀 So sánh: IPsec thuần (crypto map) — để thấy nó KHÔNG chạy được OSPF

⭐ **Bài tập:** tháo GRE, dựng IPsec thuần bằng crypto map giữa R1–R2 (§5.4), rồi thử bật OSPF.
✅ **Bạn sẽ thấy:** ⭐ **OSPF neighbor KHÔNG BAO GIỜ lên** (multicast `224.0.0.5` không qua được crypto map).
⭐ **Đây là cách chứng minh mạnh nhất vì sao GRE over IPsec tồn tại.**

### 11.5 🚀 Bắt gói bằng Wireshark

⭐ Bắt gói trên link R1↔R-ISP trong EVE-NG *(chuột phải link → Capture)*:

| Giai đoạn | ⭐ Bạn sẽ thấy |
|---|---|
| ⭐ **Trước khi bật IPsec** | ⭐ **Gói GRE — và Wireshark GIẢI MÃ ĐƯỢC toàn bộ**: thấy rõ IP nội bộ 10.1.1.1, thấy cả gói OSPF bên trong. 🔴 ⭐ **Bằng chứng GRE không mã hóa gì cả** |
| ⭐ **Sau khi bật IPsec** | ⭐ **Chỉ thấy `ESP`** — nội dung là **một khối byte vô nghĩa**. ⭐ Không đọc được IP nội bộ, không thấy OSPF |
| ⭐ **Lúc mới bật** | ⭐ Thấy **ISAKMP trên UDP 500** — chính là Phase 1 đang bắt tay |

> 💡 ⭐⭐ **Đây là bài lab thuyết phục nhất cả module.** ⭐ Chụp lại hai ảnh Wireshark (trước/sau)
> và dán vào `SO-TAY-LOI.md`. ⭐ **Nhìn một lần là nhớ cả đời sự khác nhau giữa GRE và GRE over IPsec.**

---

## 💡 12. THỰC CHIẾN ĐI LÀM

| # | Tình huống thật | ⭐ Điều người mới làm sai | ⭐ Cách làm đúng |
|:---:|---|---|---|
| 1 | Gán VRF cho interface trên switch production | Đặt IP trước, gán VRF sau | 🔴 ⭐ **IP bay mất, mất kết nối tới thiết bị.** ⭐ **VRF trước, IP sau.** ⭐ Và **luôn làm qua console/OOB**, đừng làm qua chính interface đó |
| 2 | "VRF không hoạt động, ping không được" | Xóa đi cấu hình lại | ⭐ **99% là quên gõ `vrf`** trong lệnh ping/show. ⭐ Kiểm tra cái này **trước tiên** |
| 3 | Dựng VPN site-to-site, cần chạy OSPF giữa 2 site | Dùng IPsec thuần (crypto map) | 🔴 ⭐ **OSPF không lên** (multicast). ⭐ **Phải dùng GRE over IPsec** |
| 4 | VPN "lên" nhưng người dùng kêu web load nửa chừng | Đổ lỗi ISP | ⭐⭐ **MTU/MSS.** ⭐ Thêm `ip mtu 1400` + `ip tcp adjust-mss 1360` **cả hai đầu** |
| 5 | VPN lên (`QM_IDLE`) nhưng không ping được qua | Debug crypto hàng giờ | ⭐⭐ Kiểm tra **NAT có "ăn" mất traffic VPN không** (§5.5) — ⭐ `deny` traffic VPN trong NAT ACL |
| 6 | Tunnel cứ lên xuống liên tục sau khi bật routing | Nghĩ do đường truyền ISP kém | ⭐⭐ **Recursive routing.** Xem log tìm `%TUN-5-RECURDOWN`. ⭐ Gỡ mạng WAN khỏi giao thức chạy qua tunnel |
| 7 | Tunnel hiện up/up nhưng đầu kia đã tắt máy | Tin vào `show ip int brief` | ⭐ **GRE là stateless.** ⭐ **Luôn bật `keepalive`** để trạng thái phản ánh đúng |
| 8 | Cắm host ảo hóa (Proxmox/ESXi) vào switch | Bật `port-security maximum 1` | 🔴 ⭐ **Sập port ngay** — một cáp mang MAC của **hàng chục VM** (§2.2) |
| 9 | Port nối host ảo hóa | Để access port rồi thắc mắc sao VM chỉ vào được 1 VLAN | ⭐ **Trunk** (VST), ⭐ **native VLAN khớp** với VLAN quản lý host. 🔴 ⭐ Native lệch = **mất quản lý host** |
| 10 | Triển khai VXLAN trong DC | Giữ nguyên MTU 1500 | 🔴 ⭐ **VXLAN thêm 50 byte** → ⭐ **phải bật jumbo frame (9216) trên toàn underlay** |
| 11 | Cần cách ly mạng camera khỏi mạng văn phòng | Chỉ dùng ACL | ⭐ **VRF mạnh hơn** — cách ly ở tầng **bảng định tuyến**, không phụ thuộc việc nhớ viết đủ ACL |
| 12 | Sếp hỏi "mình có nên làm SD-Access không" | Trả lời theo brochure | ⭐ Hiểu rằng nó là ⭐ **LISP + VXLAN + TrustSec trên nền VRF** — cần **DNA Center + ISE + switch đủ đời**. ➡️ **Module-09** |

> 🔴 ⭐⭐ **Ba câu thần chú của module này:**
> 1. ⭐ **"VRF trước, IP sau. Ping thì nhớ gõ `vrf`."**
> 2. ⭐ **"Tunnel destination không được đi qua tunnel."**
> 3. ⭐ **"GRE cho routing, IPsec cho bảo mật — và luôn nhớ MSS."**

---

## 🎓 13. BẪY TRONG ĐỀ ENCOR

| # | ⭐ Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | "VMware Workstation là hypervisor Type 1" | 🔴 ⭐ **Type 2** (chạy trên OS). ⭐ **ESXi/Hyper-V/KVM/Proxmox = Type 1** |
| 2 | "vSwitch cần chạy STP để chống loop" | 🔴 ⭐⭐ **KHÔNG.** ⭐ vSwitch **không bao giờ forward giữa 2 uplink** → không thể tạo loop |
| 3 | "vSwitch học MAC từ uplink như switch thường" | 🔴 ⭐ **Không** — nó **đã biết trước** MAC của các VM cắm vào |
| 4 | "VST là VM tự gắn thẻ VLAN" | 🔴 ⭐ **VST = vSwitch gắn thẻ.** ⭐ **VGT mới là VM tự gắn** |
| 5 | "VRF chia CPU/RAM của router" | 🔴 ⭐ **VRF chỉ chia BẢNG ĐỊNH TUYẾN** (control plane), không chia tài nguyên phần cứng |
| 6 | "Hai VRF không thể dùng cùng dải IP" | 🔴 ⭐⭐ **Dùng được — đó chính là điểm mạnh nhất của VRF** |
| 7 | "Gán VRF xong IP vẫn còn nguyên" | 🔴 ⭐⭐ **IP BỊ XÓA.** Phải đặt lại |
| 8 | "`ping 10.1.1.1` sẽ tới host trong VRF" | 🔴 ⭐⭐ **Không** — phải `ping vrf <tên> 10.1.1.1` |
| 9 | "VRF-lite cần MPLS" | 🔴 ⭐ **Không.** ⭐ **VRF-lite = không MPLS, không MP-BGP.** ENCOR chỉ hỏi VRF-lite |
| 10 | "Route Target dùng trong VRF-lite" | 🔴 ⭐ **RT chỉ dùng với MP-BGP/MPLS.** ⭐ VRF-lite chỉ khai **RD** cho đủ cú pháp |
| 11 | "GRE có mã hóa dữ liệu" | 🔴 ⭐⭐ **KHÔNG.** ⭐ GRE hoàn toàn trong suốt |
| 12 | "GRE overhead là 20 byte" | 🔴 ⭐ **24 byte** (20 IP mới + 4 GRE) → ⭐ **tunnel MTU 1476** |
| 13 | "IPsec thuần chạy được OSPF" | 🔴 ⭐⭐ **KHÔNG** — không chở được multicast. ⭐ **Phải GRE over IPsec** |
| 14 | "GRE over IPsec dùng tunnel mode" | 🔴 ⭐⭐ **TRANSPORT mode** (GRE đã có IP header rồi) |
| 15 | "AH mã hóa dữ liệu" | 🔴 ⭐ **AH chỉ xác thực, KHÔNG mã hóa.** ⭐ **ESP mới mã hóa** |
| 16 | "AH đi qua NAT được" | 🔴 ⭐ **Không** — AH ký cả IP header. ⭐ **ESP + NAT-T (UDP 4500)** thì được |
| 17 | "ESP là IP protocol 51" | 🔴 ⭐ **ESP = 50 · AH = 51** |
| 18 | "IKE Phase 2 xác thực đối tác" | 🔴 ⭐ **Phase 1 xác thực.** ⭐ Phase 2 chốt transform-set và interesting traffic |
| 19 | "`MM_NO_STATE` nghĩa là VPN đã lên" | 🔴 ⭐⭐ **Phase 1 ĐANG HỎNG.** ⭐ **`QM_IDLE` mới là tốt** |
| 20 | "ACL interesting traffic giống nhau ở hai đầu" | 🔴 ⭐ **Phải ĐỐI XỨNG GƯƠNG** — đảo source/destination |
| 21 | "Recursive routing là lỗi phần cứng" | 🔴 ⭐ **Lỗi thiết kế định tuyến** — route tới tunnel destination đi qua chính tunnel |
| 22 | "`ip mtu` giải quyết được mọi vấn đề MTU" | 🔴 ⭐ Cần cả ⭐ **`ip tcp adjust-mss`** — ⭐ nó ngăn gói lớn **được tạo ra**, thay vì phân mảnh sau |
| 23 | "LISP là giao thức định tuyến thay thế BGP" | 🔴 ⭐ **LISP là kiến trúc map-and-encap**, mô hình ⭐ **PULL** (như DNS), không phải PUSH như BGP |
| 24 | "ITR mở gói, ETR bọc gói" | 🔴 ⭐⭐ **Ngược. ITR (Ingress) BỌC · ETR (Egress) MỞ** |
| 25 | "Map Server trả lời truy vấn của ITR" | 🔴 ⭐ **Map RESOLVER nhận truy vấn.** ⭐ **Map SERVER nhận đăng ký từ ETR** |
| 26 | "VNI dài 12 bit như VLAN" | 🔴 ⭐⭐ **VNI = 24 bit → ~16 triệu segment** |
| 27 | "VXLAN dùng UDP 4341" | 🔴 ⭐⭐ **VXLAN = UDP 4789.** ⭐ **4341 là LISP data**, 4342 là LISP control |
| 28 | "VXLAN overhead giống GRE" | 🔴 ⭐ **VXLAN 50 byte** (bọc cả frame Ethernet) vs ⭐ **GRE 24 byte** (chỉ bọc gói IP) |
| 29 | "VXLAN thay thế được routing" | 🔴 ⭐ **VXLAN CẦN một underlay đã định tuyến** để chạy trên đó |
| 30 | "SD-Access dùng VXLAN làm control plane" | 🔴 ⭐⭐ **VXLAN = DATA plane · LISP = CONTROL plane · TrustSec = POLICY plane** |

---

## 🐛 14. GỠ LỖI NHANH

### 14.1 ⭐ Hộp lệnh vạn năng

```
═══ VRF ═══
show vrf                              ! VRF nào tồn tại, interface nào thuộc nó
show vrf detail
show ip route vrf <TEN>               ! bảng route CỦA VRF
show ip interface brief vrf <TEN>
show ip protocols vrf <TEN>
show ip arp vrf <TEN>
ping vrf <TEN> <ip>                   ! ĐỪNG QUÊN "vrf"
traceroute vrf <TEN> <ip>

═══ GRE ═══
show interface tunnel0                ! up/up? transport MTU? keepalive?
show ip route <tunnel-destination>    ! CÓ trỏ qua Tunnel0 không? (recursive!)
ping <tunnel-peer> df-bit size 1476   ! test MTU thật
show log | include TUN-5-RECURDOWN    ! bằng chứng recursive routing
debug tunnel                          ! ⚠️ chỉ trong lab

═══ IPsec — theo ĐÚNG thứ tự này ═══
ping <peer-public-ip>                 ! ① underlay có thông không
show crypto isakmp sa                 ! ② Phase 1: QM_IDLE = tốt
show crypto ipsec sa                  ! ③ Phase 2: encaps/decaps CÓ TĂNG không
show crypto session detail            ! ④ tóm tắt
show crypto map                       ! (nếu dùng crypto map)
show crypto ipsec transform-set
clear crypto isakmp                   ! ép đàm phán lại Phase 1
clear crypto sa                       ! ép đàm phán lại Phase 2
debug crypto isakmp                   ! ⚠️ chỉ trong lab — rất nhiều output
debug crypto ipsec

═══ Nền tảng ═══
show ip route
show ip ospf neighbor
show ip access-lists                  ! ACL NAT có deny traffic VPN chưa
show ip nat translations              ! NAT có "ăn" mất traffic VPN không
```

### 14.2 ⭐⭐ Bảng: triệu chứng → nguyên nhân → cách sửa

| 🔴 Triệu chứng | ⭐ Nguyên nhân | ✅ Cách sửa |
|---|---|---|
| ⭐⭐ **VRF: ping không được** | ⭐⭐ **Quên gõ `vrf` trong lệnh ping** | ⭐ `ping vrf <TEN> <ip>` — **kiểm tra cái này ĐẦU TIÊN** |
| ⭐⭐ **Gán VRF xong interface mất IP** | ⭐ **Hành vi bình thường của IOS** | ⭐ Đặt lại IP. ⭐ **Lần sau: VRF trước, IP sau** |
| ⭐ **VRF: route không xuất hiện** | Interface chưa gán VRF · routing protocol chưa khai `vrf` | ⭐ `show vrf` xem interface đã thuộc VRF chưa · `router ospf X vrf Y` |
| ⭐ **Hai VRF cần nói chuyện mà không được** | Chưa route leaking | ⭐ Static với từ khóa `global`, hoặc MP-BGP RT (§3.5). ⭐ **Nhớ làm CẢ HAI CHIỀU** |
| ⭐ **Tunnel down/down** | `tunnel source` sai interface, hoặc interface đó down | ⭐ `show ip interface brief` kiểm tra interface nguồn |
| ⭐⭐ **Tunnel up/down** | ⭐ **Không có route tới `tunnel destination`** | ⭐ `show ip route <dest>` |
| ⭐⭐ **Tunnel FLAPPING liên tục** | ⭐⭐ **RECURSIVE ROUTING** | ⭐ `show log \| inc RECURDOWN` · gỡ mạng WAN khỏi routing-qua-tunnel (§4.3) |
| ⭐ **Tunnel up/up nhưng đầu kia đã chết** | ⭐ GRE **stateless**, chưa bật keepalive | ⭐ `keepalive 10 3` cả hai đầu |
| ⭐⭐ **Ping OK nhưng web/HTTPS treo nửa chừng** | ⭐⭐ **MTU/MSS** | ⭐ `ip mtu 1400` + `ip tcp adjust-mss 1360` **cả hai đầu** |
| 🔴 ⭐ **`show crypto isakmp sa` TRỐNG** | Chưa có traffic kích hoạt · không tới được peer · ACL/interesting traffic không khớp | ⭐ Ping để tạo traffic · kiểm tra `ping <peer-public>` |
| 🔴 ⭐⭐ **State = `MM_NO_STATE`** | ⭐⭐ **Sai pre-shared key** hoặc **lệch ISAKMP policy** | ⭐ So từng tham số **HAGLE** hai đầu · kiểm tra key và địa chỉ peer |
| ⭐ **Phase 1 OK, Phase 2 không có SA** | ⭐ **Lệch transform-set** hoặc **ACL không đối xứng** | ⭐ `show crypto ipsec transform-set` hai đầu · ACL phải đảo gương |
| 🔴 ⭐⭐ **`encaps` tăng, `decaps` = 0** | ⭐⭐ **Chiều về bị chặn** — firewall chặn ESP/UDP500, hoặc đầu kia sai cấu hình, hoặc thiếu route ngược | ⭐ Kiểm tra firewall giữa hai site · kiểm tra cấu hình + route ở đầu kia |
| ⭐ **`decaps` tăng, `encaps` = 0** | ⭐ Traffic của mình không vào tunnel | ⭐ Kiểm tra routing đẩy traffic qua Tunnel0 · ACL interesting traffic |
| ⭐⭐ **VPN lên (`QM_IDLE`) nhưng không ping qua được** | ⭐⭐ **NAT "ăn" mất traffic VPN** | ⭐ `deny` traffic VPN trong NAT ACL, đặt **TRƯỚC** `permit` (§5.5) |
| ⭐ **`% Invalid input` ở lệnh crypto** | ⭐ Image thiếu feature `securityk9` | ⭐ `show version \| include Security` · đổi sang **CSR1000v** (§1.1) |
| ⭐ **VPN lên rồi tự rớt sau vài giờ** | ⭐ **Lifetime lệch** giữa hai đầu, hoặc rekey thất bại | ⭐ So `lifetime` Phase 1 & 2 · bật `crypto isakmp keepalive` (DPD) |

### 14.3 ⭐ Quy trình troubleshoot GRE over IPsec — 6 bước

```
① UNDERLAY:   ping <peer-public-ip>            → không thông? sửa routing/ISP TRƯỚC
② PHASE 1:    show crypto isakmp sa            → QM_IDLE?  không → sai PSK / policy
③ PHASE 2:    show crypto ipsec sa             → có SA?    không → transform-set / ACL
④ DỮ LIỆU:  encaps VÀ decaps CÓ TĂNG không?  → chỉ 1 chiều tăng → firewall / route ngược
⑤ TUNNEL:     show interface tunnel0           → up/up? có flap (recursive)?
⑥ ROUTING:    show ip ospf neighbor            → FULL? có học route của site kia không?
                 ping <LAN-dich> source <LAN-nguon>
```
> ⭐ **Đi đúng thứ tự này thì không bao giờ lạc.** ⭐ **Đừng nhảy vào `debug crypto` ở bước đầu** —
> nó cho hàng trăm dòng và bạn sẽ không biết đọc từ đâu.

---

## 📝 15. QUIZ TỰ KIỂM TRA

**1.** Type 1 và Type 2 hypervisor khác nhau gì? Cho 2 ví dụ mỗi loại.
<details><summary>Đáp án</summary>

⭐ **Type 1 (bare metal):** chạy **thẳng trên phần cứng** → nhanh hơn, dùng trong DC.
Ví dụ: ⭐ **VMware ESXi, Microsoft Hyper-V, KVM/Proxmox VE, XenServer**.

⭐ **Type 2 (hosted):** chạy **trên một hệ điều hành** → chậm hơn, dùng trên máy cá nhân.
Ví dụ: ⭐ **VMware Workstation, VirtualBox, Parallels**.
</details>

**2.** Vì sao vSwitch không cần chạy STP?
<details><summary>Đáp án</summary>

⭐⭐ **Vì vSwitch KHÔNG BAO GIỜ chuyển tiếp frame từ uplink này sang uplink khác** →
⭐ **về mặt kiến trúc, nó không thể tạo ra vòng lặp.** Nó chỉ chuyển VM↔VM và VM↔uplink.

⭐ Ngoài ra vSwitch cũng **không học MAC từ uplink** — nó **đã biết trước** MAC của các VM cắm vào nó,
và **drop** gói không thuộc VM nào.
</details>

**3.** EST, VST, VGT — ai gắn thẻ VLAN trong mỗi kiểu? Kiểu nào phổ biến nhất?
<details><summary>Đáp án</summary>

| Kiểu | Ai gắn thẻ | Port switch vật lý |
|---|---|---|
| ⭐ **EST** | **Switch vật lý** | Access |
| ⭐⭐ **VST** | ⭐ **vSwitch** | ⭐ **Trunk** |
| ⭐ **VGT** | ⭐ **VM (guest OS)** tự gắn | Trunk |

⭐ **VST phổ biến nhất** — mỗi port group một VLAN ID, port switch là trunk.
</details>

**4.** Đặt cùng địa chỉ `10.10.10.1/24` lên hai interface của cùng một router — khi nào được phép?
<details><summary>Đáp án</summary>

⭐⭐ **Khi hai interface nằm trong HAI VRF KHÁC NHAU.**

⭐ Mỗi VRF có bảng định tuyến riêng hoàn toàn → không xung đột.
⭐ **Đây là điểm mạnh lớn nhất của VRF** — cho phép hosting nhiều khách hàng dùng trùng dải IP riêng.
</details>

**5.** Bạn gõ `vrf forwarding KHACH-A` lên interface đang có IP. Chuyện gì xảy ra?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **IP bị XÓA khỏi interface:**
```
% Interface ... IPv4 disabled and address(es) removed due to enabling VRF KHACH-A
```
⭐ **Phải đặt lại IP sau khi gán VRF.**
🔴 ⭐ **Trên production:** nếu bạn đang SSH qua chính interface đó → ⭐ **mất kết nối tới thiết bị**.
⭐ **Quy tắc: VRF trước, IP sau. Và làm qua console/OOB.**
</details>

**6.** GRE overhead bao nhiêu? Tunnel IP MTU mặc định? Vì sao?
<details><summary>Đáp án</summary>

⭐ **Overhead = 24 byte** = 20 (IP header mới) + 4 (GRE header).
⭐ **Tunnel transport MTU = 1500 − 24 = 1476 byte.**
</details>

**7.** Vì sao IPsec thuần không chạy được OSPF, còn GRE over IPsec thì được?
<details><summary>Đáp án</summary>

⭐ OSPF dùng **multicast** (`224.0.0.5` / `224.0.0.6`).
🔴 ⭐ **IPsec thuần (crypto map) không chở được multicast** → OSPF hello không qua được → neighbor không lên.

⭐⭐ **GRE CHỞ ĐƯỢC multicast** (nó bọc mọi thứ vào một gói **unicast** IP). Khi bọc GRE vào IPsec:
⭐ IPsec chỉ thấy một luồng **unicast GRE (protocol 47)** giữa hai IP public → mã hóa bình thường.

⭐ **Câu tóm tắt: "GRE cho routing đi qua, IPsec cho nó đi qua an toàn."**
</details>

**8.** GRE over IPsec dùng transport mode hay tunnel mode? Vì sao?
<details><summary>Đáp án</summary>

⭐⭐ **TRANSPORT mode.**

⭐ Vì **GRE đã thêm một IP header mới rồi** (IP public → IP public). ⭐ Tunnel mode sẽ thêm **thêm một
IP header nữa** → thừa 20 byte vô ích.
⭐ *(Tunnel mode vẫn chạy được, chỉ kém hiệu quả.)*
</details>

**9.** Nêu 5 tham số của IKE Phase 1 phải khớp. Mẹo nhớ?
<details><summary>Đáp án</summary>

⭐ **Hash · Authentication · DH Group · Lifetime · Encryption** → ⭐ **"HAGLE"**.

⭐ *(Lifetime thực tế: bên nào ngắn hơn sẽ được dùng, nên không lệch cũng không chết ngay — nhưng đề vẫn liệt kê nó.)*
</details>

**10.** ESP vs AH: protocol number, cái nào mã hóa, cái nào qua NAT được?
<details><summary>Đáp án</summary>

| | ⭐ **ESP** | **AH** |
|---|---|---|
| IP protocol | ⭐ **50** | **51** |
| Mã hóa | ⭐ **CÓ** | 🔴 **KHÔNG** (chỉ xác thực) |
| Qua NAT | ⭐ Được (với **NAT-T, UDP 4500**) | 🔴 ⭐ **Không** (AH ký cả IP header) |

⭐ **Thực tế gần như luôn dùng ESP.**
</details>

**11.** `show crypto isakmp sa` cho `MM_NO_STATE`. Lỗi ở phase nào, nguyên nhân khả dĩ?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Phase 1 đang HỎNG.**

⭐ **Nguyên nhân:** (a) ⭐ **sai pre-shared key** · (b) ⭐ **lệch ISAKMP policy** (một trong 5 tham số HAGLE) ·
(c) sai địa chỉ peer · (d) UDP 500 bị firewall chặn.

⭐ **Trạng thái tốt là `QM_IDLE`.**
</details>

**12.** `encaps` tăng nhưng `decaps` = 0. Nghĩa là gì?
<details><summary>Đáp án</summary>

⭐⭐ **Mình gửi được, nhưng KHÔNG nhận được gì về.**

⭐ **Nguyên nhân khả dĩ:** (a) ⭐ **firewall chặn chiều về** (ESP protocol 50 / UDP 4500) ·
(b) đầu kia cấu hình sai / chưa có `tunnel protection` · (c) ⭐ **đầu kia thiếu route ngược về mình**.

⭐ ⭐ **Ngược lại (`decaps` tăng, `encaps` = 0)** = traffic của mình không đi vào tunnel → kiểm tra routing/ACL.
</details>

**13.** Tunnel flapping với `%TUN-5-RECURDOWN`. Giải thích và nêu 2 cách sửa.
<details><summary>Đáp án</summary>

⭐⭐ **Recursive routing:** route tới `tunnel destination` được học **qua chính tunnel đó** → vòng lặp
("muốn tới đích phải qua tunnel; muốn qua tunnel phải biết đường tới đích") → router tự tắt tunnel.

⭐ **Hai cách sửa:**
1. ⭐⭐ **Không advertise mạng WAN vào giao thức định tuyến chạy qua tunnel** *(cách đúng nhất)*
2. ⭐ **Static route /32 tới tunnel destination** trỏ ra ISP — AD 1 thắng OSPF AD 110, và /32 thắng longest-prefix

⭐ **Nguyên tắc: underlay và overlay phải là hai miền định tuyến tách biệt.**
</details>

**14.** "Ping OK nhưng web load nửa chừng rồi treo" qua tunnel. Nguyên nhân và 2 lệnh sửa?
<details><summary>Đáp án</summary>

⭐⭐ **Vấn đề MTU/MSS.** ⭐ Gói nhỏ (ping, DNS) qua được; gói lớn (dữ liệu HTTP) vượt MTU và bị drop.

```
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360         ! dòng quan trọng hơn
```
⭐ **Phải đặt trên CẢ HAI đầu.**
⭐ **`adjust-mss` quan trọng hơn** vì nó khiến hai host **tự gửi gói nhỏ ngay từ đầu** → không cần phân mảnh
(phân mảnh tốn CPU và hay bị firewall chặn).
</details>

**15.** LISP: EID và RLOC là gì? ITR và ETR làm gì? Map Server khác Map Resolver ra sao?
<details><summary>Đáp án</summary>

⭐ **EID** (Endpoint Identifier) = ⭐ **"anh LÀ AI"** — danh tính host, không đổi khi di chuyển.
⭐ **RLOC** (Routing Locator) = ⭐ **"anh Ở ĐÂU"** — địa chỉ của router đang phục vụ host đó.

⭐ **ITR** (Ingress) = ⭐ **BỌC** gói (encapsulate) — lối vào.
⭐ **ETR** (Egress) = ⭐ **MỞ** gói (decapsulate) — lối ra. ⭐ Và **ETR đăng ký EID của mình với MS**.
⭐ **xTR** = làm cả hai.

⭐ **Map SERVER** = nơi các ETR ⭐ **ĐĂNG KÝ** ("tôi phụ trách EID này").
⭐ **Map RESOLVER** = nơi ITR ⭐ **HỎI** ("EID này ở RLOC nào?"). ⭐ Thường chạy chung một thiết bị (MS/MR).

⭐ **Port: UDP 4341 (data) · UDP 4342 (control).**
</details>

**16.** Vì sao nói "LISP là mô hình PULL còn BGP là PUSH"?
<details><summary>Đáp án</summary>

⭐ **BGP/IGP = PUSH:** đẩy **toàn bộ** thông tin định tuyến cho mọi router → ai cũng phải giữ bảng route đầy đủ
→ ⭐ bảng route phình to.

⭐⭐ **LISP = PULL:** ITR **không giữ gì cả**, khi cần mới ⭐ **hỏi Map Resolver**, được trả lời thì
⭐ **lưu vào map-cache**. ⭐ **Giống hệt DNS.**

⭐ **Lợi ích:** bảng nhỏ hơn nhiều, và host di chuyển chỉ cần **đăng ký lại với MS** thay vì cập nhật toàn mạng.
</details>

**17.** VXLAN: VNI bao nhiêu bit, bao nhiêu segment, port nào, overhead bao nhiêu?
<details><summary>Đáp án</summary>

⭐⭐ **VNI = 24 bit → ~16.777.216 (≈16 triệu) segment** *(so với VLAN 12 bit = 4094)*
⭐⭐ **Port: UDP 4789**
⭐ **Overhead: 50 byte** (14 Eth ngoài + 20 IP + 8 UDP + 8 VXLAN)
🔴 ⭐ **Hệ quả: underlay phải tăng MTU** — thường bật **jumbo frame 9216**.
</details>

**18.** GRE và VXLAN đều là overlay. Khác nhau ở đâu?
<details><summary>Đáp án</summary>

| | ⭐ **GRE** | ⭐⭐ **VXLAN** |
|---|---|---|
| Bọc cái gì | ⭐ **Gói IP (L3)** | ⭐⭐ **Cả frame Ethernet (L2)** |
| Vận chuyển | IP protocol **47** | ⭐ **UDP 4789** |
| Overhead | ⭐ **24 byte** | ⭐ **50 byte** |
| Số segment | (không áp dụng) | ⭐ **VNI 24 bit = 16 triệu** |
| Dùng ở đâu | ⭐ **WAN site-to-site** | ⭐⭐ **Data center fabric, SD-Access** |
</details>

**19.** Bộ ba công nghệ của SD-Access và vai trò mỗi cái?
<details><summary>Đáp án</summary>

⭐⭐ **LISP = CONTROL plane** ("host này ở đâu")
⭐⭐ **VXLAN = DATA plane** (chở gói qua fabric, mang VNI và SGT)
⭐⭐ **TrustSec/SGT = POLICY plane** ("ai được nói chuyện với ai")

⭐ **Và:** ⭐ **VN (Virtual Network) trong SD-Access chính là VRF.**

⭐ **Câu thần chú:** *"SD-Access = LISP điều khiển + VXLAN dữ liệu + TrustSec chính sách, trên nền VRF."*
</details>

**20.** Bạn dựng GRE over IPsec, `show crypto isakmp sa` = `QM_IDLE`, `encaps`/`decaps` đều tăng, nhưng ping từ LAN A sang LAN B vẫn fail. Kiểm tra gì tiếp?
<details><summary>Đáp án</summary>

⭐ **VPN đã hoạt động** (`QM_IDLE` + cả hai chiều đều tăng) → ⭐ **vấn đề KHÔNG còn ở IPsec.**

⭐ **Kiểm tra tiếp theo thứ tự:**
1. ⭐ `show ip ospf neighbor` — neighbor qua tunnel có **FULL** không?
2. ⭐ `show ip route` — có học được route tới LAN đầu kia không?
3. ⭐⭐ **NAT có "ăn" mất traffic không** — `show ip nat translations`, kiểm tra NAT ACL đã `deny` traffic VPN chưa (§5.5)
4. ⭐ ACL trên interface tunnel hoặc LAN
5. ⭐ Ping có dùng đúng `source` không — ⭐ `ping 10.2.2.1 source 10.1.1.1` *(không có `source` thì router dùng IP của interface đi ra → có thể không khớp route/ACL)*
</details>

---

## 📚 16. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| ⭐ **Hypervisor / VMM** | Phần mềm chạy máy ảo |
| ⭐ **Type 1 / Type 2** | Bare-metal (ESXi, KVM, Proxmox) / Hosted (Workstation, VirtualBox) |
| ⭐ **Guest / Host** | Máy ảo / Máy vật lý |
| ⭐ **vCPU / vRAM / vDisk / vNIC** | CPU/RAM/ổ đĩa/card mạng ảo |
| ⭐ **vSwitch** | Switch phần mềm trong hypervisor — ⭐ **không chạy STP** |
| ⭐ **vSS / vDS** | vSwitch chuẩn (từng host) / phân tán (cả cụm) |
| ⭐ **Port group** | Nhóm cổng ảo có cùng chính sách/VLAN |
| ⭐ **EST / VST / VGT** | Switch vật lý gắn thẻ / vSwitch gắn thẻ / VM tự gắn thẻ |
| **SR-IOV / Passthrough** | VM nói thẳng với phần cứng, bỏ qua vSwitch |
| ⭐ **NFV** | Chạy chức năng mạng dưới dạng VM (CSR1000v…) |
| ⭐ **Live migration / vMotion** | Chuyển VM đang chạy sang host khác |
| ⭐⭐ **VRF** | Virtual Routing and Forwarding — ⭐ nhiều bảng route trên một router |
| ⭐ **VRF-lite** | VRF **không** MPLS, không MP-BGP — ⭐ cái ENCOR hỏi |
| ⭐ **RD** (Route Distinguisher) | Làm route unique — ⭐ chỉ thực sự dùng trong MPLS L3VPN |
| ⭐ **RT** (Route Target) | Điều khiển import/export route — ⭐ chỉ MPLS/MP-BGP |
| ⭐ **Route leaking** | Cố ý cho hai VRF (hoặc VRF↔global) thấy nhau |
| ⭐ **`global` keyword** | Trong static route: trỏ sang bảng định tuyến global |
| ⭐⭐ **GRE** | Generic Routing Encapsulation — ⭐ **24 byte, KHÔNG mã hóa, CHỞ được multicast** |
| ⭐ **Underlay / Overlay** | Mạng vật lý bên dưới / mạng ảo chạy trên nó |
| ⭐⭐ **Recursive routing** | Route tới tunnel destination đi qua chính tunnel → `%TUN-5-RECURDOWN` |
| ⭐ **`ip mtu` / `ip tcp adjust-mss`** | Giới hạn kích thước gói IP / ⭐ sửa MSS trong TCP SYN |
| ⭐ **Keepalive (GRE)** | Kiểm tra đầu kia còn sống — ⭐ GRE mặc định **stateless** |
| ⭐ **mGRE / NHRP / DMVPN** | GRE đa điểm / bảng ánh xạ tunnel↔public / VPN hub-spoke động |
| ⭐⭐ **IPsec** | Bộ giao thức bảo mật: mã hóa + toàn vẹn + xác thực |
| ⭐⭐ **ESP / AH** | ⭐ **Protocol 50, CÓ mã hóa** / **51, chỉ xác thực, không qua NAT** |
| ⭐⭐ **Tunnel mode / Transport mode** | Thêm IP header mới (IPsec thuần) / giữ IP header gốc (⭐ **GRE over IPsec**) |
| ⭐ **IKE Phase 1 / Phase 2** | Dựng kênh đàm phán an toàn / thỏa thuận đường hầm dữ liệu |
| ⭐ **HAGLE** | Mẹo nhớ 5 tham số Phase 1: Hash-Auth-Group-Lifetime-Encryption |
| ⭐⭐ **`QM_IDLE`** | ⭐ **Phase 1 THÀNH CÔNG** |
| 🔴 ⭐ **`MM_NO_STATE`** | ⭐ **Phase 1 ĐANG HỎNG** |
| ⭐ **NAT-T** | NAT Traversal — bọc ESP vào ⭐ **UDP 4500** |
| ⭐ **DPD** (Dead Peer Detection) | Phát hiện đầu kia chết |
| ⭐ **Interesting traffic** | ACL định nghĩa traffic nào được mã hóa — ⭐ **phải đối xứng gương** |
| ⭐ **`encaps` / `decaps`** | Số gói đã bọc / đã mở — ⭐ **cả hai phải tăng** |
| ⭐ **Crypto map / IPsec profile** | Cách cũ (gắn lên interface) / ⭐ **cách mới (gắn lên tunnel)** |
| ⭐⭐ **LISP** | Locator/ID Separation Protocol — tách "AI" khỏi "Ở ĐÂU" |
| ⭐⭐ **EID / RLOC** | Danh tính host / Vị trí (địa chỉ router phục vụ) |
| ⭐⭐ **ITR / ETR / xTR** | ⭐ **Bọc** (vào) / ⭐ **Mở** (ra) / cả hai |
| ⭐⭐ **MS / MR** | Map **Server** (nhận đăng ký) / Map **Resolver** (nhận truy vấn) |
| ⭐ **PITR / PETR** | Proxy — cầu nối LISP ↔ không-LISP |
| ⭐ **Map-cache** | Bộ nhớ đệm EID→RLOC trên ITR |
| ⭐ **PULL vs PUSH** | LISP hỏi khi cần (như DNS) / BGP đẩy hết cho mọi người |
| ⭐⭐ **VXLAN** | MAC-in-UDP — ⭐ **VNI 24 bit, UDP 4789, overhead 50 byte** |
| ⭐⭐ **VNI / VTEP** | Định danh segment (16 triệu) / điểm bọc-mở gói |
| ⭐ **BUM traffic** | Broadcast, Unknown unicast, Multicast |
| ⭐⭐ **EVPN (MP-BGP EVPN)** | Control plane hiện đại cho VXLAN — quảng bá MAC/IP bằng BGP |
| ⭐ **Spine-Leaf** | Kiến trúc DC hai tầng, ECMP mọi đường — ➡️ Module-09 |

---

## 🎯 17. ĐÚC KẾT MODULE-08

**3 điều rút ra:**

1. 🔴 ⭐⭐ **VRF là ảo hóa BẢNG ĐỊNH TUYẾN — và nó có đúng hai cái bẫy, cả hai đều đơn giản đến mức
   người ta không tin:** ⭐ **(1) gán VRF vào interface sẽ XÓA IP** → luôn **VRF trước, IP sau** ·
   ⭐ **(2) quên gõ `vrf` trong `ping`/`show` = đang tra bảng global = không bao giờ tới được** —
   ⭐ **đây là nguyên nhân của 90% ca "VRF không hoạt động"**. Sức mạnh đổi lại là ⭐ **hai VRF dùng
   trùng IP vẫn chạy**, và ⭐ **VRF chính là "VN" của SD-Access**.

2. 🔴 ⭐⭐ **GRE và IPsec bù đắp cho nhau, và ghép lại là câu trả lời cho cả mục 2.2.b:**
   ⭐ **GRE chở được multicast (→ chạy được OSPF/EIGRP) nhưng KHÔNG mã hóa** ·
   ⭐ **IPsec mã hóa nhưng KHÔNG chở được multicast** → ⭐⭐ **GRE over IPsec, transport mode,
   `tunnel protection ipsec profile`**. ⭐ Ba con số/trạng thái phải thuộc: ⭐ **GRE 24 byte → MTU 1476** ·
   ⭐ **`QM_IDLE` = Phase 1 OK, `MM_NO_STATE` = hỏng** · ⭐⭐ **`encaps` VÀ `decaps` phải cùng tăng**.
   Và hai bẫy kinh điển: 🔴 ⭐ **recursive routing** (*"đường tới tunnel destination không được đi qua tunnel"*)
   và 🔴 ⭐ **MTU/MSS** (*"ping OK, web treo nửa chừng"* → `ip mtu 1400` + `ip tcp adjust-mss 1360`).

3. ⭐⭐ **LISP và VXLAN chỉ cần "describe" — nhưng phải describe cho ĐÚNG, vì Module-09 xây trên chúng:**
   ⭐ **LISP tách EID ("anh là ai") khỏi RLOC ("anh ở đâu"), mô hình PULL như DNS**
   (⭐ **ITR bọc · ETR mở · MS nhận đăng ký · MR nhận truy vấn** · ⭐ UDP 4341/4342) ·
   ⭐ **VXLAN là MAC-in-UDP: VNI 24 bit (16 triệu), UDP 4789, overhead 50 byte**, cần underlay đã định tuyến.
   ⭐⭐ Ghép lại: ⭐ **SD-Access = LISP (control) + VXLAN (data) + TrustSec (policy), trên nền VRF.**

🧠 **Một câu để nhớ:** *⭐ **VRF là nhiều công ty thuê chung một tòa nhà** — cùng số phòng cũng không sao,
nhưng ⭐ **phải nói rõ bạn đang hỏi danh bạ của công ty nào**. ⭐ **GRE là phong bì trong suốt, IPsec là
hộp niêm phong không gửi được thư báo chung** — ⭐ **nên phải bỏ phong bì vào hộp**. Còn ⭐ **LISP là DNS
cho vị trí** và ⭐ **VXLAN là gửi nguyên cả căn phòng qua đường bưu điện** — ⭐ **hai thứ này ghép lại
chính là SD-Access ở module sau.***

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ **Type 1 vs Type 2** hypervisor + 2 ví dụ mỗi loại | ☐ |
| 2 | ⭐ VM gồm những thành phần ảo nào · vì sao **không bật port-security max 1** trên port host ảo hóa | ☐ |
| 3 | ⭐⭐ **Vì sao vSwitch không cần STP** | ☐ |
| 4 | ⭐ vSwitch khác switch vật lý ở **3 điểm** nào | ☐ |
| 5 | ⭐⭐ **EST / VST / VGT** — ai gắn thẻ, port switch là gì | ☐ |
| 6 | ⭐ vSS vs vDS · Linux bridge / OVS | ☐ |
| 7 | ⭐⭐ **VRF là gì** — nó ảo hóa cái gì (và **không** ảo hóa cái gì) | ☐ |
| 8 | ⭐⭐ Vì sao **hai VRF dùng trùng IP được** | ☐ |
| 9 | ⭐ **VRF-lite vs VRF trong MPLS L3VPN** — RD/RT dùng ở đâu | ☐ |
| 10 | ⭐ Hai cú pháp VRF (`ip vrf` vs `vrf definition`) khác gì | ☐ |
| 11 | 🔴 ⭐⭐ **BẪY 1**: gán VRF vào interface có IP → chuyện gì xảy ra | ☐ |
| 12 | 🔴 ⭐⭐ **BẪY 2**: vì sao `ping <ip>` không tới host trong VRF | ☐ |
| 13 | ⭐ Cấu hình static / OSPF / BGP **trong VRF** | ☐ |
| 14 | ⭐ **Route leaking** — 3 cách, và từ khóa `global` | ☐ |
| 15 | ⭐ 4 use case thật của VRF (kể cả **Mgmt-vrf** và **VN của SD-Access**) | ☐ |
| 16 | ⭐⭐ **GRE overhead** và tunnel MTU — con số và cách tính | ☐ |
| 17 | 🔴 ⭐⭐ **GRE có mã hóa không? Chở được multicast không?** | ☐ |
| 18 | ⭐ 4 thứ phải khớp giữa hai đầu GRE | ☐ |
| 19 | 🔴 ⭐⭐ **Recursive routing** — cơ chế, thông báo lỗi, **2 cách sửa** | ☐ |
| 20 | ⭐⭐ Vì sao tunnel hiện **up/up giả** · `keepalive` giải quyết gì | ☐ |
| 21 | ⭐⭐ **MTU vs MSS** — 2 lệnh, con số, **vì sao `adjust-mss` quan trọng hơn** | ☐ |
| 22 | ⭐ 3 việc IPsec làm | ☐ |
| 23 | ⭐⭐ **ESP vs AH** — protocol number, mã hóa, NAT | ☐ |
| 24 | ⭐⭐ **Tunnel vs Transport mode** — cái nào cho GRE over IPsec, **vì sao** | ☐ |
| 25 | ⭐⭐ **Phase 1 vs Phase 2** làm gì · **5 tham số HAGLE** | ☐ |
| 26 | ⭐ **IKEv1 vs IKEv2** · **NAT-T** dùng port nào | ☐ |
| 27 | ⭐ ACL interesting traffic phải **đối xứng gương** — nghĩa là gì | ☐ |
| 28 | 🔴 ⭐⭐ **Vì sao IPsec thuần không chạy được OSPF** | ☐ |
| 29 | ⭐⭐ **3 lợi ích của `tunnel protection ipsec profile`** so với crypto map | ☐ |
| 30 | ⭐⭐ **`QM_IDLE` vs `MM_NO_STATE`** nghĩa gì | ☐ |
| 31 | ⭐⭐ **`encaps` tăng / `decaps` = 0** → chẩn đoán gì | ☐ |
| 32 | ⭐⭐ **VPN lên mà không ping được** → nghi ngờ **NAT** như thế nào | ☐ |
| 33 | ⭐ **DMVPN** gồm 3 thành phần nào | ☐ |
| 34 | ⭐⭐ **LISP: EID vs RLOC** — mỗi cái trả lời câu hỏi gì | ☐ |
| 35 | ⭐⭐ **ITR / ETR / xTR / MS / MR** — ai làm gì (⭐ chú ý MS≠MR) | ☐ |
| 36 | ⭐ Luồng **map-request → map-reply → map-cache** | ☐ |
| 37 | ⭐ **Port LISP** 4341 / 4342 | ☐ |
| 38 | ⭐⭐ **PULL vs PUSH** — vì sao nói *"LISP là DNS cho vị trí"* | ☐ |
| 39 | ⭐⭐ **VXLAN: VNI mấy bit, bao nhiêu segment, port nào, overhead bao nhiêu** | ☐ |
| 40 | ⭐ **VTEP** là gì · **underlay vs overlay** | ☐ |
| 41 | ⭐ Vì sao VXLAN **bắt buộc tăng MTU** underlay | ☐ |
| 42 | ⭐ **Flood-and-learn vs EVPN** | ☐ |
| 43 | ⭐⭐ **VLAN vs GRE vs VXLAN** — bảng so sánh | ☐ |
| 44 | ⭐⭐ **Bộ ba SD-Access**: LISP/VXLAN/TrustSec + VRF = VN | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ **Bước 0**: chứng minh ping LAN↔LAN **THẤT BẠI** trước khi có tunnel | ☐ |
| 2 | ⭐⭐ **Bước 1**: tạo 2 VRF với **cùng dải IP `10.10.10.0/24`** — cả hai interface up | ⭐⭐ ☐ |
| 3 | ⭐ Chứng minh 3 bảng route độc lập (`show ip route` vs `show ip route vrf ...`) | ☐ |
| 4 | 🔴 ⭐⭐ **Tái hiện BẪY 2**: ping không có `vrf` → fail · có `vrf` → khác hẳn | ⭐⭐ ☐ |
| 5 | 🔴 ⭐⭐ **Tái hiện BẪY 1**: đặt IP trước → gán VRF → **thấy IP bay mất** | ⭐⭐ ☐ |
| 6 | ⭐ **Bước 2**: GRE tunnel up/up, ping được `172.16.0.2` | ☐ |
| 7 | ⭐⭐ Đọc được **`Tunnel transport MTU 1476`** và giải thích con số | ⭐⭐ ☐ |
| 8 | ⭐⭐ OSPF **FULL qua tunnel** + ping LAN↔LAN **thành công** | ⭐⭐ ☐ |
| 9 | ⭐ Xác nhận **R-ISP hoàn toàn không biết mạng 10.x** | ☐ |
| 10 | 🔴 ⭐⭐ **Bước 3**: tái hiện **`%TUN-5-RECURDOWN`** — thấy tunnel flapping | ⭐⭐ ☐ |
| 11 | ⭐⭐ Chỉ ra **dòng route gây lỗi** (`via Tunnel0`) trong `show ip route <dest>` | ⭐⭐ ☐ |
| 12 | ⭐ Sửa bằng **cả 2 cách** và giải thích vì sao mỗi cách hiệu quả | ☐ |
| 13 | ⭐⭐ **Bước 4**: tự tìm ra ngưỡng **1476** bằng `ping df-bit` (thử 1476 rồi 1477) | ⭐⭐ ☐ |
| 14 | ⭐ Áp `ip mtu 1400` + `ip tcp adjust-mss 1360` cả hai đầu | ☐ |
| 15 | ⭐⭐ **Bước 5**: bật IPsec → `show crypto isakmp sa` = **`QM_IDLE`** | ⭐⭐ ☐ |
| 16 | ⭐⭐ Thấy **`prot 47`** (GRE) trong `show crypto ipsec sa` ident | ⭐⭐ ☐ |
| 17 | ⭐⭐ Ping 20 gói → xác nhận **`encaps` VÀ `decaps` cùng tăng đúng 20** | ⭐⭐ ☐ |
| 18 | ⭐⭐ Xác nhận **OSPF vẫn FULL** sau khi bật IPsec | ⭐⭐ ☐ |
| 19 | 🔴 ⭐⭐ **Bước 6 phá 1**: sai PSK → thấy **`MM_NO_STATE`** | ⭐⭐ ☐ |
| 20 | 🔴 ⭐ **Bước 6 phá 2**: lệch transform-set → Phase 1 OK nhưng **không có SA Phase 2** | ⭐ ☐ |
| 21 | ⭐ **Bước 6 phá 3**: gỡ `tunnel protection` một đầu → traffic tắc | ☐ |
| 22 | 🚀 ⭐ **§11.1**: phân biệt được `tunnel vrf` và `vrf forwarding` trên Tunnel | 🚀 ☐ |
| 23 | 🚀 **§11.2**: route leaking VRF↔global **cả hai chiều** | 🚀 ☐ |
| 24 | 🚀 **§11.3**: OSPF chạy trong VRF | 🚀 ☐ |
| 25 | 🚀 ⭐⭐ **§11.4**: chứng minh **IPsec thuần KHÔNG lên được OSPF neighbor** | 🚀 ⭐⭐ ☐ |
| 26 | 🚀 ⭐⭐ **§11.5**: Wireshark — **thấy rõ IP nội bộ khi chỉ có GRE**, chỉ thấy **ESP** sau khi bật IPsec | 🚀 ⭐⭐ ☐ |
| 27 | ⭐ Ghi ít nhất **2 mục** vào `SO-TAY-LOI.md` từ module này | ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 2, 4, 5** (hai bẫy VRF), **mục 8, 10, 11**
> (OSPF qua tunnel + recursive routing), **mục 13** (tự tìm ra 1476), và **mục 15–19** (IPsec + `MM_NO_STATE`).
> ⭐ Bỏ §11 nếu bám tiến độ — ⭐ **nhưng mục 26 (Wireshark) rất đáng làm, chỉ mất 10 phút và nhớ cả đời.**
>
> ⚠️ ⭐ **Chưa tick được ≥ 38/44 Phần A và ≥ 15/27 Phần B thì chưa nên sang Module-09** —
> ⭐ **Module-09 (SD-Access, SD-WAN) xây TRỰC TIẾP trên LISP, VXLAN và VRF của module này.**

---

## 🔗 18. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Virtualization*, *Foundational Network Programmability* (phần overlay), *Tunneling* |
| **Cisco doc** ⭐⭐ | ***Configuring VRF-lite*** (IOS-XE Routing Configuration Guide) — ⭐ tài liệu gốc cho §3 |
| **Cisco doc** ⭐ | *VRF-Aware Services* — danh sách dịch vụ hỗ trợ VRF (ping/ssh/tftp/snmp…) |
| **Cisco doc** ⭐⭐ | ***Configuring a GRE Tunnel over IPsec with OSPF*** — ⭐ **tài liệu quan trọng nhất của §6**, có cả cấu hình đầy đủ hai đầu |
| **Cisco doc** ⭐⭐ | *Troubleshooting IPsec VPN* / *IPsec Troubleshooting: Understanding and Using debug Commands* — ⭐ giải thích `QM_IDLE`, `MM_NO_STATE` |
| **Cisco doc** ⭐ | *Resolve IPsec Error "Recursive Routing"* · *Tunnel MTU and TCP MSS Adjust* |
| **Cisco doc** ⭐ | *IPsec Anti-Replay / NAT Traversal (NAT-T)* · *IKEv2 Configuration Guide* |
| **Cisco doc** ⭐⭐ | ***LISP Overview*** và *LISP Configuration Guide* — ⭐ có sơ đồ luồng map-request rất rõ |
| **Cisco doc** ⭐⭐ | ***VXLAN Overview*** / *VXLAN EVPN Configuration Guide* — ⭐ đọc phần Overview là đủ cho ENCOR |
| **Cisco doc** ⭐ | *Cisco Nexus/Catalyst VXLAN BGP EVPN Design Guide* — ⭐ chỉ đọc chương giới thiệu |
| **Cisco CVD** ⭐⭐ | ***SD-Access Solution Design Guide*** — ⭐ **đọc trước 10 trang đầu**, nó nối §7+§8 vào Module-09 |
| **RFC 2784** | GRE |
| **RFC 4301 / 4303** | IPsec Architecture / ESP |
| **RFC 7348** | ⭐ **VXLAN** |
| **RFC 6830 / 9300** | ⭐ **LISP** |
| **VMware doc** ⭐ | *vSphere Networking Guide* — chương **VLAN Configuration (EST/VST/VGT)** ⭐ giải thích rõ nhất §2.3 |
| **Proxmox doc** ⭐ | *Network Configuration* — ⭐ **đối chiếu trực tiếp với kinh nghiệm của bạn**: Linux bridge, VLAN-aware bridge, OVS |
| **Video** ⭐ | CBT Nuggets ENCOR — module Virtualization & Tunneling · **Keith Barker**: search `Keith Barker GRE over IPsec`, `Keith Barker VRF lite` |
| **NetworkLessons** ⭐⭐ | ⭐ Loạt bài **rất hay** cho module này: *VRF Lite*, *GRE Tunnel*, *IPsec VPN*, *GRE over IPsec*, *LISP*, *VXLAN* — nhiều bài free |
| **Wireshark** ⭐⭐ | Filter: `gre` · `esp` · `isakmp` · `vxlan` · `lisp`. ⭐ **Bắt gói trước/sau khi bật IPsec là bài học đắt giá nhất** (§11.5) |
| **Forum** | https://community.cisco.com — search: `tunnel recursive routing`, `mm_no_state ipsec`, `encaps but no decaps`, `vrf ping not working`, `gre tunnel mtu web pages not loading`, `ospf over ipsec not working` |

---

**➡️ Tiếp theo:** Module-09 — Architecture & QoS
*(2-tier/3-tier · Spine-Leaf · **SD-Access** (dùng LISP+VXLAN+VRF của module này!) · **SD-WAN** · **QoS** · Wireless design — **Tuần 15**)*

> ⭐ **Module-09 là module "tỉ lệ điểm/công sức tốt nhất" của cả kỳ thi** — Architecture chiếm **15% đề**
> nhưng ⭐ **gần như chỉ hỏi khái niệm, rất ít cấu hình**. ⭐ Cộng thêm QoS (thuộc Domain 1.6) thì đây là
> module **học nhớ**, không phải module **học lab**.
>
> ⭐ **Và bạn đã có sẵn nền:** ⭐ **LISP + VXLAN + VRF ở Module-08 chính là ruột của SD-Access.**
