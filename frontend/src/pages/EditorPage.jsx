import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Send, Download, Loader2, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { mockGeneratePDF, mockChatResponse } from '../utils/mockData';

const EditorPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState('');
  const messagesEndRef = useRef(null);
  const iframeRef = useRef(null);

  useEffect(() => {
    const initialPrompt = location.state?.initialPrompt;
    if (initialPrompt && messages.length === 0) {
      handleInitialGeneration(initialPrompt);
    }
  }, [location.state]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInitialGeneration = async (prompt) => {
    setMessages([{ role: 'user', content: prompt }]);
    setLoading(true);

    // Mock delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const generatedHTML = mockGeneratePDF(prompt);
    setHtmlContent(generatedHTML);
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: "I've generated your PDF content. You can see the preview on the right. Feel free to ask me to modify anything!",
      },
    ]);
    setLoading(false);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    // Mock delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const response = mockChatResponse(userMessage, htmlContent);
    setHtmlContent(response.html);
    setMessages((prev) => [...prev, { role: 'assistant', content: response.message }]);
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownloadPDF = () => {
    // Mock download - will be implemented with backend
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'document.html';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Home
          </Button>
          <h1 className="text-xl font-semibold text-gray-800">PDF Editor</h1>
        </div>
        <Button
          onClick={handleDownloadPDF}
          disabled={!htmlContent}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Download PDF
        </Button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-white">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl px-4 py-3 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  <span className="text-sm text-gray-600">Generating...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me to modify the PDF..."
                rows={3}
                className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!input.trim() || loading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white p-3 rounded-xl"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="w-1/2 bg-gray-100 p-6 overflow-hidden">
          <div className="h-full bg-white rounded-lg shadow-lg overflow-hidden">
            {htmlContent ? (
              <iframe
                ref={iframeRef}
                srcDoc={htmlContent}
                title="PDF Preview"
                className="w-full h-full border-0"
                sandbox="allow-same-origin"
              />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <p className="text-lg font-medium">Preview will appear here</p>
                  <p className="text-sm mt-2">Start by describing what you want to create</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditorPage;