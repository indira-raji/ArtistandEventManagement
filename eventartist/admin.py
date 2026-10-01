from django.contrib import admin
from .models import (
    UserAccount,
    Artistcard,
    EventCategory,
    EventType,
    EventManagement,
    EventService,
    EventPackage,
    EventPortfolio,
    Artist,
    ArtistPortfolio,
    ArtistBooking,
    EventBooking,
    Payment,
    CompanyEvent
)

# ===============================
# Basic Models
# ===============================

admin.site.register(UserAccount)
admin.site.register(Artistcard)
admin.site.register(EventCategory)
admin.site.register(EventType)


# ===============================
# Event Management Admin
# ===============================

class EventServiceInline(admin.TabularInline):
    model = EventService
    extra = 1


class EventPortfolioInline(admin.TabularInline):
    model = EventPortfolio
    extra = 1


class EventManagementAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'owner_name', 'email', 'city', 'status')
    list_filter = ('status', 'city')
    search_fields = ('team_name', 'owner_name', 'email')
    inlines = [EventServiceInline, EventPortfolioInline]


admin.site.register(EventManagement, EventManagementAdmin)


# ===============================
# Event Package
# ===============================

class EventPackageAdmin(admin.ModelAdmin):
    list_display = ('package_name', 'package_type', 'price', 'event_type')
    list_filter = ('package_type', 'event_type')
    search_fields = ('package_name',)


admin.site.register(EventPackage, EventPackageAdmin)


# ===============================
# Event Portfolio
# ===============================

admin.site.register(EventPortfolio)
admin.site.register(EventService)


# ===============================
# Artist Admin
# ===============================

class ArtistPortfolioInline(admin.TabularInline):
    model = ArtistPortfolio
    extra = 1


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('stage_name', 'artist_type', 'experience', 'available_city', 'status')
    list_filter = ('artist_type', 'status', 'available_city')
    search_fields = ('stage_name', 'full_name', 'email')
    inlines = [ArtistPortfolioInline]


admin.site.register(Artist, ArtistAdmin)


# ===============================
# Artist Portfolio
# ===============================

admin.site.register(ArtistPortfolio)


# ===============================
# Bookings
# ===============================

class ArtistBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'event_name', 'event_date', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('event_name',)


admin.site.register(ArtistBooking, ArtistBookingAdmin)


class EventBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'event_type', 'event_date', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('company__team_name',)


admin.site.register(EventBooking, EventBookingAdmin)


# ===============================
# Payments
# ===============================

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__name',)


admin.site.register(Payment, PaymentAdmin)


# ===============================
# Company Events
# ===============================

class CompanyEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'company', 'event_type', 'location')
    search_fields = ('event_name',)


admin.site.register(CompanyEvent, CompanyEventAdmin)