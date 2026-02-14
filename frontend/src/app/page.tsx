'use client';

import { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'ai';
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [dream, setDream] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleDream = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/dream');
      const data = await res.json();
      setDream(data.dream);
    } catch (error) {
      console.error('Error fetching dream:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!res.ok) throw new Error('Network response was not ok');

      const data = await res.json();
      const aiMessage: Message = { role: 'ai', content: data.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [...prev, { role: 'ai', content: 'Sorry, I encountered an error.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-4 bg-gray-50 text-gray-900">
      <div className="z-10 w-full max-w-2xl flex-col items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-2xl font-bold mb-4">Dreamer</h1>
        
        <div className="w-full bg-white shadow-md rounded-lg p-4 h-[70vh] overflow-y-auto mb-4 flex flex-col gap-3">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg max-w-[80%] ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white self-end'
                  : 'bg-gray-200 text-gray-800 self-start'
              }`}
            >
              {msg.content}
            </div>
          ))}
          {loading && <div className="text-gray-500 text-xs italic self-start">Thinking...</div>}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="w-full flex gap-2">
          <input
            type="text"
            className="flex-grow p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-400"
            disabled={loading}
          >
            Send
          </button>
          <button
            type="button"
            onClick={handleDream}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:bg-purple-400"
            disabled={loading}
          >
            ✨ Dream
          </button>
        </form>

        {dream && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl p-6 max-w-lg w-full shadow-2xl border-t-4 border-purple-500 max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-serif italic text-purple-800 mb-4">A Dream Sequence...</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-wrap italic">
                {dream}
              </div>
              <button 
                onClick={() => setDream(null)}
                className="mt-6 w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors"
              >
                Return to reality
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}