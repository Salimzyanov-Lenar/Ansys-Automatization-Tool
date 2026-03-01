from django.urls import path
from ansys_api import views


urlpatterns = [
    path('', views.main_page, name='ansys_api_main_page'),

    path('user-tasks/', views.user_tasks_page, name='ansys_api_user_tasks_page'),
    path('user-tasks/<int:user_task_id>/', views.retrieve_user_task_page, name='ansys_api_retrieve_user_task_page'),
    path('user-tasks/<int:user_task_id>/edit/', views.edit_user_task, name='ansys_api_edit_user_task'),
    path('user-tasks/<int:user_task_id>/delete/', views.delete_user_task, name='ansys_api_delete_user_task'),
    path('user-tasks/<int:user_task_id>/execute/', views.execute_user_task, name='ansys_api_execute_user_task'),
    path('user-tasks/create/', views.create_user_task, name='ansys_api_create_user_task'),

    path('user-tasks/<int:user_task_id>/experiment/', views.run_experiment_view, name='ansys_api_run_experiment'),
 
    path('experiments/', views.experiment_page, name='ansys_api_experiment_page'),
    path('experiments/<int:experiment_id>/results/', views.experiment_results_page, name='ansys_api_experiment_results_page'),
    path('experiments/<int:experiment_id>/graphs/', views.get_experiment_graphs, name="ansys_api_experiment_graphs_page"),

    path('results/', views.results_page, name='ansys_api_results_page'),
    path('graphs/', views.graphs_page, name='ansys_api_graphs_page'),
    path('docs/', views.docs_page, name='ansys_api_docs_page'),
]