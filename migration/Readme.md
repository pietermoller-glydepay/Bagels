# Actual Budget to Bagels Migration

This script helps migrate data from Actual Budget (https://actualbudget.com/) to Bagels. It transfers your accounts, categories, and transactions while preserving their relationships and attributes.

**IMPORTANT**: This script was tested with a fresh Bagels installation. Running it on an existing Bagels database may have unexpected results. Always backup your Bagels database before running the migration.

## Important Notes

- Transactions without categories in Actual Budget will be assigned to an "Uncategorized" category in Bagels
- The script converts all amounts from cents (Actual Budget) to dollars (Bagels)

## Steps to Migrate

1. Export Your Actual Budget Data:
 - Open Actual Budget
 - Navigate to More → Settings → Export Data
 - Save and extract the zip file
 - Locate the `db.sqlite` file in the extracted contents

2. Find Your Bagels Database Path:

 ```bash
 bagels locate database
 ```

3. Update the Migration Script:

 - Open `migrate_actualbudget.py`
 - Replace the database paths in the script:
   ```python
   migrator = BudgetToBagelsMigration(
       'path/to/your/actualbudget/db.sqlite',  # Source database
       'path/to/your/bagels/db.db'            # Target database
   )
   ```

4. Run the Migration:

 ```bash
 uv run python3 migrate_actualbudget.py
 ```


