/* ============================================================
   mPython VirtualBoard · 宣传站脚本
   1. 中英双语切换   2. 导航交互   3. Hero OLED 打字机
   4. 可交互虚拟板演示   5. 快速开始 Tab   6. 滚动进场动画
   ============================================================ */

(function () {
  "use strict";

  /* ---------------- 1. 语言包 ---------------- */
  var I18N = {
    "zh-CN": {
      "meta.title": "mPython VirtualBoard · 虚拟掌控板",
      "nav.features": "核心功能",
      "nav.editions": "两个版本",
      "nav.demo": "在线体验",
      "nav.start": "快速开始",
      "hero.eyebrow": "面向中小学的掌控板仿真教学平台",
      "hero.title": "没有实体板，<br />也能学<span class=\"grad\">掌控板编程</span>",
      "hero.sub": "mPython VirtualBoard 在电脑上完整复刻掌控板：OLED、RGB 灯、按键、触摸与全套传感器。打开即写、运行即见，让每一节编程课都不再受硬件限制。",
      "hero.cta1": "立即开始",
      "hero.cta2": "在线体验虚拟板",
      "hero.stat1": "硬件组件仿真",
      "hero.stat2": "编程模式",
      "hero.stat3": "界面语言",
      "hero.stat4": "开源免费",
      "why.title": "为课堂拆掉硬件的门槛",
      "why.sub": "器材不够、损耗心疼、课前发放课后回收——这些都不该成为编程课的阻碍。",
      "why.c1t": "零器材开课",
      "why.c1d": "一人一台电脑即可拥有完整的掌控板体验，学校无需集中采购与维护硬件。",
      "why.c2t": "代码所见即所得",
      "why.c2d": "运行的每一行代码都实时反映在虚拟板的屏幕、灯光与传感器上，调试直观。",
      "why.c3t": "无缝衔接真实硬件",
      "why.c3d": "同一套 mPython / PinPong API，课堂上在虚拟板验证，课后可直接烧录到实体板。",
      "feat.title": "一套工具，覆盖教学全链路",
      "feat.sub": "从图形化启蒙到代码进阶，从虚拟仿真到真实传感器，一个平台全部搞定。",
      "feat.f1t": "完整硬件仿真",
      "feat.f1d": "OLED 屏、三路 RGB、双按键、六路触摸、蜂鸣器，以及加速度、陀螺仪、磁力、光线、声音传感器，一应俱全。",
      "feat.f2t": "双编程模式",
      "feat.f2d": "mPython 与 PinPong 两条教学路径自由切换，贴合不同教材与课程体系。",
      "feat.f3t": "Mind+ 图形化转译",
      "feat.f3d": "粘贴 Mind+ 上传模式自动生成的代码，内置转译器一键转为 Python 并直接运行，平滑完成图形化到代码的过渡。",
      "feat.f4t": "本地 AI 辅助改写",
      "feat.f4d": "PinPong 模式接入本地 Ollama + DeepSeek 模型，把自然语言课堂要求改写成规范教学代码，数据不出本机。",
      "feat.f5t": "真实传感器接入",
      "feat.f5d": "通过 USB 串口连接实体掌控板，实时读取真实加速度、陀螺仪、磁力、光线与声音数据，虚实验证两不误。",
      "feat.f6t": "Thonny 联动与悬浮窗",
      "feat.f6d": "桌面版可与 Thonny / IDLE 无缝配合，虚拟板窗口始终置顶悬浮，边写代码边看效果。",
      "ed.title": "两个版本，各取所需",
      "ed.sub": "同一颗仿真内核，两种产品形态，覆盖不同教学习惯。",
      "ed.web.tag": "推荐 · 一体化工作台",
      "ed.web.desc": "PyWebView + Vue3 打造的现代化教学工作台，内置编辑器，打开即用。",
      "ed.web.l1": "Monaco 编辑器，F5 运行 / F6 停止",
      "ed.web.l2": "Mind+ 上传模式代码转译与运行",
      "ed.web.l3": "PinPong 模式本地 AI 改写",
      "ed.web.l4": "真实传感器串口接入",
      "ed.web.l5": "传感器手动控制面板与快捷预设",
      "ed.desk.tag": "桌面 · IDE 联动",
      "ed.desk.desc": "Tkinter + Socket 架构的桌面仿真器，专为 Thonny / IDLE 课堂联动设计。",
      "ed.desk.l1": "一键启动整条虚拟板链路",
      "ed.desk.l2": "始终置顶的悬浮显示窗口",
      "ed.desk.l3": "Thonny / IDLE 远程控制",
      "ed.desk.l4": "8 种界面语言自由切换",
      "ed.desk.l5": "虚拟 USB 与客户端库支持",
      "demo.title": "先玩一分钟，再决定",
      "demo.sub": "下面就是一块活的虚拟掌控板。按下按键、晃动它，看看会发生什么。",
      "demo.inputLabel": "OLED 显示文字",
      "demo.inputPh": "输入点什么呢…",
      "demo.show": "显示",
      "demo.shake": "模拟晃动",
      "demo.rainbow": "RGB 彩虹",
      "demo.hint": "提示：也可以直接点板子上的 A / B 按键。",
      "demo.msgA": "Button A pressed!",
      "demo.msgB": "Button B pressed!",
      "demo.msgShake": "Shaking! x:0.8 y:-0.3",
      "demo.msgRainbow": "Rainbow RGB ~",
      "demo.msgReady": "Ready.",
      "demo.codeDefault": "from mpython import *\n\noled.DispChar('Hello!', 0, 0)\noled.show()\nrgb[0] = (255, 0, 0)\nrgb.write()",
      "demo.codeShow": "from mpython import *\n\noled.DispChar('{TEXT}', 0, 0)\noled.show()",
      "demo.codeBtn": "from mpython import *\n\nwhile True:\n    if {BTN}.value:\n        oled.DispChar('{TEXT}', 0, 0)\n        oled.show()",
      "demo.codeShake": "from mpython import *\n\nx = accelerometer.get_x()\ny = accelerometer.get_y()\noled.DispChar('x:%.1f y:%.1f' % (x, y), 0, 0)\noled.show()",
      "demo.codeRainbow": "from mpython import *\n\ncolors = [(255,0,0), (255,165,0), (255,255,0),\n          (0,255,0), (0,0,255), (139,0,255)]\nfor i, c in enumerate(colors):\n    rgb[i % 3] = c\n    rgb.write()",
      "hw.title": "熟悉的硬件，熟悉的 API",
      "hw.sub": "虚拟板与实体掌控板保持一致的编程接口，学过的知识零成本迁移。",
      "hw.h1": "组件",
      "hw.r1": "OLED 显示屏",
      "hw.r2": "按键 A / B",
      "hw.r3": "触摸按键 ×6",
      "hw.r4": "光线传感器",
      "hw.r5": "声音传感器",
      "hw.r6": "加速度计",
      "hw.r7": "陀螺仪",
      "hw.r8": "地磁传感器",
      "sc.title": "为真实课堂而设计",
      "sc.s1t": "图形化 → 代码过渡课",
      "sc.s1d": "学生先用 Mind+ 图形化编程，再观察转译后的 Python 代码，自然理解抽象概念。",
      "sc.s2t": "传感器认知课",
      "sc.s2d": "连接实体板或使用手动控制面板，直观理解加速度、光线、声音的数值变化。",
      "sc.s3t": "AI 代码改写课",
      "sc.s3d": "学生先写原始代码，再用本地 AI 改写为规范版本，对比中学习编程规范。",
      "sc.s4t": "无硬件演示课",
      "sc.s4d": "机房没有实体板时，虚拟板提供与真实硬件完全一致的教学体验。",
      "start.title": "三分钟跑起来",
      "start.sub": "Python 3.10+，Windows / macOS / Linux 全平台支持。",
      "start.tabWeb": "VM Studio 工作台",
      "start.tabDesk": "桌面版虚拟机",
      "start.github": "前往 GitHub 获取源码",
      "footer.slogan": "让掌控板编程学习，不再受硬件限制。",
      "footer.author": "开发作者：林奕呈"
    },
    "en": {
      "meta.title": "mPython VirtualBoard · Virtual Board Simulator",
      "nav.features": "Features",
      "nav.editions": "Editions",
      "nav.demo": "Live Demo",
      "nav.start": "Quick Start",
      "hero.eyebrow": "A board simulation platform for K-12 coding classes",
      "hero.title": "Learn <span class=\"grad\">board coding</span>,<br />no hardware required",
      "hero.sub": "mPython VirtualBoard faithfully recreates the mPython board on your computer: OLED, RGB LEDs, buttons, touch pads and a full set of sensors. Write, run and see — every coding class, free from hardware limits.",
      "hero.cta1": "Get Started",
      "hero.cta2": "Try the Live Board",
      "hero.stat1": "Simulated components",
      "hero.stat2": "Coding modes",
      "hero.stat3": "UI languages",
      "hero.stat4": "Free & open source",
      "why.title": "Removing the hardware barrier",
      "why.sub": "Not enough kits, fear of damage, handing out and collecting devices — none of these should block a coding class.",
      "why.c1t": "Zero-kit classes",
      "why.c1d": "Every student gets a complete board experience on their own computer. No bulk purchase, no maintenance.",
      "why.c2t": "What you code is what you see",
      "why.c2d": "Every line of code is reflected live on the virtual board's screen, lights and sensors. Debugging becomes intuitive.",
      "why.c3t": "A smooth path to real hardware",
      "why.c3d": "The same mPython / PinPong APIs: verify on the virtual board in class, flash to a real board at home.",
      "feat.title": "One toolkit for the whole teaching loop",
      "feat.sub": "From block-based coding to real Python, from virtual simulation to real sensors — all in one platform.",
      "feat.f1t": "Complete hardware simulation",
      "feat.f1d": "OLED display, 3 RGB LEDs, dual buttons, 6 touch pads, buzzer, plus accelerometer, gyroscope, magnetometer, light and sound sensors.",
      "feat.f2t": "Dual coding modes",
      "feat.f2d": "Switch freely between mPython and PinPong teaching paths to fit different curricula.",
      "feat.f3t": "Mind+ block transpiling",
      "feat.f3d": "Paste auto-generated Mind+ upload-mode code and the built-in transpiler converts it to Python and runs it — a smooth bridge from blocks to code.",
      "feat.f4t": "Local AI code rewriting",
      "feat.f4d": "PinPong mode integrates local Ollama + DeepSeek models, turning natural-language requirements into well-structured teaching code. Data never leaves your machine.",
      "feat.f5t": "Real sensor input",
      "feat.f5d": "Connect a physical board via USB serial to read real accelerometer, gyroscope, magnetometer, light and sound data in real time.",
      "feat.f6t": "Thonny integration & floating window",
      "feat.f6d": "The desktop edition works seamlessly with Thonny / IDLE, with an always-on-top floating board window while you code.",
      "ed.title": "Two editions, pick your fit",
      "ed.sub": "The same simulation core in two product shapes, for different teaching habits.",
      "ed.web.tag": "Recommended · All-in-one studio",
      "ed.web.desc": "A modern teaching workbench built with PyWebView + Vue3, with a built-in editor. Ready out of the box.",
      "ed.web.l1": "Monaco editor, F5 to run / F6 to stop",
      "ed.web.l2": "Mind+ upload-mode transpiling & running",
      "ed.web.l3": "Local AI rewriting in PinPong mode",
      "ed.web.l4": "Real sensor input over serial",
      "ed.web.l5": "Manual sensor control panel & presets",
      "ed.desk.tag": "Desktop · IDE integration",
      "ed.desk.desc": "A Tkinter + Socket simulator designed for classroom integration with Thonny / IDLE.",
      "ed.desk.l1": "One-click launcher for the whole stack",
      "ed.desk.l2": "Always-on-top floating display",
      "ed.desk.l3": "Remote control from Thonny / IDLE",
      "ed.desk.l4": "8 UI languages, switch anytime",
      "ed.desk.l5": "Virtual USB & client libraries",
      "demo.title": "Play for a minute first",
      "demo.sub": "Below is a living virtual board. Press its buttons, shake it — see what happens.",
      "demo.inputLabel": "Text for the OLED",
      "demo.inputPh": "Type something…",
      "demo.show": "Show",
      "demo.shake": "Simulate shake",
      "demo.rainbow": "RGB rainbow",
      "demo.hint": "Tip: you can also click the A / B buttons on the board itself.",
      "demo.msgA": "Button A pressed!",
      "demo.msgB": "Button B pressed!",
      "demo.msgShake": "Shaking! x:0.8 y:-0.3",
      "demo.msgRainbow": "Rainbow RGB ~",
      "demo.msgReady": "Ready.",
      "demo.codeDefault": "from mpython import *\n\noled.DispChar('Hello!', 0, 0)\noled.show()\nrgb[0] = (255, 0, 0)\nrgb.write()",
      "demo.codeShow": "from mpython import *\n\noled.DispChar('{TEXT}', 0, 0)\noled.show()",
      "demo.codeBtn": "from mpython import *\n\nwhile True:\n    if {BTN}.value:\n        oled.DispChar('{TEXT}', 0, 0)\n        oled.show()",
      "demo.codeShake": "from mpython import *\n\nx = accelerometer.get_x()\ny = accelerometer.get_y()\noled.DispChar('x:%.1f y:%.1f' % (x, y), 0, 0)\noled.show()",
      "demo.codeRainbow": "from mpython import *\n\ncolors = [(255,0,0), (255,165,0), (255,255,0),\n          (0,255,0), (0,0,255), (139,0,255)]\nfor i, c in enumerate(colors):\n    rgb[i % 3] = c\n    rgb.write()",
      "hw.title": "Familiar hardware, familiar APIs",
      "hw.sub": "The virtual board keeps the same programming interfaces as the real one — everything students learn transfers directly.",
      "hw.h1": "Component",
      "hw.r1": "OLED display",
      "hw.r2": "Buttons A / B",
      "hw.r3": "Touch pads ×6",
      "hw.r4": "Light sensor",
      "hw.r5": "Sound sensor",
      "hw.r6": "Accelerometer",
      "hw.r7": "Gyroscope",
      "hw.r8": "Magnetometer",
      "sc.title": "Designed for real classrooms",
      "sc.s1t": "Blocks-to-code transition",
      "sc.s1d": "Students start with Mind+ blocks, then read the transpiled Python to grasp abstract concepts naturally.",
      "sc.s2t": "Sensor exploration",
      "sc.s2d": "Connect a real board or use the manual control panel to see acceleration, light and sound values change live.",
      "sc.s3t": "AI code-rewriting practice",
      "sc.s3d": "Students write raw code first, then let local AI rewrite it into a canonical version — learning style by comparison.",
      "sc.s4t": "Hardware-free demos",
      "sc.s4d": "When no physical boards are available, the virtual board delivers an identical teaching experience.",
      "start.title": "Up and running in 3 minutes",
      "start.sub": "Python 3.10+. Works on Windows, macOS and Linux.",
      "start.tabWeb": "VM Studio",
      "start.tabDesk": "Desktop VM",
      "start.github": "Get the source on GitHub",
      "footer.slogan": "Learning board coding, free from hardware limits.",
      "footer.author": "Author: Lin Yicheng"
    }
  };

  var LANG_KEY = "mpvb-site-lang";
  var currentLang = "zh-CN";
  try {
    currentLang = localStorage.getItem(LANG_KEY) || "zh-CN";
  } catch (e) { /* localStorage 不可用时保持默认 */ }

  function t(key) {
    var pack = I18N[currentLang] || I18N["zh-CN"];
    return pack[key] != null ? pack[key] : (I18N["zh-CN"][key] || key);
  }

  function applyLang(lang) {
    currentLang = I18N[lang] ? lang : "zh-CN";
    try { localStorage.setItem(LANG_KEY, currentLang); } catch (e) {}
    document.documentElement.lang = currentLang;
    document.title = t("meta.title");
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.innerHTML = t(el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
    });
    var toggle = document.getElementById("langToggle");
    if (toggle) toggle.textContent = currentLang === "zh-CN" ? "EN" : "中文";
    restartHeroTyper();
    renderDemoCode(demoState.lastAction);
  }

  /* ---------------- 2. 导航交互 ---------------- */
  var nav = document.getElementById("nav");
  window.addEventListener("scroll", function () {
    nav.classList.toggle("is-scrolled", window.scrollY > 12);
  }, { passive: true });

  var burger = document.getElementById("navBurger");
  var navLinks = document.getElementById("navLinks");
  burger.addEventListener("click", function () {
    navLinks.classList.toggle("is-open");
  });
  navLinks.addEventListener("click", function (e) {
    if (e.target.tagName === "A") navLinks.classList.remove("is-open");
  });

  document.getElementById("langToggle").addEventListener("click", function () {
    applyLang(currentLang === "zh-CN" ? "en" : "zh-CN");
  });

  /* ---------------- 3. Hero OLED 打字机 ---------------- */
  var heroOled = document.getElementById("heroOled");
  var HERO_MSGS = {
    "zh-CN": ["Hello, mPython!", "你好，掌控板！", "for i in range(3):", "rgb.write()", "Ready to learn >"],
    "en": ["Hello, mPython!", "No hardware needed!", "for i in range(3):", "rgb.write()", "Ready to learn >"]
  };
  var heroTimer = null;

  function restartHeroTyper() {
    if (heroTimer) clearInterval(heroTimer);
    var msgs = HERO_MSGS[currentLang] || HERO_MSGS["zh-CN"];
    var idx = 0, charIdx = 0, deleting = false;
    heroOled.textContent = "";
    heroTimer = setInterval(function () {
      var msg = msgs[idx];
      if (!deleting) {
        charIdx++;
        heroOled.textContent = msg.slice(0, charIdx);
        if (charIdx >= msg.length) { deleting = true; charIdx = msg.length + 12; }
      } else {
        charIdx--;
        if (charIdx <= msg.length) heroOled.textContent = msg.slice(0, Math.max(charIdx, 0));
        if (charIdx <= 0) { deleting = false; idx = (idx + 1) % msgs.length; }
      }
    }, 90);
  }

  /* ---------------- 4. 可交互虚拟板演示 ---------------- */
  var demoOled = document.getElementById("demoOled");
  var demoCode = document.getElementById("demoCode");
  var demoBoard = document.getElementById("demoBoard");
  var demoLeds = [
    document.getElementById("demoRgb0"),
    document.getElementById("demoRgb1"),
    document.getElementById("demoRgb2")
  ];
  var demoState = { lastAction: "default", text: "" };
  var rainbowTimer = null;

  function setOled(text) {
    demoOled.textContent = text;
    demoOled.style.animation = "none";
    void demoOled.offsetWidth; /* 重启动画 */
    demoOled.style.animation = "";
  }

  function setLeds(colors) {
    demoLeds.forEach(function (led, i) {
      var c = colors[i];
      if (c) {
        led.style.background = c;
        led.style.boxShadow = "0 0 12px " + c + ", 0 0 26px " + c + "66";
      } else {
        led.style.background = "";
        led.style.boxShadow = "";
      }
    });
  }

  function stopRainbow() {
    if (rainbowTimer) { clearInterval(rainbowTimer); rainbowTimer = null; }
  }

  function renderDemoCode(action) {
    demoState.lastAction = action || "default";
    var code;
    switch (action) {
      case "show":
        code = t("demo.codeShow").replace("{TEXT}", demoState.text || "Hello!");
        break;
      case "btnA":
        code = t("demo.codeBtn").replace("{BTN}", "button_a").replace("{TEXT}", t("demo.msgA"));
        break;
      case "btnB":
        code = t("demo.codeBtn").replace("{BTN}", "button_b").replace("{TEXT}", t("demo.msgB"));
        break;
      case "shake":
        code = t("demo.codeShake");
        break;
      case "rainbow":
        code = t("demo.codeRainbow");
        break;
      default:
        code = t("demo.codeDefault");
    }
    demoCode.textContent = code;
  }

  /* 显示文字 */
  var demoText = document.getElementById("demoText");
  function doShow() {
    stopRainbow();
    var text = demoText.value.trim() || "Hello!";
    demoState.text = text;
    setOled(text);
    setLeds([]);
    renderDemoCode("show");
  }
  document.getElementById("demoShow").addEventListener("click", doShow);
  demoText.addEventListener("keydown", function (e) {
    if (e.key === "Enter") doShow();
  });

  /* A / B 按键 */
  function bindBoardButton(id, action, color) {
    var btn = document.getElementById(id);
    btn.addEventListener("click", function () {
      stopRainbow();
      btn.classList.add("is-pressed");
      setTimeout(function () { btn.classList.remove("is-pressed"); }, 160);
      setOled(t("demo.msg" + (action === "btnA" ? "A" : "B")));
      setLeds(action === "btnA" ? [color, null, null] : [null, null, color]);
      renderDemoCode(action);
    });
  }
  bindBoardButton("demoBtnA", "btnA", "#f43f5e");
  bindBoardButton("demoBtnB", "btnB", "#3b82f6");

  /* 模拟晃动 */
  document.getElementById("demoShake").addEventListener("click", function () {
    stopRainbow();
    setOled(t("demo.msgShake"));
    setLeds(["#10b981", "#10b981", "#10b981"]);
    renderDemoCode("shake");
    var n = 0;
    var shaker = setInterval(function () {
      demoBoard.style.transform =
        "translate(" + (Math.random() * 14 - 7) + "px," + (Math.random() * 10 - 5) + "px) rotate(" + (Math.random() * 4 - 2) + "deg)";
      if (++n > 10) {
        clearInterval(shaker);
        demoBoard.style.transform = "";
      }
    }, 50);
  });

  /* RGB 彩虹 */
  document.getElementById("demoRainbow").addEventListener("click", function () {
    stopRainbow();
    setOled(t("demo.msgRainbow"));
    renderDemoCode("rainbow");
    var palette = ["#f43f5e", "#f59e0b", "#facc15", "#10b981", "#3b82f6", "#8b5cf6"];
    var step = 0;
    rainbowTimer = setInterval(function () {
      setLeds([palette[step % 6], palette[(step + 2) % 6], palette[(step + 4) % 6]]);
      step++;
    }, 220);
    setTimeout(function () { stopRainbow(); setLeds([]); }, 4600);
  });

  /* ---------------- 5. 快速开始 Tab ---------------- */
  function bindTab(tabId, panelId) {
    document.getElementById(tabId).addEventListener("click", function () {
      document.querySelectorAll(".start-tab").forEach(function (el) { el.classList.remove("is-active"); });
      document.querySelectorAll(".start-panel").forEach(function (el) { el.classList.remove("is-active"); });
      document.getElementById(tabId).classList.add("is-active");
      document.getElementById(panelId).classList.add("is-active");
    });
  }
  bindTab("tabWeb", "panelWeb");
  bindTab("tabDesk", "panelDesk");

  /* ---------------- 6. 滚动进场动画（同组卡片交错延迟） ---------------- */
  var revealTargets = document.querySelectorAll(
    ".why-card, .feature-card, .edition-card, .scene-card, .hw-table-wrap, .demo-wrap, .start-panels"
  );
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var groupCount = new Map();
  revealTargets.forEach(function (el) {
    el.classList.add("reveal");
    var p = el.parentElement;
    var i = groupCount.get(p) || 0;
    el.style.setProperty("--d", Math.min(i * 70, 420) + "ms");
    groupCount.set(p, i + 1);
  });
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealTargets.forEach(function (el) { io.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------------- 7. 顶部滚动进度条 ---------------- */
  var progress = document.getElementById("scrollProgress");
  function updateProgress() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    progress.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress, { passive: true });
  updateProgress();

  /* ---------------- 8. 导航 Scrollspy ---------------- */
  var spyLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var spyMap = spyLinks.map(function (a) {
    return { a: a, sec: document.querySelector(a.getAttribute("href")) };
  }).filter(function (x) { return x.sec; });
  if ("IntersectionObserver" in window && spyMap.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          spyLinks.forEach(function (a) { a.classList.remove("is-active"); });
          var hit = spyMap.filter(function (x) { return x.sec === en.target; })[0];
          if (hit) hit.a.classList.add("is-active");
        }
      });
    }, { rootMargin: "-35% 0px -55% 0px" });
    spyMap.forEach(function (x) { spy.observe(x.sec); });
  }

  /* ---------------- 9. Hero 板 3D 倾斜 + 辉光跟随 ---------------- */
  var hero = document.querySelector(".hero");
  var heroBoard = document.querySelector(".hero-board");
  var boardFloat = document.querySelector(".board-float");
  var finePointer = window.matchMedia("(pointer: fine)").matches;
  if (hero && heroBoard && boardFloat && !reduceMotion && finePointer) {
    var tX = 0, tY = 0, cX = 0, cY = 0, rafId = null;
    var tiltLoop = function () {
      cX += (tX - cX) * 0.12;
      cY += (tY - cY) * 0.12;
      boardFloat.style.transform = "rotateX(" + cX.toFixed(2) + "deg) rotateY(" + cY.toFixed(2) + "deg)";
      if (Math.abs(tX - cX) > 0.02 || Math.abs(tY - cY) > 0.02) {
        rafId = requestAnimationFrame(tiltLoop);
      } else { rafId = null; }
    };
    var kickTilt = function () { if (!rafId) rafId = requestAnimationFrame(tiltLoop); };
    heroBoard.addEventListener("pointermove", function (e) {
      var r = heroBoard.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      tY = px * 14; tX = -py * 12;
      kickTilt();
    });
    heroBoard.addEventListener("pointerleave", function () { tX = 0; tY = 0; kickTilt(); });
    hero.addEventListener("pointermove", function (e) {
      var r = hero.getBoundingClientRect();
      hero.style.setProperty("--gx", ((e.clientX - r.left) / r.width * 100).toFixed(1) + "%");
      hero.style.setProperty("--gy", ((e.clientY - r.top) / r.height * 100).toFixed(1) + "%");
    });
  }

  /* ---------------- 10. 卡片聚光灯 ---------------- */
  if (finePointer && !reduceMotion) {
    document.querySelectorAll(".feature-card, .why-card, .scene-card, .edition-card").forEach(function (card) {
      card.classList.add("spotlight");
      card.addEventListener("pointermove", function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty("--mx", (e.clientX - r.left) + "px");
        card.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    });
  }

  /* ---------------- 11. Hero 数据计数动画 ---------------- */
  var statDts = document.querySelectorAll(".hero-stats dt");
  function animateCount(el) {
    var m = el.textContent.match(/^(\d+)(.*)$/);
    if (!m) return;
    var target = parseInt(m[1], 10), suffix = m[2] || "";
    var t0 = null, dur = 1300;
    var step = function (ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  if (!reduceMotion && "IntersectionObserver" in window && statDts.length) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { animateCount(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.4 });
    statDts.forEach(function (dt) { cio.observe(dt); });
  }

  /* ---------------- 12. 返回顶部 ---------------- */
  var toTop = document.getElementById("toTop");
  window.addEventListener("scroll", function () {
    toTop.classList.toggle("is-show", window.scrollY > 600);
  }, { passive: true });
  toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });

  /* ---------------- 启动 ---------------- */
  applyLang(currentLang);
})();
