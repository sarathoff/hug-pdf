import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────
function timeAgo(dateStr) {
    const diff = (Date.now() - new Date(dateStr)) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return new Date(dateStr).toLocaleDateString();
}

const MODE_INFO = {
    normal: { label: 'Standard', color: 'bg-blue-100 text-blue-700' },
    research: { label: 'Research', color: 'bg-purple-100 text-purple-700' },
    ebook: { label: 'eBook', color: 'bg-amber-100 text-amber-700' },
    ppt: { label: 'Slides', color: 'bg-green-100 text-green-700' },
};

// ──────────────────────────────────────────────
// Skeleton card
// ──────────────────────────────────────────────
function SessionSkeleton() {
    return (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 animate-pulse space-y-3">
            <div className="h-4 bg-gray-100 rounded w-3/4" />
            <div className="h-3 bg-gray-100 rounded w-1/3" />
            <div className="flex gap-2 pt-2">
                <div className="h-8 bg-gray-100 rounded-lg flex-1" />
                <div className="h-8 bg-gray-100 rounded-lg w-16" />
            </div>
        </div>
    );
}

// ──────────────────────────────────────────────
// Empty state
// ──────────────────────────────────────────────
function EmptyState({ onNew }) {
    return (
        <div className="col-span-full flex flex-col items-center justify-center py-24 text-center">
            <div className="w-20 h-20 mb-6 rounded-2xl bg-gradient-to-br from-violet-100 to-blue-100 flex items-center justify-center shadow-inner">
                <svg className="w-10 h-10 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No documents yet</h3>
            <p className="text-gray-500 max-w-xs mb-8">
                Generate your first PDF and it'll appear here so you can continue editing anytime.
            </p>
            <button
                onClick={onNew}
                className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/20 transition-all hover:scale-105 active:scale-95"
            >
                ✨ Create your first PDF
            </button>
        </div>
    );
}

// ──────────────────────────────────────────────
// Session Card
// ──────────────────────────────────────────────
function SessionCard({ session, onContinue, onDelete, deleting }) {
    const modeInfo = MODE_INFO[session.mode] || MODE_INFO.normal;

    return (
        <div className="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-violet-200 transition-all duration-200 p-5 flex flex-col gap-3">
            {/* Mode chip + time */}
            <div className="flex items-center justify-between">
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${modeInfo.color}`}>
                    {modeInfo.label}
                </span>
                <span className="text-xs text-gray-400">{timeAgo(session.created_at)}</span>
            </div>

            {/* Title */}
            <p className="text-sm font-semibold text-gray-800 leading-snug line-clamp-2 flex-1">
                {session.title || 'Untitled Document'}
            </p>

            {/* Actions */}
            <div className="flex gap-2 pt-1">
                <button
                    onClick={() => onContinue(session)}
                    className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-xl transition-all hover:scale-[1.02] active:scale-95 shadow-sm shadow-violet-500/20"
                >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Continue
                </button>
                <button
                    onClick={() => onDelete(session.session_id)}
                    disabled={deleting === session.session_id}
                    className="px-3 py-2 rounded-xl border border-gray-200 hover:border-red-200 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all disabled:opacity-40"
                    title="Delete"
                >
                    {deleting === session.session_id ? (
                        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                        </svg>
                    ) : (
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    )}
                </button>
            </div>
        </div>
    );
}

// ──────────────────────────────────────────────
// Main Dashboard Page
// ──────────────────────────────────────────────
export default function DashboardPage() {
    const navigate = useNavigate();
    const { user, token, loading: authLoading } = useAuth();

    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [deleting, setDeleting] = useState(null);
    const [resuming, setResuming] = useState(null);

    // Redirect if not logged in
    useEffect(() => {
        if (!authLoading && !user) navigate('/auth');
    }, [authLoading, user, navigate]);

    // Fetch sessions
    const fetchSessions = useCallback(async () => {
        if (!token) return;
        try {
            setLoading(true);
            setError(null);
            const res = await axios.get(`${API}/sessions`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSessions(res.data.sessions || []);
        } catch (err) {
            console.error('Failed to fetch sessions:', err);
            setError('Failed to load your documents. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        if (token) fetchSessions();
    }, [token, fetchSessions]);

    // Continue a session — fetch full data then navigate to editor
    const handleContinue = async (session) => {
        setResuming(session.session_id);
        try {
            const res = await axios.get(`${API}/sessions/${session.session_id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = res.data;
            navigate('/editor', {
                state: {
                    sessionId: data.session_id,
                    initialLatex: data.current_latex,
                    skipGeneration: true,
                    messages: data.messages || [],
                    mode: data.mode || 'normal',
                    fromDashboard: true,
                }
            });
        } catch (err) {
            console.error('Failed to load session:', err);
            alert('Could not load this document. Please try again.');
            setResuming(null);
        }
    };

    // Delete a session
    const handleDelete = async (sessionId) => {
        if (!window.confirm('Delete this document? This cannot be undone.')) return;
        setDeleting(sessionId);
        try {
            await axios.delete(`${API}/sessions/${sessionId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSessions(prev => prev.filter(s => s.session_id !== sessionId));
        } catch (err) {
            console.error('Failed to delete session:', err);
            alert('Could not delete this document. Please try again.');
        } finally {
            setDeleting(null);
        }
    };

    if (authLoading) return null;

    return (
        <div className="min-h-screen">
            {/* ── Page header ── */}
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8">
                <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-2xl">📄</span>
                            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">My Documents</h1>
                        </div>
                        <p className="text-gray-500 text-sm">
                            Pick up where you left off — all your generated PDFs in one place.
                        </p>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                        {/* Credits chip */}
                        {user && (
                            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 border border-violet-200 rounded-full">
                                <svg className="w-3.5 h-3.5 text-violet-600" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                <span className="text-xs font-semibold text-violet-700">{user.credits} credits</span>
                            </div>
                        )}
                        <button
                            onClick={() => navigate('/')}
                            className="flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-xl shadow-md shadow-violet-500/20 transition-all hover:scale-105 active:scale-95"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            New PDF
                        </button>
                    </div>
                </div>
            </div>

            {/* ── Content ── */}
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">

                {/* Error banner */}
                {error && (
                    <div className="mb-6 flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
                        <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12A9 9 0 113 12a9 9 0 0118 0z" />
                        </svg>
                        {error}
                        <button onClick={fetchSessions} className="ml-auto underline font-medium">Retry</button>
                    </div>
                )}

                {/* Session count */}
                {!loading && sessions.length > 0 && (
                    <p className="text-sm text-gray-400 mb-4">{sessions.length} document{sessions.length !== 1 ? 's' : ''}</p>
                )}

                {/* Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {loading ? (
                        Array.from({ length: 8 }).map((_, i) => <SessionSkeleton key={i} />)
                    ) : sessions.length === 0 ? (
                        <EmptyState onNew={() => navigate('/')} />
                    ) : (
                        sessions.map(session => (
                            <SessionCard
                                key={session.session_id}
                                session={session}
                                onContinue={handleContinue}
                                onDelete={handleDelete}
                                deleting={deleting}
                            />
                        ))
                    )}
                </div>

                {/* Global resuming overlay */}
                {resuming && (
                    <div className="fixed inset-0 bg-white/70 backdrop-blur-sm z-50 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin" />
                            <p className="text-sm font-semibold text-violet-700">Loading your document…</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
