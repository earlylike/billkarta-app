/* BillKarta Android shim. Injected into every bundled page by sync-pages.sh.
   1. The app is fully offline, so the pages' "no internet" popup must never show.
   2. WebView ignores blob/download links, so hand those files to the native app. */
(function () {
  try {
    Object.defineProperty(Navigator.prototype, 'onLine', {
      get: function () { return true; },
      configurable: true
    });
  } catch (e) {}

  function bridge() { return window.AndroidBridge; }

  function sendToApp(href, name) {
    fetch(href).then(function (r) { return r.blob(); }).then(function (blob) {
      var fr = new FileReader();
      fr.onloadend = function () {
        var s = String(fr.result);
        var base64 = s.slice(s.indexOf(',') + 1);
        var type = blob.type || 'application/octet-stream';
        if (!name) name = type === 'application/pdf' ? 'BillKarta.pdf' : 'BillKarta-file';
        bridge().saveFile(base64, name, type);
      };
      fr.readAsDataURL(blob);
    }).catch(function () {
      try { bridge().toast('Could not save the file'); } catch (e) {}
    });
  }

  function isFileLink(a) {
    if (!a || a.tagName !== 'A' || !a.href || !bridge()) return false;
    return a.hasAttribute('download') || a.href.indexOf('blob:') === 0 || a.href.indexOf('data:') === 0;
  }

  var origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (isFileLink(this)) { sendToApp(this.href, this.getAttribute('download')); return; }
    return origClick.apply(this, arguments);
  };

  var origDispatch = EventTarget.prototype.dispatchEvent;
  EventTarget.prototype.dispatchEvent = function (ev) {
    if (ev && ev.type === 'click' && isFileLink(this)) {
      sendToApp(this.href, this.getAttribute('download'));
      return true;
    }
    return origDispatch.apply(this, arguments);
  };

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (isFileLink(a)) {
      e.preventDefault();
      e.stopPropagation();
      sendToApp(a.href, a.getAttribute('download'));
    }
  }, true);
})();
