from django.contrib import admin
from django.utils.html import format_html

from ansys_api.models import Executor, UserTask, CalculationResult, Graph
from ansys_api.executor import execute_user_task
from ansys_api.services import update_config_with_new_params, _build_graph_with_experiement_result


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'config', 'project', 'executor', 'created_at')

    def save_model(self, request, user_task, form, change):
        # super().save_model(request, user_task, form, change)
        update_config_with_new_params(user_task=user_task, new_params=form.cleaned_data["parameters"])
        execute_user_task(user_task)
        super().save_model(request, user_task, form, change)


@admin.register(CalculationResult)
class CalculationResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'user_task', 'created_at')


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview', 'graph', 'user_task', 'created_at')

    def save_model(self, request, graph, form, change):
        super().save_model(request, graph, form, change)
        _build_graph_with_experiement_result(graph=graph)

    def preview(self, obj):
        if obj.graph:
            return format_html(
                '<img src="{}" style="max-height: 200px;" />',
                obj.graph.url,
            )
        return "-"
    
    preview.short_description = "Preview"