#!/usr/bin/env python3
"""
TH-AI Passport Automated Course Runner
- Automatically sorts courses by highest points descending
- Automatically sets video speed to 2x (maximum supported in LMS UI)
- Auto-completes quizzes and moves between lessons
- Auto-enrolls and moves to next course upon completion
"""

import subprocess
import json
import time
import re
import sys
import platform
import socket
import urllib.request
import base64
import os

IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

class SimpleCDPClient:
    """Minimal zero-dependency WebSocket client for Chrome DevTools Protocol on Windows/Linux."""
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self._connect()

    def _connect(self):
        url = self.ws_url.replace("ws://", "")
        parts = url.split("/", 1)
        host_port = parts[0].split(":")
        self.host = host_port[0]
        self.port = int(host_port[1]) if len(host_port) > 1 else 80
        self.path = "/" + parts[1]
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((self.host, self.port))
        
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        res = self.sock.recv(4096)
        if b"101 Switching Protocols" not in res:
            raise ConnectionError("WebSocket handshake failed")

    def send_frame(self, text):
        data = text.encode('utf-8')
        length = len(data)
        frame = bytearray([0x81])
        mask = os.urandom(4)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))
        frame.extend(mask)
        masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        frame.extend(masked_data)
        self.sock.sendall(frame)

    def recv_frame(self):
        head = self.sock.recv(2)
        if not head:
            return ""
        length = head[1] & 0x7F
        if length == 126:
            length = int.from_bytes(self.sock.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.sock.recv(8), 'big')
        payload = b""
        while len(payload) < length:
            chunk = self.sock.recv(min(length - len(payload), 4096))
            if not chunk:
                break
            payload += chunk
        return payload.decode('utf-8', errors='ignore')

    def execute_js(self, js_code):
        try:
            payload = json.dumps({
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": js_code,
                    "returnByValue": True
                }
            })
            self.send_frame(payload)
            res = self.recv_frame()
            data = json.loads(res)
            val = data.get("result", {}).get("result", {}).get("value")
            return json.dumps(val) if isinstance(val, (dict, list)) else str(val or "")
        except Exception:
            try:
                self._connect()
            except Exception:
                pass
            return ""

_cdp_client = None

def get_cdp_client():
    global _cdp_client
    if _cdp_client:
        return _cdp_client
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
        tabs = json.loads(req.read().decode())
        target_url = None
        for tab in tabs:
            if "aipass.net" in tab.get("url", ""):
                target_url = tab.get("webSocketDebuggerUrl")
                break
        if not target_url and tabs:
            target_url = tabs[0].get("webSocketDebuggerUrl")
        if target_url:
            _cdp_client = SimpleCDPClient(target_url)
            return _cdp_client
    except Exception:
        return None
    return None

def exec_js(js_code):
    """Executes JavaScript inside the active Google Chrome tab across macOS and Windows."""
    if IS_MAC:
        cmd = ["osascript", "-l", "JavaScript", "-e", f"""
            const app = Application("Google Chrome");
            app.windows[0].activeTab.execute({{javascript: {json.dumps(js_code)}}});
        """]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.stdout.strip()
        except Exception:
            return ""
    else:
        # Windows / Linux: Uses Chrome DevTools Protocol (CDP) on port 9222
        client = get_cdp_client()
        if client:
            return client.execute_js(js_code)
        return ""

def log(msg, color="white"):
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "magenta": "\033[95m",
        "blue": "\033[94m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    c = colors.get(color, "")
    r = colors["reset"]
    print(f"{c}{msg}{r}", flush=True)

def parse_points(text):
    """Extract numeric points from text like '2,055 คะแนน' or '525 คะแนน'"""
    m = re.search(r'([0-9,]+)\s*คะแนน', text)
    if m:
        num = int(m.group(1).replace(',', ''))
        if '+250' in text or 'โบนัส' in text:
            num += 250
        return num
    return 0

def get_page_status():
    """Detects current page state: LMS Home, Course Detail, or Lesson/Quiz."""
    js = """
    (() => {
        let url = window.location.href;
        let isLesson = url.includes('/lesson/');
        let isCourse = url.includes('/courses/');
        let isHome = url.endsWith('/lms') || url.endsWith('/lms/');
        
        let video = document.querySelector('video');
        let hasVideo = !!video;
        let videoEnded = video ? video.ended : false;
        let videoTime = video ? video.currentTime : 0;
        let videoDuration = video ? video.duration : 0;
        let videoPaused = video ? video.paused : false;
        let videoRate = video ? video.playbackRate : 1;
        
        let speedBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Playback speed'));
        let speedBtnText = speedBtn ? speedBtn.innerText.trim() : '';
        
        let bodyText = document.body.innerText || '';
        let hasCongrats = bodyText.includes('ยินดีด้วย!') || bodyText.includes('คุณเรียนจบบทเรียนนี้แล้ว') || bodyText.includes('เรียนจบทุกบทเรียน');
        let hasCourseCompleted = bodyText.includes('ยินดีด้วย! คุณเรียนจบหลักสูตรนี้แล้ว') || bodyText.includes('ดาวน์โหลดใบประกาศ');
        
        let quizTitle = Array.from(document.querySelectorAll('h1, h2, h3, h4, p')).find(e => e.innerText && e.innerText.includes('แบบทดสอบ'));
        let hasQuiz = !!quizTitle && !hasVideo;
        
        let buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
        
        return JSON.stringify({
            url,
            isLesson,
            isCourse,
            isHome,
            hasVideo,
            videoTime,
            videoDuration,
            videoEnded,
            videoPaused,
            videoRate,
            speedBtnText,
            hasCongrats,
            hasCourseCompleted,
            hasQuiz,
            buttons
        });
    })()
    """
    res = exec_js(js)
    try:
        return json.loads(res)
    except:
        return None

def click_button_by_text(target_texts):
    """Finds and clicks a button that matches one of target_texts."""
    js = f"""
    (() => {{
        let targets = {json.dumps(target_texts)};
        let btns = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
        for (let t of targets) {{
            let btn = btns.find(b => b.innerText && b.innerText.trim() === t);
            if (btn) {{
                btn.click();
                return 'clicked ' + t;
            }}
        }}
        // Partial match fallback
        for (let t of targets) {{
            let btn = btns.find(b => b.innerText && b.innerText.includes(t));
            if (btn) {{
                btn.click();
                return 'partial clicked ' + t;
            }}
        }}
        return 'not found';
    }})()
    """
    return exec_js(js)

def ensure_2x_speed():
    """Selects 2x speed in Video.js control bar if not already active."""
    js = """
    (() => {
        let v = document.querySelector('video');
        if (!v) return 'no video';
        
        let speedBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Playback speed'));
        if (speedBtn && !speedBtn.innerText.includes('2x')) {
            speedBtn.click();
            let item2x = Array.from(document.querySelectorAll('.vjs-menu-item')).find(el => el.innerText.trim() === '2x');
            if (item2x) {
                item2x.click();
            }
        }
        
        v.muted = true;
        if (v.paused) v.play();
        return 'speed ensured';
    })()
    """
    return exec_js(js)

def handle_quiz():
    """Answers quiz questions and submits."""
    js = """
    (() => {
        let startBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('เริ่มทำแบบทดสอบ'));
        if (startBtn) {
            startBtn.click();
            return 'clicked start quiz';
        }
        
        let options = Array.from(document.querySelectorAll('input[type="radio"], [role="radio"], .quiz-option, label'));
        if (options.length > 0) {
            for (let opt of options) {
                if (opt.tagName === 'INPUT' && !opt.checked) {
                    opt.click();
                    break;
                } else if (opt.getAttribute('role') === 'radio' && opt.getAttribute('aria-checked') !== 'true') {
                    opt.click();
                    break;
                }
            }
        }
        
        let submitBtn = Array.from(document.querySelectorAll('button')).find(b => 
            b.innerText.includes('ส่งคำตอบ') || 
            b.innerText.includes('ตรวจคำตอบ') || 
            b.innerText.includes('ส่งแบบทดสอบ') ||
            b.innerText.includes('ยืนยันคำตอบ')
        );
        if (submitBtn) {
            submitBtn.click();
            return 'clicked submit quiz';
        }
        
        let nextBtn = Array.from(document.querySelectorAll('button')).find(b => 
            b.innerText.trim() === 'ข้อถัดไป' || 
            b.innerText.trim() === 'ถัดไป' ||
            b.innerText.trim() === 'ดูผลคะแนน'
        );
        if (nextBtn) {
            nextBtn.click();
            return 'clicked next question';
        }
        
        return 'quiz step handled';
    })()
    """
    return exec_js(js)

def get_home_courses():
    """Scrapes all available courses from LMS home and sorts by points descending."""
    js = """
    (() => {
        window.scrollTo(0, document.body.scrollHeight);
        
        let cards = Array.from(document.querySelectorAll('div, section, article')).filter(el => {
            let t = el.innerText || '';
            return t.includes('คะแนน') && (t.includes('นาที') || t.includes('ชั่วโมง'));
        });
        
        let found = [];
        let seen = new Set();
        
        for (let card of cards) {
            let lines = card.innerText.split('\\n').map(l => l.trim()).filter(Boolean);
            let pointLine = lines.find(l => l.includes('คะแนน'));
            let timeLine = lines.find(l => l.includes('นาที') || l.includes('ชั่วโมง'));
            
            if (pointLine && timeLine) {
                let h3 = card.querySelector('h3, h4');
                let title = h3 ? h3.innerText.trim() : '';
                if (!title) {
                    title = lines.find(l => !l.includes('คะแนน') && !l.includes('นาที') && !l.includes('ชั่วโมง') && !l.includes('โบนัส') && l.length > 3);
                }
                
                if (title && !seen.has(title)) {
                    seen.add(title);
                    let isCompleted = card.innerText.includes('ดูจบแล้ว') || card.innerText.includes('เรียนจบแล้ว') || card.innerText.includes('100%');
                    let hasBonus = card.innerText.includes('+250 โบนัส') || card.innerText.includes('โบนัส');
                    
                    found.push({
                        title: title,
                        pointText: pointLine,
                        timeText: timeLine,
                        hasBonus: hasBonus,
                        isCompleted: isCompleted
                    });
                }
            }
        }
        return JSON.stringify(found);
    })()
    """
    res = exec_js(js)
    try:
        raw = json.loads(res or "[]")
        for item in raw:
            item["points"] = parse_points(item["pointText"])
            if item["hasBonus"]:
                item["points"] += 250
        raw.sort(key=lambda x: x["points"], reverse=True)
        return raw
    except:
        return []

def click_course_card(title):
    """Clicks a course card by its title on LMS home."""
    js = f"""
    (() => {{
        let title = {json.dumps(title)};
        let h3s = Array.from(document.querySelectorAll('h3, h4, p, span, div')).filter(e => e.innerText && e.innerText.trim() === title);
        for (let h of h3s) {{
            let curr = h;
            while (curr && curr !== document.body) {{
                if (curr.tagName === 'A' || curr.tagName === 'BUTTON' || window.getComputedStyle(curr).cursor === 'pointer') {{
                    curr.click();
                    return 'clicked card: ' + title;
                }}
                curr = curr.parentElement;
            }}
            h.click();
            return 'clicked h: ' + title;
        }}
        return 'title card not found';
    }})()
    """
    return exec_js(js)

def update_readme_and_push(completed_courses, total_points):
    """Updates README.md with live completion stats and pushes to GitHub."""
    try:
        readme_path = "README.md"
        if not os.path.exists(readme_path):
            return
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        stats_markdown = f"""<!-- STATS_START -->
## 🏆 สถิติการเรียนล่าสุด (Live Completion Stats)

> อัปเดตล่าสุด: `{time.strftime('%Y-%m-%d %H:%M:%S')}`
* **คะแนนสะสมรวม:** `{total_points:,} คะแนน`
* **คอร์สที่เรียนจบแล้ว:** `{len(completed_courses)} คอร์ส`

| # | ชื่อคอร์สที่สำเร็จ | คะแนนที่ได้รับ | สถานะ |
|---|---|---|---|
"""
        for idx, c in enumerate(completed_courses, 1):
            stats_markdown += f"| {idx} | **{c.get('title')}** | {c.get('points', 0):,} คะแนน | ✅ สำเร็จ |\n"
        stats_markdown += "<!-- STATS_END -->"

        if "<!-- STATS_START -->" in content and "<!-- STATS_END -->" in content:
            content = re.sub(r'<!-- STATS_START -->.*?<!-- STATS_END -->', stats_markdown, content, flags=re.DOTALL)
        else:
            if "## 🛡️ License & Credit" in content:
                content = content.replace("## 🛡️ License & Credit", stats_markdown + "\n\n---\n\n## 🛡️ License & Credit")
            else:
                content += "\n\n" + stats_markdown

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        subprocess.run(["git", "add", "README.md", "progress.json"], capture_output=True)
        subprocess.run(["git", "commit", "-m", f"chore: auto-update progress ({len(completed_courses)} courses, {total_points:,} pts) [skip ci]"], capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True)
        log(f"\n🚀 อัปเดตสถิติลง README.md และ Push ขึ้น GitHub เรียบร้อยแล้ว! (รวม {total_points:,} คะแนน)", "magenta")
    except Exception as e:
        log(f"\n⚠️ Auto-push error: {e}", "red")

def main_loop():
    log("="*60, "cyan")
    log("🚀 RATAI LESSON AUTOCOMPLETER STARTED", "bold")
    log(f"💻 Platform: {'macOS (AppleScript JXA)' if IS_MAC else 'Windows / Linux (CDP port 9222)'}", "cyan")
    log("="*60, "cyan")
    
    # Load progress
    progress_file = "progress.json"
    completed_courses = []
    total_points = 0
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                completed_courses = saved.get("completed_courses", [])
                total_points = saved.get("total_points", 0)
        except Exception:
            pass
            
    current_course = None
    
    # Verify Connection at startup
    initial_check = exec_js("document.title")
    if not initial_check:
        log("\n⚠️ ยังไม่สามารถเชื่อมต่อกับ Google Chrome ได้", "yellow")
        if IS_MAC:
            log("🍏 วิธีตั้งค่าสำหรับ macOS (ทำครั้งเดียว):", "bold")
            log("   1. เปิด Google Chrome และเข้าสู่ระบบ https://de.aipass.net/lms", "cyan")
            log("   2. ที่เมนูด้านบนสุดของ Mac เลือก: View (มุมมอง) > Developer (นักพัฒนา)", "cyan")
            log("   3. ติ๊กถูกที่: 'Allow JavaScript from Apple Events'", "green")
        else:
            log("🪟 วิธีตั้งค่าสำหรับ Windows (ทำครั้งเดียว):", "bold")
            log("   1. ปิด Google Chrome ทั้งหมดก่อน", "cyan")
            log("   2. กดปุ่ม Win + R บนคีย์บอร์ด แล้วพิมพ์:", "cyan")
            log("      chrome.exe --remote-debugging-port=9222", "green")
            log("   3. เปิดแท็บเข้าสู่ระบบ https://de.aipass.net/lms", "cyan")
        log("\n⏳ กำลังรอการเชื่อมต่อกับ Chrome กรุณาทำตามขั้นตอนด้านบน...", "yellow")
    
    last_time_val = -1
    stall_count = 0
    
    while True:
        try:
            status = get_page_status()
            if not status:
                time.sleep(3)
                continue
            
            # --- CASE 1: Inside Lesson / Video ---
            if status["isLesson"]:
                if status["hasCongrats"]:
                    log("🎉 บทเรียนเสร็จสิ้น! กำลังคลิก 'เรียนต่อ'...", "green")
                    click_button_by_text(["เรียนต่อ", "ต่อไป", "ปิด"])
                    time.sleep(2)
                    continue
                
                if status["hasCourseCompleted"]:
                    log("🏆 ยินดีด้วย! จบคอร์สนี้เรียบร้อยแล้ว กำลังกลับหน้าแรก...", "magenta")
                    if current_course and not any(c.get("title") == current_course.get("title") for c in completed_courses):
                        completed_courses.append(current_course)
                        total_points += current_course.get("points", 0)
                        with open(progress_file, "w", encoding="utf-8") as f:
                            json.dump({"completed_courses": completed_courses, "total_points": total_points}, f, ensure_ascii=False, indent=2)
                        update_readme_and_push(completed_courses, total_points)
                    exec_js("window.location.href = 'https://de.aipass.net/lms'")
                    time.sleep(4)
                    continue
                
                if status["hasVideo"]:
                    curr = status.get("videoTime") or 0
                    dur = status.get("videoDuration") or 0
                    pct = int((curr / dur) * 100) if dur > 0 else 0
                    
                    if not "2x" in status.get("speedBtnText", ""):
                        ensure_2x_speed()
                    
                    bar_len = 25
                    filled = int(bar_len * pct / 100)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(f"\r▶️ [วิดีโอ 2x] [{bar}] {pct}% ({int(curr)}s/{int(dur)}s)")
                    sys.stdout.flush()
                    
                    if status["videoPaused"] or int(curr) == int(last_time_val):
                        stall_count += 1
                        if stall_count >= 5:
                            exec_js("let v = document.querySelector('video'); if (v) { v.muted=true; v.play(); }")
                            stall_count = 0
                    else:
                        stall_count = 0
                        last_time_val = curr
                    
                    if dur > 0 and curr >= (dur - 0.5):
                        sys.stdout.write("\n")
                        log("🏁 วิดีโอจบแล้ว กำลังรอระบบบันทึกคะแนน...", "green")
                        time.sleep(2)
                        click_button_by_text(["เรียนต่อ", "ต่อไป", "ปิด"])
                    
                    time.sleep(1)
                    continue
                
                if status["hasQuiz"]:
                    log("\n📝 ตรวจพบแบบทดสอบ กำลังจัดการแบบทดสอบ...", "yellow")
                    res = handle_quiz()
                    log(f"   Quiz Action: {res}", "cyan")
                    time.sleep(2)
                    continue
                
                click_button_by_text(["เรียนต่อ", "ต่อไป"])
                time.sleep(2)
                continue
            
            # --- CASE 2: Inside Course Detail Page ---
            if status["isCourse"]:
                log("📖 อยู่ในหน้ารายละเอียดคอร์ส กำลังคลิกเริ่มเรียน...", "cyan")
                click_button_by_text(["เริ่มเรียน", "เรียนต่อ"])
                time.sleep(3)
                continue
            
            # --- CASE 3: On LMS Home Page ---
            if status["isHome"]:
                log("\n🏠 อยู่หน้าหลัก LMS กำลังสแกนหาคอร์สที่คะแนนสูงสุด...", "cyan")
                courses = get_home_courses()
                
                uncompleted = [c for c in courses if not c["isCompleted"]]
                log(f"📊 พบทั้งหมด {len(courses)} คอร์ส (ยังไม่ทำ {len(uncompleted)} คอร์ส)", "bold")
                
                if not uncompleted:
                    log("🎉 ทำครบทุกคอร์สแล้ว! สุดยอดมากครับ!", "green")
                    update_readme_and_push(completed_courses, total_points)
                    break
                
                target = uncompleted[0]
                current_course = target
                log(f"🎯 เลือกคอร์สคะแนนสูงสุด: {target['title']} ({target['points']:,} คะแนน)", "green")
                click_course_card(target["title"])
                time.sleep(3)
                continue
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            log("\n🛑 หยุดการทำงานโดยผู้ใช้", "yellow")
            break
        except Exception as e:
            log(f"\n⚠️ Error: {e}", "red")
            time.sleep(2)

if __name__ == "__main__":
    main_loop()
