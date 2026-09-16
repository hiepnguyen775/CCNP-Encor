# LAB 12 — Tuần 18–19: JSON · REST · NETCONF/RESTCONF · EEM · Ansible

> 📘 **Lý thuyết:** [Module-12](Module-12-Automation-va-Programmability.md) —
> đọc **PHẦN 1 (§2)** trước, rồi mở lab này **song song** với Phần 2.
>
> ⏱️ **Thời gian:** ~10 giờ *(chia 2 tuần)* · 💾 **RAM:** ⭐ **0,5 GB** · 🧰 **Cần:** Internet + EVE-NG *(chỉ cho Lab D)*
>
> ✅ ⭐ **Đây là lab NHẸ NHẤT cả khoá.**  Phần lớn chạy trên **máy bạn** và **DevNet Sandbox**.

---

## Lab này trả lời 8 câu hỏi

| # | Câu hỏi | Bài |
|:---:|---|:---:|
| 1 | Lấy giá trị lồng sâu trong JSON bằng cách nào? | 12-A |
| 2 | `401` và `403` khác nhau ra sao khi NHÌN THẤY thật? | 12-B |
| 3 | Gọi REST API rồi đọc mã trạng thái thế nào? | 12-B |
| 4 | Cổng 830 thật sự trả về cái gì? | 12-C |
| 5 | RESTCONF đổi được cấu hình thật không? | 12-C |
| 6 | 🔴 **Tự viết một EEM applet từ đầu** | **12-D** |
| 7 | 🔴 **Vì sao `action 10` chạy trước `action 2`?** | **12-D** |
| 8 | "Idempotent" nhìn thấy được không? | 12-E |

---

## 🧰 Chuẩn bị

### Bảng: bài nào cần gì

| Bài | Nội dung | Cần gì | Thời gian |
|:---:|---|---|:---:|
| **12-A** | JSON & Python | ⭐ **Chỉ máy bạn** | 1,5 giờ |
| **12-B** | REST API | ⭐ **Máy bạn + Internet** | 2 giờ |
| **12-C** | NETCONF/RESTCONF | ⭐ **DevNet Sandbox** | 2,5 giờ |
| 🔴 **12-D** | **EEM** | 🔴  **EVE-NG — 1 con vIOS, 512 MB** | **3 giờ** |
| **12-E** | Ansible | ⭐ **Máy Linux/WSL + EVE-NG** | 1 giờ |

### Cài đặt trên máy bạn

```bash
python --version            # cần Python 3.6 trở lên
pip install requests netmiko ncclient
```

> ⭐ **Windows:**  **dùng WSL (Ubuntu) cho bài 12-E** —  **Ansible không chạy máy điều khiển trên Windows thuần.**
> ⭐ Bài 12-A → 12-D thì Windows bình thường là đủ.

### 🔴 Lấy thông tin DevNet Sandbox

> 🔴  **Đọc kỹ:**  **tên host và tài khoản sandbox do Cisco công bố và CÓ THỂ THAY ĐỔI.**
>
> ⭐ **Vào [developer.cisco.com/site/sandbox](https://developer.cisco.com/site/sandbox/) →
> đăng nhập → chọn "Always On" → lấy thông tin TẠI THỜI ĐIỂM BẠN HỌC.**
>
> 🔴  **Đừng chép cứng từ tài liệu cũ** — đây là lỗi làm mất thời gian nhiều nhất của người mới.
>
> ⭐ **Hai sandbox cần lấy:**
> | Sandbox | Dùng cho |
> |---|---|
> | ⭐ **IOS XE on Cat8000V — Always On** | Bài **12-C** |
> | ⭐ **Cisco DNA Center — Always On** | Bài **12-B** |
>
> ⭐ Ghi lại vào một file cho tiện: `host` · `username` · `password` · `port`.

### Topology cho bài 12-D (EEM)

```
        ┌─────────────────┐
        │       R1        │   vIOS · 512 MB
        │   (vIOS router) │   ⭐ Dùng lại đúng con router của Module-11
        │                 │
        │  Gi0/0 ─────────┼── (để trống, ta sẽ shut/no shut để tạo sự kiện)
        └─────────────────┘
```

> ✅ ⭐ **Chỉ cần MỘT router.**  **EEM không cần mạng, không cần neighbor.**

---

## ⚠️ Đọc trước khi bắt đầu

| Điều cần biết | Chi tiết |
|---|---|
| 🔴  **vIOS KHÔNG có NETCONF/RESTCONF** | **Bài 12-C BẮT BUỘC dùng Sandbox.** Gõ `netconf-yang` trên vIOS sẽ báo lệnh không tồn tại |
| 🔴  **Sandbox là của chung** | **Có lúc chậm hoặc bận.** Đừng tưởng script mình sai — thử lại sau vài phút |
| ⭐ **Đừng phá sandbox** | **Người khác cũng đang dùng.** Đổi `description` thì được, đừng `shutdown` cổng hay xoá config |
| 🔴  **EEM `sync yes` có thể tự khoá bạn** | **Luôn giữ SẴN một phiên console thứ hai đang mở** khi làm bài 12-D bước 6 |
| ⭐ **Lỗi > 15 phút** | Ghi vào [`SO-TAY-LOI.md`](SO-TAY-LOI.md) rồi đi tiếp, quay lại sau |

---

# 🧪 LAB 12-A — Đọc JSON và Python

> 📘 **Lý thuyết:** [§3](Module-12-Automation-va-Programmability.md) *(JSON)* và [§9](Module-12-Automation-va-Programmability.md) *(Python)*
> ⏱️ **1,5 giờ** · 🧰 **Chỉ cần máy bạn**

---

## Bước A1 — Tự tay chứng minh "mảng đếm từ 0"

**🎯 Mục tiêu:** xoá vĩnh viễn cái bẫy hay làm mất điểm nhất domain 6.0.

**Gõ** — tạo file `a1.py`:

```python
interfaces = ["Gi0/0", "Gi0/1", "Gi0/2"]

print("len  =", len(interfaces))
print("[0]  =", interfaces[0])
print("[2]  =", interfaces[2])
print("[-1] =", interfaces[-1])
print("[3]  =", interfaces[3])      # dong nay se LOI - co y de vay
```

```bash
python a1.py
```

**Sẽ thấy:**

```
len  = 3
[0]  = Gi0/0
[2]  = Gi0/2
[-1] = Gi0/2
Traceback (most recent call last):
  ...
IndexError: list index out of range
```

**💡 Vì sao:** ⭐ **`len()` trả về 3, nhưng chỉ số hợp lệ chỉ là 0, 1, 2.**
⭐ **`[3]` vượt ra ngoài → `IndexError`.**  **Đây chính là thứ đề ENCOR hỏi** —
và bạn vừa tự tay nhìn thấy nó thay vì học thuộc.

**✅ Checkpoint:** ⭐ Bạn giải thích được **vì sao `len` = 3 mà `[3]` lại lỗi**.

---

## Bước A2 — Bóc dữ liệu lồng nhau, từng bậc một

**🎯 Mục tiêu:** đọc được `data["interfaces"][1]["mtu"]` mà không phải đoán.

**Gõ** — file `a2.py`:

```python
data = {
    "device": "R1",
    "interfaces": [
        {"name": "Gi0/0", "enabled": True,  "mtu": 1500},
        {"name": "Gi0/1", "enabled": False, "mtu": 9000}
    ]
}

# ⭐ BÓC TỪNG BẬC - dung in ra de NHIN thay tung buoc
buoc1 = data["interfaces"]
print("Buoc 1 - lay mang :", buoc1)

buoc2 = buoc1[1]
print("Buoc 2 - phan tu THU HAI:", buoc2)

buoc3 = buoc2["mtu"]
print("Buoc 3 - lay mtu  :", buoc3)

print("Viet gon mot dong :", data["interfaces"][1]["mtu"])
```

**Sẽ thấy:**

```
Buoc 1 - lay mang : [{'name': 'Gi0/0', ...}, {'name': 'Gi0/1', ...}]
Buoc 2 - phan tu THU HAI: {'name': 'Gi0/1', 'enabled': False, 'mtu': 9000}
Buoc 3 - lay mtu  : 9000
Viet gon mot dong : 9000
```

**💡 Vì sao:** ⭐ **Trong phòng thi bạn không in ra được — nhưng bạn vẫn phải đọc TỪNG BẬC trong đầu.**
⭐ **Người mới sai vì nhìn cả cụm `data["interfaces"][1]["mtu"]` rồi đoán.**
⭐ Làm bài này vài lần là thành phản xạ.

**✅ Checkpoint:** ⭐ Che dòng cuối, tự nói ra kết quả, rồi mở ra đối chiếu — đúng.

---

## Bước A3 — 🔴 Tìm lỗi trong file JSON

**🎯 Mục tiêu:** đây **chính xác là dạng câu hỏi của mục 6.2 (Construct)**.

**Gõ** — tạo file `sai.json`:

```
{
  'device': "R1",
  "mtu": 1500,
}
```

Rồi kiểm tra bằng Python:

```python
import json
with open("sai.json") as f:
    print(json.load(f))
```

**Sẽ thấy:** một lỗi `json.decoder.JSONDecodeError`.

**💡 Vì sao — file này có BA lỗi:**

| # | Lỗi | Sửa thành |
|:---:|---|---|
| 1 | 🔴 **`'device'` nháy đơn** | `"device"` |
| 2 | 🔴 **Dấu phẩy sau `1500`** | Bỏ dấu phẩy |
| 3 | *(nếu bạn thêm `// comment`)* | 🔴 **JSON không có comment** |

**Gõ tiếp** — sửa lại cho đúng rồi chạy lại:

```json
{
  "device": "R1",
  "mtu": 1500
}
```

**✅ Checkpoint:** ⭐ File chạy qua `json.load()` không lỗi, và  **bạn kể được cả 3 lỗi mà không nhìn bảng.**

---

# 🧪 LAB 12-B — Gọi REST API và đọc mã trạng thái

> 📘 **Lý thuyết:** [§5](Module-12-Automation-va-Programmability.md) *(REST)* và [§10](Module-12-Automation-va-Programmability.md) *(DNAC)*
> ⏱️ **2 giờ** · 🧰 **Máy bạn + DevNet Sandbox DNA Center**

---

## Bước B1 — Xin token từ DNA Center

**🎯 Mục tiêu:** thấy tận mắt luồng **"xin token trước, gọi API sau"**.

**Gõ** — file `b1.py` *(điền thông tin sandbox của bạn vào 3 dòng đầu)*:

```python
import requests
requests.packages.urllib3.disable_warnings()

DNAC = "https://..."          # ⭐ lay tu trang DevNet Sandbox
USER = "..."
PASS = "..."

r = requests.post(DNAC + "/dna/system/api/v1/auth/token",
                  auth=(USER, PASS), verify=False)

print("Ma trang thai:", r.status_code)
print("Noi dung tra ve:", r.json())
```

**Sẽ thấy:**

```
Ma trang thai: 200
Noi dung tra ve: {'Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6...'}
```

**💡 Vì sao:** ⭐ **`POST` chứ không phải `GET`** — vì bạn đang **gửi thông tin đăng nhập lên**.
⭐ **`200` nghĩa là thành công VÀ có dữ liệu trả về** — chính là cái token.

**✅ Checkpoint:** ⭐ Bạn nhận được `200` và một chuỗi token dài.

---

## Bước B2 — 🔴 CỐ Ý gây lỗi 401 để nhìn thấy nó

**🎯 Mục tiêu:** ⭐ **đây là bước quan trọng nhất bài 12-B.**
⭐ Bạn sẽ **nhớ 401 mãi mãi** vì đã tự tay tạo ra nó.

**Gõ** — file `b2.py`:

```python
import requests
requests.packages.urllib3.disable_warnings()

DNAC = "https://..."

# ① Goi API ma KHONG co token
r1 = requests.get(DNAC + "/dna/intent/api/v1/network-device", verify=False)
print("① Khong co token  ->", r1.status_code)

# ② Goi API voi token SAI
r2 = requests.get(DNAC + "/dna/intent/api/v1/network-device",
                  headers={"X-Auth-Token": "token-bay-ba"}, verify=False)
print("② Token sai       ->", r2.status_code)

# ③ Goi SAI duong dan (voi token dung - lay lai tu b1.py)
# r3 = requests.get(DNAC + "/dna/intent/api/v1/khong-ton-tai",
#                   headers={"X-Auth-Token": token}, verify=False)
# print("③ Sai duong dan  ->", r3.status_code)
```

**Sẽ thấy:**

```
① Khong co token  -> 401
② Token sai       -> 401
③ Sai duong dan   -> 404
```

**💡 Vì sao:**

| Mã | Nghĩa | ⭐ Bạn đi kiểm tra cái gì |
|:---:|---|---|
| 🔴  **401** | **Vấn đề DANH TÍNH** | **Token — có chưa, đúng chưa, hết hạn chưa** |
| ⭐ **404** | **Sai đường dẫn** | **Gõ lại URL** |

> ⭐ **Ghi nhớ bằng cảm giác:**  **bạn vừa thấy `401` xuất hiện ở CẢ HAI trường hợp
> "không có token" và "token sai"** — đúng như ví von cái rạp phim: ⭐ **không vé và vé giả đều bị chặn ở cửa như nhau.**

**✅ Checkpoint:** ⭐ Bạn tạo ra được `401` **theo ý muốn**, và giải thích được vì sao nó không phải `403`.

---

## Bước B3 — Gọi API thật và đọc payload

**🎯 Mục tiêu:** ghép token vào header và bóc dữ liệu trả về.

**Gõ** — file `b3.py`:

```python
import requests
requests.packages.urllib3.disable_warnings()

DNAC = "https://..."
USER = "..."
PASS = "..."

# ① Xin token
token = requests.post(DNAC + "/dna/system/api/v1/auth/token",
                      auth=(USER, PASS), verify=False).json()["Token"]

# ② Goi API that
r = requests.get(DNAC + "/dna/intent/api/v1/network-device",
                 headers={"X-Auth-Token": token}, verify=False)

print("Ma trang thai:", r.status_code)

if r.status_code == 200:                      # ⭐ LUON kiem tra TRUOC khi .json()
    ds = r.json()["response"]
    print("So thiet bi:", len(ds))
    for tb in ds:
        print(" -", tb["hostname"], "|", tb["managementIpAddress"], "|", tb["platformId"])
else:
    print("Loi:", r.text)
```

**Sẽ thấy:** danh sách thiết bị thật trong sandbox.

**💡 Vì sao:** ⭐ **Chú ý dòng `if r.status_code == 200:`** —  **đây là thói quen phải có.**
🔴  **Gọi `.json()` trên một phản hồi `401` sẽ lỗi hoặc trả về rỗng, và bạn sẽ đi tìm nhầm chỗ hàng giờ.**

**✅ Checkpoint:** ⭐ In ra được **tên + IP** của ít nhất một thiết bị.

---

# 🧪 LAB 12-C — NETCONF & RESTCONF trên thiết bị thật

> 📘 **Lý thuyết:** [§7](Module-12-Automation-va-Programmability.md) — đọc hết §7 trước khi làm
> ⏱️ **2,5 giờ** · 🧰 🔴 **DevNet Sandbox "IOS XE on Cat8000V — Always On"**
>
> 🔴  **Bài này KHÔNG làm được trên EVE-NG vIOS.** Xem lý do ở [§1.2](Module-12-Automation-va-Programmability.md).

---

## Bước C1 — 🔴 Nhìn thấy cổng 830 trả lời

**🎯 Mục tiêu:** ⭐ **chứng minh NETCONF đang sống — bằng MỘT lệnh, không cần script.**

**Gõ** *(từ máy bạn, không phải trên router)*:

```bash
ssh -p 830 USER@HOST-SANDBOX -s netconf
```

**Sẽ thấy** — một khối XML đổ ra ngay lập tức:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
    <capability>urn:ietf:params:netconf:capability:writable-running:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
    ... (rat nhieu dong) ...
  </capabilities>
  <session-id>12345</session-id>
</hello>
]]>]]>
```

**💡 Vì sao — đây là thứ đáng giá nhất bài C1:**

> ⭐ **Khối `<hello>` này là THIẾT BỊ ĐANG TỰ KHAI nó làm được gì.**
>
> ⭐ **Tìm trong danh sách xem có dòng nào chứa chữ `candidate` không:**
> - ⭐ **Có `:candidate`** →  **máy này hỗ trợ bản nháp + commit/rollback** *(§7.3)*
> - ⭐ **Chỉ có `:writable-running`** →  **ghi thẳng vào running, KHÔNG có bản nháp**
>
> 🔴  **Đây là cách duy nhất để biết chắc — đừng đoán theo tài liệu.**

**Thoát:** nhấn `Ctrl+C`.

**✅ Checkpoint:** ⭐ Bạn thấy khối `<hello>`, và  **trả lời được máy này có `candidate` hay không.**

---

## Bước C2 — Đọc cấu hình qua RESTCONF

**🎯 Mục tiêu:** so sánh **cùng một thông tin** lấy bằng CLI và bằng RESTCONF.

**Gõ** — trước hết xem bằng CLI cho quen mắt:

```
Router# show running-config | section interface GigabitEthernet1
```

**Rồi lấy đúng thứ đó bằng RESTCONF:**

```bash
curl -k -u USER:PASS \
     -H "Accept: application/yang-data+json" \
     https://HOST-SANDBOX/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1
```

**Sẽ thấy:**

```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet1",
    "description": "MANAGEMENT INTERFACE - DON'T TOUCH ME",
    "type": "iana-if-type:ethernetCsmacd",
    "enabled": true,
    "ietf-ip:ipv4": { "address": [ { "ip": "10.10.20.48", "netmask": "255.255.255.0" } ] }
  }
}
```

**💡 Vì sao:** ⭐ **Cùng một sự thật, hai cách thể hiện.**
⭐ **CLI trả về CHỮ để người đọc** — máy muốn lấy số phải cắt chuỗi *(screen scraping)*.
⭐ **RESTCONF trả về CẤU TRÚC** — máy lấy `["enabled"]` là xong, không bao giờ nhầm.
⭐ **Đó chính là toàn bộ lý do YANG tồn tại** *(§6.3)*.

**✅ Checkpoint:** ⭐ Bạn lấy được JSON và chỉ ra được **giá trị `enabled`**.

---

## Bước C3 — 🔴 CỐ Ý gây lỗi 415

**🎯 Mục tiêu:** ⭐ **gặp trước trong lab cái lỗi sẽ chặn bạn ngoài đời.**

**Gõ** — bỏ `yang-data`, chỉ để `application/json`:

```bash
curl -k -u USER:PASS -i \
     -H "Accept: application/json" \
     https://HOST-SANDBOX/restconf/data/ietf-interfaces:interfaces
```

**Sẽ thấy:** một mã lỗi ⭐ **`415 Unsupported Media Type`** *(hoặc `406`, tuỳ phiên bản)*.

**Gõ lại cho đúng:**

```bash
curl -k -u USER:PASS -i \
     -H "Accept: application/yang-data+json" \
     https://HOST-SANDBOX/restconf/data/ietf-interfaces:interfaces
```

**💡 Vì sao:** 🔴  **RESTCONF đòi đúng `application/yang-data+json`, không nhận `application/json` thuần.**
⭐ **Rất nhiều người mới bị chặn ngay bước đầu vì chỗ này** và tưởng do sai mật khẩu.
⭐ **Cờ `-i` cho bạn thấy cả header phản hồi** — dùng nó khi cần nhìn mã trạng thái.

**✅ Checkpoint:** ⭐ Bạn tạo ra `415` rồi tự sửa được.

---

## Bước C4 — Đổi cấu hình thật bằng RESTCONF

**🎯 Mục tiêu:** ⭐ **chứng minh RESTCONF ghi được, không chỉ đọc.**

> ⚠️ ⭐ **Chỉ đổi `description`.**  **Đừng `shutdown` cổng nào, đừng xoá gì** — sandbox là của chung.
> ⚠️ ⭐ **Đổi trên một interface loopback hoặc interface phụ nếu có** — đừng đụng cổng quản lý.

**Gõ** — tạo `payload.json`:

```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet2",
    "description": "Sua boi LAB 12-C"
  }
}
```

```bash
curl -k -u USER:PASS -X PATCH -i \
     -H "Content-Type: application/yang-data+json" \
     -d @payload.json \
     https://HOST-SANDBOX/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet2
```

**Sẽ thấy:** ⭐ **`HTTP/1.1 204 No Content`**

**💡 Vì sao — chú ý mã `204`, không phải `200`:**

> ⭐ **`204` = "đã làm xong, nhưng không có gì để trả về cho anh".**
> ⭐ Hợp lý: bạn vừa **SỬA**, đâu có hỏi gì mà cần dữ liệu trả lời.
> ⭐ **`200` là khi bạn ĐỌC — có nội dung gửi về.**
>
> ⭐ **Đây là dạng câu hỏi 6.5:** *"PATCH thành công trả về mã nào?"* →  **thường là `204`.**

**Kiểm chứng** — đọc lại bằng bước C2, hoặc trên router:

```
Router# show running-config | section interface GigabitEthernet2
 description Sua boi LAB 12-C          ← ⭐ đã đổi thật
```

**✅ Checkpoint:** ⭐ Bạn nhận `204` và  **nhìn thấy mô tả mới trong `show run`** — tức là đã đổi cấu hình thiết bị thật bằng HTTP.

---

# 🧪 LAB 12-D — 🔴 EEM: TỰ VIẾT APPLET

> 📘 **Lý thuyết:** [§8](Module-12-Automation-va-Programmability.md) — đọc hết §8 trước khi làm
> ⏱️ **3 giờ** · 🧰 ⭐ **EVE-NG — 1 con vIOS, 512 MB** *(dùng lại router của Module-11)*
>
> 🔴  **ĐÂY LÀ BÀI QUAN TRỌNG NHẤT CỦA CẢ MODULE.**
> ⭐ Blueprint mục 6.6 bắt **CONSTRUCT** —  **đề có thể yêu cầu bạn viết applet, không chỉ đọc.**

---

## Bước D1 — Applet đầu tiên: chứng minh EEM còn sống

**🎯 Mục tiêu:** hiểu bộ khung 3 dòng, và biết log của EEM trông thế nào.

**Gõ:**

```
R1(config)# event manager applet CHAO-HOI
R1(config-applet)# event none
R1(config-applet)# action 1.0 syslog msg "Xin chao tu EEM"
R1(config-applet)# end
!
R1# event manager run CHAO-HOI
```

**Sẽ thấy:**

```
R1#
%HA_EM-6-LOG: CHAO-HOI: Xin chao tu EEM
```

**💡 Vì sao:**
⭐ **`event none`** nghĩa là **applet không tự chạy** — chỉ chạy khi bạn gõ `event manager run`.
⭐ **Luôn bắt đầu bằng `event none` khi học hoặc khi viết applet mới:**
⭐ **bạn test được ngay, không phải ngồi chờ sự kiện thật xảy ra.**

⭐ Chú ý định dạng log:  **`%HA_EM-6-LOG: <tên applet>: <nội dung>`** —
nhớ mặt nó để sau này tìm trong `show logging`.

**✅ Checkpoint:** ⭐ Thấy dòng `%HA_EM-6-LOG` có tên applet của bạn.

---

## Bước D2 — 🔴 TỰ TAY TÁI HIỆN BẪY THỨ TỰ ACTION

**🎯 Mục tiêu:** ⭐ **đây là bước giá trị nhất bài 12-D.**
⭐ Bạn sẽ **không bao giờ quên bẫy này** vì đã tự nhìn thấy nó.

**Gõ** — cố ý đánh số kiểu "tự nhiên":

```
R1(config)# event manager applet BAY-THU-TU
R1(config-applet)# event none
R1(config-applet)# action 1  syslog msg "BUOC MOT"
R1(config-applet)# action 2  syslog msg "BUOC HAI"
R1(config-applet)# action 10 syslog msg "BUOC MUOI"
R1(config-applet)# end
!
R1# event manager run BAY-THU-TU
```

**Sẽ thấy** — 🔴 **KHÔNG phải thứ tự bạn mong đợi:**

```
%HA_EM-6-LOG: BAY-THU-TU: BUOC MOT
%HA_EM-6-LOG: BAY-THU-TU: BUOC MUOI     ← 🔴 CHẠY TRƯỚC "BUOC HAI"!
%HA_EM-6-LOG: BAY-THU-TU: BUOC HAI
```

**💡 Vì sao:**

> 🔴  **IOS sắp xếp nhãn action như SẮP TỪ ĐIỂN, không phải như sắp SỐ.**
>
> ⭐ So sánh từng ký tự:  **`"1"` < `"10"` < `"2"`** — vì ký tự `1` đứng trước ký tự `2`.
> ⭐ Y hệt cách từ điển xếp **"an"** trước **"b"** dù "an" dài hơn.

**Gõ tiếp** — sửa lại cho đúng:

```
R1(config)# no event manager applet BAY-THU-TU
R1(config)# event manager applet THU-TU-DUNG
R1(config-applet)# event none
R1(config-applet)# action 1.0  syslog msg "BUOC MOT"
R1(config-applet)# action 2.0  syslog msg "BUOC HAI"
R1(config-applet)# action 10.0 syslog msg "BUOC MUOI"
R1(config-applet)# end
!
R1# event manager run THU-TU-DUNG
```

**Sẽ thấy** — giờ đã đúng:

```
%HA_EM-6-LOG: THU-TU-DUNG: BUOC MOT
%HA_EM-6-LOG: THU-TU-DUNG: BUOC HAI
%HA_EM-6-LOG: THU-TU-DUNG: BUOC MUOI
```

> ⭐ **Đó là lý do mọi tài liệu Cisco đều viết `1.0`, `2.0`, `3.0`** — **không phải cho đẹp.**

**✅ Checkpoint:** 🔴  **Bạn đã tận mắt thấy `action 10` chạy trước `action 2`**, và giải thích được vì sao.

---

## Bước D3 — Applet phản ứng với sự kiện thật

**🎯 Mục tiêu:** để applet **tự chạy** khi một cổng chết.

**Gõ:**

```
R1(config)# event manager applet CONG-CHET
R1(config-applet)# event syslog pattern "Interface GigabitEthernet0/1, changed state to down"
R1(config-applet)# action 1.0 syslog msg "EEM: Gi0/1 vua chet - dang thu thap"
R1(config-applet)# action 2.0 cli command "enable"
R1(config-applet)# action 3.0 cli command "show interfaces GigabitEthernet0/1"
R1(config-applet)# action 4.0 syslog msg "EEM: da chup lai hien trang"
R1(config-applet)# end
```

**Tạo sự kiện:**

```
R1(config)# interface GigabitEthernet0/1
R1(config-if)# shutdown
```

**Sẽ thấy:**

```
%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to administratively down
%HA_EM-6-LOG: CONG-CHET: EEM: Gi0/1 vua chet - dang thu thap
%HA_EM-6-LOG: CONG-CHET: EEM: da chup lai hien trang
```

**💡 Vì sao:** ⭐ **`action 2.0 cli command "enable"` là BẮT BUỘC** *(Bẫy 2, §8.5)* —
⭐ **phiên CLI của EEM bắt đầu ở chế độ user EXEC**, y như bạn vừa telnet vào.
⭐ **Không có `enable` thì lệnh `show interfaces` ở dòng 3.0 sẽ thất bại.**

> ⭐ **Thử cho hỏng một lần:**  **xoá dòng `action 2.0` rồi `shutdown` lại.**
> ⭐ **Tự tay làm hỏng một lần thì nhớ lâu hơn đọc mười lần.**

> ⚠️ ⭐ **Nếu applet không chạy:**  **so chính xác chuỗi trong `pattern` với dòng syslog thật.**
> ⭐ Mỗi nền tảng ghi hơi khác nhau.  **Cách chắc ăn: `shutdown` trước, xem dòng log thật hiện ra sao,
> rồi mới chép đúng đoạn đó vào `pattern`.**

**✅ Checkpoint:** ⭐ Applet **tự chạy** khi bạn `shutdown`, không cần gọi tay.

---

## Bước D4 — Tự sao lưu mỗi khi có người lưu cấu hình

**🎯 Mục tiêu:** viết applet **có giá trị thật ngoài đời**.

**Gõ:**

```
R1(config)# event manager applet BACKUP-KHI-LUU
R1(config-applet)# event cli pattern "write mem.*" sync no skip no
R1(config-applet)# action 1.0 syslog msg "EEM: co nguoi vua luu config"
R1(config-applet)# action 2.0 cli command "enable"
R1(config-applet)# action 3.0 cli command "show running-config | redirect flash:backup-config.txt"
R1(config-applet)# action 4.0 syslog msg "EEM: da sao luu ra flash:backup-config.txt"
R1(config-applet)# end
!
R1# write memory
```

**Sẽ thấy:**

```
Building configuration...
[OK]
%HA_EM-6-LOG: BACKUP-KHI-LUU: EEM: co nguoi vua luu config
%HA_EM-6-LOG: BACKUP-KHI-LUU: EEM: da sao luu ra flash:backup-config.txt
```

**Kiểm chứng file đã được tạo:**

```
R1# dir flash:
    -rw-        4521   <ngay gio>   backup-config.txt      ← ⭐ có thật
```

**💡 Vì sao:**

| Tham số | Nghĩa | Nếu đổi |
|---|---|---|
| ⭐ **`sync no`** | **Applet chạy song song, không chặn lệnh** | `sync yes` → applet chạy TRƯỚC và có quyền chặn |
| **`skip no`** | **Lệnh `write memory` vẫn chạy bình thường** | `skip yes` → 🔴 **lệnh gốc BỊ BỎ QUA** |

> ⭐ **Đây là applet đầu tiên bạn viết mà có giá trị thật:**
> ⭐ **nó giải quyết vấn đề "ai đó sửa config rồi lưu, hôm sau mạng hỏng, không ai biết trước đó thế nào".**

**✅ Checkpoint:** ⭐ File `backup-config.txt` xuất hiện trong `dir flash:` sau khi bạn `write memory`.

---

## Bước D5 — ⚠️ Applet CHẶN một lệnh

**🎯 Mục tiêu:** thấy `sync yes` và `$_exit_status` — thứ khiến EEM mạnh hơn mọi công cụ khác.

> 🔴  **TRƯỚC KHI LÀM BƯỚC NÀY:**
> ⭐ **Mở SẴN một phiên console thứ hai vào R1 và để đó.**
> ⭐ **Nếu applet viết sai làm bạn tự khoá mình, bạn còn đường vào để xoá nó.**
>  **Trong EVE-NG thì xấu nhất là khởi động lại node.** 🔴  **Ngoài đời đây là lỗi rất đắt.**

**Gõ:**

```
R1(config)# event manager applet CHAN-RELOAD
R1(config-applet)# event cli pattern "^reload" sync yes
R1(config-applet)# action 1.0 syslog msg "EEM: CO NGUOI DINH RELOAD!"
R1(config-applet)# action 2.0 set _exit_status "0"
R1(config-applet)# end
!
R1# reload
```

**Sẽ thấy** — ⭐ **lệnh `reload` KHÔNG chạy**, thiết bị không hỏi "Proceed with reload?" nữa:

```
%HA_EM-6-LOG: CHAN-RELOAD: EEM: CO NGUOI DINH RELOAD!
R1#
```

**💡 Vì sao:**

| `$_exit_status` | Nghĩa |
|:---:|---|
| **`0`** | 🔴  **KHÔNG cho lệnh chạy** |
| ⭐ **`1`** | **Cho lệnh chạy bình thường** |

> ⭐ **`sync yes` nghĩa là applet chạy TRƯỚC lệnh và có quyền quyết định lệnh có được thực thi không.**
> ⭐ Đây là thứ **script bên ngoài không bao giờ làm được** — script chỉ chạy *sau khi* việc đã xảy ra.

**⭐ DỌN DẸP — bắt buộc, đừng bỏ qua:**

```
R1(config)# no event manager applet CHAN-RELOAD
```

**✅ Checkpoint:** ⭐ `reload` bị chặn ·  **sau đó bạn đã xoá applet** *(đừng thực sự reload thiết bị)*.

---

## Bước D6 — Kiểm chứng và gỡ lỗi

**🎯 Mục tiêu:** thuộc 3 lệnh verify — đề hỏi, và bạn cần khi lab hỏng.

**Gõ:**

```
R1# show event manager policy registered
No.  Class    Type    Event Type   Trap  Time Registered   Name
1    applet   user    none         Off   ...               CHAO-HOI
2    applet   user    syslog       Off   ...               CONG-CHET
3    applet   user    cli          Off   ...               BACKUP-KHI-LUU

R1# show event manager statistics policy
                                        Average    Maximum
No.  Class   Triggered  Suppressed  Run Time   Run Time   Name
1    applet          2           0     0.012      0.020   CHAO-HOI
2    applet          1           0     0.340      0.340   CONG-CHET

R1# show running-config | section event manager
```

**💡 Vì sao — đây là quy trình gỡ lỗi EEM, đi đúng thứ tự:**

```
① show event manager policy registered
   └─ KHÔNG thấy tên applet?   → 🔴 cú pháp sai, IOS đã từ chối ngay lúc gõ
                                  → gõ lại từng dòng, xem dòng nào báo lỗi

② show event manager statistics policy
   └─ Triggered = 0?           → 🔴 event KHÔNG BAO GIỜ KHỚP
                                  → sai pattern (Bẫy 5)
                                  → test nhanh: đổi tạm sang "event none"
                                    rồi "event manager run"

③ Chạy rồi mà kết quả sai?    → 🔴 Bẫy 1 (thứ tự action)
                                  🔴 Bẫy 2 (thiếu enable)
                                  🔴 Bẫy 3 (quá 20 giây - maxrun)
                                  🔴 Bẫy 4 (AAA chặn)
```

**✅ Checkpoint:** ⭐ Bạn đọc được cột **`Triggered`** và biết nó nói lên điều gì.

---

# 🧪 LAB 12-E — Ansible và "idempotent"

> 📘 **Lý thuyết:** [§11](Module-12-Automation-va-Programmability.md)
> ⏱️ **1 giờ** · 🧰 ⭐ **Máy Linux/WSL + R1 trong EVE-NG** *(cần thông được mạng từ máy bạn tới R1)*
>
> ⭐ **Bài này là BỔ TRỢ.**  Blueprint chỉ bắt *Compare*, không bắt cấu hình.
> ⭐ **Làm được thì tốt, không làm được cũng không mất điểm** — nhưng nó cho bạn thấy
> **idempotent** bằng mắt, mà đó là khái niệm xuyên suốt cả module.

---

## Bước E1 — Chuẩn bị

**Trên R1** *(để Ansible SSH vào được)*:

```
R1(config)# hostname R1
R1(config)# ip domain-name lab.local
R1(config)# crypto key generate rsa modulus 2048
R1(config)# username ansible privilege 15 secret MatKhauRatDai
R1(config)# line vty 0 4
R1(config-line)# transport input ssh
R1(config-line)# login local
```

**Trên máy bạn (WSL/Linux):**

```bash
pip install ansible
ansible --version
```

**File `inventory.ini`:**

```ini
[routers]
R1 ansible_host=192.168.1.11

[routers:vars]
ansible_user=ansible
ansible_password=MatKhauRatDai
ansible_network_os=cisco.ios.ios
ansible_connection=ansible.netcommon.network_cli
```

**✅ Checkpoint:** `ansible --version` chạy được và bạn **SSH tay** vào R1 thành công.

---

## Bước E2 — 🔴 NHÌN THẤY "idempotent"

**🎯 Mục tiêu:** ⭐ **đây là toàn bộ lý do có bài 12-E.**

**File `them-vlan.yml`:**

```yaml
---
- name: Them VLAN 20
  hosts: routers
  gather_facts: false
  tasks:
    - name: Tao interface loopback 20
      cisco.ios.ios_config:
        lines:
          - description TAO BOI ANSIBLE
        parents: interface Loopback20
```

**Chạy LẦN THỨ NHẤT:**

```bash
ansible-playbook -i inventory.ini them-vlan.yml
```

```
TASK [Tao interface loopback 20] ***
changed: [R1]                          ← ⭐ CHANGED - da tao moi

PLAY RECAP ***
R1 : ok=1  changed=1  unreachable=0  failed=0
```

**Chạy LẦN THỨ HAI — đúng lệnh đó, không sửa gì:**

```bash
ansible-playbook -i inventory.ini them-vlan.yml
```

```
TASK [Tao interface loopback 20] ***
ok: [R1]                               ← ⭐ OK - KHONG lam gi ca!

PLAY RECAP ***
R1 : ok=1  changed=0  unreachable=0  failed=0     ← ⭐ changed = 0
```

**💡 Vì sao — đây là điều quan trọng nhất bài E:**

> 🔴  **Lần hai, Ansible KIỂM TRA TRƯỚC, thấy cấu hình đã đúng rồi nên KHÔNG làm gì cả.**
> ⭐ **`changed=0` chính là "idempotent" mà bạn đã gặp ba lần trong lý thuyết** *(§5.1, §11.1, §11.4)* —
> ⭐ **giờ bạn nhìn thấy nó bằng mắt.**
>
> ⭐ **Đối chiếu với script gõ CLI thô:**  **script sẽ gõ lại y nguyên lần hai, không cần biết đã có chưa.**
> ⭐ **Khác biệt đó là thứ cho phép bạn DÁM chạy lại playbook khi nó lỡ đứt giữa chừng.**

**✅ Checkpoint:** ⭐ Bạn thấy **`changed=1` ở lần một** và **`changed=0` ở lần hai**, và giải thích được vì sao.

---

# ✅ TỰ CHẤM LAB 12

> ⭐ **Đánh dấu từng ô. Chưa tick hết thì đừng sang Module-13.**

## Phần bắt buộc

| ☐ | Việc | Bài |
|:---:|---|:---:|
| ☐ | Giải thích được vì sao `len()` = 3 mà `[3]` lại lỗi | A1 |
| ☐ | Bóc được giá trị lồng 3 bậc **không nhìn đáp án** | A2 |
| ☐ | Kể được **3 lỗi** trong file JSON sai mà không nhìn bảng | A3 |
| ☐ | Xin được token DNAC, nhận `200` | B1 |
| ☐ | 🔴 **Tự tạo ra `401` theo ý muốn** và giải thích vì sao không phải `403` | B2 |
| ☐ | In ra được tên + IP thiết bị từ payload | B3 |
| ☐ | Thấy khối `<hello>` ở cổng 830 | C1 |
| ☐ | 🔴 **Trả lời được: máy sandbox có hỗ trợ `candidate` không?** | C1 |
| ☐ | Lấy được cấu hình interface bằng RESTCONF | C2 |
| ☐ | 🔴 **Tự tạo ra `415` rồi tự sửa** | C3 |
| ☐ | Đổi được `description` thật, nhận `204` | C4 |
| ☐ | 🔴  **Viết được applet EEM đầu tiên và chạy tay** | D1 |
| ☐ | 🔴  **TẬN MẮT thấy `action 10` chạy TRƯỚC `action 2`** | D2 |
| ☐ | Applet tự chạy khi `shutdown` cổng | D3 |
| ☐ | Tạo được `backup-config.txt` trong flash khi `write memory` | D4 |
| ☐ | Chặn được lệnh `reload` bằng `sync yes` — **và đã xoá applet sau đó** | D5 |
| ☐ | Đọc được cột `Triggered` | D6 |

## Phần bổ trợ *(không bắt buộc)*

| ☐ | Việc | Bài |
|:---:|---|:---:|
| ☐ | Chạy được playbook Ansible đầu tiên | E1–E2 |
| ☐ | 🔴 Thấy `changed=1` lần một và `changed=0` lần hai | E2 |

---

## 🔴 Bài kiểm tra cuối — không nhìn tài liệu

> ⭐ **Đây mới là thứ chứng minh bạn đã nắm Domain 6.0.**
> ⭐ **Đóng hết tài liệu. Mở một con router trắng. Làm trong 15 phút:**

| # | Yêu cầu |
|:---:|---|
| 1 | ⭐ **Viết một applet EEM tên `TU-KIEM-TRA`**, chạy bằng tay, ghi 3 dòng syslog **theo đúng thứ tự 1 → 2 → 3** |
| 2 | ⭐ **Viết một applet chạy khi có người gõ `show version`**, ghi lại vào syslog |
| 3 | ⭐ **Không nhìn tài liệu, nói ra:** NETCONF dùng cổng nào · RESTCONF cổng nào · cái nào rollback được |
| 4 | ⭐ **Nói ra:** `401` khác `403` chỗ nào · `PUT` khác `PATCH` chỗ nào |
| 5 | ⭐ **Nói ra:** Ansible agent hay agentless · Puppet thì sao |

<details><summary>⭐ Đáp án bài 1 và 2</summary>

**Bài 1:**

```
event manager applet TU-KIEM-TRA
 event none
 action 1.0 syslog msg "MOT"
 action 2.0 syslog msg "HAI"
 action 3.0 syslog msg "BA"
```

⭐ **Điểm chấm:**  **nhãn phải là `1.0`/`2.0`/`3.0`** — viết `1`/`2`/`3` thì ở đây vẫn đúng thứ tự,
nhưng ⭐ **thành thói quen sai khi có action thứ 10.**

**Bài 2:**

```
event manager applet BAT-SHOW-VERSION
 event cli pattern "show ver.*" sync no skip no
 action 1.0 syslog msg "EEM: co nguoi vua go show version"
```

⭐ **Điểm chấm:**  **`.*` để khớp cả `show ver` lẫn `show version`** ·  **`skip no` để lệnh gốc vẫn chạy.**

**Bài 3–5:** xem [§17.1 — bảng đúc kết](Module-12-Automation-va-Programmability.md).
</details>

---

> 🧭 **Xong LAB 12 = bạn đã phủ 100% blueprint ENCOR.**
>
> ⭐ **Tiếp theo:** quay lại [§12.4 của lý thuyết](Module-12-Automation-va-Programmability.md) để **tự vẽ lại kiến trúc**,
> rồi sang **Module-13 — Ôn thi & Chiến thuật phòng thi**.
