# Tài liệu tham khảo — Cisco DOC chính thống · Video · Diễn đàn uy tín

> Nguyên tắc dùng file này: **repo này là xương sống, các nguồn dưới đây là thịt.**
> Đừng mở hết 20 nguồn cùng lúc — đó là cách chắc chắn nhất để bị ngợp rồi bỏ.
> Mỗi module tôi sẽ chỉ đúng 2–3 link cần đọc. File này để bạn tra khi muốn đào sâu.

> ⚠️ **Link Cisco hay bị đổi đường dẫn.** Nếu link 404, copy tên tài liệu rồi tìm trên
> `cisco.com` hoặc Google — tài liệu vẫn còn, chỉ chuyển chỗ.

---

## 1. Nguồn CHÍNH THỨC của Cisco — ưu tiên số 1

### 1.1 Trang phải bookmark ngay

| Nguồn | Link | Dùng để làm gì | Miễn phí |
|---|---|---|:---:|
| **Trang đề thi 350-401 chính thức** | https://www.cisco.com/c/en/us/training-events/training-certifications/exams/current-list/encor-350-401.html | **Xác nhận blueprint hiện hành** trước khi học/book thi. Có PDF exam topics tải về | ✅ |
| **Cisco Learning Network (CLN)** | https://learningnetwork.cisco.com | Diễn đàn CHÍNH THỨC của Cisco. Có **study group 350-401** miễn phí, người đã thi chia sẻ kinh nghiệm | ✅ |
| **Cisco Community** | https://community.cisco.com | Forum kỹ thuật lớn nhất, có kỹ sư Cisco (VIP/Employee) trả lời. Chỗ hỏi khi lab lỗi | ✅ |
| **Cisco DevNet** | https://developer.cisco.com | Toàn bộ phần Automation (15% đề). Có sandbox + learning lab | ✅ |
| **Cisco DevNet Sandbox** | https://developer.cisco.com/site/sandbox/ | **Cực quan trọng với bạn** — thiết bị thật online: IOS-XE, Cat9k, DNA Center, vManage. Bù cho việc PC 16 GB không dựng nổi | ✅ |
| **Cisco Live On-Demand** | https://www.ciscolive.com/on-demand.html | **Mỏ vàng bị đánh giá thấp nhất.** Slide + video các session BRKxxx do chính kỹ sư Cisco trình bày | ✅ (cần đăng ký free) |
| **Cisco Design Zone (CVD)** | https://www.cisco.com/c/en/us/solutions/design-zone.html | Validated Design — cách Cisco thật sự khuyên thiết kế mạng. Phần Architecture 15% lấy từ đây | ✅ |
| **Cisco Feature Navigator** | https://cfnng.cisco.com | Tra feature X có trên IOS version nào / platform nào. Dùng khi lab báo "invalid command" | ✅ |
| **Cisco U.** | https://u.cisco.com | Nền tảng học chính thức mới của Cisco, có khóa ENCOR + lab tích hợp | ⭕ Có free tier |
| **Cisco Support Config Guides** | https://www.cisco.com/c/en/us/support/all/index.html | Configuration Guide theo platform — **nguồn chuẩn nhất về cú pháp lệnh** | ✅ |

### 1.2 Configuration Guide theo chủ đề — đọc khi cần cú pháp chính xác

Cách tra: vào `cisco.com/support` → chọn platform (VD *Catalyst 9300*) → **Configure** → *Configuration Guides* → chọn IOS-XE version → tìm chương.

| Module | Chương Config Guide cần tìm | Từ khóa search |
|---|---|---|
| M01 Forwarding | *IP Switching / CEF Configuration Guide* | `IOS-XE CEF configuration guide` |
| M02 Layer 2 | *Layer 2/3 Configuration Guide* → chương STP, MST, EtherChannel | `Catalyst 9300 spanning-tree configuration guide` |
| M03 Routing | *IP Routing Configuration Guide* | `IOS-XE IP routing configuration guide` |
| M04 OSPF | *IP Routing: OSPF Configuration Guide* | `IOS-XE OSPF configuration guide` |
| M05 BGP | *IP Routing: BGP Configuration Guide* + **BGP Best Path Selection Algorithm** (doc kinh điển) | `BGP best path selection algorithm cisco` |
| M06 FHRP/NAT | *First Hop Redundancy Protocols Config Guide* · *IP Addressing: NAT Config Guide* | `IOS-XE HSRP configuration guide` |
| M07 Wireless | *Cisco Catalyst 9800 Series Wireless Controller Software Configuration Guide* | `Catalyst 9800 configuration guide` |
| M08 Overlay | *VXLAN Config Guide* · *LISP Config Guide* · *VPN/IPsec Config Guide* | `IOS-XE VXLAN configuration guide` |
| M09 QoS | *QoS Configuration Guide* + **QoS Design Guide (Design Zone)** | `cisco enterprise QoS design guide` |
| M10 Security | *Security Configuration Guide* → chương AAA, 802.1X, CoPP · **Cisco Guide to Harden IOS Devices** | `cisco guide to harden cisco ios devices` |
| M11 Assurance | *Flexible NetFlow Config Guide* · *SNMP Config Guide* · *IP SLAs Config Guide* | `IOS-XE flexible netflow configuration guide` |
| M12 Automation | *Programmability Configuration Guide* (chương NETCONF/RESTCONF) + DevNet | `IOS-XE programmability configuration guide` |

### 1.3 Tài liệu Cisco kinh điển — nên đọc dù không thi

| Tài liệu | Vì sao đáng đọc |
|---|---|
| **BGP Best Path Selection Algorithm** | Bản gốc của "13 bước path selection". Đề ENCOR hỏi trực tiếp từ đây |
| **Cisco Guide to Harden Cisco IOS Devices** | Toàn bộ khối hardening ở Module-10 nằm trong doc này |
| **OSPF Design Guide** | Giải thích *vì sao* có area, stub, virtual-link — không chỉ *cách* cấu hình |
| **Enterprise QoS Solution Reference Network Design (SRND)** | Chuẩn mực về QoS. Bảng marking EF/AF41/CS6 lấy từ đây |
| **Campus LAN and Wireless LAN Design Guide (CVD)** | Nền của toàn bộ Module-09 |
| **SD-Access Solution Design Guide (CVD)** | Đọc 20 trang đầu là đủ cho đề |

---

## 2. Sách

### 2.1 Sách chính — bắt buộc có

| Sách | Tác giả | Ghi chú |
|---|---|---|
| **CCNP and CCIE Enterprise Core ENCOR 350-401 Official Cert Guide** (Cisco Press) | Brad Edgeworth, Ramiro Garza Rios, David Hucaby, Jason Gooley | Sách nền của kỳ thi. ~1100 trang. Kèm Pearson Test Prep (bank câu hỏi). **Mua bản mới nhất** — kiểm tra edition khớp blueprint hiện hành |

> 💡 **Cách dùng OCG cùng repo này:** repo này cho bạn **thứ tự học + lab step-by-step + bảng đúc kết**.
> OCG cho bạn **độ sâu và độ đầy đủ**. Mỗi module trong repo tôi ghi rõ nên đọc chương nào của OCG.
> Đừng đọc OCG tuyến tính từ trang 1 — đó là cách bỏ ngang ở trang 200.

### 2.2 Sách bổ trợ — chỉ mua khi thấy yếu đúng chỗ đó

| Yếu ở đâu | Sách | Khi nào cần |
|---|---|---|
| Routing (OSPF/BGP) chưa thấm | *Routing TCP/IP Volume 1 & 2* — Jeff Doyle | Nếu tuần 7–10 học mãi không vào |
| Wireless mù tịt | *CWNA Certified Wireless Network Administrator Study Guide* | Chỉ đọc chương RF + 802.11, bỏ phần còn lại |
| Automation | *Network Programmability and Automation* — Edelman, Lowe, Oswalt (O'Reilly) | Tuần 18–19. **Bạn có thể bỏ qua** vì đã có repo network-automation-mastery |
| SD-WAN | *Cisco Software-Defined Wide Area Networks* (Cisco Press) | Chỉ nếu định thi concentration ENSDWI |
| Tư duy thiết kế | *Optimal Routing Design* (Cisco Press) | Đọc sau khi đỗ, cho công việc |

---

## 3. Video

### 3.1 Video theo mức độ

| Nguồn | Kiểu | Chi phí | Phù hợp với bạn ở đâu |
|---|---|---|---|
| **Jeremy's IT Lab** (YouTube) | CCNA full course, free, dạy rất chậm và rõ | **$0** | ⭐ **Tuần 1–2 (Phase 0)** — nền tảng VLAN/STP/OSPF cơ bản. Đúng level bạn đang cần vá |
| **David Bombal** (YouTube) | Networking + lab EVE-NG/GNS3 | **$0** | Tuần 0 — có video dựng EVE-NG. Và nhiều video khái niệm lẻ |
| **Keith Barker** (YouTube) | Giải thích khái niệm ngắn gọn, rất dễ hiểu | **$0** | Khi bí 1 khái niệm cụ thể — search `Keith Barker + <chủ đề>` |
| **CBT Nuggets — ENCOR (Knox Hutchinson)** | Khóa ENCOR full, bám blueprint, dễ vào | ~$59/tháng | ⭐ Nếu chọn 1 khóa video duy nhất thì chọn cái này |
| **Kevin Wallace Training** | Gọn, đi thẳng vào đề, hợp ôn cuối | ~$50/tháng | ⭐ **Tuần 20** — ôn nước rút |
| **INE (Brian McGahan)** | Sâu nhất, chuẩn CCIE | ~$99/tháng | Chỉ nếu bạn định lên CCIE. Với mục tiêu ENCOR là **quá sâu** |
| **Cisco U.** | Chính thức Cisco, có lab | Có free tier | Phần SD-Access/SD-WAN/DNAC — chính chủ nói chuẩn nhất |
| **Cisco Live On-Demand** | Session kỹ thuật của kỹ sư Cisco | **$0** | ⭐ Xem session `BRKCRS`/`BRKENT` về chủ đề đang học. Chất lượng cao hơn nhiều khóa trả tiền |

### 3.2 Session Cisco Live nên tìm (search trên ciscolive.com)

| Chủ đề đang học | Từ khóa search |
|---|---|
| Layer 2 / STP | `Cisco Live spanning tree deep dive` |
| OSPF | `Cisco Live OSPF deployment best practices` |
| BGP | `Cisco Live BGP best practices enterprise` |
| Campus design | `Cisco Live campus network design` |
| SD-Access | `Cisco Live SD-Access design deployment` |
| SD-WAN | `Cisco Live SD-WAN architecture` |
| Wireless | `Cisco Live wireless 802.11 design` |
| QoS | `Cisco Live enterprise QoS design` |
| Programmability | `Cisco Live IOS-XE programmability NETCONF RESTCONF` |
| Troubleshooting | `Cisco Live troubleshooting campus` |

> 💡 Cách dùng: mỗi module, tìm 1 session Cisco Live tương ứng, **tải slide PDF** (thường 100–200 trang,
> chất lượng như sách) và xem video ở tốc độ 1.5x. Đây là nguồn free tốt nhất tồn tại.

---

## 4. Diễn đàn & cộng đồng uy tín

### 4.1 Nơi HỎI khi bị kẹt — xếp theo thứ tự nên dùng

| Nơi | Link | Hỏi gì ở đây | Chất lượng trả lời |
|---|---|---|---|
| **Cisco Learning Network — Study Group 350-401** | https://learningnetwork.cisco.com | Câu hỏi về **đề thi**, blueprint, kinh nghiệm thi | ⭐⭐⭐⭐ Chính thức |
| **Cisco Community** | https://community.cisco.com | Câu hỏi **kỹ thuật**: lab lỗi, output lạ, cú pháp lệnh | ⭐⭐⭐⭐⭐ Có kỹ sư Cisco |
| **r/ccnp** (Reddit) | https://reddit.com/r/ccnp | Kinh nghiệm ôn, review khóa học, "tôi vừa đỗ — đây là cách tôi học" | ⭐⭐⭐⭐ Thật, thẳng |
| **r/networking** (Reddit) | https://reddit.com/r/networking | Câu hỏi **thực chiến đi làm**, không phải chuyện thi cử | ⭐⭐⭐⭐⭐ Toàn người làm thật |
| **r/ccna** (Reddit) | https://reddit.com/r/ccna | Tuần 1–2, câu hỏi nền tảng | ⭐⭐⭐ |
| **EVE-NG Community Forum** | https://www.eve-ng.net/forum/ | Lỗi EVE-NG, node không boot, image không nhận | ⭐⭐⭐⭐ |
| **Cisco DevNet Community** | https://developer.cisco.com/support/ | Lỗi API, sandbox, RESTCONF | ⭐⭐⭐⭐ |
| **VnPro** (Việt Nam) | https://vnpro.vn | Bài viết tiếng Việt, khóa học có người kèm | ⭐⭐⭐ Tiếng Việt |

### 4.2 Cách hỏi để được trả lời (quan trọng — người mới thường hỏi sai cách)

❌ **Đừng hỏi:** *"OSPF của tôi không chạy, giúp với"*

✅ **Hãy hỏi:**
```
Topology: R1 (Gi0/1: 10.0.0.1/30) --- R2 (Gi0/1: 10.0.0.2/30), cùng area 0
Vấn đề: neighbor kẹt ở ExStart, không lên Full
Đã thử: ping được 2 chiều, area khớp, timer khớp
Output:
  R1# show ip ospf neighbor
  <paste output thật>
  R1# show ip ospf interface Gi0/1
  <paste output thật>
Môi trường: EVE-NG, vIOS 15.7(3)M
```
Kèm topology + output + *đã thử gì* → tỉ lệ được trả lời tăng gấp 10 lần.

### 4.3 Blog & tài liệu tự học chất lượng cao

| Nguồn | Link | Ghi chú |
|---|---|---|
| **NetworkLessons.com** (Rene Molenaar) | https://networklessons.com | Giải thích rõ nhất trên internet về STP/OSPF/BGP. Có bài free, membership ~$15/tháng. ⭐ Nếu bí lý thuyết, vào đây trước |
| **Nick Russo — njrusmc.net** | https://njrusmc.net | Notes ENCOR/CCIE **miễn phí**, rất mạnh phần automation & design |
| **ipSpace.net** (Ivan Pepelnjak) | https://blog.ipspace.net | Sâu, thẳng thắn, phá vỡ marketing hype về SDN/SD-WAN. Đọc để **hiểu thật** |
| **Packet Pushers** (podcast) | https://packetpushers.net | Nghe khi đi đường. Giúp hiểu bối cảnh ngành, không phải để thi |
| **Cisco Blogs** | https://blogs.cisco.com | Cập nhật feature mới, SD-Access/SD-WAN |
| **LabEveryday** (Du'An Lightfoot) | YouTube | Automation + lab thực hành, giọng dễ theo |

---

## 5. Nguồn LUYỆN ĐỀ

| Nguồn | Chi phí | Đánh giá | Dùng khi nào |
|---|---|---|---|
| **Boson ExSim-Max for 350-401** | ~$100 | ⭐⭐⭐⭐⭐ **Sát đề nhất, giải thích đáp án cực chi tiết.** Chuẩn vàng để quyết định có book thi hay chưa | Tuần 20. **Đạt ≥85% ổn định qua 3 đề khác nhau mới book thi** |
| **Pearson Test Prep** (kèm sách OCG) | Kèm sách | ⭐⭐⭐⭐ Bám sát sách, tốt để kiểm tra sau mỗi chương | Sau mỗi module |
| **Cisco U. practice** | Có free tier | ⭐⭐⭐ Chính thức | Tuần 20 |
| ⛔ **"Dump" đề thi lậu** | — | **Đừng dùng.** Ba lý do: (1) vi phạm Cisco Certification Agreement, có thể bị hủy cert vĩnh viễn; (2) đề dump thường sai đáp án; (3) học dump thì vào làm việc không dùng được gì | Không bao giờ |

---

## 6. Công cụ lab & tra cứu

| Công cụ | Link | Dùng để |
|---|---|---|
| **EVE-NG Documentation** | https://www.eve-ng.net/index.php/documentation/ | ⭐ **Đọc trước khi làm Module-00.** Cookbook PDF official |
| **Cisco Packet Tracer** | https://www.netacad.com/courses/packet-tracer | Free sau khi đăng ký NetAcad. Lab L2/L3 cơ bản siêu nhẹ, chạy được cả khi máy yếu |
| **Cisco Software Download** | https://software.cisco.com | Nơi tải image chính thức (cần CCO account, một số image cần contract) |
| **Cisco Feature Navigator** | https://cfnng.cisco.com | Tra feature có trên IOS version nào |
| **Cisco Command Lookup Tool** | https://www.cisco.com/c/en/us/support/web/tools/help/command_lookup_tool.html | Tra ý nghĩa 1 lệnh IOS (cần CCO login) |
| **IP Subnet Calculator** | https://www.subnet-calculator.com | Tuần 1–2, dùng cho tới khi tự tính nhẩm được |
| **Wireshark** | https://www.wireshark.org | ⭐ Bắt gói từ EVE-NG. Xem BPDU/OSPF hello/CAPWAP thật — hiểu nhanh hơn đọc sách |

> ⚠️ **Về image Cisco cho EVE-NG:** repo này **không cung cấp và không chỉ nguồn tải image lậu.**
> Đường hợp pháp: (a) CCO account có service contract → tải từ software.cisco.com;
> (b) đăng ký **CML Personal** (~$199/năm) — kèm sẵn image hợp pháp, khỏi phải lo;
> (c) dùng **DevNet Sandbox** (free, thiết bị thật online) + **Packet Tracer** cho lab cơ bản.
> Module-00 §5 nói rõ cách đặt image vào EVE-NG với **bất kỳ image bạn có hợp pháp**.

---

## 7. Lịch dùng tài liệu theo tuần

Bảng này để bạn không phải nghĩ "hôm nay nên mở nguồn nào".

| Tuần | Repo này | Sách OCG | Video | Nguồn khác |
|:---:|---|---|---|---|
| 0 | Module-00 | — | David Bombal (EVE-NG setup) | EVE-NG Documentation |
| 1–2 | Module-P0 | Ch. mở đầu | **Jeremy's IT Lab** (nền tảng) | Packet Tracer nếu EVE-NG chưa xong |
| 3 | Module-01 | Ch. Packet Forwarding | CBT Nuggets | CEF Config Guide |
| 4–5 | Module-02 | Ch. Spanning Tree, EtherChannel | CBT Nuggets | **NetworkLessons** (STP) + Cisco Live STP |
| 6 | Module-03 | Ch. IP Routing | CBT Nuggets | IP Routing Config Guide |
| 7–8 | Module-04 | Ch. OSPF (2 chương) | CBT Nuggets | **NetworkLessons** (OSPF) + OSPF Design Guide |
| 9–10 | Module-05 | Ch. BGP | CBT Nuggets | **BGP Best Path Selection** (doc Cisco) |
| 11 | Module-06 | Ch. FHRP, NAT | CBT Nuggets | FHRP Config Guide |
| 12–13 | Module-07 | Ch. Wireless (2–3 chương) | Cisco U. wireless | DevNet Sandbox WLC + CWNA (chương RF) |
| 14 | Module-08 | Ch. Virtualization, Tunnels | CBT Nuggets | VXLAN/LISP Config Guide + ipSpace |
| 15 | Module-09 | Ch. Architecture, QoS | Cisco U. SD-Access | **Design Zone CVD** + QoS SRND |
| 16 | Module-10 | Ch. Security | CBT Nuggets | Harden IOS Devices guide |
| 17 | Module-11 | Ch. Network Assurance | CBT Nuggets | Flexible NetFlow Config Guide |
| 18–19 | Module-12 | Ch. Automation (2 chương) | **DevNet Learning Labs** | Nick Russo notes + repo network-automation-mastery của bạn |
| 20 | Module-13 | Review toàn bộ + Pearson Test Prep | **Kevin Wallace** (ôn nhanh) | **Boson ExSim-Max** + r/ccnp exam reports |

---

## 8. 3 nguồn nếu chỉ được chọn 3

Vì tôi biết bảng trên dài và bạn sẽ hỏi "vậy tối thiểu cần gì":

| # | Nguồn | Vì sao |
|:---:|---|---|
| 1 | **Repo này + lab EVE-NG** | Thứ tự học, lab có hướng dẫn, bảng đúc kết. Đây là xương sống |
| 2 | **Sách OCG 350-401** | Độ sâu và đầy đủ. Repo không thay được sách 1100 trang |
| 3 | **Boson ExSim-Max** | Không có nó thì bạn không biết mình đã sẵn sàng chưa. Đừng đóng $400 phí thi khi chưa biết |

Ba thứ này ≈ **$550** và **đủ để đỗ**. Mọi thứ khác là bổ trợ.
