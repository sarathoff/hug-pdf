import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Menu,
    X,
    Zap,
    Info,
    CreditCard,
    LogOut,
    ChevronRight,
    LayoutDashboard,
    Code,
    BookOpen,
    Github,
} from 'lucide-react';
import { Button } from './ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "./ui/dropdown-menu"
import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "./ui/avatar"
import { useAuth } from '../context/AuthContext';


const Header = () => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const navigation = [
        { name: 'API Docs', href: '/api-docs', icon: Code },
        { name: 'Blog', href: '/blog', icon: BookOpen },
        { name: 'Pricing', href: '/pricing', icon: CreditCard },
        { name: 'About', href: '/about', icon: Info },
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b border-slate-200/60 bg-white/90 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="h-16 flex items-center justify-between">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-90 shrink-0">
                        <img
                            src="/logo.png"
                            alt="HugPDF Logo"
                            className="h-8 w-8 object-contain"
                        />
                        <span className="font-bold text-slate-900 text-lg hidden sm:inline-block">
                            HugPDF
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-1">
                        {navigation.map((item) => (
                            <Link
                                key={item.name}
                                to={item.href}
                                className="text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 px-3 py-2 rounded-lg transition-colors"
                            >
                                {item.name}
                            </Link>
                        ))}
                    </nav>

                    {/* Desktop Actions */}
                    <div className="hidden md:flex items-center gap-3">
                        {/* GitHub Link */}
                        <a
                            href="https://github.com/sarathoff/hug-pdf"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hidden lg:flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                            <Github className="h-4 w-4" />
                            GitHub
                        </a>

                        {user ? (
                            <div className="flex items-center gap-3">
                                {/* Credits badge */}
                                <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 border border-violet-200 rounded-full">
                                    <Zap className="h-3.5 w-3.5 text-violet-600" />
                                    <span className="text-xs font-semibold text-violet-700">
                                        {user.credits} credits
                                    </span>
                                </div>

                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" className="relative h-9 w-9 rounded-full ring-2 ring-slate-100 hover:ring-violet-200 p-0 transition-all">
                                            <Avatar className="h-8 w-8">
                                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`} alt={user.email} />
                                                <AvatarFallback className="bg-violet-100 text-violet-700 text-xs font-semibold">
                                                    {user.email?.substring(0, 2).toUpperCase()}
                                                </AvatarFallback>
                                            </Avatar>
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent className="w-56" align="end" forceMount>
                                        <DropdownMenuLabel className="font-normal">
                                            <div className="flex flex-col space-y-1">
                                                <p className="text-sm font-medium leading-none text-slate-900">{user.email?.split('@')[0]}</p>
                                                <p className="text-xs leading-none text-slate-500 truncate">
                                                    {user.email}
                                                </p>
                                            </div>
                                        </DropdownMenuLabel>
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem onClick={() => navigate('/editor')}>
                                            <LayoutDashboard className="mr-2 h-4 w-4" />
                                            <span>Dashboard</span>
                                        </DropdownMenuItem>
                                        <DropdownMenuItem onClick={() => navigate('/developer')}>
                                            <Code className="mr-2 h-4 w-4" />
                                            <span>Developer</span>
                                        </DropdownMenuItem>
                                        <DropdownMenuItem onClick={() => navigate('/pricing')}>
                                            <CreditCard className="mr-2 h-4 w-4" />
                                            <span>Subscription</span>
                                        </DropdownMenuItem>
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
                                            <LogOut className="mr-2 h-4 w-4" />
                                            <span>Log out</span>
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <Link to="/auth">
                                    <Button
                                        variant="ghost"
                                        className="text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 h-9 px-4"
                                    >
                                        Log in
                                    </Button>
                                </Link>
                                <Link to="/auth">
                                    <Button className="h-9 px-4 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-lg shadow-sm shadow-violet-500/20 transition-all">
                                        Get Started
                                        <ChevronRight className="ml-1 h-4 w-4" />
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="flex md:hidden">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="text-slate-600 hover:text-slate-900 h-9 w-9"
                        >
                            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden border-t border-slate-100 bg-white/95 backdrop-blur-xl">
                    <div className="px-4 py-3 space-y-1">
                        {navigation.map((item) => (
                            <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-lg transition-colors"
                            >
                                <item.icon className="h-4 w-4 text-slate-400" />
                                {item.name}
                            </Link>
                        ))}

                        {/* GitHub in mobile menu */}
                        <a
                            href="https://github.com/sarathoff/hug-pdf"
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={() => setIsMobileMenuOpen(false)}
                            className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-lg transition-colors"
                        >
                            <Github className="h-4 w-4 text-slate-400" />
                            GitHub
                        </a>
                    </div>

                    <div className="px-4 pb-4 border-t border-slate-100 mt-1 pt-3">
                        {user ? (
                            <div className="space-y-2">
                                <div className="flex items-center gap-3 px-3 py-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                    <Avatar className="h-8 w-8 shrink-0">
                                        <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`} />
                                        <AvatarFallback className="bg-violet-100 text-violet-700 text-xs font-semibold">
                                            {user.email?.substring(0, 2).toUpperCase()}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="flex flex-col min-w-0">
                                        <span className="text-sm font-medium text-slate-900 truncate">{user.email}</span>
                                        <span className="text-xs text-violet-600 font-semibold">{user.credits} Credits Available</span>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <Button
                                        variant="outline"
                                        className="text-sm h-9 border-slate-200"
                                        onClick={() => { navigate('/editor'); setIsMobileMenuOpen(false); }}
                                    >
                                        <LayoutDashboard className="mr-2 h-4 w-4" />
                                        Dashboard
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="text-sm h-9 border-slate-200 text-red-600 hover:text-red-700 hover:border-red-200"
                                        onClick={handleLogout}
                                    >
                                        <LogOut className="mr-2 h-4 w-4" />
                                        Log out
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 gap-2">
                                <Link to="/auth" onClick={() => setIsMobileMenuOpen(false)}>
                                    <Button variant="outline" className="w-full h-9 text-sm border-slate-200 text-slate-700">
                                        Log in
                                    </Button>
                                </Link>
                                <Link to="/auth" onClick={() => setIsMobileMenuOpen(false)}>
                                    <Button className="w-full h-9 text-sm bg-violet-600 hover:bg-violet-700 text-white font-semibold">
                                        Get Started
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </header>
    );
};

export default Header;
