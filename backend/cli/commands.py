"""
CLI Command Line Interface for IDX Emiten KeyStats & Scoring Engine.
Usage:
    python -m cli.commands calc BBRI
    python -m cli.commands compare BBCA BBRI BMRI
    python -m cli.commands screen --preset BUFFETT_MOAT
    python -m cli.commands list
"""

import typer
from typing import List, Optional
from app.services.emiten_service import EmitenService
from app.services.comparison_service import ComparisonService
from app.services.screener_service import ScreenerService
from app.models.screener import ScreenerCriteria, ScreenerPreset
from cli.terminal_app import TerminalRenderer, console

app = typer.Typer(help="IDX Emiten Fundamental KeyStats & Scoring Engine CLI")

# Initialize services
emiten_service = EmitenService()
comparison_service = ComparisonService(emiten_service)
screener_service = ScreenerService(emiten_service)


@app.command(name="calc")
def calc(
    ticker: str = typer.Argument(..., help="IDX Stock Ticker (e.g. BBRI, BBCA, ASII, ADRO)"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Simulate with custom/override market price (IDR)"),
    live: bool = typer.Option(True, "--live/--cached", help="Fetch live realtime quote from IDX/Yahoo Finance")
):
    """Deep-dive fundamental analysis & valuation with live real-time price or simulation."""
    status_msg = f"[bold cyan]Fetching Realtime KeyStats for {ticker.upper()}..." if not price else f"[bold cyan]Simulating KeyStats for {ticker.upper()} at Rp{price:,.0f}..."
    with console.status(status_msg):
        report = emiten_service.analyze_single_emiten(ticker, override_price=price, force_live=live)
        
    if not report:
        console.print(f"[bold red]❌ Error: Emiten '{ticker.upper()}' tidak ditemukan atau data tidak tersedia.[/bold red]")
        raise typer.Exit(code=1)
        
    TerminalRenderer.render_single_emiten(report)


@app.command(name="compare")
def compare(
    tickers: List[str] = typer.Argument(..., help="List of stock tickers to compare (e.g. BBCA BBRI BMRI BBNI)")
):
    """Side-by-side peer comparison and benchmark analysis for multiple emitens."""
    with console.status(f"[bold cyan]Comparing {len(tickers)} emitens..."):
        resp = comparison_service.compare_emitens(tickers)
        
    if not resp.items:
        console.print("[bold red]❌ Error: Tidak ada emiten valid yang dapat dibandingkan.[/bold red]")
        raise typer.Exit(code=1)
        
    TerminalRenderer.render_comparison(resp)


@app.command(name="screen")
def screen(
    preset: Optional[str] = typer.Option(None, help="Preset: BUFFETT_MOAT, DIVIDEND_CASH_COW, GARP, DEEP_VALUE, MOMENTUM_QUALITY"),
    min_roe: Optional[float] = typer.Option(None, help="Minimum ROE %"),
    max_der: Optional[float] = typer.Option(None, help="Maximum DER ratio"),
    min_piotroski: Optional[int] = typer.Option(None, help="Minimum Piotroski F-Score (0-9)"),
    min_div_yield: Optional[float] = typer.Option(None, help="Minimum Dividend Yield %"),
    min_score: Optional[float] = typer.Option(None, help="Minimum Composite Score (0-100)")
):
    """Run quantitative fundamental screening with filters or presets."""
    preset_enum = None
    if preset:
        try:
            preset_enum = ScreenerPreset[preset.upper()]
        except KeyError:
            console.print(f"[bold red]❌ Unknown preset '{preset}'. Available: {[p.name for p in ScreenerPreset]}[/bold red]")
            raise typer.Exit(code=1)
            
    criteria = ScreenerCriteria(
        preset=preset_enum,
        min_roe=min_roe,
        max_der=max_der,
        min_piotroski_f=min_piotroski,
        min_dividend_yield=min_div_yield,
        min_composite_score=min_score
    )
    
    with console.status("[bold cyan]Running Multi-Factor Screener..."):
        resp = screener_service.run_screener(criteria)
        
    TerminalRenderer.render_screener(resp)


@app.command(name="list")
def list_emitens():
    """List all supported/cached IDX emitens."""
    tickers = emiten_service.list_all_available_tickers()
    console.print(f"[bold green]Daftar Emiten Terdaftar ({len(tickers)} Emitens):[/bold green]")
    for t in tickers:
        console.print(f"  • [bold cyan]{t}[/bold cyan]")


if __name__ == "__main__":
    app()
