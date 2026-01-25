import React, { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Slider } from './ui/slider';
import { Loader2 } from 'lucide-react';

const PPTSetupForm = ({ onGenerate, onCancel, isGenerating }) => {
    const [inputMode, setInputMode] = useState('topic'); // 'topic' or 'content'
    const [topic, setTopic] = useState('');
    const [content, setContent] = useState('');
    const [numSlides, setNumSlides] = useState([10]);
    const [style, setStyle] = useState('minimal');

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (inputMode === 'topic' && !topic.trim()) {
            alert('Please enter a topic');
            return;
        }
        
        if (inputMode === 'content' && !content.trim()) {
            alert('Please enter some content');
            return;
        }

        onGenerate({
            topic: inputMode === 'topic' ? topic : null,
            content: inputMode === 'content' ? content : null,
            numSlides: 10,
            style: 'minimal'
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            {/* Input Mode Selection */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                    How would you like to create your presentation?
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() => setInputMode('topic')}
                        className={`p-4 rounded-xl border-2 transition-all text-left ${
                            inputMode === 'topic'
                                ? 'border-orange-500 bg-orange-50 text-orange-700'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }`}
                    >
                        <div className="font-semibold mb-1">From Topic</div>
                        <div className="text-xs">AI researches and creates slides</div>
                    </button>
                    <button
                        type="button"
                        onClick={() => setInputMode('content')}
                        className={`p-4 rounded-xl border-2 transition-all text-left ${
                            inputMode === 'content'
                                ? 'border-orange-500 bg-orange-50 text-orange-700'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }`}
                    >
                        <div className="font-semibold mb-1">From Content</div>
                        <div className="text-xs">Convert your text to slides</div>
                    </button>
                </div>
            </div>

            {/* Topic or Content Input */}
            {inputMode === 'topic' ? (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Presentation Topic
                    </label>
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="e.g., Climate Change..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        disabled={isGenerating}
                    />
                    <p className="mt-2 text-xs text-gray-500">
                        AI will research this topic and create professional slides
                    </p>
                </div>
            ) : (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Content
                    </label>
                    <Textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Paste your content here..."
                        className="min-h-[150px] resize-none"
                        disabled={isGenerating}
                    />
                    <p className="mt-2 text-xs text-gray-500">
                        AI will organize your content into slides
                    </p>
                </div>
            )}

            {/* Credit Usage Info */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="font-medium text-orange-900">Professional Presentation</div>
                        <div className="text-sm text-orange-700">Detailed research, structured slides, and relevant images</div>
                    </div>
                    <div className="flex flex-col items-end">
                        <div className="text-2xl font-bold text-orange-600">1 Credit</div>
                        <div className="text-xs text-orange-600">per presentation</div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
                <Button
                    type="button"
                    variant="outline"
                    onClick={onCancel}
                    className="flex-1"
                    disabled={isGenerating}
                >
                    Cancel
                </Button>
                <Button
                    type="submit"
                    className="flex-1 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white"
                    disabled={isGenerating}
                >
                    {isGenerating ? (
                        <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Generating...
                        </>
                    ) : (
                        'Generate Presentation'
                    )}
                </Button>
            </div>
        </form>
    );
};

export default PPTSetupForm;
