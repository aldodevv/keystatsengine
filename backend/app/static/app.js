/**
 * Frontend JavaScript for IDX Emiten KeyStats & Scoring Engine
 * Stockbit-Grade Fundamental Intelligence Terminal
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('KeyStats Engine Frontend Initializing...');

    // -------------------------------------------------------------
    // 1. Tab Navigation
    // -------------------------------------------------------------
    const tabs = {
        'tab-market': 'section-market',
        'tab-single': 'section-single',
        'tab-compare': 'section-compare',
        'tab-screener': 'section-screener'
    };

    Object.keys(tabs).forEach(tabId => {
        const btn = document.getElementById(tabId);
        if (!btn) return;
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
            const targetSection = document.getElementById(tabs[tabId]);
            if (targetSection) {
                targetSection.classList.remove('hidden');
            }

            // Trigger fetch for tab if needed
            if (tabId === 'tab-market') {
                loadMarketSummary();
            } else if (tabId === 'tab-compare') {
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

    async function loadSingleEmiten(ticker, customPrice = null, forceLive = false, isSilent = false) {
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
                if (!isSilent) {
                    alert(`Emiten '${ticker}' tidak ditemukan atau data belum tersedia.`);
                }
                return;
            }
            const data = await resp.json();
            renderSingleEmiten(data);
        } catch (err) {
            console.error('Error loading single emiten:', err);
            if (!isSilent) {
                alert('Gagal mengambil data emiten.');
            }
        }
    }

    function renderSingleEmiten(data) {
        if (!data) return;

        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== undefined && val !== null) el.textContent = val;
        };

        setTxt('r-ticker', data.ticker);
        setTxt('r-name', data.name);
        setTxt('r-sector', data.sector);
        setTxt('r-industry', data.industry);
        setTxt('r-price', `Rp ${Number(data.current_price).toLocaleString('id-ID')}`);
        setTxt('r-market-cap', `Rp ${(data.market_cap / 1e12).toFixed(1)} T`);

        // Realtime Price Change %
        const priceChangeElem = document.getElementById('r-price-change');
        const pChange = data.price_change_pct || 0;
        if (priceChangeElem) {
            priceChangeElem.textContent = `(${pChange >= 0 ? '+' : ''}${pChange.toFixed(2)}%)`;
            priceChangeElem.className = pChange >= 0 ? "text-sm font-semibold font-mono text-brand-400" : "text-sm font-semibold font-mono text-rose-400";
        }

        // Upside Badge
        const upside = data.valuation?.upside_downside_pct || 0;
        const upsideBadge = document.getElementById('r-upside-badge');
        if (upsideBadge) {
            upsideBadge.textContent = `${upside > 0 ? '+' : ''}${upside.toFixed(1)}% Upside`;
            upsideBadge.className = upside > 0 
                ? "text-xs font-sans font-bold px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30"
                : "text-xs font-sans font-bold px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30";
        }

        // Composite Score & Grade
        setTxt('r-composite-score', data.composite_score);
        const gradeElem = document.getElementById('r-grade');
        if (gradeElem) {
            gradeElem.textContent = `GRADE ${data.grade}`;
            if (['A+', 'A'].includes(data.grade)) {
                gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-brand-500/20 text-brand-400 border border-brand-500/40";
            } else if (data.grade === 'B') {
                gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-amber-500/20 text-amber-400 border border-amber-500/40";
            } else {
                gradeElem.className = "px-2.5 py-0.5 text-xs font-bold font-mono rounded bg-rose-500/20 text-rose-400 border border-rose-500/40";
            }
        }

        // Action Verdict
        const verdictBadge = document.getElementById('r-verdict-badge');
        if (verdictBadge) {
            verdictBadge.textContent = data.verdict;
            if (data.verdict === 'STRONG BUY' || data.verdict === 'BUY') {
                verdictBadge.className = "mt-2 px-3.5 py-1.5 rounded-xl font-extrabold text-xs sm:text-sm tracking-wide bg-brand-600 text-white shadow-lg shadow-brand-600/30";
            } else if (data.verdict === 'HOLD') {
                verdictBadge.className = "mt-2 px-3.5 py-1.5 rounded-xl font-extrabold text-xs sm:text-sm tracking-wide bg-amber-500 text-dark-bg shadow-lg shadow-amber-500/30";
            } else {
                verdictBadge.className = "mt-2 px-3.5 py-1.5 rounded-xl font-extrabold text-xs sm:text-sm tracking-wide bg-rose-500 text-white shadow-lg shadow-rose-500/30";
            }
        }
        setTxt('r-fair-value-text', `Target: Rp ${Number(data.valuation?.average_fair_value || 0).toLocaleString('id-ID')}`);

        // Sensitivity Matrix Scenarios
        const sensContainer = document.getElementById('sensitivity-cards-container');
        if (sensContainer && data.price_sensitivity_scenarios) {
            sensContainer.innerHTML = data.price_sensitivity_scenarios.map(sc => {
                const isBase = sc.price_change_pct === 0.0;
                const borderClass = isBase ? 'border-brand-500 bg-brand-500/10 shadow-lg ring-1 ring-brand-500/40' : 'border-dark-border bg-dark-bg/60 hover:border-slate-500';
                const label = isBase ? 'HARGA SEKARANG' : `${sc.price_change_pct > 0 ? '+' : ''}${sc.price_change_pct}%`;
                const verdictCol = sc.verdict === 'STRONG BUY' || sc.verdict === 'BUY' ? 'text-brand-400' : (sc.verdict === 'HOLD' ? 'text-amber-400' : 'text-rose-400');

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
        setTxt('p-val-score', `${data.radar?.valuation || 0}/100`);
        setTxt('r-per', `${data.valuation?.per || 0}x`);
        setTxt('r-pbv', `${data.valuation?.pbv || 0}x`);
        setTxt('r-ev-ebitda', `${data.valuation?.ev_ebitda || 0}x`);
        setTxt('r-peg', data.valuation?.peg_ratio ? `${data.valuation.peg_ratio}x` : 'N/A');
        setTxt('r-graham', data.valuation?.graham_number ? `Rp ${Number(data.valuation.graham_number).toLocaleString('id-ID')}` : 'N/A');
        setTxt('r-dcf', data.valuation?.dcf_fair_value ? `Rp ${Number(data.valuation.dcf_fair_value).toLocaleString('id-ID')}` : 'N/A');
        setTxt('r-avg-fair', `Rp ${Number(data.valuation?.average_fair_value || 0).toLocaleString('id-ID')}`);

        // Pillar 2: Profitability
        setTxt('p-prof-score', `${data.radar?.profitability || 0}/100`);
        setTxt('r-roe', `${data.profitability?.roe || 0}%`);
        setTxt('r-roa', `${data.profitability?.roa || 0}%`);
        setTxt('r-roic', `${data.profitability?.roic || 0}%`);
        setTxt('r-gpm', `${data.profitability?.gpm || 0}%`);
        setTxt('r-npm', `${data.profitability?.npm || 0}%`);
        setTxt('r-dupont-ato', `${data.profitability?.dupont_asset_turnover || 0}x`);
        setTxt('r-dupont-em', `${data.profitability?.dupont_equity_multiplier || 0}x`);

        // Pillar 3: Health & Solvency
        setTxt('p-health-score', `${data.radar?.financial_health || 0}/100`);
        setTxt('r-der', `${data.solvency?.der || 0}x`);
        setTxt('r-net-der', `${data.solvency?.net_debt_to_equity || 0}x`);
        setTxt('r-altman', `${data.solvency?.altman_z_score || 0} (${data.solvency?.altman_zone || 'SAFE'})`);
        setTxt('r-piotroski', `${data.quality?.piotroski_f_score || 0} / 9`);
        setTxt('r-current-ratio', `${data.liquidity?.current_ratio || 0}x`);
        setTxt('r-cfo-ratio', `${data.quality?.cfo_to_net_income || 0}x`);
        setTxt('r-quality-badge', data.quality?.piotroski_f_score >= 7 ? 'PRISTINE' : 'ADEQUATE');

        // Pillar 4: Cash Flow & Dividend
        setTxt('p-cf-score', `${data.radar?.cash_flow_quality || 0}/100`);
        setTxt('r-fcf', `Rp ${((data.cash_flow_dividend?.fcf || 0) / 1e12).toFixed(1)} T`);
        setTxt('r-fcf-yield', `${data.cash_flow_dividend?.fcf_yield || 0}%`);
        setTxt('r-div-yield', `${data.cash_flow_dividend?.dividend_yield || 0}%`);
        setTxt('r-dpr', `${data.cash_flow_dividend?.dpr || 0}%`);
        setTxt('r-rev-growth', `${(data.growth?.revenue_growth_yoy || 0) > 0 ? '+' : ''}${data.growth?.revenue_growth_yoy || 0}%`);
        setTxt('r-eps-growth', `${(data.growth?.eps_growth_yoy || 0) > 0 ? '+' : ''}${data.growth?.eps_growth_yoy || 0}%`);
        setTxt('r-div-safe', (data.cash_flow_dividend?.dpr || 0) <= 80 ? 'SUSTAINABLE' : 'HIGH PAYOUT');

        // Bank Panel
        const bankPanel = document.getElementById('bank-panel');
        if (bankPanel) {
            if (data.bank_metrics && data.bank_metrics.is_bank) {
                bankPanel.classList.remove('hidden');
                setTxt('b-car', `${data.bank_metrics.car}%`);
                setTxt('b-npl-gross', `${data.bank_metrics.npl_gross}%`);
                setTxt('b-npl-net', `${data.bank_metrics.npl_net}%`);
                setTxt('b-nim', `${data.bank_metrics.nim}%`);
                setTxt('b-cir', `${data.bank_metrics.cost_to_income}%`);
                setTxt('b-casa', `${data.bank_metrics.casa_ratio}%`);
                setTxt('b-ldr', `${data.bank_metrics.ldr}%`);
            } else {
                bankPanel.classList.add('hidden');
            }
        }

        // Bull & Bear Cases & Red Flags
        const bullContainer = document.getElementById('r-bull-cases');
        if (bullContainer) {
            bullContainer.innerHTML = (data.bull_cases || []).map(b => `<li>${b}</li>`).join('') || '<li class="text-slate-500">Tidak ada bull case dominan.</li>';
        }

        const bearContainer = document.getElementById('r-bear-cases');
        if (bearContainer) {
            bearContainer.innerHTML = (data.bear_cases || []).map(b => `<li>${b}</li>`).join('') || '<li class="text-slate-500">Tidak ada risiko mayor teridentifikasi.</li>';
        }

        const flagsContainer = document.getElementById('r-red-flags');
        if (flagsContainer) {
            flagsContainer.innerHTML = (data.red_flags || []).map(f => `<li>${f}</li>`).join('') || '<li class="text-slate-500">Tidak ada red flag / risiko neraca aman.</li>';
        }
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            if (singleInput) loadSingleEmiten(singleInput.value);
        });
    }

    if (singleInput) {
        singleInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') loadSingleEmiten(singleInput.value);
        });
    }

    if (refreshLiveBtn) {
        refreshLiveBtn.addEventListener('click', () => {
            loadSingleEmiten(currentActiveTicker, null, true);
        });
    }

    if (simPriceBtn) {
        simPriceBtn.addEventListener('click', () => {
            const p = parseFloat(simPriceInput ? simPriceInput.value : 0);
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
            const t = chip.textContent.trim();
            if (singleInput) singleInput.value = t;
            loadSingleEmiten(t);
        });
    });

    // -------------------------------------------------------------
    // 3. Peer Comparison Logic
    // -------------------------------------------------------------
    const compareInput = document.getElementById('compare-input');
    const compareRunBtn = document.getElementById('compare-run-btn');

    async function runComparison(customTickers) {
        const raw = customTickers || (compareInput ? compareInput.value : 'BBCA,BBRI,BMRI,BBNI');
        const tickers = raw.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
        if (!tickers.length) return;

        try {
            const resp = await fetch('/api/v1/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers })
            });
            if (!resp.ok) return;
            const data = await resp.json();
            renderComparison(data);
        } catch (err) {
            console.error('Error running comparison:', err);
        }
    }

    function renderComparison(data) {
        if (!data) return;

        // Champions cards
        const champContainer = document.getElementById('compare-champions-container');
        if (champContainer && data.best_in_class) {
            const labels = {
                'cheapest_pe': { name: 'Cheapest P/E', icon: '💰' },
                'cheapest_pbv': { name: 'Cheapest P/B', icon: '🏷️' },
                'highest_roe': { name: 'Highest ROE', icon: '🚀' },
                'highest_dividend_yield': { name: 'Top Dividend', icon: '💵' },
                'highest_piotroski_f': { name: 'Top Quality F', icon: '⭐' },
                'overall_champion': { name: 'Overall Leader', icon: '🏆' }
            };

            champContainer.innerHTML = Object.keys(data.best_in_class).map(key => {
                const info = labels[key] || { name: key, icon: '✨' };
                const ticker = data.best_in_class[key];
                return `
                    <div class="bg-dark-card border border-dark-border p-3 rounded-xl shadow text-center">
                        <div class="text-xs text-slate-400 flex items-center justify-center gap-1">${info.icon} ${info.name}</div>
                        <div class="text-lg font-mono font-extrabold text-white mt-1">${ticker}</div>
                    </div>
                `;
            }).join('');
        }

        // Table Rows
        const tbody = document.getElementById('compare-tbody');
        if (tbody && data.items) {
            tbody.innerHTML = data.items.map(item => {
                const isWinner = data.best_in_class && data.best_in_class['overall_champion'] === item.ticker;
                const scoreClass = isWinner ? 'bg-brand-500/20 text-brand-300 font-bold border border-brand-500/30' : 'text-slate-200';
                const gradeClass = ['A+', 'A'].includes(item.grade) ? 'text-brand-400 font-bold' : 'text-amber-400 font-bold';

                return `
                    <tr class="hover:bg-dark-surface/40 transition">
                        <td class="p-3.5 font-bold text-white flex items-center gap-1.5 font-mono">
                            <span class="px-2 py-0.5 rounded bg-brand-600/20 border border-brand-500/30 text-brand-300">${item.ticker}</span>
                            ${isWinner ? '👑' : ''}
                        </td>
                        <td class="p-3.5 text-right font-mono">Rp ${Number(item.current_price).toLocaleString('id-ID')}</td>
                        <td class="p-3.5 text-right font-mono">${item.per}x</td>
                        <td class="p-3.5 text-right font-mono">${item.pbv}x</td>
                        <td class="p-3.5 text-right font-mono text-brand-400">${item.roe}%</td>
                        <td class="p-3.5 text-right font-mono">${item.der}x</td>
                        <td class="p-3.5 text-center font-mono">${item.piotroski_f_score}/9</td>
                        <td class="p-3.5 text-right font-mono">${item.altman_z_score}</td>
                        <td class="p-3.5 text-right font-mono text-purple-400">${item.dividend_yield}%</td>
                        <td class="p-3.5 text-right font-mono ${item.upside_pct > 0 ? 'text-brand-400' : 'text-rose-400'}">${item.upside_pct > 0 ? '+' : ''}${item.upside_pct}%</td>
                        <td class="p-3.5 text-center"><span class="px-2 py-0.5 rounded ${scoreClass}">${item.composite_score}</span></td>
                        <td class="p-3.5 text-center ${gradeClass}">${item.grade}</td>
                        <td class="p-3.5 text-center"><span class="px-2 py-0.5 text-[10px] rounded bg-dark-surface border border-dark-border text-slate-300">${item.verdict}</span></td>
                    </tr>
                `;
            }).join('');
        }
    }

    if (compareRunBtn) {
        compareRunBtn.addEventListener('click', () => runComparison());
    }

    document.querySelectorAll('.compare-preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (compareInput) compareInput.value = btn.dataset.tickers;
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
            if (!resp.ok) return;
            const data = await resp.json();
            currentScreenerResults = data.results || [];
            renderScreener(data);
        } catch (err) {
            console.error('Error running screener:', err);
        }
    }

    function renderScreener(data) {
        if (!data) return;

        const countBadge = document.getElementById('screener-count-badge');
        if (countBadge) {
            countBadge.textContent = `Menampilkan ${data.total_matched} Emiten Terpilih (${data.applied_preset || 'CUSTOM'})`;
        }

        const tbody = document.getElementById('screener-tbody');
        if (tbody && data.results) {
            tbody.innerHTML = data.results.map((item, idx) => {
                const gradeClass = ['A+', 'A'].includes(item.grade) ? 'text-brand-400 font-bold' : 'text-amber-400 font-bold';
                const scoreClass = item.composite_score >= 75 ? 'text-brand-400 font-bold' : 'text-slate-200';

                return `
                    <tr class="hover:bg-dark-surface/40 transition">
                        <td class="p-3.5 text-slate-500">${idx + 1}</td>
                        <td class="p-3.5 font-bold text-brand-300 font-mono">
                            <button class="hover:underline" onclick="switchSingle('${item.ticker}')">${item.ticker}</button>
                        </td>
                        <td class="p-3.5 text-slate-300 truncate max-w-[200px]">${item.name}</td>
                        <td class="p-3.5 text-slate-400">${item.sector}</td>
                        <td class="p-3.5 text-right font-mono">Rp ${Number(item.current_price).toLocaleString('id-ID')}</td>
                        <td class="p-3.5 text-right font-mono">${item.per}x</td>
                        <td class="p-3.5 text-right font-mono">${item.pbv}x</td>
                        <td class="p-3.5 text-right font-mono text-brand-400">${item.roe}%</td>
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
    }

    // -------------------------------------------------------------
    // 5. Market Summary & Daily Top Picks Logic
    // -------------------------------------------------------------
    let allMarketEmitens = [];
    let currentMarketData = null;

    async function loadMarketSummary(retryCount = 0) {
        const topPicksContainer = document.getElementById('top-picks-container');
        const tbody = document.getElementById('market-tbody');
        
        try {
            const resp = await fetch('/api/v1/market/summary');
            if (!resp.ok) {
                throw new Error(`HTTP status ${resp.status}`);
            }
            const data = await resp.json();
            currentMarketData = data;
            allMarketEmitens = data.emitens || [];

            renderMarketOverview(data);
        } catch (err) {
            console.error('Error fetching market summary:', err);
            // Auto retry if server is waking up
            if (retryCount < 3) {
                console.log(`Retrying market summary in 2s (attempt ${retryCount + 1})...`);
                setTimeout(() => loadMarketSummary(retryCount + 1), 2000);
                return;
            }

            if (topPicksContainer) {
                topPicksContainer.innerHTML = `
                    <div class="col-span-full bg-dark-card border border-brand-500/30 rounded-2xl p-6 text-center space-y-3">
                        <div class="text-brand-400 text-sm font-bold">⚡ Menghubungkan ke Server Fundamental...</div>
                        <p class="text-xs text-slate-400">Server sedang menyiapkan kalkulasi IDX. Klik tombol di bawah untuk memuat data.</p>
                        <button onclick="loadMarketSummary(0)" class="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition shadow-md inline-flex items-center gap-2">
                            <span>🔄 Muat Ulang Rekomendasi</span>
                        </button>
                    </div>
                `;
            }
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="13" class="p-6 text-center text-slate-400 font-mono text-xs">
                            Server sedang memproses. Klik tombol "Update Rekomendasi" di atas untuk memuat ulang.
                        </td>
                    </tr>
                `;
            }
        }
    }
    window.loadMarketSummary = loadMarketSummary;

    function renderMarketOverview(data) {
        if (!data) return;

        // Date and Stats
        const dateEl = document.getElementById('market-generated-date');
        if (dateEl && data.generated_at_desc) {
            dateEl.textContent = data.generated_at_desc;
        }

        const stats = data.stats;
        if (stats) {
            const elTotal = document.getElementById('m-stat-total');
            const elUnder = document.getElementById('m-stat-undervalued');
            const elOver = document.getElementById('m-stat-overvalued');
            const elScore = document.getElementById('m-stat-avg-score');
            const elRoe = document.getElementById('m-stat-avg-roe');
            const elDiv = document.getElementById('m-stat-avg-div');

            if (elTotal) elTotal.textContent = stats.total_emitens;
            if (elUnder) elUnder.textContent = stats.undervalued_count;
            if (elOver) elOver.textContent = stats.overvalued_count;
            if (elScore) elScore.textContent = stats.avg_composite_score;
            if (elRoe) elRoe.textContent = `${stats.avg_roe}%`;
            if (elDiv) elDiv.textContent = `${stats.avg_dividend_yield}%`;
        }

        // Render Top Picks Cards
        const topPicksContainer = document.getElementById('top-picks-container');
        if (topPicksContainer && data.top_picks) {
            const colorMap = {
                emerald: {
                    border: 'border-brand-500/30 hover:border-brand-400',
                    bgGlow: 'bg-emerald-950/15',
                    tagBg: 'bg-brand-500/15 text-brand-400 border-brand-500/30',
                    btnBg: 'bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-600/20',
                    textAcc: 'text-brand-400'
                },
                cyan: {
                    border: 'border-cyan-500/30 hover:border-cyan-400',
                    bgGlow: 'bg-cyan-950/15',
                    tagBg: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
                    btnBg: 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/20',
                    textAcc: 'text-cyan-400'
                },
                indigo: {
                    border: 'border-indigo-500/30 hover:border-indigo-400',
                    bgGlow: 'bg-indigo-950/15',
                    tagBg: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
                    btnBg: 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20',
                    textAcc: 'text-indigo-400'
                },
                amber: {
                    border: 'border-amber-500/30 hover:border-amber-400',
                    bgGlow: 'bg-amber-950/15',
                    tagBg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
                    btnBg: 'bg-amber-600 hover:bg-amber-500 text-white shadow-lg shadow-amber-600/20',
                    textAcc: 'text-amber-400'
                }
            };

            topPicksContainer.innerHTML = data.top_picks.map(pick => {
                const c = colorMap[pick.badge_color] || colorMap.emerald;
                const upsideSign = pick.upside_pct >= 0 ? '+' : '';
                const upsideColor = pick.upside_pct >= 0 ? 'text-brand-400' : 'text-rose-400';

                return `
                    <div class="top-pick-card bg-dark-card border ${c.border} rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col justify-between relative overflow-hidden ${c.bgGlow}">
                        <div class="space-y-3.5">
                            <!-- Category Badge -->
                            <div class="flex items-center justify-between gap-2">
                                <span class="px-2.5 py-0.5 text-[10px] font-mono font-bold rounded-full border ${c.tagBg}">
                                    ${pick.category_tag}
                                </span>
                                <span class="px-2 py-0.5 text-xs font-mono font-bold rounded-lg bg-dark-bg border border-dark-border ${pick.grade.startsWith('A') ? 'text-brand-400' : 'text-amber-400'}">
                                    Grade ${pick.grade} (${pick.composite_score})
                                </span>
                            </div>

                            <!-- Ticker & Company Name -->
                            <div>
                                <div class="flex items-center gap-2">
                                    <span class="text-2xl font-extrabold text-white tracking-tight font-mono">${pick.ticker}</span>
                                    <span class="text-xs text-slate-400 truncate max-w-[170px]">${pick.name}</span>
                                </div>
                                <span class="text-[11px] text-slate-500 font-mono">${pick.sector}</span>
                            </div>

                            <!-- Price vs Fair Value & Upside -->
                            <div class="p-3 bg-dark-bg/90 border border-dark-border rounded-xl font-mono text-xs space-y-1.5">
                                <div class="flex items-center justify-between text-slate-400">
                                    <span>Harga Pasar:</span>
                                    <span class="text-slate-100 font-bold">Rp ${Number(pick.current_price).toLocaleString('id-ID')}</span>
                                </div>
                                <div class="flex items-center justify-between text-slate-400">
                                    <span>Nilai Wajar:</span>
                                    <span class="${c.textAcc} font-bold">Rp ${Number(pick.fair_value).toLocaleString('id-ID')}</span>
                                </div>
                                <div class="flex items-center justify-between border-t border-dark-border pt-1">
                                    <span class="text-slate-300 font-sans font-medium text-[11px]">Potensi Upside:</span>
                                    <span class="${upsideColor} font-bold text-sm">${upsideSign}${pick.upside_pct.toFixed(1)}%</span>
                                </div>
                            </div>

                            <!-- Key Metrics Pills -->
                            <div class="flex flex-wrap gap-1.5 text-[10px] font-mono">
                                ${pick.key_metrics_summary.map(m => `
                                    <span class="px-2 py-0.5 rounded bg-dark-surface border border-dark-border text-slate-300">${m}</span>
                                `).join('')}
                            </div>

                            <!-- Catalyst Paragraph -->
                            <div class="text-xs text-slate-300 leading-relaxed bg-dark-bg/60 p-2.5 rounded-lg border border-dark-border/70">
                                <span class="text-slate-400 font-medium block text-[10px] uppercase font-mono mb-1">💡 Katalis Esok Hari:</span>
                                ${pick.catalyst}
                            </div>
                        </div>

                        <!-- Action Button -->
                        <div class="mt-4 pt-3 border-t border-dark-border">
                            <button onclick="switchSingle('${pick.ticker}')" class="w-full py-2.5 px-4 rounded-xl ${c.btnBg} font-bold text-xs transition-all flex items-center justify-center gap-2">
                                <span>🔍 Lihat Detail Analisis ${pick.ticker}</span>
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Populate Sector Filter Options
        const sectorSelect = document.getElementById('market-sector-filter');
        if (sectorSelect) {
            const sectors = Array.from(new Set(allMarketEmitens.map(e => e.sector))).filter(Boolean).sort();
            sectorSelect.innerHTML = '<option value="ALL">Semua Sektor</option>' + 
                sectors.map(s => `<option value="${s}">${s}</option>`).join('');
        }

        // Render Table
        renderMarketTable();
    }

    function renderMarketTable() {
        const tbody = document.getElementById('market-tbody');
        if (!tbody) return;

        const searchQuery = (document.getElementById('market-search-input')?.value || '').trim().toUpperCase();
        const selectedSector = document.getElementById('market-sector-filter')?.value || 'ALL';
        const sortMode = document.getElementById('market-sort-select')?.value || 'score';

        let filtered = allMarketEmitens.filter(it => {
            const matchSearch = !searchQuery || it.ticker.includes(searchQuery) || it.name.toUpperCase().includes(searchQuery);
            const matchSector = selectedSector === 'ALL' || it.sector === selectedSector;
            return matchSearch && matchSector;
        });

        // Sorting
        filtered.sort((a, b) => {
            if (sortMode === 'score') return b.composite_score - a.composite_score;
            if (sortMode === 'upside') return b.upside_pct - a.upside_pct;
            if (sortMode === 'roe') return b.roe - a.roe;
            if (sortMode === 'dividend') return b.dividend_yield - a.dividend_yield;
            if (sortMode === 'pe') return (a.per || 999) - (b.per || 999);
            return 0;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="13" class="p-6 text-center text-slate-500 font-mono">
                        Tidak ada emiten yang sesuai dengan kriteria pencarian.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filtered.map((item, idx) => {
            const gradeClass = ['A+', 'A'].includes(item.grade) ? 'text-brand-400 font-bold' : 'text-amber-400 font-bold';
            const scoreClass = item.composite_score >= 75 ? 'text-brand-400 font-bold' : 'text-slate-200';
            const upsideClass = item.upside_pct >= 0 ? 'text-brand-400 font-bold' : 'text-rose-400';
            const upsideSign = item.upside_pct >= 0 ? '+' : '';

            return `
                <tr class="hover:bg-dark-surface/40 transition">
                    <td class="p-3.5 text-slate-500">${idx + 1}</td>
                    <td class="p-3.5">
                        <div class="flex items-center gap-2">
                            <button onclick="switchSingle('${item.ticker}')" class="font-bold text-brand-300 hover:text-brand-200 hover:underline font-mono text-sm">
                                ${item.ticker}
                            </button>
                            <span class="text-slate-300 truncate max-w-[150px] hidden sm:inline">${item.name}</span>
                        </div>
                    </td>
                    <td class="p-3.5 text-slate-400">${item.sector}</td>
                    <td class="p-3.5 text-right font-mono">Rp ${Number(item.current_price).toLocaleString('id-ID')}</td>
                    <td class="p-3.5 text-right font-mono">${item.per}x</td>
                    <td class="p-3.5 text-right font-mono">${item.pbv}x</td>
                    <td class="p-3.5 text-right font-mono text-brand-400">${item.roe}%</td>
                    <td class="p-3.5 text-right font-mono ${upsideClass}">${upsideSign}${item.upside_pct ? item.upside_pct.toFixed(1) : '0.0'}%</td>
                    <td class="p-3.5 text-center font-mono">${item.piotroski_f_score}/9</td>
                    <td class="p-3.5 text-right font-mono text-amber-400">${item.dividend_yield}%</td>
                    <td class="p-3.5 text-center font-mono ${scoreClass}">${item.composite_score}</td>
                    <td class="p-3.5 text-center ${gradeClass}">${item.grade}</td>
                    <td class="p-3.5 text-center">
                        <button onclick="switchSingle('${item.ticker}')" class="px-2.5 py-1 rounded-lg bg-brand-600/20 hover:bg-brand-600 text-brand-300 hover:text-white border border-brand-500/30 text-xs font-sans transition">
                            Analisis ➔
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    window.switchSingle = function(ticker) {
        if (!ticker) return;
        ticker = ticker.trim().toUpperCase();
        
        const singleTab = document.getElementById('tab-single');
        if (singleTab) {
            singleTab.click();
        }
        
        if (singleInput) {
            singleInput.value = ticker;
        }
        loadSingleEmiten(ticker);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Market filters & Search listeners
    const marketSearch = document.getElementById('market-search-input');
    if (marketSearch) marketSearch.addEventListener('input', renderMarketTable);

    const marketSectorFilter = document.getElementById('market-sector-filter');
    if (marketSectorFilter) marketSectorFilter.addEventListener('change', renderMarketTable);

    const marketSortSelect = document.getElementById('market-sort-select');
    if (marketSortSelect) marketSortSelect.addEventListener('change', renderMarketTable);

    const refreshMarketBtn = document.getElementById('refresh-market-btn');
    if (refreshMarketBtn) refreshMarketBtn.addEventListener('click', () => loadMarketSummary(0));

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

    const screenerFilterBtn = document.getElementById('screener-filter-btn');
    if (screenerFilterBtn) {
        screenerFilterBtn.addEventListener('click', () => {
            const custom = {
                min_roe: parseFloat(document.getElementById('f-min-roe')?.value) || null,
                max_der: parseFloat(document.getElementById('f-max-der')?.value) || null,
                min_piotroski_f: parseInt(document.getElementById('f-min-pio')?.value) || null,
                min_dividend_yield: parseFloat(document.getElementById('f-min-div')?.value) || null,
                max_pe: parseFloat(document.getElementById('f-max-pe')?.value) || null,
                min_composite_score: parseFloat(document.getElementById('f-min-score')?.value) || null
            };
            runScreener('CUSTOM', custom);
        });
    }

    // CSV Export
    const screenerCsvBtn = document.getElementById('screener-export-csv');
    if (screenerCsvBtn) {
        screenerCsvBtn.addEventListener('click', () => {
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
    }

    // -------------------------------------------------------------
    // Initial load: Load Market Overview by default & prepare BBRI
    // -------------------------------------------------------------
    loadMarketSummary();
    loadSingleEmiten('BBRI', null, false, true);
});
