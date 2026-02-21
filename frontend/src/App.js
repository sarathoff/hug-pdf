// Copyright (c) 2026 HugPDF Contributors
// SPDX-License-Identifier: MIT
// https://github.com/sarathoff/hug-pdf

import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { AuthProvider } from "./context/AuthContext";
import HomePage from "./pages/HomePage";
import EditorPage from "./pages/EditorPage";
import AuthPage from "./pages/AuthPage";
import PricingPage from "./pages/PricingPage";
import PaymentSuccessPage from "./pages/PaymentSuccessPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import TermsPage from "./pages/TermsPage";
import PrivacyPage from "./pages/PrivacyPage";
import SuccessPage from "./pages/SuccessPage";
import DeveloperPage from "./pages/DeveloperPage";
import ApiDocsPage from "./pages/ApiDocsPage";
import BlogPage from "./pages/BlogPage";
import BlogPostPage from "./pages/BlogPostPage";
import Layout from "./components/Layout";
import CookieConsent from "./components/CookieConsent";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log(response.data.message);
      } catch (e) {
        console.error(e, `errored out requesting / api`);
      }
    };
    testConnection();
  }, []);

  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            {/* Pages with Standard Layout (Header + Footer) */}
            <Route path="/" element={<Layout><HomePage /></Layout>} />
            <Route path="/pricing" element={<Layout><PricingPage /></Layout>} />
            <Route path="/about" element={<Layout><AboutPage /></Layout>} />
            <Route path="/contact" element={<Layout><ContactPage /></Layout>} />
            <Route path="/terms" element={<Layout><TermsPage /></Layout>} />
            <Route path="/privacy" element={<Layout><PrivacyPage /></Layout>} />
            <Route path="/payment/success" element={<Layout><PaymentSuccessPage /></Layout>} />
            <Route path="/success" element={<Layout><SuccessPage /></Layout>} />
            <Route path="/developer" element={<Layout><DeveloperPage /></Layout>} />
            <Route path="/api-docs" element={<Layout><ApiDocsPage /></Layout>} />
            <Route path="/blog" element={<Layout><BlogPage /></Layout>} />
            <Route path="/blog/:slug" element={<Layout><BlogPostPage /></Layout>} />

            {/* Pages with Custom/Standalone Layout */}
            <Route path="/editor" element={<EditorPage />} />
            <Route path="/auth" element={<AuthPage />} />
          </Routes>
        </BrowserRouter>
        <CookieConsent />
      </div>
    </AuthProvider>
  );
}

export default App;
