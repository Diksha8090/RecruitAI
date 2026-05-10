import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineSparkles, HiOutlinePaperAirplane, HiOutlineRefresh, HiOutlineUser } from 'react-icons/hi';
import toast from 'react-hot-toast';
import Topbar from '../components/Topbar';
import { chatAPI } from '../services';

const SUGGESTIONS = [
  'Who are the top 3 candidates?',
  'Which candidates have Python skills?',
  'Compare the qualifications of all candidates',
  'What positions are currently open?',
  'Who has the highest GitHub score?',
  'Show me candidates with 3+ years experience',
];

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5
        ${isUser ? 'bg-gradient-to-br from-teal to-brand-blue' : 'bg-dark-600 border border-dark-500'}`}>
        {isUser ? <HiOutlineUser className="text-dark-900 text-sm" /> : <HiOutlineSparkles className="text-teal text-sm" />}
      </div>
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed
        ${isUser ? 'bg-teal text-dark-900 font-medium rounded-tr-sm' : 'bg-dark-700 border border-dark-500 text-gray-300 rounded-tl-sm'}`}>
        {msg.content}
      </div>
    </motion.div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your AI HR assistant. I have access to all your candidates, job postings, and analysis data. Ask me anything about your hiring pipeline!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (text) => {
    const content = text || input.trim();
    if (!content || loading) return;
    const userMsg = { role: 'user', content };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = [...messages, userMsg].slice(1).map(m => ({ role: m.role, content: m.content }));
      const res = await chatAPI.hrChat(history);
      setMessages(m => [...m, { role: 'assistant', content: res.data.reply }]);
    } catch (err) {
      setMessages(m => [...m, { role: 'assistant', content: 'Something went wrong. Please try again.' }]);
      toast.error('Chat error');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setMessages([{
      role: 'assistant',
      content: "Hi! I'm your AI HR assistant. Ask me anything about your hiring pipeline!"
    }]);
  };

  return (
    <div className="flex flex-col h-full">
      <Topbar title="AI HR Assistant" subtitle="Ask questions about your candidates and jobs" />

      <div className="flex flex-1 overflow-hidden">
        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((m, i) => <Message key={i} msg={m} />)}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-dark-600 border border-dark-500 flex items-center justify-center">
                  <HiOutlineSparkles className="text-teal text-sm" />
                </div>
                <div className="bg-dark-700 border border-dark-500 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1.5">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-dark-500 bg-dark-900/50">
            <div className="flex gap-3 max-w-4xl mx-auto">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
                placeholder="Ask about candidates, skills, rankings..."
                className="input flex-1"
                disabled={loading}
              />
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() => send()}
                disabled={loading || !input.trim()}
                className="btn-primary px-4"
              >
                <HiOutlinePaperAirplane className="text-lg" />
              </motion.button>
              <motion.button whileTap={{ scale: 0.95 }} onClick={reset}
                className="w-11 h-11 bg-dark-700 border border-dark-500 rounded-lg flex items-center justify-center text-gray-400 hover:text-white hover:border-teal transition-all">
                <HiOutlineRefresh className="text-lg" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Sidebar suggestions */}
        <div className="hidden lg:flex flex-col w-72 border-l border-dark-500 p-5 space-y-4 overflow-y-auto">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Suggested Questions</p>
            <div className="space-y-2">
              {SUGGESTIONS.map(s => (
                <motion.button
                  key={s}
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => send(s)}
                  disabled={loading}
                  className="w-full text-left text-sm text-gray-400 px-3 py-2.5 rounded-lg bg-dark-700 border border-dark-500 hover:border-teal/50 hover:text-white transition-all"
                >
                  {s}
                </motion.button>
              ))}
            </div>
          </div>

          <div className="card bg-gradient-to-br from-teal/10 to-brand-blue/10 border-teal/20">
            <HiOutlineSparkles className="text-teal text-xl mb-2" />
            <p className="text-sm font-semibold text-white mb-1">AI-Powered Insights</p>
            <p className="text-xs text-gray-500">I can analyze candidates, compare profiles, find skill gaps, and give hiring recommendations based on your data.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
