import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import ChatLoadingStages from '../components/ChatLoadingStages';
import { Sparkles } from 'lucide-react';

// Shadcn UI Components
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { ScrollArea } from '../components/ui/scroll-area';
import { Card } from '../components/ui/card';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../components/ui/tooltip';

// Icons
import {
    Send,
    Download,
    Loader2,
    Eye,
    Code,
    ZoomIn,
    ZoomOut,
    Maximize2,
    Minimize2,
    ChevronLeft,
    RefreshCw
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditorPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, token, refreshUser } = useAuth();

    // State
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [htmlContent, setHtmlContent] = useState('');
    const [latexContent, setLatexContent] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [pdfPreviewUrl, setPdfPreviewUrl] = useState(null);
    const [previewLoading, setPreviewLoading] = useState(false);
    const [previewError, setPreviewError] = useState(null);
    const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'preview' | 'code'
    const [downloadLoading, setDownloadLoading] = useState(false);
    const [pdfZoom, setPdfZoom] = useState(100);
    const [isFullscreen, setIsFullscreen] = useState(false);

    // Refs for preventing double-firing
    const initialized = useRef(false);
    const messagesEndRef = useRef(null);
    const iframeRef = useRef(null);
    const previewTimeoutRef = useRef(null);

    // Auto-scroll to bottom of chat
    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    // Initial Generation
    const handleInitialGeneration = useCallback(async (prompt) => {
        // Prevent double-initialization
        if (initialized.current) return;
        if (messages.length > 0) return; // Don't run if messages already exist

        initialized.current = true; // Mark as initialized immediately

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

            // Deduplicate: Only add if not already present (failsafe)
            setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg && lastMsg.content === response.data.message) {
                    return prev;
                }
                return [
                    ...prev,
                    {
                        role: 'assistant',
                        content: response.data.message,
                    },
                ];
            });

            setLoading(false); // Stop loading immediately after content

            // Run user refresh in background
            if (refreshUser) refreshUser().catch(console.error);

            if (window.innerWidth >= 768) {
                setActiveTab('preview');
            }

        } catch (error) {
            setLoading(false);
            console.error('Error generating initial content:', error);
            const errorMsg = error.response?.status === 402
                ? 'Insufficient credits. Please purchase more credits to continue.'
                : 'Sorry, there was an error generating your PDF. Please try again.';

            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: errorMsg },
            ]);

            if (error.response?.status === 402) {
                setTimeout(() => navigate('/pricing'), 3000);
            }
        }
    }, [token, navigate, refreshUser, messages.length]);

    // Check Auth & Initial Prompt
    useEffect(() => {
        const initialPrompt = location.state?.initialPrompt;
        if (initialPrompt && !initialized.current) {
            handleInitialGeneration(initialPrompt);
        }
    }, [location.state, handleInitialGeneration]);

    // Generate Preview
    const generatePreview = useCallback(async (html, latex) => {
        const contentForPreview = latex || html;
        if (!contentForPreview) {
            setPdfPreviewUrl(null);
            setPreviewLoading(false);
            return;
        }

        setPreviewLoading(true);
        setPreviewError(null);

        if (previewTimeoutRef.current) {
            clearTimeout(previewTimeoutRef.current);
        }

        previewTimeoutRef.current = setTimeout(async () => {
            try {
                // Optimization: Use LaTeX if available, otherwise fall back to HTML
                const response = await axios.post(
                    `${API}/preview-pdf`,
                    {
                        latex_content: latex || undefined,
                        html_content: html
                    },
                    { responseType: 'blob' }
                );

                const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
                setPdfPreviewUrl((prevUrl) => {
                    if (prevUrl) window.URL.revokeObjectURL(prevUrl);
                    return url;
                });

            } catch (error) {
                console.error('Error generating preview:', error);
                const errorDetail = error.response?.data?.detail || 'Failed to refresh preview.';
                setPreviewError(errorDetail);
            } finally {
                setPreviewLoading(false);
            }
        }, 2000);
    }, []);

    useEffect(() => {
        // Trigger preview generation when either HTML or LaTeX content changes
        if (htmlContent || latexContent) {
            generatePreview(htmlContent, latexContent);
        }
    }, [htmlContent, latexContent, generatePreview]);

    // Cleanup
    useEffect(() => {
        return () => {
            if (pdfPreviewUrl) window.URL.revokeObjectURL(pdfPreviewUrl);
            if (previewTimeoutRef.current) clearTimeout(previewTimeoutRef.current);
        };
    }, [pdfPreviewUrl]);

    // Send Message
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
            if (response.data.latex_content) setLatexContent(response.data.latex_content);

            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: response.data.message }
            ]);

            if (window.innerWidth >= 768) {
                setActiveTab('preview');
            }
        } catch (error) {
            console.error('Error in chat:', error);
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: 'Sorry, there was an error processing your request.' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async () => {
        if (!latexContent && !htmlContent) return;
        setDownloadLoading(true);
        try {
            const response = await axios.post(
                `${API}/download-pdf`,
                { latex_content: latexContent, html_content: htmlContent, filename: 'document.pdf' },
                { responseType: 'blob', headers: token ? { Authorization: `Bearer ${token}` } : {} }
            );
            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'document.pdf');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            alert('Error downloading PDF.');
        } finally {
            setDownloadLoading(false);
        }
    };

    return (
        <div className="h-dvh flex flex-col md:flex-row bg-background overflow-hidden relative">
            {/* Mobile Header */}
            <div className="md:hidden flex items-center justify-between px-4 py-3 border-b bg-white z-20 shadow-sm flex-shrink-0">
                <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="-ml-2">
                    <ChevronLeft className="h-5 w-5 mr-1" />
                </Button>

                {/* Mobile Tabs */}
                <div className="flex bg-gray-100 rounded-lg p-1">
                    <button
                        onClick={() => setActiveTab('chat')}
                        className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${activeTab === 'chat' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500'}`}
                    >
                        Chat
                    </button>
                    <button
                        onClick={() => setActiveTab('preview')}
                        className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${activeTab === 'preview' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500'}`}
                    >
                        PDF
                    </button>
                </div>

                <div className="w-8"></div>
            </div>

            {/* Sidebar / Chat Panel */}
            <div className={`w-full md:w-1/3 lg:w-[400px] flex flex-col border-r bg-gray-50/50 backdrop-blur-sm
                ${activeTab === 'chat' ? 'flex h-full' : 'hidden md:flex'}`}>

                {/* Desktop Header */}
                <div className="hidden md:flex p-4 border-b bg-white items-center justify-between shadow-sm z-10 flex-shrink-0">
                    <Button variant="ghost" size="icon" onClick={() => navigate('/')} className="h-8 w-8">
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <span className="font-semibold text-sm">Editor</span>
                    <Badge variant="secondary" className="text-xs">
                        {user?.credits || 0} credits
                    </Badge>
                </div>

                {/* Messages Area */}
                <ScrollArea className="flex-1 px-4 py-6">
                    <div className="space-y-6 max-w-full pb-4">
                        {messages.length === 0 && !loading && (
                            <div className="text-center p-8 text-gray-400 mt-10">
                                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <Sparkles className="w-8 h-8 text-blue-400 opacity-60" />
                                </div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Start Creating</h3>
                                <p className="text-sm">Describe the PDF you want to create in the box below.</p>
                            </div>
                        )}
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`rounded-2xl px-5 py-3.5 max-w-[85%] text-sm leading-relaxed shadow-sm ${message.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-br-none'
                                        : 'bg-white border text-gray-800 rounded-bl-none'
                                        }`}
                                >
                                    <p className="whitespace-pre-wrap break-words">{message.content}</p>
                                </div>
                            </div>
                        ))}
                        {loading && <ChatLoadingStages />}
                        <div ref={messagesEndRef} />
                    </div>
                </ScrollArea>

                {/* Chat Input Area */}
                <div className="p-3 md:p-4 bg-white border-t flex-shrink-0 sticky bottom-0 z-10 safe-area-bottom shadow-lg md:shadow-none">
                    <div className="relative flex items-end gap-2 bg-gray-50 rounded-xl p-2 border border-gray-200 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
                        <Textarea
                            placeholder="Describe changes..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSendMessage();
                                }
                            }}
                            className="min-h-[50px] max-h-[120px] bg-transparent border-0 focus-visible:ring-0 resize-none p-2 text-sm leading-normal w-full"
                        />
                        <Button
                            size="icon"
                            className={`h-10 w-10 flex-shrink-0 transition-all duration-200 ${input.trim() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                            onClick={handleSendMessage}
                            disabled={!input.trim() || loading || !sessionId}
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>

            {/* Preview Panel */}
            <div className={`flex-1 flex flex-col bg-gray-100 ${isFullscreen ? 'fixed inset-0 z-50' : 'relative h-full'}
                ${(activeTab === 'preview' || activeTab === 'code') ? 'flex' : 'hidden md:flex'}`}>

                {/* Toolbar */}
                <div className="h-14 border-b bg-white flex items-center justify-between px-4 shadow-sm z-10 flex-shrink-0">
                    <div className="flex items-center gap-2">
                        <div className="hidden md:flex bg-gray-100 rounded-lg p-1">
                            <button
                                onClick={() => setActiveTab('preview')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab !== 'code' ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}
                            >
                                <Eye className="w-3 h-3 inline mr-1" /> Preview
                            </button>
                            <button
                                onClick={() => setActiveTab('code')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'code' ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}
                            >
                                <Code className="w-3 h-3 inline mr-1" /> Code
                            </button>
                        </div>
                        {activeTab === 'code' && (
                            <span className="md:hidden text-sm font-semibold">LaTeX Source</span>
                        )}
                        {activeTab === 'preview' && (
                            <span className="md:hidden text-sm font-semibold">PDF Preview</span>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                        {activeTab === 'preview' && (
                            <Button variant="ghost" size="sm" className="md:hidden text-xs" onClick={() => setActiveTab('code')}>
                                <Code className="w-4 h-4 mr-1" /> Code
                            </Button>
                        )}
                        {activeTab === 'code' && (
                            <Button variant="ghost" size="sm" className="md:hidden text-xs" onClick={() => setActiveTab('preview')}>
                                <Eye className="w-4 h-4 mr-1" /> PDF
                            </Button>
                        )}

                        <Button
                            variant="default"
                            size="sm"
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md h-8 text-xs sm:text-sm px-3 sm:px-4"
                            onClick={handleDownloadPDF}
                            disabled={downloadLoading}
                        >
                            {downloadLoading ? <Loader2 className="h-3 w-3 animate-spin mr-1 sm:mr-2" /> : <Download className="h-3 w-3 mr-1 sm:mr-2" />}
                            Download
                        </Button>
                    </div>
                </div>

                {/* Preview Content */}
                <div className="flex-1 overflow-hidden relative bg-gray-200/50 flex justify-center items-start overflow-y-auto p-0 sm:p-4">
                    {activeTab === 'code' ? (
                        <div className="w-full h-full p-2 sm:p-0 max-w-4xl">
                            <Card className="w-full h-full shadow-sm border-0 rounded-none sm:rounded-lg overflow-hidden">
                                <textarea
                                    className="w-full h-full p-4 font-mono text-xs sm:text-sm resize-none focus:outline-none bg-white text-gray-800"
                                    value={latexContent || htmlContent}
                                    readOnly
                                />
                            </Card>
                        </div>
                    ) : (
                        <div className="relative w-full h-full flex justify-center">
                            {previewLoading && (
                                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20">
                                    <div className="bg-gray-900/80 backdrop-blur text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-xs font-medium animate-pulse">
                                        <Loader2 className="w-3 h-3 animate-spin" />
                                        Updating Preview...
                                    </div>
                                </div>
                            )}

                            {previewError && (
                                <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-20 max-w-md w-full px-4">
                                    <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg shadow-lg">
                                        <p className="font-semibold text-sm mb-1">Preview Error</p>
                                        <p className="text-xs whitespace-pre-wrap">{previewError}</p>
                                    </div>
                                </div>
                            )}

                            {pdfPreviewUrl ? (
                                <div className="w-full h-full bg-gray-200/50 overflow-auto flex justify-center py-8">
                                    <iframe
                                        ref={iframeRef}
                                        src={`${pdfPreviewUrl}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`}
                                        className="h-[calc(100vh-140px)] w-[90%] max-w-4xl shadow-2xl bg-white"
                                        style={{ minHeight: '800px' }}
                                        title="PDF Preview"
                                    />
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center p-8 text-gray-400 mt-20">
                                    <Eye className="w-12 h-12 mb-4 opacity-20" />
                                    <p className="text-sm">Preview will appear here</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default EditorPage;
