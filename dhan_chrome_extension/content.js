// MiroFish AI Copilot — Injected Directly Inside Dhan Terminal (web.dhan.co / tv.dhan.co)

(function () {
  if (document.getElementById("mirofish-dhan-hud")) return;

  const API_BASE = "http://127.0.0.1:8000";
  let currentSymbol = "NIFTY";
  let seenAlertIds = new Set();

  const hud = document.createElement("div");
  hud.id = "mirofish-dhan-hud";
  hud.innerHTML = `
    <div class="mf-hud-header" id="mfHudHeader">
      <div class="mf-hud-title">
        <span>🇮🇳 MiroFish AI Copilot</span>
        <span class="mf-badge" style="background:rgba(34,197,94,0.2);color:#4ade80;border:1px solid #22c55e;" id="mfConnTag">LIVE</span>
      </div>
      <div class="mf-hud-controls">
        <button id="mfRefreshBtn" title="Refresh Now">↻</button>
        <button id="mfFullBtn" title="Open Full AI Dashboard">↗</button>
        <button id="mfMinBtn" title="Minimize/Expand">—</button>
      </div>
    </div>
    <div class="mf-hud-body" id="mfHudBody">
      <!-- Symbol Selector -->
      <div style="display:flex; gap:6px;">
        <select id="mfSymSelect" style="flex:1; background:#1e293b; color:#fff; border:1px solid #475569; border-radius:6px; padding:5px 8px; font-size:12px;">
          <option value="NIFTY">NIFTY 50</option>
          <option value="BANKNIFTY">BANK NIFTY</option>
          <option value="SENSEX">SENSEX</option>
          <option value="FINNIFTY">FINNIFTY</option>
          <option value="MIDCPNIFTY">MIDCPNIFTY</option>
          <option value="RELIANCE">RELIANCE</option>
          <option value="HDFCBANK">HDFC BANK</option>
          <option value="TATASTEEL">TATA STEEL</option>
          <option value="BAJFINANCE">BAJFINANCE</option>
          <option value="BHARTIARTL">BHARTI AIRTEL</option>
        </select>
        <button class="mf-btn" id="mfScanBtn">⚡ Analyze</button>
      </div>

      <!-- Anti-Loss Discipline Guard -->
      <div class="mf-section" id="mfGuardBox" style="border-color:rgba(34,197,94,0.35); background:rgba(34,197,94,0.06);">
        <div style="font-weight:700; color:#4ade80; margin-bottom:3px;">🛡️ Anti-Loss Discipline Guard (ID: 1000659782)</div>
        <div id="mfGuardText" style="font-size:11px; color:#cbd5e1;">Checking today's order count & risk rules...</div>
      </div>

      <!-- Smart Option Buyer vs Seller Regime -->
      <div class="mf-section" id="mfRegimeBox" style="border-color:rgba(251,191,36,0.4); background:rgba(251,191,36,0.07);">
        <div style="font-weight:800; color:#fbbf24; font-size:12.5px;" id="mfRegimeTitle">🤖 Detecting Option Regime...</div>
        <div id="mfRegimeSub" style="font-size:11px; color:#e2e8f0; margin-top:4px; line-height:1.4;">Scanning Momentum & Squeeze...</div>
      </div>

      <!-- Actionable Trade Plan -->
      <div class="mf-section">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <strong style="color:#a5f3fc;">🎯 Sniper Trade Plan</strong>
          <span id="mfActionBadge" class="mf-badge" style="background:rgba(99,102,241,0.25); color:#c7d2fe;">--</span>
        </div>
        <div id="mfTradePlan" style="font-size:11.5px; line-height:1.6; color:#cbd5e1;">Loading live levels...</div>
      </div>

      <!-- Pre-Breakout Radar Alerts -->
      <div class="mf-section">
        <div style="font-weight:700; color:#fde68a; margin-bottom:5px;">🚨 Pre-Breakout & Fast Momentum Radar</div>
        <div id="mfPreAlerts" style="font-size:11px; display:flex; flex-direction:column; gap:6px; max-height:150px; overflow-y:auto;">Scanning...</div>
      </div>
    </div>
  `;

  document.body.appendChild(hud);

  // Minimize / Expand
  document.getElementById("mfMinBtn").addEventListener("click", () => {
    hud.classList.toggle("minimized");
  });

  // Open Full Dashboard
  document.getElementById("mfFullBtn").addEventListener("click", () => {
    window.open(API_BASE, "_blank");
  });

  // Symbol Change & Refresh
  document.getElementById("mfSymSelect").addEventListener("change", (e) => {
    currentSymbol = e.target.value;
    refreshAllDhanCopilot();
  });
  document.getElementById("mfScanBtn").addEventListener("click", () => refreshAllDhanCopilot());
  document.getElementById("mfRefreshBtn").addEventListener("click", () => refreshAllDhanCopilot());

  // Make HUD Draggable
  const header = document.getElementById("mfHudHeader");
  let isDragging = false, startX, startY, startLeft, startTop;
  header.addEventListener("mousedown", (e) => {
    if (e.target.tagName === "BUTTON") return;
    isDragging = true;
    const rect = hud.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    startLeft = rect.left;
    startTop = rect.top;
    hud.style.bottom = "auto";
    hud.style.right = "auto";
    hud.style.left = startLeft + "px";
    hud.style.top = startTop + "px";
  });
  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    hud.style.left = (startLeft + (e.clientX - startX)) + "px";
    hud.style.top = (startTop + (e.clientY - startY)) + "px";
  });
  window.addEventListener("mouseup", () => { isDragging = false; });

  function playBeep() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [880, 1174].forEach((f, i) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.frequency.value = f;
        g.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.12);
        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.1);
        o.connect(g);
        g.connect(ctx.destination);
        o.start(ctx.currentTime + i * 0.12);
        o.stop(ctx.currentTime + i * 0.12 + 0.11);
      });
    } catch (e) {}
  }

  async function refreshAllDhanCopilot() {
    // 1. Check Dhan Account Discipline Guard
    try {
      const dRes = await fetch(`${API_BASE}/api/dhan/status`);
      const dData = await dRes.json();
      const conn = dData.connection || {};
      const guardBox = document.getElementById("mfGuardBox");
      const guardText = document.getElementById("mfGuardText");
      const ordCount = conn.today_orders_count || 0;
      const bal = Number(conn.available_balance || 0).toFixed(2);

      if (ordCount >= 6) {
        guardBox.style.borderColor = "#ef4444";
        guardBox.style.background = "rgba(239,68,68,0.15)";
        guardText.innerHTML = `<strong style="color:#f87171;">🛑 STOP OVERTRADING! Today Orders: ${ordCount}/6.</strong> Do NOT average losing options! Activate Kill-Switch.`;
      } else {
        guardBox.style.borderColor = "rgba(34,197,94,0.35)";
        guardBox.style.background = "rgba(34,197,94,0.06)";
        guardText.innerHTML = `Margin: <strong>Rs.${bal}</strong> | Today Orders: <strong>${ordCount}/6</strong> | Rule: <strong>NO Averaging Losers!</strong>`;
      }
    } catch (e) {}

    // 2. Adaptive Option Buyer vs Seller Regime
    try {
      const rRes = await fetch(`${API_BASE}/api/options/adaptive-regime?symbol=${encodeURIComponent(currentSymbol)}`);
      const rData = await rRes.json();
      const titleEl = document.getElementById("mfRegimeTitle");
      const subEl = document.getElementById("mfRegimeSub");
      const boxEl = document.getElementById("mfRegimeBox");
      const isBuy = (rData.regime_mode || "").includes("BUY");
      titleEl.textContent = `🤖 ${rData.regime_mode || "ADAPTIVE REGIME"}`;
      titleEl.style.color = isBuy ? "#4ade80" : "#38bdf8";
      boxEl.style.borderColor = isBuy ? "rgba(34,197,94,0.45)" : "rgba(56,189,248,0.45)";
      const legs = (rData.strategy_details?.legs || []).map(l => `${l.action} ${l.strike} ${l.type} @Rs.${l.premium}`).join(" | ");
      subEl.innerHTML = `${rData.rationale}<br/><strong style="color:#fde68a;">👉 ${rData.recommended_strategy}: ${legs}</strong>`;
    } catch (e) {}

    // 3. Sniper Trade Plan
    try {
      const aRes = await fetch(`${API_BASE}/api/analyze?symbol=${encodeURIComponent(currentSymbol)}`);
      const aData = await aRes.json();
      const cons = aData.consensus || {};
      const tp = cons.trade_plan || {};
      const act = cons.recommended_action || "WAIT";
      const badge = document.getElementById("mfActionBadge");
      badge.textContent = act.slice(0, 20);
      document.getElementById("mfTradePlan").innerHTML = `
        <div>Spot Price: <strong class="mf-green">Rs.${aData.live_quote?.current_price || '--'}</strong> (${aData.live_quote?.p_change || 0}%)</div>
        <div>Entry: <strong>${tp.entry_zone || '--'}</strong></div>
        <div>Stop-Loss (Strict): <strong class="mf-red">Rs.${tp.stop_loss || '--'}</strong></div>
        <div>Target 1 / 2: <strong class="mf-green">Rs.${tp.target_1 || '--'} / Rs.${tp.target_2 || '--'}</strong></div>
      `;
    } catch (e) {}

    // 4. Pre-Breakout & Fast Momentum Radar
    try {
      const mRes = await fetch(`${API_BASE}/api/market/momentum-fast`);
      const mData = await mRes.json();
      const notifs = mData.notifications || [];
      const container = document.getElementById("mfPreAlerts");

      if (notifs.length > 0) {
        let newBeep = false;
        container.innerHTML = notifs.slice(0, 4).map(n => {
          if (!seenAlertIds.has(n.id)) {
            seenAlertIds.add(n.id);
            newBeep = true;
          }
          const clr = n.priority === "HIGH_PRE_BREAKOUT" ? "#fbbf24" : "#4ade80";
          return `
            <div style="padding:6px 8px; border-left:3px solid ${clr}; background:rgba(255,255,255,0.03); border-radius:4px;">
              <div style="font-weight:700; color:${clr};">${n.symbol} — ${n.action}</div>
              <div style="color:#94a3b8; font-size:10.5px;">Sqz: ${n.squeeze_score}% | Mom: ${n.momentum_score} | ${n.option_mode}</div>
            </div>`;
        }).join("");
        if (newBeep) playBeep();
      }
    } catch (e) {}
  }

  refreshAllDhanCopilot();
  setInterval(refreshAllDhanCopilot, 25000);
})();
