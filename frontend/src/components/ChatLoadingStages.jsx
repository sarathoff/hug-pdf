import React, { useState, useEffect } from 'react';
import { Brain, FileText, Sparkles, CheckCircle2, Loader2 } from 'lucide-react';

const stages = [
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

const ChatLoadingStages = () => {
    const [currentStage, setCurrentStage] = useState(0);
    const [progress, setProgress] = useState(0);

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
            setCurrentStage((prev) => (prev + 1) % stages.length);
            setProgress(0);
        }, 2000);

        return () => {
            clearInterval(progressInterval);
            clearInterval(stageInterval);
        };
    }, []);

    const CurrentIcon = stages[currentStage].icon;

    return (
        <div className="flex justify-start">
            <div className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3 sm:px-4 py-2 sm:py-3 ${stages[currentStage].bgColor} border border-gray-200`}>
                <div className="flex items-center gap-2 mb-2">
                    <CurrentIcon className={`w-4 h-4 ${stages[currentStage].color} animate-pulse`} />
                    <span className="text-xs sm:text-sm text-gray-700 font-medium">
                        {stages[currentStage].text}
                    </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div
                        className={`h-full ${stages[currentStage].color.replace('text-', 'bg-')} transition-all duration-100 ease-linear`}
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Stage indicators */}
                <div className="flex items-center gap-1 mt-2">
                    {stages.map((stage, index) => (
                        <div
                            key={index}
                            className={`h-1 flex-1 rounded-full transition-all duration-300 ${index < currentStage
                                ? 'bg-green-500'
                                : index === currentStage
                                    ? stages[currentStage].color.replace('text-', 'bg-')
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
