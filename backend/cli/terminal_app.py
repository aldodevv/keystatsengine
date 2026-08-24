"""
Terminal Rich Renderer for Emiten KeyStats, Radar Charts, Comparison Matrix, and Screener.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich import box
from app.models.score import EmitenAnalysisReport, VerdictAction, HealthZone
from app.models.screener import ComparisonResponse, ScreenerResponse


console = Console()


class TerminalRenderer:
    @staticmethod
    def render_single_emiten(report: EmitenAnalysisReport):
        # Grade & Verdict Colors
        grade_color = "bold green" if report.grade in ["A+", "A"] else ("bold yellow" if report.grade == "B" else "bold red")
        verdict_color = "bold black on green" if report.verdict == VerdictAction.STRONG_BUY else (
            "bold black on bright_green" if report.verdict == VerdictAction.BUY else (
                "bold black on yellow" if report.verdict == VerdictAction.HOLD else "bold white on red"
            )
        )
        
        # Header Panel
        header_text = Text()
        header_text.append(f" {report.ticker} ", style="bold white on blue")
        header_text.append(f"  {report.name}  |  Sector: {report.sector}  |  Industry: {report.industry}\n", style="dim")
        
        # Realtime price with change %
        price_change_style = "bold green" if (report.price_change_pct or 0) >= 0 else "bold red"
        change_sign = "+" if (report.price_change_pct or 0) > 0 else ""
        header_text.append(f"Realtime Price: Rp{report.current_price:,.0f} ", style="bold white")
        header_text.append(f"({change_sign}{report.price_change_pct:.2f}%) ", style=price_change_style)
        if report.previous_close:
            header_text.append(f"Prev Close: Rp{report.previous_close:,.0f}  ", style="dim")
        header_text.append(f"Market Cap: Rp{report.market_cap / 1e12:,.1f} Triliun\n")
        header_text.append(f"Fundamental Score: {report.composite_score}/100  Grade: ", style="bold")
        header_text.append(f"[{report.grade}] ", style=grade_color)
        header_text.append(f"  Action Verdict: ", style="bold")
        header_text.append(f" {report.verdict.value} ", style=verdict_color)
        
        console.print(Panel(header_text, title="[bold cyan]🏛️ IDX EMITEN KEYSTATS & VALUATION REPORT (REALTIME ACTIVE)[/bold cyan]", border_style="cyan", box=box.ROUNDED))

        # 4 Core KPI Tables
        # Table 1: Valuation
        val_table = Table(title="[bold yellow]💰 Valuation & Fair Value[/bold yellow]", box=box.SIMPLE)
        val_table.add_column("Metric", style="bold")
        val_table.add_column("Value", justify="right")
        val_table.add_row("P/E Ratio (PER)", f"{report.valuation.per}x")
        val_table.add_row("P/B Ratio (PBV)", f"{report.valuation.pbv}x")
        val_table.add_row("EV / EBITDA", f"{report.valuation.ev_ebitda}x")
        if report.valuation.peg_ratio:
            val_table.add_row("PEG Ratio", f"{report.valuation.peg_ratio}x")
        if report.valuation.graham_number:
            val_table.add_row("Graham Number", f"Rp{report.valuation.graham_number:,.0f}")
        if report.valuation.dcf_fair_value:
            val_table.add_row("DCF Fair Value", f"Rp{report.valuation.dcf_fair_value:,.0f}")
        val_table.add_row("Avg Fair Value", f"[bold cyan]Rp{report.valuation.average_fair_value:,.0f}[/bold cyan]")
        
        upside_style = "bold green" if report.valuation.upside_downside_pct > 0 else "bold red"
        val_table.add_row("Upside/Downside", f"[{upside_style}]{report.valuation.upside_downside_pct:+.1f}%[/{upside_style}]")

        # Table 2: Profitability
        prof_table = Table(title="[bold green]📈 Profitability & DuPont[/bold green]", box=box.SIMPLE)
        prof_table.add_column("Metric", style="bold")
        prof_table.add_column("Value", justify="right")
        prof_table.add_row("Return on Equity (ROE)", f"[bold]{report.profitability.roe}%[/bold]")
        prof_table.add_row("Return on Assets (ROA)", f"{report.profitability.roa}%")
        prof_table.add_row("ROIC", f"{report.profitability.roic}%")
        prof_table.add_row("Gross Profit Margin", f"{report.profitability.gpm}%")
        prof_table.add_row("Operating Margin", f"{report.profitability.opm}%")
        prof_table.add_row("Net Profit Margin", f"[bold]{report.profitability.npm}%[/bold]")
        prof_table.add_row("DuPont Net Margin", f"{report.profitability.dupont_net_margin * 100:.1f}%")
        prof_table.add_row("DuPont Asset Turnover", f"{report.profitability.dupont_asset_turnover:.2f}x")
        prof_table.add_row("DuPont Equity Mult.", f"{report.profitability.dupont_equity_multiplier:.2f}x")

        # Table 3: Financial Health & Solvency
        health_table = Table(title="[bold blue]🛡️ Financial Health & Solvency[/bold blue]", box=box.SIMPLE)
        health_table.add_column("Metric", style="bold")
        health_table.add_column("Value", justify="right")
        health_table.add_row("Debt to Equity (DER)", f"{report.solvency.der}x")
        health_table.add_row("Net Debt / Equity", f"{report.solvency.net_debt_to_equity}x")
        
        z_style = "bold green" if report.solvency.altman_zone == HealthZone.SAFE else ("bold yellow" if report.solvency.altman_zone == HealthZone.GREY else "bold red")
        health_table.add_row("Altman Z-Score", f"[{z_style}]{report.solvency.altman_z_score} ({report.solvency.altman_zone.value})[/{z_style}]")
        
        f_style = "bold green" if report.quality.piotroski_f_score >= 7 else ("bold yellow" if report.quality.piotroski_f_score >= 5 else "bold red")
        health_table.add_row("Piotroski F-Score", f"[{f_style}]{report.quality.piotroski_f_score}/9[/{f_style}]")
        health_table.add_row("Current Ratio", f"{report.liquidity.current_ratio}x")
        health_table.add_row("CFO to Net Income", f"{report.quality.cfo_to_net_income}x")

        # Table 4: Cash Flow & Dividend
        cf_table = Table(title="[bold magenta]💵 Cash Flow & Dividends[/bold magenta]", box=box.SIMPLE)
        cf_table.add_column("Metric", style="bold")
        cf_table.add_column("Value", justify="right")
        cf_table.add_row("Free Cash Flow (FCF)", f"Rp{report.cash_flow_dividend.fcf / 1e12:,.1f} T")
        cf_table.add_row("FCF Yield", f"{report.cash_flow_dividend.fcf_yield}%")
        cf_table.add_row("Dividend Yield", f"[bold magenta]{report.cash_flow_dividend.dividend_yield}%[/bold magenta]")
        cf_table.add_row("Dividend Payout (DPR)", f"{report.cash_flow_dividend.dpr}%")
        if report.cash_flow_dividend.cash_dividend_coverage:
            cf_table.add_row("Cash Div Coverage", f"{report.cash_flow_dividend.cash_dividend_coverage}x")
        cf_table.add_row("Revenue Growth YoY", f"{report.growth.revenue_growth_yoy:+0.1f}%")
        cf_table.add_row("EPS Growth YoY", f"{report.growth.eps_growth_yoy:+0.1f}%")

        console.print(Columns([val_table, prof_table, health_table, cf_table], equal=True))

        # Banking metrics if available
        if report.bank_metrics:
            bm = report.bank_metrics
            bank_table = Table(title="[bold magenta]🏦 Banking Regulatory Metrics (OJK / BI Standards)[/bold magenta]", box=box.SIMPLE)
            bank_table.add_column("CAR (Capital Adequacy)", justify="center")
            bank_table.add_column("NPL Gross", justify="center")
            bank_table.add_column("NPL Net", justify="center")
            bank_table.add_column("NIM (Net Margin)", justify="center")
            bank_table.add_column("BOPO (Efficiency)", justify="center")
            bank_table.add_column("CASA Ratio", justify="center")
            bank_table.add_column("LDR (Liquidity)", justify="center")
            bank_table.add_row(
                f"{bm.get('car')}%",
                f"{bm.get('npl_gross')}%",
                f"{bm.get('npl_net')}%",
                f"{bm.get('nim')}%",
                f"{bm.get('bopo')}%",
                f"{bm.get('casa')}%",
                f"{bm.get('ldr')}%"
            )
            console.print(Panel(bank_table, border_style="magenta", box=box.ROUNDED))

        # 5-Axis Radar Score Visualization
        radar_panel = Table(title="[bold cyan]📊 5-Pillars Fundamental Health Scorecard[/bold cyan]", box=box.MINIMAL_DOUBLE_HEAD)
        radar_panel.add_column("Pillar", style="bold", width=22)
        radar_panel.add_column("Score (0-100)", justify="right", width=14)
        radar_panel.add_column("Visual Bar", width=35)
        
        pillars = [
            ("Valuation Attractiveness", report.radar.valuation, "yellow"),
            ("Profitability Power", report.radar.profitability, "green"),
            ("Financial Health & Solvency", report.radar.financial_health, "blue"),
            ("Growth Momentum", report.radar.growth, "magenta"),
            ("Cash Flow & Quality", report.radar.cash_flow_quality, "cyan")
        ]
        
        for name, score, col in pillars:
            bar_len = int(score / 100 * 25)
            bar_str = f"[{col}]{'█' * bar_len}{'░' * (25 - bar_len)}[/{col}]"
            radar_panel.add_row(name, f"[{col}]{score}/100[/{col}]", bar_str)
            
        console.print(Panel(radar_panel, border_style="cyan"))

        # Price Sensitivity Simulation Table (for Daily Traders)
        if report.price_sensitivity_scenarios:
            sens_table = Table(title="[bold yellow]🎯 Real-Time Price Sensitivity Matrix (Entry / Exit Simulation)[/bold yellow]", box=box.ROUNDED)
            sens_table.add_column("Price Shift", justify="center")
            sens_table.add_column("Simulated Price", justify="right")
            sens_table.add_column("PER (x)", justify="right")
            sens_table.add_column("PBV (x)", justify="right")
            sens_table.add_column("Div Yield", justify="right")
            sens_table.add_column("Upside %", justify="right")
            sens_table.add_column("Score", justify="center")
            sens_table.add_column("Verdict", justify="center")
            
            for sc in report.price_sensitivity_scenarios:
                is_current = sc.price_change_pct == 0.0
                row_style = "bold white on blue" if is_current else ""
                shift_str = "CURRENT PRICE" if is_current else f"{sc.price_change_pct:+.0f}%"
                
                sens_table.add_row(
                    f"[{row_style}]{shift_str}[/{row_style}]" if is_current else shift_str,
                    f"Rp{sc.simulated_price:,.0f}",
                    f"{sc.per}x",
                    f"{sc.pbv}x",
                    f"{sc.dividend_yield}%",
                    f"{sc.upside_pct:+.1f}%",
                    f"{sc.composite_score}/100",
                    f"{sc.verdict}",
                    style="bold" if is_current else ""
                )
            console.print(Panel(sens_table, border_style="yellow"))

        # Insights Panel (Bull vs Bear & Green/Red Flags)
        flags_text = Text()
        if report.bull_cases:
            flags_text.append("\n🐂 Bull Case / Keunggulan Fundamental:\n", style="bold green")
            for b in report.bull_cases:
                flags_text.append(f"  ✓ {b}\n", style="green")
        if report.bear_cases:
            flags_text.append("\n🐻 Bear Case / Risiko Fundamental:\n", style="bold red")
            for br in report.bear_cases:
                flags_text.append(f"  ⚠ {br}\n", style="red")
        if report.red_flags:
            flags_text.append("\n🚩 Red Flags:\n", style="bold magenta")
            for rf in report.red_flags:
                flags_text.append(f"  • {rf}\n", style="magenta")
                
        console.print(Panel(flags_text, title="[bold]🧠 AI / Algorithmic Fundamental Synthesis[/bold]", border_style="dim", box=box.ROUNDED))

    @staticmethod
    def render_comparison(resp: ComparisonResponse):
        table = Table(title="[bold cyan]⚖️ IDX EMITEN PEER COMPARISON MATRIX[/bold cyan]", box=box.DOUBLE_EDGE)
        table.add_column("Ticker", style="bold white on blue", justify="center")
        table.add_column("Price (IDR)", justify="right")
        table.add_column("PER (x)", justify="right")
        table.add_column("PBV (x)", justify="right")
        table.add_column("ROE (%)", justify="right")
        table.add_column("DER (x)", justify="right")
        table.add_column("Piotroski", justify="center")
        table.add_column("Altman Z", justify="right")
        table.add_column("Div Yield", justify="right")
        table.add_column("Upside %", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Grade", justify="center")
        table.add_column("Verdict", justify="center")
        
        for item in resp.items:
            # Highlight champions
            pe_style = "bold green" if resp.best_in_class.get("cheapest_pe") == item.ticker else ""
            pbv_style = "bold green" if resp.best_in_class.get("cheapest_pbv") == item.ticker else ""
            roe_style = "bold green" if resp.best_in_class.get("highest_roe") == item.ticker else ""
            div_style = "bold green" if resp.best_in_class.get("highest_dividend_yield") == item.ticker else ""
            pio_style = "bold green" if resp.best_in_class.get("highest_piotroski_f") == item.ticker else ""
            z_style = "bold green" if resp.best_in_class.get("safest_altman_z") == item.ticker else ""
            
            score_style = "bold white on green" if resp.best_in_class.get("overall_champion") == item.ticker else "bold"
            grade_style = "bold green" if item.grade in ["A+", "A"] else ("bold yellow" if item.grade == "B" else "bold red")
            
            table.add_row(
                item.ticker,
                f"Rp{item.current_price:,.0f}",
                f"[{pe_style}]{item.per}x[/{pe_style}]" if pe_style else f"{item.per}x",
                f"[{pbv_style}]{item.pbv}x[/{pbv_style}]" if pbv_style else f"{item.pbv}x",
                f"[{roe_style}]{item.roe}%[/{roe_style}]" if roe_style else f"{item.roe}%",
                f"{item.der}x",
                f"[{pio_style}]{item.piotroski_f_score}/9[/{pio_style}]" if pio_style else f"{item.piotroski_f_score}/9",
                f"[{z_style}]{item.altman_z_score}[/{z_style}]" if z_style else f"{item.altman_z_score}",
                f"[{div_style}]{item.dividend_yield}%[/{div_style}]" if div_style else f"{item.dividend_yield}%",
                f"{item.upside_pct:+.1f}%",
                f"[{score_style}] {item.composite_score} [/{score_style}]",
                f"[{grade_style}]{item.grade}[/{grade_style}]",
                item.verdict
            )
            
        console.print(table)
        
        # Best in class legend
        champ_text = Text()
        champ_text.append("\n🏆 Best-in-Class Winners:\n", style="bold yellow")
        for metric, ticker in resp.best_in_class.items():
            champ_text.append(f"  • {metric.replace('_', ' ').title()}: ", style="bold")
            champ_text.append(f"{ticker}\n", style="bold cyan")
        console.print(Panel(champ_text, border_style="yellow", box=box.ROUNDED))

    @staticmethod
    def render_screener(resp: ScreenerResponse):
        title = f"[bold cyan]🔍 IDX SCREENER RESULTS (Found: {resp.total_matched} Emitens)[/bold cyan]"
        if resp.applied_preset:
            title += f" [yellow]Preset: {resp.applied_preset}[/yellow]"
            
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("#", justify="center")
        table.add_column("Ticker", style="bold white on blue", justify="center")
        table.add_column("Company Name", style="dim")
        table.add_column("Sector")
        table.add_column("Price (IDR)", justify="right")
        table.add_column("PER", justify="right")
        table.add_column("PBV", justify="right")
        table.add_column("ROE", justify="right")
        table.add_column("DER", justify="right")
        table.add_column("Piotroski", justify="center")
        table.add_column("Altman Z", justify="right")
        table.add_column("Div Yield", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Grade", justify="center")
        table.add_column("Verdict", justify="center")
        
        for idx, item in enumerate(resp.results, start=1):
            grade_style = "bold green" if item.grade in ["A+", "A"] else ("bold yellow" if item.grade == "B" else "bold red")
            score_style = "bold green" if item.composite_score >= 75 else ("bold yellow" if item.composite_score >= 60 else "bold red")
            
            table.add_row(
                str(idx),
                item.ticker,
                item.name[:25],
                item.sector[:18],
                f"Rp{item.current_price:,.0f}",
                f"{item.per}x",
                f"{item.pbv}x",
                f"{item.roe}%",
                f"{item.der}x",
                f"{item.piotroski_f_score}/9",
                f"{item.altman_z_score}",
                f"{item.dividend_yield}%",
                f"[{score_style}]{item.composite_score}[/{score_style}]",
                f"[{grade_style}]{item.grade}[/{grade_style}]",
                item.verdict
            )
            
        console.print(table)
