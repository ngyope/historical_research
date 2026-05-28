"""
build.py — Histographia データビルダー
yaml/ 以下の YAML ファイルから data_sample.js / sources.js を再生成する。

実行方法:
  cd Histographia/Data
  python build.py
"""
from pathlib import Path

BASE = Path(__file__).parent

CHAPTER_HEADER = (
    "// ⚠ 自動生成ファイル — 直接編集しないこと。\n"
    "// 編集は yaml/ 以下のファイルを変更し、python Data/build.py を実行すること。\n"
    "// インタラクティブ歴史学習アプリの chapter データ。\n"
    "// 本体はYAMLテキスト。index.html がこのファイルを <script src> で読み込む。\n"
    "// （file:// で開く際の fetch 制約を避けるための薄いラッパ）\n"
    "// chapter 間の繋がりは各 chapter の links フィールドで直接定義する (双方向リンクとして扱われる)。\n"
    "window.HISTORY_CHAPTERS = String.raw`\n"
    "chapters:\n"
)
SOURCE_HEADER = (
    "// ⚠ 自動生成ファイル — 直接編集しないこと。\n"
    "// 編集は yaml/ 以下のファイルを変更し、python Data/build.py を実行すること。\n"
    "// インタラクティブ歴史学習アプリの source データ (atomic)。\n"
    "// 本体はYAMLテキスト。index.html がこのファイルを <script src> で読み込む。\n"
    "// （file:// で開く際の fetch 制約を避けるための薄いラッパ）\n"
    "// chapter 間の繋がり (next 関係) と階層 (M/S) は Data/themes.js で定義する。\n"
    "window.HISTORY_SOURCES = String.raw`\n"
    "sources:\n"
)
FOOTER = "\n`;\n"


def extract_body(yaml_file, top_key):
    """YAML ファイルからトップレベルキー行を除いたリスト部分を返す。"""
    text = yaml_file.read_text(encoding='utf-8')
    marker = f'{top_key}:\n'
    idx = text.find(marker)
    if idx == -1:
        raise ValueError(f'{yaml_file.name}: "{marker.strip()}" が見つかりません')
    body = text[idx + len(marker):]
    # 先頭の空行を除去してエントリが直接始まるようにする
    return body.lstrip('\n')


def build_js(yaml_dir, top_key, header, out_file):
    yaml_files = sorted(yaml_dir.glob('*.yaml'))
    if not yaml_files:
        raise FileNotFoundError(f'{yaml_dir} に *.yaml ファイルがありません')

    parts = []
    item_count = 0
    for f in yaml_files:
        body = extract_body(f, top_key)
        parts.append(body)
        item_count += body.count('\n  - id: ') + (1 if body.startswith('  - id: ') else 0)

    combined = '\n'.join(parts)
    # 末尾の余分な空行を1行に整理
    combined = combined.rstrip('\n')

    content = header + combined + FOOTER
    out_file.write_text(content, encoding='utf-8')
    return len(yaml_files), item_count


def build():
    chapters_dir = BASE / 'yaml' / 'chapters'
    sources_dir = BASE / 'yaml' / 'sources'

    n_files, n_items = build_js(
        chapters_dir, 'chapters', CHAPTER_HEADER, BASE / 'data_sample.js'
    )
    print(f'chapters: {n_files} ファイル / {n_items} 件 → data_sample.js')

    n_files, n_items = build_js(
        sources_dir, 'sources', SOURCE_HEADER, BASE / 'sources.js'
    )
    print(f'sources : {n_files} ファイル / {n_items} 件 → sources.js')

    print('ビルド完了。')


if __name__ == '__main__':
    build()
