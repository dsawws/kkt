/**
 * Tools for ContentTable CKEditor: dirty warning, preview, equalize, layout toggle,
 * dialog defaults for new tables/images.
 */
(function () {
    var PREVIEW_CSS =
        'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.5;color:#1d2327;margin:24px;max-width:1100px}' +
        '.content-block a{color:#2e7d32;text-decoration:underline}' +
        '.content-block table{width:100%;border-collapse:collapse;margin:12px 0}' +
        '.content-block table th{background:#e8f5e9;color:#1b5e20;padding:10px 14px;border:1px solid #ddd;text-align:left}' +
        '.content-block table td{padding:10px 14px;border:1px solid #ddd;vertical-align:top}' +
        '.content-block table tr:nth-child(even) td{background:#f9f9f9}' +
        '.content-block table img{max-width:100%;height:auto}';

    function getEditor(name) {
        if (typeof CKEDITOR === 'undefined') return null;
        if (name && CKEDITOR.instances[name]) return CKEDITOR.instances[name];
        for (var key in CKEDITOR.instances) {
            if (CKEDITOR.instances.hasOwnProperty(key)) return CKEDITOR.instances[key];
        }
        return null;
    }

    function selectedTable(editor) {
        if (!editor) return null;
        var sel = editor.getSelection();
        if (!sel) return null;
        var start = sel.getStartElement();
        if (!start) return null;
        return start.getAscendant('table', true);
    }

    function countColumns(table) {
        var rows = table.$.rows;
        var max = 0;
        for (var i = 0; i < rows.length; i++) {
            var cells = rows[i].cells;
            var count = 0;
            for (var j = 0; j < cells.length; j++) {
                count += cells[j].colSpan || 1;
            }
            if (count > max) max = count;
        }
        return max;
    }

    function equalizeColumns(editor) {
        var table = selectedTable(editor);
        if (!table) {
            alert('Выделите ячейку внутри таблицы');
            return;
        }
        editor.fire('saveSnapshot');
        var n = countColumns(table);
        if (!n) return;
        var pct = (100 / n).toFixed(4).replace(/\.?0+$/, '') + '%';
        table.setStyle('width', '100%');
        table.setStyle('table-layout', 'fixed');
        var rows = table.$.rows;
        for (var r = 0; r < rows.length; r++) {
            var cells = rows[r].cells;
            for (var c = 0; c < cells.length; c++) {
                var cell = new CKEDITOR.dom.element(cells[c]);
                var span = cells[c].colSpan || 1;
                var w = ((100 / n) * span).toFixed(4).replace(/\.?0+$/, '') + '%';
                cell.setStyle('width', w);
                cell.removeAttribute('width');
            }
        }
        editor.fire('saveSnapshot');
    }

    function equalizeRows(editor) {
        var table = selectedTable(editor);
        if (!table) {
            alert('Выделите ячейку внутри таблицы');
            return;
        }
        editor.fire('saveSnapshot');
        var rows = table.$.rows;
        var n = rows.length;
        if (!n) return;
        var pct = (100 / n).toFixed(4).replace(/\.?0+$/, '') + '%';
        table.setStyle('width', '100%');
        table.setStyle('height', '100%');
        for (var r = 0; r < n; r++) {
            var tr = new CKEDITOR.dom.element(rows[r]);
            tr.setStyle('height', pct);
            var cells = rows[r].cells;
            for (var c = 0; c < cells.length; c++) {
                new CKEDITOR.dom.element(cells[c]).setStyle('height', pct);
            }
        }
        editor.fire('saveSnapshot');
    }

    function setTableLayout(editor, mode) {
        var table = selectedTable(editor);
        if (!table) {
            alert('Выделите ячейку внутри таблицы');
            return;
        }
        editor.fire('saveSnapshot');
        table.setStyle('width', '100%');
        table.setStyle('table-layout', mode === 'auto' ? 'auto' : 'fixed');
        editor.fire('saveSnapshot');
    }

    function openPreview(editor) {
        var html = editor ? editor.getData() : '';
        var win = window.open('', '_blank');
        if (!win) {
            alert('Разрешите всплывающие окна для предпросмотра');
            return;
        }
        win.document.open();
        win.document.write(
            '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">' +
            '<meta name="viewport" content="width=device-width,initial-scale=1">' +
            '<title>Предпросмотр таблицы</title><style>' + PREVIEW_CSS + '</style></head>' +
            '<body><div class="content-block">' + html + '</div></body></html>'
        );
        win.document.close();
    }

    function setupDialogDefaults() {
        if (typeof CKEDITOR === 'undefined' || CKEDITOR._cmsTableDialogs) return;
        CKEDITOR._cmsTableDialogs = true;

        CKEDITOR.on('dialogDefinition', function (ev) {
            var name = ev.data.name;
            var def = ev.data.definition;

            if (name === 'table' || name === 'tableProperties') {
                var info = def.getContents('info');
                if (info) {
                    var width = info.get('txtWidth');
                    if (width) width['default'] = '100%';
                }
                var oldOnOk = def.onOk;
                def.onOk = function () {
                    if (typeof oldOnOk === 'function') oldOnOk.apply(this, arguments);
                    var editor = ev.editor;
                    setTimeout(function () {
                        var table = selectedTable(editor);
                        if (!table) {
                            var sel = editor.getSelection();
                            var el = sel && sel.getStartElement();
                            table = el && el.getAscendant('table', true);
                        }
                        // After insert, find the last table if selection fails
                        if (!table) {
                            var tables = editor.document.getElementsByTag('table');
                            if (tables.count()) {
                                table = tables.getItem(tables.count() - 1);
                            }
                        }
                        if (!table) return;
                        table.setStyle('width', '100%');
                        table.setStyle('table-layout', 'fixed');
                        var n = countColumns(table);
                        if (!n) return;
                        var rows = table.$.rows;
                        for (var r = 0; r < rows.length; r++) {
                            var cells = rows[r].cells;
                            for (var c = 0; c < cells.length; c++) {
                                var cell = new CKEDITOR.dom.element(cells[c]);
                                var span = cells[c].colSpan || 1;
                                var w = ((100 / n) * span).toFixed(4).replace(/\.?0+$/, '') + '%';
                                cell.setStyle('width', w);
                                var h = ((100 / rows.length)).toFixed(4).replace(/\.?0+$/, '') + '%';
                                cell.setStyle('height', h);
                            }
                        }
                    }, 0);
                };
            }

            if (name === 'image' || name === 'image2') {
                var imgInfo = def.getContents('info');
                if (imgInfo) {
                    var txtWidth = imgInfo.get('txtWidth');
                    var txtHeight = imgInfo.get('txtHeight');
                    if (txtWidth) txtWidth['default'] = '100%';
                    if (txtHeight) txtHeight['default'] = '100%';
                }
                var oldImageOk = def.onOk;
                def.onOk = function () {
                    if (typeof oldImageOk === 'function') oldImageOk.apply(this, arguments);
                    var editor = ev.editor;
                    setTimeout(function () {
                        var sel = editor.getSelection();
                        var el = sel && sel.getStartElement();
                        var img = el && (el.is('img') ? el : el.getAscendant('img', true));
                        if (!img) {
                            var imgs = editor.document.getElementsByTag('img');
                            if (imgs.count()) img = imgs.getItem(imgs.count() - 1);
                        }
                        if (!img) return;
                        img.setStyle('width', '100%');
                        img.setStyle('height', '100%');
                        img.setAttribute('width', '100%');
                        img.setAttribute('height', '100%');
                    }, 0);
                };
            }
        });
    }

    function setupDirtyWarning(form, editor) {
        if (!form || form.dataset.dirtyBound) return;
        form.dataset.dirtyBound = '1';
        var dirty = false;
        var submitting = false;

        function markDirty() { dirty = true; }
        function markClean() { dirty = false; }

        form.querySelectorAll('input, textarea, select').forEach(function (el) {
            el.addEventListener('change', markDirty);
            el.addEventListener('input', markDirty);
        });

        if (editor && !editor._cmsDirtyBound) {
            editor._cmsDirtyBound = true;
            editor.on('change', markDirty);
            editor.on('key', markDirty);
        }

        form.addEventListener('submit', function () {
            submitting = true;
            markClean();
        });

        window.addEventListener('beforeunload', function (e) {
            if (!dirty || submitting) return;
            e.preventDefault();
            e.returnValue = '';
            return '';
        });
    }

    window.initTableEditor = function (opts) {
        opts = opts || {};
        setupDialogDefaults();

        var form = document.querySelector(opts.formSelector || 'form');
        var editorName = opts.editorName || 'id_content';
        var toolsBound = false;

        function bindTools() {
            if (toolsBound) return;
            toolsBound = true;

            var btnPreview = document.getElementById('btn-table-preview');
            if (btnPreview) {
                btnPreview.addEventListener('click', function (e) {
                    e.preventDefault();
                    openPreview(getEditor(editorName));
                });
            }

            var btnCols = document.getElementById('btn-equalize-cols');
            if (btnCols) {
                btnCols.addEventListener('click', function () {
                    equalizeColumns(getEditor(editorName));
                });
            }

            var btnRows = document.getElementById('btn-equalize-rows');
            if (btnRows) {
                btnRows.addEventListener('click', function () {
                    equalizeRows(getEditor(editorName));
                });
            }

            var btnFixed = document.getElementById('btn-layout-fixed');
            if (btnFixed) {
                btnFixed.addEventListener('click', function () {
                    setTableLayout(getEditor(editorName), 'fixed');
                });
            }

            var btnAuto = document.getElementById('btn-layout-auto');
            if (btnAuto) {
                btnAuto.addEventListener('click', function () {
                    setTableLayout(getEditor(editorName), 'auto');
                });
            }
        }

        function bind() {
            bindTools();
            setupDirtyWarning(form, getEditor(editorName));
        }

        if (typeof CKEDITOR !== 'undefined') {
            if (CKEDITOR.instances[editorName]) {
                bind();
            } else {
                CKEDITOR.on('instanceReady', function (ev) {
                    if (ev.editor.name === editorName || !opts.editorName) {
                        bind();
                    }
                });
                setTimeout(bind, 800);
            }
        } else {
            bind();
        }
    };

    /** Lightweight dirty warning for any panel form with CKEditor */
    window.initPanelFormDirty = function (opts) {
        opts = opts || {};
        var form = document.querySelector(opts.formSelector || 'form');
        var editorName = opts.editorName || null;

        function start(editor) {
            setupDirtyWarning(form, editor);
        }

        if (typeof CKEDITOR === 'undefined') {
            start(null);
            return;
        }
        CKEDITOR.on('instanceReady', function () {
            start(getEditor(editorName));
        });
        setTimeout(function () { start(getEditor(editorName)); }, 600);
    };
})();
