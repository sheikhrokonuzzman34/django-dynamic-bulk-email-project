import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.urls import reverse

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

def send_bulk_email(request):
    if request.method == 'POST':
        form = BulkEmailForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.cleaned_data['template']
            excel_file = request.FILES['excel_file']
            
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
                        # Prepare email content
                        context = Context({'name': row['name']})
                        subject_template = Template(template.subject)
                        body_template = Template(template.body)
                        
                        subject = subject_template.render(context)
                        body = body_template.render(context)
                        
                        # Send email
                        send_mail(
                            subject,
                            body,
                            settings.DEFAULT_FROM_EMAIL,
                            [row['email']],
                            fail_silently=False,
                        )
                        
                        # Log success
                        EmailLog.objects.create(
                            subject=subject,
                            recipient_email=row['email'],
                            recipient_name=row['name'],
                            body=body,
                            status='SUCCESS'
                        )
                        success_count += 1
                        
                    except Exception as e:
                        # Log failure
                        EmailLog.objects.create(
                            subject=subject if 'subject' in locals() else template.subject,
                            recipient_email=row['email'],
                            recipient_name=row['name'],
                            body=body if 'body' in locals() else template.body,
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