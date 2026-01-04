import React from 'react';
import { FileText, AlertCircle } from 'lucide-react';

const TermsPage = () => {
    const lastUpdated = 'December 31, 2025';

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
            <div className="max-w-4xl mx-auto px-6 py-16">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="flex justify-center mb-4">
                        <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl">
                            <FileText className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl font-bold mb-4">
                        Terms of Service
                    </h1>
                    <p className="text-gray-600">Last updated: {lastUpdated}</p>
                </div>

                {/* Content */}
                <div className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
                    {/* Introduction */}
                    <div>
                        <p className="text-gray-700 leading-relaxed">
                            Welcome to HugPDF. By accessing or using our service, you agree to be bound by these
                            Terms of Service. Please read them carefully.
                        </p>
                    </div>

                    {/* Acceptance of Terms */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            By accessing and using HugPDF, you accept and agree to be bound by the terms and
                            provision of this agreement. If you do not agree to these terms, please do not use our service.
                        </p>
                    </section>

                    {/* Use License */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Use License</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            Permission is granted to temporarily use HugPDF for personal, non-commercial purposes.
                            This is the grant of a license, not a transfer of title, and under this license you may not:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>Modify or copy the materials</li>
                            <li>Use the materials for any commercial purpose</li>
                            <li>Attempt to decompile or reverse engineer any software</li>
                            <li>Remove any copyright or proprietary notations</li>
                            <li>Transfer the materials to another person or "mirror" the materials on any other server</li>
                        </ul>
                    </section>

                    {/* User Responsibilities */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Responsibilities</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            You are responsible for:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>Maintaining the confidentiality of any content you create</li>
                            <li>All activities that occur under your usage</li>
                            <li>Ensuring your use complies with applicable laws and regulations</li>
                            <li>Not using the service to generate illegal, harmful, or offensive content</li>
                        </ul>
                    </section>

                    {/* AI-Generated Content */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">4. AI-Generated Content</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            HugPDF uses Google Gemini AI to generate content. You acknowledge that:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>AI-generated content may not always be accurate or appropriate</li>
                            <li>You are responsible for reviewing and verifying all generated content</li>
                            <li>We do not guarantee the quality, accuracy, or suitability of generated content</li>
                            <li>You should not rely solely on AI-generated content for critical decisions</li>
                        </ul>
                    </section>

                    {/* Disclaimer */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Disclaimer</h2>
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-3">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                                <p className="text-sm text-gray-700">
                                    The materials on HugPDF are provided on an 'as is' basis. We make no warranties,
                                    expressed or implied, and hereby disclaim and negate all other warranties including, without
                                    limitation, implied warranties or conditions of merchantability, fitness for a particular
                                    purpose, or non-infringement of intellectual property or other violation of rights.
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Limitations */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Limitations</h2>
                        <p className="text-gray-700 leading-relaxed">
                            In no event shall HugPDF or its creators be liable for any damages (including, without
                            limitation, damages for loss of data or profit, or due to business interruption) arising out of
                            the use or inability to use the materials on our service.
                        </p>
                    </section>

                    {/* Service Availability */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Service Availability</h2>
                        <p className="text-gray-700 leading-relaxed">
                            We reserve the right to modify, suspend, or discontinue the service at any time without notice.
                            We will not be liable if for any reason all or any part of the service is unavailable at any time.
                        </p>
                    </section>

                    {/* Modifications */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Revisions and Errata</h2>
                        <p className="text-gray-700 leading-relaxed">
                            We may revise these terms of service at any time without notice. By using this service, you are
                            agreeing to be bound by the then current version of these terms of service.
                        </p>
                    </section>

                    {/* Governing Law */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Governing Law</h2>
                        <p className="text-gray-700 leading-relaxed">
                            These terms and conditions are governed by and construed in accordance with applicable laws,
                            and you irrevocably submit to the exclusive jurisdiction of the courts in that location.
                        </p>
                    </section>

                    {/* Contact */}
                    <section className="border-t border-gray-200 pt-6">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
                        <p className="text-gray-700 leading-relaxed">
                            If you have any questions about these Terms of Service, please contact us at{' '}
                            <a href="mailto:contact@hugpdf.app" className="text-blue-600 hover:underline">
                                contact@hugpdf.app
                            </a>
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default TermsPage;
