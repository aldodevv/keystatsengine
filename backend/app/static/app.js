/**
 * Frontend JavaScript for IDX Emiten KeyStats & Scoring Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // 1. Tab Navigation
    // -------------------------------------------------------------
    const tabs = {
        'tab-single': 'section-single',
        'tab-compare': 'section-compare',
        'tab-screener': 'section-screener'
    };

    Object.keys(tabs).forEach(tabId => {
        const btn = document.getElementById(tabId);
        btn.addEventListener('click', () => {
            // Update Tab Styles
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.remove('active', 'text-white', 'bg-brand-600', 'shadow-md');
                t.classList.add('text-slate-400');
            });
            btn.classList.add('active', 'text-white', 'bg-brand-600', 'shadow-md');
            btn.classList.remove('text-slate-400');

            // Show corresponding section
            document.querySelectorAll('.tab-content').forEach(s => s.classList.add('hidden'));
            document.getElementById(tabs[tabId]).classList.remove('hidden');

            // Trigger fetch for tab if needed
            if (tabId === 'tab-compare') {
                runComparison();
            } else if (tabId === 'tab-screener') {
                runScreener('BUFFETT_MOAT');
            }
        });
    });

    // -------------------------------------------------------------
    // 2. Single Emiten Analysis
    // -------------------------------------------------------------
    const singleInput = document.getElementById('single-ticker-input');
    const searchBtn = document.getElementById('single-search-btn');
    const refreshLiveBtn = document.getElementById('refresh-live-price-btn');
    const simPriceInput = document.getElementById('sim-price-input');
    const simPriceBtn = document.getElementById('sim-price-btn');
    let currentActiveTicker = 'BBRI';

    async function loadSingleEmiten(ticker, customPrice = null, forceLive = false) {
        if (!ticker) return;
        ticker = ticker.trim().toUpperCase();
        currentActiveTicker = ticker;
        
        let url = `/api/v1/emiten/${ticker}?live=${forceLive}`;
        if (customPrice && customPrice > 0) {
            url += `&price=${customPrice}`;
        }
        
        try {
            const resp = await fetch(url);
            if (!resp.ok) {
                alert(`Emiten '${ticker}' tidak ditemukan atau data belum tersedia.`);
                return;
            }
            const data = await resp.json();
            renderSingleEmiten(data);
        } catch (err) {
            console.error(err);
            alert('Gagal mengambil data emiten.');
        }
    }

    function renderSingleEmiten(data) {
        document.getElementById('r-ticker').textContent = data.ticker;
        document.getElementById('r-name').textContent = data.name;
        document.getElementById('r-sector').textContent = data.sector;
        document.getElementById('r-industry').textContent = data.industry;
        document.getElementById('r-price').textContent = `Rp ${Number(data.current_price).toLocaleString('id-ID')}`;
        document.getElementById('r-market-cap').textContent = `Rp ${(data.market_cap / 1e12).toFixed(1)} T`;

        // Realtime Price Change %
        const priceChangeElem = document.getElementById('r-price-change');
        const pChange = data.price_change_pct || 0;
        priceChangeElem.textContent = `(${pChange >= 0 ? '+' : ''}${pChange.toFixed(2)}%)`;
        if (pChange >= 0) {
            priceChangeElem.className = "text-sm font-semibold font-mono text-emerald-400";
        } else {
            priceChangeElem.className = "text-sm font-semibold font-mono text-rose-400";
        }

        // Upside Badge
        const upside = data.valuation.upside_downside_pct;
        const upsideBadge = document.getElementById('r-upside-badge');
        upsideBadge.textContent = `${upside > 0 ? '+' : ''}${upside.toFixed(1)}% Upside`;
        if (upside > 0) {
            upsideBadge.className = "text-xs font-sans font-bold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        } else {
            upsideBadge.className = "text-xs font-sans font-bold px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30";
        }

        // Composite Score & Grade
        document.getElementById('r-composite-score').textContent = data.composite_score;
        const gradeElem = document.getElementById('r-grade');
        gradeElem.textContent = `GRADE ${data.grade}`;
        if (['A+', 'A'].includes(data.grade)) {
            gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
        } else if (data.grade === 'B') {
            gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-amber-500/20 text-amber-400 border border-amber-500/40";
        } else {
            gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-rose-500/20 text-rose-400 border border-rose-500/40";
        }

        // Action Verdict
        const verdictBadge = document.getElementById('r-verdict-badge');
        verdictBadge.textContent = data.verdict;
        if (data.verdict === 'STRONG BUY' || data.verdict === 'BUY') {
            verdictBadge.className = "mt-2 px-4 py-1.5 rounded-xl font-display font-extrabold text-sm tracking-wide bg-emerald-500 text-dark-bg shadow-lg shadow-emerald-500/30";
        } else if (data.verdict === 'HOLD') {
            verdictBadge.className = "mt-2 px-4 py-1.5 rounded-xl font-display font-extrabold text-sm tracking-wide bg-amber-500 text-dark-bg shadow-lg shadow-amber-500/30";
        } else {
            verdictBadge.className = "mt-2 px-4 py-1.5 rounded-xl font-display font-extrabold text-sm tracking-wide bg-rose-500 text-white shadow-lg shadow-rose-500/30";
        }
        document.getElementById('r-fair-value-text').textContent = `Target: Rp ${Number(data.valuation.average_fair_value).toLocaleString('id-ID')}`;

        // Sensitivity Matrix Scenarios
        const sensContainer = document.getElementById('sensitivity-cards-container');
        if (data.price_sensitivity_scenarios && data.price_sensitivity_scenarios.length > 0) {
            sensContainer.innerHTML = data.price_sensitivity_scenarios.map(sc => {
                const isBase = sc.price_change_pct === 0.0;
                const borderClass = isBase ? 'border-brand-500 bg-brand-500/10 shadow-lg ring-1 ring-brand-500/40' : 'border-dark-border bg-dark-bg/60 hover:border-slate-500';
                const label = isBase ? 'HARGA SEKARANG' : `${sc.price_change_pct > 0 ? '+' : ''}${sc.price_change_pct}%`;
                const verdictCol = sc.verdict === 'STRONG BUY' || sc.verdict === 'BUY' ? 'text-emerald-400' : (sc.verdict === 'HOLD' ? 'text-amber-400' : 'text-rose-400');

                return `
                    <div class="p-2.5 rounded-xl border ${borderClass} transition cursor-pointer" onclick="simulatePrice(${sc.simulated_price})">
                        <div class="text-[10px] font-bold ${isBase ? 'text-brand-300' : 'text-slate-400'}">${label}</div>
                        <div class="text-sm font-bold text-white mt-0.5">Rp ${Number(sc.simulated_price).toLocaleString('id-ID')}</div>
                        <div class="text-[11px] text-slate-300 mt-1">PER: <strong>${sc.per}x</strong></div>
                        <div class="text-[11px] text-purple-300">Div: <strong>${sc.dividend_yield}%</strong></div>
                        <div class="text-[11px] font-bold text-cyan-300 mt-0.5">Skor: ${sc.composite_score}</div>
                        <div class="text-[10px] font-bold ${verdictCol} mt-0.5">${sc.verdict}</div>
                    </div>
                `;
            }).join('');
        }

        // Pillar 1: Valuation
        document.getElementById('p-val-score').textContent = `${data.radar.valuation}/100`;
        document.getElementById('r-per').textContent = `${data.valuation.per}x`;
        document.getElementById('r-pbv').textContent = `${data.valuation.pbv}x`;
        document.getElementById('r-ev-ebitda').textContent = `${data.valuation.ev_ebitda}x`;
        document.getElementById('r-peg').textContent = data.valuation.peg_ratio ? `${data.valuation.peg_ratio}x` : 'N/A';
        document.getElementById('r-graham').textContent = data.valuation.graham_number ? `Rp ${Number(data.valuation.graham_number).toLocaleString('id-ID')}` : 'N/A';
        document.getElementById('r-dcf').textContent = data.valuation.dcf_fair_value ? `Rp ${Number(data.valuation.dcf_fair_value).toLocaleString('id-ID')}` : 'N/A';
        document.getElementById('r-avg-fair').textContent = `Rp ${Number(data.valuation.average_fair_value).toLocaleString('id-ID')}`;

        // Pillar 2: Profitability
        document.getElementById('p-prof-score').textContent = `${data.radar.profitability}/100`;
        document.getElementById('r-roe').textContent = `${data.profitability.roe}%`;
        document.getElementById('r-roa').textContent = `${data.profitability.roa}%`;
        document.getElementById('r-roic').textContent = `${data.profitability.roic}%`;
        document.getElementById('r-gpm').textContent = `${data.profitability.gpm}%`;
        document.getElementById('r-npm').textContent = `${data.profitability.npm}%`;
        document.getElementById('r-dupont-ato').textContent = `${data.profitability.dupont_asset_turnover}x`;
        document.getElementById('r-dupont-em').textContent = `${data.profitability.dupont_equity_multiplier}x`;

        // Pillar 3: Health & Solvency
        document.getElementById('p-health-score').textContent = `${data.radar.financial_health}/100`;
        document.getElementById('r-der').textContent = `${data.solvency.der}x`;
        document.getElementById('r-net-der').textContent = `${data.solvency.net_debt_to_equity}x`;
        document.getElementById('r-altman').textContent = `${data.solvency.altman_z_score} (${data.solvency.altman_zone})`;
        document.getElementById('r-piotroski').textContent = `${data.quality.piotroski_f_score} / 9`;
        document.getElementById('r-current-ratio').textContent = `${data.liquidity.current_ratio}x`;
        document.getElementById('r-cfo-ratio').textContent = `${data.quality.cfo_to_net_income}x`;

        // Pillar 4: Cash Flow & Dividend
        document.getElementById('p-cf-score').textContent = `${data.radar.cash_flow_quality}/100`;
        document.getElementById('r-fcf').textContent = `Rp ${(data.cash_flow_dividend.fcf / 1e12).toFixed(1)} T`;
        document.getElementById('r-fcf-yield').textContent = `${data.cash_flow_dividend.fcf_yield}%`;
        document.getElementById('r-div-yield').textContent = `${data.cash_flow_dividend.dividend_yield}%`;
        document.getElementById('r-dpr').textContent = `${data.cash_flow_dividend.dpr}%`;
        document.getElementById('r-rev-growth').textContent = `${data.growth.revenue_growth_yoy > 0 ? '+' : ''}${data.growth.revenue_growth_yoy}%`;
        document.getElementById('r-eps-growth').textContent = `${data.growth.eps_growth_yoy > 0 ? '+' : ''}${data.growth.eps_growth_yoy}%`;

        // Bank Panel
        const bankPanel = document.getElementById('bank-panel');
        if (data.bank_metrics) {
            bankPanel.classList.remove('hidden');
            document.getElementById('b-car').textContent = `${data.bank_metrics.car}%`;
            document.getElementById('b-npl-gross').textContent = `${data.bank_metrics.npl_gross}%`;
            document.getElementById('b-npl-net').textContent = `${data.bank_metrics.npl_net}%`;
            document.getElementById('b-nim').textContent = `${data.bank_metrics.nim}%`;
            document.getElementById('b-bopo').textContent = `${data.bank_metrics.bopo}%`;
            document.getElementById('b-casa').textContent = `${data.bank_metrics.casa}%`;
            document.getElementById('b-ldr').textContent = `${data.bank_metrics.ldr}%`;
        } else {
            bankPanel.classList.add('hidden');
        }

        // Radar Bar Charts
        document.getElementById('bar-val-txt').textContent = `${data.radar.valuation} / 100`;
        document.getElementById('bar-val').style.width = `${data.radar.valuation}%`;

        document.getElementById('bar-prof-txt').textContent = `${data.radar.profitability} / 100`;
        document.getElementById('bar-prof').style.width = `${data.radar.profitability}%`;

        document.getElementById('bar-health-txt').textContent = `${data.radar.financial_health} / 100`;
        document.getElementById('bar-health').style.width = `${data.radar.financial_health}%`;

        document.getElementById('bar-growth-txt').textContent = `${data.radar.growth} / 100`;
        document.getElementById('bar-growth').style.width = `${data.radar.growth}%`;

        document.getElementById('bar-cf-txt').textContent = `${data.radar.cash_flow_quality} / 100`;
        document.getElementById('bar-cf').style.width = `${data.radar.cash_flow_quality}%`;

        // Bull & Bear Cases
        const bullContainer = document.getElementById('list-bull-cases');
        bullContainer.innerHTML = (data.bull_cases || []).map(b => `<li class="flex items-start gap-1.5"><span class="text-emerald-400">✓</span> ${b}</li>`).join('') || '<li class="text-slate-500">Tidak ada bull case dominan.</li>';

        const bearContainer = document.getElementById('list-bear-cases');
        bearContainer.innerHTML = (data.bear_cases || []).map(b => `<li class="flex items-start gap-1.5"><span class="text-rose-400">⚠</span> ${b}</li>`).join('') || '<li class="text-slate-500">Tidak ada risiko mayor teridentifikasi.</li>';

        // Signal Flags
        const flagsContainer = document.getElementById('badge-flags-container');
        const greens = (data.green_flags || []).map(f => `<span class="px-2.5 py-1 rounded-lg text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">✓ ${f}</span>`);
        const reds = (data.red_flags || []).map(f => `<span class="px-2.5 py-1 rounded-lg text-xs font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">⚠ ${f}</span>`);
        flagsContainer.innerHTML = [...greens, ...reds].join('') || '<span class="text-slate-500 text-xs">Netral.</span>';
    }

    searchBtn.addEventListener('click', () => loadSingleEmiten(singleInput.value));
    singleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadSingleEmiten(singleInput.value);
    });

    if (refreshLiveBtn) {
        refreshLiveBtn.addEventListener('click', () => {
            loadSingleEmiten(currentActiveTicker, null, true);
        });
    }

    if (simPriceBtn) {
        simPriceBtn.addEventListener('click', () => {
            const p = parseFloat(simPriceInput.value);
            if (p > 0) loadSingleEmiten(currentActiveTicker, p);
        });
    }

    if (simPriceInput) {
        simPriceInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const p = parseFloat(simPriceInput.value);
                if (p > 0) loadSingleEmiten(currentActiveTicker, p);
            }
        });
    }

    window.simulatePrice = function(targetPrice) {
        if (simPriceInput) simPriceInput.value = targetPrice;
        loadSingleEmiten(currentActiveTicker, targetPrice);
    };

    document.querySelectorAll('.quick-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            singleInput.value = chip.textContent.trim();
            loadSingleEmiten(chip.textContent.trim());
        });
    });

    // -------------------------------------------------------------
    // 3. Peer Comparison Logic
    // -------------------------------------------------------------
    const compareInput = document.getElementById('compare-input');
    const compareRunBtn = document.getElementById('compare-run-btn');

    async function runComparison(customTickers) {
        const raw = customTickers || compareInput.value;
        const tickers = raw.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
        if (!tickers.length) return;

        try {
            const resp = await fetch('/api/v1/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers })
            });
            const data = await resp.json();
            renderComparison(data);
        } catch (err) {
            console.error(err);
        }
    }

    function renderComparison(data) {
        // Champions cards
        const champContainer = document.getElementById('compare-champions-container');
        const labels = {
            'cheapest_pe': { name: 'Cheapest P/E', icon: '💰', color: 'amber' },
            'cheapest_pbv': { name: 'Cheapest P/B', icon: '🏷️', color: 'yellow' },
            'highest_roe': { name: 'Highest ROE', icon: '🚀', color: 'emerald' },
            'highest_dividend_yield': { name: 'Top Dividend', icon: '💵', color: 'purple' },
            'highest_piotroski_f': { name: 'Top Quality F', icon: '⭐', color: 'cyan' },
            'overall_champion': { name: 'Overall Leader', icon: '🏆', color: 'emerald' }
        };

        champContainer.innerHTML = Object.keys(data.best_in_class).map(key => {
            const info = labels[key] || { name: key, icon: '✨', color: 'blue' };
            const ticker = data.best_in_class[key];
            return `
                <div class="bg-dark-card border border-dark-border p-3 rounded-xl shadow text-center">
                    <div class="text-xs text-slate-400 flex items-center justify-center gap-1">${info.icon} ${info.name}</div>
                    <div class="text-lg font-display font-black text-white mt-1">${ticker}</div>
                </div>
            `;
        }).join('');

        // Table Rows
        const tbody = document.getElementById('compare-tbody');
        tbody.innerHTML = data.items.map(item => {
            const isWinner = data.best_in_class['overall_champion'] === item.ticker;
            const scoreClass = isWinner ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30' : 'text-slate-200';
            const gradeClass = ['A+', 'A'].includes(item.grade) ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold';

            return `
                <tr class="hover:bg-dark-surface/40 transition">
                    <td class="p-3.5 font-bold text-white flex items-center gap-1.5">
                        <span class="px-2 py-0.5 rounded bg-brand-600/20 border border-brand-500/30 text-brand-300">${item.ticker}</span>
                        ${isWinner ? '👑' : ''}
                    </td>
                    <td class="p-3.5 text-right font-mono">Rp ${Number(item.current_price).toLocaleString('id-ID')}</td>
                    <td class="p-3.5 text-right font-mono ${data.best_in_class['cheapest_pe'] === item.ticker ? 'text-emerald-400 font-bold' : ''}">${item.per}x</td>
                    <td class="p-3.5 text-right font-mono ${data.best_in_class['cheapest_pbv'] === item.ticker ? 'text-emerald-400 font-bold' : ''}">${item.pbv}x</td>
                    <td class="p-3.5 text-right font-mono ${data.best_in_class['highest_roe'] === item.ticker ? 'text-emerald-400 font-bold' : ''}">${item.roe}%</td>
                    <td class="p-3.5 text-right font-mono">${item.der}x</td>
                    <td class="p-3.5 text-center font-mono ${data.best_in_class['highest_piotroski_f'] === item.ticker ? 'text-emerald-400 font-bold' : ''}">${item.piotroski_f_score}/9</td>
                    <td class="p-3.5 text-right font-mono">${item.altman_z_score}</td>
                    <td class="p-3.5 text-right font-mono ${data.best_in_class['highest_dividend_yield'] === item.ticker ? 'text-purple-400 font-bold' : ''}">${item.dividend_yield}%</td>
                    <td class="p-3.5 text-right font-mono ${item.upside_pct > 0 ? 'text-emerald-400' : 'text-rose-400'}">${item.upside_pct > 0 ? '+' : ''}${item.upside_pct}%</td>
                    <td class="p-3.5 text-center"><span class="px-2 py-0.5 rounded ${scoreClass}">${item.composite_score}</span></td>
                    <td class="p-3.5 text-center ${gradeClass}">${item.grade}</td>
                    <td class="p-3.5 text-center"><span class="px-2 py-0.5 text-[10px] rounded bg-dark-surface border border-dark-border text-slate-300">${item.verdict}</span></td>
                </tr>
            `;
        }).join('');
    }

    compareRunBtn.addEventListener('click', () => runComparison());
    document.querySelectorAll('.compare-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            compareInput.value = btn.dataset.tickers;
            runComparison(btn.dataset.tickers);
        });
    });

    // -------------------------------------------------------------
    // 4. Screener Logic
    // -------------------------------------------------------------
    let currentScreenerResults = [];

    async function runScreener(presetName, customCriteria = {}) {
        const payload = {
            preset: presetName || 'BUFFETT_MOAT',
            ...customCriteria
        };

        try {
            const resp = await fetch('/api/v1/screener/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            currentScreenerResults = data.results || [];
            renderScreener(data);
        } catch (err) {
            console.error(err);
        }
    }

    function renderScreener(data) {
        document.getElementById('screener-count-badge').textContent = `Menampilkan ${data.total_matched} Emiten Terpilih (${data.applied_preset || 'CUSTOM'})`;
        const tbody = document.getElementById('screener-tbody');

        tbody.innerHTML = data.results.map((item, idx) => {
            const gradeClass = ['A+', 'A'].includes(item.grade) ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold';
            const scoreClass = item.composite_score >= 75 ? 'text-emerald-400 font-bold' : 'text-slate-200';

            return `
                <tr class="hover:bg-dark-surface/40 transition">
                    <td class="p-3.5 text-slate-500">${idx + 1}</td>
                    <td class="p-3.5 font-bold text-brand-300">
                        <button class="hover:underline font-mono" onclick="switchSingle('${item.ticker}')">${item.ticker}</button>
                    </td>
                    <td class="p-3.5 text-slate-300 truncate max-w-[200px]">${item.name}</td>
                    <td class="p-3.5 text-slate-400">${item.sector}</td>
                    <td class="p-3.5 text-right font-mono">Rp ${Number(item.current_price).toLocaleString('id-ID')}</td>
                    <td class="p-3.5 text-right font-mono">${item.per}x</td>
                    <td class="p-3.5 text-right font-mono">${item.pbv}x</td>
                    <td class="p-3.5 text-right font-mono text-emerald-400">${item.roe}%</td>
                    <td class="p-3.5 text-right font-mono">${item.der}x</td>
                    <td class="p-3.5 text-center font-mono">${item.piotroski_f_score}/9</td>
                    <td class="p-3.5 text-right font-mono text-purple-400">${item.dividend_yield}%</td>
                    <td class="p-3.5 text-center font-mono ${scoreClass}">${item.composite_score}</td>
                    <td class="p-3.5 text-center ${gradeClass}">${item.grade}</td>
                    <td class="p-3.5 text-center"><span class="px-2 py-0.5 text-[10px] rounded bg-dark-surface border border-dark-border text-slate-300">${item.verdict}</span></td>
                </tr>
            `;
        }).join('');
    }

    window.switchSingle = function(ticker) {
        document.getElementById('tab-single').click();
        singleInput.value = ticker;
        loadSingleEmiten(ticker);
    };

    document.querySelectorAll('.screener-preset-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.screener-preset-card').forEach(c => {
                c.classList.remove('bg-brand-600/10', 'border-brand-500', 'text-white', 'shadow-lg');
                c.classList.add('bg-dark-card', 'border-dark-border', 'text-slate-300');
            });
            card.classList.add('bg-brand-600/10', 'border-brand-500', 'text-white', 'shadow-lg');
            card.classList.remove('bg-dark-card', 'border-dark-border', 'text-slate-300');

            runScreener(card.dataset.preset);
        });
    });

    document.getElementById('screener-filter-btn').addEventListener('click', () => {
        const custom = {
            min_roe: parseFloat(document.getElementById('f-min-roe').value) || null,
            max_der: parseFloat(document.getElementById('f-max-der').value) || null,
            min_piotroski_f: parseInt(document.getElementById('f-min-pio').value) || null,
            min_dividend_yield: parseFloat(document.getElementById('f-min-div').value) || null,
            max_pe: parseFloat(document.getElementById('f-max-pe').value) || null,
            min_composite_score: parseFloat(document.getElementById('f-min-score').value) || null
        };
        runScreener('CUSTOM', custom);
    });

    // CSV Export
    document.getElementById('screener-export-csv').addEventListener('click', () => {
        if (!currentScreenerResults.length) return;
        const headers = ["Ticker", "Company Name", "Sector", "Price", "PER", "PBV", "ROE", "DER", "Piotroski", "Altman Z", "Div Yield", "Composite Score", "Grade", "Verdict"];
        const rows = currentScreenerResults.map(it => [
            it.ticker, `"${it.name}"`, `"${it.sector}"`, it.current_price, it.per, it.pbv, it.roe, it.der, it.piotroski_f_score, it.altman_z_score, it.dividend_yield, it.composite_score, it.grade, it.verdict
        ]);

        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `idx_screener_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Initial load
    loadSingleEmiten('BBRI');
});
