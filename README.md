![Github CI](https://github.com/edukorg/drf-toolkit/workflows/Github%20CI/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/maintainability)](https://codeclimate.com/github/edukorg/drf-toolkit/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/test_coverage)](https://codeclimate.com/github/edukorg/drf-toolkit/test_coverage)

# Django REST Framework Toolkit

## Motivation

[Django](https://www.djangoproject.com/) and [DRF](https://www.django-rest-framework.org/) is an awesome combination to build REST APIs.

DRF also support a lot of great [plugins](https://www.django-rest-framework.org/community/third-party-packages/) that can extend even further it's capabilities.

The DRF Toolkit comes apply common [RESTFul patterns](https://restfulapi.net/) to the framework by adding base classes that can be used in your existing DRF projects.

Most use cases are covered by DRF Toolkit, allowing your project to be way simpler so you only have to worry about the business logic.


## Usage

- Install with: ``pip install drf-kit``
- Choose which features you want to use, and apply them accordinly.

# Features

## Models

DRF Toolkit's Models provide abstract models that can be inherited, thus providing some features:

### Diff

Allows tracking in-memory changes to fields from given model.

**All models** support this feature.

**HOW IT WORKS**:
Some properties allow extracting these info:
- `._diff`: dict with tuples `(before, after)` of every changed field
- `._has_changed`: boolean if the model has any change since its previous load

**USE CASE**: to make decisions during the processing only when a given field has changed.

### Context-based Storage

Allows to use model's context to build file storage paths, instead of storing all files in a single "folder".

**All models** support this feature.

**HOW IT WORKS**:
- once a model is created and it has a file field, the file is stored temporarily in a temporary path, and then persisted into the database
- after stored, the model gets its primary key from the database, then the definitive file path can be set.
- with the definitive file path, the file is moved in the bucket to its final destination and then the model is updated with the definitive file path.

**CAVEATS**: models that have file-fields are stored twice, hitting database two times.

**USE CASE**: to store files in S3/GCS using the model's PK in file's path. Such as `/users/100/profile.png`

### Self Ordering

Powered by `django-ordered-model`, models' ordering can be persisted into the database.

The order can also be relative to another field.

**Only Ordered* models** support this feature.

**HOW IT WORKS**:
- models have an additional field `order` that stores the position
- before saving/removing, the order is checked (for sparse positions or out-of-index), which can trigger a complete reordering of all other models.

**CAVEATS**: if a given ordering will generate sparse list (eg. deleting or changing position), all other models will be updated.

**USE CASE**: to store ordered Chapters (eg. chapter 1, chapter 2) for Books. So Book 1 can have Chapters 1, 2 and 3; and Book 2 can have its own Chapter 1 and 2. Individually ordered.

### Inheritance

### Logic Deletion

### How to Use

## Serializers

### How to Use

## Views

### How to Use

### Exception Handling

## Signals

### How to Use

## Filters

### How to Use

## Pagination

### How to Use

## Caching

### How to Use

## Testing

## Signals

### How to Use

