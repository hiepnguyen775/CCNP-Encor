# Module-13 — Ôn thi & Chiến thuật phòng thi

> 🧭 **Lộ trình:** [Module-12](Module-12-Automation-va-Programmability.md) → `[Bạn đang ở đây] Module-13` → **Phòng thi**
>
> 📊 **Blueprint:** module này **không dạy kiến thức mới**. Nó làm ba việc:
> **ráp lại** · **kiểm chứng bằng LAB tổng hợp** · **dạy cách đi thi**.
>
> ⏱️ **Tuần 20** · 20–25 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **Tôi đã học hết 12 module rồi — làm sao biết mình THẬT SỰ sẵn sàng, và thi thế nào cho đúng cách?**

⭐ Chú ý: **"học xong" và "sẵn sàng thi" là hai chuyện khác nhau.**
Nhiều người trượt không phải vì thiếu kiến thức, mà vì **chưa bao giờ ghép các mảnh lại với nhau**,
hoặc **không biết cách phân bổ thời gian trong phòng thi**.

## Ba cửa phải qua

```
   ┌─────────────────────────────────────────────────────────┐
   │  CỬA 1 — LAB CAPSTONE                                   │
   │  Dựng một hệ thống chạm cả 6 domain, rồi DIỄN TẬP SỰ CỐ │
   │  → Chứng minh bạn GHÉP được, không chỉ nhớ được         │
   └───────────────────────┬─────────────────────────────────┘
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │  CỬA 2 — LUYỆN ĐỀ                                       │
   │  Đạt ổn định ≥ 85% qua 3 bộ đề KHÁC NHAU                │
   │  → Chứng minh bạn ĐỌC ĐỀ đúng, không chỉ hiểu đúng      │
   └───────────────────────┬─────────────────────────────────┘
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │  CỬA 3 — CHECKLIST TRƯỚC KHI ĐÓNG TIỀN                  │
   │  → Chưa qua cửa 1 và 2 thì ĐỪNG book exam               │
   └─────────────────────────────────────────────────────────┘
```

## 6 ý phải nhớ về kỳ thi

| # | Ý | Vì sao quan trọng |
|:---:|---|---|
| 1 | 🔴 **Đề Cisco KHÔNG cho quay lại câu trước** | Đã bấm tiếp là mất luôn. Đổi hẳn cách làm bài |
| 2 | 🔴 **120 phút, khoảng 90–110 câu** | Trung bình **hơn 1 phút/câu** — không có chỗ cho đắn đo |
| 3 | **Cisco không công bố điểm đạt** | Nên đừng tính "làm đúng 70% là qua" — cứ làm tốt nhất có thể |
| 4 | 🔴 **Domain 3.0 chiếm 30%** | Gần 1/3 đề. Yếu chỗ này thì không cứu được bằng chỗ khác |
| 5 | ⭐ **Câu "chọn 2/chọn 3" không có điểm một phần** | Đúng 1 trong 2 vẫn là **sai cả câu** |
| 6 | 🔴 **Mục 4.7 nằm ở Domain 4.0** | Ôn theo domain rất dễ bỏ sót chỗ này |

## 🗺️ Bố cục module

| Phần | Nội dung | Làm khi nào |
|---|---|---|
| 🧠 **PHẦN 1** (§2) | **Hiểu kỳ thi** — nó hỏi kiểu gì, bẫy ở đâu | Đọc đầu tiên |
| ⚙️ **PHẦN 2** (§3) | **Ôn tập nhanh 6 domain** — bảng tra mọi con số | Ôn mỗi ngày |
| 🧪 **PHẦN 3** | 🔴 **LAB CAPSTONE** — file riêng | **Làm trước khi luyện đề** |
| 🏗️ **PHẦN 4** (§4–§5) | **Luyện đề + lộ trình 7 ngày cuối** | Tuần cuối |
| 📎 **PHỤ LỤC** | Checklist book exam · ngày thi | Trước khi đóng tiền |

---

## ⭐ 0. Phạm vi

### 0.1 Module này khác 12 module trước ở chỗ nào

> ⭐ **12 module trước dạy bạn KIẾN THỨC. Module này dạy bạn CÁCH DÙNG kiến thức đó
> trong hai hoàn cảnh rất khác nhau:** một hệ thống thật, và một phòng thi có đồng hồ đếm ngược.

| | 12 module trước | Module này |
|---|---|---|
| Mục tiêu | **Hiểu** | 🔴 **Chứng minh là hiểu** |
| Cách học | Đọc → lab từng phần | 🔴 **Lab tổng hợp → luyện đề** |
| Đo bằng | Tự thấy "à ra thế" | 🔴 **Điểm số khách quan** |
| Sai thì | Đọc lại | 🔴 **Biết chính xác quay lại module nào** |

### 0.2 🔴 Thứ tự BẮT BUỘC

```
① LAB CAPSTONE        ← LÀM TRƯỚC. Đây là chỗ lộ ra lỗ hổng thật
       ↓
② Vá lỗ hổng          ← Quay lại đúng module bị mất điểm
       ↓
③ LUYỆN ĐỀ            ← Chỉ bắt đầu khi capstone đã đạt ≥ 80
       ↓
④ CHECKLIST → book exam
```

> 🔴 **Đừng đảo thứ tự.**  **Luyện đề trước khi làm capstone là sai lầm phổ biến nhất:**
> đề trắc nghiệm cho bạn **cảm giác an toàn giả** *(nhìn 4 đáp án là nhớ ra)*,
> trong khi capstone bắt bạn **tạo ra từ con số 0** — và đó mới là thước đo thật.

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức** | 🔴 **Đã học xong Module-00 → 12.** Thiếu module nào thì quay lại học trước |
| **Lab** | EVE-NG — 🔴 **6 node, ~3,5 GB RAM** *(xem [LAB Capstone](Module-13-LAB-Capstone.md))* |
| **Bộ đề** | ⭐ **Ít nhất 2 nguồn khác nhau** — xem §4.1 |
| **Thời gian** | ⭐ **20–25 giờ** · đừng dồn vào 2 ngày cuối |
| **Sổ tay lỗi** | [`SO-TAY-LOI.md`](SO-TAY-LOI.md) — 🔴 **giờ là lúc đọc lại toàn bộ sổ này** |

---

## 🧠 PHẦN 1 — HIỂU KỲ THI

> ⭐ **Phần này không có lệnh nào.** Nó nói về **cách kỳ thi vận hành** —
> thứ ảnh hưởng tới điểm của bạn không kém gì kiến thức.

### 2.1 Kỳ thi trông như thế nào

| | |
|---|---|
| **Mã đề** | **350-401 ENCOR** |
| **Thời gian** | 🔴 **120 phút** |
| **Số câu** | ⭐ **Khoảng 90–110** *(Cisco không công bố con số cố định)* |
| **Điểm đạt** | ⭐ **Cisco KHÔNG công bố** — đừng tính toán "làm đúng bao nhiêu thì qua" |
| **Ngôn ngữ** | Tiếng Anh *(có bản tiếng Nhật)* |
| **Hiệu lực** | ⭐ **3 năm** |
| **Giá trị** | Là **bài thi lõi** của CCNP Enterprise, đồng thời là **bài điều kiện** của CCIE Enterprise |
| **Chi phí** | ⚠️ **Thay đổi theo thời điểm và khu vực** — xem trang Cisco lúc bạn đăng ký |

> 🔴  **Điều quan trọng nhất về hình thức thi:**
> ⭐ **Bạn KHÔNG quay lại được câu trước.** Bấm "Next" là xong, không có nút "Back",
> không có "đánh dấu để xem lại" như nhiều kỳ thi khác.
>
> ⭐ **Hệ quả rất thực tế:**  **chiến thuật "lướt qua làm câu dễ trước, câu khó để sau"
> KHÔNG dùng được.** Bạn phải **quyết ngay tại chỗ** cho từng câu.

### 2.2 🔴 Ba dạng câu hỏi và cách xử lý khác nhau

| Dạng | Chiếm | Cách xử lý |
|---|---|---|
| **Trắc nghiệm 1 đáp án** | Nhiều nhất | ⭐ **Loại trừ 2 đáp án sai rõ ràng trước**, rồi so 2 cái còn lại |
| 🔴 **Chọn 2 / chọn 3** | Khá nhiều | 🔴 **KHÔNG có điểm một phần.** Đúng 1/2 vẫn **sai cả câu** |
| **Kéo–thả (drag & drop)** | Ít hơn | ⭐ **Làm cặp chắc chắn trước**, còn lại suy ra bằng loại trừ |

> 🔴  **Câu "chọn 2" là nơi mất điểm oan nhất.**
> ⭐ Người học thường **thấy một đáp án đúng là mừng quá bấm luôn**, quên rằng phải đủ hai.
> ⭐ **Thói quen phải rèn: đọc kỹ dòng "(Choose two.)" TRƯỚC khi đọc đáp án.**

### 2.3 ⭐ Ba kiểu bẫy mà đề ENCOR hay dùng

> ⭐ **Đây không phải "mẹo thi" — đây là cách đề kiểm tra xem bạn hiểu SÂU hay chỉ thuộc lòng.**

#### Bẫy 1 — Đúng kỹ thuật nhưng sai ngữ cảnh

> ⭐ Đề mô tả một tình huống, và trong 4 đáp án có **2–3 cái đều là lệnh/khái niệm ĐÚNG**,
> nhưng chỉ **một cái đúng với TÌNH HUỐNG đó**.
>
> ⭐ **Ví dụ:** *"Cổng access nối PC, muốn chặn switch lạ chiếm quyền root."*
> ⭐ **BPDU Guard và Root Guard đều là câu trả lời hợp lý về mặt kỹ thuật** —
> nhưng "cổng access nối PC" chỉ có **một** đáp án đúng.
>
> 🔴 **Cách chống:**  **đọc kỹ danh từ chỉ VỊ TRÍ và VAI TRÒ** *(cổng access? trunk? biên? lõi?)*.
> Đề cài chìa khoá ở đó.

#### Bẫy 2 — Đảo chiều hai khái niệm đối nhau

> ⭐ Đề rất thích các cặp mà người học **nhớ được tên nhưng lẫn chiều**:
>
> | Cặp hay bị đảo | Nhớ đúng |
> |---|---|
> | **Local Preference / AS-path** | LocalPref **CAO** thắng · AS-path **NGẮN** thắng |
> | **401 / 403** | 401 = **danh tính** · 403 = **quyền hạn** |
> | **Northbound / Southbound** | North = **lên** ứng dụng · South = **xuống** thiết bị |
> | **HSRP preempt / VRRP preempt** | HSRP **TẮT** sẵn · VRRP **BẬT** sẵn |
> | **IGMP Querier / PIM DR** | Querier = IP **thấp** nhất · DR = IP **cao** nhất |
> | **`Content-Type` / `Accept`** | Content-Type = thứ tôi **GỬI** · Accept = thứ tôi **NHẬN** |
>
> 🔴 **Cách chống:**  **học theo CẶP, không học rời.** Mỗi lần nhớ một cái, nhớ luôn cái ngược lại.

#### Bẫy 3 — Câu hỏi có điều kiện ẩn

> ⭐ Đề cho một cấu hình rồi hỏi kết quả — nhưng **kết quả phụ thuộc vào một dòng bạn dễ bỏ qua**.
>
> ⭐ **Ví dụ:** hỏi "traffic đi đường nào?" khi có cả static route lẫn OSPF —
> ⭐ **câu trả lời phụ thuộc AD**, mà AD lại nằm ở một dòng khác trong cấu hình.
>
> 🔴 **Cách chống:**  **đọc TOÀN BỘ đoạn config trước khi đọc câu hỏi.** Đừng đọc câu hỏi rồi
> mới quét config tìm đáp án — cách đó khiến bạn bỏ sót dòng quyết định.

---

## ⚙️ PHẦN 2 — ÔN TẬP NHANH 6 DOMAIN

> ⭐ **Cách dùng phần này:** mỗi ngày đọc **một domain**, che cột phải, tự trả lời.
> 🔴 **Đừng đọc một lượt cả 6 domain trong một buổi** — không đọng lại gì.

### 3.1 Domain 3.0 — Infrastructure (30% — phần lớn nhất)

**Layer 2**

| Hỏi | Đáp |
|---|---|
| STP có mấy trạng thái? RSTP mấy? | STP **5** *(Disabled·Blocking·Listening·Learning·Forwarding)* · RSTP **3** *(Discarding·Learning·Forwarding)* |
| Timer STP mặc định | Hello **2s** · Forward delay **15s** · Max age **20s** → hội tụ ~**50s** |
| Priority STP nhận bội số của | **4096** |
| BPDU Guard vs Root Guard | BPDU Guard: **cổng access**, nhận BPDU nào cũng **err-disable** · Root Guard: **cổng trunk**, chỉ chặn BPDU **tốt hơn**, **tự phục hồi** |
| Loop Guard chống gì | **Mất BPDU** trên cổng non-designated → chống vòng lặp một chiều |
| EtherChannel: giao thức | **LACP** *(chuẩn mở)* · **PAgP** *(Cisco)* |
| LACP mode nào không lên | 🔴 **Cả hai đầu `passive`** |
| `(P)` `(I)` `(s)` `(D)` | P=trong bó · 🔴 **I=chạy độc lập, bó KHÔNG lên** · s=treo · D=down |
| MST: 3 thứ phải giống để cùng region | **Tên region · số revision · bảng ánh xạ VLAN→instance** |

**Định tuyến chung**

| Hỏi | Đáp |
|---|---|
| AD: Connected · Static · eBGP · OSPF · EIGRP · RIP · iBGP | **0 · 1 · 20 · 110 · 90 · 120 · 200** |
| Thứ tự chọn tuyến | 🔴 **Prefix dài nhất → AD nhỏ nhất → metric nhỏ nhất** |
| CEF gồm 2 bảng | **FIB** *(từ RIB)* và **Adjacency table** *(lớp 2)* |
| Vì sao `debug ip packet` không thấy traffic xuyên qua | 🔴 **CEF chuyển ở phần cứng, không lên CPU** |

**OSPF**

| Hỏi | Đáp |
|---|---|
| Có mấy trạng thái neighbor | 🔴 **8** — luồng thường **7** *(Down→Init→2-Way→ExStart→Exchange→Loading→Full)*; **Attempt** là thứ 8, **chỉ ở NBMA** |
| Kẹt ExStart/Exchange = lỗi gì | 🔴 **MTU mismatch** |
| LSA 1·2·3·4·5·7 | Router · Network · Summary liên vùng · ASBR Summary · External · **NSSA External** |
| Stub chặn gì | LSA **5** |
| Totally stubby chặn gì | LSA **3, 4, 5** → thay bằng **một default** |
| NSSA cho phép gì | LSA **7** *(ASBR trong vùng)*, vẫn chặn LSA 5 |
| `area X range` vs `summary-address` | `range` = tóm tắt **liên vùng**, ở **ABR** · `summary-address` = tóm tắt **tuyến ngoại**, ở **ASBR** |
| Timer mặc định broadcast / NBMA | Hello **10**/Dead **40** · NBMA Hello **30**/Dead **120** |
| Reference bandwidth | 🔴 **Phải đặt GIỐNG NHAU trên mọi router** |

**BGP**

| Hỏi | Đáp |
|---|---|
| eBGP vs iBGP AD | **20** vs **200** |
| iBGP: thiếu gì thì tuyến không dùng được | 🔴 **`next-hop-self`** |
| Peer bằng loopback cần thêm | 🔴 **`update-source Loopback0`** |
| Thứ tự chọn đường *(đầu bảng)* | **Weight cao → LocalPref cao → tự sinh → AS-path ngắn → Origin (i<e<?) → MED thấp → eBGP hơn iBGP** |
| Weight và LocalPref: phạm vi | Weight **chỉ trong 1 router** · LocalPref **trong cả AS** |
| Ảnh hưởng traffic ĐI RA / ĐI VÀO | Ra = **LocalPref** · Vào = 🔴 **AS-path prepend** |
| LocalPref/AS-path: chiều nào thắng | 🔴 **LocalPref CAO thắng · AS-path NGẮN thắng** |

**FHRP**

| Hỏi | HSRP | VRRP | GLBP |
|---|---|---|---|
| Của ai | Cisco | **Chuẩn mở** | Cisco |
| Multicast | v1 **224.0.0.2** · v2 **224.0.0.102** | **224.0.0.18** | **224.0.0.102** |
| Vận chuyển | **UDP 1985** | **IP protocol 112** | **UDP 3222** |
| vMAC | v1 `0000.0C07.AC`+grp · v2 `0000.0C9F.F`+grp | `0000.5E00.01`+VRID | `0007.B400.`+grp+AVF |
| 🔴 **Preempt mặc định** | 🔴 **TẮT** | 🔴 **BẬT** | Tắt |
| Cân bằng tải | Không *(trừ nhiều group)* | Không | 🔴 **CÓ — nhiều AVF** |

---

**Wireless** *(cũng thuộc Domain 3.0 — mục 3.3)*

| Hỏi | Đáp |
|---|---|
| CAPWAP dùng cổng nào | 🔴 **Control 5246 · Data 5247** *(UDP)* |
| 802.11a/b/g/n/ac/ax băng tần | a=**5** · b/g=**2.4** · n=**cả hai** · ac=🔴 **chỉ 5** · ax=**2.4+5+6** |
| Channel 2.4 GHz không chồng lấn | 🔴 **1 – 6 – 11** |
| DFS bắt buộc ở băng nào | **UNII-2A** *(52–64)* và **UNII-2C** *(100–144)* |
| CAC bao lâu | **60 giây** · 🔴 **TDWR (ch 120/124/128) = 600 giây** |
| Phát hiện radar thì | Rời channel trong **10 giây**, không quay lại **30 phút** |
| Thiết kế RSSI tối thiểu | 🔴 **≥ −67 dBm** ở mọi điểm cần phủ |
| Channel bonding 40 MHz | Mất 🔴 **−3 dB SNR** |
| AP mode local vs FlexConnect | Local: data về WLC · FlexConnect: 🔴 **data thoát tại chỗ**, port switch phải là **trunk** |
| Roaming trong cùng mobility group | **Intra-controller** *(nhanh)* vs **Inter-controller** |

**IP Services** *(mục 3.4)*

| Hỏi | Đáp |
|---|---|
| NAT: thiếu từ khoá nào thì không phải PAT | 🔴 **`overload`** |
| NAT không chạy mà không báo lỗi | 🔴 **Quên `ip nat inside` / `ip nat outside`** |
| NTP stratum | Càng nhỏ càng gần nguồn chuẩn; `ntp master N` đặt stratum N |
| IGMP Querier bầu theo | 🔴 **IP THẤP nhất** |
| PIM DR bầu theo | 🔴 **IP CAO nhất** |
| PIM Sparse vs Dense | Sparse: **kéo theo yêu cầu** *(cần RP)* · Dense: **đẩy rồi cắt tỉa** |

### 3.2 Domain 5.0 — Security (20%)

| Hỏi | Đáp |
|---|---|
| TACACS+ vs RADIUS: cổng | TACACS+ 🔴 **TCP 49** · RADIUS **UDP 1812/1813** |
| TACACS+ vs RADIUS: mã hoá | TACACS+ 🔴 **mã hoá TOÀN BỘ gói** · RADIUS **chỉ mã hoá mật khẩu** |
| TACACS+ vs RADIUS: tách AAA | TACACS+ 🔴 **tách riêng 3 phần** · RADIUS **gộp Authen+Author** |
| Dùng cái nào cho quản trị thiết bị | 🔴 **TACACS+** *(vì có authorization từng lệnh)* |
| Dùng cái nào cho 802.1X | 🔴 **RADIUS** |
| ACL vty dùng lệnh gì | 🔴 **`access-class`**, không phải `ip access-group` |
| IPv6 ACL: bẫy gì | 🔴 **`deny ipv6 any any` tường minh sẽ GIẾT NDP** → phải `permit icmp any any nd-na/nd-ns` **TRƯỚC** |
| CoPP áp ở đâu | 🔴 **`control-plane`**, không phải interface |
| CoPP: lớp định tuyến nên đặt | 🔴 **`exceed-action transmit`** *(chỉ đếm, không bóp)* |
| 802.1X: 3 vai trò | **Supplicant** *(client)* · **Authenticator** *(switch)* · **Authentication server** *(RADIUS)* |
| MACsec hoạt động ở lớp nào | **Lớp 2** — mã hoá chặng-tới-chặng |
| TrustSec: SGT là gì | Thẻ gắn vào traffic theo **danh tính**, không theo IP · SXP dùng cổng **64999** |
| SSH: sinh khoá cần gì trước | 🔴 **hostname + ip domain-name** |

### 3.3 Domain 4.0 — Network Assurance (10%)

| Hỏi | Đáp |
|---|---|
| Syslog: 8 mức, 0 và 7 là gì | **0 = Emergency** · **7 = Debug** — 🔴 **số nhỏ = nghiêm trọng hơn** |
| `logging trap` vs `logging buffered` | trap = **gửi đi** · buffered = **giữ tại chỗ**. 🔴 **Gửi đi nên CHẶT hơn** |
| Thiếu gì thì log vô giá trị | 🔴 **`service timestamps log datetime msec`** + **NTP** |
| SNMP cổng | **161** *(truy vấn)* · **162** *(trap/inform)* |
| Trap vs Inform | Inform 🔴 **có xác nhận**, trap thì không |
| SNMPv3: 3 mức bảo mật | **noAuthNoPriv · authNoPriv · authPriv** |
| Flexible NetFlow: 4 thành phần | 🔴 **record → exporter → monitor → áp lên interface** |
| `match` vs `collect` | `match` = **khoá** định nghĩa luồng · `collect` = **số liệu** đếm thêm |
| Lỗi số 1 của FNF | 🔴 **Quên áp `ip flow monitor` lên interface** → cache rỗng |
| SPAN / RSPAN / ERSPAN | Cùng switch · qua **VLAN chuyên dụng** *(cần `remote-span`)* · qua **L3 bằng GRE** |
| ERSPAN mặc định | 🔴 **Bị `shutdown`** — phải `no shutdown` |
| IP SLA: `source-interface` | Cú pháp **tùy chọn**, nhưng 🔴 **thiếu là đo sai đường** → track không bao giờ Down |
| IP SLA: quên gì thì không chạy | 🔴 **`ip sla schedule ... life forever start-time now`** |
| 🔴 **Mục 4.7 là gì** | 🔴 **NETCONF/RESTCONF** — xem Domain 6.0 bên dưới |

### 3.4 Domain 6.0 — Automation (15%)

| Hỏi | Đáp |
|---|---|
| NETCONF / RESTCONF cổng | 🔴 **SSH 830** / 🔴 **HTTPS 443** |
| Định dạng | NETCONF **chỉ XML** · RESTCONF **JSON hoặc XML** |
| Cái nào rollback được | 🔴 **CHỈ NETCONF** *(có `candidate` + `commit`)* |
| Cả hai dùng chung gì | 🔴 **YANG** |
| YANG là gì | 🔴 **KHUÔN dữ liệu**, không phải giao thức |
| YANG: 4 loại node | **leaf · leaf-list · container · list** *(list có KHOÁ)* |
| HTTP verb idempotent | 🔴 **GET · PUT · DELETE** *(POST và PATCH thì KHÔNG)* |
| 200 / 201 / 204 | OK có dữ liệu · Đã tạo · Xong nhưng **không có nội dung** |
| 🔴 **401 vs 403** | 🔴 **401 = danh tính** *(chưa/sai token)* · **403 = quyền hạn** |
| 415 nghĩa là | 🔴 **Sai `Content-Type`** — RESTCONF cần `application/yang-data+json` |
| JSON: 3 điều cấm | 🔴 **Không comment · không dấu phẩy thừa · không nháy đơn** |
| JSON vs Python: true/false/null | JSON **viết thường** · Python **`True`/`False`/`None`** |
| EEM: bộ khung | 🔴 **`event` (khi nào) + `action` (làm gì)** |
| EEM: bẫy thứ tự | 🔴 **Nhãn sắp theo CHUỖI: 1 → 10 → 2.** Luôn viết `1.0`, `2.0` |
| EEM: thiếu gì thì lệnh show hỏng | 🔴 **`action 1.0 cli command "enable"`** |
| Agentless / Agent | 🔴 **Ansible, SaltStack(ssh)** / 🔴 **Puppet, Chef** |
| Push / Pull | Ansible, Salt = **push** · Puppet, Chef = **pull** |
| DNAC vs vManage xác thực | DNAC **token** *(`X-Auth-Token`)* · vManage **cookie** *(`JSESSIONID`)* |
| Northbound / Southbound | North = **lên ứng dụng** · South = **xuống thiết bị** |

### 3.5 Domain 1.0 Architecture (15%) & 2.0 Virtualization (10%)

| Hỏi | Đáp |
|---|---|
| 3 lớp kiến trúc | **Access · Distribution · Core** |
| Collapsed core là gì | Gộp Distribution + Core — hợp với site nhỏ |
| SD-Access: 2 mặt phẳng địa chỉ | **Underlay** *(mạng vật lý)* · **Overlay** *(VXLAN)* |
| SD-Access dùng 3 giao thức | 🔴 **LISP** *(control)* · **VXLAN** *(data)* · **TrustSec/SGT** *(policy)* |
| SD-WAN: 4 thành phần | **vManage** *(quản lý)* · **vSmart** *(control)* · **vBond** *(kết nối ban đầu)* · **vEdge/cEdge** *(data)* |
| VXLAN cổng / phần thêm | 🔴 **UDP 4789** · thêm **50 byte** |
| LISP cổng | **4342** *(control)* · **4341** *(data)* |
| GRE thêm bao nhiêu byte | 🔴 **24 byte** → MTU thường còn **1476** |
| VRF-lite là gì | Nhiều **bảng định tuyến riêng** trên cùng một thiết bị |
| 🔴 Ping trong VRF | 🔴 **Phải khai `vrf`**, không thì nó dùng bảng global |
| `ip vrf` vs `vrf definition` | Cũ *(chỉ IPv4)* vs mới *(đa giao thức, có address-family)* |
| QoS: DSCP EF · CS3 · CS6 · AF41 | 🔴 **46 · 24 · 48 · 34** |
| Công thức AFxy | 🔴 **8x + 2y** |
| Ngưỡng thoại | 🔴 **Trễ ≤ 150 ms · Jitter ≤ 30 ms · Mất gói ≤ 1%** |
| Shaping vs Policing | Shaping **đệm lại rồi gửi từ từ** · Policing 🔴 **vứt hoặc hạ mức ngay** |
| Trust boundary nên đặt ở | 🔴 **Càng gần thiết bị đầu cuối càng tốt** *(access layer)* |

---

## 🧪 PHẦN 3 — LAB CAPSTONE

> 🔴 **Đây là cửa số 1. Làm TRƯỚC khi luyện đề.**

> ### 👉 **[LAB CAPSTONE — Dự án "Mạng công ty VLT"](Module-13-LAB-Capstone.md)**

| | |
|---|---|
| **Quy mô** | 6 node · ~3,5 GB RAM · 12–16 giờ |
| **Hình thức** | 🔴 **13 Task theo yêu cầu NGHIỆP VỤ** — đề không nói cho bạn dùng lệnh gì |
| **Chấm** | 100 điểm · đạt từ **80** |
| 🔴 **Phần quan trọng nhất** | 🔴 **5 bài DIỄN TẬP SỰ CỐ** ở cuối — kiểm tra hệ thống **ghép lại** có chạy không |

> ⭐ **Vì sao capstone quan trọng hơn luyện đề:**
> ⭐ Đề trắc nghiệm cho bạn **4 đáp án để nhận ra**. Capstone bắt bạn **tạo ra từ con số 0**.
> 🔴 **Rất nhiều người làm đề được 85% nhưng không dựng nổi hệ thống** — và chính nhóm đó
> hay trượt ở những câu tình huống của đề thật.
>
> ⭐ Ngoài ra, capstone lộ ra một loại lỗi mà **đề trắc nghiệm không bao giờ hỏi được**:
> 🔴 **lỗi ghép nối** — mỗi phần đúng, nhưng lắp vào nhau thì hỏng.

---

## 🏗️ PHẦN 4 — LUYỆN ĐỀ & LỘ TRÌNH CUỐI

### 4.1 Luyện đề thế nào cho có ích

| Nguyên tắc | Chi tiết |
|---|---|
| 🔴 **Ít nhất 2 nguồn khác nhau** | Quen một bộ đề là bạn đang **học thuộc bộ đề đó**, không phải học kiến thức |
| 🔴 **Bấm giờ THẬT ngay từ lần đầu** | **120 phút, không dừng, không tra tài liệu.** Luyện không bấm giờ gần như vô ích |
| 🔴 **Tập KHÔNG quay lại câu trước** | Đề thật không cho quay lại. Luyện mà cho phép quay lại là luyện sai điều kiện |
| ⭐ **Chấm xong phải đọc lại CẢ câu đúng** | Nhiều câu bạn **đúng do đoán** — đó là lỗ hổng chưa lộ |
| 🔴 **Ghi câu sai vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md)** | Ghi **lý do sai**, không chỉ ghi đáp án đúng |
| **Mục tiêu: ≥ 85% ổn định qua 3 bộ khác nhau** | 🔴 **"Ổn định" nghĩa là 3 lần liên tiếp**, không phải may một lần |

> 🔴 **Sai lầm phổ biến:** làm đi làm lại **một** bộ đề tới khi được 95%.
> ⭐ **Con số đó không nói lên gì cả** — bạn chỉ đang nhớ thứ tự đáp án.

### 4.2 🔴 Quản lý thời gian trong phòng thi

```
   120 phút  ÷  ~100 câu  ≈  1 phút 12 giây / câu
```

| Loại câu | Thời gian nên dùng | Nếu quá thì |
|---|---|---|
| **Câu bạn biết chắc** | **< 30 giây** | — |
| **Câu phải suy luận** | **1–2 phút** | — |
| 🔴 **Câu bạn không biết** | 🔴 **TỐI ĐA 2 phút** | 🔴 **Loại trừ, chọn đáp án hợp lý nhất, BẤM TIẾP** |

> 🔴  **Đây là điều quan trọng nhất của cả §4:**
> ⭐ **Vì không quay lại được, mỗi phút bạn nấn ná ở một câu khó là một phút bị LẤY MẤT
> khỏi những câu dễ ở phía sau mà bạn chắc chắn làm được.**
>
> 🔴 **Ngồi 6 phút với một câu khó rồi vẫn sai = bạn vừa mất câu đó CỘNG THÊM 4–5 câu dễ phía sau.**
> ⭐ **Đổi một câu khó lấy 4 câu dễ luôn là món hời.**

⭐ **Mốc tự kiểm trong phòng thi:**

| Đã dùng | Nên đang ở khoảng câu |
|:---:|---|
| 30 phút | ~25 |
| 60 phút | ~50 |
| 90 phút | ~75 |

> ⭐ **Chậm hơn mốc → tăng tốc ngay, cắt bớt thời gian đắn đo.**
> ⭐ **Nhanh hơn nhiều → bạn đang đọc quá nhanh, dễ sót chữ "(Choose two.)".**

### 4.3 Lộ trình 7 ngày cuối

| Ngày | Làm gì | Bao lâu |
|:---:|---|:---:|
| **−7** | 🔴 **Làm LAB Capstone, Task 1 → 6** | 6 giờ |
| **−6** | 🔴 **Capstone Task 7 → 13 + toàn bộ Diễn tập** | 6 giờ |
| **−5** | **Vá lỗ hổng** — quay lại đúng module bị mất điểm | 4 giờ |
| **−4** | **Đề số 1** *(bấm giờ)* → chấm → đọc lại **cả câu đúng** | 4 giờ |
| **−3** | **Đề số 2** *(nguồn khác)* → chấm → ghi sổ lỗi | 4 giờ |
| **−2** | **Đề số 3** → chấm · ⭐ **đọc lại toàn bộ [`SO-TAY-LOI.md`](SO-TAY-LOI.md)** | 4 giờ |
| **−1** | 🔴 **KHÔNG học cái mới.** Chỉ đọc §3 *(bảng số)* + ngủ sớm | 2 giờ |
| **Ngày thi** | Xem §6 | — |

> 🔴 **Ngày −1 tuyệt đối không học kiến thức mới.**
> ⭐ Não cần thời gian sắp xếp lại thứ đã học. **Nhồi thêm vào ngày cuối chỉ làm nhiễu
> những gì bạn đã nắm chắc**, và làm bạn mất ngủ — thứ tai hại hơn nhiều so với việc
> thiếu một kiến thức lẻ.

---

# 📎 PHỤ LỤC

---

## 🚪 5. CHECKLIST TRƯỚC KHI ĐÓNG TIỀN

> 🔴 **Đây là cửa cuối. Chưa tick đủ thì đừng book exam** — tiền thi không rẻ và không hoàn lại.

### Cửa 1 — Năng lực thực hành

| ☐ | Điều kiện |
|:---:|---|
| ☐ | **LAB Capstone đạt ≥ 80/100** |
| ☐ | 🔴 **Qua đủ 5 bài Diễn tập sự cố** *(đặc biệt Diễn tập 3 — đường chết mà router sống)* |
| ☐ | **Vẽ lại được sơ đồ capstone bằng tay**, đủ IP · VLAN · AS · area |
| ☐ | 🔴 **Tự viết được một EEM applet từ đầu** không nhìn tài liệu *(blueprint 6.6 bắt CONSTRUCT)* |
| ☐ | Bật được NETCONF/RESTCONF và gọi được một lệnh RESTCONF |

### Cửa 2 — Năng lực làm đề

| ☐ | Điều kiện |
|:---:|---|
| ☐ | 🔴 **≥ 85% ổn định qua 3 bộ đề KHÁC NHAU** |
| ☐ | **Làm đủ 120 phút mà không hết giờ** |
| ☐ | **Không quay lại câu trước** trong lúc luyện |
| ☐ | Đã **đọc lại cả những câu làm đúng** và biết mình đúng vì hiểu hay vì đoán |

### Cửa 3 — Phủ kín blueprint

| ☐ | Domain | % | Tự tin? |
|:---:|---|:---:|---|
| ☐ | **3.0 Infrastructure** | 30% | 🔴 Yếu chỗ này thì **không cứu được bằng chỗ khác** |
| ☐ | **5.0 Security** | 20% | |
| ☐ | **1.0 Architecture** | 15% | |
| ☐ | **6.0 Automation** | 15% | 🔴 Nhớ **mục 6.6 bắt CONSTRUCT** |
| ☐ | **2.0 Virtualization** | 10% | |
| ☐ | **4.0 Assurance** | 10% | 🔴 **Đừng quên mục 4.7 NETCONF/RESTCONF** |

> 🔴 **Nếu còn thiếu một ô nào ở Cửa 1 hoặc Cửa 2 — đừng book.**
> ⭐ **Lùi 2 tuần rẻ hơn rất nhiều so với trượt một lần.**

---

## 📅 6. NGÀY THI

| Việc | Chi tiết |
|---|---|
| **Giấy tờ** | 🔴 **Hai giấy tờ tuỳ thân**, một cái có ảnh. **Tên phải KHỚP CHÍNH XÁC** với tên đăng ký |
| **Đến sớm** | **30 phút** — trung tâm cần thời gian làm thủ tục |
| **Thi tại nhà** | Kiểm tra trước: webcam · mạng ổn định · bàn trống hoàn toàn · phòng riêng |
| **Trước khi vào** | Đi vệ sinh · uống nước · **không uống quá nhiều cà phê** |
| **Bảng nháp** | Trung tâm cấp. ⭐ **Việc đầu tiên: viết ra vài bảng số bạn sợ quên** *(AD · DSCP · cổng)* |
| 🔴 **Trong khi thi** | 🔴 **Đọc kỹ "(Choose two.)"** · **không nấn ná quá 2 phút một câu** · **bám mốc thời gian §4.2** |
| **Biết kết quả** | Ngay sau khi nộp bài |

> ⭐ **Mẹo nhỏ nhưng thật sự có ích:**  **ngay khi vào chỗ ngồi, trước khi bấm bắt đầu,
> viết ra bảng nháp những con số bạn hay quên nhất** — bảng AD, DSCP, cổng NETCONF/RESTCONF,
> thứ tự BGP. ⭐ **Lúc đó đầu bạn còn tỉnh táo nhất.** Về sau chỉ việc nhìn xuống.

---

## 🔄 7. NẾU TRƯỢT

> ⭐ **Trượt ENCOR không hiếm. Nó là bài thi khó và rộng.** Việc cần làm:

| Bước | Làm gì |
|:---:|---|
| 1 | ⭐ **Đọc kỹ bảng điểm theo domain** mà Cisco trả về — nó chỉ đúng chỗ bạn yếu |
| 2 | ⭐ **Ghi lại NGAY những câu/chủ đề bạn thấy khó** *(trong 1 giờ đầu, lúc còn nhớ)* |
| 3 | ⭐ **Quay lại đúng module của domain yếu nhất** — đừng học lại từ đầu |
| 4 | ⭐ **Làm lại LAB Capstone**, tập trung vào domain đó |
| 5 | ⚠️ **Chờ đủ thời gian quy định của Cisco mới được thi lại** — xem chính sách lúc đó |

> ⭐ **Đừng book lại ngay tuần sau.**  **Trượt vì thiếu nền tảng thì thi lại sớm cũng trượt tiếp.**

---

## 🎯 8. ĐÚC KẾT — BẠN ĐÃ ĐI QUA NHỮNG GÌ

| Giai đoạn | Tuần | Bạn có được gì |
|---|:---:|---|
| Nền tảng | 0–2 | Dựng được lab, ôn lại CCNA |
| **Infrastructure** | 3–11 | 🔴 **STP · OSPF · BGP · FHRP · NAT — 30% đề, phần nặng nhất** |
| Wireless & Overlay | 12–15 | RF · CAPWAP · VRF · GRE · VXLAN · SD-WAN · SD-Access · QoS |
| Security | 16 | AAA · ACL · CoPP · 802.1X · TrustSec · MACsec |
| Assurance | 17 | Syslog · SNMP · NetFlow · SPAN · IP SLA |
| Automation | 18–19 | JSON · REST · YANG · NETCONF/RESTCONF · **EEM** · Ansible |
| **Tổng hợp** | 20 | 🔴 **Capstone chạm cả 6 domain + diễn tập sự cố** |

> ⭐ **Điều đáng giá nhất bạn mang theo không phải là tấm chứng chỉ.**
>
>  Đó là **cách nghĩ** mà capstone đã rèn: 🔴 **"thứ tôi vừa thêm vào có phá hỏng thứ tôi
> đã làm trước đó không?"** — câu hỏi mà người làm hệ thống thật hỏi liên tục.
>
> ⭐ Và **thói quen kiểm chứng bằng cách gây hỏng có chủ đích**, thay vì tin rằng
> "cấu hình đúng là chạy đúng".

---

## 🔗 9. TÀI LIỆU

| Nguồn | Dùng để |
|---|---|
| **[Blueprint chính thức 350-401](https://learningnetwork.cisco.com/)** | 🔴 **Đối chiếu lần cuối — đây là nguồn chuẩn duy nhất** |
| **Cisco Learning Network** | Diễn đàn, tài liệu, thông tin kỳ thi mới nhất |
| **Boson ExSim-Max 350-401** | Bộ đề sát nhất với đề thật *(có phí)* |
| **Cisco Press — CCNP ENCOR 350-401 OCG** | Sách chính thống |
| **[Cisco DevNet](https://developer.cisco.com/)** | Sandbox + tài liệu API cho Domain 6.0 |
| **Chính repo này** | 🔴 **Đọc §3 mỗi ngày 10 phút** trong tuần cuối |

---

> 🎓 **Chúc bạn thi tốt.**
>
> ⭐ Nếu bạn đã qua được **cả ba cửa** ở §5 thì bạn **không cần may mắn** —
> bạn đã làm đủ phần việc của mình rồi.
