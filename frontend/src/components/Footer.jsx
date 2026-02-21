import React from 'react';
import { Link } from 'react-router-dom';
import { Github, Twitter, Linkedin } from 'lucide-react';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-white border-t border-slate-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Main footer grid */}
                <div className="py-12 grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-12">
                    {/* Brand Column */}
                    <div className="col-span-2 md:col-span-1 space-y-4">
                        <Link to="/" className="flex items-center gap-2.5 group">
                            <img
                                src="/logo.png"
                                alt="HugPDF Logo"
                                className="h-8 w-8 object-contain"
                            />
                            <span className="font-bold text-slate-900 text-lg">HugPDF</span>
                        </Link>
                        <p className="text-sm text-slate-500 leading-relaxed max-w-xs">
                            AI-powered document generation. Create beautiful PDFs from simple prompts in seconds.
                        </p>
                        {/* Open source badge */}
                        <a
                            href="https://github.com/sarathoff/hug-pdf"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-700 text-white text-xs font-medium rounded-full transition-colors"
                        >
                            <Github className="h-3.5 w-3.5" />
                            Open Source on GitHub
                        </a>
                    </div>

                    {/* Product Column */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-900">Product</h3>
                        <ul className="space-y-3">
                            {[
                                { label: 'Pricing', to: '/pricing' },
                                { label: 'Editor', to: '/editor' },
                                { label: 'API Docs', to: '/api-docs' },
                                { label: 'Developer Portal', to: '/developer' },
                            ].map((item) => (
                                <li key={item.label}>
                                    <Link
                                        to={item.to}
                                        className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                                    >
                                        {item.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Resources Column */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-900">Resources</h3>
                        <ul className="space-y-3">
                            {[
                                { label: 'About', to: '/about' },
                                { label: 'Contact', to: '/contact' },
                                { label: 'Blog', to: '/blog' },
                                { label: 'GitHub', href: 'https://github.com/sarathoff/hug-pdf' },
                            ].map((item) => (
                                <li key={item.label}>
                                    {item.href ? (
                                        <a
                                            href={item.href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                                        >
                                            {item.label}
                                        </a>
                                    ) : (
                                        <Link
                                            to={item.to}
                                            className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                                        >
                                            {item.label}
                                        </Link>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Legal Column */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-900">Legal</h3>
                        <ul className="space-y-3">
                            {[
                                { label: 'Terms of Service', to: '/terms' },
                                { label: 'Privacy Policy', to: '/privacy' },
                                {
                                    label: 'MIT License',
                                    href: 'https://github.com/sarathoff/hug-pdf/blob/main/LICENSE',
                                },
                            ].map((item) => (
                                <li key={item.label}>
                                    {item.href ? (
                                        <a
                                            href={item.href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                                        >
                                            {item.label}
                                        </a>
                                    ) : (
                                        <Link
                                            to={item.to}
                                            className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                                        >
                                            {item.label}
                                        </Link>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="py-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-sm text-slate-400 text-center sm:text-left">
                        &copy; {currentYear} HugPDF Contributors. Released under MIT License.
                    </p>

                    <div className="flex items-center gap-1">
                        <a
                            href="https://twitter.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="Twitter"
                            className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        >
                            <Twitter className="h-4 w-4" />
                        </a>
                        <a
                            href="https://github.com/sarathoff/hug-pdf"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="GitHub"
                            className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        >
                            <Github className="h-4 w-4" />
                        </a>
                        <a
                            href="https://linkedin.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="LinkedIn"
                            className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                        >
                            <Linkedin className="h-4 w-4" />
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
