import React from 'react';
import { Sparkles } from 'lucide-react';
import ChatLoadingStages from './ChatLoadingStages';

const MessageList = ({ messages, loading, pptGenerating, mode, messagesEndRef }) => {
    return (
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
            {((loading || pptGenerating) && <ChatLoadingStages mode={mode} />)}
            <div ref={messagesEndRef} className="h-4" />
        </div>
    );
};

export default React.memo(MessageList);
