import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { 
  Key, Copy, Trash2, Plus, Code, BarChart3, 
  CheckCircle2, AlertCircle, Loader2, Eye, EyeOff 
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DeveloperPage = () => {
  const { user, token, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newlyCreatedKey, setNewlyCreatedKey] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('keys');

  const fetchApiKeys = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/v1/keys`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys(response.data.keys || []);
    } catch (err) {
      console.error('Error fetching API keys:', err);
      setError(err.response?.data?.detail || 'Failed to load API keys');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth');
    }
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user && token) {
      fetchApiKeys();
    }
  }, [user, token, fetchApiKeys]);

  const createApiKey = async (e) => {
    e.preventDefault();
    if (!newKeyName.trim()) {
      setError('Please enter a name for your API key');
      return;
    }

    try {
      setCreating(true);
      setError('');
      const response = await axios.post(
        `${API}/v1/keys`,
        { name: newKeyName, tier: 'free' },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setNewlyCreatedKey(response.data);
        setSuccess('API key created successfully!');
        setNewKeyName('');
        await fetchApiKeys();
      }
    } catch (err) {
      console.error('Error creating API key:', err);
      setError(err.response?.data?.detail || 'Failed to create API key');
    } finally {
      setCreating(false);
    }
  };

  const revokeApiKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/v1/keys/${keyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('API key revoked successfully');
      await fetchApiKeys();
    } catch (err) {
      console.error('Error revoking API key:', err);
      setError(err.response?.data?.detail || 'Failed to revoke API key');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(''), 2000);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Developer Portal</h1>
          <p className="text-gray-600">
            Manage your API keys and integrate PDF generation into your applications
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {success && (
          <Alert className="mb-4 border-green-500 bg-green-50">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Newly Created Key Alert */}
        {newlyCreatedKey && (
          <Alert className="mb-4 border-blue-500 bg-blue-50">
            <Key className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-900">
              <div className="font-semibold mb-2">Your API Key (save this now - it won't be shown again!):</div>
              <div className="flex items-center gap-2 bg-white p-3 rounded border border-blue-200 font-mono text-sm">
                <code className="flex-1 break-all">{newlyCreatedKey.api_key}</code>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyToClipboard(newlyCreatedKey.api_key)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <Button
                size="sm"
                variant="ghost"
                className="mt-2"
                onClick={() => setNewlyCreatedKey(null)}
              >
                I've saved it
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="keys" className="flex items-center gap-2">
              <Key className="h-4 w-4" />
              API Keys
            </TabsTrigger>
            <TabsTrigger value="docs" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Documentation
            </TabsTrigger>
            <TabsTrigger value="usage" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Usage
            </TabsTrigger>
          </TabsList>

          {/* API Keys Tab */}
          <TabsContent value="keys" className="space-y-6">
            {/* Create New Key */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Create New API Key
                </CardTitle>
                <CardDescription>
                  Generate a new API key to access the PDF generation API
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={createApiKey} className="flex gap-4">
                  <div className="flex-1">
                    <Label htmlFor="keyName">Key Name</Label>
                    <Input
                      id="keyName"
                      placeholder="My Application"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button type="submit" disabled={creating}>
                      {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Create Key
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* API Keys List */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Your API Keys</h3>
              {apiKeys.length === 0 ? (
                <Card>
                  <CardContent className="py-12 text-center text-gray-500">
                    <Key className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p>No API keys yet. Create one to get started!</p>
                  </CardContent>
                </Card>
              ) : (
                apiKeys.map((key) => (
                  <Card key={key.id}>
                    <CardContent className="py-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-semibold">{key.name}</h4>
                            <Badge variant={key.tier === 'pro' ? 'default' : 'secondary'}>
                              {key.tier}
                            </Badge>
                            {!key.is_active && (
                              <Badge variant="destructive">Revoked</Badge>
                            )}
                          </div>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div className="flex items-center gap-2 font-mono">
                              <span className="text-gray-400">Key:</span>
                              <code className="bg-gray-100 px-2 py-1 rounded">
                                {key.key_prefix}
                              </code>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 w-6 p-0"
                                onClick={() => copyToClipboard(key.key_prefix)}
                              >
                                <Copy className="h-3 w-3" />
                              </Button>
                            </div>
                            <div>
                              <span className="text-gray-400">Created:</span>{' '}
                              {new Date(key.created_at).toLocaleDateString()}
                            </div>
                            {key.last_used_at && (
                              <div>
                                <span className="text-gray-400">Last used:</span>{' '}
                                {new Date(key.last_used_at).toLocaleDateString()}
                              </div>
                            )}
                            <div>
                              <span className="text-gray-400">Usage:</span>{' '}
                              {key.requests_count} / {key.requests_limit} requests
                            </div>
                          </div>
                        </div>
                        {key.is_active && (
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => revokeApiKey(key.id)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Revoke
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Documentation Tab */}
          <TabsContent value="docs">
            <DocumentationTab />
          </TabsContent>

          {/* Usage Tab */}
          <TabsContent value="usage">
            <UsageTab apiKeys={apiKeys} token={token} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Documentation Component
const DocumentationTab = () => {
  const [copiedExample, setCopiedExample] = useState('');

  const copyExample = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedExample(id);
    setTimeout(() => setCopiedExample(''), 2000);
  };

  const curlExample = `curl -X POST ${BACKEND_URL}/api/v1/generate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Create a professional resume for John Doe"}' \\
  --output document.pdf`;

  const pythonExample = `import requests

response = requests.post(
    "${BACKEND_URL}/api/v1/generate",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"prompt": "Create a professional resume for John Doe"}
)

with open("document.pdf", "wb") as f:
    f.write(response.content)`;

  const javascriptExample = `const axios = require('axios');
const fs = require('fs');

axios.post('${BACKEND_URL}/api/v1/generate', {
  prompt: 'Create a professional resume for John Doe'
}, {
  headers: { 'Authorization': 'Bearer YOUR_API_KEY' },
  responseType: 'arraybuffer'
}).then(response => {
  fs.writeFileSync('document.pdf', response.data);
  console.log('PDF generated!');
});`;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Reference</CardTitle>
          <CardDescription>Complete guide to using the PDF Generation API</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Endpoint */}
          <div>
            <h3 className="font-semibold mb-2">Endpoint</h3>
            <code className="bg-gray-100 px-3 py-2 rounded block">
              POST {BACKEND_URL}/api/v1/generate
            </code>
          </div>

          {/* Authentication */}
          <div>
            <h3 className="font-semibold mb-2">Authentication</h3>
            <p className="text-sm text-gray-600 mb-2">
              Include your API key in the Authorization header:
            </p>
            <code className="bg-gray-100 px-3 py-2 rounded block text-sm">
              Authorization: Bearer YOUR_API_KEY
            </code>
          </div>

          {/* Request Body */}
          <div>
            <h3 className="font-semibold mb-2">Request Body</h3>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
{`{
  "prompt": "Create a professional resume for John Doe",
  "mode": "normal"  // optional: "normal", "research", "ebook"
}`}
            </pre>
          </div>

          {/* Response */}
          <div>
            <h3 className="font-semibold mb-2">Response</h3>
            <p className="text-sm text-gray-600">
              Returns a PDF file (binary) with the following headers:
            </p>
            <ul className="text-sm text-gray-600 mt-2 space-y-1 list-disc list-inside">
              <li>Content-Type: application/pdf</li>
              <li>X-RateLimit-Limit: 10</li>
              <li>X-RateLimit-Remaining: 9</li>
              <li>X-RateLimit-Reset: timestamp</li>
            </ul>
          </div>

          {/* Rate Limits */}
          <div>
            <h3 className="font-semibold mb-2">Rate Limits</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-blue-50 p-3 rounded">
                <div className="font-medium">Free Tier</div>
                <div className="text-gray-600">10 req/min, 1000 req/month</div>
              </div>
              <div className="bg-purple-50 p-3 rounded">
                <div className="font-medium">Pro Tier</div>
                <div className="text-gray-600">100 req/min, 10000 req/month</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Code Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Code Examples</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* cURL */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">cURL</h4>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => copyExample('curl', curlExample)}
              >
                {copiedExample === 'curl' ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
              {curlExample}
            </pre>
          </div>

          {/* Python */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">Python</h4>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => copyExample('python', pythonExample)}
              >
                {copiedExample === 'python' ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
              {pythonExample}
            </pre>
          </div>

          {/* JavaScript */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">JavaScript (Node.js)</h4>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => copyExample('js', javascriptExample)}
              >
                {copiedExample === 'js' ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
              {javascriptExample}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Usage Component
const UsageTab = ({ apiKeys, token }) => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Usage Statistics</CardTitle>
          <CardDescription>Monitor your API usage and rate limits</CardDescription>
        </CardHeader>
        <CardContent>
          {apiKeys.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>No API keys yet. Create one to start tracking usage!</p>
            </div>
          ) : (
            <div className="space-y-6">
              {apiKeys.map((key) => (
                <div key={key.id} className="border-b pb-6 last:border-0">
                  <h4 className="font-semibold mb-4">{key.name}</h4>
                  <div className="space-y-4">
                    {/* Usage Progress */}
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600">Monthly Usage</span>
                        <span className="font-medium">
                          {key.requests_count} / {key.requests_limit}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${Math.min(
                              (key.requests_count / key.requests_limit) * 100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-sm text-gray-600">Total Requests</div>
                        <div className="text-2xl font-bold">{key.requests_count}</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-sm text-gray-600">Remaining</div>
                        <div className="text-2xl font-bold">
                          {key.requests_limit - key.requests_count}
                        </div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-sm text-gray-600">Tier</div>
                        <div className="text-2xl font-bold capitalize">{key.tier}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DeveloperPage;
