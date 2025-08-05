"""
URL configuration for torax_ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# Imports para Swagger (drf-yasg)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de la vista del esquema de la API para Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="ToraxIA API",
        default_version='v1',
        description="Documentación de la API ToraxIA. Aquí se pueden ver y probar todos los endpoints disponibles.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="pnepotti@gmail.com"),
        license=openapi.License(name="UTN FRLP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para la administración
    # Incluye las rutas de la app diagnosticos
    path('diagnostics/', include('diagnostics.urls')),

    # URLs para la documentación de la API con Swagger y ReDoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]

# Para servir archivos estáticos y medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
