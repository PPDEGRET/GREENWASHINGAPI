# GreenCheck Database Schema

This document outlines the schema for the new tables in the GreenCheck database.

## `users` Table

This table stores user information, including authentication credentials and onboarding data.

| Column          | Type          | Description                                      |
| --------------- | ------------- | ------------------------------------------------ |
| `id`            | `UUID`        | Primary key for the user.                        |
| `email`         | `String(320)` | User's email address (unique).                   |
| `hashed_password` | `String(1024)`| Hashed password for the user.                    |
| `is_active`     | `Boolean`     | Whether the user's account is active.            |
| `is_superuser`  | `Boolean`     | Whether the user has superuser privileges.       |
| `is_verified`   | `Boolean`     | Whether the user's email has been verified.      |
| `is_premium`    | `Boolean`     | Whether the user is a premium member.            |
| `created_at`    | `DateTime`    | Timestamp of when the user was created.          |
| `last_login_at` | `DateTime`    | Timestamp of the user's last login.              |
| `company_name`  | `String(100)` | User's company name.                             |
| `sector`        | `String(100)` | User's industry sector.                          |
| `company_size`  | `String(50)`  | Size of the user's company.                      |
| `country`       | `String(100)` | User's country.                                  |
| `role`          | `String(100)` | User's role in their company.                    |
| `use_cases`     | `JSON`        | A list of the user's primary use cases.          |
| `custom_needs`  | `String(500)` | A description of the user's custom needs.        |

## `usage_logs` Table

This table stores a log of each analysis performed by a user.

| Column                | Type       | Description                                      |
| --------------------- | ---------- | ------------------------------------------------ |
| `id`                  | `UUID`     | Primary key for the usage log entry.             |
| `user_id`             | `UUID`     | Foreign key to the `users` table.                |
| `timestamp`           | `DateTime` | Timestamp of when the analysis was performed.    |
| `input_type`          | `String(50)` | The type of input provided for analysis.         |
| `chars_count`         | `Integer`  | The number of characters in the input text.      |
| `premium_features_used` | `Boolean`  | Whether premium features were used in the analysis.|
| `result_json`         | `JSON`     | The JSON result of the analysis.                 |
| `duration_ms`         | `Integer`  | The duration of the analysis in milliseconds.    |
