# -*- coding: utf-8 -*-
from pathlib import Path
import html
import re

OUT = Path(".")

PAGES = [
    ("index.html", "概要", "社内で uv を使うための導入・移行・運用ガイド"),
    ("install.html", "インストール", "uv のインストール"),
    ("setup.html", "ネットワーク設定の基本", "uv のネットワーク設定の基本"),
    ("usage.html", "基本操作と概念", "uv の基本操作と概念"),
    ("start-project.html", "プロジェクトの始め方", "uv で新規プロジェクトを始める"),
    ("copy-existing-project.html", "既存プロジェクトをコピーして始める方法", "uv 対応済みプロジェクトを手元で動かす"),
    ("migration.html", "Poetry + pyenv からの移行", "Poetry + pyenv から uv へ移行する"),
    ("security.html", "セキュリティ運用", "uv 利用時のセキュリティ運用"),
]

PAGE_SUMMARIES = [
    "社内の Python 開発環境を uv ベースで導入・移行・運用するための全体像を示します。",
    "社内標準の uv バージョンを Windows 端末へ導入し、uv コマンドを利用できる状態にします。",
    "社内 proxy、証明書、private package repository など、uv のネットワーク設定の考え方を整理します。",
    "uv を使ううえで必要になる主要概念、基本コマンド、依存関係の記法を整理します。",
    "uv を使って新規 Python プロジェクトを作成し、初回実行できる状態にする流れを示します。",
    "uv 対応済みの既存プロジェクトを取得し、lock file を尊重して手元で動かす流れを示します。",
    "Poetry + pyenv 構成の既存プロジェクトを uv ベースの運用へ移行する手順を整理します。",
    "uv 利用時に必要な脆弱性監査、ライセンス確認、依存追加時のレビュー観点を整理します。",
]


def extract_toc_entries(body):
    entries = []
    pending_section = None

    for line in body.splitlines():
        section_match = re.search(r'<section id="([^"]+)"[^>]*data-toc[^>]*>', line)
        if section_match and 'data-toc-level="3"' not in line:
            pending_section = section_match.group(1)
            continue

        h2_match = re.search(r"<h2>(.*?)</h2>", line)
        if pending_section and h2_match:
            entries.append({"id": pending_section, "title": h2_match.group(1), "level": 2})
            pending_section = None
            continue

        h3_match = re.search(r'<h3 id="([^"]+)"[^>]*data-toc[^>]*>(.*?)</h3>', line)
        if h3_match:
            entries.append({"id": h3_match.group(1), "title": h3_match.group(2), "level": 3})

    return entries


def render_chapter_toc_entries(entries, chapter_href, indent="              "):
    if not entries:
        return f"{indent}<li>No sections</li>"

    groups = []
    for entry in entries:
        if entry["level"] <= 2 or not groups:
            groups.append({"entry": entry, "children": []})
        else:
            groups[-1]["children"].append(entry)

    lines = []
    for group in groups:
        entry = group["entry"]
        href = html.escape(f"{chapter_href}#{entry['id']}", quote=True)
        title = html.escape(entry["title"])
        lines.append(f'{indent}<li><a href="{href}">{title}</a>')
        if group["children"]:
            lines.append(f"{indent}  <ol>")
            for child in group["children"]:
                child_href = html.escape(f"{chapter_href}#{child['id']}", quote=True)
                child_title = html.escape(child["title"])
                lines.append(f'{indent}    <li><a href="{child_href}">{child_title}</a></li>')
            lines.append(f"{indent}  </ol>")
        lines.append(f"{indent}</li>")

    return "\n".join(lines)


def render_contents_tree(current_index, toc_entries_by_page):
    lines = []
    for index, (href, label, _) in enumerate(PAGES):
        open_attr = " open" if index == current_index else ""
        current_attr = ' aria-current="page"' if index == current_index else ""
        safe_href = html.escape(href, quote=True)
        safe_label = html.escape(label)
        lines.append('            <li class="site-contents-chapter">')
        lines.append(f"              <details{open_attr}>")
        lines.append(f'                <summary><a href="{safe_href}"{current_attr}>{safe_label}</a></summary>')
        lines.append('                <ol class="toc-tree toc-tree-numbered">')
        lines.append(render_chapter_toc_entries(toc_entries_by_page[index], href, "                  "))
        lines.append("                </ol>")
        lines.append("              </details>")
        lines.append("            </li>")
    return "\n".join(lines)


def sidebar(current_index, toc_entries_by_page):
    return f"""
    <aside class="sidebar">
      <header class="sidebar-header" aria-labelledby="sidebar-title">
        <h2 id="sidebar-title" class="sidebar-title">社内 uv 利用ガイド</h2>
        <p class="sidebar-subtitle">Poetry + pyenv から uv へ移行するための標準手順</p>
      </header>
      <details class="nav-section" open>
        <summary>Contents</summary>
        <div class="nav-body">
          <ol class="nav-list site-contents-tree">
{render_contents_tree(current_index, toc_entries_by_page)}
          </ol>
        </div>
      </details>
      <details class="nav-section" open>
        <summary>References</summary>
        <div class="nav-body">
          <ol class="nav-list">
            <li><a href="https://docs.astral.sh/uv/" target="_blank" rel="noreferrer">uv 公式ドキュメント</a></li>
            <li><a href="https://github.com/tyaso777/html-doc-template" target="_blank" rel="noreferrer">html-doc-template</a></li>
          </ol>
        </div>
      </details>
    </aside>"""


def code(lang, text):
    text = text.replace("\\n", "\n")
    return f'<div class="code-caption">{lang}</div>\n<pre class="code-block language-{lang}"><code class="language-{lang}">{text}</code></pre>'


def table(headers, rows):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def project_command_effects_table():
    return table(
        ["コマンド", "起きること", "作成されるもの", "更新されるもの"],
        [
            [
                "<code>uv init $projectName</code>",
                "現在のフォルダの下に <code>$projectName</code> で指定したプロジェクトを作成する。",
                "プロジェクトフォルダ、<code>pyproject.toml</code>、<code>README.md</code>、サンプルコードなど。",
                "通常は既存ファイルを更新しない。既存フォルダを指定する場合は内容を確認する。",
            ],
            [
                "<code>uv python pin 3.12</code>",
                "このプロジェクトで使う Python バージョンを指定する。",
                "<code>.python-version</code> が無い場合は作成する。",
                "既に <code>.python-version</code> がある場合は更新する。",
            ],
            [
                "<code>uv add requests</code>",
                "<code>requests</code> を依存関係に追加し、依存解決を行う。",
                "<code>uv.lock</code> が無い場合は作成する。必要に応じて <code>.venv</code> を作成する。",
                "<code>pyproject.toml</code> と <code>uv.lock</code> を更新する。既に <code>.venv</code> がある場合は環境も更新する。",
            ],
        ],
    )


def nav(prev_page=None, next_page=None):
    links = []
    if prev_page:
        href, label, _ = prev_page
        links.append(f'<a class="chapter-nav-link" href="{href}"><span>Previous</span><strong>{label}</strong></a>')
    if next_page:
        href, label, _ = next_page
        links.append(f'<a class="chapter-nav-link next" href="{href}"><span>Next</span><strong>{label}</strong></a>')
    return '<nav class="chapter-nav" aria-label="ページ移動">' + "\n".join(links) + "</nav>"


def strip_manual_number(title):
    title = re.sub(r"^手順\s*\d+\s*[:：]\s*", "", title)
    title = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", title)
    return title


def apply_heading_numbering(body):
    h2_count = 0
    h3_count = 0
    numbered = []
    pending_h2 = None

    for line in body.splitlines():
        if "<section " in line and "data-toc" in line and "data-toc-level=\"3\"" not in line:
            match = re.search(r'data-toc-title="([^"]+)"', line)
            if match:
                h2_count += 1
                h3_count = 0
                raw_title = strip_manual_number(match.group(1))
                numbered_title = f"{h2_count}. {raw_title}"
                pending_h2 = numbered_title
        elif "<h3 " in line and "data-toc" in line:
            match = re.search(r'data-toc-title="([^"]+)"', line)
            if match:
                h3_count += 1
                raw_title = strip_manual_number(match.group(1))
                numbered_title = f"{h2_count}.{h3_count} {raw_title}"
                line = re.sub(r"(>)([^<]+)(</h3>)", lambda m: f"{m.group(1)}{numbered_title}{m.group(3)}", line, count=1)

        if pending_h2 and "<h2>" in line:
            line = re.sub(r"<h2>.*?</h2>", f"<h2>{pending_h2}</h2>", line, count=1)
            pending_h2 = None

        numbered.append(line)

    return "\n".join(numbered)


def runner_stubs():
    return """
      <div class="visually-hidden" aria-hidden="true">
        <textarea id="python-code"></textarea>
        <button id="load-button" type="button">Load Python Runtime</button>
        <button id="run-button" type="button">Run Python</button>
        <button id="reset-button" type="button">Reset Code</button>
        <button id="restart-runtime-button" type="button">Restart Python Runtime</button>
        <pre id="output"></pre>
        <span id="pyodide-status"></span>
      </div>"""


def page_header(title, summary):
    return f"""      <header class="hero">
        <h1>{title}</h1>
        <p>{summary}</p>
      </header>"""


def shell(title, body, idx, toc_entries_by_page):
    prev_page = PAGES[idx - 1] if idx > 0 else None
    next_page = PAGES[idx + 1] if idx < len(PAGES) - 1 else None
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - 社内 uv 利用ガイド</title>
  <link rel="stylesheet" href="assets/css/technical-doc.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
</head>
<body>
  <div class="layout">
    {sidebar(idx, toc_entries_by_page)}
    <main class="content">
{body}
      {nav(prev_page, next_page)}
      <footer class="footer">最終更新: 2026-06-18</footer>
      {runner_stubs()}
    </main>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-powershell.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-toml.min.js"></script>
  <script src="assets/js/technical-doc.js"></script>
</body>
</html>
"""


index_body = f"""
      <section id="purpose" data-toc data-toc-title="目的">
        <h2>目的</h2>
        <p>このガイドは、社内の Python 開発環境を uv ベースで導入・移行・運用するための標準手順をまとめたものです。Windows 端末、社内 proxy、社内 CA、private package repository を利用する環境を主な対象にしています。</p>
        <p>開発者が同じ手順で Python、仮想環境、依存関係、lock file、監査コマンドを扱えるようにし、ローカル環境と CI の差分を小さくすることを目的とします。</p>
      </section>
      <section id="target-readers" data-toc data-toc-title="対象読者">
        <h2>対象読者</h2>
        <ul>
          <li>Python プロジェクトを新規に作成する開発者</li>
          <li><code>pyenv + Poetry</code> 構成の既存プロジェクトを uv へ移行する担当者</li>
          <li>社内 proxy、証明書、private index、CI 設定を整備する担当者</li>
          <li>依存パッケージの脆弱性監査やライセンス確認を運用する担当者</li>
        </ul>
      </section>
      <section id="guide-map" data-toc data-toc-title="ガイド構成">
        <h2>ガイド構成</h2>
        {table(["ページ", "主な内容", "読むタイミング"], [
            ['<a href="install.html">インストール</a>', 'proxy 配下での導入、uv バージョン固定、導入確認', '初回導入時'],
            ['<a href="setup.html">ネットワーク設定の基本</a>', '<code>HTTP_PROXY</code>、<code>HTTPS_PROXY</code>、<code>UV_SYSTEM_CERTS</code>、private package repository、依存解決の考え方', '初回導入時、SSL エラー対応時'],
            ['<a href="usage.html">基本操作と概念</a>', 'プロジェクト、仮想環境、lock、sync、tool、pip 互換', '日常開発'],
            ['<a href="start-project.html">プロジェクトの始め方</a>', '新規プロジェクト作成、Python バージョン固定、初回依存追加、初回実行', '新規開発開始時'],
            ['<a href="copy-existing-project.html">既存プロジェクトをコピーして始める方法</a>', 'clone / コピー後の同期、既存 lock file の利用、動作確認', '既存 uv プロジェクト利用時'],
            ['<a href="migration.html">Poetry + pyenv からの移行</a>', '対応表、移行手順、互換でない点、CI 変更', '既存プロジェクト移行時'],
            ['<a href="security.html">セキュリティ運用</a>', '<code>pip-audit</code>、<code>pip-licenses</code>、依存追加時チェック、CI 監査', '標準化、監査、リリース前'],
        ])}
      </section>
      <section id="operational-assumptions" data-toc data-toc-title="運用上の前提">
        <h2>運用上の前提</h2>
        <ul>
          <li>uv 本体は、社内で確認済みの標準バージョンを利用します。</li>
          <li>プロジェクトの Python バージョンは <code>.python-version</code> と <code>pyproject.toml</code> で明示します。</li>
          <li>社内 proxy と証明書設定は、ユーザー環境変数または CI の環境変数で管理します。</li>
          <li>依存パッケージの解決では、必要に応じて <code>--exclude-newer "X days"</code> を使い、公開直後のパッケージを避けます。</li>
          <li>アプリケーション開発では <code>uv.lock</code> をコミットし、レビュー対象に含めます。</li>
          <li>脆弱性監査とライセンス監査は、ローカル確認と CI の両方で実行できる形にします。</li>
        </ul>
      </section>
"""

install_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、社内標準の uv バージョンを Windows 端末へ導入し、<code>uv --version</code> で利用可能な状態にすることです。社内 proxy が必要な環境を前提に、proxy 設定の確認、PowerShell セッションへの proxy 設定、バージョンを指定したインストール、インストール確認の順に実施します。</p>
        <p>会社の端末管理ルールにより、外部サイトからのインストーラ取得、PowerShell スクリプト実行、開発ツール導入に申請や承認が必要な場合があります。インストール作業の前に、IT 部門への申請や必要な事前対応を済ませてから実行します。</p>
      </section>
      <section id="prerequisites" data-toc data-toc-title="proxy 設定を確認する">
        <h2>proxy 設定を確認する</h2>
        <p>Windows 端末では、まず WinHTTP proxy の設定を確認します。</p>
        {code("powershell", "netsh winhttp show proxy")}
      </section>
      <section id="proxy-settings" data-toc data-toc-title="proxy を設定する">
        <h2>proxy を設定する</h2>
        <p>社内 proxy を利用する場合は、インストーラを実行する前に PowerShell セッションへ proxy を設定します。</p>
        {code("powershell", '# proxy をこの PowerShell セッションに設定する\\n$env:HTTP_PROXY="http://proxy.example.co.jp:8080"\\n$env:HTTPS_PROXY="http://proxy.example.co.jp:8080"')}
      </section>
      <section id="versioned-install" data-toc data-toc-title="uv のバージョンを指定してインストールする">
        <h2>uv のバージョンを指定してインストールする</h2>
        <p>社内標準の uv バージョンを指定してインストールします。開発者間で uv のバージョンを揃えることで、コマンド挙動や lock file 更新時の差分を説明しやすくなります。</p>
        {code("powershell", '$uvVersion="0.11.8"\\npowershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/$uvVersion/install.ps1 | iex"')}
        <aside class="callout callout-warning">uv 本体は、社内で確認済みの標準バージョンを社内ポータルやセットアップスクリプトで明示します。</aside>
        <aside class="callout callout-info">検証用端末や一時的な確認では、バージョンを指定せずに <code>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"</code> を実行することもできます。社内標準の開発環境では、上記のバージョン指定インストールを使います。</aside>
      </section>
      <section id="verify-install" data-toc data-toc-title="インストール確認">
        <h2>インストール確認</h2>
        {code("powershell", "uv --version\\nuv help\\nuv python list")}
      </section>
"""

setup_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、社内ネットワーク配下で uv を安定して利用するために必要な環境変数と設定の考え方を整理することです。社内 proxy、SSL inspection、社内 CA、private package repository を利用する環境を前提に、<code>HTTP_PROXY</code>、<code>HTTPS_PROXY</code>、<code>UV_SYSTEM_CERTS</code> などの設定方法を説明します。</p>
        <p>実際の作業手順は、<a href="start-project.html">プロジェクトの始め方</a> と <a href="copy-existing-project.html">既存プロジェクトをコピーして始める方法</a> で改めて記載します。このページでは、各設定が何のためのものか、どこに保存されるか、どの範囲に効くかを押さえます。</p>
      </section>
      <section id="proxy-check" data-toc data-toc-title="proxy の確認">
        <h2>proxy の確認</h2>
        <p>Windows 端末で OS 側に設定されている WinHTTP proxy を確認します。このコマンドは設定を変更せず、現在の端末設定を表示するだけです。</p>
        {code("powershell", 'netsh winhttp show proxy')}
      </section>
      <section id="setting-scope" data-toc data-toc-title="設定の有効範囲">
        <h2>設定の有効範囲</h2>
        <p>uv に渡す設定は、どこに保存するかで有効範囲が変わります。トラブル時に原因を追えるよう、手順書やセットアップスクリプトでは「このセッションだけ」なのか「永続設定」なのかを明示します。</p>
        <p>設定方法には、PowerShell でコマンドとして実行するものと、設定ファイルに記載するものがあります。下表では、設定方法欄の先頭にどちらの操作かを示します。</p>
        <div class="table-wrap"><table>
          <thead>
            <tr>
              <th style="width: 12rem;">設定方法</th>
              <th>有効範囲</th>
              <th>保存場所</th>
              <th>確認方法</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>PowerShell で一時設定</strong><br><code>$env:<wbr>NAME="VALUE"</code></td>
              <td>現在の PowerShell セッションのみ</td>
              <td>現在のプロセス環境。PowerShell を閉じると消える。</td>
              <td><code>echo $env:<wbr>NAME</code></td>
            </tr>
            <tr>
              <td><strong>PowerShell で永続設定</strong><br><code>[Environment]::<wbr>SetEnvironmentVariable("NAME", "VALUE", "User")</code></td>
              <td>現在の Windows ユーザーで永続</td>
              <td>Windows のユーザー環境変数。新しく開いた PowerShell から反映される。</td>
              <td><code>[Environment]::<wbr>GetEnvironmentVariable("NAME", "User")</code></td>
            </tr>
            <tr>
              <td><strong>プロジェクト設定ファイルに記載</strong><br><code>pyproject.toml</code> の <code>[tool.uv]</code></td>
              <td>そのプロジェクト配下</td>
              <td>プロジェクトの <code>pyproject.toml</code></td>
              <td>ファイルをレビューする</td>
            </tr>
            <tr>
              <td><strong>uv 設定ファイルに記載</strong><br><code>uv.toml</code></td>
              <td>配置場所に応じてプロジェクト / ユーザー / システム</td>
              <td>プロジェクトの <code>uv.toml</code>、または Windows では <code>%APPDATA%&#92;<wbr>uv&#92;<wbr>uv.toml</code></td>
              <td>ファイルをレビューする</td>
            </tr>
          </tbody>
        </table></div>
        <aside class="callout callout-info">同じ設定が複数箇所にある場合、コマンドライン引数、環境変数、永続設定ファイルの順に優先されます。検証時は一時的な <code>$env:</code> 設定が残っていないか確認します。</aside>
      </section>
      <section id="proxy-env-vars" data-toc data-toc-title="proxy 環境変数">
        <h2>proxy 環境変数</h2>
        <p>この PowerShell セッションだけで試す場合は、<code>$env:HTTP_PROXY</code> と <code>$env:HTTPS_PROXY</code> を設定します。値は PowerShell を閉じると消えます。</p>
        {code("powershell", '# proxy をこの PowerShell セッションに設定する\\n$env:HTTP_PROXY="http://proxy.example.co.jp:8080"\\n$env:HTTPS_PROXY="http://proxy.example.co.jp:8080"\\n\\n# 設定された proxy を確認する\\necho $env:HTTP_PROXY\\necho $env:HTTPS_PROXY')}
        <p>次回以降の PowerShell でも使う場合は、Windows のユーザー環境変数として保存します。保存後、既に開いている PowerShell には自動反映されないため、新しい PowerShell を開いて確認します。</p>
        {code("powershell", '# proxy を Windows のユーザー環境変数として保存する\\n[Environment]::SetEnvironmentVariable("HTTP_PROXY", "http://proxy.example.co.jp:8080", "User")\\n[Environment]::SetEnvironmentVariable("HTTPS_PROXY", "http://proxy.example.co.jp:8080", "User")\\n\\n# 新しい PowerShell を開き、保存された proxy が反映されていることを確認する\\necho $env:HTTP_PROXY\\necho $env:HTTPS_PROXY')}
      </section>
      <section id="system-certs" data-toc data-toc-title="社内 CA / SSL inspection">
        <h2>社内 CA / SSL inspection</h2>
        <p>社内 proxy が TLS 通信を検査している場合、OS の証明書ストアに入っている社内ルート CA を uv に利用させます。まずは現在の PowerShell セッションだけで有効化して、通信できるか確認します。</p>
        {code("powershell", '# OS の証明書ストアをこの PowerShell セッションで利用する\\n$env:UV_SYSTEM_CERTS="1"\\n\\n# 設定された値を確認する\\necho $env:UV_SYSTEM_CERTS')}
        <p>継続して必要な端末では、Windows のユーザー環境変数として永続化します。保存場所は Windows のユーザー環境変数です。</p>
        {code("powershell", '# OS の証明書ストアを使う設定を Windows のユーザー環境変数として保存する\\n[Environment]::SetEnvironmentVariable("UV_SYSTEM_CERTS", "1", "User")\\n\\n# 新しい PowerShell を開き、保存された値が反映されていることを確認する\\necho $env:UV_SYSTEM_CERTS')}
      </section>
      <section id="private-index" data-toc data-toc-title="private package repository">
        <h2>private package repository</h2>
        <p>private package repository は、社内で作成した Python パッケージや、社内でミラーした外部パッケージを配布するためのパッケージ置き場です。PyPI ではなく社内の package index から取得する必要があるプロジェクトで使います。</p>
        <p>すべてのプロジェクトで設定するものではありません。公開 PyPI から依存パッケージを取得できるプロジェクトや、社内 private package を使わないプロジェクトでは、この設定は不要です。</p>
        <p>private package repository をプロジェクトごとに固定する場合は、プロジェクトの <code>pyproject.toml</code> に保存します。この設定はリポジトリに含まれるため、レビューと履歴管理の対象になります。</p>
        {code("toml", '[[tool.uv.index]]\\nname = "internal"\\nurl = "https://packages.example.co.jp/simple"\\ndefault = true')}
        <p>端末全体の既定値として保存する場合は、Windows では <code>%APPDATA%\\uv\\uv.toml</code> を使います。ユーザー設定に入れると、複数プロジェクトへ影響するため、社内標準として配布する設定だけにします。</p>
        {code("toml", '[[index]]\\nname = "internal"\\nurl = "https://packages.example.co.jp/simple"\\ndefault = true')}
      </section>
      <section id="exclude-newer" data-toc data-toc-title="新しすぎるリリースを避ける">
        <h2>新しすぎるリリースを避ける</h2>
        <p>依存パッケージの公開直後は、破損した wheel、差し戻し、悪意あるパッケージ混入、社内 mirror への反映遅延が起きる可能性があります。</p>
        {code("powershell", '# コマンド実行時に、直近 7 日以内に公開された依存パッケージを避ける\\nuv lock --exclude-newer "7 days"\\nuv sync --exclude-newer "7 days"\\n\\n# この PowerShell セッションの既定値として設定する\\n$env:UV_EXCLUDE_NEWER="7 days"\\n\\n# 設定された値で lock / sync を実行する\\nuv lock\\nuv sync')}
        <p><code>X=7</code> とする場合は、<code>--exclude-newer "7 days"</code> または <code>UV_EXCLUDE_NEWER="7 days"</code> を指定します。<code>$env:UV_EXCLUDE_NEWER</code> は現在の PowerShell セッションだけに効きます。永続化する場合はユーザー環境変数として保存できますが、lock file 更新の意図が見えにくくなるため、社内標準ではコマンドライン引数またはCIスクリプトで明示します。</p>
      </section>
"""

usage_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、uv を使ううえで必要になる基本概念、主要コマンド、依存関係の書き方を整理することです。実際の作業手順は、<a href="start-project.html">プロジェクトの始め方</a> や <a href="copy-existing-project.html">既存プロジェクトをコピーして始める方法</a> で扱います。</p>
      </section>
      <section id="core-concepts" data-toc data-toc-title="主要概念">
        <h2>主要概念</h2>
        {table(["概念", "説明"], [
            ["<code>pyproject.toml</code>", "プロジェクトのメタデータ、依存関係、ツール設定を置く標準ファイル。"],
            ["<code>uv.lock</code>", "解決済み依存関係を固定する lock file。"],
            ["<code>.python-version</code>", "プロジェクトで使う Python バージョンを指定するファイル。"],
            ["<code>.venv</code>", "プロジェクトローカルの仮想環境。標準ではプロジェクトフォルダ直下に作成される。"],
            ["<code>UV_PROJECT_ENVIRONMENT</code>", "プロジェクト仮想環境の作成先を変更する環境変数。共有フォルダ上に <code>.venv</code> を置きたくない場合に使う。"],
            ["<code>uv run</code>", "必要に応じて環境を同期し、仮想環境内でコマンドを実行する。"],
        ])}
      </section>
      <section id="new-project" data-toc data-toc-title="新規プロジェクト">
        <h2>新規プロジェクト</h2>
        <p><code>$projectName</code> には作成したいプロジェクトフォルダ名を指定します。<code>C:&#92;path&#92;to&#92;your&#92;project-parent-folder</code> は例であり、プロジェクトを配置する親フォルダのパスに置き換えます。</p>
        <p>仮想環境名をプロジェクト名だけで決めると、別の場所にある同名プロジェクトと衝突する可能性があります。そのため、プロジェクトの保存場所から短いハッシュを作り、仮想環境名の末尾に付けます。</p>
        {code("powershell", '# プロジェクト名を設定する\\n$projectName="my-app"\\n\\n# プロジェクトを配置する親フォルダへ移動する\\ncd C:\\path\\to\\your\\project-parent-folder\\n\\n# 現在のフォルダの下にプロジェクトを作成する\\nuv init $projectName\\n\\n# 作成されたプロジェクトフォルダへ移動する\\ncd $projectName\\n\\n# 同じプロジェクト名の仮想環境と衝突しないように、\\n# プロジェクトの保存場所をもとに短いハッシュを作る\\n$projectRoot=(Resolve-Path .).Path.ToLowerInvariant()\\n$sha256=[System.Security.Cryptography.SHA256]::Create()\\n$hashBytes=$sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($projectRoot))\\n$hash=([System.BitConverter]::ToString($hashBytes) -replace "-", "").Substring(0,8).ToLowerInvariant()\\n\\n# 仮想環境の作成先を、このプロジェクト用のローカルフォルダに設定する\\n$env:UV_PROJECT_ENVIRONMENT="$env:USERPROFILE\\.uv\\venvs\\$projectName-$hash"\\n\\n# 設定された仮想環境の場所を確認する\\necho $env:UV_PROJECT_ENVIRONMENT\\n\\n# プロジェクトで使う Python バージョンを固定する\\nuv python pin 3.12\\n\\n# 依存関係を追加して、プロジェクト環境で実行する\\nuv add requests\\nuv run python -c "import requests; print(requests.__version__)"')}
        <p>uv のコマンドは、ファイルを新規作成する場合と、既存ファイルを更新する場合があります。初回実行時に作成されるものと、既に存在する場合に更新されるものを分けて確認します。</p>
        {project_command_effects_table()}
      </section>
      <section id="dependencies" data-toc data-toc-title="依存関係の追加と削除">
        <h2>依存関係の追加と削除</h2>
        {code("powershell", 'uv add pandas\\nuv add "fastapi[standard]"\\nuv add --dev pytest ruff\\nuv remove pandas\\nuv lock')}
      </section>
      <section id="pyproject-dependency-notation" data-toc data-toc-title="pyproject.toml のライブラリ記法">
        <h2>pyproject.toml のライブラリ記法</h2>
        <p>uv の依存管理では、<code>uv add</code> で指定した内容が <code>pyproject.toml</code> に記録され、解決結果が <code>uv.lock</code> に固定されます。レビュー時は、lock file だけでなく <code>pyproject.toml</code> にどのような制約が入ったかを確認します。</p>
        <p>基本は PEP 508 の dependency specifier です。ライブラリ名、バージョン制約、extras、環境マーカーを 1 つの文字列として書きます。</p>
        {code("toml", '[project]\\nname = "my-app"\\nversion = "0.1.0"\\nrequires-python = ">=3.11,<3.13"\\ndependencies = [\\n    "pandas>=2.2,<3",\\n    "requests>=2.32",\\n    "fastapi[standard]>=0.115",\\n    "pywin32>=306; sys_platform == \\"win32\\"",\\n]')}
        <aside class="callout callout-warning">手で <code>pyproject.toml</code> を編集することもできますが、通常は <code>uv add</code> を使います。<code>uv add</code> は依存定義と lock file の更新を同時に行うため、記法ミスや lock file の更新漏れを減らせます。</aside>
      </section>
      <section id="version-specifiers" data-toc data-toc-title="バージョン制約の書き方">
        <h2>バージョン制約の書き方</h2>
        {table(["指定", "例", "使いどころ"], [
            ["下限のみ", "<code>pandas&gt;=2.2</code>", "基本形。新しい互換版を許容する。"],
            ["範囲指定", "<code>pandas&gt;=2.2,&lt;3</code>", "メジャーバージョンをまたぐ破壊的変更を避けたい場合。"],
            ["完全固定", "<code>pandas==2.2.3</code>", "一時的な回避策や再現性が強く必要な場合。通常は lock file 固定を優先する。"],
            ["除外", "<code>pandas!=2.2.2</code>", "特定バージョンに既知不具合がある場合。"],
            ["互換リリース", "<code>pandas~=2.2</code>", "PEP 440 の互換リリース指定。チームで意味を統一してから使う。"],
        ])}
        <p>アプリケーションでは <code>&gt;=下限,&lt;次のメジャー</code> のように許容範囲を明示し、実際に使う正確なバージョンは <code>uv.lock</code> で固定します。</p>
      </section>
      <section id="poetry-caret-notation" data-toc data-toc-title="Poetry の ^ 記法との対応">
        <h2>Poetry の ^ 記法との対応</h2>
        <p>Poetry では <code>^2.2</code> のような caret requirement をよく使います。これは Poetry 独自の便利な記法で、Python 標準の PEP 508 文字列として <code>[project].dependencies</code> にそのまま書くものではありません。uv 管理へ移行する場合は、意味が分かる範囲指定へ展開して書きます。</p>
        {table(["Poetry 記法", "展開後の例", "意味"], [
            ["<code>^2.2</code>", "<code>&gt;=2.2,&lt;3</code>", "2.x 系を許容し、3.0.0 以上は避ける。"],
            ["<code>^2.2.3</code>", "<code>&gt;=2.2.3,&lt;3</code>", "2.2.3 以上の 2.x 系を許容する。"],
            ["<code>^0.5.1</code>", "<code>&gt;=0.5.1,&lt;0.6</code>", "0.x 系では互換範囲が狭くなる点に注意する。"],
            ["<code>^0.0.3</code>", "<code>&gt;=0.0.3,&lt;0.0.4</code>", "0.0.x では patch 範囲だけを許容する。"],
            ["<code>^1.0.0</code>", "<code>&gt;=1.0.0,&lt;2</code>", "1.x 系を許容する。"],
        ])}
        <aside class="callout callout-warning"><code>~=2.2</code> は PEP 440 の compatible release 指定ですが、Poetry の <code>^</code> と常に同じ意味ではありません。社内標準では、移行時に <code>^</code> を機械的に <code>~=</code> へ置き換えず、<code>&gt;=下限,&lt;上限</code> の形で明示します。</aside>
      </section>
      <section id="uv-add-notation" data-toc data-toc-title="uv add での指定方法">
        <h2>uv add での指定方法</h2>
        <p><code>uv add</code> でも、基本的には <code>pyproject.toml</code> に入る文字列と同じ指定を使います。PowerShell では <code>&lt;</code>、<code>&gt;</code>、<code>;</code>、extras を含む指定が解釈されないよう、依存指定全体を引用符で囲みます。</p>
        {code("powershell", 'uv add "pandas>=2.2,<3"\\nuv add "requests>=2.32"\\nuv add "fastapi[standard]>=0.115"\\nuv add "pywin32>=306; sys_platform == \\"win32\\""\\nuv add --dev "pytest>=8" ruff\\nuv add --optional notebook "jupyterlab>=4"')}
        <p>上記の結果、runtime dependency は <code>[project].dependencies</code> に、開発用依存は <code>[dependency-groups].dev</code> に、optional dependency は <code>[project.optional-dependencies]</code> に入ります。</p>
        {code("toml", '[dependency-groups]\\ndev = [\\n    "pytest>=8",\\n    "ruff",\\n]\\n\\n[project.optional-dependencies]\\nnotebook = [\\n    "jupyterlab>=4",\\n]')}
      </section>
      <section id="project-environment-location" data-toc data-toc-title="仮想環境を C ドライブ内に分離する">
        <h2>仮想環境を C ドライブ内に分離する</h2>
        <p>uv のプロジェクト仮想環境は、標準ではプロジェクトフォルダ直下の <code>.venv</code> に作成されます。プロジェクトを共有フォルダ上で扱う場合、ネットワーク越しの大量ファイルアクセスを避けるため、仮想環境だけをローカルディスクへ配置できます。</p>
        <p><code>UV_PROJECT_ENVIRONMENT</code> を設定すると、uv が作成・利用するプロジェクト仮想環境の場所を変更できます。次の例では、pyenv-win の配置に近い考え方として、ユーザーフォルダ配下の <code>.uv&#92;venvs</code> にこのプロジェクト用の仮想環境を作成します。</p>
        <p>仮想環境を集約するフォルダは <code>$env:USERPROFILE&#92;.uv&#92;venvs</code> です。仮想環境名は <code>プロジェクト名-パス由来ハッシュ</code> の形にします。これにより、同じプロジェクト名でも保存場所が異なる場合は別の仮想環境になります。</p>
        {code("powershell", '# プロジェクト名を設定する\\n$projectName="my-app"\\n\\n# 同じプロジェクト名の仮想環境と衝突しないように、\\n# プロジェクトの保存場所をもとに短いハッシュを作る\\n$projectRoot=(Resolve-Path .).Path.ToLowerInvariant()\\n$sha256=[System.Security.Cryptography.SHA256]::Create()\\n$hashBytes=$sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($projectRoot))\\n$hash=([System.BitConverter]::ToString($hashBytes) -replace "-", "").Substring(0,8).ToLowerInvariant()\\n\\n# このプロジェクト用の仮想環境をユーザーフォルダ配下に配置する\\n$env:UV_PROJECT_ENVIRONMENT="$env:USERPROFILE\\.uv\\venvs\\$projectName-$hash"\\n\\n# 設定された仮想環境の場所を確認する\\necho $env:UV_PROJECT_ENVIRONMENT\\n\\n# 指定した場所に仮想環境を作成・同期する\\nuv sync')}
        <aside class="callout callout-warning"><code>UV_PROJECT_ENVIRONMENT</code> に固定の絶対パスを指定して複数プロジェクトで使い回すと、仮想環境の内容が上書きされる可能性があります。社内手順では、プロジェクト名とパス由来ハッシュを含むパスを使います。</aside>
        <p><code>UV_PROJECT_ENVIRONMENT</code> はプロジェクトごとに異なる値を指定する必要があります。そのため、Windows のユーザー環境変数として永続化する運用は標準にはしません。プロジェクトごとの作業開始手順またはセットアップスクリプトで、この PowerShell セッションに設定します。</p>
      </section>
      <section id="extras-markers-sources" data-toc data-toc-title="extras・markers・特殊な依存">
        <h2>extras・markers・特殊な依存</h2>
        <h3 id="extras" data-toc data-toc-level="3" data-toc-title="extras">extras</h3>
        <p>extras は、パッケージが提供する追加依存をまとめて入れる指定です。例: <code>fastapi[standard]</code>、<code>requests[socks]</code>。</p>
        {code("powershell", 'uv add "fastapi[standard]>=0.115"')}
        <h3 id="environment-markers" data-toc data-toc-level="3" data-toc-title="environment markers">environment markers</h3>
        <p>OS や Python バージョンで依存を分ける場合は environment marker を使います。</p>
        {code("toml", 'dependencies = [\\n    "pywin32>=306; sys_platform == \\"win32\\"",\\n    "tomli>=2; python_version < \\"3.11\\"",\\n]')}
        <h3 id="direct-url-git-path" data-toc data-toc-level="3" data-toc-title="direct URL / Git / path">direct URL / Git / path</h3>
        <p>通常の社内開発では package index からの依存を優先します。Git、URL、path 依存は再現性、認証、監査、ライセンス確認が難しくなるため、必要な場合だけ使います。</p>
        {code("powershell", 'uv add "my-package @ git+https://github.com/example/my-package.git@v1.2.3"\\nuv add "my-lib @ file:///${PWD}/libs/my-lib"')}
        <aside class="callout callout-warning">Git や path 依存を使う場合は、参照先、タグまたは commit、認証方式、CI で取得できることを必ず確認します。社内標準では private package repository へ配布してから通常依存として追加する方がレビューしやすいです。</aside>
      </section>
      <section id="python-management" data-toc data-toc-title="Python の管理">
        <h2>Python の管理</h2>
        {code("powershell", "uv python list\\nuv python install 3.12\\nuv python pin 3.12\\nuv run python --version")}
        <aside class="callout callout-warning">uv は通常、管理対象 Python として python-build-standalone の配布物を利用します。pyenv のように任意の全バージョンをソースビルドできる前提ではありません。</aside>
      </section>
"""

start_project_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、uv を使って新規 Python プロジェクトを作成し、Python バージョン固定、依存追加、lock file 作成、初回実行まで進めることです。社内ネットワーク配下では、必要に応じて proxy と証明書設定を行ってから作業します。</p>
      </section>
      <section id="prerequisites" data-toc data-toc-title="前提を確認する">
        <h2>前提を確認する</h2>
        <ul>
          <li>uv がインストール済みであること。</li>
          <li>社内 proxy や SSL inspection が必要な端末では、ネットワーク設定を行えること。</li>
          <li>プロジェクトで利用する Python バージョンが決まっていること。</li>
        </ul>
      </section>
      <section id="network-session-settings" data-toc data-toc-title="ネットワーク設定を適用する">
        <h2>ネットワーク設定を適用する</h2>
        <p>この PowerShell セッションだけで作業する場合は、proxy と証明書設定をセッションに設定してから uv コマンドを実行します。</p>
        {code("powershell", '# proxy をこの PowerShell セッションに設定する\\n$env:HTTP_PROXY="http://proxy.example.co.jp:8080"\\n$env:HTTPS_PROXY="http://proxy.example.co.jp:8080"\\n\\n# OS の証明書ストアをこの PowerShell セッションで利用する\\n$env:UV_SYSTEM_CERTS="1"\\n\\n# 設定された値を確認する\\necho $env:HTTP_PROXY\\necho $env:HTTPS_PROXY\\necho $env:UV_SYSTEM_CERTS')}
      </section>
      <section id="create-project" data-toc data-toc-title="プロジェクトを作成する">
        <h2>プロジェクトを作成する</h2>
        <p><code>uv init フォルダ名</code> を実行すると、現在のフォルダの下に新しいプロジェクトフォルダが作成されます。<code>$projectName</code> には実際のプロジェクト名を設定します。<code>C:&#92;path&#92;to&#92;your&#92;project-parent-folder</code> は例であり、プロジェクトを配置する親フォルダのパスに置き換えます。</p>
        <p>共有フォルダ上で作業する場合は、<code>uv add</code> や <code>uv sync</code> の前に <code>UV_PROJECT_ENVIRONMENT</code> を設定します。仮想環境名をプロジェクト名だけで決めると、別の場所にある同名プロジェクトと衝突する可能性があるため、プロジェクトの保存場所から作った短いハッシュを末尾に付けます。</p>
        {code("powershell", '# プロジェクト名を設定する\\n$projectName="my-app"\\n\\n# プロジェクトを配置する親フォルダへ移動する\\ncd C:\\path\\to\\your\\project-parent-folder\\n\\n# 現在のフォルダの下にプロジェクトを作成する\\nuv init $projectName\\n\\n# 作成されたプロジェクトフォルダへ移動する\\ncd $projectName\\n\\n# 同じプロジェクト名の仮想環境と衝突しないように、\\n# プロジェクトの保存場所をもとに短いハッシュを作る\\n$projectRoot=(Resolve-Path .).Path.ToLowerInvariant()\\n$sha256=[System.Security.Cryptography.SHA256]::Create()\\n$hashBytes=$sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($projectRoot))\\n$hash=([System.BitConverter]::ToString($hashBytes) -replace "-", "").Substring(0,8).ToLowerInvariant()\\n\\n# 仮想環境の作成先を、このプロジェクト用のローカルフォルダに設定する\\n$env:UV_PROJECT_ENVIRONMENT="$env:USERPROFILE\\.uv\\venvs\\$projectName-$hash"\\n\\n# 設定された仮想環境の場所を確認する\\necho $env:UV_PROJECT_ENVIRONMENT\\n\\n# プロジェクトで使う Python バージョンを固定する\\nuv python pin 3.12')}
        <p>以下のコマンドは、プロジェクト内のファイルや仮想環境を作成・更新します。レビュー時は、どのファイルが作成され、どのファイルが更新されたかを確認します。</p>
        {project_command_effects_table()}
      </section>
      <section id="add-dependencies" data-toc data-toc-title="依存関係を追加する">
        <h2>依存関係を追加する</h2>
        {code("powershell", 'uv add requests\\nuv add --dev pytest ruff')}
      </section>
      <section id="first-run" data-toc data-toc-title="初回実行する">
        <h2>初回実行する</h2>
        {code("powershell", 'uv lock\\nuv sync\\nuv run python --version\\nuv run pytest')}
      </section>
      <section id="commit-targets" data-toc data-toc-title="コミット対象を確認する">
        <h2>コミット対象を確認する</h2>
        <p>通常は <code>pyproject.toml</code>、<code>uv.lock</code>、<code>.python-version</code> をコミット対象にします。<code>.venv</code> は各端末で再生成するためコミットしません。</p>
      </section>
"""

copy_existing_project_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、uv 対応済みの既存プロジェクトを clone またはコピーし、手元の端末で同期して動作確認することです。既存の <code>uv.lock</code> を尊重し、意図しない依存更新を避けながら環境を再現します。</p>
      </section>
      <section id="copy-or-clone" data-toc data-toc-title="プロジェクトを取得する">
        <h2>プロジェクトを取得する</h2>
        {code("powershell", 'git clone https://github.com/example/my-app.git\\ncd my-app')}
        <aside class="callout callout-info">フォルダをコピーして始める場合も、<code>.venv</code> はコピーせず、手元で <code>uv sync</code> により再生成します。</aside>
      </section>
      <section id="network-session-settings" data-toc data-toc-title="ネットワーク設定を適用する">
        <h2>ネットワーク設定を適用する</h2>
        <p>依存パッケージ取得時に社内 proxy や社内 CA が必要な場合は、同期前にこの PowerShell セッションへ設定します。</p>
        {code("powershell", '# proxy をこの PowerShell セッションに設定する\\n$env:HTTP_PROXY="http://proxy.example.co.jp:8080"\\n$env:HTTPS_PROXY="http://proxy.example.co.jp:8080"\\n\\n# OS の証明書ストアをこの PowerShell セッションで利用する\\n$env:UV_SYSTEM_CERTS="1"\\n\\n# 設定された値を確認する\\necho $env:HTTP_PROXY\\necho $env:HTTPS_PROXY\\necho $env:UV_SYSTEM_CERTS')}
      </section>
      <section id="check-python-version" data-toc data-toc-title="Python バージョン指定を確認する">
        <h2>Python バージョン指定を確認する</h2>
        <p><code>.python-version</code> と <code>pyproject.toml</code> の <code>requires-python</code> を確認し、プロジェクトが想定する Python バージョンで同期します。</p>
        {code("powershell", 'Get-Content .python-version\\nSelect-String -Path pyproject.toml -Pattern "requires-python"')}
      </section>
      <section id="sync-environment" data-toc data-toc-title="環境を同期する">
        <h2>環境を同期する</h2>
        <p>既存の lock file を使って環境を再現します。通常の利用開始時は lock file を更新しません。</p>
        {code("powershell", 'uv sync --locked')}
      </section>
      <section id="verify-project" data-toc data-toc-title="動作確認する">
        <h2>動作確認する</h2>
        {code("powershell", 'uv run python --version\\nuv run pytest')}
      </section>
      <section id="lock-file-policy" data-toc data-toc-title="lock file 更新の扱い">
        <h2>lock file 更新の扱い</h2>
        <p>利用開始だけが目的の場合は <code>uv.lock</code> を更新しません。依存追加やバージョン更新が目的の場合だけ、変更理由を明確にして lock file を更新します。</p>
      </section>
"""

migration_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、Poetry + pyenv を前提にした既存プロジェクトを uv ベースの運用へ移行する手順と判断点を整理することです。単にコマンドを置き換えるのではなく、Python バージョン、仮想環境、依存解決、lock file、CI の扱いを揃えることを目的にします。</p>
      </section>
      <section id="migration-goal" data-toc data-toc-title="移行のゴール">
        <h2>移行のゴール</h2>
        <p>Poetry + pyenv から uv へ移行する目的は、単にコマンド名を置き換えることではありません。Python バージョン、仮想環境、依存解決、lock file、CI の実行手順を uv に揃え、開発者ごとの環境差分を減らすことがゴールです。</p>
        <aside class="callout callout-warning">移行 PR では、<code>poetry.lock</code> から <code>uv.lock</code> へ lock file が変わるため差分が大きくなります。依存追加や大きなバージョン更新とは別 PR に分け、移行そのものの差分をレビューしやすくします。</aside>
      </section>
      <section id="command-mapping" data-toc data-toc-title="コマンド対応表">
        <h2>コマンド対応表</h2>
        {table(["現在", "uv", "補足"], [
            ["<code>pyenv install 3.11.9</code>", "<code>uv python install 3.11.9</code>", "uv で利用できる Python バージョンに限る。"],
            ["<code>pyenv local 3.11.9</code>", "<code>uv python pin 3.11.9</code>", "<code>.python-version</code> を作成または更新する。"],
            ["<code>poetry init</code>", "<code>uv init</code>", "既存プロジェクトでは上書きに注意する。"],
            ["<code>poetry add requests</code>", "<code>uv add requests</code>", "<code>pyproject.toml</code> と <code>uv.lock</code> を更新する。"],
            ["<code>poetry add --group dev pytest</code>", "<code>uv add --dev pytest</code>", "開発用依存として追加する。"],
            ["<code>poetry install</code>", "<code>uv sync</code>", "lock file に合わせて仮想環境を作る。"],
            ["<code>poetry run pytest</code>", "<code>uv run pytest</code>", "プロジェクト環境で実行する。"],
            ["<code>poetry lock</code>", "<code>uv lock</code>", "<code>poetry.lock</code> ではなく <code>uv.lock</code> を生成する。"],
            ["<code>poetry env info</code>", "<code>uv run python -c ...</code>", "必要なら <code>sys.executable</code> や <code>sys.version</code> を確認する。"],
        ])}
      </section>
      <section id="pre-migration-inventory" data-toc data-toc-title="事前調査">
        <h2>事前調査</h2>
        <p>最初に、現在のプロジェクトが Poetry と pyenv にどの程度依存しているかを確認します。この段階ではまだ lock file を更新しません。</p>
        <ol>
          <li><code>.python-version</code>、CI、Dockerfile、README に書かれている Python バージョンを確認する。</li>
          <li><code>pyproject.toml</code> の <code>[tool.poetry]</code>、依存関係、dev group、scripts、package 設定を確認する。</li>
          <li><code>poetry.lock</code> が最新か、現在の CI が <code>poetry install</code> で通っているか確認する。</li>
          <li>Poetry plugin、private index、認証、社内 CA、proxy 設定の有無を確認する。</li>
          <li><code>poetry</code>、<code>pyenv</code>、<code>poetry.lock</code>、<code>POETRY_</code> をリポジトリ内で検索する。</li>
        </ol>
        {code("powershell", "uv --version\\npoetry --version\\npython --version\\nGet-ChildItem -Recurse -File | Select-String -Pattern 'poetry|pyenv|POETRY_|poetry.lock'")}
      </section>
      <section id="migration-policy" data-toc data-toc-title="移行方針を決める">
        <h2>移行方針を決める</h2>
        <p>手を動かす前に、移行後の標準を明確にします。ここが曖昧だと、ローカルでは動いても CI や他メンバーの環境で差分が出ます。</p>
        <ul>
          <li>Python バージョンは既存の <code>.python-version</code> を維持するか、移行と同時に変更するか。</li>
          <li>uv 本体の標準バージョンを何にするか。</li>
          <li><code>uv.lock</code> をコミット対象にするか。アプリケーション開発では原則コミットする。</li>
          <li>依存解決時の <code>--exclude-newer "X days"</code> を標準にするか。</li>
          <li>private index を <code>pyproject.toml</code> に書くか、ユーザー / CI の uv 設定に置くか。</li>
          <li>Poetry 固有の package 設定や scripts を uv / PEP 621 形式へ移す範囲。</li>
        </ul>
      </section>
      <section id="local-migration" data-toc data-toc-title="ローカルで移行する">
        <h2>ローカルで移行する</h2>
        <p>移行作業は専用ブランチで行います。まず uv で Python を固定し、lock file を作り、テストが通るところまで確認します。</p>
        {code("powershell", 'git switch -c migrate-to-uv\\nuv python pin 3.12\\nuv lock --exclude-newer "7 days"\\nuv sync\\nuv run python --version\\nuv run pytest')}
        <aside class="callout callout-warning"><code>uv lock</code> は <code>poetry.lock</code> をそのまま変換するコマンドではありません。<code>pyproject.toml</code> の依存定義から uv が新しく解決し、<code>uv.lock</code> を生成します。</aside>
      </section>
      <section id="pyproject-adjustments" data-toc data-toc-title="pyproject.toml を調整する">
        <h2>pyproject.toml を調整する</h2>
        <p>Poetry だけが読む設定と、PEP 621 / uv が読む設定を分けて確認します。既存の <code>[tool.ruff]</code>、<code>[tool.pytest.ini_options]</code>、<code>[tool.mypy]</code> などのツール設定は基本的にそのまま維持します。</p>
        <ul>
          <li><code>[project]</code> の <code>requires-python</code> が実際の Python バージョンと合っているか確認する。</li>
          <li>runtime dependency と dev dependency が正しいグループに入っているか確認する。</li>
          <li>Poetry の scripts を使っている場合、<code>[project.scripts]</code> へ移せるか確認する。</li>
          <li>private index の URL に認証情報を直接書いていないか確認する。</li>
          <li>パッケージとして配布しないアプリケーションなら、build 設定が不要か確認する。</li>
        </ul>
        <p>Poetry では <code>[tool.poetry.dependencies]</code> に TOML テーブル形式で依存を書くことがありますが、uv では通常 <code>[project].dependencies</code> に PEP 508 文字列として記録します。Poetry の <code>^2.2</code> のような caret requirement は、<code>&gt;=2.2,&lt;3</code> のように範囲指定へ展開します。依存追加は <code>uv add "pandas&gt;=2.2,&lt;3"</code> のように行い、記法の詳細は <a href="usage.html#pyproject-dependency-notation">pyproject.toml のライブラリ記法</a> と <a href="usage.html#poetry-caret-notation">Poetry の ^ 記法との対応</a> を参照します。</p>
        {table(["Poetry 形式の例", "uv / PEP 621 形式の例"], [
            ['<code>pandas = "^2.2"</code>', '<code>"pandas&gt;=2.2,&lt;3"</code>'],
            ['<code>python = "&gt;=3.11,&lt;3.13"</code>', '<code>requires-python = "&gt;=3.11,&lt;3.13"</code>'],
            ['<code>pytest = &#123; group = "dev", version = "^8" &#125;</code>', '<code>[dependency-groups].dev = ["pytest&gt;=8"]</code>'],
            ['<code>fastapi = &#123; extras = ["standard"], version = "^0.115" &#125;</code>', '<code>"fastapi[standard]&gt;=0.115"</code>'],
        ])}
      </section>
      <section id="verification" data-toc data-toc-title="動作確認する">
        <h2>動作確認する</h2>
        <p>Poetry で実行していたチェックを uv 経由に置き換え、同じ結果になるか確認します。</p>
        {code("powershell", "uv sync --locked\\nuv run pytest\\nuv run ruff check .\\nuv run python -m pip check\\nuv tree")}
        <p>確認すべき観点:</p>
        <ul>
          <li>テスト結果が Poetry 環境と一致するか。</li>
          <li>CLI entry point やアプリ起動コマンドが動くか。</li>
          <li>Jupyter、pre-commit、IDE の interpreter 設定が <code>.venv</code> を参照できるか。</li>
          <li>proxy / SSL / private index が CI とローカルで同じように通るか。</li>
        </ul>
      </section>
      <section id="ci-and-docker" data-toc data-toc-title="CI / Docker を更新する">
        <h2>CI / Docker を更新する</h2>
        <p>CI では lock file を勝手に更新させないため、<code>uv sync --locked</code> を使います。社内 proxy や証明書が必要な場合は、ジョブ環境変数として <code>HTTP_PROXY</code>、<code>HTTPS_PROXY</code>、<code>UV_SYSTEM_CERTS</code> を設定します。</p>
        {code("yaml", '- name: Install uv\\n  uses: astral-sh/setup-uv@v5\\n  with:\\n    version: "0.11.8"\\n\\n- name: Install Python\\n  run: uv python install\\n\\n- name: Sync dependencies\\n  run: uv sync --locked\\n\\n- name: Run tests\\n  run: uv run pytest')}
        <p>Dockerfile がある場合は、<code>poetry install</code>、<code>poetry export</code>、<code>pip install -r requirements.txt</code> のどれを使っているかを確認し、uv の sync / export に置き換えます。</p>
      </section>
      <section id="cleanup" data-toc data-toc-title="Poetry / pyenv 前提を整理する">
        <h2>Poetry / pyenv 前提を整理する</h2>
        <p>テストと CI が通った後で、古い前提を整理します。先に消すと原因切り分けが難しくなるため、検証後に行います。</p>
        <ul>
          <li><code>poetry.lock</code> を削除し、<code>uv.lock</code> を追加する。</li>
          <li>README の <code>poetry install</code>、<code>poetry run</code>、<code>pyenv install</code> を uv コマンドに置き換える。</li>
          <li>CI、Dockerfile、pre-commit、開発者向けセットアップ手順から Poetry 前提を除く。</li>
          <li><code>.python-version</code> は uv でも使うため、必要なら維持する。</li>
          <li>Poetry を完全に不要にするか、配布用途だけ残すかを明記する。</li>
        </ul>
      </section>
      <section id="review-checklist" data-toc data-toc-title="レビュー観点">
        <h2>レビュー観点</h2>
        <ul>
          <li><code>pyproject.toml</code> の依存定義が意図せず変わっていないか。</li>
          <li><code>uv.lock</code> の差分が移行目的に対して妥当か。</li>
          <li>Python バージョンが CI、ローカル、Docker で一致しているか。</li>
          <li>proxy / SSL / private index の設定に認証情報が混入していないか。</li>
          <li>README の手順だけで新規開発者が環境構築できるか。</li>
          <li>移行 PR に機能追加や依存の大幅更新が混ざっていないか。</li>
        </ul>
      </section>
"""

security_body = f"""
      <section class="chapter-intro" aria-label="このページの目的">
        <h2>ページ概要</h2>
        <p>このページの目的は、uv で依存関係を管理するプロジェクトに対して、脆弱性監査、ライセンス確認、依存追加時レビューをどのように組み込むかを整理することです。監査ツールの導入例と、CI やレビューで確認する観点を扱います。</p>
      </section>
      <section id="minimum-checks" data-toc data-toc-title="最低限入れるチェック">
        <h2>最低限入れるチェック</h2>
        {table(["項目", "ツール例", "目的"], [
            ["脆弱性監査", "<code>pip-audit</code>", "既知 CVE や advisories の検出。"],
            ["ライセンス監査", "<code>pip-licenses</code>", "利用不可ライセンスや不明ライセンスの検出。"],
            ["静的解析", "<code>ruff</code>, <code>mypy</code>", "品質と型の回帰検出。"],
        ])}
      </section>
      <section id="pip-audit" data-toc data-toc-title="pip-audit">
        <h2>pip-audit</h2>
        {code("powershell", "uv add --dev pip-audit\\nuv sync --locked\\nuv run pip-audit")}
      </section>
      <section id="pip-licenses" data-toc data-toc-title="pip-licenses">
        <h2>pip-licenses</h2>
        {code("powershell", "uv add --dev pip-licenses\\nuv run pip-licenses --format=markdown --output-file=licenses.md")}
      </section>
      <section id="dependency-review" data-toc data-toc-title="依存追加時のレビュー観点">
        <h2>依存追加時のレビュー観点</h2>
        <ul>
          <li>依存名が社内標準や既存依存と重複・類似していないか。</li>
          <li>typosquatting らしい名前ではないか。</li>
          <li>公開直後のパッケージや、メンテナ変更直後のパッケージではないか。</li>
          <li><code>uv.lock</code> の差分が依存追加の目的に対して妥当か。</li>
        </ul>
      </section>
"""

BODIES = [
    index_body,
    install_body,
    setup_body,
    usage_body,
    start_project_body,
    copy_existing_project_body,
    migration_body,
    security_body,
]

numbered_bodies = [apply_heading_numbering(body) for body in BODIES]
toc_entries_by_page = [extract_toc_entries(body) for body in numbered_bodies]

for idx, ((filename, _, title), body) in enumerate(zip(PAGES, numbered_bodies)):
    content = page_header(title, PAGE_SUMMARIES[idx]) + "\n" + body
    (OUT / filename).write_text(shell(title, content, idx, toc_entries_by_page), encoding="utf-8")
