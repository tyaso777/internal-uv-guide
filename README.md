# 社内 uv 利用ガイド

社内 Python 開発環境を uv ベースで導入・移行・運用するためのガイドです。

## Contents

- [概要](chapters/index.html)
- [インストール](chapters/install.html)
- [ネットワーク設定の基本](chapters/setup.html)
- [基本操作と概念](chapters/usage.html)
- [新規 uv プロジェクトの始め方](chapters/start-project.html)
- [clone・コピーした uv プロジェクトの始め方](chapters/copy-existing-project.html)
- [Poetry + pyenv からの移行](chapters/migration.html)
- [セキュリティ運用](chapters/security.html)

## Template

This document uses assets from [tyaso777/html-doc-template](https://github.com/tyaso777/html-doc-template).

## Generate

このリポジトリでは、`chapters-src/` を編集用の正本とし、テンプレート標準の build script で公開用 HTML を生成します。

```powershell
python scripts\build_site.py
python scripts\check_html.py
```
