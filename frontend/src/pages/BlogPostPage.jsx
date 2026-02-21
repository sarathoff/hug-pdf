// Copyright (c) 2026 HugPDF Contributors
// SPDX-License-Identifier: MIT
import React, { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Clock, Tag, Github, ArrowRight, BookOpen } from 'lucide-react';
import { BLOG_POSTS } from './BlogPage';
import { Button } from '../components/ui/button';

// ─── Blog Content ─────────────────────────────────────────────────────────────

const CodeBlock = ({ code, language = 'bash' }) => (
  <pre className="bg-slate-900 text-slate-100 rounded-xl p-4 overflow-x-auto text-sm leading-relaxed my-4">
    <code>{code}</code>
  </pre>
);

const Section = ({ title, children }) => (
  <div className="mb-8">
    <h2 className="text-2xl font-bold text-slate-900 mb-4 mt-10 pb-2 border-b border-slate-200">{title}</h2>
    {children}
  </div>
);

const Note = ({ type = 'info', children }) => {
  const styles = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  };
  return (
    <div className={`border rounded-xl p-4 my-4 text-sm leading-relaxed ${styles[type]}`}>
      {children}
    </div>
  );
};

// ─── Individual Post Content ──────────────────────────────────────────────────

const PostContent = ({ slug }) => {
  switch (slug) {

    case 'hugpdf-api-windows':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            This guide walks you through integrating the HugPDF API on Windows — from installation to building
            your first automated PDF pipeline using Python, PowerShell, and Node.js.
          </p>

          <Section title="Prerequisites">
            <ul className="list-disc list-inside space-y-2 text-slate-600">
              <li>Windows 10 or Windows 11</li>
              <li>Python 3.10+ (from <a href="https://python.org" className="text-violet-600 hover:underline">python.org</a>) or <code className="bg-slate-100 px-1 rounded">winget install Python.Python.3</code></li>
              <li>A HugPDF API key — get one free at <Link to="/developer" className="text-violet-600 hover:underline">hugpdf.app/developer</Link></li>
            </ul>
          </Section>

          <Section title="Step 1: Set Your API Key">
            <p className="text-slate-600 mb-3">Store your API key as an environment variable so it's never hardcoded:</p>
            <CodeBlock language="powershell" code={`# PowerShell — set for current session
$env:HUGPDF_API_KEY = "pdf_live_YOUR_API_KEY"

# Set permanently (user-level)
[System.Environment]::SetEnvironmentVariable("HUGPDF_API_KEY", "pdf_live_YOUR_API_KEY", "User")

# Verify
echo $env:HUGPDF_API_KEY`} />
          </Section>

          <Section title="Step 2: Install the requests Library">
            <CodeBlock language="powershell" code={`# Open PowerShell and run:
pip install requests

# Or in a virtual environment (recommended):
python -m venv hugpdf-env
hugpdf-env\\Scripts\\activate
pip install requests`} />
          </Section>

          <Section title="Step 3: Generate Your First PDF">
            <p className="text-slate-600 mb-3">Create a file called <code className="bg-slate-100 px-1 rounded">generate_pdf.py</code>:</p>
            <CodeBlock language="python" code={`import os
import requests

API_KEY = os.environ.get("HUGPDF_API_KEY")
API_URL = "https://api.hugpdf.app/api/v1/generate"

def generate_pdf(prompt: str, mode: str = "normal", filename: str = "output.pdf") -> None:
    print(f"Generating PDF: {prompt[:60]}...")

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={"prompt": prompt, "mode": mode},
        timeout=60
    )

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        credits = response.headers.get("X-Credits-Remaining", "unknown")
        print(f"✓ Saved to {filename} | Credits remaining: {credits}")
    else:
        error = response.json()
        print(f"✗ Error {response.status_code}: {error.get('detail')}")

if __name__ == "__main__":
    generate_pdf(
        "Create a professional invoice for web development services, client: Acme Corp, amount: $3,500",
        filename="invoice.pdf"
    )`} />
            <CodeBlock language="powershell" code={`python generate_pdf.py`} />
          </Section>

          <Section title="Step 4: PowerShell Script">
            <p className="text-slate-600 mb-3">For simpler use cases, call the API directly from PowerShell:</p>
            <CodeBlock language="powershell" code={`$headers = @{
    "Authorization" = "Bearer $env:HUGPDF_API_KEY"
    "Content-Type"  = "application/json"
}
$body = @{
    prompt = "Create a certificate of completion for John Doe - Advanced Python Course 2026"
    mode   = "normal"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://api.hugpdf.app/api/v1/generate" \`
    -Method POST -Headers $headers -Body $body \`
    -OutFile "certificate.pdf"

Write-Host "PDF saved to certificate.pdf"`} />
          </Section>

          <Section title="Step 5: Scheduled Automation with Task Scheduler">
            <p className="text-slate-600 mb-3">Generate PDFs on a schedule using Windows Task Scheduler:</p>
            <CodeBlock language="powershell" code={`# Create a scheduled task to run every Monday at 8 AM
$action = New-ScheduledTaskAction -Execute "python" \`
    -Argument "C:\\PDFBot\\generate_pdf.py" \`
    -WorkingDirectory "C:\\PDFBot"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "08:00AM"

Register-ScheduledTask -TaskName "WeeklyPDFReport" \`
    -Action $action -Trigger $trigger -RunLevel Highest`} />
          </Section>

          <Note type="success">
            <strong>Pro tip:</strong> On Windows, store your API key in Windows Credential Manager for extra security:
            <CodeBlock language="powershell" code={`cmdkey /generic:hugpdf /user:apikey /pass:pdf_live_YOUR_KEY`} />
          </Note>

          <Section title="Next Steps">
            <p className="text-slate-600 mb-3">Now that you have the basics working:</p>
            <ul className="list-disc list-inside space-y-2 text-slate-600">
              <li>Explore the <Link to="/api-docs" className="text-violet-600 hover:underline">full API documentation</Link></li>
              <li>Try <Link to="/blog/hugpdf-make-automation" className="text-violet-600 hover:underline">Make.com automation</Link> for no-code workflows</li>
              <li>Build a <Link to="/blog/hugpdf-n8n-workflow" className="text-violet-600 hover:underline">self-hosted n8n pipeline</Link></li>
            </ul>
          </Section>
        </>
      );

    case 'hugpdf-api-macos':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            Set up the HugPDF API on macOS using Homebrew, Python virtual environments, and shell scripts.
            This guide covers everything from installation to running automated PDF workflows.
          </p>

          <Section title="Prerequisites">
            <ul className="list-disc list-inside space-y-2 text-slate-600">
              <li>macOS 12 Monterey or later</li>
              <li>Homebrew: <code className="bg-slate-100 px-1 rounded text-sm">/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"</code></li>
              <li>A HugPDF API key from <Link to="/developer" className="text-violet-600 hover:underline">hugpdf.app/developer</Link></li>
            </ul>
          </Section>

          <Section title="Step 1: Install Python & Set Up Environment">
            <CodeBlock code={`# Install Python via Homebrew
brew install python@3.11

# Verify installation
python3 --version

# Create project directory and virtual environment
mkdir ~/hugpdf-automation && cd ~/hugpdf-automation
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests`} />
          </Section>

          <Section title="Step 2: Configure API Key via .zshrc">
            <CodeBlock code={`# Add to ~/.zshrc (or ~/.bash_profile for bash)
echo 'export HUGPDF_API_KEY="pdf_live_YOUR_API_KEY"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $HUGPDF_API_KEY`} />
            <Note type="warning">
              Never commit your API key to Git. Add <code>.env</code> to your <code>.gitignore</code>.
            </Note>
          </Section>

          <Section title="Step 3: Python Script">
            <CodeBlock language="python" code={`#!/usr/bin/env python3
"""HugPDF automation script for macOS."""
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("HUGPDF_API_KEY")
if not API_KEY:
    print("Error: HUGPDF_API_KEY not set. Run: export HUGPDF_API_KEY=your_key")
    sys.exit(1)

def generate_pdf(prompt: str, mode: str = "normal") -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = Path(f"~/Desktop/hugpdf_{ts}.pdf").expanduser()

    r = requests.post(
        "https://api.hugpdf.app/api/v1/generate",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt, "mode": mode},
        timeout=60
    )
    r.raise_for_status()

    output.write_bytes(r.content)
    print(f"✓ PDF saved to Desktop: {output.name}")
    # Open in Preview automatically
    os.system(f"open {output}")
    return output

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Create a professional resume for a senior iOS developer at Apple"
    generate_pdf(prompt)`} />
          </Section>

          <Section title="Step 4: Shell Script + Alias">
            <p className="text-slate-600 mb-3">Create a handy <code className="bg-slate-100 px-1 rounded text-sm">hugpdf</code> command:</p>
            <CodeBlock code={`# Create the script
cat > /usr/local/bin/hugpdf << 'EOF'
#!/bin/bash
source ~/hugpdf-automation/venv/bin/activate
python3 ~/hugpdf-automation/generate.py "$@"
EOF
chmod +x /usr/local/bin/hugpdf

# Now use it from anywhere
hugpdf "Create a business report for Q1 2026 with key metrics and analysis"`} />
          </Section>

          <Section title="Step 5: Automate with launchd (macOS Cron)">
            <CodeBlock language="xml" code={`<!-- ~/Library/LaunchAgents/com.hugpdf.weekly.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.hugpdf.weekly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/Users/you/hugpdf-automation/generate.py</string>
    <string>Weekly team status report for engineering department</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>1</integer>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HUGPDF_API_KEY</key>
    <string>pdf_live_YOUR_API_KEY</string>
  </dict>
</dict>
</plist>`} />
            <CodeBlock code={`# Load the agent
launchctl load ~/Library/LaunchAgents/com.hugpdf.weekly.plist`} />
          </Section>
        </>
      );

    case 'hugpdf-api-linux':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            This guide covers production-ready PDF automation on Linux — including Debian/Ubuntu setup, systemd services,
            cron jobs, Docker containers, and CI/CD integration.
          </p>

          <Section title="Prerequisites">
            <CodeBlock code={`# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv curl

# CentOS/RHEL/Fedora
sudo dnf install -y python3 python3-pip curl

# Arch Linux
sudo pacman -S python python-pip curl`} />
          </Section>

          <Section title="Step 1: Virtual Environment Setup">
            <CodeBlock code={`mkdir -p /opt/hugpdf && cd /opt/hugpdf
python3 -m venv venv
source venv/bin/activate
pip install requests

# Store API key securely
echo "HUGPDF_API_KEY=pdf_live_YOUR_KEY" > /opt/hugpdf/.env
chmod 600 /opt/hugpdf/.env`} />
          </Section>

          <Section title="Step 2: Python Script">
            <CodeBlock language="python" code={`#!/opt/hugpdf/venv/bin/python3
"""HugPDF CLI for Linux."""
import os, sys, requests, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# Load .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("HUGPDF_API_KEY")
OUTPUT_DIR = Path("/var/hugpdf/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate(prompt: str, mode: str = "normal") -> int:
    r = requests.post(
        "https://api.hugpdf.app/api/v1/generate",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt, "mode": mode},
        timeout=90
    )
    if r.status_code != 200:
        logger.error(f"API error {r.status_code}: {r.json().get('detail')}")
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR / f"doc_{ts}.pdf"
    out.write_bytes(r.content)
    logger.info(f"Saved: {out} | Credits: {r.headers.get('X-Credits-Remaining')}")
    return 0

if __name__ == "__main__":
    sys.exit(generate(" ".join(sys.argv[1:]) or "Test document"))`} />
          </Section>

          <Section title="Step 3: systemd Service">
            <CodeBlock code={`# /etc/systemd/system/hugpdf-generator.service
[Unit]
Description=HugPDF Document Generator
After=network.target

[Service]
Type=oneshot
User=hugpdf
WorkingDirectory=/opt/hugpdf
EnvironmentFile=/opt/hugpdf/.env
ExecStart=/opt/hugpdf/venv/bin/python3 /opt/hugpdf/generate.py "Weekly analytics report"

[Install]
WantedBy=multi-user.target`} />
            <CodeBlock code={`# Create service user
sudo useradd -r -s /bin/false hugpdf
sudo chown -R hugpdf:hugpdf /opt/hugpdf /var/hugpdf

sudo systemctl daemon-reload
sudo systemctl enable hugpdf-generator
sudo systemctl start hugpdf-generator
sudo journalctl -u hugpdf-generator -f`} />
          </Section>

          <Section title="Step 4: Cron Job">
            <CodeBlock code={`# Edit crontab
sudo crontab -e -u hugpdf

# Add (runs every Monday at 9 AM):
0 9 * * 1 /opt/hugpdf/venv/bin/python3 /opt/hugpdf/generate.py "Weekly report" >> /var/log/hugpdf.log 2>&1`} />
          </Section>

          <Section title="Step 5: Docker Container">
            <CodeBlock code={`# Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install requests
COPY generate.py .
ENV HUGPDF_API_KEY=""
CMD ["python3", "generate.py", "Docker test document"]`} />
            <CodeBlock code={`# Build and run
docker build -t hugpdf-bot .
docker run -e HUGPDF_API_KEY=pdf_live_YOUR_KEY hugpdf-bot

# With custom prompt
docker run -e HUGPDF_API_KEY=pdf_live_YOUR_KEY hugpdf-bot \
  python3 generate.py "Q2 2026 Financial Summary Report"

# Docker Compose
cat > docker-compose.yml << 'EOF'
version: "3.8"
services:
  hugpdf:
    build: .
    environment:
      HUGPDF_API_KEY: \${HUGPDF_API_KEY}
    volumes:
      - ./output:/var/hugpdf/output
EOF

docker compose up`} />
          </Section>

          <Note type="info">
            <strong>CI/CD Integration:</strong> Set <code>HUGPDF_API_KEY</code> as a GitHub Actions secret,
            then call the API in your pipeline to auto-generate release notes, documentation, or reports.
          </Note>
        </>
      );

    case 'hugpdf-make-automation':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            Make.com (formerly Integromat) is one of the most powerful no-code automation platforms.
            In this guide, you'll build a workflow that automatically generates PDFs whenever a trigger fires —
            like a new form submission, CRM entry, or spreadsheet row.
          </p>

          <Note type="info">
            You'll need a Make.com account (free tier works) and a HugPDF API key from{' '}
            <Link to="/developer" className="text-violet-600 hover:underline">hugpdf.app/developer</Link>.
          </Note>

          <Section title="How It Works">
            <p className="text-slate-600 mb-4">Make.com uses HTTP modules to call external APIs. The pattern is:</p>
            <div className="bg-slate-50 rounded-xl p-4 font-mono text-sm text-slate-700 border border-slate-200">
              Trigger (Google Forms / Typeform / Airtable) → HTTP Module (HugPDF API) → Store PDF (Google Drive / Email / Slack)
            </div>
          </Section>

          <Section title="Step 1: Create a New Scenario">
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Go to <strong>make.com</strong> → <strong>Create a new Scenario</strong></li>
              <li>Choose your trigger (e.g., <strong>Google Forms</strong> → <em>Watch Responses</em>)</li>
              <li>Connect your Google account and select your form</li>
            </ol>
          </Section>

          <Section title="Step 2: Add the HTTP Module">
            <ol className="list-decimal list-inside space-y-3 text-slate-600 mb-4">
              <li>Click the <strong>+</strong> to add a new module</li>
              <li>Search for <strong>HTTP</strong> → select <strong>Make a request</strong></li>
              <li>Configure the module:</li>
            </ol>
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden mb-4">
              <table className="w-full text-sm">
                <tbody className="divide-y divide-slate-100">
                  {[
                    { field: 'URL', value: 'https://api.hugpdf.app/api/v1/generate' },
                    { field: 'Method', value: 'POST' },
                    { field: 'Headers', value: 'Authorization: Bearer pdf_live_YOUR_KEY' },
                    { field: 'Body type', value: 'Raw' },
                    { field: 'Content type', value: 'JSON (application/json)' },
                  ].map(row => (
                    <tr key={row.field}>
                      <td className="px-4 py-2 font-medium text-slate-700 w-36 bg-slate-50">{row.field}</td>
                      <td className="px-4 py-2 font-mono text-slate-600 text-xs">{row.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-slate-600 mb-3">In the Request body, map your form data to the prompt:</p>
            <CodeBlock language="json" code={`{
  "prompt": "Create a professional proposal for {{1.company_name}} - Project: {{1.project_description}} - Budget: {{1.budget}}",
  "mode": "normal"
}`} />
          </Section>

          <Section title="Step 3: Configure Binary Response">
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>In the HTTP module settings, enable <strong>"Parse response"</strong></li>
              <li>Set <strong>Response type</strong> to <strong>Binary</strong> (since we receive a PDF file)</li>
              <li>This stores the PDF as a binary data bundle for the next module</li>
            </ol>
          </Section>

          <Section title="Step 4: Save PDF to Google Drive">
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Add a <strong>Google Drive</strong> module → <strong>Upload a File</strong></li>
              <li>Set <strong>File name</strong> to: <code className="bg-slate-100 px-1 rounded">proposal_{"{{"}1.company_name{"}}"}.pdf</code></li>
              <li>Set <strong>Data</strong> to the binary output from the HTTP module: <code className="bg-slate-100 px-1 rounded">{"{{"}2.data{"}}"}</code></li>
              <li>Choose the destination folder</li>
            </ol>
          </Section>

          <Section title="Step 5: Send PDF via Email (Optional)">
            <p className="text-slate-600 mb-3">Add a Gmail module after Google Drive to email the PDF to the client:</p>
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Module: <strong>Gmail → Send an Email</strong></li>
              <li><strong>To:</strong> <code>{"{{"}1.email{"}}"}</code></li>
              <li><strong>Subject:</strong> Your proposal is ready</li>
              <li><strong>Attachment:</strong> Use the Google Drive file link from step 4</li>
            </ol>
          </Section>

          <Section title="Real-World Use Cases">
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { title: 'Invoice Generation', desc: 'Trigger: New row in Google Sheets → Generate invoice PDF → Email to client' },
                { title: 'Client Proposals', desc: 'Trigger: Typeform submission → Generate proposal → Save to Drive + notify Slack' },
                { title: 'Contract Creation', desc: 'Trigger: HubSpot deal created → Generate contract → Add to CRM' },
                { title: 'Report Automation', desc: 'Trigger: Airtable record → Generate weekly report → Share via Notion' },
              ].map((c, i) => (
                <div key={i} className="bg-violet-50 border border-violet-200 rounded-xl p-4">
                  <h4 className="font-bold text-violet-800 mb-1">{c.title}</h4>
                  <p className="text-sm text-violet-700">{c.desc}</p>
                </div>
              ))}
            </div>
          </Section>
        </>
      );

    case 'hugpdf-n8n-workflow':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            n8n is a powerful self-hosted workflow automation tool. This guide shows how to build
            production-grade PDF generation pipelines that run on your own infrastructure.
          </p>

          <Note type="info">
            n8n can be self-hosted (free, open-source) or used via n8n.cloud. Both work with the HugPDF API.
          </Note>

          <Section title="Install n8n">
            <CodeBlock code={`# Using Docker (recommended)
docker run -d --name n8n \\
  -p 5678:5678 \\
  -e N8N_BASIC_AUTH_ACTIVE=true \\
  -e N8N_BASIC_AUTH_USER=admin \\
  -e N8N_BASIC_AUTH_PASSWORD=yourpassword \\
  -v n8n_data:/home/node/.n8n \\
  n8nio/n8n

# Access at http://localhost:5678

# Or using npm
npm install n8n -g && n8n start`} />
          </Section>

          <Section title="Step 1: Set API Credentials">
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>In n8n, go to <strong>Settings → Credentials</strong></li>
              <li>Click <strong>Add Credential</strong> → select <strong>Header Auth</strong></li>
              <li>Name: <code>HugPDF API</code>, Header: <code>Authorization</code>, Value: <code>Bearer pdf_live_YOUR_KEY</code></li>
            </ol>
          </Section>

          <Section title="Step 2: HTTP Request Node">
            <p className="text-slate-600 mb-3">In your workflow, add an <strong>HTTP Request</strong> node:</p>
            <CodeBlock language="json" code={`{
  "method": "POST",
  "url": "https://api.hugpdf.app/api/v1/generate",
  "authentication": "headerAuth",
  "credentials": "HugPDF API",
  "bodyParametersUi": {
    "parameter": [
      { "name": "prompt", "value": "={{ $json.prompt }}" },
      { "name": "mode",   "value": "normal" }
    ]
  },
  "responseFormat": "file",
  "dataPropertyName": "pdfData"
}`} />
          </Section>

          <Section title="Step 3: Workflow Examples">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Webhook-triggered PDF generation</h3>
            <div className="bg-slate-50 rounded-xl p-4 font-mono text-sm text-slate-700 border border-slate-200 mb-4">
              Webhook → Set (build prompt) → HTTP Request (HugPDF) → Write Binary File → Respond to Webhook
            </div>
            <CodeBlock language="javascript" code={`// In a "Code" node to build the prompt dynamically:
const data = $input.first().json;

return [{
  json: {
    prompt: \`Create a detailed invoice for:
Company: \${data.company}
Services: \${data.services.join(', ')}
Total: $\${data.total}
Due Date: \${data.due_date}\`,
    mode: "normal",
    filename: \`invoice_\${data.company}_\${Date.now()}.pdf\`
  }
}];`} />
          </Section>

          <Section title="Step 4: Database-triggered Workflow">
            <p className="text-slate-600 mb-3">Trigger PDF generation from a Postgres/MySQL record:</p>
            <div className="bg-slate-50 rounded-xl p-4 font-mono text-sm text-slate-700 border border-slate-200">
              Cron (every 5 min) → Postgres (SELECT pending orders) → Split In Batches → HTTP Request (HugPDF) → Postgres (UPDATE status = 'sent') → Email
            </div>
          </Section>

          <Section title="Step 5: Error Handling & Retries">
            <CodeBlock language="javascript" code={`// In an "If" node after the HTTP Request:
// Route failures to a retry queue

// Error branch: Add to queue
const error = $input.first().json;
if (error.statusCode === 429) {
  // Rate limited - schedule retry in 60 seconds
  return [{ json: { retry_after: 60, ...error } }];
} else if (error.statusCode === 402) {
  // Out of credits - send alert
  return [{ json: { alert: "Out of credits!", ...error } }];
}`} />
          </Section>

          <Section title="n8n Workflow JSON">
            <p className="text-slate-600 mb-3">Import this ready-to-use workflow into n8n:</p>
            <CodeBlock language="json" code={`{
  "name": "HugPDF Generator",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": { "httpMethod": "POST", "path": "generate-pdf" }
    },
    {
      "name": "Generate PDF",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.hugpdf.app/api/v1/generate",
        "headers": { "Authorization": "Bearer ={{ $credentials.apiKey }}" },
        "body": { "prompt": "={{ $json.prompt }}", "mode": "={{ $json.mode || 'normal' }}" },
        "responseFormat": "file"
      }
    }
  ]
}`} />
          </Section>
        </>
      );

    case 'hugpdf-zapier-automation':
      return (
        <>
          <p className="text-lg text-slate-600 leading-relaxed mb-8">
            Zapier connects HugPDF with 5,000+ apps without any code. This guide shows how to use Zapier's
            Webhooks by Zapier to trigger PDF generation from any supported app.
          </p>

          <Section title="What You'll Need">
            <ul className="list-disc list-inside space-y-2 text-slate-600">
              <li>Zapier account (Starter plan or higher for webhooks)</li>
              <li>HugPDF API key from <Link to="/developer" className="text-violet-600 hover:underline">hugpdf.app/developer</Link></li>
            </ul>
          </Section>

          <Section title="Step 1: Create a New Zap">
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Go to <strong>zapier.com</strong> → <strong>Create Zap</strong></li>
              <li>Choose your trigger app (e.g., <strong>Google Forms</strong>)</li>
              <li>Set up your trigger event and test it</li>
            </ol>
          </Section>

          <Section title="Step 2: Add Webhooks Action">
            <ol className="list-decimal list-inside space-y-3 text-slate-600">
              <li>Search for <strong>Webhooks by Zapier</strong></li>
              <li>Choose <strong>POST</strong> as the action event</li>
              <li>Configure the webhook:</li>
            </ol>
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden my-4">
              <table className="w-full text-sm">
                <tbody className="divide-y divide-slate-100">
                  {[
                    { field: 'URL', value: 'https://api.hugpdf.app/api/v1/generate' },
                    { field: 'Payload Type', value: 'JSON' },
                    { field: 'Data — prompt', value: 'Create a proposal for {{company}} worth {{amount}}' },
                    { field: 'Data — mode', value: 'normal' },
                    { field: 'Headers — Authorization', value: 'Bearer pdf_live_YOUR_KEY' },
                    { field: 'Unflatten', value: 'yes' },
                  ].map(row => (
                    <tr key={row.field}>
                      <td className="px-4 py-2 font-medium text-slate-700 w-48 bg-slate-50">{row.field}</td>
                      <td className="px-4 py-2 font-mono text-slate-600 text-xs">{row.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>

          <Section title="Step 3: Handle the PDF Response">
            <p className="text-slate-600 mb-3">
              The HugPDF API returns a binary PDF file. Zapier will receive this as a file object.
              Use a <strong>Google Drive → Upload File</strong> action to save it:
            </p>
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Add action: <strong>Google Drive → Upload File</strong></li>
              <li>File: Select the response from the Webhook step</li>
              <li>File name: <code>{"{{"}company{"}}"}_proposal.pdf</code></li>
              <li>Folder: Choose your Drive folder</li>
            </ol>
          </Section>

          <Section title="Popular Zap Templates">
            <div className="space-y-3">
              {[
                { from: 'Google Forms', to: 'Google Drive', desc: 'New form response → Generate PDF → Save to Drive' },
                { from: 'HubSpot', to: 'Gmail', desc: 'Deal stage changed → Generate contract → Email to contact' },
                { from: 'Typeform', to: 'Slack', desc: 'New submission → Generate report → Post to Slack channel' },
                { from: 'Airtable', to: 'Dropbox', desc: 'New record → Generate invoice → Save to Dropbox' },
              ].map((z, i) => (
                <div key={i} className="flex items-center gap-4 bg-white border border-slate-200 rounded-xl p-4">
                  <div className="text-sm font-medium text-slate-700 w-28 shrink-0">{z.from}</div>
                  <ArrowRight className="w-4 h-4 text-slate-400 shrink-0" />
                  <div className="text-sm text-slate-500 flex-1">{z.desc}</div>
                  <div className="text-sm font-medium text-violet-600 w-24 shrink-0 text-right">{z.to}</div>
                </div>
              ))}
            </div>
          </Section>
        </>
      );

    default:
      return <p className="text-slate-600">Post not found.</p>;
  }
};

// ─── Main BlogPostPage Component ──────────────────────────────────────────────

const BlogPostPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  const post = BLOG_POSTS.find(p => p.slug === slug);
  const related = BLOG_POSTS.filter(p => p.slug !== slug).slice(0, 3);

  useEffect(() => {
    if (!post) navigate('/blog');
    window.scrollTo(0, 0);
  }, [post, navigate]);

  if (!post) return null;

  return (
    <div className="min-h-screen bg-white">
      {/* Hero */}
      <div className={`py-16 px-4 ${
        post.category === 'Automation'
          ? 'bg-gradient-to-br from-violet-900 to-indigo-900'
          : 'bg-gradient-to-br from-slate-900 to-slate-700'
      } text-white`}>
        <div className="max-w-3xl mx-auto">
          <Link to="/blog" className="inline-flex items-center gap-2 text-sm text-white/60 hover:text-white mb-8 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Blog
          </Link>
          <div className="flex items-center gap-3 mb-4">
            <span className="px-2.5 py-1 bg-white/20 rounded-full text-xs font-medium flex items-center gap-1">
              <Tag className="w-3 h-3" /> {post.category}
            </span>
            {post.tags.slice(0, 3).map(tag => (
              <span key={tag} className="px-2.5 py-1 bg-white/10 rounded-full text-xs">{tag}</span>
            ))}
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4 leading-snug">{post.title}</h1>
          <p className="text-lg text-white/70 mb-6">{post.excerpt}</p>
          <div className="flex items-center gap-6 text-sm text-white/50">
            <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" />{new Date(post.date).toLocaleDateString('en-US', { dateStyle: 'long' })}</span>
            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" />{post.readTime}</span>
            <span className="flex items-center gap-1.5"><BookOpen className="w-4 h-4" />{post.author}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-4 py-12">
        <article className="prose prose-slate max-w-none">
          <PostContent slug={slug} />
        </article>

        {/* CTA */}
        <div className="mt-16 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-2">Start building today</h3>
          <p className="text-violet-200 mb-6">Get your free API key and generate your first PDF in under 5 minutes.</p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to="/developer">
              <Button className="bg-white text-violet-700 hover:bg-violet-50 gap-2">
                Get Free API Key <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <a href="https://github.com/sarathoff/hug-pdf" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 gap-2">
                <Github className="w-4 h-4" /> View on GitHub
              </Button>
            </a>
          </div>
        </div>

        {/* Related Posts */}
        <div className="mt-16">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Related Articles</h3>
          <div className="grid sm:grid-cols-3 gap-4">
            {related.map(p => (
              <Link key={p.slug} to={`/blog/${p.slug}`} className="group">
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 hover:border-violet-300 hover:shadow-md transition-all h-full">
                  <span className="text-xs text-violet-600 font-medium">{p.category}</span>
                  <h4 className="font-semibold text-slate-900 group-hover:text-violet-700 text-sm mt-1 leading-snug">{p.title}</h4>
                  <span className="text-xs text-slate-400 mt-2 block">{p.readTime}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogPostPage;
