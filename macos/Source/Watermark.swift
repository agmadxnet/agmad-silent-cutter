import AppKit

struct WatermarkSettings {
    var x: Double = 0.95
    var y: Double = 0.95
    var width: Double = 0.15
    var opacity: Double = 0.7
}
final class WatermarkCanvas: NSView {
    var frameImage: NSImage!
    var logo: NSImage!
    var settings = WatermarkSettings()
    var editable = true
    override var isFlipped: Bool { true }
    var videoRect: NSRect {
        guard let image = frameImage else { return .zero }
        let scale = min(bounds.width / image.size.width, bounds.height / image.size.height)
        let size = NSSize(width: image.size.width * scale, height: image.size.height * scale)
        return NSRect(x: (bounds.width-size.width)/2, y: (bounds.height-size.height)/2, width: size.width, height: size.height)
    }
    var logoRect: NSRect {
        let video = videoRect
        guard let logo = logo, logo.size.height > 0 else { return .zero }
        let width = min(video.width * settings.width, video.height * 0.8 * logo.size.width / logo.size.height)
        let height = width * logo.size.height / logo.size.width
        return NSRect(x: video.minX + (video.width-width)*settings.x, y: video.minY + (video.height-height)*settings.y, width: width, height: height)
    }
    override func draw(_ dirtyRect: NSRect) {
        NSColor.black.setFill(); bounds.fill()
        frameImage?.draw(in: videoRect, from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: true, hints: nil)
        logo?.draw(in: logoRect, from: .zero, operation: .sourceOver, fraction: settings.opacity, respectFlipped: true, hints: nil)
        NSColor.controlAccentColor.setStroke()
        let outline = NSBezierPath(rect: logoRect.insetBy(dx: -2, dy: -2)); outline.lineWidth = 1
        outline.setLineDash([4,3], count: 2, phase: 0); outline.stroke()
    }
    func position(_ event: NSEvent) {
        guard editable else { return }
        let p = convert(event.locationInWindow, from: nil), video = videoRect, logo = logoRect
        settings.x = min(1,max(0, (p.x-video.minX-logo.width/2)/max(1,video.width-logo.width)))
        settings.y = min(1,max(0, (p.y-video.minY-logo.height/2)/max(1,video.height-logo.height)))
        needsDisplay = true
    }
    override func mouseDown(with event: NSEvent) { position(event) }
    override func mouseDragged(with event: NSEvent) { position(event) }
}
final class WatermarkEditor: NSWindowController {
    let canvas = WatermarkCanvas()
    let sizeSlider = NSSlider(value: 15, minValue: 5, maxValue: 40, target: nil, action: nil)
    let opacitySlider = NSSlider(value: 70, minValue: 0, maxValue: 100, target: nil, action: nil)
    let sizeLabel = NSTextField(labelWithString: "Size 15%")
    let opacityLabel = NSTextField(labelWithString: "Opacity 70%")
    var onDone: ((WatermarkSettings) -> Void)?
    init(frame: NSImage, logo: NSImage, settings: WatermarkSettings) {
        let panel = NSPanel(contentRect: NSRect(x:0,y:0,width:720,height:620), styleMask:[.titled], backing:.buffered, defer:false)
        super.init(window: panel)
        panel.title = "Watermark placement"; panel.appearance = NSAppearance(named:.darkAqua)
        canvas.frameImage = frame; canvas.logo = logo; canvas.settings = settings
        canvas.translatesAutoresizingMaskIntoConstraints = false
        canvas.heightAnchor.constraint(equalToConstant:360).isActive = true
        let corners = NSStackView();corners.spacing = 6
        for (index,title) in ["Top left","Top right","Bottom left","Bottom right","Centre"].enumerated() {
            let button = NSButton(title:title,target:self,action:#selector(preset(_:)));button.tag = index;button.bezelStyle = .rounded
            button.bezelColor = NSColor(srgbRed:0.15,green:0.18,blue:0.23,alpha:1)
            button.attributedTitle = NSAttributedString(string:title,attributes:[.foregroundColor:NSColor.white,.font:NSFont.systemFont(ofSize:11)])
            corners.addArrangedSubview(button)
        }
        sizeSlider.doubleValue = settings.width*100; opacitySlider.doubleValue = settings.opacity*100
        for slider in [sizeSlider,opacitySlider] { slider.target = self; slider.action = #selector(change); slider.widthAnchor.constraint(equalToConstant:180).isActive = true }
        let controls = NSStackView(views:[sizeLabel,sizeSlider,opacityLabel,opacitySlider]); controls.spacing = 12;controls.heightAnchor.constraint(equalToConstant:28).isActive = true
        let hint = NSTextField(wrappingLabelWithString:"Drag or click on the frame to position the PNG. Transparency is preserved. Preview uses the first video frame; the watermark appears throughout the export. This adds a video encoding pass.")
        hint.font = .systemFont(ofSize:12); hint.textColor = .secondaryLabelColor
        let done = NSButton(title:"Use watermark",target:self,action:#selector(done)); done.bezelStyle = .rounded
        let cancel = NSButton(title:"Cancel",target:self,action:#selector(cancel)); cancel.bezelStyle = .rounded
        for button in [cancel,done] {
            button.appearance = NSAppearance(named:.darkAqua)
            button.bezelColor = NSColor(srgbRed:0.15,green:0.18,blue:0.23,alpha:1)
            button.contentTintColor = .white
        }
        for button in [cancel,done] { button.attributedTitle = NSAttributedString(string:button.title,attributes:[.foregroundColor:NSColor.white,.font:NSFont.systemFont(ofSize:13)]) }
        done.bezelColor = .controlAccentColor
        let actions = NSStackView(views:[corners,cancel,done]); actions.spacing = 12
        let stack = NSStackView(views:[canvas,controls,hint,actions]);stack.orientation = .vertical;stack.alignment = .leading;stack.spacing = 14;stack.translatesAutoresizingMaskIntoConstraints = false
        stack.setVisibilityPriority(.mustHold,for:controls)
        stack.setVisibilityPriority(.mustHold,for:hint)
        panel.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo:panel.contentView!.leadingAnchor,constant:20),stack.trailingAnchor.constraint(equalTo:panel.contentView!.trailingAnchor,constant:-20),stack.topAnchor.constraint(equalTo:panel.contentView!.topAnchor,constant:20),stack.bottomAnchor.constraint(equalTo:panel.contentView!.bottomAnchor,constant:-20),canvas.widthAnchor.constraint(equalTo:stack.widthAnchor),hint.widthAnchor.constraint(equalTo:stack.widthAnchor)])
        change()
    }
    required init?(coder:NSCoder) { fatalError() }
    @objc func change() {
        canvas.settings.width = sizeSlider.doubleValue/100;canvas.settings.opacity = opacitySlider.doubleValue/100;canvas.needsDisplay = true
        sizeLabel.stringValue = "Size \(Int(sizeSlider.doubleValue))%";opacityLabel.stringValue = "Opacity \(Int(opacitySlider.doubleValue))%"
    }
    @objc func preset(_ sender:NSButton) {
        let positions:[(Double,Double)] = [(0.05,0.05),(0.95,0.05),(0.05,0.95),(0.95,0.95),(0.5,0.5)]
        guard (0..<positions.count).contains(sender.tag) else { return }
        let p = positions[sender.tag];canvas.settings.x = p.0;canvas.settings.y = p.1;canvas.needsDisplay = true
    }
    @objc func done() { onDone?(canvas.settings);window?.sheetParent?.endSheet(window!) }
    @objc func cancel() { window?.sheetParent?.endSheet(window!) }
}
