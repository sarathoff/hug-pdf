import React from 'react';
import Header from './Header';
import Footer from './Footer';

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-gray-50/30 flex flex-col relative">
            {/* Unified Background Gradients for all pages using Layout */}
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none -z-10"></div>
            <div className="fixed top-0 left-0 w-full h-[500px] bg-gradient-to-b from-blue-50/40 via-purple-50/20 to-transparent pointer-events-none -z-10"></div>

            <Header />
            <main className="flex-grow relative z-0">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;
