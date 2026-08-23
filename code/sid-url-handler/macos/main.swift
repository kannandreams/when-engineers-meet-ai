import AppKit
import Foundation

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationWillFinishLaunching(_ notification: Notification) {
        NSAppleEventManager.shared().setEventHandler(
            self,
            andSelector: #selector(handleGetURLEvent(_:withReplyEvent:)),
            forEventClass: AEEventClass(kInternetEventClass),
            andEventID: AEEventID(kAEGetURL)
        )
    }

    @objc
    func handleGetURLEvent(
        _ event: NSAppleEventDescriptor,
        withReplyEvent replyEvent: NSAppleEventDescriptor
    ) {
        guard let sidURL = event
            .paramDescriptor(forKeyword: AEKeyword(keyDirectObject))?
            .stringValue
        else {
            log("Failed to read sid:// URL")
            return
        }

        log("Received URL: \(sidURL)")

        let process = Process()

        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [
            "python3",
            "YOUR_FOLDER_PATH/sid.py", // Replace YOUR_FOLDER_PATH with the actual path to sid.py
            sidURL
        ]

        let outputPipe = Pipe()
        let errorPipe = Pipe()

        process.standardOutput = outputPipe
        process.standardError = errorPipe

        do {
            try process.run()
            process.waitUntilExit()

            let stdout = outputPipe.fileHandleForReading.readDataToEndOfFile()
            let stderr = errorPipe.fileHandleForReading.readDataToEndOfFile()

            if let output = String(data: stdout, encoding: .utf8),
               !output.isEmpty {
                log("Python stdout:\n\(output)")
            }

            if let error = String(data: stderr, encoding: .utf8),
               !error.isEmpty {
                log("Python stderr:\n\(error)")
            }

            log("Python exited with status: \(process.terminationStatus)")
        } catch {
            log("Failed to launch sid.py: \(error)")
        }
    }

    private func log(_ message: String) {
        let path = "/tmp/sid-url-handler.log"
        let line = "[\(Date())] \(message)\n"

        guard let data = line.data(using: .utf8) else {
            return
        }

        if FileManager.default.fileExists(atPath: path),
           let handle = FileHandle(forWritingAtPath: path) {
            handle.seekToEndOfFile()
            handle.write(data)
            try? handle.close()
        } else {
            FileManager.default.createFile(
                atPath: path,
                contents: data
            )
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()

app.delegate = delegate
app.run()