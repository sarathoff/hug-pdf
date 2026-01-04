import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Send, Download, Loader2, Home, CreditCard, LogOut, Eye, Code } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditorPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, token, refreshUser, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState('');
  const [latexContent, setLatexContent] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState(null);
  const [showSource, setShowSource] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const iframeRef = useRef(null);
  const previewTimeoutRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleInitialGeneration = useCallback(async (prompt) => {
    setMessages([{ role: 'user', content: prompt }]);
    setLoading(true);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.post(
        `${API}/generate-initial`,
        { prompt: prompt },
        { headers }
      );

      setSessionId(response.data.session_id);
      setHtmlContent(response.data.html_content);
      if (response.data.latex_content) {
        setLatexContent(response.data.latex_content);
      }
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.message,
        },
      ]);

      // Refresh user data to update credits
      if (refreshUser) {
        await refreshUser();
      }
    } catch (error) {
      console.error('Error generating initial content:', error);
      const errorMsg = error.response?.status === 402
        ? 'Insufficient credits. Please purchase more credits to continue.'
        : 'Sorry, there was an error generating your PDF. Please try again.';

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: errorMsg,
        },
      ]);

      if (error.response?.status === 402) {
        setTimeout(() => navigate('/pricing'), 2000);
      }
    } finally {
      setLoading(false);
    }
  }, [token, navigate, refreshUser]);

  const generatePreview = useCallback(async (content) => {
    if (!content) {
      setPdfPreviewUrl(null);
      setPreviewError(null);
      setPreviewLoading(false);
      return;
    }

    // Set loading immediately (before debounce)
    setPreviewLoading(true);
    setPreviewError(null);

    // Clear any existing timeout
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current);
    }

    // Debounce preview generation
    previewTimeoutRef.current = setTimeout(async () => {
      try {
        const response = await axios.post(
          `${API}/preview-pdf`,
          {
            latex_content: content,
            html_content: content
          },
          {
            responseType: 'blob'
          }
        );

        // Create new blob URL
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));

        // Revoke old URL to prevent memory leaks (using functional update to avoid dependency)
        setPdfPreviewUrl((prevUrl) => {
          if (prevUrl) {
            window.URL.revokeObjectURL(prevUrl);
          }
          return url;
        });

        setPreviewError(null);
        setPreviewLoading(false);
      } catch (error) {
        console.error('Error generating preview:', error);
        setPreviewError(error.response?.data?.detail || 'Failed to generate preview. Please check your LaTeX syntax.');
        setPdfPreviewUrl(null);
        setPreviewLoading(false);
      }
    }, 1500); // 1.5 second debounce
  }, []); // No dependencies needed

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }

    const initialPrompt = location.state?.initialPrompt;
    if (initialPrompt && messages.length === 0) {
      handleInitialGeneration(initialPrompt);
    }
  }, [location.state, user, navigate, messages.length, handleInitialGeneration]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Generate preview when content changes
  useEffect(() => {
    if (htmlContent) {
      generatePreview(htmlContent);
    }
  }, [htmlContent, generatePreview]);

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      if (pdfPreviewUrl) {
        window.URL.revokeObjectURL(pdfPreviewUrl);
      }
      if (previewTimeoutRef.current) {
        clearTimeout(previewTimeoutRef.current);
      }
    };
  }, [pdfPreviewUrl]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading || !sessionId) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: userMessage,
        current_html: htmlContent
      });

      setHtmlContent(response.data.html_content);
      if (response.data.latex_content) {
        setLatexContent(response.data.latex_content);
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.message }
      ]);
    } catch (error) {
      console.error('Error in chat:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownloadPDF = async () => {
    console.log('Download button clicked');
    console.log('latexContent:', latexContent ? `${latexContent.substring(0, 100)}...` : 'null');
    console.log('htmlContent:', htmlContent ? `${htmlContent.substring(0, 100)}...` : 'null');

    if (!latexContent && !htmlContent) {
      console.error('No content available for download');
      alert('No content available. Please generate a document first.');
      return;
    }

    setDownloadLoading(true);
    try {
      console.log('Sending download request to:', `${API}/download-pdf`);
      const response = await axios.post(
        `${API}/download-pdf`,
        {
          latex_content: latexContent,
          html_content: htmlContent,
          filename: 'document.pdf'
        },
        {
          responseType: 'blob',
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
      );

      console.log('Download response received, size:', response.data.size);

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'document.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      console.log('Download completed successfully');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      console.error('Error response:', error.response);

      // Try to read error message from blob if it's a text response
      if (error.response?.data instanceof Blob) {
        const text = await error.response.data.text();
        console.error('Error details:', text);
        try {
          const errorData = JSON.parse(text);
          alert(errorData.detail || 'Error downloading PDF. Please try again.');
        } catch {
          alert(text || 'Error downloading PDF. Please try again.');
        }
      } else {
        const errorMsg = error.response?.data?.detail || error.message || 'Error downloading PDF. Please try again.';
        alert(errorMsg);
      }
    } finally {
      setDownloadLoading(false);
    }
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
          {user && (
            <div className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded-lg">
              <CreditCard className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-semibold text-blue-900">{user.credits} Credits</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="text-gray-600 hover:text-red-600 hover:bg-red-50"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
          <Button
            onClick={handleDownloadPDF}
            disabled={!htmlContent || downloadLoading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white flex items-center gap-2"
          >
            {downloadLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Download PDF
              </>
            )}
          </Button>
        </div>
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
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
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
                disabled={!input.trim() || loading || !sessionId}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white p-3 rounded-xl"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="w-1/2 bg-gray-100 p-6 overflow-hidden">
          <div className="h-full bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
            {htmlContent ? (
              <>
                <div className="bg-gray-800 text-white px-4 py-2 flex items-center justify-between">
                  <span className="text-sm font-mono">
                    {showSource ? 'LaTeX Source Code' : 'PDF Preview'}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowSource(!showSource)}
                    className="text-white hover:bg-gray-700 flex items-center gap-2"
                  >
                    {showSource ? (
                      <>
                        <Eye className="w-4 h-4" />
                        Show Preview
                      </>
                    ) : (
                      <>
                        <Code className="w-4 h-4" />
                        Show Source
                      </>
                    )}
                  </Button>
                </div>
                {showSource ? (
                  <textarea
                    value={htmlContent}
                    readOnly
                    className="flex-1 w-full p-4 font-mono text-sm border-0 resize-none focus:outline-none bg-gray-50"
                    style={{ fontFamily: 'Consolas, Monaco, "Courier New", monospace' }}
                  />
                ) : (
                  <div className="flex-1 relative">
                    {previewLoading && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
                        <div className="text-center">
                          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">Generating preview...</p>
                        </div>
                      </div>
                    )}
                    {previewError && (
                      <div className="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
                        <div className="text-center p-6">
                          <p className="text-sm text-red-600 mb-2">Preview Error</p>
                          <p className="text-xs text-red-500">{previewError}</p>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => generatePreview(htmlContent)}
                            className="mt-4"
                          >
                            Retry
                          </Button>
                        </div>
                      </div>
                    )}
                    {pdfPreviewUrl && !previewLoading && !previewError && (
                      <iframe
                        ref={iframeRef}
                        src={pdfPreviewUrl}
                        className="w-full h-full border-0"
                        title="PDF Preview"
                      />
                    )}
                    {!pdfPreviewUrl && !previewLoading && !previewError && (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        <div className="text-center">
                          <p className="text-lg font-medium">Preview will appear here</p>
                          <p className="text-sm mt-2">Waiting for content...</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <p className="text-lg font-medium">PDF preview will appear here</p>
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
