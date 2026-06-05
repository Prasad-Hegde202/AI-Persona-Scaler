"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import axios from "axios";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
  time: string;
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeAnswer(raw: any): string {
  if (typeof raw === "string") return raw;
  if (raw == null) return "";
  if (typeof raw === "object") {
    return raw.text ?? raw.answer ?? raw.content ?? raw.message ?? JSON.stringify(raw);
  }
  return String(raw);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeSources(raw: any): string[] {
  if (!raw) return [];
  const arr = Array.isArray(raw) ? raw : [raw];
  return arr
    .flat()
    .map((s) => {
      if (typeof s === "string") return s;
      if (s == null) return null;
      if (typeof s === "object") {
        if (s.repo && s.type) return `${s.repo} (${s.type})`;
        if (s.repo) return String(s.repo);
        if (s.name) return String(s.name);
        if (s.title) return String(s.title);
        if (s.url) return String(s.url);
        return JSON.stringify(s);
      }
      return String(s);
    })
    .filter(Boolean) as string[];
}

const SUGGESTIONS = [
  "Tell me about NextStep AI",
  "Why are you a good fit for this role?",
  "Tell me about your NILM project",
  "Explain your Auto-Trader project",
  "Tell me about yourself",
  "Tell me about your experience",
  "What AI projects have you built?",
  "Tell me about your GitHub repositories",
  "What would you enhance in your NILM Project?",
  "Schedule an interview",
];

const PHONE = "+16626578733";
const PHONE_DISPLAY = "+1 (662) 657-8733";

const SunIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
);

const MoonIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
  </svg>
);

const PhoneIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.68A2 2 0 012 1h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
  </svg>
);

export default function Home() {
  const [dark, setDark] = useState(true);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [phoneCopied, setPhoneCopied] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/`)
      .then(() => console.log("Backend Awake"))
      .catch(() => console.log("Backend Waking Up"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handlePhoneClick = () => {
    // On mobile: open dialer. On desktop: copy to clipboard as fallback.
    if (/Mobi|Android/i.test(navigator.userAgent)) {
      window.location.href = `tel:${PHONE}`;
    } else {
      navigator.clipboard.writeText(PHONE_DISPLAY).then(() => {
        setPhoneCopied(true);
        setTimeout(() => setPhoneCopied(false), 2000);
      });
    }
  };

  const sendMessage = async (text?: string) => {
    const content = (text ?? question).trim();
    if (!content || loading) return;
    setMessages((prev) => [...prev, { role: "user", text: content, time: getTime() }]);
    setQuestion("");
    setLoading(true);
    try {
      const { data } = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat`,
        { question: content },
        { timeout: 120000 }
      );
      setMessages((prev) => [...prev, {
        role: "assistant",
        text: normalizeAnswer(data.answer ?? data.response ?? data.result ?? data),
        sources: normalizeSources(data.sources ?? data.references ?? data.context ?? []),
        time: getTime(),
      }]);
    } catch (err: unknown) {
      let errorText = "Could not reach the backend. Please check if the server is running.";
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 429) {
          errorText = "Rate limit reached — the AI is taking a short break. Please wait a moment and try again.";
        } else if (err.response?.data?.error) {
          errorText = `Error: ${err.response.data.error}`;
        }
      }
      setMessages((prev) => [...prev, { role: "assistant", text: errorText, time: getTime() }]);
    }
    setLoading(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const t = dark ? {
    page: "bg-[#0D0F14]",
    shell: "bg-[#161A23] border-[#2A3045]",
    header: "border-[#2A3045]",
    title: "text-[#E8ECF4]",
    sub: "text-[#8892A4]",
    toggle: "bg-[#1E2330] border-[#2A3045] text-[#8892A4] hover:border-[#4F7FFF] hover:text-[#A5BFFF]",
    phonePill: "bg-[#0D2A1A] border-[#1A4A2E] text-[#4ADE80] hover:bg-[#0F3320] hover:border-[#22C55E]",
    phonePillCopied: "bg-[#0F3320] border-[#22C55E] text-[#4ADE80]",
    chat: "bg-[#161A23]",
    empty: "text-[#E8ECF4]",
    emptyP: "text-[#8892A4]",
    emptyIcon: "bg-[#1E2330] border-[#313852]",
    chip: "bg-[#1E2330] border-[#2A3045] text-[#8892A4] hover:bg-[#252B3B] hover:border-[#4F7FFF] hover:text-[#A5BFFF]",
    bubbleBot: "bg-[#1E2330] text-[#E8ECF4] border border-[#2A3045]",
    bubbleUser: "bg-[#4F7FFF] text-white",
    avaBot: "bg-[#1E2330] border border-[#313852] text-[#A5BFFF]",
    avaUser: "bg-[#4F7FFF] text-white",
    ts: "text-[#4E5872]",
    typing: "bg-[#1E2330] border border-[#2A3045]",
    dot: "bg-[#313852]",
    srcTag: "bg-[#252B3B] border-[#313852] text-[#8892A4]",
    footer: "border-[#2A3045] bg-[#161A23]",
    inputWrap: "bg-[#1E2330] border-[#2A3045] focus-within:border-[#4F7FFF]",
    input: "text-[#E8ECF4] placeholder:text-[#4E5872]",
    sendActive: "bg-[#4F7FFF] hover:opacity-90",
    sendDisabled: "bg-[#252B3B]",
    meta: "text-[#4E5872]",
    divider: "bg-[#2A3045]",
  } : {
    page: "bg-[#F0F2F7]",
    shell: "bg-white border-[#DEE3EF]",
    header: "border-[#DEE3EF]",
    title: "text-[#0D1117]",
    sub: "text-[#5A6478]",
    toggle: "bg-[#F4F6FB] border-[#DEE3EF] text-[#5A6478] hover:border-[#3B6EF0] hover:text-[#1A4ACB]",
    phonePill: "bg-[#F0FDF4] border-[#BBF7D0] text-[#16A34A] hover:bg-[#DCFCE7] hover:border-[#4ADE80]",
    phonePillCopied: "bg-[#DCFCE7] border-[#4ADE80] text-[#15803D]",
    chat: "bg-white",
    empty: "text-[#0D1117]",
    emptyP: "text-[#5A6478]",
    emptyIcon: "bg-[#F4F6FB] border-[#C8CEDF]",
    chip: "bg-[#F4F6FB] border-[#DEE3EF] text-[#5A6478] hover:bg-[#EBF0FF] hover:border-[#3B6EF0] hover:text-[#1A4ACB]",
    bubbleBot: "bg-[#EAECF4] text-[#0D1117]",
    bubbleUser: "bg-[#3B6EF0] text-white",
    avaBot: "bg-[#EBF0FF] border border-[#C8CEDF] text-[#1A4ACB]",
    avaUser: "bg-[#3B6EF0] text-white",
    ts: "text-[#9BA3B8]",
    typing: "bg-[#EAECF4]",
    dot: "bg-[#9BA3B8]",
    srcTag: "bg-[#F4F6FB] border-[#C8CEDF] text-[#5A6478]",
    footer: "border-[#DEE3EF] bg-white",
    inputWrap: "bg-[#F4F6FB] border-[#DEE3EF] focus-within:border-[#3B6EF0]",
    input: "text-[#0D1117] placeholder:text-[#9BA3B8]",
    sendActive: "bg-[#3B6EF0] hover:opacity-90",
    sendDisabled: "bg-[#EAECF4]",
    meta: "text-[#9BA3B8]",
    divider: "bg-[#DEE3EF]",
  };

  return (
    <main className={`min-h-screen ${t.page} flex justify-center items-start p-4 md:p-6 transition-colors duration-200`}>
      <div
        className={`w-full max-w-3xl ${t.shell} rounded-2xl border flex flex-col overflow-hidden transition-colors duration-200`}
        style={{ height: "calc(100vh - 3rem)", maxHeight: "700px" }}
      >
        {/* ── Header ── */}
        <div className={`flex items-center gap-3 px-5 py-3.5 border-b ${t.header} flex-shrink-0`}>
          {/* Left: name + subtitle + status */}
          <div className="flex-1 min-w-0">
            <h1 className={`font-semibold text-[15px] ${t.title} leading-tight`}>
              Prasad Hegde — AI Persona
            </h1>
            <p className={`text-[12.5px] ${t.sub} mt-0.5`}>
              Resume · Projects · GitHub · Skills
            </p>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11.5px] text-emerald-400 font-medium">Available</span>
            </div>
          </div>

          {/* Right: phone pill + theme toggle */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Phone pill — opens dialer on mobile, copies on desktop */}
            <button
              onClick={handlePhoneClick}
              title={phoneCopied ? "Copied!" : "Call Prasad"}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[12px] font-medium transition-all ${
                phoneCopied ? t.phonePillCopied : t.phonePill
              }`}
            >
              <PhoneIcon />
              <span className="hidden sm:inline">
                {phoneCopied ? "Copied!" : PHONE_DISPLAY}
              </span>
              <span className="sm:hidden">
                {phoneCopied ? "✓" : "Call"}
              </span>
            </button>

            {/* Theme toggle */}
            <button
              onClick={() => setDark(!dark)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[12px] font-medium transition-all ${t.toggle}`}
            >
              {dark ? <SunIcon /> : <MoonIcon />}
              <span className="hidden sm:inline">{dark ? "Light" : "Dark"}</span>
            </button>
          </div>
        </div>

        {/* ── Chat area ── */}
        <div className={`flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3 ${t.chat} transition-colors duration-200`}>
          {messages.length === 0 && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center py-6">
              <div className={`w-12 h-12 rounded-full ${t.emptyIcon} border flex items-center justify-center`}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
                  className={dark ? "text-[#A5BFFF]" : "text-[#1A4ACB]"}>
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
              </div>
              <div>
                <h2 className={`font-semibold text-[15px] ${t.empty}`}>Ask me anything</h2>
                <p className={`text-[13px] ${t.emptyP} mt-1 max-w-xs mx-auto leading-relaxed`}>
                  Explore Prasad&apos;s work, skills, and projects through conversation.
                </p>
              </div>

              {/* Suggestion chips */}
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className={`${t.chip} border rounded-full px-3.5 py-1.5 text-[12.5px] transition-all`}
                  >
                    {s}
                  </button>
                ))}
              </div>

              {/* CTA — recruiter call-out */}
              <div className={`mt-2 flex items-center gap-2 px-4 py-2.5 rounded-xl border ${dark ? "bg-[#0D2A1A] border-[#1A4A2E]" : "bg-[#F0FDF4] border-[#BBF7D0]"}`}>
                <span className="text-[13px]">📞</span>
                <span className={`text-[12.5px] font-medium ${dark ? "text-[#86EFAC]" : "text-[#15803D]"}`}>
                  Recruiter? Call directly:&nbsp;
                </span>
                <a
                  href={`tel:${PHONE}`}
                  className={`text-[12.5px] font-semibold underline underline-offset-2 ${dark ? "text-[#4ADE80]" : "text-[#16A34A]"}`}
                >
                  {PHONE_DISPLAY}
                </a>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2.5 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-[11px] font-semibold mt-0.5 ${msg.role === "user" ? t.avaUser : t.avaBot}`}>
                {msg.role === "user" ? "You" : "PH"}
              </div>
              <div className={`max-w-[76%] flex flex-col gap-1.5 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`px-3.5 py-2.5 rounded-2xl text-[14px] leading-relaxed whitespace-pre-line ${
                  msg.role === "user" ? `${t.bubbleUser} rounded-br-sm` : `${t.bubbleBot} rounded-bl-sm`
                }`}>
                  {msg.text}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="flex flex-col gap-1.5">
                    <span className={`text-[10.5px] font-medium uppercase tracking-wider px-1 ${t.ts}`}>Sources</span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.sources.map((src, j) => (
                        <span key={j} className={`border rounded px-2.5 py-1 text-[11.5px] font-medium ${t.srcTag}`}>{src}</span>
                      ))}
                    </div>
                  </div>
                )}
                <span className={`text-[11px] px-1 ${t.ts}`}>{msg.time}</span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-2.5">
              <div className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-[11px] font-semibold ${t.avaBot}`}>
                PH
              </div>
              <div className={`${t.typing} rounded-2xl rounded-bl-sm px-4 py-3`}>
                <p className="text-sm">Connecting to AI backend...</p>
                <p className="text-xs opacity-70 mt-1">First request may take up to 60 seconds.</p>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* ── Footer ── */}
        <div className={`px-4 py-3 border-t ${t.footer} flex-shrink-0 transition-colors duration-200`}>
          <div className="flex gap-2 items-center">
            <div className={`flex-1 flex items-center ${t.inputWrap} border rounded-xl transition-colors`}>
              <input
                ref={inputRef}
                type="text"
                placeholder="Type a message…"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                className={`flex-1 bg-transparent border-none outline-none px-4 py-2.5 text-[14px] ${t.input} disabled:opacity-40`}
              />
            </div>
            <button
              onClick={() => sendMessage()}
              disabled={loading || !question.trim()}
              className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all active:scale-95 disabled:cursor-not-allowed ${
                !loading && question.trim() ? t.sendActive : t.sendDisabled
              }`}
              aria-label="Send"
            >
              <svg width="15" height="15" viewBox="0 0 20 20" fill="none">
                <path d="M3 10L17 3L10 17L8.5 11.5L3 10Z" fill="white"/>
              </svg>
            </button>
          </div>

          {/* Footer meta */}
          <div className={`flex items-center justify-center gap-1.5 mt-2 text-[11px] ${t.meta}`}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="opacity-60">
              <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            Responses from Prasad&apos;s resume, GitHub &amp; project docs
            <span className={`mx-1.5 w-px h-3 inline-block ${t.divider}`} />
            <PhoneIcon />
            <a href={`tel:${PHONE}`} className={`font-medium hover:underline ${dark ? "text-[#4ADE80]" : "text-[#16A34A]"}`}>
              {PHONE_DISPLAY}
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
