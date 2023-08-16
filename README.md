
# Databyte Django App

## General Details

### Description

The digital era sees data growing exponentially. Keeping track of storage usage is more important than ever. The Databyte app aids in this endeavor by offering tools to monitor and compute the storage usage of Django model instances. With its custom field types and automated calculations, integrating storage tracking into your Django project becomes a breeze.
### Features
 - **Custom Field Types**:  Databyte introduces three custom field types:
   - `ExternalStorageTrackingField`: A simple BigIntegerField to keep track of external storage. 
   - `AutomatedStorageTrackingField`: A BigIntegerField that automatically computes the storage used by its containing record.
   - `StorageAwareForeignKey`: A ForeignKey field that indicates to Databyte that it should recognize this parent-child relationship in storage counting.

 - **Automated Computation**:  Storage usage is computed and updated automatically whenever a record changes.

 - **Child Storage Computation**: Automatically aggregates storage information from child records linked via a `StorageAwareForeignKey`.

 - **File Storage Calculation**: For models with `FileField` or `ImageField`, Databyte can compute the storage taken up by these files.

 - **Dynamic Parent-Child Relationships**: Using the `StorageAwareForeignKey`, you can define which records should contribute to their parent's storage count.

## Setup Instructions
1. **Install the App**:

    ```
    pip install databyte
    ```

2. **Add the App**: 
Include 'databyte' in your INSTALLED_APPS setting.

    ```python
    INSTALLED_APPS = [
        ...
        'databyte',
        ...
    ]
    ```

3. **Run Migrations**:
As with any new app added to a Django project, run migrations:

    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

## Usage
- **Integrate Custom Fields**:
Introduce the `ExternalStorageTrackingField` and `AutomatedStorageTrackingField` in any model you wish to track:
    ```python
    from django.db import models
    from databyte.fields import ExternalStorageTrackingField, AutomatedStorageTrackingField
    
    class MyModel(models.Model):
        external_storage = ExternalStorageTrackingField()
        automated_storage = AutomatedStorageTrackingField(include_in_parents_count=True)
    ```
- **File Storage**:
If your model has a `FileField` or `ImageField`, Databyte will automatically account for their sizes when computing storage.

- **Parent-Child Relationships**:
Use `StorageAwareForeignKey` to establish which child records should be accounted for in parent records' storage calculations:
    ```python
    from django.db import models
    from databyte.fields import StorageAwareForeignKey
    
    class ChildModel(models.Model):
    parent = StorageAwareForeignKey(ParentModel, on_delete=models.CASCADE, count_as_storage_parent=True)
    ```

- **Signal Integration**:
Ensure the signals provided by Databyte are integrated to automatically update storage values on record save and delete events.

## Contributing
As this is an open-source project hosted on GitHub, your contributions and improvements are welcome! Follow these general steps for contributing:

1. **Fork the Repository**: 
Start by forking the main repository to your personal GitHub account.

2. **Clone the Forked Repository**: 
Clone your forked repository to your local machine.

    ```
    git clone https://github.com/YidiSprei/DjangoDatabyte.git
    ```

3. **Create a New Branch**: 
Before making any changes, create a new branch:

    ```
    git checkout -b feature-name
    ```

4. **Make Your Changes**: 
Implement your features, enhancements, or bug fixes.

5. **Commit & Push**:

    ```
    git add .
    git commit -m "Descriptive commit message about changes"
    git push origin feature-name
    ```
   
6. **Create a Pull Request (PR)**: 
Go to your forked repository on GitHub and click the "New Pull Request" button. Make sure the base fork is the original repository, and the head fork is your repository and branch. Fill out the PR template with the necessary details.

Remember to always be respectful and kind in all interactions with the community. It's all about learning, growing, and helping each other succeed!

## Credits
Developed with 💙 by Yidi Sprei. We thank all the contributors and the Django community for their support and inspiration.

