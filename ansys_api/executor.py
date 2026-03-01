import time
import subprocess
import os
from ansys_api.models import Experiment, UserTask, CalculationResult
from django.core.files import File


class UserTaskExcutor:
    """
    A class to execute Ansys Fluent with a given configuration file.
    """
    def __init__(self, user_task: UserTask):
        self.user_task = user_task
        self.command = [
            self.user_task.executor.pure_path,
            "-B",
            "-F", user_task.project_path, 
            "-R", user_task.config.path,
        ]

    def __call__(self, *args, **kwds):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"An error occurred while executing Ansys Fluent: {result.stderr}")
                raise RuntimeError("ANSYS failed")

            else:
                print(f"Ansys Fluent executed successfully: {result.stdout}")
        except Exception as e:
            print(f"Exception occurred while executing Ansys Fluent: {e}")


def execute_user_task(user_task: UserTask, experiment: Experiment | None =None):
    """
    A function to execute Ansys Fluent with a given UserTask instance.
    """
    executor = UserTaskExcutor(user_task)
    try:
        print("Start calculation...")
        executor()
        print("Calculation completed.")
        print("Saving result...")

        for _ in range(10):
            time.sleep(1)

        result_path = user_task.result_path
        with open(result_path, 'rb') as csv_file:
            django_file = File(csv_file)
            result = CalculationResult(user_task=user_task)
            if experiment:
                result.experiment = experiment
            result.result.save(os.path.basename(result_path), django_file, save=True)

        print("Result saved.")
    except Exception as e:
        print(f"Exception occurred while executing user task: {e}")
