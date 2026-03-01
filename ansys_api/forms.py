from django import forms
from ansys_api.models import UserTask, Experiment


class UserTaskForm(forms.ModelForm):
    class Meta:
        model = UserTask
        fields = [
            'config',
            'project',
            'executor',
            'parameters',
        ]


class ExperimentForm(forms.ModelForm):
    experiment_parameters = forms.CharField(
        label="Experiment parameters (JSON)",
        widget=forms.Textarea(attrs={"rows": 8}),
        required=True,
    )

    class Meta:
        model = Experiment
        fields = ["name", "description", "experiment_parameters"]
