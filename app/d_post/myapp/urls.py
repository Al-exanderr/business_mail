from django.urls import include, path
from . import views
from .views import (Login, TrackSHPI, RegistryGroups,
                    AddScanShpi, AddRegistry, AddNoticesXLSX,
                    Statistics, Statistics_print, Detail_statistics,
                    GetAbonentsInfoView)
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # /myapp/
    path('', views.index, name='index'),

    # /myapp/track_shpi/
    path('track_shpi/', TrackSHPI.as_view()),

    # /myapp/track_shpi/<int:shpi>/
    path('track_shpi/<int:shpi>/', views.track_detail_shpi),

    # /myapp/login/
    path('login/', Login.as_view()),

    # /myapp/logout/
    path('logout/', views.logout_view),

    # /myapp/add_registry/
    path('add_registry/', AddRegistry.as_view()),

    # /myapp/add_scan_shpi/
    path('add_scan_shpi/', AddScanShpi.as_view()),

    # /myapp/add_notices_xlsx/
    path('add_notices_xlsx/', AddNoticesXLSX.as_view()),

    # /myapp/pdf/
    path('track_as_pdf/', views.generate_pdf),

    # /myapp/view_stat/
    path('view_stat/', Statistics.as_view()),

    # /myapp/view_detail_stat/
    path('view_detail_stat/', Detail_statistics.as_view()),

    # /myapp/print_statistic
    path('print_statistic/', Statistics_print.as_view()),

    # /myapp/view_registers/
    path('view_registers/', views.view_registers),

    # /myapp/view_ordinary_registry/
    path('view_ordinary_registry/<int:registry_id>/',
         views.view_ordinary_registry),

    # /myapp/view_registers/ current registry
    path('view_registers/<int:register>/', views.view_registery_detail),

    # /myapp/view_list_of_registers/
    path('view_list_of_registers/', views.view_list_of_registers),

    # /myapp/del_registers/
    path('del_registers/', RegistryGroups.as_view()),

    # /myapp/search/
    path('search/', views.search, name='search'),

    # API ------
    # /myapp/
    path('api/abonents/', GetAbonentsInfoView.as_view()),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
