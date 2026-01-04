import React from 'react';
import { Shield, Lock, Eye, Database, Cookie } from 'lucide-react';

const PrivacyPage = () => {
    const lastUpdated = 'December 31, 2025';

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
            <div className="max-w-4xl mx-auto px-6 py-16">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="flex justify-center mb-4">
                        <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl">
                            <Shield className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl font-bold mb-4">
                        Privacy Policy
                    </h1>
                    <p className="text-gray-600">Last updated: {lastUpdated}</p>
                </div>

                {/* Content */}
                <div className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
                    {/* Introduction */}
                    <div>
                        <p className="text-gray-700 leading-relaxed">
                            At HugPDF, we take your privacy seriously. This Privacy Policy explains how we collect,
                            use, and protect your information when you use our service.
                        </p>
                    </div>

                    {/* Information Collection */}
                    <section>
                        <div className="flex items-center gap-3 mb-4">
                            <Database className="w-6 h-6 text-blue-600" />
                            <h2 className="text-2xl font-bold text-gray-900">1. Information We Collect</h2>
                        </div>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            We collect minimal information to provide our service:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li><strong>Session Data:</strong> Temporary session IDs to maintain your editing session</li>
                            <li><strong>Content Data:</strong> The prompts and content you create (stored temporarily)</li>
                            <li><strong>Usage Data:</strong> Basic analytics about how the service is used</li>
                            <li><strong>Technical Data:</strong> Browser type, device information, and IP address</li>
                        </ul>
                    </section>

                    {/* How We Use Information */}
                    <section>
                        <div className="flex items-center gap-3 mb-4">
                            <Eye className="w-6 h-6 text-blue-600" />
                            <h2 className="text-2xl font-bold text-gray-900">2. How We Use Your Information</h2>
                        </div>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            We use the collected information to:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>Provide and maintain the PDF generation service</li>
                            <li>Improve and optimize our service</li>
                            <li>Understand how users interact with our platform</li>
                            <li>Detect and prevent technical issues</li>
                            <li>Comply with legal obligations</li>
                        </ul>
                    </section>

                    {/* Data Storage */}
                    <section>
                        <div className="flex items-center gap-3 mb-4">
                            <Lock className="w-6 h-6 text-blue-600" />
                            <h2 className="text-2xl font-bold text-gray-900">3. Data Storage and Security</h2>
                        </div>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-3">
                            <p className="text-sm text-gray-700 mb-2">
                                <strong>Database:</strong> We use Supabase (PostgreSQL) to store session data securely.
                            </p>
                            <p className="text-sm text-gray-700">
                                <strong>Security:</strong> All data is transmitted over HTTPS and stored with industry-standard encryption.
                            </p>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                            Your session data and generated content are stored temporarily to enable the chat and editing
                            features. We do not permanently store your generated documents unless you explicitly save them.
                        </p>
                    </section>

                    {/* Third-Party Services */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Third-Party Services</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            We use the following third-party services:
                        </p>
                        <div className="space-y-3">
                            <div className="border border-gray-200 rounded-lg p-4">
                                <h3 className="font-semibold text-gray-900 mb-1">Google Gemini AI</h3>
                                <p className="text-sm text-gray-600">
                                    Used for AI-powered content generation. Your prompts are sent to Google's servers for processing.
                                    Please review{' '}
                                    <a
                                        href="https://policies.google.com/privacy"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        Google's Privacy Policy
                                    </a>
                                    {' '}for more information.
                                </p>
                            </div>
                            <div className="border border-gray-200 rounded-lg p-4">
                                <h3 className="font-semibold text-gray-900 mb-1">Supabase</h3>
                                <p className="text-sm text-gray-600">
                                    Used for database hosting. Please review{' '}
                                    <a
                                        href="https://supabase.com/privacy"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        Supabase's Privacy Policy
                                    </a>
                                    {' '}for more information.
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Cookies */}
                    <section>
                        <div className="flex items-center gap-3 mb-4">
                            <Cookie className="w-6 h-6 text-blue-600" />
                            <h2 className="text-2xl font-bold text-gray-900">5. Cookies and Tracking</h2>
                        </div>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            We use minimal cookies and local storage to:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>Maintain your session while using the service</li>
                            <li>Remember your preferences</li>
                            <li>Analyze usage patterns (anonymized)</li>
                        </ul>
                        <p className="text-gray-700 leading-relaxed mt-3">
                            You can disable cookies in your browser settings, but this may affect the functionality of our service.
                        </p>
                    </section>

                    {/* Data Retention */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Data Retention</h2>
                        <p className="text-gray-700 leading-relaxed">
                            We retain session data only for as long as necessary to provide the service. Session data is
                            automatically deleted after a period of inactivity. We do not permanently store your generated
                            PDFs on our servers.
                        </p>
                    </section>

                    {/* Your Rights */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Your Rights</h2>
                        <p className="text-gray-700 leading-relaxed mb-3">
                            You have the right to:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                            <li>Access the data we have about you</li>
                            <li>Request deletion of your data</li>
                            <li>Object to processing of your data</li>
                            <li>Request data portability</li>
                            <li>Withdraw consent at any time</li>
                        </ul>
                    </section>

                    {/* Children's Privacy */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Children's Privacy</h2>
                        <p className="text-gray-700 leading-relaxed">
                            Our service is not intended for children under 13 years of age. We do not knowingly collect
                            personal information from children under 13. If you are a parent or guardian and believe your
                            child has provided us with personal information, please contact us.
                        </p>
                    </section>

                    {/* Changes to Policy */}
                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Changes to This Policy</h2>
                        <p className="text-gray-700 leading-relaxed">
                            We may update this Privacy Policy from time to time. We will notify you of any changes by posting
                            the new Privacy Policy on this page and updating the "Last updated" date.
                        </p>
                    </section>

                    {/* Contact */}
                    <section className="border-t border-gray-200 pt-6">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
                        <p className="text-gray-700 leading-relaxed">
                            If you have any questions about this Privacy Policy, please contact us at{' '}
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

export default PrivacyPage;
