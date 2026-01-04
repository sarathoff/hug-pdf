import React, { useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import confetti from 'canvas-confetti';

const SuccessPage = () => {
    const [searchParams] = useSearchParams();

    useEffect(() => {
        // Trigger confetti on load
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }, []);

    return (
        <div className="min-h-screen bg-white flex items-center justify-center px-4">
            <div className="max-w-md w-full text-center">
                <div className="mb-8 flex justify-center">
                    <div className="p-4 bg-green-100 rounded-full">
                        <CheckCircle className="w-16 h-16 text-green-600" />
                    </div>
                </div>

                <h1 className="text-4xl font-bold text-gray-900 mb-4">Payment Successful!</h1>
                <p className="text-lg text-gray-600 mb-8">
                    Thank you for your purchase. Your account has been upgraded to Pro.
                </p>

                <div className="space-y-4">
                    <Link
                        to="/editor"
                        className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                    >
                        Start Creating PDFs
                        <ArrowRight className="w-5 h-5" />
                    </Link>

                    <Link
                        to="/"
                        className="block text-gray-500 hover:text-gray-700 font-medium"
                    >
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default SuccessPage;
