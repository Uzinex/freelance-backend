from django.contrib import admin
from django.urls import path, include
from strawberry.django.views import GraphQLView
from schema import schema
from payments import views as payment_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/', include('accounts.urls')),
    path('graphql/', GraphQLView.as_view(schema=schema)),
    path('api/payments/callback/<str:provider>/', payment_views.payment_callback),
]
