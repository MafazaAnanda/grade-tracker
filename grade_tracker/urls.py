from django.urls import path
from grade_tracker.views import landing_page_view, register_view, login_view, logout_view, dashboard_view, create_mata_kuliah_view, create_komponen_penilaian_view

app_name = 'grade_tracker'

urlpatterns = [
    path('', landing_page_view, name='landing_page'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-mata-kuliah/', create_mata_kuliah_view, name='create_mata_kuliah'),
    path('mata-kuliah/<uuid:mata_kuliah_id>/create_komponen/', create_komponen_penilaian_view, name='create_komponen_penilaian'),
]