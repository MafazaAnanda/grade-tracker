from django.urls import path
from grade_tracker.views import (
    landing_page_view, register_view, login_view, logout_view, home_view, 
    mata_kuliah_details_views, create_mata_kuliah_view, 
    create_komponen_penilaian_view, edit_mata_kuliah_view, delete_mata_kuliah_view
)

app_name = 'grade_tracker'

urlpatterns = [
    path('', landing_page_view, name='landing_page'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('create-mata-kuliah/', create_mata_kuliah_view, name='create_mata_kuliah'),
    path('mata-kuliah/<uuid:mata_kuliah_id>/create_komponen/', create_komponen_penilaian_view, name='create_komponen_penilaian'),
    path('mata-kuliah/<uuid:mata_kuliah_id>/edit/', edit_mata_kuliah_view, name='edit_mata_kuliah'),
    path('mata-kuliah/<uuid:mata_kuliah_id>delete/', delete_mata_kuliah_view, name='delete_mata_kuliah'),
    path('mata-kuliah<uuid:mata_kuliah_id>details/', mata_kuliah_details_views, name='mata_kuliah_details'),
]