# Module-12 — Automation & Programmability

> 🧭 **Lộ trình:** [Module-11](Module-11-Network-Assurance.md) → `[Bạn đang ở đây] Module-12` → Module-13 (Ôn thi)
>
> 📊 **Blueprint — Domain 6.0 Automation (15% đề):**
> · ⭐ **6.1 — Interpret basic Python components and scripts**
> · ⭐ **6.2 — Construct valid JSON encoded file**
> · 🟡 **6.3 — Describe the high-level principles and benefits of a data modeling language, such as YANG**
> · 🟡 **6.4 — Describe APIs for Cisco DNA Center and vManage**
> · ⭐ **6.5 — Interpret REST API response codes and results in payload using Cisco DNA Center and RESTCONF**
> · 🔴  **6.6 — CONSTRUCT EEM applet to automate configuration, troubleshooting, or data collection**
> · 🟡 **6.7 — Compare agent vs. agentless orchestration tools (Chef, Puppet, Ansible, SaltStack)**
>
> 📊 **Và một mục MƯỢN từ Domain 4.0:**
> · 🔴  **4.7 — CONFIGURE AND VERIFY NETCONF and RESTCONF** → dạy ở **§7** module này
>
> ⏱️ **Tuần 18–19** · 14 giờ

---

# 📌 TÓM TẮT — đọc 10 phút là nắm khung

## Module này trả lời một câu hỏi duy nhất

> **Làm sao ra lệnh cho mạng mà KHÔNG phải gõ tay từng thiết bị — và làm sao ĐỌC HIỂU
> thứ mà máy trả lời lại?**

⭐ Chú ý vế thứ hai. **Đề ENCOR hỏi bạn ĐỌC nhiều hơn hỏi bạn VIẾT.** Đề đưa một đoạn JSON,
một đoạn Python, một mã lỗi HTTP rồi hỏi *"giá trị nào / kết quả gì / sai ở đâu"*.
Bạn **không cần trở thành lập trình viên**. Bạn cần **đọc trôi**.

## Toàn cảnh: từ người đến thiết bị có mấy đường?

```
   BẠN / SCRIPT / CONTROLLER
            │
    ┌───────┴────────┬─────────────────┬──────────────────┐
    │                │                 │                  │
   CLI            NETCONF           RESTCONF         Controller API
 (gõ tay)        SSH · 830         HTTPS · 443      HTTPS · 443
    │                │                 │           (DNAC / vManage)
    │             XML · RPC       JSON hoặc XML            │
    │                │              HTTP verb              │
    │                └────── cùng dùng YANG ──────┘        │
    │                       (khuôn dữ liệu)                │
    └────────────────────────┬─────────────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  THIẾT BỊ MẠNG  │
                    └─────────────────┘

   Và một đường ĐẶC BIỆT — chạy NGAY TRÊN thiết bị, không cần ai bên ngoài:
                    ┌─────────────────┐
                    │   EEM applet    │  "tự động tại chỗ"
                    └─────────────────┘
```

## 8 ý phải nhớ

| # | Ý | Vì sao quan trọng |
|:---:|---|---|
| 1 | **NETCONF = SSH 830 · RESTCONF = HTTPS 443** | Cặp số bị hỏi nhiều nhất của cả hai domain 4.0 và 6.0 |
| 2 | ⭐ **Chỉ NETCONF có `candidate` datastore + commit/rollback** | RESTCONF đổi là ăn ngay, không hoàn tác được |
| 3 | ⭐ **YANG là KHUÔN, không phải giao thức** | NETCONF/RESTCONF là *cách chở*; YANG là *hình dạng của hàng* |
| 4 | 🔴  **401 = chưa/sai xác thực · 403 = đã xác thực nhưng KHÔNG ĐỦ QUYỀN** | Đề rất thích cặp này. Nhầm là mất điểm |
| 5 | ⭐ **GET/PUT/DELETE idempotent · POST/PATCH KHÔNG** | Gọi PUT 10 lần kết quả như 1 lần. POST 10 lần → tạo 10 thứ |
| 6 | 🔴 **JSON: không comment, không dấu phẩy thừa, key phải trong `" "`** | Mục 6.2 bắt bạn *construct* — tức là tìm ra file nào SAI |
| 7 | 🔴  **EEM applet = `event` (khi nào) + `action` (làm gì)** | Mục duy nhất trong domain 6.0 bắt **CONSTRUCT** — phải viết được |
| 8 | ⭐ **Ansible/SaltStack = agentless · Puppet/Chef = agent** | Thiết bị mạng không cài agent được → nên Ansible thắng trong mạng |

## Bảng lệnh cốt lõi

| Việc | Lệnh |
|---|---|
| **Bật NETCONF** | `netconf-yang` |
| **Bật RESTCONF** | `restconf` + `ip http secure-server` |
| **Xem phiên NETCONF** | `show netconf-yang sessions` |
| **Xem tiến trình YANG** | `show platform software yang-management process` |
| **Tạo EEM applet** | `event manager applet <TÊN>` |
| **Chạy EEM thủ công** | `event manager run <TÊN>` |
| **Xem EEM đã đăng ký** | `show event manager policy registered` |
| **Xem EEM chạy mấy lần** | `show event manager statistics policy` |

## 🗺️ Bố cục module

| Phần | Nội dung | Đọc khi nào |
|---|---|---|
| 🧠 **PHẦN 1** (§2) | **CÁI ĐÓ LÀ GÌ** — ví von, không có lệnh | ⭐ **Đọc đầu tiên, đọc hết** |
| ⚙️ **PHẦN 2** (§3–§10) | **NÓ CHẠY THẾ NÀO** — cơ chế, cú pháp, bảng | Đọc sau Phần 1 |
| 🧪 **PHẦN 3** | **NHÌN THẤY NÓ** — trỏ sang file LAB | Mở song song khi làm lab |
| 🏗️ **PHẦN 4** | **TOPO & KIẾN TRÚC** — ráp lại thành bức tranh | Đọc sau khi làm lab xong |
| 📎 **PHỤ LỤC** | Bẫy đề · gỡ lỗi · quiz · thuật ngữ | ⛔ **KHÔNG đọc lần đầu** — để tra cứu |

---

## ⭐ 0. Phạm vi

### 0.1 Domain 6.0 là domain "ĐỌC", không phải domain "VIẾT"

> ⭐ **Đây là điều quan trọng nhất cần hiểu trước khi học.**
>
> Domain 6.0 chiếm **15% đề** — nhiều thứ ba sau Infrastructure (30%) và Security (20%).
> Nhưng **bạn không bị bắt lập trình**. Đề đưa sẵn một đoạn code / một payload / một mã lỗi
> rồi hỏi bạn **hiểu nó nói gì**.
>
> 🔴 **Ngoại lệ duy nhất là mục 6.6 (EEM)** — động từ là **"CONSTRUCT"**, tức là bạn **phải viết được**.

| Chủ đề | Blueprint | Động từ đề bài | Mức cần đạt | Thời gian |
|---|---|---|---|---|
| **JSON / XML / YAML** | ⭐ **6.2** | **Construct** | Nhìn ra file nào **SAI cú pháp** · lấy đúng giá trị lồng nhau | 2 giờ |
| **REST API** | ⭐ **6.5** | **Interpret** | **Mã trạng thái** · verb · header · token flow | 2 giờ |
| **YANG** | 🟡 **6.3** | **Describe** | Là gì · 4 loại node · native vs OpenConfig vs IETF | 1 giờ |
| **NETCONF / RESTCONF** | 🔴  **4.7** | 🔴 **Configure and verify** | **Bật được · gọi được · so sánh được** | 3 giờ |
| **EEM** | 🔴  **6.6** | 🔴 **CONSTRUCT** | **Tự viết applet từ đầu** — không được chép | 2.5 giờ |
| **Python** | ⭐ **6.1** | **Interpret** | Đọc netmiko/requests · biết script in ra gì | 2 giờ |
| **Ansible & công cụ** | 🟡 **6.7** | **Compare** | ⭐ **Agent vs agentless** · push vs pull | 1 giờ |
| **DNAC & vManage API** | 🟡 **6.4** | **Describe** | ⭐ **Luồng xin token** — không cần nhớ endpoint | 30 phút |

### 0.2 🔴 Module này KHÉP LẠI Domain 4.0

> 🔴  **Nhắc lại cảnh báo ở [Module-11 §0.2](Module-11-Network-Assurance.md):**
> mục **4.7 NETCONF/RESTCONF** thuộc **Domain 4.0**, nhưng được dạy ở đây (**§7**)
> vì không thể hiểu nó mà không hiểu YANG trước.
>
> ⭐ **Học xong §7 thì Domain 4.0 mới thực sự trọn vẹn.** Trước đó, dù đã xong Module-11,
> bạn vẫn đang thiếu một mục.

### 0.3 Bốn mối nối với những gì đã học

| Nối với | Chỗ nào |
|---|---|
| **[Module-11](Module-11-Network-Assurance.md)** — Syslog | ⭐ **EEM bắt sự kiện bằng chính dòng syslog** bạn đã học đọc ở đó |
| **[Module-10](Module-10-Security.md)** — SSH, AAA | ⭐ NETCONF **chạy trên SSH**. Script đăng nhập bằng đúng user AAA đó |
| **[Module-09 §7.8](Module-09-Architecture-va-QoS.md)** — DNA Center | ⭐ Ở đó học **nó làm gì**. Ở đây học **gọi nó bằng API thế nào** |
| **[Module-03](Module-03-IP-Routing-Nen-tang.md)** — IP SLA + track | ⭐ EEM là **bậc cao hơn của track**: track chỉ bật/tắt route, EEM **chạy được cả loạt lệnh** |

---

## ✅ 1. Chuẩn bị

### 1.1 Cần gì để học module này

| Cần có | Chi tiết |
|---|---|
| **Kiến thức trước** | Module-10 (SSH) · Module-11 (Syslog — cho EEM) · Module-09 §7 (DNAC/SD-WAN là gì) |
| **Thiết bị lab** | ⭐ **Hai đường, chọn một** — xem §1.2 |
| **Trên máy bạn** | Python 3 · `pip install requests netmiko ncclient` · Postman *(hoặc `curl`)* |
| **RAM** | ⭐ **Gần như 0** nếu dùng DevNet Sandbox — đây là module **nhẹ RAM nhất** cả khoá |

### 1.2 🔴 Vấn đề thật: EVE-NG của bạn KHÔNG chạy được NETCONF/RESTCONF

> 🔴  **Đọc kỹ chỗ này, nó quyết định cách bạn học 2 tuần tới.**
>
> Ảnh **vIOS / vIOS-L2** bạn dùng từ Module-00 tới giờ là **IOS cổ điển** —
> ⭐ **nó KHÔNG có `netconf-yang`, KHÔNG có `restconf`.** Gõ vào sẽ báo lệnh không tồn tại.
> Hai thứ đó chỉ có trên **IOS-XE** (CSR1000v / Cat8000v).

| Đường | Cần gì | Ưu | Nhược |
|---|---|---|---|
| ⭐ **A. DevNet Sandbox** *(khuyến nghị)* | Chỉ cần **Internet** | **Miễn phí · luôn bật · đã có sẵn NETCONF/RESTCONF/API thật** | Cần mạng · dùng chung nên có lúc chậm |
| **B. CSR1000v/Cat8000v trong EVE-NG** | Ảnh IOS-XE + ⭐ **~4 GB RAM cho 1 node** | Offline · toàn quyền | **Chiếm 4/10 GB RAM khả dụng** · phải tự kiếm ảnh |

> ⭐ **Khuyến nghị thẳng:**  **dùng đường A cho §7 (NETCONF/RESTCONF) và §10 (DNAC API)**,
> ⭐ **dùng EVE-NG vIOS sẵn có cho §8 (EEM)** — vì  **EEM chạy tốt trên vIOS cổ điển.**
>
> Nghĩa là bạn **không cần tải thêm ảnh nào** để học trọn module này.

| Blueprint | Học ở đâu |
|---|---|
| 🔴 **4.7 NETCONF/RESTCONF** | **DevNet Sandbox** *(vIOS không có)* |
| 🔴 **6.6 EEM** | **EVE-NG vIOS — dùng lại đúng lab Module-11** |
| **6.1 Python · 6.2 JSON · 6.5 REST** | ⭐ **Ngay trên máy bạn** — không cần thiết bị |
| **6.4 DNAC / vManage API** | ⭐ **DevNet Sandbox** |
| **6.3 YANG · 6.7 Ansible** | Đọc + xem model trên sandbox |

### 1.3 DevNet Sandbox — vào thế nào

> ⭐ Truy cập **[developer.cisco.com/site/sandbox](https://developer.cisco.com/site/sandbox/)** →
> đăng nhập bằng tài khoản Cisco (miễn phí) → chọn **"Always-On"** (không cần đặt chỗ, không cần VPN).
>
> ⭐ **Hai sandbox bạn cần:**
> - ⭐ **IOS XE on Cat8000V — Always On** *(cho §7: NETCONF/RESTCONF)*
> - ⭐ **Cisco DNA Center — Always On** *(cho §10: API)*
>
> ⚠️ ⭐ **Thông tin đăng nhập và tên host do Cisco công bố ngay trên trang sandbox và
> CÓ THỂ THAY ĐỔI.** ⭐ **Luôn lấy từ trang đó tại thời điểm bạn học**, đừng chép cứng
> từ tài liệu cũ (kể cả tài liệu này) — đây là lỗi làm mất thời gian nhiều nhất của người mới.
>
> ⭐ Một số sandbox "Reserved" cần VPN (AnyConnect).  **Always-On thì không cần** — ưu tiên loại này.

---

## 🧠 PHẦN 1 — CÁI ĐÓ LÀ GÌ

> ⭐ **Phần này KHÔNG có lệnh, KHÔNG có bảng tra cứu.** Chỉ có ví von.
> Mục tiêu: đọc xong bạn **nói lại được cho người khác nghe** mà không cần mở tài liệu.
> ⭐ **Đọc hết phần này trước khi sang Phần 2.**

### 2.1 Automation là gì — bài toán 100 con switch

Bạn có **1 switch** cần thêm VLAN 20. Bạn SSH vào, gõ 3 dòng, xong trong 1 phút. **Không cần automation.**

Bạn có **100 switch** cần thêm VLAN 20.

- Gõ tay: 100 phút, và **thế nào cũng có vài con bị gõ sai** — sai chỗ nào thì 3 tháng sau mới lộ.
- Tệ hơn: sếp hỏi *"con nào đã có VLAN 20 rồi?"* → bạn phải SSH vào **từng con** để đếm.

⭐ **Automation không phải là "công nghệ cao". Nó là cách trả lời hai câu hỏi trên mà
không phụ thuộc vào việc bạn có mỏi tay hay không.**

Và nó sinh ra ba thứ mà gõ tay không bao giờ có:

> 🍰 **Ví von — công thức làm bánh.**
> Gõ tay giống **nấu theo trí nhớ**: ngon dở tuỳ hôm nay bạn tỉnh táo cỡ nào.
> Automation giống **viết công thức ra giấy**: ai làm cũng ra cùng một cái bánh,
> sai thì sửa công thức chứ không đổ lỗi cho người nấu, và **năm sau mở ra vẫn biết hồi đó làm gì.**

⭐ Ba thứ đó là: **nhất quán** (mọi thiết bị giống nhau) · **kiểm chứng được** (biết ai đổi gì, lúc nào) ·
**lặp lại được** (làm lại lần thứ 100 vẫn đúng như lần đầu).

### 2.2 API là gì — người bồi bàn

Bạn vào nhà hàng. Bạn **không đi thẳng xuống bếp** tự lấy đồ ăn. Bạn:

1. Xem **menu** — biết nhà hàng có món gì, gọi bằng tên nào.
2. Nói với **bồi bàn** — "cho tôi món số 7".
3. Bồi bàn mang đồ ăn ra, **hoặc** nói "hết món rồi" / "anh chưa đặt bàn".

> 🍽️ ⭐ **API chính là người bồi bàn đó.** Bạn không cần biết bếp nấu thế nào.
> Bạn chỉ cần biết **gọi món ra sao** (endpoint + verb) và **hiểu câu trả lời** (mã trạng thái + payload).

⭐ **Điều này giải thích vì sao đề chỉ bắt bạn "Interpret":**
người gọi món không cần biết nấu — nhưng **phải hiểu khi bồi bàn nói "hết món"**.

Và câu trả lời có hai phần luôn đi cùng nhau:

- ⭐ **Mã trạng thái** — *"được hay không được, và không được thì vì sao"* (200, 401, 404…).
- ⭐ **Payload** — *"đây là hàng của anh"* (nội dung JSON/XML trả về).

🔴  **Người mới hay chỉ nhìn payload mà bỏ qua mã trạng thái** — rồi ngồi đọc một payload rỗng
mà không hiểu vì sao, trong khi mã đã nói rõ `401` từ đầu.

### 2.3 JSON · XML · YAML — ba cách viết CÙNG MỘT thứ

Ba định dạng này **không phải ba công nghệ khác nhau**. Chúng là **ba lối viết** của cùng một nội dung —
giống như viết cùng một địa chỉ theo ba kiểu:

> 📮 **Ví von — ghi địa chỉ lên phong bì.**
> - **JSON** = ghi có **dấu ngoặc rõ ràng**: `{tên: Hiệp, số nhà: 12}` — máy đọc nhanh, người đọc được.
> - **XML** = ghi kiểu **có thẻ mở và thẻ đóng**: `<tên>Hiệp</tên>` — dài dòng nhưng chặt chẽ, khó nhầm.
> - **YAML** = ghi kiểu **thụt đầu dòng như dàn ý**: người đọc dễ nhất, nhưng **lệch một dấu cách là hỏng**.

⭐ **Quy tắc nhớ ai dùng cái nào:**

| Định dạng | Ai dùng nó | Dấu hiệu nhận ra trong 1 giây |
|---|---|---|
| **JSON** | ⭐ **REST API, RESTCONF** | `{` và `[` |
| **XML** | ⭐ **NETCONF** *(bắt buộc)* | `<thẻ>…</thẻ>` |
| **YAML** | ⭐ **Ansible playbook** | Thụt đầu dòng + dấu `-` đầu dòng |

🔴  **Cái bẫy của cả ba:** chúng đều **rất kén dấu**. Thừa một dấu phẩy trong JSON,
thiếu một thẻ đóng trong XML, dùng **Tab thay dấu cách** trong YAML — **đều hỏng toàn bộ file**,
chứ không phải hỏng một dòng. Đề rất thích cho bạn một file sai một ký tự rồi hỏi "sai ở đâu".

### 2.4 YANG là gì — tờ khai có sẵn ô trống

Đây là khái niệm người mới thấy mơ hồ nhất. Bỏ hết chữ "data modeling language" đi đã.

> 📋 ⭐ **Ví von — tờ khai xuất nhập cảnh.**
> Tờ khai in sẵn quy định: ô "Họ tên" là **chữ**, ô "Ngày sinh" là **ngày**, ô "Quốc tịch" **bắt buộc điền**,
> ô "Số hộ chiếu" **chỉ được 1 giá trị**, ô "Nước đã đi qua" **được điền nhiều dòng**.
>
> ⭐ **YANG chính là cái TỜ KHAI đó** — nó mô tả **thiết bị có những ô gì, mỗi ô kiểu dữ liệu nào,
> ô nào bắt buộc, ô nào lặp được.**
> ⭐ **NETCONF và RESTCONF chỉ là CÁCH BẠN GỬI tờ khai đi** — gửi qua bưu điện hay gửi qua email.

⭐ **Câu chốt phải nhớ:** **YANG là KHUÔN của dữ liệu. NETCONF/RESTCONF là ĐƯỜNG VẬN CHUYỂN.**
⭐ Hai thứ khác hẳn nhau, và đề hay cố tình làm bạn lẫn.

⭐ **Vì sao cần khuôn?** Vì trước YANG, mỗi hãng — thậm chí mỗi dòng máy — trả lời một kiểu.
Script viết cho Cisco không chạy được với hãng khác. Có khuôn chung thì **một script dùng được cho nhiều nơi**.

### 2.5 NETCONF vs RESTCONF — thư bảo đảm và bưu thiếp

Cả hai đều dùng để nói chuyện với thiết bị. Khác nhau ở **mức độ cẩn thận**.

> ✉️ ⭐ **Ví von — gửi thư.**
>
> **NETCONF = thư bảo đảm có ký nhận.**
> Bạn **khoá hòm thư lại** (`lock`) để không ai chen ngang, **viết nháp** vào bản nháp (`candidate`),
> đọc lại, rồi mới **ký xác nhận gửi** (`commit`). ⭐ **Thấy sai trước khi ký → xé nháp, không ai biết.**
> ⭐ **Và nếu gửi 5 thay đổi mà cái thứ 3 sai → CẢ 5 CÙNG BỊ HUỶ**, không có chuyện nửa vời.
>
> **RESTCONF = bưu thiếp.**
> Viết xong **thả vào thùng thư là đi luôn.** Nhanh, tiện, ai cũng gửi được.
> 🔴 **Nhưng viết sai thì… nó đã đi rồi.** Không có bản nháp, không có nút hoàn tác.

⭐ **Đây là điểm khác biệt quan trọng nhất giữa hai giao thức, và là câu hỏi đề hay ra nhất:**
⭐ **chỉ NETCONF có `candidate` datastore, có `commit`, có `rollback`, và có tính "toàn bộ hoặc không gì cả".**

⭐ **Suy ra cách chọn trong thực tế:**

| Tình huống | Dùng | Vì sao |
|---|---|---|
| ⭐ **Đổi cấu hình phức tạp** trên router lõi lúc 2h sáng | **NETCONF** | Sai còn rollback được |
| ⭐ **Đọc trạng thái** để vẽ dashboard | **RESTCONF** | Nhanh, JSON, script nào cũng gọi được |

### 2.6 EEM là gì — người trực đêm

Mọi thứ ở trên đều cần **một cái máy khác** đứng ngoài ra lệnh vào. Nếu 2 giờ sáng
đường truyền chập chờn mà không ai thức thì sao?

> 🌙 ⭐ **Ví von — bác bảo vệ trực đêm.**
> Bạn dặn bác: *"Hễ NGHE thấy chuông cửa (**event**) thì BẬT đèn và GỌI cho tôi (**action**)."*
> Rồi bạn đi ngủ. ⭐ **Bác ở ngay trong toà nhà — không cần ai điều khiển từ xa, không cần mạng còn sống.**

⭐ **EEM = `event` (khi nào làm) + `action` (làm gì).** Chỉ có thế. Nó **chạy ngay trên thiết bị**.

⭐ **Đây là điểm mạnh riêng của EEM mà script bên ngoài không có:**
⭐ **khi mạng đứt, script ở xa không SSH vào được nữa — nhưng EEM vẫn chạy**, vì nó đã ở sẵn bên trong.

⭐ Chuông cửa có thể là: **một dòng syslog** · **ai đó gõ một lệnh** · **đến giờ hẹn** ·
**một cổng vừa down** · **bạn gọi tay**.

### 2.7 Agent vs agentless — nhân viên thường trú hay thợ gọi đến

Khi quản lý hàng trăm máy, có hai trường phái:

> 🏠 ⭐ **Ví von — sửa nhà.**
>
> **Agent (Puppet, Chef)** = ⭐ **thuê một nhân viên SỐNG LUÔN trong nhà.**
> Anh ta **tự đi hỏi trung tâm** *"hôm nay có việc gì cho tôi không?"* rồi tự làm.
> ⭐ Ưu: nhà nào cũng có người túc trực, tự sửa khi lệch chuẩn.
> 🔴 Nhược:  **phải CÀI được người đó vào nhà đã.**
>
> **Agentless (Ansible, SaltStack chế độ SSH)** = ⭐ **gọi thợ đến khi cần.**
> Thợ gõ cửa (SSH/API), làm xong thì về. ⭐ Không cần cài gì trong nhà.

🔴  **Và đây là lý do quyết định trong ngành mạng:**
⭐ **bạn KHÔNG cài được phần mềm lạ lên switch/router Cisco.** Nó là hệ đóng.
⭐ **Nên trong mạng, agentless — cụ thể là Ansible — gần như luôn thắng.**

⭐ Puppet/Chef mạnh ở **server Linux** (nơi cài agent thoải mái), nên bạn vẫn gặp chúng —
nhưng ở mảng server, không phải mảng thiết bị mạng.

---

> ✅ **Hết Phần 1.** Nếu bạn nói lại được **7 ví von** trên bằng lời của mình
> (100 con switch · bồi bàn · phong bì · tờ khai · thư bảo đảm vs bưu thiếp · bác bảo vệ · thuê thợ)
> thì **đã nắm đủ khung để sang Phần 2**. Chưa được thì đọc lại — đừng sang vội.

---

## ⚙️ PHẦN 2 — NÓ CHẠY THẾ NÀO

---

## 📘 3. 🔴  JSON (blueprint 6.2 — CONSTRUCT)

> 🔗 Ví von ở **§2.3** — "ghi địa chỉ lên phong bì". Đọc lại nếu chưa rõ.
>
> 🔴  Động từ blueprint là **CONSTRUCT** — nghĩa là đề sẽ cho bạn **file JSON sai**
> và hỏi **sai ở đâu**, hoặc bắt bạn **chọn file nào đúng**. Phần này phải thuộc.

### 3.1 Hai cấu trúc, sáu kiểu giá trị — hết

⭐ **JSON chỉ có HAI cấu trúc:**

| Ký hiệu | Tên | Nghĩa | Truy cập bằng |
|:---:|---|---|---|
| `{ }` | **Object** | Tập hợp **cặp key–value**, không thứ tự | ⭐ **Tên key** |
| `[ ]` | **Array** | Danh sách **có thứ tự** | ⭐ **Số thứ tự, đếm từ 0** |

⭐ **Và chỉ SÁU kiểu giá trị:**

| Kiểu | Ví dụ hợp lệ | 🔴 Ví dụ SAI |
|---|---|---|
| **String** | `"Gi0/0"` | `'Gi0/0'` ← 🔴 **nháy đơn KHÔNG hợp lệ** |
| **Number** | `1500` · `-3` · `2.5` · `1e3` | `+5` · `007` ← 🔴 không được dấu `+`, không số 0 đứng đầu |
| **Boolean** | `true` · `false` | `True` · `TRUE` ← 🔴 **phải viết thường** |
| **Null** | `null` | `NULL` · `nil` · `None` ← 🔴 |
| **Object** | `{"a": 1}` | — |
| **Array** | `[1, 2, 3]` | — |

> 🔴  **Key LUÔN là string và LUÔN phải trong nháy kép.**
> `{"name": "R1"}` ✅ · `{name: "R1"}` 🔴 SAI · `{'name': 'R1'}` 🔴 SAI
>
> ⭐ Chỗ này khác Python.  **Trong Python `{'a': 1}` chạy được, trong JSON thì KHÔNG.**
> Đây là bẫy hay nhất vì hai thứ trông rất giống nhau.

### 3.2 🔴  Bốn lỗi JSON đề hay cho

```json
{
  "device": "R1",
  "interfaces": [
    {
      "name": "GigabitEthernet0/0",
      "enabled": true,
      "mtu": 1500,
      "description": null
    },
    {
      "name": "GigabitEthernet0/1",
      "enabled": false,
      "mtu": 9000,
      "description": "Uplink"
    }
  ]
}
```

⭐ **Đó là file ĐÚNG.** Giờ là bốn cách làm nó sai:

| # | Lỗi | Trông thế nào | Vì sao sai |
|:---:|---|---|---|
| 1 | 🔴  **Dấu phẩy thừa** | `"mtu": 1500,` rồi `}` ngay sau | **Phần tử CUỐI không được có dấu phẩy** |
| 2 | 🔴  **Thêm comment** | `// đây là uplink` hoặc `# ...` | **JSON KHÔNG có comment.** Một dòng comment là hỏng cả file |
| 3 | 🔴  **Nháy đơn** | `'name': 'R1'` | JSON chỉ chấp nhận **nháy kép** |
| 4 | 🔴  **Lệch ngoặc** | `[` mở mà đóng bằng `}` | `{` khép bằng `}`, `[` khép bằng `]` |

> 💡 ⭐ **Mẹo chấm nhanh trong phòng thi:**  **đếm ngoặc từ trong ra ngoài**, và
> ⭐ **nhìn dấu phẩy ngay TRƯỚC mỗi dấu `}` hoặc `]`** — hai chỗ này gom gần hết lỗi.

### 3.3 ⭐ Lấy giá trị lồng nhau — dạng câu hỏi kinh điển

> ❓ **Đề hỏi:** *Với payload ở §3.2, `interfaces[1]["mtu"]` bằng bao nhiêu?*

⭐ **Cách đọc — đi từng bước, đừng nhảy cóc:**

```
interfaces          → lấy mảng [ ... ]         (2 phần tử)
interfaces[1]       → phần tử THỨ HAI          ← 🔴 đếm từ 0!
                      = { "name": "GigabitEthernet0/1", ... }
interfaces[1]["mtu"] → 9000 ✅
```

🔴  **Bẫy số một của cả domain 6.0: mảng đếm từ 0.**
⭐ `[0]` là phần tử **đầu tiên**, `[1]` là phần tử **thứ hai**.
⭐ Đề cố tình cho mảng 2–3 phần tử để bạn nhầm một bậc.

---

## 📘 4. ⭐ XML và YAML — đọc được là đủ

> ⭐ Blueprint chỉ bắt *construct* **JSON**. XML và YAML thì **cần đọc được**,
> vì ⭐ **NETCONF bắt buộc XML** và  **Ansible bắt buộc YAML**.

### 4.1 XML — cái gì mở thì phải đóng

```xml
<interface>
  <name>GigabitEthernet0/0</name>
  <enabled>true</enabled>
  <mtu>1500</mtu>
</interface>
```

| Quy tắc | Chi tiết |
|---|---|
| **Đúng MỘT thẻ gốc** | Cả file bọc trong 1 thẻ ngoài cùng. Hai thẻ gốc = 🔴 sai |
| ⭐ **Mọi thẻ phải đóng** | `<mtu>1500</mtu>` hoặc thẻ rỗng `<shutdown/>` |
| 🔴  **Phân biệt HOA–thường** | `<Name>` và `<name>` là **hai thẻ khác nhau** |
| **Lồng phải đúng thứ tự** | `<a><b></b></a>` ✅ · `<a><b></a></b>` 🔴 |
| ⭐ **Namespace `xmlns`** | Cho biết thẻ này thuộc **model YANG nào** — gặp nhiều ở NETCONF |

> ⭐ **Vì sao NETCONF chọn XML mà không chọn JSON?** Vì XML có **namespace** và
> ⭐ **cấu trúc chặt hơn** — hợp với thứ cần chính xác tuyệt đối như đổi cấu hình.

### 4.2 YAML — dấu cách là cú pháp

```yaml
---
- name: Them VLAN 20 vao switch
  hosts: switches
  gather_facts: false
  tasks:
    - name: Tao VLAN
      cisco.ios.ios_config:
        lines:
          - vlan 20
          - name KE-TOAN
```

| Quy tắc | Chi tiết |
|---|---|
| 🔴  **CHỈ dùng dấu cách, TUYỆT ĐỐI không Tab** | **Lỗi số 1 của người mới.** Editor hiện Tab giống dấu cách → nhìn không ra |
| ⭐ **Thụt lề = cấp bậc** | Thụt sâu hơn nghĩa là "nằm trong". Lệch 1 dấu cách là đổi ý nghĩa |
| **`key: value`** | **Phải có dấu cách SAU dấu hai chấm.** `key:value` 🔴 sai |
| ⭐ **`-` đầu dòng = phần tử danh sách** | Giống `[ ]` của JSON |
| ⭐ **`#` là comment** | **YAML CÓ comment** — khác hẳn JSON |
| ⭐ **`---`** | Đánh dấu bắt đầu một tài liệu |

> 🔴  **Câu hỏi đề hay ra:** *"Định dạng nào cho phép comment?"*
> → ⭐ **YAML có (`#`), XML có (`<!-- -->`), JSON KHÔNG CÓ.**

### 4.3 ⭐ Bảng so sánh — học thuộc bảng này là xong §3–§4

| | **JSON** | **XML** | **YAML** |
|---|---|---|---|
| **Nhận ra bằng** | `{ }` `[ ]` | `<thẻ></thẻ>` | Thụt lề + `-` |
| ⭐ **Ai dùng** | **REST / RESTCONF** | **NETCONF** | **Ansible** |
| **Comment** | 🔴 **KHÔNG** | ✅ `<!-- -->` | ✅ `#` |
| **Phân biệt hoa thường** | ✅ | ✅ | ✅ |
| **Nhạy dấu cách** | Không | Không | 🔴  **CỰC KỲ** |
| **Người đọc dễ** | Khá | Khó nhất | ⭐ **Dễ nhất** |
| **Máy đọc gọn** | ⭐ **Gọn nhất** | Cồng kềnh | Khá |

---

## 📘 5. 🔴  REST API (blueprint 6.5 — INTERPRET)

> 🔗 Ví von ở **§2.2** — "người bồi bàn".
>
> 🔴  **Đây là mục ăn điểm nhiều nhất domain 6.0.** Nó không cần lab, không cần thiết bị —
> chỉ cần thuộc bảng. ⭐ **Học chắc §5 là gần như chắc chắn có điểm.**

### 5.1 ⭐ Năm động từ — và câu hỏi "idempotent"

| Verb | Làm gì | ⭐ **Idempotent?** | Gọi 10 lần thì sao |
|---|---|:---:|---|
| ⭐ **GET** | **Đọc** | ✅ **Có** | Đọc 10 lần, không đổi gì |
| 🔴 **POST** | **Tạo mới** | 🔴 **KHÔNG** | **Tạo ra 10 thứ!** |
| ⭐ **PUT** | **Thay thế TOÀN BỘ** | ✅ **Có** | Ghi đè 10 lần, kết quả như 1 lần |
| 🔴 **PATCH** | **Sửa MỘT PHẦN** | 🔴 **Không** *(theo chuẩn)* | Tuỳ nội dung sửa |
| ⭐ **DELETE** | **Xoá** | ✅ **Có** | Lần đầu xoá, các lần sau "vốn đã không còn" |

> 🔴  **"Idempotent" nghĩa là: LÀM 1 LẦN hay LÀM 10 LẦN thì kết quả CUỐI CÙNG giống nhau.**
>
> 🚪 ⭐ **Ví von — cái công tắc và cái chuông.**
> ⭐ **PUT giống GẠT công tắc sang "BẬT"** — gạt 10 lần thì đèn vẫn chỉ đang bật. ✅ Idempotent.
> 🔴 **POST giống BẤM chuông** — bấm 10 lần thì chuông kêu 10 lần. Không idempotent.

⭐ **Vì sao đề quan tâm?** Vì  **script bị lỗi mạng rồi chạy lại là chuyện thường.**
 Chạy lại một `PUT` thì an toàn. 🔴 **Chạy lại một `POST` có thể tạo ra bản ghi trùng.**

⭐ **Phân biệt PUT và PATCH** — đề hay hỏi:

| | **PUT** | **PATCH** |
|---|---|---|
| Nghĩa | ⭐ **Thay cả cái** | **Sửa vài chỗ** |
| Gửi lên | ⭐ **TOÀN BỘ** đối tượng | **Chỉ phần muốn đổi** |
| 🔴 Rủi ro | **Trường nào không gửi có thể bị XOÁ/về mặc định** | An toàn hơn |

### 5.2 🔴  Mã trạng thái — bảng phải thuộc lòng

⭐ **Nhớ theo NHÓM trước, nhớ số sau:**

```
   1xx  →  "Đang xử lý…"          (hiếm gặp trong đề)
   2xx  →  ✅ THÀNH CÔNG
   3xx  →  ↪️  Chuyển hướng đi chỗ khác
   4xx  →  🔴 LỖI CỦA BẠN        ← bạn gọi sai
   5xx  →  🔴 LỖI CỦA SERVER     ← bạn gọi đúng, nó tự hỏng
```

> ⭐ **Câu thần chú:**  **4 = lỗi của TÔI · 5 = lỗi của NÓ.**
> ⭐ Chỉ cần nhớ mỗi câu này là đã trả lời được kha khá câu hỏi.

| Mã | Tên | ⭐ Nghĩa thực tế |
|:---:|---|---|
| ⭐ **200** | OK | **Thành công, và CÓ dữ liệu trả về** |
| ⭐ **201** | Created | **Đã TẠO xong** — thường là kết quả của `POST` |
| **202** | Accepted | ⭐ **Đã nhận việc nhưng CHƯA làm xong** — hay gặp ở DNAC *(xem §10)* |
| ⭐ **204** | No Content | **Thành công nhưng KHÔNG có gì trả về** — thường sau `DELETE` |
| ⭐ **400** | Bad Request | **Payload sai cú pháp** — JSON hỏng, thiếu trường |
| 🔴  **401** | Unauthorized | 🔴  **CHƯA đăng nhập / token SAI / token HẾT HẠN** |
| 🔴  **403** | Forbidden | 🔴  **ĐÃ đăng nhập rồi, nhưng KHÔNG ĐỦ QUYỀN** |
| ⭐ **404** | Not Found | **Sai đường dẫn (URL)** hoặc vật cần tìm không tồn tại |
| **405** | Method Not Allowed | ⭐ Đúng URL nhưng **sai verb** *(ví dụ `DELETE` vào chỗ chỉ cho `GET`)* |
| **409** | Conflict | Xung đột — ví dụ tạo cái đã tồn tại |
| **415** | Unsupported Media Type | 🔴  **Sai header `Content-Type`** |
| **429** | Too Many Requests | Gọi quá nhanh, bị chặn tốc độ |
| ⭐ **500** | Internal Server Error | **Server tự hỏng** — không phải lỗi bạn |
| **503** | Service Unavailable | Server quá tải / đang bảo trì |

> 🔴  **BẪY KINH ĐIỂN NHẤT — phân biệt 401 và 403.**
>
> 🎫 ⭐ **Ví von — vào rạp phim.**
> ⭐ **401** = *"Vé của anh đâu?"* →  **bạn chưa đưa vé, hoặc vé giả, hoặc vé hết hạn.**
> ⭐ **403** = *"Vé thật, mời vào. Nhưng phòng VIP thì anh không được vào."*
> → ⭐ **danh tính OK, nhưng quyền không đủ.**
>
> ⭐ **Chốt:**  **401 = vấn đề DANH TÍNH · 403 = vấn đề QUYỀN HẠN.**
> ⭐ Thấy `401` → đi kiểm tra **token**. Thấy `403` → đi kiểm tra **role của user**.

### 5.3 ⭐ Header — hai cái hay bị lẫn

| Header | Nghĩa | ⭐ Nhớ bằng |
|---|---|---|
| ⭐ **`Content-Type`** | **Định dạng thứ TÔI ĐANG GỬI ĐI** | *"Hàng tôi gửi được gói thế này"* |
| ⭐ **`Accept`** | **Định dạng tôi MUỐN NHẬN VỀ** | *"Xin trả lời tôi bằng kiểu này"* |
| **`Authorization`** | Thông tin xác thực *(Basic / Bearer)* | — |
| **`X-Auth-Token`** | ⭐ **Token riêng của DNA Center** | Xem §10 |

> 🔴  **Sai `Content-Type` → `415 Unsupported Media Type`.**
> ⭐ Với RESTCONF, giá trị đúng là  **`application/yang-data+json`** *(hoặc `…+xml`)* —
> ⭐ **không phải `application/json` thuần**. Đây là chỗ người mới hay bị chặn ngay bước đầu.

### 5.4 ⭐ Mổ xẻ một URL RESTCONF

```
https://10.10.20.48:443/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1
└─┬──┘ └────┬─────┘└┬┘└───┬────┘└─┬─┘└────────┬─────────┘└──────────┬──────────────┘
  │         │       │     │       │           │                     │
  │         │       │     │       │           │                     └─ khoá của list
  │         │       │     │       │           └─ tên MODULE YANG : CONTAINER
  │         │       │     │       └─ "data" = dữ liệu · "operations" = gọi RPC
  │         │       │     └─ gốc RESTCONF (cố định)
  │         │       └─ cổng 443
  │         └─ IP thiết bị
  └─ 🔴 LUÔN là https — RESTCONF KHÔNG chạy trên http thường
```

| Thành phần | Ý nghĩa |
|---|---|
| ⭐ **`/restconf/data/`** | **Truy cập DỮ LIỆU** (config + trạng thái) |
| **`/restconf/operations/`** | Gọi **hành động (RPC)** do model định nghĩa |
| ⭐ **`ietf-interfaces:interfaces`** | **Trước dấu `:` là tên MODULE YANG**, sau là container |
| ⭐ **`interface=GigabitEthernet1`** | **Chọn đúng MỘT phần tử trong list bằng khoá của nó** |

---

## 📘 6. 🟡 ⭐ YANG (blueprint 6.3 — DESCRIBE)

> 🔗 Ví von ở **§2.4** — "tờ khai có sẵn ô trống".
>
> 🟡 Động từ là **Describe** — ⭐ **bạn KHÔNG phải viết model YANG.** Chỉ cần hiểu nó là gì,
> có mấy loại node, và có mấy dòng model.

### 6.1 ⭐ Bốn loại node — đủ để đọc mọi model

| Node | Là gì | ⭐ Ví von với tờ khai | Ví dụ |
|---|---|---|---|
| ⭐ **leaf** | **Một ô, một giá trị** | Ô "Ngày sinh" | `mtu = 1500` |
| **leaf-list** | **Một ô, NHIỀU giá trị cùng kiểu** | Ô "Các nước đã đi qua" | danh sách DNS server |
| ⭐ **container** | **Một NHÓM ô** — bản thân nó không có giá trị | Khung "Thông tin cá nhân" | `interfaces` |
| 🔴  **list** | **Nhiều BẢN GHI, mỗi bản có KHOÁ riêng** | Mỗi người khai một tờ | `interface` *(khoá = `name`)* |

> ⭐ **Phân biệt `container` và `list` — đề hay hỏi:**
> ⭐ **`container` xuất hiện ĐÚNG MỘT LẦN.**  **`list` xuất hiện NHIỀU LẦN và phải có KHOÁ để phân biệt.**
>
> ⭐ Đó chính là lý do URL RESTCONF ở §5.4 viết `interface=GigabitEthernet1` —
> ⭐ **`interface` là một `list`, nên phải chỉ rõ khoá thì mới biết lấy cái nào.**

### 6.2 ⭐ Ba dòng model — bảng phải nhớ

| Dòng | Ai làm | Ưu | Nhược |
|---|---|---|---|
| **Native** *(`Cisco-IOS-XE-native`)* | **Riêng Cisco** | **Phủ gần như MỌI tính năng** của thiết bị | 🔴 **Chỉ chạy với Cisco** — đổi hãng là viết lại |
| ⭐ **IETF** *(`ietf-interfaces`)* | Tổ chức chuẩn IETF | **Chuẩn mở, nhiều hãng theo** | **Chỉ phủ phần CHUNG nhất** — thiếu tính năng riêng |
| ⭐ **OpenConfig** | **Liên minh các nhà mạng lớn** | **Trung lập hãng, thiết kế theo nhu cầu vận hành thật** | Không phải thiết bị nào cũng hỗ trợ đủ |

> ⭐ **Đánh đổi phải hiểu:**  **model càng CHUẨN CHUNG thì càng ÍT tính năng riêng.**
> ⭐ Muốn dùng một tính năng đặc thù của Cisco → **buộc phải dùng native model**, và
> ⭐ **chấp nhận script đó không chạy được với hãng khác.**

### 6.3 ⭐ Lợi ích — câu trả lời cho "benefits" trong blueprint

| Lợi ích | Nghĩa thực tế |
|---|---|
| ⭐ **Có cấu trúc** | Máy đọc được **chắc chắn**, không phải đoán như khi bóc chữ từ `show` |
| ⭐ **Kiểm tra được trước khi gửi** | Sai kiểu dữ liệu → **bị chặn ngay**, không phải chờ thiết bị báo lỗi |
| ⭐ **Trung lập hãng** *(với IETF/OpenConfig)* | Một script dùng cho nhiều hãng |
| ⭐ **Tự mô tả** | Model nói rõ có ô nào, kiểu gì → công cụ tự sinh code được |

> 🔴  **Vì sao điều này quan trọng — đối chiếu với cách CŨ:**
> ⭐ Trước YANG, script phải chạy `show interfaces` rồi **cắt chuỗi văn bản** để lấy số.
> 🔴  **Chỉ cần Cisco đổi một dấu cách trong output là script chết.**
> ⭐ Cách đó gọi là **"screen scraping"** — và YANG sinh ra để xoá bỏ nó.

---

## 📘 7. 🔴  NETCONF & RESTCONF (blueprint 4.7 — CONFIGURE AND VERIFY)

> 🔗 Ví von ở **§2.5** — "thư bảo đảm và bưu thiếp".
>
> 🔴  **Đây là mục KHÉP LẠI Domain 4.0** *(xem §0.2)*. Động từ là **Configure and verify** —
> ⭐ **phải bật được và kiểm chứng được**, không chỉ đọc.
>
> 🔴  **Nhắc lại §1.2: vIOS trong EVE-NG KHÔNG có hai lệnh này.** Dùng **DevNet Sandbox**.

### 7.1 ⭐ Bảng so sánh — câu hỏi ra nhiều nhất

| | ⭐ **NETCONF** | **RESTCONF** |
|---|---|---|
| 🔴  **Vận chuyển / cổng** | 🔴  **SSH — cổng 830** | 🔴  **HTTPS — cổng 443** |
| ⭐ **Định dạng** | **CHỈ XML** | **JSON hoặc XML** |
| ⭐ **Kiểu thao tác** | **RPC** — `<get-config>`, `<edit-config>` | **HTTP verb** — GET/POST/PUT/PATCH/DELETE |
| 🔴  **Datastore** | 🔴  **`running` · `candidate` · `startup`** | **Chủ yếu `running`** |
| 🔴  **Giao dịch (commit/rollback)** | 🔴  **CÓ — toàn bộ hoặc không gì cả** | 🔴 **KHÔNG** |
| **Khoá thiết bị khi sửa** | **CÓ — `<lock>`** | 🔴 **Không** |
| ⭐ **Đổi nhiều thứ một lượt** | **CÓ** | **Mỗi lần gọi một thứ** |
| ⭐ **Mô hình dữ liệu** | **YANG** | **YANG** *(giống nhau!)* |
| ⭐ **Hợp với** | **Đổi cấu hình phức tạp, cần an toàn** | **Đọc trạng thái, tích hợp nhanh** |
| ⭐ **Định nghĩa ở** | RFC 6241 | RFC 8040 |

> ⭐ **Ba câu chốt cho phòng thi:**
> ⭐ **1. NETCONF = SSH 830 · RESTCONF = HTTPS 443.**
> ⭐ **2. Cả hai đều dùng YANG** — khác nhau ở *cách chở*, không phải ở *khuôn dữ liệu*.
> ⭐ **3. Chỉ NETCONF có candidate + commit + rollback + lock.**

### 7.2 ⭐ Bốn tầng của NETCONF

```
   ┌──────────────────────────────────────────────┐
   │ ④ CONTENT      — dữ liệu, theo khuôn YANG    │  "gửi CÁI GÌ"
   ├──────────────────────────────────────────────┤
   │ ③ OPERATIONS   — <get-config> <edit-config>  │  "LÀM GÌ với nó"
   ├──────────────────────────────────────────────┤
   │ ② MESSAGES     — <rpc> <rpc-reply>           │  "gói tin bọc ngoài"
   ├──────────────────────────────────────────────┤
   │ ① TRANSPORT    — 🔴 SSH cổng 830             │  "chở bằng gì"
   └──────────────────────────────────────────────┘
```

⭐ **Các thao tác chính:**

| RPC | Làm gì |
|---|---|
| ⭐ **`<get>`** | Lấy **cấu hình + trạng thái đang chạy** |
| ⭐ **`<get-config>`** | **Chỉ lấy CẤU HÌNH** — nói rõ lấy từ datastore nào |
| 🔴  **`<edit-config>`** | **Sửa cấu hình** *(merge / replace / create / delete)* |
| ⭐ **`<lock>` / `<unlock>`** | **Khoá datastore** để không ai chen ngang |
| 🔴  **`<commit>`** | **Chốt thay đổi từ `candidate` sang `running`** |
| ⭐ **`<discard-changes>`** | **Xé bản nháp** — bỏ mọi thứ chưa commit |
| ⭐ **`<validate>`** | **Kiểm tra trước khi commit** |
| **`<close-session>`** | Đóng phiên của mình |

### 7.3 🔴  Ba datastore — hiểu chỗ này là hiểu vì sao NETCONF an toàn hơn

```
   ┌─────────────┐   edit-config    ┌─────────────┐   commit    ┌────────────┐
   │   Bạn gõ    │ ───────────────▶ │  CANDIDATE  │ ──────────▶ │  RUNNING   │
   │             │                  │  (bản nháp) │             │(đang chạy) │
   └─────────────┘                  └─────────────┘             └─────┬──────┘
                                           │                          │
                                    discard-changes             copy-config
                                       (xé nháp)                      ▼
                                                                ┌────────────┐
                                                                │  STARTUP   │
                                                                │(khởi động) │
                                                                └────────────┘
```

| Datastore | Là gì | ⭐ Tương đương trên IOS |
|---|---|---|
| ⭐ **`running`** | **Cấu hình ĐANG chạy** | `running-config` |
| 🔴  **`candidate`** | 🔴  **BẢN NHÁP — sửa ở đây KHÔNG ảnh hưởng gì cho tới khi `commit`** | **IOS không có thứ tương đương!** |
| ⭐ **`startup`** | Cấu hình dùng khi khởi động lại | `startup-config` |

> 🔴  **`candidate` chính là thứ IOS cổ điển KHÔNG CÓ, và là lý do NETCONF đáng dùng.**
> ⭐ Trên CLI, bạn gõ `shutdown` là cổng **tắt ngay lập tức**.
> ⭐ Với `candidate`, bạn soạn xong 20 dòng, **đọc lại**, rồi mới `commit` —  **và nếu dòng thứ 15 sai,
> CẢ 20 DÒNG cùng bị huỷ.** Không có chuyện cấu hình dở dang.
>
> ⚠️ ⭐ **Lưu ý thực tế:**  **không phải nền tảng nào cũng bật sẵn `candidate`.**
> ⭐ Thiết bị công bố khả năng của nó trong bản tin `<hello>` lúc mở phiên —
> ⭐ **cứ xem `<hello>` là biết máy đó hỗ trợ gì.**

---

### 7.4 🔴  CẤU HÌNH — bật hai giao thức

```
! ═══ ĐIỀU KIỆN TIÊN QUYẾT: phải có AAA, thiếu là NETCONF từ chối đăng nhập ═══
aaa new-model
aaa authentication login default local
aaa authorization exec default local          ! ⚠️ THIẾU DÒNG NÀY là lỗi hay gặp nhất
!
username admin privilege 15 algorithm-type scrypt secret MatKhauRatDai
!
! ═══ NETCONF — chỉ MỘT dòng ═══
netconf-yang
!
! ═══ RESTCONF — cần HTTPS ═══
ip http secure-server                          ! ⚠️ RESTCONF KHÔNG chạy trên http thường
restconf
```

> 🔴  **Bẫy số 1 khi bật NETCONF/RESTCONF trên IOS-XE:**
> ⭐ **hai giao thức này xác thực QUA AAA.**  **Thiếu `aaa authorization exec default local`
> thì bạn SSH vào bình thường vẫn được, nhưng NETCONF/RESTCONF trả về lỗi xác thực** —
> và thông báo lỗi **không hề nhắc gì tới AAA**. ⭐ **Rất khó đoán nếu không biết trước.**
>
> ⚠️ ⭐ **Bẫy số 2:** sau khi gõ `netconf-yang`, các tiến trình nền cần  **vài chục giây đến 1–2 phút**
> mới lên hết. ⭐ **Thử kết nối ngay sẽ thất bại.** Chờ rồi kiểm tra bằng §7.5.

### 7.5 ⭐ KIỂM CHỨNG — verify

```
! ─── Các tiến trình nền đã chạy chưa? ───
show platform software yang-management process

! Mong đợi các tiến trình ở trạng thái Running, đặc biệt:
!   confd     : Running      ← lõi xử lý NETCONF/RESTCONF
!   ncsshd    : Running      ← 🔴 daemon SSH riêng cho NETCONF (cổng 830)
!   dmiauthd  : Running      ← 🔴 xác thực — nếu DỪNG thì AAA đang có vấn đề
!   nesd / syncfd / ndbmand : Running

! ─── Ai đang kết nối NETCONF? ───
show netconf-yang sessions

! ─── Thiết bị hỗ trợ datastore nào? ───
show netconf-yang datastores
```

> ⭐ **Cách kiểm chứng nhanh nhất mà không cần viết script** — gõ từ **máy bạn**, không phải trên router:
>
> ```
> ssh -p 830 admin@<ip-thiet-bi> -s netconf
> ```
>
> ⭐ Nếu thiết bị trả về một khối XML `<hello>` liệt kê **capabilities** thì
> ⭐ **NETCONF đã chạy đúng** — và  **chính khối đó cho bạn biết máy này có hỗ trợ `candidate` hay không.**

---

### 7.6 ⭐ Gọi RESTCONF bằng `curl` — đọc hiểu là đủ

```bash
# ĐỌC thông tin một interface  (GET)
curl -k -u admin:MatKhauRatDai \
     -H "Accept: application/yang-data+json" \
     https://DIA-CHI-IP/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1

# ĐỔI mô tả interface  (PATCH — chỉ sửa đúng phần gửi lên)
curl -k -u admin:MatKhauRatDai -X PATCH \
     -H "Content-Type: application/yang-data+json" \
     -d @payload.json \
     https://DIA-CHI-IP/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1
```

⭐ Nội dung `payload.json`:

```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet1",
    "description": "Sua bang RESTCONF"
  }
}
```

| Cờ | Nghĩa |
|---|---|
| `-k` | ⭐ **Bỏ qua kiểm tra chứng chỉ** — thiết bị dùng chứng chỉ tự ký |
| `-u` | User:mật khẩu *(xác thực kiểu Basic)* |
| `-H` | ⭐ **Header** — chú ý `yang-data+json`, xem §5.3 |
| `-X` | Chọn **verb** |
| `-d @file` | ⭐ **Payload gửi đi**, đọc từ file |

> ⭐ **Đọc mã trả về — đây là dạng câu hỏi 6.5:**
>
> | Mã | Nghĩa trong ngữ cảnh RESTCONF |
> |:---:|---|
> | ⭐ **200** | Đọc/sửa xong, **có** nội dung trả về |
> | ⭐ **204** | Sửa xong, **không** có nội dung trả về |
> | 🔴 **401** | Sai user/mật khẩu **hoặc thiếu cấu hình AAA ở §7.4** |
> | 🔴 **404** | **Sai đường dẫn YANG** — gõ nhầm tên module/container |
> | 🔴 **415** | **Quên `yang-data+json`** trong `Content-Type` |

---

## 📘 8. 🔴  EEM — EMBEDDED EVENT MANAGER (blueprint 6.6 — CONSTRUCT)

> 🔗 Ví von ở **§2.6** — "bác bảo vệ trực đêm".
>
> 🔴  **ĐÂY LÀ MỤC QUAN TRỌNG NHẤT CỦA MODULE.** Động từ blueprint là **CONSTRUCT** —
> ⭐ **mục DUY NHẤT trong cả domain 6.0 bắt bạn TỰ VIẾT.** Đọc hiểu là không đủ.
>
> ✅ ⭐ **Tin tốt: EEM chạy tốt trên vIOS trong EVE-NG** — không cần DevNet Sandbox.
> ⭐ Dùng lại đúng lab Module-11.

### 8.1 ⭐ Bộ khung — thuộc lòng 3 dòng này là viết được mọi applet

```
event manager applet TEN-APPLET          ← ① đặt tên
 event <KHI NÀO>                          ← ② điều kiện kích hoạt  (chỉ MỘT event)
 action 1.0 <LÀM GÌ>                      ← ③ việc phải làm (nhiều action, chạy theo thứ tự)
 action 2.0 <LÀM GÌ NỮA>
```

> ⭐ **Chỉ có thế. `event` = KHI NÀO · `action` = LÀM GÌ.**
> ⭐ Mỗi applet có **đúng một `event`**, nhưng **bao nhiêu `action` cũng được**.

### 8.2 ⭐ Các loại `event` hay dùng

| Event | Kích hoạt khi | ⭐ Dùng để |
|---|---|---|
| 🔴  **`event syslog pattern "..."`** | **Có dòng syslog KHỚP mẫu** | **Phổ biến nhất.** Bắt link down, bắt neighbor rớt |
| 🔴  **`event cli pattern "..."`** | **Ai đó GÕ một lệnh khớp mẫu** | **Chặn/ghi lại lệnh nguy hiểm**, tự backup khi `write mem` |
| **`event none`** | 🔴  **Không tự chạy — chỉ chạy khi bạn gọi tay** | **Dùng để TEST applet.** Học EEM nên bắt đầu từ đây |
| ⭐ **`event timer watchdog time <giây>`** | **Cứ N giây một lần** | Thu thập dữ liệu định kỳ |
| **`event timer cron cron-entry "..."`** | Theo lịch kiểu cron | Backup lúc 2h sáng |
| ⭐ **`event interface name <if> parameter ...`** | Thông số cổng vượt ngưỡng | Cảnh báo lỗi cổng |
| **`event snmp oid ... `** | Giá trị SNMP vượt ngưỡng | Giám sát CPU/RAM |
| ⭐ **`event track <n> state ...`** | **Đối tượng `track` đổi trạng thái** | **Nối thẳng với IP SLA ở Module-03/06A** |

> ⭐ **Bắt đầu học luôn từ `event none`.**  Vì nó cho bạn **chạy applet khi nào muốn**
> bằng `event manager run <tên>` — ⭐ **không phải ngồi chờ sự kiện thật xảy ra.**
> ⭐ Viết xong, test bằng `event none`, chạy đúng rồi mới đổi sang event thật.

### 8.3 ⭐ Các `action` hay dùng

| Action | Làm gì |
|---|---|
| 🔴  **`action X cli command "..."`** | **Gõ một lệnh IOS** như thể bạn đang ngồi gõ |
| 🔴  **`action X syslog msg "..."`** | **Ghi một dòng vào syslog** — cách báo cáo đơn giản nhất |
| ⭐ **`action X wait <giây>`** | Chờ |
| ⭐ **`action X set <biến> <giá trị>`** | Đặt biến |
| ⭐ **`action X if / elseif / else / end`** | Rẽ nhánh theo điều kiện |
| **`action X while / end`** | Lặp |
| **`action X mail ...`** | Gửi email |
| **`action X snmp-trap ...`** | Bắn SNMP trap |
| ⭐ **`action X reload`** | ⚠️ **Khởi động lại thiết bị** — cẩn thận |

⭐ **Vài biến có sẵn, dùng ngay trong `action`:**

| Biến | Chứa gì |
|---|---|
| ⭐ **`$_syslog_msg`** | **Nguyên văn dòng syslog đã kích hoạt applet** |
| ⭐ **`$_cli_msg`** | **Nguyên văn lệnh mà người dùng vừa gõ** |
| **`$_event_pub_time`** | Thời điểm sự kiện xảy ra |
| **`$_cli_result`** | Kết quả của `action cli command` ngay trước đó |

---

### 8.4 ⭐ BỐN VÍ DỤ — dựng từ dễ đến khó

#### ⭐ Ví dụ 1 — applet đơn giản nhất, để hiểu bộ khung

```
event manager applet CHAO-HOI
 event none
 action 1.0 syslog msg "Xin chao tu EEM - applet da chay"
```

```
! Chạy tay:
R1# event manager run CHAO-HOI

! Xem kết quả:
R1# show logging | include Xin chao
%HA_EM-6-LOG: CHAO-HOI: Xin chao tu EEM - applet da chay
```

> ⭐ **Làm ví dụ này TRƯỚC MỌI THỨ KHÁC.**  Nó chứng minh EEM đang sống,
> và cho bạn thấy **định dạng dòng log mà EEM sinh ra** (`%HA_EM-6-LOG`).

#### ⭐ Ví dụ 2 — tự ghi log khi một cổng chết

```
event manager applet CANH-BAO-CONG-CHET
 event syslog pattern "Interface GigabitEthernet0/1, changed state to down"
 action 1.0 syslog msg "EEM: Gi0/1 vua chet - dang thu thap thong tin"
 action 2.0 cli command "enable"
 action 3.0 cli command "show interfaces GigabitEthernet0/1"
 action 4.0 syslog msg "EEM: Ket qua thu thap: $_cli_result"
```

> ⭐ **Giá trị thật:**  **lúc cổng chết lúc 3h sáng, thông tin được chụp lại NGAY khoảnh khắc đó.**
> ⭐ Sáng hôm sau bạn vào xem thì cổng đã tự lên lại, `show interface` chẳng còn dấu vết gì —
> ⭐ **nhưng EEM đã ghi hộ bạn rồi.**

#### 🔴  Ví dụ 3 — tự sao lưu mỗi khi có người lưu cấu hình

```
event manager applet BACKUP-KHI-LUU
 event cli pattern "write mem.*" sync no skip no
 action 1.0 syslog msg "EEM: co nguoi vua luu config - dang sao luu"
 action 2.0 cli command "enable"
 action 3.0 cli command "show running-config | redirect flash:backup-config.txt"
 action 4.0 syslog msg "EEM: da sao luu xong ra flash:backup-config.txt"
```

| Tham số | Nghĩa |
|---|---|
| ⭐ **`sync no`** | **Applet chạy SONG SONG**, không chặn lệnh của người dùng |
| ⭐ **`skip no`** | **Lệnh gốc VẪN được thực thi bình thường** |

> ⭐ **Đây chính là ví dụ ROADMAP nhắc tới.**  Nó giải quyết một vấn đề rất thật:
> ⭐ **ai đó sửa config rồi lưu, hôm sau mạng hỏng, không ai biết trước đó config thế nào.**

#### 🔴  Ví dụ 4 — CHẶN một lệnh nguy hiểm

```
event manager applet CHAN-RELOAD
 event cli pattern "^reload" sync yes
 action 1.0 syslog msg "EEM: CO NGUOI DINH RELOAD THIET BI!"
 action 2.0 set _exit_status "0"
```

| ⭐ `$_exit_status` | Nghĩa |
|:---:|---|
| **`0`** | 🔴  **KHÔNG cho lệnh chạy** — chặn lại |
| ⭐ **`1`** | **Cho lệnh chạy bình thường** |

> 🔴  **`sync yes` là thứ khiến EEM mạnh hơn hẳn mọi công cụ khác:**
> ⭐ **applet chạy TRƯỚC lệnh, và có quyền quyết định lệnh đó có được thực thi hay không.**
>
> ⚠️ ⭐ **Cẩn thận tối đa với applet loại này.**  **Viết sai regex là bạn tự khoá mình khỏi thiết bị.**
> ⭐ **Luôn test trên lab trước**, và  **luôn giữ sẵn một phiên SSH khác đang mở** phòng khi hỏng.

---

### 8.5 🔴  NĂM CÁI BẪY CỦA EEM — chỗ này làm hỏng lab nhiều nhất

#### 🔴  Bẫy 1 — thứ tự `action` sắp theo CHỮ, không theo SỐ

```
! ❌ SAI — bạn tưởng chạy 1 → 2 → 10
 action 1  syslog msg "buoc mot"
 action 2  syslog msg "buoc hai"
 action 10 syslog msg "buoc muoi"

! 🔴 THỰC TẾ CHẠY:  1  →  10  →  2
!    vì so sánh như CHUỖI KÝ TỰ: "1" < "10" < "2"
```

```
! ✅ ĐÚNG — dùng số thập phân đều nhau
 action 1.0  syslog msg "buoc mot"
 action 2.0  syslog msg "buoc hai"
 action 10.0 syslog msg "buoc muoi"
```

> 🔴  **Đây là bẫy kinh điển nhất của EEM.**  **IOS sắp xếp nhãn action như SẮP TỪ ĐIỂN,
> không phải như sắp số.** ⭐ **Nên luôn viết `1.0`, `2.0`, `3.0`…** — đó là lý do mọi tài liệu Cisco
> đều viết kiểu đó, chứ không phải cho đẹp.

#### 🔴  Bẫy 2 — quên `enable`

```
! ❌ SAI
 action 1.0 cli command "show running-config"     ← 🔴 applet vào ở chế độ user EXEC

! ✅ ĐÚNG
 action 1.0 cli command "enable"                  ← ⭐ BẮT BUỘC trước mọi lệnh privileged
 action 2.0 cli command "show running-config"
```

> ⭐ **Phiên CLI của EEM bắt đầu ở chế độ user EXEC**, y như bạn vừa telnet vào.
> ⭐ **Muốn chạy lệnh cần quyền cao thì phải `enable` trước.**

#### ⭐ Bẫy 3 — applet bị giết vì chạy quá lâu

> ⭐ **Applet có giới hạn thời gian chạy mặc định (`maxrun`) — khoảng 20 giây.**
> ⭐ Applet thu thập nhiều lệnh nặng sẽ **bị cắt giữa chừng** mà không báo gì rõ ràng.
>
> ⭐ **Cách xử lý:** khai báo dài hơn ngay ở dòng đầu:
> ```
> event manager applet THU-THAP-NHIEU
>  event none maxrun 120
> ```

#### 🔴  Bẫy 4 — AAA chặn lệnh của EEM

```
event manager applet BACKUP-KHI-LUU authorization bypass
```

> 🔴  **Nếu thiết bị có `aaa authorization commands` *(Module-10)*, thì các lệnh EEM gõ ra
> CŨNG bị đưa đi xin phép server AAA.** ⭐ **Server không biết "EEM" là ai → từ chối → applet im lặng không làm gì.**
> ⭐ **`authorization bypass` bảo IOS: applet này khỏi phải xin phép.**

#### ⭐ Bẫy 5 — mẫu (pattern) khớp quá rộng hoặc quá hẹp

| Viết | Khớp cái gì |
|---|---|
| `"reload"` | ⭐ **Khớp cả `show reload`!** — quá rộng |
| ⭐ **`"^reload"`** | **Chỉ khớp lệnh BẮT ĐẦU bằng `reload`** |
| `"write mem"` | Không khớp `write memory` nếu có chữ sau *(tuỳ ngữ cảnh)* |
| ⭐ **`"write mem.*"`** | **Khớp cả `write mem` lẫn `write memory`** |

> ⭐ **`^` = đầu dòng · `$` = cuối dòng · `.` = một ký tự bất kỳ · `.*` = bất kỳ thứ gì (kể cả rỗng).**
> ⭐ **Chỉ cần nhớ chừng đó là đủ cho đề thi.**

### 8.6 ⭐ KIỂM CHỨNG EEM

```
! ─── Applet nào đã được đăng ký? ───
R1# show event manager policy registered
No.  Class     Type    Event Type   Trap  Time Registered   Name
1    applet    user    syslog       Off   Mon Sep 8 ...     CANH-BAO-CONG-CHET
2    applet    user    cli          Off   Mon Sep 8 ...     BACKUP-KHI-LUU

! ─── Applet đã chạy mấy lần? ───
R1# show event manager statistics policy

! ─── Xem toàn bộ nội dung applet đang chạy ───
R1# show running-config | section event manager

! ─── Chạy tay để test (chỉ với event none) ───
R1# event manager run CHAO-HOI

! ─── Bật debug khi applet "không chịu chạy" ───
R1# debug event manager action cli
```

> ⭐ **Quy trình gỡ lỗi EEM — theo đúng thứ tự này:**
> ⭐ **① Applet có được đăng ký không?** → `show event manager policy registered`.
> ⭐ **Không thấy tên → cú pháp sai ngay từ lúc gõ, IOS đã từ chối.**
> ⭐ **② Có chạy lần nào chưa?** → `show event manager statistics policy`.
> ⭐ **Đếm = 0 → event không bao giờ khớp → xem lại pattern (Bẫy 5).**
> ⭐ **③ Chạy rồi mà không ra kết quả?** →  **xem Bẫy 1 (thứ tự), Bẫy 2 (enable), Bẫy 4 (AAA).**

---

## 📘 9. ⭐ PYTHON (blueprint 6.1 — INTERPRET)

> ⭐ **Động từ là INTERPRET — bạn KHÔNG phải viết code.**
> ⭐ Đề cho một đoạn script rồi hỏi **"nó in ra gì"** hoặc **"dòng nào gây lỗi"**.
> ⭐ **Mục tiêu của §9: đọc trôi, không phải code giỏi.**

### 9.1 ⭐ Năm thứ phải đọc được

| Thứ | Ví dụ | ⭐ Điều phải nhớ |
|---|---|---|
| **List** | `x = ["a", "b", "c"]` | 🔴  **`x[0]` là "a"** — đếm từ 0 |
| ⭐ **Dict** | `d = {"mtu": 1500}` | **Truy cập bằng key: `d["mtu"]`** |
| 🔴  **Thụt lề** | 4 dấu cách | 🔴  **Thụt lề LÀ cú pháp** — sai thụt lề là lỗi, không phải xấu |
| ⭐ **`for`** | `for i in x:` | Lặp qua từng phần tử |
| ⭐ **`if`** | `if mtu > 1500:` | Rẽ nhánh |

```python
interfaces = ["Gi0/0", "Gi0/1", "Gi0/2"]

print(interfaces[0])      # → Gi0/0    ← 🔴 phần tử ĐẦU TIÊN
print(interfaces[2])      # → Gi0/2
print(len(interfaces))    # → 3        ← đếm SỐ LƯỢNG thì bắt đầu từ 1
print(interfaces[-1])     # → Gi0/2    ← ⭐ số âm = đếm ngược từ cuối
```

> 🔴  **Bẫy số một:**  **`len()` trả về 3, nhưng chỉ số hợp lệ là 0, 1, 2.**
> ⭐ **`interfaces[3]` sẽ LỖI** — đề rất hay hỏi chỗ này.

### 9.2 ⭐ Đọc dữ liệu lồng nhau — dạng câu hỏi hay gặp nhất

```python
data = {
    "device": "R1",
    "interfaces": [
        {"name": "Gi0/0", "enabled": True,  "mtu": 1500},
        {"name": "Gi0/1", "enabled": False, "mtu": 9000}
    ]
}

print(data["device"])                       # → R1
print(data["interfaces"][1]["mtu"])         # → 9000   ← ⭐ đi từng bước!
print(len(data["interfaces"]))              # → 2

for intf in data["interfaces"]:
    if intf["enabled"]:
        print(intf["name"] + " dang BAT")
    else:
        print(intf["name"] + " dang TAT")

# Kết quả in ra:
#   Gi0/0 dang BAT
#   Gi0/1 dang TAT
```

> ⭐ **Cách đọc `data["interfaces"][1]["mtu"]` — đọc TỪ TRÁI SANG PHẢI, từng bậc một:**
> ⭐ `data["interfaces"]` → lấy **mảng** ·
> ⭐ `[1]` → lấy **phần tử thứ HAI** *(đếm từ 0!)* ·
> ⭐ `["mtu"]` → lấy giá trị `9000`.
>
> 🔴  **Đừng nhảy cóc.**  **Người mới sai vì đọc cả cụm một lúc rồi đoán.**

> ⚠️ ⭐ **Lưu ý JSON vs Python — chỗ rất dễ lẫn** *(nối với §3.1)*:
> ⭐ **Trong Python là `True`/`False`/`None` (viết HOA chữ đầu).**
> ⭐ **Trong JSON là `true`/`false`/`null` (viết THƯỜNG hết).**
> 🔴  **Đề cho một file JSON có `True` rồi hỏi sai ở đâu — đó chính là lỗi.**

### 9.3 ⭐ Ba thư viện phải nhận ra mặt

| Thư viện | Dùng để | Nhận ra bằng |
|---|---|---|
| ⭐ **`netmiko`** | **SSH vào thiết bị và gõ lệnh CLI** | `ConnectHandler` · `send_command` |
| ⭐ **`requests`** | **Gọi REST API** | `requests.get` · `.json()` · `.status_code` |
| ⭐ **`ncclient`** | **Nói chuyện NETCONF** | `manager.connect` · `get_config` |

#### ⭐ netmiko — tự động hoá kiểu "gõ CLI hộ bạn"

```python
from netmiko import ConnectHandler

thiet_bi = {
    "device_type": "cisco_ios",
    "host": "10.0.0.1",
    "username": "admin",
    "password": "MatKhauRatDai",
}

ket_noi = ConnectHandler(**thiet_bi)
ket_qua = ket_noi.send_command("show ip interface brief")
print(ket_qua)
ket_noi.disconnect()
```

> ⭐ **netmiko vẫn là "screen scraping"** *(§6.3)* — nó **gõ lệnh và đọc chữ trả về.**
> ⭐ **Ưu điểm lớn: chạy được với MỌI thiết bị có SSH**, kể cả IOS cũ không có NETCONF —
> ⭐ **tức là chạy được trên vIOS trong EVE-NG của bạn.**

#### ⭐ requests — gọi REST API

```python
import requests

url = "https://10.0.0.1/restconf/data/ietf-interfaces:interfaces"
headers = {"Accept": "application/yang-data+json"}

r = requests.get(url, headers=headers, auth=("admin", "MatKhau"), verify=False)

print(r.status_code)          # → 200   ← 🔴 LUÔN kiểm tra dòng này TRƯỚC
if r.status_code == 200:
    du_lieu = r.json()        # đổi JSON thành dict Python
    print(du_lieu)
else:
    print("Loi:", r.status_code)
```

| Thành phần | Nghĩa |
|---|---|
| 🔴  **`r.status_code`** | **Mã trạng thái — xem bảng §5.2** |
| ⭐ **`r.json()`** | **Đổi payload JSON thành dict Python** |
| **`r.text`** | Payload thô dạng chuỗi |
| ⭐ **`verify=False`** | **Bỏ qua chứng chỉ tự ký** — tương đương `-k` của `curl` |

> 🔴  **Thói quen phải có:**  **kiểm tra `status_code` TRƯỚC khi gọi `.json()`.**
> ⭐ Gọi `.json()` trên một phản hồi `401` sẽ **lỗi hoặc trả về rỗng**, và bạn sẽ đi tìm nhầm chỗ.
> 🔗 ⭐ **Đây chính là ý đã cảnh báo ở §2.2** — người mới hay bỏ qua mã trạng thái.

---

## 📘 10. 🟡 ⭐ API CỦA DNA CENTER & vMANAGE (blueprint 6.4 — DESCRIBE)

> 🔗 Hai sản phẩm này bạn đã gặp ở **[Module-09 §7](Module-09-Architecture-va-QoS.md)** —
> ở đó học **nó làm gì**, ở đây học **gọi nó thế nào**.
>
> 🟡 Động từ là **Describe** — ⭐ **KHÔNG cần nhớ endpoint.**  **Chỉ cần nhớ LUỒNG XIN TOKEN.**

### 10.1 ⭐ Northbound và Southbound — khái niệm nền

```
        ┌──────────────────────────┐
        │  SCRIPT / ỨNG DỤNG CỦA BẠN │
        └────────────┬─────────────┘
                     │  ⭐ NORTHBOUND API  (REST/JSON — thứ BẠN gọi)
        ┌────────────▼─────────────┐
        │   CONTROLLER             │
        │   (DNA Center / vManage) │
        └────────────┬─────────────┘
                     │  ⭐ SOUTHBOUND  (NETCONF · CLI · SNMP · Telemetry)
        ┌────────────▼─────────────┐
        │    THIẾT BỊ MẠNG         │
        └──────────────────────────┘
```

> ⭐ **Nhớ theo hướng bản đồ: BẮC ở TRÊN, NAM ở DƯỚI.**
> ⭐ **Northbound = hướng LÊN người dùng/ứng dụng** → REST API, đây là thứ bạn gọi.
> ⭐ **Southbound = hướng XUỐNG thiết bị** → controller tự lo, bạn không đụng tới.
>
> ⭐ **Giá trị thật:** bạn gọi **một** lệnh northbound *("tạo VLAN 20 cho toàn campus")*,
> controller tự dịch thành **hàng trăm** lệnh southbound cho từng thiết bị.

### 10.2 ⭐ DNA Center — luồng hai bước

```
┌─ BƯỚC 1: XIN TOKEN ────────────────────────────────────────────┐
│  POST  https://<dnac>/dna/system/api/v1/auth/token             │
│  Xác thực: Basic (username + password)                         │
│  ⭐ Trả về:  { "Token": "eyJhbGciOi..." }                       │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─ BƯỚC 2: GỌI API THẬT ─────────────────────────────────────────┐
│  GET  https://<dnac>/dna/intent/api/v1/network-device          │
│  ⭐ Header:  X-Auth-Token: eyJhbGciOi...                        │
└────────────────────────────────────────────────────────────────┘
```

| Điều phải nhớ | Chi tiết |
|---|---|
| 🔴  **Phải xin token TRƯỚC** | **Gọi thẳng API mà không có token → `401`** *(xem §5.2)* |
| ⭐ **Token đi trong header `X-Auth-Token`** | **Riêng của DNAC** — không phải `Authorization` chuẩn |
| ⭐ **Xin token dùng verb `POST`** | Không phải GET |
| ⭐ **Token có hạn** | **Hết hạn → `401` → phải xin lại.** Script dài phải tự xin lại |
| ⭐ **`/dna/intent/api/v1/...`** | **"Intent API"** — nhóm API chính bạn dùng |

```python
import requests
requests.packages.urllib3.disable_warnings()

dnac = "https://sandboxdnac.cisco.com"

# Bước 1 — xin token
r = requests.post(dnac + "/dna/system/api/v1/auth/token",
                  auth=("USER", "MATKHAU"), verify=False)
token = r.json()["Token"]

# Bước 2 — gọi API thật
r2 = requests.get(dnac + "/dna/intent/api/v1/network-device",
                  headers={"X-Auth-Token": token}, verify=False)
print(r2.status_code)
for tb in r2.json()["response"]:
    print(tb["hostname"], tb["managementIpAddress"])
```

> ⚠️ ⭐ **Tên host và tài khoản sandbox do Cisco công bố và CÓ THỂ ĐỔI** — xem lại **§1.3**.
> ⭐ **Luôn lấy từ trang DevNet tại thời điểm bạn học.**

### 10.3 ⭐ vManage (SD-WAN) — khác DNAC ở chỗ nào

| | ⭐ **DNA Center** | **vManage** |
|---|---|---|
| **Cách xác thực** | **Token trong header** | 🔴  **Session cookie** *(`JSESSIONID`)* |
| ⭐ **Endpoint đăng nhập** | `/dna/system/api/v1/auth/token` | **`/j_security_check`** |
| ⭐ **Gốc API** | `/dna/intent/api/v1/...` | **`/dataservice/...`** |
| ⭐ **Quản cái gì** | **Campus / SD-Access** | **WAN / SD-WAN** |

> ⭐ **Điều cần nhớ, chỉ một câu:**
> ⭐ **DNAC dùng TOKEN (header `X-Auth-Token`) · vManage dùng COOKIE phiên (`JSESSIONID`).**
>
> ⭐ Các bản vManage mới còn yêu cầu thêm **token chống giả mạo (CSRF)** lấy từ
> `/dataservice/client/token` rồi gửi kèm ở header `X-XSRF-TOKEN`.
> ⭐ **Biết là có bước đó — không cần thuộc.**

---

## 📘 11. 🟡 ⭐ CÔNG CỤ ĐIỀU PHỐI — AGENT vs AGENTLESS (blueprint 6.7 — COMPARE)

> 🔗 Ví von ở **§2.7** — "nhân viên thường trú hay thợ gọi đến".
>
> 🟡 Động từ là **Compare** — ⭐ **đề hỏi SO SÁNH, không hỏi cấu hình.**  **Học bảng §11.1 là chính.**

### 11.1 ⭐ Bảng so sánh bốn công cụ — bảng quan trọng nhất của §11

| | ⭐ **Ansible** | **SaltStack** | **Puppet** | **Chef** |
|---|---|---|---|---|
| 🔴  **Agent?** | 🔴  **AGENTLESS** | **Cả hai** *(minion hoặc salt-ssh)* | 🔴  **AGENT** | 🔴  **AGENT** |
| ⭐ **Push hay Pull** | **PUSH** | **PUSH** | **PULL** | **PULL** |
| ⭐ **Ngôn ngữ mô tả** | **YAML** | **YAML** | **Ruby DSL** *(manifest)* | **Ruby** *(recipe)* |
| ⭐ **Kết nối bằng** | **SSH / API** | ZeroMQ *(hoặc SSH)* | Kênh riêng của agent | Kênh riêng của agent |
| 🔴  **Hợp với thiết bị mạng?** | 🔴  **RẤT HỢP** | Được | 🔴 **Kém** | 🔴 **Kém** |

> 🔴  **Câu hỏi đề hay ra nhất — nhớ đúng bốn chữ này:**
> ⭐ **Ansible = agentless · Puppet = agent · Chef = agent · SaltStack = cả hai.**
>
> ⭐ **Mẹo nhớ:**  **"An" trong Ansible — AN toàn vì KHÔNG cần cài gì."**
> ⭐ Và  **Puppet/Chef đều là tiếng Anh chỉ NGƯỜI/VẬT sống trong nhà** *(con rối, đầu bếp)* → **agent**.

### 11.2 ⭐ Push vs Pull — khác nhau ở AI CHỦ ĐỘNG

```
   ⭐ PUSH (Ansible, SaltStack)         ⭐ PULL (Puppet, Chef)

   ┌──────────┐                        ┌──────────┐
   │ MÁY ĐIỀU │ ──── "làm đi!" ───▶    │  TRUNG   │  ◀── "có việc gì
   │  KHIỂN   │                        │   TÂM    │       cho tôi không?"
   └──────────┘                        └──────────┘            │
        ⭐ Máy chủ CHỦ ĐỘNG               ⭐ AGENT trên máy con  │
        ⭐ Chạy khi BẠN gõ lệnh            CHỦ ĐỘNG hỏi, định kỳ ┘
```

| | ⭐ **Push** | **Pull** |
|---|---|---|
| Ai khởi xướng | ⭐ **Máy điều khiển** | **Agent trên máy con** |
| Thời điểm | ⭐ **Ngay khi bạn chạy** | Theo chu kỳ *(vd mỗi 30 phút)* |
| ⭐ **Ưu** | **Kiểm soát chính xác lúc nào thay đổi** | **Tự sửa khi cấu hình bị lệch chuẩn** |
| 🔴 **Nhược** | Không tự phát hiện lệch chuẩn | **Phải cài agent** · khó đoán lúc nào chạy |

### 11.3 ⭐ Ansible trong mạng — ba khái niệm đủ dùng

| Khái niệm | Là gì |
|---|---|
| ⭐ **Inventory** | **Danh sách thiết bị** cần quản, có nhóm |
| ⭐ **Playbook** | **File YAML mô tả việc cần làm** *(xem §4.2)* |
| ⭐ **Module** | **Việc cụ thể** — `ios_config`, `ios_command`, `ios_facts` |

| Module | Dùng khi |
|---|---|
| 🔴  **`ios_config`** | **ĐỔI cấu hình** —  **idempotent: đã có rồi thì KHÔNG làm lại** |
| ⭐ **`ios_command`** | **Chỉ CHẠY lệnh và lấy output** *(thường là `show`)* — không đổi gì |
| **`ios_facts`** | Thu thập thông tin thiết bị |

> 🔴  **`ios_config` vs `ios_command` — đề hay hỏi:**
> ⭐ **`ios_config` để SỬA, `ios_command` để XEM.**
> ⭐ **`ios_command` KHÔNG vào được chế độ config** — dùng nó để đổi cấu hình là sai công cụ.

### 11.4 ⭐ Idempotent — khái niệm xuyên suốt cả module

> ⭐ **Đây là lần thứ ba khái niệm này xuất hiện** *(§5.1 với HTTP verb, §11.1 với công cụ, và ở đây)*.
> ⭐ **Không phải trùng lặp — đó là dấu hiệu nó quan trọng.**

> 🔁 ⭐ **Định nghĩa một câu:**  **chạy 1 lần hay 100 lần, kết quả cuối cùng như nhau.**

| Công cụ | Thể hiện thế nào |
|---|---|
| ⭐ **REST** | **`PUT` idempotent · `POST` không** *(§5.1)* |
| ⭐ **Ansible** | **`ios_config` kiểm tra trước: VLAN 20 đã có thì báo `ok`, chưa có mới báo `changed`** |
| 🔴  **Script gõ CLI thô** | 🔴  **KHÔNG idempotent** — cứ chạy là gõ lại, không cần biết đã có chưa |

> ⭐ **Vì sao đây là lý do người ta bỏ script CLI để dùng Ansible:**
> ⭐ **script CLI chạy lại lần hai có thể làm hỏng thứ đang chạy đúng.**
> ⭐ **Ansible chạy lại lần hai thì báo "không có gì để làm" và dừng.**
> ⭐ **Khác biệt đó chính là thứ cho phép bạn dám chạy lại khi script lỡ đứt giữa chừng.**

---

## 🧪 PHẦN 3 — NHÌN THẤY NÓ

> LAB đã tách ra file riêng để bạn **mở song song** với lý thuyết — một cửa sổ đọc, một cửa sổ gõ.

> ### 👉 **[LAB 12 — Tuần 18–19: JSON · REST · NETCONF/RESTCONF · EEM · Ansible](Module-12-LAB.md)**

| Tuần | Nội dung | Trả lời câu hỏi | Ví von ở Phần 1 | Cơ chế ở Phần 2 |
|:---:|---|---|---|---|
| 18 | **Đọc JSON & gọi REST** | Lấy đúng giá trị lồng nhau bằng cách nào? `401` khác `403` ra sao? | §2.2 · §2.3 | §3 · §5 |
| 18 | **NETCONF/RESTCONF trên Sandbox** | Cổng 830 trả về gì? RESTCONF đổi được config thật không? | §2.5 thư vs bưu thiếp | §7 |
| 19 | 🔴 **EEM — tự viết applet** | Làm sao thiết bị TỰ xử lý lúc 3h sáng? | §2.6 bác bảo vệ | §8 |
| 19 | **Ansible playbook đầu tiên** | Chạy lại lần hai thì sao? *(idempotent)* | §2.7 thuê thợ | §11 |

> ⚠️ 🔴  **Automation là thứ phải GÕ mới hiểu.**
> ⭐ Bảng mã trạng thái đọc mãi vẫn mơ hồ, nhưng **tự tay gửi sai token rồi nhận đúng `401`**
> thì nhớ mãi.
>
> ⭐ **Đặc biệt bài EEM** — đó là lúc bạn thấy thiết bị **tự làm việc mà không cần bạn**,
> và hiểu vì sao blueprint bắt **CONSTRUCT** chứ không chỉ *describe*.

---

## 🏗️ PHẦN 4 — TOPO & KIẾN TRÚC

> ⭐ Phần này ráp mọi thứ đã học thành **một bức tranh dùng được ngoài đời**.
> ⭐ Đọc sau khi đã làm LAB.

### 12.1 ⭐ Một hệ automation thật trông như thế nào

```
 ┌────────────────────────────────────────────────────────────────────┐
 │  ① KHO LƯU MÃ NGUỒN (Git)                                          │
 │     Playbook · script · template · lịch sử ai đổi gì lúc nào        │
 └────────────────────────────┬───────────────────────────────────────┘
                              │
 ┌────────────────────────────▼───────────────────────────────────────┐
 │  ② MÁY ĐIỀU KHIỂN (Linux)                                          │
 │     Ansible · Python · ncclient/netmiko/requests                    │
 └───────┬──────────────────┬─────────────────────┬───────────────────┘
         │                  │                     │
    ⭐ SSH/CLI         ⭐ NETCONF 830        ⭐ REST API 443
    (netmiko)          (ncclient)          (DNAC / vManage)
         │                  │                     │
         │                  │            ┌────────▼────────┐
         │                  │            │  ③ CONTROLLER   │
         │                  │            │  DNAC / vManage │
         │                  │            └────────┬────────┘
         │                  │                     │ ⭐ southbound
 ┌───────▼──────────────────▼─────────────────────▼───────────────────┐
 │  ④ THIẾT BỊ MẠNG                                                    │
 │     + 🔴 EEM chạy NGAY BÊN TRONG — không phụ thuộc ai bên ngoài     │
 └────────────────────────────────────────────────────────────────────┘
```

### 12.2 ⭐ Quyết định: việc này dùng công cụ nào?

| Tình huống | ⭐ Dùng | Vì sao |
|---|---|---|
| ⭐ **Lấy thông tin 200 thiết bị để làm báo cáo** | **Ansible** *(`ios_command`)* hoặc **netmiko** | Đọc thuần, không sửa gì |
| **Đổi cấu hình phức tạp trên router lõi** | 🔴  **NETCONF** | **Có candidate + rollback** — sai còn cứu được |
| ⭐ **Vẽ dashboard tình trạng cổng** | **RESTCONF** | Nhanh, trả JSON, dễ ghép |
| **Thiết bị phải TỰ phản ứng lúc 3h sáng** | 🔴  **EEM** | **Duy nhất chạy được khi mạng đã đứt** |
| ⭐ **Đổi chính sách cho cả campus** | **DNAC API** | Một lệnh → controller lo phần còn lại |
| ⭐ **Thiết bị cũ không có NETCONF** | **netmiko / Ansible qua SSH** | **Cái gì cũng có SSH** |

> ⭐ **Nguyên tắc chọn — nhớ một câu:**
> ⭐ **Cần AN TOÀN → NETCONF. Cần NHANH → RESTCONF. Cần CHẠY KHI MẤT MẠNG → EEM.
> Cần LÀM HÀNG LOẠT → Ansible. Thiết bị QUÁ CŨ → netmiko.**

### 12.3 ⭐ Ba sự thật đi làm

> 🔴  **Sự thật 1 — automation KHÔNG giảm lỗi, nó NHÂN RỘNG lỗi.**
> ⭐ Gõ tay sai một lệnh → hỏng **một** thiết bị.
> 🔴  **Chạy một playbook sai → hỏng ĐỒNG THỜI 200 thiết bị, trong 30 giây.**
> ⭐ **Vì vậy: luôn chạy thử trên lab · luôn dùng `--check` của Ansible · luôn bắt đầu từ một thiết bị.**

> 🔴  **Sự thật 2 — thứ đáng tự động hoá đầu tiên KHÔNG phải cấu hình, mà là ĐỌC.**
> ⭐ Người mới hay lao vào viết script đổi config — thứ rủi ro nhất.
> ⭐ **Việc đáng làm trước là script CHỈ ĐỌC:** kiểm kê thiết bị, tìm cổng đang tắt,
> đối chiếu cấu hình với chuẩn. ⭐ **Đọc thì không bao giờ làm sập mạng**, mà giá trị thu về đã rất lớn.

> 🔴  **Sự thật 3 — EEM là thứ dễ bị quên nhất nhưng cứu bạn nhiều nhất.**
> ⭐ Mọi công cụ khác đều cần **mạng còn sống** để SSH vào.
> 🔴  **Đúng lúc mạng hỏng — lúc bạn cần thông tin nhất — thì chúng vô dụng.**
> ⭐ **EEM đã nằm sẵn trong thiết bị nên vẫn chạy.**  Một applet 5 dòng ghi lại hiện trạng
> lúc sự cố xảy ra **có giá trị hơn cả một hệ giám sát đắt tiền** nhìn từ bên ngoài.

### 12.4 ⭐ Tự vẽ lại — kiểm tra bạn đã thật sự hiểu

> ⭐ **Gấp tài liệu lại. Lấy giấy. Vẽ và trả lời:**
>
> 1. ⭐ Vẽ sơ đồ **§12.1** — 4 tầng, và **ba đường** từ máy điều khiển xuống thiết bị *(ghi rõ cổng)*.
> 2. ⭐ **EEM nằm ở đâu trong sơ đồ đó, và vì sao vị trí đó quan trọng?**
> 3. ⭐ Viết lại **bộ khung EEM 3 dòng** ở §8.1 — không nhìn tài liệu.
> 4. ⭐ **NETCONF khác RESTCONF ở 3 điểm nào?** *(gợi ý: cổng · định dạng · giao dịch)*
> 5. ⭐ **`401` và `403` khác nhau ra sao?** Trả lời bằng ví von cái rạp phim.
> 6. ⭐ **Vì sao trong mạng người ta chọn agentless?**
>
> ⭐ **Trả lời trôi cả 6 câu = bạn đã nắm Domain 6.0.**
> ⭐ Vướng câu nào thì quay lại đúng mục đó, đừng đọc lại cả module.

---

# 📎 PHỤ LỤC — TRA CỨU

> ⛔ ⭐ **KHÔNG đọc phần này ở lần đọc đầu tiên.**
> ⭐ Đây là chỗ để **tra khi ôn thi** và **tra khi lab hỏng**.

---

## 🎓 13. BẪY TRONG ĐỀ ENCOR

| # | Bẫy | 🔴 Sự thật |
|:---:|---|---|
| 1 | 🔴  **"NETCONF và RESTCONF thuộc domain 6.0"** | 🔴  **SAI — mục 4.7, thuộc Domain 4.0 Network Assurance** |
| 2 | 🔴  **Nhầm 401 với 403** | **401 = DANH TÍNH *(chưa/sai token)* · 403 = QUYỀN HẠN *(đúng người, không đủ quyền)*** |
| 3 | 🔴  **Tưởng mảng đếm từ 1** | 🔴  **`[0]` là phần tử ĐẦU TIÊN** |
| 4 | 🔴  **Tưởng `action 10` chạy sau `action 2`** | 🔴  **Sắp theo CHUỖI: 1 → 10 → 2.** Luôn viết `1.0`, `2.0` |
| 5 | 🔴  **Tưởng JSON có comment** | 🔴  **JSON KHÔNG có comment.** YAML có `#`, XML có `<!-- -->` |
| 6 | 🔴  **Viết `True`/`None` trong JSON** | **JSON dùng `true`/`false`/`null` viết THƯỜNG.** `True` là của Python |
| 7 | 🔴  **Tưởng POST idempotent** | **GET/PUT/DELETE idempotent · POST/PATCH KHÔNG** |
| 8 | 🔴  **Tưởng RESTCONF rollback được** | 🔴  **KHÔNG. Chỉ NETCONF có candidate + commit + rollback** |
| 9 | 🔴  **Đảo cổng 830 và 443** | **NETCONF = SSH 830 · RESTCONF = HTTPS 443** |
| 10 | 🔴  **Tưởng Ansible cần agent** | 🔴  **Ansible AGENTLESS.** Puppet/Chef mới cần agent |
| 11 | 🔴  **Tưởng YANG là giao thức** | **YANG là KHUÔN DỮ LIỆU.** NETCONF/RESTCONF mới là giao thức |
| 12 | ⭐ **Dùng `ios_command` để đổi config** | **Sai công cụ — `ios_command` chỉ CHẠY lệnh. Sửa thì dùng `ios_config`** |
| 13 | ⭐ **Nhầm `Content-Type` với `Accept`** | **`Content-Type` = thứ TÔI GỬI · `Accept` = thứ tôi MUỐN NHẬN** |
| 14 | ⭐ **Nhầm `container` với `list` trong YANG** | **`container` xuất hiện 1 lần · `list` nhiều lần và CÓ KHOÁ** |
| 15 | ⭐ **Tưởng Northbound đi xuống thiết bị** | **Northbound = LÊN ứng dụng · Southbound = XUỐNG thiết bị** |
| 16 | ⭐ **Nhầm PUT với PATCH** | **PUT thay TOÀN BỘ *(trường thiếu có thể bị xoá)* · PATCH sửa MỘT PHẦN** |

---

## 🐛 14. GỠ LỖI NHANH

### 14.1 🔴 NETCONF / RESTCONF không chạy

| Triệu chứng | 🔴 Nguyên nhân hay gặp nhất | Kiểm tra bằng | Sửa |
|:---:|---|---|---|
| **Gõ `netconf-yang` báo lệnh không tồn tại** | 🔴  **Đang dùng vIOS, không phải IOS-XE** | `show version` | **Dùng DevNet Sandbox** *(§1.2)* |
| 🔴  **Kết nối 830 bị từ chối xác thực** | 🔴  **Thiếu `aaa authorization exec default local`** | `show run \| include aaa` | **Thêm dòng đó** *(§7.4)* |
| ⭐ **Vừa bật xong, kết nối không được** | **Tiến trình nền chưa lên hết** | `show platform software yang-management process` | **Chờ 1–2 phút** |
| ⭐ **RESTCONF trả `404`** | **Sai đường dẫn YANG** | Đối chiếu tên module | **Kiểm tra `module:container`** |
| 🔴 **RESTCONF trả `415`** | 🔴  **Quên `yang-data+json`** | Xem header đã gửi | **Đặt `Content-Type: application/yang-data+json`** |
| ⭐ **RESTCONF không kết nối được** | **Thiếu `ip http secure-server`** | `show run \| include http` | **Bật HTTPS** |
| ⭐ **`401` dù mật khẩu đúng** | **Token hết hạn** *(với DNAC)* | Xin token mới | **Xin lại token** |

### 14.2 🔴 EEM không chạy

```
① Applet có được đăng ký không?
   show event manager policy registered
   │
   ├─ KHÔNG thấy tên  → 🔴 cú pháp sai, IOS đã từ chối ngay lúc gõ
   │                     → gõ lại từng dòng, xem dòng nào báo lỗi
   │
   └─ CÓ thấy → ②
                │
② Đã chạy lần nào chưa?
   show event manager statistics policy
   │
   ├─ Số lần = 0  → 🔴 EVENT KHÔNG BAO GIỜ KHỚP
   │                 → xem lại pattern (Bẫy 5, §8.5)
   │                 → test nhanh: đổi tạm sang "event none" rồi chạy tay
   │
   └─ Có chạy → ③
                │
③ Chạy rồi mà không ra kết quả mong muốn:
   ├─ 🔴 Thứ tự action sai      → Bẫy 1: dùng 1.0 / 2.0 / 3.0
   ├─ 🔴 Thiếu "enable"         → Bẫy 2
   ├─ 🔴 Bị AAA chặn            → Bẫy 4: thêm "authorization bypass"
   └─ 🔴 Chạy quá 20 giây       → Bẫy 3: thêm "maxrun"
```

### 14.3 ⭐ Script Python lỗi

| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| ⭐ **`KeyError`** | **Sai tên key, hoặc key không tồn tại** | **In cả dict ra xem có gì: `print(data)`** |
| **`IndexError`** | 🔴  **Lấy `[3]` trong mảng chỉ có 3 phần tử** | **Chỉ số hợp lệ là 0,1,2** |
| ⭐ **`IndentationError`** | **Thụt lề lệch** | **Dùng 4 dấu cách đều nhau, không trộn Tab** |
| **`.json()` báo lỗi** | 🔴  **Phản hồi không phải JSON** *(thường vì đã lỗi `401`)* | **In `r.status_code` và `r.text` ra trước** |
| ⭐ **Cảnh báo chứng chỉ SSL** | Chứng chỉ tự ký | **`verify=False`** *(chỉ trong lab)* |

---

## 📝 15. QUIZ TỰ KIỂM TRA

> ⭐ **Tự trả lời TRƯỚC khi mở đáp án.**  Sai câu nào → quay lại đúng mục đó.

**1.** NETCONF và RESTCONF dùng cổng nào? Thuộc domain nào trong blueprint?

<details><summary>Đáp án</summary>

⭐ **NETCONF = SSH cổng 830** ·  **RESTCONF = HTTPS cổng 443**.

🔴  **Cả hai thuộc mục 4.7 — Domain 4.0 Network Assurance**, KHÔNG phải 6.0.
*(§7.1 · §0.2)*
</details>

**2.** Cho payload sau, `data["interfaces"][0]["mtu"]` bằng bao nhiêu?

```json
{"interfaces": [{"name": "Gi0/0", "mtu": 1500}, {"name": "Gi0/1", "mtu": 9000}]}
```

<details><summary>Đáp án</summary>

⭐ **1500.**

🔴  **`[0]` là phần tử ĐẦU TIÊN** — tức `Gi0/0`. Rất nhiều người trả lời 9000 vì tưởng đếm từ 1. *(§3.3 · §9.2)*
</details>

**3.** File JSON dưới đây sai ở đâu — có mấy lỗi?

```
{
  'device': "R1",        // ten thiet bi
  "mtu": 1500,
}
```

<details><summary>Đáp án</summary>

⭐ **Ba lỗi:**
1. 🔴 **`'device'` dùng nháy đơn** — JSON chỉ chấp nhận nháy kép.
2. 🔴 **`// ten thiet bi`** — JSON **không có comment**.
3. 🔴 **Dấu phẩy sau `1500`** — phần tử cuối không được có dấu phẩy.
*(§3.1 · §3.2)*
</details>

**4.** API trả về `403`. Bạn đi kiểm tra cái gì đầu tiên?

<details><summary>Đáp án</summary>

⭐ **Kiểm tra QUYỀN (role) của tài khoản** — không phải kiểm tra token.

⭐ **`403` nghĩa là danh tính đã được chấp nhận nhưng không đủ quyền** *(ví von: vé thật, nhưng không được vào phòng VIP)*.
⭐ Nếu là **`401`** thì mới đi kiểm tra token/mật khẩu. *(§5.2)*
</details>

**5.** Applet sau có gì sai? Nó sẽ chạy theo thứ tự nào?

```
event manager applet TEST
 event none
 action 1  syslog msg "mot"
 action 2  syslog msg "hai"
 action 10 syslog msg "muoi"
```

<details><summary>Đáp án</summary>

🔴  **Chạy theo thứ tự: 1 → 10 → 2.**

⭐ **IOS sắp xếp nhãn action như CHUỖI KÝ TỰ**, không phải như số: `"1" < "10" < "2"`.

⭐ **Sửa:** dùng `1.0`, `2.0`, `10.0`. *(§8.5 Bẫy 1)*
</details>

**6.** Vì sao chỉ NETCONF mới `rollback` được mà RESTCONF thì không?

<details><summary>Đáp án</summary>

⭐ **Vì NETCONF có `candidate` datastore — một bản nháp tách rời khỏi `running`.**

⭐ Bạn sửa vào `candidate`, thiết bị **chưa áp dụng gì cả**, tới khi `commit` mới chuyển sang `running`.
⭐ Chưa commit thì `discard-changes` là xong.  **Và nếu commit lỗi thì TOÀN BỘ thay đổi bị huỷ, không có nửa vời.**

🔴  **RESTCONF ghi thẳng vào `running`** — không có bản nháp nên không có gì để quay lại. *(§7.3 · §2.5)*
</details>

**7.** Ansible, Puppet, Chef, SaltStack — cái nào agentless? Vì sao điều đó quan trọng với thiết bị mạng?

<details><summary>Đáp án</summary>

 **Ansible = agentless** ·  **SaltStack = cả hai** *(minion hoặc salt-ssh)* · 🔴 **Puppet và Chef = agent.**

🔴  **Quan trọng vì bạn KHÔNG cài được phần mềm lạ lên switch/router Cisco** — nó là hệ đóng.
⭐ **Nên trong mạng, agentless gần như luôn thắng.** *(§11.1 · §2.7)*
</details>

**8.** Bật `netconf-yang` xong, kết nối cổng 830 báo lỗi xác thực dù user/mật khẩu đúng. Nguyên nhân?

<details><summary>Đáp án</summary>

🔴  **Thiếu `aaa authorization exec default local`.**

⭐ NETCONF/RESTCONF xác thực **qua AAA**.  **Thiếu dòng đó thì SSH thường vẫn vào được,
nhưng NETCONF bị từ chối** — và thông báo lỗi **không hề nhắc tới AAA**. *(§7.4)*
</details>

**9.** `PUT` và `PATCH` khác nhau thế nào? Cái nào rủi ro hơn?

<details><summary>Đáp án</summary>

⭐ **`PUT` thay TOÀN BỘ đối tượng** — phải gửi đủ mọi trường.
⭐ **`PATCH` chỉ sửa PHẦN bạn gửi lên.**

🔴  **`PUT` rủi ro hơn: trường nào bạn không gửi có thể bị xoá hoặc về mặc định.** *(§5.1)*
</details>

**10.** YANG là giao thức hay là gì? Nêu 4 loại node.

<details><summary>Đáp án</summary>

🔴  **YANG KHÔNG phải giao thức — nó là NGÔN NGỮ MÔ TẢ KHUÔN dữ liệu** *(ví von: tờ khai)*.
⭐ **NETCONF/RESTCONF mới là giao thức vận chuyển.**

⭐ **Bốn node:** `leaf` *(một ô, một giá trị)* · `leaf-list` *(một ô, nhiều giá trị)* ·
`container` *(nhóm ô, xuất hiện 1 lần)* · `list` *(nhiều bản ghi, CÓ KHOÁ)*. *(§6.1 · §2.4)*
</details>

**11.** Viết một EEM applet: khi có người gõ `write memory` thì ghi một dòng syslog và sao lưu config ra flash.

<details><summary>Đáp án</summary>

```
event manager applet BACKUP-KHI-LUU
 event cli pattern "write mem.*" sync no skip no
 action 1.0 syslog msg "EEM: co nguoi vua luu config"
 action 2.0 cli command "enable"
 action 3.0 cli command "show running-config | redirect flash:backup-config.txt"
 action 4.0 syslog msg "EEM: da sao luu xong"
```

⭐ **Ba điểm chấm:**  **nhãn dạng `1.0`** *(Bẫy 1)* ·  **có `enable` trước lệnh privileged** *(Bẫy 2)* ·
⭐ **`skip no` để lệnh gốc vẫn chạy.** *(§8.4 ví dụ 3)*
</details>

**12.** DNA Center và vManage xác thực khác nhau ra sao?

<details><summary>Đáp án</summary>

⭐ **DNAC:** `POST /dna/system/api/v1/auth/token` → nhận **Token** → gửi kèm header  **`X-Auth-Token`**.

⭐ **vManage:** `POST /j_security_check` → nhận **cookie phiên `JSESSIONID`**.

⭐ **Một câu:**  **DNAC dùng TOKEN, vManage dùng COOKIE.** *(§10.2 · §10.3)*
</details>

---

## 📚 16. THUẬT NGỮ ANH–VIỆT

| Tiếng Anh | Tiếng Việt | ⭐ Giải thích ngắn |
|---|---|---|
| **API** | Giao diện lập trình ứng dụng | ⭐ **"Người bồi bàn"** — cách gọi món mà không cần vào bếp |
| **REST** | Kiểu thiết kế API dựa trên HTTP | Dùng verb GET/POST/PUT/PATCH/DELETE |
| **Endpoint** | Điểm cuối / đường dẫn API | Địa chỉ URL của một thứ cụ thể |
| **Payload** | Nội dung gửi/nhận | Phần dữ liệu thật, không tính header |
| **Header** | Tiêu đề gói tin | Thông tin đi kèm: định dạng, token… |
| **Status code** | Mã trạng thái | ⭐ **200/401/403/404/500…** |
| 🔴 **Idempotent** | Lặp lại không đổi kết quả | **Chạy 1 lần hay 100 lần đều như nhau** |
| **Token** | Thẻ truy cập | Chứng minh danh tính sau khi đăng nhập |
| **YANG** | Ngôn ngữ mô hình dữ liệu | ⭐ **"Tờ khai"** — khuôn của dữ liệu |
| **Datastore** | Kho cấu hình | `running` · `candidate` · `startup` |
| 🔴 **Candidate** | Bản nháp | **Sửa ở đây chưa ảnh hưởng gì tới thiết bị** |
| **Commit** | Chốt thay đổi | Đưa bản nháp thành hiệu lực |
| **Rollback** | Quay lui | Trả về trạng thái trước |
| **RPC** | Lệnh gọi thủ tục từ xa | Cách NETCONF ra lệnh |
| **Capability** | Khả năng thiết bị công bố | Có trong bản tin `<hello>` |
| **EEM** | Trình quản lý sự kiện nhúng | ⭐ **"Bác bảo vệ trực đêm"** |
| **Applet** | Một kịch bản EEM nhỏ | `event` + `action` |
| **Event detector** | Bộ phát hiện sự kiện | Thứ theo dõi "khi nào" |
| **Agent / Agentless** | Có / không cần cài phần mềm | ⭐ **Ansible agentless · Puppet-Chef agent** |
| **Push / Pull** | Đẩy / Kéo | ⭐ **Ai chủ động: máy chủ hay máy con** |
| **Playbook** | Kịch bản Ansible | File YAML mô tả việc cần làm |
| **Inventory** | Danh sách thiết bị | Ansible quản những máy nào |
| **Module** *(Ansible)* | Đơn vị việc | `ios_config`, `ios_command` |
| **Northbound** | Hướng lên | ⭐ **Controller ↔ ứng dụng/script** |
| **Southbound** | Hướng xuống | ⭐ **Controller ↔ thiết bị** |
| **Screen scraping** | Bóc chữ từ màn hình | ⭐ **Cách CŨ — đọc output `show` bằng cắt chuỗi** |
| **Sandbox** | Môi trường thử nghiệm | DevNet — thiết bị thật, miễn phí |

---

## 🎯 17. ĐÚC KẾT MODULE-12

### 17.1 ⭐ Nếu chỉ nhớ được MỘT bảng — nhớ bảng này

| Thứ | ⭐ Con số / sự thật |
|---|---|
| 🔴  **NETCONF** | **SSH · cổng 830 · chỉ XML · CÓ candidate/commit/rollback/lock** |
| 🔴  **RESTCONF** | **HTTPS · cổng 443 · JSON hoặc XML · KHÔNG rollback** |
| ⭐ **Cả hai** | **Đều dùng YANG** |
| 🔴  **401 vs 403** | **401 = danh tính · 403 = quyền hạn** |
| ⭐ **Idempotent** | **GET · PUT · DELETE** *(POST và PATCH thì không)* |
| 🔴  **EEM** | **`event` + `action` · nhãn `1.0`/`2.0` · phải `enable` trước** |
| ⭐ **Agentless** | **Ansible** *(và SaltStack qua SSH)* |
| ⭐ **Agent** | **Puppet · Chef** |
| ⭐ **DNAC vs vManage** | **Token (`X-Auth-Token`) vs Cookie (`JSESSIONID`)** |
| ⭐ **JSON** | **Không comment · không phẩy thừa · nháy kép · `true/false/null` thường** |

### 17.2 ⭐ Bảy ví von — nói lại được là đã hiểu

| Khái niệm | Ví von |
|---|---|
| **Automation** | ⭐ **Công thức làm bánh** — ai làm cũng ra cùng một cái |
| **API** | ⭐ **Người bồi bàn** — gọi món, không cần vào bếp |
| **JSON/XML/YAML** | ⭐ **Ba cách ghi địa chỉ lên phong bì** |
| **YANG** | ⭐ **Tờ khai có sẵn ô trống** |
| **NETCONF vs RESTCONF** | ⭐ **Thư bảo đảm vs bưu thiếp** |
| **EEM** | ⭐ **Bác bảo vệ trực đêm** |
| **Agent vs agentless** | ⭐ **Nhân viên thường trú vs thợ gọi đến** |
| **401 vs 403** | ⭐ **Không có vé vs có vé nhưng không được vào phòng VIP** |
| **Idempotent** | ⭐ **Gạt công tắc vs bấm chuông** |

### 17.3 🔴  Module này khép lại điều gì

> 🔴  **Học xong §7 là Domain 4.0 mới TRỌN VẸN** *(mục 4.7)*.
> ⭐ Trước đó, dù đã xong Module-11, bạn vẫn đang thiếu một mục.

| Domain | % đề | Xong sau module nào |
|---|:---:|---|
| **3.0 Infrastructure** | 30% | Module-02 → 07B |
| **5.0 Security** | 20% | Module-10 |
| **1.0 Architecture** | 15% | Module-09 |
| 🔴  **6.0 Automation** | **15%** | 🔴  **Module-12 — chính module này** |
| **2.0 Virtualization** | 10% | Module-08 |
| 🔴  **4.0 Assurance** | **10%** | 🔴  **Module-11 + §7 module này** |

> ✅ ⭐ **Hết Module-12 = đã phủ 100% blueprint.**  Còn lại là **ôn tập và luyện đề — Module-13.**

### 17.4 ⭐ Ba việc làm ngay sau khi đọc xong

| # | Việc | Vì sao |
|:---:|---|---|
| 1 | ⭐ **Làm [LAB 12](Module-12-LAB.md)** | **Đặc biệt bài EEM** — blueprint bắt CONSTRUCT |
| 2 | ⭐ **Viết một applet EEM cho lab của chính bạn** | **Tự nghĩ ra bài toán mới là lúc thật sự thuộc** |
| 3 | ⭐ **Đọc lại §17.1 mỗi ngày 2 phút tới khi thi** | **Bảng đó là phần dễ mất điểm vì quên, không phải vì không hiểu** |

---

## 🔗 18. TÀI LIỆU CHO MODULE NÀY

| Nguồn | Dùng để |
|---|---|
| ⭐ **[Cisco DevNet Sandbox](https://developer.cisco.com/site/sandbox/)** | **Thiết bị thật, miễn phí — bắt buộc cho §7 và §10** |
| ⭐ **[Cisco DevNet Learning Labs](https://developer.cisco.com/learning/)** | Bài học từng bước về REST/NETCONF/RESTCONF |
| ⭐ **[Cisco YANG models trên GitHub](https://github.com/YangModels/yang)** | Xem model thật của từng phiên bản IOS-XE |
| **RFC 6241** | Chuẩn NETCONF |
| **RFC 8040** | Chuẩn RESTCONF |
| **RFC 7950** | Chuẩn YANG 1.1 |
| ⭐ **Cisco IOS EEM Configuration Guide** | **Tra đầy đủ event detector và action** |
| ⭐ **[Ansible cisco.ios collection](https://docs.ansible.com/)** | Tra module `ios_config`, `ios_command` |
| ⭐ **[OpenConfig](https://openconfig.net/)** | Model trung lập hãng |
| ⭐ **Repo `network-automation-mastery` của bạn** | **Phủ sâu hơn phần Python/Ansible — học chéo, đừng học lại** |

---

> 🧭 **Tiếp theo:** Module-13 — Ôn thi & Chiến thuật phòng thi
>
> ⭐ **Trước khi sang, tự chấm §12.4** *(vẽ lại)* và  **làm hết [LAB 12](Module-12-LAB.md)**.
