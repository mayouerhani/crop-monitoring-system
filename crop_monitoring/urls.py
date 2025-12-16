from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('api.urls')),
]

from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs d'authentification - AJOUTE CETTE LIGNE
    path('api/auth/', include('authentication.urls')),
    
    # URLs de l'API existante
    path('api/', include('api.urls', namespace='api')),  
    path('api/', include('monitoring.urls')),
]
