from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Report, Feedback, BannedUser
from users.models import User
from messaging.models import Conversation, Message

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.username == 'Snapit')

@user_passes_test(is_admin)
def admin_dashboard(request):
    reports_pending = Report.objects.filter(resolved=False).count()
    feedbacks_count = Feedback.objects.count()
    banned_users = BannedUser.objects.count()
    
    recent_reports = Report.objects.select_related('reporter', 'reported_user').order_by('-created_at')[:5]
    recent_feedbacks = Feedback.objects.select_related('user').order_by('-created_at')[:5]
    
    return render(request, 'snap_settings/admin_dashboard.html', {
        'reports_pending': reports_pending,
        'feedbacks_count': feedbacks_count,
        'banned_users': banned_users,
        'recent_reports': recent_reports,
        'recent_feedbacks': recent_feedbacks
    })

@user_passes_test(is_admin)
def admin_reports(request):
    filter_status = request.GET.get('status', 'pending')
    if filter_status == 'resolved':
        reports = Report.objects.filter(resolved=True)
    elif filter_status == 'all':
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(resolved=False)
        
    reports = reports.select_related('reporter', 'reported_user').order_by('-created_at')
    return render(request, 'snap_settings/admin_reports.html', {'reports': reports, 'filter_status': filter_status})

@user_passes_test(is_admin)
def admin_feedbacks(request):
    feedbacks = Feedback.objects.select_related('user').order_by('-created_at')
    return render(request, 'snap_settings/admin_feedbacks.html', {'feedbacks': feedbacks})

@user_passes_test(is_admin)
def admin_resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.resolved = True
    report.save()
    messages.success(request, f"Report {report.id} resolved.")
    return redirect('snap_settings:admin_reports')

@user_passes_test(is_admin)
def admin_warn_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        reason = request.POST.get('reason', 'Violation of terms.')
        snapit_admin = User.objects.get(username='Snapit')
        
        # Determine or create conversation between Snapit and the user
        conv = Conversation.objects.filter(participants=snapit_admin).filter(participants=user).first()
        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(snapit_admin, user)
            
        warning_text = f"⚠️ OFFICIAL WARNING\n\nYou have received a warning for the following reason:\n{reason}\n\nPlease adhere to the community guidelines to avoid account suspension."
        Message.objects.create(conversation=conv, sender=snapit_admin, content=warning_text)
        conv.save()
        
        messages.success(request, f"Warning sent to {user.username}.")
        # Optional: Resolve associated report if passed
        report_id = request.POST.get('report_id')
        if report_id:
            try:
                r = Report.objects.get(id=report_id)
                r.resolved = True
                r.save()
            except Report.DoesNotExist:
                pass
                
    return redirect(request.META.get('HTTP_REFERER', 'snap_settings:admin_reports'))

@user_passes_test(is_admin)
def admin_ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser or user.username == 'Snapit':
        messages.error(request, "Cannot ban an administrator.")
        return redirect(request.META.get('HTTP_REFERER', 'snap_settings:admin_reports'))
        
    user.is_active = False
    user.save()
    
    # Record the ban for the 14-day deletion cycle
    BannedUser.objects.get_or_create(user=user, defaults={'reason': 'Banned via admin portal'})
    
    messages.success(request, f"User {user.username} has been deactivated and scheduled for deletion in 14 days.")
    
    # Auto-resolve related reports
    Report.objects.filter(reported_user=user, resolved=False).update(resolved=True)
    
    return redirect(request.META.get('HTTP_REFERER', 'snap_settings:admin_reports'))
