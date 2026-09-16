# LAB 09 — Tuần 15: Thiết kế & QoS

> 📘 **Lý thuyết:** [Module-09](Module-09-Architecture-va-QoS.md) —
> đọc **Phần 1** và **Phần 2 mục §3 (campus), §7 (SD-WAN), §8 (SD-Access), §9 (QoS)** trước khi làm.
>
> ⏱️ **Thời gian:** ~3 giờ · 💾 **RAM:** 1 GB — nhẹ nhất repo · 🧰 **Cần:** giấy bút + 2× vIOS

---

## ⭐ Module "học bằng đầu" — Domain 1.0 không có mục nào bắt cấu hình

Toàn bộ Domain 1.0 dùng từ *Explain · Analyze · Differentiate · Describe*.
Nên lab ở đây chủ yếu là **lab-trên-giấy** — đúng dạng câu hỏi của đề.

| LAB | Nội dung | Cần gì | Bắt buộc? |
|---|---|---|:---:|
| **A** | ⭐ **Chọn thiết kế** — 10 tình huống | Giấy bút | **Có** |
| **B** | QoS trên EVE-NG (MQC, LLQ, shaping) | 2× vIOS | ⭐ **Có** |
| **C** | ⭐ **Điền bảng thành phần SD-WAN / SD-Access** | Giấy bút | **Có** |
| **D** | Nhìn DNA Center & vManage thật | DevNet Sandbox | Nên |

> ⭐ **LAB C là bài đáng làm nhất.** Điền được bảng 4 thành phần SD-WAN và 5 fabric role
> SD-Access **từ trí nhớ** là bạn đã nắm phần lớn câu hỏi của mục 1.4 và 1.5.

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| **Viết đáp án TRƯỚC khi mở gợi ý** | LAB A và C chỉ có giá trị nếu bạn tự làm trước |
| **LAB B: đổi DSCP sang ToS** | `ping ... tos <n>` nhận **ToS**, không phải DSCP. ⭐ `ToS = DSCP × 4` (EF 46 → 184) |
| 🔴 **Đừng cố dựng SD-WAN on-prem** | vManage + vSmart + vBond + 2 vEdge = **20+ GB RAM**. Máy bạn không kham nổi, **và đề không hỏi cấu hình** |
| **Sandbox là môi trường dùng chung** | ⭐ Chỉ **XEM**, đừng đổi cấu hình |

---

## 🧪 10. LAB 09

| LAB | Cần gì | Thời gian | Bắt buộc? |
|---|---|:---:|:---:|
| **A** — Lab-trên-giấy: chọn design | Bút + giấy | 30 phút | ⭐ **Bắt buộc** |
| **B** — QoS trên EVE-NG (2 router) | ⭐ 2× vIOS (~1 GB) | 60 phút | **Bắt buộc** |
| **C** — Lab-trên-giấy: điền bảng thành phần | Bút + giấy | 20 phút | ⭐ **Bắt buộc** |
| **D** — DevNet Sandbox: DNA Center & vManage | Trình duyệt | 45 phút | ⭐ Rất nên |

---

### LAB A — ⭐ Chọn thiết kế (30 phút, trên giấy)

> ⭐ **Đây đúng dạng câu hỏi của Domain 1.0.** Viết đáp án **trước khi** mở gợi ý.

| # | Tình huống | Câu hỏi |
|:---:|---|---|
| 1 | Công ty 1 tòa nhà, 4 tầng, 300 nhân viên | 2-tier hay 3-tier? Vì sao? |
| 2 | Đại học 6 tòa nhà, mỗi tòa 1 khối distribution | 2-tier hay 3-tier? Vì sao? |
| 3 | Data center mới, chủ yếu chạy microservices | Kiến trúc nào? Vì sao? |
| 4 | 40 chi nhánh, WLC ở HQ, WAN 20 Mbps hay đứt | Mô hình WLAN nào? |
| 5 | Bệnh viện muốn tìm được máy thở ở đâu, sai số < 2 m | Công nghệ gì? Yêu cầu thiết kế AP? |
| 6 | Cần chạy ứng dụng tài chính, tuân thủ nghiêm, độ trễ thấp | On-prem hay cloud? |
| 7 | Chi nhánh có MPLS 10 Mbps + Internet 200 Mbps, muốn voice luôn tốt | Giải pháp? Cơ chế nào? |
| 8 | Campus muốn camera **không bao giờ** nói chuyện được với máy nhân viên | VN hay SGT? |
| 9 | Trong phòng kế toán, muốn máy thực tập sinh không truy cập được server lương | VN hay SGT? |
| 10 | Link vật lý 1 Gbps, hợp đồng nhà mạng 300 Mbps, hay bị mất gói voice | Policing hay shaping? Ở đâu? |

<details><summary>⭐ Đáp án LAB A</summary>

| # | ⭐ Đáp án |
|:---:|---|
| 1 | ⭐ **2-tier (collapsed core).** Chỉ 1 khối distribution → **không cần Core riêng**. Rẻ hơn, đơn giản hơn |
| 2 | ⭐ **3-tier.** 6 khối distribution → full-mesh cần **15 link** →  **phải có Core** làm điểm tập trung |
| 3 | ⭐ **Spine-Leaf.** Microservices =  **traffic East-West khổng lồ** · cần  **độ trễ đều (luôn 2 hop)** ·  ECMP dùng hết đường, không STP.  Overlay **VXLAN + EVPN** |
| 4 | ⭐ **Distributed / FlexConnect + local switching.**  WAN 20 Mbps không kham nổi CAPWAP data của 40 site.  Thêm **local auth + FlexConnect Group** để sống sót khi đứt WAN *(07B §5)* |
| 5 | **Cisco Hyperlocation (AoA)** — RSSI trilateration chỉ đạt 5–10 m. 🔴  **Yêu cầu thiết kế: phải có AP ở CHU VI khu vực**, không chỉ ở giữa |
| 6 | ⭐ **On-premises** (hoặc private cloud). Lý do:  **tuân thủ/chủ quyền dữ liệu dễ chứng minh** ·  **độ trễ thấp nhất tới người dùng nội bộ** · toàn quyền kiểm soát.  *(Có thể hybrid: dữ liệu nhạy cảm on-prem, phần co giãn trên cloud.)* |
| 7 | ⭐ **SD-WAN với AAR (Application-Aware Routing).**  **BFD đo loss/latency/jitter trên cả hai đường**; định nghĩa **SLA class cho voice**;  traffic voice **tự chuyển sang đường nào đạt SLA**.  Dùng được **cả hai** đường thay vì để Internet nằm không |
| 8 | ⭐ **VN (Virtual Network) = VRF** —  **macro-segmentation, cách ly TUYỆT ĐỐI.**  Nhớ thiết kế **fusion router** nếu camera cần dịch vụ chung (NTP/DHCP) |
| 9 | ⭐ **SGT** —  **micro-segmentation TRONG CÙNG một VN.** ISE gán SGT khi 802.1X xác thực |
| 10 | ⭐ **Shaping, ở router phía mình, chiều OUTBOUND, shape xuống 300 Mbps.**  Lý do: nếu không shape, router bắn 1 Gbps →  **nhà mạng policing và vứt NGẪU NHIÊN (vứt cả voice)**.  Shape ở mình → **mình tự quyết ai bị chờ** → lồng LLQ bên trong shaper (hierarchical QoS) để voice vẫn đi trước |
</details>

---

### LAB B — ⭐ QoS trên EVE-NG (60 phút)

**Topology:** `R1 ──Gi0/0── R2` (2× vIOS, ~1 GB)

```
!═══════ R1 ═══════
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.252
 no shutdown

! ─── ① CLASS-MAP ───
class-map match-all VOICE
 match dscp ef
class-map match-all SIGNALING
 match dscp cs3
class-map match-all SCAVENGER
 match dscp cs1

! ─── ② POLICY-MAP ───
policy-map WAN-OUT
 class VOICE
  priority percent 10
 class SIGNALING
  bandwidth percent 5
 class SCAVENGER
  bandwidth percent 1
 class class-default
  fair-queue
  random-detect

! ─── ③ ÁP LÊN INTERFACE ───
interface GigabitEthernet0/0
 service-policy output WAN-OUT
```

✅ **Checkpoint B.1 — ⭐ lệnh quan trọng nhất của QoS:**
```
R1# show policy-map interface GigabitEthernet0/0

 Service-policy output: WAN-OUT
   Class-map: VOICE (match-all)
     0 packets, 0 bytes
     Match: dscp ef (46)
     Priority: 10% (100000 kbps), burst bytes 2500000, b/w exceed drops: 0
   Class-map: SIGNALING (match-all)
     Match: dscp cs3 (24)
     bandwidth 5% (50000 kbps)
   Class-map: class-default (match-any)
     Fair-queue: per-flow queue limit 16
     Exp-weight-constant: 9 (1/512)      ← WRED đang bật
```

✅ **Checkpoint B.2 — ⭐ sinh traffic có DSCP và xem bộ đếm tăng:**
```
R1# ping 10.0.0.2 tos 184 repeat 100
!     tos 184 = DSCP 46 (EF)   [184 = 46 × 4, vì DSCP nằm ở 6 bit CAO của byte ToS]

R1# show policy-map interface Gi0/0 | section VOICE
   Class-map: VOICE (match-all)
     100 packets, 11400 bytes        ← BỘ ĐẾM ĐÃ TĂNG!
     Match: dscp ef (46)
```
> 💡 ⭐ **Công thức đổi DSCP → ToS: `ToS = DSCP × 4`.**
> ⭐ EF(46)→184 · CS3(24)→96 · CS6(48)→192 · CS1(8)→32 · AF41(34)→136.
> ⭐ **Thử ping với `tos 96` và xem class SIGNALING tăng** — bạn vừa tự chứng minh classification hoạt động.

✅ **Checkpoint B.3 — ⭐ thêm shaping (hierarchical QoS):**
```
policy-map SHAPE-100M
 class class-default
  shape average 100000000
  service-policy WAN-OUT        ! queue lồng BÊN TRONG shaper
!
interface GigabitEthernet0/0
 no service-policy output WAN-OUT
 service-policy output SHAPE-100M
```
```
R1# show policy-map interface Gi0/0 | include shape|Shaping|Target
    shape (average) cir 100000000, bc 400000, be 400000
    target shape rate 100000000
```

✅ **Checkpoint B.4 — 🔴  cố ý làm sai để hiểu:**
```
! Thử áp WRED lên class VOICE:
R1(config)# policy-map WAN-OUT
R1(config-pmap)# class VOICE
R1(config-pmap-c)# random-detect
```
⭐ **Quan sát:** IOS **từ chối** hoặc cảnh báo —  **không cho dùng WRED cùng `priority`.**
> 💡 ⭐ **Bài học:**  **WRED và LLQ không đi với nhau.**  Voice là UDP, **không chịu được mất gói**,
> và priority queue không có chỗ cho "vứt sớm ngẫu nhiên".

✅ **Checkpoint B.5 — ⭐ thử `priority percent 80`:**
```
R1(config-pmap-c)# priority percent 80
```
⭐ **Quan sát:** IOS có thể **báo lỗi vượt băng thông khả dụng**, hoặc chấp nhận nhưng  **không còn chỗ
cho các class khác**.
> 💡 ⭐ **Bài học:**  **priority queue ≤ 33%.**  Cho tất cả vào làn ưu tiên = không còn ưu tiên.

---

### LAB C — ⭐ Điền bảng thành phần (20 phút, trên giấy)

> ⭐ **Che đáp án. Điền từ trí nhớ. Đây là dạng câu hỏi đề ra nhiều nhất của 1.4 và 1.5.**

**Bảng 1 — SD-WAN:**

| Thành phần | Plane | Làm gì | Cần IP public? | Chở data? |
|---|---|---|---|---|
| vManage | ____ | ____ | ____ | ____ |
| vSmart | ____ | ____ | ____ | ____ |
| vBond | ____ | ____ | ____ | ____ |
| vEdge/cEdge | ____ | ____ | ____ | ____ |

**Bảng 2 — SD-Access:**

| Fabric role | Chạy giao thức gì | Làm gì |
|---|---|---|
| Control Plane Node | ____ | ____ |
| Border Node | ____ | ____ |
| Edge Node | ____ | ____ |
| Intermediate Node | ____ | ____ |

**Bảng 3 — điền nhanh:**

| Câu | Trả lời |
|---|---|
| SD-Access: control / data / policy plane dùng gì? | ____ / ____ / ____ |
| SD-WAN: control plane protocol? data plane? | ____ / ____ |
| VN = ? · SGT dùng để làm gì? | ____ |
| DSCP của: Voice · Signaling · Network Control · Video call · Scavenger | ____ |
| Ngưỡng voice: latency · jitter · loss | ____ |
| Policing vs Shaping: cái nào vứt, cái nào chờ, chiều nào? | ____ |

<details><summary>⭐ Đáp án LAB C</summary>

**Bảng 1:**
| Thành phần | Plane | Làm gì | IP public? | Chở data? |
|---|---|---|---|---|
| ⭐ **vManage** | Management | GUI/API, template, giám sát | Không bắt buộc | ❌ |
| **vSmart** | Control | **Chạy OMP**, phân phối route/TLOC/policy | Không bắt buộc | 🔴  **KHÔNG** |
| ⭐ **vBond** | Orchestration | Xác thực & giới thiệu thiết bị mới, phát hiện NAT | **CÓ — duy nhất** | ❌ |
| ⭐ **vEdge/cEdge** | Data | **Forward traffic thật** qua IPsec | (tùy transport) | **CÓ** |

**Bảng 2:**
| Role | Giao thức | Làm gì |
|---|---|---|
| ⭐ **Control Plane Node** | **LISP MS/MR** | CSDL "host nào ở đâu" (HTDB) |
| ⭐ **Border Node** | LISP PxTR + VRF-lite handoff | Cửa ra vào fabric (internal/external/anywhere) |
| ⭐ **Edge Node** | **LISP xTR** | Cắm endpoint · bọc/mở VXLAN ·  **anycast gateway** · áp SGT |
| **Intermediate Node** | Chỉ IP routing (IS-IS) | 🔴  **Không biết gì về fabric** |

**Bảng 3:**
| Câu | ⭐ Trả lời |
|---|---|
| SD-Access 3 plane | ⭐ **LISP** /  **VXLAN** /  **TrustSec (SGT)** |
| SD-WAN | ⭐ **OMP** /  **IPsec** |
| VN = ? SGT? | ⭐ **VN = VRF (macro-segmentation)** ·  **SGT = micro-segmentation trong cùng VN** |
| DSCP | ⭐ **EF=46 · CS3=24 · CS6=48 · AF41=34 · CS1=8** |
| Ngưỡng voice | ⭐ **≤150 ms · ≤30 ms · ≤1 %** |
| Policing/Shaping | ⭐ **Policing VỨT (in+out)** ·  **Shaping CHỜ (chỉ out)** |
</details>

---

### LAB D — 🚀 DevNet Sandbox: nhìn DNA Center & vManage thật (45 phút)

| Bước | Làm |
|:---:|---|
| 1 | `developer.cisco.com/site/sandbox/` → đăng nhập |
| 2 | Tìm sandbox ⭐ **"DNA Center"** và  **"SD-WAN"** — ưu tiên **Always-On** |
| 3 | ⚠️ ⭐ **Lấy URL + tài khoản từ chính trang sandbox** (Cisco đổi định kỳ) |

⭐ **Trên DNA Center — tìm 4 thứ:**

| # | Tìm gì | Ở đâu | Liên hệ |
|:---:|---|---|:---:|
| 1 | ⭐ **4 workflow** Design/Policy/Provision/Assurance | Menu chính | §7.8 |
| 2 | ⭐ **Virtual Network (VN)** đã tạo | Policy → Virtual Network | §7.6 |
| 3 | ⭐ **Scalable Group (SGT)** và ma trận chính sách | Policy → Group-Based Access Control | §7.6 |
| 4 | ⭐ **Fabric role** của từng thiết bị | Provision → Fabric | §7.3 |

⭐ **Trên vManage — tìm 4 thứ:**

| # | Tìm gì | Ở đâu | Liên hệ |
|:---:|---|---|:---:|
| 1 | ⭐ **Danh sách controller** (vManage/vSmart/vBond) | Monitor → Network / Administration → Controllers | §6.2 |
| 2 | ⭐ **TLOC và Color** của từng edge | Monitor → Devices → *(chọn)* → Real Time → **Control TLOC** | §6.3 |
| 3 | ⭐ **OMP routes** | Monitor → Devices → Real Time → **OMP Routes** | §6.3 |
| 4 | ⭐ **Application-Aware Routing / SLA** | Configuration → Policies · Monitor → Applications | §6.4 |

> ⚠️ ⭐ **Sandbox always-on là môi trường DÙNG CHUNG — chỉ XEM, đừng đổi cấu hình.**

✅ **Checkpoint D:** trả lời được — ⭐ *"Trong sandbox này có bao nhiêu VN? Edge nào có mấy TLOC và color gì?"*
