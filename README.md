<div align="center">

# ⚡ RatAI Lesson AutoCompleter

### 🚀 Autonomous High-Yield Course & Quiz Automator for TH-AI Passport
**Cross-Platform Automation Bot (macOS & Windows)**

[![GitHub Stars](https://img.shields.io/github/stars/Ampsoria/RatAI_Lesson_AutoCompleter?style=for-the-badge&logo=github&color=blue)](https://github.com/Ampsoria/RatAI_Lesson_AutoCompleter)
[![GitHub Forks](https://img.shields.io/github/forks/Ampsoria/RatAI_Lesson_AutoCompleter?style=for-the-badge&logo=github&color=purple)](https://github.com/Ampsoria/RatAI_Lesson_AutoCompleter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![macOS](https://img.shields.io/badge/macOS-AppleScript%20JXA-black?style=for-the-badge&logo=apple&logoColor=white)]()
[![Windows](https://img.shields.io/badge/Windows-CDP%20Port%209222-0078D6?style=for-the-badge&logo=windows&logoColor=white)]()
[![Zero Dependency](https://img.shields.io/badge/Dependencies-0%20External%20Pkgs-brightgreen?style=for-the-badge)]()

<br/>

**RatAI Lesson AutoCompleter** คือระบบ Automation อัจฉริยะแบบ Zero-dependency ที่พัฒนาขึ้นเพื่ออำนวยความสะดวกในการเรียน, เร่งเก็บคะแนนสูงสุด, ทำแบบทดสอบ และสะสมใบประกาศนียบัตรบนแพลตฟอร์ม [TH-AI Passport LMS](https://de.aipass.net/lms) โดยรองรับทั้งระบบปฏิบัติการ **macOS** และ **Windows** อย่างสมบูรณ์แบบ

Developed with ❤️ by **[Ampsoria](https://github.com/Ampsoria)**

</div>

---

## 🌟 จุดเด่นและความสามารถ (Highlights & Features)

| Feature | รายละเอียดความสามารถ |
| :--- | :--- |
| 🌐 **Dual-OS Support** | รองรับทั้ง **macOS** (ผ่าน AppleScript JXA) และ **Windows** (ผ่าน Chrome DevTools Protocol พอร์ต 9222) |
| 🎯 **Smart Yield Priority** | สแกนและคำนวณคะแนนทุกคอร์สแบบ Real-time (+250 คะแนนโบนัส) เรียงลำดับทำคอร์สที่ได้คะแนนสูงสุดก่อนเสมอ |
| ⚡ **2x Playback Auto-Lock** | ล็อคความเร็ว 2 เท่าบน Video.js อัตโนมัติทุกครั้งที่เริ่มบทเรียนใหม่ ลดเวลาเรียนลง 50% ครบทุก Milestone เซิร์ฟเวอร์ |
| 📝 **Smart Quiz Solver** | ตรวจจับแบบทดสอบประจำบทเรียน เลือกตัวเลือก ตรวจทาน และส่งผลคะแนนทันทีโดยไม่ต้องคลิกเอง |
| 🔄 **Self-Navigating Loop** | ตรวจจับป๊อปอัป "ยินดีด้วย!", กด "เรียนต่อ", รับ Certificate และเปลี่ยนคอร์สอัตโนมัติเมื่อเรียนจบ |
| 🛡️ **Anti-Bot Detection Free** | ควบคุมผ่านเบราว์เซอร์จริงที่ผู้ใช้เปิดไว้ ไม่ต้องใช้ ChromeDriver หรือสร้าง Profile ใหม่ จึงปลอดภัยและใช้ Session จริง |
| 📦 **Zero Dependencies** | พัฒนาด้วย Pure Python Standard Library (`subprocess`, `json`, `time`, `re`, `sys`, `socket`) รันได้ทันทีโดยไม่ต้อง `pip install` |

---

## 🏗️ แผนภาพการทำงาน (Architecture Workflow)

```mermaid
flowchart TD
    A[🏁 Start: auto_study.py] --> B{ตรวจสอบระบบปฏิบัติการ}
    
    B -->|macOS| C1[เชื่อมต่อผ่าน AppleScript JXA]
    B -->|Windows| C2[เชื่อมต่อผ่าน Chrome CDP Port 9222]
    
    C1 --> D{เช็คสถานะหน้าจอเว็บ}
    C2 --> D
    
    D -->|หน้าหลัก LMS| E[สแกนหาคอร์สคะแนนสูงสุด]
    E --> F[คัดกรองคอร์สที่ยังไม่ทำ]
    F --> G[คลิกเข้าคอร์สที่คุ้มค่าที่สุด]
    
    D -->|หน้ารายละเอียด| H[คลิกปุ่ม 'เริ่มเรียน' / 'เรียนต่อ']
    
    D -->|หน้าบทเรียน: วิดีโอ| I[ล็อคความเร็ว 2x Playback Speed]
    I --> J[เล่นวิดีโอจนจบ Milestone]
    J --> K[คลิก 'เรียนต่อ' / บทเรียนถัดไป]
    
    D -->|หน้าบทเรียน: แบบทดสอบ| L[ตรวจจับตัวเลือก & ตอบแบบทดสอบ]
    L --> M[ส่งคำตอบ & ไปข้อถัดไป]
    
    K --> N{จบคอร์สทั้งหมดหรือยัง?}
    M --> N
    N -->|ยังไม่จบ| D
    N -->|จบคอร์ส| O[🏆 บันทึกคะแนน & เริ่มคอร์สถัดไป]
```

---

## 🤖 สำหรับ AI Agent (AI Instructions & Guide)

> **สำหรับ AI Assistants (เช่น Google Antigravity, Claude, Cursor, ChatGPT Desktop, Windsurf, AutoGPT):**  
> หากคุณได้รับมอบหมายให้รันระบบนี้แทนผู้ใช้ กรุณาอ่านและปฏิบัติตามแนวทางนี้เพื่อแนะนำผู้ใช้และรันสคริปต์ได้อย่างราบรื่น:

### 📋 ขั้นตอนการทำงานของ AI Agent:

1. **ตรวจสอบ OS ของผู้ใช้:**
   * ตรวจสอบว่าระบบเป็น macOS หรือ Windows (`platform.system()`)
2. **แนะนำวิธีเปิด Chrome ให้ผู้ใช้:**
   * **กรณีผู้ใช้ใช้ Windows:**
     * แจ้งให้ผู้ใช้ปิด Chrome เดิม หรือเปิด Chrome ใหม่ด้วยโหมด Debugging:
       ```cmd
       chrome.exe --remote-debugging-port=9222
       ```
     * แจ้งให้ผู้ใช้เข้าสู่ระบบที่ [https://de.aipass.net/lms](https://de.aipass.net/lms)
   * **กรณีผู้ใช้ใช้ macOS:**
     * แจ้งให้ผู้ใช้เปิดแท็บ [https://de.aipass.net/lms](https://de.aipass.net/lms) บน Chrome
     * แนะนำให้คลิกเมนู: `View (มุมมอง) > Developer (นักพัฒนา) > Allow JavaScript from Apple Events` (ทำเพียงครั้งเดียว)
3. **สั่งรันและตรวจจับสถานะ:**
   * สั่งรันคำสั่งในเทอร์มินัลแบบ Background Task:
     ```bash
     python3 auto_study.py    # บน macOS
     python auto_study.py     # บน Windows
     ```
   * ตรวจสอบ Progress จาก Terminal Output / Log Streams โดยตรง (ไม่ต้องเปิด browser subagent ให้เปลือง token)
   * เมื่อจบคอร์ส ให้แจ้งสรุปคะแนนและใบประกาศที่ได้รับให้ผู้ใช้ทราบ

---

## ⚙️ ข้อกำหนดและการตั้งค่าสำหรับผู้ใช้ (Setup Guide)

### 🪟 1. สำหรับผู้ใช้ Windows

1. **ปิด Google Chrome เดิมทั้งหมด** (ตรวจสอบที่ Taskbar หรือปิดผ่าน Task Manager)
2. **เปิด Chrome ในโหมด Remote Debugging:**
   * กดปุ่ม `Windows + R` บนคีย์บอร์ด
   * วางคำสั่งนี้ลงในช่อง Run แล้วกด Enter:
     ```cmd
     chrome.exe --remote-debugging-port=9222
     ```
   * *(หากคำสั่งหา chrome ไม่เจอ สามารถเปิด Command Prompt แล้วพิมพ์ `start chrome.exe --remote-debugging-port=9222`)*
3. **เข้าสู่ระบบ:**
   * ในหน้าต่าง Chrome ที่เปิดขึ้นมา ให้เข้าไปที่ [https://de.aipass.net/lms](https://de.aipass.net/lms) แล้วล็อกอินบัญชีของคุณ
4. **เปิด Command Prompt / PowerShell ในโฟลเดอร์โปรเจกต์ แล้วรัน:**
   ```cmd
   python auto_study.py
   ```

---

### 🍏 2. สำหรับผู้ใช้ macOS

1. **เปิดสิทธิ์ควบคุม Chrome (ทำเพียงครั้งเดียว):**
   * เปิด Google Chrome
   * ที่แถบ Menu Bar ด้านบนสุดของหน้าจอ Mac เลือก: **View (มุมมอง)** > **Developer (นักพัฒนา)**
   * คลิกติ๊กถูกที่: **"Allow JavaScript from Apple Events"** (อนุญาต JavaScript จาก Apple Events)
2. **เข้าสู่ระบบ:**
   * เปิดแท็บ [https://de.aipass.net/lms](https://de.aipass.net/lms) แล้วล็อกอินให้เรียบร้อย
3. **เปิด Terminal ในโฟลเดอร์โปรเจกต์ แล้วรัน:**
   ```bash
   python3 auto_study.py
   ```

---

## 💻 ตัวอย่างการแสดงผลบน Terminal (Live Progress)

```text
============================================================
🚀 RATAI LESSON AUTOCOMPLETER STARTED
💻 Platform: macOS (AppleScript JXA)
============================================================
🎯 คัดเลือกคอร์สคะแนนสูงสุด: Cloud-native with Azure Container Apps (2,055 คะแนน)
📖 อยู่ในหน้ารายละเอียดคอร์ส กำลังคลิกเริ่มเรียน...
▶️ [วิดีโอ 2x] [██████████████████░░░░░░░] 74% (702s/948s)
🏁 วิดีโอจบแล้ว กำลังรอระบบบันทึกคะแนน...
🎉 บทเรียนเสร็จสิ้น! กำลังคลิก 'เรียนต่อ'...
```

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```text
RatAI_Lesson_AutoCompleter/
├── auto_study.py        # Core Engine รองรับทั้ง macOS & Windows
├── requirements.txt     # ระบุสถานะ Zero-dependency
├── README.md            # คู่มือฉบับสมบูรณ์สำหรับผู้ใช้และ AI Agent
├── LICENSE              # MIT License
└── .gitignore           # กรองไฟล์แคชที่ไม่จำเป็น
```

---

## 🛡️ License & Credit

เผยแพร่ภายใต้สัญญาอนุญาต **MIT License** ดูรายละเอียดเพิ่มเติมได้ที่ [LICENSE](LICENSE)

* **ผู้พัฒนา (Author):** **[Ampsoria](https://github.com/Ampsoria)**
* **GitHub Repository:** [https://github.com/Ampsoria/RatAI_Lesson_AutoCompleter](https://github.com/Ampsoria/RatAI_Lesson_AutoCompleter)

> *Disclaimer: โปรเจกต์นี้สร้างขึ้นเพื่อการศึกษาและการวิจัยด้าน Automation เท่านั้น ผู้ใช้งานควรปฏิบัติตามนโยบายและข้อกำหนดของแพลตฟอร์ม*
