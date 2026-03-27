/**
 * Email MCP Server - Silver Tier
 * Express server for sending emails with Human-in-the-Loop approval.
 */

const express = require('express');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
const winston = require('winston');

dotenv.config();

const PORT = process.env.MCP_PORT || 3000;
const SMTP_HOST = process.env.SMTP_HOST || 'smtp.gmail.com';
const SMTP_PORT = process.env.SMTP_PORT || 587;
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;
const VAULT_PATH = process.env.VAULT_PATH || path.join(__dirname, '..', 'AI_Employee_Vault');
const APPROVED_FOLDER = path.join(VAULT_PATH, 'Approved');
const LOGS_FOLDER = path.join(__dirname, '..', 'logs');

try { if (!fs.existsSync(LOGS_FOLDER)) fs.mkdirSync(LOGS_FOLDER, { recursive: true }); } catch(e) {}

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
    transports: [
        new winston.transports.File({ filename: path.join(LOGS_FOLDER, 'mcp_error.log'), level: 'error' }),
        new winston.transports.File({ filename: path.join(LOGS_FOLDER, 'mcp.log') })
    ]
});

let transporter = null;

function createTransporter() {
    transporter = nodemailer.createTransport({
        host: SMTP_HOST,
        port: parseInt(SMTP_PORT),
        secure: SMTP_PORT == '465',
        auth: { user: SMTP_USER, pass: SMTP_PASS }
    });
    transporter.verify((err, success) => {
        if (err) { logger.error('SMTP failed:', err); console.error('SMTP connection failed'); }
        else { logger.info('SMTP verified'); console.log('✓ SMTP connection verified'); }
    });
}

function isValidEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }

function validateInput(data) {
    const errors = [];
    if (!data.to) errors.push('Missing "to" field');
    else if (!isValidEmail(data.to)) errors.push('Invalid email: ' + data.to);
    if (!data.subject) errors.push('Missing "subject" field');
    if (!data.body) errors.push('Missing "body" field');
    return errors;
}

function findApprovedDraft(emailData) {
    if (!fs.existsSync(APPROVED_FOLDER)) return null;
    const files = fs.readdirSync(APPROVED_FOLDER).filter(f => f.toLowerCase().startsWith('email_') && f.endsWith('.md'));
    if (files.length === 0) return null;
    for (const file of files) {
        const content = fs.readFileSync(path.join(APPROVED_FOLDER, file), 'utf-8');
        const toMatch = content.toLowerCase().includes(emailData.to.toLowerCase());
        const subjectMatch = content.toLowerCase().includes(emailData.subject.toLowerCase());
        const isApproved = !content.includes('status: sent');
        if ((toMatch || subjectMatch) && isApproved) return { filename: file, filePath: path.join(APPROVED_FOLDER, file), content };
    }
    return { filename: files[0], filePath: path.join(APPROVED_FOLDER, files[0]), content: fs.readFileSync(path.join(APPROVED_FOLDER, files[0]), 'utf-8') };
}

function markAsSent(draftInfo) {
    let content = draftInfo.content.replace(/status:\s*(pending|approved)/i, 'status: sent');
    if (!content.includes('sent_date:')) content = content.replace(/status:\s*sent/i, 'status: sent\nsent_date: ' + new Date().toISOString());
    fs.writeFileSync(draftInfo.filePath, content, 'utf-8');
}

async function sendEmailWithRetry(mailOptions, maxRetries = 3) {
    for (let i = 1; i <= maxRetries; i++) {
        try {
            const info = await transporter.sendMail(mailOptions);
            return { success: true, messageId: info.messageId };
        } catch (err) {
            if (i < maxRetries) await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
            else return { success: false, error: err.message };
        }
    }
}

const app = express();
app.use(express.json());
app.use((req, res, next) => { logger.info(req.method + ' ' + req.path); next(); });

app.get('/health', (req, res) => res.json({ status: 'healthy', smtp_connected: transporter !== null }));

app.get('/approved', (req, res) => {
    if (!fs.existsSync(APPROVED_FOLDER)) return res.json({ drafts: [] });
    const files = fs.readdirSync(APPROVED_FOLDER).filter(f => f.startsWith('email_') && f.endsWith('.md')).map(f => ({ filename: f }));
    res.json({ drafts: files, count: files.length });
});

app.post('/send_email', async (req, res) => {
    try {
        const { to, subject, body } = req.body;
        const errors = validateInput({ to, subject, body });
        if (errors.length > 0) return res.status(400).json({ success: false, errors });

        console.log('\n📧 Checking for approved draft...');
        const draftInfo = findApprovedDraft({ to, subject, body });
        
        if (!draftInfo) {
            logger.warn('No approved draft - email NOT sent');
            console.log('⚠ No approved draft found in /Approved/ folder');
            console.log('❌ Email NOT sent - Human-in-the-Loop check failed');
            return res.status(403).json({ success: false, error: 'No approved draft found' });
        }

        console.log('✓ Approved draft found: ' + draftInfo.filename);
        
        const mailOptions = { from: SMTP_USER, to, subject, text: body };
        console.log('📤 Sending email to ' + to + '...');
        
        const result = await sendEmailWithRetry(mailOptions);
        
        if (result.success) {
            markAsSent(draftInfo);
            console.log('✓ Email sent successfully to ' + to);
            logger.info('Email sent', { to, messageId: result.messageId });
            res.json({ success: true, messageId: result.messageId, draft_file: draftInfo.filename });
        } else {
            console.log('❌ Failed: ' + result.error);
            res.status(500).json({ success: false, error: result.error });
        }
    } catch (err) {
        logger.error('Error:', err);
        console.log('❌ Error: ' + err.message);
        res.status(500).json({ success: false, error: err.message });
    }
});

if (!SMTP_USER || !SMTP_PASS) { console.error('❌ Set SMTP_USER and SMTP_PASS in .env'); process.exit(1); }

createTransporter();
if (!fs.existsSync(APPROVED_FOLDER)) { fs.mkdirSync(APPROVED_FOLDER, { recursive: true }); console.log('✓ Created Approved folder'); }

app.listen(PORT, () => {
    logger.info('MCP Server started on port ' + PORT);
    console.log('\n' + '='.repeat(60));
    console.log('📧 Email MCP Server');
    console.log('='.repeat(60));
    console.log('MCP Server started on port ' + PORT);
    console.log('SMTP: ' + SMTP_HOST + ':' + SMTP_PORT);
    console.log('='.repeat(60));
});
