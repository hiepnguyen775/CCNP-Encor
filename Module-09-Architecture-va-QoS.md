# Module-09 — Architecture & QoS

> 🧭 **Lộ trình:** [Module-08](Module-08-Virtualization-va-Overlay.md) → `[Bạn đang ở đây] Module-09` → Module-10 (Security)
>
> 📊 **Blueprint — Domain 1.0 Architecture (15% đề) — gần như TRỌN VẸN một domain:**
> · **1.1 — Explain the different design principles used in an enterprise network** (1.1.a 2-tier/3-tier/fabric, capacity planning · 1.1.b HA: redundancy, FHRP, SSO)
> · **1.2 — Analyze design principles of a WLAN deployment** (1.2.a deployment models · 1.2.b location services · 1.2.c client density)
> · **1.3 — Differentiate between on-premises and cloud infrastructure deployments**
> · ⭐⭐ **1.4 — Explain the working principles of the Cisco SD-WAN solution**
> · ⭐⭐ **1.5 — Explain the working principles of the Cisco SD-Access solution**
> · ⭐⭐ **1.6 — Describe concepts of wired and wireless QoS**
> · *(1.7 hardware vs software switching → đã học ở [Module-01](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md))*
>
> ⏱️ **Tuần 15** · 10 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **Xếp thiết bị mạng thế nào cho một doanh nghiệp — và vì sao xếp kiểu này
> chứ không phải kiểu kia?**

## ⭐ Module có tỉ lệ điểm/công sức TỐT NHẤT cả kỳ thi

```
   Domain 1.0 Architecture = 15% đề

   Toàn bộ dùng từ:  Explain · Analyze · Differentiate · Describe
   KHÔNG có một chữ "Configure" nào.

   ┌─────────────────────────────────────────────────────┐
   │  Infrastructure (30%)  →  ~4-5 giờ học cho mỗi 1%   │
   │  Architecture   (15%)  →  ⭐ ~0.7 giờ cho mỗi 1%     │
   └─────────────────────────────────────────────────────┘

   Nghĩa là: 15% số điểm lấy được CHỈ BẰNG HỌC BẢNG.
   Không cần dựng lab SD-WAN 20 GB RAM.
```

🔴 **Nhưng có bẫy ngược:** vì dễ nên nhiều người học qua loa, rồi tắc ở câu
*vBond làm gì* / *Control Plane Node chạy giao thức nào*.
⭐ **Hai bảng thành phần SD-WAN và SD-Access phải thuộc như bảng cửu chương.**

## Ba mục chiếm 2/3 số câu

| Mục | Phải thuộc cái gì |
|---|---|
| ⭐⭐ **§7 SD-WAN** | **vManage** (quản lý) · **vSmart** (OMP, control — 🔴 **KHÔNG chở data**) · **vBond** (🔴 **thành phần DUY NHẤT cần IP public**) · **cEdge** (data qua IPsec) |
| ⭐⭐ **§8 SD-Access** | **LISP** (control) + **VXLAN** (data) + **TrustSec** (policy), trên nền **VRF**.<br>5 fabric role · ⭐ **anycast gateway** thay thế FHRP |
| ⭐⭐ **§9 QoS** | **DiffServ** · ⭐ **LLQ cho voice** · ⭐ **Policing VỨT / Shaping CHỜ** · WRED |

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | **ACL đặt ở Distribution** | Access quá nhiều thiết bị · **Core phải giữ đơn giản và nhanh** |
| 2 | **2-tier hay 3-tier?** | Cần Core riêng khi có **≥ 3 khối distribution** *(n khối full-mesh cần n(n−1)/2 link)* |
| 3 | **Spine-Leaf cho DC** | Vì traffic DC là **East-West**, và cần **luôn đúng 2 hop** |
| 4 | ⭐⭐ **SD-WAN 3 câu chốt** | IP public → **vBond** · chạy OMP → **vSmart** · traffic qua vSmart? → 🔴 **KHÔNG** |
| 5 | ⭐⭐ **SD-Access 3 plane** | **LISP** control · **VXLAN** data · **TrustSec** policy · **VN = VRF** |
| 6 | ⭐⭐ **Anycast gateway** | Mọi edge node **cùng IP + cùng MAC** → thay thế HSRP hoàn toàn |
| 7 | ⭐⭐ **Voice: 150 / 30 / 1** | Latency ≤ **150 ms** · jitter ≤ **30 ms** · loss ≤ **1 %** · MOS > 4.0 |

## Bảng số QoS phải thuộc

| Nhóm | Giá trị |
|---|---|
| ⭐ **DSCP** | **EF = 46** *(voice)* · **CS3 = 24** *(signaling)* · **CS6 = 48** *(network control)* · **AF41 = 34** *(video)* · **CS1 = 8** *(scavenger)* · **DF = 0** |
| ⭐ **Công thức** | `AFxy = 8x + 2y` · `CSx = 8x` · 🔴 **y CAO = DỄ BỊ VỨT hơn** |
| ⭐ **Giới hạn** | Priority queue **≤ 33%** băng thông link |
| ⭐ **CoS** | 3 bit, **CHỈ tồn tại trên trunk** *(nằm trong tag 802.1Q)* |

## 🗺️ Bố cục module

| Phần | Tên | Thời gian |
|:---:|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** — 4 ví von | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** — ⭐ **§7, §8, §9 chiếm 2/3 số câu** | 5 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** — [LAB 09](Module-09-LAB.md), ⭐ **RAM 1 GB, nhẹ nhất repo** | 3 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** — SD-WAN vs SD-Access | 45 phút |
| **📎** | **PHỤ LỤC** — 🔴 không đọc lần đầu | — |

> 🔴 **Đừng cố dựng SD-WAN on-prem.** vManage + vSmart + vBond + 2 vEdge = **20+ GB RAM**.
> Máy bạn không kham nổi, **và đề KHÔNG hỏi cấu hình**. Dùng **DevNet Sandbox** để *nhìn* là đủ.

---

## ⭐ 0. Phạm vi — module "tỉ lệ điểm/công sức tốt nhất" của cả kỳ thi

### 0.1 Đọc cái này trước

> 🔴 ⭐⭐ **TOÀN BỘ Domain 1.0 dùng các từ: "Explain", "Analyze", "Differentiate", "Describe".**
> ⭐ **KHÔNG có một chữ "Configure" nào.**
>
> ⭐ Nghĩa là: đây là ⭐ **15% số điểm mà bạn có thể lấy CHỈ BẰNG CÁCH HỌC BẢNG** —
> không cần dựng lab SD-WAN 20 GB RAM, không cần DNA Center.

| So sánh | Infrastructure (30%) | ⭐ **Architecture (15%)** |
|---|---|---|
| Kiểu hỏi | Cấu hình + đọc output + troubleshoot | ⭐ **Vai trò thành phần · chọn design nào cho case nào** |
| Cần lab? | ⭐ **Bắt buộc** | ⭐ **Gần như không** |
| Giờ học/1% điểm | ~4–5 giờ | ⭐ **~0.7 giờ** |

🔴 ⭐ **Nhưng có một cái bẫy ngược:** vì dễ nên nhiều người **học qua loa**, rồi vào phòng thi
gặp câu *"vBond làm gì"* / *"Control Plane Node của SD-Access chạy giao thức nào"* thì tắc.
⭐ **Bảng thành phần SD-WAN và SD-Access phải thuộc như bảng cửu chương.**

### 0.2 Bảng phạm vi

| Chủ đề | Blueprint | Mức cần đạt | Thời gian |
|---|---|---|---|
| ⭐ **2-tier / 3-tier / collapsed core** | 1.1.a | ⭐ Vai trò từng lớp · **chọn cái nào khi nào** | 1 giờ |
| ⭐ **Spine-Leaf · east-west** | 1.1.a | ⭐ Vì sao DC không dùng 3-tier | 30 phút |
| ⭐ **Capacity planning / oversubscription** | 1.1.a | ⭐ Tỉ lệ 20:1 và 4:1 | 20 phút |
| ⭐ **High availability** | 1.1.b | ⭐ Redundancy các tầng · **SSO/NSF/GR** · StackWise/VSS · FHRP *(ôn M06A)* | 1 giờ |
| ⭐ **WLAN deployment models** | 1.2.a | ⭐ **6 mô hình** — bảng so sánh | 45 phút |
| ⭐ **Location services** | 1.2.b | ⭐ RSSI trilateration vs **Hyperlocation (AoA)** vs BLE | 30 phút |
| ⭐ **Client density** | 1.2.c | *(đã học kỹ ở **[07A §4.2](Module-07A-Wireless-RF-802.11-AP-Antenna.md)** — chỉ ôn lại)* | 15 phút |
| ⭐ **On-prem vs Cloud** | 1.3 | ⭐ IaaS/PaaS/SaaS · 4 cách kết nối cloud · CapEx vs OpEx | 45 phút |
| 🔴 ⭐⭐ **SD-WAN** | ⭐⭐ **1.4** | ⭐⭐ **4 thành phần + OMP + TLOC + color.** ⭐ **Học thuộc** | 1.5 giờ |
| 🔴 ⭐⭐ **SD-Access** | ⭐⭐ **1.5** | ⭐⭐ **5 fabric role + LISP/VXLAN/TrustSec + anycast GW + VN/SGT.** ⭐ **Học thuộc** | 2 giờ |
| 🔴 ⭐⭐ **QoS** | ⭐⭐ **1.6** | ⭐⭐ **DiffServ · DSCP · LLQ · policing vs shaping · WMM · ngưỡng voice** | 2.5 giờ |

> ⭐ **Ba mục in đỏ (SD-WAN, SD-Access, QoS) chiếm khoảng 2/3 số câu của Domain 1.0.**
> ⭐ Nếu thiếu thời gian: ⭐ **học 3 mục đó trước**, các mục còn lại đọc bảng là đủ.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | ⭐ **Module-08 §7–8 (LISP + VXLAN + VRF)** — ⭐ **SD-Access xây thẳng trên đó** · Module-06A (FHRP, SSO) · Module-07A §4.2 (client density) · Module-02 (STP/EtherChannel) |
| **Lab** | ⭐ **1 lab QoS nhỏ trên EVE-NG** (2 router) + ⭐ **lab-trên-giấy** cho design + ⭐ **DevNet Sandbox** (DNA Center / vManage) |
| **RAM** | ⭐ **~1 GB** (2× vIOS) — ⭐ module nhẹ nhất về lab |
| **Thời lượng** | 6h lý thuyết · 3h lab · 1h quiz |

> 🔴 ⭐ **Đừng cố dựng SD-WAN on-prem.** vManage + vSmart + vBond + 2 vEdge = ⭐ **20+ GB RAM**.
> ⭐ **Máy bạn không kham nổi, và đề KHÔNG hỏi cấu hình.** ⭐ Dùng **DevNet Sandbox** để *nhìn*, thế là đủ.

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> Module-09 toàn khái niệm kiến trúc trừu tượng (SD-WAN, SD-Access, QoS).
> Bốn ví von dưới đây biến chúng thành chuyện đời thường.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 Ba lớp campus là ba vai trò trong một công ty

- ⭐ **Access = lễ tân** — tiếp xúc trực tiếp với khách (người dùng), kiểm tra giấy tờ (802.1X), rất đông.
- ⭐ **Distribution = quản lý tầng** — ⭐ **nơi ra quyết định và áp quy định** (ACL, policy, gateway).
  ⭐ Nó là **ranh giới**: dưới nó là L2, trên nó là L3.
- ⭐ **Core = đường cao tốc** — ⭐ **không có đèn đỏ, không có trạm thu phí, không có biển cấm.**
  ⭐ Chỉ có một nhiệm vụ: **chạy thật nhanh**.

🔴 ⭐ **Vì thế đặt ACL vào Core giống như đặt trạm thu phí giữa đường cao tốc** — sai chỗ.

### 2.2 SD-WAN: bốn con người trong một công ty vận tải

- ⭐ **vBond = anh bảo vệ ở cổng.** ⭐ **Xe mới tới thì gặp anh này TRƯỚC.** Anh kiểm giấy tờ (chứng thư),
  rồi chỉ: *"vào trong gặp giám đốc và điều độ viên"*. ⭐ **Anh phải đứng ở ngoài cổng → phải có địa chỉ ai cũng tìm được (IP public).**
- ⭐ **vManage = giám đốc.** Bạn nói chuyện với ông này. Ông ra chính sách, xem báo cáo.
- ⭐ **vSmart = điều độ viên.** ⭐ Ông cầm bản đồ, biết tất cả tuyến đường, **bảo từng xe đi đường nào**.
  🔴 ⭐ **Nhưng ông KHÔNG lái xe, và hàng hóa KHÔNG đi qua bàn ông.**
- ⭐ **vEdge/cEdge = tài xế.** ⭐ **Chở hàng thật.** Xe này nói chuyện thẳng với xe kia (IPsec), không qua điều độ.

⭐ **Và BFD/AAR = tài xế liên tục báo về "đường này đang kẹt"** → điều độ viên đổi tuyến cho hàng ưu tiên.

### 2.3 SD-Access: anycast gateway là "cửa ra vào ở mọi bức tường"

⭐ Mạng truyền thống: cả tòa nhà có **một cửa chính** (gateway ở distribution). ⭐ Bạn ở tầng 5 muốn ra ngoài
thì phải đi bộ xuống tầng trệt. ⭐ **HSRP** chỉ là *"có hai bác bảo vệ thay phiên gác cái cửa đó"*.

⭐⭐ **SD-Access: MỌI bức tường đều là cửa ra, và mọi cửa đều mang CÙNG một số nhà.**
⭐ Bạn đứng ở đâu cũng có cửa ngay cạnh, ⭐ **và vì mọi cửa cùng số nhà nên bạn chuyển chỗ mà
không phải đổi địa chỉ, không phải hỏi lại đường (không ARP lại).**

⭐ **Đó là toàn bộ ý nghĩa của anycast gateway** — và là lý do SD-Access **không cần HSRP**.

### 2.4 QoS: sân bay giờ cao điểm

- ⭐ **Marking (DSCP)** = ⭐ **in hạng vé lên boarding pass**. Làm **một lần ở quầy check-in**
  (⭐ **trust boundary, càng gần nguồn càng tốt**), sau đó ai cũng chỉ cần nhìn tấm vé.
- ⭐⭐ **LLQ** = ⭐ **làn ưu tiên đi thẳng ra cửa**. ⭐ Voice đi làn này.
  🔴 ⭐ **Nhưng nếu cho 80% hành khách vào làn ưu tiên thì nó hết là ưu tiên** → ⭐ **giới hạn 33%**.
- ⭐ **CBWFQ** = ⭐ **mỗi hạng vé được đảm bảo một số quầy làm thủ tục** — chắc chắn được phục vụ,
  ⭐ **nhưng không hứa là nhanh**.
- ⭐ **Policing** = ⭐ **hành lý quá cân thì VỨT LẠI.** ⭐ **Shaping** = ⭐ **cho chờ chuyến sau.**
- ⭐ **WRED** = ⭐ **thấy sắp quá tải thì mời rải rác vài người đổi chuyến TRƯỚC KHI vỡ trận**,
  thay vì để đến lúc đầy rồi ⭐ **đuổi hết một loạt** (tail drop) làm cả sân bay hỗn loạn cùng lúc
  (⭐ **TCP global synchronization**).

⭐ **Và trust boundary = "không tin hành khách tự in vé hạng thương gia ở nhà"** —
🔴 ⭐ **đó chính là lý do không tin DSCP từ PC người dùng.**


---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 ba vai trò trong công ty | → | **§3 Thiết kế campus (Access/Dist/Core)** |
> | §2.2 công ty vận tải | → | **§7 SD-WAN** 🔴 ⭐⭐ |
> | §2.3 cửa ra ở mọi bức tường | → | **§8 SD-Access (anycast gateway)** 🔴 ⭐⭐ |
> | §2.4 sân bay giờ cao điểm | → | **§9 QoS** 🔴 ⭐⭐ |
>
> ⭐ **Ba mục in đỏ (§7, §8, §9) chiếm khoảng 2/3 số câu của Domain 1.0.**
> Thiếu thời gian thì học ba mục đó trước, phần còn lại đọc bảng là đủ.

---

## 📘 3. THIẾT KẾ CAMPUS (blueprint 1.1.a)

### 3.1 ⭐⭐ Ba lớp kinh điển

```
        ┌──────────────────────────────────┐
        │      CORE  (backbone)          │  "chuyển gói NHANH, không làm gì khác"
        └────────┬────────────────┬────────┘
                 │                │
        ┌────────┴────────┐ ┌─────┴──────────┐
        │ DISTRIBUTION │ │  DISTRIBUTION  │  "ranh giới L2/L3, nơi ĐẶT CHÍNH SÁCH"
        └───┬────────┬────┘ └────────────────┘
            │        │
     ┌──────┴──┐ ┌───┴─────┐
     │ ACCESS│ │ ACCESS  │                    "cắm người dùng, PoE, port security"
     └────┬────┘ └─────────┘
       PC/phone/AP
```

| Lớp | ⭐ Nhiệm vụ chính | ⭐ Đặt gì ở đây | ⭐ **KHÔNG** đặt gì |
|---|---|---|---|
| ⭐⭐ **Access** | Cắm thiết bị đầu cuối | ⭐ **PoE · VLAN · port security · 802.1X · PortFast/BPDU Guard · QoS trust boundary** | Routing phức tạp, ACL nặng |
| ⭐⭐ **Distribution** | ⭐ **Tổng hợp access · RANH GIỚI L2/L3** | ⭐ **SVI/gateway · FHRP (HSRP) · ACL · route summarization · redistribution · policy** | Cắm người dùng trực tiếp |
| ⭐⭐ **Core** | ⭐ **CHUYỂN GÓI CỰC NHANH** | ⭐ **Chỉ routing L3 + ECMP. CÀNG ĐƠN GIẢN CÀNG TỐT** | 🔴 ⭐ **ACL · NAT · QoS phức tạp · policy** — mọi thứ làm chậm nó |

> 🔴 ⭐⭐ **Câu hỏi đề kinh điển:** *"Nên đặt ACL/policy ở lớp nào?"*
> ⭐ **DISTRIBUTION.** ⭐ Access thì quá nhiều thiết bị (khó quản lý), ⭐ **Core thì phải giữ cho nhanh và đơn giản.**

### 3.2 ⭐⭐ 2-tier (Collapsed Core) vs 3-tier

```
   ═══ 3-TIER ═══                    ═══ 2-TIER (Collapsed Core) ═══

   CORE                              ┌── CORE + DISTRIBUTION gộp làm một ──┐
    │                                │          (thường 2 switch)             │
   DIST                              └──────┬──────────────┬──────────────────┘
    │                                       │              │
   ACCESS                                 ACCESS        ACCESS
```

| | **3-tier** | ⭐ **2-tier (Collapsed Core)** |
|---|---|---|
| ⭐ **Dùng khi** | ⭐ **Nhiều tòa nhà / nhiều khối distribution** (thường **≥ 3** khối) | ⭐ **Một tòa nhà / campus nhỏ-vừa** |
| Vì sao cần Core riêng | ⭐ **Nối các khối distribution với nhau.** Không có core thì các dist phải **full-mesh** → số link bùng nổ | Chỉ có 1–2 khối → **không cần** |
| Chi phí | Cao hơn | ⭐ Thấp hơn |
| Độ phức tạp | Cao hơn | Thấp hơn |
| ⭐ Khả năng mở rộng | ⭐ **Tốt** | Hạn chế |

> ⭐⭐ **Quy tắc quyết định — nhớ câu này:**
> ⭐ ***"Cần Core riêng khi số khối distribution nhiều tới mức nối chúng trực tiếp với nhau trở nên rối."***
> ⭐ Cisco thường lấy mốc ⭐ **3 khối distribution trở lên → tách Core.**
> *(Toán học: n khối full-mesh cần `n(n−1)/2` link. 3 khối = 3 link (còn OK), 6 khối = 15 link (thảm họa).)*

### 3.3 ⭐ Access layer: L2 access vs Routed access

| | ⭐ **Layer 2 access** *(truyền thống)* | ⭐ **Routed access** *(L3 xuống tận access)* |
|---|---|---|
| Ranh giới L3 ở | ⭐ **Distribution** | ⭐ **Access switch** |
| Link access↔dist | ⭐ **Trunk L2** | ⭐ **Routed link (L3)** |
| Ai lo hội tụ | ⭐ **STP + FHRP** | ⭐ **Giao thức định tuyến (EIGRP/OSPF)** |
| Hội tụ | Chậm hơn | ⭐ **Nhanh hơn nhiều** |
| VLAN trải nhiều access switch | ✅ Được | 🔴 ⭐ **KHÔNG** (mỗi switch một subnet) |
| ⭐ Nhược điểm | STP là điểm yếu | ⭐ Không kéo VLAN xuyên switch được |

⭐ **Xu hướng hiện đại:** ⭐ **routed access** (và SD-Access dùng underlay routed access).
⭐ **Nhưng nhiều nơi vẫn cần L2 access** vì ứng dụng cũ đòi cùng subnet.

### 3.4 ⭐⭐ Spine-Leaf — vì sao Data Center KHÔNG dùng 3-tier

```
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │ SPINE 1 │   │ SPINE 2 │   │ SPINE 3 │
        └──┬─┬─┬──┘   └──┬─┬─┬──┘   └──┬─┬─┬──┘
           │ │ └──────────┼─┼──┐       │ │ │
     ┌─────┘ └────┐  ┌────┘ │  └───────┘ │ │      MỌI leaf nối TỚI MỌI spine
     │            │  │      │            │ │      KHÔNG có link leaf–leaf
   ┌─┴────┐  ┌────┴──┴┐  ┌──┴────────────┴─┴┐     KHÔNG có link spine–spine
   │LEAF 1│  │ LEAF 2 │  │      LEAF 3      │
   └──┬───┘  └───┬────┘  └────────┬─────────┘
   servers    servers          servers
```

| | ⭐ **3-tier (campus)** | ⭐⭐ **Spine-Leaf (DC)** |
|---|---|---|
| Traffic chủ yếu | ⭐ **North-South** (người dùng ↔ server/Internet) | ⭐⭐ **East-West** (server ↔ server: app↔DB, VM↔VM, microservices) |
| Số hop giữa 2 endpoint | ⭐ **Thay đổi** (2 hop hoặc 4 hop tùy vị trí) | ⭐⭐ **LUÔN LUÔN 2 hop** (leaf→spine→leaf) → ⭐ **độ trễ dự đoán được** |
| STP | Có | ⭐ **Không cần** — underlay routed, ⭐ **ECMP dùng hết mọi đường** |
| Mở rộng | Thêm tầng | ⭐ **Thêm spine** = tăng băng thông cho tất cả · **thêm leaf** = tăng số port |
| Overlay | Không bắt buộc | ⭐⭐ **VXLAN + EVPN** *(Module-08 §8)* |

> ⭐⭐ **Câu chốt:** ⭐ **"3-tier tối ưu cho North-South. Spine-Leaf tối ưu cho East-West và độ trễ ĐỀU."**
> ⭐ **Đây là lý do ảo hóa/microservices làm DC phải đổi kiến trúc** — traffic server↔server bùng nổ.

### 3.5 ⭐ Capacity planning & oversubscription

> ⭐ **Oversubscription** = tổng băng thông **phía dưới** lớn hơn băng thông **lên trên** bao nhiêu lần.

```
   Access switch: 48 port × 1 Gbps = 48 Gbps phía dưới
                  uplink 2 × 10 Gbps = 20 Gbps lên trên
   Oversubscription = 48 / 20 = 2.4 : 1
```

| Chặng | ⭐ Tỉ lệ Cisco khuyến nghị |
|---|---|
| ⭐ **Access → Distribution** | ⭐ **20 : 1** |
| ⭐ **Distribution → Core** | ⭐ **4 : 1** |
| Spine-Leaf (DC hiện đại) | ⭐ **3:1 hoặc thấp hơn** — nhiều nơi làm **1:1 (non-blocking)** |

⭐ **Vì sao được phép oversubscribe:** ⭐ **không phải tất cả port đều truyền hết công suất cùng lúc.**
🔴 ⭐ **Nhưng nếu oversubscribe quá tay → nghẽn uplink → mọi thứ chậm mà `show interface` trên access lại "sạch".**

⭐ **Các yếu tố khác của capacity planning:** số user/port · băng thông mỗi ứng dụng · ngân sách **PoE**
(⭐ AP Wi-Fi 6 cần **802.3at/bt**) · công suất **backplane/switching fabric** · dự phòng tăng trưởng 3–5 năm.

---

## 📘 4. HIGH AVAILABILITY (blueprint 1.1.b)

### 4.1 ⭐⭐ Bảng dự phòng theo từng tầng

| Tầng | Kỹ thuật | ⭐ Chống hỏng cái gì |
|---|---|---|
| **Nguồn điện** | Dual power supply, dual UPS, 2 nguồn điện lưới | Chết một nguồn |
| **Card điều khiển** | ⭐ **Dual supervisor + SSO** | Chết một supervisor |
| **Link** | ⭐ **EtherChannel (LACP)** *(M02)* · nhiều uplink | Đứt một sợi cáp |
| **Thiết bị** | ⭐ **StackWise / VSS / StackWise Virtual / vPC** | Chết cả một switch |
| ⭐ **Gateway** | ⭐⭐ **HSRP / VRRP / GLBP** *(M06A)* | Chết router gateway |
| **Đường đi L3** | ⭐ **ECMP · floating static · IP SLA + track** *(M03)* | Đứt một đường |
| **Phần mềm** | ⭐ **ISSU** (nâng cấp không gián đoạn) | Downtime khi nâng cấp |
| **Site** | Data center thứ hai, DR | Mất cả một site |

### 4.2 ⭐⭐ SSO · NSF · GR — ba chữ hay lẫn nhau

| | ⭐ **SSO** (Stateful Switchover) | ⭐ **NSF** (Nonstop Forwarding) | ⭐ **GR** (Graceful Restart) |
|---|---|---|---|
| Ai làm | ⭐ **Bên trong MỘT thiết bị** (2 supervisor) | ⭐ **Bên trong MỘT thiết bị** | ⭐ **Thiết bị HÀNG XÓM hỗ trợ** |
| Làm gì | ⭐ **Đồng bộ trạng thái** sang supervisor dự phòng → chuyển đổi **không mất trạng thái** | ⭐ **Tiếp tục FORWARD gói** (dùng FIB cũ) trong khi control plane đang khởi động lại | ⭐ **Hàng xóm "giữ chỗ"**, không xóa route, chờ bạn khôi phục |
| Tầng nào | Control plane | ⭐ **Data plane** | Control plane (phía hàng xóm) |
| ⭐ Nhớ bằng | ⭐ *"Bộ não dự phòng đã học thuộc bài"* | ⭐ *"Chân vẫn chạy trong lúc não đang reboot"* | ⭐ *"Hàng xóm giả vờ không thấy gì"* |

> ⭐⭐ **Ba cái này đi CÙNG NHAU:** ⭐ **SSO** chuyển sang sup dự phòng · ⭐ **NSF** giữ cho gói vẫn chảy
> trong lúc đó · ⭐ **GR** làm hàng xóm không rút route của bạn. ⭐ **Thiếu một cái là vẫn rớt.**

### 4.3 ⭐ Gộp nhiều switch thành một

| Công nghệ | Nền tảng | Ý tưởng |
|---|---|---|
| ⭐ **StackWise / StackWise-480** | Catalyst access (2960X/9200/9300) | ⭐ Nhiều switch **cáp stack** thành **một thiết bị logic**, một control plane |
| ⭐ **VSS / StackWise Virtual** | Catalyst 4500/6500/9400/9500 | ⭐ **Hai switch lớn** → một thiết bị logic qua link tốc độ cao (**VSL**) |
| **vPC** (virtual PortChannel) | Nexus | ⭐ Hai switch **giữ control plane RIÊNG** nhưng cho phép host tạo **EtherChannel qua CẢ HAI** |

> ⭐⭐ **Lợi ích chung — và đây là lý do người ta dùng:**
> ⭐ **Biến hai uplink lên hai switch khác nhau thành MỘT EtherChannel** →
> 🔴 ⭐ **STP không còn chặn đường nào nữa** (vì với STP đó chỉ là một link logic) →
> ⭐ **dùng được 100% băng thông + hội tụ nhanh hơn nhiều so với STP.**
>
> ⭐ **Khác biệt vPC:** ⭐ **hai control plane riêng biệt** → nâng cấp/reboot từng con được, ⭐ **an toàn hơn**
> (VSS/Stack lỗi phần mềm có thể sập cả cặp).

⭐ **FHRP** (HSRP/VRRP/GLBP) đã học kỹ ở ⭐ **[Module-06A](Module-06A-FHRP-HSRP-VRRP-GLBP.md)** —
⭐ blueprint 1.1.b nhắc lại nó, nên **ôn lại bảng so sánh 3 giao thức + object tracking**.

---

## 📘 5. THIẾT KẾ WLAN (blueprint 1.2)

### 5.1 ⭐⭐ Sáu mô hình triển khai WLAN (1.2.a)

| Mô hình | Điều khiển ở đâu | Data đi đâu | ⭐ Dùng khi |
|---|---|---|---|
| ⭐ **Autonomous** (controller-less) | ⭐ **Trong từng AP** | Ra thẳng LAN | ⭐ 1–5 AP. Quán cà phê, văn phòng siêu nhỏ |
| ⭐⭐ **Centralized** (controller-based) | ⭐ **WLC tập trung** | ⭐ **CAPWAP về WLC** | ⭐⭐ **Campus/tòa nhà, WLC cùng site.** *(07B §4)* |
| ⭐⭐ **Distributed / Branch** (**FlexConnect**) | WLC ở HQ | ⭐ **Ra thẳng LAN chi nhánh** | ⭐⭐ **Nhiều chi nhánh, WAN hẹp/hay đứt.** *(07B §5)* |
| ⭐ **Embedded (EWC)** | ⭐ **WLC chạy trên chính một AP** | Ra LAN tại site | ⭐ Site nhỏ-vừa (**< ~100 AP**), không muốn mua WLC |
| ⭐ **Cloud-managed** | ⭐ **Dashboard trên đám mây** (Meraki) hoặc **9800-CL trên cloud** | ⭐ Meraki: ra thẳng LAN | ⭐ Nhiều site nhỏ, đội IT mỏng, muốn quản lý một chỗ |
| ⭐ **Remote branch / OEAP** | WLC ở HQ | ⭐ **DTLS tunnel qua Internet về HQ** | ⭐ **AP mang về nhà nhân viên** |

> 🔴 ⭐ **Bẫy hay gặp:** ⭐ **"Cloud" ở đây có HAI nghĩa khác nhau:**
> · ⭐ **Cloud-managed** (Meraki): ⭐ **chỉ QUẢN LÝ ở cloud, DATA vẫn ra thẳng LAN tại chỗ**
> · ⭐ **Cloud-hosted WLC** (9800-CL trên AWS/Azure): WLC là VM trên cloud, ⭐ **AP vẫn dựng CAPWAP tới nó**

### 5.2 ⭐ Location Services (1.2.b)

| Kỹ thuật | Cách hoạt động | ⭐ Độ chính xác |
|---|---|---|
| ⭐ **RSSI trilateration** | ⭐ **≥ 3 AP** cùng nghe được client → tính giao điểm từ độ mạnh tín hiệu | ⭐ **~5–10 m** |
| ⭐⭐ **Cisco Hyperlocation (AoA)** | ⭐ **Angle of Arrival** — module antenna đặc biệt đo **GÓC** tín hiệu tới | ⭐⭐ **~1 m** |
| ⭐ **BLE beacon** | Đèn hiệu Bluetooth phát ID, app trên điện thoại nghe | ~1–3 m, ⭐ **cần app** |
| **Fingerprinting (RF map)** | So mẫu RSSI với bản đồ đã khảo sát trước | Vài mét, tốn công khảo sát |
| **GPS** | Vệ tinh | ⭐ **Không dùng được trong nhà** |

⭐ **Nền tảng phần mềm:** ⭐ **Cisco CMX** (cũ) → ⭐ **Cisco Spaces / DNA Spaces** (hiện tại).
⭐ **Ứng dụng:** tìm tài sản (bệnh viện tìm máy thở), phân tích luồng khách (bán lẻ), tìm client khi troubleshoot,
định vị **rogue AP**, tuân thủ **E911**.

> 🔴 ⭐⭐ **Yêu cầu THIẾT KẾ quan trọng nhất cho location — đề hay hỏi:**
> ⭐ **Phải có AP ở CHU VI (perimeter) của khu vực, không chỉ ở giữa.**
> ⭐ Vì trilateration cần **bao vây** mục tiêu. ⭐ AP chỉ đặt giữa trần → mọi client đều "ở giữa" →
> ⭐ **định vị sai bét.** ⭐ Cisco khuyến nghị AP đặt so le kiểu **zig-zag**, khoảng cách ~12–21 m.

### 5.3 ⭐ Client density (1.2.c)

⭐ Đã học kỹ ở ⭐ **[Module-07A §4.2](Module-07A-Wireless-RF-802.11-AP-Antenna.md)**. ⭐ **Ôn nhanh:**

| ⭐ Điểm phải nhớ |
|---|
| ⭐⭐ **Thiết kế theo CAPACITY, không theo COVERAGE** cho văn phòng/lớp học/hội trường |
| ⭐ **6 cần gạt:** giảm công suất + thêm AP · tắt low data rate · 20/40 MHz · band select · ≤ 3–4 SSID · airtime fairness |
| 🔴 ⭐ **"Sóng yếu thì THÊM AP, đừng tăng công suất"** |
| ⭐ **RSSI ≥ −67 dBm khắp nơi · SNR ≥ 25 dB · cell overlap 15–20%** |

---

## 📘 6. ON-PREM vs CLOUD (blueprint 1.3)

### 6.1 ⭐ Ba mô hình dịch vụ

```
   AI QUẢN CÁI GÌ:              On-Prem    IaaS     PaaS     SaaS
   ─────────────────────────────────────────────────────────────────
   Ứng dụng / Dữ liệu               BẠN       BẠN      BẠN     NCC
   Runtime / Middleware             BẠN       BẠN     NCC   NCC
   Hệ điều hành                     BẠN       BẠN     NCC   NCC
   Ảo hóa / Server / Storage        BẠN      NCC   NCC   NCC
   Mạng / Điện / Nhà xưởng          BẠN      NCC   NCC   NCC
                                             (NCC = nhà cung cấp cloud)
```

| | ⭐ **IaaS** | ⭐ **PaaS** | ⭐ **SaaS** |
|---|---|---|---|
| Bạn nhận được | ⭐ **Máy ảo, mạng, ổ đĩa** | ⭐ **Nền tảng để chạy code** | ⭐ **Phần mềm dùng ngay** |
| Ví dụ | ⭐ **AWS EC2, Azure VM, GCP CE** | App Engine, Azure App Service, Heroku | ⭐ **Microsoft 365, Salesforce, Webex** |
| ⭐ Người làm mạng quan tâm nhất | ⭐⭐ **IaaS** — vì bạn phải tự dựng VPC/VNet, subnet, routing, firewall | Ít | Ít |

⭐ **Mô hình triển khai:** ⭐ **Public** (AWS/Azure/GCP) · ⭐ **Private** (cloud riêng trong DC của bạn —
⭐ **cụm Proxmox của bạn chính là private cloud**) · ⭐ **Hybrid** (kết hợp) · **Multi-cloud** (nhiều NCC).

### 6.2 ⭐⭐ Bốn cách kết nối tới Cloud — bảng phải nhớ

| Cách | Đường đi | Độ trễ / ổn định | Chi phí | ⭐ Dùng khi |
|---|---|---|---|---|
| ⭐ **Internet + VPN (IPsec)** | Qua Internet công cộng | 🟡 Thay đổi | ⭐ **Rẻ nhất** | ⭐ Mặc định, khối lượng vừa · *(chính là **GRE/IPsec** Module-08!)* |
| ⭐⭐ **Direct Connect / ExpressRoute / Cloud Interconnect** | ⭐ **Đường riêng, KHÔNG qua Internet** | ⭐⭐ **Ổn định, độ trễ thấp, có SLA** | Đắt | ⭐⭐ **Production quan trọng, dữ liệu lớn, cần SLA** |
| ⭐ **Colocation / CSP peering** | Đặt thiết bị ở DC trung lập, peering trực tiếp | ⭐ Rất tốt | Đắt | Kết nối **nhiều cloud** cùng lúc |
| ⭐ **SD-WAN Cloud OnRamp** | ⭐ SD-WAN **tự chọn đường tốt nhất** tới cloud | ⭐ **Tự tối ưu theo thời gian thực** | Vừa | ⭐ **Đã có SD-WAN** (§6) |

⭐ **Router ảo trong cloud:** ⭐ **Cisco Catalyst 8000v / CSR1000v** — chạy IOS-XE **dưới dạng VM trên AWS/Azure**
→ ⭐ dựng được IPsec/BGP/VRF ngay trong VPC. ⭐ **Đây chính là NFV** (Module-08 §2.3).

### 6.3 ⭐ Chọn On-prem hay Cloud

| Tiêu chí | ⭐ **On-premises** | ⭐ **Cloud** |
|---|---|---|
| ⭐ Chi phí | ⭐ **CapEx** (mua một lần, khấu hao) | ⭐ **OpEx** (trả theo tháng/mức dùng) |
| ⭐ Co giãn | 🔴 Chậm — phải mua thêm phần cứng | ⭐⭐ **Gần như tức thì** |
| Kiểm soát | ⭐ **Toàn quyền** | Hạn chế trong khuôn khổ NCC |
| Tuân thủ / chủ quyền dữ liệu | ⭐ **Dễ chứng minh** | Phụ thuộc vùng & chứng chỉ của NCC |
| Độ trễ tới người dùng nội bộ | ⭐ **Thấp nhất** | Phụ thuộc đường ra |
| Nhân sự vận hành | ⭐ Cần đội đầy đủ | Ít hơn ở tầng hạ tầng |
| 🔴 **Chi phí ẩn** | Điện, làm mát, mặt bằng, refresh 5 năm | 🔴 ⭐ **Egress (phí ra dữ liệu)** — ⭐ thứ hay bị bỏ sót nhất |

> ⭐ **Cho đề thi:** ⭐ **CapEx vs OpEx · elasticity · shared responsibility · Direct Connect có SLA còn VPN thì không.**
> ⭐ Đề hỏi ở mức "chọn phương án nào cho tình huống này", không hỏi chi tiết kỹ thuật cloud.

---

## 📘 7. 🔴 ⭐⭐ SD-WAN (blueprint 1.4)

### 7.1 ⭐ Vấn đề của WAN truyền thống

| 🔴 Vấn đề | ⭐ SD-WAN giải quyết |
|---|---|
| ⭐ MPLS **đắt**, lắp mới mất **hàng tháng** | ⭐ **Dùng được cả Internet/4G rẻ**, coi mọi đường là **transport** |
| ⭐ Cấu hình **từng router một** qua CLI | ⭐ **Template tập trung trên vManage** |
| ⭐ Đường backup **nằm không** (active/standby) | ⭐⭐ **Dùng ĐỒNG THỜI tất cả đường**, chia theo ứng dụng |
| ⭐ Traffic SaaS phải **chạy vòng về HQ** rồi mới ra Internet | ⭐ **Direct Internet Access / Cloud OnRamp** tại chi nhánh |
| ⭐ Router mới phải có **kỹ sư đến tận nơi** | ⭐⭐ **ZTP / PnP** — cắm điện + mạng là tự cấu hình |
| ⭐ Không biết đường nào đang tốt | ⭐⭐ **BFD đo loss/latency/jitter liên tục** → **AAR** tự chuyển |

### 7.2 ⭐⭐ BỐN THÀNH PHẦN — bảng QUAN TRỌNG NHẤT của §6

```
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │ vMANAGE   │   │ vSMART    │   │ vBOND     │
   │  QUẢN LÝ     │   │  ĐIỀU KHIỂN  │   │  ĐIỀU PHỐI   │
   │  (GUI/API)   │   │  (OMP+policy)│   │  (kết nối    │
   │              │   │              │   │   đầu tiên)  │
   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
          │  DTLS/TLS        │ OMP           │ CHỈ nó cần IP PUBLIC
          └──────────┬───────┴──────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────┴─────┐             ┌─────┴────┐
   │ cEdge /  │═══ IPsec ═══│ cEdge /  │   DATA PLANE
   │  vEdge   │   (data thật)  │  vEdge   │   Traffic KHÔNG đi qua vSmart!
   └──────────┘             └──────────┘
```

| Thành phần | ⭐ Plane | ⭐⭐ Làm gì | ⭐ Điểm nhận dạng |
|---|---|---|---|
| ⭐⭐ **vManage** | ⭐ **Management** | ⭐ **GUI/API duy nhất** — cấu hình bằng **template**, giám sát, nâng cấp, báo cáo | ⭐ *"Cái bạn ĐĂNG NHẬP VÀO"* |
| ⭐⭐ **vSmart** | ⭐ **Control** | ⭐⭐ **Chạy OMP** — phân phối **route, TLOC, chính sách** cho tất cả edge. ⭐ **Như một Route Reflector cho overlay** | 🔴 ⭐⭐ ***KHÔNG BAO GIỜ chở dữ liệu người dùng*** |
| ⭐⭐ **vBond** | ⭐ **Orchestration** | ⭐ **Điểm liên hệ ĐẦU TIÊN** — xác thực thiết bị mới, ⭐ **giới thiệu** nó cho vManage & vSmart, ⭐ **phát hiện NAT** | 🔴 ⭐⭐ ***Thành phần DUY NHẤT bắt buộc có IP PUBLIC*** |
| ⭐⭐ **vEdge / cEdge** | ⭐ **Data** | ⭐ **Router tại site** — dựng **IPsec tunnel** với nhau, ⭐ **forward traffic thật** | ⭐ **cEdge = IOS-XE** (ISR/Cat8000) · **vEdge = Viptela OS** (đời cũ) |

> 🔴 ⭐⭐ **Ba câu đề hỏi đi hỏi lại — thuộc lòng:**
> 1. ⭐ ***"Thành phần nào cần IP public?"*** → ⭐ **vBond**
> 2. ⭐ ***"Traffic người dùng có đi qua vSmart không?"*** → ⭐ **KHÔNG. vSmart chỉ là control plane.**
> 3. ⭐ ***"Thành phần nào chạy OMP với các edge?"*** → ⭐ **vSmart**
>
> ⭐ **Mẹo nhớ 4 chữ v:** ⭐ **vManage = "tôi QUẢN"** · ⭐ **vSmart = "tôi NGHĨ"** ·
> ⭐ **vBond = "tôi GIỚI THIỆU"** · ⭐ **vEdge/cEdge = "tôi CHẠY"**.

⭐ *(Trên Cisco Catalyst SD-WAN đời mới, tên gọi đã đổi: **SD-WAN Manager** (vManage) ·
**SD-WAN Controller** (vSmart) · **SD-WAN Validator** (vBond). ⭐ **Đề vẫn dùng tên cũ — biết cả hai.**)*

### 7.3 ⭐⭐ OMP, TLOC, Color — ba thuật ngữ phải hiểu

| Thuật ngữ | Nghĩa |
|---|---|
| ⭐⭐ **OMP** (Overlay Management Protocol) | ⭐ **"BGP của overlay"** — chạy **giữa edge và vSmart** trong đường hầm DTLS/TLS. ⭐ Quảng bá **3 loại route**: **OMP route** (prefix), **TLOC route** (điểm cuối transport), **Service route** (firewall/IPS ở site nào) |
| ⭐⭐ **TLOC** (Transport Locator) | ⭐ **"Chỗ cắm dây WAN"** — định danh bằng bộ ba: ⭐ **System IP + Color + Encapsulation** |
| ⭐⭐ **Color** | ⭐ **Nhãn dán cho từng đường WAN.** ⭐ **Private color** (`mpls`, `private1-6`) dùng **IP riêng** · ⭐ **Public color** (`biz-internet`, `public-internet`, `lte`) dùng **IP public sau NAT** |
| ⭐ **System IP** | ⭐ **Định danh duy nhất của router** — như `router-id`. Không phải interface thật |
| ⭐ **Site ID** | Số hiệu site. ⭐ **Cùng Site ID thì KHÔNG dựng tunnel với nhau** |
| ⭐ **Organization Name** | ⭐ **Phải giống hệt** trên mọi thành phần, khớp với chứng thư |

> ⭐ **Ví dụ TLOC:** router `10.0.0.1` có 2 đường WAN → ⭐ **2 TLOC**:
> `(10.0.0.1, mpls, ipsec)` và `(10.0.0.1, biz-internet, ipsec)`.
> ⭐ **Nhờ có 2 TLOC, vSmart biết có 2 đường tới site đó** và có thể ra chính sách chọn đường.

### 7.4 ⭐ Chính sách & Application-Aware Routing

| Loại chính sách | Áp ở đâu | Làm gì |
|---|---|---|
| ⭐ **Centralized Control Policy** | ⭐ **Trên vSmart** | ⭐ Điều khiển **route nào được quảng bá cho ai** → tạo hình topology (full-mesh / hub-spoke) |
| ⭐ **Centralized Data Policy** | ⭐ Cấu hình ở vSmart, ⭐ **thực thi ở edge** | Chọn đường theo ứng dụng, NAT, service chaining |
| ⭐⭐ **AAR** (Application-Aware Routing) | vSmart → edge | ⭐⭐ **Định nghĩa SLA class** (loss/latency/jitter) → ⭐ **traffic tự đi đường nào ĐẠT SLA** |
| ⭐ **Localized Policy** | ⭐ **Trên chính edge** | ACL, QoS, route policy cục bộ |

> ⭐⭐ **AAR hoạt động thế nào:** ⭐ **BFD chạy trên MỌI tunnel IPsec**, liên tục đo
> ⭐ **loss / latency / jitter**. ⭐ Nếu đường MPLS vi phạm SLA của lớp Voice → ⭐ **traffic voice tự chuyển
> sang Internet**, còn traffic khác vẫn ở MPLS. ⭐ **Đây là điểm bán hàng lớn nhất của SD-WAN.**

⭐ **Onboarding thiết bị mới (ZTP/PnP):** cắm điện + mạng → router gọi về **PnP/ZTP server của Cisco** →
được chỉ tới ⭐ **vBond** → vBond xác thực (chứng thư + serial) → giới thiệu tới ⭐ **vManage** →
⭐ **tải template về** → tham gia overlay. ⭐ **Không cần kỹ sư đến tận nơi.**

### 7.5 ⭐ WAN truyền thống vs SD-WAN

| | ⭐ **WAN truyền thống** | ⭐⭐ **SD-WAN** |
|---|---|---|
| Đường truyền | MPLS là chính | ⭐ **MPLS + Internet + 4G/5G — dùng HẾT** |
| Chọn đường | ⭐ Theo **route/metric tĩnh** | ⭐⭐ **Theo ỨNG DỤNG + chất lượng đường THỰC TẾ** |
| Cấu hình | CLI từng thiết bị | ⭐ **Template tập trung** |
| Triển khai site mới | Kỹ sư đến tận nơi | ⭐ **ZTP** |
| Mã hóa | Phải tự dựng IPsec | ⭐ **Mặc định có, tự động quản lý khóa** |
| Ra Internet ở chi nhánh | Chạy vòng về HQ | ⭐ **DIA / Cloud OnRamp** |
| Nhìn thấy ứng dụng | 🔴 Gần như không | ⭐ **DPI, hiển thị theo app** |

---

## 📘 8. 🔴 ⭐⭐ SD-ACCESS (blueprint 1.5)

### 8.1 ⭐⭐ Nhắc lại nền tảng từ Module-08

> ⭐⭐ **Câu thần chú (đã học ở [Module-08 §8.5](Module-08-Virtualization-va-Overlay.md)):**
>
> | Tầng | Công nghệ | Vai trò |
> |---|---|---|
> | ⭐⭐ **Control plane** | ⭐ **LISP** | "Host này ở đâu?" — map **EID ↔ RLOC** |
> | ⭐⭐ **Data plane** | ⭐ **VXLAN** | Chở gói qua fabric, mang **VNI** + **SGT** |
> | ⭐⭐ **Policy plane** | ⭐ **TrustSec (SGT)** | "Ai được nói chuyện với ai" *(Module-10)* |
> | ⭐ **Nền** | ⭐ **VRF** | ⭐ **VN (Virtual Network) trong SD-Access CHÍNH LÀ VRF** |

### 8.2 ⭐⭐ Kiến trúc tổng

```
   ┌──────────────────┐        ┌──────────────────┐
   │ DNA CENTER    │◄──────►│    ISE        │   TẦNG ĐIỀU KHIỂN
   │ Design·Policy·   │        │  Identity &      │   (ngoài fabric)
   │ Provision·Assure │        │  SGT / 802.1X    │
   └────────┬─────────┘        └──────────────────┘
            │ (tự động hóa + giám sát)
   ═════════╪══════════════ FABRIC ══════════════════════════
            │
      ┌─────┴──────┐       ┌──────────────┐      ┌────────────────┐
      │ CONTROL │       │ BORDER    │      │ FABRIC WLC  │
      │ PLANE NODE │       │    NODE      │      │  + Fabric AP   │
      │ (LISP MS/MR)│      │ (ra ngoài)   │      └────────────────┘
      └────────────┘       └──────────────┘
            │                     │
      ┌─────┴─────────────────────┴──────┐
      │      EDGE NODES (LISP xTR)     │  ← nơi CẮM người dùng
      │      + Anycast Gateway         │
      └───────────────────────────────────┘
                    │
              PC / phone / AP / IoT
```

### 8.3 ⭐⭐ NĂM FABRIC ROLE — bảng PHẢI HỌC THUỘC

| Role | ⭐⭐ Làm gì | ⭐ Chạy gì |
|---|---|---|
| ⭐⭐ **Control Plane Node** | ⭐⭐ **Cơ sở dữ liệu "host nào ở đâu"** (HTDB). Nhận đăng ký từ edge, trả lời truy vấn | ⭐⭐ **LISP Map-Server / Map-Resolver** *(M08 §7)* |
| ⭐⭐ **Border Node** | ⭐ **Cửa ra vào của fabric** — nối fabric với thế giới bên ngoài (DC, Internet, mạng cũ) | ⭐ LISP PxTR + **VRF-lite handoff** |
| ⭐⭐ **Edge Node** | ⭐⭐ **Nơi endpoint CẮM VÀO.** Đăng ký EID với CP node, ⭐ **bọc/mở VXLAN**, ⭐ **cung cấp anycast gateway**, áp SGT | ⭐⭐ **LISP xTR** |
| ⭐ **Intermediate Node** | ⭐ **Chỉ chuyển gói IP của underlay** — ⭐ **KHÔNG biết gì về fabric** | Chỉ IP routing (IS-IS) |
| ⭐ **Fabric WLC + Fabric AP** | WLC tích hợp fabric · AP ở **fabric mode** | ⭐ Xem §7.5 — **có bẫy!** |
| **Extended Node** | Switch **không phải fabric** (VD switch công nghiệp IE) cắm sau edge node | — |
| **Fabric in a Box** | ⭐ **Một thiết bị làm CẢ 3 vai** (CP + Border + Edge) | ⭐ Cho site rất nhỏ |

⭐ **Ba loại Border Node:**

| Loại | Nối ra đâu |
|---|---|
| ⭐ **Internal Border** | ⭐ Ra mạng **ĐÃ BIẾT** (data center, mạng cũ) — quảng bá các prefix cụ thể vào fabric |
| ⭐ **External Border** | ⭐ Ra mạng **KHÔNG BIẾT** (Internet) — ⭐ **là "default exit"**, không cần import route |
| ⭐ **Anywhere / Internal+External** | Làm cả hai |

> 🔴 ⭐⭐ **Bốn câu đề chắc chắn hỏi:**
> 1. ⭐ *"Control Plane Node chạy giao thức gì?"* → ⭐ **LISP (Map-Server/Map-Resolver)**
> 2. ⭐ *"Endpoint cắm vào node nào?"* → ⭐ **Edge Node** (là **xTR**)
> 3. ⭐ *"Node nào bọc gói VXLAN?"* → ⭐ **Edge Node** (và Border node ở chiều ra)
> 4. ⭐ *"Intermediate node có biết về fabric không?"* → 🔴 ⭐ **KHÔNG — nó chỉ định tuyến IP underlay**

### 8.4 ⭐⭐ Anycast Gateway — khái niệm hay nhất của SD-Access

```
   TẤT CẢ Edge Node đều dùng CÙNG một IP gateway VÀ CÙNG một MAC cho mỗi subnet

   Edge-1: SVI 10.10.10.1 / MAC 0000.0c9f.f001   giống hệt
   Edge-2: SVI 10.10.10.1 / MAC 0000.0c9f.f001   giống hệt
   Edge-3: SVI 10.10.10.1 / MAC 0000.0c9f.f001   giống hệt

   Hệ quả: người dùng cắm ở ĐÂU cũng thấy gateway "ngay cạnh mình"
   → di chuyển khắp campus mà KHÔNG đổi IP, KHÔNG cần ARP lại, KHÔNG cần HSRP
```

| ⭐ Lợi ích | Chi tiết |
|---|---|
| ⭐⭐ **Mobility hoàn hảo** | Host đi bất cứ đâu trong fabric — ⭐ **IP và gateway không đổi** |
| ⭐ **Không cần FHRP** | ⭐ **Không HSRP, không VRRP** trong fabric — gateway **luôn cục bộ** |
| ⭐ **Không cần kéo VLAN** | Cùng subnet xuất hiện ở mọi edge mà ⭐ **không có L2 trải rộng thật** → **không STP xuyên fabric** |
| ⭐ **Định tuyến tối ưu** | Gói đi ra ngay tại edge, ⭐ **không phải chạy về distribution** |

> ⭐⭐ **So sánh giúp bạn nhớ:** mạng truyền thống dùng ⭐ **HSRP** để hai router **chia nhau** một IP ảo
> ở **một chỗ**. ⭐ **SD-Access dùng anycast gateway để TẤT CẢ switch cùng có một IP ở MỌI chỗ.**

### 8.5 ⭐⭐ SD-Access Wireless — chỗ có bẫy

```
   CONTROL plane:  Fabric AP ══ CAPWAP control ══► Fabric WLC   (như bình thường)

   DATA plane:  Fabric AP ══ VXLAN ══► Edge Node ══► fabric
                       KHÔNG có CAPWAP data tunnel về WLC!
```

> 🔴 ⭐⭐ **Đây là điểm khác biệt lớn nhất so với wireless truyền thống (Module-07B §4):**
> ⭐ Trong mô hình **Centralized/Local mode**, ⭐ **mọi traffic client tunnel về WLC** ("hairpinning").
> ⭐ Trong **SD-Access wireless**, ⭐⭐ **AP bọc thẳng traffic client vào VXLAN và đưa cho Edge Node** →
> ⭐ **traffic wireless đi cùng đường, cùng chính sách với traffic có dây.**
>
> ⭐ **Lợi ích:** ⭐ **wired và wireless dùng CHUNG một chính sách, chung một SGT, chung một VN** —
> ⭐ đây là mục tiêu *"policy nhất quán"* của SD-Access.

### 8.6 ⭐⭐ Segmentation: VN vs SGT

| | ⭐⭐ **VN** (Virtual Network) | ⭐⭐ **SGT** (Scalable Group Tag) |
|---|---|---|
| Gọi là | ⭐ **Macro-segmentation** | ⭐ **Micro-segmentation** |
| Thực chất là | ⭐⭐ **VRF** *(Module-08 §3)* | ⭐ Nhãn số gán cho nhóm người/thiết bị |
| Mang trong VXLAN bằng | ⭐ **VNI** | ⭐ **Trường SGT trong VXLAN-GPO header** |
| Cách ly | ⭐ **TUYỆT ĐỐI** — hai VN không thấy nhau *(trừ khi qua fusion router)* | ⭐ **Trong CÙNG một VN** — kiểm soát ai nói với ai |
| Ví dụ | `VN-NHANVIEN` · `VN-CAMERA` · `VN-KHACH` | Trong VN-NHANVIEN: `Ke_toan` không được nói với `Marketing` |
| Ai gán | Thiết kế mạng | ⭐ **ISE gán khi 802.1X xác thực** |

> ⭐⭐ **Cách nhớ:** ⭐ **VN = những TÒA NHÀ riêng biệt** (không có cửa nối nhau) ·
> ⭐ **SGT = quy định ai được vào PHÒNG nào trong cùng một tòa nhà.**

### 8.7 ⭐ Underlay, Overlay, Transit

| | Chi tiết |
|---|---|
| ⭐ **Underlay** | ⭐ **Mạng IP thuần đã định tuyến** giữa các fabric node. ⭐ Thường **routed access + IS-IS**. Dựng **thủ công** hoặc bằng ⭐ **LAN Automation** (DNAC dùng PnP tự dựng) |
| ⭐ **Overlay** | ⭐ **Fabric thật** — VXLAN chở VN + SGT chạy trên underlay |
| ⭐ **SD-Access Transit** | ⭐ Nối **nhiều fabric site** với nhau, ⭐ **GIỮ NGUYÊN VN và SGT** xuyên suốt |
| ⭐ **IP Transit** | ⭐ Nối ra mạng thường qua **VRF-lite handoff** tại border. 🔴 ⭐ **SGT bị MẤT** *(trừ khi dùng SXP hoặc inline tagging)* |
| ⭐ **Fusion Router** | ⭐ Router/firewall **ngoài fabric** làm nhiệm vụ **cho các VN nói chuyện với nhau** và truy cập **dịch vụ chung** (DNS, DHCP, AD) |

> 🔴 ⭐ **Bẫy thiết kế thật:** ⭐ **VN cách ly TUYỆT ĐỐI** → mọi thứ dùng chung (DHCP, DNS, AD, in ấn)
> ⭐ **phải đi vòng qua fusion router**. ⭐ **Quên thiết kế fusion router = fabric dựng xong nhưng không ai làm việc được.**

### 8.8 ⭐ DNA Center — bốn workflow

| Workflow | Làm gì |
|---|---|
| ⭐ **Design** | Cây site (khu vực/tòa nhà/tầng), thiết lập chung: DNS, DHCP, NTP, AAA, ⭐ **bản đồ sàn cho wireless** |
| ⭐ **Policy** | ⭐ **Tạo VN, gán SGT, viết chính sách nhóm** *(đồng bộ với ISE)* |
| ⭐ **Provision** | ⭐ Đẩy cấu hình xuống thiết bị, gán fabric role, ⭐ **LAN Automation** |
| ⭐⭐ **Assurance** | ⭐ Health score, ⭐ **Path Trace**, ⭐ **Network Time Travel**, Client 360 → ⭐ **Module-11** |

⭐ **Yêu cầu triển khai thực tế:** ⭐ **DNA Center** (appliance, đắt) + ⭐ **ISE** + ⭐ **switch đủ đời**
(Catalyst 9000 series) + ⭐ **license DNA Advantage**. ⭐ **Không phải mạng nào cũng làm được SD-Access.**

### 8.9 ⭐⭐ SD-WAN vs SD-Access — đừng lẫn hai cái

| | ⭐ **SD-WAN** | ⭐ **SD-Access** |
|---|---|---|
| ⭐ Phạm vi | ⭐⭐ **WAN — giữa các SITE** | ⭐⭐ **CAMPUS — bên trong một site** |
| Controller | ⭐ **vManage / vSmart / vBond** | ⭐ **DNA Center + ISE** |
| Control plane | ⭐ **OMP** | ⭐ **LISP** |
| Data plane | ⭐ **IPsec** (hoặc GRE) | ⭐ **VXLAN** |
| Policy | Chính sách tập trung trên vSmart | ⭐ **TrustSec / SGT** (qua ISE) |
| Giải quyết | ⭐ Chi phí & chất lượng đường WAN | ⭐ Phân đoạn & chính sách nhất quán trong campus |

> 🔴 ⭐⭐ **Đây là bảng dễ mất điểm nhất Domain 1.0** vì hai cái tên giống nhau.
> ⭐ **Mẹo:** ⭐ **WAN = giữa các thành phố (OMP + IPsec)** · ⭐ **Access = trong tòa nhà (LISP + VXLAN)**.

---

## 📘 9. 🔴 ⭐⭐ QoS (blueprint 1.6)

### 9.1 ⭐ Bốn thứ QoS chống lại

| Vấn đề | Nghĩa | ⭐ Ngưỡng cho **VOICE** *(phải nhớ!)* |
|---|---|---|
| ⭐ **Latency / Delay** | Thời gian đi một chiều | ⭐⭐ **≤ 150 ms** |
| ⭐ **Jitter** | Độ dao động của latency | ⭐⭐ **≤ 30 ms** |
| ⭐ **Loss** | Tỉ lệ mất gói | ⭐⭐ **≤ 1 %** |
| **Bandwidth** | Băng thông khả dụng | ⭐ **~21–320 kbps/cuộc gọi** (tùy codec + overhead) |

> 🔴 ⭐⭐ **BA CON SỐ `150 / 30 / 1` LÀ THỨ ĐƯỢC HỎI NHIỀU NHẤT TRONG CẢ MỤC QoS.**
> ⭐ **Nhớ: "một trăm năm mươi / ba mươi / một phần trăm".**
>
> ⭐ *(Video tương tác, tham khảo: latency ~200–400 ms · jitter ~30–50 ms · loss ~0.1–1 %.)*

### 9.2 ⭐⭐ Ba mô hình QoS

| Mô hình | Cách hoạt động | ⭐ Thực tế |
|---|---|---|
| **Best Effort** | ⭐ Không làm gì — FIFO | Mặc định. Không đảm bảo gì |
| ⭐ **IntServ** (Integrated Services) | ⭐ **RSVP đặt chỗ trước** cho từng luồng, **end-to-end** | 🔴 ⭐ **Không mở rộng được** (mỗi luồng một trạng thái) — hầu như không dùng |
| ⭐⭐ **DiffServ** (Differentiated Services) | ⭐⭐ **Đánh dấu gói thành các LỚP**, mỗi thiết bị tự xử theo lớp (**PHB**) | ⭐⭐ **CÁI MÀ MỌI NGƯỜI DÙNG — và cái ENCOR hỏi** |

> ⭐ **Cách nhớ:** ⭐ **IntServ = đặt bàn trước nhà hàng** (chắc chắn có chỗ, nhưng nhà hàng phải nhớ từng khách).
> ⭐⭐ **DiffServ = phân hạng vé máy bay** (hạng thương gia lên trước — ⭐ **hãng không cần nhớ tên bạn,
> chỉ cần nhìn tấm vé**).

### 9.3 ⭐⭐ Classification & Marking

| Nơi đánh dấu | Trường | Số bit | Giá trị | ⭐ Ghi chú |
|---|---|:---:|---|---|
| ⭐ **Layer 2** | ⭐ **CoS** (802.1p trong tag 802.1Q) | ⭐ **3 bit** | 0–7 | 🔴 ⭐⭐ **CHỈ tồn tại trên TRUNK!** ⭐ Access port không có tag → **không có CoS** |
| ⭐⭐ **Layer 3** | ⭐⭐ **DSCP** (6 bit đầu của trường ToS/TC) | ⭐ **6 bit** | 0–63 | ⭐⭐ **Cái chính. Sống sót suốt hành trình L3** |
| Layer 3 (cũ) | **IP Precedence** | 3 bit | 0–7 | ⭐ 3 bit đầu của DSCP. ⭐ `CSx` chính là tương thích ngược với IP Prec |
| MPLS | **EXP / TC** | 3 bit | 0–7 | Trong nhãn MPLS |
| ⭐ **Wireless** | ⭐ **UP** (User Priority, 802.11e/WMM) | 3 bit | 0–7 | ⭐ Xem §8.7 |

#### ⭐⭐ Bảng DSCP phải nhớ

| Tên PHB | ⭐ DSCP | Dùng cho |
|---|:---:|---|
| ⭐⭐ **EF** (Expedited Forwarding) | ⭐⭐ **46** | ⭐⭐ **VOICE** — giá trị được hỏi nhiều nhất |
| **CS7** | 56 | Dành riêng cho mạng (ít dùng) |
| ⭐ **CS6** | ⭐ **48** | ⭐ **Network Control** — OSPF/BGP/EIGRP/HSRP |
| **CS5** | 40 | Broadcast video |
| **CS4** | 32 | Realtime interactive |
| ⭐ **AF41** | ⭐ **34** | ⭐ **Multimedia conferencing** (video call) |
| ⭐ **AF31** | ⭐ **26** | Multimedia streaming |
| ⭐ **CS3** | ⭐ **24** | ⭐ **Call signaling** (SIP/SCCP) |
| **CS2** | 16 | OAM (quản trị) |
| **AF21** | 18 | Transactional data |
| **AF11** | 10 | Bulk data |
| ⭐ **CS1** | ⭐ **8** | ⭐ **Scavenger** — thấp hơn cả best-effort (P2P, backup) |
| ⭐⭐ **DF / BE** | ⭐⭐ **0** | ⭐ **Best Effort** — mặc định |

⭐⭐ **Công thức tính AF — học công thức, khỏi học thuộc bảng:**
```
   AFxy  →  DSCP = 8x + 2y
      x = LỚP (1–4), càng cao càng ưu tiên
      y = XÁC SUẤT BỊ VỨT (1–3), càng cao càng DỄ BỊ VỨT khi nghẽn

   AF41 = 8(4) + 2(1) = 34 ✓
   AF31 = 8(3) + 2(1) = 26 ✓
   AF23 = 8(2) + 2(3) = 22
```
⭐⭐ **Và CSx = 8x:** CS1=8 · CS3=24 · CS6=48 · CS7=56.

> 🔴 ⭐⭐ **BẪY về `y` trong AF:** ⭐ **y CAO = DỄ BỊ VỨT HƠN**, không phải "ưu tiên cao hơn".
> ⭐ AF11 **an toàn hơn** AF13 dù cùng lớp 1.

#### ⭐⭐ Trust Boundary

```
   NGUYÊN TẮC: đặt trust boundary CÀNG GẦN NGUỒN CÀNG TỐT

   [IP Phone]──[PC]     [Access SW]        [Dist]      [Core]
       TIN            TIN phone         tin         tin
                         KHÔNG tin PC
                         ↑
                    ĐÂY LÀ TRUST BOUNDARY
```
| ⭐ Quy tắc | Vì sao |
|---|---|
| ⭐ **Tin điện thoại IP** (nhận qua CDP) | Thiết bị của công ty, đánh dấu đúng |
| 🔴 ⭐ **KHÔNG tin PC người dùng** | ⭐ **Ai cũng có thể tự đặt DSCP EF cho game của mình** → cướp hết ưu tiên của voice |
| ⭐ Không tin thì làm gì | ⭐ **Ghi đè về 0** (`DF`), hoặc phân loại lại bằng ACL/NBAR |

### 9.4 ⭐⭐ Queuing — xếp hàng

| Cơ chế | Cách hoạt động | ⭐ Ghi chú |
|---|---|---|
| **FIFO** | Ai tới trước đi trước | Mặc định, không có QoS |
| **WFQ** | Chia đều theo luồng | Tự động, không cấu hình được chi tiết |
| ⭐ **CBWFQ** | ⭐ **Bảo đảm % băng thông cho mỗi CLASS** | ⭐ Có bảo đảm, ⭐ **nhưng không bảo đảm ĐỘ TRỄ** |
| ⭐⭐ **LLQ** (Low Latency Queuing) | ⭐⭐ **CBWFQ + một PRIORITY QUEUE được phục vụ TRƯỚC TIÊN** | ⭐⭐ **BẮT BUỘC CHO VOICE** — chỉ nó đảm bảo được độ trễ |

> 🔴 ⭐⭐ **Hai điều phải nhớ về LLQ:**
> 1. ⭐ **Voice PHẢI dùng LLQ** (`priority`), không phải `bandwidth` — ⭐ vì CBWFQ đảm bảo **băng thông**
>    nhưng **không đảm bảo ĐỘ TRỄ**, mà voice sợ trễ hơn sợ thiếu băng thông.
> 2. ⭐⭐ **Priority queue nên ≤ 33% băng thông link.** ⭐ Nếu để quá lớn → ⭐ **các lớp khác bị bỏ đói**
>    (priority queue có **policer** ngầm, nhưng thiết kế vẫn sai).

### 9.5 ⭐⭐ Congestion Avoidance — WRED

| | ⭐ **Tail Drop** *(mặc định)* | ⭐⭐ **WRED** (Weighted Random Early Detection) |
|---|---|---|
| Cách làm | ⭐ Hàng đợi đầy → ⭐ **vứt HẾT gói mới tới** | ⭐ **Vứt NGẪU NHIÊN một số gói TRƯỚC KHI đầy** |
| 🔴 Hậu quả | ⭐⭐ **TCP Global Synchronization** — tất cả luồng TCP **cùng lúc** giảm tốc rồi **cùng lúc** tăng tốc → ⭐ **băng thông dao động hình răng cưa, lãng phí** | ⭐ Chỉ vài luồng giảm tốc mỗi lần → ⭐ **link được dùng ĐỀU và đầy hơn** |
| "Weighted" nghĩa là | — | ⭐ **Vứt gói có xác suất-vứt CAO trước** (AF13 trước AF11) |

> 🔴 ⭐⭐ **Hai điều phải nhớ về WRED:**
> 1. ⭐ **WRED chỉ có tác dụng với TCP** (vì TCP mới có cơ chế giảm tốc khi mất gói).
>    ⭐ **UDP không quan tâm** — vứt gói UDP chỉ làm hỏng chất lượng, không làm nó chậm lại.
> 2. 🔴 ⭐⭐ **TUYỆT ĐỐI KHÔNG áp WRED lên hàng đợi VOICE (LLQ).** ⭐ Voice là UDP và **không chịu được mất gói**.

### 9.6 ⭐⭐ Policing vs Shaping — bảng đề hỏi rất nhiều

```
   POLICING                            SHAPING
   Vượt tốc độ → VỨT (hoặc hạ mark)     Vượt tốc độ → CHO VÀO HÀNG ĐỢI, thả từ từ

   Mbps                                   Mbps
    │ ╱╲    ╱╲   ← cắt ngọn             │ ___________  ← làm phẳng
    │╱  ╲__╱  ╲                            │╱
    ├─────────── CIR                       ├─────────── CIR
    └──────────► t                         └──────────► t
```

| | ⭐⭐ **Policing** | ⭐⭐ **Shaping** |
|---|---|---|
| ⭐ Gói vượt hạn mức | ⭐⭐ **VỨT** (hoặc **re-mark** xuống lớp thấp) | ⭐⭐ **BUFFER rồi gửi sau** |
| ⭐ **Chiều áp dụng** | ⭐⭐ **Inbound VÀ outbound** | ⭐⭐ **Outbound** (thực tế gần như luôn thế) |
| ⭐ Ảnh hưởng độ trễ | ⭐ **Không thêm trễ** (vứt là xong) | 🔴 ⭐ **THÊM trễ và jitter** (vì phải chờ trong buffer) |
| ⭐ Cần buffer? | ❌ Không | ⭐ **Có — cần bộ nhớ** |
| ⭐ Với TCP | 🔴 **Gây retransmit nhiều** | ⭐ **Thân thiện với TCP hơn** |
| ⭐⭐ **Dùng khi** | ⭐ **Ép giới hạn** (nhà mạng giới hạn khách; chặn traffic rác) · ⭐ **traffic INBOUND** | ⭐⭐ **Khớp tốc độ với nhà mạng** để tránh bị **nhà mạng policing** (VD link vật lý 1 Gbps nhưng hợp đồng chỉ 200 Mbps) |

> ⭐⭐ **Câu chốt:** ⭐ **"Policing VỨT, Shaping CHỜ."**
> ⭐ **"Policing làm được cả hai chiều, Shaping chỉ chiều RA."**
>
> 🔴 ⭐⭐ **Use case kinh điển của shaping:** ⭐ **cổng vật lý 1 Gbps nhưng nhà mạng chỉ bán 200 Mbps.**
> ⭐ Không shape → router bắn 1 Gbps → ⭐ **nhà mạng policing và VỨT ngẫu nhiên (vứt cả gói voice!)**.
> ⭐ **Shape xuống 200 Mbps ở router → mình tự quyết gói nào bị chờ → voice vẫn được ưu tiên.**

⭐ **Token bucket (chỉ cần hiểu ý):** ⭐ **CIR** (tốc độ cam kết) · ⭐ **Bc** (burst cho phép mỗi chu kỳ) ·
⭐ **Be** (burst vượt mức). ⭐ Có token thì gói được đi, hết token thì bị vứt/chờ.

### 9.7 ⭐⭐ Wireless QoS

| Khái niệm | Chi tiết |
|---|---|
| ⭐⭐ **WMM** (Wi-Fi Multimedia) | ⭐ Triển khai thực tế của **802.11e**. ⭐ **Bắt buộc** cho Wi-Fi 4 trở lên |
| ⭐⭐ **4 Access Category** | ⭐ **AC_VO** (Voice) · **AC_VI** (Video) · **AC_BE** (Best Effort) · **AC_BK** (Background) |
| ⭐ **Cách nó ưu tiên** | ⭐ **Không phải hàng đợi nghiêm ngặt** — ⭐ lớp cao được ⭐ **thời gian chờ ngắn hơn và backoff nhỏ hơn** → ⭐ **xác suất chiếm sóng cao hơn** *(nhớ CSMA/CA — [07A §2.8](Module-07A-Wireless-RF-802.11-AP-Antenna.md))* |
| ⭐ **UP → AC** | UP 6,7 → **Voice** · UP 4,5 → **Video** · UP 0,3 → **Best Effort** · UP 1,2 → **Background** |

⭐⭐ **Hai điểm về QoS trong mạng có WLC — hay ra đề:**

| # | Điểm |
|:---:|---|
| 1 | ⭐⭐ **CAPWAP phải mang QoS ra HEADER NGOÀI.** ⭐ Traffic client nằm **bên trong** tunnel CAPWAP → mạng có dây **không nhìn thấy** DSCP bên trong. ⭐ **AP/WLC phải COPY DSCP ra header CAPWAP ngoài**, nếu không QoS **vô hình** trên đoạn AP↔WLC |
| 2 | ⭐ **Ánh xạ DSCP ↔ UP.** ⭐ Cách cũ (`DSCP >> 3`) khiến ⭐ **EF (46) rơi vào UP 5 = hàng đợi VIDEO**, không phải voice! ⭐ **RFC 8325** sửa lại — ⭐ Cisco hiện khuyến nghị theo **RFC 8325** |

### 9.8 ⭐ MQC — cấu hình QoS bằng 3 bước

> ⭐ Blueprint 1.6 chỉ nói *"Describe"*, nhưng ⭐ **MQC rất đơn giản và giúp bạn hiểu bản chất** —
> ⭐ **đáng bỏ 30 phút lab** (§10.2).

```
! ═══ ① CLASS-MAP — "nhận diện traffic" ═══
class-map match-all VOICE
 match dscp ef
class-map match-all SIGNALING
 match dscp cs3
class-map match-any VIDEO
 match dscp af41 af42 af43
class-map match-all SCAVENGER
 match dscp cs1

! ═══ ② POLICY-MAP — "làm gì với nó" ═══
policy-map WAN-OUT
 class VOICE
  priority percent 10           ! LLQ — hàng đợi ưu tiên tuyệt đối
 class SIGNALING
  bandwidth percent 5              ! CBWFQ — bảo đảm băng thông
 class VIDEO
  bandwidth percent 25
  random-detect dscp-based         ! WRED (KHÔNG áp lên class VOICE!)
 class SCAVENGER
  bandwidth percent 1              ! bóp gần chết
 class class-default
  fair-queue
  random-detect

! ═══ ③ SERVICE-POLICY — "áp lên đâu" ═══
interface GigabitEthernet0/0
 service-policy output WAN-OUT

! ═══ Shaping (hay dùng lồng nhau: shape ngoài, queue trong) ═══
policy-map SHAPE-200M
 class class-default
  shape average 200000000          ! 200 Mbps
  service-policy WAN-OUT           ! "hierarchical QoS" — queue BÊN TRONG shaper

! ═══ Verify ═══
show policy-map interface GigabitEthernet0/0     ! lệnh quan trọng nhất
show class-map
show policy-map
```

⭐ **AutoQoS:** `auto qos voip cisco-phone` / `auto qos trust` — ⭐ Cisco tự sinh cấu hình QoS theo best practice.
⭐ **Rất hay để bắt đầu**, sau đó chỉnh tay.

### 9.9 ⭐ Mô hình 12 lớp của Cisco (chỉ cần nhận diện)

| Lớp | ⭐ Marking | Hàng đợi |
|---|---|---|
| ⭐ **Voice** | ⭐ **EF (46)** | ⭐⭐ **LLQ (priority)** |
| Broadcast Video | CS5 | Priority hoặc CBWFQ |
| Realtime Interactive | CS4 | Priority hoặc CBWFQ |
| ⭐ Multimedia Conferencing | ⭐ **AF41** | CBWFQ + WRED |
| Multimedia Streaming | AF31 | CBWFQ + WRED |
| ⭐ **Network Control** | ⭐ **CS6** | CBWFQ |
| ⭐ **Signaling** | ⭐ **CS3** | CBWFQ |
| OAM | CS2 | CBWFQ |
| Transactional Data | AF21 | CBWFQ + WRED |
| Bulk Data | AF11 | CBWFQ + WRED |
| ⭐ **Scavenger** | ⭐ **CS1** | ⭐ **Bóp tối thiểu** |
| ⭐ **Best Effort** | ⭐ **DF (0)** | Phần còn lại |

> ⭐ **Không cần thuộc cả 12 dòng.** ⭐ **Thuộc 5 dòng in đậm là đủ cho đề:**
> ⭐ **EF=46 (voice) · CS3=24 (signaling) · CS6=48 (network control) · AF41=34 (video call) · CS1=8 (scavenger) · DF=0.**

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> ### 👉 **[LAB 09 — Tuần 15: Thiết kế & QoS](Module-09-LAB.md)**

> ⭐ **Domain 1.0 không có mục nào bắt cấu hình** — toàn *Explain / Analyze / Describe*.
> Nên lab ở đây chủ yếu là **lab-trên-giấy**, đúng dạng câu hỏi của đề.

| LAB | Nội dung | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|---|---|---|---|
| **A** | ⭐⭐ Chọn thiết kế (10 tình huống) | §2.1 ba vai trò trong công ty | §3 · §5 |
| **B** | QoS trên EVE-NG (MQC, LLQ, shaping) | §2.4 sân bay giờ cao điểm | §9 |
| **C** | ⭐⭐ Điền bảng SD-WAN / SD-Access | §2.2 công ty vận tải · §2.3 cửa ở mọi bức tường | §7 · §8 |
| **D** | Nhìn DNA Center & vManage thật | — | §7 · §8 |

> ⭐ **LAB C là bài đáng làm nhất module.** Nếu bạn điền được **từ trí nhớ** bảng
> 4 thành phần SD-WAN (vManage/vSmart/vBond/cEdge) và 5 fabric role SD-Access
> (Control Plane/Border/Edge/Intermediate/Fabric WLC), bạn đã nắm phần lớn
> câu hỏi của mục **1.4** và **1.5** — hai mục chiếm nhiều điểm nhất Domain 1.0.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Module này **vốn đã là** module kiến trúc. Phần 4 ở đây làm việc khác: **gộp mọi thứ lại
> thành một bức tranh doanh nghiệp hoàn chỉnh**, và chỉ ra chỗ hai giải pháp SD-* gặp nhau.

### 4.1 Bản đồ: SD-WAN và SD-Access gặp nhau ở đâu

```
   ══════════ GIỮA CÁC SITE  →  SD-WAN ══════════

      Chi nhánh A ─────┐                    ┌───── Chi nhánh B
                       │  vManage (quản lý) │
                       ├─ vSmart  (OMP)     ┤
                       │  vBond   (gác cổng)│
      Trụ sở ──────────┘   Data plane: IPsec └───── Data center


   ══════════ TRONG MỘT CAMPUS  →  SD-ACCESS ══════════

      ┌──────────────────────────────────────────────┐
      │  DNA Center (tự động hoá) + ISE (danh tính)  │
      ├──────────────────────────────────────────────┤
      │  Control plane : LISP    "host X ở đâu"      │
      │  Data plane    : VXLAN   (mang VNI + SGT)    │
      │  Policy plane  : TrustSec                    │
      │  Nền           : VRF  (= Virtual Network)    │
      └──────────────────────────────────────────────┘

   🔴 HAI GIẢI PHÁP KHÁC NHAU — đừng lẫn:
      SD-WAN  = giữa các THÀNH PHỐ  (OMP + IPsec)
      SD-Access = trong một TÒA NHÀ (LISP + VXLAN)
```

### 4.2 Bảng gỡ rối — SD-WAN vs SD-Access

| | ⭐ **SD-WAN** | ⭐ **SD-Access** |
|---|---|---|
| Phạm vi | ⭐ **WAN — giữa các SITE** | ⭐ **CAMPUS — trong một site** |
| Controller | **vManage · vSmart · vBond** | **DNA Center + ISE** |
| Control plane | ⭐ **OMP** | ⭐ **LISP** |
| Data plane | ⭐ **IPsec** | ⭐ **VXLAN** |
| Policy | Chính sách tập trung trên vSmart | ⭐ **TrustSec / SGT** |
| Giải quyết | Chi phí & chất lượng đường WAN | Phân đoạn & chính sách nhất quán |

> ⭐ **Mẹo nhớ:** **W**AN = giữa các thành phố (**O**MP) · **A**ccess = trong tòa nhà (**L**ISP).

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐⭐ **vSmart KHÔNG chở dữ liệu** | Nó chỉ là control plane. Traffic người dùng đi **thẳng giữa các cEdge** qua IPsec. Và ⭐ **vBond là thành phần DUY NHẤT bắt buộc có IP public** |
| ⭐⭐ **SD-Access bỏ hẳn FHRP** | **Anycast gateway** cho phép *mọi* edge node cùng một IP+MAC → không còn Active/Standby. Đây là lý do Module-06A nói *"SD-Access không cần HSRP"* |
| 🔴 ⭐⭐ **VN cách ly TUYỆT ĐỐI** | Dựng SD-Access xong mà DHCP/DNS không chạy — vì dịch vụ chung **phải đi qua fusion router**. Đây là lỗi triển khai phổ biến nhất |

### 4.4 QoS — bốn cặp đối lập thay được cả mục §9

| | Cái này | vs | Cái kia |
|---|---|:---:|---|
| **Mô hình** | ⭐ **DiffServ** (đánh dấu theo lớp) | vs | IntServ (RSVP — không mở rộng được) |
| **Hàng đợi** | ⭐⭐ **LLQ** — đảm bảo **ĐỘ TRỄ** *(cho voice)* | vs | CBWFQ — chỉ đảm bảo **BĂNG THÔNG** |
| **Vượt tốc độ** | ⭐ **Policing** — **VỨT** *(in + out)* | vs | **Shaping** — **CHỜ** *(chỉ out)* |
| **Chống nghẽn** | ⭐ **WRED** — vứt sớm *(chỉ TCP)* | vs | Tail drop — gây **TCP global sync** |

⭐⭐ **Ba nhóm số phải thuộc:**
**Voice = 150 ms / 30 ms / 1 %** · **EF=46 · CS3=24 · CS6=48 · AF41=34 · CS1=8 · DF=0** *(`AFxy = 8x+2y`)*
· **priority queue ≤ 33%**

### 4.5 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| TrustSec/SGT *(policy plane)* | ⭐ Cấu hình **TrustSec, SGACL, SXP** | **Module-10 §8** |
| QoS marking, trust boundary | Đo chất lượng thật bằng **IP SLA (MOS, jitter)** | **Module-11 §7** |
| DNA Center 4 workflow | ⭐ **Assurance**: Path Trace, Network Time Travel | **Module-11 §9** |
| SD-WAN AAR (đo bằng BFD) | Nguyên lý giống **IP SLA + track** *(M03, M06A)* | — |

### 4.6 Vẽ lại để nhớ

> **Bài tập 20 phút, trên giấy. Đây là bài tập quan trọng nhất Module-09.**
>
> 1. Vẽ lại **cả hai** sơ đồ ở §4.1 **không nhìn tài liệu**
> 2. Điền bảng 4 thành phần SD-WAN và 5 fabric role SD-Access
> 3. Trả lời: *Traffic người dùng trong SD-WAN có đi qua vSmart không? Vì sao?*

<details>
<summary>Đáp án câu 3</summary>

🔴 ⭐⭐ **KHÔNG.**

**vSmart là CONTROL plane** — nó chạy **OMP** để phân phối **route, TLOC và chính sách**
cho các edge. Nhưng traffic người dùng đi **thẳng giữa các cEdge/vEdge** qua **IPsec tunnel**.

⭐ **Ẩn dụ:** vSmart là **điều độ viên** — ông cầm bản đồ và bảo từng xe đi đường nào,
**nhưng hàng hóa không đi qua bàn ông**.

*(Câu này là một trong ba câu đề hỏi đi hỏi lại về SD-WAN. Hai câu còn lại:
**thành phần nào cần IP public** → vBond · **ai chạy OMP** → vSmart.)*

</details>

---

## 💡 4.7 Thực chiến đi làm

| # | Tình huống thật | ⭐ Điều người mới làm sai | ⭐ Cách làm đúng |
|:---:|---|---|---|
| 1 | Mạng chậm, sếp bảo "mua switch core mạnh hơn" | Mua ngay | ⭐ Đo **oversubscription** và **utilization uplink** trước. ⭐ Thường nghẽn ở **access→dist**, không phải core |
| 2 | Đặt ACL chặn giữa các VLAN | Đặt trên Core cho "tiện" | 🔴 ⭐ **Đặt ở DISTRIBUTION.** Core phải nhanh và đơn giản |
| 3 | Nâng cấp IOS cho switch distribution | Reboot giữa ngày | ⭐ Có **StackWise/VSS + ISSU** thì làm được ít gián đoạn — ⭐ **nhưng vẫn nên làm ngoài giờ** |
| 4 | Triển khai QoS | Tin DSCP từ mọi thiết bị | 🔴 ⭐⭐ **Không tin PC người dùng.** ⭐ Đặt **trust boundary ở access switch**, chỉ tin **IP phone** |
| 5 | Voice rè, giật | Tăng băng thông WAN | ⭐ Thường **không phải thiếu băng thông** mà là ⭐ **thiếu LLQ**. ⭐ Kiểm tra 3 số **150/30/1** trước |
| 6 | Link 1 Gbps, hợp đồng 200 Mbps, hay mất gói | Đổ lỗi nhà mạng | ⭐⭐ **Shape xuống 200 Mbps ở router mình** — nếu không, ⭐ nhà mạng policing và **vứt ngẫu nhiên cả gói voice** |
| 7 | Bật WRED cho tất cả class | Cho "đồng bộ" | 🔴 ⭐ **KHÔNG áp WRED lên hàng đợi voice.** WRED chỉ có nghĩa với **TCP** |
| 8 | Wireless voice kém dù QoS trên dây đã chuẩn | Chỉnh QoS trên switch | ⭐⭐ **Kiểm tra CAPWAP có copy DSCP ra header ngoài không** (§8.7) — nếu không, ⭐ QoS **vô hình** trên đoạn AP↔WLC |
| 9 | Sếp hỏi "SD-WAN có thay được MPLS không" | Trả lời "có/không" | ⭐ Câu trả lời đúng: ⭐ **SD-WAN không thay MPLS — nó cho phép DÙNG CẢ HAI và tự chọn đường theo ứng dụng.** Nhiều nơi giữ MPLS nhỏ lại + thêm Internet |
| 10 | Muốn làm SD-Access | Mua DNA Center trước | ⭐ Kiểm tra trước: ⭐ **switch có đủ đời không (Cat9000)**, ⭐ **có ISE chưa**, ⭐ **license DNA Advantage**, và ⭐ **đã thiết kế fusion router chưa** |
| 11 | Dựng SD-Access xong, DHCP không hoạt động | Debug fabric | ⭐⭐ **VN cách ly tuyệt đối** → DHCP/DNS/AD là **dịch vụ chung**, phải đi qua ⭐ **fusion router**. ⭐ Đây là lỗi triển khai phổ biến nhất |
| 12 | Thiết kế location services | Đặt AP đều ở giữa trần | 🔴 ⭐ **Phải có AP ở CHU VI**, nếu không trilateration sai bét (§4.2) |

> 🔴 ⭐⭐ **Ba câu thần chú của module này:**
> 1. ⭐ **"ACL ở distribution. Core chỉ để chạy nhanh."**
> 2. ⭐ **"Voice = EF = LLQ. Và nhớ 150/30/1."**
> 3. ⭐ **"SD-WAN dùng OMP+IPsec giữa các site. SD-Access dùng LISP+VXLAN trong campus."**

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§13) |
> | Quên lệnh | **Hộp lệnh** (§13.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§12) + **Quiz** (§14) |
> | Gặp từ lạ | **Thuật ngữ** (§15) |
> | Tự chấm | **Đúc kết** (§16) |

---

## 🎓 12. BẪY TRONG ĐỀ ENCOR

| # | ⭐ Bẫy | ✅ Sự thật |
|:---:|---|---|
| 1 | "Nên đặt ACL/policy ở Core" | 🔴 ⭐ **DISTRIBUTION.** Core phải đơn giản và nhanh |
| 2 | "Collapsed core nghĩa là bỏ lớp access" | 🔴 ⭐ **Gộp CORE + DISTRIBUTION.** Access vẫn còn |
| 3 | "3-tier luôn tốt hơn 2-tier" | 🔴 ⭐ Chỉ cần khi có **nhiều khối distribution** (thường ≥3). Nhỏ mà 3-tier = **lãng phí** |
| 4 | "Spine-Leaf có link giữa các leaf" | 🔴 ⭐⭐ **KHÔNG có leaf–leaf, KHÔNG có spine–spine** |
| 5 | "Spine-Leaf tối ưu cho North-South" | 🔴 ⭐ **East-West.** North-South là mô hình campus 3-tier |
| 6 | "SSO và NSF là một" | 🔴 ⭐⭐ **SSO = chuyển sang supervisor dự phòng (control).** ⭐ **NSF = tiếp tục forward gói (data).** ⭐ **GR = hàng xóm giữ chỗ** |
| 7 | "vPC giống VSS/StackWise" | 🔴 ⭐ **vPC giữ HAI control plane riêng.** VSS/Stack gộp thành một |
| 8 | "Cloud-managed Wi-Fi nghĩa là data đi qua cloud" | 🔴 ⭐ **Meraki chỉ QUẢN LÝ ở cloud, DATA ra thẳng LAN** |
| 9 | "RSSI trilateration chính xác ~1 m" | 🔴 ⭐ **~5–10 m.** ⭐ **Hyperlocation (AoA) mới đạt ~1 m** |
| 10 | "Location chỉ cần AP dày ở giữa phòng" | 🔴 ⭐ **Phải có AP ở CHU VI** |
| 11 | "IaaS thì nhà cung cấp lo cả OS" | 🔴 ⭐ **IaaS: BẠN lo OS trở lên.** ⭐ PaaS mới lo hộ OS/runtime |
| 12 | "VPN qua Internet có SLA như Direct Connect" | 🔴 ⭐ **Không.** ⭐ Direct Connect/ExpressRoute có **SLA và độ trễ ổn định** |
| 13 | "Cloud luôn rẻ hơn on-prem" | 🔴 ⭐ Là **OpEx vs CapEx**, và ⭐ **phí egress** hay bị bỏ sót |
| 14 | 🔴 ⭐⭐ "Traffic người dùng đi qua vSmart" | 🔴 ⭐⭐ **KHÔNG. vSmart là CONTROL plane.** Data đi **thẳng giữa các edge** qua IPsec |
| 15 | "vManage cần IP public" | 🔴 ⭐⭐ **vBOND là thành phần duy nhất bắt buộc IP public** |
| 16 | "vBond phân phối route" | 🔴 ⭐ **vSmart phân phối route (OMP).** ⭐ vBond chỉ **xác thực + giới thiệu + phát hiện NAT** |
| 17 | "OMP chạy giữa các edge với nhau" | 🔴 ⭐ **OMP chạy giữa edge và vSmart** (như client–route reflector) |
| 18 | "TLOC chỉ là địa chỉ IP" | 🔴 ⭐ **TLOC = System IP + Color + Encapsulation** |
| 19 | "SD-WAN thay thế hoàn toàn MPLS" | 🔴 ⭐ Nó **dùng được cả MPLS lẫn Internet** và chọn theo ứng dụng |
| 20 | 🔴 ⭐⭐ "SD-Access dùng VXLAN làm control plane" | 🔴 ⭐⭐ **LISP = control · VXLAN = data · TrustSec = policy** |
| 21 | "Edge Node chạy LISP Map-Server" | 🔴 ⭐⭐ **Control Plane Node chạy MS/MR.** ⭐ **Edge Node là xTR** |
| 22 | "Intermediate node cần biết về fabric" | 🔴 ⭐ **Không** — nó chỉ định tuyến IP underlay |
| 23 | "SD-Access cần HSRP cho gateway" | 🔴 ⭐⭐ **Không — dùng ANYCAST GATEWAY** (cùng IP+MAC trên mọi edge) |
| 24 | "VN và SGT là một" | 🔴 ⭐⭐ **VN = VRF = macro** · ⭐ **SGT = micro, trong cùng một VN** |
| 25 | 🔴 ⭐ "SD-Access wireless: data vẫn CAPWAP về WLC" | 🔴 ⭐⭐ **KHÔNG.** ⭐ **Control là CAPWAP, nhưng DATA là VXLAN từ AP thẳng vào Edge Node** |
| 26 | "SD-WAN và SD-Access dùng chung controller" | 🔴 ⭐ **SD-WAN: vManage/vSmart/vBond** · ⭐ **SD-Access: DNA Center + ISE** |
| 27 | "IntServ là mô hình QoS phổ biến nhất" | 🔴 ⭐⭐ **DiffServ.** IntServ (RSVP) **không mở rộng được** |
| 28 | "CoS tồn tại trên mọi port" | 🔴 ⭐⭐ **CoS nằm trong tag 802.1Q → CHỈ có trên TRUNK** |
| 29 | "DSCP có 8 giá trị" | 🔴 ⭐ **6 bit → 64 giá trị (0–63).** ⭐ IP Precedence mới là 3 bit/8 giá trị |
| 30 | "EF = 26" | 🔴 ⭐⭐ **EF = 46.** ⭐ 26 là AF31 |
| 31 | "AF13 tốt hơn AF11" | 🔴 ⭐⭐ **y CAO = DỄ BỊ VỨT hơn.** AF11 an toàn hơn AF13 |
| 32 | "CBWFQ đảm bảo độ trễ thấp" | 🔴 ⭐⭐ **CBWFQ đảm bảo BĂNG THÔNG, không đảm bảo ĐỘ TRỄ.** ⭐ **Voice cần LLQ** |
| 33 | "Priority queue càng lớn càng tốt" | 🔴 ⭐ **≤ 33%** — lớn quá thì các class khác bị bỏ đói |
| 34 | 🔴 ⭐⭐ "Shaping vứt gói" | 🔴 ⭐⭐ **Shaping BUFFER rồi gửi sau.** ⭐ **Policing mới VỨT** |
| 35 | "Shaping làm được cả inbound" | 🔴 ⭐ **Shaping thực tế chỉ OUTBOUND.** ⭐ **Policing làm được cả hai chiều** |
| 36 | "WRED giúp cả TCP lẫn UDP" | 🔴 ⭐ **Chỉ TCP.** ⭐ Và 🔴 **không bao giờ áp lên hàng đợi voice** |
| 37 | "Tail drop tốt vì công bằng" | 🔴 ⭐ Nó gây ⭐ **TCP global synchronization** — băng thông dao động, lãng phí |
| 38 | "Trust boundary nên đặt ở core" | 🔴 ⭐⭐ **Càng GẦN NGUỒN càng tốt** — thường là **access switch** |
| 39 | "WMM có 8 access category" | 🔴 ⭐ **4: Voice · Video · Best Effort · Background** |
| 40 | "Voice chịu được 300 ms độ trễ" | 🔴 ⭐⭐ **≤ 150 ms một chiều** (jitter ≤30 ms, loss ≤1%) |

---

## 🐛 13. GỠ LỖI NHANH

### 13.1 ⭐ Hộp lệnh

```
═══ QoS (cái duy nhất gõ lệnh nhiều trong module này) ═══
show policy-map interface <intf>        ! LỆNH QUAN TRỌNG NHẤT — bộ đếm từng class
show policy-map
show class-map
show mls qos                            ! (switch đời cũ) QoS đã bật chưa
show mls qos interface <intf>            ! trust state của port
show platform hardware qos ...           ! (Cat9k) chi tiết phần cứng
show interface <intf> | include drops|queue

═══ Thiết kế / HA ═══
show interface <intf> | include rate|drops    ! đo oversubscription thực tế
show interfaces counters errors
show redundancy states                   ! SSO: ACTIVE / STANDBY HOT
show redundancy                          ! trạng thái supervisor
show switch                              ! StackWise: thành viên & vai trò
show switch stack-ports
show standby brief                       ! HSRP (M06A)
show etherchannel summary                ! (M02)
show power inline                        ! ngân sách PoE

═══ SD-Access / SD-WAN (chỉ để nhận biết — không cần thuộc) ═══
show lisp session                        ! trên fabric node
show lisp instance-id <n> ipv4 database
show device-tracking database
show sdwan control connections           ! trên cEdge: kết nối tới vBond/vSmart/vManage
show sdwan omp routes                    ! OMP routes
show sdwan omp tlocs                     ! TLOC
show sdwan bfd sessions                  ! đo loss/latency/jitter (nền của AAR)
```

### 13.2 ⭐⭐ Bảng: triệu chứng → nguyên nhân → cách sửa

| 🔴 Triệu chứng | ⭐ Nguyên nhân | ✅ Cách sửa |
|---|---|---|
| ⭐ **Mạng chậm giờ cao điểm, switch access "sạch"** | ⭐ **Nghẽn UPLINK** — oversubscription quá cao | ⭐ `show interface <uplink>` xem rate & drops · thêm uplink / EtherChannel |
| ⭐⭐ **Voice rè/giật nhưng băng thông còn dư** | ⭐⭐ **Thiếu LLQ** — voice đang xếp hàng cùng data | ⭐ `show policy-map interface` xem có `priority` cho class VOICE không |
| ⭐ **Voice tốt trong LAN, tệ qua WAN** | ⭐ Nhà mạng **policing** vì mình bắn quá tốc độ hợp đồng | ⭐⭐ **Shape ở router mình** xuống đúng tốc độ hợp đồng, lồng LLQ bên trong |
| ⭐ **QoS cấu hình rồi mà không có tác dụng** | (a) ⭐ **Chưa `service-policy` lên interface** · (b) sai chiều (in/out) · (c) ⭐ **traffic không khớp class-map** | ⭐ `show policy-map interface` — ⭐ **nếu bộ đếm class = 0 thì classification sai** |
| ⭐ **DSCP bị xóa về 0 khi qua switch** | ⭐ Port **không trust** · QoS bật nhưng chưa cấu hình trust | ⭐ `show mls qos interface` · đặt `trust dscp` hoặc `trust device cisco-phone` |
| ⭐ **DSCP đúng trên dây, sai trên wireless** | ⭐⭐ **CAPWAP không copy DSCP ra header ngoài** · ánh xạ DSCP↔UP sai | ⭐ Kiểm tra QoS profile trên WLC · dùng ánh xạ **RFC 8325** |
| ⭐ **PC người dùng "cướp" hết ưu tiên** | 🔴 ⭐ **Trust boundary đặt sai** — đang tin DSCP từ PC | ⭐ Đặt trust boundary ở **access switch**, chỉ tin **IP phone** |
| ⭐ **TCP throughput dao động hình răng cưa** | ⭐ **TCP global synchronization** do tail drop | ⭐ Bật **WRED** trên các class TCP (🔴 **không bật cho voice**) |
| ⭐ **Supervisor dự phòng không lên STANDBY HOT** | Lệch phiên bản IOS · chưa cấu hình SSO | ⭐ `show redundancy states` · đồng bộ version |
| ⭐ **SD-Access: có IP nhưng không tới được DNS/DHCP** | ⭐⭐ **VN cách ly tuyệt đối** — chưa có **fusion router** cho dịch vụ chung | ⭐ Cấu hình fusion router / VRF leaking tại border |
| ⭐ **SD-WAN: edge không lên control connection** | Sai **Organization Name** · chứng thư · ⭐ **vBond không reachable** · NTP lệch | ⭐ `show sdwan control connections` · kiểm tra **vBond có IP public** không |
| ⭐ **SD-WAN: AAR không chuyển đường** | ⭐ **BFD session down** hoặc chưa định nghĩa **SLA class** | ⭐ `show sdwan bfd sessions` · kiểm tra policy trên vSmart |

---

## 📝 14. QUIZ TỰ KIỂM TRA

**1.** Khi nào cần 3-tier thay vì 2-tier? Nên đặt ACL ở lớp nào?
<details><summary>Đáp án</summary>

⭐ **Cần 3-tier khi có NHIỀU KHỐI DISTRIBUTION** (Cisco thường lấy mốc **≥ 3**) — vì nối chúng trực tiếp
với nhau cần `n(n−1)/2` link, tăng rất nhanh. ⭐ **Core làm điểm tập trung.**

⭐ **ACL/policy đặt ở DISTRIBUTION** — ⭐ access thì quá nhiều thiết bị, ⭐ **core phải giữ đơn giản và nhanh.**
</details>

**2.** Vì sao Data Center dùng Spine-Leaf thay vì 3-tier?
<details><summary>Đáp án</summary>

⭐ **Vì traffic DC chủ yếu là EAST-WEST** (server↔server: app↔DB, VM↔VM, microservices), không phải North-South.

⭐ **Spine-Leaf cho:** ⭐ **luôn đúng 2 hop** giữa hai leaf bất kỳ → **độ trễ dự đoán được** ·
⭐ **không STP**, underlay routed + **ECMP dùng hết mọi đường** · ⭐ mở rộng bằng cách **thêm spine** (băng thông)
hoặc **thêm leaf** (số port).

🔴 ⭐ **Không có link leaf–leaf, không có link spine–spine.**
</details>

**3.** Phân biệt SSO, NSF, GR.
<details><summary>Đáp án</summary>

⭐ **SSO** — trong **một thiết bị**: đồng bộ trạng thái sang **supervisor dự phòng** → chuyển đổi không mất trạng thái *(control plane)*.
⭐ **NSF** — trong **một thiết bị**: ⭐ **tiếp tục FORWARD gói bằng FIB cũ** trong lúc control plane khởi động lại *(data plane)*.
⭐ **GR** — ở **hàng xóm**: ⭐ **không xóa route của bạn**, chờ bạn khôi phục.

⭐ **Nhớ:** *"não dự phòng đã thuộc bài (SSO) · chân vẫn chạy khi não reboot (NSF) · hàng xóm giả vờ không thấy (GR)"*.
</details>

**4.** Kể 6 mô hình triển khai WLAN. Mô hình nào cho 40 chi nhánh WAN hẹp?
<details><summary>Đáp án</summary>

⭐ **Autonomous · Centralized · Distributed (FlexConnect) · Embedded (EWC) · Cloud-managed · Remote branch (OEAP)**

⭐ **40 chi nhánh WAN hẹp → Distributed / FlexConnect với local switching** (+ local auth + FlexConnect Group
để sống sót khi đứt WAN).
</details>

**5.** Muốn định vị tài sản trong bệnh viện sai số dưới 2 m. Công nghệ gì? Yêu cầu thiết kế AP?
<details><summary>Đáp án</summary>

⭐⭐ **Cisco Hyperlocation (Angle of Arrival)** — ~1 m. *(RSSI trilateration chỉ 5–10 m; BLE beacon ~1–3 m nhưng cần app.)*

🔴 ⭐⭐ **Yêu cầu thiết kế:** ⭐ **phải có AP ở CHU VI (perimeter) khu vực, không chỉ ở giữa** —
trilateration cần **bao vây** mục tiêu.
</details>

**6.** SD-WAN: thành phần nào cần IP public? Thành phần nào chạy OMP? Traffic người dùng đi qua đâu?
<details><summary>Đáp án</summary>

⭐⭐ **IP public: vBOND** (thành phần duy nhất bắt buộc).
⭐⭐ **Chạy OMP: vSMART** (với các edge, như route reflector cho overlay).
⭐⭐ **Traffic người dùng: đi THẲNG giữa các cEdge/vEdge qua IPsec** — 🔴 ⭐ **KHÔNG qua vSmart.**
</details>

**7.** TLOC gồm những gì? Private color khác public color chỗ nào?
<details><summary>Đáp án</summary>

⭐⭐ **TLOC = System IP + Color + Encapsulation.**

⭐ **Private color** (`mpls`, `private1-6`) → dùng ⭐ **IP riêng** (mạng tin cậy, không NAT).
⭐ **Public color** (`biz-internet`, `public-internet`, `lte`) → dùng ⭐ **IP public sau NAT**.

⭐ Một router có 2 đường WAN → **2 TLOC** → vSmart biết có 2 đường tới site đó.
</details>

**8.** SD-Access: ba plane dùng công nghệ gì? Fabric role nào chạy LISP Map-Server?
<details><summary>Đáp án</summary>

⭐⭐ **Control = LISP · Data = VXLAN · Policy = TrustSec (SGT).** ⭐ Nền: **VRF (= VN)**.

⭐⭐ **Control Plane Node** chạy **LISP Map-Server/Map-Resolver** (cơ sở dữ liệu HTDB "host nào ở đâu").
⭐ **Edge Node là LISP xTR** (bọc/mở VXLAN, anycast gateway).
</details>

**9.** Anycast gateway là gì và nó thay thế cái gì?
<details><summary>Đáp án</summary>

⭐⭐ **TẤT CẢ Edge Node dùng CÙNG một IP gateway VÀ CÙNG một MAC cho mỗi subnet.**

⭐ **Kết quả:** host cắm ở đâu cũng thấy gateway **ngay cạnh mình** → ⭐ **di chuyển khắp fabric mà
không đổi IP, không cần ARP lại**, và ⭐ **định tuyến tối ưu ngay tại edge**.

⭐⭐ **Nó thay thế FHRP (HSRP/VRRP)** — ⭐ **SD-Access không cần HSRP trong fabric.**
</details>

**10.** SD-Access wireless: data plane của client đi đường nào?
<details><summary>Đáp án</summary>

⭐⭐ **CONTROL plane: CAPWAP từ Fabric AP về Fabric WLC** (như bình thường).
⭐⭐ **DATA plane: Fabric AP bọc traffic client vào VXLAN và đưa THẲNG cho Edge Node** —
🔴 ⭐⭐ **KHÔNG có CAPWAP data tunnel về WLC.**

⭐ **Lợi ích:** wired và wireless dùng **chung VN, chung SGT, chung chính sách**.
</details>

**11.** VN và SGT khác nhau thế nào? Cho ví dụ mỗi cái.
<details><summary>Đáp án</summary>

⭐⭐ **VN (Virtual Network) = VRF = MACRO-segmentation** — cách ly **tuyệt đối**, mang bằng **VNI**.
⭐ VD: `VN-NHANVIEN` · `VN-CAMERA` · `VN-KHACH` — camera **không bao giờ** thấy máy nhân viên.

⭐⭐ **SGT = MICRO-segmentation TRONG cùng một VN** — mang trong **VXLAN-GPO header**, ISE gán khi 802.1X.
⭐ VD: trong `VN-NHANVIEN`, SGT `ThucTapSinh` không truy cập được server có SGT `Luong`.

⭐ **Nhớ:** ⭐ **VN = những TÒA NHÀ riêng · SGT = quyền vào PHÒNG trong cùng tòa nhà.**
</details>

**12.** Ngưỡng chất lượng cho Voice: latency, jitter, loss?
<details><summary>Đáp án</summary>

⭐⭐ **Latency ≤ 150 ms (một chiều) · Jitter ≤ 30 ms · Loss ≤ 1 %.**

⭐ Băng thông ~21–320 kbps/cuộc gọi tùy codec + overhead.
⭐ **Ba con số 150/30/1 là thứ được hỏi nhiều nhất trong mục QoS.**
</details>

**13.** DSCP của Voice, Signaling, Network Control, Video call, Scavenger? Công thức AF?
<details><summary>Đáp án</summary>

⭐ **Voice = EF = 46** · ⭐ **Signaling = CS3 = 24** · ⭐ **Network Control = CS6 = 48** ·
⭐ **Video conferencing = AF41 = 34** · ⭐ **Scavenger = CS1 = 8** · **Best Effort = DF = 0**

⭐⭐ **Công thức: `AFxy → DSCP = 8x + 2y`** · **`CSx → DSCP = 8x`**
🔴 ⭐ **y CAO = DỄ BỊ VỨT hơn** (AF11 an toàn hơn AF13).
</details>

**14.** Vì sao voice phải dùng LLQ chứ không phải CBWFQ? Priority queue nên tối đa bao nhiêu?
<details><summary>Đáp án</summary>

⭐⭐ **CBWFQ đảm bảo BĂNG THÔNG nhưng KHÔNG đảm bảo ĐỘ TRỄ.** ⭐ Voice sợ **trễ và jitter** hơn sợ
thiếu băng thông (chỉ cần vài chục kbps).

⭐⭐ **LLQ = CBWFQ + priority queue được phục vụ TRƯỚC TIÊN** → đảm bảo được độ trễ.

⭐ **Priority queue nên ≤ 33% băng thông link** — lớn quá thì các class khác bị bỏ đói.
</details>

**15.** Policing vs Shaping: cái nào vứt, chiều nào áp dụng được, và use case kinh điển của shaping?
<details><summary>Đáp án</summary>

| | ⭐ **Policing** | ⭐ **Shaping** |
|---|---|---|
| Gói vượt | ⭐ **VỨT** (hoặc re-mark) | ⭐ **BUFFER, gửi sau** |
| Chiều | ⭐ **Inbound VÀ outbound** | ⭐ **Outbound** |
| Độ trễ | Không thêm | ⭐ **Thêm trễ + jitter** |

⭐⭐ **Use case kinh điển của shaping:** ⭐ **cổng vật lý 1 Gbps nhưng hợp đồng nhà mạng chỉ 200 Mbps.**
🔴 ⭐ Không shape → router bắn 1 Gbps → ⭐ **nhà mạng policing và vứt NGẪU NHIÊN (vứt cả voice)**.
⭐ Shape ở mình xuống 200 Mbps → ⭐ **mình tự quyết ai bị chờ** → lồng LLQ bên trong (hierarchical QoS).
</details>

**16.** WRED giải quyết vấn đề gì? Hai điều cấm kỵ khi dùng WRED?
<details><summary>Đáp án</summary>

⭐ **Giải quyết TCP global synchronization:** tail drop làm **tất cả** luồng TCP cùng lúc giảm tốc rồi cùng lúc
tăng tốc → ⭐ **băng thông dao động hình răng cưa, lãng phí link.**
⭐ WRED **vứt ngẫu nhiên vài gói TRƯỚC KHI hàng đợi đầy** → chỉ vài luồng giảm tốc → link được dùng đều.

⭐ **Hai điều cấm kỵ:**
1. 🔴 ⭐⭐ **KHÔNG áp WRED lên hàng đợi VOICE/LLQ** — voice là UDP và không chịu được mất gói
2. ⭐ **Đừng kỳ vọng WRED giúp UDP** — chỉ TCP mới có cơ chế giảm tốc khi mất gói
</details>

**17.** Trust boundary nên đặt ở đâu và vì sao không tin PC người dùng?
<details><summary>Đáp án</summary>

⭐ **Càng GẦN NGUỒN càng tốt — thường là ACCESS SWITCH.**

⭐ **Tin IP phone** (nhận diện qua CDP) vì đó là thiết bị công ty, đánh dấu đúng.
🔴 ⭐⭐ **KHÔNG tin PC người dùng** vì ⭐ **ai cũng có thể tự đặt DSCP EF cho game/torrent của mình** →
cướp hết ưu tiên của voice.

⭐ Không tin thì **ghi đè DSCP về 0 (DF)** hoặc phân loại lại bằng ACL/NBAR.
</details>

**18.** WMM có mấy access category? Vấn đề QoS đặc thù của mạng có WLC là gì?
<details><summary>Đáp án</summary>

⭐ **4 AC: Voice (AC_VO) · Video (AC_VI) · Best Effort (AC_BE) · Background (AC_BK).**
⭐ Nó ưu tiên bằng cách cho lớp cao **thời gian chờ và backoff ngắn hơn** → ⭐ xác suất chiếm sóng cao hơn
*(CSMA/CA — 07A §2.8)*.

⭐⭐ **Vấn đề đặc thù với WLC:** ⭐ **traffic client nằm BÊN TRONG tunnel CAPWAP** → mạng có dây
**không nhìn thấy** DSCP bên trong. ⭐ **AP/WLC phải COPY DSCP ra header CAPWAP NGOÀI**,
nếu không QoS **vô hình** trên đoạn AP↔WLC.

⭐ *(Điểm phụ: ánh xạ DSCP↔UP cũ (`DSCP>>3`) đẩy EF(46) vào UP 5 = hàng đợi VIDEO — RFC 8325 sửa lại.)*
</details>

**19.** SD-WAN và SD-Access khác nhau ở đâu? (5 điểm)
<details><summary>Đáp án</summary>

| | ⭐ **SD-WAN** | ⭐ **SD-Access** |
|---|---|---|
| Phạm vi | ⭐ **WAN — giữa các SITE** | ⭐ **CAMPUS — trong một site** |
| Controller | ⭐ **vManage/vSmart/vBond** | ⭐ **DNA Center + ISE** |
| Control plane | ⭐ **OMP** | ⭐ **LISP** |
| Data plane | ⭐ **IPsec** | ⭐ **VXLAN** |
| Policy | Chính sách tập trung trên vSmart | ⭐ **TrustSec / SGT** |

⭐ **Mẹo:** ⭐ **WAN = giữa các thành phố (OMP+IPsec)** · ⭐ **Access = trong tòa nhà (LISP+VXLAN)**.
</details>

**20.** `show policy-map interface Gi0/0` cho thấy class VOICE có `0 packets`. Nhưng người dùng vẫn kêu voice tệ. Chẩn đoán?
<details><summary>Đáp án</summary>

🔴 ⭐⭐ **Bộ đếm = 0 nghĩa là KHÔNG CÓ GÓI NÀO KHỚP class-map** → ⭐ **classification đang sai**, chứ không phải
queuing sai.

⭐ **Nguyên nhân khả dĩ:**
1. ⭐⭐ **Traffic voice không được đánh dấu EF** — ⭐ **trust boundary sai**, hoặc switch access đang **ghi đè DSCP về 0**
2. ⭐ Sai chiều — áp `output` nhưng đang đo traffic đi vào
3. ⭐ `class-map` khớp sai (VD `match dscp ef` nhưng điện thoại đánh `af41`)
4. ⭐ Policy chưa `service-policy` lên đúng interface

⭐ **Kiểm tra:** `show mls qos interface <access-port>` xem trust state · bắt gói xem DSCP thực tế của luồng voice.
</details>

---

## 📚 15. THUẬT NGỮ ANH–VIỆT

| English | Tiếng Việt / Giải thích |
|---|---|
| ⭐ **Access / Distribution / Core** | Ba lớp campus. ⭐ **Policy ở distribution, core giữ đơn giản** |
| ⭐ **Collapsed core (2-tier)** | Gộp core + distribution |
| ⭐ **Routed access** | L3 xuống tận access switch |
| ⭐ **Spine-Leaf** | Kiến trúc DC 2 tầng — ⭐ **luôn 2 hop, không leaf-leaf** |
| ⭐ **North-South / East-West** | User↔server / ⭐ **server↔server** |
| ⭐ **Oversubscription** | Tỉ lệ băng thông dưới/trên — ⭐ **20:1 access→dist, 4:1 dist→core** |
| ⭐ **SSO / NSF / GR** | Chuyển sup dự phòng / vẫn forward khi control reboot / hàng xóm giữ chỗ |
| ⭐ **StackWise / VSS / vPC** | Gộp switch thành một logic / ⭐ **vPC giữ 2 control plane riêng** |
| ⭐ **ISSU** | Nâng cấp phần mềm không gián đoạn |
| ⭐ **Autonomous / Centralized / Distributed / EWC / Cloud / OEAP** | 6 mô hình triển khai WLAN |
| ⭐ **Trilateration / AoA / Hyperlocation** | Định vị bằng RSSI (~5–10 m) / bằng **góc tới** (~1 m) |
| ⭐ **CMX / Cisco Spaces** | Nền tảng location analytics |
| ⭐ **IaaS / PaaS / SaaS** | Hạ tầng / Nền tảng / Phần mềm dạng dịch vụ |
| ⭐ **CapEx / OpEx** | Chi phí đầu tư một lần / chi phí vận hành định kỳ |
| ⭐ **Direct Connect / ExpressRoute** | Đường riêng tới cloud — ⭐ **có SLA** |
| ⭐ **Egress cost** | ⭐ Phí đưa dữ liệu RA khỏi cloud — chi phí ẩn hay bị quên |
| ⭐⭐ **vManage / vSmart / vBond / vEdge-cEdge** | Management / ⭐ **Control (OMP)** / ⭐ **Orchestration (IP public)** / Data |
| ⭐⭐ **OMP** | Overlay Management Protocol — ⭐ "BGP của overlay", chạy **edge ↔ vSmart** |
| ⭐⭐ **TLOC** | Transport Locator = ⭐ **System IP + Color + Encapsulation** |
| ⭐ **Color** | Nhãn đường WAN — ⭐ **private** (IP riêng) vs **public** (IP sau NAT) |
| ⭐ **System IP / Site ID / Org Name** | Định danh router / site / tổ chức (phải khớp chứng thư) |
| ⭐⭐ **AAR** | Application-Aware Routing — ⭐ chọn đường theo **SLA đo bằng BFD** |
| ⭐ **DIA / Cloud OnRamp** | Ra Internet thẳng tại chi nhánh / tối ưu đường tới cloud |
| ⭐ **ZTP / PnP** | Cắm điện là tự cấu hình |
| ⭐⭐ **DNA Center / ISE** | Bộ điều khiển SD-Access / máy chủ danh tính & chính sách |
| ⭐⭐ **Control Plane Node** | ⭐ **LISP MS/MR** — CSDL "host ở đâu" (HTDB) |
| ⭐⭐ **Border / Edge / Intermediate Node** | Cửa ra vào / ⭐ **nơi cắm endpoint (xTR)** / ⭐ **chỉ IP underlay** |
| ⭐ **Fabric WLC / Fabric AP** | WLC & AP tích hợp fabric — ⭐ **data là VXLAN, không CAPWAP** |
| ⭐ **Extended Node / Fabric in a Box** | Switch không-fabric sau edge / một hộp làm cả 3 vai |
| ⭐⭐ **Anycast Gateway** | ⭐ **Cùng IP+MAC gateway trên MỌI edge node** → thay thế FHRP |
| ⭐⭐ **VN / SGT** | ⭐ **VRF = macro-segmentation** / ⭐ **micro-segmentation trong VN** |
| ⭐ **Underlay / Overlay / Transit** | IP thuần / fabric VXLAN / cách nối nhiều fabric site |
| ⭐ **LAN Automation** | DNAC tự dựng underlay bằng PnP |
| ⭐ **Fusion Router** | Router/FW ngoài fabric — ⭐ **cho các VN nói chuyện & dùng dịch vụ chung** |
| ⭐ **Best Effort / IntServ / DiffServ** | Không QoS / RSVP đặt chỗ / ⭐ **đánh dấu theo lớp (cái ENCOR hỏi)** |
| ⭐ **PHB** (Per-Hop Behavior) | Cách mỗi thiết bị xử lý một lớp |
| ⭐ **CoS / DSCP / IP Precedence** | ⭐ **L2 3 bit (CHỈ trên trunk)** / ⭐ **L3 6 bit** / L3 3 bit (cũ) |
| ⭐⭐ **EF / AF / CS / DF** | ⭐ **EF=46 voice** · ⭐ `AFxy = 8x+2y` · ⭐ `CSx = 8x` · DF=0 |
| ⭐ **Trust boundary** | ⭐ Ranh giới tin marking — **càng gần nguồn càng tốt** |
| ⭐ **FIFO / WFQ / CBWFQ / LLQ** | Không QoS / chia đều / ⭐ **bảo đảm băng thông** / ⭐⭐ **bảo đảm ĐỘ TRỄ — cho voice** |
| ⭐ **Tail drop / WRED** | Đầy thì vứt hết / ⭐ **vứt sớm ngẫu nhiên, chống TCP global sync** |
| ⭐ **TCP Global Synchronization** | Mọi luồng TCP cùng giảm rồi cùng tăng tốc → lãng phí link |
| ⭐⭐ **Policing / Shaping** | ⭐ **VỨT, in+out** / ⭐ **BUFFER, chỉ out** |
| ⭐ **CIR / Bc / Be / Token bucket** | Tốc độ cam kết / burst / burst vượt / cơ chế đếm |
| ⭐ **MQC** | class-map → policy-map → ⭐ **service-policy** |
| ⭐ **Hierarchical QoS** | ⭐ Queue lồng bên trong shaper |
| ⭐⭐ **WMM / Access Category / UP** | QoS Wi-Fi — ⭐ **4 AC: VO/VI/BE/BK** · User Priority 0–7 |
| ⭐ **AutoQoS / NBAR** | Tự sinh cấu hình QoS / nhận diện ứng dụng sâu |

---

## 🎯 16. ĐÚC KẾT MODULE-09

**3 điều rút ra:**

1. ⭐⭐ **Thiết kế là chuyện "đặt đúng việc vào đúng lớp":** ⭐ **Access tiếp người dùng · Distribution
   đặt CHÍNH SÁCH và là ranh giới L2/L3 · Core CHỈ chạy nhanh** (🔴 ⭐ **không ACL ở core**).
   ⭐ **2-tier khi ít khối distribution, 3-tier khi nhiều (≥3).** ⭐ **DC thì khác hẳn: Spine-Leaf** vì
   ⭐ **traffic là East-West** và cần ⭐ **độ trễ đều (luôn 2 hop)**. ⭐ Và HA là **nhiều lớp chồng nhau**:
   ⭐ **SSO (não dự phòng) + NSF (chân vẫn chạy) + GR (hàng xóm giữ chỗ)**.

2. 🔴 ⭐⭐ **SD-WAN và SD-Access là hai thứ KHÁC NHAU, và đề gài đúng chỗ đó:**
   ⭐⭐ **SD-WAN = giữa các SITE**: ⭐ **vBond (IP public, giới thiệu) · vSmart (OMP, control, KHÔNG chở data) ·
   vManage (GUI) · cEdge (data qua IPsec)**, cộng ⭐ **TLOC = SystemIP+Color+Encap** và ⭐ **AAR đo bằng BFD**.
   ⭐⭐ **SD-Access = trong CAMPUS**: ⭐ **LISP (control) + VXLAN (data) + TrustSec (policy) trên nền VRF**,
   với ⭐ **Control Plane Node = LISP MS/MR · Edge Node = xTR + ANYCAST GATEWAY** (⭐ **thay thế HSRP**),
   ⭐ **VN = macro (VRF) · SGT = micro**, và 🔴 ⭐ **wireless data đi VXLAN thẳng vào edge, KHÔNG CAPWAP về WLC**.

3. 🔴 ⭐⭐ **QoS quy về bốn cặp đối lập — thuộc bốn cặp này là đủ:**
   ⭐ **DiffServ (dùng) vs IntServ (không mở rộng được)** ·
   ⭐⭐ **LLQ cho VOICE (đảm bảo ĐỘ TRỄ) vs CBWFQ (chỉ đảm bảo BĂNG THÔNG)** ·
   ⭐⭐ **Policing VỨT (in+out) vs Shaping CHỜ (chỉ out)** ·
   ⭐ **WRED vứt sớm (chỉ TCP, 🔴 không cho voice) vs Tail drop gây TCP global sync**.
   ⭐ Cộng ba nhóm số phải thuộc: ⭐⭐ **voice = 150 ms / 30 ms / 1 %** · ⭐ **EF=46, CS3=24, CS6=48,
   AF41=34, CS1=8, DF=0** (⭐ `AFxy = 8x+2y`) · ⭐ **priority queue ≤ 33%**.
   Và ⭐ **trust boundary càng gần nguồn càng tốt — tin IP phone, KHÔNG tin PC.**

🧠 **Một câu để nhớ:** *Campus là ⭐ **một công ty có lễ tân (access), quản lý tầng (distribution) và
đường cao tốc (core)** — ⭐ **đừng đặt trạm thu phí giữa cao tốc**. ⭐ **SD-WAN là công ty vận tải**:
⭐ **vBond gác cổng, vSmart điều độ (không lái xe), cEdge chở hàng**. ⭐ **SD-Access là tòa nhà mà mọi bức
tường đều là cửa ra mang cùng số nhà** (anycast gateway). Còn ⭐ **QoS là sân bay giờ cao điểm** —
⭐ **in hạng vé một lần ở quầy check-in (trust boundary), mở làn ưu tiên cho voice (LLQ) nhưng đừng
để 80% khách vào làn đó**, và ⭐ **quá cân thì hoặc VỨT (policing) hoặc CHO CHỜ CHUYẾN SAU (shaping)**.*

---

### ✅ TỰ CHẤM

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | ⭐⭐ Vai trò 3 lớp campus · ⭐ **đặt ACL ở lớp nào, vì sao** | ☐ |
| 2 | ⭐⭐ **2-tier vs 3-tier** — mốc quyết định và lý do toán học | ☐ |
| 3 | ⭐ **L2 access vs Routed access** — ưu/nhược | ☐ |
| 4 | ⭐⭐ **Spine-Leaf**: cấu trúc, vì sao 2 hop, vì sao DC cần nó | ☐ |
| 5 | ⭐ **North-South vs East-West** | ☐ |
| 6 | ⭐ **Oversubscription** — cách tính + 2 tỉ lệ khuyến nghị | ☐ |
| 7 | ⭐ Bảng dự phòng theo tầng (nguồn/sup/link/thiết bị/gateway/L3/phần mềm) | ☐ |
| 8 | ⭐⭐ **SSO vs NSF vs GR** | ☐ |
| 9 | ⭐ **StackWise vs VSS vs vPC** — vPC khác chỗ nào | ☐ |
| 10 | ⭐⭐ **6 mô hình triển khai WLAN** | ☐ |
| 11 | ⭐ Hai nghĩa khác nhau của "cloud" trong WLAN | ☐ |
| 12 | ⭐ **Location services**: trilateration vs AoA vs BLE + độ chính xác | ☐ |
| 13 | 🔴 ⭐ **Yêu cầu thiết kế AP cho location** | ☐ |
| 14 | ⭐ **IaaS / PaaS / SaaS** — ai lo cái gì | ☐ |
| 15 | ⭐⭐ **4 cách kết nối cloud** — cái nào có SLA | ☐ |
| 16 | ⭐ **CapEx vs OpEx** + chi phí ẩn của mỗi bên | ☐ |
| 17 | 🔴 ⭐⭐ **4 thành phần SD-WAN** — plane, nhiệm vụ | ☐ |
| 18 | 🔴 ⭐⭐ **Thành phần nào cần IP public?** | ☐ |
| 19 | 🔴 ⭐⭐ **Traffic người dùng có qua vSmart không?** | ☐ |
| 20 | ⭐⭐ **OMP** chạy giữa ai với ai, quảng bá 3 loại route gì | ☐ |
| 21 | ⭐⭐ **TLOC** gồm 3 thành phần nào · **private vs public color** | ☐ |
| 22 | ⭐⭐ **AAR** hoạt động thế nào (vai trò của BFD) | ☐ |
| 23 | ⭐ **WAN truyền thống vs SD-WAN** — 5 điểm | ☐ |
| 24 | 🔴 ⭐⭐ **3 plane của SD-Access** + VRF nằm ở đâu | ☐ |
| 25 | 🔴 ⭐⭐ **5 fabric role** — ai chạy gì | ☐ |
| 26 | ⭐ **3 loại Border Node** | ☐ |
| 27 | 🔴 ⭐⭐ **Anycast gateway** — cơ chế và nó thay thế cái gì | ☐ |
| 28 | 🔴 ⭐⭐ **SD-Access wireless**: control đi đâu, **data đi đâu** | ☐ |
| 29 | ⭐⭐ **VN vs SGT** + ví dụ mỗi cái | ☐ |
| 30 | ⭐ **Underlay / Overlay / SD-Access transit vs IP transit** | ☐ |
| 31 | ⭐ **Fusion router** giải quyết vấn đề gì | ☐ |
| 32 | ⭐ **4 workflow của DNA Center** | ☐ |
| 33 | 🔴 ⭐⭐ **SD-WAN vs SD-Access** — 5 điểm khác biệt | ☐ |
| 34 | 🔴 ⭐⭐ **Ngưỡng voice 150/30/1** | ☐ |
| 35 | ⭐⭐ **3 mô hình QoS** — vì sao IntServ không dùng được | ☐ |
| 36 | ⭐⭐ **CoS vs DSCP** — số bit, và 🔴 **vì sao CoS chỉ có trên trunk** | ☐ |
| 37 | ⭐⭐ **DSCP: EF · CS3 · CS6 · AF41 · CS1 · DF** + công thức `8x+2y` | ☐ |
| 38 | 🔴 ⭐ Trong `AFxy`, **y cao nghĩa là gì** | ☐ |
| 39 | ⭐⭐ **Trust boundary** — đặt ở đâu, vì sao không tin PC | ☐ |
| 40 | ⭐⭐ **CBWFQ vs LLQ** — vì sao voice phải dùng LLQ · giới hạn 33% | ☐ |
| 41 | ⭐⭐ **Tail drop vs WRED** · **TCP global synchronization** | ☐ |
| 42 | 🔴 ⭐ **2 điều cấm kỵ của WRED** | ☐ |
| 43 | 🔴 ⭐⭐ **Policing vs Shaping** — 4 điểm + use case kinh điển | ☐ |
| 44 | ⭐ **MQC 3 bước** · **hierarchical QoS** là gì | ☐ |
| 45 | ⭐⭐ **WMM 4 AC** · 🔴 **vấn đề CAPWAP với QoS** | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | ⭐⭐ **LAB A**: làm đúng ≥ 8/10 tình huống **trước khi** mở đáp án | ⭐⭐ ☐ |
| 2 | ⭐ Riêng câu 1–3 (2-tier/3-tier/spine-leaf) — giải thích được **lý do**, không chỉ đáp án | ☐ |
| 3 | ⭐ Riêng câu 8–9 — phân biệt đúng **VN vs SGT** | ⭐ ☐ |
| 4 | ⭐⭐ Riêng câu 10 — giải thích được **vì sao phải shape chứ không police** | ⭐⭐ ☐ |
| 5 | ⭐ **LAB B**: cấu hình xong MQC, `show policy-map interface` hiện đủ 4 class | ☐ |
| 6 | ⭐⭐ **Ping với `tos 184`** → thấy bộ đếm class VOICE tăng | ⭐⭐ ☐ |
| 7 | ⭐ Tính được `ToS = DSCP × 4` và thử thêm `tos 96` (CS3) | ☐ |
| 8 | ⭐ Thêm shaping lồng LLQ (**hierarchical QoS**) và verify | ☐ |
| 9 | 🔴 ⭐ Thử áp **WRED lên class VOICE** → thấy IOS từ chối/cảnh báo | ⭐ ☐ |
| 10 | 🔴 ⭐ Thử **`priority percent 80`** → hiểu vì sao giới hạn 33% | ⭐ ☐ |
| 11 | ⭐⭐ **LAB C bảng 1**: điền đúng ≥ 3/4 dòng SD-WAN **từ trí nhớ** | ⭐⭐ ☐ |
| 12 | ⭐⭐ **LAB C bảng 2**: điền đúng ≥ 3/4 fabric role **từ trí nhớ** | ⭐⭐ ☐ |
| 13 | ⭐⭐ **LAB C bảng 3**: điền đúng ≥ 5/6 dòng **từ trí nhớ** | ⭐⭐ ☐ |
| 14 | 🚀 **LAB D**: đăng nhập được sandbox DNA Center | 🚀 ☐ |
| 15 | 🚀 ⭐ Tìm được **VN** và **SGT matrix** trên DNA Center | 🚀 ☐ |
| 16 | 🚀 ⭐ Tìm được **fabric role** của thiết bị trên DNA Center | 🚀 ☐ |
| 17 | 🚀 ⭐⭐ Tìm được **TLOC + color** của một edge trên vManage | 🚀 ⭐⭐ ☐ |
| 18 | 🚀 ⭐ Xem được **OMP routes** và **BFD sessions** | 🚀 ☐ |

> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên ⭐⭐ **LAB C toàn bộ** (mục 11–13 — đây **chính xác** là
> dạng câu hỏi của 1.4 và 1.5), rồi **LAB A** (mục 1, 3, 4), rồi **mục 6** của LAB B.
> ⭐ **Bỏ LAB D nếu bám tiến độ** — nó hay nhưng không bắt buộc.
>
> ⚠️ ⭐ **Chưa tick được ≥ 39/45 Phần A thì đọc lại §6, §7, §8** — ⭐ **ba mục này chiếm ~2/3 số câu của Domain 1.0.**
>
> 🎉 ⭐ **Hết Module-09 = xong Domain 1.0 Architecture (15%) + Domain 2.0 Virtualization (10%).**
> ⭐ **Cộng với Domain 3.0 Infrastructure (30%) đã xong ở Module-07B → bạn đã phủ 55% nội dung đề.**
> ⭐ **Đây là mốc Tuần 15 của ROADMAP — hơn nửa chặng đường.**

---

## 🔗 17. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương *Enterprise Network Design*, *Wireless Design*, *Cloud*, *SD-WAN*, *SD-Access*, *QoS* |
| **Cisco CVD** ⭐⭐ | ***Campus LAN and Wireless LAN Design Guide*** — ⭐ tài liệu gốc cho §2, §4 (có cả số liệu oversubscription) |
| **Cisco CVD** ⭐⭐ | ***SD-Access Solution Design Guide*** — ⭐⭐ **tài liệu quan trọng nhất của §7**. Có sơ đồ fabric role rất rõ |
| **Cisco CVD** ⭐ | *SD-WAN Design Guide* · *SD-WAN End-to-End Deployment Guide* |
| **Cisco doc** ⭐⭐ | ***Cisco SD-WAN Overview*** — ⭐ giải thích 4 plane, OMP, TLOC, color |
| **Cisco doc** ⭐ | *Cisco SD-WAN Policies Configuration Guide* — chương **Application-Aware Routing** |
| **Cisco doc** ⭐⭐ | ***Software-Defined Access Fabric Roles*** · *SD-Access Wireless Design and Deployment Guide* |
| **Cisco doc** ⭐⭐ | ***Enterprise QoS Solution Reference Network Design Guide (SRND)*** — ⭐⭐ **kinh thánh của QoS Cisco**: mô hình 12 lớp, ngưỡng voice, khuyến nghị marking |
| **Cisco doc** ⭐ | *QoS: Modular QoS Command-Line Interface Configuration Guide* (MQC) |
| **Cisco doc** ⭐ | *QoS: Policing and Shaping Configuration Guide* · *Congestion Avoidance (WRED)* |
| **Cisco doc** ⭐ | *Wireless QoS Deployment Guide* — ⭐ WMM, ánh xạ DSCP↔UP, QoS trên CAPWAP |
| **Cisco doc** | *High Availability Configuration Guide* — SSO/NSF/ISSU · *StackWise Virtual Configuration* |
| **Cisco doc** | *Cisco Spaces (DNA Spaces) Overview* — location services |
| **RFC 2474 / 2475** | ⭐ **DSCP / DiffServ Architecture** |
| **RFC 2597 / 3246** | ⭐ **AF PHB / EF PHB** |
| **RFC 8325** | ⭐ **Ánh xạ DSCP ↔ 802.11 User Priority** *(sửa lỗi mapping cũ)* |
| **Cisco DevNet** ⭐ | `developer.cisco.com/site/sandbox/` — sandbox **DNA Center** và **SD-WAN** (LAB D) |
| **Video** ⭐ | CBT Nuggets ENCOR — module Architecture & QoS · **Keith Barker**: search `Keith Barker QoS`, `Keith Barker SD-Access` · **Cisco Live**: search `BRKCRS-2810 SD-Access`, `BRKRST-2043 QoS design` |
| **Cisco Live** ⭐⭐ | ⭐ **Nguồn tốt nhất cho Architecture** — search trên `ciscolive.com/on-demand`: `SD-Access design`, `SD-WAN design`, `Campus design best practices`, `Enterprise QoS design` |
| **NetworkLessons** ⭐ | *QoS Classification/Marking*, *CBWFQ*, *LLQ*, *Policing vs Shaping*, *WRED* — ⭐ nhiều bài free, giải thích rất dễ hiểu |
| **Forum** | https://community.cisco.com — search: `llq vs cbwfq voice`, `policing vs shaping which to use`, `sd-access fusion router dhcp`, `sdwan control connection down vbond`, `capwap qos dscp not preserved` |

---

**➡️ Tiếp theo:** Module-10 — Security
*(ACL nâng cao · CoPP · device hardening · AAA TACACS+/RADIUS · 802.1X/MAB/WebAuth · **TrustSec/SGT** · MACsec — **Tuần 16**)*

> 🔴 ⭐⭐ **Module-10 là khối lớn thứ hai của kỳ thi — Security chiếm 20% đề**, và ⭐ **có rất nhiều
> "configure and verify"**. ⭐ **Quay lại chế độ lab nghiêm túc.**
>
> ⭐ **Và bạn đã có sẵn hai mối nối:** ⭐ **TrustSec/SGT** ở Module-10 chính là **policy plane của SD-Access**
> (§7.6) · ⭐ **802.1X** chính là thứ gán SGT và VLAN động mà bạn đã gặp ở **Module-07B §8**.
