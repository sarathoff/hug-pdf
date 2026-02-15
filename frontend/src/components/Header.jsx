import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    FileText,
    Menu,
    X,
    User as UserIcon,
    Compass,
    Zap,
    Info,
    CreditCard,
    LogOut,
    ChevronRight,
    LayoutDashboard,
    Code
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
        { name: 'Pricing', href: '/pricing', icon: CreditCard },
        { name: 'About', href: '/about', icon: Info },
        { name: 'Contact', href: '/contact', icon: Compass },
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b border-gray-200/50 bg-white/80 backdrop-blur-xl supports-[backdrop-filter]:bg-white/60">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 transition-opacity hover:opacity-90">
                        <img
                            src="/logo.png"
                            alt="HugPDF Logo"
                            className="h-8 w-8 object-contain"
                        />
                        <span className="hidden font-bold sm:inline-block bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                            HugPDF
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-6">
                        {navigation.map((item) => (
                            <Link
                                key={item.name}
                                to={item.href}
                                className="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors"
                            >
                                {item.name}
                            </Link>
                        ))}
                    </nav>

                    {/* Desktop Actions */}
                    <div className="hidden md:flex items-center gap-4">
                        {user ? (
                            <div className="flex items-center gap-4">
                                <div className="hidden lg:flex flex-col items-end mr-2">
                                    <span className="text-sm font-medium text-gray-900">{user.email?.split('@')[0]}</span>
                                    <span className="text-xs text-blue-600 font-medium bg-blue-50 px-2 py-0.5 rounded-full">
                                        {user.credits} Credits
                                    </span>
                                </div>
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" className="relative h-10 w-10 rounded-full ring-2 ring-gray-100 hover:ring-blue-100 p-0">
                                            <Avatar className="h-9 w-9">
                                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`} alt={user.email} />
                                                <AvatarFallback>
                                                    {user.email?.substring(0, 2).toUpperCase()}
                                                </AvatarFallback>
                                            </Avatar>
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent className="w-56" align="end" forceMount>
                                        <DropdownMenuLabel className="font-normal">
                                            <div className="flex flex-col space-y-1">
                                                <p className="text-sm font-medium leading-none">{user.email}</p>
                                                <p className="text-xs leading-none text-muted-foreground">
                                                    {user.credits <= 5 ? 'Free Plan' : 'Pro Plan'}
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
                            <div className="flex items-center gap-3">
                                <Link to="/auth">
                                    <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                                        Log in
                                    </Button>
                                </Link>
                                <Link to="/auth">
                                    <Button className="bg-gray-900 hover:bg-gray-800 text-white shadow-lg shadow-gray-200">
                                        Sign up
                                        <ChevronRight className="ml-1.5 h-4 w-4" />
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
                            className="text-gray-600"
                        >
                            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden border-t border-gray-100 bg-white">
                    <div className="space-y-1 p-4">
                        {navigation.map((item) => (
                            <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="flex items-center gap-3 px-4 py-3 text-base font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-xl transition-colors"
                            >
                                <item.icon className="h-5 w-5 text-gray-400" />
                                {item.name}
                            </Link>
                        ))}

                        <div className="border-t border-gray-100 my-4 pt-4">
                            {user ? (
                                <div className="space-y-3">
                                    <div className="px-4 py-2 flex items-center gap-3 bg-blue-50 rounded-xl">
                                        <Avatar className="h-10 w-10 border-2 border-white">
                                            <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`} />
                                            <AvatarFallback>{user.email?.substring(0, 2).toUpperCase()}</AvatarFallback>
                                        </Avatar>
                                        <div className="flex flex-col">
                                            <span className="font-medium text-gray-900">{user.email}</span>
                                            <span className="text-xs text-blue-600 font-bold">{user.credits} Credits Available</span>
                                        </div>
                                    </div>
                                    <Button
                                        variant="outline"
                                        className="w-full justify-start"
                                        onClick={handleLogout}
                                    >
                                        <LogOut className="mr-2 h-4 w-4" />
                                        Log out
                                    </Button>
                                </div>
                            ) : (
                                <div className="grid grid-cols-2 gap-3">
                                    <Link to="/auth">
                                        <Button variant="outline" className="w-full">
                                            Log in
                                        </Button>
                                    </Link>
                                    <Link to="/auth">
                                        <Button className="w-full bg-gray-900 text-white">
                                            Sign up
                                        </Button>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
};

export default Header;
