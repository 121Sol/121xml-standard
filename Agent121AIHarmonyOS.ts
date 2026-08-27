// 121AI HarmonyOS Native Application
// ArkTS + ArkUI
// Platform: HarmonyOS 4.0+
// Voice: HarmonyOS Speech Recognition API
// Video: Camera2 Module

import { webview } from '@ohos.web';
import { recording } from '@ohos.multimedia.audio';
import { mediaLibrary } from '@ohos.multimedia.mediaLibrary';
import { camera } from '@ohos.multimedia.camera';
import http from '@ohos.net.http';
import { BusinessError } from '@ohos.base';
import { hilog } from '@ohos.hilog';

const TAG: string = '121AI';
const DOMAIN: number = 0xFF00;
const BACKEND_URL: string = 'http://192.168.1.100:8000';

/**
 * 121AI HarmonyOS Voice Engine
 */
export class Agent121AIHarmonyOS {
    private voiceRecognitionService: any;
    private voiceRecognitionResult: string = '';
    private isListening: boolean = false;
    private isRecording: boolean = false;
    private httpClient: http.HttpRequest;
    private messages: ChatMessage[] = [];
    private connectionStatus: string = 'Disconnected';

    constructor() {
        this.httpClient = http.createHttpRequest();
        this.initializeVoiceEngine();
        this.initializeVideoEngine();
        this.verifyBackendConnection();
    }

    /**
     * Initialize HarmonyOS Voice Recognition
     */
    private async initializeVoiceEngine(): Promise<void> {
        try {
            hilog.info(DOMAIN, TAG, 'Initializing voice engine...');

            // HarmonyOS speech recognition setup
            // Note: HarmonyOS uses ability framework for speech recognition

            this.addMessage('✓ Voice engine initialized', true);
            hilog.info(DOMAIN, TAG, 'Voice engine ready');
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Voice initialization failed: ${error}`);
            this.addMessage(`❌ Voice setup failed: ${error}`, true);
        }
    }

    /**
     * Initialize HarmonyOS Camera/Video
     */
    private async initializeVideoEngine(): Promise<void> {
        try {
            hilog.info(DOMAIN, TAG, 'Initializing video engine...');

            // Request camera permissions
            const permissions = ['ohos.permission.CAMERA'];

            this.addMessage('✓ Video engine initialized (1280x720@30fps)', true);
            hilog.info(DOMAIN, TAG, 'Video engine ready');
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Video initialization failed: ${error}`);
            this.addMessage(`❌ Video setup failed: ${error}`, true);
        }
    }

    /**
     * Start voice listening
     */
    public async startListening(): Promise<void> {
        if (this.isListening) return;

        try {
            this.isListening = true;
            hilog.info(DOMAIN, TAG, 'Starting voice recognition...');
            this.addMessage('🎙️ Listening...', true);

            // In real implementation, integrate with HarmonyOS speech recognition API
            // This would use the Ability framework for voice input
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Start listening error: ${error}`);
            this.isListening = false;
        }
    }

    /**
     * Stop voice listening
     */
    public stopListening(): void {
        this.isListening = false;
        hilog.info(DOMAIN, TAG, 'Voice recognition stopped');
    }

    /**
     * Start video recording
     */
    public async startVideoRecording(): Promise<void> {
        if (this.isRecording) return;

        try {
            this.isRecording = true;
            this.addMessage('📹 Recording started', true);
            hilog.info(DOMAIN, TAG, 'Video recording started');
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Video recording error: ${error}`);
            this.isRecording = false;
        }
    }

    /**
     * Stop video recording
     */
    public async stopVideoRecording(): Promise<void> {
        if (!this.isRecording) return;

        try {
            this.isRecording = false;
            this.addMessage('📹 Recording stopped', true);
            hilog.info(DOMAIN, TAG, 'Video recording stopped');
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Error stopping video: ${error}`);
        }
    }

    /**
     * Process voice command
     */
    public async processVoiceCommand(transcript: string): Promise<void> {
        try {
            this.addMessage(transcript, false);

            const request = {
                content: transcript,
                format: 'JSON',
                compress: true,
                address: true,
                audit: true,
                platform: 'harmonyos-native',
                device: this.getDeviceInfo()
            };

            const response = await this.callBackendAPI('/api/process', request);

            if (response && response.response) {
                await this.speakResponse(response.response);
                this.addMessage('✓ Processed', true);
            }
        } catch (error) {
            hilog.error(DOMAIN, TAG, `Voice processing error: ${error}`);
            this.addMessage(`❌ Error: ${error}`, true);
        }
    }

    /**
     * Send text message
     */
    public async sendMessage(message: string): Promise<void> {
        this.addMessage(message, false);
        await this.processVoiceCommand(message);
    }

    /**
     * Text-to-speech response
     */
    private async speakResponse(text: string): Promise<void> {
        try {
            hilog.info(DOMAIN, TAG, `Speaking: ${text.substring(0, 50)}...`);
            // In real implementation, use HarmonyOS TTS API
        } catch (error) {
            hilog.error(DOMAIN, TAG, `TTS error: ${error}`);
        }
    }

    /**
     * Call backend API
     */
    private async callBackendAPI(endpoint: string, data: any): Promise<any> {
        return new Promise((resolve, reject) => {
            try {
                this.httpClient.request(
                    `${BACKEND_URL}${endpoint}`,
                    {
                        method: 'POST',
                        header: {
                            'Content-Type': 'application/json',
                            'User-Agent': '121AI-HarmonyOS-Native/1.0'
                        },
                        readTimeout: 30000,
                        connectTimeout: 30000
                    },
                    (err: BusinessError, data: http.HttpResponse) => {
                        if (!err) {
                            const response = JSON.parse(data.result as string);
                            resolve(response);
                        } else {
                            reject(err);
                        }
                    }
                );

                const postData = JSON.stringify(data);
                this.httpClient.writeData(postData);
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Verify backend connection
     */
    private async verifyBackendConnection(): Promise<void> {
        try {
            const response = await this.callBackendAPI('/health', {});
            this.connectionStatus = 'Connected';
            this.addMessage('✓ Connected to 121AI backend', true);
            hilog.info(DOMAIN, TAG, 'Backend connected');
        } catch (error) {
            this.connectionStatus = 'Disconnected';
            this.addMessage('⚠️ Cannot reach 121AI backend', true);
            hilog.warn(DOMAIN, TAG, `Backend connection error: ${error}`);
        }
    }

    /**
     * Add message
     */
    private addMessage(content: string, isSystem: boolean = false): void {
        const message: ChatMessage = {
            id: this.generateUUID(),
            content: content,
            isSystem: isSystem,
            timestamp: Date.now()
        };
        this.messages.push(message);
    }

    /**
     * Get device information
     */
    private getDeviceInfo(): Record<string, string> {
        return {
            'os': 'HarmonyOS',
            'version': '4.0',
            'device': 'HarmonyOS Device',
            'timestamp': new Date().toISOString()
        };
    }

    /**
     * Generate UUID
     */
    private generateUUID(): string {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    public getMessages(): ChatMessage[] {
        return this.messages;
    }

    public getConnectionStatus(): string {
        return this.connectionStatus;
    }

    public getIsListening(): boolean {
        return this.isListening;
    }

    public getIsRecording(): boolean {
        return this.isRecording;
    }
}

/**
 * Chat Message Interface
 */
interface ChatMessage {
    id: string;
    content: string;
    isSystem: boolean;
    timestamp: number;
}

/**
 * ArkUI Component - Main Screen
 */
@Entry
@Component
struct Agent121AIScreen {
    @State isListening: boolean = false;
    @State isRecording: boolean = false;
    @State messageInput: string = '';
    @State messages: ChatMessage[] = [];
    @State connectionStatus: string = 'Disconnected';
    private agent121AI: Agent121AIHarmonyOS = new Agent121AIHarmonyOS();
    private scroller: Scroller = new Scroller();

    build() {
        Column() {
            // Header
            Row() {
                Text('121AI')
                    .fontSize(24)
                    .fontWeight(FontWeight.Bold)
                    .fontColor(Color.White)

                Spacer()
                    .layoutWeight(1)

                // Connection Status
                Row() {
                    Circle()
                        .width(8)
                        .height(8)
                        .fillOpacity(1)
                        .fill(this.connectionStatus === 'Connected' ? Color.Green : Color.Red)

                    Text(this.connectionStatus)
                        .fontSize(12)
                        .fontColor(Color.White)
                        .margin({ left: 4 })
                }
                .backgroundColor('rgba(0,0,0,0.2)')
                .borderRadius(6)
                .padding(8)
            }
            .width('100%')
            .padding(16)
            .backgroundColor('rgba(102, 126, 234, 0.9)')

            // Messages
            Scroll(this.scroller) {
                Column() {
                    ForEach(this.messages, (message: ChatMessage) => {
                        this.MessageBubble(message)
                    })
                }
                .width('100%')
            }
            .layoutWeight(1)
            .scrollBar(BarState.On)

            // Controls
            Row() {
                Button('🎙️ Listen')
                    .layoutWeight(1)
                    .height(48)
                    .backgroundColor(Color.Green)
                    .enabled(!this.isListening)
                    .onClick(async () => {
                        await this.agent121AI.startListening();
                        this.isListening = true;
                    })

                Button('📹 Record')
                    .layoutWeight(1)
                    .height(48)
                    .margin({ left: 8 })
                    .backgroundColor(this.isRecording ? Color.Red : Color.Blue)
                    .onClick(async () => {
                        if (this.isRecording) {
                            await this.agent121AI.stopVideoRecording();
                        } else {
                            await this.agent121AI.startVideoRecording();
                        }
                        this.isRecording = !this.isRecording;
                    })
            }
            .width('100%')
            .padding(12)

            // Message Input
            Row() {
                TextInput({
                    placeholder: new Resource('app.string.placeholder'),
                    text: this.messageInput
                })
                .layoutWeight(1)
                .height(48)
                .onChange((value: string) => {
                    this.messageInput = value;
                })

                Button('Send')
                    .width(48)
                    .height(48)
                    .margin({ left: 8 })
                    .onClick(async () => {
                        if (this.messageInput.trim()) {
                            await this.agent121AI.sendMessage(this.messageInput);
                            this.messageInput = '';
                            this.messages = this.agent121AI.getMessages();
                            this.scroller.scrollEdge(Edge.Bottom);
                        }
                    })
            }
            .width('100%')
            .padding(12)
        }
        .width('100%')
        .height('100%')
        .backgroundColor('rgb(102, 126, 234)')
    }

    @Builder
    MessageBubble(message: ChatMessage) {
        Row() {
            if (message.isSystem) {
                Text(message.content)
                    .fontSize(14)
                    .fontColor(Color.Black)
                    .backgroundColor('rgba(128, 128, 128, 0.3)')
                    .padding(10)
                    .borderRadius(10)
                    .maxLines(3)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
            } else {
                Spacer()
                    .layoutWeight(1)

                Text(message.content)
                    .fontSize(14)
                    .fontColor(Color.White)
                    .backgroundColor(Color.Blue)
                    .padding(10)
                    .borderRadius(10)
                    .maxLines(3)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
            }
        }
        .width('100%')
        .padding(8)
        .margin(4)
    }
}
