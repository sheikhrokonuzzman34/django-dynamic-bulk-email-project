import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context

from main.forms import *
from main.models import *

def template_list(request):
    templates = EmailTemplate.objects.all().order_by('-created_at')
    return render(request, 'emails/template_list.html', {'templates': templates})

def template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email template created successfully!')
            return redirect('template_list')
    else:
        form = EmailTemplateForm()
    
    return render(request, 'emails/template_form.html', {'form': form})

def template_edit(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email template updated successfully!')
            return redirect('template_list')
    else:
        form = EmailTemplateForm(instance=template)
    
    return render(request, 'emails/template_form.html', {
        'form': form,
        'template': template
    })

def template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Email template deleted successfully!')
        return redirect('template_list')
    
    return render(request, 'emails/template_confirm_delete.html', {
        'template': template
    })
    
    
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.utils.html import strip_tags
from django.contrib import messages
from django.conf import settings
import pandas as pd
from .forms import BulkEmailForm
from .models import EmailTemplate, EmailLog

def send_bulk_email(request):
    if request.method == 'POST':
        form = BulkEmailForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.cleaned_data['template']
            excel_file = request.FILES['excel_file']
            file_name = excel_file.name  # Get the name of the uploaded file
            
            try:
                # Read Excel file
                df = pd.read_excel(excel_file)
                required_columns = ['name', 'email']
                
                # Validate Excel structure
                if not all(col in df.columns for col in required_columns):
                    messages.error(request, 'Excel file must contain "name" and "email" columns!')
                    return redirect('send_bulk_email')
                
                success_count = 0
                error_count = 0
                
                # Process each row
                for _, row in df.iterrows():
                    try:
                        # Prepare email content with file name in the context
                        context = Context({
                            'name': row['name'],
                            'file_name': file_name  # Include the file name in the context
                        })
                        subject_template = Template(template.subject)
                        body_template = Template(template.body)  # Assuming template.body contains HTML content
                        
                        # Render subject and body
                        subject = subject_template.render(context)
                        html_body = body_template.render(context)
                        plain_body = strip_tags(html_body)  # Convert HTML to plain text for plain text alternative
                        
                        # Prepare and send email
                        email = EmailMultiAlternatives(
                            subject,
                            plain_body,  # Set plain text body as fallback
                            settings.DEFAULT_FROM_EMAIL,
                            [row['email']]
                        )
                        email.attach_alternative(html_body, "text/html")  # Attach HTML content
                        
                        # Send email
                        email.send(fail_silently=False)

                        # Log success
                        EmailLog.objects.create(
                            subject=subject,
                            recipient_email=row['email'],
                            recipient_name=row['name'],
                            body=html_body,
                            status='SUCCESS'
                        )
                        success_count += 1

                    except Exception as e:
                        # Log failure
                        EmailLog.objects.create(
                            subject=subject if 'subject' in locals() else template.subject,
                            recipient_email=row['email'],
                            recipient_name=row['name'],
                            body=html_body if 'html_body' in locals() else template.body,
                            status='FAILED',
                            error_message=str(e)
                        )
                        error_count += 1
                
                messages.success(
                    request,
                    f'Bulk email process completed. Success: {success_count}, Failed: {error_count}'
                )
                return redirect('email_logs')
                
            except Exception as e:
                messages.error(request, f'Error processing Excel file: {str(e)}')
                return redirect('send_bulk_email')
    else:
        form = BulkEmailForm()
    
    return render(request, 'emails/send_bulk_email.html', {'form': form})

def email_logs(request):
    logs = EmailLog.objects.all().order_by('-sent_at')
    return render(request, 'emails/email_logs.html', {'logs': logs})



def delete_selected_email_logs(request):
    if request.method == 'POST':
        log_ids = request.POST.getlist('log_ids')
        
        if log_ids:
            # Delete selected logs
            EmailLog.objects.filter(id__in=log_ids).delete()
            messages.success(request, f'Successfully deleted {len(log_ids)} log(s).')
        else:
            messages.warning(request, 'No logs selected for deletion.')
            
    return redirect('email_logs')