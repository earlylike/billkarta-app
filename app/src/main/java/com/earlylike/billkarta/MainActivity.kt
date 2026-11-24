package com.earlylike.billkarta

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import java.util.Locale
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.os.SystemClock
import android.provider.MediaStore
import android.util.Base64
import android.view.WindowManager
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.SystemBarStyle
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.google.android.play.core.appupdate.AppUpdateManager
import com.google.android.play.core.appupdate.AppUpdateManagerFactory
import com.google.android.play.core.appupdate.AppUpdateOptions
import com.google.android.play.core.install.model.AppUpdateType
import com.google.android.play.core.install.model.UpdateAvailability
import androidx.activity.result.IntentSenderRequest
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewAssetLoader

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private lateinit var outer: FrameLayout
    private lateinit var splash: FrameLayout
    private var splashStart = 0L

    // Forced (immediate) update through Google Play. Only works for the Play Store install; other installs just skip it.
    private var appUpdateManager: AppUpdateManager? = null
    private var updateDialog: AlertDialog? = null
    private var updateFlowActive = false

    private val updateLauncher =
        registerForActivityResult(ActivityResultContracts.StartIntentSenderForResult()) { result ->
            updateFlowActive = false
            if (result.resultCode != RESULT_OK) showUpdateDialog()
        }

    private val fileChooser =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val uris: Array<Uri>? =
                if (result.resultCode == RESULT_OK && result.data != null) {
                    val data = result.data!!
                    val clip = data.clipData
                    when {
                        clip != null -> Array(clip.itemCount) { clip.getItemAt(it).uri }
                        data.data != null -> arrayOf(data.data!!)
                        else -> null
                    }
                } else null
            filePathCallback?.onReceiveValue(uris)
            filePathCallback = null
        }

    // Always show dates as dd/mm/yyyy (English-India) in the date pickers, whatever the phone's region is.
    override fun attachBaseContext(newBase: Context) {
        val locale = Locale("en", "IN")
        Locale.setDefault(locale)
        val config = Configuration(newBase.resources.configuration)
        config.setLocale(locale)
        super.attachBaseContext(newBase.createConfigurationContext(config))
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        // Edge-to-edge with transparent bars and light icons (the app is dark); insets are handled below.
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(Color.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.dark(Color.TRANSPARENT)
        )
        super.onCreate(savedInstanceState)
        // Block screenshots, screen recording and the recent-apps preview of every page.
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        setContentView(R.layout.activity_main)
        webView = findViewById(R.id.webview)
        outer = findViewById(R.id.outer)
        splash = findViewById(R.id.splash)
        splashStart = SystemClock.uptimeMillis()
        // Safety net: never keep the logo screen up for more than 4 seconds.
        splash.postDelayed({ hideSplash() }, 4000)
        if (savedInstanceState != null) finishSplashNow()

        // Keep content clear of the status bar and navigation bar.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.root)) { v, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout()
            )
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }

        // Serves the bundled pages from https://appassets.androidplatform.net/assets/...
        // so all three pages share one origin (and therefore one localStorage).
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            setSupportZoom(false)
            builtInZoomControls = false
            textZoom = 100
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView, request: WebResourceRequest
            ): WebResourceResponse? = assetLoader.shouldInterceptRequest(request.url)

            override fun onPageFinished(view: WebView, url: String) {
                hideSplash()
            }

            override fun shouldOverrideUrlLoading(
                view: WebView, request: WebResourceRequest
            ): Boolean {
                val uri = request.url
                if (uri.host == WebViewAssetLoader.DEFAULT_DOMAIN) return false
                // WhatsApp, browser links, etc. open in their own apps.
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                } catch (e: ActivityNotFoundException) {
                    Toast.makeText(this@MainActivity, R.string.no_app_for_link, Toast.LENGTH_SHORT).show()
                }
                return true
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                view: WebView,
                callback: ValueCallback<Array<Uri>>,
                params: FileChooserParams
            ): Boolean {
                filePathCallback?.onReceiveValue(null)
                filePathCallback = callback
                return try {
                    fileChooser.launch(params.createIntent())
                    true
                } catch (e: Exception) {
                    filePathCallback = null
                    false
                }
            }
        }

        webView.addJavascriptInterface(Bridge(), "AndroidBridge")

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) webView.goBack() else finish()
            }
        })

        try {
            appUpdateManager = AppUpdateManagerFactory.create(this)
        } catch (e: Exception) {
            appUpdateManager = null
        }

        if (savedInstanceState == null) {
            webView.loadUrl(HOME_URL)
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    override fun onResume() {
        super.onResume()
        checkForUpdate()
    }

    /** Asks Google Play (in the background) if a newer version exists; if so, starts the full-screen immediate update. */
    private fun checkForUpdate() {
        val mgr = appUpdateManager ?: return
        if (updateFlowActive || updateDialog?.isShowing == true) return
        try {
            mgr.appUpdateInfo.addOnSuccessListener { info ->
                if (isFinishing || isDestroyed || updateFlowActive || updateDialog?.isShowing == true) return@addOnSuccessListener
                val a = info.updateAvailability()
                if (a == UpdateAvailability.UPDATE_AVAILABLE ||
                    a == UpdateAvailability.DEVELOPER_TRIGGERED_UPDATE_IN_PROGRESS
                ) {
                    if (info.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)) {
                        try {
                            updateFlowActive = true
                            mgr.startUpdateFlowForResult(
                                info, updateLauncher,
                                AppUpdateOptions.newBuilder(AppUpdateType.IMMEDIATE).build()
                            )
                        } catch (e: Exception) {
                            updateFlowActive = false
                            showUpdateDialog()
                        }
                    } else {
                        showUpdateDialog()
                    }
                }
            }
        } catch (e: Exception) {
            // Not installed from Google Play (test build): nothing to do.
        }
    }

    /** Our own blocking card, used when Play cannot update inside the app. Opens the Play Store page. */
    private fun showUpdateDialog() {
        if (isFinishing || isDestroyed || updateDialog?.isShowing == true) return
        val dlg = AlertDialog.Builder(this)
            .setTitle(R.string.update_title)
            .setMessage(R.string.update_msg)
            .setCancelable(false)
            .setPositiveButton(R.string.update_btn, null)
            .create()
        dlg.show()
        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener { openPlayStorePage() }
        updateDialog = dlg
    }

    private fun openPlayStorePage() {
        val id = "com.earlylike.billkarta"
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$id")))
        } catch (e: Exception) {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=$id")))
            } catch (e2: Exception) {
                Toast.makeText(this, R.string.no_app_for_link, Toast.LENGTH_SHORT).show()
            }
        }
    }

    /** Shows the logo for at least MIN_SPLASH_MS, then fades it out to reveal the first page. */
    private fun hideSplash() {
        if (splash.visibility != android.view.View.VISIBLE || splash.animation != null) return
        val wait = (MIN_SPLASH_MS - (SystemClock.uptimeMillis() - splashStart)).coerceAtLeast(0)
        splash.postDelayed({
            if (splash.visibility != android.view.View.VISIBLE) return@postDelayed
            applyAppBackground()
            splash.animate().alpha(0f).setDuration(280).withEndAction {
                splash.visibility = android.view.View.GONE
            }.start()
        }, wait)
    }

    private fun finishSplashNow() {
        applyAppBackground()
        splash.visibility = android.view.View.GONE
    }

    private fun applyAppBackground() {
        val bg = ContextCompat.getColor(this, R.color.app_background)
        outer.setBackgroundColor(bg)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onDestroy() {
        updateDialog?.dismiss()
        filePathCallback?.onReceiveValue(null)
        filePathCallback = null
        webView.destroy()
        super.onDestroy()
    }

    /** Methods the pages call (through app-shim.js) to save PDFs and backups. */
    inner class Bridge {
        @JavascriptInterface
        fun toast(message: String) {
            runOnUiThread { Toast.makeText(this@MainActivity, message, Toast.LENGTH_SHORT).show() }
        }

        /** Opens the phone's share sheet with a ready message (used by the share icon on the first page). */
        @JavascriptInterface
        fun shareApp(text: String) {
            runOnUiThread {
                try {
                    val send = Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_TEXT, text)
                    }
                    startActivity(Intent.createChooser(send, "Share BillKarta"))
                } catch (e: Exception) {
                    Toast.makeText(this@MainActivity, "Could not open share", Toast.LENGTH_SHORT).show()
                }
            }
        }

        @JavascriptInterface
        fun saveFile(base64: String, fileName: String, mimeType: String) {
            try {
                val bytes = Base64.decode(base64, Base64.DEFAULT)
                val safeName = fileName.replace(Regex("[\\\\/:*?\"<>|]"), "_")
                val values = ContentValues().apply {
                    put(MediaStore.MediaColumns.DISPLAY_NAME, safeName)
                    put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
                    put(
                        MediaStore.MediaColumns.RELATIVE_PATH,
                        Environment.DIRECTORY_DOWNLOADS + "/BillKarta"
                    )
                }
                val resolver = contentResolver
                val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                    ?: throw IllegalStateException("Could not create file")
                resolver.openOutputStream(uri)?.use { it.write(bytes) }
                    ?: throw IllegalStateException("Could not write file")

                runOnUiThread {
                    Toast.makeText(
                        this@MainActivity,
                        getString(R.string.saved_to_downloads, safeName),
                        Toast.LENGTH_LONG
                    ).show()
                    if (mimeType == "application/pdf") openFile(uri, mimeType)
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, R.string.save_failed, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun openFile(uri: Uri, mimeType: String) {
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, mimeType)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        try {
            startActivity(intent)
        } catch (e: ActivityNotFoundException) {
            // No PDF viewer installed: the file is still in Downloads.
        }
    }

    companion object {
        private const val MIN_SPLASH_MS = 1000L
        private const val HOME_URL =
            "https://appassets.androidplatform.net/assets/www/frontpage/index.html"
    }
}
