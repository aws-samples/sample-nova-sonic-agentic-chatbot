'use client';

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import AudioCapture from '@/components/audio-capture';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { User, Bot, Mic, MicOff, Power, PowerOff, X, ChevronDown } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import AudioCaptureMediaRecorder from '@/components/audio-capture-mediarecorder';
import { ToolOutput } from '@/components/tool-outputs/ToolOutput';
import type { ToolOutput as ToolOutputType, FinanceAppToolOutput } from '@/components/tool-outputs/types';
import { AudioPlaybackService } from '@/components/audio-playback';
import { motion, AnimatePresence } from 'framer-motion';
import { FinanceApp, FinanceAction } from '@/components/apps/FinanceApp';
import type { FinanceState } from '@/components/apps/FinanceApp';

interface TextMessage {
  text: string;
  role: string;
}

interface ModelOption {
  id: string;
  name: string;
  description: string;
}

const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: 'amazon.nova-sonic-v1:0',
    name: 'Nova Sonic',
    description: 'Speech-to-speech model for conversational AI'
  },
  {
    id: 'amazon.nova-2-sonic-v1:0',
    name: 'Nova 2 Sonic',
    description: 'Enhanced multilingual speech-to-speech model'
  }
];

interface LanguageOption {
  code: string;
  name: string;
}

const AVAILABLE_LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'de', name: 'German' },
  { code: 'fr', name: 'French' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'hi', name: 'Hindi' },
];

// Add these message animation variants before the Home component
const messageVariants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.95
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 260,
      damping: 20
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 }
  }
};

const avatarVariants = {
  initial: { scale: 0 },
  animate: {
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 260,
      damping: 20,
      delay: 0.1
    }
  }
};

export default function Home() {
  const [status, setStatus] = useState('Disconnected');
  const [recording, setRecording] = useState(false);
  const [textOutputs, setTextOutputs] = useState<TextMessage[]>([]);
  const [toolUiOutput, setToolUiOutput] = useState<ToolOutputType | null>(null);
  const [currentTool, setCurrentTool] = useState<{ name: string, content: string } | null>(null);
  const [waitingForTool, setWaitingForTool] = useState(false);
  const [wsKey, setWsKey] = useState(0);
  const [isThinking, setIsThinking] = useState(false);
  const [toolConfigs, setToolConfigs] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>(AVAILABLE_MODELS[0].id);
  const [selectedLanguage, setSelectedLanguage] = useState<string>(AVAILABLE_LANGUAGES[0].code);
  // Finance state management
  const [financeState, setFinanceState] = useState<FinanceState | null>(null);
  const [financeAction, setFinanceAction] = useState<FinanceAction>(null);
  const [isLoadingFinanceState, setIsLoadingFinanceState] = useState(true);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  // Generate typing sound programmatically instead of using MP3
  const [audioContext] = useState(() => typeof window !== 'undefined' ? new (window.AudioContext || (window as any).webkitAudioContext)() : null);
  const typingSoundInterval = useRef<NodeJS.Timeout | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const displayedMessages = useRef<Set<string>>(new Set());
  const displayedTextContentIds = useRef<Set<string>>(new Set());
  const contentIdToStage = useRef<Record<string, string>>({});
  const pendingTexts = useRef<Record<string, TextMessage>>({});
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const playbackServiceRef = useRef<AudioPlaybackService | null>(null);

  // Debug-enhanced recording state setter
  const setRecordingWithDebug = useCallback((value: boolean) => {
    console.log(`[Recording State] Setting to ${value}. Triggered by:`, new Error().stack);
    setRecording(value);
  }, []);

  const connect = () => {
    if (wsRef.current) wsRef.current.close();
    wsRef.current = new WebSocket(`ws://localhost:8000/ws?model=${encodeURIComponent(selectedModel)}&language=${encodeURIComponent(selectedLanguage)}`);
    setStatus('Connecting...');
    setWsKey(k => k + 1);

    wsRef.current.onopen = () => setStatus('Connected');
    wsRef.current.onclose = () => {
      setStatus('Disconnected');
      setRecordingWithDebug(false);
    };
    wsRef.current.onerror = () => setStatus('Error');
    wsRef.current.onmessage = (event) => {
      if (typeof event.data === 'string') {
        try {
          const msg = JSON.parse(event.data);
          console.log('[WS MESSAGE]', msg);

          if (msg.event) handleEventMessage(msg.event);
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      }
    };
  };

  // Memoize handlers to prevent unnecessary re-renders
  const handleAudioError = useCallback((error: Error) => {
    console.error('[Audio Error]', error);
    setRecordingWithDebug(false);
  }, [setRecordingWithDebug]);

  const addMessage = useCallback((message: TextMessage) => {
    const messageKey = `${message.role}:${message.text}`;
    if (!displayedMessages.current.has(messageKey)) {
      console.log('[ADDING MESSAGE]', message);
      displayedMessages.current.add(messageKey);
      setTextOutputs(prev => [...prev, message]);
    } else {
      console.log('[SKIPPING DUPLICATE]', message);
    }
  }, []);

  // Function to generate a typing sound programmatically
  const playTypingBeep = useCallback(() => {
    if (!audioContext) return;

    try {
      // Create a short beep sound (like a keyboard click)
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // Set frequency for a subtle click sound
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);

      // Set volume envelope for a quick click
      gainNode.gain.setValueAtTime(0, audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.1);
    } catch (err) {
      console.error('Error playing typing sound:', err);
    }
  }, [audioContext]);

  // Function to start looping the typing sound
  const startTypingSound = useCallback(() => {
    if (audioContext) {
      // Set up the interval to play the sound repeatedly
      typingSoundInterval.current = setInterval(() => {
        playTypingBeep();
      }, 1500); // Adjust interval as needed (current: 1.5 seconds)
    }
  }, [audioContext, playTypingBeep]);

  // Function to stop the typing sound
  const stopTypingSound = useCallback(() => {
    if (typingSoundInterval.current) {
      clearInterval(typingSoundInterval.current);
      typingSoundInterval.current = null;
    }
  }, []);

  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (typingSoundInterval.current) {
        clearInterval(typingSoundInterval.current);
      }
    };
  }, []);

  // Fetch initial finance state on component mount
  useEffect(() => {
    const fetchFinanceState = async () => {
      try {
        setIsLoadingFinanceState(true);
        const response = await fetch('http://localhost:8000/api/finance/state');
        if (response.ok) {
          const data = await response.json();
          setFinanceState(data);
        } else {
          console.error('Failed to fetch finance state:', response.status);
        }
      } catch (error) {
        console.error('Error fetching finance state:', error);
      } finally {
        setIsLoadingFinanceState(false);
      }
    };

    fetchFinanceState();
  }, []);

  const handleEventMessage = (event: any) => {
    console.log('[WS EVENT]', event);

    if (event.init) {
      // Store tool configurations
      setToolConfigs(event.init.toolConfigs);
      return;
    }

    if (event.contentStart && event.contentStart.type === 'TEXT') {
      const contentId = event.contentStart.contentId;
      let stage = 'FINAL';
      if (event.contentStart.additionalModelFields) {
        try {
          const fields = JSON.parse(event.contentStart.additionalModelFields);
          if (fields.generationStage) stage = fields.generationStage;
        } catch (e) {
          console.error('[TEXT STAGE ERROR]', e);
        }
      }
      if (contentId) {
        console.log('[TEXT STAGE]', contentId, stage);
        contentIdToStage.current[contentId] = stage;
      }
    } else if (event.contentStart && event.contentStart.type === 'TOOL') {
      console.log('[TOOL START]', event);
      setWaitingForTool(true);
    } else if (event.toolUse) {
      console.log('[TOOL USE]', event.toolUse);
      setWaitingForTool(true);
      const toolName = event.toolUse.toolName;

      // Find the tool configuration and get its short description
      const toolConfig = toolConfigs.find((t: any) => t.name === toolName);
      setCurrentTool({
        name: toolName || 'Unknown Tool',
        content: 'Processing...'
      });
    } else if (event.toolResult) {
      // Tool result received
      console.log('[TOOL RESULT FULL]', event.toolResult);
      try {
        const parsedContent = JSON.parse(event.toolResult.content);
        console.log('[TOOL RESULT PARSED]', parsedContent);
      } catch (e) {
        console.error('[TOOL RESULT PARSE ERROR]', e);
      }
      setWaitingForTool(false);
      setCurrentTool(prev => prev ? {
        ...prev,
        content: JSON.stringify(JSON.parse(event.toolResult.content), null, 2)
      } : null);
    } else if (event.toolUiOutput) {
      // Handle tool UI output
      console.log('[TOOL UI OUTPUT]', event.toolUiOutput);

      // Handle barge-in events
      if (event.toolUiOutput.type === 'barge_in') {
        console.log('[BARGE IN] Stopping audio playback');
        if (playbackServiceRef.current) {
          playbackServiceRef.current.stop();
        }
      }

      // Handle tool execution progress events
      if (event.toolUiOutput.type === 'tool_exec_progress') {
        const status = event.toolUiOutput.content.status;
        if (status === 'started') {
          startTypingSound();
        } else if (status === 'completed') {
          stopTypingSound();
        }
      }

      // Update finance state when finance tool outputs are received
      if (event.toolUiOutput.type === 'app' && event.toolUiOutput.appName === 'finance') {
        const financeOutput = event.toolUiOutput as FinanceAppToolOutput;
        if (financeOutput.props?.state) {
          setFinanceState(financeOutput.props.state);
        }
        if (financeOutput.props?.action) {
          setFinanceAction(financeOutput.props.action);
          // Clear the action after animation completes
          setTimeout(() => setFinanceAction(null), 1500);
        }
      }

      // Set the entire toolUiOutput object to preserve all fields (appName, props, etc)
      setToolUiOutput(event.toolUiOutput);
    } else if (event.contentEnd && event.contentEnd.type === 'TOOL') {
      // Tool usage ended
      console.log('[TOOL END]', event);
      setCurrentTool(null);
      setWaitingForTool(false);
    } else if (event.audioOutput) {
      // Stream audio chunk immediately
      const base64Audio = event.audioOutput.content;
      const audioBytes = base64ToArrayBuffer(base64Audio);
      if (playbackServiceRef.current) {
        playbackServiceRef.current.playPCM(audioBytes);
      }

      // Agent is speaking when audio is being output
      setIsAgentSpeaking(true);

      // If there's pending text for this contentId, show it
      const contentId = event.audioOutput.contentId || 'default';
      if (contentId && pendingTexts.current[contentId]) {
        const textMessage = pendingTexts.current[contentId];
        addMessage(textMessage);
        displayedTextContentIds.current.add(contentId);
        delete pendingTexts.current[contentId];
      }
    } else if (event.contentEnd && event.contentEnd.type === 'AUDIO') {
      // Agent stopped speaking when audio content ends
      setIsAgentSpeaking(false);
    } else if (event.textOutput) {
      const text = event.textOutput.content;
      const role = event.textOutput.role || 'ASSISTANT';
      const contentId = event.textOutput.contentId;

      console.log('[TEXT EVENT]', {
        text,
        role,
        contentId,
        hasContentId: !!contentId,
        isDisplayed: displayedTextContentIds.current.has(contentId),
      });

      // Skip empty messages
      if (!text || text.trim() === '') {
        return;
      }

      // Show text immediately for USER and SYSTEM roles
      if (role === 'USER' || role === 'SYSTEM') {
        console.log('[SHOWING USER/SYSTEM TEXT]', { text, role });
        addMessage({ text, role });
        if (contentId) displayedTextContentIds.current.add(contentId);
      } else if (role === 'ASSISTANT') {
        // For assistant messages, check if we have corresponding audio
        const hasAudioOutput = event.audioOutput && event.audioOutput.contentId === contentId;

        // Show text immediately if no audio is expected
        if (!contentId || !hasAudioOutput) {
          console.log('[SHOWING ASSISTANT TEXT IMMEDIATELY]', { text, role });
          addMessage({ text, role });
          if (contentId) displayedTextContentIds.current.add(contentId);
        } else {
          // Buffer the text to sync with audio
          console.log('[BUFFERING ASSISTANT TEXT]', { text, contentId });
          pendingTexts.current[contentId] = { text, role };
        }
      }
    }
  };

  const disconnect = useCallback(() => {
    console.log('[Disconnect] Cleaning up connection');
    setRecordingWithDebug(false);
    setStatus('Disconnected');
    setTextOutputs([]);
    displayedMessages.current.clear();
    displayedTextContentIds.current.clear();
    contentIdToStage.current = {};
    pendingTexts.current = {};
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setWsKey(k => k + 1);
    }
    if (playbackServiceRef.current) {
      playbackServiceRef.current.stop();
    }
  }, [setRecordingWithDebug]);

  const startRecording = useCallback(() => {
    console.log('[Start Recording]');
    setRecordingWithDebug(true);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send('start_audio');
    }
  }, [setRecordingWithDebug]);

  const stopRecording = useCallback(() => {
    console.log('[Stop Recording]');
    setRecordingWithDebug(false);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send('stop_audio');
    }
  }, [setRecordingWithDebug]);

  // Memoize audio capture components
  const audioCaptureComponent = useMemo(() => (
    <AudioCapture
      key={wsKey}
      websocket={wsRef.current}
      isCapturing={recording}
      onError={handleAudioError}
      inline
      setIsThinking={setIsThinking}
    />
  ), [wsKey, recording, handleAudioError, setIsThinking]);

  const audioMediaRecorderComponent = useMemo(() => (
    <AudioCaptureMediaRecorder
      websocket={wsRef.current}
      isCapturing={recording}
      onError={handleAudioError}
      inline
      setIsThinking={setIsThinking}
      promptName={wsRef.current ? 'user_audio_prompt' : 'inactive_prompt'}
      contentName={wsRef.current ? `user_audio_${Date.now()}` : 'inactive_content'}
    />
  ), [wsKey, recording, handleAudioError, setIsThinking]);

  const base64LPCM = (base64String: string): string => {
    const byteCharacters = atob(base64String);
    const byteArrays = new Uint8Array(byteCharacters.length);

    for (let i = 0; i < byteCharacters.length; i++) {
      byteArrays[i] = byteCharacters.charCodeAt(i);
    }

    const sampleRate = 24000;
    const numChannels = 1;
    const bitsPerSample = 16;
    const byteRate = sampleRate * numChannels * (bitsPerSample / 8);
    const blockAlign = numChannels * (bitsPerSample / 8);
    const wavSize = byteArrays.length + 36;

    const wavHeader = new Uint8Array(44);
    const view = new DataView(wavHeader.buffer);

    let offset = 0;
    for (let i = 0; i < 4; i++) view.setUint8(offset++, "RIFF".charCodeAt(i));
    view.setUint32(offset, wavSize, true); offset += 4;
    for (let i = 0; i < 4; i++) view.setUint8(offset++, "WAVE".charCodeAt(i));
    for (let i = 0; i < 4; i++) view.setUint8(offset++, "fmt ".charCodeAt(i));
    view.setUint32(offset, 16, true); offset += 4;
    view.setUint16(offset, 1, true); offset += 2;
    view.setUint16(offset, numChannels, true); offset += 2;
    view.setUint32(offset, sampleRate, true); offset += 4;
    view.setUint32(offset, byteRate, true); offset += 4;
    view.setUint16(offset, blockAlign, true); offset += 2;
    view.setUint16(offset, bitsPerSample, true); offset += 2;
    for (let i = 0; i < 4; i++) view.setUint8(offset++, "data".charCodeAt(i));
    view.setUint32(offset, byteArrays.length, true); offset += 4;

    const wavBlob = new Blob([wavHeader, byteArrays], { type: "audio/wav" });
    return URL.createObjectURL(wavBlob);
  };

  // Helper function to convert base64 to ArrayBuffer
  const base64ToArrayBuffer = (base64: string): ArrayBuffer => {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  };

  useEffect(() => {
    if (!playbackServiceRef.current) {
      playbackServiceRef.current = new AudioPlaybackService();
    }

    return () => {
      if (playbackServiceRef.current) {
        playbackServiceRef.current.stop();
      }
    };
  }, []);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Add effect to log toolUiOutput state changes
  useEffect(() => {
    console.log('[TOOL UI OUTPUT STATE]', toolUiOutput);
  }, [toolUiOutput]);

  // Add clearToolOutput function
  const clearToolOutput = useCallback(() => {
    console.log('[CLEARING TOOL UI OUTPUT] by user');
    setToolUiOutput(null);
  }, []);

  // Add useEffect for auto-scrolling
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [textOutputs]); // Scroll when messages change

  const playTypingSound = useCallback(() => {
    playTypingBeep();
  }, [playTypingBeep]);

  return (
    <main className="min-h-screen h-screen  flex flex-row items-stretch bg-gray-100">
      {/* Left pane for banking dashboard */}
      <section className="w-full bg-white flex flex-col border-r border-gray-200 h-full overflow-hidden">
        <div className="p-2 border-0 border-gray-100 flex justify-between items-center shrink-0">
          {/* <Button
            onClick={playTypingSound}
            variant="ghost"
            className="h-8 px-4 hover:bg-gray-100"
          >
            Play Sound
          </Button> */}
          {toolUiOutput && toolUiOutput.type !== 'app' && (
            <Button
              onClick={clearToolOutput}
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full hover:bg-gray-100 ml-auto"
            >
              <X size={16} />
            </Button>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          {isLoadingFinanceState ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600" />
              <p className="text-sm">Loading financial data...</p>
            </div>
          ) : waitingForTool ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600" />
              <p className="text-sm">Processing...</p>
            </div>
          ) : toolUiOutput && toolUiOutput.type !== 'app' ? (
            <ToolOutput output={toolUiOutput as ToolOutputType} websocket={wsRef.current} />
          ) : financeState ? (
            <FinanceApp
              action={financeAction}
              state={financeState}
              isAgentSpeaking={isAgentSpeaking}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400 text-center">
              <div>
                <p className="mb-2">Finance Dashboard</p>
                <p className="text-sm">Unable to load financial data</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Right chat panel */}
      <aside className="w-full max-w-md flex flex-col h-screen justify-between bg-white border-r border-gray-200">
        <Card className="flex-1 shadow-xl border-0 p-8 space-y-6 bg-white h-full flex flex-col">
          <div className="flex flex-col gap-3 mb-2 border-b pb-4 border-gray-100">
            <div className="flex gap-2">
              <Select
                value={selectedModel}
                onValueChange={setSelectedModel}
                disabled={status === 'Connected'}
              >
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {AVAILABLE_MODELS.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      <span className="font-medium">{model.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={selectedLanguage}
                onValueChange={setSelectedLanguage}
                disabled={status === 'Connected'}
              >
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Language" />
                </SelectTrigger>
                <SelectContent>
                  {AVAILABLE_LANGUAGES.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      <span>{lang.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={status === 'Connected' ? disconnect : connect}
                className={`bg-black text-white hover:bg-neutral-800 border-0 shadow-none rounded-full p-0 w-10 h-10 flex items-center justify-center`}
                size="icon"
                aria-label={status === 'Connected' ? 'Disconnect' : 'Connect'}
              >
                {status === 'Connected' ? <PowerOff size={20} /> : <Power size={20} />}
              </Button>
              <Button
                onClick={recording ? stopRecording : startRecording}
                disabled={status !== 'Connected'}
                className={`bg-black text-white hover:bg-neutral-800 border-0 shadow-none rounded-full p-0 w-10 h-10 flex items-center justify-center ${status !== 'Connected' ? 'opacity-50' : ''}`}
                size="icon"
                aria-label={recording ? 'Stop Recording' : 'Start Recording'}
              >
                {recording ? <MicOff size={20} /> : <Mic size={20} />}
              </Button>
              <div className="ml-6 w-full">
                {audioCaptureComponent}
              </div>
            </div>
            <span className="ml-2 flex items-center">
              <span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-2" title={status}></span>
            </span>
          </div>

          <div ref={chatContainerRef} className="h-96 overflow-y-auto space-y-4 bg-white p-0 rounded-lg border-0 border-gray-200 flex-1">
            <AnimatePresence>
              {textOutputs.map((msg, i) => (
                <motion.div
                  key={i}
                  layout
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  variants={messageVariants}
                  className={`flex items-start gap-3 ${msg.role === 'USER' ? 'justify-end' : 'justify-start'
                    }`}
                >
                  {msg.role === 'ASSISTANT' && (
                    <motion.div
                      variants={avatarVariants}
                      initial="initial"
                      animate="animate"
                    >
                      <Avatar className="bg-black text-white w-10 h-10 ring-2 ring-offset-2 ring-black/5">
                        <AvatarImage src="/nova-sonic-avatar.png" alt="Assistant" />
                        <AvatarFallback><Bot size={20} /></AvatarFallback>
                      </Avatar>
                    </motion.div>
                  )}
                  <motion.div
                    className={`p-3 rounded-2xl shadow-sm max-w-[70%] text-sm font-medium backdrop-blur-sm ${msg.role === 'USER'
                      ? 'bg-black text-white rounded-br-none shadow-lg'
                      : msg.role === 'SYSTEM'
                        ? 'bg-gray-100/80 text-gray-500 text-sm italic'
                        : msg.role === 'ASSISTANT'
                          ? 'bg-gray-100/80 text-black rounded-bl-none shadow-md'
                          : 'bg-gray-100/80 text-black'
                      }`}
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 400, damping: 17 }}
                  >
                    {msg.text}
                  </motion.div>
                  {msg.role === 'USER' && (
                    <motion.div
                      variants={avatarVariants}
                      initial="initial"
                      animate="animate"
                    >
                      <Avatar className="bg-black text-white w-10 h-10 ring-2 ring-offset-2 ring-black/5">
                        <AvatarFallback><User size={20} /></AvatarFallback>
                      </Avatar>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </Card>
      </aside>
    </main>
  );
}