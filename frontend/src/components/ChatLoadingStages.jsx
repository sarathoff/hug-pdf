import React, { useState, useEffect } from 'react';
import { Brain, FileText, Sparkles, CheckCircle2, Loader2, Presentation } from 'lucide-react';

const defaultStages = [
    {
        icon: Brain,
        text: 'Thinking...',
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        duration: 2000
    },
    {
        icon: FileText,
        text: 'Planning structure...',
        color: 'text-purple-500',
        bgColor: 'bg-purple-50',
        duration: 2000
    },
    {
        icon: Sparkles,
        text: 'Generating content...',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50',
        duration: 2000
    },
    {
        icon: CheckCircle2,
        text: 'Finalizing...',
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        duration: 2000
    },
];

const ebookStages = [
    {
        icon: Brain,
        text: 'Planning 20+ page structure...',
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        duration: 3000
    },
    {
        icon: FileText,
        text: 'Writing chapters (this takes ~1 min)...',
        color: 'text-purple-500',
        bgColor: 'bg-purple-50',
        duration: 15000
    },
    {
        icon: Sparkles,
        text: 'Formatting pages & Table of Contents...',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50',
        duration: 5000
    },
    {
        icon: CheckCircle2,
        text: 'Polishing output...',
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        duration: 2000
    },
];

const researchStages = [
    {
        icon: Brain,
        text: 'Searching for academic sources...',
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        duration: 3000
    },
    {
        icon: FileText,
        text: 'Analyzing & Citing data...',
        color: 'text-purple-500',
        bgColor: 'bg-purple-50',
        duration: 4000
    },
    {
        icon: Sparkles,
        text: 'Writing research paper...',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50',
        duration: 3000
    },
    {
        icon: CheckCircle2,
        text: 'Finalizing bibliography...',
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        duration: 2000
    },
];

const pptStages = [
    {
        icon: Brain,
        text: 'Structuring presentation outline...',
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        duration: 2000
    },
    {
        icon: FileText,
        text: 'Generating slide content...',
        color: 'text-purple-500',
        bgColor: 'bg-purple-50',
        duration: 3000
    },
    {
        icon: Presentation,
        text: 'Designing slide layouts...',
        color: 'text-orange-500',
        bgColor: 'bg-orange-50',
        duration: 3000
    },
    {
        icon: CheckCircle2,
        text: 'Finalizing deck...',
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        duration: 2000
    },
];

const ChatLoadingStages = ({ mode = 'normal' }) => {
    const [currentStage, setCurrentStage] = useState(0);
    const [progress, setProgress] = useState(0);

    // Select stages based on mode
    let currentStages = defaultStages;
    if (mode === 'ebook') currentStages = ebookStages;
    if (mode === 'research') currentStages = researchStages;
    if (mode === 'ppt') currentStages = pptStages;

    useEffect(() => {
        // Reset stage when mode changes
        setCurrentStage(0);
        setProgress(0);
    }, [mode]);

    useEffect(() => {
        // Progress bar animation
        const progressInterval = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 100) return 0;
                return prev + 2;
            });
        }, 100);

        // Stage cycling
        const stageInterval = setInterval(() => {
            setCurrentStage((prev) => (prev + 1) % currentStages.length);
            setProgress(0);
        }, currentStages[currentStage].duration || 2000);

        return () => {
            clearInterval(progressInterval);
            clearInterval(stageInterval);
        };
    }, [currentStages, currentStage]);

    const CurrentIcon = currentStages[currentStage].icon;

    return (
        <div className="flex justify-start">
            <div className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3 sm:px-4 py-2 sm:py-3 ${currentStages[currentStage].bgColor} border border-gray-200`}>
                <div className="flex items-center gap-2 mb-2">
                    <CurrentIcon className={`w-4 h-4 ${currentStages[currentStage].color} animate-pulse`} />
                    <span className="text-xs sm:text-sm text-gray-700 font-medium">
                        {currentStages[currentStage].text}
                    </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div
                        className={`h-full ${currentStages[currentStage].color.replace('text-', 'bg-')} transition-all duration-100 ease-linear`}
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Stage indicators */}
                <div className="flex items-center gap-1 mt-2">
                    {currentStages.map((stage, index) => (
                        <div
                            key={index}
                            className={`h-1 flex-1 rounded-full transition-all duration-300 ${index < currentStage
                                ? 'bg-green-500'
                                : index === currentStage
                                    ? currentStages[currentStage].color.replace('text-', 'bg-')
                                    : 'bg-gray-300'
                                }`}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ChatLoadingStages;
