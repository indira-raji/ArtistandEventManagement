from django.db import models

# =======================
# User Account
# =======================
class UserAccount(models.Model):
    USER_TYPES = (
        ('user', 'User'),
        ('artist', 'Artist'),
        ('event', 'Event Management')
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    usertype = models.CharField(max_length=20, choices=USER_TYPES)

    def __str__(self):
        return self.name


# =======================
# Artist Card
# =======================
class Artistcard(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    query = models.CharField(max_length=50, blank=True)  # Optional

    def __str__(self):
        return self.title


# =======================
# Event Category
# =======================
class EventCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =======================
# Event Type
# =======================
class EventType(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        related_name="events"
    )

    def __str__(self):
        return self.title


# =======================
# Event Management
# =======================
class EventManagement(models.Model):
    user = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status = models.CharField(
    max_length=20,
    choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')],
    default='pending'
)
    team_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    social_link = models.URLField(blank=True, null=True)
    experience = models.PositiveIntegerField(default=0)
    languages = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to="event_management/logos/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name


# =======================
# Event Service
# =======================
class EventService(models.Model):
    company = models.ForeignKey(
        EventManagement,
        on_delete=models.CASCADE,
        related_name="services"
    )
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,  # Safe if event_type deleted
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.company.team_name} - {self.event_type.title if self.event_type else 'N/A'}"


# =======================
# Event Package
# =======================
class EventPackage(models.Model):
    service = models.ForeignKey(
        EventService,
        on_delete=models.CASCADE,
        related_name="packages"
    )
    PACKAGE_CHOICES = [
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Diamond', 'Diamond'),
    ]
    package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES,default='Silver' ) 
    package_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE ,default=1)  
    image = models.ImageField(upload_to="event_packages/", blank=True, null=True)

    def __str__(self):
        return f"{self.package_name} - {self.service.event_type.title if self.service.event_type else 'N/A'}"


# =======================
# Event Portfolio
# =======================
class EventPortfolio(models.Model):
    company = models.ForeignKey(
        EventManagement,
        on_delete=models.CASCADE,
        related_name="portfolio"
    )
    image = models.ImageField(upload_to="event_portfolio/")
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.company.team_name} Portfolio"

class Artist(models.Model):

    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
    max_length=20,
    choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')],
    default='pending'
)
    full_name = models.CharField(max_length=150)
    stage_name = models.CharField(max_length=150)

    email = models.EmailField()
    phone = models.CharField(max_length=15)

    artist_type = models.CharField(max_length=100)

    languages = models.CharField(max_length=200)

    experience = models.PositiveIntegerField()
    previous_events = models.PositiveIntegerField()

    skills = models.TextField()

    price_start = models.DecimalField(max_digits=10, decimal_places=2)
    price_end = models.DecimalField(max_digits=10, decimal_places=2)

    travel_charge = models.DecimalField(max_digits=10, decimal_places=2)

    available_city = models.CharField(max_length=200)

    available_days = models.CharField(max_length=50)
    location = models.CharField(max_length=200,default="location")
    time_start = models.TimeField()
    time_end = models.TimeField()

    bio = models.TextField()

    profile_image = models.ImageField(upload_to="artists/profile/")

    social_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stage_name

class ArtistPortfolio(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="portfolio")

    image = models.ImageField(upload_to="artists/portfolio/")

    def __str__(self):
        return self.artist.stage_name

class ArtistBooking(models.Model):

    STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
)
    
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    customer_phone = models.CharField(max_length=15,default="None")
    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    location = models.CharField(max_length=200,default="location")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.artist.stage_name}"
    
class EventBooking(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
   

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    customer_phone = models.CharField(max_length=15,default="None")
    company = models.ForeignKey(EventManagement, on_delete=models.CASCADE)
    location = models.CharField(max_length=200,default="location")

    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)

    event_date = models.DateField()

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.company.team_name}"







class Payment(models.Model):

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    booking = models.ForeignKey(
        "ArtistBooking",
        on_delete=models.CASCADE
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending','Pending'),
            ('paid','Paid')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.amount}"
    
# =======================
# Company Event Packages
# =======================

class CompanyEvent(models.Model):

    company = models.ForeignKey(
        EventManagement,
        on_delete=models.CASCADE,
        related_name="company_events"
    )

    event_name = models.CharField(max_length=200)

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE
    )

    location = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    silver_price = models.DecimalField(max_digits=10, decimal_places=2)

    gold_price = models.DecimalField(max_digits=10, decimal_places=2)

    platinum_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name
