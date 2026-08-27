// 121AI Windows Native Application
// C# .NET 8 + Windows App SDK (WinUI 3)
// Platform: Windows 10/11
// Voice: Windows.Media.SpeechRecognition, Text-to-Speech
// Video: Windows.Media.Capture

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Windows.Media.SpeechRecognition;
using Windows.Media.SpeechSynthesis;
using Windows.Media.Capture;
using Windows.Media.MediaProperties;
using Windows.Storage;
using Windows.Networking.Connectivity;
using System.Net.Http;
using System.Text.Json;
using System.Diagnostics;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.Foundation;

namespace Agent121AI.Windows
{
    /// <summary>
    /// 121AI Native Windows Application
    /// Full integration with Windows voice, video, and API backend
    /// </summary>
    public class Agent121AIWindows
    {
        private MediaCapture mediaCapture;
        private SpeechRecognizer speechRecognizer;
        private SpeechSynthesizer speechSynthesizer;
        private HttpClient apiClient;
        private bool isRecording = false;
        private bool isListening = false;
        private string backendUrl = "http://localhost:8000";

        public event EventHandler<VoiceEventArgs> OnVoiceInput;
        public event EventHandler<VideoEventArgs> OnVideoFrame;
        public event EventHandler<MessageEventArgs> OnMessage;

        public Agent121AIWindows()
        {
            apiClient = new HttpClient();
            apiClient.DefaultRequestHeaders.Add("User-Agent", "121AI-Windows-Native/1.0");
        }

        /// <summary>
        /// Initialize 121AI Voice Engine
        /// </summary>
        public async Task InitializeVoiceEngine()
        {
            try
            {
                // Initialize speech recognizer
                speechRecognizer = new SpeechRecognizer();

                // Compile constraints
                var constraintsTopLevel = new SpeechRecognitionTopicConstraint(
                    SpeechRecognitionScenario.FormFilling,
                    "formFillingConstraint"
                );
                speechRecognizer.Constraints.Add(constraintsTopLevel);

                var result = await speechRecognizer.CompileConstraintsAsync();
                if (result.Status != SpeechRecognitionCompilationStatus.Success)
                {
                    throw new Exception($"Speech recognition compilation failed: {result.Status}");
                }

                // Initialize speech synthesizer
                speechSynthesizer = new SpeechSynthesizer();

                Debug.WriteLine("[121AI] Voice engine initialized");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Voice initialization failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Initialize 121AI Video Engine
        /// </summary>
        public async Task InitializeVideoEngine()
        {
            try
            {
                mediaCapture = new MediaCapture();

                var settings = new MediaCaptureInitializationSettings
                {
                    StreamingCaptureMode = StreamingCaptureMode.Video,
                    PhotoCaptureSource = PhotoCaptureSource.VideoPreview
                };

                await mediaCapture.InitializeAsync(settings);

                // Set up video encoding
                var videoProperties = mediaCapture.VideoDeviceController.GetMediaStreamProperties(
                    MediaStreamType.VideoPreview) as VideoEncodingProperties;

                videoProperties.Width = 1280;
                videoProperties.Height = 720;
                videoProperties.FrameRate.Numerator = 30;
                videoProperties.FrameRate.Denominator = 1;

                await mediaCapture.VideoDeviceController.SetMediaStreamPropertiesAsync(
                    MediaStreamType.VideoPreview, videoProperties);

                Debug.WriteLine("[121AI] Video engine initialized (1280x720@30fps)");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Video initialization failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Start voice recognition with continuous listening
        /// </summary>
        public async Task StartListening()
        {
            if (isListening) return;

            try
            {
                isListening = true;
                Debug.WriteLine("[121AI] Starting voice recognition...");

                while (isListening)
                {
                    var result = await speechRecognizer.RecognizeAsync();

                    if (result.Status == SpeechRecognitionResultStatus.Success)
                    {
                        var transcript = result.Text;
                        Debug.WriteLine($"[121AI VOICE] {transcript}");

                        OnVoiceInput?.Invoke(this, new VoiceEventArgs
                        {
                            Transcript = transcript,
                            Confidence = (float)result.Confidence,
                            Timestamp = DateTime.UtcNow
                        });

                        // Send to backend for processing
                        await ProcessVoiceCommand(transcript);
                    }
                    else if (result.Status == SpeechRecognitionResultStatus.NoMatch)
                    {
                        Debug.WriteLine("[121AI] No speech recognized");
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Voice recognition error: {ex.Message}");
                isListening = false;
            }
        }

        /// <summary>
        /// Stop voice recognition
        /// </summary>
        public void StopListening()
        {
            isListening = false;
            Debug.WriteLine("[121AI] Voice recognition stopped");
        }

        /// <summary>
        /// Start video capture and streaming
        /// </summary>
        public async Task StartVideoCapture()
        {
            if (isRecording) return;

            try
            {
                isRecording = true;
                Debug.WriteLine("[121AI] Starting video capture...");

                // Start preview
                var previewProperties = mediaCapture.VideoDeviceController.GetMediaStreamProperties(
                    MediaStreamType.VideoPreview) as VideoEncodingProperties;

                // Record video to file
                var videoFile = await ApplicationData.Current.LocalFolder.CreateFileAsync(
                    $"121ai_capture_{DateTime.Now:yyyyMMdd_HHmmss}.mp4",
                    CreationCollisionOption.GenerateUniqueName);

                var videoProfile = MediaEncodingProfile.CreateMp4(VideoEncodingQuality.Hd720p);

                await mediaCapture.StartRecordingToStorageFileAsync(videoProfile, videoFile);
                Debug.WriteLine($"[121AI] Video recording started: {videoFile.Path}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Video capture error: {ex.Message}");
                isRecording = false;
            }
        }

        /// <summary>
        /// Stop video capture
        /// </summary>
        public async Task StopVideoCapture()
        {
            if (!isRecording) return;

            try
            {
                await mediaCapture.StopRecordingAsync();
                isRecording = false;
                Debug.WriteLine("[121AI] Video recording stopped");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Error stopping video: {ex.Message}");
            }
        }

        /// <summary>
        /// Process voice command through 121AI backend
        /// </summary>
        private async Task ProcessVoiceCommand(string transcript)
        {
            try
            {
                var request = new
                {
                    content = transcript,
                    format = "JSON",
                    compress = true,
                    address = true,
                    audit = true,
                    platform = "windows-native",
                    device = GetDeviceInfo()
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await apiClient.PostAsync($"{backendUrl}/api/process", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<JsonElement>(responseBody);

                    Debug.WriteLine($"[121AI] Processed: {result}");

                    // Text-to-speech response
                    if (result.TryGetProperty("response", out var responseText))
                    {
                        await SpeakResponse(responseText.GetString());
                    }

                    OnMessage?.Invoke(this, new MessageEventArgs
                    {
                        Content = responseBody,
                        Timestamp = DateTime.UtcNow,
                        Status = "success"
                    });
                }
                else
                {
                    Debug.WriteLine($"[121AI ERROR] API error: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Processing failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Speak response using text-to-speech
        /// </summary>
        private async Task SpeakResponse(string text)
        {
            try
            {
                if (string.IsNullOrEmpty(text)) return;

                var stream = speechSynthesizer.SynthesizeTextToStreamAsync(text).AsTask();
                await stream;

                Debug.WriteLine($"[121AI TTS] Speaking: {text.Substring(0, Math.Min(50, text.Length))}...");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Text-to-speech error: {ex.Message}");
            }
        }

        /// <summary>
        /// Send message to backend API
        /// </summary>
        public async Task SendMessage(string message)
        {
            try
            {
                var request = new
                {
                    content = message,
                    format = "JSON",
                    compress = true,
                    platform = "windows-native"
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await apiClient.PostAsync($"{backendUrl}/api/process", content);
                var responseBody = await response.Content.ReadAsStringAsync();

                OnMessage?.Invoke(this, new MessageEventArgs
                {
                    Content = responseBody,
                    Timestamp = DateTime.UtcNow,
                    Status = response.IsSuccessStatusCode ? "success" : "error"
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Message send failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Get device information
        /// </summary>
        private Dictionary<string, string> GetDeviceInfo()
        {
            return new Dictionary<string, string>
            {
                { "os", "Windows" },
                { "version", Environment.OSVersion.VersionString },
                { "processor_count", Environment.ProcessorCount.ToString() },
                { "machine_name", Environment.MachineName },
                { "timestamp", DateTime.UtcNow.ToString("O") }
            };
        }

        /// <summary>
        /// Cleanup resources
        /// </summary>
        public async Task Cleanup()
        {
            try
            {
                if (isRecording)
                    await StopVideoCapture();

                if (isListening)
                    StopListening();

                mediaCapture?.Dispose();
                speechRecognizer?.Dispose();
                speechSynthesizer?.Dispose();
                apiClient?.Dispose();

                Debug.WriteLine("[121AI] Resources cleaned up");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Cleanup failed: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Event arguments for voice input
    /// </summary>
    public class VoiceEventArgs : EventArgs
    {
        public string Transcript { get; set; }
        public float Confidence { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Event arguments for video frames
    /// </summary>
    public class VideoEventArgs : EventArgs
    {
        public byte[] Frame { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Event arguments for messages
    /// </summary>
    public class MessageEventArgs : EventArgs
    {
        public string Content { get; set; }
        public DateTime Timestamp { get; set; }
        public string Status { get; set; }
    }
}
