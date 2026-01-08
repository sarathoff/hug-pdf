import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Github, Twitter, Linkedin } from 'lucide-react';
import { Button } from './ui/button';
import { Separator } from './ui/separator';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-white border-t border-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand Section */}
                    <div className="col-span-1 md:col-span-1 flex flex-col gap-4">
                        <Link to="/" className="flex items-center gap-2">
                            <div className="bg-gradient-to-tr from-blue-600 to-purple-600 p-1.5 rounded-lg text-white">
                                <FileText className="h-4 w-4" />
                            </div>
                            <span className="font-bold text-gray-900">HugPDF</span>
                        </Link>
                        <p className="text-sm text-gray-500 leading-relaxed">
                            AI-powered document generation made simple. Create beautiful PDFs in seconds.
                        </p>
                    </div>

                    {/* Links Column 1 */}
                    <div>
                        <h3 className="font-semibold text-gray-900 mb-4 text-sm">Product</h3>
                        <ul className="space-y-3 text-sm text-gray-600">
                            <li><Link to="/pricing" className="hover:text-blue-600 transition-colors">Pricing</Link></li>
                            <li><Link to="/editor" className="hover:text-blue-600 transition-colors">Editor</Link></li>
                            <li><Link to="/features" className="hover:text-blue-600 transition-colors">Features</Link></li>
                        </ul>
                    </div>

                    {/* Links Column 2 */}
                    <div>
                        <h3 className="font-semibold text-gray-900 mb-4 text-sm">Company</h3>
                        <ul className="space-y-3 text-sm text-gray-600">
                            <li><Link to="/about" className="hover:text-blue-600 transition-colors">About</Link></li>
                            <li><Link to="/contact" className="hover:text-blue-600 transition-colors">Contact</Link></li>
                            <li><Link to="/blog" className="hover:text-blue-600 transition-colors">Blog</Link></li>
                        </ul>
                    </div>

                    {/* Links Column 3 */}
                    <div>
                        <h3 className="font-semibold text-gray-900 mb-4 text-sm">Legal</h3>
                        <ul className="space-y-3 text-sm text-gray-600">
                            <li><Link to="/terms" className="hover:text-blue-600 transition-colors">Terms of Service</Link></li>
                            <li><Link to="/privacy" className="hover:text-blue-600 transition-colors">Privacy Policy</Link></li>
                        </ul>
                    </div>
                </div>

                <Separator className="my-8" />

                <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-gray-500">
                        © {currentYear} HugPDF. All rights reserved.
                    </p>

                    <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                            <Twitter className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                            <Github className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-500 hover:text-gray-900">
                            <Linkedin className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
