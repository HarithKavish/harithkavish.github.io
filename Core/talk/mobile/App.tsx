import React, { useState, useRef, useCallback, memo, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Pressable,
  FlatList,
  StyleSheet,
  Platform,
  Keyboard,
  Animated,
  PanResponder,
  Linking,
  ActivityIndicator,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { StatusBar, setStatusBarHidden } from 'expo-status-bar';
import * as SplashScreen from 'expo-splash-screen';
import Markdown from 'react-native-markdown-display';
import * as Clipboard from 'expo-clipboard';

// Keep splash visible until we're ready
SplashScreen.preventAutoHideAsync();

// ─── Config ────────────────────────────────────────────────
const API_BASE = 'https://jarvis.harithkavish40.workers.dev';
const FLUSH_INTERVAL = 60;
const TOP_SAFE_MARGIN = 14; // space above first message for camera notch area

// ─── Types ─────────────────────────────────────────────────
interface StatusStep {
  id: string;
  text: string;
  state: 'loading' | 'completed' | 'error';
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  streaming?: boolean;
  statusSteps?: StatusStep[];
}

// ─── Collapsible code block component ──────────────────────
const CollapsibleCodeBlock = memo(({ code, language, streaming }: { code: string; language?: string; streaming?: boolean }) => {
  const [collapsed, setCollapsed] = useState(!streaming); // open by default if streaming

  const copyCode = useCallback(() => {
    Clipboard.setStringAsync(code);
  }, [code]);

  return (
    <View style={codeStyles.container}>
      <View style={codeStyles.header}>
        <TouchableOpacity onPress={() => setCollapsed(c => !c)} style={codeStyles.toggleBtn} activeOpacity={0.6}>
          <Text style={codeStyles.toggleIcon}>{collapsed ? '▶' : '▼'}</Text>
          <Text style={codeStyles.langLabel}>{language || 'code'}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={copyCode} style={codeStyles.copyBtn} activeOpacity={0.6}>
          <Text style={codeStyles.copyIcon}>⧉</Text>
        </TouchableOpacity>
      </View>
      {!collapsed && (
        <View style={codeStyles.codeBody}>
          <Text style={codeStyles.codeText}>{code}</Text>
        </View>
      )}
    </View>
  );
});

const codeStyles = StyleSheet.create({
  container: { backgroundColor: '#111', borderRadius: 8, marginVertical: 6, overflow: 'hidden', borderWidth: 1, borderColor: '#222' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 6, backgroundColor: '#181818' },
  toggleBtn: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  toggleIcon: { color: '#888', fontSize: 10 },
  langLabel: { color: '#888', fontSize: 11, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  copyBtn: { padding: 4 },
  copyIcon: { color: '#888', fontSize: 14 },
  codeBody: { padding: 10 },
  codeText: { color: '#7dd3fc', fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 13 },
});

// ─── Convert bare URLs into markdown links so they become tappable ──
function linkifyUrls(text: string): string {
  // Use a safer regex to avoid negative lookbehind crashes on older JS engines.
  // We match existing markdown links or bare URLs. If it's a bare URL (group 1), we wrap it.
  const urlRegex = /\[[^\]]*\]\([^)]+\)|\b(https?:\/\/[^\s)\]>"'`,]+)/g;
  return text.replace(urlRegex, (match, p1) => {
    if (p1) {
      return `[${p1}](${p1})`;
    }
    return match;
  });
}

// ─── Process markdown text: extract fenced code blocks → CollapsibleCodeBlock ──
const ProcessedMarkdown = memo(({ text, streaming }: { text: string; streaming?: boolean }) => {
  // Split text into segments: regular markdown and fenced code blocks
  const segments = useMemo(() => {
    const parts: { type: 'md' | 'code'; content: string; lang?: string }[] = [];
    // Match code blocks, including unclosed ones at the end of the text
    const regex = /```([^\r\n]*)\r?\n([\s\S]*?)(?:```|$)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      // Text before this code block
      if (match.index > lastIndex) {
        parts.push({ type: 'md', content: text.slice(lastIndex, match.index) });
      }
      parts.push({ type: 'code', content: match[2], lang: match[1]?.trim() || undefined });
      lastIndex = match.index + match[0].length;
    }
    // Remaining text after last code block
    if (lastIndex < text.length) {
      parts.push({ type: 'md', content: text.slice(lastIndex) });
    }
    return parts;
  }, [text]);

  return (
    <>
      {segments.map((seg, i) =>
        seg.type === 'code' ? (
          <CollapsibleCodeBlock key={i} code={seg.content} language={seg.lang} streaming={streaming} />
        ) : (
          <Markdown
            key={i}
            style={mdStyles}
            onLinkPress={(url: string) => {
              Linking.openURL(url).catch(() => { });
              return false; // prevent default
            }}
          >
            {linkifyUrls(seg.content)}
          </Markdown>
        )
      )}
    </>
  );
});

// ─── Markdown styles (static) ──────────────────────────────
const mdStyles = StyleSheet.create({
  body: { color: '#e0e0e0', fontSize: 15, lineHeight: 21 },
  heading1: { color: '#fff', fontSize: 22, fontWeight: '700' as const, marginVertical: 6 },
  heading2: { color: '#fff', fontSize: 19, fontWeight: '700' as const, marginVertical: 5 },
  heading3: { color: '#fff', fontSize: 17, fontWeight: '600' as const, marginVertical: 4 },
  strong: { color: '#fff', fontWeight: '700' as const },
  em: { color: '#ccc', fontStyle: 'italic' as const },
  bullet_list: { marginVertical: 4 },
  ordered_list: { marginVertical: 4 },
  list_item: { marginVertical: 2 },
  code_inline: { backgroundColor: '#2a2a2a', color: '#7dd3fc', paddingHorizontal: 4, borderRadius: 4, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 13 },
  // Hide default fenced code rendering since we handle it ourselves
  fence: { display: 'none' as any },
  code_block: { display: 'none' as any },
  blockquote: { borderLeftWidth: 3, borderLeftColor: '#444', paddingLeft: 10, marginVertical: 6 },
  link: { color: '#60a5fa', textDecorationLine: 'underline' as const },
  paragraph: { marginTop: 0, marginBottom: 6 },
});

// ─── Copy button under a bubble ────────────────────────────
const CopyButton = memo(({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    Clipboard.setStringAsync(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [text]);

  return (
    <TouchableOpacity onPress={handleCopy} style={copyBtnStyles.btn} activeOpacity={0.6}>
      <Text style={copyBtnStyles.text}>{copied ? '✓ Copied' : '⧉ Copy'}</Text>
    </TouchableOpacity>
  );
});

const copyBtnStyles = StyleSheet.create({
  btn: { paddingHorizontal: 8, paddingVertical: 3, marginTop: 2, marginBottom: 6 },
  text: { color: '#555', fontSize: 11 },
});

// ─── Status steps view (VS Code Copilot-style progress) ───
const StatusStepsView = memo(({ steps }: { steps: StatusStep[] }) => (
  <View style={statusStepStyles.container}>
    {steps.map((step) => (
      <View key={step.id} style={statusStepStyles.step}>
        <View style={statusStepStyles.icon}>
          {step.state === 'loading' ? (
            <ActivityIndicator size="small" color="#888" />
          ) : step.state === 'completed' ? (
            <Text style={statusStepStyles.completedIcon}>✓</Text>
          ) : (
            <Text style={statusStepStyles.errorIcon}>✗</Text>
          )}
        </View>
        <Text style={[statusStepStyles.stepText, step.state === 'error' && statusStepStyles.errorText]}>
          {step.text}
        </Text>
      </View>
    ))}
  </View>
));

const statusStepStyles = StyleSheet.create({
  container: { marginBottom: 8 },
  step: { flexDirection: 'row', alignItems: 'center', marginVertical: 3, paddingHorizontal: 4 },
  icon: { width: 20, alignItems: 'center', marginRight: 8 },
  completedIcon: { color: '#4ade80', fontSize: 14, fontWeight: '700' },
  errorIcon: { color: '#f87171', fontSize: 14, fontWeight: '700' },
  stepText: { color: '#c0c0c0', fontSize: 13, flex: 1, lineHeight: 18 },
  errorText: { color: '#f87171' },
});

// ─── Memoised message bubble ───────────────────────────────
const MessageBubble = memo(({ item, isFirst }: { item: Message; isFirst: boolean }) => {
  const isUser = item.role === 'user';

  if (isUser) {
    return (
      <View style={[isFirst && { marginTop: TOP_SAFE_MARGIN }]}>
        <View style={[styles.bubble, styles.userBubble]}>
          <Text style={[styles.bubbleText, styles.userText]}>{item.text}</Text>
        </View>
        <View style={{ alignSelf: 'flex-end' }}>
          <CopyButton text={item.text} />
        </View>
      </View>
    );
  }

  // Assistant: full width, no bubble background, no border radius
  return (
    <View style={[isFirst && { marginTop: TOP_SAFE_MARGIN }]}>
      <View style={styles.assistantContainer}>
        {item.statusSteps && item.statusSteps.length > 0 && (
          <StatusStepsView steps={item.statusSteps} />
        )}
        {item.text ? (
          <ProcessedMarkdown text={item.text} streaming={item.streaming} />
        ) : item.streaming ? (
          <Text style={styles.streamingText}>...</Text>
        ) : null}
      </View>
      {!item.streaming && item.text ? (
        <View style={{ alignSelf: 'flex-start' }}>
          <CopyButton text={item.text} />
        </View>
      ) : null}
    </View>
  );
}, (prev, next) => {
  return prev.item.text === next.item.text
    && prev.item.streaming === next.item.streaming
    && prev.isFirst === next.isFirst
    && prev.item.statusSteps === next.item.statusSteps;
});

// ─── Joystick (swipe gesture) ───────────────────────────────
const Joystick = memo(({ onScrollUp, onScrollDown, onGoTop, onGoBottom }: {
  onScrollUp: () => void;
  onScrollDown: () => void;
  onGoTop: () => void;
  onGoBottom: () => void;
}) => {
  const scrollInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const tapTimestamps = useRef<number[]>([]);
  const tapTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const currentDir = useRef<'up' | 'down' | null>(null);
  const didSwipe = useRef(false);

  const stopScroll = useCallback(() => {
    if (scrollInterval.current) {
      clearInterval(scrollInterval.current);
      scrollInterval.current = null;
    }
    currentDir.current = null;
  }, []);

  const startScroll = useCallback((direction: 'up' | 'down') => {
    if (currentDir.current === direction) return;
    stopScroll();
    currentDir.current = direction;
    const fn = direction === 'up' ? onScrollUp : onScrollDown;
    fn();
    scrollInterval.current = setInterval(fn, 30);
  }, [onScrollUp, onScrollDown, stopScroll]);

  const handleTap = useCallback(() => {
    const now = Date.now();
    tapTimestamps.current.push(now);
    tapTimestamps.current = tapTimestamps.current.filter(t => now - t < 600);

    if (tapTimer.current) {
      clearTimeout(tapTimer.current);
      tapTimer.current = null;
    }

    if (tapTimestamps.current.length >= 3) {
      tapTimestamps.current = [];
      onGoTop();
      return;
    }

    tapTimer.current = setTimeout(() => {
      if (tapTimestamps.current.length === 2) {
        onGoBottom();
      }
      tapTimestamps.current = [];
      tapTimer.current = null;
    }, 350);
  }, [onGoTop, onGoBottom]);

  const panResponder = useMemo(() => PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: (_, gs) => Math.abs(gs.dy) > 3,
    onPanResponderGrant: () => { didSwipe.current = false; },
    onPanResponderMove: (_, gs) => {
      if (Math.abs(gs.dy) > 5) {
        didSwipe.current = true;
        startScroll(gs.dy < 0 ? 'up' : 'down');
      }
    },
    onPanResponderRelease: (_, gs) => {
      stopScroll();
      if (!didSwipe.current && Math.abs(gs.dy) < 10 && Math.abs(gs.dx) < 10) {
        handleTap();
      }
      didSwipe.current = false;
    },
    onPanResponderTerminate: () => {
      stopScroll();
      didSwipe.current = false;
    },
  }), [startScroll, stopScroll, handleTap]);

  return (
    <View {...panResponder.panHandlers} style={joystickStyles.container}>
      <Text style={joystickStyles.arrowUp}>▲</Text>
      <Text style={joystickStyles.arrowDown}>▼</Text>
    </View>
  );
});

const joystickStyles = StyleSheet.create({
  container: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#111',
    borderWidth: 1,
    borderColor: '#2a2a2a',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 2,
  },
  arrowUp: { color: '#555', fontSize: 10 },
  arrowDown: { color: '#555', fontSize: 10 },
});

// ─── App ───────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [splashDone, setSplashDone] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const abortRef = useRef<AbortController | null>(null);
  const textInputRef = useRef<TextInput>(null);

  // Refs for batched token flushing
  const accumulatedRef = useRef('');
  const statusStepsRef = useRef<StatusStep[]>([]);
  const statusDirtyRef = useRef(false);
  const assistantIdRef = useRef('');
  const flushTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const needsScrollRef = useRef(false);
  const bubbleCreatedRef = useRef(false);
  const inputTextRef = useRef(''); // Tracks input value for keyboard handlers

  // Bottom bar state
  const [bottomBarVisible, setBottomBarVisible] = useState(true);
  const [inputExpanded, setInputExpanded] = useState(false);
  const [contentOverflows, setContentOverflows] = useState(false);
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const lastScrollY = useRef(0);
  const keyboardHeightAnim = useRef(new Animated.Value(0)).current;
  const bottomBarSlide = useRef(new Animated.Value(0)).current; // 0=visible, 1=hidden
  const collapsingRef = useRef(false); // prevent re-expand during collapse

  // Hide status bar + splash screen on mount
  useEffect(() => {
    setStatusBarHidden(true, 'none');
    // Hide native splash quickly — React splash takes over
    requestAnimationFrame(() => {
      SplashScreen.hideAsync().catch(() => { });
    });
    // Show React splash for a moment, then reveal chat
    setTimeout(() => setSplashDone(true), 1200);
  }, []);

  // Keyboard listeners — stick input bar to keyboard + auto-collapse
  useEffect(() => {
    const showSub = Keyboard.addListener(
      Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow',
      (e) => {
        setKeyboardHeight(e.endCoordinates.height);
        Animated.timing(keyboardHeightAnim, {
          toValue: e.endCoordinates.height,
          duration: Platform.OS === 'ios' ? 250 : 100,
          useNativeDriver: false,
        }).start();
      }
    );
    const hideSub = Keyboard.addListener(
      Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide',
      () => {
        setKeyboardHeight(0);
        Animated.timing(keyboardHeightAnim, {
          toValue: 0,
          duration: Platform.OS === 'ios' ? 250 : 100,
          useNativeDriver: false,
        }).start();
        // Collapse input bar after keyboard hides, only if no text is typed
        // so user doesn't lose sight of their draft if they dismiss keyboard physically
        if (!inputTextRef.current.trim()) {
          collapsingRef.current = true;
          setInputExpanded(false);
          setTimeout(() => { collapsingRef.current = false; }, 100);
        }
      }
    );
    return () => { showSub.remove(); hideSub.remove(); };
  }, [keyboardHeightAnim]);

  // Toggle bottom bar visibility (tap on chat area)
  const toggleBottomBar = useCallback(() => {
    if (inputExpanded) return; // don't toggle while input is open
    setBottomBarVisible(v => {
      const next = !v;
      Animated.timing(bottomBarSlide, {
        toValue: next ? 0 : 1,
        duration: 200,
        useNativeDriver: false,
      }).start();
      return next;
    });
  }, [inputExpanded, bottomBarSlide]);

  // Expand input bar → show input + auto-open keyboard
  const expandInputBar = useCallback(() => {
    if (collapsingRef.current) return;
    setInputExpanded(true);
    // Auto-focus the text input after state update
    setTimeout(() => textInputRef.current?.focus(), 50);
  }, []);

  // Collapse input bar → dismiss keyboard manually + force input bar to hide
  const collapseInputBar = useCallback(() => {
    Keyboard.dismiss();
    setInputExpanded(false);
  }, []);

  // Track scroll for overflow detection
  const handleScroll = useCallback((e: NativeSyntheticEvent<NativeScrollEvent>) => {
    const contentH = e.nativeEvent.contentSize.height;
    const layoutH = e.nativeEvent.layoutMeasurement.height;
    setContentOverflows(contentH > layoutH + 10);
    lastScrollY.current = e.nativeEvent.contentOffset.y;
  }, []);

  // Instant scroll
  const scrollToEnd = useCallback((animated = false) => {
    flatListRef.current?.scrollToEnd({ animated });
  }, []);

  // Joystick/scroll handlers (for the separate scroll button)
  const joystickScrollUp = useCallback(() => {
    flatListRef.current?.scrollToOffset({ offset: Math.max(0, lastScrollY.current - 200), animated: false });
  }, []);

  const joystickScrollDown = useCallback(() => {
    flatListRef.current?.scrollToOffset({ offset: lastScrollY.current + 200, animated: false });
  }, []);

  const joystickGoTop = useCallback(() => {
    flatListRef.current?.scrollToOffset({ offset: 0, animated: true });
  }, []);

  const joystickGoBottom = useCallback(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, []);

  // Flush accumulated tokens to React state at a capped rate
  const startFlushing = useCallback((assistantId: string) => {
    if (flushTimerRef.current) return;
    flushTimerRef.current = setInterval(() => {
      const text = accumulatedRef.current;
      const hasStepChanges = statusDirtyRef.current;
      if (!text && !hasStepChanges) return;

      const steps = hasStepChanges ? [...statusStepsRef.current] : undefined;
      if (hasStepChanges) statusDirtyRef.current = false;

      // Create the assistant bubble on first token/status (not before)
      if (!bubbleCreatedRef.current) {
        bubbleCreatedRef.current = true;
        setMessages(prev => [...prev, { id: assistantId, role: 'assistant', text, streaming: true, statusSteps: steps || [] }]);
      } else {
        setMessages(prev =>
          prev.map(m => {
            if (m.id !== assistantId) return m;
            const updated: Message = { ...m, text };
            if (steps) updated.statusSteps = steps;
            return updated;
          })
        );
      }

      if (needsScrollRef.current) {
        needsScrollRef.current = false;
        requestAnimationFrame(() => scrollToEnd(false));
      }
    }, FLUSH_INTERVAL);
  }, [scrollToEnd]);

  const stopFlushing = useCallback(() => {
    if (flushTimerRef.current) {
      clearInterval(flushTimerRef.current);
      flushTimerRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopFlushing();
  }, [stopFlushing]);

  // Send message and stream response via SSE
  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;

    Keyboard.dismiss();
    setInput('');
    inputTextRef.current = '';

    const userMsgId = `user-${Date.now()}`;
    const assistantId = `asst-${Date.now()}`;
    assistantIdRef.current = assistantId;
    accumulatedRef.current = '';
    statusStepsRef.current = [];
    statusDirtyRef.current = false;
    bubbleCreatedRef.current = false;

    // Add only user message — assistant bubble appears on first token
    setMessages(prev => [...prev, { id: userMsgId, role: 'user', text }]);
    setStreaming(true);
    requestAnimationFrame(() => scrollToEnd(false));

    // Start the batched flush timer
    startFlushing(assistantId);

    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        abortRef.current = { abort: () => xhr.abort() } as AbortController;
        let lastIndex = 0;
        let streamBuffer = '';

        xhr.open('POST', `${API_BASE}/api/chat`);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onprogress = () => {
          const newText = xhr.responseText.substring(lastIndex);
          lastIndex = xhr.responseText.length;
          streamBuffer += newText;

          // Extract all full lines (separated by newline)
          let newlineIdx;
          while ((newlineIdx = streamBuffer.indexOf('\n')) >= 0) {
            const line = streamBuffer.slice(0, newlineIdx).trim();
            streamBuffer = streamBuffer.slice(newlineIdx + 1);

            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (!payload) continue;

            try {
              const parsed = JSON.parse(payload);
              if (parsed.done) {
                // Stream complete — mark ALL remaining loading steps as completed.
                // This is the universal safety net: no matter what workflow or status
                // patterns the worker sends, nothing stays spinning after completion.
                statusStepsRef.current = statusStepsRef.current.map(s =>
                  s.state === 'loading' ? { ...s, state: 'completed' as const } : s
                );
                statusDirtyRef.current = true;
                continue;
              }
              if (parsed.error) {
                accumulatedRef.current += `\n[Error: ${parsed.error}]`;
                needsScrollRef.current = true;
                continue;
              }
              if (parsed.status) {
                const statusText = parsed.status as string;
                let stepId: string;
                let displayText: string;
                let state: 'loading' | 'completed' | 'error';

                // ── Assign stable IDs to known message patterns ──
                // This allows follow-up messages to UPDATE existing entries
                // (e.g., "Layer 1/3 done" updates the "⚡ Layer 1/3: ..." entry).
                const stepMatch = statusText.match(/^Step (\d+)\/(\d+): (.+)$/);
                const layerStartMatch = statusText.match(/^⚡\s*Layer (\d+)\/(\d+):/);
                const layerDoneMatch = statusText.match(/^Layer (\d+)\/(\d+)\s+done/);

                if (stepMatch) {
                  stepId = `step-${stepMatch[1]}`;
                  displayText = stepMatch[3];
                } else if (statusText.startsWith('Rephraser Agent:')) {
                  stepId = 'rephraser';
                  displayText = statusText.replace('Rephraser Agent: ', '');
                } else if (statusText.startsWith('Planner Agent:')) {
                  stepId = 'planner';
                  displayText = statusText.replace('Planner Agent: ', '');
                } else if (statusText.startsWith('Task Classifier')) {
                  stepId = 'classifier';
                  displayText = statusText;
                } else if (statusText.startsWith('Classifier reasoning')) {
                  stepId = 'classifier-reason';
                  displayText = statusText;
                } else if (layerStartMatch) {
                  stepId = `layer-${layerStartMatch[1]}`;
                  displayText = statusText;
                } else if (layerDoneMatch) {
                  stepId = `layer-${layerDoneMatch[1]}`;
                  displayText = statusText;
                } else if (statusText.startsWith('Execution graph:')) {
                  stepId = 'execution-graph';
                  displayText = statusText;
                } else if (statusText.startsWith('Plan ready')) {
                  stepId = 'plan-ready';
                  displayText = statusText;
                } else {
                  // Fallback: stable ID from content prefix so duplicates can merge
                  stepId = `status-${statusText.slice(0, 40).replace(/[^a-zA-Z0-9]/g, '-').replace(/-+/g, '-')}`;
                  displayText = statusText;
                }

                // ── Determine state ──
                // Priority: error → explicit completion → active work → informational (completed)
                if (statusText.includes('— Error:') || statusText.includes('— Skipped:')) {
                  state = 'error';
                } else if (
                  statusText.endsWith('✓') ||
                  statusText.includes(' done') ||
                  (stepId === 'planner' && (statusText.includes('Plan ready') || statusText.includes('Refined plan'))) ||
                  (stepId === 'rephraser' && !statusText.includes('...'))
                ) {
                  state = 'completed';
                } else if (
                  stepMatch ||                  // Step X/Y in progress
                  statusText.endsWith('...') ||  // Actively running ("Planning steps...")
                  layerStartMatch                // Layer starting parallel work
                ) {
                  state = 'loading';
                } else {
                  // Informational messages (classifier results, execution graph, etc.)
                  // are already done by the time we see them.
                  state = 'completed';
                }

                const steps = statusStepsRef.current;
                const existingIdx = steps.findIndex(s => s.id === stepId);
                const step: StatusStep = { id: stepId, text: displayText, state };
                if (existingIdx >= 0) {
                  steps[existingIdx] = step;
                } else {
                  steps.push(step);
                }
                statusDirtyRef.current = true;
                needsScrollRef.current = true;
              }
              if (parsed.text) {
                accumulatedRef.current += parsed.text;
                needsScrollRef.current = true;
              }
            } catch {
              // skip malformed SSE lines
            }
          }
        };

        xhr.onload = () => resolve();
        xhr.onerror = () => reject(new Error('Network request failed'));
        xhr.ontimeout = () => reject(new Error('Request timed out'));
        xhr.onabort = () => resolve();

        xhr.send(JSON.stringify({ message: text }));
      });
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      // Mark pending steps as failed
      statusStepsRef.current = statusStepsRef.current.map(s =>
        s.state === 'loading' ? { ...s, state: 'error' as const, text: s.text.replace(/\.\.\.$/, '') + ' — Connection lost' } : s
      );
      if (!accumulatedRef.current) {
        accumulatedRef.current = `Connection error: ${(err as Error).message}`;
        needsScrollRef.current = true;
      }
    } finally {
      stopFlushing();
      abortRef.current = null;

      // Safety net: mark any remaining loading steps as completed.
      // The `done` handler above does the same, but this covers edge cases
      // where the stream ended without a done signal (e.g., abrupt close).
      // The catch block already marks loading steps as 'error' for failures,
      // so this only upgrades steps that weren't already handled.
      statusStepsRef.current = statusStepsRef.current.map(s =>
        s.state === 'loading' ? { ...s, state: 'completed' as const } : s
      );

      // Final flush: push remaining text + status steps + clear streaming flag → triggers Markdown render
      const finalText = accumulatedRef.current;
      const finalSteps = [...statusStepsRef.current];
      if (finalText || finalSteps.length > 0) {
        if (!bubbleCreatedRef.current) {
          // Edge case: stream ended before flush timer fired
          setMessages(prev => [...prev, { id: assistantId, role: 'assistant', text: finalText, streaming: false, statusSteps: finalSteps }]);
        } else {
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, text: finalText, streaming: false, statusSteps: finalSteps } : m)
          );
        }
      }

      setStreaming(false);
      requestAnimationFrame(() => scrollToEnd(true));
    }
  }, [input, streaming, scrollToEnd, startFlushing, stopFlushing]);

  // Render item — wrapped in Pressable so tapping anywhere (including text) toggles bottom bar
  // Interactive elements (links, buttons) capture their own taps and won't trigger this
  const renderMessage = useCallback(({ item, index }: { item: Message; index: number }) => (
    <Pressable onPress={toggleBottomBar}>
      <MessageBubble item={item} isFirst={index === 0} />
    </Pressable>
  ), [toggleBottomBar]);

  const keyExtractor = useCallback((m: Message) => m.id, []);

  // Bottom bar slide animation
  const bottomBarTranslateY = bottomBarSlide.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 100],
  });

  // Dynamic padding for chat content: extra space when keyboard + input bar are open
  const INPUT_BAR_HEIGHT = 60; // approximate height of expanded input row
  const BOTTOM_BUTTONS_SPACE = 80; // space for collapsed buttons
  const dynamicPaddingBottom = inputExpanded
    ? keyboardHeight + INPUT_BAR_HEIGHT + 12
    : BOTTOM_BUTTONS_SPACE;

  // React splash screen — shows "Jarvis" text before chat
  if (!splashDone) {
    return (
      <View style={styles.splashScreen}>
        <StatusBar hidden />
        <Text style={styles.splashTitle}>Jarvis</Text>
        <Text style={styles.splashSubtitle}>How can I help you?</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar hidden />

      {/* Chat area — FlatList with tap handler that doesn't block scrolling */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={keyExtractor}
        renderItem={renderMessage}
        style={styles.chatArea}
        contentContainerStyle={[styles.chatContent, { paddingBottom: dynamicPaddingBottom }]}
        keyboardShouldPersistTaps="handled"
        removeClippedSubviews={Platform.OS === 'android'}
        maxToRenderPerBatch={8}
        windowSize={7}
        onScroll={handleScroll}
        scrollEventThrottle={16}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <Pressable style={styles.emptyContainer} onPress={toggleBottomBar}>
            <Text style={styles.emptyTitle}>Jarvis</Text>
            <Text style={styles.emptySubtitle}>How can I help you?</Text>
          </Pressable>
        }
        ListFooterComponent={
          messages.length > 0 ? (
            <Pressable style={styles.tapZone} onPress={toggleBottomBar} />
          ) : null
        }
        ListHeaderComponent={
          messages.length > 0 ? (
            <Pressable style={styles.tapZone} onPress={toggleBottomBar} />
          ) : null
        }
      />

      {/* Bottom bar — absolute overlay */}
      <Animated.View style={[
        styles.bottomOverlay,
        {
          bottom: keyboardHeightAnim,
          transform: [{ translateY: bottomBarTranslateY }],
        },
      ]}>
        {inputExpanded ? (
          /* ─── Expanded: input bar ─── */
          <View style={styles.inputRow}>
            <TouchableOpacity
              style={styles.kbBtn}
              onPress={collapseInputBar}
              activeOpacity={0.7}
            >
              <Text style={styles.kbIcon}>⌨</Text>
            </TouchableOpacity>
            <TextInput
              ref={textInputRef}
              style={styles.textInput}
              value={input}
              onChangeText={(t) => { setInput(t); inputTextRef.current = t; }}
              placeholder="Type a message…"
              placeholderTextColor="#666"
              multiline
              editable={!streaming}
              onSubmitEditing={sendMessage}
              blurOnSubmit={false}
            />
            <TouchableOpacity
              style={[styles.sendBtn, (!input.trim() || streaming) && styles.sendBtnDisabled]}
              onPress={sendMessage}
              disabled={!input.trim() || streaming}
              activeOpacity={0.7}
            >
              <Text style={styles.sendBtnText}>➤</Text>
            </TouchableOpacity>
          </View>
        ) : (
          /* ─── Collapsed: keyboard button + optional scroll button ─── */
          <Pressable style={styles.collapsedRow} onPress={toggleBottomBar}>
            <TouchableOpacity
              style={styles.kbBtn}
              onPress={expandInputBar}
              activeOpacity={0.7}
            >
              <Text style={styles.kbIcon}>⌨</Text>
            </TouchableOpacity>
            {contentOverflows && (
              <Joystick
                onScrollUp={joystickScrollUp}
                onScrollDown={joystickScrollDown}
                onGoTop={joystickGoTop}
                onGoBottom={joystickGoBottom}
              />
            )}
          </Pressable>
        )}
      </Animated.View>
    </View>
  );
}

// ─── Styles ────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },

  chatArea: {
    flex: 1,
  },
  chatContent: {
    paddingHorizontal: 12,
    paddingTop: 6,
    flexGrow: 1,
    justifyContent: 'flex-end',
  },

  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyTitle: {
    color: '#fff',
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
  },
  emptySubtitle: {
    color: '#666',
    fontSize: 16,
  },

  // Tap zone for toggling bottom bar (between messages)
  tapZone: {
    height: 15,
  },

  // User bubble — toned down contrast
  bubble: {
    maxWidth: '80%',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 18,
    marginBottom: 2,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#1a3a6e',
    borderBottomRightRadius: 4,
  },
  bubbleText: {
    fontSize: 15,
    lineHeight: 21,
  },
  userText: {
    color: '#d0d8e8',
  },

  // Assistant: full width, no bubble, no background
  assistantContainer: {
    width: '100%',
    paddingHorizontal: 4,
    paddingVertical: 6,
    marginBottom: 2,
  },
  streamingText: {
    color: '#e0e0e0',
    fontSize: 15,
    lineHeight: 21,
    paddingHorizontal: 4,
  },

  // Bottom overlay — absolute, transparent background
  bottomOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    paddingHorizontal: 12,
    paddingBottom: Platform.OS === 'ios' ? 24 : 12,
  },

  // Collapsed: keyboard button + optional scroll button, spread apart
  collapsedRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },

  // Keyboard button (round)
  kbBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#111',
    borderWidth: 1,
    borderColor: '#2a2a2a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  kbIcon: {
    color: '#888',
    fontSize: 20,
  },

  // Expanded input row — transparent background
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 6,
  },
  textInput: {
    flex: 1,
    minHeight: 42,
    maxHeight: 120,
    backgroundColor: '#111',
    borderRadius: 21,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: '#fff',
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#222',
  },
  sendBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#2563eb',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendBtnDisabled: {
    backgroundColor: '#222',
  },
  sendBtnText: {
    color: '#fff',
    fontSize: 18,
  },

  // Splash screen — matches landing page style
  splashScreen: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  splashTitle: {
    color: '#fff',
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
  },
  splashSubtitle: {
    color: '#666',
    fontSize: 16,
  },
});
