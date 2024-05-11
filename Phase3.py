#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import requests
from zipfile import ZipFile
from io import BytesIO
from radon.metrics import mi_visit
import matplotlib.pyplot as plt

# List of repositories to analyze
REPOSITORIES = [
    "https://github.com/pallets/flask",
    "https://github.com/requests/requests"
]

def download_repository(repository):
    """ Download and extract repository contents. """
    repo_name = repository.split("/")[-1]
    repo_zip_url = f"{repository}/archive/refs/heads/main.zip"
    response = requests.get(repo_zip_url)
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zip_file:
            zip_file.extractall(repo_name)
        return repo_name
    else:
        print(f"Failed to download repository: {repository}")
        return None

def calculate_cohesion(files):
    total_lines = 0
    total_code_lines = 0
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines += len(lines)
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            total_code_lines += len(code_lines)
    cohesion = total_code_lines / total_lines if total_lines != 0 else 0
    return cohesion

def calculate_coupling(files):
    unique_imports = set()
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            imports = [line.strip().split()[-1] for line in lines if line.strip().startswith('import') and len(line.strip().split()) > 1]
            unique_imports.update(imports)
    return len(unique_imports)

def analyze_files(repo_path):
    """ Analyze Python files in the repository. """
    metrics = {}
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        radon_metrics = mi_visit(content, multi=True)  # Radon metrics
                        cohesion = calculate_cohesion([file_path])
                        coupling = calculate_coupling([file_path])
                        metrics[file] = {'Radon Metrics': radon_metrics, 'Cohesion': cohesion, 'Coupling': coupling}
                except Exception as e:
                    print(f"Error calculating metrics for {file_path}: {e}")
    return metrics

def analyze_repositories(repositories):
    """ Analyze multiple repositories. """
    repository_metrics = {}
    for repository in repositories:
        repo_path = download_repository(repository)
        if repo_path:
            print(f"Analyzing repository: {repository}")
            repository_name = repository.split("/")[-1]
            repository_metrics[repository_name] = analyze_files(repo_path)
            print()
        else:
            print(f"Failed to analyze repository: {repository}")
    return repository_metrics

def print_comparison(repository_metrics):
    """ Print comparison of metrics between repositories. """
    for repository, metrics in repository_metrics.items():
        print(f"Metrics for {repository}:")
        for file, values in metrics.items():
            print(f"\tFile: {file}")
            for metric, value in values.items():
                print(f"\t\t{metric}: {value}")
            print()
        print()

def plot_comparison(repository_metrics):
    """ Plot comparison of metrics between repositories. """
    avg_cohesion = []
    avg_coupling = []
    repositories = []

    for repository, metrics in repository_metrics.items():
        repositories.append(repository)
        cohesion_sum = 0
        coupling_sum = 0
        num_files = len(metrics)
        
        for file_metrics in metrics.values():
            cohesion_sum += file_metrics['Cohesion']
            coupling_sum += file_metrics['Coupling']
        
        avg_cohesion.append(cohesion_sum / num_files)
        avg_coupling.append(coupling_sum / num_files)

    plt.figure(figsize=(10, 6))
    plt.bar(repositories, avg_cohesion, color='blue', label='Average Cohesion')
    plt.bar(repositories, avg_coupling, color='orange', label='Average Coupling', alpha=0.5)
    plt.xlabel('Repositories')
    plt.ylabel('Metrics')
    plt.title('Average Cohesion and Coupling Comparison')
    plt.legend()
    plt.show()

def main():
    repository_metrics = analyze_repositories(REPOSITORIES)
    print_comparison(repository_metrics)
    plot_comparison(repository_metrics)

if __name__ == "__main__":
    main()


# In[ ]:




