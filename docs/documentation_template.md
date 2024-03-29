# Introduction
This is a chalice template which allows the user to create backend application and follows best practices. This provides extensive set of features and allows very smooth quick setup of the initial project.

# Quickstart
Run `chalice local` inside the runtime folder and send a `GET` request to `http://localhost:8000/` to see the output:  
```json
{
    'healthcheck': 'healthy'
}
``` 
There are various other APIs listed for you depending on the options you select while service creation.

# How to set it up?
For the developemnt setup you just follow the commands below:  
1. `cd runtime`
2. `pip install -r requirements.txt`
3. `chalice local`

## External APIs/Services
* If you have selected the social authentication features then you have to create the clients for them and provide the client_id and secret values in the environment variables.  
* If you have selected the database feature then you have to create the database and provide the credentials in the environment variables.

## Migrations
* After you have provided the database credentials in the .env file you can run the migrations inside runtime folder.  
* `alembic -c chalicelib/alembic.ini revision --autogenerate -m "<msg>"`  
    This will auto generate the migration file inside /runtime/migrations/versions folder after you have made any changes to the model. Similar to Django `makemigrations` command.  
* `alembic -c chalicelib/alembic.ini upgrade heads`  
    This will push the migration file to your connected database and make changes to your tables. You can look to the `alembic_versions` tables in your database to see the recent push made to it. This is same as the Django `migrate` command.  
* If you create a new model just import it in the `env.py` file inside the migrations folder and follow the above steps. This will make the make the autogenerated migration files to include changes for this newly created model too.   
## Environment Variable Set up
All the key values are included in the .env.dev.template and .env.prod.template file as per requirement. You can set them up using our platform, more details are in the enviromemnt management doc.

# How to use it?
You can use customize the APIs according to your requirement. You can use the social auth APIs to register the user or login into the website or fetch some other metadata. 

## Sample Usage
The `/auth/integrations/google` API just updates the google_access_token and google_refresh_token. You can extent this to store other data of the user such as first_name, last_name, address, etc. from google. The `/auth/social/devconnect` API is used for user login and register.

## Run scripts
There is a scripts folder which contains all the scripts that needs to be run depending on the state of the project. You can customize these scripts as per your requirement.

`init.sh`: Runs at the time of workspace creation in devspace.  
`entrypoint.sh`: Runs when the created workspace is activated in devspace.  
`deploy.sh`: Run this script to deploy your project.  
`destroy.sh`: Run this script to destroy the deployment.

# How to deploy it in production?
You can use the scripts `deploy.sh` and `destroy.sh` to deploy your project or destroy thhe deployment respectively.

## Changes to IaC
Is there a need to add new components to deployment environment? 

Eg. S3Bucket to store media, x-ray daemon to capture traces. 

`Note: Ideally, the required infrastructure changes should have already been present as part of the feature, and this section just makes those explicity clear`

## Environment Variable Set up
You need to add the AWS environment variables for production. You can do this using our platform again. All the required variables are listed in the .env.prod.template file.
