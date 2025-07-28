"""
Email Notification Service
Handles sending email notifications for job application workflow
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", "noreply@hotelonboarding.com")
        self.from_name = os.getenv("FROM_NAME", "Hotel Onboarding System")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Check if email is configured (skip default placeholder values)
        self.is_configured = bool(
            self.smtp_username and 
            self.smtp_password and 
            self.smtp_username != "your-email@gmail.com" and
            self.smtp_password != "your-app-password"
        )
        
        if not self.is_configured:
            logger.warning("Email service not configured. Email notifications will be logged only.")
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email with HTML and optional text content"""
        
        if not self.is_configured:
            logger.info(f"📧 [DEV MODE] Email would be sent to {to_email}")
            logger.info(f"📧 [DEV MODE] Subject: {subject}")
            logger.info(f"📧 [DEV MODE] Content preview: {(text_content or html_content)[:200]}...")
            return True  # Return success for development
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _get_email_template(self, template_type: str, **kwargs) -> tuple[str, str]:
        """Get email template HTML and text content"""
        
        if template_type == "approval":
            return self._get_approval_template(**kwargs)
        elif template_type == "rejection":
            return self._get_rejection_template(**kwargs)
        elif template_type == "talent_pool":
            return self._get_talent_pool_template(**kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def _get_approval_template(self, applicant_name: str, property_name: str, position: str, 
                             job_title: str, start_date: str, pay_rate: float, 
                             onboarding_link: str, manager_name: str, manager_email: str) -> tuple[str, str]:
        """Get approval email template"""
        
        subject = f"Congratulations! Job Offer from {property_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .button {{ display: inline-block; background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Congratulations, {applicant_name}!</h1>
                </div>
                <div class="content">
                    <p>We are pleased to offer you the position of <strong>{job_title}</strong> at <strong>{property_name}</strong>.</p>
                    
                    <h3>Job Details:</h3>
                    <ul>
                        <li><strong>Position:</strong> {position}</li>
                        <li><strong>Pay Rate:</strong> ${pay_rate:.2f}/hour</li>
                        <li><strong>Start Date:</strong> {start_date}</li>
                        <li><strong>Property:</strong> {property_name}</li>
                    </ul>
                    
                    <p>To accept this offer and complete your onboarding process, please click the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{onboarding_link}" class="button">Complete Onboarding</a>
                    </div>
                    
                    <p><strong>Important:</strong> This onboarding link will expire in 7 days. Please complete your onboarding as soon as possible.</p>
                    
                    <p>If you have any questions, please contact your hiring manager:</p>
                    <p><strong>{manager_name}</strong><br>
                    Email: <a href="mailto:{manager_email}">{manager_email}</a></p>
                    
                    <p>We look forward to welcoming you to our team!</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Hotel Onboarding System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Congratulations, {applicant_name}!
        
        We are pleased to offer you the position of {job_title} at {property_name}.
        
        Job Details:
        - Position: {position}
        - Pay Rate: ${pay_rate:.2f}/hour
        - Start Date: {start_date}
        - Property: {property_name}
        
        To accept this offer and complete your onboarding process, please visit:
        {onboarding_link}
        
        Important: This onboarding link will expire in 7 days. Please complete your onboarding as soon as possible.
        
        If you have any questions, please contact your hiring manager:
        {manager_name}
        Email: {manager_email}
        
        We look forward to welcoming you to our team!
        
        ---
        This is an automated message from the Hotel Onboarding System.
        Please do not reply to this email.
        """
        
        return html_content, text_content
    
    def _get_rejection_template(self, applicant_name: str, property_name: str, position: str, 
                               manager_name: str, manager_email: str) -> tuple[str, str]:
        """Get rejection email template"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .footer {{ background-color: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Update</h1>
                </div>
                <div class="content">
                    <p>Dear {applicant_name},</p>
                    
                    <p>Thank you for your interest in the <strong>{position}</strong> position at <strong>{property_name}</strong>.</p>
                    
                    <p>After careful consideration, we have decided to move forward with another candidate for this particular role. This decision was not easy, as we received many qualified applications.</p>
                    
                    <p>We encourage you to apply for future openings that match your skills and experience. We will keep your application on file for consideration for other opportunities.</p>
                    
                    <p>If you have any questions, please feel free to contact:</p>
                    <p><strong>{manager_name}</strong><br>
                    Email: <a href="mailto:{manager_email}">{manager_email}</a></p>
                    
                    <p>Thank you again for your interest in joining our team.</p>
                    
                    <p>Best regards,<br>
                    The Hiring Team at {property_name}</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Hotel Onboarding System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Dear {applicant_name},
        
        Thank you for your interest in the {position} position at {property_name}.
        
        After careful consideration, we have decided to move forward with another candidate for this particular role. This decision was not easy, as we received many qualified applications.
        
        We encourage you to apply for future openings that match your skills and experience. We will keep your application on file for consideration for other opportunities.
        
        If you have any questions, please feel free to contact:
        {manager_name}
        Email: {manager_email}
        
        Thank you again for your interest in joining our team.
        
        Best regards,
        The Hiring Team at {property_name}
        
        ---
        This is an automated message from the Hotel Onboarding System.
        Please do not reply to this email.
        """
        
        return html_content, text_content
    
    def _get_talent_pool_template(self, applicant_name: str, property_name: str, position: str, 
                                 manager_name: str, manager_email: str) -> tuple[str, str]:
        """Get talent pool notification template"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f59e0b; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .footer {{ background-color: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>You're in Our Talent Pool!</h1>
                </div>
                <div class="content">
                    <p>Dear {applicant_name},</p>
                    
                    <p>Thank you for your interest in the <strong>{position}</strong> position at <strong>{property_name}</strong>.</p>
                    
                    <p>While we have selected another candidate for this specific role, we were impressed with your qualifications and would like to keep you in our talent pool for future opportunities.</p>
                    
                    <p><strong>What this means:</strong></p>
                    <ul>
                        <li>Your application will be kept on file for future openings</li>
                        <li>You'll be among the first to be contacted for similar positions</li>
                        <li>We may reach out when new opportunities become available</li>
                    </ul>
                    
                    <p>We encourage you to continue checking our job postings and applying for positions that interest you.</p>
                    
                    <p>If you have any questions, please feel free to contact:</p>
                    <p><strong>{manager_name}</strong><br>
                    Email: <a href="mailto:{manager_email}">{manager_email}</a></p>
                    
                    <p>Thank you for your continued interest in joining our team!</p>
                    
                    <p>Best regards,<br>
                    The Hiring Team at {property_name}</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Hotel Onboarding System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Dear {applicant_name},
        
        Thank you for your interest in the {position} position at {property_name}.
        
        While we have selected another candidate for this specific role, we were impressed with your qualifications and would like to keep you in our talent pool for future opportunities.
        
        What this means:
        - Your application will be kept on file for future openings
        - You'll be among the first to be contacted for similar positions
        - We may reach out when new opportunities become available
        
        We encourage you to continue checking our job postings and applying for positions that interest you.
        
        If you have any questions, please feel free to contact:
        {manager_name}
        Email: {manager_email}
        
        Thank you for your continued interest in joining our team!
        
        Best regards,
        The Hiring Team at {property_name}
        
        ---
        This is an automated message from the Hotel Onboarding System.
        Please do not reply to this email.
        """
        
        return html_content, text_content
    
    async def send_approval_notification(self, applicant_email: str, applicant_name: str, 
                                       property_name: str, position: str, job_title: str,
                                       start_date: str, pay_rate: float, onboarding_link: str,
                                       manager_name: str, manager_email: str) -> bool:
        """Send approval notification email"""
        
        html_content, text_content = self._get_approval_template(
            applicant_name=applicant_name,
            property_name=property_name,
            position=position,
            job_title=job_title,
            start_date=start_date,
            pay_rate=pay_rate,
            onboarding_link=onboarding_link,
            manager_name=manager_name,
            manager_email=manager_email
        )
        
        subject = f"Congratulations! Job Offer from {property_name}"
        
        return await self.send_email(applicant_email, subject, html_content, text_content)
    
    async def send_rejection_notification(self, applicant_email: str, applicant_name: str,
                                        property_name: str, position: str,
                                        manager_name: str, manager_email: str) -> bool:
        """Send rejection notification email"""
        
        html_content, text_content = self._get_rejection_template(
            applicant_name=applicant_name,
            property_name=property_name,
            position=position,
            manager_name=manager_name,
            manager_email=manager_email
        )
        
        subject = f"Application Update - {property_name}"
        
        return await self.send_email(applicant_email, subject, html_content, text_content)
    
    async def send_talent_pool_notification(self, applicant_email: str, applicant_name: str,
                                          property_name: str, position: str,
                                          manager_name: str, manager_email: str) -> bool:
        """Send talent pool notification email"""
        
        html_content, text_content = self._get_talent_pool_template(
            applicant_name=applicant_name,
            property_name=property_name,
            position=position,
            manager_name=manager_name,
            manager_email=manager_email
        )
        
        subject = f"You're in Our Talent Pool - {property_name}"
        
        return await self.send_email(applicant_email, subject, html_content, text_content)

# Create global email service instance
email_service = EmailService()