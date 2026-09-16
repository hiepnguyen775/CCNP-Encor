# Module-06A — FHRP: HSRP, VRRP, GLBP & Object Tracking

> 🧭 **Lộ trình:** [Module-05B](Module-05B-BGP-Path-Selection-va-Filtering.md) → `[Bạn đang ở đây] Module-06A` → [Module-06B](Module-06B-NAT-NTP-Multicast.md) → Module-07 (Wireless)
>
> 📊 **Blueprint:**
> · **3.4.c — Configure first hop redundancy protocols, such as HSRP and VRRP** (Infrastructure 30%)
> · **1.1.b — High availability techniques such as redundancy, FHRP, and SSO** (Architecture 15%)
>
> ⏱️ **Tuần 11 (nửa đầu)** · 5 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Máy tính chỉ khai được MỘT default gateway. Vậy nếu router gateway đó chết thì sao?"**

## Ý tưởng, trong một hình

```
   VẤN ĐỀ:  PC khai gateway = 10.10.10.1  (IP thật của Router-A)
            Router-A chết  →  ⭐ PC mất mạng hoàn toàn
            Có Router-B dự phòng cũng vô ích — PC không biết nó tồn tại

   GIẢI PHÁP FHRP:  tạo ra một GATEWAY ẢO

        Router-A (Active)          Router-B (Standby)
         IP thật 10.10.10.2         IP thật 10.10.10.3
              └──────────┬──────────────┘
                         │
              ⭐ IP ẢO   10.10.10.1   ← PC khai cái này
              ⭐ MAC ẢO  0000.0c07.acXX

   Router-A chết → Router-B nhận luôn IP ảo VÀ MAC ảo
                 → ⭐ PC KHÔNG HỀ BIẾT có chuyện gì xảy ra
                 → không phải ARP lại, không phải đổi cấu hình
```

## Bảng so sánh 3 FHRP — bảng đề hỏi trực tiếp

| | **HSRP** | **VRRP** | **GLBP** |
|---|---|---|---|
| Chuẩn | ⭐ **Cisco độc quyền** | ⭐ **Chuẩn mở (RFC)** | ⭐ Cisco độc quyền |
| Vai trò | Active / Standby | Master / Backup | AVG / AVF |
| ⭐ **Preempt mặc định** | 🔴 ⭐⭐ **TẮT** | ⭐⭐ **BẬT** | Tắt |
| Priority mặc định | 100 | 100 | 100 |
| ⭐ **Load balancing** | ❌ *(phải chia thủ công theo VLAN)* | ❌ | ⭐ **CÓ — tự động** |
| Địa chỉ | 224.0.0.2 *(v1)* · 224.0.0.102 *(v2)* | 224.0.0.18 | 224.0.0.102 |
| Cấp độ ENCOR | ⭐ **Configure** | ⭐ **Configure** | 🟡 Chỉ *describe* |

## 6 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **FHRP làm gì** | Tạo **IP ảo + MAC ảo** để client không bao giờ biết router nào đang phục vụ |
| 2 | 🔴 ⭐⭐ **Bẫy số 1** | **HSRP TẮT preempt mặc định** → đặt priority cao mà quên `preempt` là **vô tác dụng** |
| 3 | **VRRP ngược lại** | VRRP **BẬT** preempt mặc định |
| 4 | ⭐⭐ **Lỗ hổng của FHRP** | Nó chỉ biết *"router kia còn sống không"*, **KHÔNG biết** *"đường ra Internet còn thông không"* |
| 5 | ⭐⭐ **Cách vá** | **Object tracking + IP SLA** → đường chết thì **tự hạ priority** → router kia giành Active |
| 6 | ⭐ **`preempt delay minimum`** | Router vừa boot chưa có bảng route đầy đủ → **đừng giành Active ngay** |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì / làm gì |
|---|---|
| `show standby brief` | ⭐ HSRP: ai Active, priority bao nhiêu, VIP là gì |
| `show standby` | Chi tiết: timer, preempt bật chưa, track gì |
| `show vrrp brief` | VRRP: ai Master |
| `show glbp brief` | GLBP: AVG là ai, các AVF |
| ⭐ `show track` | Track Up/Down + **ai đang dùng nó** |
| `show ip sla statistics` | Phép đo đứng sau track |
| `debug standby terse` | Theo dõi chuyển trạng thái *(chỉ lab)* |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | 5 ví von, đọc **một mạch** | 30 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | 7 mục. ⭐⭐ **Then chốt: §3.2 (bảng so sánh), §3.6 (tracking)** | 2 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB 06A](Module-06A-LAB.md) — 6 bước | 7 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | Đặt FHRP ở đâu, ghép với gì. **Vẽ lại trên giấy** | 30 phút |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra | — |

> ⭐ **Nếu chỉ có thời gian cho một thứ:** làm **[LAB bước 3 — Object Tracking + IP SLA](Module-06A-LAB.md)**.
>
> Nó vá đúng lỗ hổng chết người của FHRP, và dùng lại kỹ thuật bạn đã học ở
> [Module-03](Module-03-IP-Routing-Nen-tang.md) — lần này gắn vào HSRP thay vì static route.

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

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> FHRP là chủ đề **dễ hiểu nhất khối routing** — năm ví von dưới đây gần như đủ để bạn
> nắm bản chất trước khi mở bảng so sánh.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 FHRP như số điện thoại tổng đài

PC được cho **một số hotline: `10.1.1.1`** (Virtual IP).

- **Không có FHRP:** hotline là số **di động cá nhân** của anh R1. Anh R1 nghỉ → không ai nghe.
  Muốn sửa → gọi từng khách hàng đổi số. Bất khả thi.
- ⭐ **Có FHRP:** hotline là **số tổng đài**. Anh R1 nghỉ → anh R2 nhấc máy.
  ⭐ **Khách hàng không biết gì cả**, vẫn gọi số cũ.

Và **Virtual MAC** = ⭐ **cái máy điện thoại vật lý** ở tổng đài. Đổi người nghe nhưng
**không đổi máy** → khách không phải quay số lại (không phải ARP lại).

🧠 **Một câu để nhớ:** *FHRP không làm router dự phòng nhanh hơn — nó làm **PC không cần biết**
có bao nhiêu router. Toàn bộ giá trị nằm ở chỗ đó.*

### 2.2 Preempt — "chiếm lại ghế" và vì sao HSRP tắt mặc định

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

### 2.3 ⭐ `preempt delay minimum` — bài học từ sự cố thật

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

### 2.4 GLBP như quầy thu ngân có người điều phối

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

### 2.5 Vì sao FHRP cần object tracking

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
## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ lắp **cơ chế thật, con số và câu lệnh** vào hình dung bạn vừa có.
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 số điện thoại tổng đài | → | **§3.1 FHRP giải quyết gì · §3.2 Bảng so sánh 3 FHRP** ⭐⭐ |
> | §2.2 chiếm lại ghế · §2.3 `preempt delay` | → | **§3.3 HSRP · §3.4 VRRP** |
> | §2.4 quầy thu ngân có điều phối | → | **§3.5 GLBP** |
> | §2.5 vì sao cần tracking | → | **§3.6 Object Tracking + FHRP** ⭐⭐ |
>
> ⚠️ **Hai mục quan trọng nhất: §3.2** (bảng so sánh 3 FHRP — đề hỏi trực tiếp)
> và **§3.6** (object tracking — phần thực chiến nhất).

### 3.1 FHRP giải quyết vấn đề gì

```
   KHÔNG CÓ FHRP                          CÓ FHRP
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
      │   gateway trên │                      PC KHÔNG BIẾT GÌ
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

### 3.2 ⭐⭐ BẢNG SO SÁNH 3 FHRP — bảng quan trọng nhất module

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

### 3.3 ⭐ HSRP chi tiết

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
 standby version 2                       ! phải đặt TRƯỚC khi cấu hình group > 255
 standby 10 ip 10.1.10.1
```
⚠️ **Đổi version = HSRP reset** → có ngắt ngắn. Và ⭐ **cả 2 router phải cùng version**.

#### Cấu hình HSRP đầy đủ

```
interface Vlan10
 ip address 10.1.10.2 255.255.255.0
 !
 standby version 2                                    ! nên dùng v2
 standby 10 ip 10.1.10.1                              ! Virtual IP
 standby 10 priority 110                              ! CAO thắng (default 100)
 standby 10 preempt                                   ! PHẢI GÕ — mặc định TẮT!
 standby 10 preempt delay minimum 60                  ! chờ 60s sau reboot mới preempt
 standby 10 timers 1 3                                ! hello 1s / hold 3s
 standby 10 timers msec 200 msec 750                  ! hoặc millisecond
 standby 10 authentication md5 key-string MyHsrpKey   ! MD5
 standby 10 name VLAN10-GW                            ! tên (tiện quản lý)
 standby 10 track 1 decrement 30                      ! object tracking
```

⭐ **`preempt delay minimum`** — cực quan trọng ở production:
sau khi router reboot, interface lên **trước khi** routing protocol hội tụ.
Nếu preempt ngay → nó thành Active mà **chưa có route** → ⭐ **black hole**.
`preempt delay minimum 60` cho nó 60 giây để OSPF/BGP hội tụ trước.

**Kiểm tra:**
```
show standby                              ! chi tiết mọi group
show standby brief                        ! bảng gọn — dùng nhiều nhất
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
  Active virtual MAC address is 0000.0c9f.f00a           ← vMAC (HSRPv2, group 10)
    Local virtual MAC address is 0000.0c9f.f00a (v2 default)
  Hello time 3 sec, hold time 10 sec
    Next hello sent in 1.024 secs
  Authentication MD5, key-string
  Preemption enabled, delay min 60 secs
  Active router is local
  Standby router is 10.1.10.3, priority 100 (expires in 9.056 sec)
  Priority 110 (configured 110)
    Track object 1 state Up decrement 30                 ← tracking
  Group name is "VLAN10-GW" (cfgd)
```

---

### 3.4 ⭐ VRRP chi tiết

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
 vrrp 10 ip 10.1.10.1                                  ! Virtual IP
 vrrp 10 priority 110
 vrrp 10 preempt                                        ! (mặc định đã BẬT)
 vrrp 10 timers advertise 1
 vrrp 10 authentication text MyVrrpKey
 vrrp 10 track 1 decrement 30
 vrrp 10 description VLAN10-GW

! ═══ Cú pháp MỚI (VRRPv3, hỗ trợ IPv6) ═══
fhrp version vrrp v3                                    ! global
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
show vrrp brief                           ! bảng gọn
show vrrp interface Vlan10
show fhrp verbose                          ! mọi FHRP trên router
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

### 3.5 🟡 GLBP — load balancing tự động

⭐ **Điểm khác biệt duy nhất đáng nhớ:** HSRP/VRRP chỉ có **1 router forward**.
GLBP cho ⭐ **tối đa 4 router cùng forward** trong **cùng một group**.

#### Cơ chế — AVG và AVF

```
                    AVG (Active Virtual Gateway) — 1 per group
                    Nhiệm vụ: TRẢ LỜI ARP cho Virtual IP
                              nhưng trả về vMAC KHÁC NHAU cho từng host
                              
   PC1 ARP "10.1.1.1?" ──▶ AVG trả: vMAC1 (0007.B400.0A01) ──▶ PC1 dùng R1
   PC2 ARP "10.1.1.1?" ──▶ AVG trả: vMAC2 (0007.B400.0A02) ──▶ PC2 dùng R2
   PC3 ARP "10.1.1.1?" ──▶ AVG trả: vMAC1 ──▶ PC3 dùng R1
   PC4 ARP "10.1.1.1?" ──▶ AVG trả: vMAC2 ──▶ PC4 dùng R2
   
   AVF (Active Virtual Forwarder) — tối đa 4/group, mỗi cái 1 vMAC
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
 glbp 10 load-balancing round-robin          ! chỉ AVG quyết định
 glbp 10 weighting 100 lower 80 upper 90     ! weight + ngưỡng cho AVF
 glbp 10 weighting track 1 decrement 30
 glbp 10 authentication md5 key-string MyGlbpKey
```

**Kiểm tra:**
```
show glbp
show glbp brief                            ! thấy cả AVG và từng AVF
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

### 3.6 ⭐⭐ Object Tracking + FHRP — phần đề rất hay hỏi

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
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1    ! source-interface BẮT BUỘC
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now              ! KHÔNG ĐƯỢC QUÊN

! ═══ 2. Track object ═══
track 1 ip sla 1 reachability
 delay down 3 up 10                                        ! chống flapping

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
 standby 10 track 10 decrement 30            ! track fail → priority 110-30 = 80
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
decrement = 30  → 110-30 =  80 < 100 → ✅ Failover (có biên an toàn)
```

⭐ **Công thức:** `decrement > (priority_của_tôi − priority_của_router_kia)`.
Nên để **dư biên** — trong ví dụ trên, chọn 20–30 thay vì đúng 11.

**Kiểm tra:**
```
show track                                  ! mọi track object
show track 1
show ip sla statistics 1                    ! return code, successes
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
    HSRP Vlan10 10                           ← xác nhận HSRP đang dùng track này
```

---

### 3.7 🟡 HA khác — SSO, NSF, StackWise (mục 1.1.b, describe)

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

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết.

> ### 👉 **[LAB 06A — Tuần 11: HSRP · VRRP · GLBP · Tracking](Module-06A-LAB.md)**

| Bước | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|
| 1 | HSRP cơ bản + ⭐ **bẫy preempt** | §2.1 số điện thoại tổng đài · §2.2 chiếm lại ghế | §3.3 |
| 2 | ⭐ Đo downtime khi failover | §2.3 `preempt delay` | §3.3 |
| 3 | ⭐⭐ **Object Tracking + IP SLA** | §2.5 vì sao FHRP cần tracking | §3.6 |
| 4 | VRRP (preempt **BẬT** mặc định) | §2.2 | §3.4 |
| 5 | 🟡 GLBP (tùy chọn) | §2.4 quầy thu ngân có điều phối | §3.5 |
| 6 | 🚀 Authentication FHRP | — | §3.3 · §3.4 |

> ⚠️ **Bước 3 là phần giá trị nhất của Module-06A**, và nó nối thẳng về
> [Module-03](Module-03-IP-Routing-Nen-tang.md) — bạn dùng lại đúng kỹ thuật **IP SLA + track**
> đã học ở đó, nhưng lần này gắn vào HSRP thay vì static route.
>
> Bạn sẽ tạo ra tình huống ⭐ **"gateway còn sống nhưng đường ra Internet đã chết"** —
> và thấy HSRP **không hề biết** cho tới khi bạn thêm tracking.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học 3 giao thức FHRP + object tracking. Phần này trả lời:
> **đặt FHRP ở đâu trong campus, và ghép với cái gì để nó thực sự đáng tin?**

### 4.1 Bản đồ: FHRP nằm ở đâu, và nó KHÔNG bảo vệ được gì

```
                        INTERNET
                            │
                   ┌────────┴────────┐
                   │   Router biên   │   🔴 FHRP KHÔNG biết đoạn này chết
                   └────────┬────────┘      → phải dùng ④ TRACKING
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
   ┌──────┴───────┐                  ┌────────┴──────┐
   │   Dist-1     │◄──── ③ ─────────►│    Dist-2     │
   │              │   (2 con phải     │               │
   │ ① ACTIVE     │    nói chuyện     │  ② STANDBY    │
   │   priority 110│    được với nhau)│    priority 100│
   │   preempt ✅  │                  │               │
   └──────┬───────┘                  └────────┬──────┘
          │        VLAN 10 — gateway ảo       │
          │        10.10.10.1 (VIP)           │
          └────────────────┬──────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Switch L2  │
                    └──────┬──────┘
                           │
                    [PC] gateway = 10.10.10.1
                         ⭐ PC không bao giờ biết có 2 router
```

### 4.2 Năm quyết định — và sai thì hỏng thế nào

| # | Quyết định | Vì sao | 🔴 Sai thì hỏng thế nào |
|:---:|---|---|---|
| ① | **Đặt FHRP ở Distribution** | Đó là nơi có **SVI / gateway** của VLAN | Đặt ở access → access không route được, vô nghĩa |
| ② | **Router Active nên trùng với Root Bridge STP** | Nếu không, traffic đi **zigzag**: lên Dist-2 (theo STP) rồi chạy ngang sang Dist-1 (theo HSRP) | ⭐ **Lãng phí link ngang, tăng độ trễ.** Lỗi thiết kế rất phổ biến |
| ③ | 🔴 ⭐⭐ **BẬT `preempt` trên HSRP** | HSRP **mặc định TẮT preempt** | Router chính sống lại nhưng **không giành lại Active** → bạn tưởng đang chạy chính mà thực ra đang chạy dự phòng |
| ④ | ⭐⭐ **Ghép với object tracking** | FHRP chỉ biết *"router kia còn sống không"* | Đường ra Internet chết mà gateway vẫn sống → ⭐ **HSRP không chuyển, client mất mạng mà FHRP báo "bình thường"** |
| ⑤ | **`preempt delay minimum`** | Router vừa boot xong chưa có bảng route đầy đủ | Giành Active ngay khi vừa lên → ⭐ **hút traffic vào một router chưa biết đường đi** → mất mạng vài chục giây |

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| 🔴 ⭐⭐ **HSRP mặc định TẮT preempt, VRRP mặc định BẬT** | Đây là khác biệt bị hỏi nhiều nhất và cũng gây sự cố thật nhiều nhất. Đặt priority 110 cho HSRP mà quên `preempt` → **không có tác dụng gì** |
| ⭐⭐ **FHRP chỉ bảo vệ chặng ĐẦU TIÊN** | Tên nó là *First Hop* Redundancy. Nó **không biết gì** về đoạn từ gateway ra Internet. ⭐ **Object tracking là thứ duy nhất vá được lỗ hổng này** |
| ⭐ **`preempt delay minimum` sinh ra từ sự cố thật** | Router reboot → HSRP lên trong **vài giây**, nhưng OSPF/BGP cần **vài chục giây** để hội tụ. Không có delay → router giành Active khi **chưa có route** → traffic vào rồi bị bỏ |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| Object tracking + IP SLA | Đo jitter/MOS · SLA cho VoIP | **Module-11 §7** |
| FHRP (redundancy gateway) | HA toàn diện: SSO/NSF/GR · StackWise/VSS/vPC | **Module-09 §3** |
| Redundancy ở Distribution | Thiết kế campus 2-tier/3-tier | **Module-09 §2** |
| Gateway ảo dùng chung | ⭐ **Anycast Gateway của SD-Access** — mọi edge node cùng một IP | **Module-09 §7.4** |
| Authentication FHRP | AAA · 802.1X · MACsec | **Module-10** |

> ⭐ **Một liên hệ đáng nhớ:** SD-Access **bỏ hẳn FHRP** — vì **anycast gateway** cho phép
> *mọi* switch cùng làm gateway với **cùng một IP và MAC**. Không còn Active/Standby nữa.
> Bạn sẽ thấy điều đó ở Module-09.

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Đánh dấu ① → ⑤
> 3. Trả lời: *"Router Active vẫn sống, HSRP báo bình thường, nhưng người dùng mất Internet. Chuyện gì xảy ra và sửa thế nào?"*

<details>
<summary>Đáp án câu 3</summary>

⭐ **Đường từ router Active ra Internet đã chết** — nhưng bản thân router vẫn sống, nên
HSRP hoàn toàn không biết. Nó vẫn giữ vai Active và **vẫn hút toàn bộ traffic của client
vào một router không có đường ra**.

⭐ **Sửa bằng object tracking:**
1. Tạo phép đo: `ip sla` ping tới một địa chỉ ngoài Internet
2. `track 1 ip sla 10 reachability`
3. Trên interface HSRP: `standby 10 track 1 decrement 20`

Khi IP SLA thất bại → track Down → **HSRP tự hạ priority 20 điểm** → router kia
(có preempt) **giành Active** → traffic chuyển sang đường còn sống.

⭐ **Đây chính là LAB bước 3**, và là lý do object tracking tồn tại.

</details>

---

## 💡 4.6 Thực chiến đi làm

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

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) — quy trình 5 bước cho FHRP |
> | Quên lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ lạ | **Thuật ngữ** (§9) |
> | Tự chấm | **Đúc kết** (§10) |

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
show standby brief                          ! LỆNH ĐẦU TIÊN — chú ý cột P (preempt)
show standby                                ! chi tiết mọi group
show standby <interface> <group>            ! chi tiết 1 group: vMAC, timer, auth, track
show standby all
show standby internal
debug standby                               ! ⚠️ chỉ lab
debug standby events                        ! ⚠️
debug standby errors                        ! hữu ích cho auth mismatch

! ═══ VRRP ═══
show vrrp brief                             ! chú ý cột Pre (Y = preempt)
show vrrp
show vrrp interface <if>
show fhrp verbose                           ! MỌI FHRP trên router
debug vrrp all                              ! ⚠️

! ═══ GLBP ═══
show glbp brief                             ! thấy cả AVG (Fwd -) và AVF (Fwd 1,2..)
show glbp
show glbp <if> <group>

! ═══ TRACKING + IP SLA ═══
show track                                  ! mọi object + "Tracked by"
show track <n>
show track brief
show ip sla summary                         ! 
show ip sla statistics <n>                  ! return code, successes, time to live
show ip sla configuration <n>
debug track                                 ! ⚠️
debug ip sla trace <n>                      ! ⚠️

! ═══ NỀN TẢNG (đừng bỏ) ═══
show ip interface brief                     ! interface up?
show interfaces trunk                       ! VLAN có được trunk? (trên switch)
show vlan brief
show arp                                    ! vMAC có đúng?
show mac address-table | include 0000.0c    ! vMAC học ở port nào (MAC flapping?)
show logging | include HSRP|VRRP|GLBP|TRACK|BADAUTH
show ip route 0.0.0.0                       ! router Active có đường ra?
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
   → Đọc: Grp · Pri · CỘT P (preempt) · State · Active/Standby · Virtual IP
        ↓
1. STATE CÓ ĐÚNG NHƯ THIẾT KẾ?
   ├─ Router priority cao mà là Standby  → CỘT P TRỐNG? → thiếu `preempt`
   ├─ CẢ 2 đều Active                    → auth mismatch / L2 / trunk / encapsulation
   ├─ Standby = "unknown"                → không thấy neighbor → L2 / VLAN / ACL
   └─ State đúng → sang bước 2
        ↓
2. CÓ TRACKING CHƯA?
   show standby <if> <grp> | include Track
   ├─ KHÔNG có dòng Track → HA GIẢ → cấu hình IP SLA + track
   └─ Có → sang bước 3
        ↓
3. TRACKING CÓ HOẠT ĐỘNG?
   show track
   ├─ Không có "Tracked by: HSRP..."     → chưa gắn vào FHRP
   ├─ Reachability Down ngay từ đầu       → quên `ip sla schedule`?
   │                                         show ip sla statistics <n> → time to live = 0?
   ├─ Luôn Up dù uplink chết              → thiếu `source-interface`
   └─ Up/Down đúng → sang bước 4
        ↓
4. TRACK DOWN MÀ KHÔNG FAILOVER?
   show standby brief   (xem Pri SAU KHI giảm)
   ├─ Pri sau giảm vẫn > router kia       → decrement quá nhỏ
   └─ Pri sau giảm < router kia           → ROUTER KIA CÓ `preempt` KHÔNG?
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
 standby 10 preempt delay minimum 60          ! nên có luôn
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

! Trên router B
show standby brief
! Gi0/0.10    10   100   Standby ...               ← CỘT P TRỐNG!
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
! (TRỐNG — không có dòng Track)                      ← ĐÂY LÀ VẤN ĐỀ
show ip route 0.0.0.0
! % Network not in table                              ← router Active không có đường ra
```

⭐ **Sửa — 3 bước (kết hợp Module-03 §2.4):**

```
! 1. IP SLA — ping THẬT một đích Internet qua ĐÚNG uplink
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1     ! source-interface BẮT BUỘC
 frequency 5
 timeout 2000
ip sla schedule 1 life forever start-time now               ! ĐỪNG QUÊN

! 2. Track object — kết hợp nhiều điều kiện
track 1 ip sla 1 reachability
 delay down 3 up 10
track 2 interface GigabitEthernet0/1 line-protocol
track 3 ip route 0.0.0.0 0.0.0.0 reachability
!
track 10 list boolean and                                   ! AND cả 3
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
show track 10                    ! "Tracked by: HSRP ..." phải có
show ip sla statistics 1         ! return code OK, time to live Forever
show standby brief               ! cột P có trên CẢ 2 router
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
 standby 10 preempt delay minimum 90        ! dài hơn thời gian hội tụ IGP/BGP
```

⭐ **Chọn giá trị bao nhiêu:** phải **dài hơn thời gian hội tụ routing** của mạng bạn.
- OSPF nội bộ: 30–60 s là đủ
- ⭐ **BGP với ISP (nhận full table):** cần **120–300 s** (nhận 900k prefix mất vài phút)

**Các biến thể:**
```
standby 10 preempt delay minimum 90        ! chờ 90 s sau khi interface up
standby 10 preempt delay reload 120        ! chờ 120 s sau khi ROUTER RELOAD
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
!  10   0000.0c9f.f00a   DYNAMIC   Gi0/1        ← VÀ ở port R2 → FLAPPING
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
 standby 10 priority 110              ! Active VLAN 10
 standby 10 preempt
interface Gi0/0.20
 standby 20 priority 90               ! Standby VLAN 20
 standby 20 preempt

! ═══ R2 ═══
interface Gi0/0.10
 standby 10 priority 90               ! Standby VLAN 10
 standby 10 preempt
interface Gi0/0.20
 standby 20 priority 110              ! Active VLAN 20
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
   ═══ THIẾT KẾ CŨ ═══              ═══ STACKWISE VIRTUAL ═══

   [SW-A]  [SW-B]                    ╔═══ 1 SWITCH LOGIC ═══╗
     │  ╳    │   ← STP block         ║  [SW-A] ═══ [SW-B]   ║
     └───┬───┘                       ╚═══════╦══════════════╝
     [Access]                                ║ MEC (không block)
   + cần HSRP giữa SW-A/SW-B              [Access]
                                        không cần HSRP
                                        không cần STP block
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
