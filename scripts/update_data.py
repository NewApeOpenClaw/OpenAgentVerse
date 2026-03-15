#!/usr/bin/env python3
"""
OpenAgentVerse 自动更新脚本
自动收集GitHub上OpenClaw相关项目的最新数据
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"命令执行失败: {cmd}")
            print(f"错误: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return None

def search_openclaw_projects():
    """搜索OpenClaw相关项目"""
    print("搜索OpenClaw相关项目...")
    
    search_queries = [
        '"openclaw"',
        '"clawdbot"',
        '"mimiclaw"',
        '"clawhub"',
        '"skillhub"',
        '"open agent"',
        '"ai agent"'
    ]
    
    all_projects = []
    
    for query in search_queries:
        print(f"搜索: {query}")
        cmd = f'gh search repos {query} --limit 10 --json name,fullName,description,stargazersCount,forksCount,updatedAt'
        output = run_command(cmd)
        
        if output:
            try:
                projects = json.loads(output)
                all_projects.extend(projects)
            except:
                pass
    
    # 去重
    unique_projects = {}
    for project in all_projects:
        full_name = project.get('fullName')
        if full_name and full_name not in unique_projects:
            unique_projects[full_name] = project
    
    return list(unique_projects.values())

def generate_daily_report(projects):
    """生成每日报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 按星标数排序
    sorted_projects = sorted(projects, key=lambda x: x.get('stargazersCount', 0), reverse=True)
    
    report = f"""# OpenAgentVerse 每日数据报告 ({date_str})

**生成时间**: {now}
**分析项目数**: {len(projects)}

## 📊 今日热门项目 Top 5

"""
    
    for i, project in enumerate(sorted_projects[:5], 1):
        stars = project.get('stargazersCount', 0)
        forks = project.get('forksCount', 0)
        desc = project.get('description', '')[:80]
        
        report += f"{i}. **{project.get('fullName')}** - ⭐{stars:,} | 🍴{forks:,}\n"
        if desc:
            report += f"   {desc}\n"
        report += "\n"
    
    # 统计数据
    total_stars = sum(p.get('stargazersCount', 0) for p in projects)
    total_forks = sum(p.get('forksCount', 0) for p in projects)
    
    report += f"""
## 📈 今日统计数据

- **分析项目数**: {len(projects)}
- **总星标数**: ⭐ {total_stars:,}
- **总Fork数**: 🍴 {total_forks:,}
- **最高星标项目**: ⭐ {sorted_projects[0].get('stargazersCount', 0):,} ({sorted_projects[0].get('fullName')})

## 🔄 更新日志

- {date_str}: 自动收集了 {len(projects)} 个OpenClaw相关项目
- 数据来源: GitHub Search API
- 更新频率: 每日自动更新

---

*本报告由OpenAgentVerse自动更新系统生成*
"""
    
    return report

def update_stats_in_readme(projects):
    """更新README中的统计数据"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 读取现有README
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        
        # 查找并替换统计数据部分
        if "## 📊 数据统计" in content:
            # 计算新统计数据
            sorted_projects = sorted(projects, key=lambda x: x.get('stargazersCount', 0), reverse=True)
            total_stars = sum(p.get('stargazersCount', 0) for p in projects)
            total_forks = sum(p.get('forksCount', 0) for p in projects)
            
            new_stats = f"""## 📊 数据统计

- **已收集项目**: {len(projects)}+
- **最高星标项目**: ⭐{sorted_projects[0].get('stargazersCount', 0) if sorted_projects else 0} ({sorted_projects[0].get('fullName') if sorted_projects else 'N/A'})
- **总星标数**: ⭐{total_stars:,}
- **总Fork数**: 🍴{total_forks:,}
- **更新频率**: 每日自动更新
- **最后更新**: {now}
"""
            import re
            pattern = r"## 📊 数据统计[\s\S]*?(?=\n## |\Z)"
            content = re.sub(pattern, new_stats, content)
            
            # 写回文件
            readme_path.write_text(content, encoding='utf-8')
            print("README统计数据已更新")
    
    return datetime.now().strftime("%Y-%m-%d")

def main():
    print("=" * 60)
    print("OpenAgentVerse 自动更新脚本")
    print("=" * 60)
    
    # 搜索项目
    projects = search_openclaw_projects()
    if not projects:
        print("未找到任何项目")
        return 1
    
    print(f"找到 {len(projects)} 个项目")
    
    # 生成每日报告
    report = generate_daily_report(projects)
    
    # 保存每日报告
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_dir = Path("reports/daily")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{date_str}-report.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"每日报告已保存: {report_path}")
    
    # 更新README统计数据
    update_date = update_stats_in_readme(projects)
    
    # 保存项目数据JSON
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / f"{date_str}-projects.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": update_date,
            "total_projects": len(projects),
            "projects": projects[:20]
        }, f, indent=2, ensure_ascii=False)
    print(f"项目数据已保存: {data_path}")
    
    print("=" * 60)
    print("自动更新完成!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())