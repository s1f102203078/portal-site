// トップページ Hero セクションの背景: モチベーショングラフを円錐の地形にし、
// 等高線として描画する。カーソルのX位置で等高線の間隔(密度)が変わる。
// bg-gray-50(明るい背景)向けに、線は暗い色の半透明で描画する。
(function () {
  const canvas = document.getElementById('terrain-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // ---- 啓介さんの自己分析シート「①モチベーショングラフ」の実データ(小2〜現在) ----
  const motivationData = [-3, 1, -2, 3, -1, 3, -4, 4, 5, 4, -4, -2, 2, 4, -1, -2, 3, -5, 2, -3, -5, 3];

  // ---- 固定パラメータ(トップページ用に確定した値) ----
  const RIDGE_AMP = 100;      // 山の高さ: スライダー範囲 0〜200 の 50%
  const SPREAD_PCT = 60;      // 円錐の裾野の広さ: スライダー範囲 5〜60 の 100%(最大値)
  const STEP_MIN = 4, STEP_MAX = 30; // 等高線の間隔: カーソルのX位置(0〜100%)で可変
  const REFERENCE_W = 1600;   // PC想定の基準幅。狭い画面では地形を縮小せず中央の窓だけ表示する

  let W, H, WORLD_W, viewOffsetX;
  let cachedGrid = null, cachedMinV = 0, cachedMaxV = 0;
  let currentStep = (STEP_MIN + STEP_MAX) / 2;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    W = canvas.width = Math.round(rect.width);
    H = canvas.height = Math.round(rect.height);
    WORLD_W = Math.max(W, REFERENCE_W);
    viewOffsetX = (WORLD_W - W) / 2;
    cachedGrid = null;
    buildAndCache();
    draw();
  }
  window.refreshTerrainBackground = resize;
  window.addEventListener('resize', resize);

  // 各データ点を円錐の頂点として扱い、実ピクセル距離に応じて線形減衰させる(=円錐の側面)
  function buildHeightGrid(cols, rows, ridgeAmp, spreadPct) {
    const n = motivationData.length;
    const spacing = WORLD_W / (n - 1);
    const peakPxY = H / 2;
    const MARGIN = 6;
    const baseUnit = Math.min(spacing, H * 0.4);
    const maxRadius = peakPxY - MARGIN;
    const radius = Math.min(baseUnit * (spreadPct / 30), maxRadius);
    const peakPxX = motivationData.map((_, k) => (k / (n - 1)) * WORLD_W);

    const grid = [];
    for (let j = 0; j < rows; j++) {
      const row = [];
      const py = (j / (rows - 1)) * H;
      for (let i = 0; i < cols; i++) {
        const px = viewOffsetX + (i / (cols - 1)) * W;
        let best = 0;
        for (let k = 0; k < n; k++) {
          const dx = px - peakPxX[k], dy = py - peakPxY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist >= radius) continue;
          const contribution = motivationData[k] * (1 - dist / radius);
          if (Math.abs(contribution) > Math.abs(best)) best = contribution;
        }
        row.push(best * (ridgeAmp / 5));
      }
      grid.push(row);
    }
    return grid;
  }

  function buildAndCache() {
    const cols = 140, rows = 80;
    cachedGrid = buildHeightGrid(cols, rows, RIDGE_AMP, SPREAD_PCT);
    cachedMinV = Infinity; cachedMaxV = -Infinity;
    cachedGrid.forEach(r => r.forEach(v => { if (v < cachedMinV) cachedMinV = v; if (v > cachedMaxV) cachedMaxV = v; }));
  }

  function marchingSquares(grid, cols, rows, level) {
    const segs = [];
    const val = (i, j) => grid[j][i];
    const interp = (v0, v1) => (level - v0) / (v1 - v0 + 1e-9);
    for (let j = 0; j < rows - 1; j++) {
      for (let i = 0; i < cols - 1; i++) {
        const tl = val(i, j), tr = val(i + 1, j), br = val(i + 1, j + 1), bl = val(i, j + 1);
        let idx = 0;
        if (tl > level) idx |= 8;
        if (tr > level) idx |= 4;
        if (br > level) idx |= 2;
        if (bl > level) idx |= 1;
        if (idx === 0 || idx === 15) continue;
        const top = [i + interp(tl, tr), j];
        const right = [i + 1, j + interp(tr, br)];
        const bottom = [i + interp(bl, br), j + 1];
        const left = [i, j + interp(tl, bl)];
        const table = {
          1: [[left, bottom]], 2: [[bottom, right]], 3: [[left, right]],
          4: [[top, right]], 5: [[left, top], [bottom, right]], 6: [[top, bottom]],
          7: [[left, top]], 8: [[top, left]], 9: [[top, bottom]],
          10: [[top, right], [left, bottom]], 11: [[top, right]], 12: [[left, right]],
          13: [[bottom, right]], 14: [[left, bottom]]
        };
        const lines = table[idx] || [];
        for (const [p0, p1] of lines) segs.push([p0, p1]);
      }
    }
    return segs;
  }

  function draw() {
    if (!cachedGrid) return;
    const cols = 140, rows = 80;
    const step = currentStep;

    ctx.clearRect(0, 0, W, H); // bg-gray-50 の上に敷くだけなので塗りつぶさず透明に

    const sx = W / (cols - 1), sy = H / (rows - 1);
    const levels = [];
    for (let L = Math.ceil(cachedMinV / step) * step; L <= cachedMaxV; L += step) levels.push(L);

    levels.forEach(level => {
      const segs = marchingSquares(cachedGrid, cols, rows, level);
      // 明るい背景(bg-gray-50)向け: 濃いグレーの半透明線
      ctx.strokeStyle = level === 0 ? 'rgba(17,24,39,0.22)' : 'rgba(17,24,39,0.10)';
      ctx.lineWidth = level === 0 ? 1.2 : 0.7;
      ctx.beginPath();
      segs.forEach(([p0, p1]) => {
        ctx.moveTo(p0[0] * sx, p0[1] * sy);
        ctx.lineTo(p1[0] * sx, p1[1] * sy);
      });
      ctx.stroke();
    });
  }

  // ---- カーソルのX位置(0〜100%)で等高線の間隔をリアルタイムに変える ----
  // タッチデバイスは mousemove がほぼ発火しないため中間値に固定される
  let rafPending = false;
  window.addEventListener('mousemove', (e) => {
    const pct = Math.min(1, Math.max(0, e.clientX / W));
    currentStep = STEP_MIN + pct * (STEP_MAX - STEP_MIN);
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(() => { draw(); rafPending = false; });
    }
  });

  resize();
})();
