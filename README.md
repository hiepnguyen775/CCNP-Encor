# CCNP ENCOR 350-401 — Tự học từ nền tảng đến thi đỗ

> Bộ tài liệu tự học **CCNP Enterprise Core (350-401 ENCOR)** viết cho người tự học,
> lab chạy trên **EVE-NG Community + VMware Workstation**, ngân sách **PC 16 GB RAM**.
>
> Mục tiêu kép: **thi đỗ 350-401** *và* **làm được việc thật** trên hạ tầng mạng doanh nghiệp.

---

## 1. Đọc cái này trước — lời thật của người dạy

Tôi sẽ không nói với bạn "3 tháng có CCNP". Đây là những gì thật:

| Điều bạn cần biết | Sự thật |
|---|---|
| ENCOR khó cỡ nào? | Đây là **đề CCNP**, dùng làm cửa vào CCIE Enterprise. Nó không phải CCNA nâng cao — nó rộng gấp 3 lần CCNA và hỏi sâu hơn. |
| Học bao lâu? | Với trình độ hiện tại của bạn (biết VLAN/IP, mờ routing) và **10 giờ/tuần** → **20 tuần** là con số thật. Ai nói 8 tuần là đang bán khóa học. |
| Đọc sách là đủ? | Không. **Lý do số 1 người tự học rớt ENCOR là học chay không lab.** Đề có câu simulation và rất nhiều câu "xem output này, chuyện gì đang xảy ra" — không lab thì không đọc nổi output. |
| Có phải học hết mọi thứ? | Không. Đề chia theo tỷ trọng %, có phần chỉ hỏi khái niệm (SD-WAN, SD-Access) chứ không bắt cấu hình. Repo này chỉ ra rõ chỗ nào **cấu hình được**, chỗ nào **chỉ cần hiểu**. |
| Máy 16 GB có lab được không? | **Được ~85% nội dung ENCOR.** Phần không dựng nổi (Cat9kv 18 GB, Nexus 9000v 8 GB, WLC + AP thật, SD-WAN on-prem) tôi chỉ ra **Plan B miễn phí** bằng Cisco DevNet Sandbox. |

### Nguyên tắc học của repo này

1. **Không học chay.** Mỗi module có LAB. Đọc xong mà không lab = coi như chưa học module đó.
2. **Hiểu bản chất trước, gõ lệnh sau.** Học "vì sao OSPF cần DR/BDR" quan trọng hơn học `ip ospf priority`.
3. **Không nhảy cóc.** Repo xếp thứ tự học ≠ thứ tự blueprint. Blueprint xếp theo domain, repo xếp theo **thứ tự dễ hiểu dần**.
4. **Lab phải chạy được trên máy bạn.** Mọi topology đều ghi rõ RAM cần. Không có lab nào đòi máy 64 GB.

---

## 2. Cấu hình lab đã chốt

| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| Máy host | PC ở nhà, **16 GB RAM** | Cấp 10–12 GB cho EVE-NG, để lại 4–6 GB cho Windows |
| Hypervisor | **VMware Workstation** | Phải bật *Virtualize Intel VT-x/EPT* — xem Module-00 |
| Network emulator | **EVE-NG Community Edition** (OVA) | Free, web UI kéo-thả, dễ nhất cho người mới |
| Image chính | vIOS / vIOS-L2 / IOL (nhẹ), CSR1000v (nặng hơn) | Bạn tự chuẩn bị image hợp pháp — xem Module-00 §5 |
| Plan B miễn phí | **Cisco DevNet Sandbox** + Packet Tracer | Cho DNA Center, vManage, RESTCONF, Cat9k thật |

---

## 3. Mục lục repo

### Giai đoạn chuẩn bị

| File | Nội dung | Tuần |
|---|---|---|
| [ROADMAP.md](ROADMAP.md) | **Lộ trình 20 tuần dạng bảng** — đọc ngay sau README | — |
| [Module-00-Setup-Lab-EVE-NG.md](Module-00-Setup-Lab-EVE-NG.md) | Dựng lab EVE-NG trên VMware từ số 0 | Tuần 0 |
| [Module-P0-Nen-tang-Ready-for-ENCOR.md](Module-P0-Nen-tang-Ready-for-ENCOR.md) | Vá nền tảng: CLI Cisco, VLAN/trunk, STP, cách chọn đường, static/OSPF cơ bản, NAT, ACL | Tuần 1–2 |

### Khối Infrastructure — 30% đề, nặng nhất

| File | Nội dung | Tuần |
|---|---|---|
| [Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md](Module-01-Packet-Forwarding-va-Kien-truc-Thiet-bi.md)<br>+ 🧪 [**Module-01-LAB.md**](Module-01-LAB.md) | Control/Data/Management plane, Process switching → CEF, RIB vs FIB, CAM/TCAM, SDM<br>⭐ **Có trang TÓM TẮT 10 phút + lộ trình đọc 3 mức + LAB tách riêng** | Tuần 3 |
| [Module-02-Layer2-STP-RSTP-MST-EtherChannel.md](Module-02-Layer2-STP-RSTP-MST-EtherChannel.md) | STP sâu, RSTP, MST, các loại Guard + UDLD, EtherChannel LACP/PAgP | Tuần 4–5 |
| [Module-03-IP-Routing-Nen-tang.md](Module-03-IP-Routing-Nen-tang.md) | Bảng định tuyến, AD, longest-prefix, static + **IP SLA/track**, redistribute, EIGRP↔OSPF | Tuần 6 |
| [Module-04A-OSPF-Nen-tang-va-LSDB.md](Module-04A-OSPF-Nen-tang-va-LSDB.md) | Neighbor states, network type, **DR/BDR**, **LSA type 1–3**, đọc LSDB | Tuần 7 |
| [Module-04B-OSPF-Area-Summarization-OSPFv3.md](Module-04B-OSPF-Area-Summarization-OSPFv3.md) | LSA 4–5–7, **area type** (stub/NSSA), **summarization**, filtering, virtual-link, auth, OSPFv3 | Tuần 8 |
| [Module-05A-BGP-Nen-tang-va-eBGP-Peering.md](Module-05A-BGP-Nen-tang-va-eBGP-Peering.md) | eBGP peering, 6 neighbor state, 3 bảng BGP, `network` statement, attribute | Tuần 9 |
| [Module-05B-BGP-Path-Selection-va-Filtering.md](Module-05B-BGP-Path-Selection-va-Filtering.md) | ⭐ **13 bước path selection**, Weight/LocPref/prepend/MED, community, filtering, `aggregate-address` | Tuần 10 |
| [Module-06A-FHRP-HSRP-VRRP-GLBP.md](Module-06A-FHRP-HSRP-VRRP-GLBP.md) | HSRP/VRRP/GLBP, ⭐ **object tracking + IP SLA**, SSO/NSF/StackWise | Tuần 11 |
| [Module-06B-NAT-NTP-Multicast.md](Module-06B-NAT-NTP-Multicast.md) | NAT/PAT nâng cao, ⭐ **thứ tự NAT–routing**, NAT dual-ISP, NTP, Multicast (IGMP/PIM) | Tuần 11 |

### Khối Wireless / Overlay / Architecture

| File | Nội dung | Tuần |
|---|---|---|
| [Module-07A-Wireless-RF-802.11-AP-Antenna.md](Module-07A-Wireless-RF-802.11-AP-Antenna.md) | dBm/EIRP/RSSI/SNR, band & channel & DFS, CCI vs ACI, CSMA/CA, 802.11 a→ax, MIMO/OFDMA, ⭐ **9 AP mode**, ⭐ **antenna** | Tuần 12 |
| [Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md](Module-07B-CAPWAP-WLC-FlexConnect-Roaming.md) | Split-MAC, CAPWAP 5246/5247, ⭐ **AP join & discovery & WLC selection**, FlexConnect, ⭐ **roaming L2/L3 anchor-foreign**, ⭐ **troubleshoot 6 tầng** | Tuần 13 |
| [Module-08-Virtualization-va-Overlay.md](Module-08-Virtualization-va-Overlay.md) | Hypervisor/vSwitch (EST/VST/VGT), ⭐ **VRF-lite**, ⭐ **GRE**, ⭐ **IPsec & GRE over IPsec**, LISP, VXLAN | Tuần 14 |
| [Module-09-Architecture-va-QoS.md](Module-09-Architecture-va-QoS.md) | 2-tier/3-tier, Spine-Leaf, HA (SSO/NSF/GR), WLAN design, cloud, ⭐ **SD-WAN**, ⭐ **SD-Access**, ⭐ **QoS** | Tuần 15 |

### Khối Security / Assurance / Automation

| File | Nội dung | Tuần |
|---|---|---|
| [Module-10-Security.md](Module-10-Security.md) | Hardening & password type, ⭐ **AAA (TACACS+/RADIUS)**, ⭐ **ACL nâng cao**, ⭐ **CoPP**, 802.1X/MAB/WebAuth, wireless security, TrustSec, MACsec, NGFW, REST API security | Tuần 16 |
| [Module-11-Network-Assurance.md](Module-11-Network-Assurance.md) | Syslog, SNMPv2c/v3, ⭐ **Flexible NetFlow**, SPAN/RSPAN/ERSPAN, ⭐ **IP SLA**, ⭐ **debug an toàn**, DNA Center Assurance | Tuần 17 |
| Module-12-Automation-va-Programmability.md | JSON/XML/YAML, REST API, NETCONF/RESTCONF/YANG, EEM, Python netmiko, Ansible, DNAC & vManage API | Tuần 18–19 |

### Về đích

| File | Nội dung | Tuần |
|---|---|---|
| Module-13-On-thi-va-Chien-thuat-Phong-thi.md | LAB tổng hợp, bảng bẫy đề, mock exam, chiến thuật thời gian, checklist trước khi book exam | Tuần 20 |
| [Tai-lieu-tham-khao.md](Tai-lieu-tham-khao.md) | Cisco doc chính thống, sách, video, diễn đàn uy tín, nguồn đề luyện | — |

---

## 4. Khuôn chuẩn của mỗi module

Mỗi file module đều có đúng 12 khối sau, luôn cùng thứ tự — để bạn biết trước mình đang đọc gì:

| # | Khối | Dùng để làm gì |
|---|---|---|
| 1 | 🧭 **Breadcrumb + Vị trí trong blueprint** | Biết mình đang ở đâu, module này chiếm bao nhiêu % đề |
| 2 | ✅ **Chuẩn bị trước khi học** | Kiến thức cần có trước + lab cần dựng + RAM cần |
| 3 | 📘 **Lý thuyết — dạng bảng** | **Bảng là trung tâm.** Nắm kiến thức chính nhanh, dùng tra cứu lại về sau |
| 4 | 📖 **Hiểu rõ hơn** | Analogy + mô hình tư duy. Đọc khi bảng ở trên "đúng mà không hiểu" |
| 5 | 🧪 **LAB — step by step** | Topology + bảng nối dây + config đầy đủ + **output mẫu** + ✅ Checkpoint + ⚠️ nếu lỗi + 💡 vì sao |
| 6 | 🚀 **LAB nâng cao** | Biến thể sát thực tế / sát dạng đề simulation |
| 7 | 💡 **Thực chiến đi làm** | Kiến thức production mà giáo trình thi bỏ quên |
| 8 | 🎓 **Bẫy trong đề ENCOR** | Những chỗ đề hay gài. Đọc trước khi thi |
| 9 | 🐛 **Gỡ lỗi nhanh** | Lệnh debug vạn năng + bảng *triệu chứng → nguyên nhân → cách sửa* |
| 10 | 📝 **Quiz tự kiểm tra** | Câu hỏi dạng đề, đáp án giấu trong `<details>` |
| 11 | 📚 **Thuật ngữ Anh–Việt** | Đề thi bằng tiếng Anh — bảng này để bạn không bị chặn bởi từ vựng |
| 12 | 🎯 **Đúc kết + Tự chấm** | 3 điều rút ra + checklist tự đánh giá đã đạt chưa |

---

## 5. Cách dùng repo (đọc kỹ, đây là phần quyết định bạn có bỏ ngang hay không)

### Nhịp học 1 tuần chuẩn (10 giờ)

| Buổi | Thời lượng | Làm gì |
|---|---|---|
| Buổi 1 | 2h | Đọc khối 📘 Lý thuyết + 📖 Hiểu rõ hơn. **Không lab.** Chỉ hiểu. |
| Buổi 2 | 2.5h | Làm 🧪 LAB cơ bản theo từng bước. Gõ tay, **không copy cả block một lần** |
| Buổi 3 | 2h | Làm 🚀 LAB nâng cao + đọc 💡 Thực chiến |
| Buổi 4 | 1.5h | Đọc 🎓 Bẫy đề + 🐛 Gỡ lỗi. **Tự cố ý phá lab** rồi sửa lại |
| Buổi 5 | 2h | Làm 📝 Quiz. Sai câu nào → quay lại đúng mục đó. Ghi 🎯 Đúc kết bằng lời của bạn |

### 5 quy tắc bắt buộc

1. **Gõ tay, không copy-paste toàn bộ.** Copy-paste giúp lab chạy, không giúp bạn thi. Nhưng khi lab đã chạy đúng rồi thì paste lại để tiết kiệm thời gian là được.
2. **Cố ý phá lab.** Lab chạy đúng dạy bạn ít hơn lab bị lỗi. Sau khi lab chạy: shutdown 1 link, đổi sai area, đổi sai AS number — rồi tự tìm ra bằng `show`/`debug`.
3. **Viết sổ lỗi của riêng bạn.** Tạo file `SO-TAY-LOI.md` trong repo. Mỗi lần bạn mất >15 phút vì 1 lỗi → ghi vào. Cuối khóa đây là tài sản giá trị nhất.
4. **Không bỏ dở giữa module.** Thà học 1 module trong 2 tuần còn hơn học nửa vời 4 module.
5. **Chưa đạt ✅ Tự chấm thì chưa sang module sau.** Nghiêm túc chỗ này.

### Nếu bạn bị kẹt

| Kẹt gì | Làm gì |
|---|---|
| Lab không chạy | Xem 🐛 Gỡ lỗi nhanh trong module đó → rồi Module-00 §8 (lỗi EVE-NG thường gặp) |
| Lý thuyết không hiểu | Đọc 📖 Hiểu rõ hơn → rồi tra link Cisco doc ở cuối module |
| Học mãi không nhớ | Bình thường. Quay lại đọc **chỉ bảng ở khối 📘** của các module cũ, 15 phút/ngày |
| Mất động lực | Nhìn ROADMAP.md, xem mình đã đi được bao nhiêu tuần. Đừng so với người khác |

---

## 6. Điều kiện thi & chi phí (cập nhật lúc viết — hãy tự kiểm tra lại)

| Mục | Chi tiết |
|---|---|
| Mã đề | **350-401 ENCOR** |
| Thời lượng | 120 phút |
| Số câu | ~90–105 (multiple choice, drag-drop, và **simulation**) |
| Ngôn ngữ | Tiếng Anh (và tiếng Nhật) |
| Điều kiện tiên quyết | **Không có** — không cần CCNA. Nhưng thực tế cần nền CCNA |
| Chi phí thi | ~$400 USD (giá Cisco, chưa VAT — kiểm tra lại tại Pearson VUE) |
| CCNP Enterprise = | ENCOR + **1 môn concentration** (ENARSI / ENSDWI / ENAUTO / ENSLD / ENWLSD / ENWLSI) |
| Giá trị khác | ENCOR là **qualifying exam** của CCIE Enterprise Infrastructure |
| Hiệu lực | 3 năm, gia hạn bằng thi lại hoặc Continuing Education credits |
| Không đảo câu | ⚠️ Đề Cisco **không cho quay lại câu trước**. Xem chiến thuật ở Module-13 |

> ⚠️ **Cisco cập nhật blueprint định kỳ.** Trước khi mua sách hay book thi, mở
> [Exam Topics 350-401 trên Cisco Learning Network](https://learningnetwork.cisco.com/s/encor-exam-topics)
> để xác nhận version blueprint hiện hành. Repo này viết theo blueprint v1.1.

---

## 7. Trạng thái biên soạn

| Batch | Nội dung | Trạng thái |
|---|---|---|
| 1 | README + ROADMAP + Tài liệu tham khảo + Sổ tay lỗi | ✅ Xong |
| 2 | Module-00 (Setup lab) + Module-P0 (Nền tảng) | ✅ Xong — **đủ để bạn học Tuần 0–2 ngay** |
| 3 | **Module-01 → 06B (Infrastructure — 30% đề, phần lớn nhất)** | ✅ **Xong** — đủ để học Tuần 3–11 |
| 4 | **Module-07A/07B + 08 + 09 (Wireless / Overlay / Architecture & QoS)** | ✅ **Xong** |
| 5 | Module-10 → 12 (Security / Assurance / Automation) | ⏳ Chờ |
| 6 | Module-13 (Ôn thi) | ⏳ Chờ |

**Tiến độ hiện tại:** 19 file · **~26.200 dòng** · phủ **Tuần 0 → 15** của ROADMAP.

⭐ **Ba domain đã XONG TRỌN VẸN:**

| Domain | % đề | Module phụ trách | |
|---|:---:|---|:---:|
| **3.0 Infrastructure** | **30%** | Module-02 → 07B | ✅ |
| **1.0 Architecture** | **15%** | Module-01 (§1.7) + Module-09 | ✅ |
| **2.0 Virtualization** | **10%** | Module-08 | ✅ |
| **Tổng đã phủ** | ⭐ **55%** | | ✅ |

⭐ Còn lại: **5.0 Security (20%)** · **6.0 Automation (15%)** · **4.0 Network Assurance (10%)**.

---

## 8. Liên quan

- Repo **network-automation-mastery** của bạn phủ phần lớn kiến thức của Module-12 (Automation, 15% đề)
  — học chéo được, đừng học lại từ đầu.
- Kinh nghiệm vận hành cụm ảo hóa của bạn giúp ích trực tiếp cho Module-08 (vSwitch, VLAN trunk vào hypervisor)
  và Module-11 (monitoring).

---

**Bắt đầu ở đâu:** đọc [ROADMAP.md](ROADMAP.md) → làm [Module-00](Module-00-Setup-Lab-EVE-NG.md) để có lab → vào [Module-P0](Module-P0-Nen-tang-Ready-for-ENCOR.md).
