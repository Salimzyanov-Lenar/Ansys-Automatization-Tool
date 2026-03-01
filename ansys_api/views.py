import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from ansys_api import models, forms, executor, services


def main_page(request):
    return render(request, "ansys_api/main_page.html")


def experiment_page(request):
    experiments = models.Experiment.objects.order_by("-created_at")
    context = {"experiments": experiments}
    return render(request, "ansys_api/experiment_page.html", context=context)


def experiment_results_page(request, experiment_id):
    experiment = get_object_or_404(models.Experiment, id=experiment_id)
    calculation_results = experiment.calculation_results.order_by("-created_at")
    context = {"experiment": experiment, "user_calculation_results": calculation_results}
    return render(request, "ansys_api/results_page.html", context=context)


def get_experiment_graphs(request, experiment_id):
    experiment = get_object_or_404(models.Experiment, id=experiment_id)
    graph = services._build_graph_for_experiment(experiment)
    if graph:
        messages.success(request, "График успешно построен.")
    else:
        messages.warning(request, "Не удалось построить график.")
    experiment_graphs = experiment.graphics.order_by("-created_at")
    context = {"experiment": experiment, "task_graphs": experiment_graphs}
    return render(request, "ansys_api/graphs_page.html", context=context)


def run_experiment_view(request, user_task_id):
    user_task = get_object_or_404(models.UserTask, id=user_task_id)

    if request.method == "POST":
        form = forms.ExperimentForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user_task = user_task

            experiment_params_raw = form.cleaned_data["experiment_parameters"]
            try:
                runs = services.parse_experiment_parameters(experiment_params_raw)
            except Exception as e:
                form.add_error("experiment_parameters", f"Ошибка парсинга: {e}")
            else:
                exp.parameters = json.loads(experiment_params_raw)
                exp.save()

                # looping through runs and executing them sequentially
                for run_params in runs:
                    services.update_config_with_new_params(
                        user_task=user_task,
                        new_params=run_params,
                    )
                    user_task.parameters = run_params
                    user_task.save(update_fields=["parameters"])
                    executor.execute_user_task(user_task=user_task, experiment=exp)

                messages.success(request, f"Эксперимент '{exp.name}' запущен ({len(runs)} запусков).")
                return redirect("ansys_api_retrieve_user_task_page", user_task_id=user_task.id)
    else:
        initial = {}
        if user_task.parameters:
            initial["experiment_parameters"] = json.dumps(user_task.parameters, indent=2, ensure_ascii=False)
        form = forms.ExperimentForm(initial=initial)

    return render(
        request,
        "ansys_api/run_experiment_page.html",
        {"user_task": user_task, "form": form},
    )


def execute_user_task(request, user_task_id):
    user_task = get_object_or_404(models.UserTask, id=user_task_id)
    executor.execute_user_task(user_task) 
    messages.success(request, "Задача успешно запущена!")
    return redirect(reverse('ansys_api_retrieve_user_task_page', kwargs={'user_task_id': user_task.id}))


def user_tasks_page(request):
    user_tasks = models.UserTask.objects.order_by("-created_at")
    context = {"user_tasks": user_tasks}
    return render(request, "ansys_api/user_tasks_page.html", context=context)


def retrieve_user_task_page(request, user_task_id):
    user_task = get_object_or_404(models.UserTask, id=user_task_id)
    context = {"user_task": user_task}
    return render(request, "ansys_api/retrieve_user_task_page.html", context=context)


def edit_user_task(request, user_task_id):
    user_task = get_object_or_404(models.UserTask, id=user_task_id)
    if request.method == "POST":
        form = forms.UserTaskForm(request.POST, request.FILES, instance=user_task)
        if form.is_valid():
            form.save()
            services.update_config_with_new_params(user_task=user_task, new_params=form.cleaned_data["parameters"])
            messages.success(request, "Задача успешно обновлена!")
            return redirect(reverse('ansys_api_retrieve_user_task_page', kwargs={'user_task_id': user_task.id}))
        else:
            form = forms.UserTaskForm(instance=user_task)
    return render(request, "ansys_api/edit_user_task.html", {"form": forms.UserTaskForm(instance=user_task), "user_task": user_task})


def create_user_task(request):
    if request.method == "POST":
        form = forms.UserTaskForm(request.POST, request.FILES)
        if form.is_valid():
            user_task = form.save()
            return redirect("ansys_api_retrieve_user_task_page", user_task_id=user_task.id)
    else:
        form = forms.UserTaskForm()

    return render(request, "ansys_api/create_user_task.html", {"form": form})


def delete_user_task(request, user_task_id):
    user_task = get_object_or_404(models.UserTask, id=user_task_id)

    if request.method == "POST":
        user_task.delete()
        messages.success(request, "Задача успешно удалена!")
        return redirect(reverse('ansys_api_user_tasks_page'))
    
    return render(request, "ansys_api/delete_user_task.html", {"user_task": user_task})


def results_page(request):
    user_calculation_results = models.CalculationResult.objects.order_by("-created_at")
    context = {"user_calculation_results": user_calculation_results}
    return render(request, "ansys_api/results_page.html", context=context)


def graphs_page(request):
    task_graphs = models.Graph.objects.order_by("-created_at")
    context = {"task_graphs": task_graphs}
    return render(request, "ansys_api/graphs_page.html", context=context)


def docs_page(request):
    return render(request, "ansys_api/docs_page.html")
