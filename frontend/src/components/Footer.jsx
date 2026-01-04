import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Heart } from 'lucide-react';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    const footerLinks = [
        { path: '/about', label: 'About' },
        { path: '/contact', label: 'Contact' },
        { path: '/terms', label: 'Terms' },
        { path: '/privacy', label: 'Privacy' },
    ];

    return (
        <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Brand Section */}
                    <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-2">
                            <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                                <FileText className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                HugPDF
                            </span>
                        </div>
                        <p className="text-sm text-gray-600">
                            Create beautiful PDFs with AI-powered document generation.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Quick Links</h3>
                        <ul className="space-y-2">
                            {footerLinks.map((link) => (
                                <li key={link.path}>
                                    <Link
                                        to={link.path}
                                        className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
                                    >
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* About Section */}
                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">About</h3>
                        <p className="text-sm text-gray-600 mb-2">
                            Powered by Google Gemini AI and built with modern web technologies.
                        </p>
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                            <span>Made with</span>
                            <Heart className="w-4 h-4 text-red-500 fill-current" />
                            <span>by Sarath</span>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-gray-600">
                            © {currentYear} HugPDF. All rights reserved.
                        </p>
                        <p className="text-sm text-gray-600">
                            Built with React, FastAPI & Supabase
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
