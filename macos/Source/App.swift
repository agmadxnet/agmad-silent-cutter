import AppKit
import AVKit
import AVFoundation
import UniformTypeIdentifiers

struct Clip {
    let start: Double
    let duration: Double
    let source: Double
}
func mappedTime(_ seconds: Double, _ clips: [Clip]) -> Double? {
    guard let clip = clips.last(where: { seconds >= $0.start }) else { return clips.first?.source }
    return clip.source + min(max(0, seconds - clip.start), clip.duration)
}
// Import once. Later app launches retain changes made in the installed release.
func migrateReleaseSettings(_ current: UserDefaults, latest: [String: Any]?, older: [String: Any]?, original: [String: Any]?) {
    guard !current.bool(forKey: "release13SettingsImported") else { return }
    let keys = ["destination", "engine", "cleanup", "scaleMode", "scaleLevel", "customThreshold", "customPadding", "customPause"]
    if let latest = latest {
        for key in keys { if let value = latest[key] { current.set(value, forKey: key) } }
    } else if let older = older {
        for key in keys { if let value = older[key] { current.set(value, forKey: key) } }
        let mode = older["cutMode"] as? Int ?? 0
        let gentle = min(2,max(0,older["gentlePreset"] as? Int ?? 1))
        let standard = min(4,max(0,older["strength"] as? Int ?? 2))
        current.set(mode == 2 ? 1 : 0, forKey: "scaleMode")
        current.set(mode == 1 ? standard+1 : [-3,-1,0][gentle], forKey: "scaleLevel")
    } else {
        if let original = original {
            for key in keys where current.object(forKey: key) == nil { if let value = original[key] { current.set(value, forKey: key) } }
        }
        if current.object(forKey: "scaleLevel") == nil, current.object(forKey: "strength") != nil {
            current.set(min(4,max(0,current.integer(forKey: "strength")))+1, forKey: "scaleLevel")
        }
    }
    current.set(true, forKey: "release13SettingsImported")
}
final class DropView: NSView {
    var onFile: ((URL) -> Void)?
    override init(frame: NSRect) {
        super.init(frame: frame)
        registerForDraggedTypes([.fileURL])
    }
    required init?(coder: NSCoder) { fatalError() }
    override func draw(_ dirtyRect: NSRect) {
        NSColor(srgbRed: 6/255, green: 7/255, blue: 8/255, alpha: 1).setFill()
        bounds.fill()
        super.draw(dirtyRect)
    }
    override func draggingEntered(_ sender: NSDraggingInfo) -> NSDragOperation { .copy }
    override func performDragOperation(_ sender: NSDraggingInfo) -> Bool {
        guard let urls = sender.draggingPasteboard.readObjects(forClasses: [NSURL.self]) as? [URL], let first = urls.first else { return false }
        onFile?(first)
        return true
    }
}
final class App: NSObject, NSApplicationDelegate {
    let defaults: UserDefaults = {
        if CommandLine.arguments.contains("--integration-test") || CommandLine.arguments.contains("--smoke-test") { return UserDefaults(suiteName: "net.agmad.silentcutter.release13.validation")! }
        return UserDefaults.standard
    }()
    var window: NSWindow!
    var source: URL?
    var output: URL?
    var log: URL?
    var job: Process?
    var gotDone = false
    var wasCancelled = false
    var clips: [Clip] = []
    var observer: Any?
    var followBusy = false
    var root: URL { Bundle.main.resourceURL!.appendingPathComponent("engine") }
    var dataRoot: URL {
        if (CommandLine.arguments.contains("--integration-test") || CommandLine.arguments.contains("--smoke-test")), let path = ProcessInfo.processInfo.environment["AGMAD_TEST_DATA"] { return URL(fileURLWithPath: path) }
        return FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("Agmad Silent Cutter")
    }
    func prepareDataDirectory() throws {
        let fm = FileManager.default
        try fm.createDirectory(at: dataRoot.appendingPathComponent("tools"), withIntermediateDirectories: true)
        for name in ["LOGS", "CACHE"] { try fm.createDirectory(at: dataRoot.appendingPathComponent(name), withIntermediateDirectories: true) }
        for relative in ["Setup_Local_Audio.command", "tools/process.py", "tools/music.py", "tools/requirements-music.txt"] {
            let dest = dataRoot.appendingPathComponent(relative)
            let bytes = try Data(contentsOf: root.appendingPathComponent(relative))
            try bytes.write(to: dest, options: .atomic)
            if relative.hasSuffix(".command") { try fm.setAttributes([.posixPermissions: 0o755], ofItemAtPath: dest.path) }
        }
    }
    var destination: URL!
    var engineRoot: URL!
    let sourceLabel = NSTextField(labelWithString: "Choose a video, or drag it into this window")
    let folderLabel = NSTextField(labelWithString: "")
    let engineLabel = NSTextField(labelWithString: "")
    let status = NSTextField(labelWithString: "Ready. Choose a video to begin.")
    let statistics = NSTextField(labelWithString: "Your original video remains untouched.")
    let strength = NSSegmentedControl(labels: ["−5", "−4", "−3", "−2", "−1", "0", "+1", "+2", "+3", "+4", "+5"], trackingMode: .selectOne, target: nil, action: nil)
    let cleanup = NSPopUpButton()
    let scope = NSPopUpButton()
    let startField = NSTextField(string: "0")
    let audio = NSSegmentedControl(labels: ["Original audio", "Edited audio"], trackingMode: .selectOne, target: nil, action: nil)
    let linked = NSButton(checkboxWithTitle: "Link comparison to edited timeline", target: nil, action: nil)
    let originalView = AVPlayerView()
    let editedView = AVPlayerView()
    let progress = NSProgressIndicator()
    let processButton = NSButton(title: "Process video", target: nil, action: nil)
    let cancelButton = NSButton(title: "Cancel", target: nil, action: nil)
    let openButton = NSButton(title: "Open output folder", target: nil, action: nil)
    let logButton = NSButton(title: "Open report", target: nil, action: nil)
    let cutMode = NSPopUpButton()
    let advancedToggle = NSButton(checkboxWithTitle: "Advanced values", target: nil, action: nil)
    let thresholdField = NSTextField(string: "2")
    let paddingField = NSTextField(string: "0.30")
    let pauseField = NSTextField(string: "0.8")
    let resetButton = NSButton(title: "Reset to preset", target: nil, action: nil)
    let cutHint = NSTextField(labelWithString: "")
    var advancedPanel: NSStackView!
    var customValues: [Double] = [2, 0.30, 0.8]
    var previousMode = 0
    var jobControls: [NSControl] = []
    let gentleValues: [[Double]] = [[0.5,0.50,1.5],[0.75,0.40,1.2],[1,0.35,1],[1.5,0.325,0.9],[2,0.30,0.8],[4,0.25,0.6]]
    let standardValues: [[Double]] = [[8,0.20,0.45],[12,0.12,0.25],[20,0.06,0.15],[30,0.04,0.10],[40,0.02,0.08]]

    func label(_ text: String) -> NSTextField {
        let f = NSTextField(labelWithString: text)
        f.font = .systemFont(ofSize: 12, weight: .medium)
        return f
    }
    func row(_ views: [NSView]) -> NSStackView {
        let s = NSStackView(views: views)
        s.orientation = .horizontal; s.spacing = 12; s.alignment = .centerY
        return s
    }
    func button(_ title: String, _ action: Selector) -> NSButton {
        let b = NSButton(title: title, target: self, action: action)
        b.bezelStyle = .rounded
        return b
    }
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.appearance = NSAppearance(named: .aqua)
        migrateReleaseSettings(defaults,
            latest: defaults.persistentDomain(forName: "net.agmad.silentcutter.test13"),
            older: defaults.persistentDomain(forName: "net.agmad.silentcutter.test12"),
            original: defaults.persistentDomain(forName: "local.silencecutter.mac"))
        do { try prepareDataDirectory() } catch {
            let alert = NSAlert(); alert.messageText = "Agmad Silent Cutter cannot create its working folder"; alert.informativeText = error.localizedDescription; alert.runModal(); NSApp.terminate(nil); return
        }
        let appMenu = NSMenu()
        let item = NSMenuItem(); appMenu.addItem(item)
        let menu = NSMenu()
        menu.addItem(withTitle: "About Agmad Silent Cutter", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        menu.addItem(NSMenuItem.separator())
        menu.addItem(withTitle: "Quit Agmad Silent Cutter", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        item.submenu = menu
        let editItem = NSMenuItem(title: "Edit", action: nil, keyEquivalent: "")
        let edit = NSMenu(title: "Edit")
        edit.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        edit.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        edit.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        edit.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = edit; appMenu.addItem(editItem); NSApp.mainMenu = appMenu
        destination = URL(fileURLWithPath: defaults.string(forKey: "destination") ?? FileManager.default.urls(for: .moviesDirectory, in: .userDomainMask)[0].appendingPathComponent("Agmad Silent Cutter").path)
        try? FileManager.default.createDirectory(at: destination, withIntermediateDirectories: true)
        engineRoot = URL(fileURLWithPath: defaults.string(forKey: "engine") ?? dataRoot.path)
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1120, height: 820), styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        window.title = "Agmad Silent Cutter"; window.appearance = NSAppearance(named: .darkAqua); window.backgroundColor = NSColor(srgbRed: 6/255, green: 7/255, blue: 8/255, alpha: 1); window.minSize = NSSize(width: 950, height: 700)
        let content = DropView(frame: window.contentView!.bounds)
        content.onFile = { [weak self] url in if self?.job == nil { self?.loadSource(url) } }
        window.contentView = content
        let title = NSTextField(labelWithString: "Agmad Silent Cutter")
        title.font = .systemFont(ofSize: 30, weight: .light)
        title.textColor = NSColor(srgbRed: 242/255, green: 243/255, blue: 246/255, alpha: 1)
        let brand = NSTextField(labelWithString: "A G M A D   /   LOCAL VIDEO TOOLS                                    1.4.0")
        brand.font = .systemFont(ofSize: 10, weight: .medium); brand.textColor = NSColor(srgbRed: 175/255, green: 182/255, blue: 197/255, alpha: 1)
        let subtitle = NSTextField(labelWithString: "Local cleanup. Clearer pacing. Originals preserved.")
        subtitle.textColor = .secondaryLabelColor; subtitle.font = .systemFont(ofSize: 13)
        sourceLabel.lineBreakMode = .byTruncatingMiddle
        folderLabel.lineBreakMode = .byTruncatingMiddle
        engineLabel.lineBreakMode = .byTruncatingMiddle; engineLabel.textColor = .secondaryLabelColor
        let choose = button("Choose video…", #selector(chooseSource))
        let folder = button("Output destination…", #selector(chooseDestination))
        let engine = button("Use existing v4 setup…", #selector(chooseEngine))
        let setup = button("Install cleanup tools…", #selector(runSetup))
        let sourceRow = row([choose, sourceLabel])
        let folderRow = row([folder, folderLabel])
        cleanup.addItems(withTitles: ["Off", "Noise", "Music"])
        cleanup.selectItem(at: min(2, max(0, defaults.integer(forKey: "cleanup"))))
        strength.selectedSegment = min(10, max(0, defaults.integer(forKey: "scaleLevel") + 5))
        strength.target = self; strength.action = #selector(presetChanged)
        cleanup.target = self; cleanup.action = #selector(saveSettings)
        scope.addItems(withTitles: ["Full video", "30-second test", "60-second test"])
        scope.target = self; scope.action = #selector(scopeChanged)
        startField.placeholderString = "Seconds"; startField.isEnabled = false
        startField.widthAnchor.constraint(equalToConstant: 75).isActive = true
        cutMode.addItems(withTitles: ["Preset scale", "Custom"])
        cutMode.selectItem(at: min(1, max(0, defaults.integer(forKey: "scaleMode"))))
        previousMode = cutMode.indexOfSelectedItem
        for (i, key) in ["customThreshold", "customPadding", "customPause"].enumerated() { if defaults.object(forKey: key) != nil { customValues[i] = defaults.double(forKey: key) } }
        cutMode.target = self; cutMode.action = #selector(cutModeChanged)
        advancedToggle.target = self; advancedToggle.action = #selector(toggleAdvanced)
        if previousMode == 1 { advancedToggle.state = .on }
        let cutRow = row([label("Cutting mode"), cutMode, strength, advancedToggle])
        let settings = row([label("Audio cleanup"), cleanup, label("Process"), scope, label("Start (sec)"), startField])
        for (field, bounds) in [(thresholdField, (0.5,40.0)), (paddingField, (0.02,0.60)), (pauseField, (0.1,2.0))] {
            let formatter = NumberFormatter(); formatter.locale = Locale(identifier: "en_US_POSIX"); formatter.numberStyle = .decimal; formatter.usesGroupingSeparator = false; formatter.maximumFractionDigits = 3
            formatter.minimum = NSNumber(value: bounds.0); formatter.maximum = NSNumber(value: bounds.1)
            field.formatter = formatter; field.widthAnchor.constraint(equalToConstant: 70).isActive = true
        }
        resetButton.target = self; resetButton.action = #selector(resetCustom)
        resetButton.bezelStyle = .rounded
        resetButton.toolTip = "Load the selected scale level within Custom limits. Custom minimum speech stays at 0.15 seconds."
        let valuesRow = row([label("Threshold (%)"), thresholdField, label("Padding (sec)"), paddingField, label("Minimum pause (sec)"), pauseField, resetButton])
        let guide = NSTextField(wrappingLabelWithString: "Custom limits — threshold 0.5–40%: lower keeps quieter words. Padding 0.02–0.60s: higher protects word edges.\nMinimum pause 0.10–2.0s: higher keeps short pauses. Use a 30-second test; values use a decimal point.")
        guide.font = .systemFont(ofSize: 11); guide.textColor = .secondaryLabelColor
        advancedPanel = NSStackView(views: [valuesRow, guide]); advancedPanel.orientation = .vertical; advancedPanel.alignment = .leading; advancedPanel.spacing = 6
        cutHint.font = .systemFont(ofSize: 11); cutHint.textColor = .secondaryLabelColor
        refreshCutControls()
        originalView.controlsStyle = .none; editedView.controlsStyle = .inline
        originalView.videoGravity = .resizeAspect; editedView.videoGravity = .resizeAspect
        func panel(_ heading: String, _ player: AVPlayerView) -> NSStackView {
            let h = label(heading)
            h.font = .systemFont(ofSize: 11, weight: .medium); h.textColor = .secondaryLabelColor
            player.wantsLayer = true; player.layer?.cornerRadius = 14; player.layer?.masksToBounds = true; player.layer?.borderWidth = 1; player.layer?.borderColor = NSColor(srgbRed: 0.32, green: 0.36, blue: 0.44, alpha: 0.55).cgColor
            let stack = NSStackView(views: [h, player]); stack.orientation = .vertical; stack.spacing = 8; stack.alignment = .leading
            player.translatesAutoresizingMaskIntoConstraints = false
            player.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
            return stack
        }
        let left = panel("ORIGINAL", originalView)
        let right = panel("EDITED — appears after processing", editedView)
        let players = row([left, right]); players.distribution = .fillEqually
        left.widthAnchor.constraint(equalTo: right.widthAnchor).isActive = true
        players.heightAnchor.constraint(greaterThanOrEqualToConstant: 150).isActive = true
        originalView.heightAnchor.constraint(equalTo: editedView.heightAnchor).isActive = true
        linked.state = .on; linked.target = self; linked.action = #selector(linkChanged)
        audio.selectedSegment = 1; audio.target = self; audio.action = #selector(audioChanged)
        audio.isEnabled = false; linked.isEnabled = false
        let comparison = row([linked, audio])
        processButton.target = self; processButton.action = #selector(processVideo); processButton.bezelStyle = .rounded
        processButton.keyEquivalent = "\r"
        processButton.bezelColor = NSColor(srgbRed: 198/255, green: 212/255, blue: 1, alpha: 1)
        processButton.contentTintColor = NSColor(srgbRed: 6/255, green: 7/255, blue: 8/255, alpha: 1)
        processButton.attributedTitle = NSAttributedString(string: "Process video", attributes: [.foregroundColor: NSColor.black, .font: NSFont.systemFont(ofSize: 13, weight: .medium)])
        cancelButton.target = self; cancelButton.action = #selector(cancelJob); cancelButton.bezelStyle = .rounded; cancelButton.isEnabled = false
        openButton.target = self; openButton.action = #selector(openOutput); openButton.bezelStyle = .rounded
        logButton.target = self; logButton.action = #selector(openLog); logButton.bezelStyle = .rounded; logButton.isEnabled = false
        let actions = row([processButton, cancelButton, openButton, logButton])
        progress.style = .spinning; progress.controlSize = .small; progress.isDisplayedWhenStopped = false
        status.lineBreakMode = .byTruncatingMiddle
        statistics.font = .monospacedDigitSystemFont(ofSize: 13, weight: .regular)
        let support = row([engine, setup, engineLabel])
        let outer = NSStackView(views: [brand, title, subtitle, sourceRow, folderRow, cutRow, settings, cutHint, advancedPanel, players, comparison, statistics, actions, row([progress, status]), support])
        outer.orientation = .vertical; outer.alignment = .leading; outer.spacing = 10
        outer.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(outer)
        NSLayoutConstraint.activate([outer.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 24), outer.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -24), outer.topAnchor.constraint(equalTo: content.topAnchor, constant: 24), outer.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -24)])
        for wide in [sourceRow, folderRow, players, support] { wide.widthAnchor.constraint(equalTo: outer.widthAnchor).isActive = true }
        sourceLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        folderLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        engineLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        jobControls = [choose, folder, engine, setup, strength, cleanup, scope, startField, cutMode, advancedToggle, thresholdField, paddingField, pauseField, resetButton]
        refreshPaths(); processButton.isEnabled = false
        window.center(); window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true)
        observer = nil
        if CommandLine.arguments.contains("--integration-test") {
            let env = ProcessInfo.processInfo.environment
            if let input = env["CUTTER_INPUT"], let engine = env["CUTTER_ENGINE"], let dest = env["CUTTER_DEST"] {
                engineRoot = URL(fileURLWithPath: engine); destination = URL(fileURLWithPath: dest); refreshPaths()
                loadSource(URL(fileURLWithPath: input)); strength.selectedSegment = min(10,max(0,(Int(env["CUTTER_LEVEL"] ?? "0") ?? 0)+5)); cleanup.selectItem(at: Int(env["CUTTER_CLEANUP"] ?? "0") ?? 0)
                cutMode.selectItem(at: Int(env["CUTTER_PROFILE"] ?? "0") ?? 0)
                previousMode = cutMode.indexOfSelectedItem
                if previousMode == 1 { advancedToggle.state = .on }
                refreshCutControls()
                processVideo()
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 45) { print("Integration timed out"); self.cancelJob(); exit(2) }
        }
        if CommandLine.arguments.contains("--smoke-test") {
            cutMode.selectItem(at: 0); cutModeChanged(); strength.selectedSegment = 10; presetChanged()
            cutMode.selectItem(at: 1); cutModeChanged(); resetCustom()
            assert(customValues[2] == 0.10 && readCustom() != nil)
            thresholdField.stringValue = "0.5"; paddingField.stringValue = "0.02"; pauseField.stringValue = "0.10"
            assert(readCustom() != nil)
            thresholdField.stringValue = "0.49"; assert(readCustom() == nil)
            resetCustom(); cutMode.selectItem(at: 0); cutModeChanged()
            assert(!strength.isHidden)
            let suite = "net.agmad.silentcutter.release13.migration-check"
            let prefs = UserDefaults(suiteName: suite)!
            prefs.removePersistentDomain(forName: suite)
            prefs.set(2,forKey:"strength")
            migrateReleaseSettings(prefs, latest: ["scaleLevel": -2, "scaleMode": 1, "customThreshold": 1.25, "engine": "/example/engine"], older: nil, original: nil)
            assert(prefs.integer(forKey:"scaleLevel") == -2 && prefs.integer(forKey:"scaleMode") == 1 && prefs.double(forKey:"customThreshold") == 1.25)
            prefs.set(4,forKey:"scaleLevel")
            migrateReleaseSettings(prefs, latest: ["scaleLevel": -5], older: nil, original: nil)
            assert(prefs.integer(forKey:"scaleLevel") == 4)
            prefs.removePersistentDomain(forName:suite)
            migrateReleaseSettings(prefs, latest:nil, older:["cutMode":0,"gentlePreset":1], original:nil)
            assert(prefs.integer(forKey:"scaleLevel") == -1)
            prefs.removePersistentDomain(forName:suite)
            prefs.set(2,forKey:"strength")
            migrateReleaseSettings(prefs, latest:nil, older:nil, original:nil)
            assert(prefs.integer(forKey:"scaleLevel") == 3)
            prefs.removePersistentDomain(forName:suite)
            print("Migration, preset switching, Custom reset, and field-boundary checks passed")
            assert(mappedTime(1.5, [Clip(start: 0, duration: 1, source: 0), Clip(start: 1, duration: 2, source: 4)]) == 4.5)
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                if let image = content.bitmapImageRepForCachingDisplay(in: content.bounds) {
                    content.cacheDisplay(in: content.bounds, to: image)
                    if let data = image.representation(using: .png, properties: [:]), let path = ProcessInfo.processInfo.environment["CUTTER_SCREENSHOT"] { try? data.write(to: URL(fileURLWithPath: path)) }
                }
                print("UI smoke test and comparison mapping passed")
                NSApp.terminate(nil)
            }
        }
    }
    func refreshPaths() {
        folderLabel.stringValue = destination.path
        engineLabel.stringValue = "Tools: " + engineRoot.lastPathComponent
    }
    @objc func chooseSource() {
        let p = NSOpenPanel(); p.allowedContentTypes = [.movie, .video]; p.allowsMultipleSelection = false
        if p.runModal() == .OK, let u = p.url { loadSource(u) }
    }
    func loadSource(_ url: URL) {
        guard job == nil else { return }
        stopPlayers()
        source = url; output = nil; clips = []; log = nil
        sourceLabel.stringValue = url.lastPathComponent
        originalView.player = AVPlayer(url: url); originalView.player?.isMuted = false
        originalView.controlsStyle = .inline
        editedView.player = nil
        audio.isEnabled = false; linked.isEnabled = false; logButton.isEnabled = false
        processButton.isEnabled = true; status.stringValue = "Ready to process."
        statistics.stringValue = "Choose a short test to check settings before processing the full video."
    }
    @objc func chooseDestination() {
        let p = NSOpenPanel(); p.canChooseDirectories = true; p.canChooseFiles = false; p.canCreateDirectories = true; p.directoryURL = destination
        if p.runModal() == .OK, let u = p.url { destination = u; defaults.set(u.path, forKey: "destination"); refreshPaths() }
    }
    @objc func chooseEngine() {
        let p = NSOpenPanel(); p.canChooseDirectories = true; p.canChooseFiles = false
        p.message = "Choose your working Mac_Silence_Cutter_v4 folder to reuse its installed cleanup tools."
        if p.runModal() == .OK, let u = p.url {
            guard FileManager.default.fileExists(atPath: u.appendingPathComponent("tools/process.py").path) else { showError("Select the extracted Silence Cutter folder containing tools/process.py."); return }
            engineRoot = u; defaults.set(u.path, forKey: "engine"); refreshPaths()
        }
    }
    @objc func runSetup() {
        NSWorkspace.shared.open(dataRoot.appendingPathComponent("Setup_Local_Audio.command"))
        engineRoot = dataRoot; defaults.set(dataRoot.path, forKey: "engine"); refreshPaths()
        status.stringValue = "Setup opened in Terminal. Wait for “Setup complete” before processing."
    }
    func valuesValid(_ values: [Double]) -> Bool {
        return values.count == 3 && values.allSatisfy { $0.isFinite } && (0.5...40).contains(values[0]) && (0.02...0.60).contains(values[1]) && (0.10...2).contains(values[2])
    }
    func readCustom() -> [Double]? {
        let fields = [thresholdField, paddingField, pauseField]
        let values = fields.compactMap { Double($0.stringValue) }
        return valuesValid(values) ? values : nil
    }
    func baseValues() -> [Double] {
        let index = max(0,strength.selectedSegment)
        return index <= 5 ? gentleValues[index] : standardValues[index-6]
    }
    func refreshCutControls() {
        let custom = cutMode.indexOfSelectedItem == 1
        strength.isHidden = custom
        advancedPanel?.isHidden = advancedToggle.state != .on
        let values = custom ? customValues : baseValues()
        for (field,value) in zip([thresholdField,paddingField,pauseField], values) { field.stringValue = String(format: "%.3f",value); field.isEnabled = custom && job == nil }
        resetButton.isEnabled = custom && job == nil
        cutHint.stringValue = custom ? "Custom values remembered. Reset loads the selected scale level within Custom limits." : "−5 gentlest · 0 balanced (still cuts pauses) · +5 strongest. +1 to +5 are unchanged."
    }
    @objc func cutModeChanged() {
        if previousMode == 1 {
            guard let values = readCustom() else { cutMode.selectItem(at: previousMode); showError("Use threshold 0.5–40%, padding 0.02–0.60s, and minimum pause 0.10–2.0s."); return }
            customValues = values
        }
        previousMode = cutMode.indexOfSelectedItem
        if previousMode == 1 { advancedToggle.state = .on }
        refreshCutControls(); saveSettings()
    }
    @objc func presetChanged() { refreshCutControls(); saveSettings() }
    @objc func toggleAdvanced() { advancedPanel.isHidden = advancedToggle.state != .on }
    @objc func resetCustom() {
        let values = baseValues()
        customValues = [values[0], values[1], max(0.10,values[2])]
        refreshCutControls(); saveSettings()
    }
    @objc func saveSettings() {
        if cutMode.indexOfSelectedItem == 1, let values = readCustom() { customValues = values }
        defaults.set(cutMode.indexOfSelectedItem, forKey: "scaleMode"); defaults.set(strength.selectedSegment - 5, forKey: "scaleLevel")
        for (key,value) in zip(["customThreshold", "customPadding", "customPause"],customValues) { defaults.set(value, forKey:key) }
        defaults.set(cleanup.indexOfSelectedItem, forKey: "cleanup")
    }
    @objc func scopeChanged() { startField.isEnabled = scope.indexOfSelectedItem > 0 && job == nil }
    func stopPlayers() {
        originalView.player?.pause(); editedView.player?.pause()
        if let observer = observer { editedView.player?.removeTimeObserver(observer); self.observer = nil }
    }
    @objc func audioChanged() {
        originalView.player?.isMuted = audio.selectedSegment != 0
        editedView.player?.isMuted = audio.selectedSegment != 1
    }
    @objc func linkChanged() {
        originalView.player?.pause(); editedView.player?.pause()
        originalView.controlsStyle = linked.state == .on ? .none : .inline
    }
    func follow(_ seconds: Double) {
        guard linked.state == .on, let target = mappedTime(seconds, clips), let before = originalView.player, let after = editedView.player else { return }
        let current = before.currentTime().seconds
        if !followBusy && (!current.isFinite || abs(current - target) > 0.12) {
            followBusy = true
            before.seek(to: CMTime(seconds: target, preferredTimescale: 600), toleranceBefore: .zero, toleranceAfter: .zero) { [weak self] _ in DispatchQueue.main.async { self?.followBusy = false } }
        }
        if after.rate > 0 { before.play() } else { before.pause() }
    }
    func busy(_ value: Bool) {
        for control in jobControls { control.isEnabled = !value }
        processButton.isEnabled = !value && source != nil; cancelButton.isEnabled = value
        startField.isEnabled = !value && scope.indexOfSelectedItem > 0
        if value { progress.startAnimation(nil) } else { progress.stopAnimation(nil); refreshCutControls() }
    }
    @objc func processVideo() {
        guard job == nil, let source = source else { return }
        let start = Double(startField.stringValue) ?? -1
        if scope.indexOfSelectedItem > 0 && (!start.isFinite || start < 0) { showError("Enter a non-negative start time in seconds."); return }
        window.makeFirstResponder(nil)
        if cutMode.indexOfSelectedItem == 1 && readCustom() == nil { showError("Custom values are outside the allowed limits. See Advanced values for guidance."); return }
        stopPlayers(); saveSettings(); gotDone = false; wasCancelled = false; clips = []
        output = nil; log = nil; logButton.isEnabled = false; editedView.player = nil
        audio.isEnabled = false; linked.isEnabled = false
        originalView.player?.isMuted = false; originalView.controlsStyle = .inline
        busy(true); status.stringValue = "Starting local processing…"
        let p = Process(); job = p
        p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        let length = scope.indexOfSelectedItem == 1 ? 30 : scope.indexOfSelectedItem == 2 ? 60 : 0
        p.arguments = ["python3", "-u", root.appendingPathComponent("tools/gui_process.py").path, "--input", source.path, "--destination", destination.path, "--engine", engineRoot.path, "--level", String(strength.selectedSegment - 5), "--mode", ["off", "noise", "music"][cleanup.indexOfSelectedItem], "--start", String(max(0, start)), "--length", String(length)]
        p.arguments! += ["--profile", ["scale", "custom"][cutMode.indexOfSelectedItem]]
        if cutMode.indexOfSelectedItem == 1 { p.arguments! += ["--threshold", String(customValues[0]), "--padding", String(customValues[1]), "--pause", String(customValues[2])] }
        var env = ProcessInfo.processInfo.environment
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        p.environment = env
        let pipe = Pipe(); p.standardOutput = pipe; p.standardError = pipe
        // A single background reader keeps newline-delimited events ordered.
        do {
            try p.run()
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                var buffer = Data()
                while true {
                    let data = pipe.fileHandleForReading.availableData
                    if data.isEmpty { break }
                    buffer.append(data)
                    while let newline = buffer.firstIndex(of: 10) {
                        let line = Data(buffer[..<newline]); buffer.removeSubrange(...newline)
                        DispatchQueue.main.async { self?.handle(line) }
                    }
                }
                if !buffer.isEmpty { let line = buffer; DispatchQueue.main.async { self?.handle(line) } }
                p.waitUntilExit()
                DispatchQueue.main.async {
                    guard let self = self else { return }
                    self.job = nil; self.busy(false)
                    if self.wasCancelled { self.status.stringValue = "Cancelled. Original preserved." }
                    else if !self.gotDone && p.terminationStatus != 0 { self.status.stringValue = "Processing failed. Open report for details, or check cleanup setup." }
                }
            }
        } catch { job = nil; busy(false); showError(error.localizedDescription) }
    }
    func handle(_ data: Data) {
        guard let e = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let event = e["event"] as? String else { return }
        switch event {
        case "stage": status.stringValue = e["message"] as? String ?? "Processing…"
        case "log": if let path = e["path"] as? String { log = URL(fileURLWithPath: path); logButton.isEnabled = true }
        case "error": showError(e["message"] as? String ?? "Processing failed.")
        case "done":
            gotDone = true
            guard let path = e["output"] as? String else { return }
            output = URL(fileURLWithPath: path)
            clips = (e["clips"] as? [[String: Double]] ?? []).compactMap { c in
                guard let s = c["start"], let d = c["duration"], let o = c["source"] else { return nil }; return Clip(start: s, duration: d, source: o)
            }
            editedView.player = AVPlayer(url: output!)
            audio.isEnabled = true; linked.isEnabled = true
            linked.state = .on; originalView.controlsStyle = .none; audioChanged()
            observer = editedView.player?.addPeriodicTimeObserver(forInterval: CMTime(seconds: 0.04, preferredTimescale: 600), queue: .main) { [weak self] t in self?.follow(t.seconds) }
            follow(0)
            let before = e["inputDuration"] as? Double ?? 0, after = e["outputDuration"] as? Double ?? 0, removed = e["removedPercent"] as? Double ?? 0
            statistics.stringValue = String(format: "Input / test: %.1fs     Edited: %.1fs     Removed: %.1f%%", before, after, removed)
            status.stringValue = "Finished. Use the edited player's controls for linked comparison."
            NSApp.requestUserAttention(.informationalRequest)
            if CommandLine.arguments.contains("--integration-test") {
                self.editedView.player?.play()
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                    assert(self.editedView.player?.currentItem?.status == .readyToPlay)
                    assert(self.originalView.player?.currentItem?.status == .readyToPlay)
                    let editedSeconds = self.editedView.player!.currentTime().seconds
                    let originalSeconds = self.originalView.player!.currentTime().seconds
                    assert(editedSeconds > 0.5)
                    assert(abs(originalSeconds - (mappedTime(editedSeconds, self.clips) ?? -100)) < 0.35)
                    self.editedView.player?.pause(); self.originalView.player?.pause()
                    if let view = self.window.contentView, let image = self.window.contentView?.bitmapImageRepForCachingDisplay(in: self.window.contentView!.bounds) {
                        view.cacheDisplay(in: view.bounds, to: image)
                        if let data = image.representation(using: .png, properties: [:]), let path = ProcessInfo.processInfo.environment["CUTTER_SCREENSHOT"] { try? data.write(to: URL(fileURLWithPath: path)) }
                    }
                    print("Native GUI processing integration passed; output and mapped players loaded")
                    NSApp.terminate(nil)
                }
            }
        case "cancelled": status.stringValue = "Cancelled."
        default: break
        }
    }
    @objc func cancelJob() {
        wasCancelled = true; status.stringValue = "Cancelling…"; cancelButton.isEnabled = false
        if job?.isRunning == true { job?.terminate() }
    }
    @objc func openOutput() { NSWorkspace.shared.open(output?.deletingLastPathComponent() ?? destination) }
    @objc func openLog() { if let log = log { NSWorkspace.shared.open(log) } }
    func showError(_ message: String) {
        status.stringValue = message
        let alert = NSAlert(); alert.messageText = "Agmad Silent Cutter"; alert.informativeText = message; alert.alertStyle = .warning
        alert.beginSheetModal(for: window)
    }
    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        if job?.isRunning == true {
            let a = NSAlert(); a.messageText = "A video is still processing"; a.addButton(withTitle: "Keep working"); a.addButton(withTitle: "Cancel and quit")
            if a.runModal() == .alertFirstButtonReturn { return .terminateCancel }
            cancelJob()
        }
        stopPlayers(); return .terminateNow
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
}
let app = NSApplication.shared
app.setActivationPolicy(.regular)
let delegate = App(); app.delegate = delegate
app.run()
