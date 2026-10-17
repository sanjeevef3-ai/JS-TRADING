"""
Interactive CLI for Indian Stock Market MiroFish AI Engine
Delivers real-time analysis, pattern detection, MTF confluence, and swarm consensus in the terminal.
"""

import sys
import argparse
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns

from engine import IndianMarketAIEngine
from learning import SelfRefineEngine

console = Console()

def run_cli_analysis(symbol_query: str, style: str = "Intraday Swing", risk: str = "Moderate"):
    console.print(Panel(
        f"[bold cyan]🇮🇳 Indian Stock Market AI Engine | MiroFish Swarm Core[/bold cyan]\n"
        f"[green]Analyzing live market data, multi-timeframe confluence, and chart patterns...[/green]",
        border_style="cyan"
    ))

    with console.status(f"[bold yellow]Ingesting live feed for '{symbol_query}' & running MiroFish Swarm...[/bold yellow]", spinner="dots"):
        engine = IndianMarketAIEngine()
        res = engine.analyze_symbol(
            query=symbol_query,
            trading_style=style,
            risk_tolerance=risk
        )

    sym = res["symbol"]
    ticker = res["ticker"]
    quote = res["live_quote"]
    cur_p = quote.get("current_price", 0.0)
    chg = quote.get("change", 0.0)
    p_chg = quote.get("p_change", 0.0)
    color = "green" if chg >= 0 else "red"
    sign = "+" if chg >= 0 else ""

    # 1. LIVE QUOTE PANEL
    quote_text = (
        f"[bold white]{sym}[/bold white] ({ticker})\n"
        f"LTP: [bold {color}]₹{cur_p}[/bold {color}]  [bold {color}]{sign}{chg} ({sign}{p_chg}%)[/bold {color}]\n"
        f"Day Range: ₹{quote.get('low', '-')} - ₹{quote.get('high', '-')} | Volume: {quote.get('volume', 0):,}\n"
        f"52W High: ₹{quote.get('52w_high', '-')} | 52W Low: ₹{quote.get('52w_low', '-')}"
    )
    console.print(Panel(quote_text, title="[bold]📊 Live Market Snapshot[/bold]", border_style=color))

    # 2. MULTI-TIMEFRAME CONFLUENCE TABLE
    conf = res["confluence"]
    table_mtf = Table(title="⏱️ Multi-Timeframe Confluence Matrix (5m, 15m, 1h, 1D)", border_style="blue")
    table_mtf.add_column("Timeframe", justify="center", style="bold")
    table_mtf.add_column("Direction", justify="center")
    table_mtf.add_column("Score", justify="center")
    table_mtf.add_column("RSI (14)", justify="center")
    table_mtf.add_column("EMA 20", justify="center")
    table_mtf.add_column("Supertrend", justify="center")

    for tf, data in conf.get("timeframe_breakdown", {}).items():
        b = data.get("bias", "Neutral")
        b_style = "green" if "Bullish" in b else ("red" if "Bearish" in b else "yellow")
        table_mtf.add_row(
            tf.upper(),
            f"[{b_style}]{b}[/{b_style}]",
            str(data.get("score", 0)),
            str(data.get("rsi", "-")),
            f"₹{data.get('ema20', '-')}",
            str(data.get("supertrend", "-"))
        )
    console.print(table_mtf)
    console.print(f"[bold blue]MTF Confluence State:[/bold blue] {conf.get('confluence_state')}")
    console.print(f"[bold blue]Recommended Action:[/bold blue] {conf.get('action_recommendation')}\n")

    # 3. DETECTED PATTERNS RADAR TABLE
    patterns = res["patterns"]
    pat_list = patterns.get("all_detected_patterns", [])
    table_pat = Table(title=f"📐 Detected Patterns Radar ({len(pat_list)} patterns found)", border_style="magenta")
    table_pat.add_column("Timeframe", justify="center")
    table_pat.add_column("Pattern Name", style="bold")
    table_pat.add_column("Type")
    table_pat.add_column("Bias", justify="center")
    table_pat.add_column("Confidence", justify="center")
    table_pat.add_column("Description")

    for p in pat_list[:8]: # Show top 8 prominent patterns
        pb = p.get("bias", "Neutral")
        pb_style = "green" if "Bullish" in pb else ("red" if "Bearish" in pb else "yellow")
        conf_val = p.get("calibrated_confidence", p.get("confidence", 70))
        table_pat.add_row(
            p.get("timeframe", "-").upper(),
            p.get("pattern", "Unknown"),
            p.get("type", "Chart"),
            f"[{pb_style}]{pb}[/{pb_style}]",
            f"{conf_val}%",
            p.get("desc", "-")[:65] + "..." if len(p.get("desc", "")) > 65 else p.get("desc", "-")
        )
    console.print(table_pat)

    # 4. MIROFISH SWARM TRANSCRIPT
    swarm = res["swarm_simulation"]
    console.print(Panel(
        "\n".join([
            f"[bold cyan]{entry.get('speaker', '')}[/bold cyan]: {entry.get('comment', '')}"
            for round_data in swarm.get("debate_transcript", [])
            for entry in round_data.get("entries", [])
            if "speaker" in entry
        ]),
        title="[bold yellow]🧠 MiroFish Swarm Deliberation & Cross-Examination[/bold yellow]",
        border_style="yellow"
    ))

    # 5. FINAL TRADE PLAN & CONSENSUS
    consensus = res["consensus"]
    tp = consensus.get("trade_plan", {})
    probs = consensus.get("probability_matrix", {})
    cdir = consensus.get("direction", "NEUTRAL")
    cdir_style = "bold green" if "BULLISH" in cdir else ("bold red" if "BEARISH" in cdir else "bold yellow")

    plan_text = (
        f"[bold]Consensus Verdict:[/bold] [{cdir_style}]{cdir}[/{cdir_style}] ({probs.get('bullish_pct')}% Bull / {probs.get('bearish_pct')}% Bear)\n"
        f"[bold]Trade Action:[/bold] [bold cyan]{consensus.get('recommended_action')}[/bold cyan]\n"
        f"--------------------------------------------------\n"
        f"🎯 [bold green]Recommended Entry Zone:[/bold green] {tp.get('entry_zone')}\n"
        f"🛑 [bold red]Strict Stop-Loss (Invalidation):[/bold red] ₹{tp.get('stop_loss')}\n"
        f"🚀 [bold cyan]Target 1 (Conservative):[/bold cyan] ₹{tp.get('target_1')}\n"
        f"🚀 [bold cyan]Target 2 (Extended):[/bold cyan] ₹{tp.get('target_2')}\n"
        f"🚀 [bold cyan]Target 3 (Runner):[/bold cyan] ₹{tp.get('target_3')}\n"
        f"⚖️ [bold]Risk-to-Reward Ratio:[/bold] {tp.get('risk_reward_ratio')}\n"
        f"⚠️ [bold yellow]Invalidation Criterion:[/bold yellow] {tp.get('invalidation_criteria')}\n"
        f"--------------------------------------------------\n"
        f"[italic]{consensus.get('executive_summary')}[/italic]"
    )
    console.print(Panel(plan_text, title="[bold green]🏆 Actionable Trade Plan & Execution Matrix[/bold green]", border_style="green"))

    console.print(f"[dim]Execution: {res['execution_metadata']['elapsed_seconds']}s | Loop Shield: {res['execution_metadata']['loop_guard_status']} | 0 Infinite Loops Guaranteed[/dim]\n")

def main():
    parser = argparse.ArgumentParser(description="Indian Stock Market MiroFish AI Engine CLI")
    parser.add_argument("--symbol", "-s", type=str, default=None, help="Stock symbol or index (e.g. NIFTY, BANKNIFTY, RELIANCE, TCS)")
    parser.add_argument("--style", type=str, default="Intraday Swing", choices=["Intraday Scalp", "Intraday Swing", "Positional Delivery"], help="Trading style")
    parser.add_argument("--risk", type=str, default="Moderate", choices=["Conservative", "Moderate", "Aggressive"], help="Risk profile")
    parser.add_argument("--refine", action="store_true", help="Run self-refine code & system health check")

    args = parser.parse_args()

    if args.refine:
        console.print("[bold yellow]Running Self-Developing Code & Health Refinement...[/bold yellow]")
        refiner = SelfRefineEngine()
        report = refiner.run_full_self_refinement()
        console.print(report)
        return

    sym = args.symbol
    if not sym:
        sym = console.input("[bold cyan]Enter Indian Stock or Index (e.g., NIFTY, BANKNIFTY, RELIANCE, TCS, INFY): [/bold cyan]").strip()
        if not sym:
            sym = "NIFTY"

    run_cli_analysis(sym, args.style, args.risk)

if __name__ == "__main__":
    main()
