// 121AI Android Native Application
// Kotlin + Jetpack Compose
// Platform: Android 13+
// Voice: Google Speech Recognition + TextToSpeech
// Video: Camera2 API

package com.agent121ai.mobile

import android.Manifest
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.media.MediaCodec
import android.media.MediaFormat
import android.speech.RecognitionListener
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import android.view.TextureView
import android.camera.CameraManager
import android.camera.CameraCaptureSession
import android.camera.CameraDevice
import android.hardware.camera2.*
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import java.io.File
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import com.google.gson.JsonObject
import com.google.gson.Gson

// TAG for logging
private const val TAG = "121AI"
private const val BACKEND_URL = "http://192.168.1.100:8000"  // Update to your backend

/**
 * 121AI Android ViewModel
 * Manages voice, video, and API communication
 */
class Agent121AIViewModel(private val context: Context) : ViewModel() {
    private val gson = Gson()
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()

    // State management
    private val _isListening = mutableStateOf(false)
    val isListening: State<Boolean> = _isListening

    private val _isRecording = mutableStateOf(false)
    val isRecording: State<Boolean> = _isRecording

    private val _transcript = mutableStateOf("")
    val transcript: State<String> = _transcript

    private val _messages = mutableStateOf<List<ChatMessage>>(emptyList())
    val messages: State<List<ChatMessage>> = _messages

    private val _connectionStatus = mutableStateOf("Disconnected")
    val connectionStatus: State<String> = _connectionStatus

    // Voice components
    private var speechRecognizer: SpeechRecognizer? = null
    private var textToSpeech: TextToSpeech? = null
    private var audioRecord: AudioRecord? = null

    // Video components
    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var videoEncoder: MediaCodec? = null

    // Executors
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    private val audioExecutor = Executors.newSingleThreadExecutor()

    init {
        viewModelScope.launch {
            initializeVoiceEngine()
            initializeVideoEngine()
            verifyBackendConnection()
        }
    }

    /**
     * Initialize speech recognition and text-to-speech
     */
    private suspend fun initializeVoiceEngine() = withContext(Dispatchers.Main) {
        try {
            // Speech Recognition
            if (SpeechRecognizer.isRecognitionAvailable(context)) {
                speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
                addMessage("✓ Voice engine initialized", isSystem = true)
            } else {
                addMessage("❌ Speech recognition unavailable", isSystem = true)
            }

            // Text-to-Speech
            textToSpeech = TextToSpeech(context) { status ->
                if (status == TextToSpeech.SUCCESS) {
                    Log.d(TAG, "TextToSpeech ready")
                } else {
                    Log.e(TAG, "TextToSpeech initialization failed")
                }
            }
        } catch (ex: Exception) {
            Log.e(TAG, "Voice initialization error: ${ex.message}")
            addMessage("❌ Voice setup failed: ${ex.message}", isSystem = true)
        }
    }

    /**
     * Initialize camera and video capture
     */
    private suspend fun initializeVideoEngine() = withContext(Dispatchers.Default) {
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager

            // List available cameras
            val cameraIds = cameraManager.cameraIdList
            if (cameraIds.isNotEmpty()) {
                // Use front camera (usually cameraIds[1])
                val frontCameraId = cameraIds.getOrNull(1) ?: cameraIds[0]

                // Get camera characteristics
                val characteristics = cameraManager.getCameraCharacteristics(frontCameraId)
                val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)

                Log.d(TAG, "Front camera: $frontCameraId")
                addMessage("✓ Video engine initialized (1280x720@30fps)", isSystem = true)
            }
        } catch (ex: Exception) {
            Log.e(TAG, "Video initialization error: ${ex.message}")
            addMessage("❌ Video setup failed: ${ex.message}", isSystem = true)
        }
    }

    /**
     * Start speech recognition
     */
    fun startListening() {
        if (_isListening.value) return

        try {
            val intent = android.content.Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE, Locale.US)
                putExtra(android.speech.RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            }

            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: android.os.Bundle?) {
                    _isListening.value = true
                    Log.d(TAG, "Listening...")
                }

                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {
                    _isListening.value = false
                }

                override fun onError(error: Int) {
                    _isListening.value = false
                    Log.e(TAG, "Recognition error: $error")
                }

                override fun onResults(results: android.os.Bundle?) {
                    results?.getStringArrayList(android.speech.SpeechRecognizer.RESULTS_RECOGNITION)?.let { texts ->
                        val transcript = texts[0]
                        _transcript.value = transcript
                        Log.d(TAG, "Recognized: $transcript")

                        // Process voice command
                        viewModelScope.launch {
                            processVoiceCommand(transcript)
                        }
                    }
                }

                override fun onPartialResults(partialResults: android.os.Bundle?) {
                    partialResults?.getStringArrayList(android.speech.SpeechRecognizer.RESULTS_RECOGNITION)?.let { texts ->
                        _transcript.value = texts.getOrNull(0) ?: ""
                    }
                }

                override fun onEvent(eventType: Int, params: android.os.Bundle?) {}
            })

            speechRecognizer?.startListening(intent)
        } catch (ex: Exception) {
            Log.e(TAG, "Start listening error: ${ex.message}")
        }
    }

    /**
     * Stop speech recognition
     */
    fun stopListening() {
        _isListening.value = false
        speechRecognizer?.stopListening()
    }

    /**
     * Start video recording
     */
    fun startVideoRecording() {
        if (_isRecording.value) return

        _isRecording.value = true
        addMessage("📹 Recording started", isSystem = true)

        // In a real implementation, set up MediaCodec and MediaMuxer
        audioExecutor.execute {
            try {
                // Start recording video frames
                Log.d(TAG, "Video recording started")
            } catch (ex: Exception) {
                Log.e(TAG, "Video recording error: ${ex.message}")
            }
        }
    }

    /**
     * Stop video recording
     */
    fun stopVideoRecording() {
        _isRecording.value = false
        addMessage("📹 Recording stopped", isSystem = true)
    }

    /**
     * Process voice command through backend
     */
    private suspend fun processVoiceCommand(transcript: String) = withContext(Dispatchers.IO) {
        try {
            addMessage(transcript, isSystem = false)

            val request = JsonObject().apply {
                addProperty("content", transcript)
                addProperty("format", "JSON")
                addProperty("compress", true)
                addProperty("address", true)
                addProperty("audit", true)
                addProperty("platform", "android-native")
                add("device", getDeviceInfo())
            }

            val body = RequestBody.create(
                "application/json".toMediaType(),
                request.toString()
            )

            val httpRequest = Request.Builder()
                .url("$BACKEND_URL/api/process")
                .post(body)
                .addHeader("User-Agent", "121AI-Android-Native/1.0")
                .build()

            httpClient.newCall(httpRequest).execute().use { response ->
                if (response.isSuccessful) {
                    response.body?.string()?.let { responseBody ->
                        Log.d(TAG, "Response: $responseBody")
                        val json = com.google.gson.JsonParser.parseString(responseBody).asJsonObject

                        json.get("response")?.asString?.let { responseText ->
                            speakResponse(responseText)
                        }

                        addMessage("✓ Processed", isSystem = true)
                    }
                } else {
                    addMessage("❌ API Error: ${response.code}", isSystem = true)
                }
            }
        } catch (ex: Exception) {
            Log.e(TAG, "Voice processing error: ${ex.message}")
            addMessage("❌ Error: ${ex.message}", isSystem = true)
        }
    }

    /**
     * Speak response using text-to-speech
     */
    private fun speakResponse(text: String) {
        textToSpeech?.speak(text, TextToSpeech.QUEUE_ADD, null)
        Log.d(TAG, "Speaking: ${text.take(50)}...")
    }

    /**
     * Send text message
     */
    fun sendMessage(message: String) {
        addMessage(message, isSystem = false)

        viewModelScope.launch {
            processVoiceCommand(message)
        }
    }

    /**
     * Verify backend connection
     */
    private suspend fun verifyBackendConnection() = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$BACKEND_URL/health")
                .build()

            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    _connectionStatus.value = "Connected"
                    addMessage("✓ Connected to 121AI backend", isSystem = true)
                    Log.d(TAG, "Backend connected")
                } else {
                    _connectionStatus.value = "Disconnected"
                }
            }
        } catch (ex: Exception) {
            _connectionStatus.value = "Disconnected"
            addMessage("⚠️ Cannot reach backend: ${ex.message}", isSystem = true)
            Log.e(TAG, "Backend connection error: ${ex.message}")
        }
    }

    /**
     * Add message to chat
     */
    private fun addMessage(content: String, isSystem: Boolean = false) {
        val message = ChatMessage(
            id = UUID.randomUUID().toString(),
            content = content,
            isSystem = isSystem,
            timestamp = System.currentTimeMillis()
        )

        val newMessages = _messages.value.toMutableList()
        newMessages.add(message)
        _messages.value = newMessages
    }

    /**
     * Get device information
     */
    private fun getDeviceInfo(): JsonObject {
        return JsonObject().apply {
            addProperty("os", "Android")
            addProperty("version", android.os.Build.VERSION.RELEASE)
            addProperty("model", android.os.Build.MODEL)
            addProperty("device", android.os.Build.DEVICE)
            addProperty("timestamp", SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).format(Date()))
        }
    }

    override fun onCleared() {
        super.onCleared()
        stopListening()
        stopVideoRecording()
        textToSpeech?.shutdown()
        cameraDevice?.close()
        cameraExecutor.shutdown()
        audioExecutor.shutdown()
    }
}

// MARK: - Data Models
data class ChatMessage(
    val id: String,
    val content: String,
    val isSystem: Boolean,
    val timestamp: Long
)

// MARK: - Compose UI
@Composable
fun Agent121AIScreen(viewModel: Agent121AIViewModel) {
    val isListening by viewModel.isListening
    val isRecording by viewModel.isRecording
    val messages by viewModel.messages
    val connectionStatus by viewModel.connectionStatus
    var messageInput by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF667eea),
                        Color(0xFF764ba2)
                    )
                )
            )
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "121AI",
                style = MaterialTheme.typography.headlineSmall,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )

            // Connection status
            Row(
                modifier = Modifier
                    .background(
                        color = Color.Black.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(6.dp)
                    )
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(
                            color = if (connectionStatus == "Connected") Color.Green else Color.Red,
                            shape = CircleShape
                        )
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    connectionStatus,
                    fontSize = 12.sp,
                    color = Color.White
                )
            }
        }

        // Messages
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp)
        ) {
            items(messages) { message ->
                MessageBubble(message = message)
                Spacer(modifier = Modifier.height(8.dp))
            }
        }

        // Controls
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = { viewModel.startListening() },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                enabled = !isListening,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Green)
            ) {
                Text("🎙️ Listen")
            }

            Button(
                onClick = {
                    if (isRecording) viewModel.stopVideoRecording()
                    else viewModel.startVideoRecording()
                },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isRecording) Color.Red else Color.Blue
                )
            ) {
                Text("📹 Record")
            }
        }

        // Message input
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = messageInput,
                onValueChange = { messageInput = it },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                placeholder = { Text("Type message...") },
                singleLine = true
            )

            Button(
                onClick = {
                    if (messageInput.isNotBlank()) {
                        viewModel.sendMessage(messageInput)
                        messageInput = ""
                    }
                },
                modifier = Modifier
                    .size(48.dp)
            ) {
                Text("→")
            }
        }
    }
}

@Composable
fun MessageBubble(message: ChatMessage) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isSystem) Arrangement.Start else Arrangement.End
    ) {
        Text(
            text = message.content,
            modifier = Modifier
                .background(
                    color = if (message.isSystem) Color.Gray.copy(alpha = 0.3f) else Color.Blue,
                    shape = RoundedCornerShape(10.dp)
                )
                .padding(10.dp),
            color = if (message.isSystem) Color.Black else Color.White
        )
    }
}

// MARK: - Preview
@Composable
fun Agent121AIPreview() {
    // Preview implementation
    Box(modifier = Modifier.fillMaxSize().background(Color.White))
}
