/**
 * WorldQuant BRAIN Alpha Portal — v2 Application
 * Full auth state machine, 8-slot queue dashboard, pass/fail matrix,
 * results explorer with filtering/sorting, PnL chart modal.
 */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  // ═══════════════════════════════════════════════════ STATE ═══════════

  const state = {
    authenticated: false,
    userEmail: '',
    personaUrl: null,
    currentBatch: null,
    results: [],
    slots: [],
    sortCol: 'sharpe',
    sortAsc: false,
    eliteOnly: false,
    expandedRows: new Set(),
    pnlChart: null,
    pollInterval: null,
    slotElapsedTimers: {},
    lastRateLimit: {},
    batchItems: [],          // flat list of items from active batch for matrix
    batchUniverses: new Set()
  };

  // ═══════════════════════════════════════════════════ PRESETS ══════════

  const PRESETS = {
    momentum: [
      "normalize(ts_decay_linear(zscore(group_neutralize((rank(ts_delta(rank(returns), 3)) * rank(ts_delta(rank(volume), 3))), market)), 3))",
      "normalize(ts_decay_linear(zscore(group_neutralize((rank(ts_delta(rank(vwap), 5)) * rank(ts_delta(rank(adv20), 5))), market)), 2))",
      "normalize(ts_decay_linear(zscore(group_neutralize(rank(ts_delta(close, 5)) * rank(adv20), sector)), 5))"
    ],
    reversion: [
      "normalize(ts_decay_linear(zscore(group_neutralize((rank(ts_delta(implied_volatility_mean_skew_10, 3)) - rank(ts_delta(implied_volatility_mean_skew_10, 10))), market)), 2))",
      "normalize(ts_decay_linear(zscore(group_neutralize(-rank(ts_delta(close, 1)) * rank(adv20), industry)), 3))"
    ],
    volatility: [
      "normalize(ts_decay_linear(zscore(group_neutralize((rank(ts_delta(rank(returns), 3)) * rank(parkinson_volatility_10)), market)), 3))",
      "normalize(ts_decay_linear(zscore(group_neutralize(rank(ts_mean(volume/adv20, 10)), sector)), 5))"
    ],
    liquidity: [
      "normalize(ts_decay_linear(zscore(group_neutralize(((rank(rank(nws18_bee_fast_d1) - rank(adv20))) * rank(adv20)), market)), 5))",
      "normalize(ts_decay_linear(zscore(group_neutralize(rank(ts_mean(volume, 5)) - rank(ts_mean(volume, 20)), industry)), 3))"
    ]
  };

  // ═══════════════════════════════════════════════════ INIT ═════════════

  function init() {
    buildSlotGrid();
    bindLoginEvents();
    bindMainEvents();
    loadDefaultSettings();
    enterMainApp();
    checkAuthOnLoad();
  }

  // ═══════════════════════════════════════════════════ LOGIN ════════════

  function bindLoginEvents() {
    // Show/hide cookie paste area
    document.getElementById('loginCookieToggle').addEventListener('click', () => {
      const area = document.getElementById('cookiePasteArea');
      area.style.display = area.style.display === 'none' ? 'block' : 'none';
    });

    // Password visibility toggle
    document.getElementById('passToggle').addEventListener('click', () => {
      const inp = document.getElementById('loginPassword');
      const ico = document.getElementById('passToggle').querySelector('i');
      if (inp.type === 'password') {
        inp.type = 'text';
        ico.className = 'fa-solid fa-eye-slash';
      } else {
        inp.type = 'password';
        ico.className = 'fa-solid fa-eye';
      }
    });

    // Login button
    document.getElementById('loginBtn').addEventListener('click', handleLogin);
    document.getElementById('loginPassword').addEventListener('keydown', e => {
      if (e.key === 'Enter') handleLogin();
    });

    // Cookie save
    document.getElementById('cookieSaveBtn').addEventListener('click', handleCookieSave);

    // Face ID flow
    document.getElementById('openFaceScanBtn').addEventListener('click', () => {
      if (!state.personaUrl && !state.inquiryId) { toast('No face scan URL. Click Sign In first.', 'error'); return; }
      const targetUrl = state.inquiryId
        ? `https://api.worldquantbrain.com/authentication/persona?inquiry=${state.inquiryId}`
        : state.personaUrl;
      window.open(targetUrl, '_blank');
      toast('Face scan opened. Complete it, then click "Done — Verify Session".', 'info');
      pollPersonaAuth();
    });

    document.getElementById('verifyFaceBtn').addEventListener('click', async () => {
      await performPersonaVerification();
    });

    document.getElementById('backToLoginBtn').addEventListener('click', () => {
      showLoginStep('loginStepCredentials');
    });
  }

  async function performPersonaVerification() {
    const btn = document.getElementById('verifyFaceBtn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Verifying...';
    }

    try {
      const resp = await fetch('/api/auth/complete-persona', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona_url: state.personaUrl })
      });
      const data = await resp.json();

      if (data.success) {
        toast(`Face scan verified! Authenticated as ${data.user_email}`, 'success');
        state.authenticated = true;
        state.userEmail = data.user_email;
        enterMainApp();
      } else {
        const statusEl = document.getElementById('faceVerifyStatus');
        if (statusEl) {
          statusEl.textContent = data.message || 'Verification failed. Complete the face scan first.';
          statusEl.style.display = 'block';
          statusEl.style.background = 'rgba(255,77,109,0.1)';
          statusEl.style.color = 'var(--accent-red)';
        }
        toast(data.message || 'Face scan not yet complete. Try again.', 'warning');
      }
    } catch (e) {
      toast('Server error during verification.', 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Done — Verify Session';
      }
    }
  }

  function launchPersonaWindow(inquiryId) {
    const url = `https://api.worldquantbrain.com/authentication/persona?inquiry=${inquiryId}`;
    const popup = window.open(url, 'brain_face_scan', 'width=600,height=750,scrollbars=yes,resizable=yes');
    if (popup) {
      popup.focus();
      toast('Face Scan window opened. Complete the camera scan to authenticate.', 'info');
    } else {
      toast('Popup blocked by browser. Click "Open Face Scan" to open manually.', 'warning');
    }
    // Start auto-polling to detect when scan completes
    pollPersonaAuth();
  }

  async function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    const errEl = document.getElementById('loginError');

    if (!email || !password) {
      errEl.textContent = 'Please enter both email and password.';
      errEl.style.display = 'block';
      return;
    }
    errEl.style.display = 'none';
    setLoginBtnLoading(true);

    try {
      const resp = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await resp.json();

      if (data.success) {
        toast(`Authenticated as ${data.user_email}!`, 'success');
        state.authenticated = true;
        state.userEmail = data.user_email;
        enterMainApp();
      } else if (data.requires_persona) {
        state.personaUrl = data.persona_url;
        state.inquiryId = data.inquiry_id;

        showLoginStep('loginStepFaceId');
        const statusEl = document.getElementById('faceVerifyStatus');
        if (statusEl) {
          statusEl.textContent = 'Face scan required. Complete the scan in the popup window.';
          statusEl.style.display = 'block';
        }

        // Open standalone popup window (avoids iframe refused to connect!)
        if (data.inquiry_id) {
          launchPersonaWindow(data.inquiry_id);
        }
      } else {
        errEl.textContent = data.message || 'Authentication failed.';
        errEl.style.display = 'block';
      }
    } catch (e) {
      errEl.textContent = 'Server connection error. Is the portal running?';
      errEl.style.display = 'block';
    } finally {
      setLoginBtnLoading(false);
    }
  }

  async function handleCookieSave() {
    const cookie = document.getElementById('cookiePasteInput').value.trim();
    if (!cookie) { toast('Please paste a cookie or JWT token.', 'warning'); return; }

    try {
      const resp = await fetch('/api/auth/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookie })
      });
      const data = await resp.json();
      if (data.success) {
        toast(`Session valid: ${data.user_email}`, 'success');
        state.authenticated = true;
        state.userEmail = data.user_email;
        enterMainApp();
      } else {
        toast(`Cookie invalid: ${data.details || 'Unknown error'}`, 'error');
      }
    } catch (e) {
      toast('Error saving cookie.', 'error');
    }
  }

  function pollPersonaAuth() {
    // Poll the complete-persona endpoint every 5s — it checks if BRAIN accepted the face scan
    let attempts = 0;
    const maxAttempts = 36; // poll for 3 minutes max
    const interval = setInterval(async () => {
      attempts++;
      try {
        const resp = await fetch('/api/auth/complete-persona', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ persona_url: state.personaUrl })
        });
        const data = await resp.json();
        if (data.success) {
          clearInterval(interval);
          toast(`Face login verified! Authenticated as ${data.user_email}`, 'success');
          state.authenticated = true;
          state.userEmail = data.user_email;
          enterMainApp();
        }
        // If not yet complete, keep polling silently
      } catch (_) {}
      if (attempts >= maxAttempts) clearInterval(interval);
    }, 5000);
  }

  async function checkAuthOnLoad() {
    try {
      const resp = await fetch('/api/auth/status');
      const data = await resp.json();
      if (data.authenticated) {
        state.authenticated = true;
        state.userEmail = data.user_email;
        if (data.rate_limit) state.lastRateLimit = data.rate_limit;
        updateAuthBadge(true, state.userEmail);
      } else {
        updateAuthBadge(false, 'Auth Required');
        if (data.details && data.details.startsWith('FACE_REQUIRED:')) {
          state.personaUrl = data.details.replace('FACE_REQUIRED:', '');
          toast('Face scan required for launching new simulations. Click key icon to authenticate.', 'warning');
        }
      }
    } catch (_) {
      updateAuthBadge(false, 'Connecting...');
    }
  }

  async function checkAuthAndProceed() {
    try {
      const resp = await fetch('/api/auth/status');
      const data = await resp.json();
      if (data.authenticated) {
        toast(`Authenticated as ${data.user_email}`, 'success');
        state.authenticated = true;
        state.userEmail = data.user_email;
        enterMainApp();
      } else if (data.details && data.details.startsWith('FACE_REQUIRED:')) {
        state.personaUrl = data.details.replace('FACE_REQUIRED:', '');
        showLoginStep('loginStepFaceId');
        toast('Face scan required. Open the scan and complete it.', 'warning');
        pollPersonaAuth();
      } else {
        toast('Session not yet verified. Complete the face scan first.', 'warning');
      }
    } catch (_) {
      toast('Error checking auth.', 'error');
    }
  }

  function enterMainApp() {
    document.getElementById('loginOverlay').style.display = 'none';
    document.getElementById('mainApp').style.display = 'flex';
    updateAuthBadge(true, state.userEmail);
    startPolling();
    fetchResults();
    fetchRateLimit();
  }

  function showLoginStep(stepId) {
    document.querySelectorAll('.login-step').forEach(s => s.classList.remove('active'));
    document.getElementById(stepId).classList.add('active');
  }

  function setLoginBtnLoading(loading) {
    const btn = document.getElementById('loginBtn');
    btn.disabled = loading;
    btn.querySelector('.btn-login-text').style.display = loading ? 'none' : 'inline-flex';
    btn.querySelector('.btn-login-loading').style.display = loading ? 'inline-flex' : 'none';
  }

  // ═══════════════════════════════════════════════════ MAIN EVENTS ══════

  function bindMainEvents() {
    // Tab bar (alpha input)
    document.querySelectorAll('.tab[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        document.querySelectorAll('.tab[data-tab]').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(tabId).classList.add('active');
      });
    });

    // Preset insert
    document.getElementById('insertPresetBtn').addEventListener('click', () => {
      const key = document.getElementById('presetSelect').value;
      const exprs = PRESETS[key] || [];
      const inp = document.getElementById('alphaInput');
      const cur = inp.value.trim();
      inp.value = cur ? cur + '\n' + exprs.join('\n') : exprs.join('\n');
      updateExprCount();
      // switch to editor tab
      document.querySelector('.tab[data-tab="tabEditor"]').click();
      toast(`Inserted ${exprs.length} preset expressions.`, 'success');
    });

    // File upload
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('drag-over'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
    dropzone.addEventListener('drop', e => {
      e.preventDefault(); dropzone.classList.remove('drag-over');
      if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => { if (e.target.files.length) handleFileUpload(e.target.files[0]); });

    // Count expressions on input
    document.getElementById('alphaInput').addEventListener('input', updateExprCount);

    // Clear editor
    document.getElementById('clearEditorBtn').addEventListener('click', () => {
      document.getElementById('alphaInput').value = '';
      updateExprCount();
    });

    // Launch
    document.getElementById('launchBtn').addEventListener('click', handleLaunch);

    // Save defaults
    document.getElementById('saveDefaultsBtn').addEventListener('click', saveDefaultSettings);

    // Global cancel
    document.getElementById('globalCancelBtn').addEventListener('click', handleGlobalCancel);

    // Submitable Alphas button
    const subBtn = document.getElementById('viewSubmitableBtn');
    if (subBtn) subBtn.addEventListener('click', viewSubmitableReport);

    // Download Batch CSV button
    const csvBtn = document.getElementById('downloadBatchCsvBtn');
    if (csvBtn) {
      csvBtn.addEventListener('click', () => {
        if (!state.currentBatch) { toast('No active batch to download.', 'warning'); return; }
        window.open(`/api/simulations/batch/${state.currentBatch}/csv`, '_blank');
      });
    }

    // Open login overlay from badge
    document.getElementById('authBadge').addEventListener('click', () => {
      const overlay = document.getElementById('loginOverlay');
      overlay.style.display = overlay.style.display === 'flex' ? 'none' : 'flex';
    });

    // Open session modal
    document.getElementById('openSettingsCredBtn').addEventListener('click', () => {
      showModal('sessionModal');
    });
    document.getElementById('sessionSaveBtn').addEventListener('click', async () => {
      const cookie = document.getElementById('sessionCookieInput').value.trim();
      if (!cookie) return;
      const resp = await fetch('/api/auth/update', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookie })
      });
      const data = await resp.json();
      if (data.success) {
        toast(`Session updated: ${data.user_email}`, 'success');
        updateAuthBadge(true, data.user_email);
        hideModal('sessionModal');
      } else {
        toast('Failed to validate cookie.', 'error');
      }
    });

    // Modal close buttons
    document.querySelectorAll('.modal-close[data-close]').forEach(btn => {
      btn.addEventListener('click', () => hideModal(btn.getAttribute('data-close')));
    });
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', e => {
        if (e.target === modal) hideModal(modal.id);
      });
    });

    // Filters
    ['searchInput', 'filterStatus', 'filterUniverse', 'filterSharpe'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', renderResultsTable);
    });

    // Elite only toggle
    document.getElementById('eliteOnlyBtn').addEventListener('click', () => {
      state.eliteOnly = !state.eliteOnly;
      document.getElementById('eliteOnlyBtn').classList.toggle('active', state.eliteOnly);
      renderResultsTable();
    });

    // Sorting
    document.querySelectorAll('#resultsTable th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        const col = th.getAttribute('data-sort');
        if (state.sortCol === col) { state.sortAsc = !state.sortAsc; }
        else { state.sortCol = col; state.sortAsc = false; }
        renderResultsTable();
      });
    });

    // Universe Quick Chips
    document.querySelectorAll('.univ-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const val = chip.getAttribute('data-univ');
        const input = document.getElementById('sUniverse');
        if (input) input.value = val;
        document.querySelectorAll('.univ-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
      });
    });

    // Region change auto-suggest standard universe
    const regionEl = document.getElementById('sRegion');
    if (regionEl) {
      const regionDefaults = {
        USA: 'TOP3000',
        GLB: 'TOP3000',
        EUR: 'EUR_TOP1000',
        ASI: 'ASI_TOP1000',
        IND: 'IND_TOP500',
        CHN: 'CHN_TOP1000',
        KOR: 'KOR_TOP500',
        HKG: 'HKG_TOP500',
        DEU: 'DEU_TOP500',
        GBR: 'GBR_TOP500'
      };
      regionEl.addEventListener('change', () => {
        const selectedRegion = regionEl.value;
        const univInput = document.getElementById('sUniverse');
        if (univInput && regionDefaults[selectedRegion]) {
          univInput.value = regionDefaults[selectedRegion];
          toast(`Updated default universe for ${selectedRegion} to ${regionDefaults[selectedRegion]}`, 'info');
        }
      });
    }

    // Exports
    document.getElementById('exportCsvBtn').addEventListener('click', () => { window.location.href = '/api/export/csv'; });
    document.getElementById('exportEliteBtn').addEventListener('click', () => { window.location.href = '/api/export/elite'; });
  }

  // ═══════════════════════════════════════════════════ FILE UPLOAD ══════

  function handleFileUpload(file) {
    const reader = new FileReader();
    reader.onload = e => {
      const lines = e.target.result.split(/\r?\n/).map(l => l.trim()).filter(l => l && !l.startsWith('#'));
      if (!lines.length) { toast('No valid expressions in file.', 'warning'); return; }
      const inp = document.getElementById('alphaInput');
      const cur = inp.value.trim();
      inp.value = cur ? cur + '\n' + lines.join('\n') : lines.join('\n');
      updateExprCount();
      document.querySelector('.tab[data-tab="tabEditor"]').click();
      toast(`Loaded ${lines.length} expressions from ${file.name}`, 'success');
    };
    reader.readAsText(file);
  }

  function updateExprCount() {
    const raw = document.getElementById('alphaInput').value;
    const count = raw.split(/\n/).map(l => l.trim()).filter(l => l && !l.startsWith('#')).length;
    document.getElementById('exprCount').textContent = `${count} expression${count !== 1 ? 's' : ''}`;
  }

  // ═══════════════════════════════════════════════════ SETTINGS ═════════

  const SETTING_IDS = ['sLang', 'sInstrument', 'sRegion', 'sDelay', 'sUniverse',
    'sNeutralization', 'sDecay', 'sTruncation', 'sPasteurization', 'sUnitHandling',
    'sNanHandling', 'sPeriodYears', 'sPeriodMonths', 'sMaxTrade', 'sMaxPosition',
    'sDryRun', 'sAutoSubmit'];

  function saveDefaultSettings() {
    const settings = {};
    SETTING_IDS.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      settings[id] = el.type === 'checkbox' ? el.checked : el.value;
    });
    localStorage.setItem('brainPortalDefaults_v2', JSON.stringify(settings));
    toast('Settings saved as default.', 'success');
  }

  function loadDefaultSettings() {
    try {
      const saved = localStorage.getItem('brainPortalDefaults_v2');
      if (!saved) return;
      const settings = JSON.parse(saved);
      SETTING_IDS.forEach(id => {
        const el = document.getElementById(id);
        if (!el || !(id in settings)) return;
        if (el.type === 'checkbox') el.checked = settings[id];
        else el.value = settings[id];
      });
    } catch (_) {}
  }

  function getSettings() {
    const years = parseInt(document.getElementById('sPeriodYears').value, 10) || 0;
    const months = parseInt(document.getElementById('sPeriodMonths').value, 10) || 0;
    const testPeriod = (years > 0 || months > 0) ? `P${years}Y${months}M` : '';
    return {
      language: document.getElementById('sLang').value,
      instrumentType: document.getElementById('sInstrument').value,
      region: document.getElementById('sRegion').value,
      delay: parseInt(document.getElementById('sDelay').value, 10),
      universe: document.getElementById('sUniverse').value,
      neutralization: document.getElementById('sNeutralization').value,
      decay: parseInt(document.getElementById('sDecay').value, 10) || 0,
      truncation: parseFloat(document.getElementById('sTruncation').value) || 0.07,
      pasteurization: document.getElementById('sPasteurization').value,
      unitHandling: document.getElementById('sUnitHandling').value,
      nanHandling: document.getElementById('sNanHandling').value,
      testPeriod,
      maxTrade: document.getElementById('sMaxTrade').value,
      maxPosition: document.getElementById('sMaxPosition').value,
      dry_run: document.getElementById('sDryRun').checked,
      auto_submit: document.getElementById('sAutoSubmit').checked
    };
  }

  // ═══════════════════════════════════════════════════ LAUNCH ═══════════

  async function handleLaunch() {
    const rawInput = document.getElementById('alphaInput').value.trim();
    if (!rawInput) { toast('Please enter at least one alpha expression.', 'warning'); return; }

    let expressions = parseExpressions(rawInput);
    if (!expressions.length) { toast('No valid expressions parsed.', 'warning'); return; }

    const settings = getSettings();

    // Track universes for matrix
    state.batchUniverses = new Set([settings.universe]);
    state.batchItems = expressions.map(expr => ({ expression: expr, universe: settings.universe, status: 'QUEUED', result: null }));

    const btn = document.getElementById('launchBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Launching...';

    try {
      const resp = await fetch('/api/simulations/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expressions, settings })
      });
      const data = await resp.json();

      if (resp.ok && data.batch_id) {
        state.currentBatch = data.batch_id;
        toast(`Batch ${data.batch_id} launched — ${data.total_enqueued} alphas queued!`, 'success');
        showBatchProgress(0, data.total_enqueued);
        document.getElementById('matrixCard').style.display = 'block';
        renderMatrix();
        startPolling();
      } else {
        toast(`Launch error: ${data.error || 'Unknown error'}`, 'error');
      }
    } catch (e) {
      toast('Server error during launch.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-play"></i> Launch Simulation';
    }
  }

  function parseExpressions(raw) {
    let text = raw.trim();
    if (text.startsWith('```')) text = text.replace(/^```(?:json)?/, '').replace(/```$/, '').trim();
    let exprs = [];
    if (text.startsWith('[')) {
      try {
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed)) exprs = parsed.map(x => String(x).trim()).filter(Boolean);
      } catch (_) {}
    }
    if (!exprs.length) {
      exprs = text.split(/\n/).map(l => {
        let s = l.trim();
        while (s.length > 1 && ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'")) || s.startsWith(',') || s.endsWith(','))) {
          if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) s = s.slice(1,-1).trim();
          else if (s.startsWith(',')) s = s.slice(1).trim();
          else if (s.endsWith(',')) s = s.slice(0,-1).trim();
        }
        return s;
      }).filter(s => s && !s.startsWith('#'));
    }
    return exprs;
  }

  // ═══════════════════════════════════════════════════ GLOBAL CANCEL ════

  async function handleGlobalCancel() {
    if (!confirm('Cancel all running and queued simulations?')) return;
    try {
      const resp = await fetch('/api/simulations/cancel', { method: 'POST' });
      const data = await resp.json();
      toast(data.message || 'All simulations cancelled.', 'warning');
      fetchQueueAndSlots();
    } catch (e) {
      toast('Error cancelling.', 'error');
    }
  }

  async function cancelSingleSlot(batchId, itemIndex) {
    try {
      const resp = await fetch('/api/simulations/cancel/item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch_id: batchId, item_index: itemIndex })
      });
      const data = await resp.json();
      if (data.success) {
        toast(`Simulation slot cancelled.`, 'warning');
      } else {
        toast(data.error || 'Cannot cancel this slot.', 'error');
      }
    } catch (e) {
      toast('Error cancelling slot.', 'error');
    }
  }

  // ═══════════════════════════════════════════════════ POLLING ══════════

  function startPolling() {
    if (state.pollInterval) clearInterval(state.pollInterval);
    state.pollInterval = setInterval(fetchQueueAndSlots, 2500);
  }

  async function fetchQueueAndSlots() {
    try {
      const [slotsResp, batchesResp] = await Promise.all([
        fetch('/api/simulations/slots'),
        fetch('/api/simulations/batches')
      ]);

      if (slotsResp.ok) {
        state.slots = await slotsResp.json();
        renderSlots();
      }

      if (batchesResp.ok) {
        const batches = await batchesResp.json();
        const activeBatch = state.currentBatch
          ? batches.find(b => b.batch_id === state.currentBatch)
          : batches.find(b => b.status === 'RUNNING');

        if (activeBatch) {
          showBatchProgress(activeBatch.progress, activeBatch.total, activeBatch.completed, activeBatch);
          updateQueueBadge(activeBatch);

          if (activeBatch.status === 'COMPLETED' || activeBatch.status === 'CANCELLED') {
            fetchResults();
            fetchBatchDetails(activeBatch.batch_id);
          }
        } else if (batches.length === 0 || batches.every(b => !['RUNNING','PENDING'].includes(b.status))) {
          hideBatchProgress();
        }
      }
    } catch (_) {}
  }

  async function fetchBatchDetails(batchId) {
    try {
      const resp = await fetch(`/api/simulations/batch/${batchId}`);
      if (!resp.ok) return;
      const data = await resp.json();
      if (data.items) {
        // Update state.batchItems for matrix
        data.items.forEach((item, idx) => {
          if (state.batchItems[idx]) {
            state.batchItems[idx].status = item.status;
            state.batchItems[idx].result = item.result;
          }
        });
        renderMatrix();
      }
    } catch (_) {}
  }

  async function fetchResults() {
    try {
      const resp = await fetch('/api/results');
      if (!resp.ok) return;
      const data = await resp.json();
      state.results = Array.isArray(data) ? data : [];
      renderResultsTable();
    } catch (_) {}
  }

  async function fetchRateLimit() {
    try {
      const resp = await fetch('/api/simulations/ratelimit');
      if (!resp.ok) return;
      const data = await resp.json();
      state.lastRateLimit = data;
      updateRateLimitDisplay(data);
    } catch (_) {}
  }

  // ═══════════════════════════════════════════════════ SLOT GRID ════════

  function buildSlotGrid() {
    const grid = document.getElementById('slotGrid');
    grid.innerHTML = '';
    for (let i = 0; i < 8; i++) {
      const card = document.createElement('div');
      card.className = 'slot-card idle';
      card.id = `slot-card-${i}`;
      card.innerHTML = `
        <button class="slot-cancel-btn" id="slot-cancel-${i}" title="Cancel this simulation">
          <i class="fa-solid fa-xmark"></i>
        </button>
        <div class="slot-num">SLOT ${i + 1}</div>
        <div class="slot-status-icon" id="slot-icon-${i}">
          <i class="fa-solid fa-circle"></i>
        </div>
        <div class="slot-expr" id="slot-expr-${i}">idle</div>
        <div class="slot-elapsed" id="slot-elapsed-${i}"></div>
      `;
      grid.appendChild(card);

      document.getElementById(`slot-cancel-${i}`).addEventListener('click', () => {
        const slotData = state.slots[i];
        if (slotData && slotData.batch_id !== null && slotData.item_index !== null) {
          cancelSingleSlot(slotData.batch_id, slotData.item_index);
        }
      });
    }
  }

  function renderSlots() {
    const slots = state.slots;
    for (let i = 0; i < 8; i++) {
      const slotData = slots[i] || { status: 'IDLE', expression: null, start_time: null };
      const card = document.getElementById(`slot-card-${i}`);
      const iconEl = document.getElementById(`slot-icon-${i}`);
      const exprEl = document.getElementById(`slot-expr-${i}`);
      const elapsedEl = document.getElementById(`slot-elapsed-${i}`);

      if (!card) continue;

      const isActive = slotData.status === 'SIMULATING';

      card.className = `slot-card ${isActive ? 'simulating' : 'idle'}`;

      if (isActive) {
        iconEl.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        const expr = slotData.expression || '';
        exprEl.textContent = expr.length > 24 ? expr.substring(0, 24) + '…' : expr;
        exprEl.title = expr;

        // Elapsed timer
        if (slotData.start_time) {
          const started = new Date(slotData.start_time).getTime();
          if (!state.slotElapsedTimers[i]) {
            state.slotElapsedTimers[i] = setInterval(() => {
              const sec = Math.floor((Date.now() - started) / 1000);
              const el = document.getElementById(`slot-elapsed-${i}`);
              if (el) el.textContent = `${sec}s`;
            }, 1000);
          }
        }
      } else {
        iconEl.innerHTML = '<i class="fa-solid fa-circle"></i>';
        exprEl.textContent = 'idle';
        elapsedEl.textContent = '';
        if (state.slotElapsedTimers[i]) {
          clearInterval(state.slotElapsedTimers[i]);
          delete state.slotElapsedTimers[i];
        }
      }
    }

    // Update queue badge
    const running = slots.filter(s => s && s.status === 'SIMULATING').length;
    const badge = document.getElementById('queueBadge');
    if (running > 0) {
      badge.className = 'badge-pill badge-orange';
      badge.textContent = `${running}/8 running`;
    } else {
      badge.className = 'badge-pill badge-blue';
      badge.textContent = '8 slots ready';
    }
  }

  function showBatchProgress(progress, total, completed, batchData) {
    const area = document.getElementById('batchProgressArea');
    if (area) area.style.display = 'block';
    const pct = typeof progress === 'number' ? progress : 0;
    document.getElementById('batchProgressBar').style.width = `${pct}%`;
    const done = completed !== undefined ? completed : Math.floor((pct / 100) * total);
    document.getElementById('batchProgressLabel').textContent =
      `${done} / ${total} complete (${pct.toFixed(1)}%)`;

    if (batchData) {
      const startEl = document.getElementById('batchStartTime');
      const endEl = document.getElementById('batchEndTime');
      const durEl = document.getElementById('batchDuration');
      if (batchData.created_at) {
        const start = new Date(batchData.created_at);
        if (startEl) startEl.textContent = start.toLocaleTimeString();
        if (batchData.end_time) {
          const end = new Date(batchData.end_time);
          if (endEl) endEl.textContent = end.toLocaleTimeString();
          const secs = Math.max(0, Math.floor((end - start) / 1000));
          const mins = Math.floor(secs / 60);
          if (durEl) durEl.textContent = `${mins}m ${secs % 60}s`;
        } else {
          if (endEl) endEl.textContent = 'Running...';
          const secs = Math.max(0, Math.floor((Date.now() - start) / 1000));
          const mins = Math.floor(secs / 60);
          if (durEl) durEl.textContent = `${mins}m ${secs % 60}s`;
        }
      }
    }
  }

  function hideBatchProgress() {
    // Keep visible but at 100%
    document.getElementById('batchProgressBar').style.width = '100%';
  }

  function updateQueueBadge(batch) {
    const running = state.slots.filter(s => s && s.status === 'SIMULATING').length;
    const badge = document.getElementById('queueBadge');
    badge.className = 'badge-pill badge-orange';
    badge.textContent = `${running}/8 active · ${batch.total - batch.completed} queued`;
  }

  // ═══════════════════════════════════════════════════ PASS/FAIL MATRIX ═

  function renderMatrix() {
    const items = state.batchItems;
    if (!items || !items.length) return;

    const universes = [...state.batchUniverses];
    const matrixHead = document.getElementById('matrixHead');
    const matrixBody = document.getElementById('matrixBody');

    matrixHead.innerHTML = `<tr>
      <th style="min-width:160px">Alpha Expression</th>
      ${universes.map(u => `<th>${u}</th>`).join('')}
    </tr>`;

    matrixBody.innerHTML = items.map((item, idx) => {
      const expr = item.expression || '';
      const shortExpr = expr.length > 40 ? expr.substring(0, 40) + '…' : expr;
      const cells = universes.map(universe => {
        if (item.universe !== universe) return `<td class="matrix-cell"><span class="cell-empty">—</span></td>`;
        const status = item.status;
        const result = item.result;

        if (status === 'QUEUED') return `<td class="matrix-cell"><span class="cell-pending">⏳ Queued</span></td>`;
        if (status === 'SIMULATING') return `<td class="matrix-cell"><span class="cell-pending"><i class="fa-solid fa-circle-notch fa-spin"></i> Running</span></td>`;
        if (status === 'CANCELLED') return `<td class="matrix-cell"><span class="cell-fail">⊘ Cancelled</span></td>`;

        if (result && result.status === 'SUCCESS') {
          const sharpe = result.metrics?.sharpe;
          const failed = result.failed_checks || [];
          if (failed.length === 0) {
            return `<td class="matrix-cell">
              <span class="cell-pass">✓ PASS ${sharpe != null ? `(${Number(sharpe).toFixed(2)})` : ''}</span>
            </td>`;
          } else {
            return `<td class="matrix-cell">
              <span class="cell-fail">✗ ${failed.slice(0,2).join(', ')}${failed.length > 2 ? '…' : ''}</span>
            </td>`;
          }
        }
        if (result && result.status === 'CACHED_DUPLICATE') {
          const sharpe = result.metrics?.sharpe;
          return `<td class="matrix-cell">
            <span class="cell-pass">♻ Cached ${sharpe != null ? `(${Number(sharpe).toFixed(2)})` : ''}</span>
          </td>`;
        }
        const errTooltip = result?.error ? escHtml(result.error) : escHtml(result?.status || 'FAILED');
        return `<td class="matrix-cell" title="${errTooltip}"><span class="cell-fail" title="${errTooltip}">✗ ${escHtml(result?.status || 'FAILED')}</span></td>`;
      }).join('');

      return `<tr>
        <td class="matrix-alpha-col" title="${escHtml(expr)}">${escHtml(shortExpr)}</td>
        ${cells}
      </tr>`;
    }).join('');

    const total = items.length;
    const passed = items.filter(i => i.result?.status === 'SUCCESS' && !(i.result?.failed_checks?.length)).length;
    document.getElementById('matrixSubtitle').textContent = `${passed}/${total} passed`;
  }

  // ═══════════════════════════════════════════════════ RESULTS TABLE ════

  function renderResultsTable() {
    const tbody = document.getElementById('resultsBody');
    const searchQ = (document.getElementById('searchInput')?.value || '').toLowerCase();
    const fUniverse = (document.getElementById('filterUniverse')?.value || '').trim().toLowerCase();
    const fSharpe = document.getElementById('filterSharpe')?.value || 'ALL';

    let data = state.results.filter(r => {
      if (state.eliteOnly && (r.sharpe == null || Number(r.sharpe) < 1.25)) return false;
      if (fStatus !== 'ALL' && r.status !== fStatus) return false;
      if (fUniverse && fUniverse !== 'all' && !(r.universe || '').toLowerCase().includes(fUniverse)) return false;
      if (fSharpe !== 'ALL') {
        const threshold = parseFloat(fSharpe);
        if (r.sharpe == null || Number(r.sharpe) < threshold) return false;
      }
      if (searchQ) {
        const searchable = `${r.code || ''} ${r.universe || ''} ${r.neutralization || ''} ${r.status || ''}`.toLowerCase();
        if (!searchable.includes(searchQ)) return false;
      }
      return true;
    });

    // Sort
    data = data.sort((a, b) => {
      let av = a[state.sortCol], bv = b[state.sortCol];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      const numA = parseFloat(av), numB = parseFloat(bv);
      if (!isNaN(numA) && !isNaN(numB)) {
        return state.sortAsc ? numA - numB : numB - numA;
      }
      return state.sortAsc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    });

    document.getElementById('resultsCountBadge').textContent = `${data.length} alpha${data.length !== 1 ? 's' : ''}`;

    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="14" class="empty-row">No results match your filters.</td></tr>';
      return;
    }

    tbody.innerHTML = data.map((r, idx) => {
      const sharpe = r.sharpe != null ? Number(r.sharpe) : null;
      const fitness = r.fitness != null ? Number(r.fitness) : null;
      const returns = r.returns != null ? (Number(r.returns)).toFixed(2) : '—';
      const drawdown = r.drawdown != null ? (Number(r.drawdown)).toFixed(2) : '—';
      const margin = r.margin != null ? (Number(r.margin)).toFixed(4) : '—';
      const turnover = r.turnover != null ? (Number(r.turnover)).toFixed(2) : '—';

      const sharpeClass = sharpe == null ? '' :
        sharpe >= 1.25 ? 'sharpe-elite' :
        sharpe >= 1.0  ? 'sharpe-high' :
        sharpe >= 0.5  ? 'sharpe-ok' :
        sharpe >= 0    ? 'sharpe-low' : 'sharpe-neg';

      const sharpeStr = sharpe != null ? sharpe.toFixed(4) : '—';
      const fitnessStr = fitness != null ? fitness.toFixed(4) : '—';

      const statusClass = r.status === 'SUCCESS' ? 'status-success' :
        r.status === 'CACHED_DUPLICATE' ? 'status-cached' :
        r.status?.startsWith('FAILED') || r.status === 'ERROR' ? 'status-failed' : 'status-error';

      const statusLabel = r.status === 'CACHED_DUPLICATE' ? 'CACHED' : (r.status || 'UNKNOWN');

      const failedChecks = (r.failed_checks || []).filter(Boolean);
      const failedHtml = failedChecks.length
        ? `<div class="failed-checks">${failedChecks.slice(0,3).map(c => `<span class="check-tag">${escHtml(c)}</span>`).join('')}${failedChecks.length > 3 ? `<span class="check-tag">+${failedChecks.length-3}</span>` : ''}</div>`
        : '<span style="color:var(--accent-green);font-size:0.7rem">✓ All passed</span>';

      const alphaId = r.alpha_id || '';
      const expr = r.code || '';
      const shortExpr = expr.length > 40 ? expr.substring(0, 40) + '…' : expr;
      const rowId = `res-row-${idx}`;
      const expandId = `res-expand-${idx}`;

      return `
      <tr id="${rowId}">
        <td>
          <button class="expand-btn" onclick="toggleExpand('${rowId}','${expandId}')" title="Expand details">
            <i class="fa-solid fa-chevron-right" id="expand-icon-${idx}"></i>
          </button>
        </td>
        <td><span class="status-badge ${statusClass}">${escHtml(statusLabel)}</span></td>
        <td><span class="sharpe-val ${sharpeClass}">${sharpeStr}</span></td>
        <td>${fitnessStr}</td>
        <td>${returns}%</td>
        <td>${drawdown}%</td>
        <td>${margin}</td>
        <td>${turnover}%</td>
        <td><span style="font-size:0.72rem;font-weight:600;color:var(--accent-blue)">${escHtml(r.universe || '—')}</span></td>
        <td style="font-size:0.72rem">${escHtml(r.region || '—')}</td>
        <td style="font-size:0.72rem">${r.delay ?? '—'}</td>
        <td style="font-size:0.72rem">${escHtml(r.neutralization || '—')}</td>
        <td>
          <span class="expr-cell" title="${escHtml(expr)}" onclick="copyText('${encodeURIComponent(expr)}')">${escHtml(shortExpr)}</span>
        </td>
        <td>
          <div class="action-btns">
            ${alphaId ? `<button class="act-btn act-btn-view" onclick="openPnlModal('${alphaId}', ${JSON.stringify({sharpe, fitness, returns, margin, turnover, drawdown, universe: r.universe, delay: r.delay, neutralization: r.neutralization}).replace(/"/g, '&quot;')})"><i class="fa-solid fa-chart-area"></i> PnL</button>` : ''}
            ${alphaId && !alphaId.startsWith('MOCK_') ? `<button class="act-btn act-btn-submit" onclick="submitSingleAlpha('${alphaId}')" title="Submit Alpha to WorldQuant BRAIN"><i class="fa-solid fa-paper-plane"></i> Submit</button>` : ''}
            <button class="act-btn act-btn-copy" onclick="copyText('${encodeURIComponent(expr)}')"><i class="fa-solid fa-copy"></i></button>
          </div>
        </td>
      </tr>
      <tr id="${expandId}" class="expanded-row" style="display:none;">
        <td colspan="14">
          <div class="expanded-content">
            <div class="expanded-item"><span class="expanded-label">Alpha ID</span><span class="expanded-value">${escHtml(alphaId || '—')}</span></div>
            <div class="expanded-item"><span class="expanded-label">Decay</span><span class="expanded-value">${r.decay ?? '—'}</span></div>
            <div class="expanded-item"><span class="expanded-label">Truncation</span><span class="expanded-value">${r.truncation ?? '—'}</span></div>
            <div class="expanded-item"><span class="expanded-label">Pasteurization</span><span class="expanded-value">${escHtml(r.pasteurization || '—')}</span></div>
            <div class="expanded-item"><span class="expanded-label">NaN Handling</span><span class="expanded-value">${escHtml(r.nanHandling || '—')}</span></div>
            <div class="expanded-item"><span class="expanded-label">Unit Handling</span><span class="expanded-value">${escHtml(r.unitHandling || '—')}</span></div>
            <div class="expanded-item"><span class="expanded-label">Language</span><span class="expanded-value">${escHtml(r.language || '—')}</span></div>
            <div class="expanded-item" style="grid-column:1/-1"><span class="expanded-label">Failed Checks</span><div style="margin-top:4px">${failedHtml}</div></div>
            <div class="expanded-item" style="grid-column:1/-1"><span class="expanded-label">Expression</span><span class="expanded-value" style="font-family:var(--font-mono);font-size:0.68rem;word-break:break-all">${escHtml(expr)}</span></div>
          </div>
        </td>
      </tr>`;
    }).join('');
  }

  // Expose to inline handlers
  window.toggleExpand = function(rowId, expandId) {
    const expandRow = document.getElementById(expandId);
    const isHidden = expandRow.style.display === 'none';
    expandRow.style.display = isHidden ? 'table-row' : 'none';
  };

  window.copyText = function(encoded) {
    const text = decodeURIComponent(encoded);
    navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard!', 'success')).catch(() => {});
  };

  // ═══════════════════════════════════════════════════ PNL MODAL ════════

  window.openPnlModal = async function(alphaId, meta) {
    showModal('pnlModal');
    document.getElementById('pnlModalTitle').innerHTML = `<i class="fa-solid fa-chart-area"></i> PnL — ${alphaId}`;

    // Meta grid
    const metaGrid = document.getElementById('pnlMetaGrid');
    const metaItems = [
      { label: 'Sharpe', value: meta.sharpe != null ? Number(meta.sharpe).toFixed(4) : '—' },
      { label: 'Fitness', value: meta.fitness != null ? Number(meta.fitness).toFixed(4) : '—' },
      { label: 'Returns', value: meta.returns != null ? meta.returns + '%' : '—' },
      { label: 'Margin', value: meta.margin != null ? meta.margin : '—' },
      { label: 'Turnover', value: meta.turnover != null ? meta.turnover + '%' : '—' },
      { label: 'Drawdown', value: meta.drawdown != null ? meta.drawdown + '%' : '—' },
      { label: 'Universe', value: meta.universe || '—' },
      { label: 'Delay', value: meta.delay ?? '—' },
      { label: 'Neutralization', value: meta.neutralization || '—' }
    ];
    metaGrid.innerHTML = metaItems.map(m => `
      <div class="meta-item">
        <div class="meta-label">${m.label}</div>
        <div class="meta-value">${escHtml(String(m.value))}</div>
      </div>`).join('');

    // Fetch PnL
    try {
      const isMock = alphaId.startsWith('MOCK_');
      const resp = await fetch(`/api/alpha/${alphaId}/pnl${isMock ? '?mock=true' : ''}`);
      const data = await resp.json();
      const pnlData = data.pnl || [];

      const labels = pnlData.map(r => r[0]);
      const values = pnlData.map(r => r[1]);

      const canvas = document.getElementById('pnlCanvas');
      if (state.pnlChart) { state.pnlChart.destroy(); state.pnlChart = null; }

      state.pnlChart = new Chart(canvas, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Cumulative PnL',
            data: values,
            borderColor: '#00e5ff',
            backgroundColor: 'rgba(0,229,255,0.06)',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
            tooltip: {
              backgroundColor: 'rgba(13,20,36,0.95)',
              titleColor: '#00e5ff',
              bodyColor: '#e2e8f0',
              borderColor: 'rgba(0,229,255,0.3)',
              borderWidth: 1
            }
          },
          scales: {
            x: { ticks: { color: '#475569', font: { size: 10 }, maxTicksLimit: 8 }, grid: { color: 'rgba(255,255,255,0.04)' } },
            y: { ticks: { color: '#475569', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
          }
        }
      });
    } catch (_) {
      document.getElementById('pnlCanvas').parentElement.innerHTML =
        '<p style="color:var(--text-muted);text-align:center;padding:20px">PnL data unavailable for this alpha.</p>';
    }
  };

  // ═══════════════════════════════════════════════════ UI HELPERS ═══════

  function updateAuthBadge(ok, email) {
    const badge = document.getElementById('authBadge');
    const label = document.getElementById('authBadgeLabel');
    badge.className = ok ? 'auth-badge auth-badge-ok' : 'auth-badge auth-badge-err';
    label.textContent = ok ? (email || 'Authenticated') : 'Not authenticated';
  }

  function updateRateLimitDisplay(data) {
    const rem = document.getElementById('rlRemaining');
    const reset = document.getElementById('rlReset');
    if (data.remaining != null) rem.textContent = data.remaining;
    else rem.textContent = '—';
    if (data.reset_seconds != null) {
      const mins = Math.ceil(data.reset_seconds / 60);
      reset.textContent = `(resets in ${mins}m)`;
    }
  }

  function showModal(id) {
    document.getElementById(id).style.display = 'flex';
  }

  function hideModal(id) {
    document.getElementById(id).style.display = 'none';
    if (id === 'pnlModal' && state.pnlChart) {
      state.pnlChart.destroy();
      state.pnlChart = null;
    }
  }

  // ═══════════════════════════════════════════════════ TOAST ════════════

  function toast(msg, type = 'info') {
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
    const container = document.getElementById('toastContainer');
    const div = document.createElement('div');
    div.className = `toast toast-${type}`;
    div.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${escHtml(msg)}</span>`;
    container.appendChild(div);
    setTimeout(() => {
      div.classList.add('hiding');
      setTimeout(() => div.remove(), 300);
    }, 4000);
  }

  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }

  window.submitSingleAlpha = async function(alphaId) {
    if (!alphaId) return;
    if (!confirm(`Submit Alpha ${alphaId} to WorldQuant BRAIN for approval?`)) return;
    try {
      toast(`Submitting Alpha ${alphaId}...`, 'info');
      const resp = await fetch(`/api/alphas/${alphaId}/submit`, { method: 'POST' });
      const data = await resp.json();
      if (resp.ok && data.success) {
        toast(`✅ ${data.message}`, 'success');
      } else {
        toast(`❌ ${data.error || 'Submission failed'}`, 'error');
      }
    } catch (err) {
      toast(`Submission error: ${err.message}`, 'error');
    }
  };

  window.viewHighSharpeFile = async function() {
    try {
      const resp = await fetch('/api/reports/high-sharpe');
      const data = await resp.json();
      if (!data.exists || !data.count) {
        toast('No Sharpe ≥ 2.0 (0 warnings) alphas saved yet.', 'warning');
        return;
      }
      alert(`🏆 Saved High-Sharpe Alphas (Count: ${data.count}):\n\n${data.content.substring(0, 1500)}${data.content.length > 1500 ? '\n... (see high_sharpe_zero_warnings.txt)' : ''}`);
    } catch (err) {
      toast(`Error fetching report: ${err.message}`, 'error');
    }
  };

  async function viewSubmitableReport() {
    try {
      const resp = await fetch('/api/reports/submitable');
      const data = await resp.json();
      if (!data.exists || !data.count) {
        toast('No submitable alphas saved yet.', 'warning');
        return;
      }
      alert(`🚀 Submitable Alphas (Count: ${data.count}):\n\n${data.content.substring(0, 1500)}${data.content.length > 1500 ? '\n... (see submitable_alphas.txt & submitable_alphas.csv)' : ''}`);
    } catch (err) {
      toast(`Error fetching submitable report: ${err.message}`, 'error');
    }
  }
  window.viewSubmitableReport = viewSubmitableReport;

  // ═══════════════════════════════════════════════════ START ════════════
  init();
});
