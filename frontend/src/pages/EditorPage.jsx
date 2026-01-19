import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import ChatLoadingStages from '../components/ChatLoadingStages';
import ImagePicker from '../components/ImagePicker';
import PDFViewer from '../components/PDFViewer';
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
    RefreshCw,
    Image as ImageIcon,
    FileText,
    Search,
    Book,
    Lock,
    X,
    Wand2,
    Shield
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
    const [showImagePicker, setShowImagePicker] = useState(false);
    const [mode, setMode] = useState(location.state?.mode || 'normal'); // 'normal' | 'research' | 'ebook'
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [humanizeLoading, setHumanizeLoading] = useState(false);
    const [detectLoading, setDetectLoading] = useState(false);
    const [aiDetectionResult, setAiDetectionResult] = useState(null);

    // Refs for preventing double-firing
    const initialized = useRef(false);
    const messagesEndRef = useRef(null);
    const previewTimeoutRef = useRef(null);

    // Auto-scroll to bottom of chat
    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    // Auto-refresh credits every 30 seconds to keep UI in sync
    useEffect(() => {
        if (!refreshUser) return;

        // Refresh immediately on mount
        refreshUser().catch(err => console.error('Failed to refresh credits:', err));

        // Set up interval for periodic refresh
        const interval = setInterval(() => {
            refreshUser().catch(err => console.error('Failed to refresh credits:', err));
        }, 30000); // 30 seconds

        return () => clearInterval(interval);
    }, [refreshUser]);

    // Load state from localStorage on mount
    useEffect(() => {
        const savedSessionId = localStorage.getItem('hugpdf_sessionId');
        const savedMessages = localStorage.getItem('hugpdf_messages');
        const savedHtml = localStorage.getItem('hugpdf_htmlContent');
        const savedLatex = localStorage.getItem('hugpdf_latexContent');
        const savedMode = localStorage.getItem('hugpdf_mode');

        if (savedSessionId) {
            console.log('Restoring session from storage:', savedSessionId);
            setSessionId(savedSessionId);
            if (savedMessages) setMessages(JSON.parse(savedMessages));
            if (savedHtml) setHtmlContent(savedHtml);
            if (savedLatex) setLatexContent(savedLatex);
            if (savedMode) setMode(savedMode);
        }
    }, [user]); // Re-run if user changes (though mostly on mount)

    // Save state to localStorage whenever it changes
    useEffect(() => {
        if (sessionId) localStorage.setItem('hugpdf_sessionId', sessionId);
        if (messages.length > 0) localStorage.setItem('hugpdf_messages', JSON.stringify(messages));
        if (htmlContent) localStorage.setItem('hugpdf_htmlContent', htmlContent);
        if (latexContent) localStorage.setItem('hugpdf_latexContent', latexContent);
        if (mode) localStorage.setItem('hugpdf_mode', mode);
    }, [sessionId, messages, htmlContent, latexContent, mode]);

    // Handle mode change with Pro user validation
    const handleModeChange = (newMode) => {
        // Check if user is Pro for research and ebook modes
        if (newMode === 'research' || newMode === 'ebook') {
            if (!user) {
                navigate('/auth');
                return;
            }
            if (user.plan !== 'pro') {
                setShowUpgradeModal(true);
                return;
            }
        }
        setMode(newMode);
    };

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
                { prompt: prompt, mode: mode },
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
                ? (error.response?.data?.detail || 'This feature requires a Pro plan. Please upgrade to continue.')
                : 'Sorry, there was an error generating your PDF. Please try again.';

            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: errorMsg },
            ]);

            if (error.response?.status === 402) {
                setTimeout(() => navigate('/pricing'), 3000);
            }
        }
    }, [token, navigate, refreshUser, messages.length, mode]);

    // Check Auth & Initial Prompt
    useEffect(() => {
        const initialPrompt = location.state?.initialPrompt;
        if (initialPrompt && !initialized.current) {
            handleInitialGeneration(initialPrompt);
        }
    }, [location.state, handleInitialGeneration]);

    // Generate Preview
    const generatePreview = useCallback(async (content) => {
        if (!content) {
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
                const response = await axios.post(
                    `${API}/preview-pdf`,
                    { latex_content: content, html_content: content },
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
        // Generate preview when switching to preview tab
        if (activeTab === 'preview' && htmlContent && !pdfPreviewUrl) {
            generatePreview(htmlContent);
        }
    }, [activeTab, htmlContent, pdfPreviewUrl, generatePreview]);

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
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.post(`${API}/chat`, {
                session_id: sessionId,
                message: userMessage,
                current_html: htmlContent,
                mode: mode
            }, { headers });

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
            const errorMsg = error.response?.status === 402
                ? (error.response?.data?.detail || 'This feature requires a Pro plan. Please upgrade to continue.')
                : 'Sorry, there was an error processing your request.';
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: errorMsg }
            ]);

            // Redirect to pricing if 402 error
            if (error.response?.status === 402) {
                setTimeout(() => navigate('/pricing'), 3000);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async () => {
        if (!latexContent && !htmlContent) {
            alert('Please generate a document first before downloading.');
            return;
        }
        setDownloadLoading(true);
        try {
            // Prepare headers with authentication token
            const headers = {};
            if (token) {
                headers.Authorization = `Bearer ${token}`;
            }

            const response = await axios.post(
                `${API}/download-pdf`,
                { latex_content: latexContent, html_content: htmlContent, filename: 'document.pdf' },
                { responseType: 'blob', headers }
            );

            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'document.pdf');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            // Clear loading state immediately after download
            setDownloadLoading(false);

            // Refresh user credits in background (don't block UI)
            // Refresh user credits in background (don't block UI)
            if (refreshUser) {
                // Immediate refresh
                refreshUser().catch(err => console.error('Failed to refresh:', err));

                // Delayed refresh to ensure propagation
                setTimeout(() => {
                    refreshUser().catch(err => console.error('Failed to retry refresh:', err));
                }, 2000);
            }
        } catch (error) {
            console.error('Download error:', error);

            // Handle insufficient credits error
            if (error.response?.status === 402) {
                // Refresh user credits to show updated count
                if (refreshUser) {
                    await refreshUser().catch(err => console.error('Failed to refresh:', err));
                }

                // Show error and redirect to pricing
                // alert('⚠️ No credits remaining!\n\nYou need credits to download PDFs. Redirecting to pricing page...');
                setShowUpgradeModal(true);  // Show upgrade modal instead of alert

                // Immediate redirect
                // navigate('/pricing');
            } else {
                // Other errors
                alert('Error downloading PDF. Please try again.');
            }

            // Ensure loading state is cleared on error
            setDownloadLoading(false);
        }
    };

    const handleImageSelect = async (imageData) => {
        // Create a clean, professional message for display
        let displayMessage;

        if (imageData.photographer === 'User Upload') {
            displayMessage = `Add image: ${imageData.alt}`;
        } else {
            displayMessage = `Add image by ${imageData.photographer}: "${imageData.alt}"`;
        }

        // Include URL for backend processing (hidden from user)
        const backendMessage = `${displayMessage}\n[URL: ${imageData.url}]`;

        // Show clean message to user (without URL)
        setMessages((prev) => [...prev, { role: 'user', content: displayMessage }]);
        setLoading(true);
        setShowImagePicker(false);

        // Send message with URL to backend
        try {
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.post(`${API}/chat`, {
                session_id: sessionId,
                message: backendMessage,
                current_html: htmlContent,
                mode: mode
            }, { headers });

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

    // Humanize Content
    const handleHumanizeContent = async () => {
        if (!latexContent && !htmlContent) {
            alert('Please generate a document first before humanizing.');
            return;
        }

        setHumanizeLoading(true);
        try {
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.post(
                `${API}/rephrasy/humanize`,
                {
                    text: latexContent || htmlContent,
                    model: 'undetectable',
                    language: 'English'
                },
                { headers }
            );

            if (response.data.success && response.data.output) {
                // Update content with humanized version
                setLatexContent(response.data.output);
                setHtmlContent(response.data.output);

                // Add message to chat
                setMessages((prev) => [
                    ...prev,
                    {
                        role: 'assistant',
                        content: `✨ Content humanized successfully! Readability score: ${response.data.flesch_score?.toFixed(1) || 'N/A'}`
                    }
                ]);

                // Refresh preview
                if (activeTab === 'preview') {
                    setPdfPreviewUrl(null);
                    generatePreview(response.data.output);
                }
            } else {
                alert(response.data.error || 'Failed to humanize content. Please try again.');
            }
        } catch (error) {
            console.error('Humanize error:', error);
            alert('Error humanizing content. Please check your API key and try again.');
        } finally {
            setHumanizeLoading(false);
        }
    };

    // Detect AI Content
    const handleDetectAI = async () => {
        if (!latexContent && !htmlContent) {
            alert('Please generate a document first before detection.');
            return;
        }

        setDetectLoading(true);
        try {
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.post(
                `${API}/rephrasy/detect`,
                {
                    text: latexContent || htmlContent,
                    mode: ''
                },
                { headers }
            );

            if (response.data.success && response.data.result) {
                const result = response.data.result;
                setAiDetectionResult(result);

                // Add message to chat with detection results
                const aiScore = result.ai_score || result.score || 'N/A';
                setMessages((prev) => [
                    ...prev,
                    {
                        role: 'assistant',
                        content: `🔍 AI Detection Complete!\n\nAI Score: ${aiScore}\n\nThis content ${typeof aiScore === 'number' && aiScore > 0.5 ? 'appears to be AI-generated' : 'appears to be human-written'}.`
                    }
                ]);
            } else {
                alert(response.data.error || 'Failed to detect AI content. Please try again.');
            }
        } catch (error) {
            console.error('Detection error:', error);
            alert('Error detecting AI content. Please check your API key and try again.');
        } finally {
            setDetectLoading(false);
        }
    };
    return (
        <TooltipProvider>
            <div className="h-dvh flex flex-col bg-background overflow-hidden relative">
                {/* Mobile Header - Always visible on mobile */}
                <div className="md:hidden flex items-center justify-between px-4 py-3 border-b bg-white z-20 shadow-sm flex-shrink-0">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="-ml-2" aria-label="Go back">
                                <ChevronLeft className="h-5 w-5 mr-1" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Go back</p>
                        </TooltipContent>
                    </Tooltip>

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

            {/* Main Content Area - Desktop: side-by-side, Mobile: stacked with tabs */}
            <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
                {/* Sidebar / Chat Panel */}
                <div className={`w-full md:w-1/3 lg:w-[400px] flex flex-col border-r bg-gray-50/50 backdrop-blur-sm 
                    ${activeTab === 'chat' ? 'flex' : 'hidden md:flex'}`}>

                    {/* Desktop Header */}
                    <div className="hidden md:flex p-4 border-b bg-white items-center justify-between shadow-sm z-10 flex-shrink-0">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button variant="ghost" size="icon" onClick={() => navigate('/')} className="h-8 w-8" aria-label="Go back">
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Go back</p>
                            </TooltipContent>
                        </Tooltip>
                        <span className="font-semibold text-sm">Editor</span>
                        <Badge variant="secondary" className="text-xs">
                            {user?.credits || 0} credits
                        </Badge>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-hidden relative w-full">
                        <ScrollArea className="h-full w-full px-4 py-6">
                            <div className="space-y-6 pb-4">
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
                                {loading && <ChatLoadingStages mode={mode} />}
                                <div ref={messagesEndRef} className="h-4" />
                            </div>
                        </ScrollArea>
                    </div>

                    {/* Chat Input Area */}
                    <div className="p-3 md:p-4 bg-white border-t flex-shrink-0 z-10 safe-area-bottom shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] md:shadow-none">
                        {/* Mode Selector */}
                        <div className="mb-3">
                            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none mask-fade-right">
                                <button
                                    onClick={() => handleModeChange('normal')}
                                    className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap border ${mode === 'normal'
                                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                                        }`}
                                >
                                    <FileText className="w-3.5 h-3.5" />
                                    Normal
                                </button>
                                <button
                                    onClick={() => handleModeChange('research')}
                                    className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap border ${mode === 'research'
                                        ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                                        }`}
                                >
                                    <Search className="w-3.5 h-3.5" />
                                    Research
                                    {user?.plan !== 'pro' && <Lock className="w-3 h-3 ml-0.5" />}
                                </button>
                                <button
                                    onClick={() => handleModeChange('ebook')}
                                    className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap border ${mode === 'ebook'
                                        ? 'bg-green-600 text-white border-green-600 shadow-sm'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                                        }`}
                                >
                                    <Book className="w-3.5 h-3.5" />
                                    E-book
                                    {user?.plan !== 'pro' && <Lock className="w-3 h-3 ml-0.5" />}
                                </button>
                            </div>
                            {mode === 'research' && (
                                <div className="mt-2 text-[10px] uppercase tracking-wider text-purple-600 font-bold flex items-center gap-1.5 animate-in fade-in slide-in-from-left-2">
                                    <Search className="w-3 h-3" />
                                    <span>Powered by Perplexity AI</span>
                                </div>
                            )}
                        </div>

                        {/* Image Picker and Rephrasy Buttons */}
                        <div className="flex justify-end gap-2 mb-2">
                            {/* <Button
                                variant="outline"
                                size="sm"
                                onClick={handleDetectAI}
                                disabled={detectLoading || (!latexContent && !htmlContent)}
                                className="text-xs"
                            >
                                {detectLoading ? (
                                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                ) : (
                                    <Shield className="h-3 w-3 mr-1" />
                                )}
                                Check AI
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleHumanizeContent}
                                disabled={humanizeLoading || (!latexContent && !htmlContent)}
                                className="text-xs"
                            >
                                {humanizeLoading ? (
                                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                ) : (
                                    <Wand2 className="h-3 w-3 mr-1" />
                                )}
                                Humanize
                            </Button> */}
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setShowImagePicker(true)}
                                className="text-xs"
                            >
                                <ImageIcon className="h-3 w-3 mr-1" />
                                Insert Image
                            </Button>
                        </div>
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
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        size="icon"
                                        aria-label="Send message"
                                        className={`h-10 w-10 flex-shrink-0 transition-all duration-200 ${input.trim() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                                        onClick={handleSendMessage}
                                        disabled={!input.trim() || loading || !sessionId}
                                    >
                                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p>Send message</p>
                                </TooltipContent>
                            </Tooltip>
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
                                <>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="md:hidden text-xs"
                                        onClick={() => setActiveTab('code')}
                                    >
                                        <Code className="w-4 h-4 mr-1" /> Code
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-xs"
                                        onClick={() => {
                                            setPdfPreviewUrl(null);
                                            if (htmlContent) generatePreview(htmlContent);
                                        }}
                                        disabled={previewLoading || !htmlContent}
                                    >
                                        <Sparkles className="w-4 h-4 md:mr-1" />
                                        <span className="hidden md:inline">Refresh Preview</span>
                                    </Button>
                                </>
                            )}
                            {activeTab === 'code' && (
                                <Button variant="ghost" size="sm" className="md:hidden text-xs" onClick={() => setActiveTab('preview')}>
                                    <Eye className="w-4 h-4 mr-1" /> <span className="hidden sm:inline">PDF</span>
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
                                    <PDFViewer pdfUrl={pdfPreviewUrl} />
                                ) : (
                                    <div className="flex flex-col items-center justify-center p-8 text-gray-400 mt-20">
                                        <Eye className="w-12 h-12 mb-4 opacity-20" />
                                        <p className="text-sm font-medium mb-2">Preview not generated</p>
                                        <p className="text-xs text-gray-500">Click "Refresh Preview" above to generate</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

            </div>

            {/* Image Picker Modal */}
            <ImagePicker
                isOpen={showImagePicker}
                onClose={() => setShowImagePicker(false)}
                onSelectImage={handleImageSelect}
            />

            {/* Upgrade Modal for Pro Features */}
            {showUpgradeModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative">
                        <button
                            onClick={() => setShowUpgradeModal(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                            aria-label="Close modal"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Lock className="w-8 h-8 text-purple-600" />
                            </div>

                            <h3 className="text-2xl font-bold text-gray-900 mb-2">
                                Unlock Full Potential
                            </h3>
                            <p className="text-gray-600 mb-6">
                                Get more PDF downloads, access Research Mode, E-book tools, and priority support. Upgrade to Pro today!
                            </p>

                            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-6">
                                <h4 className="font-semibold text-gray-900 mb-2">Pro Features Include:</h4>
                                <ul className="text-sm text-gray-700 space-y-1 text-left">
                                    <li className="flex items-center gap-2">
                                        <Search className="w-4 h-4 text-purple-600" />
                                        Research Mode with citations
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Book className="w-4 h-4 text-green-600" />
                                        E-book creation (20+ pages)
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <FileText className="w-4 h-4 text-blue-600" />
                                        50 PDF downloads/month
                                    </li>
                                </ul>
                            </div>

                            <div className="flex gap-3">
                                <Button
                                    variant="outline"
                                    onClick={() => setShowUpgradeModal(false)}
                                    className="flex-1"
                                >
                                    Maybe Later
                                </Button>
                                <Button
                                    onClick={() => {
                                        setShowUpgradeModal(false);
                                        navigate('/pricing');
                                    }}
                                    className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                                >
                                    Upgrade to Pro
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            </div>
        </TooltipProvider>
    );
};

export default EditorPage;
