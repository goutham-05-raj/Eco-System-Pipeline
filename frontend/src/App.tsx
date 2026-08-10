import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Paperclip, Mic, ArrowUp, PanelLeft, Database, Globe, Activity } from 'lucide-react';
import { fetchOverview, fetchStartups, fetchProducts } from './api/client';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type?: 'text' | 'data_startups' | 'data_products' | 'data_overview';
  data?: any;
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    
    // Simulate AI thinking
    setTimeout(async () => {
      const q = userMsg.content.toLowerCase();
      let response: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: '' };

      if (q.includes('startup') || q.includes('companies')) {
        try {
          const startups = await fetchStartups();
          response.content = `I found ${startups.length} startups in the intelligence database. Here is a snapshot of the latest verified entities:`;
          response.type = 'data_startups';
          response.data = startups.slice(0, 4); // Show top 4
        } catch (e) {
          response.content = "I could not retrieve the startups from the GraphOne backend.";
        }
      } else if (q.includes('product') || q.includes('tools')) {
        try {
          const products = await fetchProducts();
          response.content = `I discovered ${products.length} AI products with extracted pricing models.`;
          response.type = 'data_products';
          response.data = products.slice(0, 4);
        } catch (e) {
          response.content = "Failed to fetch product intelligence.";
        }
      } else if (q.includes('overview') || q.includes('status') || q.includes('pipeline')) {
        try {
           const overview = await fetchOverview();
           response.content = `The GraphOne pipeline is operational. The database currently contains:`;
           response.type = 'data_overview';
           response.data = overview;
        } catch (e) {
           response.content = "The pipeline is currently offline or unreachable.";
        }
      } else {
        response.content = "I am GraphOne's intelligence interface. Ask me about our discovered startups, AI products, research papers, or pipeline metrics.";
      }
      setMessages(prev => [...prev, response]);
    }, 600);
  };

  return (
    <div className="flex h-screen bg-background text-primary overflow-hidden font-sans">
      
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="flex-shrink-0 bg-background border-r border-borderDark flex flex-col"
          >
            <div className="h-14 flex items-center px-4 justify-between">
              <span className="font-semibold tracking-tight">GraphOne Chat</span>
            </div>
            <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
               <div className="text-xs font-medium text-secondary px-2 mb-2">Today</div>
               <button className="w-full text-left px-2 py-2 rounded-md hover:bg-surfaceHover text-sm truncate">Startup Intelligence Query</button>
               <button className="w-full text-left px-2 py-2 rounded-md hover:bg-surfaceHover text-sm truncate">Pipeline Observability</button>
            </div>
            <div className="p-4 border-t border-borderDark flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-surfaceHover flex items-center justify-center font-bold text-sm">G1</div>
              <span className="text-sm font-medium">Administrator</span>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative h-full">
        
        {/* Header */}
        <header className="h-14 flex items-center px-4 justify-between sticky top-0 bg-background/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-2">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-surfaceHover rounded-md text-secondary hover:text-primary transition-colors">
              <PanelLeft size={18} />
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 hover:bg-surfaceHover rounded-md transition-colors text-sm font-medium">
              GraphOne Model <span className="text-secondary text-xs">▼</span>
            </button>
          </div>
          <button className="p-2 hover:bg-surfaceHover rounded-md text-secondary">
            <Settings size={18} />
          </button>
        </header>

        {/* Conversation Area */}
        <div className="flex-1 overflow-y-auto hide-scrollbar w-full">
          {messages.length === 0 ? (
            // Empty State
            <div className="h-full flex flex-col items-center justify-center max-w-[700px] mx-auto px-4 w-full">
              <div className="text-4xl font-bold tracking-tight mb-8">What do you want to know?</div>
              
              <div className="grid grid-cols-2 gap-3 w-full mb-8">
                 <button onClick={() => setInput('Show me the pipeline overview')} className="bg-surface hover:bg-surfaceHover border border-borderDark rounded-xl p-4 text-left transition-colors flex flex-col gap-2">
                    <Activity size={20} className="text-secondary" />
                    <span className="text-sm">Show me the pipeline overview</span>
                 </button>
                 <button onClick={() => setInput('What startups have we discovered?')} className="bg-surface hover:bg-surfaceHover border border-borderDark rounded-xl p-4 text-left transition-colors flex flex-col gap-2">
                    <Database size={20} className="text-secondary" />
                    <span className="text-sm">What startups have we discovered?</span>
                 </button>
              </div>
            </div>
          ) : (
            // Chat flow
            <div className="max-w-[700px] mx-auto w-full px-4 pt-6 pb-32 flex flex-col space-y-8">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                     <div className="w-8 h-8 rounded-full bg-surface border border-borderDark flex-shrink-0 flex items-center justify-center mr-4 mt-1">
                       <span className="text-xs font-bold">G</span>
                     </div>
                  )}
                  
                  <div className={`max-w-[85%] ${msg.role === 'user' ? 'bg-surface px-5 py-3 rounded-2xl rounded-tr-sm text-[15px]' : 'text-[15px] leading-relaxed'}`}>
                    {msg.content}
                    
                    {/* Render Data Cards if attached */}
                    {msg.type === 'data_startups' && msg.data && (
                      <div className="grid grid-cols-2 gap-3 mt-4">
                        {msg.data.map((s: any) => (
                          <div key={s.id} className="bg-surface border border-borderDark p-4 rounded-xl flex flex-col gap-1">
                            <span className="font-semibold">{s.startup_name}</span>
                            <span className="text-xs text-secondary font-mono">{s.source_name} • {s.employee_count_estimate || 'N/A'} emp</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.type === 'data_products' && msg.data && (
                      <div className="grid grid-cols-2 gap-3 mt-4">
                        {msg.data.map((p: any) => (
                          <div key={p.id} className="bg-surface border border-borderDark p-4 rounded-xl flex flex-col gap-1">
                            <span className="font-semibold">{p.product_name}</span>
                            <span className="text-xs text-secondary font-mono">{p.pricing_model || 'Unknown'}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {msg.type === 'data_overview' && msg.data && (
                      <div className="bg-surface border border-borderDark rounded-xl mt-4 p-4 font-mono text-sm">
                        <div className="flex justify-between py-1 border-b border-borderDark">
                          <span className="text-secondary">Startups</span>
                          <span>{msg.data.startups}</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-borderDark">
                          <span className="text-secondary">Products</span>
                          <span>{msg.data.products}</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-borderDark">
                          <span className="text-secondary">Research</span>
                          <span>{msg.data.research}</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-borderDark">
                          <span className="text-secondary">Jobs</span>
                          <span>{msg.data.jobs}</span>
                        </div>
                        <div className="flex justify-between py-1">
                          <span className="text-secondary">News</span>
                          <span>{msg.data.news}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Fixed Composer Bottom */}
        <div className="absolute bottom-0 w-full bg-gradient-to-t from-background via-background to-transparent pt-10 pb-6 px-4">
          <div className="max-w-[700px] mx-auto w-full relative">
            <form onSubmit={handleSubmit} className="relative flex items-center">
              <button type="button" className="absolute left-4 text-secondary hover:text-primary transition-colors">
                <Paperclip size={20} />
              </button>
              
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask GraphOne anything..."
                className="w-full bg-surface border border-borderDark rounded-[32px] pl-12 pr-24 py-4 text-[15px] outline-none focus:border-[#2a2a2a] transition-colors placeholder:text-secondary shadow-lg"
              />
              
              <div className="absolute right-3 flex items-center gap-1">
                <button type="button" className="p-2 text-secondary hover:text-primary transition-colors">
                  <Mic size={20} />
                </button>
                <button 
                  type="submit" 
                  disabled={!input.trim()}
                  className={`w-9 h-9 flex items-center justify-center rounded-full transition-colors ${input.trim() ? 'bg-grokOrange text-white' : 'bg-[#2a2a2a] text-secondary'}`}
                >
                  <ArrowUp size={18} strokeWidth={2.5} />
                </button>
              </div>
            </form>
            <div className="text-center mt-3 text-[11px] text-secondary">
              GraphOne can make mistakes. Verify critical intelligence.
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
