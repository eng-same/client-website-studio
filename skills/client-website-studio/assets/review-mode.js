/*
 * Review Mode: a preview-only feedback toolbar for client websites.
 * package_site.py --preview injects it into preview copies. It must never ship in a live site.
 * Notes stay in this browser (localStorage when available) until someone copies or sends them.
 */
(function () {
  'use strict';
  if (window.__reviewModeLoaded) { return; }
  window.__reviewModeLoaded = true;

  var config = window.__REVIEW_MODE__ || {};
  var isAr = (document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('ar') === 0;
  var T = isAr ? {
    note: 'ملاحظة', edit: 'تعديل النص', notes: 'الملاحظات', copy: 'نسخ الملاحظات', send: 'إرسال عبر واتساب',
    clear: 'مسح الكل', clearSure: 'اضغط مرة أخرى للمسح', close: 'إغلاق', save: 'حفظ', cancel: 'إلغاء',
    remove: 'حذف', copied: 'تم النسخ، الصقها في المحادثة', copyFailed: 'تعذّر النسخ، حدّد النص وانسخه يدوياً',
    empty: 'لا توجد ملاحظات بعد.', write: 'اكتب ملاحظتك هنا…', hintNote: 'اضغط على أي جزء من الصفحة لإضافة ملاحظة',
    hintEdit: 'اضغط على أي نص وعدّله مباشرة، ثم اضغط خارجه', title: 'ملاحظات المعاينة', page: 'الصفحة',
    at: 'عند', changed: 'تعديل نص', phone: 'هاتف', desktop: 'كمبيوتر', saved: 'تم حفظ الملاحظة', arrow: '←',
    image: 'صورة', toolbar: 'أدوات المراجعة', hide: 'إخفاء', show: 'المراجعة'
  } : {
    note: 'Note', edit: 'Edit text', notes: 'Notes', copy: 'Copy notes', send: 'Send on WhatsApp',
    clear: 'Clear all', clearSure: 'Press again to clear', close: 'Close', save: 'Save', cancel: 'Cancel',
    remove: 'Delete', copied: 'Copied. Paste it into the chat', copyFailed: 'Could not copy. Select the text and copy it',
    empty: 'No notes yet.', write: 'Write your note here…', hintNote: 'Click any part of the page to add a note',
    hintEdit: 'Click any text and type, then click outside it', title: 'Preview notes', page: 'Page',
    at: 'at', changed: 'Text change', phone: 'phone', desktop: 'computer', saved: 'Note saved', arrow: '→',
    image: 'Image', toolbar: 'Review tools', hide: 'Hide', show: 'Review'
  };

  var STORE_KEY = 'reviewMode.v1';
  var TEXT_SELECTOR = 'h1,h2,h3,h4,h5,h6,p,li,a,button,span,figcaption,blockquote,dt,dd,td,th,label,small,strong,em,b,address,cite,q';
  var NOTE_SELECTOR = 'img,picture,svg,video,iframe,a,button,h1,h2,h3,h4,h5,h6,p,li,figure,blockquote,form,table,address';
  var REGION_SELECTOR = 'section,header,footer,nav,article,aside,main';
  var SINGLE_LINE = /^(H[1-6]|A|BUTTON|LABEL|DT|TH|TD|SPAN|SMALL|STRONG|EM|B|CITE|Q)$/;

  var notes = load();
  var mode = null;
  var editing = null;
  var pending = null;
  var clearArmed = false;
  var host, root, bar, highlight, tag, panel, list, pop, popText, toast, countBadge, hint, noteBtn, editBtn;

  function load() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed.filter(function (n) { return n && typeof n === 'object'; }) : [];
    } catch (e) { return []; }
  }

  function store() {
    try { window.localStorage.setItem(STORE_KEY, JSON.stringify(notes)); } catch (e) { /* storage blocked */ }
  }

  function clip(text, max) {
    text = String(text || '').replace(/\s+/g, ' ').trim();
    return text.length > max ? text.slice(0, max - 1) + '…' : text;
  }

  function pageId() {
    var parts = decodeURIComponent(location.pathname).replace(/\\/g, '/').split('/').filter(Boolean);
    var last = parts.length ? parts[parts.length - 1] : 'index.html';
    if (last.indexOf('.') === -1) { parts.push('index.html'); last = 'index.html'; }
    var prev = parts.length > 1 ? parts[parts.length - 2] : '';
    return /^(ar|en)$/i.test(prev) ? prev + '/' + last : last;
  }

  function sectionName(el) {
    var named = el.closest('[data-section]');
    if (named) { return clip(named.getAttribute('data-section'), 40); }
    var region = el.closest(REGION_SELECTOR);
    if (region) {
      var heading = region.querySelector('h1,h2,h3');
      return heading ? clip(heading.textContent, 40) : region.tagName.toLowerCase();
    }
    return 'body';
  }

  function describe(el) {
    if (el.tagName === 'IMG') {
      var src = (el.getAttribute('src') || '').split('/').pop();
      return T.image + ': ' + clip(el.getAttribute('alt') || src, 50);
    }
    var text = clip(el.innerText || el.textContent || '', 60);
    return text || clip(el.getAttribute('aria-label') || el.tagName.toLowerCase(), 60);
  }

  function device() { return window.innerWidth < 768 ? T.phone : T.desktop; }

  function fromToolbar(event) {
    var path = event.composedPath ? event.composedPath() : [];
    return path.indexOf(host) !== -1;
  }

  function el(tagName, className, text) {
    var node = document.createElement(tagName);
    if (className) { node.className = className; }
    if (text) { node.textContent = text; }
    return node;
  }

  function button(label, className, handler) {
    var node = el('button', className, label);
    node.type = 'button';
    node.addEventListener('click', handler);
    return node;
  }

  function build() {
    host = document.createElement('div');
    host.setAttribute('data-review-mode', '');
    host.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:2147483000;';
    root = host.attachShadow({ mode: 'open' });
    var style = el('style');
    style.textContent = [
      ':host{all:initial}',
      '*{box-sizing:border-box;font-family:system-ui,"Segoe UI",Tahoma,Arial,sans-serif}',
      '.bar{position:fixed;bottom:16px;inset-inline-end:16px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;',
      'background:#1f2937;color:#fff;padding:6px;border-radius:10px;box-shadow:0 4px 18px rgba(0,0,0,.25);pointer-events:auto;max-width:calc(100vw - 32px)}',
      '.bar button,.panel button,.pop button{font-size:14px;line-height:1.2;border:0;border-radius:7px;padding:9px 12px;cursor:pointer;min-height:38px}',
      '.bar button{background:#374151;color:#fff}',
      '.bar button[aria-pressed="true"]{background:#2563eb}',
      '.bar .hide{background:transparent;color:#cbd5e1;padding:9px 8px}',
      '.bar.min > :not(.show){display:none}',
      '.bar:not(.min) .show{display:none}',
      '.bar .show{background:#2563eb}',
      '.hint{position:fixed;top:12px;inset-inline:0;margin:auto;width:max-content;max-width:calc(100vw - 24px);background:#2563eb;color:#fff;',
      'font-size:14px;padding:8px 12px;border-radius:8px;display:none;pointer-events:none}',
      '.hl{position:fixed;border:2px solid #2563eb;background:rgba(37,99,235,.08);border-radius:4px;display:none;pointer-events:none}',
      '.tag{position:fixed;background:#2563eb;color:#fff;font-size:12px;padding:2px 6px;border-radius:4px;display:none;pointer-events:none;white-space:nowrap}',
      '.panel{position:fixed;bottom:72px;inset-inline-end:16px;width:min(420px,calc(100vw - 32px));max-height:min(70vh,560px);display:none;flex-direction:column;',
      'background:#fff;color:#111827;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.3);pointer-events:auto;overflow:hidden}',
      '.panel.open{display:flex}',
      '.panel h2{font-size:16px;margin:0;padding:12px 14px;border-bottom:1px solid #e5e7eb}',
      '.list{overflow:auto;padding:8px 14px;flex:1;font-size:14px;line-height:1.5}',
      '.item{border-bottom:1px solid #f3f4f6;padding:8px 0;display:flex;gap:8px;align-items:flex-start}',
      '.item p{margin:0;flex:1;white-space:pre-wrap;word-break:break-word}',
      '.item button{background:#fee2e2;color:#991b1b;padding:4px 8px;min-height:30px;font-size:12px}',
      '.actions{display:flex;flex-wrap:wrap;gap:6px;padding:10px 14px;border-top:1px solid #e5e7eb}',
      '.actions .primary{background:#2563eb;color:#fff}',
      '.actions .wa{background:#16a34a;color:#fff}',
      '.actions .quiet{background:#f3f4f6;color:#111827}',
      '.pop{position:fixed;width:min(320px,calc(100vw - 24px));background:#fff;color:#111827;border-radius:10px;padding:10px;display:none;',
      'box-shadow:0 8px 30px rgba(0,0,0,.3);pointer-events:auto}',
      '.pop .where{font-size:12px;color:#4b5563;margin-bottom:6px}',
      '.pop textarea{width:100%;min-height:90px;font-size:15px;padding:8px;border:1px solid #d1d5db;border-radius:7px;resize:vertical}',
      '.pop .row{display:flex;gap:6px;margin-top:8px}',
      '.pop .primary{background:#2563eb;color:#fff}',
      '.pop .quiet{background:#f3f4f6;color:#111827}',
      '.toast{position:fixed;top:60px;inset-inline:0;margin:auto;width:max-content;max-width:calc(100vw - 24px);background:#111827;color:#fff;',
      'font-size:14px;padding:8px 14px;border-radius:8px;display:none;pointer-events:none}'
    ].join('\n');
    root.appendChild(style);

    var dir = isAr ? 'rtl' : 'ltr';
    highlight = el('div', 'hl');
    tag = el('div', 'tag');
    hint = el('div', 'hint');
    hint.setAttribute('dir', dir);
    toast = el('div', 'toast');
    toast.setAttribute('role', 'status');
    toast.setAttribute('dir', dir);

    bar = el('div', 'bar');
    bar.setAttribute('dir', dir);
    bar.setAttribute('role', 'toolbar');
    bar.setAttribute('aria-label', T.toolbar);
    noteBtn = button(T.note, '', function () { setMode(mode === 'note' ? null : 'note'); });
    editBtn = button(T.edit, '', function () { setMode(mode === 'edit' ? null : 'edit'); });
    var listBtn = button(T.notes, '', togglePanel);
    countBadge = el('span', '', '');
    listBtn.appendChild(countBadge);
    var hideBtn = button(T.hide, 'hide', function () { setMode(null); bar.classList.add('min'); panel.classList.remove('open'); });
    var showBtn = button(T.show, 'show', function () { bar.classList.remove('min'); });
    noteBtn.setAttribute('aria-pressed', 'false');
    editBtn.setAttribute('aria-pressed', 'false');
    [noteBtn, editBtn, listBtn, hideBtn, showBtn].forEach(function (b) { bar.appendChild(b); });

    panel = el('div', 'panel');
    panel.setAttribute('dir', dir);
    panel.appendChild(el('h2', '', T.title + (config.label ? ' — ' + config.label : '')));
    list = el('div', 'list');
    panel.appendChild(list);
    var actions = el('div', 'actions');
    actions.appendChild(button(T.copy, 'primary', copyNotes));
    actions.appendChild(button(T.send, 'wa', sendWhatsApp));
    var clearBtn = button(T.clear, 'quiet', function () {
      if (!clearArmed) { clearArmed = true; clearBtn.textContent = T.clearSure; return; }
      notes = []; store(); render(); clearArmed = false; clearBtn.textContent = T.clear;
    });
    actions.appendChild(clearBtn);
    actions.appendChild(button(T.close, 'quiet', togglePanel));
    panel.appendChild(actions);

    pop = el('div', 'pop');
    pop.setAttribute('dir', dir);
    var where = el('div', 'where');
    popText = el('textarea');
    popText.setAttribute('placeholder', T.write);
    popText.setAttribute('aria-label', T.write);
    var row = el('div', 'row');
    row.appendChild(button(T.save, 'primary', saveNote));
    row.appendChild(button(T.cancel, 'quiet', closePop));
    pop.appendChild(where);
    pop.appendChild(popText);
    pop.appendChild(row);
    popText.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { saveNote(); }
    });

    [highlight, tag, hint, bar, panel, pop, toast].forEach(function (n) { root.appendChild(n); });
    var spacer = document.createElement('div');
    spacer.setAttribute('data-review-mode', 'spacer');
    spacer.setAttribute('aria-hidden', 'true');
    document.body.appendChild(spacer);
    document.body.appendChild(host);
    var fitSpacer = function () { spacer.style.height = (bar.offsetHeight + 32) + 'px'; };
    fitSpacer();
    window.addEventListener('resize', fitSpacer);
    render();
  }

  function setMode(next) {
    finishEdit();
    closePop();
    mode = next;
    noteBtn.setAttribute('aria-pressed', String(mode === 'note'));
    editBtn.setAttribute('aria-pressed', String(mode === 'edit'));
    hint.textContent = mode === 'note' ? T.hintNote : mode === 'edit' ? T.hintEdit : '';
    hint.style.display = mode ? 'block' : 'none';
    hideHighlight();
  }

  function targetFor(node) {
    if (!(node instanceof Element)) { node = node && node.parentElement; }
    if (!node || node === document.documentElement || node === document.body) { return null; }
    if (mode === 'edit') { return node.closest(TEXT_SELECTOR); }
    return node.closest(NOTE_SELECTOR) || node.closest(REGION_SELECTOR) || node;
  }

  function showHighlight(target) {
    if (!target) { hideHighlight(); return; }
    var r = target.getBoundingClientRect();
    highlight.style.cssText = 'display:block;left:' + (r.left - 3) + 'px;top:' + (r.top - 3) + 'px;width:' +
      (r.width + 6) + 'px;height:' + (r.height + 6) + 'px;';
    tag.textContent = sectionName(target);
    var top = r.top - 24 < 0 ? r.bottom + 4 : r.top - 24;
    tag.style.cssText = 'display:block;top:' + top + 'px;' + (isAr ? 'right:' + Math.max(4, window.innerWidth - r.right - 3) : 'left:' + Math.max(4, r.left - 3)) + 'px;';
  }

  function hideHighlight() {
    if (highlight) { highlight.style.display = 'none'; tag.style.display = 'none'; }
  }

  function onMove(event) {
    if (!mode || fromToolbar(event) || editing) { return; }
    showHighlight(targetFor(event.target));
  }

  function onClick(event) {
    if (!mode || fromToolbar(event)) { return; }
    if (editing && editing.el.contains(event.target)) {
      if (event.target.closest('a,button')) { event.preventDefault(); }
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    var target = targetFor(event.target);
    if (!target) { return; }
    if (mode === 'note') { openPop(target, event.clientX, event.clientY); }
    else { startEdit(target); }
  }

  function blockActivation(event) {
    if (mode && !fromToolbar(event) && !(editing && editing.el.contains(event.target))) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  function openPop(target, x, y) {
    finishEdit();
    pending = target;
    showHighlight(target);
    pop.firstChild.textContent = '[' + sectionName(target) + '] ' + T.at + ' «' + describe(target) + '»';
    popText.value = '';
    pop.style.display = 'block';
    var w = pop.offsetWidth, h = pop.offsetHeight;
    var left = Math.min(Math.max(12, x - w / 2), window.innerWidth - w - 12);
    var top = y + 16 + h > window.innerHeight - 70 ? Math.max(12, y - h - 16) : y + 16;
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
    popText.focus();
  }

  function closePop() {
    if (pop) { pop.style.display = 'none'; }
    pending = null;
  }

  function saveNote() {
    var text = popText.value.trim();
    if (!pending || !text) { closePop(); return; }
    notes.push({ kind: 'note', page: pageId(), section: sectionName(pending), target: describe(pending),
      text: clip(text, 1000), device: device(), at: new Date().toISOString() });
    store(); render(); closePop(); hideHighlight(); flash(T.saved);
  }

  function startEdit(target) {
    finishEdit();
    var before = (target.innerText || target.textContent || '').trim();
    editing = { el: target, before: before, html: target.innerHTML, outline: target.style.outline };
    try { target.contentEditable = 'plaintext-only'; } catch (e) { target.contentEditable = 'true'; }
    if (target.contentEditable !== 'plaintext-only') { target.contentEditable = 'true'; }
    target.style.outline = '2px dashed #2563eb';
    target.addEventListener('blur', finishEdit, { once: true });
    target.addEventListener('keydown', editKeys);
    hideHighlight();
    target.focus();
  }

  function editKeys(event) {
    if (event.key === 'Escape') { event.preventDefault(); editing.el.innerHTML = editing.html; editing.el.blur(); }
    else if (event.key === 'Enter' && SINGLE_LINE.test(event.currentTarget.tagName)) { event.preventDefault(); event.currentTarget.blur(); }
  }

  function finishEdit() {
    if (!editing) { return; }
    var current = editing;
    editing = null;
    var target = current.el;
    target.removeEventListener('keydown', editKeys);
    target.removeAttribute('contenteditable');
    target.style.outline = current.outline;
    var after = (target.innerText || target.textContent || '').trim();
    if (after !== current.before) {
      notes.push({ kind: 'edit', page: pageId(), section: sectionName(target), before: clip(current.before, 500),
        after: clip(after, 500), device: device(), at: new Date().toISOString() });
      store(); render(); flash(T.saved);
    }
  }

  function line(n, i) {
    var head = (i + 1) + '. [' + n.section + '] ';
    if (n.kind === 'edit') {
      return head + T.changed + ': «' + n.before + '» ' + T.arrow + ' «' + n.after + '» (' + n.device + ')';
    }
    return head + T.at + ' «' + n.target + '»: ' + n.text + ' (' + n.device + ')';
  }

  function exportText() {
    var title = T.title + ' — ' + clip(document.title, 60) + (config.label ? ' — ' + config.label : '');
    var pages = [];
    notes.forEach(function (n) { if (pages.indexOf(n.page) === -1) { pages.push(n.page); } });
    var out = [title];
    pages.forEach(function (p) {
      out.push(T.page + ': ' + p);
      notes.filter(function (n) { return n.page === p; }).forEach(function (n, i) { out.push(line(n, i)); });
    });
    return out.join('\n');
  }

  function render() {
    countBadge.textContent = notes.length ? ' (' + notes.length + ')' : '';
    list.textContent = '';
    if (!notes.length) { list.appendChild(el('p', '', T.empty)); return; }
    notes.forEach(function (n, index) {
      var item = el('div', 'item');
      item.appendChild(el('p', '', n.page + '\n' + line(n, index)));
      item.appendChild(button(T.remove, '', function () { notes.splice(index, 1); store(); render(); }));
      list.appendChild(item);
    });
  }

  function togglePanel() {
    setMode(null);
    clearArmed = false;
    panel.classList.toggle('open');
  }

  function flash(message) {
    toast.textContent = message;
    toast.style.display = 'block';
    clearTimeout(flash.timer);
    flash.timer = setTimeout(function () { toast.style.display = 'none'; }, 2600);
  }

  function copyNotes() {
    var text = exportText();
    var fallback = function () {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.cssText = 'position:fixed;top:0;left:0;opacity:0;';
      root.appendChild(area);
      area.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      root.removeChild(area);
      flash(ok ? T.copied : T.copyFailed);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { flash(T.copied); }, fallback);
    } else {
      fallback();
    }
  }

  function sendWhatsApp() {
    window.open('https://wa.me/?text=' + encodeURIComponent(exportText()), '_blank', 'noopener');
  }

  function init() {
    build();
    document.addEventListener('mousemove', onMove, true);
    document.addEventListener('click', onClick, true);
    document.addEventListener('submit', blockActivation, true);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !editing) { closePop(); setMode(null); }
    });
    window.addEventListener('scroll', function () { if (!pending) { hideHighlight(); } }, { passive: true });
    window.__reviewMode = { notes: function () { return notes.slice(); }, exportText: exportText };
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); }
  else { init(); }
}());
