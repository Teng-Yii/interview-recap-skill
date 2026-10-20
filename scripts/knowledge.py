#!/usr/bin/env python3
"""Read explicitly configured local files, Yuque MCP documents, or Feishu CLI docs."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

READ_TOOLS = {'yuque_get_doc', 'yuque_get_document'}
PURPOSES = {'personal_facts', 'reference'}
MAX_CHARS = 40000


def read_file(path):
    path = Path(path)
    if path.stat().st_size > 8_000_000:
        raise ValueError('Context file exceeds 8MB; provide a relevant excerpt')
    if path.suffix.lower() in {'.txt', '.md', '.markdown'}:
        return path.read_text(encoding='utf-8-sig')
    if path.suffix.lower() == '.docx':
        import zipfile
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(path) as z:
            if z.getinfo('word/document.xml').file_size > 8_000_000:
                raise ValueError('DOCX content exceeds 8MB')
            root = ET.fromstring(z.read('word/document.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        return '\n'.join(''.join(p.itertext()) for p in root.findall('.//w:p', ns))
    raise ValueError('Supported context formats: .txt, .md, .docx. Export PDF to text first.')


def validate_mcp_call(tool, arguments):
    if tool not in READ_TOOLS:
        raise ValueError('Only document-read tools are allowed; use the native MCP client for other read tools.')
    if not isinstance(arguments, dict):
        raise ValueError('MCP arguments must be an object')


def _extract_body(value):
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = None
        return _extract_body(decoded) if isinstance(decoded, dict) else value
    if not isinstance(value, dict):
        raise ValueError('Unsupported document response')
    if value.get('error') or value.get('ok') is False or value.get('success') is False:
        raise ValueError('Document provider reported an error')
    if value.get('code') not in (None, 0, '0'):
        raise ValueError('Document provider reported a nonzero code')
    for key in ('body', 'body_markdown', 'markdown', 'content'):
        if isinstance(value.get(key), str) and value[key].strip():
            return value[key]
    for key in ('data', 'document', 'result'):
        if key in value:
            try:
                return _extract_body(value[key])
            except ValueError:
                pass
    raise ValueError('No document body returned')


def parse_cli_document(stdout):
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError('Expected official lark-cli JSON output') from exc
    return _extract_body(value)


def parse_mcp_document(result):
    if result.get('isError'):
        raise ValueError('MCP tool returned an error')
    if result.get('structuredContent'):
        return _extract_body(result['structuredContent'])
    texts = [c['text'] for c in result.get('content', []) if c.get('type') == 'text' and c.get('text')]
    if not texts:
        raise ValueError('MCP returned no text')
    bodies = []
    for text in texts:
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            value = text
        bodies.append(_extract_body(value))
    return '\n\n'.join(bodies)


async def _mcp_session(source, probe=False):
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise ValueError('Install optional MCP dependencies: pip install -r requirements-mcp.txt') from exc
    env = dict(os.environ)
    for key, variable in source.get('env_vars', {}).items():
        if not isinstance(variable, str) or variable not in os.environ:
            raise ValueError('A configured MCP environment variable is missing')
        env[key] = os.environ[variable]
    args = source.get('args', [])
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise ValueError('MCP args must be a list of strings')
    params = StdioServerParameters(command=source.get('command', 'npx'), args=args, env=env)
    with open(os.devnull, 'w') as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = []
                cursor = None
                while True:
                    response = await session.list_tools(cursor=cursor)
                    tools.extend(response.tools)
                    cursor = response.nextCursor
                    if not cursor:
                        break
                if probe:
                    return [{'name': t.name, 'inputSchema': t.inputSchema} for t in tools if t.name in READ_TOOLS]
                tool = source.get('tool', 'yuque_get_doc')
                arguments = source.get('arguments', {})
                validate_mcp_call(tool, arguments)
                if tool not in {t.name for t in tools}:
                    raise ValueError('Configured document-read tool is not advertised by the MCP server')
                result = await session.call_tool(tool, arguments)
                return parse_mcp_document(result.model_dump(by_alias=True, exclude_none=True))


def mcp_read(source, probe=False):
    timeout = max(1, min(float(source.get('timeout_seconds', 60)), 180))
    return asyncio.run(asyncio.wait_for(_mcp_session(source, probe), timeout))


def feishu_read(source):
    doc = source.get('doc', '')
    if not isinstance(doc, str) or not doc or doc.startswith('-'):
        raise ValueError('Feishu document URL or token is required')
    # No shell, arbitrary subcommands, or CLI arguments are accepted from document text.
    identity = source.get('identity', 'user')
    if identity not in {'user', 'bot'}:
        raise ValueError('Feishu identity must be user or bot')
    argv = [source.get('command', 'lark-cli'), 'docs', '+fetch', '--doc', doc, '--doc-format', 'markdown', '--as', identity]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=max(1, min(float(source.get('timeout_seconds', 60)), 180)))
    if result.returncode:
        raise ValueError('Feishu CLI failed; check local login, document permission and docs +fetch --help')
    return parse_cli_document(result.stdout)


def collect(config, base_dir):
    sources = config.get('sources', [])
    if not isinstance(sources, list) or len(sources) > 10:
        raise ValueError('sources must be an array of at most 10 explicitly selected documents')
    docs, warnings = [], []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError('Each source must be an object')
        if source.get('enabled') is False:
            continue
        kind = source.get('type')
        purpose = source.get('purpose', 'reference')
        if purpose not in PURPOSES:
            raise ValueError('purpose must be personal_facts or reference')
        try:
            if kind == 'local':
                path = (Path(base_dir) / source['path']).resolve()
                text, locator = read_file(path), source['path']
            elif kind == 'mcp':
                validate_mcp_call(source.get('tool', 'yuque_get_doc'), source.get('arguments', {}))
                text = mcp_read(source)
                # Store the selected doc locator, never the connection command, env or token.
                locator = source.get('url') or json.dumps(source.get('arguments', {}), ensure_ascii=False, sort_keys=True)
            elif kind == 'feishu_cli':
                text, locator = feishu_read(source), source.get('doc')
            else:
                raise ValueError('Unknown source type')
            if not text.strip():
                raise ValueError('Document is empty')
            docs.append({'id': f'K{index+1:03}', 'provider': kind, 'purpose': purpose, 'title': str(source.get('title', f'Selected document {index+1}')), 'locator': locator, 'text': text[:MAX_CHARS], 'truncated': len(text) > MAX_CHARS})
        except Exception as exc:
            # Do not serialize provider output, env, command lines or exception messages: these may contain secrets.
            warnings.append({'source_index': index+1, 'provider': kind, 'status': 'unavailable', 'reason': type(exc).__name__, 'action': 'Check this source locally; review can continue without it.'})
    return docs, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--probe', action='store_true', help='List allowed document-read MCP tool schemas, without reading any document')
    parser.add_argument('--output', help='Private context output JSON; refuses to overwrite')
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text())
    if args.probe:
        result = []
        for s in config.get('sources', []):
            if s.get('type') == 'mcp' and s.get('enabled') is not False:
                result.extend(mcp_read(s, probe=True))
    else:
        docs, warnings = collect(config, config_path.parent)
        result = {'references': docs, 'warnings': warnings}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(output+'\n')
        print(json.dumps({'saved': args.output, 'references': len(result.get('references', [])) if isinstance(result, dict) else len(result)}, ensure_ascii=False))
    else:
        print(output)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Knowledge read failed ({type(exc).__name__}). Check config, optional dependencies and provider login locally.', file=sys.stderr)
        sys.exit(1)
