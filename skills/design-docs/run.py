#!/usr/bin/env python3
"""
设计文档：根据需求分析生成架构、接口、数据模型设计。

流程：
1. 读取初步需求分析文档，解析涉及的中心
2. plan.md：按中心逐个进入对应工程目录，找出涉及的具体接口、文件及改动点
3. design.md：workspace 为 newsales 全量目录（所有代码都在），根据 plan 给出具体的改造接口/内容
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.state import get_root


def _project_to_dir(project: str) -> str:
    """将项目名转为 newsales 下的目录名。如 PCWeb(tms-PCWeb_Polaris) -> tms-PCWeb_Polaris"""
    m = re.search(r"\(([^)]+)\)", project)
    if m:
        return m.group(1)
    return project


def _run_cursor_agent(prompt: str, workspace: Path, timeout: int = 600) -> str:
    """
    使用 Cursor CLI (agent) 执行 prompt，workspace 为代码目录。
    返回 agent 输出的纯文本。
    """
    workspace = workspace.resolve()
    if not workspace.exists():
        return f"（workspace 不存在: {workspace}）"

    result = subprocess.run(
        [
            "agent",
            "-p",
            "--output-format", "text",
            "--workspace", str(workspace),
            "--trust",
            "--mode", "ask",  # 只读模式，不修改文件
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"agent failed: {result.stderr or result.stdout}")
    return (result.stdout or "").strip()


def _parse_centers_from_analysis(analysis_text: str) -> list[tuple[str, str]]:
    """
    从需求分析文档中解析涉及中心表格，返回 [(中心/模块, 所属项目), ...]。
    支持两种格式：
    - 旧：中心/模块 | 所属项目 | 负责内容
    - 新：所属项目 | 涉及功能（简短说明）
    """
    centers: list[tuple[str, str]] = []
    lines = analysis_text.split("\n")
    in_table = False
    first_col_is_project = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue

        cells = [c.strip() for c in stripped.split("|") if c.strip()]
        if not cells:
            continue

        if "所属项目" in cells or "项目" in cells:
            in_table = True
            first_col_is_project = cells[0] in ("所属项目", "项目") or "所属项目" in cells[0]
            continue

        if in_table and len(cells) >= 1:
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            if first_col_is_project:
                project = cells[0]
            else:
                project = cells[1] if len(cells) > 1 else cells[0]
            if project and project not in ("所属项目", "项目", "涉及功能"):
                center_module = project if first_col_is_project else cells[0]
                centers.append((center_module, project))

    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for c, p in centers:
        if p not in seen:
            seen.add(p)
            unique.append((c, p))
    return unique


def _get_center_dirs(centers: list[tuple[str, str]], newsales_dir: Path) -> list[str]:
    """
    从 centers 提取在 newsales 下存在的工程目录名，去重且保持顺序。
    若无匹配则回退到默认中心列表。
    """
    default_order = ("bms_Polaris", "tms-PCWeb_Polaris", "tms-React_Polaris")
    dirs_seen: set[str] = set()
    result: list[str] = []
    for _cm, proj in centers:
        d = _project_to_dir(proj)
        if d not in dirs_seen and (newsales_dir / d).is_dir():
            dirs_seen.add(d)
            result.append(d)
    if not result:
        for d in default_order:
            if (newsales_dir / d).is_dir():
                result.append(d)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--analysis-path", required=True)
    args = parser.parse_args()

    root = get_root()
    analysis_path = root / args.analysis_path
    if not analysis_path.exists():
        print(f"Error: {analysis_path} not found", file=sys.stderr)
        sys.exit(1)

    analysis_text = analysis_path.read_text(encoding="utf-8")

    newsales_path = root / "NEWSALES_CONTEXT.md"
    newsales_ctx = newsales_path.read_text(encoding="utf-8") if newsales_path.exists() else ""

    # 解析涉及的中心/项目
    centers = _parse_centers_from_analysis(analysis_text)
    if not centers:
        centers = [("bms", "bms_Polaris"), ("tms-React", "tms-React_Polaris")]

    # 目录名与 req-analysis 保持一致：从 analysis-path 的父目录名获取
    dir_name = analysis_path.parent.name
    out_dir = root / "output" / "design-docs" / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    newsales_dir = root / "newsales"
    if not newsales_dir.exists():
        print("Error: newsales 目录不存在", file=sys.stderr)
        sys.exit(1)

    center_dirs = _get_center_dirs(centers, newsales_dir)
    centers_list = "\n".join(f"- {cm} → {proj}" for cm, proj in centers)

    # 1. 生成 plan.md：按中心逐个进入对应工程，找出涉及的具体接口、文件及改动点
    plan_sections: list[str] = []
    for center_dir in center_dirs:
        ws = newsales_dir / center_dir
        section_prompt = ""
        if newsales_ctx:
            section_prompt += "## NEWSALES 项目上下文\n\n" + newsales_ctx.strip() + "\n\n---\n\n"
        section_prompt += f"""## 需求分析文档
{analysis_text[:6000]}

---

## 涉及的中心
{centers_list}

---

当前 workspace 为 **{center_dir}** 工程目录（newsales/{center_dir}），请浏览该工程代码，找出本需求涉及的具体内容。

要求（仅输出该中心的内容）：
1. 以 `## {center_dir}` 作为章节标题
2. 必须包含：
   - **改造概要**：该中心在本需求中的改造点
   - **接口字段变更**：找出具体接口（路径/方法名）、入参/出参字段名、类型、变更说明（新增/修改/删除）
   - **涉及文件**：列出要修改的文件路径（相对 newsales），及每个文件大概要改哪些内容
3. 内容需具体，基于实际代码结构，以便后续 design 据此展开
4. 不要输出「前后端衔接与一致性说明」

只输出 Markdown，不要其他说明。不要修改任何文件。"""

        try:
            section = _run_cursor_agent(section_prompt, ws)
            if section and not section.startswith("（"):
                plan_sections.append(section)
            else:
                plan_sections.append(f"## {center_dir}\n\n（生成失败或为空）")
        except RuntimeError as e:
            plan_sections.append(f"## {center_dir}\n\n（生成失败: {e}）")
            print(f"Warning: {center_dir} plan 生成失败: {e}", file=sys.stderr)

    plan_content = "\n\n---\n\n".join(plan_sections) if plan_sections else ""
    (out_dir / "plan.md").write_text(plan_content, encoding="utf-8")

    # 2. 根据 plan 生成总设计文档 design.md（workspace 为全部代码所在目录）
    plan_for_design = plan_content if plan_content else f"（执行计划为空，请基于需求分析直接设计）\n\n{analysis_text[:3000]}"
    design_prompt = ""
    if newsales_ctx:
        design_prompt += "## NEWSALES 项目上下文\n\n" + newsales_ctx.strip() + "\n\n---\n\n"
    design_prompt += f"""## 需求分析文档
{analysis_text[:6000]}

---

## 执行计划（请据此展开详细设计）
{plan_for_design[:6000]}

---

## 涉及的中心/项目
{centers_list}

---

当前 workspace 为 **newsales 全量目录**（所有中心代码都在），请浏览完整代码结构，根据上述执行计划生成**总设计文档**。

要求：
1. 文档按中心分章节，与执行计划一一对应
2. 每个中心必须包含：
   - **改造概要**：简要说明
   - **接口字段定义**：具体接口路径、HTTP 方法、入参/出参字段（字段名、类型、必填、说明）
   - **涉及文件与改动**：列出要修改的文件路径（相对 newsales），及每个文件的具体改造内容或代码片段
3. 基于执行计划中的接口、文件，给出可落地的具体改造接口/内容
4. 不要输出「前后端衔接与一致性说明」相关章节

只输出 Markdown，不要其他说明。不要修改任何文件。"""

    try:
        design_content = _run_cursor_agent(design_prompt, newsales_dir)
        if not design_content or design_content.startswith("（"):
            design_content = f"# 设计文档\n\n生成结果为空或异常：{design_content or '无输出'}"
    except RuntimeError as e:
        design_content = f"# 设计文档\n\n生成失败：{e}\n\n请检查 Cursor CLI agent 是否可用，或手动执行设计。"
        print(f"Error: design.md 生成失败: {e}", file=sys.stderr)

    (out_dir / "design.md").write_text(design_content, encoding="utf-8")
    print(str((out_dir / "design.md").relative_to(root)))


if __name__ == "__main__":
    main()
