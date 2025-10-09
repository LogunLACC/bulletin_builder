"""
Email Deliverability Guidance Module

Provides educational content and guidance for users to improve email deliverability
through proper DKIM, SPF, and DMARC configuration.
"""

import tkinter as tk
from tkinter import messagebox
import webbrowser


def show_email_auth_guidance(parent=None):
    """
    Display a comprehensive dialog explaining DKIM, SPF, and DMARC
    email authentication methods to help users improve deliverability.
    
    Args:
        parent: Optional parent window for the dialog
    """
    
    guidance_text = """Email Authentication & Deliverability Guide

To ensure your bulletins reach recipients' inboxes and avoid spam folders, 
configure these three essential email authentication methods:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SPF (Sender Policy Framework)
   What it is: Specifies which mail servers are authorized to send email 
   from your domain.
   
   How to set it up:
   • Add a TXT record to your domain's DNS settings
   • Format: v=spf1 include:_spf.yourmailprovider.com ~all
   • Example for Gmail: v=spf1 include:_spf.google.com ~all
   
   Why it matters: Prevents spammers from forging your domain name

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. DKIM (DomainKeys Identified Mail)
   What it is: Adds a digital signature to your emails to verify they 
   haven't been tampered with.
   
   How to set it up:
   • Your email provider generates a public/private key pair
   • Add the public key as a TXT record to your DNS
   • Format: selector._domainkey.yourdomain.com TXT "v=DKIM1; k=rsa; p=[key]"
   • Most providers (Gmail, Outlook, etc.) provide setup instructions
   
   Why it matters: Proves email authenticity and protects your reputation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. DMARC (Domain-based Message Authentication)
   What it is: Tells receiving mail servers what to do if SPF or DKIM 
   checks fail, and provides reporting.
   
   How to set it up:
   • Add a TXT record at _dmarc.yourdomain.com
   • Format: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
   • Policies: none (monitor), quarantine (spam folder), reject (block)
   • Start with p=none to monitor, then increase strictness
   
   Why it matters: Gives you control and visibility over email authentication

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quick Setup Checklist:
☐ Contact your email provider for their specific SPF/DKIM setup guides
☐ Access your domain registrar's DNS management console
☐ Add SPF TXT record with authorized mail servers
☐ Generate DKIM keys and add public key to DNS
☐ Add DMARC policy record (start with p=none for monitoring)
☐ Wait 24-48 hours for DNS propagation
☐ Test your configuration at mail-tester.com or mxtoolbox.com
☐ Monitor DMARC reports and adjust policy as needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Common Email Providers:
• Gmail/Google Workspace: support.google.com/a/topic/2716885
• Microsoft 365: docs.microsoft.com/microsoft-365/security
• GoDaddy: godaddy.com/help/add-an-spf-record-19218
• Cloudflare: developers.cloudflare.com/dns/manage-dns-records

Additional Tips:
✓ Use a consistent "From" address and domain
✓ Keep your mailing list clean (remove bounces)
✓ Avoid spam trigger words in subject lines
✓ Include unsubscribe links in all emails
✓ Warm up new domains gradually (start with small batches)
✓ Monitor your sender reputation regularly
"""
    
    # Create a custom dialog window
    dialog = tk.Toplevel(parent)
    dialog.title("Email Deliverability Guidance")
    dialog.geometry("800x650")
    
    # Make dialog modal
    dialog.transient(parent)
    dialog.grab_set()
    
    # Add a frame with scrollbar for the content
    frame = tk.Frame(dialog)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create text widget with scrollbar
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(
        frame,
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        font=("Courier New", 10),
        padx=10,
        pady=10
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)
    
    # Insert the guidance text
    text_widget.insert("1.0", guidance_text)
    text_widget.config(state=tk.DISABLED)  # Make read-only
    
    # Add buttons at the bottom
    button_frame = tk.Frame(dialog)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def open_test_tool():
        """Open mail-tester.com in browser"""
        webbrowser.open("https://www.mail-tester.com")
    
    def open_mx_toolbox():
        """Open MX Toolbox for DNS/DMARC checking"""
        webbrowser.open("https://mxtoolbox.com/SuperTool.aspx")
    
    def copy_to_clipboard():
        """Copy guidance text to clipboard"""
        try:
            dialog.clipboard_clear()
            dialog.clipboard_append(guidance_text)
            messagebox.showinfo(
                "Copied",
                "Email deliverability guide copied to clipboard!",
                parent=dialog
            )
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy: {e}", parent=dialog)
    
    # Add action buttons
    tk.Button(
        button_frame,
        text="Test Email Configuration",
        command=open_test_tool,
        width=25
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="Check DNS Records",
        command=open_mx_toolbox,
        width=25
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="Copy to Clipboard",
        command=copy_to_clipboard,
        width=20
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="Close",
        command=dialog.destroy,
        width=15
    ).pack(side=tk.RIGHT, padx=5)
    
    # Center the dialog on parent or screen
    if parent:
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")


def init(app):
    """
    Initialize email deliverability guidance feature on the app instance.
    
    Args:
        app: The main application instance
    """
    app.show_email_auth_guidance = lambda: show_email_auth_guidance(parent=app)
