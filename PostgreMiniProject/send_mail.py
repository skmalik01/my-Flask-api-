import smtplib
from email.mime.text import MIMEText

def send_mail(customer, dealer, rating, comments):
    port = 587  # TLS port
    smtp_server = 'live.smtp.mailtrap.io'  # Correct Mailtrap SMTP server
    login = 'smtp@mailtrap.io'  # Replace with your actual Mailtrap username
    password = '6fabd1406a6b02ba14e1f4d93c785416'  # Replace with your actual Mailtrap password
    
    message = f"""
    <h3>New Feedback Submission</h3>
    <ul>
        <li>Customer : {customer}</li>
        <li>Dealer : {dealer}</li>
        <li>Rating : {rating}</li>
        <li>Comments : {comments}</li>
    </ul>
    """
    
    sender_email = 'malikshaikh@gmail.com'
    reciever_email = 'ayelik01@gmail.com'
    
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Lexus Feedback'
    msg['From'] = sender_email  # Fix: Use actual email variable
    msg['To'] = reciever_email  # Fix: Use actual email variable
    
    try:
        # Create SMTP session
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure connection using TLS
            server.login(login, password)  # Authenticate
            server.sendmail(sender_email, reciever_email, msg.as_string())  
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
