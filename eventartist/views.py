from django.shortcuts import render, redirect
from .models import UserAccount
from .models import Artistcard
from .models import EventCategory,ArtistBooking,EventBooking,Payment,EventPortfolio,Artist,CompanyEvent
from .forms import EventManagementForm
from .models import EventType, EventService,EventManagement,EventPackage,ArtistPortfolio
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from decimal import Decimal
from secrets import compare_digest

COMMISSION_RATE = Decimal("0.10")

def signup(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        repassword = request.POST.get("repassword")
        usertype = request.POST.get("usertype")

        # Password match validation
        if password != repassword:
            return render(request,"signup.html",{"error":"Passwords do not match"})

        try:
            validate_password(password)
        except ValidationError as error:
            return render(request, "signup.html", {"error": " ".join(error.messages)})

        # Email already exists
        if UserAccount.objects.filter(email=email).exists():
            return render(request,"signup.html",{"error":"Email already registered"})

        # Save data
        UserAccount.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            usertype=usertype
        )

        return redirect("login")

    return render(request,"signup.html")# Create your views here.



def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        # Superuser check
        try:
            django_user = User.objects.get(email=email)

            user = authenticate(request, username=django_user.username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                return redirect("admin-dashboard")

        except User.DoesNotExist:
            pass


        # Normal users
        try:
            user = UserAccount.objects.get(email=email)

            password_matches = check_password(password, user.password)
            if not password_matches and compare_digest(password, user.password):
                # Existing records used plain-text passwords. Upgrade each
                # account only after its owner has authenticated successfully.
                user.password = make_password(password)
                user.save(update_fields=["password"])
                password_matches = True

            if not password_matches:
                raise UserAccount.DoesNotExist

            request.session["user_id"] = user.id
            request.session["user_type"] = user.usertype

            # ✅ Always go to home
            return redirect("home")

        except UserAccount.DoesNotExist:

            return render(request, "login.html", {"error": "Invalid Email or Password"})


    return render(request, "login.html")

def profile_redirect(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    if user.usertype == "artist":
        return redirect("artist_dashboard")

    elif user.usertype == "event":
        return redirect("event_dashboard")

    else:
        return redirect("user-dashboard")
def Home(request):
    """
    Home page view.
    Renders the main sections: events, artists, about, contact.
    """
    artists = Artistcard.objects.all()
    categories = EventCategory.objects.prefetch_related('events').all()
    return render(request, 'home/home.html', {"artists": artists,"categories": categories})


def artistview(request):
    artists = Artistcard.objects.all()   # get all records from sqlite///
    return render(request, "home/artisthome.html", {"artists": artists})


def eventview(request):
    categories = EventCategory.objects.prefetch_related('events').all()
    return render(request, "home/eventhome.html", {"categories": categories})



def event_management_register(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # not logged in

    user = UserAccount.objects.get(id=user_id)

    # Check if EventManagement already exists for this user
    if EventManagement.objects.filter(user=user).exists():
        messages.info(request, "You have already registered your company.")
        return redirect("user-dashboard")  # redirect to home/dashboard

    # If not exists, create a new instance
    company, created = EventManagement.objects.get_or_create(user=user)
    is_edit = not created

    event_types = EventType.objects.all()

    if request.method == "POST":
        form = EventManagementForm(request.POST, request.FILES, instance=company)

        if form.is_valid():
            company = form.save(commit=False)
            company.user = user
            company.save()

            # Remove old EventService and save new selections
            EventService.objects.filter(company=company).delete()
            selected_events = request.POST.getlist("event_types")
            for event_id in selected_events:
                event_type = EventType.objects.get(id=event_id)
                EventService.objects.create(company=company, event_type=event_type)

            messages.success(request, "Event Management Registration Successful!")
            return redirect("user-dashboard")

    else:
        form = EventManagementForm(instance=company)

    return render(request, "event/event_register.html", {
        "form": form,
        "event_types": event_types,
        "is_edit": is_edit
    })
def user_logout(request):
    logout(request)
    return redirect("login")   # redirect to login page

def event_packages_view(request):
    # Default event type name
    default_event_name = 'Event'

    # Get selected event from GET params or use default
    selected_event_name = request.GET.get('event_type', default_event_name)

    # Get Category object (assuming EventType model is actually Category)
    try:
        selected_category = EventType.objects.get(title=selected_event_name)
    except EventType.DoesNotExist:
        selected_category = None

    # Filter packages by package_type and selected category
    if selected_category:
        silver_packages = EventPackage.objects.filter(
        package_type='Silver',
        event_type=selected_category
        )

        gold_packages = EventPackage.objects.filter(
        package_type='Gold',
        event_type=selected_category
        )

        diamond_packages = EventPackage.objects.filter(
        package_type='Diamond',
        event_type=selected_category
        )
    else:
        silver_packages = EventPackage.objects.none()
        gold_packages = EventPackage.objects.none()
        diamond_packages = EventPackage.objects.none()

    package_groups = [
        ('Silver', silver_packages),
        ('Gold', gold_packages),
        ('Diamond', diamond_packages),
    ]

    context = {
        'event_types': EventType.objects.all(),
        'selected_event': selected_event_name,
        'package_groups': package_groups,
    }

    return render(request, 'event/eventandpackage.html', context)

def package_detail(request, id):
    package = EventPackage.objects.get(id=id)
    return render(request, "event/eventandpackage.html", {"package": package})


def artist_register(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)
    artist_types = Artistcard.objects.all()
    # ✅ Check if artist already registered
    if Artist.objects.filter(user=user).exists():
        messages.info(request, "You have already registered as an artist.")
        return redirect("artist_dashboard")

    if request.method == "POST":

        artist = Artist.objects.create(
            user=user,
            full_name=request.POST.get("full_name"),
            stage_name=request.POST.get("stage_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            artist_type=request.POST.get("artist_type"),
            languages=request.POST.get("languages"),
            experience=request.POST.get("experience"),
            previous_events=request.POST.get("previous_events"),
            skills=request.POST.get("skills"),
            price_start=request.POST.get("price_start"),
            price_end=request.POST.get("price_end"),
            travel_charge=request.POST.get("travel_charge"),
            available_city=request.POST.get("available_city"),
            available_days=request.POST.get("available_days"),
            time_start=request.POST.get("time_start"),
            time_end=request.POST.get("time_end"),
            bio=request.POST.get("bio"),
            profile_image=request.FILES.get("profile_image"),
            social_link=request.POST.get("social_link"),
        )

        # Portfolio images
        images = request.FILES.getlist("portfolio")

        for img in images:
            ArtistPortfolio.objects.create(
                artist=artist,
                image=img
            )

        messages.success(request, "Artist Registered Successfully!")

        return redirect("artist_dashboard")

    return render(request, "artist/artist_register.html",{"artist_types": artist_types})

def admin_dashboard(request):

    artist_count = Artist.objects.filter(status="approved").count()

    user_count = UserAccount.objects.filter(usertype="user").count()

    event_count = EventManagement.objects.filter(status="approved").count()

    bookings = ArtistBooking.objects.count() + EventBooking.objects.count()

    revenue = Decimal("0")

    artist_bookings = ArtistBooking.objects.filter(status="confirmed")
    event_bookings = EventBooking.objects.filter(status="confirmed")

    for b in artist_bookings:
        revenue += b.amount * COMMISSION_RATE

    for b in event_bookings:
        revenue += b.amount * COMMISSION_RATE

    context = {
        "artist_count": artist_count,
        "user_count": user_count,
        "event_count": event_count,
        "bookings": bookings,
        "revenue": revenue
    }

    return render(request,"admin/dashboard.html",context)
def admin_artists(request):

    pending_artists = Artist.objects.filter(status="pending")
    approved_artists = Artist.objects.filter(status="approved")
    rejected_artists = Artist.objects.filter(status="rejected")
    context = {
        "pending_artists": pending_artists,
        "approved_artists": approved_artists,
        "rejected_artists": rejected_artists
    }

    return render(request,"admin/artists.html",context)

def approve_artist(request,id):

    artist = Artist.objects.get(id=id)

    artist.status = "approved"

    artist.save()

    return redirect("admin-artists")
def reject_artist(request,id):

    artist = Artist.objects.get(id=id)

    artist.status = "rejected"

    artist.save()

    return redirect("admin-artists")

def admin_events(request):

    pending_events = EventManagement.objects.filter(status="pending")

    approved_events = EventManagement.objects.filter(status="approved")
    rejected_events= EventManagement.objects.filter(status="rejected")


    return render(request,"admin/events.html",{
        "pending_events":pending_events,
        "approved_events":approved_events,
        "rejected_events":rejected_events

    })
def approve_event(request,id):

    event = EventManagement.objects.get(id=id)
    event.status = "approved"
    event.save()

    return redirect("admin-events")


def reject_event(request,id):

    event = EventManagement.objects.get(id=id)
    event.status = "rejected"
    event.save()

    return redirect("admin-events")
def event_details(request, id):

    event = EventManagement.objects.get(id=id)

    return render(request, "admin/event_registration_details.html", {
        "event": event
    })


def artist_booking_history(request):

    bookings = ArtistBooking.objects.select_related("artist","user")

    return render(request,"admin/artist booking history.html",{
        "bookings":bookings
    })

def event_booking_history(request):

    bookings = EventBooking.objects.select_related(
        "user",
        "company",
        "event_type"
    ).all().order_by("-created_at")

    return render(request,"admin/event booking history.html",{
        "bookings":bookings
    })

def admin_revenue(request):

    artist_bookings = ArtistBooking.objects.filter(status="confirmed")

    event_bookings = EventBooking.objects.filter(status="confirmed")

    total_revenue = Decimal("0")

    for b in artist_bookings:
        total_revenue += b.amount * COMMISSION_RATE

    for b in event_bookings:
        total_revenue += b.amount * COMMISSION_RATE

    return render(request,"admin/revenue.html",{
        "revenue":total_revenue
    })


@login_required
def admin_settings(request):

    admin = request.user

    if request.method == "POST":

        admin.username = request.POST.get("name")

        password = request.POST.get("password")

        if password:
            admin.set_password(password)
            admin.save()

        messages.success(request,"Profile updated")

    return render(request,"admin/settings.html",{
        "admin":admin
    })



def artist_dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist = Artist.objects.filter(user=user).first()

    if not artist:
        return redirect("artist-register")

    # Status check first
    if artist.status == "pending":
        return render(request, "artist/waiting.html", {"artist": artist})

    if artist.status == "rejected":
        return render(request, "artist/rejected.html", {"artist": artist})

    # Approved artist
    bookings = ArtistBooking.objects.filter(artist=artist)

    total_bookings = bookings.count()

    upcoming_events = bookings.filter(status="confirmed").count()

    total_earnings = bookings.filter(
        status="completed"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    context = {
        "artist": artist,
        "bookings": bookings,
        "total_bookings": total_bookings,
        "upcoming_events": upcoming_events,
        "total_earnings": total_earnings
    }

    return render(request, "artist/artist_dashboard.html", context)


def artist_profile(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist = Artist.objects.get(user=user)

    if artist.status != "approved":
        messages.error(request,"Wait for admin approval")
        return redirect("artist_dashboard")

    if request.method == "POST":

        artist.full_name = request.POST.get("full_name")
        artist.stage_name = request.POST.get("stage_name")
        artist.phone = request.POST.get("phone")
        artist.email = request.POST.get("email")
        artist.available_days = request.POST.get("available_days")

        artist.save()

        messages.success(request,"Profile updated")


    return render(request,"artist/profile.html",{
    "artist":artist,
    
})     
def upload_portfolio(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)
    artist = Artist.objects.get(user=user)

    if request.method == "POST":

        files = request.FILES.getlist("images")

        for file in files:
            ArtistPortfolio.objects.create(
                artist=artist,
                image=file
            )

    portfolio = ArtistPortfolio.objects.filter(artist=artist)

    return render(request,"artist/portfolio.html",{
        "artist":artist,
        "portfolio":portfolio
    })
    

def delete_artist_portfolio(request,id):

    portfolio = ArtistPortfolio.objects.get(id=id)
    portfolio.delete()

    return redirect("upload_portfolio")

def artist_bookings(request):

    user_id = request.session.get("user_id")
    user = UserAccount.objects.get(id=user_id)
    artist = Artist.objects.get(user=user)

    bookings = ArtistBooking.objects.filter(artist=artist)

    return render(request,"artist/bookings.html",{"bookings":bookings})
def accept_booking(request,id):

    user_id = request.session.get("user_id")
    user = UserAccount.objects.get(id=user_id)

    artist = Artist.objects.get(user=user)
    
    booking = ArtistBooking.objects.get(id=id, artist=artist)

    booking.status = "confirmed"
    booking.save()

    return redirect("artist_bookings_users")

def reject_booking(request,id):

    user_id = request.session.get("user_id")
    user = UserAccount.objects.get(id=user_id)

    artist = Artist.objects.get(user=user)

    booking = ArtistBooking.objects.get(id=id, artist=artist)

    booking.status = "rejected"
    booking.save()

    return redirect("artist_bookings_users")

def artist_payments(request):

    user_id = request.session.get("user_id")
    user = UserAccount.objects.get(id=user_id)
    artist = Artist.objects.get(user=user)

    payments = Payment.objects.filter(artist=artist)

    return render(request,"artist/payment.html",{"payments":payments})


def booking_history(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist = Artist.objects.get(user=user)

    accepted = ArtistBooking.objects.filter(
        artist=artist,
        status="confirmed"
    )

    rejected = ArtistBooking.objects.filter(
        artist=artist,
        status="rejected"
    )

    completed = ArtistBooking.objects.filter(
        artist=artist,
        status="completed"
    )

    context = {
        "accepted": accepted,
        "rejected": rejected,
        "completed": completed
    }

    return render(request, "artist/booking_history.html", context)


def user_dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist_bookings = ArtistBooking.objects.filter(user=user)
    event_bookings = EventBooking.objects.filter(user=user)

    total_bookings = artist_bookings.count() + event_bookings.count()

    
    pending = artist_bookings.filter(status="pending").count() + event_bookings.filter(status="pending").count()

    confirmed = artist_bookings.filter(status="confirmed").count() + event_bookings.filter(status="confirmed").count()

    payments = Payment.objects.filter(user=user)

    total_payment = sum(p.amount for p in payments)

    context = {

        "user":user,
        "artist_bookings":artist_bookings,
        "event_bookings":event_bookings,
        "payments":payments,

        "total_bookings":total_bookings,
        "pending":pending,
        "confirmed":confirmed,
        "total_payment":total_payment

    }

    return render(request,"user/user_dashboard.html",context)

def user_booking_history(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist_history = ArtistBooking.objects.filter(user=user).order_by("-id")

    event_history = EventBooking.objects.filter(user=user).order_by("-id")

    context = {
        "artist_history": artist_history,
        "event_history": event_history
    }

    return render(request, "user/history.html", context)


def event_dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    company = EventManagement.objects.get(user=user)

    bookings = EventBooking.objects.filter(company=company)

    total_bookings = bookings.count()

    pending = bookings.filter(status="pending").count()

    confirmed = bookings.filter(status="confirmed").count()

    completed = bookings.filter(status="completed").count()

    revenue = bookings.filter(
        status="completed"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    total_events = CompanyEvent.objects.filter(company=company).count()

    return render(request,"event/dashboard.html",{

        "company":company,
        "total_bookings":total_bookings,
        "pending":pending,
        "confirmed":confirmed,
        "completed":completed,
        "revenue":revenue,
        "total_events":total_events

    })

def event_profile(request):

    user_id = request.session.get("user_id")

    user = UserAccount.objects.get(id=user_id)

    company = EventManagement.objects.get(user=user)

    if request.method == "POST":

        company.team_name = request.POST.get("team_name")

        company.owner_name = request.POST.get("owner_name")

        company.email = request.POST.get("email")

        company.phone = request.POST.get("phone")

        company.save()

        messages.success(request,"Profile Updated")

        return redirect("event_profile")

    return render(request,"event/profile.html",{"company":company})

def event_portfolio(request):

    user_id = request.session.get("user_id")

    user = UserAccount.objects.get(id=user_id)

    company = EventManagement.objects.get(user=user)

    if request.method == "POST":

        images = request.FILES.getlist("images")

        for img in images:

            EventPortfolio.objects.create(
                company=company,
                image=img
            )

    portfolio = EventPortfolio.objects.filter(company=company)

    return render(request,"event/portfolio.html",{
        "portfolio":portfolio
    })

def delete_event_portfolio(request,id):

    portfolio = EventPortfolio.objects.get(id=id)

    portfolio.delete()

    return redirect("event_portfolio")

def add_event(request):

    user = UserAccount.objects.get(id=request.session["user_id"])

    company = EventManagement.objects.get(user=user)

    if request.method == "POST":

        CompanyEvent.objects.create(

            company=company,

            event_name=request.POST.get("event_name"),

            event_type_id=request.POST.get("event_type"),

            location=request.POST.get("location"),

            description=request.POST.get("description"),

            silver_price=request.POST.get("silver_price"),

            gold_price=request.POST.get("gold_price"),

            platinum_price=request.POST.get("platinum_price")

        )

        return redirect("manage_events")

def manage_events(request):

    user = UserAccount.objects.get(id=request.session["user_id"])

    company = EventManagement.objects.get(user=user)

    events = CompanyEvent.objects.filter(company=company)

    event_types = EventType.objects.all()

    return render(request,"event/manage_events.html",{

        "events":events,
        "event_types":event_types

    })

def delete_event(request,id):

    event = CompanyEvent.objects.get(id=id)

    event.delete()

    return redirect("manage_events")

def booking_requests(request):

    user = UserAccount.objects.get(id=request.session["user_id"])

    company = EventManagement.objects.get(user=user)

    bookings = EventBooking.objects.filter(company=company)

    return render(request,"event/booking_requests.html",{
        "bookings":bookings
    })

def approve_booking(request,id):

    booking = EventBooking.objects.get(id=id)

    booking.status="confirmed"

    booking.save()

    return redirect("booking_requests")

def reject_booking(request,id):

    booking = EventBooking.objects.get(id=id)

    booking.status="rejected"

    booking.save()

    return redirect("booking_requests")


def my_bookings(request):

    user = UserAccount.objects.get(id=request.session["user_id"])

    artist_bookings = ArtistBooking.objects.filter(user=user)

    event_bookings = EventBooking.objects.filter(user=user)

    return render(request,"event/my_bookings.html",{

        "artist_bookings":artist_bookings,

        "event_bookings":event_bookings

    })

def event_payments(request):

    user = UserAccount.objects.get(id=request.session["user_id"])

    company = EventManagement.objects.get(user=user)

    payments = EventBooking.objects.filter(
        company=company,
        status="completed"
    )

    total = payments.aggregate(Sum("amount"))["amount__sum"] or 0

    return render(request,"event/payments.html",{

        "payments":payments,
        "total":total

    })
def user_payments(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    artist_payments = Payment.objects.filter(user=user)

    event_bookings = EventBooking.objects.filter(
        user=user,
        status="confirmed"
    )

    context = {
        "artist_payments": artist_payments,
        "event_bookings": event_bookings
    }

    return render(request,"user/payments.html",context)
def user_profile(request):


    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = UserAccount.objects.get(id=user_id)

    if request.method == "POST":

        user.name = request.POST.get("name")
        user.email = request.POST.get("email")

        password = request.POST.get("password")

        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                messages.error(request, " ".join(error.messages))
                return render(request, "user/profile.html", {"user": user})
            user.password = make_password(password)

        user.save()

        messages.success(request,"Profile updated successfully")

    return render(request,"user/profile.html",{"user":user})

def user_artist_detail(request, id):

    artist = get_object_or_404(Artist, id=id)

    portfolio = artist.portfolio.all()

    return render(request, "home/artist_detail.html", {
        "artist": artist,
        "portfolio": portfolio
    })

def artist_by_type(request, type):

    card = Artistcard.objects.filter(title=type).first()

    artists = Artist.objects.filter(artist_type=type, status="approved")

    context = {
        "card": card,
        "artists": artists,
        "type": type
    }

    return render(request, "home/artistlist.html", context)
def book_artist(request, id):

    artist = get_object_or_404(Artist, id=id)

    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        event_name = request.POST.get("event_name")
        event_date = request.POST.get("event_date")
        location = request.POST.get("location")
        amount = request.POST.get("amount")

        user_id = request.session.get("user_id")

        ArtistBooking.objects.create(
            user_id=user_id,
            artist=artist,
            customer_phone=phone,
            event_name=event_name,
            event_date=event_date,
            location=location,
            amount=amount
        )

        return redirect("user-booking-history")

    return render(request,"user/book_artist.html",{"artist":artist})
def admin_artist_details(request, id):

    artist = get_object_or_404(Artist, id=id)

    return render(request, 'admin/artist_registration_details.html', {
        'artist': artist
    })
def admin_event_details(request, id):
    
    event = get_object_or_404(EventManagement, id=id)

    return render(request, 'admin/event_registration_details.html', {
        'event': event
    })
