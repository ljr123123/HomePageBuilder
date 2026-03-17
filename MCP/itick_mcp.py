from typing import Any, Literal

import json
import os
import sys
import time
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP


# region agent log helper
DEBUG_LOG_PATH = "debug-978671.log"
DEBUG_SESSION_ID = "978671"


def _agent_log(
    *,
    run_id: str,
    hypothesis_id: str,
    location: str,
    message: str,
    data: dict[str, Any],
) -> None:
    """Debug-mode structured logging helper (NDJSON, single-line writes)."""
    try:
        payload: dict[str, Any] = {
            "sessionId": DEBUG_SESSION_ID,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # 避免调试日志影响正常业务逻辑
        pass


# endregion agent log helper


# region agent log: cloud-friendly import bootstrap
def _bootstrap_sys_path() -> None:
    """
    Ensure repo root is on sys.path / PYTHONPATH.
    Cloud runners may start this file with cwd != repo root, which breaks
    imports like `modules.*`.
    """

    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)

    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    current = os.environ.get("PYTHONPATH", "")
    if repo_root_str not in current.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            repo_root_str if not current else current + os.pathsep + repo_root_str
        )

    _agent_log(
        run_id="cloud",
        hypothesis_id="H-path",
        location="MCP/itick_mcp.py:_bootstrap_sys_path",
        message="bootstrapped sys.path for repo root",
        data={
            "repo_root": repo_root_str,
            "cwd": os.getcwd(),
            "sys_path_head": sys.path[:5],
        },
    )


_bootstrap_sys_path()
# endregion agent log: cloud-friendly import bootstrap


# IMPORTANT: import after bootstrap
from modules.itick_api import MarketType, Region, get_market_list, headers  # noqa: E402


app = FastMCP("itick-api")


@app.tool()
def mcp_get_market_list(
    region: Region,
    financial_type: MarketType,
    code: str,
) -> dict[str, Any]:
    """
    通过 iTick 接口获取标的基础信息。

    参数
    ----
    region: 市场代码，例如 "HK" / "SZ" / "SH" / "US" / "SG" / "JP"
    financial_type: 金融类型，例如 "stock" / "forex" / "indices" / "crypto" / "future" / "fund"
    code: 代码或模糊检索关键词

    返回
    ----
    {
        "code": str,
        "name": str,
        "market_type": str,
        "exchange": str,
        "symbol": str,
    }
    """

    return get_market_list(region=region, financial_type=financial_type, code=code)


@app.tool()
def mcp_get_kline(
    region: Region,
    code: str,
    k_type: Literal[1, 5, 15, 30, 60, 101, 102, 103, 201, 202, 203],
    limit: int | None = None,
) -> dict[str, Any]:
    """
    获取 K 线数据，对应 REST 接口 /stock/kline。

    参数
    ----
    region: 市场代码，例如 "HK" / "SZ" / "SH" / "US" / "SG" / "JP"
    code: 证券代码，例如 "700.HK"
    k_type: K 线周期，1/5/15/30/60 分钟，101/102/103 日/周/月，201/202/203 季度/半年/年度
    """

    url = "https://api.itick.org/stock/kline"
    params: dict[str, Any] = {
        "region": region.lower(),
        "code": code,
        "kType": k_type,
    }
    if limit is not None:
        params["limit"] = limit
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@app.tool()
def mcp_analyze_kline_basic(
    region: Region,
    code: str,
    k_type: Literal[1, 5, 15, 30, 60, 101, 102, 103, 201, 202, 203],
    limit: int = 200,
) -> dict[str, Any]:
    """
    对 K 线数据做基础统计分析（基于收盘价）。

    分析内容包括：
    - 样本数量、起止时间
    - 收盘价的最新值、均值、最小值、最大值
    - 总体涨跌幅、最大回撤

    参数
    ----
    region: 市场代码，例如 "HK" / "SZ" / "SH" / "US" / "SG" / "JP"
    code: 证券代码，例如 "700.HK"
    k_type: K 线周期，同 mcp_get_kline
    limit: 取最近多少根 K 线做分析
    """

    # 先尝试从本地测试数据加载（方便在没有 iTick 环境时开发/调试）
    local_data: list[dict[str, Any]] | None = None

    # data 目录位于项目根目录下
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    # 针对常用标的预置本地文件名
    local_filename = None
    if region == "US" and code == "AAPL" and k_type == 101:
        local_filename = "kline_US_AAPL_101.json"
    elif region == "HK" and code == "700.HK" and k_type == 101:
        local_filename = "kline_HK_700.HK_101.json"

    if local_filename is not None:
        local_path = data_dir / local_filename
        if local_path.exists():
            try:
                payload = json.loads(local_path.read_text(encoding="utf-8"))
                local_data = payload.get("data") or []
                _agent_log(
                    run_id="local-fixture",
                    hypothesis_id="H-local",
                    location="MCP/itick_mcp.py:mcp_analyze_kline_basic:local_fixture",
                    message="loaded local kline fixture",
                    data={
                        "region": region,
                        "code": code,
                        "k_type": k_type,
                        "limit": limit,
                        "file": str(local_path),
                        "data_len": len(local_data),
                    },
                )
            except Exception as exc:
                _agent_log(
                    run_id="local-fixture",
                    hypothesis_id="H-local-error",
                    location="MCP/itick_mcp.py:mcp_analyze_kline_basic:local_fixture_error",
                    message="failed to load local kline fixture",
                    data={
                        "region": region,
                        "code": code,
                        "k_type": k_type,
                        "limit": limit,
                        "file": str(local_path),
                        "error": repr(exc),
                    },
                )

    if local_data is not None:
        data = local_data
        payload = {"code": 0, "msg": "using local test data"}
    else:
        url = "https://api.itick.org/stock/kline"
        params: dict[str, Any] = {
            "region": region.lower(),
            "code": code,
            "kType": k_type,
            "limit": limit,
        }

        # region agent log: function entry (H1-H3)
        _agent_log(
            run_id="initial",
            hypothesis_id="H1-H3",
            location="MCP/itick_mcp.py:mcp_analyze_kline_basic:request",
            message="mcp_analyze_kline_basic request params",
            data={
                "region": region,
                "code": code,
                "k_type": k_type,
                "limit": limit,
                "url": url,
                "params": params,
            },
        )
        # endregion agent log

        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()

        data = payload.get("data") or []

        # region agent log: response summary (H1-H4)
        _agent_log(
            run_id="initial",
            hypothesis_id="H1-H4",
            location="MCP/itick_mcp.py:mcp_analyze_kline_basic:response",
            message="mcp_analyze_kline_basic raw response summary",
            data={
                "payload_type": type(payload).__name__,
                "payload_keys": list(payload.keys())
                if isinstance(payload, dict)
                else None,
                "data_type": type(data).__name__,
                "data_len": len(data) if hasattr(data, "__len__") else None,
                "api_code": payload.get("code") if isinstance(payload, dict) else None,
                "api_msg": payload.get("msg") if isinstance(payload, dict) else None,
            },
        )
        # endregion agent log

        if not data:
            # region agent log: early return (H2/H4)
            _agent_log(
                run_id="initial",
                hypothesis_id="H2-H4",
                location="MCP/itick_mcp.py:mcp_analyze_kline_basic:no_data",
                message="no kline data returned from iTick, early exit",
                data={
                    "region": region,
                    "code": code,
                    "k_type": k_type,
                    "limit": limit,
                },
            )
            # endregion agent log

            return {
                "region": region,
                "code": code,
                "k_type": k_type,
                "limit": limit,
                "sample_size": 0,
                "message": "no kline data returned from iTick",
            }

    # 按时间排序，确保从旧到新
    data = sorted(data, key=lambda x: x.get("t", 0))

    closes: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    times: list[int] = []

    for bar in data:
        try:
            closes.append(float(bar["c"]))
            highs.append(float(bar["h"]))
            lows.append(float(bar["l"]))
            times.append(int(bar["t"]))
        except (KeyError, TypeError, ValueError):
            # 跳过异常数据点
            continue

    sample_size = len(closes)
    if sample_size == 0:
        return {
            "region": region,
            "code": code,
            "k_type": k_type,
            "limit": limit,
            "sample_size": 0,
            "message": "kline data has no valid OHLC fields",
        }

    import math

    last_close = closes[-1]
    mean_close = sum(closes) / sample_size
    min_close = min(closes)
    max_close = max(closes)

    # 简单波动率（基于收盘价对数收益）
    log_returns: list[float] = []
    for i in range(1, sample_size):
        if closes[i - 1] > 0 and closes[i] > 0:
            log_returns.append(math.log(closes[i] / closes[i - 1]))

    if log_returns:
        mean_ret = sum(log_returns) / len(log_returns)
        var_ret = (
            sum((r - mean_ret) ** 2 for r in log_returns) / (len(log_returns) - 1)
            if len(log_returns) > 1
            else 0.0
        )
        vol = math.sqrt(var_ret)
    else:
        vol = 0.0

    # 最大回撤（基于收盘价）
    max_drawdown = 0.0
    peak = closes[0]
    for price in closes[1:]:
        if price > peak:
            peak = price
        drawdown = (price - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    total_return = (closes[-1] / closes[0] - 1.0) if closes[0] > 0 else 0.0

    return {
        "region": region,
        "code": code,
        "k_type": k_type,
        "limit": limit,
        "sample_size": sample_size,
        "start_time": times[0] if times else None,
        "end_time": times[-1] if times else None,
        "close": {
            "last": last_close,
            "mean": mean_close,
            "min": min_close,
            "max": max_close,
        },
        "high_low": {
            "highest_high": max(highs) if highs else None,
            "lowest_low": min(lows) if lows else None,
        },
        "return": {
            "total_return": total_return,
        },
        "risk": {
            "max_drawdown": max_drawdown,
            "volatility": vol,
        },
        "raw": {
            "code": payload.get("code"),
            "msg": payload.get("msg"),
        },
    }


@app.tool()
def mcp_get_tick(
    region: Region,
    code: str,
) -> dict[str, Any]:
    """
    获取实时报价 tick，对应 REST 接口 /stock/tick。

    参数
    ----
    region: 市场代码，例如 "HK" / "SZ" / "SH" / "US" / "SG" / "JP"
    code: 证券代码，例如 "700.HK"
    """

    url = "https://api.itick.org/stock/tick"
    params = {
        "region": region,
        "code": code,
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@app.resource(
    uri="docs://itick-mcp-deploy",
    name="iTick MCP 部署说明",
    description="在 Cursor 中部署本地 iTick Python MCP 服务的完整流程文档。",
    mime_type="text/markdown",
)
def itick_mcp_deploy_doc() -> str:
    """
    iTick MCP 部署流程的 Markdown 文档内容。
    来源：项目内 docs/itick_mcp_deploy.md。
    """

    # 懒加载本地文档，作为 Resource 暴露给客户端
    from pathlib import Path

    doc_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "docs"
        / "itick_mcp_deploy.md"
    )
    return doc_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    app.run()


