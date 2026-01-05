import React, { useState, useEffect } from 'react';
import { Loader2, Sparkles, Brain, Zap } from 'lucide-react';

const ThinkingLoader = ({ message = "Generating your PDF..." }) => {
    const [thinkingText, setThinkingText] = useState('Thinking');
    const [currentStep, setCurrentStep] = useState(0);

    const thinkingSteps = [
        { icon: Brain, text: 'Analyzing your request', color: 'text-blue-500' },
        { icon: Sparkles, text: 'Crafting the perfect layout', color: 'text-purple-500' },
        { icon: Zap, text: 'Generating LaTeX code', color: 'text-yellow-500' },
        { icon: Loader2, text: 'Finalizing your document', color: 'text-green-500' }
    ];

    // Animate thinking dots
    useEffect(() => {
        const interval = setInterval(() => {
            setThinkingText(prev => {
                if (prev === 'Thinking...') return 'Thinking';
                if (prev === 'Thinking') return 'Thinking.';
                if (prev === 'Thinking.') return 'Thinking..';
                return 'Thinking...';
            });
        }, 400);

        return () => clearInterval(interval);
    }, []);

    // Cycle through thinking steps
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep(prev => (prev + 1) % thinkingSteps.length);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const CurrentIcon = thinkingSteps[currentStep].icon;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                {/* Main spinner */}
                <div className="flex justify-center mb-6">
                    <div className="relative">
                        {/* Outer spinning ring */}
                        <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                        {/* Inner icon */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <CurrentIcon className={`w-8 h-8 ${thinkingSteps[currentStep].color} animate-pulse`} />
                        </div>
                    </div>
                </div>

                {/* Thinking text */}
                <h3 className="text-2xl font-bold text-center mb-2 text-gray-900">
                    {thinkingText}
                </h3>

                {/* Current step */}
                <p className="text-center text-gray-600 mb-6 min-h-[24px] transition-all duration-300">
                    {thinkingSteps[currentStep].text}
                </p>

                {/* Progress steps */}
                <div className="space-y-3">
                    {thinkingSteps.map((step, index) => {
                        const StepIcon = step.icon;
                        const isActive = index === currentStep;
                        const isCompleted = index < currentStep;

                        return (
                            <div
                                key={index}
                                className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${isActive ? 'bg-blue-50 scale-105' : 'bg-gray-50'
                                    }`}
                            >
                                <div
                                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${isActive
                                            ? 'bg-blue-600 text-white'
                                            : isCompleted
                                                ? 'bg-green-500 text-white'
                                                : 'bg-gray-200 text-gray-400'
                                        }`}
                                >
                                    {isCompleted ? (
                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    ) : (
                                        <StepIcon className={`w-4 h-4 ${isActive ? 'animate-pulse' : ''}`} />
                                    )}
                                </div>
                                <span
                                    className={`text-sm font-medium transition-all duration-300 ${isActive ? 'text-gray-900' : 'text-gray-500'
                                        }`}
                                >
                                    {step.text}
                                </span>
                            </div>
                        );
                    })}
                </div>

                {/* Helpful tip */}
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
                    <p className="text-sm text-gray-600 text-center">
                        💡 <span className="font-medium">Pro tip:</span> This usually takes 5-10 seconds. First time might take longer due to server startup.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ThinkingLoader;
