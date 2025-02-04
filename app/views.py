"""
Definition of views.
"""

from datetime import datetime
from django.db.models import Q
from django.http import HttpRequest
from .models import RankChangeRequests, RegionChangeRequests, Users
from django.http import HttpRequest
from .models import Reports, EvidentImages, EvidentVideos
from django.utils.timezone import now
from collections import Counter
from django.http import HttpRequest
from django.contrib import messages
from .models import FeedBack
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import CaseReports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CaseReports
from django.http import HttpResponse
from django.contrib import messages
from .models import RankChangeRequests, RegionChangeRequests, Users
from app import models

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Admin-specific login check
        if username == "admin" and password == "@admin":
            return redirect("reports")
        
        # User login check (lower and upper ranks)
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user's rank
                if user.profile.rank in ['Constable', 'Sub-Inspector', 'Inspector']:
                    return redirect('view_reports')
                elif user.profile.rank in ['Superintendent', 'Director General']:
                    return redirect('view_reports1')
            else:
                messages.error(request, "Invalid username or password")
    
    return render(request, 'app/login.html')  # Render the login page for GET requests

def assign_report_form(request, report_id):
    report = get_object_or_404(Reports, id=report_id)

    # Get lower-ranked users in the same location
    eligible_users = Users.objects.filter(
        rank__in=["Constable", "Sub-Inspector", "Inspector"],
        state=request.user.state,
        city=request.user.city,
        station=request.user.station
    ).annotate(case_count=models.Count('reports'))

    if request.method == "POST":
        assigned_user_id = request.POST.get("assigned_user")
        assigned_user = get_object_or_404(Users, id=assigned_user_id)

        # Update the report with the selected user
        report.assignedpoliceid = assigned_user.id
        report.save()

        return redirect('view_reports1')  # Redirect back to the reports page

    return render(request, 'Assign_Cases.html', {
        'report': report,
        'eligible_users': eligible_users,
    })


def regional_reports_view(request):
    # Get the reports for the user's region
    user_region = request.user.state  # Assuming user's state is stored in the state attribute
    reports = Reports.objects.filter(regionname=user_region)

    return render(request, 'app/view_reports.html', {
        'reports': reports,
    })

def update_status_request(request):
    """Handles the logic for submitting rank and region change requests."""
    if request.method == 'POST':
        update_type = request.POST.get('update_type')

        if update_type == 'rank':
            current_rank = request.POST.get('current_rank')
            update_rank = request.POST.get('update_rank')

            # Save rank change request
            RankChangeRequests.objects.create(
                userid=request.user.id,
                name=request.user.username,
                policeid=request.user.policeid,
                currentrank=current_rank,
                updaterank=update_rank,
                confirmation='pending'
            )

        elif update_type == 'region':
            current_state = request.POST.get('current_state')
            current_city = request.POST.get('current_city')
            current_station = request.POST.get('current_station')
            update_state = request.POST.get('update_state')
            update_city = request.POST.get('update_city')
            update_station = request.POST.get('update_station')

            # Save region change request
            RegionChangeRequests.objects.create(
                userid=request.user.id,
                name=request.user.username,
                policeid=request.user.policeid,
                currentlocation=f"{current_state}, {current_city}, {current_station}",
                updatelocation=f"{update_state}, {update_city}, {update_station}",
                confirmation1='pending',
                confirmation2='pending'
            )

        return redirect('profile')  # Redirect back to profile page after submission

    # Prepopulate the current state and rank for the logged-in user
    context = {
        'current_rank': request.user.rank,
        'current_state': request.user.state,
        'current_city': request.user.city,
        'current_station': request.user.station,
    }
    return render(request, 'app/update_status_request.html', context)

def update_case(request, case_id):
    case = get_object_or_404(CaseReports, id=case_id)

    if request.method == 'POST':
        case.state = request.POST.get('state')
        case.city = request.POST.get('city')
        case.station = request.POST.get('station')
        case.suspects = request.POST.get('suspects')
        case.culprit = request.POST.get('culprit')
        case.casedescription = request.POST.get('case_description')
        case.save()
        return HttpResponseRedirect(reverse('assigned_cases'))  # Redirect to the cases page

    return render(request, 'update_assigned_case.html', {'case': case})


@login_required
def manage_assigned_cases(request):
    # Fetch untaken and taken cases
    user_id = request.user.id
    untaken_cases = Reports.objects.filter(assignedpoliceid=user_id, assignedpoliceid__endswith='').all()
    taken_cases = Reports.objects.filter(assignedpoliceid__startswith=str(user_id), assignedpoliceid__endswith=',taken').all()

    context = {
        'untaken_cases': untaken_cases,
        'taken_cases': taken_cases,
    }
    return render(request, 'assigned_cases.html', context)


@login_required
def take_case(request):
    if request.method == "POST":
        report_id = request.POST.get("report_id")
        report = get_object_or_404(Reports, id=report_id)

        # Update report's AssignedPoliceId
        report.assignedpoliceid = f"{request.user.id},taken"
        report.save()

        # Fetch user's details for city and station
        user = request.user
        city = user.city
        station = user.station

        # Query for Chief Officer
        chief_officer = Users.objects.filter(
            state=user.state, 
            city=city, 
            station=station, 
            rank__in=["Superintendent", "Director General"]
        ).first()

        # Insert into CaseReports
        CaseReports.objects.create(
            reportid=report.id,
            state=user.state,  # State from user
            city=city,         # City from user
            station=station,   # Station from user
            suspects="",       # Empty for now
            culprit="",        # Empty for now
            casedescription=report.description,
            officer=user.username,
            chiefofficer=chief_officer.username if chief_officer else None,  # Use Chief Officer username
        )
        return redirect("assigned_cases")
    return HttpResponse(status=400)



@login_required
def update_case(request, report_id):
    # Pass report_id to the update form
    return render(request, "app/update_case.html", {"report_id": report_id})

def view_assigned_reports(request):
    """Retrieve and display reports assigned to the logged-in user."""
    user_id = request.user.id  # Assuming the logged-in user's ID matches the `AssignedPoliceId`
    assigned_reports = Reports.objects.filter(assignedpoliceid=user_id)
    return render(request, 'view_assigned_reports.html', {'assigned_reports': assigned_reports})

def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Admin check before authentication
        if username == "admin" and password == "@admin":
            return redirect("app/Reports.html")  # Use the URL name for the admin reports page

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Fetch user rank
            try:
                user_data = Users.objects.get(username=user.username)
                rank = user_data.rank

                # Redirect based on rank
                if rank in ["Constable", "Sub-Inspector", "Inspector"]:
                    return redirect("app/view_reports.html")
                elif rank in ["Superintendent", "Director General"]:
                    return redirect("app/view_reports1.html")
                else:
                    # Undefined rank or unhandled cases
                    return render(request, "app/login.html", {"error": "Access not permitted."})
            except Users.DoesNotExist:
                return render(request, "app/login.html", {"error": "User data not found."})
        else:
            return render(request, "app/login.html", {"error": "Invalid username or password."})

    return render(request, "app/login.html")


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def report_crime(request):
    """Handles crime reporting."""
    if request.method == 'POST':
        region = request.POST.get('region')
        crime_type = request.POST.get('crime_type')
        description = request.POST.get('description')
        report_date = now()  # Automatically captures the current date and time
        uploaded_file = request.FILES.get('file_content')

        # Save the report to the database
        report = Reports.objects.create(
            regionname=region,
            crimetype=crime_type,
            description=description,
            reportdate=report_date
        )

        # Analyze the uploaded file and save in the respective model
        if uploaded_file:
            if uploaded_file.content_type.startswith('image/'):
                EvidentImages.objects.create(image=uploaded_file, cid=report)
            elif uploaded_file.content_type.startswith('video/'):
                EvidentVideos.objects.create(video=uploaded_file, cid=report)

        return redirect('home')  # Redirect after successful submission

    return render(request, 'app/Report.html', {'current_date': now()})

def admin_reports(request):
    """View for displaying reports and chart."""
    # Fetch all reports from the database
    reports = Reports.objects.all()

    # Prepare data for the chart
    crime_types = [report.crimetype for report in reports if report.crimetype]
    crime_type_counts = Counter(crime_types)  # Count occurrences of each crime type

    chart_data = {
        'labels': list(crime_type_counts.keys()),  # Crime types
        'data': list(crime_type_counts.values())  # Their respective counts
    }

    # Pass the data to the template
    context = {
        'reports': reports,
        'chart_data': chart_data
    }
    return render(request, 'app/Reports.html', context)

def admin_users(request):
    """Renders the users list page."""
    users = Users.objects.all()  # Fetch all users from the database
    return render(request, 'app/Users.html', {'users': users})

def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        police_id = request.POST.get("police_id")
        rank = request.POST.get("rank")
        state = request.POST.get("state")
        city = request.POST.get("city")
        station = request.POST.get("station")

        # Validation
        if Users.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif Users.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            # Create a new user
            user = Users.objects.create(
                username=username,
                password=password,  # Add hashing if required
                email=email,
                policeid=police_id,
                rank=rank,
                state=state,
                city=city,
                station=station,
            )
            user.save()
            messages.success(request, "User added successfully!")
            return redirect("admin_users")  # Redirect to the Users list page

    return render(request, "app/add_user.html")

def manage_requests(request):
    rank_requests = RankChangeRequests.objects.filter(confirmation__in=["Pending", "Approved"])
    region_requests = RegionChangeRequests.objects.filter(
        (Q(confirmation1="Pending") | Q(confirmation2="Pending")) | 
        (Q(confirmation1="Approved") & Q(confirmation2="Approved"))
    )
    return render(request, 'app/manage_requests.html', {
        'rank_requests': rank_requests,
        'region_requests': region_requests,
    })


def process_rank_request(request):
    """Processes a rank change request and updates the Users table."""
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        try:
            rank_request = RankChangeRequests.objects.get(id=request_id)
            user = Users.objects.get(id=rank_request.userid)
            # Update user's rank
            user.rank = rank_request.updaterank
            user.save()
            # Mark request as processed
            rank_request.confirmation = "Approved"
            rank_request.save()
        except (RankChangeRequests.DoesNotExist, Users.DoesNotExist):
            pass
    return redirect('app/Status Change Requests.html')

def process_region_request(request):
    """Processes a region change request and updates the Users table."""
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        try:
            region_request = RegionChangeRequests.objects.get(id=request_id)
            user = Users.objects.get(id=region_request.userid)
            # Update user's region
            user.state = region_request.updatelocation
            user.save()
            # Mark request as processed
            region_request.confirmation1 = "Approved"
            region_request.save()
        except (RegionChangeRequests.DoesNotExist, Users.DoesNotExist):
            pass
    return redirect('manage_requests')

def feedback_view(request):
    feedback_list = FeedBack.objects.all()
    return render(request, 'app/feedback_view.html', {'feedback_list': feedback_list})

def process_feedback(request):
    if request.method == "POST":
        # Retrieve form data
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Save feedback to the database
        feedback = FeedBack.objects.create(
            name=name,
            email=email,
            message=message
        )
        feedback.save()

        # Add a success message
        messages.success(request, "Your feedback has been submitted successfully!")

        # Redirect to a confirmation or thank-you page
        return redirect("home")

    # If the request is not POST, render the feedback form
    return render(request, "app/contact.html")

