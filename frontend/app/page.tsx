"use client";

import { useState, useEffect, useRef } from "react";
import { Upload, Send, Loader2, Brain, BarChart3, Sparkles, Zap, Shield, TrendingUp, Activity, CheckCircle2, ArrowRight, Command, Database } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { VisxChart } from "@/components/VisxChart";

interface QueryResult {
  query_id: string;
  query_text: string;
  result: {
    type: string;
    agents_executed: string[];
    analysis?: any;
    visualization?: any;
    insight?: any;
  };
  execution_time_ms: number;
}

// Simple markdown-to-JSX renderer for insight text
const renderMarkdown = (text: string) => {
  // Split by lines to handle structure
  const lines = text.split('\n');
  
  return lines.map((line, i) => {
    // Bold text: **text** -> <strong>text</strong>
    let processed = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Italic text: *text* -> <em>text</em>
    processed = processed.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // Code: `text` -> <code>text</code>
    processed = processed.replace(/`(.+?)`/g, '<code class="px-1 py-0.5 bg-white/10 rounded text-sm">$1</code>');
    
    return (
      <span key={i} dangerouslySetInnerHTML={{ __html: processed }} className="block mb-2" />
    );
  });
};

// Custom typing effect component
const TypingEffect = ({ text }: { text: string }) => {
  const [displayedText, setDisplayedText] = useState("");
  
  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      setDisplayedText(text.substring(0, index));
      index++;
      if (index > text.length) clearInterval(interval);
    }, 15); // Fast typing
    return () => clearInterval(interval);
  }, [text]);

  return <span>{displayedText}</span>;
};

// Chat bubble loading indicator with animated dots
const ChatBubbleLoader = () => {
  return (
    <div className="self-start max-w-fit">
      <div className="glass-panel px-6 py-5 flex items-center gap-1.5">
        <div className="flex items-center gap-2 mr-3">
          <div className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
            <Brain className="w-3.5 h-3.5 text-purple-400" />
          </div>
        </div>
        <span className="chat-dot w-2 h-2 rounded-full bg-slate-400" style={{ animationDelay: '0ms' }} />
        <span className="chat-dot w-2 h-2 rounded-full bg-slate-400" style={{ animationDelay: '150ms' }} />
        <span className="chat-dot w-2 h-2 rounded-full bg-slate-400" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch from browser extensions
  useEffect(() => { setMounted(true); }, []);

  // Auto-scroll to bottom of conversation
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [results, loading]);

  // Keyboard shortcut focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setDatasetId(data.dataset_id);
    } catch (error) {
      console.error("Upload error:", error);
      alert("Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!datasetId || !query.trim()) return;

    const currentQuery = query;
    setQuery("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: datasetId, query: currentQuery }),
      });

      const data = await response.json();
      setResults([{ ...data, query_text: currentQuery }, ...results]);
    } catch (error) {
      console.error("Query error:", error);
      alert("Failed to execute query");
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <>
      <div className="space-canvas" />
      
      {/* State 1: The Singularity (Empty State) */}
      <AnimatePresence>
        {!datasetId && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 flex flex-col items-center justify-center z-20 p-6"
          >
            <div className="text-center mb-12">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full glass-pill"
              >
                <Sparkles className="w-3 h-3 text-purple-400" />
                <span className="text-xs font-mono tracking-widest text-slate-300 uppercase">
                  multi-agent system
                </span>
              </motion.div>
              
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-6xl md:text-8xl font-bold tracking-tighter mb-4 glow-text bg-gradient-to-br from-white via-slate-200 to-slate-500 bg-clip-text text-transparent"
              >
                justaskit
              </motion.h1>
              
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-xl md:text-2xl text-slate-400 font-light tracking-wide"
              >
                upload csv → ask question → get answer
              </motion.p>
            </div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="relative w-full max-w-2xl group"
            >
              {/* Glowing aura effect behind dropzone */}
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 rounded-[2rem] blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-700" />
              
              <div className="relative glass-panel p-12 text-center rounded-[2rem] overflow-hidden">
                <input
                  type="file"
                  accept=".csv,.xlsx"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                
                <div className="relative z-0 flex flex-col items-center pointer-events-none">
                  {uploading ? (
                    <motion.div 
                      className="w-24 h-24 mb-6 rounded-full bg-purple-500/20 flex items-center justify-center animate-pulse-glow"
                    >
                      <Loader2 className="w-10 h-10 text-purple-400 animate-spin" />
                    </motion.div>
                  ) : (
                    <div className="w-24 h-24 mb-6 rounded-full bg-white/5 flex items-center justify-center border border-white/10 group-hover:scale-110 transition-transform duration-500 group-hover:border-purple-400/50 group-hover:shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                      <Database className="w-10 h-10 text-slate-300 group-hover:text-white transition-colors" />
                    </div>
                  )}
                  
                  <h3 className="text-2xl font-semibold text-white mb-2">
                    {uploading ? "reading your data..." : "drop a csv"}
                  </h3>
                  <p className="text-slate-400 font-mono text-sm max-w-sm">
                    csv or excel. agents will handle the rest.
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* State 2, 3 & 4: Command Center & Revelation */}
      <AnimatePresence>
        {datasetId && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col h-screen overflow-hidden relative z-10 pt-6"
          >
            {/* Top Bar Identity */}
            <div className="absolute top-6 left-6 z-50 flex items-center gap-3 glass-pill px-4 py-2">
              <Database className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-medium text-white">{file?.name || 'Dataset'}</span>
              <span className="text-xs text-slate-500 font-mono px-2 border-l border-white/10">ID: {datasetId}</span>
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse-glow-green" />
            </div>

            {/* Conversation Area */}
            <div 
              ref={scrollRef}
              className="flex-1 overflow-y-auto pb-48 px-4 w-full max-w-5xl mx-auto scroll-smooth"
            >
              <div className="flex flex-col justify-end min-h-full gap-8 pt-24">
                
                {results.length === 0 && !loading && (
                   <motion.div 
                     initial={{ opacity: 0, y: 10 }}
                     animate={{ opacity: 1, y: 0 }}
                     className="text-center self-center my-auto"
                   >
                     <Sparkles className="w-12 h-12 text-purple-400/50 mx-auto mb-6" />
                     <h2 className="text-3xl font-light text-slate-200 mb-2">ready</h2>
                     <p className="text-slate-500 font-mono text-sm">ask anything about your data</p>
                   </motion.div>
                )}

                {results.map((res, i) => (
                  <motion.div 
                    key={res.query_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="flex flex-col gap-6 w-full"
                  >
                    {/* User Query */}
                    <div className="self-end max-w-[80%]">
                      <div className="px-6 py-4 rounded-3xl rounded-tr-sm bg-gradient-to-br from-purple-600/20 to-pink-500/10 border border-purple-500/20 backdrop-blur-md">
                        <p className="text-lg text-white font-medium">{res.query_text}</p>
                      </div>
                    </div>

                    {/* AI Response Card */}
                    <div className="self-start max-w-[90%] w-full">
                      <div className="glass-panel p-8 relative overflow-hidden group">
                        
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                        
                        {/* Header Details */}
                        <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
                           <div className="flex items-center gap-3">
                             <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                               <Brain className="w-4 h-4 text-purple-400" />
                             </div>
                             <div className="flex gap-2">
                               {res.result.agents_executed.map((agent, ai) => (
                                 <Badge key={ai} variant="outline" className="font-mono text-[10px] text-slate-400 border-white/10 bg-black/20">
                                   {agent}
                                 </Badge>
                               ))}
                             </div>
                           </div>
                        </div>

                        {/* Main Content */}
                        <div className="space-y-8">
                          {res.result.insight?.text && (
                            <div className="prose prose-invert max-w-none">
                              <div className="text-lg leading-relaxed text-slate-200 tracking-wide">
                                {renderMarkdown(res.result.insight.text)}
                              </div>
                            </div>
                          )}

                          {res.result.visualization?.chart_json && (
                            <motion.div 
                              initial={{ opacity: 0, filter: "blur(10px)", y: 20 }}
                              animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
                              transition={{ delay: 0.5, duration: 0.8 }}
                              className="mt-8 rounded-2xl bg-[#030303] border border-white/5 p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] h-[400px]"
                            >
                              <VisxChart data={res.result.visualization.chart_json.data} />
                            </motion.div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}

                {/* Loading State: Chat Bubble */}
                {loading && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="w-full"
                  >
                    <ChatBubbleLoader />
                  </motion.div>
                )}
              </div>
            </div>

            {/* Prompt Bar (Omnipresent bottom Raycast style) */}
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-[#030303] via-[#030303]/90 to-transparent pb-12 pt-20">
              <div className="max-w-4xl mx-auto">
                <div className="relative group">
                  {/* Subtle outer glow on prompt */}
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/0 via-purple-500/30 to-pink-500/0 rounded-[2rem] blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-700" />
                  
                  <div className="relative flex items-center glass-input rounded-2xl overflow-hidden shadow-2xl">
                    <div className="pl-6 text-slate-500">
                      <Sparkles className="w-6 h-6" />
                    </div>
                    
                    <Input
                      ref={inputRef}
                      placeholder="ask anything... (⌘K)"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleQuery();
                        }
                      }}
                      disabled={loading}
                      className="flex-1 bg-transparent border-0 h-16 text-lg text-white placeholder:text-slate-600 focus-visible:ring-0 focus-visible:ring-offset-0 px-4"
                    />
                    
                    <button
                      onClick={handleQuery}
                      disabled={!query.trim() || loading}
                      className="mr-2 h-12 w-12 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed group-focus-within:bg-purple-500/20 group-focus-within:text-purple-300"
                    >
                      {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                
                {/* Floating Examples */}
                {results.length === 0 && !loading && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1 }}
                        className="flex flex-wrap items-center justify-center gap-3 mt-6"
                    >
                        {["Show revenue trends", "Top 3 categories", "Predict next quarter"].map((ex) => (
                            <button 
                                key={ex} 
                                onClick={() => setQuery(ex)}
                                className="px-4 py-2 rounded-full glass-pill text-sm text-slate-400 hover:text-white hover:bg-white/10 transition-all font-mono"
                            >
                                {ex} ↗
                            </button>
                        ))}
                    </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
