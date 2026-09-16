# Module-05B — BGP: Best Path Selection & Filtering

> 🧭 **Lộ trình:** [Module-05A](Module-05A-BGP-Nen-tang-va-eBGP-Peering.md) → `[Bạn đang ở đây] Module-05B` → Module-06 (IP Services)
>
> 📊 **Blueprint:** Domain **3.0 Infrastructure (30%)**, mục **3.2.c — Configure and verify eBGP
> between directly connected neighbors (⭐ **best path selection algorithm** and neighbor relationships)**
>
> ⏱️ **Tuần 10** · 10 giờ
>
> ⚠️ **13 bước path selection là một trong những thứ đề ENCOR hỏi trực tiếp và chi tiết nhất.**
> Đây là module bạn phải học thuộc bảng, không chỉ hiểu.

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **"Tôi có nhiều đường ra Internet. Làm sao bắt traffic đi ĐÚNG đường tôi muốn —
> cả chiều ra lẫn chiều vào?"**

## Câu trả lời ngắn nhất — bảng này thay được nửa module

```
   ┌──────────────────────────────────────────────────────────────┐
   │  MUỐN ĐỔI CHIỀU TRAFFIC ĐI RA  (outbound)                    │
   │     →  LOCAL PREFERENCE   (bước 2)                           │
   │     →  đặt INBOUND trên router của mình                      │
   │     →  ⭐ MÌNH TỰ QUYẾT ĐƯỢC                                  │
   ├──────────────────────────────────────────────────────────────┤
   │  MUỐN ĐỔI CHIỀU TRAFFIC ĐI VÀO  (inbound)                    │
   │     →  AS-PATH PREPEND    (bước 4)                           │
   │     →  đặt OUTBOUND ra phía ISP                              │
   │     →  🔴 CHỈ LÀ GỢI Ý — người ta nghe hay không là quyền họ  │
   └──────────────────────────────────────────────────────────────┘

   ⭐ Một câu để nhớ:  "OUTBOUND mình QUYẾT — INBOUND mình chỉ XIN."
```

## 13 bước — nhưng thực tế chỉ cần nhớ 4 bước đầu

```
   1. WEIGHT            cao thắng   (chỉ local, không quảng bá)      ⭐
   2. LOCAL PREF        cao thắng   (lan trong AS)                   ⭐⭐
   3. Locally originated (route mình tự sinh ra)                     ⭐
   4. AS-PATH           NGẮN thắng                                   ⭐⭐
   ─────────────── 4 bước trên quyết định ~95% trường hợp ───────────
   5. Origin            IGP > EGP > Incomplete
   6. MED               THẤP thắng  (chỉ so trong cùng AS)
   7. eBGP > iBGP
   8. Metric IGP tới next-hop thấp nhất
   9-10. (tie-break kỹ thuật)
   11. ROUTER ID thấp nhất
   12-13. (tie-break cuối)
```

⭐ **Mẹo nhớ 4 bước đầu: "WLAA"** — **W**eight → **L**ocal pref → **A** (locally originated) → **A**S-path.

## 7 ý phải nhớ

| # | Ý | Một câu |
|:---:|---|---|
| 1 | ⭐⭐ **Outbound vs Inbound** | **LocPref** đổi chiều RA (mình quyết) · **AS-path prepend** tác động chiều VÀO (chỉ gợi ý) |
| 2 | **Weight vs LocPref** | Weight **chỉ local**, không quảng bá · LocPref **lan trong cả AS** |
| 3 | **Cao thắng hay thấp thắng?** | Weight **cao** · LocPref **cao** · AS-path **ngắn** · MED **thấp** · Router ID **thấp** |
| 4 | **MED chỉ so trong cùng AS** | Hai đường tới **cùng một ISP** mới so MED được |
| 5 | ⭐ **`no-export` vs `no-advertise`** | `no-export` = *đừng gửi ra khỏi AS* · `no-advertise` = *đừng gửi cho BẤT KỲ ai* |
| 6 | **Filtering 4 cách** | distribute-list · prefix-list · AS-path filter · route-map |
| 7 | 🔴 **Đừng nhận full BGP table** | Internet ~**900.000 prefix** — router nhỏ hết RAM và chết |

## Bảng lệnh cốt lõi

| Lệnh | Cho biết gì / làm gì |
|---|---|
| ⭐ `show ip bgp <prefix>` | **Mọi path tới prefix đó + vì sao chọn path này** — lệnh quan trọng nhất |
| `show ip bgp` | BGP table: `*` hợp lệ, `>` best |
| `show ip bgp neighbors <ip> advertised-routes` | Tôi đang **quảng bá** gì ra |
| `show ip bgp neighbors <ip> routes` | Tôi **nhận** được gì vào |
| `show ip bgp community <c>` | Route mang community nào |
| `show route-map` / `show ip prefix-list` | Policy khớp bao nhiêu lần |
| ⭐ `clear ip bgp * soft in` | **Xin gửi lại route mà KHÔNG ngắt phiên** |

## 🗺️ Bố cục module — đọc theo đúng thứ tự này

| Phần | Tên | Đọc thế nào | Thời gian |
|:---:|---|---|:---:|
| **1** | 🧠 **CÁI ĐÓ LÀ GÌ** | 5 ví von. ⭐ **§2.1 (quy trình đấu thầu) đọc TRƯỚC bảng 13 bước** | 45 phút |
| **2** | ⚙️ **NÓ CHẠY THẾ NÀO** | 9 mục. ⭐⭐ **Then chốt: §3.1 (13 bước), §3.2 (bảng điều khiển)** | 4 giờ |
| **3** | 🧪 **NHÌN THẤY NÓ** | [LAB 05B](Module-05B-LAB.md) — 9 bước, mỗi bước đổi **một** thuộc tính | 8 giờ |
| **4** | 🏗️ **TOPO & KIẾN TRÚC** | Bốn bài toán điều khiển traffic. **Vẽ lại trên giấy** | 45 phút |
| **📎** | **PHỤ LỤC** | 🔴 **KHÔNG đọc lần đầu** — chỉ tra | — |

> ⭐ **Cách học 13 bước mà không phải học vẹt:** ở [LAB](Module-05B-LAB.md), mỗi bước chỉ đổi
> **MỘT** thuộc tính, rồi chạy `show ip bgp <prefix>` và tự hỏi:
> ***"bước thứ mấy trong 13 bước vừa quyết định kết quả này?"***
>
> Trả lời được ở cả 9 bước lab thì bạn thuộc 13 bước một cách tự nhiên.
>
> 🎯 **Hết module này là mốc Tuần 11 — mốc quan trọng nhất nửa đầu khóa.**
> Đạt được nghĩa là bạn đã qua **toàn bộ khối routing** (30% đề).

---

## ✅ 1. Chuẩn bị

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | 🔴 **Module-05A BẮT BUỘC** — phải đọc được `show ip bgp` (`*`, `>`, Weight, Path, Origin) |
| | Module-03 §2.7 (route-map + prefix-list) · Module-04B §2.4 (filtering & catch-all) |
| **Lab** | ⭐ Dùng lại **LAB 05A**, **thêm 1 link** R4↔R3 để có 2 đường |
| **RAM** | 4× 512 MB = **2 GB** ✅ |
| **Thời lượng** | 4h lý thuyết · 4h lab · 2h quiz |

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> **Đọc phần này TRƯỚC, đọc một mạch.** Không lệnh, không bảng tra.
>
> Module-05B có **13 bước path selection** — nhìn vào là thấy nản. Nhưng có một ví von
> làm cả 13 bước trở nên logic. Đọc §2.1 trước khi mở bảng 13 bước ở Phần 2.
>
> **Tự kiểm tra:** đọc xong mỗi mục, gấp tài liệu lại, nói lại trong 3 câu.

### 2.1 13 bước như quy trình đấu thầu

Bạn mở đấu thầu, có nhiều nhà thầu. Bạn xét **theo thứ tự tiêu chí**, ai thắng ở tiêu chí nào
thì **dừng luôn**, không xét tiếp:

| Bước | Tiêu chí | Ví von |
|:---:|---|---|
| 0 | Next-hop reachable | ⭐ **Đủ hồ sơ hợp lệ?** Không thì loại ngay |
| 1 | **Weight** | ⭐ **"Tôi thích ai"** — quyết định của riêng tôi, không ai biết |
| 2 | **Local Pref** | ⭐ **"Công ty tôi thích ai"** — cả công ty thống nhất |
| 3 | Locally originated | **"Hàng nhà làm"** — ưu tiên tự làm |
| 4 | **AS-path** | ⭐ **"Ai qua ít trung gian nhất"** — tiêu chí khách quan nhất |
| 5 | **Origin** | **"Nguồn gốc rõ ràng hơn"** (`network` > `redistribute`) |
| 6 | **MED** | ⭐ **"Nhà thầu tự báo giá"** — nhưng chỉ so giữa các báo giá **cùng một hãng** |
| 7 | eBGP > iBGP | **"Người ngoài trực tiếp"** hơn "nghe kể lại" |
| 8 | IGP metric | **"Ai gần cửa hơn"** — ra ngoài nhanh nhất |
| 10–13 | Oldest / Router ID / Neighbor IP | ⭐ **Tung xúi xẻ có luật** — luôn ra kết quả nhất quán |

🧠 **Một câu để nhớ:** *2 bước đầu là **ý chí của TÔI** (Weight, LocPref — CAO thắng).
Từ bước 4 là **thực tế khách quan** (AS-path, Origin, MED — THẤP thắng).
Và 4 bước cuối chỉ để **không bao giờ có tie** — mạng phải ra được một quyết định.*

### 2.2 Vì sao "inbound chỉ là gợi ý"

Bạn muốn khách vào nhà bằng **cửa sau**. Bạn:
- Treo biển ở cửa trước: *"đường này xa lắm, đi vòng"* (**AS-path prepend**)
- Hoặc ghi giá: *"cửa trước phí 200, cửa sau phí 50"* (**MED**)

⚠️ Nhưng **khách vẫn có quyền** nói *"tôi thích cửa trước"* (**Weight/Local Pref của họ**)
→ vào cửa trước.

⭐ Vì Weight/LocPref là **bước 1–2**, còn AS-path/MED là **bước 4/6** → **họ thắng**.

🧠 **Một câu để nhớ:** *⭐ **Outbound = tôi quyết. Inbound = tôi xin.***
*Đó là bản chất của BGP — mỗi AS tự chủ về chính sách của mình.*

### 2.3 `no-export` vs `no-advertise` — hai mức bí mật

| | `no-export` | `no-advertise` |
|---|---|---|
| Ví von | ⭐ **"Nội bộ công ty"** — nhân viên biết được, khách hàng không | ⭐ **"Chỉ mắt anh"** — không kể cho ai, kể cả đồng nghiệp |
| iBGP peer | ✅ Được biết | ❌ Không |
| eBGP peer | ❌ Không | ❌ Không |

⭐ **Dùng thực tế của `no-export`:** ISP cấp cho bạn một prefix để dùng nội bộ, gắn `no-export`
→ bạn dùng được trong AS mình, nhưng **không thể** quảng bá ra Internet.

🧠 **Một câu để nhớ:** *`no-export` = "đừng **xuất khẩu**" (ra khỏi AS).
`no-advertise` = "đừng **nói** với ai cả". Và ⭐ nhớ `send-community` —
không bật thì bạn dán nhãn mà không ai đọc được.*

### 2.4 Prefix-list `0.0.0.0/0` vs `0.0.0.0/0 le 32`

| Viết | Nghĩa | Ví von |
|---|---|---|
| ⭐ `permit 0.0.0.0/0` | ⭐ **CHỈ** đúng default route `0.0.0.0/0` | *"Cho phép **đúng một người** tên là 0.0.0.0/0"* |
| ⭐ `permit 0.0.0.0/0 le 32` | ⭐ **MỌI** prefix (mask 0→32) | *"Cho phép **mọi người**"* |

🔴 **Đây là lỗi gây downtime thật.** Bạn viết `permit 0.0.0.0/0` tưởng là catch-all,
thực tế chỉ cho qua default route → ⭐ **mọi prefix khác bị implicit deny** → mất hết route.

🧠 **Một câu để nhớ:** *Không có `le 32` thì không phải catch-all. Nhớ ba ký tự này
tiết kiệm cho bạn một sự cố.*

### 2.5 `aggregate-address` như đóng thùng hàng

Bạn có 4 kiện hàng nhỏ (`10.1.0.0/24` → `10.1.3.0/24`).

| Cách | Ví von |
|---|---|
| *(không option)* | ⭐ Gửi **cả thùng lớn VÀ 4 kiện nhỏ** — người nhận thấy 5 thứ (trùng lặp) |
| ⭐ `summary-only` | ⭐ Gửi **chỉ thùng lớn**, 4 kiện nhỏ **giữ lại** (`s` = suppressed) |
| ⭐ `as-set` | ⭐ Dán nhãn thùng lớn: **"bên trong có hàng từ AS 65002 và 65003"** → giữ được chống loop |

⚠️ **Không có `as-set`:** thùng lớn **không ghi nguồn gốc** → AS-path chỉ có ASN của bạn
→ ⭐ **mất chống loop** → route có thể quay lại AS gốc. IOS thêm `Atomic Aggregate` để cảnh báo.

🧠 **Một câu để nhớ:** *`summary-only` giảm số route. `as-set` giữ an toàn.
Ở Internet thật, gộp mà không có `as-set` là một trong những nguyên nhân của route leak.*

---
## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

> Giờ lắp **cơ chế thật, con số và câu lệnh** vào hình dung bạn vừa có.
>
> | Phần 1 (ví von) | → | Phần 2 (cơ chế) |
> |---|:---:|---|
> | §2.1 quy trình đấu thầu | → | **§3.1 13 bước path selection** ⭐⭐ |
> | §2.2 inbound chỉ là gợi ý | → | **§3.2 Bảng điều khiển hướng traffic** ⭐⭐ |
> | §2.3 hai mức bí mật | → | **§3.7 BGP Community** |
> | §2.4 prefix-list `le 32` | → | **§3.8 Filtering (4 cách)** |
> | §2.5 đóng thùng hàng | → | **§3.9 `aggregate-address`** |
>
> ⚠️ **Hai mục quan trọng nhất: §3.1 và §3.2.** Nếu chỉ có thời gian cho hai mục, chọn hai mục đó.
>
> ⭐ **Mẹo với 13 bước:** đừng học thuộc cả 13. Thực tế **4 bước đầu quyết định 95% trường hợp**
> (Weight → LocPref → Locally originated → AS-path). Nắm chắc 4 bước đó trước, phần còn lại
> chỉ là tie-break.

### 3.1 ⭐⭐ 13 BƯỚC BEST PATH SELECTION

BGP không có metric duy nhất. Nó so sánh **từng attribute theo đúng thứ tự** —
bước nào phân định được thì **DỪNG**, không xét bước sau.

| # | Bước | So sánh | Ghi chú |
|:---:|---|---|---|
| **0** | ⭐ **Next-hop reachable?** | Bắt buộc | ⚠️ Không reachable → **loại ngay**, không có `*` |
| **1** | ⭐ **WEIGHT** | ⭐ **CAO nhất thắng** | Cisco-only, **chỉ local**. Mặc định 32768 (của mình) / 0 (học được) |
| **2** | ⭐ **LOCAL PREFERENCE** | ⭐ **CAO nhất thắng** | Mặc định **100**. Lan **trong AS** |
| **3** | ⭐ **LOCALLY ORIGINATED** | Route do **chính router này** sinh | `network` > `aggregate-address` > `redistribute` |
| **4** | ⭐ **AS-PATH ngắn nhất** | ⭐ **NGẮN nhất thắng** | ⭐ Bước "tự nhiên" nhất — thường quyết định trên Internet |
| **5** | ⭐ **ORIGIN** | ⭐ **THẤP nhất thắng** | ⭐ `i` (IGP) **<** `e` (EGP) **<** `?` (incomplete) |
| **6** | ⭐ **MED** | ⭐ **THẤP nhất thắng** | ⚠️ Mặc định **chỉ so giữa path từ CÙNG một AS kề** |
| **7** | ⭐ **eBGP > iBGP** | ⭐ **eBGP thắng** | |
| **8** | ⭐ **IGP metric tới next-hop** | ⭐ **THẤP nhất thắng** | "Hot potato routing" — ra khỏi AS càng sớm càng tốt |
| **9** | *(Multipath)* | Nếu bật `maximum-paths` → cài nhiều path | Không phải tie-break |
| **10** | ⭐ **eBGP path CŨ nhất** | Path tồn tại lâu hơn thắng | ⭐ Ưu tiên **ổn định** hơn tối ưu |
| **11** | ⭐ **Router ID thấp nhất** | ⭐ **THẤP nhất thắng** | Của **neighbor** quảng bá route |
| **12** | **Cluster-list ngắn nhất** | Ngắn nhất thắng | Chỉ có với Route Reflector |
| **13** | ⭐ **Neighbor IP thấp nhất** | ⭐ **THẤP nhất thắng** | Tie-break cuối cùng — luôn phân định được |

#### ⭐ Mnemonic — cách nhớ 13 bước

**Tiếng Anh (phổ biến nhất):**
> ### **W**e **L**ove **O**ranges **AS** **O**ranges **M**ean **P**ure **R**efreshment

| Chữ | Bước |
|:---:|---|
| **W**e | ⭐ **Weight** (cao) |
| **L**ove | ⭐ **Local Preference** (cao) |
| **O**ranges | ⭐ **Originated** locally |
| **AS** | ⭐ **AS-path** (ngắn) |
| **O**ranges | ⭐ **Origin** (i < e < ?) |
| **M**ean | ⭐ **MED** (thấp) |
| **P**ure | ⭐ **Paths** — eBGP > iBGP |
| **R**efreshment | ⭐ **Rest**: IGP metric → oldest → **R**outer ID → cluster-list → neighbor IP |

**Tiếng Việt (nếu dễ nhớ hơn):**
> **W**ệ · **L**ớn · **O**ai · **A**S · **O**rigin · **M**ED · **P**he eBGP · **R**outer ID

⭐ **Hai quy tắc CAO/THẤP:**

| ⬆️ Càng **CAO** càng tốt | ⬇️ Càng **THẤP** càng tốt |
|---|---|
| ⭐ **Weight** (bước 1) | ⭐ **AS-path length** (bước 4) |
| ⭐ **Local Preference** (bước 2) | ⭐ **Origin** (bước 5) |
| | ⭐ **MED** (bước 6) |
| | ⭐ **IGP metric** (bước 8) |
| | ⭐ **Router ID** (bước 11) |
| | ⭐ **Neighbor IP** (bước 13) |

🧠 ***Chỉ 2 bước đầu là "CAO thắng". Từ bước 4 trở đi, tất cả "THẤP thắng".***

#### ⚠️ Chi tiết quan trọng về bước 6 (MED)

> ⭐ **Mặc định MED CHỈ được so sánh giữa các path đến từ CÙNG MỘT AS kề.**

```
Path A: AS-path "65002 65010"  MED 50    ┐ cùng AS kề 65002 → SO ĐƯỢC
Path B: AS-path "65002 65020"  MED 100   ┘

Path C: AS-path "65004 65010"  MED 10    ← AS kề khác (65004) → ⚠️ KHÔNG so với A/B
```

**Hai lệnh đổi hành vi:**
```
router bgp 65001
 bgp always-compare-med                 ! so MED giữa MỌI AS (⚠️ có thể gây bất ổn)
 bgp deterministic-med                  ! nhóm path theo AS trước khi so — KẾT QUẢ NHẤT QUÁN
 bgp bestpath med missing-as-worst      ! MED thiếu = vô cực (mặc định coi = 0)
```

> ⭐ **`bgp deterministic-med` nên bật ở production.** Không có nó, kết quả path selection
> **phụ thuộc thứ tự router học được route** → khởi động lại router có thể chọn path khác.

#### ⚠️ MED thiếu được coi là bao nhiêu?

| | Cisco mặc định | Với `bgp bestpath med missing-as-worst` |
|---|---|---|
| MED không được đặt | ⭐ **0** (tốt nhất!) | ⭐ **4294967295** (tệ nhất) |

⚠️ **Bẫy:** path **không có MED** mặc định thắng path có MED 100 — vì 0 < 100.

---

### 3.2 ⭐⭐ ĐIỀU KHIỂN HƯỚNG TRAFFIC — bảng quan trọng nhất module

Đây là bảng bạn sẽ dùng khi đi làm, và đề hỏi rất nhiều.

| Muốn điều khiển | Attribute dùng | Áp ở **chiều** nào | Ai bị ảnh hưởng |
|---|---|---|---|
| ⭐ **OUTBOUND** — traffic **RA KHỎI** AS của tôi | ⭐ **Weight** (chỉ local) hoặc ⭐ **Local Preference** (cả AS) | ⭐ **`in`** (inbound route-map) | ⭐ **Chính tôi quyết định** — chắc chắn |
| ⭐ **INBOUND** — traffic **ĐI VÀO** AS của tôi | ⭐ **AS-path prepend** hoặc ⭐ **MED** | ⭐ **`out`** (outbound route-map) | ⚠️ **AS bên kia quyết định** — chỉ là **gợi ý** |

```
   ┌─────────────────────────────────────────────────────────────────┐
   │  AS của tôi (65001)                                             │
   │                                                                  │
   │  Traffic ĐI RA ──────▶  TÔI kiểm soát hoàn toàn              │
   │                          → Weight (1 router) / LocPref (cả AS)  │
   │                          → route-map áp chiều IN                 │
   │                                                                  │
   │  Traffic ĐI VÀO ◀─────  ⚠️ AS BÊN KIA quyết định                │
   │                          → AS-path prepend / MED = chỉ GỢI Ý     │
   │                          → route-map áp chiều OUT                │
   └─────────────────────────────────────────────────────────────────┘
```

🧠 **Câu thần chú:**
> ⭐ ***"Tôi nhận route vào → tôi quyết định đi ra đâu (in → outbound traffic).
> Tôi gửi route ra → tôi gợi ý người ta đi vào đâu (out → inbound traffic)."***

⭐ **Vì sao inbound chỉ là "gợi ý":** AS bên kia có thể ⭐ **ghi đè** bằng Weight/Local Preference
của họ — hai bước **đứng TRƯỚC** AS-path và MED trong 13 bước. Bạn không kiểm soát được.

| Kỹ thuật | Kiểm soát | Độ tin cậy |
|---|---|---|
| ⭐ **Weight** | 1 router | ⭐⭐⭐ Chắc chắn (nhưng chỉ 1 router) |
| ⭐ **Local Preference** | Cả AS | ⭐⭐⭐ Chắc chắn trong AS mình |
| ⭐ **AS-path prepend** | Gợi ý AS khác | ⭐⭐ Thường hiệu quả (bước 4) |
| ⭐ **MED** | Gợi ý AS kề | ⭐ Yếu nhất (bước 6, và mặc định chỉ so cùng AS) |
| **Community** | Nhờ AS kề áp policy | ⭐⭐ Tùy AS kề có hỗ trợ |

---

### 3.3 Weight (bước 1)

| Thuộc tính | Giá trị |
|---|---|
| Bản chất | ⭐ **Cisco-only**, **KHÔNG phải attribute BGP** |
| Phạm vi | ⭐ **CHỈ local router** — không gửi cho bất kỳ peer nào |
| Giá trị | 0 – 65535 |
| Mặc định | ⭐ **32768** (route của chính mình) · **0** (học từ peer) |
| Tốt nhất | ⭐ **CAO nhất** |

```
! ═══ Cách 1: cho MỌI route từ 1 neighbor ═══
router bgp 65001
 neighbor 10.0.12.2 weight 200

! ═══ Cách 2 (linh hoạt hơn): route-map — chỉ 1 số prefix ═══
ip prefix-list PL-IMPORTANT permit 10.3.3.0/24
!
route-map RM-SET-WEIGHT permit 10
 match ip address prefix-list PL-IMPORTANT
 set weight 500
route-map RM-SET-WEIGHT permit 20              ! catch-all
!
router bgp 65001
 neighbor 10.0.12.2 route-map RM-SET-WEIGHT in     ! chiều IN
```

⭐ **Khi nào dùng Weight thay Local Preference:**

| | Weight | Local Preference |
|---|---|---|
| Phạm vi | ⭐ **1 router** | ⭐ **Cả AS** (lan qua iBGP) |
| Dùng khi | AS chỉ có 1 router biên, hoặc muốn **chỉ router này** đi khác | AS nhiều router, muốn **cả AS** đi cùng hướng |
| Ưu tiên | ⭐ Bước **1** (thắng cả LocPref) | Bước **2** |

---

### 3.4 Local Preference (bước 2)

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | **Well-known Discretionary** |
| Phạm vi | ⭐ **Trong AS** (lan qua iBGP), ⭐ **KHÔNG** qua eBGP |
| Mặc định | ⭐ **100** |
| Tốt nhất | ⭐ **CAO nhất** |
| Điều khiển | ⭐ **OUTBOUND traffic** của cả AS |

```
! ═══ Đổi giá trị mặc định cho cả router ═══
router bgp 65001
 bgp default local-preference 150

! ═══ Đặt theo prefix bằng route-map (cách chuẩn) ═══
ip prefix-list PL-VIA-ISP1 permit 10.3.3.0/24
!
route-map RM-ISP1-IN permit 10
 match ip address prefix-list PL-VIA-ISP1
 set local-preference 200                       ! ưu tiên đi qua ISP1
route-map RM-ISP1-IN permit 20                  ! catch-all
!
router bgp 65001
 neighbor 10.0.12.2 route-map RM-ISP1-IN in     ! chiều IN
```

⭐ **Kịch bản thực tế phổ biến nhất:**
```
! ISP1 = đường chính (băng thông lớn) → LocPref 200
route-map RM-ISP1-PRIMARY permit 10
 set local-preference 200
router bgp 65001
 neighbor <ISP1> route-map RM-ISP1-PRIMARY in

! ISP2 = đường dự phòng → giữ LocPref mặc định 100
! → cả AS ưu tiên ra qua ISP1; ISP1 chết thì tự chuyển ISP2
```

---

### 3.5 AS-path prepend (bước 4)

**Ý tưởng:** làm AS-path của mình **dài hơn** khi quảng bá cho một peer → peer đó thấy đường
qua mình **kém hơn** → chọn đường khác → traffic **vào** AS của tôi qua hướng khác.

```
! Áp chiều OUT — vì muốn ảnh hưởng INBOUND traffic
route-map RM-PREPEND-OUT permit 10
 set as-path prepend 65001 65001 65001         ! thêm 3 lần ASN của mình
!
router bgp 65001
 neighbor 10.0.14.2 route-map RM-PREPEND-OUT out
```

**Kết quả nhìn từ AS 65004:**
```
! TRƯỚC:
 *>  10.1.1.0/24   10.0.14.1   0   0  65001 i                    ← AS-path = 1

! SAU:
 *>  10.1.1.0/24   10.0.14.1   0   0  65001 65001 65001 65001 i  ← AS-path = 4
```

| Lưu ý | Chi tiết |
|---|---|
| Prepend **ASN của mình** | ⭐ Đúng chuẩn. Prepend ASN của người khác = **giả mạo**, có thể gây loop |
| Prepend bao nhiêu lần | ⭐ Thường **2–5**. Prepend quá nhiều (>10) có thể bị ISP filter |
| ⚠️ Không đảm bảo | Peer có thể ghi đè bằng **Weight/LocPref** (bước 1–2 > bước 4) |
| `set as-path prepend last-as <n>` | Prepend ASN của peer gần nhất, n lần |

---

### 3.6 MED (bước 6)

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | ⭐ **Optional Non-transitive** |
| Phạm vi | ⭐ Gửi **sang AS kề**, ⭐ **KHÔNG gửi tiếp** sang AS thứ 3 |
| Mặc định | ⭐ **0** (nếu không đặt) — và 0 là **tốt nhất** |
| Tốt nhất | ⭐ **THẤP nhất** |
| So sánh | ⚠️ Mặc định **chỉ giữa path từ CÙNG một AS kề** |
| Hiện ở | ⭐ Cột **`Metric`** trong `show ip bgp` |

```
! Áp chiều OUT — muốn ảnh hưởng INBOUND traffic
route-map RM-MED-OUT permit 10
 set metric 200                                ! "metric" trong route-map = MED
!
router bgp 65001
 neighbor 10.0.14.2 route-map RM-MED-OUT out
```

⭐ **Kịch bản đúng của MED:** AS của bạn có **2 link tới CÙNG một ISP** →
dùng MED để nói *"vào qua link A (MED 50) thay vì link B (MED 100)"*.

⚠️ **MED gần như vô dụng khi có 2 ISP khác nhau** — vì mặc định không so MED giữa 2 AS khác.
Lúc đó dùng **AS-path prepend**.

---

### 3.7 ⭐ BGP Community

**Ý tưởng:** gắn **nhãn** lên route → AS kề đọc nhãn và **áp chính sách** tương ứng.
Đây là cách **hợp tác** giữa 2 AS, thay vì áp đặt.

#### 4 well-known community

| Community | Giá trị | Hành vi | Dùng khi |
|---|---|---|---|
| ⭐ **`no-export`** | `0xFFFFFF01` | ⭐ **Không quảng bá cho eBGP peer** (nhưng vẫn trong AS + sub-AS confed) | "Route này chỉ dùng trong AS của bạn, đừng đưa ra Internet" |
| ⭐ **`no-advertise`** | `0xFFFFFF02` | ⭐ **Không quảng bá cho BẤT KỲ peer nào** (cả iBGP) | Route chỉ router nhận được dùng |
| ⭐ **`local-AS`**<br>(`no-export-subconfed`) | `0xFFFFFF03` | ⭐ Không ra khỏi **sub-AS** (confederation) | Chỉ dùng với confederation |
| **`internet`** | — | Quảng bá cho mọi peer (mặc định) | Xóa community |

⭐ **So sánh `no-export` và `no-advertise`:**

| | `no-export` | `no-advertise` |
|---|:---:|:---:|
| Quảng bá cho **iBGP peer** | ✅ **Có** | ❌ **Không** |
| Quảng bá cho **eBGP peer** | ❌ Không | ❌ Không |
| Mức độ chặn | Vừa | ⭐ **Chặn hoàn toàn** |

#### Community tự định nghĩa — định dạng `AS:NN`

```
ip bgp-community new-format                    ! hiện dạng 65001:100 thay vì số nguyên

route-map RM-SET-COMM permit 10
 set community 65001:100 65001:200             ! đặt 2 community
route-map RM-SET-COMM permit 20
 set community 65001:300 additive              ! THÊM vào (không ghi đè)
```

⚠️ **Không có `additive`** → ⭐ **ghi đè** toàn bộ community cũ.

#### 🔴 `send-community` — bước hay bị quên

> ⭐ **Cisco KHÔNG gửi community mặc định.** Phải bật:
```
router bgp 65001
 neighbor 10.0.12.2 send-community              ! standard
 neighbor 10.0.12.2 send-community both         ! standard + extended
```
⚠️ Thiếu lệnh này → bạn `set community` nhưng peer **không nhận được gì**.

#### Match community bằng community-list

```
! Standard community-list: 1–99
ip community-list standard CL-NO-EXPORT permit no-export
ip community-list standard CL-CUSTOMER permit 65001:100
!
! Expanded (regex): 100–500
ip community-list expanded CL-ANY-65001 permit 65001:.*
!
route-map RM-MATCH-COMM permit 10
 match community CL-CUSTOMER
 set local-preference 200
route-map RM-MATCH-COMM permit 20               ! catch-all
```

**Kiểm tra:**
```
show ip bgp community                           ! route có community
show ip bgp community no-export
show ip bgp community 65001:100
show ip bgp <prefix>                            ! dòng "Community: ..."
show ip community-list
show ip bgp neighbors <ip> | include community
```

---

### 3.8 ⭐ Filtering — 4 cách

| # | Cách | Lọc theo | Lệnh áp |
|:---:|---|---|---|
| **1** | ⭐ **Prefix-list** | ⭐ **Prefix + độ dài mask** | `neighbor x prefix-list <NAME> in\|out` |
| **2** | ⭐ **AS-path ACL (filter-list)** | ⭐ **AS-path (regex)** | `neighbor x filter-list <N> in\|out` |
| **3** | ⭐ **Route-map** | ⭐ **Mọi thứ + SỬA attribute** | `neighbor x route-map <NAME> in\|out` |
| **4** | Distribute-list | ACL / prefix-list (legacy) | `neighbor x distribute-list <N> in\|out` |

> ⭐ **Nguyên tắc chọn:** chỉ **lọc** theo prefix → **prefix-list**.
> Lọc theo AS-path → **filter-list**. Cần **sửa attribute** → **route-map**.

#### Prefix-list — chuẩn nhất cho lọc theo prefix

```
ip prefix-list PL-CUSTOMER-IN seq 5  permit 10.3.0.0/16 le 24    ! /16 đến /24 trong 10.3.0.0/16
ip prefix-list PL-CUSTOMER-IN seq 10 deny   0.0.0.0/0 le 32      ! deny phần còn lại
!
router bgp 65001
 neighbor 10.0.12.2 prefix-list PL-CUSTOMER-IN in
```

| Cú pháp | Nghĩa |
|---|---|
| `permit 10.0.0.0/8` | ⭐ **Chính xác** `10.0.0.0/8` |
| `permit 10.0.0.0/8 le 24` | ⭐ Trong `10.0.0.0/8`, mask từ **/8 đến /24** |
| `permit 10.0.0.0/8 ge 24` | Trong `10.0.0.0/8`, mask từ **/24 đến /32** |
| `permit 10.0.0.0/8 ge 16 le 24` | Mask từ **/16 đến /24** |
| ⭐ `permit 0.0.0.0/0` | ⭐ **CHỈ default route** (`0.0.0.0/0`), không phải "mọi thứ"! |
| ⭐ `permit 0.0.0.0/0 le 32` | ⭐ **MỌI prefix** — đây là **catch-all** |

🔴 **Bẫy kinh điển:** `permit 0.0.0.0/0` **KHÔNG** phải "cho phép mọi thứ" —
nó chỉ cho phép **đúng default route**. Catch-all phải là ⭐ **`permit 0.0.0.0/0 le 32`**.

⚠️ Prefix-list có ⭐ **implicit deny** ở cuối (giống route-map, Module-03 §2.7).

#### AS-path ACL — lọc theo AS-path bằng regex

```
ip as-path access-list 1 permit ^65002$              ! chỉ route sinh tại AS 65002 kề
ip as-path access-list 2 permit ^$                   ! chỉ route sinh trong AS mình
ip as-path access-list 3 deny _65099_                ! chặn route đi qua AS 65099
ip as-path access-list 3 permit .*                   ! catch-all
!
router bgp 65001
 neighbor 10.0.12.2 filter-list 1 in
```

⭐ **BẢNG REGEX AS-PATH — đề hỏi trực tiếp:**

| Regex | Nghĩa | Ví dụ khớp |
|---|---|---|
| ⭐ **`^$`** | ⭐ **AS-path RỖNG** = route sinh **trong AS của mình** | *(trống)* |
| ⭐ **`^65002$`** | ⭐ **Chỉ** AS 65002 = route sinh tại AS kề 65002 | `65002` |
| ⭐ **`^65002_`** | ⭐ **Bắt đầu** bằng 65002 = route **từ AS kề** 65002 | `65002`, `65002 65010` |
| ⭐ **`_65003_`** | ⭐ **Đi qua** AS 65003 (bất kỳ vị trí) | `65002 65003`, `65003 65010` |
| ⭐ **`_65003$`** | ⭐ **Kết thúc** bằng 65003 = route **sinh tại** AS 65003 | `65002 65003` |
| ⭐ **`.*`** | ⭐ **MỌI THỨ** — catch-all | tất cả |
| `^65002_65003$` | Đúng 2 AS theo thứ tự | `65002 65003` |
| `^[0-9]+$` | Đúng 1 AS (AS kề trực tiếp) | `65002` |

⭐ **Ý nghĩa ký tự:**

| Ký tự | Nghĩa |
|:---:|---|
| `^` | Bắt đầu chuỗi |
| `$` | Kết thúc chuỗi |
| ⭐ **`_`** | ⭐ **Dấu phân cách**: khoảng trắng, dấu phẩy, đầu chuỗi, cuối chuỗi |
| `.` | Một ký tự bất kỳ |
| `*` | 0 hoặc nhiều lần |
| `+` | 1 hoặc nhiều lần |
| `?` | 0 hoặc 1 lần |
| `[ ]` | Tập ký tự |
| `\|` | Hoặc |

**Test regex trực tiếp:**
```
show ip bgp regexp ^$                   ! route sinh trong AS mình
show ip bgp regexp ^65002$
show ip bgp regexp _65003_
show ip bgp regexp ^65002_
```

#### Route-map — lọc + sửa attribute

```
ip prefix-list PL-DENY permit 10.3.4.0/24
!
route-map RM-IN deny 5
 match ip address prefix-list PL-DENY             ! chặn prefix này
route-map RM-IN permit 10
 match as-path 1
 set local-preference 200                        ! route từ AS 65002 → LocPref 200
route-map RM-IN permit 20                         ! CATCH-ALL — đừng quên!
!
router bgp 65001
 neighbor 10.0.12.2 route-map RM-IN in
```

🔴 **Thiếu catch-all (`permit 20` không có `match`)** → ⭐ **implicit deny** → **chặn hết** route
không khớp 2 dòng trên.

#### ⭐ Áp filter xong PHẢI reset

```
clear ip bgp 10.0.12.2 soft in       ! đổi filter chiều IN
clear ip bgp 10.0.12.2 soft out      ! đổi filter chiều OUT
```
⚠️ Không reset → filter mới **không được áp** cho route đã nhận/gửi trước đó.

---

### 3.9 ⭐ `aggregate-address` — summarization của BGP

```
! ═══ Cơ bản: quảng bá CẢ aggregate VÀ các prefix con ═══
router bgp 65001
 aggregate-address 10.1.0.0 255.255.0.0

! ═══ summary-only: CHỈ quảng bá aggregate, ĐÈ các prefix con ═══
 aggregate-address 10.1.0.0 255.255.0.0 summary-only

! ═══ as-set: giữ thông tin AS-path của các prefix con ═══
 aggregate-address 10.1.0.0 255.255.0.0 summary-only as-set
```

| Tùy chọn | Hành vi |
|---|---|
| *(không có gì)* | Quảng bá **aggregate + tất cả prefix con** |
| ⭐ **`summary-only`** | ⭐ Chỉ quảng bá **aggregate**, prefix con bị **suppress** (hiện `s` trong `show ip bgp`) |
| ⭐ **`as-set`** | ⭐ Đưa AS-path của prefix con vào **AS_SET** `{65002,65003}` → **giữ chống loop** |
| `attribute-map` | Đặt attribute cho aggregate |
| `suppress-map` | Chọn prefix con nào bị suppress |
| `advertise-map` | Chọn prefix con nào vẫn quảng bá |

⭐ **Điều kiện:** phải có ⭐ **ít nhất 1 prefix con** trong BGP table, nếu không aggregate
**không được sinh ra**.

⭐ **Không có `as-set`:** aggregate có AS-path **rỗng** (chỉ ASN của mình) → ⚠️ **mất chống loop**
→ IOS thêm attribute **`Atomic Aggregate`** để cảnh báo.

**Đọc `show ip bgp` sau khi aggregate:**
```
     Network          Next Hop         Metric LocPrf Weight Path
 *>  10.1.0.0/16      0.0.0.0                     32768 i          ← aggregate
 s>  10.1.1.0/24      0.0.0.0              0      32768 i          ← s = suppressed
 s>  10.1.2.0/24      0.0.0.0              0      32768 i
```
⭐ **`s`** = suppressed (bị `summary-only` đè, **không** quảng bá cho peer).

⭐ IOS tự tạo **discard route Null0** cho aggregate (giống OSPF summarization, Module-04B §2.3):
```
show ip route 10.1.0.0 255.255.0.0
!  B  10.1.0.0/16 [200/0], 00:01:22, Null0
```

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết.

> ### 👉 **[LAB 05B — Tuần 10: Path Selection & Filtering](Module-05B-LAB.md)**

| Bước | Nội dung | Bước nào trong 13 | Cơ chế ở Phần 2 |
|:---:|---|:---:|---|
| 1 | Xác định baseline | — | §3.1 |
| 2 | Router ID (tie-break) | **11** | §3.1 |
| 3 | ⭐⭐ AS-path prepend → **INBOUND** | **4** | §3.5 |
| 4 | ⭐⭐ Local Preference → **OUTBOUND** | **2** | §3.4 |
| 5 | MED | **6** | §3.6 |
| 6 | Origin | **5** | §3.1 |
| 7 | ⭐⭐ Community | — | §3.7 |
| 8 | ⭐⭐ Filtering (4 cách) | — | §3.8 |
| 9 | `aggregate-address` | — | §3.9 |

> ⭐ **Nguyên tắc của lab này: mỗi lần chỉ đổi MỘT thuộc tính.**
>
> Sau mỗi thay đổi, chạy `show ip bgp <prefix>` và **tự trả lời: "bước thứ mấy trong 13 bước
> vừa quyết định kết quả này?"** Trả lời được câu đó ở cả 9 bước thì bạn đã thuộc 13 bước
> mà không cần học vẹt.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> Bạn vừa học cách **điều khiển** đường đi của BGP. Phần này trả lời:
> **doanh nghiệp thật muốn điều khiển cái gì, và làm bằng cách nào?**

### 4.1 Bản đồ: bốn bài toán điều khiển traffic

```
                AS 64500 (ISP-A)          AS 64600 (ISP-B)
                 1 Gbps, đắt               200 Mbps, rẻ
                      │                          │
          ┌───────────┴──────┐        ┌──────────┴───────────┐
          │    Edge-1        │◄─iBGP─►│      Edge-2          │
          │                  │        │                      │
          │ ① OUTBOUND:      │        │  ③ INBOUND:          │
          │   LOCAL-PREF cao │        │    AS-PATH PREPEND    │
          │   → traffic RA   │        │    → traffic VÀO      │
          │     đi lối này   │        │      tránh lối này    │
          │                  │        │                      │
          │ ② Lọc chiều RA:  │        │  ④ Lọc chiều VÀO:     │
          │   chỉ quảng bá   │        │    chỉ nhận default   │
          │   prefix CỦA MÌNH│        │    (đừng nhận 900k    │
          │                  │        │     route Internet)   │
          └──────────────────┘        └───────────────────────┘
                      │                          │
                      └──────────┬───────────────┘
                                 │
                         MẠNG NỘI BỘ (IGP)
```

### 4.2 Bảng quyết định — muốn gì thì dùng gì

| Bạn muốn | Dùng | Đặt ở đâu | Vì sao |
|---|---|---|---|
| ⭐ **Traffic ĐI RA theo lối tôi chọn** | ⭐ **Local Preference** (bước 2) | **inbound** trên router của mình | LocPref lan **trong AS** → mọi router nội bộ cùng chọn một lối ra |
| Chỉ một router đi lối này | **Weight** (bước 1) | inbound, local | ⭐ Weight **chỉ có ý nghĩa cục bộ**, không quảng bá |
| ⭐ **Traffic ĐI VÀO tránh một lối** | ⭐ **AS-path prepend** (bước 4) | **outbound** ra ISP | Làm đường đó *"trông xa hơn"* với người ngoài |
| Điều chỉnh vào giữa 2 link **cùng một ISP** | **MED** (bước 6) | outbound ra ISP | ⭐ MED **chỉ so sánh trong cùng AS** |
| Gắn nhãn cho ISP xử lý hộ | **Community** | outbound | `no-export`, hoặc community riêng ISP quy định |
| Bớt số route nhận vào | **Filtering** (prefix-list/route-map) | inbound | Nhận full Internet = **~900.000 route** — router nhỏ chết |
| Gọn bảng route quảng bá ra | **`aggregate-address`** | trên router mình | Gộp nhiều prefix thành một |

> 🔴 ⭐⭐ **Quy tắc vàng, nhớ một câu:**
> ⭐ **Muốn đổi chiều RA → LOCAL-PREF (mình tự quyết được).**
> ⭐ **Muốn đổi chiều VÀO → AS-PATH PREPEND (chỉ là GỢI Ý — người ta có nghe hay không là quyền họ).**

### 4.3 Ba sự thật mà chỉ người đi làm mới biết

| Sự thật | Giải thích |
|---|---|
| ⭐⭐ **Inbound bạn KHÔNG điều khiển được, chỉ gợi ý** | Traffic vào do **người ngoài quyết**. Prepend làm đường trông xa hơn, nhưng nếu ISP kia có chính sách riêng (LocPref của họ) thì họ vẫn đi lối đó. ⭐ **Đây là điều gây thất vọng nhất khi mới làm BGP** |
| ⭐⭐ **Đừng nhận full BGP table nếu không cần** | Internet có **~900.000 prefix**. Router nhỏ hết RAM/TCAM và **chết**. Hầu hết doanh nghiệp chỉ cần **default route + vài prefix**. Nhận full chỉ khi bạn thật sự cần chọn đường theo từng prefix |
| ⭐ **Lọc chiều RA quan trọng không kém chiều VÀO** | Quên lọc outbound → bạn quảng bá route học từ ISP-A sang ISP-B → ⭐ **bạn thành đường trung chuyển miễn phí cho traffic của thiên hạ**, băng thông của bạn bị dùng hết |

### 4.4 Những thứ này sẽ lớn lên thành gì

| Bạn vừa học | Sẽ thành | Ở module |
|---|---|---|
| Điều khiển traffic theo chính sách | **SD-WAN**: chọn đường theo **ứng dụng**, đo bằng BFD | **Module-09 §6** |
| Filtering bằng prefix-list/route-map | ACL nâng cao · uRPF · lọc route trong VRF | **Module-10 · Module-08** |
| Dual-ISP, đổi hướng traffic | **NAT dual-ISP** + IP SLA failover | **Module-06B** |
| `aggregate-address` | Summarization trong OSPF/EIGRP *(đã học M04B)* | — |
| Community làm nhãn chính sách | **SGT** — nhãn chính sách theo danh tính | **Module-10 §8** |

### 4.5 Vẽ lại để nhớ

> **Bài tập 15 phút, trên giấy.**
>
> 1. Vẽ lại sơ đồ §4.1 **không nhìn tài liệu**
> 2. Với mỗi bài toán ① → ④, ghi rõ **dùng thuộc tính gì, đặt inbound hay outbound**
> 3. Trả lời: *"Sếp bảo 'traffic từ Internet vào phải đi qua ISP-B'. Bạn làm được không, và hứa được tới đâu?"*

<details>
<summary>Đáp án câu 3</summary>

⭐ **Làm được ở mức GỢI Ý, không đảm bảo.**

**Cách làm:** AS-path prepend ra ISP-A (làm đường qua ISP-A trông xa hơn), hoặc gắn community
mà ISP-A quy định để họ hạ Local Preference.

**Nhưng phải nói rõ với sếp:** ⭐ **traffic đi VÀO do các AS bên ngoài quyết định, không phải mình.**
Nếu một ISP nào đó ở xa có Local Preference ưu tiên đường qua ISP-A, thì **LocPref của họ được
xét ở bước 2, trước AS-path ở bước 4** → họ vẫn đi lối đó, prepend bao nhiêu cũng vô ích.

⭐ **Đây là bài học lớn nhất của Module-05B:** *outbound bạn quyết, inbound bạn chỉ xin.*

</details>

---

## 💡 4.6 Thực chiến đi làm

| Chủ đề | Thi dạy | Thực tế đi làm |
|---|---|---|
| ⭐ **13 bước** | Học thuộc | ⭐ Thực tế **99% quyết định ở bước 1–4**. Nhưng phải biết cả 13 để giải thích được "vì sao chọn path này" khi output lạ |
| ⭐ **Dual-ISP thực tế** | Không dạy | ⭐ Công thức chuẩn: **outbound** → Local Preference (200 cho ISP chính, 100 cho backup) · **inbound** → AS-path prepend về ISP backup (2–3 lần) |
| ⭐ **Weight vs LocPref** | Cả hai | ⭐ AS có **1 router biên** → Weight đủ. AS có **nhiều router biên** → **phải dùng Local Preference** (Weight không lan qua iBGP) |
| ⭐ **MED** | Bước 6 | ⚠️ **Gần như vô dụng với 2 ISP khác nhau** (không so MED giữa 2 AS). Chỉ hữu ích khi có **2 link tới CÙNG một ISP** |
| ⭐ **`bgp deterministic-med`** | Không dạy | ⭐ **Nên bật ở production.** Không có nó → kết quả path selection **phụ thuộc thứ tự học route** → reboot router có thể chọn path khác |
| ⚠️ **`bgp always-compare-med`** | Có lệnh | ⚠️ Cẩn thận — so MED giữa các AS khác nhau là **so táo với cam** (mỗi AS có thang MED riêng). Có thể gây bất ổn |
| 🔴 **`send-community`** | Ít nhắc | 🔴 **Lỗi số 1 khi làm community.** `set community` mà không `send-community` = **không có tác dụng**, và **không có log lỗi**. Bật `send-community both` cho chắc |
| ⭐ **Community với ISP** | Khái niệm | ⭐ ISP thật cung cấp bảng community cho khách: VD `AS:80` = LocPref 80 (deprioritize), `AS:120` = LocPref 120. ⭐ **Đây là cách tốt nhất điều khiển inbound** — tốt hơn prepend |
| ⭐ **`no-export`** | Khái niệm | ⭐ Dùng khi ISP cấp prefix cho bạn dùng nội bộ. Cũng dùng để giữ route "chỉ trong AS mình" khi có nhiều peer |
| 🔴 **Catch-all** | Bẫy đề | 🔴 **Ba loại catch-all khác nhau, thuộc lòng:** prefix-list = ⭐ **`permit 0.0.0.0/0 le 32`** · AS-path ACL = ⭐ **`permit .*`** · route-map = ⭐ **`permit <seq>` không có match**. Thiếu = **mất hết route** = sự cố |
| ⭐ **`permit 0.0.0.0/0`** | Bẫy đề | 🔴 Chỉ khớp **đúng default route**. Rất nhiều người tưởng là catch-all → gây sự cố |
| ⭐ **Filter inbound với ISP** | Không dạy | ⭐ **BẮT BUỘC**: `maximum-prefix` (05A) + prefix-list inbound chặn **bogon** (`0.0.0.0/8`, `10.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `172.16.0.0/12`, `192.168.0.0/16`, `224.0.0.0/4`) và chặn prefix quá nhỏ (`ge 25`) |
| ⭐ **Filter outbound** | Không dạy | 🔴 **BẮT BUỘC**: chỉ quảng bá **prefix của chính bạn**. Thiếu filter outbound = ⭐ **route leak** — bạn quảng bá full Internet table cho ISP → sự cố diện rộng, có tiền lệ nhiều lần |
| ⭐ `show ip bgp regexp ^$` | Ít nhắc | ⭐ **Lệnh vàng để verify outbound filter**: nó liệt kê đúng những prefix sinh trong AS mình — đúng bằng những gì bạn **nên** quảng bá |
| ⭐ **`aggregate-address as-set`** | Tùy chọn | ⚠️ Thiếu `as-set` khi gộp route học từ AS khác = ⭐ **mất chống loop**. Đây là một nguyên nhân của route leak thật. **Luôn dùng `as-set`** khi gộp route không phải của mình |
| ⭐ **`summary-only`** | Tùy chọn | ⭐ Gần như **luôn dùng** — không có nó thì aggregate không giảm được route nào |
| ⭐ **Reset sau khi đổi policy** | Ít nhắc | ⭐ `soft in` (đổi inbound) / `soft out` (đổi outbound). ⚠️ Quên reset = policy mới **không áp** cho route cũ → tưởng cấu hình sai |
| ⭐ **`hit count` / counter** | Không dạy | ⭐ `show ip prefix-list detail <NAME>` và `show route-map <NAME>` có **counter**. Counter = 0 → filter **không được gọi** hoặc **không khớp** → đây là cách verify nhanh nhất |
| ⭐ **Tài liệu hóa policy** | Không có | ⭐ Mỗi route-map/prefix-list phải có comment: `! RM-ISP1-IN: uu tien ISP1 cho outbound, ticket #1234, ngay 2026-09-09`. Không có = 6 tháng sau không ai dám sửa |
| ⭐ **RPKI / ROA** | Không có trong ENCOR | ⭐ Xu hướng hiện tại: xác thực nguồn gốc prefix bằng chữ ký số. `show ip bgp rpki` trên IOS-XE mới. Biết để không lạc hậu |

---

# 📎 PHỤ LỤC — TRA CỨU

> 🔴 **KHÔNG đọc phần này ở lần học đầu tiên.**
>
> | Khi nào | Mở mục nào |
> |---|---|
> | Đang lab mà lỗi | **Gỡ lỗi nhanh** (§7) — ⭐ có quy trình *"vì sao BGP chọn path này"* theo 13 bước |
> | Quên lệnh | **Hộp lệnh** (§7.1) |
> | Tuần 20, ôn thi | **Bẫy đề** (§6) + **Quiz** (§8) |
> | Gặp từ lạ | **Thuật ngữ** (§9) |
> | Tự chấm | **Đúc kết + Milestone Tuần 11** (§10) |

---

## 🎓 6. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | Sự thật |
|:---:|---|---|
| 1 | ⭐ **Thứ tự 13 bước** | ⭐ **W**eight → **L**ocal Pref → **O**riginate → **AS**-path → **O**rigin → **M**ED → e**BGP**>iBGP → IGP metric → oldest → **R**outer ID → cluster → neighbor IP |
| 2 | ⭐ Bước nào **CAO** thắng | ⭐ **CHỈ Weight (1) và Local Preference (2)**. Từ bước 4 trở đi đều **THẤP thắng** |
| 3 | ⭐ Weight vs Local Pref — cái nào thắng | ⭐ **Weight** (bước 1 > bước 2) — dù LocPref cao hơn |
| 4 | ⭐ Weight lan tới đâu | ⭐ **CHỈ local router** — **không** gửi cho peer nào (kể cả iBGP) |
| 5 | ⭐ Local Pref lan tới đâu | ⭐ **Trong AS** (qua iBGP), **KHÔNG** qua eBGP. Mặc định **100** |
| 6 | ⭐ **Điều khiển OUTBOUND** dùng gì, chiều nào | ⭐ **Weight / Local Pref**, áp route-map chiều ⭐ **`in`** |
| 7 | ⭐ **Điều khiển INBOUND** dùng gì, chiều nào | ⭐ **AS-path prepend / MED**, áp route-map chiều ⭐ **`out`** |
| 8 | ⭐ Inbound có đảm bảo không | ❌ **Chỉ là GỢI Ý** — AS bên kia ghi đè được bằng Weight/LocPref (bước 1–2 > bước 4/6) |
| 9 | ⭐ MED mặc định so sánh thế nào | ⭐ **CHỈ giữa path từ CÙNG một AS kề**. Muốn so mọi AS → `bgp always-compare-med` |
| 10 | ⭐ MED **không được đặt** = bao nhiêu | ⭐ **0** (tốt nhất!). Muốn coi là tệ nhất → `bgp bestpath med missing-as-worst` |
| 11 | `bgp deterministic-med` làm gì | ⭐ Nhóm path theo AS **trước** khi so → kết quả **nhất quán**, không phụ thuộc thứ tự học route |
| 12 | ⭐ 3 Origin code + thứ tự | ⭐ **`i` (IGP/`network`) < `e` (EGP) < `?` (incomplete/`redistribute`)** |
| 13 | ⭐ Nên dùng `network` hay `redistribute` | ⭐ **`network`** — origin `i` **tốt hơn** `?` ở bước 5 |
| 14 | Bước 8 "IGP metric tới next-hop" nghĩa là gì | ⭐ **Hot potato routing** — chọn đường **ra khỏi AS sớm nhất** |
| 15 | Bước 10 "oldest eBGP path" | ⭐ Ưu tiên **ổn định** hơn tối ưu — path tồn tại lâu hơn thắng |
| 16 | Bước 11 Router ID của ai | ⭐ Của **neighbor quảng bá route**, **THẤP** thắng |
| 17 | ⭐ 4 well-known community | ⭐ **`no-export`** · **`no-advertise`** · **`local-AS`** · `internet` |
| 18 | ⭐ `no-export` vs `no-advertise` | ⭐ `no-export` = **không cho eBGP peer** (iBGP **vẫn được**) · `no-advertise` = ⭐ **không cho BẤT KỲ peer nào** |
| 19 | 🔴 `set community` không có tác dụng | ⭐ Thiếu **`neighbor x send-community`** — Cisco **không gửi community mặc định** |
| 20 | ⭐ `set community` không có `additive` | ⭐ **GHI ĐÈ** toàn bộ community cũ |
| 21 | Community-list standard vs expanded | Standard **1–99** (khớp giá trị) · Expanded **100–500** (regex) |
| 22 | 🔴 ⭐ Catch-all của **prefix-list** | ⭐ **`permit 0.0.0.0/0 le 32`** — ⚠️ **`permit 0.0.0.0/0` CHỈ khớp default route!** |
| 23 | 🔴 Catch-all của **AS-path ACL** | ⭐ **`permit .*`** |
| 24 | 🔴 Catch-all của **route-map** | ⭐ Statement `permit` **không có `match`** |
| 25 | ⭐ Regex `^$` | ⭐ AS-path **rỗng** = route sinh **trong AS mình** |
| 26 | ⭐ Regex `^65002$` | ⭐ **Chỉ** AS 65002 = route sinh tại AS kề đó |
| 27 | ⭐ Regex `^65002_` | ⭐ Route **từ AS kề** 65002 (bắt đầu bằng) |
| 28 | ⭐ Regex `_65003_` | ⭐ Route **đi qua** AS 65003 |
| 29 | ⭐ Regex `_65003$` | ⭐ Route **sinh tại** AS 65003 (kết thúc bằng) |
| 30 | ⭐ Ký tự `_` trong regex nghĩa gì | ⭐ **Dấu phân cách**: space, dấu phẩy, đầu chuỗi, cuối chuỗi |
| 31 | ⭐ `aggregate-address` không có option | ⭐ Quảng bá **CẢ** aggregate **VÀ** prefix con (không giảm route) |
| 32 | ⭐ `summary-only` làm gì | ⭐ **Suppress** prefix con → hiện ⭐ **`s`** trong `show ip bgp` |
| 33 | ⭐ `as-set` làm gì, vì sao cần | ⭐ Đưa AS-path của prefix con vào **AS_SET** `{65002,65003}` → ⭐ **giữ chống loop**. Thiếu = route có thể quay lại AS gốc |
| 34 | `atomic-aggregate` nghĩa là gì | ⭐ Cảnh báo route **đã bị gộp**, **mất chi tiết AS-path** |
| 35 | ⭐ Điều kiện để aggregate được sinh | ⭐ Phải có **ít nhất 1 prefix con** trong BGP table |
| 36 | ⭐ `s` trong `show ip bgp` | ⭐ **Suppressed** — bị `summary-only` đè, **không quảng bá** |
| 37 | ⭐ Đổi filter/route-map xong cần làm gì | ⭐ `clear ip bgp <ip> soft in` (inbound) / `soft out` (outbound) |
| 38 | Verify filter có hoạt động | ⭐ `show ip prefix-list detail <NAME>` → **hit count** · `show route-map <NAME>` → counter |

---

## 🐛 7. GỠ LỖI NHANH

### 7.1 Hộp lệnh vạn năng

```
! ═══ PATH SELECTION ═══
show ip bgp <prefix>                          ! MỌI path + LÝ DO best
show ip bgp                                   ! bảng tổng quan (Weight/LocPrf/Metric/Path)
show ip bgp | include <prefix>
show ip route <prefix>                        ! path nào thật sự vào RIB
show ip bgp neighbors <ip> routes             ! route nhận từ peer (sau policy)
show ip bgp neighbors <ip> advertised-routes  ! route GỬI cho peer

! ═══ ATTRIBUTE ═══
show ip bgp <prefix>                          ! Weight, localpref, metric(MED), Community
show ip bgp | include ^.*[0-9]+ +[0-9]+ +[0-9]+   ! xem cột Weight/LocPrf
show run | section router bgp                  ! xem policy đang áp
show ip bgp neighbors <ip> | include route-map|prefix-list|filter-list|weight

! ═══ COMMUNITY ═══
show ip bgp community                          ! route có community
show ip bgp community no-export
show ip bgp community <AS:NN>
show ip community-list
show ip bgp <prefix>                           ! dòng "Community: ..."
show ip bgp neighbors <ip> | include community ! send-community có bật?

! ═══ FILTERING ═══
show ip prefix-list
show ip prefix-list detail <NAME>              ! HIT COUNT
show ip as-path-access-list
show route-map <NAME>                          ! counter từng dòng
show ip bgp regexp ^$                          ! route sinh trong AS mình
show ip bgp regexp _65003_
show ip bgp filter-list <N>                    ! route khớp AS-path ACL
show ip bgp prefix-list <NAME>                 ! route khớp prefix-list

! ═══ AGGREGATE ═══
show ip bgp <aggregate-prefix>                 ! AS_SET? atomic-aggregate?
show ip bgp | include ^ s                      ! prefix bị suppressed
show ip route <aggregate> <mask>               ! discard route Null0?

! ═══ MED ═══
show run | include always-compare-med|deterministic-med|missing-as-worst

! ═══ RESET ═══
clear ip bgp <ip> soft in                      ! sau khi đổi INBOUND policy
clear ip bgp <ip> soft out                     ! sau khi đổi OUTBOUND policy

! ═══ DEBUG (⚠️ chỉ lab) ═══
debug ip bgp updates in
debug ip bgp updates out
debug ip bgp <ip> updates
undebug all
```

### 7.2 Bảng lỗi: triệu chứng → nguyên nhân → cách sửa

| # | Triệu chứng | Nguyên nhân | Lệnh chẩn đoán | Cách sửa |
|:---:|---|---|---|---|
| 1 | ⭐ **BGP chọn path "sai"** | Không hiểu đúng thứ tự 13 bước | ⭐⭐ `show ip bgp <prefix>` → so **từng attribute** theo thứ tự | Đọc theo đúng W-L-O-AS-O-M-P-R |
| 2 | ⭐ Đặt LocPref mà **path không đổi** | ⭐ **Weight** đang thắng (bước 1 > bước 2) | `show ip bgp <prefix>` → xem cột `weight` | Bỏ Weight, hoặc dùng Weight thay LocPref |
| 3 | ⭐ Đổi policy mà **không có tác dụng** | ⭐ **Chưa reset phiên** | — | ⭐ `clear ip bgp <ip> soft in` / `soft out` |
| 4 | Đặt LocPref cho 1 router mà **router khác không thấy** | ⭐ Local Pref lan qua **iBGP**, cần iBGP peering | `show ip bgp <prefix>` trên router kia | Cấu hình iBGP · hoặc dùng Weight trên từng router |
| 5 | ⭐ Đặt Weight mà **router khác không thấy** | ⭐ **Weight CHỈ local** — không bao giờ gửi đi | — | ✅ Đúng thiết kế. Dùng **Local Preference** nếu cần cả AS |
| 6 | AS-path prepend mà peer **vẫn chọn đường cũ** | ⭐ Peer ghi đè bằng **Weight/LocPref** của họ (bước 1–2 > bước 4) | `show ip bgp <prefix>` **trên peer** → xem weight/localpref | ⭐ Dùng **community** (nhờ peer áp policy) · hoặc thương lượng với ISP |
| 7 | ⭐ MED không có tác dụng | ⭐ Path đến từ **2 AS khác nhau** → mặc định **không so MED** | `show ip bgp <prefix>` → xem AS-path đầu tiên | ⭐ Peer bật `bgp always-compare-med` · hoặc dùng **AS-path prepend** thay |
| 8 | ⭐ Path **không có MED** lại thắng path có MED | ⭐ MED thiếu = **0** = tốt nhất | `show ip bgp <prefix>` → cột Metric trống | `bgp bestpath med missing-as-worst` |
| 9 | Path selection **đổi sau khi reboot** | ⭐ Thiếu **`bgp deterministic-med`** — kết quả phụ thuộc thứ tự học route | `show run \| inc deterministic` | ⭐ `bgp deterministic-med` trên mọi router |
| 10 | 🔴 `set community` **không có tác dụng** | 🔴 ⭐ Thiếu **`neighbor x send-community`** | ⭐ `show ip bgp <prefix>` **trên peer** → không có dòng `Community` | ⭐ `neighbor x send-community both` + `soft out` |
| 11 | Community cũ **bị mất** sau khi set community mới | ⭐ Thiếu từ khóa **`additive`** | `show run \| sec route-map` | `set community <new> additive` |
| 12 | 🔴 Sau khi áp prefix-list, **mất HẾT route** | 🔴 ⭐ Dùng `permit 0.0.0.0/0` (chỉ default route) thay vì **`permit 0.0.0.0/0 le 32`** | ⭐ `show ip prefix-list detail <NAME>` → xem hit count dòng deny | ⭐ Thêm `le 32` |
| 13 | 🔴 Sau khi áp AS-path ACL, mất hết route | 🔴 Thiếu catch-all **`permit .*`** | `show ip as-path-access-list` | Thêm `permit .*` ở cuối |
| 14 | 🔴 Sau khi áp route-map, mất hết route | 🔴 Thiếu catch-all `permit <seq>` không có `match` | ⭐ `show route-map <NAME>` → xem có dòng nào không có Match | Thêm statement catch-all |
| 15 | ⭐ Filter "không hoạt động" | Chưa được gọi, hoặc match không khớp | ⭐ `show ip prefix-list detail` (hit count) · `show route-map` (counter) — **counter = 0** | Kiểm tra tên · kiểm tra đã áp `neighbor x ... in/out` · `soft` reset |
| 16 | ⭐ `aggregate-address` **không xuất hiện** | ⭐ Không có prefix con nào trong BGP table | `show ip bgp \| inc <component>` | Thêm `network` cho prefix con · hoặc `ip route ... Null0` |
| 17 | Aggregate có mà prefix con **vẫn được quảng bá** | Thiếu **`summary-only`** | `show ip bgp \| inc ^ s` (không có `s` nào) | Thêm `summary-only` |
| 18 | ⭐ Route quay lại AS gốc sau khi aggregate | ⭐ Thiếu **`as-set`** → AS-path mất chi tiết → mất chống loop | ⭐ `show ip bgp <agg>` → thấy `atomic-aggregate`, AS-path chỉ có ASN mình | ⭐ Thêm **`as-set`** |
| 19 | 🔴 Quảng bá quá nhiều prefix cho ISP (route leak) | 🔴 Thiếu **filter outbound** | ⭐ `show ip bgp neighbors <ISP> advertised-routes \| count` · so với `show ip bgp regexp ^$` | ⭐ prefix-list outbound chỉ cho prefix của mình |
| 20 | Nhận prefix bogon / prefix quá nhỏ từ ISP | Thiếu filter inbound | `show ip bgp \| inc 10\.\|192.168\|127\.` | prefix-list inbound chặn bogon + `ge 25` |

### 7.3 ⭐⭐ Quy trình "vì sao BGP chọn path này" — 13 bước có hệ thống

```
show ip bgp <prefix>
   ↓ Đọc TỪNG path, so theo ĐÚNG thứ tự — bước nào khác nhau thì DỪNG

BƯỚC 0: Có dấu `*` (valid) không?
   └─ KHÔNG → next-hop unreachable → show ip route <next-hop> → HẾT
        ↓ (mọi path đều valid)
BƯỚC 1: cột `weight` — có path nào CAO hơn?
   └─ CÓ → path đó thắng → HẾT
        ↓ (bằng nhau)
BƯỚC 2: `localpref` — có path nào CAO hơn?
   └─ CÓ → path đó thắng → HẾT
        ↓
BƯỚC 3: có path nào là `local`/`sourced` (next-hop 0.0.0.0)?
   └─ CÓ → path đó thắng → HẾT
        ↓
BƯỚC 4: đếm số AS trong AS-path — có path nào NGẮN hơn?
   └─ CÓ → path đó thắng → HẾT     ← 99% dừng ở đây trên Internet
        ↓
BƯỚC 5: `Origin` — i < e < ?
   └─ Khác nhau → path có origin THẤP hơn thắng → HẾT
        ↓
BƯỚC 6: `metric` (= MED) — THẤP hơn thắng
   ⚠️ CHỈ so nếu 2 path từ CÙNG AS kề (trừ khi always-compare-med)
   └─ Khác nhau → path MED thấp thắng → HẾT
        ↓
BƯỚC 7: `external` (eBGP) vs `internal` (iBGP)
   └─ eBGP thắng → HẾT
        ↓
BƯỚC 8: IGP metric tới next-hop — THẤP hơn thắng (hot potato)
        ↓
BƯỚC 10: path nào tồn tại LÂU hơn (oldest) → thắng
        ↓
BƯỚC 11: Router ID trong ngoặc `(x.x.x.x)` — THẤP hơn thắng
        ↓
BƯỚC 13: `from <IP>` — neighbor IP THẤP hơn thắng
```

> ⭐ **Cách dùng thực tế:** copy output `show ip bgp <prefix>` ra notepad, kẻ bảng 13 dòng,
> điền giá trị từng path vào từng bước. Bước đầu tiên có giá trị **khác nhau** chính là **lý do**.
> Làm 3 lần là bạn nhớ thứ tự mà không cần bảng.

---

## 📝 8. QUIZ TỰ KIỂM TRA

**Câu 1.** Kể 13 bước path selection theo thứ tự. Nêu mnemonic. Bước nào "CAO thắng"?

<details><summary>Xem đáp án</summary>

⭐ **Mnemonic: "We Love Oranges AS Oranges Mean Pure Refreshment"**

| # | Bước | So sánh |
|:---:|---|---|
| 0 | Next-hop reachable | Bắt buộc — không thì loại |
| **1** | ⭐ **W**eight | ⭐ **CAO** thắng |
| **2** | ⭐ **L**ocal Preference | ⭐ **CAO** thắng |
| **3** | **O**riginated locally | Route của chính router |
| **4** | ⭐ **AS**-path | ⭐ **NGẮN** (thấp) thắng |
| **5** | ⭐ **O**rigin | ⭐ **THẤP** thắng (`i` < `e` < `?`) |
| **6** | ⭐ **M**ED | ⭐ **THẤP** thắng |
| **7** | **P**aths — eBGP > iBGP | eBGP thắng |
| **8** | IGP metric tới next-hop | **THẤP** thắng (hot potato) |
| 9 | *(multipath nếu bật `maximum-paths`)* | — |
| **10** | Oldest eBGP path | Cũ hơn thắng (ổn định) |
| **11** | ⭐ **R**outer ID của neighbor | ⭐ **THẤP** thắng |
| 12 | Cluster-list length | Ngắn thắng (chỉ có RR) |
| **13** | Neighbor IP | ⭐ **THẤP** thắng |

⭐⭐ **CHỈ 2 bước đầu (Weight, Local Preference) là "CAO thắng".**
Từ bước 4 trở đi **tất cả đều "THẤP thắng"**.

⭐ **Quy tắc:** bước nào phân định được thì **DỪNG NGAY**, không xét bước sau.
</details>

---

**Câu 2.** ⭐ Bạn muốn traffic **RA KHỎI** AS của mình đi qua ISP1. Dùng attribute nào,
áp route-map chiều nào? Còn muốn traffic **VÀO** AS mình qua ISP1 thì sao?

<details><summary>Xem đáp án</summary>

| Muốn | Attribute | Chiều | Ai quyết định |
|---|---|:---:|---|
| ⭐ **OUTBOUND** (ra khỏi AS) | ⭐ **Local Preference** (cả AS) hoặc **Weight** (1 router) | ⭐ **`in`** | ⭐ **TÔI** — chắc chắn |
| ⭐ **INBOUND** (vào AS) | ⭐ **AS-path prepend** hoặc **MED** | ⭐ **`out`** | ⚠️ **AS bên kia** — chỉ gợi ý |

**Cấu hình OUTBOUND (ưu tiên ISP1):**
```
route-map RM-ISP1-PRIMARY permit 10
 set local-preference 200
!
router bgp 65001
 neighbor <ISP1-IP> route-map RM-ISP1-PRIMARY in     ! chiều IN
! (ISP2 giữ mặc định LocPref 100)
```

**Cấu hình INBOUND (khách vào qua ISP1):** làm ISP2 "kém hơn"
```
route-map RM-PREPEND-ISP2 permit 10
 set as-path prepend 65001 65001 65001
!
router bgp 65001
 neighbor <ISP2-IP> route-map RM-PREPEND-ISP2 out    ! chiều OUT
```

🧠 **Câu thần chú:** ⭐ ***"Nhận route VÀO → quyết định đi RA. Gửi route RA → gợi ý người ta đi VÀO."***

⚠️ **Vì sao inbound chỉ là gợi ý:** AS bên kia ghi đè được bằng **Weight (bước 1)** hoặc
**Local Preference (bước 2)** — cả hai **đứng TRƯỚC** AS-path (bước 4) và MED (bước 6).
</details>

---

**Câu 3.** R1 có 2 path tới `10.3.3.0/24`: path A (LocPref 200, AS-path 2 hop),
path B (Weight 500, LocPref 100, AS-path 4 hop). Path nào thắng? Vì sao?

<details><summary>Xem đáp án</summary>

⭐ **Path B thắng** (Weight 500).

**Vì sao:** **Weight là BƯỚC 1**, Local Preference là **BƯỚC 2**.
BGP xét Weight **trước** → path B có Weight 500 > path A có Weight 0 → ⭐ **DỪNG NGAY**,
**không xét** LocPref (bước 2) hay AS-path (bước 4).

```
show ip bgp 10.3.3.0
!   65004 65003 65003 65003
!     10.0.14.2 ... weight 500, valid, external, best      ← thắng ở bước 1
!   65002 65003
!     10.0.12.2 ... localpref 200, valid, external          ← LocPref cao hơn nhưng vô ích
```

⭐ **Bài học:** Weight là **"quyền phủ quyết"** của router local — nó thắng mọi thứ khác.

⚠️ **Hệ quả thực tế nguy hiểm:** ai đó đặt `neighbor x weight` để "sửa tạm" một vấn đề,
rồi quên → sau này bạn đặt Local Preference mà **không có tác dụng**, mất hàng giờ debug.
⭐ Khi gặp "đặt LocPref mà path không đổi" → ⭐ **kiểm tra Weight trước**:
```
show ip bgp <prefix>            ! xem cột weight
show run | include weight
```
</details>

---

**Câu 4.** Weight và Local Preference: mỗi cái lan tới đâu? Khi nào dùng cái nào?

<details><summary>Xem đáp án</summary>

| | ⭐ **Weight** | ⭐ **Local Preference** |
|---|---|---|
| Bản chất | ⭐ **Cisco-only, KHÔNG phải attribute BGP** | Well-known Discretionary |
| Phạm vi | ⭐ **CHỈ router đó** — **không bao giờ** gửi cho peer (kể cả iBGP) | ⭐ **Cả AS** (lan qua iBGP), **không** qua eBGP |
| Mặc định | 32768 (của mình) / 0 (học được) | **100** |
| Tốt nhất | **CAO** | **CAO** |
| Bước | ⭐ **1** | **2** |

**Khi nào dùng cái nào:**

| Tình huống | Dùng |
|---|---|
| AS chỉ có **1 router biên** | ⭐ Weight (đơn giản, đủ) |
| AS có **nhiều router biên**, muốn **cả AS** đi cùng hướng | ⭐ **Local Preference bắt buộc** — Weight không lan qua iBGP |
| Muốn **chỉ 1 router** đi khác cả AS | Weight |
| Muốn ghi đè mọi thứ (kể cả LocPref của người khác) | Weight |

⚠️ **Lỗi phổ biến:** đặt Weight trên router biên rồi mong các router khác trong AS cũng
đi theo hướng đó → ⭐ **không xảy ra**. Weight không đi đâu cả.
</details>

---

**Câu 5.** Bạn đặt `set metric 500` (MED) khi quảng bá cho ISP2, nhưng traffic inbound
vẫn vào qua ISP2. Nêu 2 nguyên nhân.

<details><summary>Xem đáp án</summary>

**Nguyên nhân 1 — ⭐ MED mặc định CHỈ so giữa path từ CÙNG một AS kề.**

Nếu ISP1 và ISP2 là **2 AS khác nhau** → ISP nhận route từ 2 AS khác nhau
→ ⭐ **MED KHÔNG được so sánh** → hoàn toàn vô tác dụng.

*Sửa:*
- Nhờ ISP bật `bgp always-compare-med` (⚠️ họ thường **không** làm)
- ⭐ **Dùng AS-path prepend thay** (bước 4, luôn được so)
- ⭐ **Dùng community** mà ISP cung cấp (VD `AS:80` = LocPref 80)

⭐ **MED chỉ hữu ích khi có 2 link tới CÙNG một ISP** — lúc đó cùng AS kề nên MED được so.

**Nguyên nhân 2 — ⭐ ISP ghi đè bằng Weight/Local Preference của họ.**

MED là **bước 6**. Weight (**bước 1**) và Local Preference (**bước 2**) đứng **trước** →
nếu ISP đặt LocPref cao cho link ISP2 (VD vì lý do thương mại) thì MED của bạn **không được xét tới**.

*Kiểm tra:* nhờ ISP chạy `show ip bgp <your-prefix>` và xem `weight`/`localpref`.

⭐ **Bài học thực chiến:** điều khiển inbound là **thương lượng**, không phải cấu hình.
Thứ tự hiệu quả: ⭐ **community của ISP > AS-path prepend > MED**.
</details>

---

**Câu 6.** ⭐ Phân biệt `no-export` và `no-advertise`. Và tại sao `set community` của bạn
có thể "không có tác dụng"?

<details><summary>Xem đáp án</summary>

| | ⭐ **`no-export`** | ⭐ **`no-advertise`** |
|---|:---:|:---:|
| Quảng bá cho **eBGP peer** | ❌ **Không** | ❌ **Không** |
| Quảng bá cho **iBGP peer** | ⭐ ✅ **CÓ** | ❌ **Không** |
| Mức chặn | Vừa — "không ra khỏi AS" | ⭐ **Hoàn toàn** — "không nói với ai" |
| Ví von | *"Nội bộ công ty"* | *"Chỉ mắt anh"* |

**Dùng thực tế của `no-export`:** ISP cấp prefix cho bạn dùng nội bộ →
gắn `no-export` → bạn dùng được trong AS mình nhưng **không thể** quảng bá ra Internet.

🔴 **Vì sao `set community` "không có tác dụng":**

⭐ **Cisco KHÔNG gửi community mặc định.** Phải bật:
```
router bgp 65001
 neighbor 10.0.12.2 send-community              ! standard
 neighbor 10.0.12.2 send-community both         ! standard + extended (nên dùng)
```

⚠️ Thiếu lệnh này → bạn `set community` thành công trên router mình,
nhưng peer ⭐ **không nhận được gì**, và ⭐ **không có thông báo lỗi nào**.

**Verify (trên PEER):**
```
show ip bgp <prefix> | include Community
!       Community: no-export              ← ✅ đã nhận
```

**Nguyên nhân thứ 2 — thiếu `additive`:**
```
set community 65001:200                     ! ⚠️ GHI ĐÈ community cũ
set community 65001:200 additive            ! THÊM vào community cũ
```

⭐ **Quy trình chuẩn:** `set community` → `neighbor x send-community both` →
`clear ip bgp x soft out` → verify **trên peer**.
</details>

---

**Câu 7.** 🔴 Bạn áp prefix-list này inbound và **mất hết route**. Vì sao? Sửa thế nào?
```
ip prefix-list PL-IN seq 5  deny 10.99.0.0/16
ip prefix-list PL-IN seq 10 permit 0.0.0.0/0
```

<details><summary>Xem đáp án</summary>

🔴 ⭐ **`permit 0.0.0.0/0` CHỈ khớp ĐÚNG default route `0.0.0.0/0`** — không phải "cho phép mọi thứ"!

Nên:
- `10.99.0.0/16` → khớp `deny 10.99.0.0/16` → bị chặn (đúng ý)
- ⭐ **Mọi prefix khác** (VD `10.3.3.0/24`) → **không khớp dòng nào** →
  ⭐ **implicit deny** ở cuối prefix-list → **bị chặn hết**

**Sửa — thêm `le 32`:**
```
ip prefix-list PL-IN seq 5  deny   10.99.0.0/16
ip prefix-list PL-IN seq 10 permit 0.0.0.0/0 le 32       ! CATCH-ALL ĐÚNG
```
`permit 0.0.0.0/0 le 32` = "cho phép mọi prefix có mask từ **/0 đến /32**".

**Rồi reset:**
```
clear ip bgp <ip> soft in
```

**Verify:**
```
show ip prefix-list detail PL-IN
!    seq 5 deny 10.99.0.0/16 (hit count: 1, refcount: 1)
!    seq 10 permit 0.0.0.0/0 le 32 (hit count: 5, refcount: 1)      ← hit count tăng
show ip bgp neighbors <ip> routes
! Total number of prefixes 5
```

⭐⭐ **BA loại catch-all — thuộc lòng cả ba:**

| Công cụ | Catch-all |
|---|---|
| ⭐ **Prefix-list** | ⭐ **`permit 0.0.0.0/0 le 32`** |
| ⭐ **AS-path ACL** | ⭐ **`permit .*`** |
| ⭐ **Route-map** | ⭐ `route-map X permit <seq>` **không có `match`** |

🔴 Cả ba đều có **implicit deny** — thiếu catch-all = **mất hết route** = **sự cố production**.
</details>

---

**Câu 8.** ⭐ Điền bảng regex AS-path: `^$` · `^65002$` · `^65002_` · `_65003_` · `_65003$` · `.*`

<details><summary>Xem đáp án</summary>

| Regex | Nghĩa | Ví dụ AS-path khớp |
|---|---|---|
| ⭐ **`^$`** | ⭐ AS-path **RỖNG** = route sinh **trong AS của mình** | *(trống)* |
| ⭐ **`^65002$`** | ⭐ **CHỈ** AS 65002 = route sinh tại AS kề 65002 | `65002` |
| ⭐ **`^65002_`** | ⭐ **BẮT ĐẦU** bằng 65002 = route **từ AS kề** 65002 | `65002` · `65002 65010` · `65002 65010 65020` |
| ⭐ **`_65003_`** | ⭐ **ĐI QUA** AS 65003 (bất kỳ vị trí) | `65002 65003` · `65003 65010` · `65002 65003 65010` |
| ⭐ **`_65003$`** | ⭐ **KẾT THÚC** bằng 65003 = route **SINH TẠI** AS 65003 | `65002 65003` · `65004 65003` |
| ⭐ **`.*`** | ⭐ **MỌI THỨ** — catch-all | tất cả |

⭐ **Ký tự `_` = dấu phân cách:** khoảng trắng, dấu phẩy, **đầu chuỗi**, **cuối chuỗi**.
Nên `_65003_` khớp cả khi 65003 ở đầu hoặc cuối.

⭐ **Ứng dụng thực tế quan trọng nhất:**
```
show ip bgp regexp ^$
```
→ Liệt kê **đúng những prefix sinh trong AS của bạn** = đúng những gì bạn **NÊN** quảng bá cho ISP.
⭐ Đây là **lệnh vàng để verify outbound filter** và phát hiện route leak.

**Test regex nhanh:**
```
show ip bgp regexp <regex>
```
</details>

---

**Câu 9.** ⭐ Bạn cấu hình `aggregate-address 10.1.0.0 255.255.252.0` nhưng peer vẫn thấy
cả 4 prefix `/24`. Vì sao? Và `as-set` để làm gì?

<details><summary>Xem đáp án</summary>

**Vì sao:** ⭐ `aggregate-address` **không có option** thì quảng bá **CẢ aggregate VÀ tất cả
prefix con** → peer thấy 5 route (1 aggregate + 4 con) → **không giảm được gì**.

**Sửa — thêm `summary-only`:**
```
router bgp 65001
 aggregate-address 10.1.0.0 255.255.252.0 summary-only
```

**Verify:**
```
show ip bgp | include 10.1
! *>  10.1.0.0/22   0.0.0.0        32768 i         ← aggregate
! s>  10.1.1.0/24   0.0.0.0    0   32768 i         ← s = SUPPRESSED
! s>  10.1.2.0/24   0.0.0.0    0   32768 i
```
⭐ **`s`** = suppressed — vẫn trong BGP table nhưng **không quảng bá cho peer**.

⭐⭐ **`as-set` để làm gì — GIỮ CHỐNG LOOP:**

Khi bạn gộp các prefix **học từ AS khác**, aggregate mặc định có AS-path **chỉ chứa ASN của bạn**
→ ⭐ **mất thông tin AS đã đi qua** → ⭐ **mất chống loop** → route có thể **quay lại AS gốc**.

| | Không `as-set` | ⭐ Có `as-set` |
|---|---|---|
| AS-path của aggregate | `65001` (chỉ ASN mình) | ⭐ `65001 {65002,65003}` (**AS_SET**) |
| Attribute cảnh báo | ⭐ **`atomic-aggregate`** | Không cần |
| Chống loop | 🔴 **MẤT** | ⭐ ✅ **Hoạt động** |

```
router bgp 65001
 aggregate-address 10.3.0.0 255.255.252.0 summary-only as-set
```
```
show ip bgp 10.3.0.0
!   65001 {65002,65003}, (aggregated by 65001 1.1.1.1)     ← AS_SET
```

⭐ **Quy tắc thực chiến:** gộp prefix **của chính mình** → `summary-only` là đủ.
Gộp prefix **học từ AS khác** → ⭐ **BẮT BUỘC `as-set`**, nếu không là một nguyên nhân của route leak.

⭐ **Điều kiện:** aggregate chỉ được sinh nếu có ⭐ **ít nhất 1 prefix con** trong BGP table.
</details>

---

**Câu 10.** `show ip bgp 10.5.5.0` cho ra output này. Path nào best và vì sao?
```
Paths: (3 available, best #?, table default)
  65002 65010
    10.0.12.2 from 10.0.12.2 (2.2.2.2)
      Origin IGP, metric 100, localpref 100, valid, external
  65004 65010
    10.0.14.2 from 10.0.14.2 (4.4.4.4)
      Origin incomplete, localpref 150, valid, external
  65006 65020 65010
    10.0.16.2 from 10.0.16.2 (6.6.6.6)
      Origin IGP, metric 50, localpref 150, weight 300, valid, external
```

<details><summary>Xem đáp án</summary>

⭐ **Path 3 (qua `10.0.16.2`, AS-path `65006 65020 65010`) thắng.**

**Phân tích theo 13 bước:**

| Bước | Path 1 | Path 2 | Path 3 | Kết quả |
|:---:|---|---|---|---|
| 0. valid | ✅ | ✅ | ✅ | Tie |
| ⭐ **1. Weight** | **0** | **0** | ⭐ **300** | ⭐ **PATH 3 THẮNG — DỪNG** |
| 2. Local Pref | 100 | 150 | 150 | *(không xét)* |
| 4. AS-path | 2 | 2 | **3** | *(không xét)* |
| 5. Origin | `i` | `?` | `i` | *(không xét)* |
| 6. MED | 100 | (0) | 50 | *(không xét)* |

⭐ **Weight = bước 1** → path 3 có Weight 300 > 0 → thắng ngay, ⭐ **không xét bước nào nữa**.

⚠️ **Điểm gây bẫy:** path 3 có **AS-path DÀI NHẤT (3 hop)** — trực giác nói nó phải kém nhất.
Nhưng Weight (bước 1) đứng **trước** AS-path (bước 4) rất nhiều bước.

**Nếu KHÔNG có Weight 300** thì sẽ ra sao?

| Bước | Path 1 | Path 2 | Path 3 | Kết quả |
|:---:|---|---|---|---|
| 1. Weight | 0 | 0 | 0 | Tie |
| ⭐ **2. LocPref** | **100** | ⭐ **150** | ⭐ **150** | ⭐ **Path 1 BỊ LOẠI** |
| 3. Local originated | — | — | — | Tie |
| ⭐ **4. AS-path** | — | ⭐ **2** | **3** | ⭐ **PATH 2 THẮNG — DỪNG** |

→ ⭐ **Path 2 thắng** (LocPref 150 + AS-path ngắn hơn) — dù nó có `Origin incomplete` (`?`, kém nhất).
Vì Origin là **bước 5**, đứng **sau** AS-path (bước 4).

⭐ **Bài học:** luôn đọc theo **đúng thứ tự**, và **dừng ngay** ở bước đầu tiên có giá trị khác nhau.
Đừng để trực giác ("AS-path ngắn phải thắng", "origin `i` phải thắng") dẫn dắt.
</details>

---

**Câu 11.** ⭐ Bạn đổi route-map inbound nhưng path selection không thay đổi. Nguyên nhân?
Và lệnh nào verify filter có thật sự hoạt động?

<details><summary>Xem đáp án</summary>

**Nguyên nhân 1 (phổ biến nhất) — ⭐ chưa reset phiên:**

Policy mới **không tự động áp** cho route đã nhận trước đó.
```
clear ip bgp <ip> soft in            ! đổi INBOUND policy
clear ip bgp <ip> soft out           ! đổi OUTBOUND policy
```
⭐ `soft` dùng **route-refresh** → **không đóng phiên TCP** → không downtime.

**Nguyên nhân 2 — ⭐ Weight đang thắng:**
```
show ip bgp <prefix>                 ! xem cột weight
show run | include weight
```
Weight (bước 1) thắng Local Preference (bước 2) → route-map đặt LocPref vô hiệu.

**Nguyên nhân 3 — route-map chưa được áp / sai tên / sai chiều:**
```
show run | section router bgp
show ip bgp neighbors <ip> | include route-map|prefix-list|filter-list
```

**⭐ Lệnh verify filter có thật sự hoạt động — dùng COUNTER:**

```
show route-map <NAME>
! route-map RM-IN, permit, sequence 10
!   Match clauses:
!     ip address prefix-lists: PL-X
!   Set clauses:
!     local-preference 200
!   Policy routing matches: 0 packets, 0 bytes        ← counter
```

```
show ip prefix-list detail <NAME>
! seq 5 permit 10.3.3.0/24 (hit count: 3, refcount: 1)    ← HIT COUNT
! seq 10 deny 0.0.0.0/0 le 32 (hit count: 2, refcount: 1)
```

⭐ **Đọc counter:**

| Counter | Nghĩa |
|---|---|
| ⭐ **`hit count = 0`** trên mọi dòng | ⭐ Filter **không được gọi** — chưa áp vào neighbor, hoặc sai tên |
| `hit count > 0` ở dòng deny/catch-all, `0` ở dòng permit cụ thể | Filter được gọi nhưng **prefix không khớp** như bạn nghĩ |
| `hit count > 0` đúng chỗ | ✅ Filter hoạt động |

**Xem route nào khớp filter:**
```
show ip bgp prefix-list <NAME>       ! route khớp prefix-list
show ip bgp filter-list <N>          ! route khớp AS-path ACL
show ip bgp route-map <NAME>         ! route khớp route-map
```

⭐ **Quy trình chuẩn khi đổi policy BGP:**
1. Cấu hình policy
2. Áp vào neighbor (`neighbor x route-map Y in/out`)
3. ⭐ `clear ip bgp <ip> soft in/out`
4. ⭐ Verify **counter** (`show ip prefix-list detail` / `show route-map`)
5. Verify **kết quả** (`show ip bgp <prefix>` / `show ip bgp neighbors <ip> routes`)
</details>

---

**Câu 12.** ⭐ Kịch bản production: doanh nghiệp có 2 ISP. ISP1 = 1 Gbps (chính),
ISP2 = 200 Mbps (backup). Viết cấu hình đầy đủ cho router biên (1 router, AS 65001,
prefix của bạn là `203.0.113.0/24`).

<details><summary>Xem đáp án</summary>

```
! ═══════════ 1. PREFIX-LIST: chỉ quảng bá prefix CỦA MÌNH ═══════════
ip prefix-list PL-MY-PREFIX-OUT seq 5 permit 203.0.113.0/24
!   (implicit deny → không quảng bá gì khác — CHỐNG ROUTE LEAK)

! ═══════════ 2. PREFIX-LIST: chặn bogon + prefix quá nhỏ inbound ═══════════
ip prefix-list PL-BOGON-IN seq 5  deny 0.0.0.0/8 le 32
ip prefix-list PL-BOGON-IN seq 10 deny 10.0.0.0/8 le 32
ip prefix-list PL-BOGON-IN seq 15 deny 127.0.0.0/8 le 32
ip prefix-list PL-BOGON-IN seq 20 deny 169.254.0.0/16 le 32
ip prefix-list PL-BOGON-IN seq 25 deny 172.16.0.0/12 le 32
ip prefix-list PL-BOGON-IN seq 30 deny 192.168.0.0/16 le 32
ip prefix-list PL-BOGON-IN seq 35 deny 224.0.0.0/4 le 32
ip prefix-list PL-BOGON-IN seq 40 deny 0.0.0.0/0 ge 25       ! chặn prefix nhỏ hơn /24
ip prefix-list PL-BOGON-IN seq 45 permit 0.0.0.0/0 le 32     ! CATCH-ALL

! ═══════════ 3. OUTBOUND: ưu tiên inbound traffic vào qua ISP1 ═══════════
! ISP2 nhận AS-path DÀI HƠN → khách chọn ISP1
route-map RM-ISP2-OUT permit 10
 match ip address prefix-list PL-MY-PREFIX-OUT
 set as-path prepend 65001 65001 65001
!  (không có catch-all permit → chỉ quảng bá prefix của mình)

route-map RM-ISP1-OUT permit 10
 match ip address prefix-list PL-MY-PREFIX-OUT
!  (không prepend — ISP1 là đường chính)

! ═══════════ 4. INBOUND: ưu tiên outbound traffic ra qua ISP1 ═══════════
route-map RM-ISP1-IN permit 10
 set local-preference 200                     ! ISP1 = 200 (ưu tiên)

route-map RM-ISP2-IN permit 10
 set local-preference 100                     ! ISP2 = 100 (mặc định, backup)

! ═══════════ 5. BGP ═══════════
router bgp 65001
 bgp router-id 203.0.113.1
 bgp log-neighbor-changes
 bgp deterministic-med                        ! kết quả nhất quán
 !
 ! ─── ISP1 (chính, 1 Gbps) ───
 neighbor 198.51.100.1 remote-as 64500
 neighbor 198.51.100.1 description ---> ISP1 VNPT circuit#A123 - PRIMARY 1G
 neighbor 198.51.100.1 password <ISP1-secret>
 neighbor 198.51.100.1 ttl-security hops 1
 neighbor 198.51.100.1 maximum-prefix 200000 90      ! BẮT BUỘC
 neighbor 198.51.100.1 send-community both
 neighbor 198.51.100.1 prefix-list PL-BOGON-IN in
 neighbor 198.51.100.1 route-map RM-ISP1-IN in
 neighbor 198.51.100.1 route-map RM-ISP1-OUT out
 neighbor 198.51.100.1 fall-over                      ! xuống ngay khi mất route
 !
 ! ─── ISP2 (backup, 200 Mbps) ───
 neighbor 203.0.114.1 remote-as 64501
 neighbor 203.0.114.1 description ---> ISP2 Viettel circuit#B456 - BACKUP 200M
 neighbor 203.0.114.1 password <ISP2-secret>
 neighbor 203.0.114.1 ttl-security hops 1
 neighbor 203.0.114.1 maximum-prefix 200000 90
 neighbor 203.0.114.1 send-community both
 neighbor 203.0.114.1 prefix-list PL-BOGON-IN in
 neighbor 203.0.114.1 route-map RM-ISP2-IN in
 neighbor 203.0.114.1 route-map RM-ISP2-OUT out
 neighbor 203.0.114.1 fall-over
 !
 network 203.0.113.0 mask 255.255.255.0
```

⭐ **Giải thích logic:**

| Mục tiêu | Cách làm | Chiều |
|---|---|:---:|
| ⭐ **Outbound qua ISP1** | Local Pref **200** cho ISP1, **100** cho ISP2 | `in` |
| ⭐ **Inbound qua ISP1** | AS-path **prepend 3 lần** khi quảng bá cho ISP2 | `out` |
| 🔴 **Chống route leak** | Prefix-list outbound **chỉ** `203.0.113.0/24` (implicit deny phần còn lại) | `out` |
| 🔴 **Chống nhận rác** | Prefix-list inbound chặn **bogon** + prefix `/25` trở xuống | `in` |
| 🔴 **Chống hết RAM** | `maximum-prefix 200000 90` | — |
| **Bảo mật phiên** | `password` + `ttl-security hops 1` | — |
| **Failover nhanh** | `fall-over` (không chờ hold 180 s) | — |

⭐ **Verify sau khi cấu hình:**
```
show ip bgp summary                                          ! cả 2 Established?
show ip bgp neighbors 198.51.100.1 advertised-routes         ! CHỈ 1 prefix của mình?
show ip bgp neighbors 203.0.114.1 advertised-routes          ! CHỈ 1 prefix, AS-path prepend?
show ip bgp regexp ^$                                        ! khớp với advertised-routes?
show ip bgp 0.0.0.0/0                                        ! LocPref ISP1 = 200?
show ip route 0.0.0.0                                        ! đi qua ISP1?
show ip prefix-list detail PL-MY-PREFIX-OUT                  ! hit count > 0?
```

⭐ **Test failover:** shutdown interface ISP1 → traffic phải chuyển sang ISP2 trong vài giây.

> ⭐ **Điểm quan trọng nhất của cấu hình này:** **prefix-list outbound**.
> Thiếu nó = bạn có thể quảng bá **toàn bộ route học từ ISP1 sang ISP2** →
> trở thành **transit AS ngoài ý muốn** → traffic Internet chảy qua đường 200 Mbps của bạn →
> sập. Đây là loại sự cố đã xảy ra nhiều lần ở quy mô toàn cầu.
</details>

---

## 📚 9. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | Ghi chú |
|---|---|---|
| ⭐ **Best path selection** | Chọn đường tốt nhất | ⭐ 13 bước, dừng ở bước đầu tiên phân định |
| ⭐ **Weight** | Trọng số | ⭐ **Bước 1**, Cisco-only, **chỉ local**, **CAO** thắng |
| ⭐ **Local Preference** | Ưu tiên cục bộ | ⭐ **Bước 2**, lan **trong AS**, mặc định **100**, **CAO** thắng |
| ⭐ **Locally originated** | Sinh tại chỗ | ⭐ **Bước 3** — `network` > `aggregate` > `redistribute` |
| ⭐ **AS-path length** | Độ dài đường AS | ⭐ **Bước 4**, **NGẮN** thắng |
| ⭐ **Origin** | Nguồn gốc | ⭐ **Bước 5** — `i` < `e` < `?`, **THẤP** thắng |
| ⭐ **MED** | Phân biệt đa lối ra | ⭐ **Bước 6**, **THẤP** thắng, ⚠️ mặc định **chỉ so cùng AS kề** |
| ⭐ **Hot potato routing** | Định tuyến "khoai nóng" | ⭐ **Bước 8** — ra khỏi AS càng sớm càng tốt |
| **Oldest path** | Đường cũ nhất | **Bước 10** — ưu tiên ổn định |
| ⭐ **`always-compare-med`** | Luôn so MED | ⭐ So MED giữa **mọi** AS (⚠️ có thể bất ổn) |
| ⭐ **`deterministic-med`** | MED xác định | ⭐ Nhóm path theo AS trước khi so → **kết quả nhất quán**. Nên bật |
| **`missing-as-worst`** | MED thiếu = tệ nhất | MED không đặt → 4294967295 thay vì 0 |
| ⭐ **AS-path prepend** | Thêm ASN vào đầu | ⭐ Làm AS-path **dài hơn** → điều khiển **INBOUND**, áp chiều **`out`** |
| ⭐ **Outbound traffic** | Traffic đi ra | ⭐ Điều khiển bằng **Weight/LocPref**, chiều **`in`** — **TÔI quyết** |
| ⭐ **Inbound traffic** | Traffic đi vào | ⭐ Điều khiển bằng **prepend/MED**, chiều **`out`** — chỉ **GỢI Ý** |
| ⭐ **Community** | Cộng đồng | ⭐ Nhãn gắn lên route → AS kề đọc và áp policy. **Optional Transitive** |
| ⭐ **`no-export`** | Không xuất khẩu | ⭐ Không quảng bá cho **eBGP** peer (iBGP **vẫn được**) |
| ⭐ **`no-advertise`** | Không quảng bá | ⭐ Không quảng bá cho **BẤT KỲ** peer nào |
| **`local-AS`** | AS cục bộ | Không ra khỏi sub-AS (confederation) |
| **`internet`** | Internet | Quảng bá cho mọi peer (mặc định) |
| 🔴 ⭐ **`send-community`** | Gửi community | 🔴 **BẮT BUỘC** — Cisco không gửi community mặc định |
| ⭐ **`additive`** | Cộng thêm | ⭐ **THÊM** community (thiếu = **GHI ĐÈ**) |
| **Community-list** | Danh sách community | Standard 1–99 (giá trị) · Expanded 100–500 (regex) |
| ⭐ **Prefix-list** | Danh sách tiền tố | ⭐ Catch-all = **`permit 0.0.0.0/0 le 32`** |
| ⭐ **`le` / `ge`** | ≤ / ≥ | Giới hạn độ dài mask |
| ⭐ **AS-path ACL / filter-list** | ACL đường AS | ⭐ Lọc theo **regex AS-path**. Catch-all = **`permit .*`** |
| ⭐ **`^$`** | AS-path rỗng | ⭐ Route sinh **trong AS mình** |
| ⭐ **`_` (regex)** | Dấu phân cách | ⭐ Space, dấu phẩy, đầu/cuối chuỗi |
| ⭐ **Route-map** | Bản đồ route | ⭐ Lọc **+ sửa attribute**. Catch-all = `permit <seq>` không có `match` |
| ⭐ **Implicit deny** | Chặn ngầm | ⭐ Có ở **cả 3**: prefix-list, AS-path ACL, route-map |
| ⭐ **Hit count** | Số lần khớp | ⭐ `show ip prefix-list detail` — verify filter có hoạt động |
| ⭐ **`aggregate-address`** | Địa chỉ gộp | ⭐ Summarization của BGP |
| ⭐ **`summary-only`** | Chỉ tóm tắt | ⭐ **Suppress** prefix con → hiện **`s`** |
| ⭐ **`as-set`** | Tập AS | ⭐ Đưa AS-path prefix con vào `{65002,65003}` → ⭐ **giữ chống loop** |
| ⭐ **`s` suppressed** | Bị đè | ⭐ Prefix con bị `summary-only` — không quảng bá |
| ⭐ **`atomic-aggregate`** | Gộp nguyên tử | ⭐ Cảnh báo route đã gộp, **mất chi tiết AS-path** |
| **Aggregator** | Bộ gộp | ASN + Router ID của router đã gộp |
| 🔴 ⭐ **Route leak** | Rò rỉ route | 🔴 Quảng bá route không phải của mình → sự cố diện rộng. Chống bằng **prefix-list outbound** |
| ⭐ **Bogon** | Prefix "rác" | ⭐ Dải không được route trên Internet (private, loopback, multicast…) |
| **Transit AS** | AS trung chuyển | AS cho traffic đi xuyên qua. ⚠️ Trở thành transit **ngoài ý muốn** = sự cố |
| **RPKI / ROA** | Xác thực nguồn gốc route | Xu hướng mới — chữ ký số cho prefix. Không có trong ENCOR |

---

## 🎯 10. ĐÚC KẾT MODULE-05B

**3 điều rút ra:**

1. ⭐⭐ **13 bước, và CHỈ 2 bước đầu là "CAO thắng".** Weight (bước 1) và Local Preference (bước 2)
   — CAO thắng. Từ AS-path (bước 4) trở đi, **tất cả THẤP thắng**. Và ⭐ **Weight thắng mọi thứ khác**
   — nên khi "đặt LocPref mà path không đổi", ⭐ **kiểm tra Weight trước tiên**.

2. ⭐⭐ **"Nhận route VÀO → quyết định đi RA. Gửi route RA → gợi ý người ta đi VÀO."**
   Outbound (Weight/LocPref, chiều `in`) là ⭐ **quyết định của tôi**.
   Inbound (prepend/MED, chiều `out`) chỉ là ⭐ **gợi ý** — AS bên kia ghi đè được bằng
   Weight/LocPref của họ, vì hai bước đó đứng trước.

3. 🔴 **Ba loại catch-all khác nhau, và thiếu cái nào cũng mất hết route:**
   prefix-list = ⭐ **`permit 0.0.0.0/0 le 32`** (⚠️ **không phải** `permit 0.0.0.0/0`) ·
   AS-path ACL = ⭐ **`permit .*`** · route-map = ⭐ `permit <seq>` **không có `match`**.
   Và ⭐ **đổi policy xong phải `clear ip bgp <ip> soft in/out`**.

🧠 **Một câu để nhớ:** *BGP không tìm đường **ngắn nhất** — nó thực thi **chính sách**.
13 bước là 13 tầng chính sách, xếp từ **"ý chí của tôi"** (Weight, LocPref)
đến **"thực tế khách quan"** (AS-path, Origin, MED) rồi tới **"luật tung xúi xẻ"** (Router ID, neighbor IP)
— để mạng **luôn ra được một quyết định nhất quán**.*

---

### ✅ TỰ CHẤM — Milestone Tuần 11 (mốc quan trọng nhất nửa đầu khóa)

**Phần A — Trả lời được bằng lời của mình:**

| # | Câu | ✅ |
|:---:|---|:---:|
| 1 | ⭐ Kể 13 bước theo thứ tự + mnemonic | ☐ |
| 2 | ⭐ Bước nào "CAO thắng", bước nào "THẤP thắng"? | ☐ |
| 3 | Weight vs Local Pref: lan tới đâu, khi nào dùng cái nào, cái nào thắng? | ☐ |
| 4 | ⭐ Điều khiển OUTBOUND: attribute nào, chiều nào? | ☐ |
| 5 | ⭐ Điều khiển INBOUND: attribute nào, chiều nào, vì sao chỉ là gợi ý? | ☐ |
| 6 | ⭐ MED mặc định so sánh thế nào? 3 lệnh đổi hành vi MED? | ☐ |
| 7 | ⭐ MED không đặt = bao nhiêu? Hệ quả? | ☐ |
| 8 | 3 Origin code + thứ tự. Nên dùng `network` hay `redistribute`? | ☐ |
| 9 | Bước 8 "hot potato routing" nghĩa là gì? | ☐ |
| 10 | ⭐ `no-export` vs `no-advertise` | ☐ |
| 11 | 🔴 Vì sao `set community` có thể "không có tác dụng"? | ☐ |
| 12 | `set community` không có `additive` thì sao? | ☐ |
| 13 | 🔴 ⭐ Catch-all của prefix-list / AS-path ACL / route-map — cả 3 | ☐ |
| 14 | 🔴 `permit 0.0.0.0/0` khớp gì? | ☐ |
| 15 | ⭐ Regex: `^$` · `^65002$` · `^65002_` · `_65003_` · `_65003$` · `.*` | ☐ |
| 16 | ⭐ Ký tự `_` trong regex AS-path nghĩa gì? | ☐ |
| 17 | ⭐ `aggregate-address` không option / `summary-only` / `as-set` — mỗi cái làm gì? | ☐ |
| 18 | ⭐ Vì sao cần `as-set`? `atomic-aggregate` nghĩa là gì? | ☐ |
| 19 | `s` trong `show ip bgp` nghĩa là gì? | ☐ |
| 20 | ⭐ Đổi policy xong cần làm gì? Lệnh verify filter hoạt động? | ☐ |

**Phần B — Lab:**

| # | Yêu cầu | ✅ |
|:---:|---|:---:|
| 1 | Thêm link R4↔R3 → R1 có **2 path** tới `10.3.3.0/24`, AS-path đều dài 2 | ☐ |
| 2 | ⭐⭐ Dùng `show ip bgp <prefix>` **phân tích 13 bước** và xác định **bước nào** quyết định | ☐ |
| 3 | ⭐ Chứng minh **bước 11 (Router ID)**: đổi Router ID R4 → path đổi | ☐ |
| 4 | ⭐⭐ **AS-path prepend** (chiều `out`) → R3 đổi đường vào AS 65001 | ☐ |
| 5 | ⭐⭐ Chứng minh **"inbound chỉ là gợi ý"**: R3 dùng Weight ghi đè prepend | ☐ |
| 6 | ⭐⭐ **Local Preference** (chiều `in`) → R1 đổi đường ra, verify cột `LocPrf` | ☐ |
| 7 | ⭐⭐ Chứng minh **Weight thắng Local Preference** (bước 1 > bước 2) | ☐ |
| 8 | ⭐ Chứng minh **MED không được so** giữa 2 AS khác nhau | ☐ |
| 9 | Bật `always-compare-med` → MED có tác dụng | ☐ |
| 10 | ⭐ Chuyển `network` → `redistribute` → thấy **Origin đổi `i` → `?`** | ☐ |
| 11 | ⭐⭐ **`no-export`** + `send-community` → R2 thấy `Not advertised to any peer`, R1 **không** nhận prefix | ☐ |
| 12 | 🔴⭐ **Tái hiện lỗi quên `send-community`** → community mất → prefix **lọt ra** | ☐ |
| 13 | `no-advertise` chặn mạnh hơn `no-export` | ☐ |
| 14 | ⭐ Community tự định nghĩa (`65003:100`) + `match community` → áp LocPref 300 | ☐ |
| 15 | ⭐ Prefix-list inbound + verify bằng **hit count** | ☐ |
| 16 | 🔴⭐⭐ **Tái hiện `permit 0.0.0.0/0` thiếu `le 32`** → **mất hết route** → sửa | ☐ |
| 17 | ⭐ Test đủ 5 regex: `^$`, `^65002$`, `^65002_`, `_65003_`, `_65003$` | ☐ |
| 18 | ⭐ AS-path ACL (`filter-list`) chỉ nhận route sinh tại AS kề (`^65002$`) | ☐ |
| 19 | 🔴 Tái hiện AS-path ACL **thiếu `permit .*`** → mất hết route | ☐ |
| 20 | Route-map kết hợp `deny` + `match as-path` + `set` + **catch-all**, verify counter | ☐ |
| 21 | ⭐ `aggregate-address` **không** `summary-only` → peer thấy **cả** aggregate + con | ☐ |
| 22 | ⭐⭐ Thêm `summary-only` → prefix con hiện **`s`**, peer chỉ thấy **1 route** | ☐ |
| 23 | ⭐ Chỉ ra **discard route Null0** của aggregate | ☐ |
| 24 | ⭐⭐ Gộp route học từ AS khác **không có `as-set`** → thấy `atomic-aggregate`, AS-path mất chi tiết | ☐ |
| 25 | ⭐⭐ Thêm **`as-set`** → thấy **`{65002,65003}`**, chống loop hoạt động lại | ☐ |
| 26 | ⭐ Dùng `show ip bgp regexp ^$` verify đúng prefix mình **nên** quảng bá | ☐ |
| 27 | ⭐⭐ Viết & áp cấu hình **dual-ISP hoàn chỉnh** (quiz câu 12): LocPref in + prepend out + prefix-list 2 chiều + `maximum-prefix` + `password` | ☐ |
| 28 | Cố ý phá 1 thứ, tự tìm ra bằng **quy trình 13 bước §7.3** trong 10 phút | ☐ |

> ⚠️⚠️ **Đây là milestone quan trọng nhất nửa đầu khóa (theo ROADMAP §4, "Routing vững — tuần 11").**
> Tick được hết Phần B nghĩa là bạn đã nắm **toàn bộ khối Routing** của ENCOR:
> OSPF (Module-04A/B) + BGP (Module-05A/B) = phần lớn nhất của domain Infrastructure (30% đề).
>
> ⭐ **Nếu chỉ có thời gian làm một nửa:** ưu tiên **mục 2** (phân tích 13 bước),
> **mục 4–7** (điều khiển hướng traffic), **mục 12** (`send-community`),
> **mục 16** (`le 32`), **mục 24–25** (`as-set`), và **mục 27** (dual-ISP hoàn chỉnh).
> Sáu mục đó phủ gần hết những gì đề hỏi **và** những gì bạn cần khi đi làm.

---

## 🔗 11. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Cụ thể |
|---|---|
| **Sách OCG 350-401** | Chương **BGP** thứ hai (*"Advanced BGP"* / *"BGP Path Selection"*) — ⭐ đọc kỹ bảng 13 bước và bảng attribute |
| **Cisco doc** ⭐⭐ | ***BGP Best Path Selection Algorithm*** — ⭐ **tài liệu GỐC của 13 bước**. Search: `bgp best path selection algorithm cisco`. **Đọc bản này, không đọc bản tóm tắt của người khác** |
| **Cisco doc** ⭐ | *BGP Case Studies* — phần *Route Filtering*, *Community*, *Aggregation* với ví dụ thực tế |
| **Cisco doc** ⭐ | *Using Regular Expressions in BGP* — bảng regex AS-path đầy đủ |
| **Cisco doc** ⭐ | *BGP Communities* · *Understanding BGP Community* |
| **Cisco doc** | *Understanding Route Aggregation in BGP* — giải thích `as-set` và `atomic-aggregate` |
| **Cisco doc** | *How the `bgp deterministic-med` Command Differs from `bgp always-compare-med`* |
| **Cisco doc** ⭐ | *BGP Best Practices* / *Security Considerations for BGP* — bogon filter, maximum-prefix, route leak |
| **RFC 4271** | BGP-4 — **Section 9.1 (Decision Process)** |
| **RFC 1997** | BGP Communities Attribute — nguồn gốc `no-export`/`no-advertise` |
| **RFC 7454** | ⭐ **BGP Operations and Security** — tài liệu chuẩn về filter, bogon, route leak. **Rất đáng đọc cho công việc thật** |
| **Cisco Live** ⭐ | Search `Cisco Live BGP best practices enterprise` · `Cisco Live BGP path selection` · `Cisco Live BGP security` |
| **NetworkLessons** ⭐ | Loạt bài *BGP Attributes*, *BGP Weight/Local Preference/MED/AS-path*, *BGP Communities*, *BGP Aggregation* |
| **Video** | CBT Nuggets ENCOR — module BGP path selection · Keith Barker: search `Keith Barker BGP path selection`, `Keith Barker BGP communities` |
| **Công cụ** | **bgp.he.net** (Hurricane Electric BGP Toolkit) — xem AS-path thật trên Internet · **RIPEstat** — xem prefix của một AS |
| **Forum** | https://community.cisco.com — search `bgp weight vs local preference`, `bgp med not working different as`, `bgp aggregate as-set`, `prefix-list le 32` |

---

**➡️ Tiếp theo:** Module-06 — IP Services *(FHRP: HSRP/VRRP/GLBP · NAT/PAT nâng cao ·
NTP · Multicast (PIM/IGMP — describe) · IPv6 First-Hop Security — **Tuần 11**)*
