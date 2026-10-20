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

def exec_js(js_code):
    """Executes JavaScript inside the active Google Chrome tab via AppleScript."""
    cmd = ["osascript", "-l", "JavaScript", "-e", f"""
        const app = Application("Google Chrome");
        app.windows[0].activeTab.execute({{javascript: {json.dumps(js_code)}}});
    """]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
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

def main_loop():
    log("="*60, "cyan")
    log("🚀 TH-AI PASSPORT AUTOMATION RUNNER STARTED", "bold")
    log("="*60, "cyan")
    
    last_time_val = -1
    stall_count = 0
    
    while True:
        try:
            status = get_page_status()
            if not status:
                time.sleep(2)
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
                    exec_js("window.location.href = 'https://de.aipass.net/lms'")
                    time.sleep(3)
                    continue
                
                if status["hasVideo"]:
                    curr = status.get("videoTime") or 0
                    dur = status.get("videoDuration") or 0
                    pct = int((curr / dur) * 100) if dur > 0 else 0
                    
                    # Ensure 2x speed is selected in player
                    if not "2x" in status.get("speedBtnText", ""):
                        ensure_2x_speed()
                    
                    # Progress bar
                    bar_len = 25
                    filled = int(bar_len * pct / 100)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(f"\r▶️ [วิดีโอ 2x] [{bar}] {pct}% ({int(curr)}s/{int(dur)}s)")
                    sys.stdout.flush()
                    
                    # Check stall / auto-play
                    if status["videoPaused"] or int(curr) == int(last_time_val):
                        stall_count += 1
                        if stall_count >= 5:
                            exec_js("let v = document.querySelector('video'); if (v) { v.muted=true; v.play(); }")
                            stall_count = 0
                    else:
                        stall_count = 0
                        last_time_val = curr
                    
                    # If video near end
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
                    break
                
                target = uncompleted[0]
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
