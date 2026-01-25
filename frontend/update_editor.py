# Remove code editor tab and add auto-refresh to EditorPage

with open('src/pages/EditorPage.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove code tab from state initialization
content = content.replace(
    "const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'preview' | 'code'",
    "const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'preview'"
)

# 2. Remove Code tab button from desktop toolbar (lines 738-743)
old_code_button = '''                                <button
                                    onClick={() => setActiveTab('code')}
                                    className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'code' ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}
                                >
                                    <Code className="w-3 h-3 inline mr-1" /> Code
                                </button>'''

content = content.replace(old_code_button, '')

# 3. Remove mobile code button
old_mobile_code = '''                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="md:hidden text-xs"
                                        onClick={() => setActiveTab('code')}
                                    >
                                        <Code className="w-4 h-4 mr-1" /> Code
                                    </Button>'''

content = content.replace(old_mobile_code, '')

# 4. Add auto-refresh effect after htmlContent changes
auto_refresh_effect = '''
    // Auto-refresh preview when content changes
    useEffect(() => {
        if (htmlContent && activeTab === 'preview') {
            setPdfPreviewUrl(null);
            generatePreview(htmlContent);
        }
    }, [htmlContent, activeTab, generatePreview]);
'''

# Insert after the existing preview generation useEffect (around line 267)
content = content.replace(
    "    }, [activeTab, htmlContent, pdfPreviewUrl, generatePreview]);",
    "    }, [activeTab, htmlContent, pdfPreviewUrl, generatePreview]);" + auto_refresh_effect
)

with open('src/pages/EditorPage.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("EditorPage updated: Code tab removed and auto-refresh added!")
