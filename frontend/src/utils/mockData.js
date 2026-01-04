// Mock data for initial development

export const mockGeneratePDF = (prompt) => {
  const lowerPrompt = prompt.toLowerCase();

  // Default template
  let title = 'Generated Document';
  let content = prompt;

  if (lowerPrompt.includes('resume') || lowerPrompt.includes('cv')) {
    title = 'Professional Resume';
    content = generateResumeHTML();
  } else if (lowerPrompt.includes('proposal') || lowerPrompt.includes('business')) {
    title = 'Business Proposal';
    content = generateProposalHTML();
  } else if (lowerPrompt.includes('report') || lowerPrompt.includes('iot') || lowerPrompt.includes('future')) {
    title = 'Research Report';
    content = generateReportHTML(prompt);
  } else if (lowerPrompt.includes('invoice')) {
    title = 'Invoice';
    content = generateInvoiceHTML();
  } else {
    content = generateGenericHTML(prompt);
  }

  return content;
};

export const mockChatResponse = (message, currentHTML) => {
  const lowerMessage = message.toLowerCase();

  let responseMessage = "I've updated the document based on your request.";
  let updatedHTML = currentHTML;

  if (lowerMessage.includes('color') || lowerMessage.includes('blue') || lowerMessage.includes('red')) {
    responseMessage = "I've changed the color scheme as requested.";
    updatedHTML = currentHTML.replace(/color: #2563eb/g, 'color: #dc2626');
    updatedHTML = updatedHTML.replace(/background: linear-gradient\(135deg, #3b82f6, #8b5cf6\)/g, 'background: linear-gradient(135deg, #ef4444, #f59e0b)');
  } else if (lowerMessage.includes('larger') || lowerMessage.includes('bigger') || lowerMessage.includes('size')) {
    responseMessage = "I've increased the font sizes.";
    updatedHTML = currentHTML.replace(/font-size: 36px/g, 'font-size: 48px');
    updatedHTML = updatedHTML.replace(/font-size: 18px/g, 'font-size: 22px');
  } else if (lowerMessage.includes('margin') || lowerMessage.includes('spacing') || lowerMessage.includes('padding')) {
    responseMessage = "I've adjusted the spacing and margins.";
    updatedHTML = currentHTML.replace(/padding: 40px/g, 'padding: 60px');
  }

  return { message: responseMessage, html: updatedHTML };
};

const generateResumeHTML = () => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Resume</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: white; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #2563eb; }
        .header h1 { font-size: 36px; color: #1e293b; margin-bottom: 10px; }
        .header p { font-size: 18px; color: #64748b; }
        .section { margin-bottom: 30px; }
        .section h2 { font-size: 24px; color: #2563eb; margin-bottom: 15px; border-left: 4px solid #2563eb; padding-left: 15px; }
        .section p, .section li { font-size: 16px; color: #475569; line-height: 1.6; }
        .section ul { margin-left: 20px; }
        .section li { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>John Doe</h1>
            <p>Software Engineer | Full Stack Developer</p>
            <p>john.doe@email.com | +1 (555) 123-4567</p>
        </div>
        
        <div class="section">
            <h2>Professional Summary</h2>
            <p>Experienced software engineer with 5+ years of expertise in full-stack development. Proficient in React, Node.js, and cloud technologies. Passionate about creating efficient and scalable solutions.</p>
        </div>
        
        <div class="section">
            <h2>Work Experience</h2>
            <p><strong>Senior Software Engineer</strong> - Tech Corp (2021 - Present)</p>
            <ul>
                <li>Led development of microservices architecture serving 1M+ users</li>
                <li>Improved application performance by 40% through optimization</li>
                <li>Mentored junior developers and conducted code reviews</li>
            </ul>
            <p style="margin-top: 15px;"><strong>Software Engineer</strong> - StartupXYZ (2019 - 2021)</p>
            <ul>
                <li>Built responsive web applications using React and TypeScript</li>
                <li>Implemented RESTful APIs with Node.js and Express</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Skills</h2>
            <ul>
                <li>Languages: JavaScript, Python, Java</li>
                <li>Frontend: React, Vue.js, HTML/CSS</li>
                <li>Backend: Node.js, Express, FastAPI</li>
                <li>Databases: MongoDB, PostgreSQL</li>
                <li>Cloud: AWS, Docker, Kubernetes</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Education</h2>
            <p><strong>Bachelor of Science in Computer Science</strong></p>
            <p>University of Technology (2015 - 2019)</p>
        </div>
    </div>
</body>
</html>
`;
};

const generateProposalHTML = () => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Proposal</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: white; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .cover { text-align: center; padding: 60px 0; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border-radius: 10px; margin-bottom: 40px; }
        .cover h1 { font-size: 42px; margin-bottom: 15px; }
        .cover p { font-size: 20px; }
        .section { margin-bottom: 35px; }
        .section h2 { font-size: 28px; color: #1e293b; margin-bottom: 15px; }
        .section p { font-size: 16px; color: #475569; line-height: 1.8; margin-bottom: 12px; }
        .highlight { background: #eff6ff; padding: 20px; border-left: 4px solid #3b82f6; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="cover">
            <h1>Business Proposal</h1>
            <p>Strategic Partnership Opportunity</p>
            <p style="margin-top: 20px; font-size: 16px;">Prepared for: Valued Client</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>We are pleased to present this comprehensive proposal for a strategic partnership that will drive mutual growth and innovation. Our solution addresses key challenges in your industry while delivering measurable ROI.</p>
        </div>
        
        <div class="section">
            <h2>Problem Statement</h2>
            <p>Organizations today face increasing complexity in managing digital transformation initiatives. Traditional approaches often result in fragmented systems, reduced efficiency, and missed opportunities for innovation.</p>
        </div>
        
        <div class="section">
            <h2>Proposed Solution</h2>
            <p>Our integrated platform provides a comprehensive solution that streamlines operations, enhances collaboration, and drives measurable business outcomes.</p>
            <div class="highlight">
                <p><strong>Key Benefits:</strong></p>
                <p>• 40% reduction in operational costs</p>
                <p>• 60% improvement in team productivity</p>
                <p>• Seamless integration with existing systems</p>
                <p>• 24/7 dedicated support and maintenance</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Investment</h2>
            <p>Total project investment: $150,000</p>
            <p>Timeline: 6 months</p>
            <p>Expected ROI: 200% within first year</p>
        </div>
        
        <div class="section">
            <h2>Next Steps</h2>
            <p>We are excited about the opportunity to partner with your organization. Let's schedule a meeting to discuss how we can customize this solution to meet your specific needs.</p>
        </div>
    </div>
</body>
</html>
`;
};

const generateReportHTML = (prompt) => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: white; padding: 40px; line-height: 1.8; }
        .container { max-width: 800px; margin: 0 auto; }
        .title-page { text-align: center; padding: 80px 0; border-bottom: 2px solid #e2e8f0; margin-bottom: 40px; }
        .title-page h1 { font-size: 38px; color: #1e293b; margin-bottom: 20px; }
        .title-page p { font-size: 18px; color: #64748b; }
        .section { margin-bottom: 35px; }
        .section h2 { font-size: 26px; color: #2563eb; margin-bottom: 15px; margin-top: 25px; }
        .section h3 { font-size: 20px; color: #1e293b; margin-bottom: 10px; margin-top: 20px; }
        .section p { font-size: 16px; color: #334155; margin-bottom: 15px; text-align: justify; }
        .abstract { background: #f8fafc; padding: 25px; border-left: 4px solid #2563eb; margin: 30px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="title-page">
            <h1>The Future of IoT</h1>
            <p>A Comprehensive Analysis</p>
            <p style="margin-top: 30px;">Date: ${new Date().toLocaleDateString()}</p>
        </div>
        
        <div class="abstract">
            <h3>Abstract</h3>
            <p>This report explores the emerging trends, challenges, and opportunities in the Internet of Things (IoT) ecosystem. As we move towards a more connected world, IoT technologies are reshaping industries and transforming how we interact with our environment.</p>
        </div>
        
        <div class="section">
            <h2>1. Introduction</h2>
            <p>The Internet of Things represents a paradigm shift in technology, connecting billions of devices worldwide. From smart homes to industrial automation, IoT is revolutionizing every aspect of modern life. This report examines the future trajectory of IoT technologies and their potential impact on society.</p>
        </div>
        
        <div class="section">
            <h2>2. Current State of IoT</h2>
            <p>Today's IoT ecosystem encompasses over 30 billion connected devices globally. These devices generate massive amounts of data, enabling unprecedented insights into operational efficiency, user behavior, and system performance. Key sectors leading IoT adoption include manufacturing, healthcare, transportation, and smart cities.</p>
            
            <h3>2.1 Market Growth</h3>
            <p>The global IoT market is projected to reach $1.5 trillion by 2027, growing at a CAGR of 24%. This growth is driven by advances in connectivity, artificial intelligence, and edge computing technologies.</p>
        </div>
        
        <div class="section">
            <h2>3. Emerging Trends</h2>
            
            <h3>3.1 Edge Computing</h3>
            <p>Edge computing is becoming critical for IoT deployments, enabling real-time data processing and reducing latency. By processing data closer to the source, edge computing enhances security and reduces bandwidth requirements.</p>
            
            <h3>3.2 AI Integration</h3>
            <p>Artificial intelligence and machine learning are being integrated into IoT devices, enabling predictive maintenance, anomaly detection, and autonomous decision-making. This convergence of AI and IoT is creating intelligent systems capable of self-optimization.</p>
            
            <h3>3.3 5G Connectivity</h3>
            <p>The rollout of 5G networks is accelerating IoT adoption by providing faster speeds, lower latency, and support for massive device connectivity. 5G enables new use cases such as autonomous vehicles, remote surgery, and immersive AR/VR experiences.</p>
        </div>
        
        <div class="section">
            <h2>4. Challenges and Considerations</h2>
            <p>Despite its promise, IoT faces several challenges including security vulnerabilities, privacy concerns, interoperability issues, and the need for standardization. Addressing these challenges requires collaboration between industry stakeholders, policymakers, and technology providers.</p>
        </div>
        
        <div class="section">
            <h2>5. Future Outlook</h2>
            <p>The future of IoT is characterized by increased intelligence, autonomy, and integration. As technologies mature and costs decrease, IoT will become ubiquitous, seamlessly integrated into our daily lives. Organizations that embrace IoT strategically will gain competitive advantages through improved efficiency, innovation, and customer experiences.</p>
        </div>
        
        <div class="section">
            <h2>6. Conclusion</h2>
            <p>The Internet of Things represents a transformative force that will continue to shape our world for decades to come. By understanding current trends and preparing for future developments, organizations can position themselves to capitalize on the opportunities IoT presents while mitigating associated risks.</p>
        </div>
    </div>
</body>
</html>
`;
};

const generateInvoiceHTML = () => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: white; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #2563eb; }
        .header h1 { font-size: 32px; color: #2563eb; }
        table { width: 100%; border-collapse: collapse; margin: 30px 0; }
        th { background: #f1f5f9; padding: 12px; text-align: left; font-weight: 600; color: #1e293b; }
        td { padding: 12px; border-bottom: 1px solid #e2e8f0; color: #475569; }
        .total { text-align: right; font-size: 24px; font-weight: 700; color: #2563eb; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>INVOICE</h1>
                <p>Invoice #: INV-2024-001</p>
                <p>Date: ${new Date().toLocaleDateString()}</p>
            </div>
            <div style="text-align: right;">
                <p><strong>Your Company Name</strong></p>
                <p>123 Business Street</p>
                <p>City, State 12345</p>
            </div>
        </div>
        
        <div style="margin-bottom: 30px;">
            <p><strong>Bill To:</strong></p>
            <p>Client Name</p>
            <p>456 Client Avenue</p>
            <p>City, State 67890</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Consulting Services</td>
                    <td>10 hours</td>
                    <td>$150.00</td>
                    <td>$1,500.00</td>
                </tr>
                <tr>
                    <td>Software Development</td>
                    <td>20 hours</td>
                    <td>$200.00</td>
                    <td>$4,000.00</td>
                </tr>
                <tr>
                    <td>Project Management</td>
                    <td>5 hours</td>
                    <td>$175.00</td>
                    <td>$875.00</td>
                </tr>
            </tbody>
        </table>
        
        <div class="total">
            <p>Subtotal: $6,375.00</p>
            <p>Tax (10%): $637.50</p>
            <p style="border-top: 2px solid #2563eb; padding-top: 10px; margin-top: 10px;">Total Due: $7,012.50</p>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #f8fafc; border-radius: 8px;">
            <p><strong>Payment Terms:</strong> Due within 30 days</p>
            <p><strong>Payment Methods:</strong> Bank Transfer, Check, Credit Card</p>
        </div>
    </div>
</body>
</html>
`;
};

const generateGenericHTML = (prompt) => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: white; padding: 40px; line-height: 1.8; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { font-size: 36px; color: #1e293b; margin-bottom: 20px; }
        p { font-size: 16px; color: #475569; margin-bottom: 15px; text-align: justify; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Generated Document</h1>
        <p>${prompt}</p>
        <p>This is a generated document based on your request. You can ask me to modify the content, change colors, adjust formatting, or add more sections.</p>
    </div>
</body>
</html>
`;
};
