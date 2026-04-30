"""
Research Gatherer — Streamlit Dashboard

Unified UI for the end-to-end research pipeline:
  Phase 1: Search & Collect (research_gatherer.py)
  Phase 2: Parse URLs       (research_gatherer.py / Jina AI)
  Phase 3: Image Gathering  (image_gatherer.py)
  Phase 4: Reconstruct      (content_reconstructor.py)
  Phase 5: Browse & Export  (filesystem viewer + ZIP download)

Run:
  streamlit run app.py
"""

# ---------------------------------------------------------------------------
# Path setup — must precede any local imports
# ---------------------------------------------------------------------------
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in (_ROOT,
           os.path.join(_ROOT, 'utils'),
           os.path.join(_ROOT, 'engines'),
           os.path.join(_ROOT, 'engines_image'),
           os.path.join(_ROOT, 'libs')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Standard-library & third-party imports
# ---------------------------------------------------------------------------
import io
import logging
import queue
import re
import threading
import time
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from app_logger import QueueHandler, attach_queue_handler, detach_queue_handler, drain_queue

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title='Research Gatherer',
    page_icon='🔬',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PHASES = [
    'Phase 1: Search & Collect',
    'Phase 2: Parse URLs',
    'Phase 3: Image Gathering',
    'Phase 4: Reconstruct',
    'Phase 5: Browse & Export',
]

RECONSTRUCT_FORMAT_OPTIONS = [
    'Summary Report',
    'By Domain',
    'By Category',
    'Curated Essentials',
]

_FORMAT_METHOD_MAP = {
    'Summary Report':    ('export_summary_report',   'SUMMARY.md'),
    'By Domain':         ('export_by_domain',         'BY_DOMAIN.md'),
    'By Category':       ('export_by_category',       'BY_CATEGORY.md'),
    'Curated Essentials':('export_curated_essentials','CURATED_ESSENTIALS.md'),
}

POLL_INTERVAL = 0.4   # seconds between log polls while task runs
LOG_MAX_LINES = 600   # max lines to keep visible in log viewer

# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def _init_task() -> dict:
    return {'thread': None, 'running': False, 'done': False, 'error': None}


def _init_session():
    defaults = {
        # Global config
        'output_dir':   'research_output',
        'debug_mode':   False,
        'active_phase': PHASES[0],
        # Phase 1
        'keywords_text':  '',
        'keywords_list':  [],
        # Phase 2
        'keyword_filter': '',
        # Phase 3
        'image_min_size': 300,
        # Phase 4
        'reconstruct_formats': ['Summary Report', 'Curated Essentials'],
        # Phase 5
        'browser_selected_idx': 0,
        # Task state
        'task_search':    _init_task(),
        'task_parse':     _init_task(),
        'task_images':    _init_task(),
        'task_reconstruct': _init_task(),
        # Log queues — created once and reused across reruns
        'log_queue_search':     queue.Queue(),
        'log_queue_parse':      queue.Queue(),
        'log_queue_images':     queue.Queue(),
        'log_queue_reconstruct': queue.Queue(),
        # Captured log lines
        'logs_search':     [],
        'logs_parse':      [],
        'logs_images':     [],
        'logs_reconstruct': [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session()

# ---------------------------------------------------------------------------
# Metrics helper
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3)
def read_metrics(output_dir: str) -> dict:
    base = Path(output_dir)
    links = 0
    parsed = 0
    domains = 0
    images = 0

    links_file = base / 'collected_links.txt'
    if links_file.exists():
        try:
            links = sum(
                1 for ln in links_file.open(encoding='utf-8', errors='ignore')
                if ln.strip()
            )
        except OSError:
            pass

    parsed_dir = base / 'parsed_content'
    if parsed_dir.exists():
        domain_dirs = [d for d in parsed_dir.iterdir() if d.is_dir()]
        domains = len(domain_dirs)
        parsed = sum(len(list(d.glob('*.md'))) for d in domain_dirs)

    img_dir = base / 'images' / 'downloaded'
    if img_dir.exists():
        images = sum(1 for p in img_dir.rglob('*') if p.is_file())

    return {'links': links, 'parsed': parsed, 'domains': domains, 'images': images}

# ---------------------------------------------------------------------------
# Keyword parsing
# ---------------------------------------------------------------------------

def _parse_keywords_text(text: str) -> List[str]:
    """Split textarea input into sanitized keyword list."""
    # Import sanitize_query lazily (avoids module-level log noise at startup)
    try:
        from research_gatherer import sanitize_query
    except ImportError:
        def sanitize_query(q): return q.strip()

    keywords = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            kw = sanitize_query(line)
            if kw:
                keywords.append(kw)
    return keywords

# ---------------------------------------------------------------------------
# Task guard
# ---------------------------------------------------------------------------

def _can_launch(task_key: str) -> bool:
    task = st.session_state[task_key]
    if task['running']:
        st.warning('A task is already running. Please wait for it to finish.')
        return False
    t = task.get('thread')
    if t is not None and t.is_alive():
        st.warning('Previous task thread is still active.')
        return False
    return True

# ---------------------------------------------------------------------------
# Log viewer component
# ---------------------------------------------------------------------------

def _render_log_viewer(placeholder, log_lines: List[str], max_lines: int = LOG_MAX_LINES):
    if not log_lines:
        placeholder.empty()
        return
    display = log_lines[-max_lines:]
    html_lines = []
    for ln in display:
        safe = ln.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if ' ERROR ' in ln or ' CRITICAL ' in ln:
            color = '#ff4b4b'
        elif ' WARNING ' in ln:
            color = '#ffa500'
        elif ' DEBUG ' in ln:
            color = '#888888'
        else:
            color = '#00dd66'
        html_lines.append(f'<span style="color:{color}">{safe}</span>')

    html = (
        '<div id="log-bottom" style="background:#0e1117;color:#00dd66;'
        'font-family:monospace;font-size:12px;height:380px;overflow-y:auto;'
        'padding:10px 14px;border:1px solid #333;border-radius:6px;'
        'white-space:pre-wrap;word-break:break-all;">'
        + '<br>'.join(html_lines)
        + '</div>'
        # Auto-scroll to bottom
        + '<script>var el=document.getElementById("log-bottom");'
          'if(el){el.scrollTop=el.scrollHeight;}</script>'
    )
    placeholder.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Progress extraction
# ---------------------------------------------------------------------------

def _extract_progress(log_lines: List[str]) -> Tuple[int, int]:
    """Scan recent log lines for '[X/Y]' pattern from existing logger calls."""
    pattern = re.compile(r'\[(\d+)/(\d+)\]')
    for ln in reversed(log_lines[-60:]):
        m = pattern.search(ln)
        if m:
            return int(m.group(1)), int(m.group(2))
    return 0, 0

# ---------------------------------------------------------------------------
# Background task runners
# ---------------------------------------------------------------------------

class _PrintCapture:
    """Redirect sys.stdout → queue for content_reconstructor (uses print())."""
    def __init__(self, q: queue.Queue):
        self._q = q
    def write(self, s: str):
        if s.strip():
            self._q.put_nowait(s.strip())
    def flush(self):
        pass


def _run_search_task(keywords, output_dir, debug, log_queue, task_state):
    handler = attach_queue_handler(log_queue)
    try:
        from research_gatherer import ResearchGatherer
        g = ResearchGatherer(output_dir=output_dir, debug_mode=debug)
        g.search_and_collect(keywords)
        task_state['done'] = True
    except Exception as exc:
        task_state['error'] = str(exc)
        task_state['done'] = True
    finally:
        task_state['running'] = False
        detach_queue_handler(handler)


def _run_parse_task(output_dir, keyword_filter, debug, log_queue, task_state):
    handler = attach_queue_handler(log_queue)
    try:
        from research_gatherer import ResearchGatherer
        g = ResearchGatherer(output_dir=output_dir, debug_mode=debug)
        g.parse_collected_links(keyword_filter=keyword_filter or None)
        g.generate_summary()
        task_state['done'] = True
    except Exception as exc:
        task_state['error'] = str(exc)
        task_state['done'] = True
    finally:
        task_state['running'] = False
        detach_queue_handler(handler)


def _run_images_task(keywords, output_dir, debug, min_size, log_queue, task_state):
    handler = attach_queue_handler(log_queue)
    try:
        from image_gatherer import ImageGatherer
        ig = ImageGatherer(output_dir=output_dir, debug_mode=debug, min_image_size=min_size)
        ig.gather(keywords)
        task_state['done'] = True
    except Exception as exc:
        task_state['error'] = str(exc)
        task_state['done'] = True
    finally:
        task_state['running'] = False
        detach_queue_handler(handler)


def _run_reconstruct_task(output_dir, formats, log_queue, task_state):
    handler = attach_queue_handler(log_queue)
    old_stdout = sys.stdout
    sys.stdout = _PrintCapture(log_queue)
    try:
        from content_reconstructor import ResearchReconstructor
        r = ResearchReconstructor(output_dir)
        r.load_all_content()
        out_dir = Path(output_dir) / 'reconstructed'
        out_dir.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            if fmt in _FORMAT_METHOD_MAP:
                method_name, filename = _FORMAT_METHOD_MAP[fmt]
                getattr(r, method_name)(str(out_dir / filename))
        task_state['done'] = True
    except Exception as exc:
        task_state['error'] = str(exc)
        task_state['done'] = True
    finally:
        sys.stdout = old_stdout
        task_state['running'] = False
        detach_queue_handler(handler)

# ---------------------------------------------------------------------------
# Task launchers
# ---------------------------------------------------------------------------

def _launch(task_key, log_key, logs_key, target_fn, args):
    if not _can_launch(task_key):
        return
    # Reset state and logs
    st.session_state[task_key] = _init_task()
    st.session_state[task_key]['running'] = True
    st.session_state[logs_key] = []
    # Clear old queue messages
    q = st.session_state[log_key]
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break
    t = threading.Thread(
        target=target_fn,
        args=(*args, q, st.session_state[task_key]),
        daemon=True,
    )
    st.session_state[task_key]['thread'] = t
    t.start()

# ---------------------------------------------------------------------------
# Polling loop (runs while task is active)
# ---------------------------------------------------------------------------

def _poll_until_done(task_key: str, log_key: str, logs_key: str,
                     log_placeholder, progress_bar=None):
    """Block the Streamlit script run, polling the queue until the task ends."""
    task = st.session_state[task_key]
    while task['running']:
        st.session_state[logs_key] = drain_queue(
            st.session_state[log_key],
            st.session_state[logs_key],
        )
        _render_log_viewer(log_placeholder, st.session_state[logs_key])
        if progress_bar is not None:
            cur, total = _extract_progress(st.session_state[logs_key])
            if total > 0:
                progress_bar.progress(min(cur / total, 1.0),
                                      text=f'{cur} / {total} URLs')
        time.sleep(POLL_INTERVAL)
    # Final drain
    st.session_state[logs_key] = drain_queue(
        st.session_state[log_key],
        st.session_state[logs_key],
    )
    _render_log_viewer(log_placeholder, st.session_state[logs_key])
    if progress_bar is not None:
        progress_bar.progress(1.0, text='Complete')
    st.rerun()

# ---------------------------------------------------------------------------
# File tree / ZIP helpers
# ---------------------------------------------------------------------------

def _list_output_files(output_dir: str) -> List[Tuple[str, str]]:
    """Return [(display_label, abs_path)] for every file under output_dir."""
    base = Path(output_dir)
    if not base.exists():
        return []
    results = []
    for p in sorted(base.rglob('*')):
        if p.is_file():
            rel = p.relative_to(base)
            indent = '  ' * (len(rel.parts) - 1)
            results.append((indent + p.name, str(p)))
    return results


def _create_zip(output_dir: str) -> bytes:
    buf = io.BytesIO()
    base = Path(output_dir)
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in base.rglob('*'):
            if p.is_file():
                zf.write(p, p.relative_to(base.parent))
    return buf.getvalue()

# ---------------------------------------------------------------------------
# Phase renderers
# ---------------------------------------------------------------------------

def render_phase1():
    st.header('Phase 1: Search & Collect')
    st.caption('Search 14 web engines in parallel and collect result URLs.')

    col1, col2 = st.columns([3, 2], gap='medium')

    with col1:
        keywords_text = st.text_area(
            'Keywords (one per line)',
            value=st.session_state.keywords_text,
            height=220,
            placeholder='machine learning\nnetwork security\nsite:example.com "exact phrase"',
            key='_kw_area',
        )
        st.session_state.keywords_text = keywords_text

    with col2:
        uploaded = st.file_uploader('Or upload a .txt keyword list', type=['txt'])
        if uploaded:
            raw = uploaded.read().decode('utf-8-sig', errors='replace')
            st.session_state.keywords_text = raw
            st.rerun()
        st.info('14 web search engines active\n\nEngines run in parallel threads.')

    kw_list = _parse_keywords_text(st.session_state.keywords_text)
    st.session_state.keywords_list = kw_list

    if kw_list:
        st.caption(f'**{len(kw_list)} keyword(s) parsed:**  ' +
                   '  |  '.join(f'`{k}`' for k in kw_list[:8]) +
                   ('  |  ...' if len(kw_list) > 8 else ''))

    task = st.session_state.task_search
    btn_disabled = task['running'] or not kw_list

    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        if st.button('Start Search', disabled=btn_disabled, type='primary', use_container_width=True):
            _launch(
                'task_search', 'log_queue_search', 'logs_search',
                _run_search_task,
                (kw_list, st.session_state.output_dir, st.session_state.debug_mode),
            )
            st.rerun()

    if task['running'] or task['done'] or task['error']:
        st.divider()
        with st.expander('Search Log', expanded=task['running']):
            log_ph = st.empty()
            _render_log_viewer(log_ph, st.session_state.logs_search)

        if task['running']:
            _poll_until_done('task_search', 'log_queue_search', 'logs_search', log_ph)

        if task['done']:
            if task['error']:
                st.error(f'Search failed: {task["error"]}')
            else:
                m = read_metrics(st.session_state.output_dir)
                st.success(f'Search complete — {m["links"]} unique links collected.')
                if st.button('Proceed to Parse URLs →'):
                    st.session_state.active_phase = PHASES[1]
                    st.rerun()


def render_phase2():
    st.header('Phase 2: Parse URLs')
    st.caption('Convert collected URLs to markdown via Jina AI (r.jina.ai).')

    m = read_metrics(st.session_state.output_dir)
    col1, col2 = st.columns([2, 1], gap='medium')
    with col1:
        st.session_state.keyword_filter = st.text_input(
            'Optional URL keyword filter',
            value=st.session_state.keyword_filter,
            placeholder='e.g. github.com  (leave blank to parse all)',
        )
    with col2:
        st.metric('URLs to parse', m['links'])

    task = st.session_state.task_parse
    btn_disabled = task['running'] or m['links'] == 0

    if st.button('Start Parse', disabled=btn_disabled, type='primary'):
        _launch(
            'task_parse', 'log_queue_parse', 'logs_parse',
            _run_parse_task,
            (st.session_state.output_dir,
             st.session_state.keyword_filter,
             st.session_state.debug_mode),
        )
        st.rerun()

    if task['running'] or task['done'] or task['error']:
        st.divider()
        prog_bar = st.progress(0, text='Waiting for progress...')
        with st.expander('Parse Log', expanded=task['running']):
            log_ph = st.empty()
            _render_log_viewer(log_ph, st.session_state.logs_parse)
            # Sync progress from already-captured lines
            cur, total = _extract_progress(st.session_state.logs_parse)
            if total > 0:
                prog_bar.progress(min(cur / total, 1.0), text=f'{cur} / {total} URLs')

        if task['running']:
            _poll_until_done('task_parse', 'log_queue_parse', 'logs_parse', log_ph, prog_bar)

        if task['done']:
            if task['error']:
                st.error(f'Parse failed: {task["error"]}')
            else:
                m2 = read_metrics(st.session_state.output_dir)
                st.success(f'Parsing complete — {m2["parsed"]} documents across '
                           f'{m2["domains"]} domains.')
                # Show failed URLs if any
                failed_file = Path(st.session_state.output_dir) / 'failed_urls.txt'
                if failed_file.exists():
                    failed = [ln.strip() for ln in failed_file.read_text(encoding='utf-8').splitlines() if ln.strip()]
                    if failed:
                        with st.expander(f'{len(failed)} failed URLs'):
                            st.code('\n'.join(failed))
                if st.button('Proceed to Image Gathering →'):
                    st.session_state.active_phase = PHASES[2]
                    st.rerun()


def render_phase3():
    st.header('Phase 3: Image Gathering')
    st.caption('Search and download presentation-quality images using 4 image engines.')

    col1, col2 = st.columns([2, 1], gap='medium')
    with col1:
        st.session_state.image_min_size = st.number_input(
            'Minimum image dimension (px)',
            min_value=0,
            max_value=4000,
            value=st.session_state.image_min_size,
            step=50,
            help='Set to 0 to download images of any size (includes icons/assets).',
        )
    with col2:
        kw_count = len(st.session_state.keywords_list)
        st.metric('Keywords', kw_count)
        st.info('4 image engines:\nGoogle · Bing · Yahoo · DuckDuckGo')

    kw_list = st.session_state.keywords_list
    task = st.session_state.task_images
    btn_disabled = task['running'] or not kw_list

    if not kw_list:
        st.warning('No keywords defined. Go to Phase 1 and enter keywords first.')

    if st.button('Gather Images', disabled=btn_disabled, type='primary'):
        _launch(
            'task_images', 'log_queue_images', 'logs_images',
            _run_images_task,
            (kw_list,
             st.session_state.output_dir,
             st.session_state.debug_mode,
             st.session_state.image_min_size),
        )
        st.rerun()

    if task['running'] or task['done'] or task['error']:
        st.divider()
        with st.expander('Image Log', expanded=task['running']):
            log_ph = st.empty()
            _render_log_viewer(log_ph, st.session_state.logs_images)

        if task['running']:
            _poll_until_done('task_images', 'log_queue_images', 'logs_images', log_ph)

        if task['done']:
            if task['error']:
                st.error(f'Image gathering failed: {task["error"]}')
            else:
                m = read_metrics(st.session_state.output_dir)
                st.success(f'Image gathering complete — {m["images"]} images downloaded.')
                manifest = Path(st.session_state.output_dir) / 'images' / 'images_manifest.md'
                if manifest.exists():
                    with st.expander('Image Manifest', expanded=False):
                        st.markdown(manifest.read_text(encoding='utf-8'))
                if st.button('Proceed to Reconstruction →'):
                    st.session_state.active_phase = PHASES[3]
                    st.rerun()


def render_phase4():
    st.header('Phase 4: Content Reconstruction')
    st.caption('Organize parsed content into structured export documents.')

    m = read_metrics(st.session_state.output_dir)
    if m['parsed'] == 0:
        st.warning('No parsed documents found. Run Phase 2 (Parse URLs) first.')

    st.session_state.reconstruct_formats = st.multiselect(
        'Export formats',
        options=RECONSTRUCT_FORMAT_OPTIONS,
        default=st.session_state.reconstruct_formats,
        help='Select one or more export formats to generate.',
    )

    task = st.session_state.task_reconstruct
    btn_disabled = task['running'] or not st.session_state.reconstruct_formats or m['parsed'] == 0

    if st.button('Run Reconstruction', disabled=btn_disabled, type='primary'):
        _launch(
            'task_reconstruct', 'log_queue_reconstruct', 'logs_reconstruct',
            _run_reconstruct_task,
            (st.session_state.output_dir,
             st.session_state.reconstruct_formats),
        )
        st.rerun()

    if task['running'] or task['done'] or task['error']:
        st.divider()
        with st.expander('Reconstruction Log', expanded=task['running']):
            log_ph = st.empty()
            _render_log_viewer(log_ph, st.session_state.logs_reconstruct)

        if task['running']:
            _poll_until_done('task_reconstruct', 'log_queue_reconstruct',
                             'logs_reconstruct', log_ph)

        if task['done']:
            if task['error']:
                st.error(f'Reconstruction failed: {task["error"]}')
            else:
                st.success('Reconstruction complete.')
                recon_dir = Path(st.session_state.output_dir) / 'reconstructed'
                for fmt in st.session_state.reconstruct_formats:
                    if fmt in _FORMAT_METHOD_MAP:
                        _, filename = _FORMAT_METHOD_MAP[fmt]
                        fpath = recon_dir / filename
                        if fpath.exists():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f'**{fmt}** — `reconstructed/{filename}`  '
                                         f'({fpath.stat().st_size // 1024:,} KB)')
                            with col2:
                                st.download_button(
                                    label='Download',
                                    data=fpath.read_bytes(),
                                    file_name=filename,
                                    mime='text/markdown',
                                    key=f'dl_{filename}',
                                )
                if st.button('Browse output →'):
                    st.session_state.active_phase = PHASES[4]
                    st.rerun()


def render_phase5():
    st.header('Phase 5: Browse & Export')
    st.caption('Preview generated files and download the full output.')

    output_dir = st.session_state.output_dir
    files = _list_output_files(output_dir)

    if not files:
        st.info(f'Output directory `{output_dir}` is empty or does not exist yet.')
        return

    labels = [f[0] for f in files]
    values = [f[1] for f in files]

    # Clamp index in case file list shrank between reruns
    saved_idx = st.session_state.get('browser_selected_idx', 0)
    saved_idx = min(saved_idx, len(labels) - 1)

    col_tree, col_preview = st.columns([1, 2], gap='medium')

    with col_tree:
        st.subheader('Files')
        selected_idx = st.selectbox(
            'Select file',
            range(len(labels)),
            index=saved_idx,
            format_func=lambda i: labels[i],
            key='_file_select',
        )
        st.session_state.browser_selected_idx = selected_idx
        selected_path = values[selected_idx]
        selected_rel = os.path.relpath(selected_path, output_dir)

        file_bytes = Path(selected_path).read_bytes()
        st.download_button(
            'Download selected file',
            data=file_bytes,
            file_name=Path(selected_path).name,
            use_container_width=True,
        )

        st.divider()
        st.subheader('Full Output')
        if st.button('Create ZIP', use_container_width=True):
            zip_bytes = _create_zip(output_dir)
            st.download_button(
                'Download ZIP',
                data=zip_bytes,
                file_name=f'{Path(output_dir).name}.zip',
                mime='application/zip',
                use_container_width=True,
            )

    with col_preview:
        st.subheader(f'`{selected_rel}`')
        try:
            text = Path(selected_path).read_text(encoding='utf-8', errors='replace')
        except OSError as e:
            st.error(f'Cannot read file: {e}')
            return

        if selected_path.endswith('.md'):
            tab_rendered, tab_raw = st.tabs(['Rendered', 'Raw'])
            with tab_rendered:
                st.markdown(text)
            with tab_raw:
                st.code(text, language='markdown')
        elif selected_path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
            st.image(selected_path)
        else:
            st.code(text)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.title('🔬 Research Gatherer')
        st.caption('End-to-end research pipeline')
        st.divider()

        st.text_input(
            'Output Directory',
            key='output_dir',
            help='Relative or absolute path for all output files.',
        )
        st.checkbox('Debug Mode', key='debug_mode')

        st.divider()
        st.session_state.active_phase = st.radio(
            'Navigate',
            PHASES,
            index=PHASES.index(st.session_state.active_phase),
            key='_phase_radio',
        )
        st.divider()

        # Live metrics
        st.subheader('Metrics')
        m = read_metrics(st.session_state.output_dir)
        c1, c2 = st.columns(2)
        c1.metric('Links', m['links'])
        c2.metric('Parsed', m['parsed'])
        c1.metric('Domains', m['domains'])
        c2.metric('Images', m['images'])

        # Task status badges
        st.divider()
        st.subheader('Task Status')
        status_icons = {
            (False, False, None):   ('⬜', 'Idle'),
            (True,  False, None):   ('🔄', 'Running'),
            (False, True,  None):   ('✅', 'Done'),
        }
        for label, key in [('Search', 'task_search'), ('Parse', 'task_parse'),
                           ('Images', 'task_images'), ('Reconstruct', 'task_reconstruct')]:
            t = st.session_state[key]
            if t['error']:
                icon, txt = '❌', 'Error'
            else:
                icon, txt = status_icons.get(
                    (t['running'], t['done'], None), ('⬜', 'Idle'))
            st.write(f'{icon} **{label}**: {txt}')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    render_sidebar()

    phase = st.session_state.active_phase
    if phase == PHASES[0]:
        render_phase1()
    elif phase == PHASES[1]:
        render_phase2()
    elif phase == PHASES[2]:
        render_phase3()
    elif phase == PHASES[3]:
        render_phase4()
    elif phase == PHASES[4]:
        render_phase5()


main()
