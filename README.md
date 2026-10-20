# 🤖 TH-AI Passport LMS Automation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Standard%20Library)-green.svg)]()
[![Author](https://img.shields.io/badge/Author-Ampsoria-orange.svg)]()

> **Automated Course Runner for TH-AI Passport (`https://de.aipass.net/lms`)**  
> An autonomous bot designed to prioritize highest-scoring courses, accelerate videos to 2x, complete quizzes, and collect certifications automatically.
> 
> **Created by Ampsoria**

---

## 🌟 จุดเด่นและความสามารถ (Key Features)

* 🎯 **Smart Course Prioritization (เรียงลำดับคะแนนสูงสุด):**
  สแกนและจัดลำดับคอร์สทั้งหมดบน TH-AI Passport โดยคำนวณคะแนนรวมและคะแนนโบนัส (+250 โบนัส) แล้วเริ่มทำคอร์สที่ได้คะแนนเยอะที่สุดลงมาตามลำดับ (Descending order)
* ⚡ **2x Playback Speed Auto-Enforcer (เร่งความเร็ว 2 เท่า):**
  เนื่องจากระบบ LMS ล็อคการเลื่อนแถบเวลา (Seek Bar) เพื่อตรวจสอบ Milestone ทุก ๆ 10 วินาที สคริปต์จะปรับความเร็วเป็น **2x** บน Player ของ Chrome เสมอทุกครั้งที่เริ่มบทเรียนใหม่ ช่วยประหยัดเวลาลงครึ่งหนึ่งโดยไม่ผิดเงื่อนไขระบบ
* 📝 **Auto-Quiz & Lesson Transitions (ทำแบบทดสอบอัตโนมัติ):**
  ตรวจจับแบบทดสอบประจำบท/คอร์ส เลือกคำตอบ ส่งคำตอบ และกดปุ่ม "เรียนต่อ" / "ต่อไป" ทันทีที่จบบทเรียน
* 🔄 **Fully Autonomous Infinite Loop (ทำงานต่อเนื่องแบบอัตโนมัติ):**
  เมื่อเรียนจบคอร์ส ระบบจะบันทึกสถานะ รับคะแนน/ใบประกาศนียบัตร และกลับไปหน้าหลักเพื่อเลือกคอร์สที่ยังไม่ได้ทำถัดไปทันที
* 📦 **Zero External Dependencies (ไม่ต้องลง Library เพิ่ม):**
  ใช้เพียง Python Standard Library (`subprocess`, `json`, `time`, `re`, `sys`) รันได้ทันทีโดยไม่ต้อง `pip install` ใด ๆ

---

## 🛠️ ข้อกำหนดเบื้องต้น (Prerequisites)

1. **ระบบปฏิบัติการ:** macOS
2. **เบราว์เซอร์:** Google Chrome
3. **การตั้งค่า Chrome (สำคัญมาก - ทำเพียงครั้งเดียว):**
   * เปิด Google Chrome
   * ที่แถบเมนูด้านบนสุดของ Mac เลือก: **View (มุมมอง)** > **Developer (นักพัฒนา)**
   * ติ๊กถูกที่: **"Allow JavaScript from Apple Events"** (อนุญาต JavaScript จาก Apple Events)
4. **เข้าสู่ระบบ:**
   * เปิดแท็บ Chrome ไปที่ [https://de.aipass.net/lms](https://de.aipass.net/lms) และล็อกอินเข้าสู่ระบบให้เรียบร้อย

---

## 🚀 วิธีการใช้งาน (Usage Guide)

### สำหรับผู้ใช้งานทั่วไป (Humans)

1. Clone โปรเจกต์ลงเครื่อง:
   ```bash
   git clone https://github.com/Ampsoria/Amp_AutomateAipasssport.git
   cd Amp_AutomateAipasssport
   ```

2. เปิด Chrome ไว้ที่หน้า `https://de.aipass.net/lms` (เข้าสู่ระบบแล้ว)

3. รันสคริปต์ผ่าน Terminal:
   ```bash
   python3 auto_study.py
   ```

4. สคริปต์จะเริ่มทำงาน พร้อมแสดง Progress Bar และสถานะแบบ Real-time:
   ```text
   ============================================================
   🚀 TH-AI PASSPORT AUTOMATION RUNNER STARTED
   ============================================================
   🎯 เลือกคอร์สคะแนนสูงสุด: Cloud-native with Azure Container Apps (2,055 คะแนน)
   📖 อยู่ในหน้ารายละเอียดคอร์ส กำลังคลิกเริ่มเรียน...
   ▶️ [วิดีโอ 2x] [████████████░░░░░░░░░░░░░] 48% (456s/948s)
   ```

---

### สำหรับ AI Agents (Antigravity / Claude / AutoGPT / Cursor)

หากคุณเป็น AI Agent หรือระบบอัตโนมัติที่นำสคริปต์นี้ไปรันบนเครื่องผู้ใช้:

1. ตรวจสอบว่า Chrome กำลังรันอยู่และเปิดหน้า `https://de.aipass.net/`
2. ทดสอบการเชื่อมต่อ AppleScript:
   ```bash
   osascript -l JavaScript -e 'Application("Google Chrome").windows[0].activeTab.execute({javascript: "document.title"})'
   ```
   *หากได้ Title กลับมา แสดงว่าพร้อมทำงานทันที*
3. สั่งรันสคริปต์ใน Background Task:
   ```bash
   python3 auto_study.py
   ```
4. AI Agent สามารถอ่าน Status / Progress จาก stdout/stderr หรือ Log file ได้โดยตรงโดยไม่ต้องใช้ browser subagent เปลือง token

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```text
Amp_AutomateAipasssport/
├── auto_study.py        # สคริปต์หลัก ควบคุม Chrome อัตโนมัติ
├── requirements.txt     # แจ้งสถานะ Zero-dependency
├── README.md            # คู่มือการใช้งานและเอกสารกำกับ
├── LICENSE              # MIT License
└── .gitignore           # กรองไฟล์ที่ไม่จำเป็นสำหรับ Git
```

---

## ⚙️ เบื้องหลังการทำงาน (Technical Architecture)

1. **AppleScript JXA Bridge:**  
   ใช้ `osascript -l JavaScript` ควบคุม Google Chrome Tab ที่เปิดอยู่โดยตรง ไม่ต้องพึ่งพา Selenium หรือ ChromeDriver จึงไม่ถูกตรวจจับว่าเป็น Bot และใช้ Session/Cookies ที่ล็อกอินอยู่จริงได้ 100%
2. **Milestone Integrity Compliance:**  
   เนื่องจากระบบ TH-AI Passport ใช้ Next.js + Turbopack ร่วมกับ Video.js ตรวจจับการรับชมทุก ๆ 10 วินาที (`Math.min(s, lastConfirmedWatchedSeconds + 10)`) การเร่งสปีดที่ 2x เป็นความเร็วที่เซิร์ฟเวอร์ยอมรับทุก Milestone อย่างสมบูรณ์และได้รับคะแนนเต็มทุกบทเรียน
3. **Dynamic DOM Querying:**  
   ค้นหาและเชื่อมโยง UI Elements แบบ Dynamic ตามภาษาและสถานะของปุ่ม (`เริ่มเรียน`, `เรียนต่อ`, `แบบทดสอบ`, `ส่งคำตอบ`)

---

## 📄 License & Credits

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

* **Author:** Ampsoria
* **Repository:** [https://github.com/Ampsoria/Amp_AutomateAipasssport](https://github.com/Ampsoria/Amp_AutomateAipasssport)
