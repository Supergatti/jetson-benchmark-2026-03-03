"""
jetson_agent.py — Jetson 设备上下文工具脚本

提供对本仓库中设备文档的程序化访问，可作为智能体的上下文来源使用。
用法:
    python3 jetson_agent.py             # 打印设备摘要
    python3 jetson_agent.py --section cameras   # 打印摄像头信息
    python3 jetson_agent.py --section models    # 打印模型文件清单
    python3 jetson_agent.py --section hardware  # 打印硬件快照
"""

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

SECTIONS = {
    "hardware": REPO_ROOT / "hardware.md",
    "cameras": REPO_ROOT / "cameras.md",
    "models": REPO_ROOT / "models.md",
    "python_packages": REPO_ROOT / "python_packages.md",
    "docker": REPO_ROOT / "docker_details.md",
    "ros_isaac": REPO_ROOT / "ros_isaac.md",
    "inventory": REPO_ROOT / "jetson_system_inventory.md",
}


def print_section(name: str) -> None:
    path = SECTIONS.get(name)
    if path is None:
        print(f"Unknown section '{name}'. Available: {', '.join(SECTIONS)}")
        return
    if not path.exists():
        print(f"File not found: {path}")
        return
    print(f"\n{'='*60}")
    print(f"  {name.upper()} — {path.name}")
    print(f"{'='*60}\n")
    print(path.read_text(encoding="utf-8"))


def print_summary() -> None:
    """Print a brief device summary from the inventory document."""
    inv = SECTIONS["inventory"]
    if inv.exists():
        print(inv.read_text(encoding="utf-8"))
    else:
        print("jetson_system_inventory.md not found.")
    print("\nAvailable sections:", ", ".join(SECTIONS))
    print("Run with --section <name> for details.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jetson 设备上下文工具 — 打印设备文档各节内容"
    )
    parser.add_argument(
        "--section",
        choices=list(SECTIONS.keys()),
        help="要打印的文档节（不指定则打印总览）",
    )
    args = parser.parse_args()

    if args.section:
        print_section(args.section)
    else:
        print_summary()


if __name__ == "__main__":
    main()
