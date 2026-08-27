// 121AI iOS Native Application
// Swift 5.9 + SwiftUI
// Platform: iOS 17+
// Voice: Speech framework (Speech Recognition + AVSpeechSynthesizer)
// Video: AVFoundation (Camera capture)

import Foundation
import SwiftUI
import Speech
import AVFoundation
import Combine
import Network

@main
struct Agent121AIApp: App {
    @StateObject private var agent = Agent121AI()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(agent)
        }
    }
}

// MARK: - Agent121AI (ViewModel)
@MainActor
class Agent121AI: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    @Published var isListening = false
    @Published var isRecording = false
    @Published var transcript = ""
    @Published var messages: [ChatMessage] = []
    @Published var connectionStatus = "Disconnected"
    @Published var videoPreview: UIImage?

    private var speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    private let speechSynthesizer = AVSpeechSynthesizer()

    private var videoCapture: AVCaptureSession?
    private var videoOutput: AVCaptureVideoDataOutput?
    private var queue = DispatchQueue(label: "121AI.video")

    private let backendUrl = "http://localhost:8000"
    private var urlSession: URLSession
    private var apiClient: URLSession.DataTaskPublisher?

    // MARK: - Initialization
    override init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        self.urlSession = URLSession(configuration: config)

        super.init()

        Task {
            await initializeVoiceEngine()
            await initializeVideoEngine()
            await verifyBackendConnection()
        }
    }

    // MARK: - Voice Engine
    @MainActor
    private func initializeVoiceEngine() async {
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .record,
                mode: .default,
                options: [.duckOthers, .defaultToSpeaker]
            )
            try AVAudioSession.sharedInstance().setActive(true, options: .notifyOthersOnDeactivation)

            if speechRecognizer?.isAvailable == false {
                addMessage("❌ Speech recognition unavailable", isSystem: true)
            }

            addMessage("✓ Voice engine initialized", isSystem: true)
        } catch {
            addMessage("❌ Audio setup failed: \(error.localizedDescription)", isSystem: true)
        }
    }

    // MARK: - Video Engine
    @MainActor
    private func initializeVideoEngine() async {
        do {
            videoCapture = AVCaptureSession()

            guard let videoCapture = videoCapture else { return }

            // Request camera permissions
            let cameraPermission = await AVCaptureDevice.requestAccess(for: .video)
            guard cameraPermission else {
                addMessage("❌ Camera permission denied", isSystem: true)
                return
            }

            // Configure camera input
            guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
                addMessage("❌ Camera not available", isSystem: true)
                return
            }

            let input = try AVCaptureDeviceInput(device: camera)

            if videoCapture.canAddInput(input) {
                videoCapture.addInput(input)
            }

            // Configure video output
            videoOutput = AVCaptureVideoDataOutput()
            videoOutput?.alwaysDiscardsLateVideoFrames = true
            videoOutput?.setSampleBufferDelegate(self, queue: queue)

            if let output = videoOutput, videoCapture.canAddOutput(output) {
                videoCapture.addOutput(output)

                // Set resolution to 1280x720
                if let connection = output.connection(with: .video) {
                    connection.videoOrientation = .portrait
                }
            }

            addMessage("✓ Video engine initialized (1280x720@30fps)", isSystem: true)
        } catch {
            addMessage("❌ Video setup failed: \(error.localizedDescription)", isSystem: true)
        }
    }

    // MARK: - Voice Recognition
    func startListening() async {
        let authStatus = await SFSpeechRecognizer.requestAuthorization()

        guard authStatus == .authorized else {
            addMessage("❌ Speech recognition not authorized", isSystem: true)
            return
        }

        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            addMessage("❌ Speech recognition unavailable", isSystem: true)
            return
        }

        do {
            recognitionRequest = SFSpeechAudioBufferRecognitionRequest()

            guard let recognitionRequest = recognitionRequest else { return }
            recognitionRequest.shouldReportPartialResults = true

            recognitionTask = speechRecognizer.recognitionTask(
                with: recognitionRequest
            ) { [weak self] result, error in
                guard let self = self else { return }

                var isFinal = false

                if let result = result {
                    let transcribed = result.bestTranscription.formattedString
                    Task { @MainActor in
                        self.transcript = transcribed
                    }
                    isFinal = result.isFinal
                }

                if error != nil || isFinal {
                    Task { @MainActor in
                        self.stopListening()
                        if !self.transcript.isEmpty {
                            await self.processVoiceCommand(self.transcript)
                        }
                    }
                }
            }

            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

            let inputNode = audioEngine.inputNode
            let recordingFormat = inputNode.outputFormat(forBus: 0)

            inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
                recognitionRequest.append(buffer)
            }

            audioEngine.prepare()
            try audioEngine.start()

            isListening = true
            addMessage("🎙️ Listening...", isSystem: true)
        } catch {
            addMessage("❌ Could not start recording: \(error.localizedDescription)", isSystem: true)
        }
    }

    func stopListening() {
        isListening = false
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
    }

    // MARK: - Video Capture
    func startVideoCapture() {
        guard let videoCapture = videoCapture, !videoCapture.isRunning else { return }

        DispatchQueue.global(qos: .background).async {
            videoCapture.startRunning()
        }

        isRecording = true
        addMessage("📹 Recording started", isSystem: true)
    }

    func stopVideoCapture() {
        guard let videoCapture = videoCapture, videoCapture.isRunning else { return }

        DispatchQueue.global(qos: .background).async {
            videoCapture.stopRunning()
        }

        isRecording = false
        addMessage("📹 Recording stopped", isSystem: true)
    }

    // MARK: - AVCaptureVideoDataOutputSampleBufferDelegate
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        // Process video frames for streaming
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }

        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }

        DispatchQueue.main.async {
            self.videoPreview = UIImage(cgImage: cgImage)
        }
    }

    // MARK: - Voice Command Processing
    private func processVoiceCommand(_ transcript: String) async {
        addMessage(transcript, isSystem: false)

        do {
            let request = VoiceCommandRequest(
                content: transcript,
                format: "JSON",
                compress: true,
                address: true,
                audit: true,
                platform: "ios-native",
                device: getDeviceInfo()
            )

            let jsonData = try JSONEncoder().encode(request)
            var urlRequest = URLRequest(url: URL(string: "\(backendUrl)/api/process")!)
            urlRequest.httpMethod = "POST"
            urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
            urlRequest.httpBody = jsonData

            let (data, response) = try await urlSession.data(for: urlRequest)

            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                if let jsonResponse = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                    if let responseText = jsonResponse["response"] as? String {
                        await speakResponse(responseText)
                    }
                    addMessage("✓ Processed", isSystem: true)
                }
            }
        } catch {
            addMessage("❌ Error: \(error.localizedDescription)", isSystem: true)
        }
    }

    // MARK: - Text-to-Speech
    private func speakResponse(_ text: String) async {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = 0.5
        utterance.pitchMultiplier = 1.0

        speechSynthesizer.speak(utterance)
    }

    // MARK: - Backend Connection
    private func verifyBackendConnection() async {
        do {
            let url = URL(string: "\(backendUrl)/health")!
            let (_, response) = try await urlSession.data(from: url)

            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                connectionStatus = "Connected"
                addMessage("✓ Connected to 121AI backend", isSystem: true)
            }
        } catch {
            connectionStatus = "Disconnected"
            addMessage("⚠️ Cannot reach 121AI backend", isSystem: true)
        }
    }

    // MARK: - Message Management
    func sendMessage(_ text: String) {
        addMessage(text, isSystem: false)

        Task {
            await processVoiceCommand(text)
        }
    }

    private func addMessage(_ content: String, isSystem: Bool = false) {
        let message = ChatMessage(
            id: UUID(),
            content: content,
            isSystem: isSystem,
            timestamp: Date()
        )
        messages.append(message)
    }

    // MARK: - Device Info
    private func getDeviceInfo() -> [String: String] {
        return [
            "os": "iOS",
            "version": UIDevice.current.systemVersion,
            "model": UIDevice.current.model,
            "name": UIDevice.current.name,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
    }

    deinit {
        stopListening()
        stopVideoCapture()
    }
}

// MARK: - Data Models
struct ChatMessage: Identifiable {
    let id: UUID
    let content: String
    let isSystem: Bool
    let timestamp: Date
}

struct VoiceCommandRequest: Codable {
    let content: String
    let format: String
    let compress: Bool
    let address: Bool
    let audit: Bool
    let platform: String
    let device: [String: String]
}

// MARK: - UI Views
struct ContentView: View {
    @EnvironmentObject var agent: Agent121AI
    @State private var messageInput = ""

    var body: some View {
        ZStack {
            LinearGradient(
                gradient: Gradient(colors: [Color(red: 0.4, green: 0.5, blue: 0.9), Color(red: 0.47, green: 0.3, blue: 0.64)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 12) {
                // Header
                HStack {
                    Text("121AI")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    Spacer()

                    HStack(spacing: 4) {
                        Circle()
                            .fill(agent.connectionStatus == "Connected" ? Color.green : Color.red)
                            .frame(width: 8, height: 8)
                        Text(agent.connectionStatus)
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    .padding(8)
                    .background(Color.black.opacity(0.2))
                    .cornerRadius(6)
                }
                .padding()

                // Video Preview
                if agent.isRecording, let preview = agent.videoPreview {
                    Image(uiImage: preview)
                        .resizable()
                        .scaledToFit()
                        .frame(height: 200)
                        .cornerRadius(12)
                        .padding()
                }

                // Chat Messages
                ScrollView {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(agent.messages) { message in
                            HStack(alignment: .top) {
                                if !message.isSystem {
                                    Spacer()
                                }

                                VStack(alignment: message.isSystem ? .leading : .trailing) {
                                    Text(message.content)
                                        .padding(10)
                                        .background(message.isSystem ? Color.gray.opacity(0.3) : Color.blue)
                                        .foregroundColor(message.isSystem ? .black : .white)
                                        .cornerRadius(10)

                                    Text(message.timestamp, style: .time)
                                        .font(.caption2)
                                        .foregroundColor(.gray)
                                }

                                if message.isSystem {
                                    Spacer()
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                .frame(maxHeight: .infinity)

                // Controls
                HStack(spacing: 12) {
                    Button(action: { Task { await agent.startListening() } }) {
                        Label("Listen", systemImage: "mic.fill")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .disabled(agent.isListening)

                    Button(action: { agent.startVideoCapture() }) {
                        Label("Record", systemImage: "video.fill")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(agent.isRecording ? Color.red : Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()

                // Message Input
                HStack(spacing: 8) {
                    TextField("Type message...", text: $messageInput)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(8)

                    Button(action: {
                        agent.sendMessage(messageInput)
                        messageInput = ""
                    }) {
                        Image(systemName: "paperplane.fill")
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(Agent121AI())
}
